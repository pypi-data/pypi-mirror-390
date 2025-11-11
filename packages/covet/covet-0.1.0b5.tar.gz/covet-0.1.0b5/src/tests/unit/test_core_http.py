"""
Comprehensive Unit Tests for CovetPy Core HTTP Components

Tests HTTP request/response handling, header processing, cookie management,
and content negotiation. All tests use real HTTP semantics without mocks
to ensure production-grade behavior.
"""

import json
from datetime import datetime, timedelta

import pytest

from covet.core.http import (
    Cookie,
    HeaderProcessor,
    Request,
    Response,
    StreamingResponse,
    error_response,
    file_response,
    html_response,
    json_response,
    redirect_response,
    text_response,
)


class TestRequest:
    """Test HTTP Request object functionality."""

    def test_request_basic_creation(self):
        """Test basic request object creation."""
        request = Request(
            method="GET",
            url="/api/users",
            headers={"Content-Type": "application/json"},
            body=b'{"name": "test"}',
        )

        assert request.method == "GET"
        assert request.url == "/api/users"
        assert request.headers["Content-Type"] == "application/json"
        assert request.body == b'{"name": "test"}'

    def test_request_url_parsing(self):
        """Test URL parsing and component extraction."""
        request = Request(
            method="GET", url="/api/users?page=1&limit=10&sort=name#section1"
        )

        assert request.path == "/api/users"
        assert request.query_string == "page=1&limit=10&sort=name"
        assert request.fragment == "section1"

        # Test query parameter parsing
        assert request.query_params["page"] == "1"
        assert request.query_params["limit"] == "10"
        assert request.query_params["sort"] == "name"

    def test_request_complex_url_parsing(self):
        """Test complex URL parsing with encoding."""
        request = Request(
            method="GET",
            url="/api/search?q=hello%20world&tags=python%2Capi&utf8=%E2%9C%93",
        )

        assert request.query_params["q"] == "hello world"
        assert request.query_params["tags"] == "python,api"
        assert request.query_params["utf8"] == "✓"

    def test_request_header_processing(self):
        """Test header processing and normalization."""
        request = Request(
            method="POST",
            url="/api/data",
            headers={
                "content-type": "application/json",
                "AUTHORIZATION": "Bearer token123",
                "X-Custom-Header": "value",
                "User-Agent": "CovetPy/1.0",
            },
        )

        # Headers should be case-insensitive
        assert request.headers["Content-Type"] == "application/json"
        assert request.headers["content-type"] == "application/json"
        assert request.headers["CONTENT-TYPE"] == "application/json"

        assert request.headers["Authorization"] == "Bearer token123"
        assert request.headers["X-Custom-Header"] == "value"
        assert request.headers["User-Agent"] == "CovetPy/1.0"

    def test_request_content_type_detection(self):
        """Test content type detection and parsing."""
        # JSON content
        json_request = Request(
            method="POST",
            url="/api/data",
            headers={"Content-Type": "application/json"},
            body=b'{"name": "test", "value": 123}',
        )

        assert json_request.content_type == "application/json"
        assert json_request.is_json() is True
        assert json_request.json() == {"name": "test", "value": 123}

        # Form content
        form_request = Request(
            method="POST",
            url="/api/form",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=b"name=test&value=123&tags=python&tags=api",
        )

        assert form_request.content_type == "application/x-www-form-urlencoded"
        assert form_request.is_form() is True
        form_data = form_request.form()
        assert form_data["name"] == "test"
        assert form_data["value"] == "123"
        assert form_data.getlist("tags") == ["python", "api"]

    def test_request_multipart_processing(self):
        """Test multipart form data processing."""
        # Simulate multipart form data
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        multipart_body = (
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
            b'Content-Disposition: form-data; name="name"\r\n\r\n'
            b"test user\r\n"
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
            b'Content-Disposition: form-data; name="file"; filename="test.txt"\r\n'
            b"Content-Type: text/plain\r\n\r\n"
            b"Hello, World!\r\n"
            b"------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n"
        )

        request = Request(
            method="POST",
            url="/api/upload",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            body=multipart_body,
        )

        assert request.is_multipart() is True
        # Note: Actual multipart parsing would require full implementation

    def test_request_path_parameters(self):
        """Test path parameter extraction."""
        request = Request(
            method="GET",
            url="/api/users/123/posts/456",
            path_params={"user_id": "123", "post_id": "456"},
        )

        assert request.path_params["user_id"] == "123"
        assert request.path_params["post_id"] == "456"

    def test_request_cookies(self):
        """Test cookie parsing from headers."""
        request = Request(
            method="GET",
            url="/api/data",
            headers={"Cookie": "session_id=abc123; theme=dark; lang=en"},
        )

        assert request.cookies["session_id"] == "abc123"
        assert request.cookies["theme"] == "dark"
        assert request.cookies["lang"] == "en"

    def test_request_authentication_info(self):
        """Test authentication information extraction."""
        # Bearer token
        bearer_request = Request(
            method="GET",
            url="/api/protected",
            headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
        )

        auth_type, token = bearer_request.get_auth_info()
        assert auth_type == "Bearer"
        assert token.startswith("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")

        # Basic auth
        basic_request = Request(
            method="GET",
            url="/api/protected",
            headers={"Authorization": "Basic dXNlcjpwYXNzd29yZA=="},
        )

        auth_type, credentials = basic_request.get_auth_info()
        assert auth_type == "Basic"
        assert credentials == "dXNlcjpwYXNzd29yZA=="

    def test_request_user_agent_parsing(self):
        """Test User-Agent header parsing."""
        request = Request(
            method="GET",
            url="/api/data",
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"
            },
        )

        user_agent = request.user_agent
        assert "Chrome" in user_agent
        assert "Windows" in user_agent

        # Test client info extraction
        client_info = request.get_client_info()
        assert "browser" in client_info
        assert "os" in client_info

    def test_request_client_ip_detection(self):
        """Test client IP address detection."""
        # Direct connection
        direct_request = Request(
            method="GET", url="/api/data", client_ip="192.168.1.100"
        )

        assert direct_request.client_ip == "192.168.1.100"

        # Behind proxy
        proxy_request = Request(
            method="GET",
            url="/api/data",
            headers={
                "X-Forwarded-For": "203.0.113.1, 198.51.100.1",
                "X-Real-IP": "203.0.113.1",
            },
            client_ip="10.0.0.1",
        )

        # Should extract real client IP from headers
        real_ip = proxy_request.get_real_client_ip()
        assert real_ip == "203.0.113.1"

    def test_request_content_negotiation(self):
        """Test content negotiation headers."""
        request = Request(
            method="GET",
            url="/api/data",
            headers={
                "Accept": "application/json, text/html;q=0.9, */*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9,fr;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
            },
        )

        # Test accept header parsing
        accepted_types = request.get_accepted_content_types()
        assert "application/json" in accepted_types
        assert "text/html" in accepted_types

        # Test language preferences
        languages = request.get_accepted_languages()
        assert "en-US" in languages
        assert "en" in languages

        # Test encoding preferences
        encodings = request.get_accepted_encodings()
        assert "gzip" in encodings
        assert "deflate" in encodings


class TestResponse:
    """Test HTTP Response object functionality."""

    def test_response_basic_creation(self):
        """Test basic response creation."""
        response = Response(
            content={"message": "success"},
            status_code=200,
            headers={"X-Custom": "value"},
        )

        assert response.status_code == 200
        assert response.content == {"message": "success"}
        assert response.headers["X-Custom"] == "value"

    def test_response_json_serialization(self):
        """Test JSON response serialization."""
        data = {
            "id": 123,
            "name": "Test User",
            "created_at": "2023-01-01T00:00:00Z",
            "metadata": {"key": "value"},
            "tags": ["python", "api"],
        }

        response = Response(content=data, status_code=200)

        assert response.media_type == "application/json"
        json_body = response.get_json_body()
        assert json.loads(json_body) == data

    def test_response_text_handling(self):
        """Test text response handling."""
        text_content = "Hello, World! This is a plain text response."

        response = Response(
            content=text_content, status_code=200, media_type="text/plain"
        )

        assert response.media_type == "text/plain"
        assert response.get_text_body() == text_content
        assert response.get_bytes_body() == text_content.encode("utf-8")

    def test_response_html_handling(self):
        """Test HTML response handling."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test</title></head>
        <body><h1>Hello, World!</h1></body>
        </html>
        """

        response = Response(
            content=html_content, status_code=200, media_type="text/html"
        )

        assert response.media_type == "text/html"
        assert "<h1>Hello, World!</h1>" in response.get_text_body()

    def test_response_binary_handling(self):
        """Test binary response handling."""
        binary_data = b"\x00\x01\x02\x03\xff\xfe\xfd"

        response = Response(
            content=binary_data, status_code=200, media_type="application/octet-stream"
        )

        assert response.media_type == "application/octet-stream"
        assert response.get_bytes_body() == binary_data

    def test_response_header_management(self):
        """Test response header management."""
        response = Response(content={"message": "test"})

        # Set headers
        response.set_header("X-Custom", "value1")
        response.set_header("X-Test", "value2")

        assert response.headers["X-Custom"] == "value1"
        assert response.headers["X-Test"] == "value2"

        # Update header
        response.set_header("X-Custom", "updated_value")
        assert response.headers["X-Custom"] == "updated_value"

        # Remove header
        response.remove_header("X-Test")
        assert "X-Test" not in response.headers

    def test_response_cookie_management(self):
        """Test response cookie management."""
        response = Response(content={"message": "test"})

        # Set simple cookie
        response.set_cookie("session_id", "abc123")

        # Set cookie with options
        response.set_cookie(
            "user_prefs",
            "theme=dark",
            max_age=3600,
            secure=True,
            httponly=True,
            samesite="Strict",
        )

        # Verify cookies in headers
        cookie_headers = response.headers.get_list("Set-Cookie")
        assert any("session_id=abc123" in cookie for cookie in cookie_headers)
        assert any("user_prefs=theme=dark" in cookie for cookie in cookie_headers)
        assert any("Secure" in cookie for cookie in cookie_headers)
        assert any("HttpOnly" in cookie for cookie in cookie_headers)

    def test_response_status_codes(self):
        """Test HTTP status code handling."""
        # Success responses
        ok_response = Response(content="OK", status_code=200)
        assert ok_response.is_success() is True
        assert ok_response.is_error() is False

        created_response = Response(content="Created", status_code=201)
        assert created_response.is_success() is True

        # Client error responses
        not_found_response = Response(content="Not Found", status_code=404)
        assert not_found_response.is_client_error() is True
        assert not_found_response.is_error() is True

        # Server error responses
        server_error_response = Response(content="Internal Error", status_code=500)
        assert server_error_response.is_server_error() is True
        assert server_error_response.is_error() is True

    def test_response_caching_headers(self):
        """Test caching-related headers."""
        response = Response(content="Cacheable content")

        # Set cache control
        response.set_cache_control(max_age=3600, public=True)
        assert "Cache-Control" in response.headers
        assert "max-age=3600" in response.headers["Cache-Control"]
        assert "public" in response.headers["Cache-Control"]

        # Set ETag
        response.set_etag("abc123def456")
        assert response.headers["ETag"] == '"abc123def456"'

        # Set Last-Modified
        last_modified = datetime.utcnow()
        response.set_last_modified(last_modified)
        assert "Last-Modified" in response.headers

    def test_response_compression_support(self):
        """Test response compression support."""
        large_content = "Hello, World! " * 1000
        response = Response(content=large_content)

        # Enable compression
        compressed_body = response.get_compressed_body("gzip")
        assert len(compressed_body) < len(large_content.encode())

        # Verify compression headers
        response.set_content_encoding("gzip")
        assert response.headers["Content-Encoding"] == "gzip"


class TestStreamingResponse:
    """Test streaming response functionality."""

    async def test_streaming_response_creation(self):
        """Test streaming response creation."""

        async def generate_data():
            for i in range(5):
                yield f"chunk {i}\n"

        response = StreamingResponse(generate_data(), media_type="text/plain")

        assert response.media_type == "text/plain"
        assert response.is_streaming() is True

    async def test_streaming_response_iteration(self):
        """Test streaming response iteration."""
        chunks = ["chunk 1", "chunk 2", "chunk 3"]

        async def generate_chunks():
            for chunk in chunks:
                yield chunk

        response = StreamingResponse(generate_chunks())

        collected_chunks = []
        async for chunk in response.body_iterator:
            collected_chunks.append(chunk)

        assert collected_chunks == chunks

    async def test_streaming_json_response(self):
        """Test streaming JSON response."""

        async def generate_json_items():
            yield '{"items": ['
            for i in range(3):
                if i > 0:
                    yield ","
                yield f'{{"id": {i}, "name": "item{i}"}}'
            yield "]}"

        response = StreamingResponse(
            generate_json_items(), media_type="application/json"
        )

        # Collect all chunks
        full_content = ""
        async for chunk in response.body_iterator:
            full_content += chunk

        # Verify valid JSON
        parsed = json.loads(full_content)
        assert "items" in parsed
        assert len(parsed["items"]) == 3


class TestCookie:
    """Test Cookie object functionality."""

    def test_cookie_basic_creation(self):
        """Test basic cookie creation."""
        cookie = Cookie(name="session_id", value="abc123")

        assert cookie.name == "session_id"
        assert cookie.value == "abc123"
        assert cookie.to_string() == "session_id=abc123"

    def test_cookie_with_options(self):
        """Test cookie with various options."""
        expires = datetime.utcnow() + timedelta(days=1)
        cookie = Cookie(
            name="user_token",
            value="xyz789",
            domain="example.com",
            path="/api",
            expires=expires,
            max_age=86400,
            secure=True,
            httponly=True,
            samesite="Strict",
        )

        cookie_string = cookie.to_string()
        assert "user_token=xyz789" in cookie_string
        assert "Domain=example.com" in cookie_string
        assert "Path=/api" in cookie_string
        assert "Max-Age=86400" in cookie_string
        assert "Secure" in cookie_string
        assert "HttpOnly" in cookie_string
        assert "SameSite=Strict" in cookie_string

    def test_cookie_parsing(self):
        """Test parsing cookies from headers."""
        cookie_header = "session_id=abc123; user_id=456; theme=dark"
        cookies = Cookie.parse_header(cookie_header)

        assert len(cookies) == 3
        assert cookies["session_id"] == "abc123"
        assert cookies["user_id"] == "456"
        assert cookies["theme"] == "dark"

    def test_cookie_deletion(self):
        """Test cookie deletion."""
        cookie = Cookie.delete("old_session")

        cookie_string = cookie.to_string()
        assert "old_session=" in cookie_string
        assert "Max-Age=0" in cookie_string
        assert "expires=" in cookie_string


class TestResponseHelpers:
    """Test response helper functions."""

    def test_json_response_helper(self):
        """Test json_response helper function."""
        data = {"message": "success", "data": [1, 2, 3]}
        response = json_response(data, status_code=201)

        assert response.status_code == 201
        assert response.media_type == "application/json"
        assert response.content == data

    def test_text_response_helper(self):
        """Test text_response helper function."""
        text = "Hello, World!"
        response = text_response(text, status_code=200)

        assert response.status_code == 200
        assert response.media_type == "text/plain"
        assert response.content == text

    def test_html_response_helper(self):
        """Test html_response helper function."""
        html = "<h1>Hello, World!</h1>"
        response = html_response(html)

        assert response.status_code == 200
        assert response.media_type == "text/html"
        assert response.content == html

    def test_redirect_response_helper(self):
        """Test redirect_response helper function."""
        # Permanent redirect
        response = redirect_response("/new-path", permanent=True)
        assert response.status_code == 301
        assert response.headers["Location"] == "/new-path"

        # Temporary redirect
        response = redirect_response("/temp-path", permanent=False)
        assert response.status_code == 302
        assert response.headers["Location"] == "/temp-path"

    def test_error_response_helper(self):
        """Test error_response helper function."""
        response = error_response("Not Found", status_code=404)

        assert response.status_code == 404
        assert response.content["error"] == "Not Found"
        assert response.media_type == "application/json"

    def test_file_response_helper(self):
        """Test file_response helper function."""
        file_path = "/tmp/test.txt"
        file_content = "Test file content"

        # Create temporary file
        with open(file_path, "w") as f:
            f.write(file_content)

        try:
            response = file_response(file_path)

            assert response.headers["Content-Type"] == "text/plain"
            assert "Content-Length" in response.headers
            assert response.headers["Content-Disposition"].startswith("attachment")

        finally:
            # Cleanup
            import os

            if os.path.exists(file_path):
                os.remove(file_path)


class TestContentNegotiation:
    """Test content negotiation functionality."""

    def test_accept_header_parsing(self):
        """Test Accept header parsing."""
        accept_header = "application/json, text/html;q=0.9, text/plain;q=0.8, */*;q=0.1"
        processor = HeaderProcessor()

        parsed = processor.parse_accept_header(accept_header)

        # Should be sorted by quality (q) value
        assert parsed[0]["type"] == "application/json"
        assert parsed[0]["quality"] == 1.0
        assert parsed[1]["type"] == "text/html"
        assert parsed[1]["quality"] == 0.9

    def test_content_type_matching(self):
        """Test content type matching."""
        processor = HeaderProcessor()

        # Exact match
        assert (
            processor.match_content_type("application/json", ["application/json"])
            is True
        )

        # Wildcard match
        assert (
            processor.match_content_type("application/*", ["application/json"]) is True
        )
        assert processor.match_content_type("*/*", ["text/html"]) is True

        # No match
        assert processor.match_content_type("text/html", ["application/json"]) is False

    def test_language_negotiation(self):
        """Test language negotiation."""
        accept_language = "en-US,en;q=0.9,fr;q=0.8,de;q=0.7"
        processor = HeaderProcessor()

        parsed = processor.parse_accept_language(accept_language)

        assert parsed[0]["language"] == "en-US"
        assert parsed[0]["quality"] == 1.0
        assert parsed[1]["language"] == "en"
        assert parsed[1]["quality"] == 0.9

    def test_encoding_negotiation(self):
        """Test encoding negotiation."""
        accept_encoding = "gzip, deflate;q=0.9, br;q=0.8"
        processor = HeaderProcessor()

        parsed = processor.parse_accept_encoding(accept_encoding)

        assert "gzip" in [item["encoding"] for item in parsed]
        assert "deflate" in [item["encoding"] for item in parsed]
        assert "br" in [item["encoding"] for item in parsed]


@pytest.mark.performance
class TestHTTPPerformance:
    """Test HTTP component performance."""

    def test_request_parsing_performance(self):
        """Test request parsing performance."""
        import time

        # Create complex request
        headers = {f"X-Header-{i}": f"value-{i}" for i in range(100)}
        headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + "x" * 500,
                "Cookie": "; ".join([f"cookie{i}=value{i}" for i in range(50)]),
            }
        )

        start_time = time.perf_counter()

        for _ in range(1000):
            request = Request(
                method="POST",
                url="/api/complex?param1=value1&param2=value2",
                headers=headers,
                body=b'{"data": "test"}',
            )

            # Access various properties to trigger parsing
            _ = request.content_type
            _ = request.query_params
            _ = request.cookies
            _ = request.json()

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 1000

        # Should be fast (< 1ms per request)
        assert avg_time < 0.001, f"Request parsing too slow: {avg_time:.4f}s"

    def test_response_serialization_performance(self):
        """Test response serialization performance."""
        import time

        # Create complex response data
        data = {
            "users": [
                {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
                for i in range(1000)
            ],
            "metadata": {"total": 1000, "page": 1},
        }

        start_time = time.perf_counter()

        for _ in range(100):
            response = Response(content=data)
            _ = response.get_json_body()

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 100

        # Should be reasonably fast
        assert avg_time < 0.01, f"Response serialization too slow: {avg_time:.4f}s"
