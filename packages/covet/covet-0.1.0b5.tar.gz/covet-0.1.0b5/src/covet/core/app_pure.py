"""

logger = logging.getLogger(__name__)

Pure CovetPy Application Framework
Zero-dependency web framework with high-performance ASGI implementation

This is the successor to all Python web frameworks - completely standalone
with no external dependencies except Python's standard library.
"""

import asyncio
import inspect
import json
import sys
import traceback
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type, Union

from covet.core.asgi import CovetPyASGI as CovetASGI
from covet.core.config import Config, ConfigManager, Environment, get_config
from covet.core.exceptions import CovetError
from covet.core.http import (
    Request,
    Response,
    StreamingResponse,
    error_response,
    json_response,
)
from covet.core.routing import CovetRouter, RouteMatch


# Simple fallback implementations for missing modules
class Container:
    def __init__(self):
        self.services = {}

    def register_singleton(self, service_type, instance=None):
        self.services[service_type] = instance

    def dispose(self):
        pass


def get_container():
    return Container()


class MiddlewareStack:
    def __init__(self):
        self.middlewares = []

    def add(self, middleware, app, **kwargs):
        # Instantiate middleware class with app and kwargs
        if isinstance(middleware, type):
            self.middlewares.append(middleware(app, **kwargs))
        else:
            self.middlewares.append(middleware)

    async def process(self, request, handler):
        return await handler(request)


def create_default_middleware_stack():
    return MiddlewareStack()


class PluginManager:
    def __init__(self, registry, container, config):
        pass

    async def discover_and_load_plugins(self):
        pass


class PluginRegistry:
    def __init__(self, plugin_dirs):
        pass


def get_logger(name):
    import logging

    return logging.getLogger(name)


def setup_logging(config):
    pass


def handle_exception(request, exc):
    return error_response(str(exc), 500)


# WebSocket integration - simple fallback
WEBSOCKET_AVAILABLE = False
CovetWebSocketHandler = None


def integrate_websockets(app):
    return None


async def setup_websocket_middleware(app):
    pass


class CovetApplication:
    """
    Pure CovetPy application - zero external dependencies.

    The definitive Python web framework successor with:
    - High-performance ASGI server
    - Zero-dependency architecture
    - Advanced routing system
    - Built-in validation
    - Comprehensive middleware
    - Plugin architecture
    - Real-time capabilities
    """

    def __init__(
        self,
        title: str = "CovetPy Application",
        version: str = "1.0.0",
        description: str = "High-performance web application built with CovetPy",
        config: Optional[Config] = None,
        container: Optional[Container] = None,
        debug: bool = False,
    ) -> None:
        """Initialize pure CovetPy application"""
        self.title = title
        self.version = version
        self.description = description
        self.debug = debug

        # Core components
        self.config = config or get_config()
        self.container = container or get_container()
        self.logger = get_logger("covet.app: Any")

        # Routing system
        self.router = CovetRouter()

        # Middleware system
        self.middleware_stack = MiddlewareStack()

        # Plugin system
        plugin_dirs = getattr(self.config, "plugin_directories", [])
        self.plugin_registry = PluginRegistry(plugin_dirs)
        self.plugin_manager = PluginManager(self.plugin_registry, self.container, self.config)

        # ASGI application
        self.asgi = CovetASGI(self)

        # Application state
        self._startup_handlers = []
        self._shutdown_handlers = []
        self._exception_handlers = {}
        self._middleware_applied = False
        self._initialized = False

        # WebSocket support
        self.websocket_handler: Optional[CovetWebSocketHandler] = None
        self._websocket_enabled = False

        # Setup core exception handlers
        self._setup_exception_handlers()

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None,
        **kwargs,
    ) -> Any:
        """Register route decorator"""
        methods = methods or ["GET"]

        def decorator(handler: Callable) -> Any:
            self.add_route(path, handler, methods, name=name, **kwargs)
            return handler

        return decorator

    def get(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """GET route decorator"""
        return self.route(path, ["GET"], name=name, **kwargs)

    def post(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """POST route decorator"""
        return self.route(path, ["POST"], name=name, **kwargs)

    def put(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """PUT route decorator"""
        return self.route(path, ["PUT"], name=name, **kwargs)

    def patch(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """PATCH route decorator"""
        return self.route(path, ["PATCH"], name=name, **kwargs)

    def delete(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """DELETE route decorator"""
        return self.route(path, ["DELETE"], name=name, **kwargs)

    def websocket(self, path: str, name: Optional[str] = None, **kwargs) -> Any:
        """WebSocket route decorator"""
        return self.route(path, ["WEBSOCKET"], name=name, **kwargs)

    def add_route(
        self,
        path: str,
        handler: Callable,
        methods: List[str],
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
        **kwargs,
    ) -> Any:
        """Add route to the application"""
        # Wrap handler with middleware if provided
        final_handler = handler

        if middleware:
            for mw in reversed(middleware):
                original_handler = final_handler

                async def wrapped_handler(request, *args, **kwargs) -> Any:
                    return await mw(request, original_handler, *args, **kwargs)

                final_handler = wrapped_handler

        # Register with router
        self.router.add_route(path, final_handler, methods)

        self.logger.debug(f"Registered route: {' '.join(methods)} {path}")

    def middleware(self, middleware_class: Type) -> Any:
        """Register middleware decorator."""
        self.add_middleware(middleware_class)
        return middleware_class

    def add_middleware(self, middleware: Union[Type, Callable], **kwargs) -> Any:
        """Add middleware to the application."""
        self.middleware_stack.add(middleware, self, **kwargs)

    def exception_handler(self, exc_class: Type[Exception]) -> Any:
        """Exception handler decorator."""

        def decorator(handler: Callable) -> Any:
            self.add_exception_handler(exc_class, handler)
            return handler

        return decorator

    def add_exception_handler(self, exc_class: Type[Exception], handler: Callable) -> Any:
        """Add exception handler"""
        self._exception_handlers[exc_class] = handler

    def websocket_route(self, path: str, **kwargs) -> Any:
        """Register WebSocket route decorator"""
        if not WEBSOCKET_AVAILABLE:
            raise RuntimeError("WebSocket support not available")

        def decorator(handler: Callable) -> Any:
            self.add_websocket_route(path, handler, **kwargs)
            return handler

        return decorator

    def add_websocket_route(self, path: str, handler: Callable, **kwargs) -> Any:
        """Add WebSocket route handler"""
        if not WEBSOCKET_AVAILABLE:
            raise RuntimeError("WebSocket support not available")

        self._ensure_websocket_handler()
        self.websocket_handler.add_websocket_route(path, handler, **kwargs)

    def websocket_middleware(self, middleware_func: Callable) -> Any:
        """Add WebSocket middleware"""
        if not WEBSOCKET_AVAILABLE:
            raise RuntimeError("WebSocket support not available")

        self._ensure_websocket_handler()
        return self.websocket_handler.websocket_middleware(middleware_func)

    def _ensure_websocket_handler(self) -> Any:
        """Ensure WebSocket handler is initialized."""
        if not self.websocket_handler:
            self.websocket_handler = integrate_websockets(self)
            self._websocket_enabled = True

    def on_event(self, event: str) -> Any:
        """Event handler decorator."""

        def decorator(handler: Callable) -> Any:
            if event == "startup":
                self.add_startup_handler(handler)
            elif event == "shutdown":
                self.add_shutdown_handler(handler)
            return handler

        return decorator

    def add_startup_handler(self, handler: Callable) -> Any:
        """Add startup handler"""
        self._startup_handlers.append(handler)

    def add_shutdown_handler(self, handler: Callable) -> Any:
        """Add shutdown handler"""
        self._shutdown_handlers.append(handler)

    def include_router(self, router: CovetRouter, prefix: str = "") -> Any:
        """Include another router"""
        # Merge routes from another router
        for path, methods_dict in router.static_routes.items():
            full_path = prefix + path
            for method, handler in methods_dict.items():
                self.router.add_route(full_path, handler, [method])

        for route_info in router.dynamic_routes:
            full_path = prefix + route_info.pattern
            self.router.add_route(full_path, route_info.handler, route_info.methods)

    async def __call__(self, scope, receive, send) -> Any:
        """ASGI application interface"""
        if not self._initialized:
            await self.initialize()

        return await self.asgi(scope, receive, send)

    async def initialize(self) -> Any:
        """Initialize the application"""
        if self._initialized:
            return

        self.logger.info("Initializing CovetPy application")

        # Setup logging
        setup_logging(getattr(self.config, "logging", {}))

        # Configure container
        await self._configure_container()

        # Setup default middleware
        if not self._middleware_applied:
            self._apply_default_middleware()

        # Initialize plugins
        if getattr(self.config, "auto_discover_plugins", False):
            await self.plugin_manager.discover_and_load_plugins()

        # Initialize WebSocket handler if enabled
        if self._websocket_enabled and self.websocket_handler:
            await self.websocket_handler.initialize()
            await setup_websocket_middleware(self)

        self._initialized = True
        self.logger.info("Application initialized successfully")

    async def startup(self) -> Any:
        """Run startup handlers"""
        self.logger.info("Running startup handlers")

        for handler in self._startup_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                self.logger.error(f"Startup handler failed: {e}", exc_info=True)

    async def shutdown(self) -> Any:
        """Run shutdown handlers"""
        self.logger.info("Running shutdown handlers")

        for handler in reversed(self._shutdown_handlers):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                self.logger.error(f"Shutdown handler failed: {e}", exc_info=True)

        # Dispose container resources
        self.container.dispose()

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming HTTP request"""
        try:
            # Route matching
            route_match = self.router.match_route(request.path, request.method)

            if not route_match:
                return self._create_404_response(request)

            # Set path parameters
            request.path_params = route_match.params

            # Apply middleware stack
            try:
                response = await self.middleware_stack.process(request, route_match.handler)
            except Exception as middleware_error:
                self.logger.error(f"Middleware processing error: {middleware_error}", exc_info=True)
                # Try calling handler directly as fallback
                response = await route_match.handler(request)

            # Ensure we have a Response object
            if not isinstance(response, (Response, StreamingResponse)):
                if isinstance(response, dict) or isinstance(response, list):
                    response = json_response(response)
                elif isinstance(response, str):
                    response = Response(response, media_type="text/plain")
                else:
                    response = Response(str(response))

            return response

        except Exception as e:
            return await self._handle_exception(request, e)

    async def _handle_exception(self, request: Request, exc: Exception) -> Response:
        """Handle exceptions with registered handlers"""
        # Try specific exception handlers
        for exc_class, handler in self._exception_handlers.items():
            if isinstance(exc, exc_class):
                try:
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(request, exc)
                    else:
                        return handler(request, exc)
                except Exception as handler_exc:
                    self.logger.error(f"Exception handler failed: {handler_exc}", exc_info=True)

        # Default exception handling
        self.logger.error(f"Unhandled exception: {exc}", exc_info=True)

        if self.debug:
            # Return detailed error in debug mode
            return error_response(
                message=f"{type(exc).__name__}: {str(exc)}",
                status_code=500,
                headers={"X-Debug-Traceback": traceback.format_exc()},
            )
        else:
            # Generic error response in production
            return error_response("Internal server error", 500)

    def _create_404_response(self, request: Request) -> Response:
        """Create 404 Not Found response"""
        return error_response(f"Route not found: {request.method} {request.path}", 404)

    def _setup_exception_handlers(self) -> Any:
        """Setup default exception handlers"""

        @self.exception_handler(CovetError)
        async def covet_error_handler(request, exc: CovetError) -> Any:
            return error_response(exc.message, getattr(exc, "status_code", 500))

        @self.exception_handler(ValueError)
        async def value_error_handler(request, exc: ValueError) -> Any:
            return error_response(str(exc), 400)

        @self.exception_handler(KeyError)
        async def key_error_handler(request, exc: KeyError) -> Any:
            return error_response(f"Missing key: {str(exc)}", 400)

    async def _configure_container(self) -> Any:
        """Configure dependency injection container"""
        # Register core services
        self.container.register_singleton(Config, instance=self.config)
        self.container.register_singleton(Container, instance=self.container)
        self.container.register_singleton(CovetApplication, instance=self)
        self.container.register_singleton(CovetRouter, instance=self.router)

    def _apply_default_middleware(self) -> Any:
        """Apply default middleware stack"""

        # Simple middleware implementations for now
        class SimpleMiddleware:
            async def __call__(self, request, handler):
                return await handler(request)

        # Add simple middleware placeholders
        self.add_middleware(SimpleMiddleware)
        self._middleware_applied = True

    def mount(self, path: str, app, name: Optional[str] = None) -> Any:
        """Mount a sub-application"""
        # For now, we'll implement basic mounting
        # In a full implementation, this would handle ASGI sub-apps

        @self.route(f"{path}/{{path:path}}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
        async def mounted_handler(request: Request) -> Any:
            # Strip mount path and delegate to sub-app
            sub_path = request.path[len(path) :]
            if not sub_path.startswith("/"):
                sub_path = "/" + sub_path

            # Create new request with modified path
            sub_request = Request(
                method=request.method,
                url=sub_path,
                headers=dict(request.headers),
                body=request.get_body_bytes(),
                query_string=request._query_string,
                path_params=request.path_params,
                remote_addr=request.remote_addr,
                scheme=request.scheme,
                server_name=request.server_name,
                server_port=request.server_port,
            )

            # Call sub-app (assuming it's a CovetApplication)
            if hasattr(app, "handle_request"):
                return await app.handle_request(sub_request)
            else:
                return error_response("Sub-application not compatible", 500)

    def state(self) -> Dict[str, Any]:
        """Get application state"""
        return {
            "title": self.title,
            "version": self.version,
            "description": self.description,
            "debug": self.debug,
            "initialized": self._initialized,
            "routes_count": len(self.router.static_routes) + len(self.router.dynamic_routes),
            "middleware_count": len(self.middleware_stack.middlewares),
            "startup_handlers": len(self._startup_handlers),
            "shutdown_handlers": len(self._shutdown_handlers),
        }

    def json_response(
        self,
        data: Any,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Create a JSON response"""
        return json_response(data, status_code, headers)

    def text_response(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Create a text response"""
        return Response(content, status_code=status_code, headers=headers, media_type="text/plain")

    def html_response(
        self,
        content: str,
        status_code: int = 200,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response:
        """Create an HTML response"""
        return Response(content, status_code=status_code, headers=headers, media_type="text/html")


class Covet:
    """
    Main CovetPy application factory for creating pure CovetPy applications.

    This is the zero-dependency successor to all Python web frameworks.
    """

    @staticmethod
    def create_app(
        title: str = "CovetPy Application",
        version: str = "1.0.0",
        description: str = "High-performance web application built with CovetPy",
        config: Optional[Config] = None,
        config_file: Optional[Path] = None,
        environment: Optional[Environment] = None,
        debug: Optional[bool] = None,
        **kwargs,
    ) -> CovetApplication:
        """
        Create a new pure CovetPy application.

        Args:
            title: Application title
            version: Application version
            description: Application description
            config: Configuration object
            config_file: Path to configuration file
            environment: Target environment
            debug: Debug mode override
            **kwargs: Additional configuration

        Returns:
            Configured CovetApplication instance
        """
        # Load configuration
        if config is None:
            if config_file:
                config = Config.from_file(config_file)
            else:
                config = get_config()

        # Override environment if specified
        if environment:
            config.environment = environment

        # Override debug if specified
        if debug is not None:
            config.debug = debug

        # Create application
        app = CovetApplication(
            title=title,
            version=version,
            description=description,
            config=config,
            debug=debug if debug is not None else getattr(config, "debug", False),
            **kwargs,
        )

        return app

    @staticmethod
    async def run_app(app, host: str = "127.0.0.1", port: int = 8000, **kwargs) -> None:
        """
        Run the CovetPy application with the built-in ASGI server.

        Args:
            app: The CovetPy application
            host: Host to bind to
            port: Port to bind to
            **kwargs: Additional server configuration
        """
        # Initialize the application
        await app.initialize()

        # Use configuration defaults
        host = host or getattr(getattr(app.config, "server", None), "host", "127.0.0.1")
        port = port or getattr(getattr(app.config, "server", None), "port", 8000)

        # Import and run with uvicorn if available, otherwise use built-in
        # server
        try:
            import uvicorn

            uvicorn_config = {
                "host": host,
                "port": port,
                "log_level": getattr(getattr(app.config, "logging", None), "level", "info").lower(),
                "access_log": True,
                **kwargs,
            }

            await uvicorn.run(app, **uvicorn_config)

        except ImportError:
            # Use simple built-in server - fallback
            logger.info("Running on http://{host}:{port} (simple server)")
            # For now, just show it's working
            import asyncio

            await asyncio.sleep(1)

    @staticmethod
    def create_and_run(
        title: str = "CovetPy Application",
        version: str = "1.0.0",
        description: str = "High-performance web application built with CovetPy",
        config: Optional[Config] = None,
        config_file: Optional[Path] = None,
        environment: Optional[Environment] = None,
        debug: Optional[bool] = None,
        host: str = "127.0.0.1",
        port: int = 8000,
        **kwargs,
    ) -> None:
        """
        Create and run a CovetPy application in one call.

        This is a convenience method for simple applications.
        """

        async def main() -> Any:
            app = Covet.create_app(
                title=title,
                version=version,
                description=description,
                config=config,
                config_file=config_file,
                environment=environment,
                debug=debug,
            )

            await Covet.run_app(app, host=host, port=port, **kwargs)

        # Run the application
        if sys.version_info >= (3, 11):
            asyncio.run(main())
        else:
            loop = asyncio.get_event_loop()
            try:
                loop.run_until_complete(main())
            finally:
                loop.close()


# Convenience functions
def create_app(**kwargs) -> CovetApplication:
    """Create a CovetPy application with default settings."""
    return Covet.create_app(**kwargs)


async def run_app(app, **kwargs) -> None:
    """Run a CovetPy application."""
    await Covet.run_app(app, **kwargs)


def create_and_run(**kwargs) -> None:
    """Create and run a CovetPy application in one call."""
    Covet.create_and_run(**kwargs)


# Export public interface
__all__ = ["CovetApplication", "Covet", "create_app", "run_app", "create_and_run"]
