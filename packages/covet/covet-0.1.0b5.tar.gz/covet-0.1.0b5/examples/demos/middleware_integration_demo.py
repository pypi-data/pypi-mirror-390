#!/usr/bin/env python3
"""
CovetPy Middleware System Integration Demo

This demo shows how to integrate the new middleware system with CovetPy applications.
It demonstrates:
- Basic middleware setup
- Built-in middleware configuration
- Custom middleware development
- Production-ready middleware stack
"""

import asyncio
import json
import sys
import time
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, 'src')

from covet.core.middleware_system import (
    MiddlewareStack,
    BaseMiddleware,
    MiddlewareConfig,
    Priority,
    middleware,
    create_middleware_stack
)

from covet.core.builtin_middleware import (
    CORSMiddleware,
    RateLimitingMiddleware,
    RateLimitRule,
    SecurityHeadersMiddleware,
    CompressionMiddleware,
    RequestLoggingMiddleware,
    RequestIDMiddleware,
    create_cors_middleware,
    create_rate_limiting_middleware,
    create_security_headers_middleware,
    create_request_id_middleware
)

from covet.core.http import Request, Response, json_response


# Mock request/response for demonstration
class MockRequest:
    def __init__(self, method="GET", path="/", headers=None, remote_addr="127.0.0.1", scheme="https"):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.remote_addr = remote_addr
        self.scheme = scheme
        self.context = {}
        self.query_string = ""
        self._body = b""
    
    def cookies(self):
        return {}
    
    @property
    def content_type(self):
        return self.headers.get("content-type", "")


class MockResponse:
    def __init__(self, content="", status_code=200, headers=None):
        self.content = content
        self.status_code = status_code
        self.headers = headers or {}
    
    def get_content_bytes(self):
        return self.content.encode('utf-8') if isinstance(self.content, str) else self.content


async def demo_basic_middleware():
    """Demonstrate basic middleware functionality"""
    print("=== Basic Middleware Demo ===")
    
    # Create middleware stack
    stack = create_middleware_stack()
    
    # Add timing middleware
    @middleware(name="timing", priority=Priority.NORMAL.value)
    async def timing_middleware(request, call_next):
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000
        response.headers["X-Processing-Time"] = f"{processing_time:.2f}ms"
        
        return response
    
    # Add request ID middleware
    stack.add(create_request_id_middleware())
    stack.add(timing_middleware)
    
    # Mock handler
    async def hello_handler(request):
        return MockResponse(f"Hello from {request.path}")
    
    # Test request
    request = MockRequest(method="GET", path="/hello")
    response = await stack.process(request, hello_handler)
    
    print(f"Response: {response.content}")
    print(f"Headers: {response.headers}")
    print(f"Request ID: {getattr(request, 'request_id', 'N/A')}")
    print()


async def demo_cors_middleware():
    """Demonstrate CORS middleware"""
    print("=== CORS Middleware Demo ===")
    
    # Create CORS middleware
    cors = create_cors_middleware(
        allow_origins=["https://example.com", "https://app.example.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
        allow_credentials=True
    )
    
    stack = create_middleware_stack()
    stack.add(cors)
    
    # Test preflight request
    preflight_request = MockRequest(
        method="OPTIONS",
        path="/api/users",
        headers={"origin": "https://example.com"}
    )
    
    async def api_handler(request):
        return MockResponse('{"users": []}')
    
    response = await stack.process(preflight_request, api_handler)
    
    print("Preflight Request Response:")
    print(f"Status: {response.status_code}")
    print(f"CORS Headers: {response.headers}")
    
    # Test actual request
    actual_request = MockRequest(
        method="GET",
        path="/api/users",
        headers={"origin": "https://example.com"}
    )
    
    actual_response = MockResponse('{"users": [{"id": 1, "name": "John"}]}')
    result = await cors.process_response(actual_request, actual_response)
    
    print("\nActual Request Response:")
    print(f"CORS Headers: {result.headers}")
    print()


async def demo_rate_limiting():
    """Demonstrate rate limiting middleware"""
    print("=== Rate Limiting Demo ===")
    
    # Create rate limiting middleware
    rate_limiter = create_rate_limiting_middleware(
        default_rule=RateLimitRule(requests=3, window=60),  # 3 requests per minute
        strategy="sliding_window"
    )
    
    stack = create_middleware_stack()
    stack.add(rate_limiter)
    
    async def api_handler(request):
        return MockResponse('{"message": "API response"}')
    
    # Test multiple requests from same IP
    ip_address = "192.168.1.100"
    
    for i in range(5):
        request = MockRequest(
            method="GET",
            path="/api/data",
            remote_addr=ip_address
        )
        
        response = await stack.process(request, api_handler)
        
        print(f"Request {i+1}: Status {response.status_code}")
        if response.status_code == 429:
            print(f"  Rate limited! Headers: {response.headers}")
        else:
            print(f"  Success! Content: {response.content}")
    
    print()


async def demo_security_headers():
    """Demonstrate security headers middleware"""
    print("=== Security Headers Demo ===")
    
    # Create security headers middleware
    security = create_security_headers_middleware(
        hsts_max_age=31536000,  # 1 year
        csp_policy="default-src 'self'; script-src 'self' 'unsafe-inline'",
        frame_options="DENY"
    )
    
    stack = create_middleware_stack()
    stack.add(security)
    
    async def app_handler(request):
        return MockResponse('<html><body>Secure App</body></html>')
    
    # Test HTTPS request
    https_request = MockRequest(
        method="GET",
        path="/app",
        scheme="https"
    )
    
    response = await stack.process(https_request, app_handler)
    
    print("Security Headers Applied:")
    security_headers = {k: v for k, v in response.headers.items() 
                       if k.startswith(('Strict-Transport', 'X-', 'Content-Security', 'Referrer'))}
    
    for header, value in security_headers.items():
        print(f"  {header}: {value}")
    
    print()


async def demo_custom_middleware():
    """Demonstrate custom middleware development"""
    print("=== Custom Middleware Demo ===")
    
    # Create custom authentication middleware
    class APIKeyAuthMiddleware(BaseMiddleware):
        def __init__(self, valid_keys):
            super().__init__(MiddlewareConfig(
                name="api_key_auth",
                priority=Priority.HIGH.value,
                routes=["/api/*"]
            ))
            self.valid_keys = set(valid_keys)
        
        async def process_request(self, request):
            api_key = request.headers.get("x-api-key")
            
            if not api_key:
                return MockResponse(
                    json.dumps({"error": "API key required"}),
                    status_code=401
                )
            
            if api_key not in self.valid_keys:
                return MockResponse(
                    json.dumps({"error": "Invalid API key"}),
                    status_code=403
                )
            
            # Add authentication context
            request.context["authenticated"] = True
            request.context["api_key"] = api_key
            
            return None  # Continue processing
        
        async def process_response(self, request, response):
            response.headers["X-Auth-Method"] = "API-Key"
            return response
    
    # Create stack with custom middleware
    stack = create_middleware_stack()
    stack.add(APIKeyAuthMiddleware(["key123", "admin456"]))
    
    async def protected_handler(request):
        api_key = request.context.get("api_key", "unknown")
        return MockResponse(f'{{"message": "Protected data", "authenticated_with": "{api_key}"}}')
    
    # Test valid API key
    valid_request = MockRequest(
        method="GET",
        path="/api/protected",
        headers={"x-api-key": "key123"}
    )
    
    response = await stack.process(valid_request, protected_handler)
    print(f"Valid API Key - Status: {response.status_code}")
    print(f"Content: {response.content}")
    print(f"Auth Header: {response.headers.get('X-Auth-Method')}")
    
    # Test invalid API key
    invalid_request = MockRequest(
        method="GET",
        path="/api/protected",
        headers={"x-api-key": "invalid"}
    )
    
    response = await stack.process(invalid_request, protected_handler)
    print(f"\nInvalid API Key - Status: {response.status_code}")
    print(f"Content: {response.content}")
    
    print()


async def demo_production_stack():
    """Demonstrate a production-ready middleware stack"""
    print("=== Production Middleware Stack Demo ===")
    
    # Create comprehensive production stack
    stack = create_middleware_stack()
    
    # Add middleware in priority order
    stack.add(create_request_id_middleware(), priority=Priority.CRITICAL.value)
    
    stack.add(create_security_headers_middleware(
        hsts_max_age=31536000,
        csp_policy="default-src 'self'"
    ), priority=Priority.CRITICAL.value)
    
    stack.add(create_cors_middleware(
        allow_origins=["https://myapp.com"],
        allow_credentials=True
    ), priority=Priority.HIGH.value)
    
    stack.add(create_rate_limiting_middleware(
        default_rule=RateLimitRule(requests=100, window=60)
    ), priority=Priority.HIGH.value)
    
    # Custom logging middleware
    @middleware(name="custom_logger", priority=Priority.NORMAL.value)
    async def custom_logger(request, call_next):
        print(f"[LOG] {request.method} {request.path} from {request.remote_addr}")
        
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        
        duration = (end_time - start_time) * 1000
        print(f"[LOG] Response {response.status_code} in {duration:.2f}ms")
        
        return response
    
    stack.add(custom_logger)
    
    print("Production stack created with middleware:")
    for middleware_info in stack.list_middleware():
        print(f"  - {middleware_info['name']} (priority: {middleware_info['priority']})")
    
    # Test the full stack
    async def production_handler(request):
        return MockResponse(json.dumps({
            "message": "Production API response",
            "timestamp": time.time(),
            "request_id": getattr(request, 'request_id', 'N/A')
        }))
    
    request = MockRequest(
        method="GET",
        path="/api/v1/status",
        headers={
            "origin": "https://myapp.com",
            "accept": "application/json"
        },
        remote_addr="203.0.113.1"
    )
    
    print("\nProcessing request through production stack...")
    response = await stack.process(request, production_handler)
    
    print(f"Final Response Status: {response.status_code}")
    print(f"Response Headers: {len(response.headers)} headers applied")
    print(f"Security Headers: {len([h for h in response.headers.keys() if h.startswith('X-') or 'Security' in h])}")
    
    # Show middleware execution stats
    stats = stack.get_stats()
    print(f"\nMiddleware Stats:")
    print(f"  Total requests processed: {stats['total_requests']}")
    print(f"  Middleware executions: {dict(stats['middleware_executions'])}")
    
    print()


async def run_all_demos():
    """Run all middleware demonstrations"""
    print("CovetPy Middleware System Integration Demo")
    print("=" * 50)
    
    await demo_basic_middleware()
    await demo_cors_middleware()
    await demo_rate_limiting()
    await demo_security_headers()
    await demo_custom_middleware()
    await demo_production_stack()
    
    print("=" * 50)
    print("✓ All middleware demos completed successfully!")
    print("\nThe CovetPy middleware system provides:")
    print("  • High-performance pipeline execution")
    print("  • Multiple middleware types (function, class, decorator)")
    print("  • Built-in production-ready middleware components")
    print("  • Conditional execution and route-specific middleware")
    print("  • Priority-based ordering and composition")
    print("  • Comprehensive error handling and monitoring")
    print("  • Zero-dependency implementation")


if __name__ == "__main__":
    asyncio.run(run_all_demos())