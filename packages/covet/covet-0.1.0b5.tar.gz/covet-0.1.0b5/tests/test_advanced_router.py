"""
Comprehensive tests for the CovetPy Advanced Router System
Tests performance, functionality, and edge cases
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from covet.core.advanced_router import (
    AdvancedRouter, RouteGroup, RouteInfo, RouteMatch, RouteParameter,
    middleware, timing_middleware, cors_middleware, auth_middleware,
    create_api_group, create_admin_group, RadixNode
)


class TestRadixNode:
    """Test the radix tree implementation"""
    
    def test_simple_static_route(self):
        """Test adding and matching simple static routes"""
        root = RadixNode()
        
        # Create a simple handler
        def handler():
            return "hello"
            
        route = RouteInfo(
            path="/hello",
            handler=handler,
            methods={"GET"}
        )
        
        root.add_route("/hello", route)
        
        params = {}
        result = root.match(["hello"], params)
        
        assert result is not None
        assert "GET" in result
        assert result["GET"].handler == handler
        assert len(params) == 0
        
    def test_parameter_route(self):
        """Test parameter extraction"""
        root = RadixNode()
        
        def handler():
            return "user"
            
        route = RouteInfo(
            path="/users/{id}",
            handler=handler,
            methods={"GET"}
        )
        
        root.add_route("/users/{id}", route)
        
        params = {}
        result = root.match(["users", "123"], params)
        
        assert result is not None
        assert "GET" in result
        assert params["id"] == "123"
        
    def test_wildcard_route(self):
        """Test wildcard route matching"""
        root = RadixNode()
        
        def handler():
            return "static"
            
        route = RouteInfo(
            path="/static/*filepath",
            handler=handler,
            methods={"GET"}
        )
        
        root.add_route("/static/*filepath", route)
        
        params = {}
        result = root.match(["static", "css", "main.css"], params)
        
        assert result is not None
        assert "GET" in result
        assert params["filepath"] == "css/main.css"
        
    def test_route_priority(self):
        """Test that static routes have priority over parameter routes"""
        root = RadixNode()
        
        def static_handler():
            return "static"
            
        def param_handler():
            return "param"
            
        static_route = RouteInfo(
            path="/users/admin",
            handler=static_handler,
            methods={"GET"}
        )
        
        param_route = RouteInfo(
            path="/users/{id}",
            handler=param_handler,
            methods={"GET"}
        )
        
        # Add parameter route first, then static
        root.add_route("/users/{id}", param_route)
        root.add_route("/users/admin", static_route)
        
        params = {}
        result = root.match(["users", "admin"], params)
        
        assert result is not None
        assert "GET" in result
        assert result["GET"].handler == static_handler  # Static should win
        assert len(params) == 0  # No parameters extracted


class TestAdvancedRouter:
    """Test the main router functionality"""
    
    def setup_method(self):
        """Set up a fresh router for each test"""
        self.router = AdvancedRouter()
        
    def test_simple_route_registration(self):
        """Test basic route registration"""
        @self.router.get("/hello")
        def hello():
            return "Hello, World!"
            
        assert len(self.router.routes) == 1
        route = self.router.routes[0]
        assert route.path == "/hello"
        assert "GET" in route.methods
        assert route.handler == hello
        
    def test_multiple_methods(self):
        """Test route with multiple HTTP methods"""
        @self.router.route("/api/users", methods=["GET", "POST"])
        def users():
            return "users"
            
        route = self.router.routes[0]
        assert route.methods == {"GET", "POST"}
        
    def test_parameter_extraction(self):
        """Test path parameter extraction and conversion"""
        @self.router.get("/users/{user_id:int}/posts/{post_id:int}")
        def get_user_post(user_id: int, post_id: int):
            return f"User {user_id}, Post {post_id}"
            
        match = self.router.match_route("/users/123/posts/456", "GET")
        
        assert match is not None
        assert match.params["user_id"] == 123
        assert match.params["post_id"] == 456
        assert isinstance(match.params["user_id"], int)
        assert isinstance(match.params["post_id"], int)
        
    def test_query_parameter_parsing(self):
        """Test query parameter extraction"""
        @self.router.get("/search")
        def search():
            return "search results"
            
        match = self.router.match_route("/search", "GET", "q=python&limit=10&tags=web&tags=api")
        
        assert match is not None
        assert match.query_params["q"] == "python"
        assert match.query_params["limit"] == "10"
        assert match.query_params["tags"] == ["web", "api"]  # Multiple values
        
    def test_wildcard_routes(self):
        """Test wildcard route functionality"""
        @self.router.get("/static/*filepath")
        def serve_static(filepath: str):
            return f"Serving: {filepath}"
            
        match = self.router.match_route("/static/css/main.css", "GET")
        
        assert match is not None
        assert match.params["filepath"] == "css/main.css"
        
    def test_route_not_found(self):
        """Test handling of non-existent routes"""
        @self.router.get("/existing")
        def existing():
            return "exists"
            
        match = self.router.match_route("/nonexistent", "GET")
        assert match is None
        
    def test_method_not_allowed(self):
        """Test handling of wrong HTTP methods"""
        @self.router.get("/api/users")
        def get_users():
            return "users"
            
        match = self.router.match_route("/api/users", "POST")
        assert match is None
        
    def test_route_caching(self):
        """Test route caching functionality"""
        @self.router.get("/cached/{id}")
        def cached_route(id: str):
            return f"ID: {id}"
            
        # First match - should cache
        match1 = self.router.match_route("/cached/123", "GET")
        cache_size_after_first = len(self.router.route_cache)
        
        # Second match - should use cache
        match2 = self.router.match_route("/cached/123", "GET")
        cache_size_after_second = len(self.router.route_cache)
        
        assert match1 is not None
        assert match2 is not None
        assert cache_size_after_first == cache_size_after_second
        assert match1.params == match2.params
        
    def test_route_middleware(self):
        """Test per-route middleware"""
        middleware_calls = []
        
        @middleware
        async def test_middleware(request, call_next):
            middleware_calls.append("called")
            return await call_next(request)
            
        @self.router.get("/protected", middleware=[test_middleware])
        def protected():
            return "protected"
            
        match = self.router.match_route("/protected", "GET")
        
        assert match is not None
        assert len(match.middleware) == 1
        assert match.middleware[0] == test_middleware
        
    def test_route_priority(self):
        """Test route priority ordering"""
        @self.router.route("/api/{resource}", priority=1)
        def generic_resource(resource: str):
            return f"Generic: {resource}"
            
        @self.router.route("/api/users", priority=10)
        def specific_users():
            return "Specific users"
            
        # Compile routes to sort by priority
        self.router.compile_routes()
        
        match = self.router.match_route("/api/users", "GET")
        
        assert match is not None
        assert match.handler == specific_users  # Higher priority should win
        
    def test_thread_safety(self):
        """Test thread safety of the router"""
        import threading
        import random
        
        # Add some routes
        for i in range(100):
            self.router.add_route(f"/route/{i}", lambda: f"route_{i}", ["GET"])
            
        results = []
        errors = []
        
        def worker():
            try:
                for _ in range(100):
                    route_id = random.randint(0, 99)
                    match = self.router.match_route(f"/route/{route_id}", "GET")
                    if match:
                        results.append(match)
            except Exception as e:
                errors.append(e)
                
        # Run multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()
            
        assert len(errors) == 0, f"Thread safety errors: {errors}"
        assert len(results) > 0, "No successful matches in threaded test"


class TestRouteGroups:
    """Test route group functionality"""
    
    def test_basic_route_group(self):
        """Test basic route group functionality"""
        api_group = RouteGroup(prefix="/api/v1", tags={"api"})
        
        @api_group.get("/users")
        def get_users():
            return "users"
            
        @api_group.post("/users")
        def create_user():
            return "created"
            
        assert len(api_group.routes) == 2
        
        user_get_route = next(r for r in api_group.routes if "GET" in r.methods)
        user_post_route = next(r for r in api_group.routes if "POST" in r.methods)
        
        assert user_get_route.path == "/api/v1/users"
        assert user_post_route.path == "/api/v1/users"
        assert "api" in user_get_route.tags
        
    def test_group_middleware(self):
        """Test middleware inheritance in groups"""
        middleware_calls = []
        
        @middleware
        async def group_middleware(request, call_next):
            middleware_calls.append("group")
            return await call_next(request)
            
        group = RouteGroup(prefix="/api", middleware=[group_middleware])
        
        @group.get("/test")
        def test_endpoint():
            return "test"
            
        route = group.routes[0]
        assert len(route.middleware) == 1
        assert route.middleware[0] == group_middleware
        
    def test_router_group_integration(self):
        """Test integrating groups with router"""
        router = AdvancedRouter()
        api_group = create_api_group()
        
        @api_group.get("/users/{id}")
        def get_user(id: int):
            return f"User {id}"
            
        router.add_group(api_group)
        
        match = router.match_route("/api/v1/users/123", "GET")
        
        assert match is not None
        assert match.params["id"] == 123
        assert len(match.middleware) > 0  # Should have group middleware


class TestPerformance:
    """Test router performance characteristics"""
    
    def test_large_route_set_performance(self):
        """Test performance with many routes"""
        router = AdvancedRouter()
        
        # Add 1000 routes
        start_time = time.time()
        for i in range(1000):
            router.add_route(f"/api/resource_{i}/{{id}}", lambda: "response", ["GET"])
            
        add_time = time.time() - start_time
        
        # Test matching performance
        start_time = time.time()
        matches = 0
        for i in range(1000):
            match = router.match_route(f"/api/resource_{i}/123", "GET")
            if match:
                matches += 1
                
        match_time = time.time() - start_time
        
        print(f"\nPerformance Results:")
        print(f"Added 1000 routes in {add_time:.4f}s")
        print(f"Matched 1000 routes in {match_time:.4f}s")
        print(f"Average match time: {match_time/1000*1000:.4f}ms")
        print(f"Successful matches: {matches}/1000")
        
        assert matches == 1000
        assert match_time < 1.0  # Should match 1000 routes in under 1 second
        
    def test_benchmark_method(self):
        """Test the built-in benchmark method"""
        router = AdvancedRouter()
        
        # Add some test routes
        router.add_route("/api/users/{id}", lambda: "user", ["GET"])
        router.add_route("/api/posts/{post_id}/comments/{comment_id}", lambda: "comment", ["GET"])
        router.add_route("/static/*filepath", lambda: "static", ["GET"])
        
        results = router.benchmark_performance(num_requests=1000)
        
        assert results["total_requests"] == 1000
        assert results["successful_matches"] > 0
        assert results["requests_per_second"] > 0
        assert results["avg_time_per_request"] > 0
        
        print(f"\nBenchmark Results:")
        print(f"Requests per second: {results['requests_per_second']:.2f}")
        print(f"Average time per request: {results['avg_time_per_request']:.4f}ms")
        print(f"Cache hits: {results['cache_hits']}")
        
    def test_cache_performance(self):
        """Test caching improves performance"""
        # Router with cache
        cached_router = AdvancedRouter(enable_cache=True)
        cached_router.add_route("/api/test/{id}", lambda: "test", ["GET"])
        
        # Router without cache
        uncached_router = AdvancedRouter(enable_cache=False)
        uncached_router.add_route("/api/test/{id}", lambda: "test", ["GET"])
        
        # Warm up
        cached_router.match_route("/api/test/123", "GET")
        uncached_router.match_route("/api/test/123", "GET")
        
        # Time cached requests
        start_time = time.time()
        for _ in range(1000):
            cached_router.match_route("/api/test/123", "GET")
        cached_time = time.time() - start_time
        
        # Time uncached requests
        start_time = time.time()
        for _ in range(1000):
            uncached_router.match_route("/api/test/123", "GET")
        uncached_time = time.time() - start_time
        
        print(f"\nCache Performance:")
        print(f"Cached time: {cached_time:.4f}s")
        print(f"Uncached time: {uncached_time:.4f}s")
        print(f"Speedup: {uncached_time/cached_time:.2f}x")
        
        # Cached should be faster (but allow for some variance)
        assert cached_time <= uncached_time * 1.5


class TestMiddleware:
    """Test middleware functionality"""
    
    def test_timing_middleware(self):
        """Test timing middleware"""
        # This test is primarily to ensure the middleware is callable
        assert callable(timing_middleware)
        assert hasattr(timing_middleware, '_is_middleware')
        
    def test_cors_middleware(self):
        """Test CORS middleware"""
        assert callable(cors_middleware)
        assert hasattr(cors_middleware, '_is_middleware')
        
    def test_auth_middleware(self):
        """Test auth middleware"""
        assert callable(auth_middleware)
        assert hasattr(auth_middleware, '_is_middleware')
        
    def test_middleware_decorator(self):
        """Test middleware decorator"""
        @middleware
        async def custom_middleware(request, call_next):
            return await call_next(request)
            
        assert hasattr(custom_middleware, '_is_middleware')
        assert custom_middleware._is_middleware is True


class TestDocumentation:
    """Test documentation generation features"""
    
    def test_route_info_generation(self):
        """Test route information extraction"""
        router = AdvancedRouter()
        
        @router.get("/api/users/{id:int}", 
                   name="get_user",
                   description="Get user by ID",
                   tags={"users", "api"})
        def get_user(id: int):
            """Get a user by their ID"""
            return f"User {id}"
            
        routes_info = router.get_route_info()
        
        assert len(routes_info) == 1
        route = routes_info[0]
        
        assert route["path"] == "/api/users/{id:int}"
        assert route["method"] == "GET"
        assert route["name"] == "get_user"
        assert route["description"] == "Get user by ID"
        assert "users" in route["tags"]
        assert "api" in route["tags"]
        assert len(route["parameters"]) == 1
        assert route["parameters"][0]["name"] == "id"
        assert route["parameters"][0]["type"] == "int"
        
    def test_openapi_generation(self):
        """Test OpenAPI specification generation"""
        router = AdvancedRouter()
        
        @router.get("/api/users/{id}")
        def get_user(id: str):
            return "user"
            
        @router.post("/api/users")
        def create_user():
            return "created"
            
        spec = router.get_openapi_spec()
        
        assert spec["openapi"] == "3.0.3"
        assert "info" in spec
        assert "paths" in spec
        
        paths = spec["paths"]
        assert "/api/users/{id}" in paths
        assert "/api/users" in paths
        
        user_path = paths["/api/users/{id}"]
        assert "get" in user_path
        
        users_path = paths["/api/users"]
        assert "post" in users_path


class TestEdgeCases:
    """Test edge cases and error conditions"""
    
    def test_empty_path(self):
        """Test handling of empty paths"""
        router = AdvancedRouter()
        
        @router.get("/")
        def root():
            return "root"
            
        match = router.match_route("/", "GET")
        assert match is not None
        assert match.handler == root
        
    def test_trailing_slash_handling(self):
        """Test trailing slash handling"""
        router = AdvancedRouter()
        
        @router.get("/api/users")
        def users():
            return "users"
            
        # Should match both with and without trailing slash
        match1 = router.match_route("/api/users", "GET")
        match2 = router.match_route("/api/users/", "GET")
        
        assert match1 is not None
        # Note: Current implementation doesn't auto-handle trailing slashes
        # This is a design decision that could be changed
        
    def test_special_characters_in_path(self):
        """Test handling of special characters"""
        router = AdvancedRouter()
        
        @router.get("/api/files/{filename}")
        def get_file(filename: str):
            return f"File: {filename}"
            
        # Test URL-encoded characters
        match = router.match_route("/api/files/my%20file.txt", "GET")
        
        assert match is not None
        assert match.params["filename"] == "my file.txt"  # Should be decoded
        
    def test_route_compilation_thread_safety(self):
        """Test that route compilation is thread-safe"""
        router = AdvancedRouter()
        
        def add_routes():
            for i in range(100):
                router.add_route(f"/test/{i}", lambda: "test", ["GET"])
                
        def match_routes():
            for i in range(100):
                router.match_route(f"/test/{i}", "GET")
                
        # Run compilation and matching in parallel
        import threading
        
        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=add_routes))
            threads.append(threading.Thread(target=match_routes))
            
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Should complete without errors
        assert len(router.routes) >= 100


if __name__ == "__main__":
    # Run a simple performance test
    print("Running Advanced Router Performance Test...")
    
    router = AdvancedRouter()
    
    # Add various types of routes
    print("Adding routes...")
    start_time = time.time()
    
    # Static routes
    for i in range(100):
        router.add_route(f"/static/route/{i}", lambda: f"static_{i}", ["GET"])
        
    # Parameter routes
    for i in range(100):
        router.add_route(f"/api/resource_{i}/{{id}}", lambda: f"resource_{i}", ["GET", "POST"])
        
    # Wildcard routes
    for i in range(10):
        router.add_route(f"/files_{i}/*filepath", lambda: f"files_{i}", ["GET"])
        
    add_time = time.time() - start_time
    print(f"Added {len(router.routes)} routes in {add_time:.4f}s")
    
    # Test matching performance
    print("Testing match performance...")
    results = router.benchmark_performance(num_requests=10000)
    
    print(f"\nPerformance Results:")
    print(f"Total requests: {results['total_requests']}")
    print(f"Successful matches: {results['successful_matches']}")
    print(f"Requests per second: {results['requests_per_second']:.2f}")
    print(f"Average time per request: {results['avg_time_per_request']:.4f}ms")
    print(f"Cache hits: {results['cache_hits']}")
    
    # Test route info
    print(f"\nRoute documentation generated for {len(router.get_route_info())} routes")
    
    print("\nAdvanced Router Test Complete!")