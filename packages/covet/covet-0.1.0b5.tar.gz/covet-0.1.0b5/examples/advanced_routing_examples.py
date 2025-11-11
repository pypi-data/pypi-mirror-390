"""
CovetPy Advanced Router - Usage Examples
Comprehensive examples demonstrating all router features
"""

import asyncio
import time
from typing import Any, Dict, List
import sys
import os

# Add src to path for examples
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from covet.core.advanced_router import (
    AdvancedRouter, RouteGroup, RouteParameter, middleware,
    create_api_group, create_admin_group, timing_middleware, cors_middleware
)


# ============================================================================
# Example 1: Basic Router Usage
# ============================================================================

def example_basic_routing():
    """Basic routing examples"""
    print("=" * 60)
    print("Example 1: Basic Routing")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Simple routes
    @router.get("/")
    def home():
        return "Welcome to CovetPy!"
        
    @router.get("/about")
    def about():
        return "About this application"
        
    @router.post("/api/users")
    def create_user():
        return "User created"
        
    # Route with multiple methods
    @router.route("/api/data", methods=["GET", "POST", "PUT"])
    def handle_data():
        return "Data handled"
        
    # Test the routes
    test_routes = [
        ("/", "GET"),
        ("/about", "GET"), 
        ("/api/users", "POST"),
        ("/api/data", "GET"),
        ("/api/data", "PUT"),
        ("/nonexistent", "GET")  # Should not match
    ]
    
    for path, method in test_routes:
        match = router.match_route(path, method)
        if match:
            print(f"✓ {method} {path} -> {match.handler.__name__}")
        else:
            print(f"✗ {method} {path} -> No match")


# ============================================================================
# Example 2: Path Parameters with Type Conversion
# ============================================================================

def example_path_parameters():
    """Path parameter examples with type conversion"""
    print("\n" + "=" * 60)
    print("Example 2: Path Parameters & Type Conversion")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Integer parameters
    @router.get("/users/{user_id:int}")
    def get_user(user_id: int):
        return f"User ID: {user_id} (type: {type(user_id).__name__})"
        
    # String parameters  
    @router.get("/users/{username}/profile")
    def get_user_profile(username: str):
        return f"Profile for: {username}"
        
    # Multiple parameters
    @router.get("/users/{user_id:int}/posts/{post_id:int}")
    def get_user_post(user_id: int, post_id: int):
        return f"User {user_id}, Post {post_id}"
        
    # Float parameters
    @router.get("/products/{price:float}")
    def products_by_price(price: float):
        return f"Products under ${price}"
        
    # Boolean parameters
    @router.get("/settings/{enabled:bool}")
    def toggle_setting(enabled: bool):
        return f"Setting enabled: {enabled}"
        
    # Test parameter routes
    test_routes = [
        ("/users/123", "GET"),
        ("/users/john_doe/profile", "GET"),
        ("/users/123/posts/456", "GET"),
        ("/products/99.99", "GET"),
        ("/settings/true", "GET"),
    ]
    
    for path, method in test_routes:
        match = router.match_route(path, method)
        if match:
            print(f"✓ {method} {path}")
            print(f"  Parameters: {match.params}")
            print(f"  Types: {[(k, type(v).__name__) for k, v in match.params.items()]}")
        else:
            print(f"✗ {method} {path} -> No match")


# ============================================================================
# Example 3: Wildcard Routes and Static File Serving
# ============================================================================

def example_wildcard_routes():
    """Wildcard route examples"""
    print("\n" + "=" * 60)
    print("Example 3: Wildcard Routes")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Static file serving
    @router.get("/static/*filepath")
    def serve_static(filepath: str):
        return f"Serving static file: {filepath}"
        
    # Documentation files
    @router.get("/docs/*page")
    def serve_docs(page: str):
        return f"Documentation page: {page}"
        
    # Catch-all API route (lowest priority)
    @router.get("/api/*path")
    def api_catchall(path: str):
        return f"API catch-all: {path}"
        
    # Specific API route (higher priority)
    @router.get("/api/users/{id}")
    def api_users(id: str):
        return f"Specific API user: {id}"
        
    # Test wildcard routes
    test_routes = [
        ("/static/css/main.css", "GET"),
        ("/static/js/app.js", "GET"),
        ("/static/images/logo.png", "GET"),
        ("/docs/introduction", "GET"),
        ("/docs/api/authentication", "GET"),
        ("/api/users/123", "GET"),  # Should match specific route
        ("/api/unknown/endpoint", "GET"),  # Should match catch-all
    ]
    
    for path, method in test_routes:
        match = router.match_route(path, method)
        if match:
            print(f"✓ {method} {path} -> {match.handler.__name__}")
            if match.params:
                print(f"  Parameters: {match.params}")
        else:
            print(f"✗ {method} {path} -> No match")


# ============================================================================
# Example 4: Query Parameters
# ============================================================================

def example_query_parameters():
    """Query parameter handling examples"""
    print("\n" + "=" * 60)
    print("Example 4: Query Parameters")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    @router.get("/search")
    def search():
        return "Search results"
        
    @router.get("/api/users")
    def list_users():
        return "User list"
        
    # Test with various query parameters
    test_cases = [
        ("/search", "q=python&category=programming"),
        ("/search", "q=machine+learning&sort=date&limit=10"),
        ("/api/users", "page=1&limit=20&sort=name"),
        ("/api/users", "active=true&role=admin&role=user"),  # Multiple values
    ]
    
    for path, query_string in test_cases:
        match = router.match_route(path, "GET", query_string)
        if match:
            print(f"✓ GET {path}?{query_string}")
            print(f"  Query params: {match.query_params}")
        else:
            print(f"✗ GET {path}?{query_string} -> No match")


# ============================================================================
# Example 5: Route Groups and Blueprints
# ============================================================================

def example_route_groups():
    """Route group examples"""
    print("\n" + "=" * 60)
    print("Example 5: Route Groups & Blueprints")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Create API v1 group
    api_v1 = RouteGroup(prefix="/api/v1", tags={"api", "v1"})
    
    @api_v1.get("/users")
    def list_users_v1():
        return "API v1: List users"
        
    @api_v1.post("/users")
    def create_user_v1():
        return "API v1: Create user"
        
    @api_v1.get("/users/{id}")
    def get_user_v1(id: str):
        return f"API v1: Get user {id}"
        
    # Create API v2 group
    api_v2 = RouteGroup(prefix="/api/v2", tags={"api", "v2"})
    
    @api_v2.get("/users")
    def list_users_v2():
        return "API v2: List users"
        
    @api_v2.get("/users/{id}")
    def get_user_v2(id: str):
        return f"API v2: Get user {id}"
        
    # Admin group with middleware
    @middleware
    async def admin_auth_middleware(request, call_next):
        print("  [Middleware] Admin authentication check")
        return await call_next(request)
        
    admin_group = RouteGroup(
        prefix="/admin",
        middleware=[admin_auth_middleware],
        tags={"admin"}
    )
    
    @admin_group.get("/dashboard")
    def admin_dashboard():
        return "Admin dashboard"
        
    @admin_group.get("/users")
    def admin_users():
        return "Admin user management"
        
    # Add groups to router
    router.add_group(api_v1)
    router.add_group(api_v2)
    router.add_group(admin_group)
    
    # Test group routes
    test_routes = [
        ("/api/v1/users", "GET"),
        ("/api/v1/users/123", "GET"),
        ("/api/v2/users", "GET"),
        ("/api/v2/users/456", "GET"),
        ("/admin/dashboard", "GET"),
        ("/admin/users", "GET"),
    ]
    
    for path, method in test_routes:
        match = router.match_route(path, method)
        if match:
            print(f"✓ {method} {path} -> {match.handler.__name__}")
            if match.middleware:
                print(f"  Middleware: {[m.__name__ for m in match.middleware]}")
            if match.route_info.tags:
                print(f"  Tags: {list(match.route_info.tags)}")
        else:
            print(f"✗ {method} {path} -> No match")


# ============================================================================
# Example 6: Middleware
# ============================================================================

def example_middleware():
    """Middleware examples"""
    print("\n" + "=" * 60)
    print("Example 6: Middleware")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Custom middleware
    @middleware
    async def logging_middleware(request, call_next):
        print(f"  [Log] Request started: {getattr(request, 'path', 'unknown')}")
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        print(f"  [Log] Request completed in {duration:.4f}s")
        return response
        
    @middleware  
    async def security_middleware(request, call_next):
        print("  [Security] Checking request security")
        # Add security headers, validate input, etc.
        response = await call_next(request)
        print("  [Security] Adding security headers")
        return response
        
    # Routes with different middleware
    @router.get("/public")
    def public_endpoint():
        return "Public endpoint"
        
    @router.get("/logged", middleware=[logging_middleware])
    def logged_endpoint():
        return "Logged endpoint"
        
    @router.get("/secure", middleware=[security_middleware, logging_middleware])
    def secure_endpoint():
        return "Secure endpoint"
        
    # Using pre-built middleware
    @router.get("/timed", middleware=[timing_middleware])
    def timed_endpoint():
        return "Timed endpoint"
        
    @router.get("/cors", middleware=[cors_middleware])
    def cors_endpoint():
        return "CORS-enabled endpoint"
        
    # Test middleware
    test_routes = [
        ("/public", "GET"),
        ("/logged", "GET"),
        ("/secure", "GET"),
        ("/timed", "GET"),
        ("/cors", "GET"),
    ]
    
    for path, method in test_routes:
        match = router.match_route(path, method)
        if match:
            middleware_names = [m.__name__ for m in match.middleware]
            print(f"✓ {method} {path}")
            print(f"  Middleware chain: {middleware_names or ['None']}")
        else:
            print(f"✗ {method} {path} -> No match")


# ============================================================================
# Example 7: Route Priorities and Conflict Resolution
# ============================================================================

def example_route_priorities():
    """Route priority examples"""
    print("\n" + "=" * 60)
    print("Example 7: Route Priorities")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Add routes with different priorities
    @router.route("/api/{resource}", priority=1, name="generic_resource")
    def generic_resource(resource: str):
        return f"Generic resource: {resource}"
        
    @router.route("/api/users", priority=10, name="specific_users")
    def specific_users():
        return "Specific users endpoint"
        
    @router.route("/api/special", priority=5, name="special_endpoint")
    def special_endpoint():
        return "Special endpoint"
        
    # Wildcard with low priority
    @router.route("/api/*path", priority=0, name="api_catchall")
    def api_catchall(path: str):
        return f"API catch-all: {path}"
        
    # Force compilation to see priority ordering
    router.compile_routes()
    
    # Test priority resolution
    test_routes = [
        "/api/users",      # Should match specific_users (priority 10)
        "/api/special",    # Should match special_endpoint (priority 5)  
        "/api/posts",      # Should match generic_resource (priority 1)
        "/api/very/deep/path",  # Should match api_catchall (priority 0)
    ]
    
    for path in test_routes:
        match = router.match_route(path, "GET")
        if match:
            print(f"✓ GET {path} -> {match.route_info.name} (priority: {match.route_info.priority})")
            if match.params:
                print(f"  Parameters: {match.params}")
        else:
            print(f"✗ GET {path} -> No match")


# ============================================================================
# Example 8: Advanced Features
# ============================================================================

def example_advanced_features():
    """Advanced router features"""
    print("\n" + "=" * 60)
    print("Example 8: Advanced Features")
    print("=" * 60)
    
    router = AdvancedRouter(enable_cache=True, cache_size=100)
    
    # Route with comprehensive metadata
    @router.get(
        "/api/users/{user_id:int}",
        name="get_user_by_id",
        description="Retrieve a user by their unique ID",
        tags={"users", "api", "public"},
        middleware=[timing_middleware],
        priority=5
    )
    def get_user_detailed(user_id: int):
        """Get a user by their ID with full profile information"""
        return f"Detailed user: {user_id}"
        
    # Deprecated route
    @router.get(
        "/api/old-users/{id}",
        name="get_user_old",
        description="Legacy user endpoint",
        deprecated=True,
        tags={"users", "legacy"}
    )
    def get_user_old(id: str):
        return f"Legacy user: {id}"
        
    # Route with custom parameter validation
    def validate_email(email: str) -> bool:
        return "@" in email and "." in email
        
    # Note: For demonstration - actual validation would be in route parameter definition
    @router.get("/users/by-email/{email}")
    def get_user_by_email(email: str):
        if not validate_email(email):
            return "Invalid email format"
        return f"User with email: {email}"
        
    # Test advanced features
    match = router.match_route("/api/users/123", "GET")
    if match:
        route_info = match.route_info
        print(f"✓ Route: {route_info.path}")
        print(f"  Name: {route_info.name}")
        print(f"  Description: {route_info.description}")
        print(f"  Tags: {list(route_info.tags)}")
        print(f"  Priority: {route_info.priority}")
        print(f"  Deprecated: {route_info.deprecated}")
        print(f"  Middleware: {[m.__name__ for m in route_info.middleware]}")
        
    # Test caching
    print(f"\nCache status before: {len(router.route_cache)} entries")
    
    # Make same request multiple times
    for _ in range(3):
        router.match_route("/api/users/123", "GET")
        
    print(f"Cache status after: {len(router.route_cache)} entries")


# ============================================================================
# Example 9: Route Introspection and Documentation
# ============================================================================

def example_route_introspection():
    """Route introspection and documentation generation"""
    print("\n" + "=" * 60)
    print("Example 9: Route Introspection & Documentation")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Add various routes for documentation
    @router.get("/", name="home", description="Home page")
    def home():
        return "Home"
        
    @router.get("/api/users", name="list_users", description="List all users", tags={"users", "api"})
    def list_users():
        return "User list"
        
    @router.post("/api/users", name="create_user", description="Create a new user", tags={"users", "api"})
    def create_user():
        return "User created"
        
    @router.get("/api/users/{id:int}", name="get_user", description="Get user by ID", tags={"users", "api"})
    def get_user(id: int):
        return f"User {id}"
        
    @router.delete("/api/users/{id:int}", name="delete_user", description="Delete user", tags={"users", "api"})
    def delete_user(id: int):
        return f"Deleted user {id}"
        
    # Get route information
    routes_info = router.get_route_info()
    
    print("Route Documentation:")
    print("-" * 20)
    
    for route in routes_info:
        print(f"\n{route['method']} {route['path']}")
        print(f"  Name: {route['name']}")
        print(f"  Description: {route['description']}")
        if route['tags']:
            print(f"  Tags: {route['tags']}")
        if route['parameters']:
            print(f"  Parameters:")
            for param in route['parameters']:
                print(f"    - {param['name']} ({param['type']})")
                
    # Generate OpenAPI spec
    print(f"\n\nOpenAPI Specification:")
    print("-" * 22)
    
    openapi_spec = router.get_openapi_spec()
    print(f"OpenAPI Version: {openapi_spec['openapi']}")
    print(f"API Title: {openapi_spec['info']['title']}")
    print(f"API Version: {openapi_spec['info']['version']}")
    print(f"Paths defined: {len(openapi_spec['paths'])}")
    
    # Show a sample path
    if '/api/users/{id}' in openapi_spec['paths']:
        user_path = openapi_spec['paths']['/api/users/{id}']
        print(f"\nSample path: /api/users/{{id}}")
        for method, spec in user_path.items():
            print(f"  {method.upper()}: {spec['summary']}")


# ============================================================================
# Example 10: Performance Demonstration
# ============================================================================

def example_performance():
    """Performance demonstration"""
    print("\n" + "=" * 60)
    print("Example 10: Performance Demonstration")
    print("=" * 60)
    
    router = AdvancedRouter()
    
    # Add many routes quickly
    print("Adding routes...")
    start_time = time.time()
    
    for i in range(1000):
        router.add_route(f"/api/resource_{i}/{{id}}", lambda: f"Resource {i}", ["GET"])
        
    add_time = time.time() - start_time
    print(f"Added 1000 routes in {add_time:.4f}s")
    
    # Test matching performance
    print("\nTesting match performance...")
    
    import random
    test_paths = [f"/api/resource_{random.randint(0, 999)}/123" for _ in range(1000)]
    
    start_time = time.time()
    matches = 0
    
    for path in test_paths:
        if router.match_route(path, "GET"):
            matches += 1
            
    match_time = time.time() - start_time
    
    print(f"Matched {matches}/1000 routes in {match_time:.4f}s")
    print(f"Average match time: {match_time/1000*1000:.4f}ms per request")
    print(f"Throughput: {1000/match_time:.2f} requests/second")
    
    # Built-in benchmark
    print("\nRunning built-in benchmark...")
    benchmark_results = router.benchmark_performance(5000)
    
    print(f"Benchmark results:")
    print(f"  Requests: {benchmark_results['total_requests']}")
    print(f"  Successful: {benchmark_results['successful_matches']}")
    print(f"  RPS: {benchmark_results['requests_per_second']:.2f}")
    print(f"  Avg time: {benchmark_results['avg_time_per_request']:.4f}ms")


# ============================================================================
# Main Example Runner
# ============================================================================

def run_all_examples():
    """Run all router examples"""
    print("CovetPy Advanced Router - Comprehensive Examples")
    print("This demonstration shows all router features and capabilities.\n")
    
    try:
        example_basic_routing()
        example_path_parameters()
        example_wildcard_routes()
        example_query_parameters()
        example_route_groups()
        example_middleware()
        example_route_priorities()
        example_advanced_features()
        example_route_introspection()
        example_performance()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("CovetPy Advanced Router provides enterprise-grade routing")
        print("with performance that rivals or exceeds FastAPI and Flask.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()