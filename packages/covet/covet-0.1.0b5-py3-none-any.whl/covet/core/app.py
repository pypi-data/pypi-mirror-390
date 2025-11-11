"""
CovetPy - Simple, Flask-like Web Framework
A clean, working implementation focused on developer experience
"""

import asyncio
import inspect
import json
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from covet.core.http import Request, Response, json_response
from covet.core.routing import CovetRouter

logger = logging.getLogger(__name__)


class Covet:
    """
    Simple, Flask-like web framework with ASGI support.

    Example:
        from covet import Covet

        app = Covet()

        @app.route('/')
        async def index(request):
            return {'message': 'Hello World'}

        @app.route('/users/{user_id}')
        async def get_user(request, user_id):
            return {'user_id': user_id}

        if __name__ == '__main__':
            app.run()
    """

    def __init__(self, debug: bool = False):
        """
        Initialize Covet application.

        Args:
            debug: Enable debug mode (detailed error messages)
        """
        self.debug = debug
        self.router = CovetRouter()
        self._startup_handlers = []
        self._shutdown_handlers = []
        self._middleware = []

    def route(
        self,
        path: str,
        methods: Optional[List[str]] = None,
        name: Optional[str] = None
    ) -> Callable:
        """
        Register a route handler.

        Args:
            path: URL path (e.g., '/users/{id}')
            methods: HTTP methods (default: ['GET'])
            name: Optional route name

        Returns:
            Decorator function

        Example:
            @app.route('/hello')
            async def hello(request):
                return {'message': 'Hello!'}

            @app.route('/users/{user_id}', methods=['GET', 'POST'])
            async def user(request, user_id):
                return {'user_id': user_id}
        """
        if methods is None:
            methods = ['GET']

        def decorator(handler: Callable) -> Callable:
            # Register the route
            self.router.add_route(path, handler, methods)
            logger.debug(f"Registered route: {methods} {path} -> {handler.__name__}")
            return handler

        return decorator

    def get(self, path: str, **kwargs) -> Callable:
        """Shortcut for GET routes."""
        return self.route(path, methods=['GET'], **kwargs)

    def post(self, path: str, **kwargs) -> Callable:
        """Shortcut for POST routes."""
        return self.route(path, methods=['POST'], **kwargs)

    def put(self, path: str, **kwargs) -> Callable:
        """Shortcut for PUT routes."""
        return self.route(path, methods=['PUT'], **kwargs)

    def delete(self, path: str, **kwargs) -> Callable:
        """Shortcut for DELETE routes."""
        return self.route(path, methods=['DELETE'], **kwargs)

    def patch(self, path: str, **kwargs) -> Callable:
        """Shortcut for PATCH routes."""
        return self.route(path, methods=['PATCH'], **kwargs)

    def on_event(self, event_type: str) -> Callable:
        """
        Register startup/shutdown handler.

        Args:
            event_type: 'startup' or 'shutdown'

        Example:
            @app.on_event('startup')
            async def startup():
                print('App starting...')
        """
        def decorator(handler: Callable) -> Callable:
            if event_type == 'startup':
                self._startup_handlers.append(handler)
            elif event_type == 'shutdown':
                self._shutdown_handlers.append(handler)
            return handler
        return decorator

    def add_middleware(self, middleware: Union[type, Callable], **kwargs) -> None:
        """
        Add middleware to the application.

        Args:
            middleware: Middleware class or callable
            **kwargs: Additional parameters to pass to middleware

        Example:
            from covet.middleware.cors import CORSMiddleware

            app.add_middleware(
                CORSMiddleware,
                allow_origins=['*'],
                allow_credentials=False
            )
        """
        # Instantiate middleware class
        if isinstance(middleware, type):
            middleware_instance = middleware(self, **kwargs)
        else:
            middleware_instance = middleware

        self._middleware.append(middleware_instance)

    def on_startup(self, func: Callable) -> Callable:
        """
        Register a startup handler.

        Args:
            func: Function to call on startup

        Returns:
            The registered function

        Example:
            @app.on_startup
            async def startup():
                await init_database()
        """
        self._startup_handlers.append(func)
        return func

    def on_shutdown(self, func: Callable) -> Callable:
        """
        Register a shutdown handler.

        Args:
            func: Function to call on shutdown

        Returns:
            The registered function

        Example:
            @app.on_shutdown
            async def shutdown():
                await close_database()
        """
        self._shutdown_handlers.append(func)
        return func

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        """
        ASGI 3.0 application interface.

        This allows the app to be run with any ASGI server:
            uvicorn app:app --reload
        """
        # Direct dispatch based on scope type
        if scope['type'] == 'lifespan':
            await self._handle_lifespan(scope, receive, send)
        elif scope['type'] == 'http':
            # Apply middleware if configured
            if self._middleware:
                await self._call_with_middleware(scope, receive, send)
            else:
                await self._handle_http(scope, receive, send)
        elif scope['type'] == 'websocket':
            await self._handle_websocket(scope, receive, send)

    async def _call_with_middleware(self, scope: dict, receive: Callable, send: Callable):
        """Call HTTP handler through middleware chain."""
        # The middleware instances already have self.app set during add_middleware
        # We just need to call the outermost middleware, which will chain to the rest
        # The CORS middleware will call self.app (which is the Covet instance)
        # But we need to bypass middleware on that recursive call

        # Temporarily disable middleware to avoid infinite loop
        middleware_stack = self._middleware
        self._middleware = []

        try:
            # Call the first middleware in the chain
            await middleware_stack[0](scope, receive, send)
        finally:
            # Restore middleware
            self._middleware = middleware_stack

    async def _handle_lifespan(self, scope: dict, receive: Callable, send: Callable):
        """Handle ASGI lifespan events."""
        while True:
            message = await receive()

            if message['type'] == 'lifespan.startup':
                try:
                    # Run startup handlers
                    for handler in self._startup_handlers:
                        if asyncio.iscoroutinefunction(handler):
                            await handler()
                        else:
                            handler()
                    await send({'type': 'lifespan.startup.complete'})
                except Exception as exc:
                    logger.error(f"Startup failed: {exc}", exc_info=True)
                    await send({'type': 'lifespan.startup.failed', 'message': str(exc)})

            elif message['type'] == 'lifespan.shutdown':
                try:
                    # Run shutdown handlers
                    for handler in self._shutdown_handlers:
                        if asyncio.iscoroutinefunction(handler):
                            await handler()
                        else:
                            handler()
                    await send({'type': 'lifespan.shutdown.complete'})
                except Exception as exc:
                    logger.error(f"Shutdown failed: {exc}", exc_info=True)
                    await send({'type': 'lifespan.shutdown.failed', 'message': str(exc)})
                return

    async def _handle_http(self, scope: dict, receive: Callable, send: Callable):
        """Handle HTTP request."""
        # Create Request object
        request = Request(
            method=scope['method'],
            url=scope['path'],
            scheme=scope.get('scheme', 'http'),
            headers=dict((name.decode(), value.decode()) for name, value in scope.get('headers', [])),
            query_string=scope.get('query_string', b'').decode(),
            scope=scope,
            receive=receive
        )

        # Note: request.path is a property that parses from request.url automatically
        # Note: request.cookies() method already parses from headers

        # Create the core handler
        async def core_handler(req):
            # Match route
            route_match = self.router.match_route(req.path, req.method)

            if not route_match:
                # 404 Not Found
                return json_response(
                    {'error': 'Not Found', 'path': req.path},
                    status_code=404
                )
            else:
                # Set path parameters
                req.path_params = route_match.params

                # Call handler with path parameters
                handler = route_match.handler

                # Check handler signature
                sig = inspect.signature(handler)
                params = list(sig.parameters.values())

                # Build arguments: request + path parameters
                args = [req]
                for param in params[1:]:  # Skip first param (request)
                    if param.name in route_match.params:
                        args.append(route_match.params[param.name])

                # Call handler
                if asyncio.iscoroutinefunction(handler):
                    result = await handler(*args)
                else:
                    result = handler(*args)

                # Convert result to Response
                return self._make_response(result)

        try:
            # Call handler directly (middleware is handled at ASGI level)
            response = await core_handler(request)

        except Exception as exc:
            logger.error(f"Error handling request: {exc}", exc_info=True)
            response = self._error_response(exc)

        # Handle cookies set by middleware
        if hasattr(request, 'set_cookies'):
            for cookie_data in request.set_cookies:
                response.headers['Set-Cookie'] = cookie_data

        # Send response
        await self._send_response(response, send)

    async def _handle_websocket(self, scope: dict, receive: Callable, send: Callable):
        """Handle WebSocket connection."""
        # Basic WebSocket support - close connection for now
        await send({'type': 'websocket.close', 'code': 1000})

    def _make_response(self, result: Any) -> Response:
        """Convert handler result to Response object."""
        if isinstance(result, Response):
            return result
        elif isinstance(result, dict) or isinstance(result, list):
            return json_response(result)
        elif isinstance(result, str):
            return Response(result, media_type='text/plain')
        elif isinstance(result, bytes):
            return Response(result, media_type='application/octet-stream')
        elif result is None:
            return Response('', status_code=204)
        else:
            return Response(str(result), media_type='text/plain')

    def _error_response(self, exc: Exception) -> Response:
        """Create error response."""
        if self.debug:
            import traceback
            return json_response({
                'error': str(exc),
                'type': type(exc).__name__,
                'traceback': traceback.format_exc()
            }, status_code=500)
        else:
            return json_response({
                'error': 'Internal Server Error'
            }, status_code=500)

    async def _send_response(self, response: Response, send: Callable):
        """Send Response object via ASGI."""
        # Prepare headers
        headers = []
        for key, value in response.headers.items():
            headers.append([key.encode(), value.encode()])

        # Add Content-Length if not present
        content_bytes = response.get_content_bytes()
        has_content_length = any(name.lower() == b'content-length' for name, _ in headers)
        if not has_content_length:
            headers.append([b'content-length', str(len(content_bytes)).encode()])

        # Send response start
        await send({
            'type': 'http.response.start',
            'status': response.status_code,
            'headers': headers,
        })

        # Send response body
        await send({
            'type': 'http.response.body',
            'body': content_bytes,
        })

    def run(self, host: str = '127.0.0.1', port: int = 8000, **kwargs):
        """
        Run the application with uvicorn.

        Args:
            host: Host to bind to (default: 127.0.0.1)
            port: Port to bind to (default: 8000)
            **kwargs: Additional uvicorn configuration

        Example:
            app.run(debug=True)
            app.run(host='0.0.0.0', port=5000)
        """
        try:
            import uvicorn
        except ImportError:
            logger.error(
                "\nuvicorn is not installed!\n"
                "Install it with: pip install uvicorn[standard]\n"
                "\nOr run manually with any ASGI server:\n"
                f"  uvicorn {self.__module__}:app --host {host} --port {port}"
            )
            return

        # Merge kwargs with defaults
        config = {
            'host': host,
            'port': port,
            'log_level': 'debug' if self.debug else 'info',
            **kwargs
        }

        logger.info(f"Starting CovetPy app on http://{host}:{port}")
        uvicorn.run(self, **config)

    @property
    def routes(self):
        """Get all registered routes (for testing/debugging)."""
        routes = []
        # Add static routes
        for path, methods_dict in self.router.static_routes.items():
            for method, handler in methods_dict.items():
                routes.append((path, handler, method))
        # Add dynamic routes
        for route_info in self.router.dynamic_routes:
            for method in route_info.methods:
                routes.append((route_info.pattern, route_info.handler, method))
        return routes

    def include_router(self, router: 'CovetRouter', prefix: str = ''):
        """
        Include routes from another router.

        Args:
            router: Router instance to include
            prefix: URL prefix for all routes
        """
        # Merge routes
        for path, methods_dict in router.static_routes.items():
            full_path = prefix + path
            for method, handler in methods_dict.items():
                self.router.add_route(full_path, handler, [method])

        for route_info in router.dynamic_routes:
            full_path = prefix + route_info.pattern
            self.router.add_route(full_path, route_info.handler, route_info.methods)


# Aliases for backwards compatibility
CovetApp = Covet
Application = Covet
CovetApplication = Covet


def create_app(**kwargs) -> Covet:
    """Create a Covet application."""
    return Covet(**kwargs)


__all__ = ['Covet', 'CovetApp', 'Application', 'CovetApplication', 'create_app']
