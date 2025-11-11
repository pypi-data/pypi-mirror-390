"""
Core middleware implementation - moved from core/middleware.py for better organization.
"""

# Re-export from builtin_middleware for production middleware components
from covet.core.builtin_middleware import (
    CompressionMiddleware,
    CORSMiddleware,
    CSRFMiddleware,
    RateLimitingMiddleware,
    RateLimitRule,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    SessionMiddleware,
    SessionObject,
)

# Re-export from middleware_system for comprehensive middleware support
from covet.core.middleware_system import (
    BaseMiddleware,
    FunctionMiddleware,
    MiddlewareConfig,
    MiddlewareContext,
    MiddlewareStack,
    Priority,
    create_middleware_stack,
    middleware,
    route_middleware,
)

# Alias for backward compatibility
Middleware = BaseMiddleware
MiddlewarePhase = Priority

# Create default middleware configurations
CORS_MIDDLEWARE_CONFIG = MiddlewareConfig(
    name="cors",
    priority=Priority.HIGH.value,
    options={
        "allow_origins": ["*"],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": False,
    },
)

COMPRESSION_MIDDLEWARE_CONFIG = MiddlewareConfig(
    name="compression",
    priority=Priority.NORMAL.value,
    options={
        "minimum_size": 1000,
        "compression_level": 6,
        "enable_brotli": True,
        "enable_gzip": True,
    },
)

# Error handling middleware (simple implementation)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Simple error handling middleware"""

    async def process_request(self, request):
        return request

    async def process_response(self, request, response):
        return response

    async def process_error(self, request, error):
        """Handle errors and return appropriate response"""
        from covet.core.http import json_response

        return json_response({"error": str(error), "type": type(error).__name__}, status_code=500)


# Performance monitoring middleware (simple implementation)


class PerformanceMonitoringMiddleware(BaseMiddleware):
    """Simple performance monitoring middleware"""

    async def process_request(self, request):
        import time

        if not hasattr(request, "context"):
            request.context = {}
        request.context["start_time"] = time.time()
        return request

    async def process_response(self, request, response):
        import time

        if hasattr(request, "context") and "start_time" in request.context:
            duration = time.time() - request.context["start_time"]
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
        return response


# Rate limit middleware alias
RateLimitMiddleware = RateLimitingMiddleware

# Factory functions


def create_default_middleware_stack():
    """Create middleware stack with default middleware"""
    stack = MiddlewareStack()
    return stack


def create_debug_middleware_stack():
    """Create middleware stack for debugging"""
    stack = MiddlewareStack()
    stack.add(RequestLoggingMiddleware())
    stack.add(PerformanceMonitoringMiddleware())
    return stack


__all__ = [
    # Core classes
    "BaseMiddleware",
    "Middleware",
    "MiddlewareConfig",
    "MiddlewareContext",
    "MiddlewarePhase",
    "MiddlewareStack",
    "Priority",
    # Built-in middleware
    "CORSMiddleware",
    "CSRFMiddleware",
    "CompressionMiddleware",
    "ErrorHandlingMiddleware",
    "PerformanceMonitoringMiddleware",
    "RateLimitMiddleware",
    "RateLimitingMiddleware",
    "RateLimitRule",
    "RequestIDMiddleware",
    "RequestLoggingMiddleware",
    "SecurityHeadersMiddleware",
    "SessionMiddleware",
    "SessionObject",
    # Factory functions
    "create_default_middleware_stack",
    "create_debug_middleware_stack",
    "create_middleware_stack",
    "middleware",
    "route_middleware",
    # Configurations
    "CORS_MIDDLEWARE_CONFIG",
    "COMPRESSION_MIDDLEWARE_CONFIG",
]
