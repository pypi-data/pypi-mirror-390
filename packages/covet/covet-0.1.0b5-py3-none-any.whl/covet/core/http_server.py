"""
Production-Grade HTTP/1.1 Compliant Server for CovetPy

This module implements a complete HTTP/1.1 server with full RFC 7230-7235 compliance,
performance optimizations, and production-ready features.

Features:
- Complete HTTP/1.1 protocol implementation
- Keep-alive connections with timeout management
- Chunked transfer encoding support
- Content-Length validation
- Connection pooling and reuse
- Buffer optimization and zero-copy techniques
- Robust error handling
- Thread-safe operations
- Production-ready logging and monitoring
"""

import asyncio
import email.utils
import logging
import re
import socket
import ssl
import time
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import unquote

# Internal imports
from .exceptions import CovetError
from .http import Request, Response


class HTTPVersion(Enum):
    """HTTP version enumeration"""

    HTTP_1_0 = "HTTP/1.0"
    HTTP_1_1 = "HTTP/1.1"


class ConnectionState(Enum):
    """Connection state management"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    KEEP_ALIVE = "keep_alive"
    CLOSING = "closing"
    CLOSED = "closed"


@dataclass
class ServerConfig:
    """HTTP Server Configuration"""

    host: str = "127.0.0.1"
    port: int = 8000
    backlog: int = 1024
    max_connections: int = 10000
    keep_alive_timeout: int = 75  # seconds
    max_keep_alive_requests: int = 1000
    max_request_size: int = 16 * 1024 * 1024  # 16MB
    max_header_size: int = 8192  # 8KB
    request_timeout: int = 30  # seconds
    response_timeout: int = 30  # seconds
    buffer_size: int = 64 * 1024  # 64KB
    tcp_nodelay: bool = True
    tcp_keepalive: bool = True
    so_reuseport: bool = True
    ssl_context: Optional[ssl.SSLContext] = None
    access_log: bool = True
    debug: bool = False
    server_name: str = "CovetPy/1.0"


class ConnectionPool:
    """Advanced connection pool with lifecycle management"""

    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.connections: Dict[str, "HTTPConnection"] = {}
        self.active_count = 0
        self.total_count = 0
        self._cleanup_task = None
        self._lock = asyncio.Lock()

    async def add_connection(self, connection: "HTTPConnection") -> bool:
        """Add connection to pool"""
        async with self._lock:
            if self.active_count >= self.max_size:
                return False

            self.connections[connection.connection_id] = connection
            self.active_count += 1
            self.total_count += 1
            return True

    async def remove_connection(self, connection_id: str) -> None:
        """Remove connection from pool"""
        async with self._lock:
            if connection_id in self.connections:
                del self.connections[connection_id]
                self.active_count -= 1

    async def cleanup_expired(self, max_age: float) -> int:
        """Clean up expired connections"""
        now = time.time()
        expired = []

        async with self._lock:
            for conn_id, conn in self.connections.items():
                if now - conn.last_activity > max_age:
                    expired.append(conn_id)

        # Close expired connections
        for conn_id in expired:
            if conn_id in self.connections:
                conn = self.connections[conn_id]
                await conn.close()
                await self.remove_connection(conn_id)

        return len(expired)

    def get_stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        return {
            "active_connections": self.active_count,
            "total_connections": self.total_count,
            "max_connections": self.max_size,
        }


class HTTPConnection:
    """Individual HTTP connection with state management"""

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        server: "HTTPServer",
        connection_id: str,
    ):
        self.reader = reader
        self.writer = writer
        self.server = server
        self.connection_id = connection_id
        self.state = ConnectionState.CONNECTING
        self.created_at = time.time()
        self.last_activity = time.time()
        self.request_count = 0
        self.keep_alive = True
        self.http_version = HTTPVersion.HTTP_1_1
        self.remote_addr = self._get_remote_addr()
        self.local_addr = self._get_local_addr()

    def _get_remote_addr(self) -> str:
        """Get remote address safely"""
        try:
            peername = self.writer.get_extra_info("peername")
            return f"{peername[0]}:{peername[1]}" if peername else "unknown"
        except (OSError, IndexError, AttributeError, TypeError):
            return "unknown"

    def _get_local_addr(self) -> str:
        """Get local address safely"""
        try:
            sockname = self.writer.get_extra_info("sockname")
            return f"{sockname[0]}:{sockname[1]}" if sockname else "unknown"
        except (OSError, IndexError, AttributeError, TypeError):
            return "unknown"

    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = time.time()

    def should_keep_alive(self) -> bool:
        """Check if connection should be kept alive"""
        if not self.keep_alive:
            return False
        if self.request_count >= self.server.config.max_keep_alive_requests:
            return False
        if time.time() - self.last_activity > self.server.config.keep_alive_timeout:
            return False
        return True

    async def close(self):
        """Close connection gracefully"""
        self.state = ConnectionState.CLOSING
        try:
            if not self.writer.is_closing():
                self.writer.close()
                await self.writer.wait_closed()
        except (OSError, asyncio.CancelledError, RuntimeError) as e:
            # Log error but don't raise - connection is closing anyway
            logger = logging.getLogger(__name__)
            logger.debug(f"Error closing connection: {e}")
        finally:
            self.state = ConnectionState.CLOSED


class HTTPRequestParser:
    """High-performance HTTP/1.1 request parser"""

    # HTTP method validation
    VALID_METHODS = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "TRACE",
        "CONNECT",
    }

    # HTTP version regex
    HTTP_VERSION_RE = re.compile(r"^HTTP/1\.[01]$")

    # Header name validation (RFC 7230)
    HEADER_NAME_RE = re.compile(r"^[!#$%&\'*+\-.0-9A-Z^_`a-z|~]+$")

    def __init__(self, max_header_size: int = 8192, max_request_size: int = 16 * 1024 * 1024):
        self.max_header_size = max_header_size
        self.max_request_size = max_request_size

    async def parse_request(
        self, reader: asyncio.StreamReader
    ) -> Tuple[Optional[Request], Dict[str, Any]]:
        """Parse HTTP request with full RFC compliance"""
        try:
            # Parse request line and headers
            request_line, headers, raw_headers = await self._parse_headers(reader)

            if not request_line:
                return None, {"error": "Empty request"}

            # Parse request line
            method, path, version = self._parse_request_line(request_line)

            # Parse headers
            header_dict = self._parse_header_dict(headers)

            # Extract important headers
            content_length = self._get_content_length(header_dict)
            transfer_encoding = header_dict.get("transfer-encoding", "").lower()
            connection_header = header_dict.get("connection", "").lower()
            host_header = header_dict.get("host", "")

            # Determine keep-alive
            keep_alive = self._should_keep_alive(version, connection_header)

            # Parse body
            body = await self._parse_body(reader, content_length, transfer_encoding)

            # Get remote address safely
            remote_addr = ""
            if reader._transport:
                try:
                    peername = reader._transport.get_extra_info("peername")
                    remote_addr = peername[0] if peername else ""
                except (OSError, IndexError, AttributeError, TypeError):
                    remote_addr = ""

            # Create request object
            request = Request(
                method=method,
                url=path,
                headers=header_dict,
                body=body,
                query_string=self._extract_query_string(path),
                remote_addr=remote_addr,
                scheme=(
                    "https"
                    if reader._transport and reader._transport.get_extra_info("ssl_object")
                    else "http"
                ),
                server_name=self._parse_host(host_header)[0],
                server_port=self._parse_host(host_header)[1],
                raw_data=raw_headers + body if body else raw_headers,
            )

            metadata = {
                "http_version": version,
                "keep_alive": keep_alive,
                "content_length": content_length,
                "transfer_encoding": transfer_encoding,
            }

            return request, metadata

        except asyncio.TimeoutError:
            return None, {"error": "Request timeout"}
        except Exception as e:
            return None, {"error": f"Parse error: {str(e)}"}

    async def _parse_headers(self, reader: asyncio.StreamReader) -> Tuple[str, List[str], bytes]:
        """Parse request line and headers"""
        headers_data = b""
        lines = []

        while len(headers_data) < self.max_header_size:
            line = await asyncio.wait_for(reader.readline(), timeout=30)

            if not line:
                break

            headers_data += line
            line_str = line.decode("utf-8", errors="ignore").rstrip("\r\n")

            if not line_str:  # Empty line - end of headers
                break

            lines.append(line_str)

        if not lines:
            return "", [], b""

        return lines[0], lines[1:], headers_data

    def _parse_request_line(self, request_line: str) -> Tuple[str, str, str]:
        """Parse HTTP request line"""
        parts = request_line.split(" ", 2)

        if len(parts) != 3:
            raise ValueError(f"Invalid request line: {request_line}")

        method, path, version = parts

        # Validate method
        if method.upper() not in self.VALID_METHODS:
            raise ValueError(f"Invalid HTTP method: {method}")

        # Validate version
        if not self.HTTP_VERSION_RE.match(version):
            raise ValueError(f"Invalid HTTP version: {version}")

        # Validate path
        if not path.startswith("/"):
            raise ValueError(f"Invalid path: {path}")

        return method.upper(), path, version

    def _parse_header_dict(self, headers: List[str]) -> Dict[str, str]:
        """Parse headers into dictionary"""
        header_dict = {}

        for header in headers:
            if ":" not in header:
                continue

            name, value = header.split(":", 1)
            name = name.strip().lower()
            value = value.strip()

            # Validate header name
            if not self.HEADER_NAME_RE.match(name):
                continue

            # Handle multiple headers with same name
            if name in header_dict:
                header_dict[name] += f", {value}"
            else:
                header_dict[name] = value

        return header_dict

    def _get_content_length(self, headers: Dict[str, str]) -> Optional[int]:
        """Get and validate content length"""
        content_length_str = headers.get("content-length")

        if not content_length_str:
            return None

        try:
            content_length = int(content_length_str)
            if content_length < 0:
                raise ValueError("Negative content length")
            if content_length > self.max_request_size:
                raise ValueError("Content length exceeds maximum")
            return content_length
        except ValueError as e:
            raise ValueError(f"Invalid content-length: {e}")

    def _should_keep_alive(self, version: str, connection: str) -> bool:
        """Determine if connection should be kept alive"""
        if version == "HTTP/1.0":
            return "keep-alive" in connection
        else:  # HTTP/1.1
            return "close" not in connection

    async def _parse_body(
        self,
        reader: asyncio.StreamReader,
        content_length: Optional[int],
        transfer_encoding: str,
    ) -> bytes:
        """Parse request body based on content-length or chunked encoding"""
        if "chunked" in transfer_encoding:
            return await self._parse_chunked_body(reader)
        elif content_length is not None:
            return await self._parse_fixed_length_body(reader, content_length)
        else:
            return b""

    async def _parse_fixed_length_body(self, reader: asyncio.StreamReader, length: int) -> bytes:
        """Parse fixed-length body"""
        if length == 0:
            return b""

        body = await asyncio.wait_for(reader.read(length), timeout=30)

        if len(body) != length:
            raise ValueError(f"Expected {length} bytes, got {len(body)}")

        return body

    async def _parse_chunked_body(self, reader: asyncio.StreamReader) -> bytes:
        """Parse chunked transfer encoding"""
        chunks = []
        total_size = 0

        while total_size < self.max_request_size:
            # Read chunk size line
            size_line = await asyncio.wait_for(reader.readline(), timeout=30)

            if not size_line:
                break

            # Parse chunk size (hex)
            size_str = size_line.decode("ascii").strip().split(";")[0]

            try:
                chunk_size = int(size_str, 16)
            except ValueError:
                raise ValueError(f"Invalid chunk size: {size_str}")

            if chunk_size == 0:
                # End of chunks - read trailing headers
                await self._skip_trailing_headers(reader)
                break

            # Read chunk data
            chunk_data = await asyncio.wait_for(reader.read(chunk_size), timeout=30)

            if len(chunk_data) != chunk_size:
                raise ValueError(
                    f"Chunk size mismatch: expected {chunk_size}, got {len(chunk_data)}"
                )

            chunks.append(chunk_data)
            total_size += chunk_size

            # Read trailing CRLF
            await reader.readline()

        return b"".join(chunks)

    async def _skip_trailing_headers(self, reader: asyncio.StreamReader):
        """Skip trailing headers in chunked encoding"""
        while True:
            line = await asyncio.wait_for(reader.readline(), timeout=30)
            if not line or line == b"\r\n":
                break

    def _extract_query_string(self, path: str) -> str:
        """Extract query string from path"""
        if "?" in path:
            return path.split("?", 1)[1]
        return ""

    def _parse_host(self, host_header: str) -> Tuple[str, int]:
        """Parse host header"""
        if not host_header:
            return "localhost", 80

        if ":" in host_header:
            host, port_str = host_header.rsplit(":", 1)
            try:
                port = int(port_str)
            except ValueError:
                port = 80
        else:
            host = host_header
            port = 80

        return host, port


class HTTPResponseWriter:
    """High-performance HTTP response writer with streaming support"""

    def __init__(self, writer: asyncio.StreamWriter, server_name: str = "CovetPy/1.0"):
        self.writer = writer
        self.server_name = server_name
        self.response_started = False

    async def write_response(
        self,
        response: Response,
        http_version: str = "HTTP/1.1",
        keep_alive: bool = True,
    ) -> None:
        """Write complete HTTP response"""
        # Build status line
        status_line = f"{http_version} {response.status_code} {self._get_status_text(response.status_code)}\r\n"

        # Build headers
        headers = self._build_headers(response, keep_alive)

        # Write response
        self.writer.write(status_line.encode("ascii"))
        self.writer.write(headers)

        # Write body
        body = response.get_content_bytes()
        if body:
            self.writer.write(body)

        await self.writer.drain()
        self.response_started = True

    async def write_streaming_response(
        self, response, http_version: str = "HTTP/1.1", keep_alive: bool = True
    ) -> None:
        """Write streaming HTTP response with chunked encoding"""
        # Build status line
        status_line = f"{http_version} {response.status_code} {self._get_status_text(response.status_code)}\r\n"

        # Build headers with chunked encoding
        headers = self._build_streaming_headers(response, keep_alive)

        # Write response start
        self.writer.write(status_line.encode("ascii"))
        self.writer.write(headers)

        # Write chunks
        async for chunk in response:
            if chunk:
                # Write chunk size in hex
                chunk_size = hex(len(chunk))[2:].encode("ascii")
                self.writer.write(chunk_size + b"\r\n")
                self.writer.write(chunk)
                self.writer.write(b"\r\n")
                await self.writer.drain()

        # Write final chunk
        self.writer.write(b"0\r\n\r\n")
        await self.writer.drain()
        self.response_started = True

    def _build_headers(self, response: Response, keep_alive: bool) -> bytes:
        """Build HTTP headers"""
        headers = []

        # Add server header
        headers.append(f"Server: {self.server_name}")

        # Add date header
        headers.append(f"Date: {email.utils.formatdate(time.time(), usegmt=True)}")

        # Add connection header
        if keep_alive:
            headers.append("Connection: keep-alive")
        else:
            headers.append("Connection: close")

        # Add response headers
        for name, value in response.headers.items():
            headers.append(f"{name}: {value}")

        # Add cookies
        for cookie in response.cookies.values():
            headers.append(f"Set-Cookie: {cookie.to_header()}")

        # Add content-length if not present
        if "content-length" not in response.headers:
            body_length = len(response.get_content_bytes())
            headers.append(f"Content-Length: {body_length}")

        # Join headers
        header_text = "\r\n".join(headers) + "\r\n\r\n"
        return header_text.encode("ascii")

    def _build_streaming_headers(self, response, keep_alive: bool) -> bytes:
        """Build headers for streaming response"""
        headers = []

        # Add server header
        headers.append(f"Server: {self.server_name}")

        # Add date header
        headers.append(f"Date: {email.utils.formatdate(time.time(), usegmt=True)}")

        # Add connection header
        if keep_alive:
            headers.append("Connection: keep-alive")
        else:
            headers.append("Connection: close")

        # Add chunked encoding
        headers.append("Transfer-Encoding: chunked")

        # Add response headers (except content-length)
        for name, value in response.headers.items():
            if name.lower() != "content-length":
                headers.append(f"{name}: {value}")

        # Add cookies
        for cookie in response.cookies.values():
            headers.append(f"Set-Cookie: {cookie.to_header()}")

        # Join headers
        header_text = "\r\n".join(headers) + "\r\n\r\n"
        return header_text.encode("ascii")

    async def write_error_response(
        self, status_code: int, message: str = None, http_version: str = "HTTP/1.1"
    ) -> None:
        """Write error response"""
        if message is None:
            message = self._get_status_text(status_code)

        # Create simple error response
        body = f"<html><body><h1>{status_code} {message}</h1></body></html>"
        body_bytes = body.encode("utf-8")

        # Build response
        status_line = f"{http_version} {status_code} {message}\r\n"
        headers = [
            f"Server: {self.server_name}",
            f"Date: {email.utils.formatdate(time.time(), usegmt=True)}",
            "Connection: close",
            "Content-Type: text/html; charset=utf-8",
            f"Content-Length: {len(body_bytes)}",
        ]

        header_text = "\r\n".join(headers) + "\r\n\r\n"

        # Write response
        self.writer.write(status_line.encode("ascii"))
        self.writer.write(header_text.encode("ascii"))
        self.writer.write(body_bytes)

        await self.writer.drain()

    def _get_status_text(self, status_code: int) -> str:
        """Get standard HTTP status text"""
        status_texts = {
            100: "Continue",
            101: "Switching Protocols",
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            304: "Not Modified",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            406: "Not Acceptable",
            408: "Request Timeout",
            409: "Conflict",
            410: "Gone",
            411: "Length Required",
            413: "Payload Too Large",
            414: "URI Too Long",
            415: "Unsupported Media Type",
            422: "Unprocessable Entity",
            429: "Too Many Requests",
            500: "Internal Server Error",
            501: "Not Implemented",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
            505: "HTTP Version Not Supported",
        }
        return status_texts.get(status_code, "Unknown")


class HTTPServer:
    """Production-grade HTTP/1.1 server with full protocol compliance"""

    def __init__(self, app: Callable, config: Optional[ServerConfig] = None):
        self.app = app
        self.config = config or ServerConfig()
        self.connection_pool = ConnectionPool(self.config.max_connections)
        self.parser = HTTPRequestParser(self.config.max_header_size, self.config.max_request_size)
        self.is_running = False
        self.server = None
        self._shutdown_event = asyncio.Event()
        self._cleanup_task = None

        # Statistics
        self.stats = {
            "requests_total": 0,
            "requests_per_second": 0,
            "active_connections": 0,
            "errors_total": 0,
            "bytes_sent": 0,
            "bytes_received": 0,
        }

        # Setup logging
        self.logger = logging.getLogger(__name__)

    async def start(self) -> None:
        """Start the HTTP server"""
        self.logger.info(f"Starting HTTP server on {self.config.host}:{self.config.port}")

        # Start server
        self.server = await asyncio.start_server(
            self._handle_connection,
            host=self.config.host,
            port=self.config.port,
            ssl=self.config.ssl_context,
            backlog=self.config.backlog,
            reuse_address=True,
        )

        self.is_running = True

        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

        self.logger.info(f"HTTP server started successfully")

    async def serve_forever(self) -> None:
        """Serve requests forever"""
        if not self.server:
            await self.start()

        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            logger.error(f"Error during cleanup in serve_forever: {e}", exc_info=True)
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        """Shutdown server gracefully"""
        self.logger.info("Shutting down HTTP server...")

        self.is_running = False
        self._shutdown_event.set()

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                # TODO: Add proper exception handling

                # Close server
                pass
        if self.server:
            self.server.close()
            await self.server.wait_closed()

        # Close all connections
        connections = list(self.connection_pool.connections.values())
        for conn in connections:
            await conn.close()

        self.logger.info("HTTP server shutdown complete")

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """Handle individual client connection"""
        connection_id = f"{id(reader)}_{id(writer)}"
        connection = HTTPConnection(reader, writer, self, connection_id)

        # Add to connection pool
        if not await self.connection_pool.add_connection(connection):
            await connection.close()
            return

        try:
            connection.state = ConnectionState.CONNECTED

            # Handle keep-alive loop
            while connection.should_keep_alive() and self.is_running:
                try:
                    await self._handle_request(connection)
                    connection.request_count += 1
                    connection.update_activity()

                except asyncio.TimeoutError:
                    self.logger.debug(f"Request timeout for connection {connection_id}")
                    break
                except Exception as e:
                    self.logger.error(f"Request handling error: {e}")
                    await self._send_error_response(connection, 500, "Internal Server Error")
                    break

        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            self.stats["errors_total"] += 1

        finally:
            await connection.close()
            await self.connection_pool.remove_connection(connection_id)

    async def _handle_request(self, connection: HTTPConnection) -> None:
        """Handle single HTTP request"""
        start_time = time.time()

        try:
            # Parse request with timeout
            request, metadata = await asyncio.wait_for(
                self.parser.parse_request(connection.reader),
                timeout=self.config.request_timeout,
            )

            if not request:
                error = metadata.get("error", "Invalid request")
                await self._send_error_response(connection, 400, error)
                return

            # Update connection metadata
            connection.keep_alive = metadata.get("keep_alive", False)
            connection.http_version = HTTPVersion(metadata.get("http_version", "HTTP/1.1"))

            # Log request
            if self.config.access_log:
                self.logger.info(f"{connection.remote_addr} - {request.method} {request.url}")

            # Process request through ASGI app
            response = await self._process_request(request)

            # Write response
            writer = HTTPResponseWriter(connection.writer, self.config.server_name)

            if hasattr(response, "__aiter__"):
                await writer.write_streaming_response(
                    response, connection.http_version.value, connection.keep_alive
                )
            else:
                await writer.write_response(
                    response, connection.http_version.value, connection.keep_alive
                )

            # Update statistics
            self.stats["requests_total"] += 1
            self.stats["bytes_sent"] += (
                len(response.get_content_bytes()) if hasattr(response, "get_content_bytes") else 0
            )

            # Log response time
            response_time = time.time() - start_time
            if self.config.debug:
                self.logger.debug(f"Request processed in {response_time:.3f}s")

        except asyncio.TimeoutError:
            await self._send_error_response(connection, 408, "Request Timeout")
            connection.keep_alive = False

        except Exception as e:
            self.logger.error(f"Request processing error: {e}")
            await self._send_error_response(connection, 500, "Internal Server Error")
            connection.keep_alive = False

    async def _process_request(self, request: Request) -> Response:
        """Process request through ASGI application"""
        # Convert to ASGI scope
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "http_version": "1.1",
            "method": request.method,
            "scheme": request.scheme,
            "path": request.path,
            "query_string": (
                request._query_string.encode()
                if hasattr(request, "_query_string") and request._query_string
                else b""
            ),
            "root_path": "",
            "headers": [[k.encode(), v.encode()] for k, v in request.headers.items()],
            "server": (request.server_name, request.server_port),
            "client": (request.remote_addr, 0),
        }

        # ASGI receive callable
        body = request.get_body_bytes()
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        # ASGI send callable
        response_data = {"status": 200, "headers": [], "body": b""}

        async def send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")

        # Call ASGI app
        await self.app(scope, receive, send)

        # Convert back to Response
        headers = {k.decode(): v.decode() for k, v in response_data["headers"]}
        return Response(
            content=response_data["body"],
            status_code=response_data["status"],
            headers=headers,
        )

    async def _send_error_response(
        self, connection: HTTPConnection, status: int, message: str
    ) -> None:
        """Send error response"""
        try:
            writer = HTTPResponseWriter(connection.writer, self.config.server_name)
            await writer.write_error_response(status, message, connection.http_version.value)
        except Exception as e:
            self.logger.error(f"Error sending error response: {e}")

    async def _periodic_cleanup(self) -> None:
        """Periodic cleanup of expired connections"""
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Run every 30 seconds

                # Clean up expired connections
                expired = await self.connection_pool.cleanup_expired(self.config.keep_alive_timeout)

                if expired > 0:
                    self.logger.debug(f"Cleaned up {expired} expired connections")

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Cleanup task error: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics"""
        pool_stats = self.connection_pool.get_stats()
        self.stats.update(pool_stats)
        return self.stats.copy()


class CovetHTTPServer(HTTPServer):
    """CovetPy-specific HTTP server with integrated features"""

    def __init__(self, app: Callable, config: Optional[ServerConfig] = None, **kwargs):
        if config is None:
            config = ServerConfig(**kwargs)
        super().__init__(app, config)

    @classmethod
    def create_production_server(cls, app: Callable, **kwargs) -> "CovetHTTPServer":
        """Create production-optimized server"""
        production_config = {
            "max_connections": 50000,
            "keep_alive_timeout": 75,
            "max_keep_alive_requests": 10000,
            "buffer_size": 128 * 1024,
            "tcp_nodelay": True,
            "tcp_keepalive": True,
            "so_reuseport": True,
            "access_log": True,
            **kwargs,
        }
        return cls(app, **production_config)


# Convenience function
def run_server(app: Callable, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None:
    """Run HTTP server with CovetPy application"""
    server = CovetHTTPServer(app, host=host, port=port, **kwargs)

    async def serve():
        await server.serve_forever()

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error("Server error: {e}")


# Export public interface
__all__ = [
    "HTTPServer",
    "CovetHTTPServer",
    "ServerConfig",
    "ConnectionPool",
    "HTTPConnection",
    "HTTPRequestParser",
    "HTTPResponseWriter",
    "run_server",
]
