"""
CovetPy Production-Grade HTTP Request and Response Objects
=========================================================

This module provides high-performance, feature-rich HTTP Request and Response objects
designed for production use with zero-copy optimizations, async support, and comprehensive
feature sets including file uploads, compression, caching, and more.

Features:
- Lazy parsing for optimal performance
- Memory-efficient zero-copy operations
- Comprehensive HTTP features
- Async body reading support
- File upload handling
- Content negotiation
- Session support
- Compression (gzip, brotli)
- ETags and cache control
- Developer-friendly API
"""

import asyncio
import email.utils
import gzip
import hashlib
import io
import json
import mimetypes
import os
import re
import time
import urllib.parse
import uuid
import weakref
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Awaitable,
    BinaryIO,
    Callable,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)
from urllib.parse import parse_qs, unquote, unquote_plus

# Optional dependencies for enhanced features
try:
    import brotli

    HAS_BROTLI = True
except ImportError:
    brotli = None
    HAS_BROTLI = False

try:
    import zstandard as zstd

    HAS_ZSTD = True
except ImportError:
    zstd = None
    HAS_ZSTD = False


# Type definitions
T = TypeVar("T")
HeadersType = Dict[str, str]
CookiesType = Dict[str, "Cookie"]
QueryParamsType = Dict[str, List[str]]
FormDataType = Dict[str, Union[str, List[str], "UploadFile"]]


@dataclass
class UploadFile:
    """Represents an uploaded file with efficient handling"""

    filename: Optional[str] = None
    content_type: Optional[str] = None
    headers: HeadersType = field(default_factory=dict)
    size: Optional[int] = None
    _file: Optional[BinaryIO] = None
    _content: Optional[bytes] = None
    _temp_file_path: Optional[str] = None

    async def read(self, size: int = -1) -> bytes:
        """Read file content"""
        if self._content is not None:
            return self._content if size == -1 else self._content[:size]

        if self._file:
            self._file.seek(0)
            content = self._file.read(size)
            if size == -1:
                self._content = content  # Cache for future reads
            return content

        return b""

    async def write(self, data: bytes) -> int:
        """Write data to file"""
        if not self._file:
            import tempfile

            self._file = tempfile.NamedTemporaryFile(delete=False)
            self._temp_file_path = self._file.name

        written = self._file.write(data)
        if self.size is None:
            self.size = written
        else:
            self.size += written
        return written

    async def save(self, path: Union[str, Path]) -> None:
        """Save uploaded file to disk"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            content = await self.read()
            f.write(content)

    def __del__(self):
        """Clean up temporary files"""
        if self._temp_file_path and os.path.exists(self._temp_file_path):
            try:
                os.unlink(self._temp_file_path)
            except OSError:
                # TODO: Add proper exception handling

                pass


class CaseInsensitiveDict(dict):
    """Case-insensitive dictionary optimized for HTTP headers"""

    def __init__(self, data: Optional[Dict[str, str]] = None):
        super().__init__()
        self._key_map = {}  # Maps lowercase keys to original case

        if data:
            for key, value in data.items():
                self[key] = value

    def __setitem__(self, key: str, value: str) -> None:
        lower_key = key.lower()

        # Remove old entry if exists
        if lower_key in self._key_map:
            old_key = self._key_map[lower_key]
            if old_key in super().keys():
                super().__delitem__(old_key)

        self._key_map[lower_key] = key
        super().__setitem__(key, value)

    def __getitem__(self, key: str) -> str:
        lower_key = key.lower()
        actual_key = self._key_map.get(lower_key, key)
        return super().__getitem__(actual_key)

    def __delitem__(self, key: str) -> None:
        lower_key = key.lower()
        if lower_key in self._key_map:
            actual_key = self._key_map[lower_key]
            del self._key_map[lower_key]
            super().__delitem__(actual_key)

    def __contains__(self, key: str) -> bool:
        return key.lower() in self._key_map

    def get(self, key: str, default: Any = None) -> Any:
        try:
            return self[key]
        except KeyError:
            return default

    def pop(self, key: str, default: Any = None) -> Any:
        try:
            value = self[key]
            del self[key]
            return value
        except KeyError:
            return default


class SessionInterface:
    """Interface for session handling"""

    async def load_session(self, session_id: str) -> Dict[str, Any]:
        """Load session data"""
        return {}

    async def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Save session data"""

    async def delete_session(self, session_id: str) -> None:
        """Delete session"""


class MemorySessionInterface(SessionInterface):
    """In-memory session storage for development"""

    def __init__(self):
        self._sessions = {}
        self._lock = asyncio.Lock()

    async def load_session(self, session_id: str) -> Dict[str, Any]:
        async with self._lock:
            return self._sessions.get(session_id, {})

    async def save_session(self, session_id: str, data: Dict[str, Any]) -> None:
        async with self._lock:
            self._sessions[session_id] = data

    async def delete_session(self, session_id: str) -> None:
        async with self._lock:
            self._sessions.pop(session_id, None)


class LazyQueryParser:
    """Lazy query string parser for performance optimization"""

    def __init__(self, query_string: str):
        self._query_string = query_string
        self._parsed: Optional[QueryParamsType] = None
        self._cache = {}

    def _parse(self) -> QueryParamsType:
        """Parse query string on demand"""
        if self._parsed is None:
            self._parsed = parse_qs(self._query_string, keep_blank_values=True)
        return self._parsed

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get first value for key"""
        if key in self._cache:
            return self._cache[key]

        values = self._parse().get(key, [])
        result = values[0] if values else default
        self._cache[key] = result
        return result

    def get_list(self, key: str) -> List[str]:
        """Get all values for key"""
        return self._parse().get(key, [])

    def items(self):
        """Iterate over all key-value pairs"""
        for key, values in self._parse().items():
            for value in values:
                yield key, value

    def keys(self):
        """Get all parameter names"""
        return self._parse().keys()

    def __contains__(self, key: str) -> bool:
        return key in self._parse()

    def __getitem__(self, key: str) -> Optional[str]:
        return self.get(key)


class StreamingBody:
    """Streaming body reader with async support"""

    def __init__(
        self,
        reader: AsyncIterator[bytes],
        content_length: Optional[int] = None,
        chunk_size: int = 8192,
    ):
        self._reader = reader
        self._content_length = content_length
        self._chunk_size = chunk_size
        self._consumed = False
        self._buffer = io.BytesIO()

    async def read(self, size: int = -1) -> bytes:
        """Read bytes from stream"""
        if self._consumed:
            return b""

        if size == -1:
            # Read all data
            chunks = []
            async for chunk in self._reader:
                chunks.append(chunk)
            self._consumed = True
            return b"".join(chunks)

        # Read specific amount
        data = b""
        remaining = size

        async for chunk in self._reader:
            if remaining <= 0:
                break

            if len(chunk) <= remaining:
                data += chunk
                remaining -= len(chunk)
            else:
                data += chunk[:remaining]
                remaining = 0

        if remaining > 0:
            self._consumed = True

        return data

    async def json(self) -> Any:
        """Parse body as JSON"""
        data = await self.read()
        return json.loads(data.decode("utf-8"))

    async def text(self, encoding: str = "utf-8") -> str:
        """Get body as text"""
        data = await self.read()
        return data.decode(encoding)

    async def form(self) -> FormDataType:
        """Parse body as form data"""
        data = await self.text()
        return parse_qs(data, keep_blank_values=True)


class MultipartParser:
    """Parser for multipart/form-data with file upload support"""

    def __init__(self, body: bytes, boundary: str):
        self.body = body
        self.boundary = boundary.encode() if isinstance(boundary, str) else boundary

    async def parse(self) -> FormDataType:
        """Parse multipart data"""
        parts = self._split_parts()
        form_data = {}

        for part in parts:
            name, value = await self._parse_part(part)
            if name:
                if name in form_data:
                    # Handle multiple values
                    if not isinstance(form_data[name], list):
                        form_data[name] = [form_data[name]]
                    form_data[name].append(value)
                else:
                    form_data[name] = value

        return form_data

    def _split_parts(self) -> List[bytes]:
        """Split body into individual parts"""
        delimiter = b"--" + self.boundary
        parts = self.body.split(delimiter)

        # Remove empty parts and end marker
        parts = [part for part in parts if part and part != b"--\r\n" and part != b"--"]

        # Clean up parts (remove leading/trailing whitespace)
        cleaned_parts = []
        for part in parts:
            part = part.strip()
            if part:
                cleaned_parts.append(part)

        return cleaned_parts

    async def _parse_part(self, part: bytes) -> Tuple[Optional[str], Union[str, UploadFile]]:
        """Parse individual part"""
        if b"\r\n\r\n" not in part:
            return None, ""

        headers_section, body_section = part.split(b"\r\n\r\n", 1)
        headers = self._parse_headers(headers_section.decode("utf-8"))

        # Extract name from Content-Disposition
        content_disposition = headers.get("content-disposition", "")
        name = self._extract_name(content_disposition)

        if not name:
            return None, ""

        # Check if this is a file upload
        filename = self._extract_filename(content_disposition)

        if filename:
            # File upload
            file_obj = UploadFile(
                filename=filename,
                content_type=headers.get("content-type", "application/octet-stream"),
                headers=headers,
                size=len(body_section),
            )
            await file_obj.write(body_section)
            return name, file_obj
        else:
            # Regular form field
            return name, body_section.decode("utf-8")

    def _parse_headers(self, headers_text: str) -> HeadersType:
        """Parse part headers"""
        headers = {}
        for line in headers_text.split("\r\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip().lower()] = value.strip()
        return headers

    def _extract_name(self, content_disposition: str) -> Optional[str]:
        """Extract name from Content-Disposition header"""
        match = re.search(r'name="([^"]*)"', content_disposition)
        return match.group(1) if match else None

    def _extract_filename(self, content_disposition: str) -> Optional[str]:
        """Extract filename from Content-Disposition header"""
        match = re.search(r'filename="([^"]*)"', content_disposition)
        return match.group(1) if match else None


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
    ):
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
        parts = [f"{self.name}={self.value}"]

        if self.max_age is not None:
            parts.append(f"Max-Age={self.max_age}")

        if self.expires:
            parts.append(f"Expires={self.expires}")

        if self.path:
            parts.append(f"Path={self.path}")

        if self.domain:
            parts.append(f"Domain={self.domain}")

        if self.secure:
            parts.append("Secure")

        if self.http_only:
            parts.append("HttpOnly")

        if self.same_site:
            parts.append(f"SameSite={self.same_site}")

        return "; ".join(parts)

    @classmethod
    def from_string(cls, cookie_string: str) -> "Cookie":
        """Parse cookie from string"""
        parts = cookie_string.split(";")
        if not parts:
            raise ValueError("Invalid cookie string")

        # First part is name=value
        name_value = parts[0].strip()
        if "=" not in name_value:
            raise ValueError("Invalid cookie format")

        name, value = name_value.split("=", 1)
        cookie = cls(name.strip(), value.strip())

        # Parse attributes
        for part in parts[1:]:
            part = part.strip()
            if "=" in part:
                attr_name, attr_value = part.split("=", 1)
                attr_name = attr_name.strip().lower()
                attr_value = attr_value.strip()

                if attr_name == "max-age":
                    cookie.max_age = int(attr_value)
                elif attr_name == "expires":
                    cookie.expires = attr_value
                elif attr_name == "path":
                    cookie.path = attr_value
                elif attr_name == "domain":
                    cookie.domain = attr_value
                elif attr_name == "samesite":
                    cookie.same_site = attr_value
            else:
                attr_name = part.lower()
                if attr_name == "secure":
                    cookie.secure = True
                elif attr_name == "httponly":
                    cookie.http_only = True

        return cookie


class Request:
    """Production-grade HTTP Request with comprehensive features"""

    def __init__(
        self,
        method: str = "GET",
        url: str = "/",
        headers: Optional[HeadersType] = None,
        body: Union[bytes, str, StreamingBody, None] = None,
        query_string: str = "",
        path_params: Optional[Dict[str, Any]] = None,
        client_addr: Optional[Tuple[str, int]] = None,
        server_addr: Optional[Tuple[str, int]] = None,
        scheme: str = "http",
        http_version: str = "1.1",
        raw_data: Optional[bytes] = None,
        session_interface: Optional[SessionInterface] = None,
    ):
        # Core request data
        self.method = method.upper()
        self.url = url
        self.scheme = scheme
        self.http_version = http_version

        # Headers with case-insensitive access
        self.headers = CaseInsensitiveDict(headers or {})

        # URL parsing (lazy)
        self._parsed_url: Optional[urllib.parse.ParseResult] = None
        self._path: Optional[str] = None

        # Extract query string from URL if not provided separately
        if not query_string and "?" in url:
            _, self._query_string = url.split("?", 1)
        else:
            self._query_string = query_string

        self._query_params: Optional[LazyQueryParser] = None

        # Body handling
        self._body = body
        self._json_cache: Optional[Any] = None
        self._form_cache: Optional[FormDataType] = None
        self._text_cache: Optional[str] = None

        # Path parameters from routing
        self.path_params = path_params or {}

        # Client and server info
        self.client = client_addr
        self.server = server_addr

        # Session support
        self._session_interface = session_interface or MemorySessionInterface()
        self._session: Optional[Dict[str, Any]] = None
        self._session_id: Optional[str] = None

        # Cookies (lazy parsed)
        self._cookies: Optional[Dict[str, str]] = None

        # Request context and metadata
        self.context: Dict[str, Any] = {}
        self._request_id: Optional[str] = None
        self._start_time = time.time()

        # Raw data for zero-copy operations
        self._raw_data = raw_data

    @property
    def path(self) -> str:
        """Get request path (lazy parsed)"""
        if self._path is None:
            if "?" in self.url:
                self._path = self.url.split("?")[0]
            else:
                self._path = self.url
        return self._path

    @property
    def query_params(self) -> LazyQueryParser:
        """Get query parameters (lazy parsed)"""
        if self._query_params is None:
            self._query_params = LazyQueryParser(self._query_string)
        return self._query_params

    @property
    def cookies(self) -> Dict[str, str]:
        """Get cookies (lazy parsed)"""
        if self._cookies is None:
            self._cookies = {}
            cookie_header = self.headers.get("cookie", "")
            if cookie_header:
                for item in cookie_header.split(";"):
                    item = item.strip()
                    if "=" in item:
                        name, value = item.split("=", 1)
                        self._cookies[name.strip()] = unquote_plus(value.strip())
        return self._cookies

    @property
    def content_type(self) -> str:
        """Get content type"""
        return self.headers.get("content-type", "")

    @property
    def content_length(self) -> Optional[int]:
        """Get content length"""
        length = self.headers.get("content-length")
        return int(length) if length and length.isdigit() else None

    @property
    def request_id(self) -> str:
        """Get or generate unique request ID"""
        if self._request_id is None:
            self._request_id = str(uuid.uuid4())
        return self._request_id

    @property
    def user_agent(self) -> str:
        """Get user agent"""
        return self.headers.get("user-agent", "")

    @property
    def accept(self) -> str:
        """Get accept header"""
        return self.headers.get("accept", "*/*")

    @property
    def accept_encoding(self) -> str:
        """Get accept-encoding header"""
        return self.headers.get("accept-encoding", "")

    @property
    def accept_language(self) -> str:
        """Get accept-language header"""
        return self.headers.get("accept-language", "")

    @property
    def remote_addr(self) -> Optional[str]:
        """Get remote IP address"""
        # Check for forwarded headers first
        forwarded_for = self.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = self.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return self.client[0] if self.client else None

    # Body reading methods
    async def body_bytes(self) -> bytes:
        """Get body as bytes"""
        if isinstance(self._body, bytes):
            return self._body
        elif isinstance(self._body, str):
            return self._body.encode("utf-8")
        elif isinstance(self._body, StreamingBody):
            return await self._body.read()
        return b""

    async def text(self, encoding: str = "utf-8") -> str:
        """Get body as text (cached)"""
        if self._text_cache is None:
            body_bytes = await self.body_bytes()
            self._text_cache = body_bytes.decode(encoding)
        return self._text_cache

    async def json(self) -> Any:
        """Parse body as JSON (cached)"""
        if self._json_cache is None:
            text_content = await self.text()
            self._json_cache = json.loads(text_content)
        return self._json_cache

    async def form(self) -> FormDataType:
        """Parse body as form data (cached)"""
        if self._form_cache is None:
            content_type = self.content_type.lower()

            if "multipart/form-data" in content_type:
                # Parse multipart data
                boundary_match = re.search(r"boundary=([^;]+)", content_type)
                if boundary_match:
                    boundary = boundary_match.group(1).strip('"')
                    body_bytes = await self.body_bytes()
                    parser = MultipartParser(body_bytes, boundary)
                    self._form_cache = await parser.parse()
                else:
                    self._form_cache = {}
            else:
                # Parse URL-encoded data
                text_content = await self.text()
                parsed = parse_qs(text_content, keep_blank_values=True)
                self._form_cache = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

        return self._form_cache

    # Content type checks
    def is_json(self) -> bool:
        """Check if request has JSON content type"""
        return "application/json" in self.content_type.lower()

    def is_form(self) -> bool:
        """Check if request is form data"""
        ct = self.content_type.lower()
        return "application/x-www-form-urlencoded" in ct or "multipart/form-data" in ct

    def is_multipart(self) -> bool:
        """Check if request is multipart form data"""
        return "multipart/form-data" in self.content_type.lower()

    def is_websocket(self) -> bool:
        """Check if this is a WebSocket upgrade request"""
        return (
            self.headers.get("upgrade", "").lower() == "websocket"
            and "upgrade" in self.headers.get("connection", "").lower()
        )

    # Content negotiation
    def accepts(self, content_type: str) -> bool:
        """Check if client accepts content type"""
        accept = self.accept.lower()
        return content_type.lower() in accept or "*/*" in accept

    def accepts_encoding(self, encoding: str) -> bool:
        """Check if client accepts encoding"""
        return encoding.lower() in self.accept_encoding.lower()

    def prefers_language(self, languages: List[str]) -> Optional[str]:
        """Get preferred language from list"""
        accept_lang = self.accept_language.lower()
        for lang in languages:
            if lang.lower() in accept_lang:
                return lang
        return None

    # Session handling
    async def session(self) -> Dict[str, Any]:
        """Get session data"""
        if self._session is None:
            session_id = self.cookies.get("session_id")
            if session_id:
                self._session_id = session_id
                self._session = await self._session_interface.load_session(session_id)
            else:
                self._session_id = str(uuid.uuid4())
                self._session = {}
        return self._session

    async def save_session(self) -> str:
        """Save session and return session ID"""
        if self._session is not None and self._session_id:
            await self._session_interface.save_session(self._session_id, self._session)
        return self._session_id

    async def clear_session(self) -> None:
        """Clear session data"""
        if self._session_id:
            await self._session_interface.delete_session(self._session_id)
        self._session = {}
        self._session_id = None

    # Utility methods
    def get_header(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get header with default value"""
        return self.headers.get(name, default)

    def has_header(self, name: str) -> bool:
        """Check if header exists"""
        return name in self.headers

    def __repr__(self) -> str:
        return f"<Request {self.method} {self.url}>"


class Response:
    """Production-grade HTTP Response with comprehensive features"""

    def __init__(
        self,
        content: Any = "",
        status_code: int = 200,
        headers: Optional[HeadersType] = None,
        media_type: Optional[str] = None,
        charset: str = "utf-8",
        background_tasks: Optional[List[Callable]] = None,
    ):
        self.status_code = status_code
        self.charset = charset

        # Auto-detect media type
        if media_type is None:
            if isinstance(content, (dict, list)):
                media_type = "application/json"
            elif isinstance(content, str):
                media_type = "text/plain"
            elif isinstance(content, bytes):
                media_type = "application/octet-stream"
            else:
                media_type = "text/plain"

        self.media_type = media_type
        self.headers = CaseInsensitiveDict(headers or {})
        self.cookies: CookiesType = {}

        # Content handling
        self._content = content
        self._body_bytes: Optional[bytes] = None

        # Compression
        self._compressed: Optional[bytes] = None
        self._compression_type: Optional[str] = None

        # Caching
        self._etag: Optional[str] = None

        # Background tasks
        self.background_tasks = background_tasks or []

        # Set default headers
        self._set_default_headers()

    def _set_default_headers(self) -> None:
        """Set default headers"""
        # Content-Type
        if "content-type" not in self.headers:
            if self.media_type.startswith("text/") or self.media_type == "application/json":
                self.headers["content-type"] = f"{self.media_type}; charset={self.charset}"
            else:
                self.headers["content-type"] = self.media_type

        # Server
        if "server" not in self.headers:
            self.headers["server"] = "CovetPy/1.0"

        # Date
        if "date" not in self.headers:
            self.headers["date"] = email.utils.formatdate(time.time(), usegmt=True)

    def get_body_bytes(self) -> bytes:
        """Get response body as bytes"""
        if self._body_bytes is None:
            if isinstance(self._content, bytes):
                self._body_bytes = self._content
            elif isinstance(self._content, str):
                self._body_bytes = self._content.encode(self.charset)
            elif isinstance(self._content, (dict, list)):
                json_str = json.dumps(self._content, ensure_ascii=False, separators=(",", ":"))
                self._body_bytes = json_str.encode(self.charset)
            else:
                self._body_bytes = str(self._content).encode(self.charset)

        return self._body_bytes

    # Cookie methods
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

    def delete_cookie(self, name: str, path: str = "/", domain: Optional[str] = None) -> None:
        """Delete a cookie"""
        self.set_cookie(
            name=name,
            value="",
            max_age=0,
            expires="Thu, 01 Jan 1970 00:00:00 GMT",
            path=path,
            domain=domain,
        )

    # Compression methods
    def compress(self, accept_encoding: str = "") -> None:
        """Compress response body based on accept-encoding"""
        if self._compressed is not None:
            return  # Already compressed

        body = self.get_body_bytes()
        if len(body) < 1024:  # Don't compress small responses
            return

        accept_encoding = accept_encoding.lower()

        # Try brotli first (best compression)
        if HAS_BROTLI and "br" in accept_encoding:
            self._compressed = brotli.compress(body)
            self._compression_type = "br"
            self.headers["content-encoding"] = "br"
        # Try gzip
        elif "gzip" in accept_encoding:
            self._compressed = gzip.compress(body)
            self._compression_type = "gzip"
            self.headers["content-encoding"] = "gzip"
        # Try zstd
        elif HAS_ZSTD and "zstd" in accept_encoding:
            compressor = zstd.ZstdCompressor()
            self._compressed = compressor.compress(body)
            self._compression_type = "zstd"
            self.headers["content-encoding"] = "zstd"

        # Update content-length if compressed
        if self._compressed is not None:
            self.headers["content-length"] = str(len(self._compressed))
            self.headers["vary"] = "Accept-Encoding"

    def get_compressed_body(self) -> bytes:
        """Get compressed body if available, otherwise original"""
        return self._compressed if self._compressed is not None else self.get_body_bytes()

    # Caching methods
    def set_etag(self, etag: str, weak: bool = False) -> None:
        """Set ETag header"""
        if weak:
            self.headers["etag"] = f'W/"{etag}"'
        else:
            self.headers["etag"] = f'"{etag}"'
        self._etag = etag

    def generate_etag(self) -> str:
        """Generate ETag from content using SHA-256 instead of MD5 for security"""
        body = self.get_body_bytes()
        etag = hashlib.sha256(body).hexdigest()
        self.set_etag(etag)
        return etag

    def set_cache_control(
        self,
        max_age: Optional[int] = None,
        no_cache: bool = False,
        no_store: bool = False,
        must_revalidate: bool = False,
        public: bool = False,
        private: bool = False,
    ) -> None:
        """Set Cache-Control header"""
        directives = []

        if no_cache:
            directives.append("no-cache")
        if no_store:
            directives.append("no-store")
        if must_revalidate:
            directives.append("must-revalidate")
        if public:
            directives.append("public")
        if private:
            directives.append("private")
        if max_age is not None:
            directives.append(f"max-age={max_age}")

        if directives:
            self.headers["cache-control"] = ", ".join(directives)

    def set_expires(self, expires: Union[str, int]) -> None:
        """Set Expires header"""
        if isinstance(expires, int):
            # Convert timestamp to HTTP date
            expires = email.utils.formatdate(expires, usegmt=True)
        self.headers["expires"] = expires

    # Status code helpers
    def is_informational(self) -> bool:
        return 100 <= self.status_code < 200

    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    def is_server_error(self) -> bool:
        return 500 <= self.status_code < 600

    # Content-Length handling
    def _update_content_length(self) -> None:
        """Update Content-Length header"""
        if "content-length" not in self.headers and "transfer-encoding" not in self.headers:
            body = self.get_compressed_body()
            self.headers["content-length"] = str(len(body))

    # ASGI compatibility
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI app interface"""
        # Ensure content-length is set
        self._update_content_length()

        # Prepare headers
        headers = []
        for name, value in self.headers.items():
            headers.append([name.encode(), value.encode()])

        # Add cookies
        for cookie in self.cookies.values():
            headers.append([b"set-cookie", cookie.to_header().encode()])

        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": headers,
            }
        )

        # Send response body
        body = self.get_compressed_body()
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )

        # Execute background tasks
        for task in self.background_tasks:
            if asyncio.iscoroutinefunction(task):
                await task()
            else:
                task()

    def __repr__(self) -> str:
        return f"<Response {self.status_code}>"


class StreamingResponse(Response):
    """Streaming HTTP response for large content"""

    def __init__(
        self,
        content: Union[AsyncGenerator[bytes, None], AsyncIterator[bytes]],
        status_code: int = 200,
        headers: Optional[HeadersType] = None,
        media_type: str = "application/octet-stream",
        charset: str = "utf-8",
    ):
        # Don't call parent __init__ with content to avoid processing
        self.status_code = status_code
        self.charset = charset
        self.media_type = media_type
        self.headers = CaseInsensitiveDict(headers or {})
        self.cookies: CookiesType = {}
        self.background_tasks: List[Callable] = []

        # Streaming content
        self._content_generator = content

        # Set default headers
        self._set_default_headers()

        # Use chunked encoding for streaming
        self.headers["transfer-encoding"] = "chunked"

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI app interface for streaming"""
        # Prepare headers
        headers = []
        for name, value in self.headers.items():
            headers.append([name.encode(), value.encode()])

        # Add cookies
        for cookie in self.cookies.values():
            headers.append([b"set-cookie", cookie.to_header().encode()])

        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": headers,
            }
        )

        # Stream response body
        async for chunk in self._content_generator:
            await send(
                {
                    "type": "http.response.body",
                    "body": chunk,
                    "more_body": True,
                }
            )

        # Send final empty chunk
        await send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            }
        )

        # Execute background tasks
        for task in self.background_tasks:
            if asyncio.iscoroutinefunction(task):
                await task()
            else:
                task()


class FileResponse(Response):
    """Response for serving files efficiently"""

    def __init__(
        self,
        path: Union[str, Path],
        status_code: int = 200,
        headers: Optional[HeadersType] = None,
        media_type: Optional[str] = None,
        filename: Optional[str] = None,
        chunk_size: int = 8192,
    ):
        self.path = Path(path)
        self.chunk_size = chunk_size

        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # Auto-detect media type
        if media_type is None:
            media_type, _ = mimetypes.guess_type(str(self.path))
            if media_type is None:
                media_type = "application/octet-stream"

        # Get file stats
        stat = self.path.stat()
        file_size = stat.st_size
        last_modified = email.utils.formatdate(stat.st_mtime, usegmt=True)

        # Initialize headers
        file_headers = {
            "content-length": str(file_size),
            "last-modified": last_modified,
        }

        if filename:
            file_headers["content-disposition"] = f'attachment; filename="{filename}"'

        if headers:
            file_headers.update(headers)

        super().__init__(
            content="",  # Will be replaced by file content
            status_code=status_code,
            headers=file_headers,
            media_type=media_type,
        )

        # Generate ETag from file metadata using SHA-256 instead of MD5 for
        # security
        etag_content = f"{self.path.name}-{stat.st_size}-{stat.st_mtime}"
        etag = hashlib.sha256(etag_content.encode()).hexdigest()
        self.set_etag(etag)

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """ASGI app interface for file serving"""
        # Prepare headers
        headers = []
        for name, value in self.headers.items():
            headers.append([name.encode(), value.encode()])

        # Add cookies
        for cookie in self.cookies.values():
            headers.append([b"set-cookie", cookie.to_header().encode()])

        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": headers,
            }
        )

        # Stream file content
        with open(self.path, "rb") as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break
                await send(
                    {
                        "type": "http.response.body",
                        "body": chunk,
                        "more_body": True,
                    }
                )

        # Send final empty chunk
        await send(
            {
                "type": "http.response.body",
                "body": b"",
                "more_body": False,
            }
        )


# Convenience functions for common response types
def json_response(
    data: Any, status_code: int = 200, headers: Optional[HeadersType] = None
) -> Response:
    """Create JSON response"""
    return Response(
        content=data,
        status_code=status_code,
        headers=headers,
        media_type="application/json",
    )


def html_response(
    content: str, status_code: int = 200, headers: Optional[HeadersType] = None
) -> Response:
    """Create HTML response"""
    return Response(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type="text/html",
    )


def text_response(
    content: str, status_code: int = 200, headers: Optional[HeadersType] = None
) -> Response:
    """Create text response"""
    return Response(
        content=content,
        status_code=status_code,
        headers=headers,
        media_type="text/plain",
    )


def redirect_response(
    url: str, status_code: int = 302, headers: Optional[HeadersType] = None
) -> Response:
    """Create redirect response"""
    redirect_headers = {"location": url}
    if headers:
        redirect_headers.update(headers)

    return Response(
        content="",
        status_code=status_code,
        headers=redirect_headers,
    )


def error_response(
    message: str, status_code: int = 500, headers: Optional[HeadersType] = None
) -> Response:
    """Create error response"""
    return json_response(
        data={"error": message, "status": status_code},
        status_code=status_code,
        headers=headers,
    )


# Status code constants
class HTTPStatus:
    """HTTP status code constants"""

    # 1xx Informational
    CONTINUE = 100
    SWITCHING_PROTOCOLS = 101
    PROCESSING = 102

    # 2xx Success
    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206

    # 3xx Redirection
    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307
    PERMANENT_REDIRECT = 308

    # 4xx Client Error
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # 5xx Server Error
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505


# Export public interface
__all__ = [
    "Request",
    "Response",
    "StreamingResponse",
    "FileResponse",
    "Cookie",
    "UploadFile",
    "CaseInsensitiveDict",
    "SessionInterface",
    "MemorySessionInterface",
    "json_response",
    "html_response",
    "text_response",
    "redirect_response",
    "error_response",
    "HTTPStatus",
]
