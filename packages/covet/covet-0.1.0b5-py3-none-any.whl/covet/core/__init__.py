"""
CovetPy Core - Zero-dependency web framework components (minimal version)
"""

import json
import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Import our new, simplified application
from covet.core.app import Covet, CovetApp, CovetApplication, create_app

# Import routing
from covet.core.routing import CovetRouter

# Import ASGI and middleware (with fallback)
try:
    from covet.core.asgi import (
        BaseHTTPMiddleware,
        CORSMiddleware,
        CovetPyASGI,
        ExceptionMiddleware,
        GZipMiddleware,
        Middleware,
        RateLimitMiddleware,
        RequestLoggingMiddleware,
        SessionMiddleware,
    )
except ImportError:
    # Graceful fallback
    BaseHTTPMiddleware = None
    CORSMiddleware = None
    CovetPyASGI = None
    ExceptionMiddleware = None
    GZipMiddleware = None
    Middleware = None
    RateLimitMiddleware = None
    RequestLoggingMiddleware = None
    SessionMiddleware = None

# Import legacy components for backwards compatibility
try:
    from covet.core.advanced_router import AdvancedRouter
    from covet.core.asgi_app import CovetASGIApp, create_asgi_app
except ImportError:
    AdvancedRouter = None
    CovetASGIApp = None
    create_asgi_app = None
# Import HTTP components
from covet.core.http import (
    Cookie,
    JSONResponse,
    Request,
    Response,
    StreamingResponse,
    error_response,
    html_response,
    json_response,
    redirect_response,
    text_response,
)

# Import routing components
from covet.core.routing import RouteGroup, RouteMatch, create_route_group

# Import HTTP server (with fallback)
try:
    from covet.core.http_server import (
        CovetHTTPServer,
        HTTPServer,
        ServerConfig,
        run_server,
    )
except ImportError:
    CovetHTTPServer = None
    HTTPServer = None
    ServerConfig = None
    run_server = None


class Environment(Enum):
    """Application environment."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class Config:
    """Application configuration."""

    def __init__(self, config_dict: Optional[dict[str, Any]] = None) -> None:
        self._config = config_dict or {}
        self.environment = Environment(self._config.get("environment", "development"))
        self.debug = self._config.get("debug", self.environment == Environment.DEVELOPMENT)
        self.host = self._config.get("host", "127.0.0.1")
        self.port = self._config.get("port", 8000)
        self.workers = self._config.get("workers", 1)
        self.app_name = self._config.get("app_name", "CovetPy")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    @classmethod
    def from_file(cls, path: str) -> "Config":
        """Load configuration from file."""
        with open(path) as f:
            if path.endswith(".json"):
                config_dict = json.load(f)
            else:
                # Simple key=value parser
                config_dict = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        config_dict[key.strip()] = value.strip()
        return cls(config_dict)


class ConfigManager:
    """Manage application configuration."""

    def __init__(self) -> None:
        self.configs: dict[str, Config] = {}
        self.active_config: Optional[Config] = None

    def load_config(self, name: str, config: Config) -> None:
        """Load a configuration."""
        self.configs[name] = config
        if not self.active_config:
            self.active_config = config

    def set_active(self, name: str) -> None:
        """Set active configuration."""
        if name in self.configs:
            self.active_config = self.configs[name]
        else:
            raise ValueError(f"Configuration '{name}' not found")

    def get_active(self) -> Config:
        """Get active configuration."""
        if not self.active_config:
            self.active_config = Config()
        return self.active_config


class PluginRegistry:
    """Registry for plugins."""

    def __init__(self) -> None:
        self.plugins: dict[str, Any] = {}

    def register(self, name: str, plugin: Any) -> None:
        """Register a plugin."""
        self.plugins[name] = plugin

    def get(self, name: str) -> Any:
        """Get a plugin."""
        return self.plugins.get(name)

    def list(self) -> list[str]:
        """List all plugin names."""
        return list(self.plugins.keys())


class PluginManager:
    """Manage plugins."""

    def __init__(self) -> None:
        self.registry = PluginRegistry()
        self.loaded_plugins: dict[str, Any] = {}

    def load_plugin(self, name: str, module_path: str) -> None:
        """Load a plugin from module path."""
        # Simple implementation - just store the path
        self.registry.register(name, module_path)

    def get_plugin(self, name: str) -> Any:
        """Get a loaded plugin."""
        return self.registry.get(name)


# CovetApp, CovetApplication, and Covet are all imported from app.py
# They are the same class with different aliases for backwards compatibility


# Also need the exceptions module
class CovetError(Exception):
    """Base exception for Covet."""


class ConfigurationError(CovetError):
    """Configuration error."""


# ASGI - now enabled

# Enhanced ASGI app

# HTTP components - now enabled

# HTTP Server - production-grade HTTP/1.1 server

# Routing - CRITICAL: Export CovetRouter from both sources
# Core module public API - low-level framework components
__all__ = [
    # Core application classes - Foundation classes for the framework
    "Covet",  # Main application class
    "CovetApp",  # Alternative application class
    "CovetApplication",  # Base application interface
    # Configuration system - Application configuration management
    "Config",  # Configuration class
    "Environment",  # Environment enumeration (dev/staging/prod)
    "ConfigManager",  # Multi-configuration management
    # Plugin architecture - Extensibility system
    "PluginManager",  # Plugin lifecycle management
    "PluginRegistry",  # Plugin registration and discovery
    # Core exceptions - Framework error hierarchy
    "CovetError",  # Base framework exception
    "ConfigurationError",  # Configuration-related errors
    # Routing system - URL routing and request dispatching
    "CovetRouter",  # Advanced routing with features
    "AdvancedRouter",  # High-performance router
    "SimpleCovetRouter",  # Lightweight router for simple apps
    "RouteMatch",  # Route matching result
    "RouteGroup",  # Route grouping and organization
    "create_route_group",  # Route group factory function
    # HTTP components - Request/response processing
    "Request",  # HTTP request object
    "Response",  # HTTP response object
    "JSONResponse",  # JSON response with automatic serialization
    "StreamingResponse",  # Streaming response for large data
    "Cookie",  # HTTP cookie handling
    # Response helpers - Convenient response creation
    "json_response",  # JSON response constructor
    "text_response",  # Plain text response constructor
    "html_response",  # HTML response constructor
    "redirect_response",  # HTTP redirect response
    "error_response",  # Error response constructor
    # HTTP Server - Production-grade HTTP server
    "HTTPServer",  # Core HTTP server implementation
    "CovetHTTPServer",  # CovetPy-specific HTTP server
    "ServerConfig",  # Server configuration
    "run_server",  # Server startup function
    # ASGI integration - Modern Python web server interface
    "CovetPyASGI",  # Main ASGI application
    "CovetASGIApp",  # Enhanced ASGI application
    "create_app",  # Application factory
    "create_asgi_app",  # ASGI application factory
    # Middleware system - Request/response processing pipeline
    "Middleware",  # Base middleware interface
    "BaseHTTPMiddleware",  # HTTP middleware base class
    "CORSMiddleware",  # Cross-Origin Resource Sharing
    "RequestLoggingMiddleware",  # Request/response logging
    "ExceptionMiddleware",  # Exception handling and error pages
    "SessionMiddleware",  # Session management
    "RateLimitMiddleware",  # Rate limiting and throttling
    "GZipMiddleware",  # Response compression
]
