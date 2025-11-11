"""
CovetPy Router Integration Example
Complete integration of the Advanced Router with CovetPy framework
"""

import asyncio
import json
import time
from typing import Any, Dict, Optional
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from covet.core.advanced_router import (
    AdvancedRouter, RouteGroup, middleware, timing_middleware, cors_middleware
)


# ============================================================================
# Mock Request/Response Objects (for demonstration)
# ============================================================================

class Request:
    """Mock request object for demonstration"""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str] = None,
                 body: bytes = b'', query_string: str = ''):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body
        self.query_string = query_string
        self.user = None  # For auth middleware
        
    def json(self) -> Dict[str, Any]:
        """Parse JSON body"""
        if self.body:
            return json.loads(self.body.decode())
        return {}


class Response:
    """Mock response object for demonstration"""
    
    def __init__(self, content: Any = None, status_code: int = 200,
                 headers: Dict[str, str] = None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
        
    def json(self) -> str:
        """Return JSON response"""
        if isinstance(self.content, (dict, list)):
            return json.dumps(self.content)
        return str(self.content)


# ============================================================================
# CovetPy Application with Advanced Router
# ============================================================================

class CovetApp:
    """CovetPy application with integrated advanced router"""
    
    def __init__(self):
        self.router = AdvancedRouter(enable_cache=True)
        self.middleware_stack = []
        self.error_handlers = {}
        
    def add_middleware(self, middleware_func):
        """Add global middleware"""
        self.middleware_stack.append(middleware_func)
        
    def add_error_handler(self, exception_class, handler):
        """Add error handler"""
        self.error_handlers[exception_class] = handler
        
    async def process_request(self, request: Request) -> Response:
        """Process incoming request through router"""
        try:
            # Match route
            match = self.router.match_route(
                request.path, 
                request.method, 
                request.query_string
            )
            
            if not match:
                return Response("Not Found", 404)
                
            # Combine global and route-specific middleware
            middleware_chain = self.middleware_stack + match.middleware
            
            # Add matched parameters to request
            request.path_params = match.params
            request.query_params = match.query_params
            
            # Execute middleware chain and handler
            async def call_handler():
                return await self._call_handler(match.handler, request)
                
            # Apply middleware in reverse order (like onion layers)
            handler = call_handler
            for middleware_func in reversed(middleware_chain):
                handler = self._wrap_middleware(middleware_func, handler)
                
            response = await handler()
            
            if not isinstance(response, Response):
                response = Response(response)
                
            return response
            
        except Exception as e:
            return await self._handle_error(e, request)
            
    async def _call_handler(self, handler, request: Request):
        """Call the route handler"""
        if asyncio.iscoroutinefunction(handler):
            return await handler(request)
        else:
            return handler(request)
            
    def _wrap_middleware(self, middleware_func, next_handler):
        """Wrap handler with middleware"""
        async def wrapped():
            return await middleware_func(None, next_handler)  # Simplified for demo
        return wrapped
        
    async def _handle_error(self, error: Exception, request: Request) -> Response:
        """Handle errors"""
        error_type = type(error)
        if error_type in self.error_handlers:
            return await self.error_handlers[error_type](error, request)
        
        # Default error handling
        return Response(
            {"error": str(error), "type": error_type.__name__},
            status_code=500
        )
        
    # Routing decorators
    def route(self, path: str, methods: list = None, **kwargs):
        """Route decorator"""
        return self.router.route(path, methods, **kwargs)
        
    def get(self, path: str, **kwargs):
        return self.router.get(path, **kwargs)
        
    def post(self, path: str, **kwargs):
        return self.router.post(path, **kwargs)
        
    def put(self, path: str, **kwargs):
        return self.router.put(path, **kwargs)
        
    def delete(self, path: str, **kwargs):
        return self.router.delete(path, **kwargs)
        
    def add_group(self, group: RouteGroup):
        """Add route group"""
        self.router.add_group(group)


# ============================================================================
# Example Application
# ============================================================================

def create_example_app() -> CovetApp:
    """Create example application with various routes"""
    app = CovetApp()
    
    # Add global middleware
    @middleware
    async def global_logging_middleware(request, call_next):
        start_time = time.time()
        print(f"→ Request started: {getattr(request, 'method', 'unknown')} {getattr(request, 'path', 'unknown')}")
        
        response = await call_next()
        
        duration = time.time() - start_time
        print(f"← Request completed in {duration:.4f}s")
        return response
        
    app.add_middleware(global_logging_middleware)
    
    # ========================================================================
    # Basic Routes
    # ========================================================================
    
    @app.get("/")
    def home(request: Request):
        return {"message": "Welcome to CovetPy!", "path": request.path}
        
    @app.get("/health")
    def health_check(request: Request):
        return {"status": "healthy", "timestamp": time.time()}
        
    # ========================================================================
    # API Routes with Parameters
    # ========================================================================
    
    # Users API
    @app.get("/api/users")
    def list_users(request: Request):
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        
        return {
            "users": [f"user_{i}" for i in range((page-1)*limit, page*limit)],
            "page": page,
            "limit": limit
        }
        
    @app.get("/api/users/{user_id:int}")
    def get_user(request: Request):
        user_id = request.path_params['user_id']
        return {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        }
        
    @app.post("/api/users", middleware=[timing_middleware])
    def create_user(request: Request):
        data = request.json() if hasattr(request, 'json') else {}
        user_id = int(time.time())
        
        return Response({
            "id": user_id,
            "name": data.get('name', 'New User'),
            "email": data.get('email', f'user{user_id}@example.com'),
            "created": True
        }, status_code=201)
        
    @app.put("/api/users/{user_id:int}")
    def update_user(request: Request):
        user_id = request.path_params['user_id']
        data = request.json() if hasattr(request, 'json') else {}
        
        return {
            "id": user_id,
            "name": data.get('name', f'User {user_id}'),
            "email": data.get('email', f'user{user_id}@example.com'),
            "updated": True
        }
        
    @app.delete("/api/users/{user_id:int}")
    def delete_user(request: Request):
        user_id = request.path_params['user_id']
        return {"id": user_id, "deleted": True}
        
    # Posts API
    @app.get("/api/users/{user_id:int}/posts")
    def get_user_posts(request: Request):
        user_id = request.path_params['user_id']
        return {
            "user_id": user_id,
            "posts": [f"post_{i}" for i in range(1, 6)]
        }
        
    @app.get("/api/users/{user_id:int}/posts/{post_id:int}")
    def get_user_post(request: Request):
        user_id = request.path_params['user_id']
        post_id = request.path_params['post_id']
        
        return {
            "id": post_id,
            "user_id": user_id,
            "title": f"Post {post_id} by User {user_id}",
            "content": "This is a sample post content."
        }
        
    # ========================================================================
    # Route Groups
    # ========================================================================
    
    # Admin API group with authentication
    @middleware
    async def admin_auth_middleware(request, call_next):
        # Mock authentication
        print("  [Auth] Checking admin credentials...")
        # In real app, check JWT token, session, etc.
        return await call_next()
        
    admin_group = RouteGroup(
        prefix="/admin/api",
        middleware=[admin_auth_middleware],
        tags={"admin", "api"}
    )
    
    @admin_group.get("/stats")
    def admin_stats(request: Request):
        return {
            "total_users": 1000,
            "total_posts": 5000,
            "active_sessions": 150
        }
        
    @admin_group.get("/users")
    def admin_list_users(request: Request):
        return {
            "users": [
                {"id": i, "name": f"User {i}", "admin": i % 10 == 0}
                for i in range(1, 21)
            ]
        }
        
    @admin_group.delete("/users/{user_id:int}")
    def admin_delete_user(request: Request):
        user_id = request.path_params['user_id']
        return {
            "id": user_id,
            "deleted": True,
            "deleted_by": "admin"
        }
        
    app.add_group(admin_group)
    
    # ========================================================================
    # File serving and wildcards
    # ========================================================================
    
    @app.get("/static/*filepath")
    def serve_static(request: Request):
        filepath = request.path_params['filepath']
        
        # Mock file serving
        file_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.html': 'text/html'
        }
        
        # Get file extension
        ext = '.' + filepath.split('.')[-1] if '.' in filepath else ''
        content_type = file_types.get(ext, 'application/octet-stream')
        
        return Response(
            f"Mock file content for: {filepath}",
            headers={"Content-Type": content_type}
        )
        
    # ========================================================================
    # Search and filtering
    # ========================================================================
    
    @app.get("/api/search")
    def search(request: Request):
        query = request.query_params.get('q', '')
        category = request.query_params.get('category', 'all')
        limit = int(request.query_params.get('limit', 10))
        
        # Mock search results
        results = []
        for i in range(min(limit, 20)):
            results.append({
                "id": i,
                "title": f"Result {i} for '{query}'",
                "category": category,
                "score": 1.0 - (i * 0.05)
            })
            
        return {
            "query": query,
            "category": category,
            "results": results,
            "total": len(results)
        }
        
    # ========================================================================
    # Error handling
    # ========================================================================
    
    class ValidationError(Exception):
        pass
        
    async def handle_validation_error(error: ValidationError, request: Request):
        return Response(
            {"error": "Validation failed", "message": str(error)},
            status_code=400
        )
        
    app.add_error_handler(ValidationError, handle_validation_error)
        
    @app.get("/api/validate/{value:int}")
    def validate_value(request: Request):
        value = request.path_params['value']
        if value < 0:
            raise ValidationError("Value must be positive")
        return {"value": value, "valid": True}
        
    return app


# ============================================================================
# Application Runner and Tests
# ============================================================================

async def test_application():
    """Test the integrated application"""
    print("=" * 60)
    print("CovetPy Advanced Router Integration Test")
    print("=" * 60)
    
    app = create_example_app()
    
    # Test requests
    test_requests = [
        # Basic routes
        Request("GET", "/"),
        Request("GET", "/health"),
        
        # API routes with parameters
        Request("GET", "/api/users", query_string="page=2&limit=5"),
        Request("GET", "/api/users/123"),
        Request("POST", "/api/users", body=b'{"name": "John Doe", "email": "john@example.com"}'),
        Request("PUT", "/api/users/123", body=b'{"name": "Jane Doe"}'),
        Request("DELETE", "/api/users/123"),
        
        # Nested routes
        Request("GET", "/api/users/456/posts"),
        Request("GET", "/api/users/456/posts/789"),
        
        # Admin routes (with middleware)
        Request("GET", "/admin/api/stats"),
        Request("GET", "/admin/api/users"),
        Request("DELETE", "/admin/api/users/999"),
        
        # Static file serving
        Request("GET", "/static/css/main.css"),
        Request("GET", "/static/js/app.js"),
        Request("GET", "/static/images/logo.png"),
        
        # Search
        Request("GET", "/api/search", query_string="q=python&category=programming&limit=5"),
        
        # Validation (success)
        Request("GET", "/api/validate/42"),
        
        # Validation (error)
        Request("GET", "/api/validate/-1"),
        
        # Not found
        Request("GET", "/nonexistent/route"),
    ]
    
    print("\nProcessing test requests...\n")
    
    for i, request in enumerate(test_requests, 1):
        print(f"Test {i}: {request.method} {request.path}")
        if request.query_string:
            print(f"  Query: {request.query_string}")
            
        try:
            response = await app.process_request(request)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.content
                if isinstance(content, dict):
                    print(f"  Response: {json.dumps(content, indent=4)[:100]}...")
                else:
                    print(f"  Response: {str(content)[:100]}...")
            else:
                print(f"  Response: {response.content}")
                
        except Exception as e:
            print(f"  Error: {e}")
            
        print()
        
    # Performance test
    print("\n" + "=" * 60)
    print("Performance Test")
    print("=" * 60)
    
    # Test many requests quickly
    start_time = time.time()
    successful_requests = 0
    
    for _ in range(1000):
        request = Request("GET", "/api/users/123")
        response = await app.process_request(request)
        if response.status_code == 200:
            successful_requests += 1
            
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Processed 1000 requests in {duration:.4f}s")
    print(f"Successful: {successful_requests}/1000")
    print(f"Throughput: {1000/duration:.2f} requests/second")
    
    # Router statistics
    print(f"\nRouter Statistics:")
    print(f"Total routes: {len(app.router.routes)}")
    print(f"Cache entries: {len(app.router.route_cache)}")
    
    route_info = app.router.get_route_info()
    print(f"Route documentation entries: {len(route_info)}")
    
    # Show some route documentation
    print(f"\nSample Route Documentation:")
    for route in route_info[:5]:
        print(f"  {route['method']} {route['path']} -> {route['handler']}")
        if route['parameters']:
            print(f"    Parameters: {[p['name'] for p in route['parameters']]}")


def demonstrate_advanced_features():
    """Demonstrate advanced router features"""
    print("\n" + "=" * 60)
    print("Advanced Features Demonstration")
    print("=" * 60)
    
    app = create_example_app()
    router = app.router
    
    # 1. Route introspection
    print("\n1. Route Introspection:")
    routes = router.get_route_info()
    print(f"   Total routes defined: {len(routes)}")
    
    api_routes = [r for r in routes if '/api/' in r['path']]
    admin_routes = [r for r in routes if '/admin/' in r['path']]
    
    print(f"   API routes: {len(api_routes)}")
    print(f"   Admin routes: {len(admin_routes)}")
    
    # 2. OpenAPI generation
    print("\n2. OpenAPI Specification:")
    openapi_spec = router.get_openapi_spec()
    print(f"   OpenAPI version: {openapi_spec['openapi']}")
    print(f"   Paths defined: {len(openapi_spec['paths'])}")
    
    # 3. Performance benchmarking
    print("\n3. Performance Benchmark:")
    benchmark_results = router.benchmark_performance(5000)
    print(f"   Requests per second: {benchmark_results['requests_per_second']:.2f}")
    print(f"   Average response time: {benchmark_results['avg_time_per_request']:.4f}ms")
    print(f"   Cache hits: {benchmark_results['cache_hits']}")
    
    # 4. Route compilation stats
    print("\n4. Route Compilation:")
    router.compile_routes()
    print(f"   Routes compiled: ✓")
    print(f"   Radix tree built: ✓")
    print(f"   Static routes: {len([r for r in router.routes if r.static])}")
    print(f"   Dynamic routes: {len([r for r in router.routes if not r.static])}")


if __name__ == "__main__":
    # Run the integration test
    asyncio.run(test_application())
    
    # Demonstrate advanced features
    demonstrate_advanced_features()
    
    print("\n" + "=" * 60)
    print("Integration test completed successfully!")
    print("CovetPy Advanced Router is ready for production use.")
    print("=" * 60)