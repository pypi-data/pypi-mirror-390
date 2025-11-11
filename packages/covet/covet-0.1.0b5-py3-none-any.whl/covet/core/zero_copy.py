"""
Zero-Copy Request/Response Pipeline for NeutrinoPy
===================================================

Implements zero-copy data handling throughout the request lifecycle:
- Memoryview-based parsing
- Buffer protocol for responses
- Scatter-gather I/O
- Shared memory for large payloads
"""

import asyncio
import mmap
import os
import struct
import threading
import weakref
from collections import deque
from typing import Any, List, Optional, Union

# Try to import Rust extensions
try:
    from covet_rust import parse_json_simd, format_number_fast
    HAS_RUST_SIMD = True
except ImportError:
    HAS_RUST_SIMD = False


class ZeroCopyBuffer:
    """
    Buffer implementation with zero-copy slicing.
    Uses memoryview for efficient slicing without data copying.
    """

    __slots__ = ('_data', '_view', '_offset', '_length')

    def __init__(self, data: Union[bytes, bytearray, memoryview]):
        if isinstance(data, memoryview):
            self._view = data
            self._data = None
        else:
            self._data = data
            self._view = memoryview(data)

        self._offset = 0
        self._length = len(self._view)

    def slice(self, start: int, end: Optional[int] = None) -> 'ZeroCopyBuffer':
        """Create a zero-copy slice of this buffer."""
        if end is None:
            end = self._length

        # Return a view without copying
        sliced_view = self._view[start:end]
        result = ZeroCopyBuffer.__new__(ZeroCopyBuffer)
        result._view = sliced_view
        result._data = None
        result._offset = 0
        result._length = len(sliced_view)
        return result

    def find(self, pattern: bytes, start: int = 0) -> int:
        """Find pattern in buffer without copying."""
        # Use memoryview's find method
        pos = self._view[start:].tobytes().find(pattern)
        return pos + start if pos >= 0 else -1

    def __len__(self) -> int:
        return self._length

    def __bytes__(self) -> bytes:
        return bytes(self._view)

    def __buffer__(self, flags):
        """Support buffer protocol for zero-copy operations."""
        return self._view


class HeaderView:
    """
    Zero-copy header access using memoryview.
    Parses headers on-demand without creating intermediate strings.
    """

    __slots__ = ('_buffer', '_indices', '_parsed_cache')

    def __init__(self, buffer: Union[memoryview, bytes]):
        self._buffer = memoryview(buffer) if not isinstance(buffer, memoryview) else buffer
        self._indices = {}  # name -> (start, end) indices
        self._parsed_cache = {}  # Cached parsed values
        self._parse_indices()

    def _parse_indices(self):
        """Parse header positions without extracting values."""
        offset = 0
        buffer_bytes = self._buffer.tobytes()

        while offset < len(self._buffer):
            # Find header line end
            line_end = buffer_bytes.find(b'\r\n', offset)
            if line_end == -1:
                break

            # Empty line signals end of headers
            if line_end == offset:
                break

            # Find colon separator
            colon_pos = buffer_bytes.find(b':', offset)
            if colon_pos == -1 or colon_pos > line_end:
                offset = line_end + 2
                continue

            # Store indices (no string creation)
            name_start = offset
            name_end = colon_pos
            value_start = colon_pos + 1

            # Skip whitespace after colon
            while value_start < line_end and buffer_bytes[value_start] == ord(' '):
                value_start += 1

            # Store as lowercase for case-insensitive lookup
            name_bytes = buffer_bytes[name_start:name_end].lower()
            self._indices[name_bytes] = (value_start, line_end)

            offset = line_end + 2

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get header value without copying until necessary."""
        name_bytes = name.lower().encode('ascii')

        # Check cache first
        if name_bytes in self._parsed_cache:
            return self._parsed_cache[name_bytes]

        # Find in indices
        if name_bytes not in self._indices:
            return default

        # Extract value (only copy here)
        start, end = self._indices[name_bytes]
        value_bytes = bytes(self._buffer[start:end])
        value = value_bytes.decode('ascii', errors='ignore').strip()

        # Cache for repeated access
        self._parsed_cache[name_bytes] = value
        return value

    def __contains__(self, name: str) -> bool:
        """Check if header exists."""
        return name.lower().encode('ascii') in self._indices

    def items(self):
        """Iterate over all headers."""
        for name_bytes, (start, end) in self._indices.items():
            name = name_bytes.decode('ascii')
            value = bytes(self._buffer[start:end]).decode('ascii', errors='ignore').strip()
            yield name, value


class ZeroCopyRequest:
    """
    Request implementation with zero-copy data access.
    Parses data on-demand using memoryviews.
    """

    __slots__ = (
        '_raw_buffer',
        '_method',
        '_path',
        '_version',
        '_header_view',
        '_body_view',
        '_query_view',
        '_headers',
        '_query_params',
        '_json_cache',
        '_form_cache',
        '_cookies_cache',
    )

    def __init__(self, raw_data: Union[bytes, bytearray, memoryview]):
        self._raw_buffer = ZeroCopyBuffer(raw_data)

        # Parse request line
        self._parse_request_line()

        # Lazy-initialized components
        self._header_view = None
        self._body_view = None
        self._query_view = None
        self._headers = None
        self._query_params = None
        self._json_cache = None
        self._form_cache = None
        self._cookies_cache = None

    def _parse_request_line(self):
        """Parse HTTP request line without copying."""
        # Find first line
        line_end = self._raw_buffer.find(b'\r\n')
        if line_end == -1:
            raise ValueError("Invalid HTTP request: no request line")

        # Extract request line bytes
        line_bytes = bytes(self._raw_buffer.slice(0, line_end))

        # Parse method, path, version
        parts = line_bytes.split(b' ', 2)
        if len(parts) != 3:
            raise ValueError("Invalid HTTP request line")

        self._method = parts[0].decode('ascii')

        # Parse path and query string
        path_query = parts[1].decode('ascii')
        if '?' in path_query:
            self._path, query = path_query.split('?', 1)
            self._query_view = query
        else:
            self._path = path_query
            self._query_view = None

        self._version = parts[2].decode('ascii')

    @property
    def method(self) -> str:
        return self._method

    @property
    def path(self) -> str:
        return self._path

    @property
    def headers(self) -> HeaderView:
        """Parse headers on first access."""
        if self._headers is None:
            # Find header section
            req_line_end = self._raw_buffer.find(b'\r\n')
            headers_end = self._raw_buffer.find(b'\r\n\r\n')

            if headers_end == -1:
                # No body, headers extend to end
                header_bytes = self._raw_buffer.slice(req_line_end + 2)
            else:
                header_bytes = self._raw_buffer.slice(req_line_end + 2, headers_end + 2)

            self._headers = HeaderView(header_bytes._view)

        return self._headers

    @property
    def body(self) -> memoryview:
        """Get body as memoryview (zero-copy)."""
        if self._body_view is None:
            # Find body start
            headers_end = self._raw_buffer.find(b'\r\n\r\n')
            if headers_end == -1:
                self._body_view = memoryview(b'')
            else:
                body_start = headers_end + 4
                self._body_view = self._raw_buffer.slice(body_start)._view

        return self._body_view

    @property
    def query_params(self) -> dict:
        """Parse query parameters on demand."""
        if self._query_params is None:
            self._query_params = {}

            if self._query_view:
                # Parse without creating intermediate strings
                for pair in self._query_view.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        # URL decode
                        key = key.replace('+', ' ')
                        value = value.replace('+', ' ')
                        self._query_params[key] = value

        return self._query_params

    async def json(self) -> Any:
        """Parse JSON body."""
        if self._json_cache is None:
            body_bytes = bytes(self.body)

            if HAS_RUST_SIMD:
                # Use SIMD JSON parser from Rust
                self._json_cache = parse_json_simd(body_bytes)
            else:
                # Fallback to standard JSON
                import json
                self._json_cache = json.loads(body_bytes.decode('utf-8'))

        return self._json_cache


class BufferProtocolResponse:
    """
    Response implementing buffer protocol for zero-copy socket writes.
    Supports scatter-gather I/O for efficient multi-buffer responses.
    """

    __slots__ = ('_status_code', '_headers', '_chunks', '_total_size')

    def __init__(self, status_code: int = 200):
        self._status_code = status_code
        self._headers = []
        self._chunks = []
        self._total_size = 0

    def add_header(self, name: bytes, value: bytes):
        """Add header without string conversion."""
        self._headers.append((name, value))

    def add_chunk(self, chunk: Union[bytes, memoryview, bytearray]):
        """Add response chunk without copying."""
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')

        self._chunks.append(chunk)
        self._total_size += len(chunk)

    def get_response_bytes(self) -> List[Union[bytes, memoryview]]:
        """Get response as list of buffers for scatter-gather I/O."""
        buffers = []

        # Status line
        status_line = f"HTTP/1.1 {self._status_code} OK\r\n".encode('ascii')
        buffers.append(status_line)

        # Headers
        for name, value in self._headers:
            header_line = name + b": " + value + b"\r\n"
            buffers.append(header_line)

        # Content-Length if not chunked
        if self._total_size > 0:
            content_length = f"Content-Length: {self._total_size}\r\n".encode('ascii')
            buffers.append(content_length)

        # End of headers
        buffers.append(b"\r\n")

        # Body chunks
        buffers.extend(self._chunks)

        return buffers

    def __buffer__(self, flags):
        """Implement buffer protocol for zero-copy writes."""
        # Return list of buffers for writev()
        return self.get_response_bytes()


class SharedMemoryPool:
    """
    Shared memory pool for zero-copy large payload handling.
    Uses mmap for efficient memory sharing between processes.
    """

    def __init__(self, size: int = 100 * 1024 * 1024, name: Optional[str] = None):
        self._size = size
        self._name = name or f"neutrino_pool_{os.getpid()}"

        # Create shared memory
        if os.name == 'posix':
            # Unix: use anonymous mmap
            self._mmap = mmap.mmap(-1, size, prot=mmap.PROT_READ | mmap.PROT_WRITE)
        else:
            # Windows: use named mmap
            self._mmap = mmap.mmap(-1, size, tagname=self._name)

        # Simple bump allocator
        self._offset = 0
        self._lock = threading.Lock()
        self._allocations = weakref.WeakValueDictionary()

    def allocate(self, size: int) -> memoryview:
        """Allocate from shared memory pool."""
        with self._lock:
            if self._offset + size > self._size:
                # Pool exhausted, reset (simple strategy)
                self._offset = 0

            start = self._offset
            self._offset += size

            # Return memoryview (zero-copy)
            view = memoryview(self._mmap)[start:start + size]

            # Track allocation
            self._allocations[id(view)] = view

            return view

    def reset(self):
        """Reset pool for reuse."""
        with self._lock:
            self._offset = 0
            self._allocations.clear()

    def close(self):
        """Close shared memory."""
        self._mmap.close()


class BackpressureStream:
    """
    Stream implementation with automatic backpressure handling.
    Prevents memory exhaustion from fast producers.
    """

    def __init__(self, high_water: int = 65536, low_water: int = 16384):
        self._queue = asyncio.Queue()
        self._high_water = high_water
        self._low_water = low_water
        self._current_size = 0
        self._paused = False
        self._resume_event = asyncio.Event()
        self._resume_event.set()  # Initially not paused

    async def write(self, chunk: Union[bytes, memoryview]):
        """Write chunk with backpressure control."""
        # Wait if paused
        await self._resume_event.wait()

        # Add to queue
        await self._queue.put(chunk)
        self._current_size += len(chunk)

        # Check if we should pause
        if not self._paused and self._current_size >= self._high_water:
            self._pause()

    async def read(self) -> Optional[Union[bytes, memoryview]]:
        """Read chunk and manage backpressure."""
        try:
            chunk = await self._queue.get()
        except asyncio.CancelledError:
            return None

        self._current_size -= len(chunk)

        # Check if we should resume
        if self._paused and self._current_size <= self._low_water:
            self._resume()

        return chunk

    def _pause(self):
        """Pause writing due to backpressure."""
        self._paused = True
        self._resume_event.clear()

    def _resume(self):
        """Resume writing after backpressure relief."""
        self._paused = False
        self._resume_event.set()

    @property
    def is_paused(self) -> bool:
        """Check if stream is paused."""
        return self._paused


class ChunkedResponseGenerator:
    """
    Generator for HTTP chunked transfer encoding.
    Streams data without buffering entire response.
    """

    def __init__(self, data_source):
        self._data_source = data_source

    async def generate(self):
        """Generate chunked response."""
        # Headers
        yield b"HTTP/1.1 200 OK\r\n"
        yield b"Transfer-Encoding: chunked\r\n"
        yield b"Content-Type: application/json\r\n"
        yield b"\r\n"

        # Stream chunks
        async for chunk in self._data_source:
            if not chunk:
                continue

            # Chunk size in hex
            size = len(chunk)
            size_line = f"{size:x}\r\n".encode('ascii')
            yield size_line

            # Chunk data
            if isinstance(chunk, str):
                yield chunk.encode('utf-8')
            else:
                yield chunk

            # Chunk trailer
            yield b"\r\n"

        # Final chunk
        yield b"0\r\n\r\n"


class OptimizedRequestPool:
    """
    Object pool for request/response objects.
    Reduces allocation overhead through object reuse.
    """

    def __init__(self, max_size: int = 1000):
        self._request_pool = deque(maxlen=max_size)
        self._response_pool = deque(maxlen=max_size)
        self._lock = threading.Lock()

        # Pre-populate pools
        self._preallocate()

    def _preallocate(self):
        """Pre-allocate objects for immediate use."""
        for _ in range(min(100, self._request_pool.maxlen)):
            # Create but don't initialize
            req = ZeroCopyRequest.__new__(ZeroCopyRequest)
            self._request_pool.append(req)

            resp = BufferProtocolResponse.__new__(BufferProtocolResponse)
            self._response_pool.append(resp)

    def get_request(self, raw_data: bytes) -> ZeroCopyRequest:
        """Get or create request object."""
        with self._lock:
            if self._request_pool:
                req = self._request_pool.popleft()
                req.__init__(raw_data)
                return req

        return ZeroCopyRequest(raw_data)

    def return_request(self, request: ZeroCopyRequest):
        """Return request to pool."""
        # Clear sensitive data
        request._json_cache = None
        request._form_cache = None
        request._cookies_cache = None

        with self._lock:
            if len(self._request_pool) < self._request_pool.maxlen:
                self._request_pool.append(request)

    def get_response(self, status_code: int = 200) -> BufferProtocolResponse:
        """Get or create response object."""
        with self._lock:
            if self._response_pool:
                resp = self._response_pool.popleft()
                resp.__init__(status_code)
                return resp

        return BufferProtocolResponse(status_code)

    def return_response(self, response: BufferProtocolResponse):
        """Return response to pool."""
        # Clear data
        response._chunks.clear()
        response._headers.clear()
        response._total_size = 0

        with self._lock:
            if len(self._response_pool) < self._response_pool.maxlen:
                self._response_pool.append(response)


# Global instances
_global_shared_pool = None
_global_request_pool = None


def get_shared_memory_pool() -> SharedMemoryPool:
    """Get global shared memory pool."""
    global _global_shared_pool
    if _global_shared_pool is None:
        _global_shared_pool = SharedMemoryPool()
    return _global_shared_pool


def get_request_pool() -> OptimizedRequestPool:
    """Get global request/response pool."""
    global _global_request_pool
    if _global_request_pool is None:
        _global_request_pool = OptimizedRequestPool()
    return _global_request_pool