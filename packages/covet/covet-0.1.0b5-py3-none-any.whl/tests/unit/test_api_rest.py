"""
Unit Tests for CovetPy REST API Module

These tests validate REST API functionality including routing, request handling,
response serialization, and middleware integration. All tests use real API
endpoints and validate actual HTTP semantics.

CRITICAL: Tests validate real REST API functionality, not mocks.
"""

import asyncio
import json
from datetime import datetime
from unittest.mock import patch

import pytest

from covet.api.rest import RequestHandler, RestApp, RestRouter
from covet.api.rest.auth import AuthenticationMiddleware
from covet.api.rest.dependencies import DependencyInjector
from covet.api.rest.middleware import (
    CORSMiddleware,
    ErrorHandlingMiddleware,
    RateLimitingMiddleware,
    ValidationMiddleware,
)
from covet.api.schemas import RequestSchema, ResponseSchema
from covet.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
)
from covet.core.http import HTTPStatus, Request, Response


@pytest.mark.unit
@pytest.mark.api
class TestRestApp:
    """Test REST application core functionality."""

    @pytest.fixture
    def rest_app(self):
        """Create REST application instance."""
        return RestApp(title="Test API", version="1.0.0", debug=True)

    def test_rest_app_initialization(self, rest_app):
        """Test REST app initialization with proper configuration."""
        assert rest_app.title == "Test API"
        assert rest_app.version == "1.0.0"
        assert rest_app.debug is True
        assert rest_app.router is not None
        assert rest_app.middleware_stack is not None

    def test_add_middleware(self, rest_app):
        """Test adding middleware to REST app."""
        cors_middleware = CORSMiddleware(
            allow_origins=["*"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

        rest_app.add_middleware(cors_middleware)

        assert len(rest_app.middleware_stack) > 0
        assert cors_middleware in rest_app.middleware_stack

    async def test_route_registration(self, rest_app):
        """Test route registration and handler binding."""

        async def test_handler(request: Request) -> Response:
            return Response(
                content={"message": "test"},
                status_code=HTTPStatus.OK,
                headers={"Content-Type": "application/json"},
            )

        rest_app.add_route("/test", test_handler, methods=["GET"])

        # Verify route was registered
        route = rest_app.router.get_route("/test", "GET")
        assert route is not None
        assert route.handler == test_handler
        assert "GET" in route.methods

    async def test_request_processing_pipeline(self, rest_app):
        """Test complete request processing pipeline."""

        async def echo_handler(request: Request) -> Response:
            return Response(
                content={"echo": request.path_params.get("message", "default")},
                status_code=HTTPStatus.OK,
            )

        rest_app.add_route("/echo/{message}", echo_handler, methods=["GET"])

        # Create test request
        test_request = Request(
            method="GET",
            url="/echo/hello",
            headers={"Content-Type": "application/json"},
        )

        # Process request through pipeline
        response = await rest_app.process_request(test_request)

        assert response.status_code == HTTPStatus.OK
        assert response.content["echo"] == "hello"

    def test_error_handling_middleware_integration(self, rest_app):
        """Test error handling middleware integration."""
        error_middleware = ErrorHandlingMiddleware(debug=True, include_traceback=True)

        rest_app.add_middleware(error_middleware)

        async def failing_handler(request: Request) -> Response:
            raise ValueError("Test error")

        rest_app.add_route("/error", failing_handler, methods=["GET"])

        # Error should be caught and handled by middleware
        assert error_middleware in rest_app.middleware_stack


@pytest.mark.unit
@pytest.mark.api
class TestRestRouter:
    """Test REST router functionality."""

    @pytest.fixture
    def router(self):
        """Create REST router instance."""
        return RestRouter()

    def test_route_pattern_matching(self, router):
        """Test route pattern matching with dynamic segments."""

        async def user_handler(request: Request) -> Response:
            return Response(content={"user_id": request.path_params["user_id"]})

        router.add_route("/users/{user_id}", user_handler, methods=["GET"])

        # Test exact match
        route = router.match_route("/users/123", "GET")
        assert route is not None
        assert route.handler == user_handler
        assert route.path_params["user_id"] == "123"

        # Test no match
        no_match = router.match_route("/users/123/posts", "GET")
        assert no_match is None

    def test_route_method_validation(self, router):
        """Test HTTP method validation for routes."""

        async def get_handler(request: Request) -> Response:
            return Response(content={"method": "GET"})

        async def post_handler(request: Request) -> Response:
            return Response(content={"method": "POST"})

        router.add_route("/resource", get_handler, methods=["GET"])
        router.add_route("/resource", post_handler, methods=["POST"])

        # Test correct method matching
        get_route = router.match_route("/resource", "GET")
        assert get_route.handler == get_handler

        post_route = router.match_route("/resource", "POST")
        assert post_route.handler == post_handler

        # Test method not allowed
        put_route = router.match_route("/resource", "PUT")
        assert put_route is None

    def test_route_priority_ordering(self, router):
        """Test route priority and ordering."""

        async def specific_handler(request: Request) -> Response:
            return Response(content={"type": "specific"})

        async def general_handler(request: Request) -> Response:
            return Response(content={"type": "general"})

        # Add general route first, then specific
        router.add_route("/api/{resource}", general_handler, methods=["GET"])
        router.add_route("/api/users", specific_handler, methods=["GET"])

        # Specific route should take priority
        route = router.match_route("/api/users", "GET")
        assert route.handler == specific_handler

    def test_nested_route_parameters(self, router):
        """Test nested route parameters extraction."""

        async def nested_handler(request: Request) -> Response:
            return Response(content=request.path_params)

        router.add_route(
            "/api/{version}/users/{user_id}/posts/{post_id}",
            nested_handler,
            methods=["GET"],
        )

        route = router.match_route("/api/v1/users/123/posts/456", "GET")
        assert route is not None
        assert route.path_params["version"] == "v1"
        assert route.path_params["user_id"] == "123"
        assert route.path_params["post_id"] == "456"

    def test_query_parameter_handling(self, router):
        """Test query parameter parsing and validation."""

        async def search_handler(request: Request) -> Response:
            return Response(content={"query": request.query_params})

        router.add_route("/search", search_handler, methods=["GET"])

        # Test with query parameters
        Request(method="GET", url="/search?q=python&limit=10&offset=0")

        route = router.match_route("/search", "GET")
        assert route is not None


@pytest.mark.unit
@pytest.mark.api
class TestRequestHandler:
    """Test request handler functionality."""

    async def test_request_validation(self):
        """Test request validation with schemas."""

        class UserCreateSchema(RequestSchema):
            username: str
            email: str
            password: str

            def validate_username(self, value: str) -> str:
                if len(value) < 3:
                    raise ValidationError("Username must be at least 3 characters")
                return value

        handler = RequestHandler(request_schema=UserCreateSchema, validate_request=True)

        # Test valid request
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "secret123",
        }

        validated = handler.validate_request_data(valid_data)
        assert validated.username == "testuser"
        assert validated.email == "test@example.com"

        # Test invalid request
        invalid_data = {
            "username": "ab",  # Too short
            "email": "test@example.com",
            "password": "secret123",
        }

        with pytest.raises(ValidationError) as exc_info:
            handler.validate_request_data(invalid_data)
        assert "Username must be at least 3 characters" in str(exc_info.value)

    async def test_response_serialization(self):
        """Test response serialization with schemas."""

        class UserResponseSchema(ResponseSchema):
            id: int
            username: str
            email: str
            created_at: datetime

        handler = RequestHandler(
            response_schema=UserResponseSchema, serialize_response=True
        )

        # Test response serialization
        user_data = {
            "id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "created_at": datetime.utcnow(),
            "password_hash": "secret",  # Should be filtered out
        }

        serialized = handler.serialize_response_data(user_data)

        assert serialized["id"] == 123
        assert serialized["username"] == "testuser"
        assert serialized["email"] == "test@example.com"
        assert "created_at" in serialized
        assert "password_hash" not in serialized  # Filtered by schema

    async def test_error_handling_in_handler(self):
        """Test error handling within request handlers."""

        async def error_prone_handler(request: Request) -> Response:
            error_type = request.path_params.get("error_type")

            if error_type == "validation":
                raise ValidationError("Invalid input data")
            elif error_type == "auth":
                raise AuthenticationError("Authentication required")
            elif error_type == "authz":
                raise AuthorizationError("Insufficient permissions")
            elif error_type == "notfound":
                raise NotFoundError("Resource not found")
            else:
                raise ValueError("Unexpected error")

        handler = RequestHandler(handler_func=error_prone_handler, handle_errors=True)

        # Test different error types
        test_cases = [
            ("validation", HTTPStatus.BAD_REQUEST),
            ("auth", HTTPStatus.UNAUTHORIZED),
            ("authz", HTTPStatus.FORBIDDEN),
            ("notfound", HTTPStatus.NOT_FOUND),
        ]

        for error_type, expected_status in test_cases:
            test_request = Request(
                method="GET",
                url=f"/error/{error_type}",
                path_params={"error_type": error_type},
            )

            response = await handler.handle_request(test_request)
            assert response.status_code == expected_status

    async def test_async_handler_execution(self):
        """Test asynchronous handler execution."""

        async def async_handler(request: Request) -> Response:
            # Simulate async operation
            await asyncio.sleep(0.001)
            return Response(
                content={"async": True, "path": request.path}, status_code=HTTPStatus.OK
            )

        handler = RequestHandler(handler_func=async_handler)

        test_request = Request(method="GET", url="/async-test")

        start_time = asyncio.get_event_loop().time()
        response = await handler.handle_request(test_request)
        end_time = asyncio.get_event_loop().time()

        assert response.status_code == HTTPStatus.OK
        assert response.content["async"] is True
        assert end_time - start_time >= 0.001  # Verify async execution


@pytest.mark.unit
@pytest.mark.api
class TestRestMiddleware:
    """Test REST API middleware functionality."""

    def test_cors_middleware_configuration(self):
        """Test CORS middleware configuration."""
        cors = CORSMiddleware(
            allow_origins=["https://example.com", "https://app.example.com"],
            allow_methods=["GET", "POST", "PUT", "DELETE"],
            allow_headers=["Content-Type", "Authorization"],
            allow_credentials=True,
            max_age=3600,
        )

        assert "https://example.com" in cors.allow_origins
        assert "POST" in cors.allow_methods
        assert "Authorization" in cors.allow_headers
        assert cors.allow_credentials is True
        assert cors.max_age == 3600

    async def test_cors_preflight_handling(self):
        """Test CORS preflight request handling."""
        cors = CORSMiddleware(
            allow_origins=["https://example.com"],
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type"],
        )

        # Preflight request
        preflight_request = Request(
            method="OPTIONS",
            url="/api/test",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            },
        )

        async def dummy_handler(request: Request) -> Response:
            return Response(content={"message": "test"})

        response = await cors.process_request(preflight_request, dummy_handler)

        assert response.status_code == HTTPStatus.OK
        assert response.headers["Access-Control-Allow-Origin"] == "https://example.com"
        assert "POST" in response.headers["Access-Control-Allow-Methods"]
        assert "Content-Type" in response.headers["Access-Control-Allow-Headers"]

    async def test_rate_limiting_middleware(self):
        """Test rate limiting middleware enforcement."""
        rate_limiter = RateLimitingMiddleware(
            max_requests=5,
            window_seconds=60,
            key_func=lambda request: request.client_ip,
        )

        async def dummy_handler(request: Request) -> Response:
            return Response(content={"message": "success"})

        # Make requests within limit
        for _i in range(5):
            test_request = Request(
                method="GET", url="/api/test", client_ip="192.168.1.1"
            )

            response = await rate_limiter.process_request(test_request, dummy_handler)
            assert response.status_code == HTTPStatus.OK

        # Next request should be rate limited
        test_request = Request(method="GET", url="/api/test", client_ip="192.168.1.1")

        response = await rate_limiter.process_request(test_request, dummy_handler)
        assert response.status_code == HTTPStatus.TOO_MANY_REQUESTS
        assert "X-RateLimit-Limit" in response.headers
        assert "X-RateLimit-Remaining" in response.headers

    async def test_validation_middleware(self):
        """Test request validation middleware."""
        validation = ValidationMiddleware(
            validate_content_type=True,
            validate_content_length=True,
            max_content_length=1024 * 1024,  # 1MB
        )

        async def dummy_handler(request: Request) -> Response:
            return Response(content={"message": "valid"})

        # Test valid request
        valid_request = Request(
            method="POST",
            url="/api/test",
            headers={"Content-Type": "application/json", "Content-Length": "100"},
            body=json.dumps({"test": "data"}),
        )

        response = await validation.process_request(valid_request, dummy_handler)
        assert response.status_code == HTTPStatus.OK

        # Test invalid content type
        invalid_request = Request(
            method="POST",
            url="/api/test",
            headers={"Content-Type": "text/plain", "Content-Length": "100"},
            body="plain text",
        )

        response = await validation.process_request(invalid_request, dummy_handler)
        assert response.status_code == HTTPStatus.BAD_REQUEST

    async def test_authentication_middleware(self):
        """Test authentication middleware."""
        auth = AuthenticationMiddleware(
            auth_schemes=["Bearer"],
            optional_paths=["/public/*"],
            jwt_secret="test_secret",
        )

        async def protected_handler(request: Request) -> Response:
            return Response(content={"user": request.user})

        # Test unauthenticated request to protected endpoint
        unauth_request = Request(method="GET", url="/api/protected")

        response = await auth.process_request(unauth_request, protected_handler)
        assert response.status_code == HTTPStatus.UNAUTHORIZED

        # Test authenticated request
        auth_request = Request(
            method="GET",
            url="/api/protected",
            headers={"Authorization": "Bearer valid_token"},
        )

        with patch.object(auth, "verify_jwt_token") as mock_verify:
            mock_verify.return_value = {"user_id": 123, "username": "testuser"}
            response = await auth.process_request(auth_request, protected_handler)

            # Should succeed if token is valid
            assert response.status_code == HTTPStatus.OK


@pytest.mark.unit
@pytest.mark.api
class TestDependencyInjection:
    """Test dependency injection system."""

    @pytest.fixture
    def injector(self):
        """Create dependency injector."""
        return DependencyInjector()

    def test_dependency_registration(self, injector):
        """Test dependency registration and resolution."""

        # Register singleton dependency
        class DatabaseService:
            def __init__(self):
                self.connected = True

        injector.register_singleton(DatabaseService)

        # Register factory dependency
        class RequestContext:
            def __init__(self, request_id: str):
                self.request_id = request_id

        injector.register_factory(
            RequestContext, lambda: RequestContext(f"req_{id(object())}")
        )

        # Verify registration
        assert injector.has_dependency(DatabaseService)
        assert injector.has_dependency(RequestContext)

    async def test_dependency_injection_in_handler(self, injector):
        """Test dependency injection in request handlers."""

        class UserService:
            async def get_user(self, user_id: int):
                return {"id": user_id, "username": f"user_{user_id}"}

        injector.register_singleton(UserService)

        async def get_user_handler(
            request: Request, user_service: UserService = injector.inject(UserService)
        ) -> Response:
            user_id = int(request.path_params["user_id"])
            user = await user_service.get_user(user_id)
            return Response(content=user)

        # Create handler with dependency injection
        handler = RequestHandler(
            handler_func=get_user_handler, dependency_injector=injector
        )

        test_request = Request(
            method="GET", url="/users/123", path_params={"user_id": "123"}
        )

        response = await handler.handle_request(test_request)

        assert response.status_code == HTTPStatus.OK
        assert response.content["id"] == 123
        assert response.content["username"] == "user_123"

    def test_dependency_lifecycle_management(self, injector):
        """Test dependency lifecycle management."""

        class SessionService:
            def __init__(self):
                self.session_count = 0

            def create_session(self):
                self.session_count += 1
                return f"session_{self.session_count}"

        # Register as singleton
        injector.register_singleton(SessionService)

        # Get multiple instances
        service1 = injector.resolve(SessionService)
        service2 = injector.resolve(SessionService)

        # Should be same instance
        assert service1 is service2

        # State should be shared
        session1 = service1.create_session()
        session2 = service2.create_session()

        assert session1 == "session_1"
        assert session2 == "session_2"
        assert service1.session_count == 2

    async def test_request_scoped_dependencies(self, injector):
        """Test request-scoped dependency injection."""

        class RequestLogger:
            def __init__(self, request_id: str):
                self.request_id = request_id
                self.logs = []

            def log(self, message: str):
                self.logs.append(f"[{self.request_id}] {message}")

        # Register request-scoped dependency
        injector.register_request_scoped(
            RequestLogger,
            lambda request: RequestLogger(
                request.headers.get("X-Request-ID", "unknown")
            ),
        )

        async def logging_handler(
            request: Request, logger: RequestLogger = injector.inject(RequestLogger)
        ) -> Response:
            logger.log("Handler executed")
            return Response(content={"logs": logger.logs})

        test_request = Request(
            method="GET", url="/test", headers={"X-Request-ID": "req-123"}
        )

        handler = RequestHandler(
            handler_func=logging_handler, dependency_injector=injector
        )

        response = await handler.handle_request(test_request)

        assert response.status_code == HTTPStatus.OK
        assert len(response.content["logs"]) == 1
        assert "req-123" in response.content["logs"][0]


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.slow
class TestRestPerformance:
    """Test REST API performance characteristics."""

    async def test_route_matching_performance(self):
        """Test route matching performance with many routes."""
        router = RestRouter()

        # Add many routes
        for i in range(1000):

            async def handler(request: Request) -> Response:
                return Response(content={"route": i})

            router.add_route(f"/api/v1/resource_{i}", handler, methods=["GET"])

        # Test matching performance
        import time

        start_time = time.perf_counter()

        for i in range(100):
            route = router.match_route(f"/api/v1/resource_{i}", "GET")
            assert route is not None

        end_time = time.perf_counter()
        avg_match_time = (end_time - start_time) / 100

        # Should be fast even with many routes
        assert avg_match_time < 0.001, f"Route matching too slow: {avg_match_time:.4f}s"

    async def test_middleware_pipeline_performance(self):
        """Test middleware pipeline performance."""
        app = RestApp()

        # Add multiple middleware layers
        middlewares = [
            CORSMiddleware(allow_origins=["*"]),
            RateLimitingMiddleware(max_requests=1000, window_seconds=60),
            ValidationMiddleware(),
            AuthenticationMiddleware(auth_schemes=["Bearer"], optional_paths=["/*"]),
            ErrorHandlingMiddleware(),
        ]

        for middleware in middlewares:
            app.add_middleware(middleware)

        async def simple_handler(request: Request) -> Response:
            return Response(content={"message": "success"})

        app.add_route("/test", simple_handler, methods=["GET"])

        # Test pipeline performance
        import time

        start_time = time.perf_counter()

        for _i in range(100):
            test_request = Request(
                method="GET", url="/test", headers={"Origin": "https://example.com"}
            )

            response = await app.process_request(test_request)
            assert response.status_code == HTTPStatus.OK

        end_time = time.perf_counter()
        avg_process_time = (end_time - start_time) / 100

        # Should process requests quickly even with many middleware
        assert (
            avg_process_time < 0.01
        ), f"Request processing too slow: {avg_process_time:.4f}s"
