"""
Pure CovetPy Built-in ASGI Server
Zero-dependency HTTP server for development and lightweight production use
"""

import asyncio
import logging
import socket
import ssl
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .asgi import CovetPyASGI as CovetASGI

logger = logging.getLogger(__name__)


class CovetServer:
    """
    Built-in ASGI server for CovetPy applications.

    Provides a zero-dependency server for development and lightweight production use.
    For production workloads, it's recommended to use uvicorn, gunicorn, or similar.
    """

    def __init__(
        self,
        app,
        host: str = "127.0.0.1",
        port: int = 8000,
        ssl_context: Optional[ssl.SSLContext] = None,
        access_log: bool = True,
        debug: bool = False,
        **kwargs,
    ) -> None:
        """Initialize the CovetPy server."""
        self.app = app
        self.host = host
        self.port = port
        self.ssl_context = ssl_context
        self.access_log = access_log
        self.debug = debug
        self.config = kwargs

        self._server = None
        self._is_running = False

    async def serve(self) -> Any:
        """Start serving the application."""
        logger.info("Starting CovetPy server on {self.host}:{self.port}")

        if self.ssl_context:
            logger.info("SSL/TLS enabled")

        if self.debug:
            logger.debug("Debug mode enabled")

        try:
            self._server = await asyncio.start_server(
                self._handle_connection,
                self.host,
                self.port,
                ssl=self.ssl_context,
                reuse_port=True,
            )

            self._is_running = True

            addrs = ", ".join(str(sock.getsockname()) for sock in self._server.sockets)
            logger.info("CovetPy server running on {addrs}")

            async with self._server:
                await self._server.serve_forever()

        except KeyboardInterrupt:
            logger.info("\nShutting down CovetPy server...")
        except Exception as e:
            logger.error("Server error: {e}")
        finally:
            self._is_running = False

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> Any:
        """Handle individual client connections"""
        client_addr = writer.get_extra_info("peername")

        try:
            # Read HTTP request
            request_data = await self._read_http_request(reader)

            if not request_data:
                return

            # Parse the request line to determine if it's HTTP
            if (
                not request_data.startswith(b"GET ")
                and not request_data.startswith(b"POST ")
                and not request_data.startswith(b"PUT ")
                and not request_data.startswith(b"PATCH ")
                and not request_data.startswith(b"DELETE ")
                and not request_data.startswith(b"HEAD ")
                and not request_data.startswith(b"OPTIONS ")
            ):
                await self._send_bad_request(writer)
                return

            # Create ASGI scope from HTTP request
            scope = await self._create_scope_from_http(request_data, client_addr, writer)

            if scope:
                # Create ASGI receive/send callables
                receive = self._create_receive(request_data)
                send = self._create_send(writer)

                # Process through ASGI application
                await self.app(scope, receive, send)

        except asyncio.CancelledError:
            logger.error(f"Error in _handle_connection: {e}", exc_info=True)
        except Exception as e:
            if self.debug:
                logger.error("Connection error from {client_addr}: {e}")

            try:
                await self._send_internal_error(writer)
            except Exception:
                logger.error(f"Resource error in _handle_connection: {e}", exc_info=True)
                # Continue cleanup despite error
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                # TODO: Add proper exception handling

                pass

    async def _read_http_request(self, reader: asyncio.StreamReader) -> bytes:
        """Read HTTP request from client"""
        try:
            # Read request line and headers
            request_lines = []

            while True:
                line = await asyncio.wait_for(reader.readline(), timeout=10.0)

                if not line:
                    break

                request_lines.append(line)

                # End of headers
                if line == b"\r\n":
                    break

            if not request_lines:
                return b""

            # Parse Content-Length for body
            headers_section = b"".join(request_lines)
            content_length = 0

            for line in request_lines:
                if line.lower().startswith(b"content-length:"):
                    try:
                        content_length = int(line.split(b":", 1)[1].strip())
                    except (ValueError, IndexError):
                        content_length = 0
                    break

            # Read body if present
            body = b""
            if content_length > 0:
                body = await asyncio.wait_for(reader.read(content_length), timeout=30.0)

            return headers_section + body

        except asyncio.TimeoutError:
            return b""
        except Exception:
            return b""

    async def _create_scope_from_http(
        self, request_data: bytes, client_addr: tuple, writer: asyncio.StreamWriter
    ) -> Optional[Dict[str, Any]]:
        """Create ASGI scope from HTTP request data"""
        try:
            # Split headers and body
            if b"\r\n\r\n" in request_data:
                headers_part, body_part = request_data.split(b"\r\n\r\n", 1)
            else:
                headers_part = request_data
                body_part = b""

            lines = headers_part.split(b"\r\n")

            if not lines:
                return None

            # Parse request line
            request_line = lines[0]
            parts = request_line.split(b" ")

            if len(parts) < 2:
                return None

            method = parts[0].decode("ascii")
            path_with_query = parts[1].decode("ascii")

            # Split path and query
            if "?" in path_with_query:
                path, query_string = path_with_query.split("?", 1)
            else:
                path = path_with_query
                query_string = ""

            # Parse headers
            headers = []
            for line in lines[1:]:
                if b":" in line:
                    name, value = line.split(b":", 1)
                    headers.append([name.strip(), value.strip()])

            # Determine server info
            server_name = self.host
            server_port = self.port

            # Override with Host header if present
            for name, value in headers:
                if name.lower() == b"host":
                    host_header = value.decode("ascii")
                    if ":" in host_header:
                        server_name, port_str = host_header.split(":", 1)
                        try:
                            server_port = int(port_str)
                        except ValueError:
                            logger.error(f"Error in operation: {e}", exc_info=True)
                    else:
                        server_name = host_header
                    break

            # Create ASGI scope
            scope = {
                "type": "http",
                "asgi": {"version": "3.0", "spec_version": "2.1"},
                "http_version": "1.1",
                "method": method,
                "scheme": "https" if self.ssl_context else "http",
                "path": path,
                "query_string": query_string.encode("ascii"),
                "root_path": "",
                "headers": headers,
                "server": (server_name, server_port),
                "client": client_addr,
            }

            return scope

        except Exception as e:
            if self.debug:
                logger.error("Error creating scope: {e}")
            return None

    def _create_receive(self, request_data: bytes) -> Callable:
        """Create ASGI receive callable"""
        # Extract body from request data
        if b"\r\n\r\n" in request_data:
            _, body = request_data.split(b"\r\n\r\n", 1)
        else:
            body = b""

        sent_body = False

        async def receive() -> Any:
            nonlocal sent_body

            if not sent_body:
                sent_body = True
                return {"type": "http.request", "body": body, "more_body": False}
            else:
                # No more body data
                return {"type": "http.disconnect"}

        return receive

    def _create_send(self, writer: asyncio.StreamWriter) -> Callable:
        """Create ASGI send callable"""
        response_started = False

        async def send(message: Dict[str, Any]) -> Any:
            nonlocal response_started

            if message["type"] == "http.response.start":
                response_started = True

                status = message["status"]
                headers = message.get("headers", [])

                # Write status line
                status_line = f"HTTP/1.1 {status} {self._get_status_text(status)}\r\n"
                writer.write(status_line.encode("ascii"))

                # Write headers
                for name, value in headers:
                    if isinstance(name, bytes):
                        name = name.decode("ascii")
                    if isinstance(value, bytes):
                        value = value.decode("ascii")

                    writer.write(f"{name}: {value}\r\n".encode("ascii"))

                # End of headers
                writer.write(b"\r\n")

            elif message["type"] == "http.response.body":
                if not response_started:
                    # Send default response start
                    await send({"type": "http.response.start", "status": 200, "headers": []})

                body = message.get("body", b"")
                if body:
                    writer.write(body)

                # Flush and close if this is the last chunk
                if not message.get("more_body", False):
                    await writer.drain()

        return send

    def _get_status_text(self, status_code: int) -> str:
        """Get HTTP status text for status code"""
        status_texts = {
            200: "OK",
            201: "Created",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            422: "Unprocessable Entity",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return status_texts.get(status_code, "Unknown")

    async def _send_bad_request(self, writer: asyncio.StreamWriter) -> Any:
        """Send 400 Bad Request response"""
        response = (
            b"HTTP/1.1 400 Bad Request\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 11\r\n"
            b"\r\n"
            b"Bad Request"
        )

        writer.write(response)
        await writer.drain()

    async def _send_internal_error(self, writer: asyncio.StreamWriter) -> Any:
        """Send 500 Internal Server Error response"""
        response = (
            b"HTTP/1.1 500 Internal Server Error\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 21\r\n"
            b"\r\n"
            b"Internal Server Error"
        )

        writer.write(response)
        await writer.drain()

    async def stop(self) -> Any:
        """Stop the server"""
        if self._server and self._is_running:
            self._server.close()
            await self._server.wait_closed()
            self._is_running = False
            logger.info("CovetPy server stopped")


def run_server(app, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> Any:
    """Run CovetPy application with built-in server"""
    server = CovetServer(app, host=host, port=port, **kwargs)

    try:
        asyncio.run(server.serve())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error("Server error: {e}")
