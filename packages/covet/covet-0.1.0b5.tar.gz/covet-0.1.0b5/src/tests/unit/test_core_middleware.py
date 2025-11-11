"""
Comprehensive Unit Tests for CovetPy Core Middleware System

Tests middleware pipeline execution, CORS handling, authentication,
rate limiting, and custom middleware functionality. All tests validate
real middleware behavior and integration patterns.
"""

import asyncio
import time
from typing import Callable
from unittest.mock import MagicMock

import pytest

from covet.core.exceptions import HTTPException
from covet.core.http import Request, Response
from covet.core.middleware import (
    BaseHTTPMiddleware,
    CORSMiddleware,
    ExceptionMiddleware,
    GZipMiddleware,
    MiddlewarePipeline,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)


class TestBaseHTTPMiddleware:
    """Test base middleware functionality."""

    @pytest.fixture
    def sample_request(self):
        """Create a sample request for testing."""
        return Request(
            method="GET", url="/api/test", headers={"User-Agent": "TestClient/1.0"}
        )

    @pytest.fixture
    def sample_response(self):
        """Create a sample response for testing."""
        return Response(content={"message": "success"}, status_code=200)

    async def test_middleware_base_functionality(self, sample_request, sample_response):
        """Test basic middleware functionality."""

        class TestMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                # Add request processing
                request.state.processed_by = "TestMiddleware"

                # Call next middleware/handler
                response = await call_next(request)

                # Add response processing
                response.headers["X-Processed-By"] = "TestMiddleware"
                return response

        middleware = TestMiddleware()

        # Mock next handler
        async def mock_handler(request):
            return sample_response

        # Process request through middleware
        response = await middleware.dispatch(sample_request, mock_handler)

        assert hasattr(sample_request.state, "processed_by")
        assert sample_request.state.processed_by == "TestMiddleware"
        assert response.headers["X-Processed-By"] == "TestMiddleware"

    async def test_middleware_exception_handling(self, sample_request):
        """Test middleware exception handling."""

        class ExceptionTestMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    return await call_next(request)
                except ValueError as e:
                    return Response(content={"error": str(e)}, status_code=400)

        middleware = ExceptionTestMiddleware()

        # Mock handler that raises exception
        async def failing_handler(request):
            raise ValueError("Test error")

        response = await middleware.dispatch(sample_request, failing_handler)

        assert response.status_code == 400
        assert response.content["error"] == "Test error"

    async def test_middleware_async_processing(self, sample_request, sample_response):
        """Test asynchronous middleware processing."""

        class AsyncMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                # Simulate async operation
                await asyncio.sleep(0.001)
                request.state.async_processed = True

                response = await call_next(request)

                # Another async operation
                await asyncio.sleep(0.001)
                response.headers["X-Async-Processed"] = "true"

                return response

        middleware = AsyncMiddleware()

        async def mock_handler(request):
            return sample_response

        start_time = time.time()
        response = await middleware.dispatch(sample_request, mock_handler)
        end_time = time.time()

        # Should take at least 2ms due to sleep
        assert (end_time - start_time) >= 0.002
        assert sample_request.state.async_processed is True
        assert response.headers["X-Async-Processed"] == "true"


class TestMiddlewarePipeline:
    """Test middleware pipeline execution."""

    @pytest.fixture
    def sample_request(self):
        return Request(method="GET", url="/api/test")

    @pytest.fixture
    def sample_response(self):
        return Response(content={"message": "success"})

    async def test_pipeline_execution_order(self, sample_request, sample_response):
        """Test middleware pipeline execution order."""
        execution_order = []

        class OrderTestMiddleware(BaseHTTPMiddleware):
            def __init__(self, name: str):
                self.name = name

            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                execution_order.append(f"{self.name}_request")
                response = await call_next(request)
                execution_order.append(f"{self.name}_response")
                return response

        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(OrderTestMiddleware("First"))
        pipeline.add_middleware(OrderTestMiddleware("Second"))
        pipeline.add_middleware(OrderTestMiddleware("Third"))

        async def final_handler(request):
            execution_order.append("handler")
            return sample_response

        await pipeline.process(sample_request, final_handler)

        # Should execute in order: First, Second, Third, handler, Third, Second, First
        expected_order = [
            "First_request",
            "Second_request",
            "Third_request",
            "handler",
            "Third_response",
            "Second_response",
            "First_response",
        ]
        assert execution_order == expected_order

    async def test_pipeline_early_response(self, sample_request):
        """Test middleware that returns early response."""

        class EarlyResponseMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                if request.headers.get("X-Skip") == "true":
                    return Response(content={"skipped": True}, status_code=200)
                return await call_next(request)

        class NeverCalledMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                # This should never be called
                request.state.never_called_reached = True
                return await call_next(request)

        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(EarlyResponseMiddleware())
        pipeline.add_middleware(NeverCalledMiddleware())

        # Add skip header
        sample_request.headers["X-Skip"] = "true"

        async def final_handler(request):
            request.state.handler_reached = True
            return Response(content={"from_handler": True})

        response = await pipeline.process(sample_request, final_handler)

        # Should return early response
        assert response.content["skipped"] is True
        assert not hasattr(sample_request.state, "never_called_reached")
        assert not hasattr(sample_request.state, "handler_reached")

    async def test_pipeline_exception_propagation(self, sample_request):
        """Test exception propagation through pipeline."""

        class ExceptionMiddleware(BaseHTTPMiddleware):
            async def dispatch(self, request: Request, call_next: Callable) -> Response:
                try:
                    return await call_next(request)
                except Exception as e:
                    request.state.exception_caught = str(e)
                    raise

        pipeline = MiddlewarePipeline()
        pipeline.add_middleware(ExceptionMiddleware())

        async def failing_handler(request):
            raise ValueError("Test exception")

        with pytest.raises(ValueError, match="Test exception"):
            await pipeline.process(sample_request, failing_handler)

        assert sample_request.state.exception_caught == "Test exception"


class TestCORSMiddleware:
    """Test CORS middleware functionality."""

    @pytest.fixture
    def cors_middleware(self):
        return CORSMiddleware(
            allow_origins=["https://example.com", "https://app.example.com"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Content-Type", "Authorization", "X-Custom-Header"],
            expose_headers=["X-Total-Count"],
            allow_credentials=True,
            max_age=3600,
        )

    async def test_cors_simple_request(self, cors_middleware):
        """Test CORS handling for simple requests."""
        request = Request(
            method="GET", url="/api/data", headers={"Origin": "https://example.com"}
        )

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await cors_middleware.dispatch(request, mock_handler)

        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert response.headers["Access-Control-Allow-Credentials"] == "true"
        assert "X-Total-Count" in response.headers["Access-Control-Expose-Headers"]

    async def test_cors_preflight_request(self, cors_middleware):
        """Test CORS preflight request handling."""
        request = Request(
            method="OPTIONS",
            url="/api/data",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            },
        )

        async def mock_handler(request):
            return Response(content={"should_not_reach": True})

        response = await cors_middleware.dispatch(request, mock_handler)

        # Should return preflight response without calling handler
        assert response.status_code == 200
        assert "should_not_reach" not in response.content
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert "POST" in response.headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]
        assert response.headers["Access-Control-Max-Age"] == "3600"

    async def test_cors_origin_validation(self, cors_middleware):
        """Test CORS origin validation."""
        # Disallowed origin
        request = Request(
            method="GET", url="/api/data", headers={"Origin": "https://malicious.com"}
        )

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await cors_middleware.dispatch(request, mock_handler)

        # Should not include CORS headers for disallowed origin
        assert "Access-Control-Allow-Origin" not in response.headers

    async def test_cors_wildcard_origin(self):
        """Test CORS with wildcard origin."""
        cors_middleware = CORSMiddleware(allow_origins=["*"])

        request = Request(
            method="GET", url="/api/data", headers={"Origin": "https://any-domain.com"}
        )

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await cors_middleware.dispatch(request, mock_handler)

        assert response.headers["Access-Control-Allow-Origin"] == "*"

    async def test_cors_no_origin_header(self, cors_middleware):
        """Test CORS handling when no Origin header is present."""
        request = Request(method="GET", url="/api/data")

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await cors_middleware.dispatch(request, mock_handler)

        # Should not add CORS headers when no Origin header
        assert "Access-Control-Allow-Origin" not in response.headers


class TestRequestLoggingMiddleware:
    """Test request logging middleware."""

    @pytest.fixture
    def logger_mock(self):
        return MagicMock()

    @pytest.fixture
    def logging_middleware(self, logger_mock):
        return RequestLoggingMiddleware(
            logger=logger_mock,
            include_headers=True,
            include_body=True,
            mask_sensitive=True,
        )

    async def test_request_logging_basic(self, logging_middleware, logger_mock):
        """Test basic request logging."""
        request = Request(
            method="POST",
            url="/api/users",
            headers={"Content-Type": "application/json"},
            body=b'{"name": "test"}',
        )

        async def mock_handler(request):
            return Response(content={"id": 123}, status_code=201)

        await logging_middleware.dispatch(request, mock_handler)

        # Verify logging calls
        assert logger_mock.info.called
        log_calls = [call.args[0] for call in logger_mock.info.call_args_list]

        # Should log request start and completion
        assert any("POST /api/users" in call for call in log_calls)
        assert any("201" in call for call in log_calls)

    async def test_request_logging_with_timing(self, logging_middleware, logger_mock):
        """Test request logging with timing information."""
        request = Request(method="GET", url="/api/slow")

        async def slow_handler(request):
            await asyncio.sleep(0.01)  # 10ms delay
            return Response(content={"data": "slow"})

        await logging_middleware.dispatch(request, slow_handler)

        # Should log timing information
        log_calls = [call.args[0] for call in logger_mock.info.call_args_list]
        assert any("ms" in call for call in log_calls)

    async def test_request_logging_sensitive_data_masking(
        self, logging_middleware, logger_mock
    ):
        """Test masking of sensitive data in logs."""
        request = Request(
            method="POST",
            url="/api/auth",
            headers={
                "Authorization": "Bearer secret_token_123",
                "X-API-Key": "api_key_456",
            },
            body=b'{"password": "secret123", "email": "user@example.com"}',
        )

        async def mock_handler(request):
            return Response(content={"success": True})

        await logging_middleware.dispatch(request, mock_handler)

        # Verify sensitive data is masked
        log_output = " ".join(
            [call.args[0] for call in logger_mock.info.call_args_list]
        )
        assert "secret_token_123" not in log_output
        assert "secret123" not in log_output
        assert "***" in log_output or "MASKED" in log_output

    async def test_request_logging_error_handling(
        self, logging_middleware, logger_mock
    ):
        """Test logging of request errors."""
        request = Request(method="GET", url="/api/error")

        async def failing_handler(request):
            raise ValueError("Something went wrong")

        with pytest.raises(ValueError):
            await logging_middleware.dispatch(request, failing_handler)

        # Should log the error
        assert logger_mock.error.called
        error_log = logger_mock.error.call_args[0][0]
        assert "ValueError" in error_log
        assert "Something went wrong" in error_log


class TestExceptionMiddleware:
    """Test exception handling middleware."""

    @pytest.fixture
    def exception_middleware(self):
        return ExceptionMiddleware(debug=True, include_traceback=True)

    async def test_exception_handling_http_exception(self, exception_middleware):
        """Test handling of HTTP exceptions."""
        request = Request(method="GET", url="/api/not-found")

        async def handler_with_http_error(request):
            raise HTTPException(status_code=404, detail="Resource not found")

        response = await exception_middleware.dispatch(request, handler_with_http_error)

        assert response.status_code == 404
        assert "error" in response.content
        assert response.content["error"]["message"] == "Resource not found"

    async def test_exception_handling_generic_exception(self, exception_middleware):
        """Test handling of generic exceptions."""
        request = Request(method="GET", url="/api/error")

        async def handler_with_error(request):
            raise ValueError("Invalid input data")

        response = await exception_middleware.dispatch(request, handler_with_error)

        assert response.status_code == 500
        assert "error" in response.content
        assert "Internal Server Error" in response.content["error"]["message"]

    async def test_exception_handling_with_debug(self, exception_middleware):
        """Test exception handling in debug mode."""
        request = Request(method="GET", url="/api/debug-error")

        async def handler_with_error(request):
            return Response(content={"unreachable": True})

        response = await exception_middleware.dispatch(request, handler_with_error)

        assert response.status_code == 500
        # In debug mode, should include traceback
        assert "traceback" in response.content["error"]
        assert "ZeroDivisionError" in response.content["error"]["traceback"]

    async def test_exception_handling_production_mode(self):
        """Test exception handling in production mode."""
        exception_middleware = ExceptionMiddleware(debug=False, include_traceback=False)
        request = Request(method="GET", url="/api/prod-error")

        async def handler_with_error(request):
            raise RuntimeError("Sensitive production error")

        response = await exception_middleware.dispatch(request, handler_with_error)

        assert response.status_code == 500
        # In production mode, should not leak sensitive information
        assert "Sensitive production error" not in str(response.content)
        assert "traceback" not in response.content.get("error", {})


class TestRateLimitMiddleware:
    """Test rate limiting middleware."""

    @pytest.fixture
    def rate_limit_middleware(self):
        return RateLimitMiddleware(
            max_requests=5,
            window_seconds=60,
            key_func=lambda request: request.client_ip or "anonymous",
        )

    async def test_rate_limiting_within_limit(self, rate_limit_middleware):
        """Test requests within rate limit."""
        request = Request(method="GET", url="/api/data", client_ip="192.168.1.100")

        async def mock_handler(request):
            return Response(content={"data": "test"})

        # Make requests within limit
        for _i in range(3):
            response = await rate_limit_middleware.dispatch(request, mock_handler)
            assert response.status_code == 200
            assert response.content["data"] == "test"

    async def test_rate_limiting_exceeded(self, rate_limit_middleware):
        """Test rate limit exceeded."""
        request = Request(method="GET", url="/api/data", client_ip="192.168.1.101")

        async def mock_handler(request):
            return Response(content={"data": "test"})

        # Exhaust rate limit
        for _i in range(5):
            response = await rate_limit_middleware.dispatch(request, mock_handler)
            assert response.status_code == 200

        # Next request should be rate limited
        response = await rate_limit_middleware.dispatch(request, mock_handler)
        assert response.status_code == 429
        assert "rate limit exceeded" in response.content["error"].lower()

    async def test_rate_limiting_headers(self, rate_limit_middleware):
        """Test rate limiting response headers."""
        request = Request(method="GET", url="/api/data", client_ip="192.168.1.102")

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await rate_limit_middleware.dispatch(request, mock_handler)

        # Should include rate limiting headers
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers
        assert "X-RateLimit-Reset" in response.headers

        assert int(response.headers["X-RateLimit-Limit"]) == 5
        assert int(response.headers["X-RateLimit-Remaining"]) == 4

    async def test_rate_limiting_different_clients(self, rate_limit_middleware):
        """Test rate limiting for different clients."""

        async def mock_handler(request):
            return Response(content={"data": "test"})

        # Client 1
        request1 = Request(method="GET", url="/api/data", client_ip="192.168.1.100")
        # Client 2
        request2 = Request(method="GET", url="/api/data", client_ip="192.168.1.200")

        # Each client should have independent rate limits
        for _i in range(5):
            response1 = await rate_limit_middleware.dispatch(request1, mock_handler)
            response2 = await rate_limit_middleware.dispatch(request2, mock_handler)

            assert response1.status_code == 200
            assert response2.status_code == 200


class TestGZipMiddleware:
    """Test GZip compression middleware."""

    @pytest.fixture
    def gzip_middleware(self):
        return GZipMiddleware(minimum_size=1024, compression_level=6)

    async def test_gzip_compression_large_response(self, gzip_middleware):
        """Test GZip compression for large responses."""
        large_content = "Hello, World! " * 1000  # > 1024 bytes

        request = Request(
            method="GET", url="/api/large", headers={"Accept-Encoding": "gzip, deflate"}
        )

        async def mock_handler(request):
            return Response(content=large_content, media_type="text/plain")

        response = await gzip_middleware.dispatch(request, mock_handler)

        # Should be compressed
        assert response.headers.get("Content-Encoding") == "gzip"
        assert "Content-Length" in response.headers
        # Compressed size should be smaller
        compressed_size = int(response.headers["Content-Length"])
        original_size = len(large_content.encode())
        assert compressed_size < original_size

    async def test_gzip_no_compression_small_response(self, gzip_middleware):
        """Test no compression for small responses."""
        small_content = "Small response"  # < 1024 bytes

        request = Request(
            method="GET", url="/api/small", headers={"Accept-Encoding": "gzip"}
        )

        async def mock_handler(request):
            return Response(content=small_content, media_type="text/plain")

        response = await gzip_middleware.dispatch(request, mock_handler)

        # Should not be compressed
        assert "Content-Encoding" not in response.headers

    async def test_gzip_no_compression_unsupported_client(self, gzip_middleware):
        """Test no compression when client doesn't support it."""
        large_content = "Hello, World! " * 1000

        request = Request(
            method="GET",
            url="/api/large",
            headers={"Accept-Encoding": "identity"},  # No gzip support
        )

        async def mock_handler(request):
            return Response(content=large_content, media_type="text/plain")

        response = await gzip_middleware.dispatch(request, mock_handler)

        # Should not be compressed
        assert "Content-Encoding" not in response.headers

    async def test_gzip_compression_json_response(self, gzip_middleware):
        """Test GZip compression for JSON responses."""
        large_data = {"items": [{"id": i, "name": f"Item {i}"} for i in range(100)]}

        request = Request(
            method="GET",
            url="/api/items",
            headers={"Accept-Encoding": "gzip, deflate, br"},
        )

        async def mock_handler(request):
            return Response(content=large_data)

        response = await gzip_middleware.dispatch(request, mock_handler)

        # JSON responses should be compressed if large enough
        assert response.headers.get("Content-Encoding") == "gzip"
        assert response.headers.get("Content-Type") == "application/json"


class TestSecurityHeadersMiddleware:
    """Test security headers middleware."""

    @pytest.fixture
    def security_middleware(self):
        return SecurityHeadersMiddleware(
            include_x_frame_options=True,
            include_x_content_type_options=True,
            include_x_xss_protection=True,
            include_strict_transport_security=True,
            include_content_security_policy=True,
            csp_policy="default-src 'self'; script-src 'self' 'unsafe-inline'",
        )

    async def test_security_headers_added(self, security_middleware):
        """Test that security headers are added to responses."""
        request = Request(method="GET", url="/api/data")

        async def mock_handler(request):
            return Response(content={"data": "test"})

        response = await security_middleware.dispatch(request, mock_handler)

        # Verify security headers
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert "Strict-Transport-Security" in response.headers
        assert "Content-Security-Policy" in response.headers
        assert "default-src 'self'" in response.headers["Content-Security-Policy"]

    async def test_security_headers_https_only(self, security_middleware):
        """Test HTTPS-only security headers."""
        # HTTP request
        http_request = Request(
            method="GET", url="/api/data", headers={"X-Forwarded-Proto": "http"}
        )

        # HTTPS request
        https_request = Request(
            method="GET", url="/api/data", headers={"X-Forwarded-Proto": "https"}
        )

        async def mock_handler(request):
            return Response(content={"data": "test"})

        http_response = await security_middleware.dispatch(http_request, mock_handler)
        https_response = await security_middleware.dispatch(https_request, mock_handler)

        # HSTS should only be set for HTTPS
        assert "Strict-Transport-Security" not in http_response.headers
        assert "Strict-Transport-Security" in https_response.headers


@pytest.mark.performance
class TestMiddlewarePerformance:
    """Test middleware performance characteristics."""

    async def test_middleware_pipeline_performance(self):
        """Test performance of middleware pipeline with multiple middlewares."""
        import time

        # Create multiple lightweight middlewares
        middlewares = []
        for i in range(10):

            class TestMiddleware(BaseHTTPMiddleware):
                def __init__(self, id):
                    self.id = id

                async def dispatch(self, request, call_next):
                    request.state.__dict__[f"middleware_{self.id}"] = True
                    response = await call_next(request)
                    response.headers[f"X-Middleware-{self.id}"] = "processed"
                    return response

            middlewares.append(TestMiddleware(i))

        pipeline = MiddlewarePipeline()
        for middleware in middlewares:
            pipeline.add_middleware(middleware)

        async def final_handler(request):
            return Response(content={"message": "success"})

        # Measure pipeline performance
        start_time = time.perf_counter()

        for _ in range(100):
            request = Request(method="GET", url="/api/test")
            await pipeline.process(request, final_handler)

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 100

        # Should be fast even with multiple middlewares
        assert (
            avg_time < 0.01
        ), f"Middleware pipeline too slow: {avg_time:.4f}s per request"

    async def test_cors_middleware_performance(self):
        """Test CORS middleware performance."""
        import time

        cors_middleware = CORSMiddleware(
            allow_origins=["*"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["*"],
        )

        async def mock_handler(request):
            return Response(content={"data": "test"})

        start_time = time.perf_counter()

        for _ in range(1000):
            request = Request(
                method="GET", url="/api/test", headers={"Origin": "https://example.com"}
            )
            await cors_middleware.dispatch(request, mock_handler)

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 1000

        # CORS processing should be very fast
        assert (
            avg_time < 0.001
        ), f"CORS middleware too slow: {avg_time:.4f}s per request"
