"""
Comprehensive Unit Tests for CovetPy Core Routing System

Tests the routing system with real route matching, parameter extraction,
and HTTP method handling. All tests validate actual routing behavior
without mocks to ensure production readiness.
"""


import pytest

from covet.core.http import Response
from covet.core.routing import (
    CovetRouter,
    MethodNotAllowedError,
    ParameterExtractor,
    PathNotFoundError,
    Route,
    RoutePattern,
)


class TestRoutePattern:
    """Test route pattern compilation and matching."""

    def test_static_route_pattern(self):
        """Test static route pattern without parameters."""
        pattern = RoutePattern("/api/users")

        assert pattern.pattern == "/api/users"
        assert pattern.regex.pattern == "^/api/users$"
        assert len(pattern.parameter_names) == 0

        # Test matching
        match = pattern.match("/api/users")
        assert match is not None
        assert match.params == {}

        # Test non-matching
        assert pattern.match("/api/posts") is None
        assert pattern.match("/api/users/1") is None

    def test_dynamic_route_pattern_single_param(self):
        """Test route pattern with single parameter."""
        pattern = RoutePattern("/api/users/{user_id}")

        assert "user_id" in pattern.parameter_names
        assert len(pattern.parameter_names) == 1

        # Test matching with integer
        match = pattern.match("/api/users/123")
        assert match is not None
        assert match.params["user_id"] == "123"

        # Test matching with string
        match = pattern.match("/api/users/alice")
        assert match is not None
        assert match.params["user_id"] == "alice"

        # Test non-matching
        assert pattern.match("/api/users") is None
        assert pattern.match("/api/users/123/posts") is None

    def test_dynamic_route_pattern_multiple_params(self):
        """Test route pattern with multiple parameters."""
        pattern = RoutePattern("/api/users/{user_id}/posts/{post_id}")

        assert "user_id" in pattern.parameter_names
        assert "post_id" in pattern.parameter_names
        assert len(pattern.parameter_names) == 2

        # Test successful matching
        match = pattern.match("/api/users/123/posts/456")
        assert match is not None
        assert match.params["user_id"] == "123"
        assert match.params["post_id"] == "456"

        # Test partial matching failure
        assert pattern.match("/api/users/123") is None
        assert pattern.match("/api/users/123/posts") is None

    def test_route_pattern_with_typed_parameters(self):
        """Test route pattern with type constraints."""
        pattern = RoutePattern("/api/users/{user_id:int}/posts/{slug:str}")

        # Test integer parameter conversion
        match = pattern.match("/api/users/123/posts/my-post")
        assert match is not None
        assert match.params["user_id"] == 123
        assert isinstance(match.params["user_id"], int)
        assert match.params["slug"] == "my-post"
        assert isinstance(match.params["slug"], str)

        # Test invalid integer
        assert pattern.match("/api/users/abc/posts/my-post") is None

    def test_route_pattern_with_optional_parameters(self):
        """Test route pattern with optional parameters."""
        pattern = RoutePattern("/api/posts{?page,limit}")

        # Test without parameters
        match = pattern.match("/api/posts")
        assert match is not None
        assert match.params.get("page") is None
        assert match.params.get("limit") is None

    def test_route_pattern_edge_cases(self):
        """Test edge cases in route pattern matching."""
        pattern = RoutePattern("/api/{category}/{action}")

        # Test with special characters in parameters
        match = pattern.match("/api/user-management/create-user")
        assert match is not None
        assert match.params["category"] == "user-management"
        assert match.params["action"] == "create-user"

        # Test with numbers and underscores
        match = pattern.match("/api/v1_api/test_123")
        assert match is not None
        assert match.params["category"] == "v1_api"
        assert match.params["action"] == "test_123"


class TestParameterExtractor:
    """Test parameter extraction from URLs."""

    def test_extract_path_parameters(self):
        """Test extraction of path parameters."""
        extractor = ParameterExtractor()

        # Simple path parameters
        result = extractor.extract("/users/{id}", "/users/123")
        assert result["id"] == "123"

        # Multiple parameters
        result = extractor.extract(
            "/users/{user_id}/posts/{post_id}", "/users/123/posts/456"
        )
        assert result["user_id"] == "123"
        assert result["post_id"] == "456"

    def test_extract_query_parameters(self):
        """Test extraction of query parameters."""
        extractor = ParameterExtractor()

        result = extractor.extract_query("?page=1&limit=10&sort=name")
        assert result["page"] == "1"
        assert result["limit"] == "10"
        assert result["sort"] == "name"

        # Test URL decoding
        result = extractor.extract_query("?name=John%20Doe&email=john%40example.com")
        assert result["name"] == "John Doe"
        assert result["email"] == "john@example.com"

    def test_parameter_type_conversion(self):
        """Test automatic type conversion of parameters."""
        extractor = ParameterExtractor()

        # Integer conversion
        result = extractor.convert_parameter("123", "int")
        assert result == 123
        assert isinstance(result, int)

        # Float conversion
        result = extractor.convert_parameter("123.45", "float")
        assert result == 123.45
        assert isinstance(result, float)

        # Boolean conversion
        assert extractor.convert_parameter("true", "bool") is True
        assert extractor.convert_parameter("false", "bool") is False
        assert extractor.convert_parameter("1", "bool") is True
        assert extractor.convert_parameter("0", "bool") is False

        # String (default)
        result = extractor.convert_parameter("hello", "str")
        assert result == "hello"
        assert isinstance(result, str)

    def test_parameter_validation(self):
        """Test parameter validation."""
        extractor = ParameterExtractor()

        # Valid parameters
        assert extractor.validate_parameter("123", "int") is True
        assert extractor.validate_parameter("123.45", "float") is True
        assert extractor.validate_parameter("hello", "str") is True

        # Invalid parameters
        assert extractor.validate_parameter("abc", "int") is False
        assert extractor.validate_parameter("abc", "float") is False


class TestRoute:
    """Test individual route objects."""

    async def dummy_handler(self, request):
        """Dummy handler for testing."""
        return {"message": "test"}

    def test_route_creation(self):
        """Test route object creation."""
        route = Route(
            path="/api/users/{user_id}",
            handler=self.dummy_handler,
            methods=["GET", "POST"],
            name="user_detail",
        )

        assert route.path == "/api/users/{user_id}"
        assert route.handler == self.dummy_handler
        assert route.methods == ["GET", "POST"]
        assert route.name == "user_detail"
        assert isinstance(route.pattern, RoutePattern)

    def test_route_method_validation(self):
        """Test HTTP method validation."""
        # Valid methods
        route = Route("/test", self.dummy_handler, ["GET", "POST", "PUT", "DELETE"])
        assert "GET" in route.methods
        assert "POST" in route.methods

        # Case insensitive
        route = Route("/test", self.dummy_handler, ["get", "post"])
        assert "GET" in route.methods
        assert "POST" in route.methods

    def test_route_matching(self):
        """Test route matching functionality."""
        route = Route("/api/users/{user_id}", self.dummy_handler, ["GET"])

        # Successful match
        match = route.match("/api/users/123", "GET")
        assert match is not None
        assert match.route == route
        assert match.params["user_id"] == "123"
        assert match.handler == self.dummy_handler

        # Path mismatch
        assert route.match("/api/posts/123", "GET") is None

        # Method mismatch
        assert route.match("/api/users/123", "POST") is None

    def test_route_with_middleware(self):
        """Test route with attached middleware."""

        async def test_middleware(request, call_next):
            response = await call_next(request)
            response.headers["X-Test"] = "middleware"
            return response

        route = Route(
            "/test", self.dummy_handler, ["GET"], middleware=[test_middleware]
        )

        assert len(route.middleware) == 1
        assert route.middleware[0] == test_middleware


class TestCovetRouter:
    """Test the main router class."""

    async def dummy_handler(self, request):
        return {"message": "test"}

    async def user_handler(self, request):
        user_id = request.path_params.get("user_id")
        return {"user_id": user_id}

    def test_router_creation(self):
        """Test router instantiation."""
        router = CovetRouter()
        assert len(router.routes) == 0
        assert isinstance(router.routes, list)

    def test_add_static_route(self):
        """Test adding static routes."""
        router = CovetRouter()

        router.add_route("/api/health", self.dummy_handler, ["GET"])
        assert len(router.routes) == 1

        route = router.routes[0]
        assert route.path == "/api/health"
        assert route.handler == self.dummy_handler
        assert route.methods == ["GET"]

    def test_add_dynamic_route(self):
        """Test adding dynamic routes with parameters."""
        router = CovetRouter()

        router.add_route("/api/users/{user_id}", self.user_handler, ["GET"])
        assert len(router.routes) == 1

        route = router.routes[0]
        assert route.path == "/api/users/{user_id}"
        assert "user_id" in route.pattern.parameter_names

    def test_add_multiple_routes(self):
        """Test adding multiple routes."""
        router = CovetRouter()

        router.add_route("/api/users", self.dummy_handler, ["GET", "POST"])
        router.add_route("/api/users/{user_id}", self.user_handler, ["GET"])
        router.add_route("/api/posts", self.dummy_handler, ["GET"])

        assert len(router.routes) == 3

    def test_route_matching_static(self):
        """Test static route matching."""
        router = CovetRouter()
        router.add_route("/api/health", self.dummy_handler, ["GET"])

        # Successful match
        match = router.match_route("/api/health", "GET")
        assert match is not None
        assert match.handler == self.dummy_handler
        assert match.params == {}

        # Path not found
        with pytest.raises(PathNotFoundError):
            router.match_route("/api/status", "GET")

        # Method not allowed
        with pytest.raises(MethodNotAllowedError):
            router.match_route("/api/health", "POST")

    def test_route_matching_dynamic(self):
        """Test dynamic route matching."""
        router = CovetRouter()
        router.add_route("/api/users/{user_id}", self.user_handler, ["GET"])

        # Successful match
        match = router.match_route("/api/users/123", "GET")
        assert match is not None
        assert match.handler == self.user_handler
        assert match.params["user_id"] == "123"

        # Match with string parameter
        match = router.match_route("/api/users/alice", "GET")
        assert match is not None
        assert match.params["user_id"] == "alice"

    def test_route_priority_ordering(self):
        """Test that routes are matched in correct priority order."""
        router = CovetRouter()

        # Add more specific route first
        router.add_route("/api/users/me", self.dummy_handler, ["GET"])
        # Add more general route second
        router.add_route("/api/users/{user_id}", self.user_handler, ["GET"])

        # More specific route should match
        match = router.match_route("/api/users/me", "GET")
        assert match.handler == self.dummy_handler

        # General route should match other paths
        match = router.match_route("/api/users/123", "GET")
        assert match.handler == self.user_handler

    def test_overlapping_routes(self):
        """Test handling of overlapping route patterns."""
        router = CovetRouter()

        router.add_route("/api/{version}/users", self.dummy_handler, ["GET"])
        router.add_route("/api/v1/users", self.user_handler, ["GET"])

        # Exact match should take priority
        match = router.match_route("/api/v1/users", "GET")
        assert match.handler == self.user_handler

        # Dynamic route should catch others
        match = router.match_route("/api/v2/users", "GET")
        assert match.handler == self.dummy_handler
        assert match.params["version"] == "v2"

    def test_route_with_multiple_methods(self):
        """Test routes with multiple HTTP methods."""
        router = CovetRouter()
        router.add_route("/api/users", self.dummy_handler, ["GET", "POST", "PUT"])

        # All methods should work
        for method in ["GET", "POST", "PUT"]:
            match = router.match_route("/api/users", method)
            assert match is not None
            assert match.handler == self.dummy_handler

        # Unsupported method should fail
        with pytest.raises(MethodNotAllowedError):
            router.match_route("/api/users", "DELETE")

    def test_complex_route_patterns(self):
        """Test complex route patterns with multiple parameters."""
        router = CovetRouter()

        router.add_route(
            "/api/v{version}/users/{user_id}/posts/{post_id}/comments",
            self.dummy_handler,
            ["GET"],
        )

        match = router.match_route("/api/v1/users/123/posts/456/comments", "GET")
        assert match is not None
        assert match.params["version"] == "1"
        assert match.params["user_id"] == "123"
        assert match.params["post_id"] == "456"

    def test_route_url_generation(self):
        """Test URL generation from route patterns."""
        router = CovetRouter()

        router.add_route(
            "/api/users/{user_id}/posts/{post_id}",
            self.dummy_handler,
            ["GET"],
            name="user_post",
        )

        # Generate URL with parameters
        url = router.url_for("user_post", user_id=123, post_id=456)
        assert url == "/api/users/123/posts/456"

        # Generate URL with string parameters
        url = router.url_for("user_post", user_id="alice", post_id="my-post")
        assert url == "/api/users/alice/posts/my-post"

    def test_route_groups_and_prefixes(self):
        """Test route grouping with common prefixes."""
        router = CovetRouter()

        # Add routes with common prefix
        api_routes = [
            ("/users", self.dummy_handler, ["GET"]),
            ("/users/{user_id}", self.user_handler, ["GET"]),
            ("/posts", self.dummy_handler, ["GET"]),
        ]

        router.add_route_group("/api/v1", api_routes)

        # Verify routes were added with prefix
        match = router.match_route("/api/v1/users", "GET")
        assert match is not None

        match = router.match_route("/api/v1/users/123", "GET")
        assert match is not None
        assert match.params["user_id"] == "123"

    def test_middleware_integration(self):
        """Test middleware integration with routing."""
        router = CovetRouter()

        async def auth_middleware(request, call_next):
            if not request.headers.get("Authorization"):
                return Response({"error": "Unauthorized"}, status_code=401)
            return await call_next(request)

        router.add_route(
            "/api/protected", self.dummy_handler, ["GET"], middleware=[auth_middleware]
        )

        route = router.routes[0]
        assert len(route.middleware) == 1
        assert route.middleware[0] == auth_middleware

    @pytest.mark.performance
    def test_routing_performance(self):
        """Test routing performance with many routes."""
        import time

        router = CovetRouter()

        # Add many routes
        for i in range(1000):
            router.add_route(f"/api/endpoint_{i}", self.dummy_handler, ["GET"])

        # Measure matching performance
        start_time = time.perf_counter()

        for i in range(100):
            try:
                router.match_route(f"/api/endpoint_{i}", "GET")
            except (PathNotFoundError, MethodNotAllowedError):
                pass

        end_time = time.perf_counter()
        avg_time = (end_time - start_time) / 100

        # Should be very fast (< 1ms per match)
        assert avg_time < 0.001, f"Routing too slow: {avg_time:.4f}s per match"

    def test_router_error_handling(self):
        """Test router error handling for edge cases."""
        router = CovetRouter()

        # Empty path
        with pytest.raises(ValueError):
            router.add_route("", self.dummy_handler, ["GET"])

        # Invalid method
        with pytest.raises(ValueError):
            router.add_route("/test", self.dummy_handler, ["INVALID"])

        # None handler
        with pytest.raises(ValueError):
            router.add_route("/test", None, ["GET"])

    def test_route_debugging_info(self):
        """Test router debugging and introspection."""
        router = CovetRouter()

        router.add_route("/api/users", self.dummy_handler, ["GET", "POST"])
        router.add_route("/api/users/{user_id}", self.user_handler, ["GET"])

        # Get routing table
        routes_info = router.get_routes_info()
        assert len(routes_info) == 2

        # Verify route information
        static_route = next(r for r in routes_info if r["path"] == "/api/users")
        assert static_route["methods"] == ["GET", "POST"]
        assert static_route["dynamic"] is False

        dynamic_route = next(
            r for r in routes_info if r["path"] == "/api/users/{user_id}"
        )
        assert dynamic_route["methods"] == ["GET"]
        assert dynamic_route["dynamic"] is True
        assert "user_id" in dynamic_route["parameters"]
