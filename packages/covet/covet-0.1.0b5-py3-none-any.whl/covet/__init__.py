"""
CovetPy - Zero-dependency, high-performance Python web framework.

A comprehensive framework providing:
- Zero external dependencies for core functionality
- High-performance ASGI application server
- Advanced dependency injection container
- Flexible plugin architecture
- Comprehensive configuration management
- Structured logging and observability
- Middleware pipeline system
- WebSocket real-time APIs
- Request/response validation
- Cross-language FFI bindings
- Production-ready error handling
- CLI tooling for development
- Enterprise compliance frameworks (HIPAA, PCI-DSS, GDPR, CCPA)
- Advanced security controls and audit logging
- Data classification and encryption systems

Get started quickly:
    from covet import CovetPy

    app = CovetPy()

    @app.route("/")
    async def hello(request):
        return {"message": "Hello, World!"}

    if __name__ == "__main__":
        app.run()

For enterprise compliance:
    from covet.compliance import configure_full_compliance
    configure_full_compliance(app)
"""

# Core application
from covet.core.app import Covet, CovetApp, CovetApplication, create_app

# HTTP components
from covet.core.http import (
    Request,
    Response,
    StreamingResponse,
    JSONResponse,
    Cookie,
    json_response,
    html_response,
    text_response,
    redirect_response,
    error_response,
)

# Routing
from covet.core.routing import CovetRouter, Router

# Configuration
from covet.config import Settings, settings

# ASGI and Middleware (optional, for advanced usage)
try:
    from covet.core.asgi import (
        CovetPyASGI,
        BaseHTTPMiddleware,
        CORSMiddleware,
        ExceptionMiddleware,
        GZipMiddleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware,
        SessionMiddleware,
        Middleware,
    )
except ImportError:
    # Graceful fallback if ASGI components not available
    CovetPyASGI = None
    BaseHTTPMiddleware = None
    CORSMiddleware = None
    ExceptionMiddleware = None
    GZipMiddleware = None
    RateLimitMiddleware = None
    RequestLoggingMiddleware = None
    SessionMiddleware = None
    Middleware = None

__version__ = "0.1.0b5"
__author__ = "CovetPy Team"
__email__ = "hello@covetpy.dev"
__license__ = "MIT"
__description__ = "A modern Python web framework inspired by Flask and FastAPI"

# Backwards compatibility: Create aliases
# The new Covet class from core.app is the main class now
CovetPy = Covet  # Old name for backwards compatibility
Config = Settings  # Alias for configuration class
App = Covet  # Alternative alias
Framework = Covet  # Descriptive alias
Application = CovetApplication  # Standard Application alias

# API and Integration layer modules - temporarily disabled to fix core import issues
# from . import api
# Integration modules not fully implemented yet
# from . import integration

# Public API exports - only include stable, well-tested components
__all__ = [
    # Version and metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    # Main application classes - Primary entry points for developers
    "CovetPy",  # Main high-level Flask-like API
    "Covet",  # Alias for CovetPy
    "CovetApp",  # Alternative application class
    "CovetApplication",  # Base application class
    # Configuration management - Essential for app setup
    "Config",  # Configuration class
    "Environment",  # Environment enumeration
    "ConfigManager",  # Multi-config management
    "Settings",  # Settings from config module
    "settings",  # Default settings instance
    # Plugin and extension system
    "PluginManager",  # Plugin management
    "PluginRegistry",  # Plugin registration
    # Core exceptions - For error handling
    "CovetError",  # Base framework exception
    "ConfigurationError",  # Configuration errors
    # ASGI application - For production deployment
    "CovetPyASGI",  # Core ASGI application
    "create_app",  # Application factory function
    # HTTP components - Core request/response handling
    "Request",  # HTTP request object
    "Response",  # HTTP response object
    "StreamingResponse",  # Streaming response for large data
    "JSONResponse",  # JSON response object
    "Cookie",  # Cookie handling
    # Response helpers - Convenient response creation
    "json_response",  # JSON response helper
    "text_response",  # Plain text response helper
    "html_response",  # HTML response helper
    "redirect_response",  # Redirect response helper
    "error_response",  # Error response helper
    # Middleware system - Request/response processing pipeline
    "Middleware",  # Base middleware class
    "BaseHTTPMiddleware",  # HTTP middleware base
    "CORSMiddleware",  # Cross-origin resource sharing
    "RequestLoggingMiddleware",  # Request logging
    "ExceptionMiddleware",  # Exception handling
    "SessionMiddleware",  # Session management
    "RateLimitMiddleware",  # Rate limiting protection
    "GZipMiddleware",  # Response compression
    # Routing - URL routing and path matching
    "CovetRouter",  # Router class
    "Router",  # Router alias
    # Configuration and settings
    "Settings",  # Application settings class
    "settings",  # Default settings instance
    # Framework aliases - Alternative names for main classes
    "App",  # Alias for CovetPy
    "Framework",  # Descriptive alias for CovetPy
    "Application",  # Standard Application alias for CovetApplication
]
