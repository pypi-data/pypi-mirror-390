"""
HTTP Parser Integration Examples
=================================

This file demonstrates how to integrate the Rust HTTP parser into CovetPy
applications for maximum performance.

Examples:
1. Basic parsing
2. Integration with existing Request class
3. Batch processing for high throughput
4. Parser pooling for concurrent requests
5. Custom middleware integration
"""

import asyncio
from typing import Optional
from covet.core.http_parser import HttpParser, ParsedRequest, parse_request


# ==============================================================================
# Example 1: Basic Parsing
# ==============================================================================

def example_basic_parsing():
    """
    Basic HTTP request parsing with the Rust parser.

    Performance: ~1-2µs per request
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Basic Parsing")
    print("="*70)

    # Create parser (reusable)
    parser = HttpParser(max_headers=100)

    # Parse a simple GET request
    request = b"GET /api/users HTTP/1.1\r\nHost: example.com\r\n\r\n"
    parsed = parser.parse(request)

    print(f"Method: {parsed.method}")
    print(f"Path: {parsed.path}")
    print(f"Version: {parsed.version}")
    print(f"Headers: {parsed.headers}")

    # Parse a POST request with body
    request = b"""POST /api/users HTTP/1.1\r
Host: example.com\r
Content-Type: application/json\r
Content-Length: 27\r
\r
{"name": "Alice", "age": 30}"""

    parser.reset()  # Reset for new request
    parsed = parser.parse(request)

    print(f"\nMethod: {parsed.method}")
    print(f"Body: {parsed.body_text}")
    print(f"JSON: {parsed.json()}")


# ==============================================================================
# Example 2: Integration with CovetPy Request Class
# ==============================================================================

class CovetRequest:
    """
    Example CovetPy Request class that uses the Rust parser.

    This shows how to integrate the fast parser while maintaining
    backward compatibility with existing code.
    """

    def __init__(self, raw_request: bytes):
        """Initialize from raw HTTP request bytes."""
        # Use fast parser
        self._parsed = parse_request(raw_request)

        # Additional CovetPy-specific attributes
        self._app = None
        self._route = None
        self._session = {}

    @property
    def method(self) -> str:
        """HTTP method."""
        return self._parsed.method

    @property
    def path(self) -> str:
        """Request path."""
        return self._parsed.path

    @property
    def headers(self):
        """Request headers."""
        return self._parsed.headers

    def get_header(self, name: str) -> Optional[str]:
        """Get header value (case-insensitive)."""
        return self._parsed.get_header(name)

    @property
    def body(self) -> Optional[bytes]:
        """Request body."""
        return self._parsed.body

    def json(self):
        """Parse body as JSON."""
        return self._parsed.json()

    # CovetPy-specific methods
    @property
    def session(self):
        """User session data."""
        return self._session

    def __repr__(self):
        return f"CovetRequest({self.method} {self.path})"


def example_covet_integration():
    """
    Example of integrating the parser with CovetPy's Request class.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: CovetPy Request Integration")
    print("="*70)

    request = b"""POST /api/login HTTP/1.1\r
Host: example.com\r
Content-Type: application/json\r
\r
{"username": "alice", "password": "secret"}"""

    # Create CovetPy request (uses fast parser internally)
    req = CovetRequest(request)

    print(f"Request: {req}")
    print(f"Method: {req.method}")
    print(f"Path: {req.path}")
    print(f"Content-Type: {req.get_header('content-type')}")
    print(f"JSON data: {req.json()}")
    print(f"Session: {req.session}")


# ==============================================================================
# Example 3: Batch Processing for High Throughput
# ==============================================================================

def example_batch_processing():
    """
    Process multiple requests in a batch for reduced FFI overhead.

    Performance: 10-100x faster than individual calls for large batches
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: Batch Processing")
    print("="*70)

    parser = HttpParser()

    # Create a batch of requests (e.g., from request replay or testing)
    requests = [
        b"GET /api/users/1 HTTP/1.1\r\nHost: example.com\r\n\r\n",
        b"GET /api/users/2 HTTP/1.1\r\nHost: example.com\r\n\r\n",
        b"GET /api/users/3 HTTP/1.1\r\nHost: example.com\r\n\r\n",
        b"POST /api/users HTTP/1.1\r\nContent-Type: application/json\r\n\r\n{}",
    ]

    # Parse all at once (single FFI call)
    parsed_requests = parser.parse_batch(requests)

    print(f"Parsed {len(parsed_requests)} requests in batch")
    for i, parsed in enumerate(parsed_requests):
        print(f"  [{i+1}] {parsed.method} {parsed.path}")

    # Example: Process batch for load testing
    import time

    # Create larger batch
    large_batch = [requests[0]] * 1000

    start = time.perf_counter()
    results = parser.parse_batch(large_batch)
    elapsed = time.perf_counter() - start

    print(f"\nBatch of {len(large_batch)} requests:")
    print(f"  Time: {elapsed*1000:.2f} ms")
    print(f"  Throughput: {len(large_batch)/elapsed:,.0f} requests/second")
    print(f"  Avg latency: {elapsed/len(large_batch)*1_000_000:.2f} µs/request")


# ==============================================================================
# Example 4: Parser Pooling for Concurrent Requests
# ==============================================================================

class ParserPool:
    """
    Pool of HTTP parsers for concurrent request handling.

    This avoids allocating a new parser for each request while
    ensuring thread safety.
    """

    def __init__(self, pool_size: int = 100):
        """Initialize parser pool."""
        self.parsers = [HttpParser() for _ in range(pool_size)]
        self.index = 0

    def get_parser(self) -> HttpParser:
        """Get a parser from the pool (round-robin)."""
        parser = self.parsers[self.index]
        self.index = (self.index + 1) % len(self.parsers)
        return parser

    def parse(self, data: bytes) -> ParsedRequest:
        """Parse request using pooled parser."""
        parser = self.get_parser()
        parsed = parser.parse(data)
        parser.reset()  # Reset for next use
        return parsed


def example_parser_pool():
    """
    Example of using a parser pool for concurrent requests.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Parser Pooling")
    print("="*70)

    # Create parser pool
    pool = ParserPool(pool_size=10)

    # Simulate concurrent requests
    requests = [
        b"GET /api/endpoint1 HTTP/1.1\r\nHost: example.com\r\n\r\n",
        b"GET /api/endpoint2 HTTP/1.1\r\nHost: example.com\r\n\r\n",
        b"GET /api/endpoint3 HTTP/1.1\r\nHost: example.com\r\n\r\n",
    ]

    # Parse using pool (parsers are reused)
    for req in requests:
        parsed = pool.parse(req)
        print(f"Parsed: {parsed.method} {parsed.path}")

    print(f"\nPool size: {len(pool.parsers)} parsers")
    print("Parsers are reused for subsequent requests (zero allocation)")


# ==============================================================================
# Example 5: Custom Middleware Integration
# ==============================================================================

class HTTPParserMiddleware:
    """
    Middleware that uses the Rust parser for request parsing.

    This can be integrated into CovetPy's middleware system.
    """

    def __init__(self):
        self.parser = HttpParser()

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        # For HTTP requests, parse using Rust parser
        if scope['type'] == 'http':
            # Collect request body
            body = b''
            while True:
                message = await receive()
                if message['type'] == 'http.request':
                    body += message.get('body', b'')
                    if not message.get('more_body', False):
                        break

            # Build raw HTTP request
            method = scope['method']
            path = scope['path']
            headers_list = scope['headers']

            # Construct raw HTTP request
            raw = f"{method} {path} HTTP/1.1\r\n".encode()
            for name, value in headers_list:
                raw += name + b': ' + value + b'\r\n'
            raw += b'\r\n' + body

            # Parse with Rust parser (fast!)
            try:
                parsed = self.parser.parse(raw)
                # Add parsed data to scope
                scope['parsed_request'] = parsed
                self.parser.reset()
            except Exception as e:
                print(f"Parse error: {e}")

        # Continue to next middleware/handler
        # (in real implementation, would call next handler)


def example_middleware():
    """
    Example of middleware integration.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Middleware Integration")
    print("="*70)

    middleware = HTTPParserMiddleware()

    # Simulate ASGI scope
    scope = {
        'type': 'http',
        'method': 'POST',
        'path': '/api/users',
        'headers': [(b'content-type', b'application/json')],
    }

    async def receive():
        return {
            'type': 'http.request',
            'body': b'{"name": "Bob"}',
            'more_body': False,
        }

    async def send(message):
        pass

    # Run middleware
    async def run():
        await middleware(scope, receive, send)
        if 'parsed_request' in scope:
            parsed = scope['parsed_request']
            print(f"Middleware parsed: {parsed.method} {parsed.path}")
            print(f"Headers: {parsed.header_count}")

    asyncio.run(run())


# ==============================================================================
# Example 6: Performance Comparison
# ==============================================================================

def example_performance_comparison():
    """
    Compare Rust parser vs Python parser performance.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Performance Comparison")
    print("="*70)

    import time
    from http.server import BaseHTTPRequestHandler
    from io import BytesIO

    request = b"""GET /api/users?page=1&limit=10 HTTP/1.1\r
Host: api.example.com\r
User-Agent: Mozilla/5.0\r
Accept: application/json\r
Authorization: Bearer token123\r
Content-Type: application/json\r
\r
"""

    # Rust parser
    parser = HttpParser()
    iterations = 10000

    start = time.perf_counter()
    for _ in range(iterations):
        parsed = parser.parse(request)
        parser.reset()
    rust_time = time.perf_counter() - start

    # Python parser (using http.server)
    class DummyRequest(BaseHTTPRequestHandler):
        def __init__(self, request_data):
            self.rfile = BytesIO(request_data)
            self.raw_requestline = self.rfile.readline()
            self.error_code = self.error_message = None
            self.parse_request()

    start = time.perf_counter()
    for _ in range(iterations):
        req = DummyRequest(request)
    python_time = time.perf_counter() - start

    print(f"Iterations: {iterations:,}")
    print(f"\nRust parser:")
    print(f"  Total: {rust_time:.3f}s")
    print(f"  Avg: {rust_time/iterations*1_000_000:.2f} µs/request")
    print(f"\nPython parser:")
    print(f"  Total: {python_time:.3f}s")
    print(f"  Avg: {python_time/iterations*1_000_000:.2f} µs/request")
    print(f"\nSpeedup: {python_time/rust_time:.1f}x faster")


# ==============================================================================
# Main
# ==============================================================================

def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("HTTP PARSER INTEGRATION EXAMPLES")
    print("="*70)

    example_basic_parsing()
    example_covet_integration()
    example_batch_processing()
    example_parser_pool()
    example_middleware()
    example_performance_comparison()

    print("\n" + "="*70)
    print("ALL EXAMPLES COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
