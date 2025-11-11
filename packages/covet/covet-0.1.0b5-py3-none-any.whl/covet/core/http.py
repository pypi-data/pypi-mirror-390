"""
CovetPy High-Performance HTTP Request/Response System
Zero-copy optimizations, streaming support, and efficient parsing
"""

import io
import json
import urllib.parse
import weakref
from collections.abc import AsyncGenerator, AsyncIterator, Generator
from typing import (
    Any,
    Callable,
    Optional,
    Union,
)
from urllib.parse import parse_qs, unquote_plus

# Optional brotli compression support
try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    brotli = None
    HAS_BROTLI = False


# Advanced buffer pool for reduced allocation overhead
class BufferPool:
    """High-performance buffer pool with tiered sizing for buffer reuse"""

    def __init__(
        self,
        small_size: int = 4096,
        medium_size: int = 8192,
        large_size: int = 65536,
        max_buffers_per_size: int = 1000,
        alignment: int = 64,  # Deprecated parameter, kept for backward compatibility
    ) -> None:
        # Note: alignment parameter is deprecated and not used.
        # Buffer alignment is not needed for pure Python operations.
        # Rust extensions handle their own memory alignment through PyO3.
        self.alignment = alignment  # Kept for backward compatibility
        self.buffer_sizes = [small_size, medium_size, large_size]
        self.max_buffers = max_buffers_per_size

        # Separate pools for different buffer sizes
        self._pools = {small_size: [], medium_size: [], large_size: []}
        self._in_use = weakref.WeakSet()

        # Pre-allocate some buffers for hot path
        self._preallocate_buffers()

    def _preallocate_buffers(self) -> None:
        """Pre-allocate buffers for immediate availability"""
        for size in self.buffer_sizes:
            for _ in range(min(100, self.max_buffers // 2)):
                buffer = self._create_aligned_buffer(size)
                self._pools[size].append(buffer)

    def _create_aligned_buffer(self, size: int) -> bytearray:
        """Create a buffer for HTTP operations.

        Note: Buffer alignment is not required for pure Python operations.
        The buffers are used internally for HTTP parsing and are not passed
        to Rust extensions. Rust extensions manage their own memory through
        PyO3 with Vec<u8> and handle alignment internally if needed.

        Args:
            size: The size of the buffer to create

        Returns:
            A new bytearray buffer of the specified size
        """
        # Simple buffer creation - alignment not needed for Python usage
        return bytearray(size)

    def get_buffer(self, min_size: int = 8192) -> bytearray:
        """Get optimally-sized buffer from pool"""
        # Find smallest buffer that meets size requirement
        chosen_size = next(
            (size for size in self.buffer_sizes if size >= min_size),
            self.buffer_sizes[-1],
        )

        pool = self._pools[chosen_size]
        if pool:
            buffer = pool.pop()
        else:
            buffer = self._create_aligned_buffer(chosen_size)

        self._in_use.add(buffer)
        return buffer

    def return_buffer(self, buffer: bytearray) -> None:
        """Return a buffer to appropriate pool"""
        if buffer not in self._in_use:
            return

        buffer_size = len(buffer)
        if buffer_size in self._pools:
            pool = self._pools[buffer_size]
            if len(pool) < self.max_buffers:
                # Clear buffer efficiently and return to pool
                buffer[:] = b""
                pool.append(buffer)

        self._in_use.discard(buffer)


# Global optimized buffer pool
_buffer_pool = BufferPool(
    small_size=4096,
    medium_size=8192,
    large_size=65536,
    max_buffers_per_size=2000,
    alignment=64,
)


class CaseInsensitiveDict(dict):
    """Optimized case-insensitive dictionary for HTTP headers with O(1) lookup"""

    __slots__ = ("_key_map", "_lower_cache")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self._key_map = {}  # Maps lowercase keys to original case keys
        self._lower_cache = {}  # Cache for lowercased keys to avoid repeated str.lower()

        if args:
            if len(args) > 1:
                raise TypeError(
                    "CaseInsensitiveDict expected at most 1 argument, got %d" % len(args)
                )
            self.update(args[0])

        self.update(kwargs)

    def _get_lower_key(self, key: str) -> str:
        """Get cached lowercase key to avoid repeated computation"""
        if key not in self._lower_cache:
            self._lower_cache[key] = key.lower()
        return self._lower_cache[key]

    def __setitem__(self, key: str, value: str) -> None:
        lower_key = self._get_lower_key(key)

        # Remove old entry if exists
        if lower_key in self._key_map:
            old_key = self._key_map[lower_key]
            if old_key in super().keys():
                super().__delitem__(old_key)

        # Set new entry
        self._key_map[lower_key] = key
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        lower_key = self._get_lower_key(key)
        return super().__getitem__(self._key_map.get(lower_key, key))

    def __delitem__(self, key: str) -> None:
        lower_key = self._get_lower_key(key)
        if lower_key in self._key_map:
            actual_key = self._key_map[lower_key]
            del self._key_map[lower_key]
            # Remove from cache too
            self._lower_cache.pop(key, None)
            super().__delitem__(actual_key)
        else:
            super().__delitem__(key)

    def __contains__(self, key: str) -> bool:
        lower_key = self._get_lower_key(key)
        return lower_key in self._key_map or super().__contains__(key)

    def get(self, key: str, default: Any = None) -> Any:
        """Get header value with case-insensitive lookup"""
        lower_key = self._get_lower_key(key)
        if lower_key in self._key_map:
            return super().__getitem__(self._key_map[lower_key])
        return default

    def update(self, other: Any) -> None:
        """Update with another dict"""
        if hasattr(other, "items"):
            for key, value in other.items():
                self[key] = value
        else:
            for key, value in other:
                self[key] = value


class LazyQueryParser:
    """Lazy query string parser for zero-copy optimization"""

    def __init__(self, query_string: str) -> None:
        self._query_string = query_string
        self._parsed = None
        self._cache = {}

    @property
    def parsed(self) -> dict[str, list[str]]:
        """Parse query string on first access"""
        if self._parsed is None:
            self._parsed = parse_qs(self._query_string, keep_blank_values=True)
        return self._parsed

    def get(self, key: str, default=None) -> Optional[str]:
        """Get first value for key"""
        if key in self._cache:
            return self._cache[key]

        values = self.parsed.get(key, [])
        result = values[0] if values else default
        self._cache[key] = result
        return result

    def get_list(self, key: str) -> list[str]:
        """Get all values for key"""
        return self.parsed.get(key, [])

    def __contains__(self, key: str) -> bool:
        return key in self.parsed

    def __getitem__(self, key: str) -> Optional[str]:
        return self.get(key)

    def items(self) -> Generator[tuple[str, str], None, None]:
        """Iterate over all key-value pairs"""
        for key, values in self.parsed.items():
            for value in values:
                yield key, value


class StreamingBody:
    """Streaming request body with efficient reading"""

    def __init__(self, stream: AsyncIterator[bytes], content_length: Optional[int] = None) -> None:
        self._stream = stream
        self._content_length = content_length
        self._consumed = False
        self._buffer = io.BytesIO()
        self._position = 0

    @property
    def content_length(self) -> Optional[int]:
        """
        Get the content length of the streaming body.

        Returns:
            Content length in bytes, or None if not specified
        """
        return self._content_length

    async def read(self, size: int = -1) -> bytes:
        """Read bytes from stream"""
        if self._consumed:
            return b""

        if size == -1:
            # Read all remaining data
            chunks = []
            async for chunk in self._stream:
                chunks.append(chunk)
            self._consumed = True
            return b"".join(chunks)

        # Read specific amount
        data = b""
        remaining = size

        async for chunk in self._stream:
            if remaining <= 0:
                break

            if len(chunk) <= remaining:
                data += chunk
                remaining -= len(chunk)
            else:
                data += chunk[:remaining]
                # Put back unused portion (simplified implementation)
                remaining = 0

        if remaining > 0:
            self._consumed = True

        return data

    async def read_line(self) -> bytes:
        """Read a line from stream.

        Uses bytearray for O(n) performance instead of O(n²).
        The original implementation using `line += bytes([byte])` created
        a new bytes object on each iteration, resulting in quadratic time
        complexity due to immutable string concatenation.

        This optimized version uses a mutable bytearray which allows
        O(1) amortized append operations, resulting in O(n) total complexity.
        """
        line = bytearray()
        async for chunk in self._stream:
            for byte in chunk:
                line.append(byte)
                if byte == ord("\n"):
                    return bytes(line)
        return bytes(line)

    async def json(self) -> Any:
        """Parse body as JSON"""
        data = await self.read()
        return json.loads(data.decode("utf-8"))

    async def text(self, encoding: str = "utf-8") -> str:
        """Get body as text"""
        data = await self.read()
        return data.decode(encoding)

    async def form(self) -> dict[str, list[str]]:
        """Parse body as form data"""
        data = await self.text()
        return parse_qs(data, keep_blank_values=True)


class Request:
    """Ultra-high-performance HTTP request with advanced zero-copy optimization"""

    __slots__ = (
        "method",
        "url",
        "scheme",
        "server_name",
        "server_port",
        "remote_addr",
        "headers",
        "_url_parts",
        "_path",
        "_query_string",
        "_query",
        "_body",
        "_form_cache",
        "_json_cache",
        "_cookies_cache",
        "path_params",
        "context",
        "_request_id",
        "_raw_data",
        "_parse_state",
        "_buffer_pool",
        "scope",
        "_receive",
    )

    def __init__(
        self,
        scope: dict = None,
        receive: Callable = None,
        method: str = None,
        url: str = None,
        headers: dict[str, str] = None,
        body: Union[bytes, StreamingBody] = None,
        query_string: str = "",
        path_params: dict[str, Any] = None,
        remote_addr: str = "",
        scheme: str = "http",
        server_name: str = "",
        server_port: int = 80,
        raw_data: bytes = None,
        buffer_pool: BufferPool = None,
    ) -> None:
        """
        Initialize HTTP Request object with ASGI support.

        ASGI Integration (Primary Usage):
            The constructor is designed for ASGI compliance, where `scope` is the
            primary parameter containing all request metadata. When `scope` is provided,
            request attributes are extracted from it automatically.

        Args:
            scope: ASGI scope dictionary containing request metadata (type, method, path,
                   headers, etc.). This is the primary parameter for ASGI integration.
                   If provided, other parameters are ignored in favor of scope values.
            receive: ASGI receive callable for reading request body asynchronously.
                     Required for streaming body support in ASGI applications.
            method: HTTP method (GET, POST, etc.). Used when constructing Request
                    manually (non-ASGI). Defaults to 'GET' if not specified.
            url: Request URL path. Used for manual construction or testing.
            headers: HTTP headers dictionary. Case-insensitive access supported.
            body: Request body as bytes or StreamingBody for lazy loading.
            query_string: URL query string (without '?'). Parsed lazily on access.
            path_params: Path parameters extracted by router (e.g., {id} from /users/{id}).
            remote_addr: Client IP address.
            scheme: URL scheme ('http' or 'https'). Default: 'http'.
            server_name: Server hostname. Default: ''.
            server_port: Server port number. Default: 80.
            raw_data: Raw HTTP request bytes for zero-copy parsing via from_bytes().
            buffer_pool: Custom BufferPool instance for memory optimization.

        Example (ASGI Usage):
            >>> # ASGI application receiving scope
            >>> async def app(scope, receive, send):
            ...     request = Request(scope=scope, receive=receive)
            ...     # Request attributes extracted from scope automatically
            ...     print(request.method, request.path)

        Example (Manual Usage):
            >>> # Direct instantiation for testing or non-ASGI contexts
            >>> request = Request(
            ...     method='POST',
            ...     url='/api/users',
            ...     headers={'Content-Type': 'application/json'},
            ...     body=b'{"name": "John"}'
            ... )

        Note:
            - When scope is provided, it takes precedence over individual parameters
            - ASGI scope format: https://asgi.readthedocs.io/en/latest/specs/www.html
            - For zero-copy parsing from raw bytes, use Request.from_bytes() instead
        """
        # ASGI support - store scope and receive first
        self.scope = scope
        self._receive = receive

        # Extract values from ASGI scope if provided, otherwise use parameters
        if scope:
            # Extract method from ASGI scope
            self.method = scope.get("method", "GET").upper()

            # Extract URL path from scope
            self.url = scope.get("path", "/")

            # Extract query string from scope (bytes in ASGI)
            query_bytes = scope.get("query_string", b"")
            self._query_string = query_bytes.decode("latin1") if isinstance(query_bytes, bytes) else query_bytes

            # Extract scheme from scope
            self.scheme = scope.get("scheme", "http")

            # Extract server info from scope
            server = scope.get("server", ("", 80))
            self.server_name = server[0] if server else ""
            self.server_port = server[1] if server and len(server) > 1 else 80

            # Extract client info from scope
            client = scope.get("client", ("", 0))
            self.remote_addr = client[0] if client else ""

            # Extract headers from ASGI scope (list of 2-tuples of byte strings)
            headers_dict = {}
            for header_name, header_value in scope.get("headers", []):
                name = header_name.decode("latin1") if isinstance(header_name, bytes) else header_name
                value = header_value.decode("latin1") if isinstance(header_value, bytes) else header_value
                headers_dict[name] = value
            self.headers = CaseInsensitiveDict(headers_dict)

            # Body handling - use receive callable for ASGI
            self._body = body  # May be None, will use _receive to get body on demand

        else:
            # Non-ASGI mode: use provided parameters
            self.method = method.upper() if method else "GET"
            self.url = url or "/"
            self.scheme = scheme
            self.server_name = server_name
            self.server_port = server_port
            self.remote_addr = remote_addr
            self.headers = CaseInsensitiveDict(headers or {})
            self._query_string = query_string
            self._body = body

        # Path and query parsing (lazy)
        self._url_parts = None
        self._path = None
        self._query = None

        # Body caches
        self._form_cache = None
        self._json_cache = None
        self._cookies_cache = None

        # Path parameters from routing
        self.path_params = path_params or {}

        # Request context for DI and middleware
        self.context = {}
        self._request_id = None

        # Zero-copy optimization support
        self._raw_data = raw_data
        self._parse_state = {"parsed": False}
        self._buffer_pool = buffer_pool or _buffer_pool

    @classmethod
    def from_bytes(cls, data: bytes, buffer_pool: BufferPool = None) -> "Request":
        """Create Request from raw HTTP bytes with zero-copy parsing"""
        request = cls(raw_data=data, buffer_pool=buffer_pool)
        request._parse_http_request()
        return request

    def _parse_http_request(self):
        """Parse HTTP request with zero-copy techniques where possible"""
        if self._parse_state["parsed"] or not self._raw_data:
            return

        # Find end of headers efficiently
        header_end = self._raw_data.find(b"\r\n\r\n")
        if header_end == -1:
            raise ValueError("Invalid HTTP request: no header termination")

        # Parse request line and headers (zero-copy where possible)
        headers_section = self._raw_data[:header_end]
        body_section = (
            self._raw_data[header_end + 4 :] if header_end + 4 < len(self._raw_data) else b""
        )

        # Parse request line
        lines = headers_section.split(b"\r\n")
        if not lines:
            raise ValueError("Invalid HTTP request: no request line")

        request_line = lines[0]
        parts = request_line.split(b" ", 2)
        if len(parts) < 2:
            raise ValueError("Invalid HTTP request line")

        self.method = parts[0].decode("ascii")
        url_with_query = parts[1].decode("ascii")

        # Parse URL and query string
        if "?" in url_with_query:
            self.url, self._query_string = url_with_query.split("?", 1)
        else:
            self.url = url_with_query
            self._query_string = ""

        # Parse headers efficiently
        headers = {}
        for line in lines[1:]:
            if b":" in line:
                key, value = line.split(b":", 1)
                headers[key.decode("ascii").strip().lower()] = value.decode("ascii").strip()

        self.headers = CaseInsensitiveDict(headers)

        # Handle body
        if body_section:
            content_length = int(self.headers.get("content-length", 0))
            if content_length > 0:
                self._body = body_section[:content_length]
            else:
                self._body = body_section

        self._parse_state["parsed"] = True

    @property
    def path(self) -> str:
        """Get request path (lazy parsed)"""
        if self._path is None:
            parsed = urllib.parse.urlparse(self.url)
            self._path = parsed.path
        return self._path

    @property
    def query(self) -> LazyQueryParser:
        """Get query parameters (lazy parsed)"""
        if self._query is None:
            self._query = LazyQueryParser(self._query_string)
        return self._query

    @property
    def body(self) -> StreamingBody:
        """Get request body with optimized handling"""
        if isinstance(self._body, StreamingBody):
            return self._body
        elif isinstance(self._body, bytes):
            # Convert bytes to streaming body with zero-copy where possible
            async def byte_stream():
                # Use memory view for zero-copy
                yield memoryview(self._body).tobytes()

            return StreamingBody(byte_stream(), len(self._body))
        else:
            # Empty body
            async def empty_stream():
                return
                yield  # Make it a generator

            return StreamingBody(empty_stream(), 0)

    def get_body_bytes(self) -> bytes:
        """Get body as bytes directly (zero-copy when possible)"""
        if isinstance(self._body, bytes):
            return self._body
        return b""

    @property
    def content_type(self) -> str:
        """Get content type"""
        return self.headers.get("content-type", "")

    @property
    def content_length(self) -> Optional[int]:
        """Get content length"""
        length = self.headers.get("content-length")
        return int(length) if length else None

    @property
    def request_id(self) -> str:
        """Get or generate request ID"""
        if self._request_id is None:
            import uuid

            self._request_id = str(uuid.uuid4())
        return self._request_id

    def is_json(self) -> bool:
        """Check if request has JSON content type"""
        content_type = self.content_type.lower()
        return "application/json" in content_type

    def is_form(self) -> bool:
        """Check if request is form data"""
        content_type = self.content_type.lower()
        return "application/x-www-form-urlencoded" in content_type

    def is_multipart(self) -> bool:
        """Check if request is multipart form data"""
        content_type = self.content_type.lower()
        return "multipart/form-data" in content_type

    def is_websocket(self) -> bool:
        """Check if this is a WebSocket upgrade request"""
        return (
            self.headers.get("upgrade", "").lower() == "websocket"
            and "upgrade" in self.headers.get("connection", "").lower()
        )

    def accepts(self, content_type: str) -> bool:
        """Check if client accepts content type"""
        accept_header = self.headers.get("accept", "*/*")
        # Simplified accept checking
        return content_type in accept_header or "*/*" in accept_header

    async def json(self) -> Any:
        """Parse request body as JSON (cached with optimized parsing)"""
        if self._json_cache is None:
            if isinstance(self._body, bytes):
                # Direct parsing from bytes for better performance
                import json

                self._json_cache = json.loads(self._body.decode("utf-8"))
            elif self._receive:
                # Get body from ASGI receive
                body_parts = []
                while True:
                    message = await self._receive()
                    if message["type"] == "http.request":
                        body_parts.append(message.get("body", b""))
                        if not message.get("more_body", False):
                            break
                    elif message["type"] == "http.disconnect":
                        break

                body_data = b"".join(body_parts)
                if body_data:
                    import json

                    self._json_cache = json.loads(body_data.decode("utf-8"))
                else:
                    self._json_cache = {}
            else:
                self._json_cache = await self.body.json()
        return self._json_cache

    async def form(self) -> dict[str, list[str]]:
        """Parse request body as form data (cached)"""
        if self._form_cache is None:
            self._form_cache = await self.body.form()
        return self._form_cache

    def cookies(self) -> dict[str, str]:
        """Parse cookies from headers (cached)"""
        if self._cookies_cache is None:
            self._cookies_cache = {}
            cookie_header = self.headers.get("cookie", "")
            if cookie_header:
                for part in cookie_header.split(";"):
                    if "=" in part:
                        key, value = part.strip().split("=", 1)
                        self._cookies_cache[key] = unquote_plus(value)

        return self._cookies_cache

    def get_header(self, name: str, default: str = None) -> Optional[str]:
        """Get header with default value"""
        return self.headers.get(name, default)

    def has_header(self, name: str) -> bool:
        """Check if header exists"""
        return name in self.headers


class Cookie:
    """HTTP Cookie with security attributes"""

    def __init__(
        self,
        name: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[str] = None,
    ) -> None:
        self.name = name
        self.value = value
        self.max_age = max_age
        self.expires = expires
        self.path = path
        self.domain = domain
        self.secure = secure
        self.http_only = http_only
        self.same_site = same_site

    def to_header(self) -> str:
        """Convert cookie to Set-Cookie header value"""
        header_parts = [f"{self.name}={self.value}"]

        if self.max_age is not None:
            header_parts.append(f"Max-Age={self.max_age}")

        if self.expires:
            header_parts.append(f"Expires={self.expires}")

        if self.path:
            header_parts.append(f"Path={self.path}")

        if self.domain:
            header_parts.append(f"Domain={self.domain}")

        if self.secure:
            header_parts.append("Secure")

        if self.http_only:
            header_parts.append("HttpOnly")

        if self.same_site:
            header_parts.append(f"SameSite={self.same_site}")

        return "; ".join(header_parts)


class StreamingResponse:
    """Streaming HTTP response for efficient data transfer"""

    def __init__(
        self,
        content: Union[str, bytes, AsyncGenerator, Generator] = "",
        status_code: int = 200,
        headers: dict[str, str] = None,
        media_type: str = "text/plain",
        charset: str = "utf-8",
    ) -> None:
        self.status_code = status_code
        self.media_type = media_type
        self.charset = charset

        # Headers with case-insensitive access
        self.headers = CaseInsensitiveDict(headers or {})
        self.cookies = {}

        # Content handling
        self._content = content
        self._body_iterator = None

        # Set default headers
        if "content-type" not in self.headers:
            if media_type.startswith("text/"):
                self.headers["content-type"] = f"{media_type}; charset={charset}"
            else:
                self.headers["content-type"] = media_type

    def set_cookie(
        self,
        name: str,
        value: str,
        max_age: Optional[int] = None,
        expires: Optional[str] = None,
        path: str = "/",
        domain: Optional[str] = None,
        secure: bool = False,
        http_only: bool = False,
        same_site: Optional[str] = None,
    ) -> None:
        """Set a cookie"""
        cookie = Cookie(
            name=name,
            value=value,
            max_age=max_age,
            expires=expires,
            path=path,
            domain=domain,
            secure=secure,
            http_only=http_only,
            same_site=same_site,
        )
        self.cookies[name] = cookie

    def delete_cookie(self, name: str, path: str = "/", domain: Optional[str] = None):
        """Delete a cookie by setting it to expire"""
        self.set_cookie(
            name=name,
            value="",
            max_age=0,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path=path,
            domain=domain,
        )

    async def __aiter__(self):
        """Async iterator for streaming response"""
        if self._body_iterator is None:
            self._body_iterator = self._create_body_iterator()

        async for chunk in self._body_iterator:
            yield chunk

    async def _create_body_iterator(self):
        """Create body iterator based on content type"""
        if isinstance(self._content, str):
            yield self._content.encode(self.charset)
        elif isinstance(self._content, bytes):
            yield self._content
        elif hasattr(self._content, "__aiter__"):
            # Async generator
            async for chunk in self._content:
                if isinstance(chunk, str):
                    yield chunk.encode(self.charset)
                else:
                    yield chunk
        elif hasattr(self._content, "__iter__"):
            # Regular generator/iterator
            for chunk in self._content:
                if isinstance(chunk, str):
                    yield chunk.encode(self.charset)
                else:
                    yield chunk
        else:
            # Single value
            if isinstance(self._content, str):
                yield self._content.encode(self.charset)
            elif isinstance(self._content, bytes):
                yield self._content
            else:
                yield str(self._content).encode(self.charset)

    def get_headers(self) -> dict[str, str]:
        """Get all headers including cookies"""
        headers = dict(self.headers)

        # Add cookie headers
        if self.cookies:
            cookie_headers = []
            for cookie in self.cookies.values():
                cookie_headers.append(cookie.to_header())

            if cookie_headers:
                if "set-cookie" in headers:
                    # Append to existing
                    existing = headers["set-cookie"]
                    if isinstance(existing, list):
                        existing.extend(cookie_headers)
                    else:
                        headers["set-cookie"] = [existing] + cookie_headers
                else:
                    headers["set-cookie"] = cookie_headers

        return headers


class Response:
    """Ultra-high-performance HTTP response with zero-copy serialization"""

    __slots__ = (
        "content",
        "status_code",
        "charset",
        "media_type",
        "headers",
        "cookies",
        "_serialized_headers",
        "_content_bytes",
        "_is_serialized",
    )

    def __init__(
        self,
        content: Any = "",
        status_code: int = 200,
        headers: dict[str, str] = None,
        media_type: str = None,
        charset: str = "utf-8",
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.charset = charset

        # Auto-detect media type
        if media_type is None:
            if isinstance(content, dict) or isinstance(content, list):
                media_type = "application/json"
            elif isinstance(content, str):
                media_type = "text/plain"
            elif isinstance(content, bytes):
                media_type = "application/octet-stream"
            else:
                media_type = "text/plain"

        self.media_type = media_type
        self.headers = CaseInsensitiveDict(headers or {})
        self.cookies = {}

        # Serialization cache for zero-copy
        self._serialized_headers = None
        self._content_bytes = None
        self._is_serialized = False

        # Set content-type if not present
        if "content-type" not in self.headers:
            if media_type.startswith("text/") or media_type == "application/json":
                self.headers["content-type"] = f"{media_type}; charset={charset}"
            else:
                self.headers["content-type"] = media_type

    def get_content_bytes(self) -> bytes:
        """Get content as bytes with caching for zero-copy"""
        if self._content_bytes is None:
            if isinstance(self.content, bytes):
                self._content_bytes = self.content
            elif isinstance(self.content, str):
                self._content_bytes = self.content.encode(self.charset)
            elif isinstance(self.content, (dict, list)):
                import json

                json_str = json.dumps(self.content, ensure_ascii=False, separators=(",", ":"))
                self._content_bytes = json_str.encode(self.charset)
            else:
                self._content_bytes = str(self.content).encode(self.charset)

        return self._content_bytes

    def serialize_headers(self) -> bytes:
        """Serialize headers with caching for zero-copy"""
        if self._serialized_headers is None:
            header_lines = []

            # Add all headers
            for key, value in self.headers.items():
                header_lines.append(f"{key}: {value}")

            # Add cookies
            for cookie in self.cookies.values():
                header_lines.append(f"Set-Cookie: {cookie.to_header()}")

            # Add content-length if not present
            if "content-length" not in self.headers:
                content_bytes = self.get_content_bytes()
                header_lines.append(f"Content-Length: {len(content_bytes)}")

            self._serialized_headers = "\r\n".join(header_lines).encode("ascii")

        return self._serialized_headers

    def to_bytes(self) -> bytes:
        """Convert response to bytes with zero-copy optimization"""
        if self._is_serialized:
            # Return cached serialized version
            status_line = f"HTTP/1.1 {self.status_code} {self._get_status_text()}".encode("ascii")
            headers_bytes = self.serialize_headers()
            content_bytes = self.get_content_bytes()

            # Use join for efficient concatenation
            return b"\r\n".join([status_line, headers_bytes, b"", content_bytes])

        # Serialize once and cache
        status_line = f"HTTP/1.1 {self.status_code} {self._get_status_text()}"
        headers_section = self.serialize_headers().decode("ascii")

        response_parts = [status_line, headers_section, ""]  # Empty line before body

        headers_str = "\r\n".join(response_parts)
        headers_bytes = headers_str.encode("ascii")
        content_bytes = self.get_content_bytes()

        result = headers_bytes + b"\r\n" + content_bytes
        self._is_serialized = True

        return result

    def _get_status_text(self) -> str:
        """Get status text for status code"""
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
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return status_texts.get(self.status_code, "Unknown")

    def set_cookie(self, *args, **kwargs) -> None:
        """Set a cookie (same as StreamingResponse)"""
        cookie = Cookie(*args, **kwargs)
        self.cookies[cookie.name] = cookie

    def delete_cookie(self, name: str, path: str = "/", domain: Optional[str] = None):
        """Delete a cookie"""
        self.set_cookie(
            name=name,
            value="",
            max_age=0,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path=path,
            domain=domain,
        )

    def to_streaming_response(self) -> StreamingResponse:
        """Convert to streaming response with zero-copy optimization"""
        # Use pre-serialized content bytes for zero-copy
        content_bytes = self.get_content_bytes()

        # Create streaming response with bytes directly
        streaming = StreamingResponse(
            content=content_bytes,
            status_code=self.status_code,
            headers=dict(self.headers),
            media_type=self.media_type,
            charset=self.charset,
        )

        # Copy cookies
        streaming.cookies = self.cookies.copy()

        return streaming

    async def send(self, send_func):
        """Send response using ASGI send function with zero-copy"""
        # Send response start
        headers_list = []
        for key, value in self.headers.items():
            headers_list.append([key.encode(), value.encode()])

        # Add cookies
        for cookie in self.cookies.values():
            headers_list.append([b"set-cookie", cookie.to_header().encode()])

        await send_func(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": headers_list,
            }
        )

        # Send response body
        content_bytes = self.get_content_bytes()
        await send_func({"type": "http.response.body", "body": content_bytes})


class JSONResponse(Response):
    """
    JSON HTTP Response with automatic serialization.

    Extends the base Response class to provide JSON-specific functionality
    with comprehensive error handling and encoding support.

    Features:
    - Automatic JSON serialization with configurable options
    - Unicode and special character handling
    - Custom JSON encoders support
    - Automatic Content-Type header setting
    - Safe handling of non-serializable objects
    - Memory-efficient for large JSON payloads

    Args:
        content: Python object to serialize as JSON (dict, list, etc.)
        status_code: HTTP status code (default: 200)
        headers: Optional custom headers
        media_type: Media type (default: "application/json")
        charset: Character encoding (default: "utf-8")
        ensure_ascii: If True, escape non-ASCII characters (default: False)
        indent: JSON indentation for pretty-printing (default: None)
        separators: Custom separators tuple (default: (',', ':') for compact JSON)
        allow_nan: If False, raise ValueError for NaN/Infinity (default: True)
        sort_keys: If True, sort dictionary keys (default: False)
        default: Custom encoder function for non-serializable objects

    Example:
        >>> # Simple JSON response
        >>> response = JSONResponse({"message": "Hello World"})
        >>>
        >>> # Error response with custom status
        >>> error = JSONResponse(
        ...     {"error": "Not found", "code": 404},
        ...     status_code=404
        ... )
        >>>
        >>> # Pretty-printed JSON (development mode)
        >>> debug_response = JSONResponse(
        ...     {"data": [1, 2, 3]},
        ...     indent=2
        ... )
        >>>
        >>> # Custom headers
        >>> response = JSONResponse(
        ...     {"data": "value"},
        ...     headers={"X-Custom-Header": "value"}
        ... )

    Note:
        - By default, uses compact JSON encoding for better performance
        - Non-ASCII characters are preserved by default (ensure_ascii=False)
        - For production, avoid using indent to minimize response size
        - Use default parameter to handle custom objects (datetime, UUID, etc.)
    """

    __slots__ = (
        "_ensure_ascii",
        "_indent",
        "_separators",
        "_allow_nan",
        "_sort_keys",
        "_default",
    )

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict[str, str] = None,
        media_type: str = "application/json",
        charset: str = "utf-8",
        # JSON serialization options
        ensure_ascii: bool = False,
        indent: Optional[int] = None,
        separators: Optional[tuple[str, str]] = (",", ":"),
        allow_nan: bool = True,
        sort_keys: bool = False,
        default: Optional[Callable[[Any], Any]] = None,
    ) -> None:
        # Store JSON serialization options
        self._ensure_ascii = ensure_ascii
        self._indent = indent
        self._separators = separators
        self._allow_nan = allow_nan
        self._sort_keys = sort_keys
        self._default = default

        # Initialize parent Response class
        # Note: We pass content as-is; serialization happens in get_content_bytes()
        super().__init__(
            content=content if content is not None else {},
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            charset=charset,
        )

    def get_content_bytes(self) -> bytes:
        """
        Serialize content to JSON bytes with custom options.

        Overrides the parent get_content_bytes() to use custom JSON
        serialization options and handle edge cases.

        Returns:
            JSON-encoded bytes

        Raises:
            TypeError: If content is not JSON-serializable
            ValueError: If allow_nan=False and content contains NaN/Infinity
        """
        if self._content_bytes is None:
            try:
                # Use custom JSON serialization options
                json_str = json.dumps(
                    self.content,
                    ensure_ascii=self._ensure_ascii,
                    indent=self._indent,
                    separators=self._separators,
                    allow_nan=self._allow_nan,
                    sort_keys=self._sort_keys,
                    default=self._default,
                )
                self._content_bytes = json_str.encode(self.charset)
            except (TypeError, ValueError) as e:
                # Re-raise with more context for debugging
                raise TypeError(
                    f"Object of type {type(self.content).__name__} is not JSON serializable. "
                    f"Consider providing a 'default' function to handle custom types. "
                    f"Original error: {str(e)}"
                ) from e

        return self._content_bytes


# Response convenience functions
def json_response(data: Any, status_code: int = 200, headers: dict[str, str] = None) -> JSONResponse:
    """
    Create JSON response (convenience function).

    This is a simple factory function that creates a standard JSON response.
    For more control over JSON serialization options, use JSONResponse class directly.

    Args:
        data: Python object to serialize as JSON
        status_code: HTTP status code (default: 200)
        headers: Optional custom headers

    Returns:
        JSONResponse instance

    Example:
        >>> response = json_response({"message": "Success"})
        >>> response = json_response({"error": "Not found"}, status_code=404)
    """
    return JSONResponse(
        content=data,
        status_code=status_code,
        headers=headers,
    )


def html_response(content: str, status_code: int = 200, headers: dict[str, str] = None) -> Response:
    """Create HTML response"""
    return Response(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type="text/html",
    )


def text_response(content: str, status_code: int = 200, headers: dict[str, str] = None) -> Response:
    """Create text response"""
    return Response(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type="text/plain",
    )


def redirect_response(url: str, status_code: int = 302, headers: dict[str, str] = None) -> Response:
    """Create redirect response"""
    response_headers = {"location": url}
    if headers:
        response_headers.update(headers)

    return Response(content="", status_code=status_code, headers=response_headers)


def error_response(
    message: str, status_code: int = 500, headers: dict[str, str] = None
) -> Response:
    """Create error response"""
    return json_response(
        data={"error": message, "status": status_code},
        status_code=status_code,
        headers=headers,
    )
