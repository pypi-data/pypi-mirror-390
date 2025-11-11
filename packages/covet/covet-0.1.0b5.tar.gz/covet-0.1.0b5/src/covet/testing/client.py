"""
CovetPy Test Client

Comprehensive testing client for CovetPy applications providing FastAPI-compatible
test interface with additional features for WebSocket testing, file uploads,
and advanced request scenarios. Built for real backend integration testing.
"""

import asyncio
import io
import json
import uuid
import weakref
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union
from urllib.parse import quote, unquote, urlencode

from covet.core.asgi import CovetPyASGI, WebSocket, WebSocketState
from covet.core.http import Request, Response


class TestResponse:
    """Test response wrapper with enhanced assertion methods"""

    def __init__(
        self,
        status_code: int,
        content: bytes,
        headers: Dict[str, str],
        request: "TestRequest",
        elapsed_time: float = 0.0,
    ):
        self.status_code = status_code
        self.content = content
        self.headers = headers
        self.request = request
        self.elapsed_time = elapsed_time
        self._json_cache = None
        self._text_cache = None

    @property
    def text(self) -> str:
        """Get response content as text"""
        if self._text_cache is None:
            encoding = self._get_encoding()
            self._text_cache = self.content.decode(encoding)
        return self._text_cache

    def json(self) -> Any:
        """Parse response content as JSON"""
        if self._json_cache is None:
            self._json_cache = json.loads(self.text)
        return self._json_cache

    @property
    def ok(self) -> bool:
        """Check if response is successful (2xx status)"""
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        """Check if response is a redirect (3xx status)"""
        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        """Check if response is a client error (4xx status)"""
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        """Check if response is a server error (5xx status)"""
        return 500 <= self.status_code < 600

    def _get_encoding(self) -> str:
        """Get encoding from content-type header"""
        content_type = self.headers.get("content-type", "")
        if "charset=" in content_type:
            return content_type.split("charset=")[1].split(";")[0].strip()
        return "utf-8"

    def raise_for_status(self) -> None:
        """Raise exception for HTTP error status codes"""
        if not self.ok:
            raise HTTPError(f"HTTP {self.status_code}: {self.text}")

    def assert_status_code(self, expected: int) -> None:
        """Assert response status code matches expected"""
        assert self.status_code == expected, f"Expected {expected}, got {self.status_code}"

    def assert_json(self, expected: Any) -> None:
        """Assert response JSON matches expected value"""
        assert self.json() == expected, f"JSON mismatch: {self.json()} != {expected}"

    def assert_contains(self, text: str) -> None:
        """Assert response text contains specified string"""
        assert text in self.text, f"Text '{text}' not found in response"

    def assert_header(self, name: str, value: str = None) -> None:
        """Assert response has header, optionally with specific value"""
        assert name.lower() in (
            k.lower() for k in self.headers.keys()
        ), f"Header '{name}' not found"
        if value is not None:
            actual = next(v for k, v in self.headers.items() if k.lower() == name.lower())
            assert actual == value, f"Header '{name}': expected '{value}', got '{actual}'"


class TestRequest:
    """Test request wrapper with metadata"""

    def __init__(
        self,
        method: str,
        url: str,
        headers: Dict[str, str] = None,
        data: Any = None,
        json_data: Any = None,
        params: Dict[str, Any] = None,
        files: Dict[str, Any] = None,
        cookies: Dict[str, str] = None,
    ):
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.data = data
        self.json_data = json_data
        self.params = params or {}
        self.files = files or {}
        self.cookies = cookies or {}
        self.id = str(uuid.uuid4())


class HTTPError(Exception):
    """HTTP error exception"""


class TestWebSocket:
    """Test WebSocket connection for testing WebSocket endpoints"""

    def __init__(self, client: "TestClient", url: str, headers: Dict[str, str] = None):
        self.client = client
        self.url = url
        self.headers = headers or {}
        self._messages_sent = []
        self._messages_received = []
        self._is_connected = False
        self._websocket = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit"""
        await self.disconnect()

    async def connect(self):
        """Connect to WebSocket endpoint"""
        # Create WebSocket connection through test client
        scope = {
            "type": "websocket",
            "path": self.url,
            "headers": [(k.encode(), v.encode()) for k, v in self.headers.items()],
            "subprotocols": [],
        }

        self._message_queue = asyncio.Queue()
        self._connected = asyncio.Event()

        async def receive():
            return await self._message_queue.get()

        async def send(message):
            if message["type"] == "websocket.accept":
                self._is_connected = True
                self._connected.set()
            elif message["type"] == "websocket.send":
                if "text" in message:
                    self._messages_received.append(message["text"])
                elif "bytes" in message:
                    self._messages_received.append(message["bytes"])
            elif message["type"] == "websocket.close":
                self._is_connected = False

        # Start WebSocket handling
        self._task = asyncio.create_task(self.client.app(scope, receive, send))

        # Send connect message
        await self._message_queue.put({"type": "websocket.connect"})
        await self._connected.wait()

    async def disconnect(self):
        """Disconnect from WebSocket"""
        if self._is_connected:
            await self._message_queue.put({"type": "websocket.disconnect"})
            self._is_connected = False
        if hasattr(self, "_task"):
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                # TODO: Add proper exception handling

                pass

    async def send_text(self, text: str):
        """Send text message"""
        if not self._is_connected:
            raise RuntimeError("WebSocket not connected")
        self._messages_sent.append(text)
        await self._message_queue.put({"type": "websocket.receive", "text": text})

    async def send_bytes(self, data: bytes):
        """Send binary message"""
        if not self._is_connected:
            raise RuntimeError("WebSocket not connected")
        self._messages_sent.append(data)
        await self._message_queue.put({"type": "websocket.receive", "bytes": data})

    async def receive_text(self) -> str:
        """Receive text message"""
        if not self._messages_received:
            await asyncio.sleep(0.1)  # Allow processing
        if self._messages_received:
            message = self._messages_received.pop(0)
            if isinstance(message, str):
                return message
            else:
                raise TypeError("Expected text message, got bytes")
        raise TimeoutError("No message received")

    async def receive_bytes(self) -> bytes:
        """Receive binary message"""
        if not self._messages_received:
            await asyncio.sleep(0.1)  # Allow processing
        if self._messages_received:
            message = self._messages_received.pop(0)
            if isinstance(message, bytes):
                return message
            else:
                raise TypeError("Expected bytes message, got text")
        raise TimeoutError("No message received")

    def assert_sent(self, expected: Union[str, bytes]):
        """Assert that a message was sent"""
        assert expected in self._messages_sent, f"Message not sent: {expected}"

    def assert_received(self, expected: Union[str, bytes]):
        """Assert that a message was received"""
        assert expected in self._messages_received, f"Message not received: {expected}"


class TestClient:
    """
    Comprehensive test client for CovetPy applications

    Provides FastAPI-compatible testing interface with additional features:
    - Sync and async methods
    - WebSocket testing support
    - File upload testing
    - Cookie handling
    - Real backend integration testing
    - Session management
    - Custom assertions
    """

    def __init__(self, app: Union[CovetPyASGI, Callable], base_url: str = "http://testserver"):
        """
        Initialize test client

        Args:
            app: CovetPy ASGI application or callable
            base_url: Base URL for requests
        """
        self.app = app
        self.base_url = base_url.rstrip("/")
        self.session_cookies = {}
        self.default_headers = {}
        self._request_history = []

    def _prepare_url(self, url: str) -> str:
        """Prepare full URL from relative path"""
        if url.startswith("http"):
            return url
        return self.base_url + ("" if url.startswith("/") else "/") + url

    def _prepare_headers(self, headers: Dict[str, str] = None) -> Dict[str, str]:
        """Prepare headers with defaults and cookies"""
        final_headers = self.default_headers.copy()
        if headers:
            final_headers.update(headers)

        # Add cookies
        if self.session_cookies:
            cookie_header = "; ".join(f"{k}={v}" for k, v in self.session_cookies.items())
            final_headers["cookie"] = cookie_header

        return final_headers

    def _process_response_cookies(self, headers: Dict[str, str]):
        """Extract and store cookies from response"""
        set_cookie = headers.get("set-cookie")
        if set_cookie:
            # Simple cookie parsing (real implementation would be more robust)
            if isinstance(set_cookie, list):
                cookies = set_cookie
            else:
                cookies = [set_cookie]

            for cookie in cookies:
                if "=" in cookie:
                    name, value = cookie.split("=", 1)
                    # Remove additional cookie attributes
                    value = value.split(";")[0]
                    self.session_cookies[name.strip()] = value.strip()

    async def _make_request(self, method: str, url: str, **kwargs) -> TestResponse:
        """Make HTTP request to application"""
        import time

        start_time = time.time()

        # Prepare request
        full_url = self._prepare_url(url)
        headers = self._prepare_headers(kwargs.pop("headers", None))

        # Handle different data types
        data = kwargs.pop("data", None)
        json_data = kwargs.pop("json", None)
        files = kwargs.pop("files", None)
        params = kwargs.pop("params", None)

        # Build request body
        body = b""
        if json_data is not None:
            body = json.dumps(json_data).encode("utf-8")
            headers["content-type"] = "application/json"
        elif data is not None:
            if isinstance(data, str):
                body = data.encode("utf-8")
                headers.setdefault("content-type", "text/plain")
            elif isinstance(data, bytes):
                body = data
                headers.setdefault("content-type", "application/octet-stream")
            elif isinstance(data, dict):
                body = urlencode(data).encode("utf-8")
                headers["content-type"] = "application/x-www-form-urlencoded"
        elif files:
            # Handle file uploads
            body, content_type = self._encode_multipart(data or {}, files)
            headers["content-type"] = content_type

        # Add query parameters
        query_string = ""
        if params:
            query_string = urlencode(params)

        # Parse URL
        from urllib.parse import urlparse

        parsed = urlparse(full_url)
        path = parsed.path
        if query_string:
            path += "?" + query_string

        # Create ASGI scope
        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.1"},
            "http_version": "1.1",
            "method": method,
            "scheme": parsed.scheme,
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string.encode(),
            "root_path": "",
            "headers": [(k.encode(), v.encode()) for k, v in headers.items()],
            "server": ("testserver", 80),
            "client": ("testclient", 12345),
        }

        # Response collection
        response_data = {"status": 200, "headers": [], "body": b""}

        # ASGI receive callable
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body, "more_body": False}
            return {"type": "http.disconnect"}

        # ASGI send callable
        async def send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")

        # Call application
        await self.app(scope, receive, send)

        # Process response
        response_headers = {k.decode(): v.decode() for k, v in response_data["headers"]}

        # Store cookies
        self._process_response_cookies(response_headers)

        # Create test request for history
        test_request = TestRequest(
            method=method,
            url=full_url,
            headers=headers,
            data=data,
            json_data=json_data,
            params=params,
            files=files,
            cookies=self.session_cookies.copy(),
        )

        self._request_history.append(test_request)

        elapsed = time.time() - start_time

        return TestResponse(
            status_code=response_data["status"],
            content=response_data["body"],
            headers=response_headers,
            request=test_request,
            elapsed_time=elapsed,
        )

    def _encode_multipart(self, data: Dict[str, Any], files: Dict[str, Any]) -> tuple[bytes, str]:
        """Encode multipart form data"""
        boundary = f"----formdata-covet-{uuid.uuid4().hex}"
        lines = []

        # Add form fields
        for key, value in data.items():
            lines.append(f"--{boundary}")
            lines.append(f'Content-Disposition: form-data; name="{key}"')
            lines.append("")
            lines.append(str(value))

        # Add files
        for key, file_data in files.items():
            lines.append(f"--{boundary}")

            if isinstance(file_data, tuple):
                filename, content, content_type = file_data
            elif hasattr(file_data, "read"):
                filename = getattr(file_data, "name", "file")
                content = file_data.read()
                content_type = "application/octet-stream"
            else:
                filename = "file"
                content = file_data
                content_type = "application/octet-stream"

            lines.append(f'Content-Disposition: form-data; name="{key}"; filename="{filename}"')
            lines.append(f"Content-Type: {content_type}")
            lines.append("")

            # Convert content to string for joining
            if isinstance(content, bytes):
                # For binary content, we'll need to handle this differently
                # This is a simplified approach
                lines.append(content.decode("latin-1"))
            else:
                lines.append(str(content))

        lines.append(f"--{boundary}--")
        lines.append("")

        body = "\r\n".join(lines).encode("utf-8")
        content_type = f"multipart/form-data; boundary={boundary}"

        return body, content_type

    # HTTP Methods - Async versions
    async def get(self, url: str, **kwargs) -> TestResponse:
        """Make async GET request"""
        return await self._make_request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> TestResponse:
        """Make async POST request"""
        return await self._make_request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> TestResponse:
        """Make async PUT request"""
        return await self._make_request("PUT", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> TestResponse:
        """Make async DELETE request"""
        return await self._make_request("DELETE", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> TestResponse:
        """Make async PATCH request"""
        return await self._make_request("PATCH", url, **kwargs)

    async def head(self, url: str, **kwargs) -> TestResponse:
        """Make async HEAD request"""
        return await self._make_request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs) -> TestResponse:
        """Make async OPTIONS request"""
        return await self._make_request("OPTIONS", url, **kwargs)

    # WebSocket support
    def websocket_connect(self, url: str, headers: Dict[str, str] = None) -> TestWebSocket:
        """Create WebSocket connection"""
        full_url = self._prepare_url(url)
        parsed = urlparse(full_url)
        return TestWebSocket(self, parsed.path, headers)

    # Session management
    def set_cookies(self, cookies: Dict[str, str]):
        """Set session cookies"""
        self.session_cookies.update(cookies)

    def clear_cookies(self):
        """Clear all session cookies"""
        self.session_cookies.clear()

    def set_headers(self, headers: Dict[str, str]):
        """Set default headers"""
        self.default_headers.update(headers)

    def clear_headers(self):
        """Clear default headers"""
        self.default_headers.clear()

    # Request history
    @property
    def last_request(self) -> Optional[TestRequest]:
        """Get the last request made"""
        return self._request_history[-1] if self._request_history else None

    @property
    def request_history(self) -> List[TestRequest]:
        """Get all requests made"""
        return self._request_history.copy()

    def clear_history(self):
        """Clear request history"""
        self._request_history.clear()


# Sync wrapper for TestClient (FastAPI compatibility)
def _run_async(coro):
    """Run async function in sync context"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # We're in an async context, create a new task
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create one
        return asyncio.run(coro)


class SyncTestClient:
    """Synchronous wrapper for TestClient (FastAPI compatibility)"""

    def __init__(self, app: Union[CovetPyASGI, Callable], base_url: str = "http://testserver"):
        self.async_client = TestClient(app, base_url)

    def get(self, url: str, **kwargs) -> TestResponse:
        """Make sync GET request"""
        return _run_async(self.async_client.get(url, **kwargs))

    def post(self, url: str, **kwargs) -> TestResponse:
        """Make sync POST request"""
        return _run_async(self.async_client.post(url, **kwargs))

    def put(self, url: str, **kwargs) -> TestResponse:
        """Make sync PUT request"""
        return _run_async(self.async_client.put(url, **kwargs))

    def delete(self, url: str, **kwargs) -> TestResponse:
        """Make sync DELETE request"""
        return _run_async(self.async_client.delete(url, **kwargs))

    def patch(self, url: str, **kwargs) -> TestResponse:
        """Make sync PATCH request"""
        return _run_async(self.async_client.patch(url, **kwargs))

    def head(self, url: str, **kwargs) -> TestResponse:
        """Make sync HEAD request"""
        return _run_async(self.async_client.head(url, **kwargs))

    def options(self, url: str, **kwargs) -> TestResponse:
        """Make sync OPTIONS request"""
        return _run_async(self.async_client.options(url, **kwargs))

    # Delegate other methods
    def __getattr__(self, name):
        return getattr(self.async_client, name)


# Convenience functions
def create_test_client(
    app: Union[CovetPyASGI, Callable],
    base_url: str = "http://testserver",
    async_client: bool = True,
) -> Union[TestClient, SyncTestClient]:
    """
    Create test client for CovetPy application

    Args:
        app: CovetPy ASGI application
        base_url: Base URL for requests
        async_client: If True, return async client; if False, return sync client

    Returns:
        TestClient instance
    """
    if async_client:
        return TestClient(app, base_url)
    else:
        return SyncTestClient(app, base_url)


# Export main classes
__all__ = [
    "TestClient",
    "SyncTestClient",
    "TestResponse",
    "TestRequest",
    "TestWebSocket",
    "HTTPError",
    "create_test_client",
]
