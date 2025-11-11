"""
Comprehensive Tests for CovetPy Middleware System

Tests all aspects of the middleware system:
- Core middleware functionality
- Pipeline execution and ordering
- Built-in middleware components
- Error handling and edge cases
- Performance characteristics
"""

import asyncio
import gzip
import json
import logging
import secrets
import time
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock

import pytest

from .builtin_middleware import (
    CompressionMiddleware,
    CORSMiddleware,
    CSRFMiddleware,
    RateLimitingMiddleware,
    RateLimitRule,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    SessionMiddleware,
)
from .exceptions import HTTPException
from .http import Request, Response, json_response
from .middleware_system import (
    BaseMiddleware,
    FunctionMiddleware,
    MiddlewareComposer,
    MiddlewareConfig,
    MiddlewareContext,
    MiddlewareStack,
    Priority,
    add_middleware_context,
    middleware,
    route_middleware,
)

logger = logging.getLogger(__name__)


# Mock objects for testing
class MockRequest:
    """Mock request object for testing"""

    def __init__(
        self,
        method: str = "GET",
        path: str = "/",
        headers: Optional[Dict[str, str]] = None,
        remote_addr: str = "127.0.0.1",
        scheme: str = "https",
        body: bytes = b"",
        query_string: str = "",
    ):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.remote_addr = remote_addr
        self.scheme = scheme
        self._body = body
        self.query_string = query_string
        self.context = {}
        self.request_id = f"test_{int(time.time() * 1000)}"

    def cookies(self) -> Dict[str, str]:
        cookie_header = self.headers.get("cookie", "")
        cookies = {}
        if cookie_header:
            for part in cookie_header.split(";"):
                if "=" in part:
                    key, value = part.strip().split("=", 1)
                    cookies[key] = value
        return cookies

    def is_form(self) -> bool:
        return "application/x-www-form-urlencoded" in self.headers.get("content-type", "")

    def get_body_bytes(self) -> bytes:
        return self._body

    @property
    def content_type(self) -> str:
        return self.headers.get("content-type", "")


class MockResponse:
    """Mock response object for testing"""

    def __init__(
        self,
        content: str = "",
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        self._content_bytes = None

    def get_content_bytes(self) -> bytes:
        if self._content_bytes is None:
            if isinstance(self.content, str):
                self._content_bytes = self.content.encode("utf-8")
            elif isinstance(self.content, bytes):
                self._content_bytes = self.content
            else:
                self._content_bytes = str(self.content).encode("utf-8")
        return self._content_bytes

    def set_cookie(self, name: str, value: str, **kwargs):
        """Mock cookie setting"""
        if "Set-Cookie" not in self.headers:
            self.headers["Set-Cookie"] = []
        elif not isinstance(self.headers["Set-Cookie"], list):
            self.headers["Set-Cookie"] = [self.headers["Set-Cookie"]]

        cookie_parts = [f"{name}={value}"]
        for key, val in kwargs.items():
            if val is True:
                cookie_parts.append(key.replace("_", "-"))
            elif val is not False and val is not None:
                cookie_parts.append(f"{key.replace('_', '-')}={val}")

        self.headers["Set-Cookie"].append("; ".join(cookie_parts))


# Test fixtures
@pytest.fixture
def mock_request():
    return MockRequest()


@pytest.fixture
def mock_response():
    return MockResponse("Test response")


@pytest.fixture
def middleware_stack():
    return MiddlewareStack()


@pytest.fixture
async def mock_handler():
    async def handler(request):
        return MockResponse("Handler response")

    return handler


# Core Middleware System Tests
class TestMiddlewareSystem:
    """Test core middleware system functionality"""

    async def test_base_middleware_abstract(self):
        """Test that BaseMiddleware is abstract"""
        with pytest.raises(TypeError):
            BaseMiddleware()

    async def test_middleware_config(self):
        """Test middleware configuration"""
        config = MiddlewareConfig(
            name="test_middleware",
            priority=100,
            routes=["/api/*"],
            exclude_routes=["/api/health"],
            conditions={"method": ["POST"]},
            options={"key": "value"},
        )

        assert config.name == "test_middleware"
        assert config.priority == 100
        assert config.routes == ["/api/*"]
        assert config.exclude_routes == ["/api/health"]
        assert config.conditions == {"method": ["POST"]}
        assert config.options == {"key": "value"}

    async def test_function_middleware_creation(self):
        """Test creating middleware from functions"""

        @middleware(name="test_func", priority=Priority.HIGH.value)
        async def test_middleware_func(request, call_next):
            response = await call_next(request)
            response.headers["X-Test"] = "middleware"
            return response

        assert isinstance(test_middleware_func, FunctionMiddleware)
        assert test_middleware_func.config.name == "test_func"
        assert test_middleware_func.config.priority == Priority.HIGH.value

    async def test_route_middleware_decorator(self):
        """Test route-specific middleware decorator"""

        @route_middleware("/api/*", priority=Priority.NORMAL.value)
        async def api_middleware(request, call_next):
            return await call_next(request)

        assert isinstance(api_middleware, FunctionMiddleware)
        assert api_middleware.config.routes == ["/api/*"]

    async def test_middleware_stack_execution(self, middleware_stack, mock_request, mock_handler):
        """Test middleware stack execution order"""
        execution_order = []

        class TestMiddleware1(BaseMiddleware):
            async def process_request(self, request):
                execution_order.append("middleware1_request")
                return request

            async def process_response(self, request, response):
                execution_order.append("middleware1_response")
                return response

        class TestMiddleware2(BaseMiddleware):
            async def process_request(self, request):
                execution_order.append("middleware2_request")
                return request

            async def process_response(self, request, response):
                execution_order.append("middleware2_response")
                return response

        # Add middleware with different priorities
        middleware_stack.add(TestMiddleware1(MiddlewareConfig(priority=100)))
        middleware_stack.add(TestMiddleware2(MiddlewareConfig(priority=50)))

        async def test_handler(request):
            execution_order.append("handler")
            return MockResponse("test")

        await middleware_stack.process(mock_request, test_handler)

        # Check execution order (lower priority runs first)
        assert execution_order == [
            "middleware2_request",
            "middleware1_request",
            "handler",
            "middleware1_response",
            "middleware2_response",
        ]

    async def test_middleware_conditional_execution(self, middleware_stack, mock_handler):
        """Test conditional middleware execution"""

        class ConditionalMiddleware(BaseMiddleware):
            def __init__(self):
                config = MiddlewareConfig(
                    routes=["/api/*"],
                    exclude_routes=["/api/health"],
                    conditions={"method": ["POST"]},
                )
                super().__init__(config)
                self.executed = False

            async def process_request(self, request):
                self.executed = True
                return request

            async def process_response(self, request, response):
                return response

        middleware = ConditionalMiddleware()
        middleware_stack.add(middleware)

        # Test matching request
        request1 = MockRequest(method="POST", path="/api/users")
        await middleware_stack.process(request1, mock_handler)
        assert middleware.executed

        # Test non-matching request (wrong method)
        middleware.executed = False
        request2 = MockRequest(method="GET", path="/api/users")
        await middleware_stack.process(request2, mock_handler)
        assert not middleware.executed

        # Test excluded route
        middleware.executed = False
        request3 = MockRequest(method="POST", path="/api/health")
        await middleware_stack.process(request3, mock_handler)
        assert not middleware.executed

    async def test_middleware_error_handling(self, middleware_stack):
        """Test middleware error handling"""

        class ErrorHandlingMiddleware(BaseMiddleware):
            async def process_request(self, request):
                return request

            async def process_response(self, request, response):
                return response

            async def process_error(self, request, error):
                if isinstance(error, ValueError):
                    return MockResponse("Error handled", status_code=400)
                return None

        middleware_stack.add(ErrorHandlingMiddleware())

        async def error_handler(request):
            raise ValueError("Test error")

        response = await middleware_stack.process(MockRequest(), error_handler)
        assert response.status_code == 400
        assert response.content == "Error handled"

    async def test_middleware_short_circuit(self, middleware_stack):
        """Test middleware short-circuiting"""

        class ShortCircuitMiddleware(BaseMiddleware):
            async def process_request(self, request):
                if request.path == "/blocked":
                    return MockResponse("Blocked", status_code=403)
                return request

            async def process_response(self, request, response):
                return response

        middleware_stack.add(ShortCircuitMiddleware())

        async def handler(request):
            return MockResponse("Normal response")

        # Test normal request
        response1 = await middleware_stack.process(MockRequest(path="/normal"), handler)
        assert response1.content == "Normal response"

        # Test blocked request
        response2 = await middleware_stack.process(MockRequest(path="/blocked"), handler)
        assert response2.status_code == 403
        assert response2.content == "Blocked"

    async def test_middleware_composition(self):
        """Test middleware composition"""

        async def middleware1(request, call_next):
            request.context["m1"] = True
            response = await call_next(request)
            response.headers["X-M1"] = "true"
            return response

        async def middleware2(request, call_next):
            request.context["m2"] = True
            response = await call_next(request)
            response.headers["X-M2"] = "true"
            return response

        composed = MiddlewareComposer.compose(
            FunctionMiddleware(middleware1), FunctionMiddleware(middleware2)
        )

        request = MockRequest()

        async def handler(req):
            return MockResponse("test")

        response = await composed(request, handler)

        assert request.context.get("m1") is True
        assert request.context.get("m2") is True
        assert response.headers.get("X-M1") == "true"
        assert response.headers.get("X-M2") == "true"


# Built-in Middleware Tests
class TestCORSMiddleware:
    """Test CORS middleware"""

    async def test_cors_preflight_request(self):
        """Test CORS preflight handling"""
        cors = CORSMiddleware(
            allow_origins=["https://example.com"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

        request = MockRequest(method="OPTIONS", headers={"origin": "https://example.com"})

        response = await cors.process_request(request)

        assert isinstance(response, MockResponse)
        assert response.status_code == 200
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert "GET, POST" in response.headers["Access-Control-Allow-Methods"]

    async def test_cors_actual_request(self):
        """Test CORS headers on actual requests"""
        cors = CORSMiddleware(allow_origins=["https://example.com"])

        request = MockRequest(headers={"origin": "https://example.com"})
        response = MockResponse("test")

        result = await cors.process_response(request, response)

        assert result.headers["Access-Control-Allow-Origin"] == "https://example.com"

    async def test_cors_wildcard_origin(self):
        """Test CORS with wildcard origin"""
        cors = CORSMiddleware(allow_origins=["*"])

        request = MockRequest(headers={"origin": "https://any-domain.com"})
        response = MockResponse("test")

        result = await cors.process_response(request, response)

        assert result.headers["Access-Control-Allow-Origin"] == "*"


class TestRateLimitingMiddleware:
    """Test rate limiting middleware"""

    async def test_rate_limiting_allowed(self):
        """Test request within rate limits"""
        rate_limiter = RateLimitingMiddleware(
            default_rule=RateLimitRule(requests=10, window=60),
            strategy="sliding_window",
        )

        request = MockRequest(remote_addr="192.168.1.1")
        result = await rate_limiter.process_request(request)

        assert isinstance(result, MockRequest)  # Request should pass through

    async def test_rate_limiting_exceeded(self):
        """Test request exceeding rate limits"""
        rate_limiter = RateLimitingMiddleware(
            default_rule=RateLimitRule(requests=1, window=60), strategy="sliding_window"
        )

        request = MockRequest(remote_addr="192.168.1.1")

        # First request should pass
        result1 = await rate_limiter.process_request(request)
        assert isinstance(result1, MockRequest)

        # Second request should be blocked
        result2 = await rate_limiter.process_request(request)
        assert isinstance(result2, MockResponse)
        assert result2.status_code == 429

    async def test_rate_limiting_different_ips(self):
        """Test rate limiting with different IP addresses"""
        rate_limiter = RateLimitingMiddleware(default_rule=RateLimitRule(requests=1, window=60))

        request1 = MockRequest(remote_addr="192.168.1.1")
        request2 = MockRequest(remote_addr="192.168.1.2")

        # Both requests should pass (different IPs)
        result1 = await rate_limiter.process_request(request1)
        result2 = await rate_limiter.process_request(request2)

        assert isinstance(result1, MockRequest)
        assert isinstance(result2, MockRequest)

    async def test_rate_limiting_strategies(self):
        """Test different rate limiting strategies"""
        strategies = ["sliding_window", "fixed_window", "token_bucket"]

        for strategy in strategies:
            rate_limiter = RateLimitingMiddleware(
                default_rule=RateLimitRule(requests=5, window=60), strategy=strategy
            )

            request = MockRequest(remote_addr=f"192.168.1.{strategy}")
            result = await rate_limiter.process_request(request)

            assert isinstance(result, MockRequest)


class TestSecurityHeadersMiddleware:
    """Test security headers middleware"""

    async def test_security_headers_https(self):
        """Test security headers for HTTPS requests"""
        security = SecurityHeadersMiddleware(hsts_max_age=31536000, csp_policy="default-src 'self'")

        request = MockRequest(scheme="https")
        response = MockResponse("test")

        result = await security.process_response(request, response)

        assert "Strict-Transport-Security" in result.headers
        assert "max-age=31536000" in result.headers["Strict-Transport-Security"]
        assert result.headers["X-Frame-Options"] == "DENY"
        assert result.headers["X-Content-Type-Options"] == "nosniff"
        assert result.headers["Content-Security-Policy"] == "default-src 'self'"

    async def test_security_headers_http(self):
        """Test security headers for HTTP requests (no HSTS)"""
        security = SecurityHeadersMiddleware()

        request = MockRequest(scheme="http")
        response = MockResponse("test")

        result = await security.process_response(request, response)

        assert "Strict-Transport-Security" not in result.headers
        assert result.headers["X-Frame-Options"] == "DENY"


class TestCompressionMiddleware:
    """Test compression middleware"""

    async def test_compression_gzip(self):
        """Test gzip compression"""
        compression = CompressionMiddleware(minimum_size=10)

        request = MockRequest(headers={"accept-encoding": "gzip"})
        response = MockResponse("This is a long response that should be compressed" * 10)
        response.headers["content-type"] = "text/html"

        # Process request to set up compression context
        await compression.process_request(request)

        # Process response
        result = await compression.process_response(request, response)

        assert result.headers.get("Content-Encoding") == "gzip"
        assert len(result.get_content_bytes()) < len(response.get_content_bytes())

    async def test_compression_skip_small_content(self):
        """Test compression skipping small content"""
        compression = CompressionMiddleware(minimum_size=1000)

        request = MockRequest(headers={"accept-encoding": "gzip"})
        response = MockResponse("small")
        response.headers["content-type"] = "text/html"

        await compression.process_request(request)
        result = await compression.process_response(request, response)

        assert "Content-Encoding" not in result.headers

    async def test_compression_skip_incompatible_types(self):
        """Test compression skipping incompatible content types"""
        compression = CompressionMiddleware()

        request = MockRequest(headers={"accept-encoding": "gzip"})
        response = MockResponse("x" * 2000)  # Large enough content
        # Non-compressible type
        response.headers["content-type"] = "image/jpeg"

        await compression.process_request(request)
        result = await compression.process_response(request, response)

        assert "Content-Encoding" not in result.headers


class TestSessionMiddleware:
    """Test session middleware"""

    async def test_session_creation(self):
        """Test session creation for new users"""
        session_middleware = SessionMiddleware(secret_key="test_secret")

        request = MockRequest()
        response = MockResponse("test")

        # Process request (should create new session)
        await session_middleware.process_request(request)

        assert hasattr(request, "session")
        assert request.context["session"]["new"] is True

        # Modify session
        request.session.set("user_id", 123)

        # Process response (should set cookie)
        result = await session_middleware.process_response(request, response)

        assert "Set-Cookie" in result.headers

    async def test_session_loading(self):
        """Test loading existing session"""
        session_middleware = SessionMiddleware(secret_key="test_secret")

        # Simulate existing session
        session_id = "test_session_id"
        signed_session = session_middleware._sign_session_id(session_id)
        session_middleware._save_session_data(session_id, {"user_id": 123})

        request = MockRequest(headers={"cookie": f"covet_session={signed_session}"})

        await session_middleware.process_request(request)

        assert request.session.get("user_id") == 123
        assert request.context["session"]["new"] is False


class TestCSRFMiddleware:
    """Test CSRF protection middleware"""

    async def test_csrf_get_request(self):
        """Test CSRF allows GET requests"""
        csrf = CSRFMiddleware(secret_key="test_secret")

        request = MockRequest(method="GET")
        result = await csrf.process_request(request)

        assert isinstance(result, MockRequest)  # Should pass through

    async def test_csrf_post_without_token(self):
        """Test CSRF blocks POST without token"""
        csrf = CSRFMiddleware(secret_key="test_secret")

        request = MockRequest(method="POST")
        result = await csrf.process_request(request)

        assert isinstance(result, MockResponse)
        assert result.status_code == 403

    async def test_csrf_post_with_valid_token(self):
        """Test CSRF allows POST with valid token"""
        csrf = CSRFMiddleware(secret_key="test_secret")

        # Generate token
        token = secrets.token_urlsafe(32)

        request = MockRequest(
            method="POST",
            headers={"cookie": f"csrf_token={token}", "x-csrftoken": token},
        )

        result = await csrf.process_request(request)

        assert isinstance(result, MockRequest)  # Should pass through


class TestRequestIDMiddleware:
    """Test request ID middleware"""

    async def test_request_id_generation(self):
        """Test request ID generation"""
        request_id_middleware = RequestIDMiddleware()

        request = MockRequest()
        response = MockResponse("test")

        await request_id_middleware.process_request(request)

        assert hasattr(request, "request_id")
        assert request.context["request_id"] == request.request_id

        result = await request_id_middleware.process_response(request, response)
        assert result.headers["X-Request-ID"] == request.request_id

    async def test_request_id_from_header(self):
        """Test using existing request ID from header"""
        request_id_middleware = RequestIDMiddleware()

        existing_id = "external-request-id-123"
        request = MockRequest(headers={"x-request-id": existing_id})

        await request_id_middleware.process_request(request)

        assert request.request_id == existing_id


# Performance Tests
class TestMiddlewarePerformance:
    """Test middleware performance characteristics"""

    async def test_middleware_stack_performance(self):
        """Test middleware stack performance with many middleware"""
        stack = MiddlewareStack()

        # Add many simple middleware
        for i in range(100):

            @middleware(name=f"middleware_{i}")
            async def simple_middleware(request, call_next):
                return await call_next(request)

            stack.add(simple_middleware)

        async def handler(request):
            return MockResponse("test")

        # Measure execution time
        start_time = time.time()
        for _ in range(10):
            await stack.process(MockRequest(), handler)
        end_time = time.time()

        # Should complete within reasonable time
        # Less than 1 second for 1000 executions
        assert (end_time - start_time) < 1.0

    async def test_rate_limiting_performance(self):
        """Test rate limiting performance under load"""
        rate_limiter = RateLimitingMiddleware(default_rule=RateLimitRule(requests=1000, window=60))

        # Simulate many requests
        start_time = time.time()
        for i in range(100):
            request = MockRequest(remote_addr=f"192.168.1.{i % 10}")
            await rate_limiter.process_request(request)
        end_time = time.time()

        # Should handle requests quickly
        assert (end_time - start_time) < 0.5  # Less than 500ms


# Integration Tests
class TestMiddlewareIntegration:
    """Test middleware integration scenarios"""

    async def test_full_middleware_stack(self):
        """Test full production middleware stack"""
        stack = MiddlewareStack()

        # Add all production middleware
        stack.add(RequestIDMiddleware())
        stack.add(SecurityHeadersMiddleware(csp_policy="default-src 'self'"))
        stack.add(CORSMiddleware(allow_origins=["https://example.com"]))
        stack.add(RateLimitingMiddleware(default_rule=RateLimitRule(100, 60)))
        stack.add(CompressionMiddleware())
        stack.add(RequestLoggingMiddleware())

        request = MockRequest(
            method="POST",
            path="/api/users",
            headers={
                "origin": "https://example.com",
                "accept-encoding": "gzip",
                "content-type": "application/json",
            },
        )

        async def handler(req):
            return MockResponse(json.dumps({"id": 1, "name": "Test User"}))

        response = await stack.process(request, handler)

        # Verify all middleware effects
        assert "X-Request-ID" in response.headers
        assert "X-Frame-Options" in response.headers
        assert "Access-Control-Allow-Origin" in response.headers
        assert hasattr(request, "request_id")

    async def test_middleware_error_propagation(self):
        """Test error propagation through middleware stack"""
        stack = MiddlewareStack()

        class ErrorMiddleware(BaseMiddleware):
            async def process_request(self, request):
                return request

            async def process_response(self, request, response):
                return response

            async def process_error(self, request, error):
                # Handle specific errors
                if isinstance(error, ValueError):
                    return MockResponse(f"Handled: {str(error)}", status_code=400)
                return None

        stack.add(ErrorMiddleware())

        async def error_handler(request):
            if request.path == "/error":
                raise ValueError("Test error")
            return MockResponse("OK")

        # Test error handling
        error_response = await stack.process(MockRequest(path="/error"), error_handler)
        assert error_response.status_code == 400
        assert "Handled: Test error" in error_response.content

        # Test normal operation
        normal_response = await stack.process(MockRequest(path="/normal"), error_handler)
        assert normal_response.content == "OK"


# Utility Tests
class TestMiddlewareUtilities:
    """Test middleware utility functions and classes"""

    async def test_middleware_context(self):
        """Test middleware context functionality"""
        context = MiddlewareContext()

        # Test basic operations
        context.set("key1", "value1")
        assert context.get("key1") == "value1"
        assert context.has("key1")

        context.set("key2", {"nested": "data"})
        assert context.get("key2")["nested"] == "data"

        # Test default values
        assert context.get("nonexistent", "default") == "default"

        # Test deletion
        context.delete("key1")
        assert not context.has("key1")

        # Test clear
        context.clear()
        assert not context.has("key2")

        # Test request ID generation
        request_id = context.request_id
        assert isinstance(request_id, str)
        assert len(request_id) > 0

    async def test_add_middleware_context_to_request(self):
        """Test adding middleware context to request objects"""
        request = MockRequest()

        context = add_middleware_context(request)

        assert hasattr(request, "middleware_context")
        assert isinstance(context, MiddlewareContext)
        assert request.middleware_context is context

        # Test idempotent behavior
        context2 = add_middleware_context(request)
        assert context2 is context


if __name__ == "__main__":
    # Run tests if executed directly
    import sys

    # Simple test runner for development
    async def run_tests():
        test_classes = [
            TestMiddlewareSystem,
            TestCORSMiddleware,
            TestRateLimitingMiddleware,
            TestSecurityHeadersMiddleware,
            TestCompressionMiddleware,
            TestSessionMiddleware,
            TestCSRFMiddleware,
            TestRequestIDMiddleware,
            TestMiddlewarePerformance,
            TestMiddlewareIntegration,
            TestMiddlewareUtilities,
        ]

        total_tests = 0
        passed_tests = 0

        for test_class in test_classes:
            logger.info("\\nRunning {test_class.__name__}...")

            instance = test_class()
            methods = [m for m in dir(instance) if m.startswith("test_")]

            for method_name in methods:
                total_tests += 1
                try:
                    method = getattr(instance, method_name)
                    if asyncio.iscoroutinefunction(method):
                        await method()
                    else:
                        method()
                    logger.info("  ✓ {method_name}")
                    passed_tests += 1
                except Exception:
                    logger.info("  ✗ {method_name}: {e}")

        logger.info("\\nTest Results: {passed_tests}/{total_tests} passed")

        if passed_tests == total_tests:
            logger.info("All tests passed! 🎉")
            sys.exit(0)
        else:
            logger.error("Some tests failed! ❌")
            sys.exit(1)

    # Run the tests
    asyncio.run(run_tests())
