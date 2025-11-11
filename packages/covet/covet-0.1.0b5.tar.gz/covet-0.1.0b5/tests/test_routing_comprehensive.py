#!/usr/bin/env python3
"""
Comprehensive test suite for CovetPy routing system

Tests all functionality of the fixed zero-dependency routing system including:
- Static route matching
- Dynamic parameter extraction ({param} and <type:param> syntax) 
- HTTP method routing
- ASGI application integration
- Error handling
- Type conversion
"""

import sys
import asyncio
import pytest
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from covet.core.routing import CovetRouter, RouteMatch, RouteInfo
from covet.core.asgi_app import CovetASGI, Request, Response, JSONResponse


class TestCovetRouter:
    """Test the core routing functionality"""
    
    def test_router_initialization(self):
        """Test router initializes correctly"""
        router = CovetRouter()
        assert router.static_routes == {}
        assert router.dynamic_routes == []
        assert router.middleware_stack == []
        assert not router._compiled
    
    def test_static_route_registration(self):
        """Test static route registration and matching"""
        router = CovetRouter()
        
        def handler():
            return {"message": "test"}
        
        # Add static route
        router.add_route("/static", handler, ["GET"])
        
        # Check it's registered as static
        assert "/static" in router.static_routes
        assert "GET" in router.static_routes["/static"]
        assert router.static_routes["/static"]["GET"] == handler
        
        # Test matching
        match = router.match_route("/static", "GET")
        assert match is not None
        assert match.handler == handler
        assert match.params == {}
    
    def test_dynamic_route_registration(self):
        """Test dynamic route registration"""
        router = CovetRouter()
        
        def handler():
            return {"message": "test"}
        
        # Add dynamic routes
        router.add_route("/users/{user_id}", handler, ["GET"])
        router.add_route("/files/<path:file_path>", handler, ["POST"])
        router.add_route("/items/<int:item_id>", handler, ["PUT"])
        
        # Check they're registered as dynamic
        assert len(router.dynamic_routes) == 3
        
        dynamic_patterns = [route.pattern for route in router.dynamic_routes]
        assert "/users/{user_id}" in dynamic_patterns
        assert "/files/<path:file_path>" in dynamic_patterns
        assert "/items/<int:item_id>" in dynamic_patterns
    
    def test_braces_parameter_extraction(self):
        """Test {param} style parameter extraction"""
        router = CovetRouter()
        
        def handler():
            return {"message": "test"}
        
        router.add_route("/users/{user_id}", handler, ["GET"])
        router.add_route("/api/v{version}/users/{user_id}", handler, ["GET"])
        
        # Test single parameter
        match = router.match_route("/users/123", "GET")
        assert match is not None
        assert match.params == {"user_id": "123"}  # {param} style stays as string
        
        # Test multiple parameters
        match = router.match_route("/api/v2/users/456", "GET")
        assert match is not None
        assert match.params == {"version": "2", "user_id": "456"}  # {param} style stays as string
        
        # Test no match
        match = router.match_route("/users", "GET")
        assert match is None
    
    def test_angle_bracket_parameter_extraction(self):
        """Test <type:param> style parameter extraction"""
        router = CovetRouter()
        
        def handler():
            return {"message": "test"}
        
        router.add_route("/items/<int:item_id>", handler, ["GET"])
        router.add_route("/files/<path:file_path>", handler, ["GET"])
        router.add_route("/docs/<str:doc_name>", handler, ["GET"])
        router.add_route("/untyped/<param_name>", handler, ["GET"])
        
        # Test int parameter
        match = router.match_route("/items/42", "GET")
        assert match is not None
        assert match.params == {"item_id": 42}
        assert isinstance(match.params["item_id"], int)
        
        # Test path parameter (should match slashes)
        match = router.match_route("/files/docs/readme.txt", "GET")
        assert match is not None
        assert match.params == {"file_path": "docs/readme.txt"}
        
        # Test string parameter
        match = router.match_route("/docs/getting-started", "GET")
        assert match is not None
        assert match.params == {"doc_name": "getting-started"}
        
        # Test untyped parameter (defaults to string)
        match = router.match_route("/untyped/test-value", "GET")
        assert match is not None
        assert match.params == {"param_name": "test-value"}
    
    def test_http_method_routing(self):
        """Test HTTP method-specific routing"""
        router = CovetRouter()
        
        def get_handler():
            return {"method": "GET"}
        
        def post_handler():
            return {"method": "POST"}
        
        def multi_handler():
            return {"method": "MULTI"}
        
        # Add routes with different methods
        router.add_route("/resource", get_handler, ["GET"])
        router.add_route("/resource", post_handler, ["POST"])
        router.add_route("/multi", multi_handler, ["GET", "POST", "PUT"])
        
        # Test method-specific matching
        match = router.match_route("/resource", "GET")
        assert match.handler == get_handler
        
        match = router.match_route("/resource", "POST")
        assert match.handler == post_handler
        
        # Test unsupported method
        match = router.match_route("/resource", "DELETE")
        assert match is None
        
        # Test multi-method route
        for method in ["GET", "POST", "PUT"]:
            match = router.match_route("/multi", method)
            assert match.handler == multi_handler
        
        # Test unsupported method on multi-method route
        match = router.match_route("/multi", "DELETE")
        assert match is None
    
    def test_route_priority(self):
        """Test that static routes have priority over dynamic routes"""
        router = CovetRouter()
        
        def static_handler():
            return {"type": "static"}
        
        def dynamic_handler():
            return {"type": "dynamic"}
        
        # Add dynamic route first
        router.add_route("/api/{path}", dynamic_handler, ["GET"])
        # Add static route second  
        router.add_route("/api/static", static_handler, ["GET"])
        
        # Static route should match
        match = router.match_route("/api/static", "GET")
        assert match.handler == static_handler
        
        # Dynamic route should still work for other paths
        match = router.match_route("/api/dynamic", "GET")
        assert match.handler == dynamic_handler
        assert match.params == {"path": "dynamic"}
    
    def test_route_listing(self):
        """Test getting all registered routes"""
        router = CovetRouter()
        
        def handler1():
            pass
        
        def handler2():
            pass
        
        router.add_route("/static", handler1, ["GET"])
        router.add_route("/users/{user_id}", handler2, ["GET", "POST"])
        
        routes = router.get_all_routes()
        
        # Should have 3 total routes (1 static + 2 dynamic)
        assert len(routes) == 3
        
        # Check route information
        static_routes = [r for r in routes if r["type"] == "static"]
        dynamic_routes = [r for r in routes if r["type"] == "dynamic"]
        
        assert len(static_routes) == 1
        assert len(dynamic_routes) == 2
        
        assert static_routes[0]["path"] == "/static"
        assert static_routes[0]["method"] == "GET"


class TestCovetASGI:
    """Test the ASGI application functionality"""
    
    def test_asgi_app_initialization(self):
        """Test ASGI app initializes correctly"""
        app = CovetASGI(debug=True)
        assert app.debug is True
        assert isinstance(app.router, CovetRouter)
        assert app.middleware_stack == []
    
    def test_route_decorators(self):
        """Test route decorator functionality"""
        app = CovetASGI()
        
        @app.get("/get-endpoint")
        def get_handler(request):
            return {"method": "GET"}
        
        @app.post("/post-endpoint") 
        def post_handler(request):
            return {"method": "POST"}
        
        @app.route("/custom-endpoint", ["PUT", "DELETE"])
        def custom_handler(request):
            return {"method": "CUSTOM"}
        
        # Check routes were registered
        routes = app.router.get_all_routes()
        paths = [r["path"] for r in routes]
        
        assert "/get-endpoint" in paths
        assert "/post-endpoint" in paths
        assert "/custom-endpoint" in paths
    
    @pytest.mark.asyncio
    async def test_request_handling(self):
        """Test request handling through ASGI"""
        app = CovetASGI(debug=True)
        
        @app.get("/test")
        async def test_handler(request):
            return {"message": "success", "path": request.path, "method": request.method}
        
        @app.post("/echo")
        async def echo_handler(request):
            data = await request.json()
            return {"echo": data}
        
        @app.get("/params/{param_id}")
        async def param_handler(request, param_id: str):
            return {"param_id": param_id, "type": type(param_id).__name__}
        
        # Test GET request
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "query_string": b"",
            "headers": [[b"accept", b"application/json"]]
        }
        
        async def mock_receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        
        response_data = {}
        
        async def mock_send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
            elif message["type"] == "http.response.body":
                response_data["body"] = message["body"]
        
        await app(scope, mock_receive, mock_send)
        
        assert response_data["status"] == 200
        assert b"success" in response_data["body"]
        
        # Test POST request with JSON body
        import json
        
        scope = {
            "type": "http",
            "method": "POST", 
            "path": "/echo",
            "query_string": b"",
            "headers": [[b"content-type", b"application/json"]]
        }
        
        test_data = {"test": "data", "number": 42}
        body_sent = False
        
        async def mock_receive_with_body():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {
                    "type": "http.request",
                    "body": json.dumps(test_data).encode(),
                    "more_body": False
                }
            return {"type": "http.request", "body": b"", "more_body": False}
        
        response_data = {}
        
        async def mock_send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
            elif message["type"] == "http.response.body":
                response_data["body"] = message["body"]
        
        await app(scope, mock_receive_with_body, mock_send)
        
        assert response_data["status"] == 200
        response_json = json.loads(response_data["body"])
        assert response_json["echo"] == test_data
        
        # Test parameter extraction
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/params/123",
            "query_string": b"",
            "headers": []
        }
        
        response_data = {}
        
        await app(scope, mock_receive, mock_send)
        
        assert response_data["status"] == 200
        response_json = json.loads(response_data["body"])
        assert response_json["param_id"] == "123"
        assert response_json["type"] == "str"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in ASGI app"""
        app = CovetASGI(debug=True)
        
        @app.get("/error")
        async def error_handler(request):
            raise ValueError("Test error")
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/error",
            "query_string": b"",
            "headers": []
        }
        
        async def mock_receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        
        response_data = {}
        
        async def mock_send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
            elif message["type"] == "http.response.body":
                response_data["body"] = message["body"]
        
        await app(scope, mock_receive, mock_send)
        
        # Should return 500 error
        assert response_data["status"] == 500
        
        import json
        response_json = json.loads(response_data["body"])
        assert "error" in response_json
        # In debug mode, should include traceback
        assert "traceback" in response_json
        
        # Test 404 for non-existent route
        scope["path"] = "/nonexistent"
        response_data = {}
        
        await app(scope, mock_receive, mock_send)
        
        assert response_data["status"] == 404


class TestIntegration:
    """Integration tests combining routing and ASGI functionality"""
    
    @pytest.mark.asyncio
    async def test_complex_routing_scenarios(self):
        """Test complex routing scenarios"""
        app = CovetASGI()
        
        @app.get("/api/v{version}/users/{user_id}/posts/<int:post_id>")
        async def complex_handler(request, version: str, user_id: int, post_id: int):
            return {
                "version": version,
                "user_id": user_id,
                "post_id": post_id,
                "types": {
                    "version": type(version).__name__,
                    "user_id": type(user_id).__name__, 
                    "post_id": type(post_id).__name__
                }
            }
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/api/v2/users/123/posts/456",
            "query_string": b"",
            "headers": []
        }
        
        async def mock_receive():
            return {"type": "http.request", "body": b"", "more_body": False}
        
        response_data = {}
        
        async def mock_send(message):
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
            elif message["type"] == "http.response.body":
                response_data["body"] = message["body"]
        
        await app(scope, mock_receive, mock_send)
        
        assert response_data["status"] == 200
        
        import json
        response_json = json.loads(response_data["body"])
        assert response_json["version"] == "2"
        assert response_json["user_id"] == "123"  # {param} stays as string
        assert response_json["post_id"] == 456    # <int:param> gets converted
        assert response_json["types"]["version"] == "str"
        assert response_json["types"]["user_id"] == "str"
        assert response_json["types"]["post_id"] == "int"


def run_tests():
    """Run all tests manually if pytest is not available"""
    import traceback
    
    test_classes = [TestCovetRouter, TestCovetASGI, TestIntegration]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        
        instance = test_class()
        
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                total_tests += 1
                print(f"Running {method_name}...", end=" ")
                
                try:
                    method = getattr(instance, method_name)
                    
                    # Handle async tests
                    if asyncio.iscoroutinefunction(method):
                        asyncio.run(method())
                    else:
                        method()
                    
                    print("✅ PASSED")
                    passed_tests += 1
                    
                except Exception as e:
                    print(f"❌ FAILED: {e}")
                    if "--verbose" in sys.argv:
                        traceback.print_exc()
    
    print(f"\n=== Test Results ===")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    
    if passed_tests == total_tests:
        print("🎯 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)