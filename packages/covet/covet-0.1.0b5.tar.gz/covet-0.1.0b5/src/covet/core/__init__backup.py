"""
CovetPy Core - Zero-dependency web framework components
"""

# ASGI
from .asgi import (
    BaseHTTPMiddleware,
    CORSMiddleware,
    CovetPyASGI,
    ExceptionMiddleware,
    GZipMiddleware,
    Middleware,
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SessionMiddleware,
    create_app,
)
from .decorators import component, injectable, provider, scoped, singleton, transient

# Dependency Injection
from .di import DIContainer, Scope, get_container

# HTTP components
from .http import (
    Cookie,
    Request,
    Response,
    StreamingResponse,
    error_response,
    html_response,
    json_response,
    redirect_response,
    text_response,
)
from .injection import DependencyModule, DIProxy, ModularDIContainer, lazy

# Content negotiation
from .negotiation import (
    CompressionHandler,
    ContentNegotiator,
    MediaType,
    ResponseProcessor,
)

# Routing
from .routing import CovetRouter, RouteGroup, RouteInfo, create_route_group

# Rust integration
from .rust_integration import (
    RustAsyncBridge,
    RustHttpParser,
    RustIntegratedRouter,
    RustJsonProcessor,
    get_performance_metrics,
    is_rust_available,
)

# WebSocket
from .websocket import (
    WebSocket,
    WebSocketConnectionError,
    WebSocketError,
    WebSocketFrame,
    WebSocketState,
)

# Validation - Skip for now to avoid circular dependencies
# from .validation import (
#     ValidatedModel, Field, ValidationError, ValidationErrors,
#     EmailValidator, URLValidator, RangeValidator,
#     TypeValidator, ConstraintValidator, validate
# )

# Validation integration components would go here when implemented
# from .validation_integration import (
#     validated_route, ValidatedApp,
#     Body, Query, Form,
#     RequestValidator, ResponseValidator
# )

# Utils - Skip imports that cause circular dependencies for now
# from .utils import (
#     performance_timer, JSONEncoder,
#     BatchProcessor, cache_response
# )

# Multipart - Skip for now to avoid circular dependencies
# from .multipart import (
#     MultipartParser, FormField,
#     FileUpload, MultipartFormData
# )


__all__ = [
    # HTTP
    "Request",
    "Response",
    "StreamingResponse",
    "Cookie",
    "json_response",
    "text_response",
    "html_response",
    "redirect_response",
    "error_response",
    # Routing
    "CovetRouter",
    "RouteInfo",
    "RouteGroup",
    "create_route_group",
    # WebSocket
    "WebSocket",
    "WebSocketState",
    "WebSocketFrame",
    "WebSocketError",
    "WebSocketConnectionError",
    # ASGI
    "CovetPyASGI",
    "create_app",
    "Middleware",
    "BaseHTTPMiddleware",
    "CORSMiddleware",
    "RequestLoggingMiddleware",
    "ExceptionMiddleware",
    "SessionMiddleware",
    "RateLimitMiddleware",
    "GZipMiddleware",
    # Dependency Injection
    "DIContainer",
    "Scope",
    "get_container",
    "injectable",
    "provider",
    "singleton",
    "component",
    "scoped",
    "transient",
    "DependencyModule",
    "DIProxy",
    "ModularDIContainer",
    "lazy",
    # Validation
    "ValidatedModel",
    "Field",
    "ValidationError",
    "ValidationErrors",
    "EmailValidator",
    "URLValidator",
    "RangeValidator",
    "TypeValidator",
    "ConstraintValidator",
    "validate",
    # Utils - Skip for now due to circular dependencies
    # 'performance_timer', 'JSONEncoder',
    # 'BatchProcessor', 'cache_response',
    # Multipart - Skip for now due to circular dependencies
    # 'MultipartParser', 'FormField',
    # 'FileUpload', 'MultipartFormData',
    # Content negotiation
    "MediaType",
    "ContentNegotiator",
    "CompressionHandler",
    "ResponseProcessor",
    # Rust integration
    "is_rust_available",
    "get_performance_metrics",
    "RustIntegratedRouter",
    "RustHttpParser",
    "RustJsonProcessor",
    "RustAsyncBridge",
]
