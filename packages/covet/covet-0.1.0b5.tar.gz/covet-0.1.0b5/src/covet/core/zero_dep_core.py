"""
CovetPy Zero-Dependency Core

This is the TRUE heart of CovetPy - a web framework written in 100% pure Python
with ZERO dependencies on FastAPI, Flask, Django, or any other web framework.

Optional integrations (like SQLAlchemy) are available but NOT required.
"""

import asyncio
import json
import logging
import re
import sys
import time
import traceback
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    List,
    Optional,
    Pattern,
    Set,
    Tuple,
    Type,
    Union,
)
from urllib.parse import parse_qs, unquote

logger = logging.getLogger(__name__)


# === Core Data Structures ===


@dataclass
class Request:
    """HTTP Request representation - pure Python."""

    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str] = field(default_factory=dict)
    path_params: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    # Additional request properties
    client: Optional[Tuple[str, int]] = None
    cookies: Dict[str, str] = field(default_factory=dict)

    async def json(self) -> Any:
        """Parse request body as JSON."""
        if self.body:
            return json.loads(self.body.decode("utf-8"))
        return None

    async def form(self) -> Dict[str, str]:
        """Parse form data."""
        if self.body and self.headers.get("Content-Type", "").startswith(
            "application/x-www-form-urlencoded"
        ):
            return dict(parse_qs(self.body.decode("utf-8")))
        return {}

    async def text(self) -> str:
        """Get body as text."""
        return self.body.decode("utf-8") if self.body else ""


@dataclass
class Response:
    """HTTP Response representation - pure Python."""

    body: Union[str, bytes, Dict[str, Any], List[Any]]
    status_code: int = 200
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-set content type based on body."""
        if isinstance(self.body, (dict, list)):
            self.headers["Content-Type"] = "application/json"
            self.body = json.dumps(self.body)
        elif isinstance(self.body, str):
            if self.body.strip().startswith("<"):
                self.headers["Content-Type"] = "text/html; charset=utf-8"
            else:
                self.headers["Content-Type"] = "text/plain; charset=utf-8"
        elif isinstance(self.body, bytes):
            self.headers.setdefault("Content-Type", "application/octet-stream")

    def set_cookie(self, name: str, value: str, **options):
        """Set a cookie."""
        self.cookies[name] = {"value": value, **options}


class Route:
    """Route definition with pattern matching."""

    def __init__(
        self,
        path: str,
        handler: Callable,
        methods: List[str],
        name: Optional[str] = None,
    ):
        self.path = path
        self.handler = handler
        self.methods = methods
        self.name = name or handler.__name__

        # Compile path pattern
        self.pattern, self.param_names = self._compile_path(path)

    def _compile_path(self, path: str) -> Tuple[Pattern, List[str]]:
        """Convert /users/{id}/posts/{post_id} to regex."""
        param_names = []
        pattern = path

        # Replace {param} with named regex groups
        for match in re.finditer(r"\{(\w+)\}", path):
            param_name = match.group(1)
            param_names.append(param_name)
            pattern = pattern.replace(match.group(0), f"(?P<{param_name}>[^/]+)")

        # Ensure exact match
        pattern = f"^{pattern}$"
        return re.compile(pattern), param_names

    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Try to match path and extract parameters."""
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None


class Middleware:
    """Base middleware class."""

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request and response."""
        # Before request
        response = await call_next(request)
        # After response
        return response


# === Core Framework ===


class ZeroDependencyApp:
    """
    The TRUE CovetPy - Zero dependency web framework.

    This is pure Python with NO external web framework dependencies.
    Features:
    - Routing with parameter extraction
    - Middleware pipeline
    - Request/Response handling
    - Error handling
    - Optional database integration
    - WebSocket support (when available)
    """

    def __init__(
        self,
        debug: bool = False,
        title: str = "CovetPy Application",
        version: str = "0.1.0",
    ):
        self.debug = debug
        self.title = title
        self.version = version

        # Routing
        self.routes: List[Route] = []
        self.route_map: Dict[str, List[Route]] = defaultdict(list)

        # Middleware
        self.middleware: List[Middleware] = []

        # Lifecycle hooks
        self.startup_handlers: List[Callable] = []
        self.shutdown_handlers: List[Callable] = []
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []

        # Error handlers
        self.error_handlers: Dict[int, Callable] = {}

        # Optional integrations
        self.db = None  # Database adapter
        self.cache = None  # Cache adapter
        self.template_engine = None  # Template engine

        # State
        self.state = {}  # Application state storage

    # === Routing Methods ===

    def route(
        self, path: str, methods: Optional[List[str]] = None, name: Optional[str] = None
    ) -> Callable:
        """Register a route handler."""
        methods = methods or ["GET"]

        def decorator(func: Callable) -> Callable:
            route = Route(path, func, methods, name)
            self.routes.append(route)

            # Add to method-specific map for faster lookup
            for method in methods:
                self.route_map[method].append(route)

            return func

        return decorator

    def get(self, path: str, **kwargs) -> Callable:
        """Register GET route."""
        return self.route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs) -> Callable:
        """Register POST route."""
        return self.route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs) -> Callable:
        """Register PUT route."""
        return self.route(path, methods=["PUT"], **kwargs)

    def delete(self, path: str, **kwargs) -> Callable:
        """Register DELETE route."""
        return self.route(path, methods=["DELETE"], **kwargs)

    def patch(self, path: str, **kwargs) -> Callable:
        """Register PATCH route."""
        return self.route(path, methods=["PATCH"], **kwargs)

    # === Lifecycle Hooks ===

    def on_startup(self, func: Callable) -> Callable:
        """Register startup handler."""
        self.startup_handlers.append(func)
        return func

    def on_shutdown(self, func: Callable) -> Callable:
        """Register shutdown handler."""
        self.shutdown_handlers.append(func)
        return func

    def before_request(self, func: Callable) -> Callable:
        """Register before request handler."""
        self.before_request_handlers.append(func)
        return func

    def after_request(self, func: Callable) -> Callable:
        """Register after request handler."""
        self.after_request_handlers.append(func)
        return func

    # === Error Handling ===

    def error_handler(self, status_code: int) -> Callable:
        """Register error handler for status code."""

        def decorator(func: Callable) -> Callable:
            self.error_handlers[status_code] = func
            return func

        return decorator

    # === Middleware ===

    def add_middleware(self, middleware: Union[Middleware, Callable]):
        """Add middleware to the pipeline."""
        if not isinstance(middleware, Middleware):
            # Wrap function-based middleware
            class FunctionMiddleware(Middleware):
                async def __call__(self, request, call_next):
                    return await middleware(request, call_next)

            middleware = FunctionMiddleware()

        self.middleware.append(middleware)

    # === Request Handling ===

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming HTTP request."""
        try:
            # Build middleware chain
            async def app_handler(req: Request) -> Response:
                return await self._route_request(req)

            handler = app_handler

            # Wrap with middleware (in reverse order)
            for mw in reversed(self.middleware):
                prev_handler = handler

                async def wrapped(req, h=prev_handler, m=mw):
                    return await m(req, h)

                handler = wrapped

            # Execute the chain
            response = await handler(request)

            return response

        except Exception as e:
            return await self._handle_error(e, request)

    async def _route_request(self, request: Request) -> Response:
        """Route request to handler."""
        # Before request hooks
        for hook in self.before_request_handlers:
            result = await hook(request)
            if result is not None:
                return self._make_response(result)

        # Find matching route
        routes_to_check = self.route_map.get(request.method, [])

        for route in routes_to_check:
            params = route.match(request.path)
            if params is not None:
                # Found match
                request.path_params = params

                # Call handler
                result = await route.handler(request)

                # Make response
                response = self._make_response(result)

                # After request hooks
                for hook in self.after_request_handlers:
                    response = await hook(request, response)

                return response

        # No route found
        return await self._handle_http_error(404, request)

    def _make_response(self, result: Any) -> Response:
        """Convert handler result to Response object."""
        if isinstance(result, Response):
            return result
        elif isinstance(result, dict) or isinstance(result, list):
            return Response(body=result)
        elif isinstance(result, str):
            return Response(body=result)
        elif isinstance(result, bytes):
            return Response(body=result)
        elif isinstance(result, tuple):
            if len(result) == 2:
                body, status = result
                return Response(body=body, status_code=status)
            elif len(result) == 3:
                body, status, headers = result
                return Response(body=body, status_code=status, headers=headers)
        else:
            # Convert to string
            return Response(body=str(result))

    async def _handle_error(self, error: Exception, request: Request) -> Response:
        """Handle exceptions."""
        logger.exception("Error handling request")

        if self.debug:
            return Response(
                body={
                    "error": str(error),
                    "type": type(error).__name__,
                    "traceback": traceback.format_exc(),
                },
                status_code=500,
            )
        else:
            return Response(body={"error": "Internal Server Error"}, status_code=500)

    async def _handle_http_error(self, status_code: int, request: Request) -> Response:
        """Handle HTTP errors."""
        if status_code in self.error_handlers:
            result = await self.error_handlers[status_code](request)
            return self._make_response(result)
        else:
            return Response(body={"error": f"HTTP {status_code}"}, status_code=status_code)

    # === Lifecycle Management ===

    async def startup(self):
        """Run startup handlers."""
        for handler in self.startup_handlers:
            await handler()

        # Connect database if configured
        if self.db and hasattr(self.db, "connect"):
            await self.db.connect()

    async def shutdown(self):
        """Run shutdown handlers."""
        # Disconnect database
        if self.db and hasattr(self.db, "disconnect"):
            await self.db.disconnect()

        for handler in self.shutdown_handlers:
            await handler()

    # === Optional Integrations ===

    def set_database(self, db: Any):
        """Set database adapter (e.g., SQLAlchemy)."""
        self.db = db

    def set_cache(self, cache: Any):
        """Set cache adapter (e.g., Redis)."""
        self.cache = cache

    def set_template_engine(self, engine: Any):
        """Set template engine (e.g., Jinja2)."""
        self.template_engine = engine

    # === ASGI Interface ===

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        """ASGI application interface."""
        if scope["type"] == "http":
            await self._handle_http(scope, receive, send)
        elif scope["type"] == "websocket":
            await self._handle_websocket(scope, receive, send)
        elif scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send)

    async def _handle_http(self, scope: dict, receive: Callable, send: Callable):
        """Handle HTTP requests in ASGI."""
        # Parse request
        request = await self._parse_asgi_request(scope, receive)

        # Handle request
        response = await self.handle_request(request)

        # Send response
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": [[k.encode(), v.encode()] for k, v in response.headers.items()],
            }
        )

        body = response.body
        if isinstance(body, str):
            body = body.encode("utf-8")

        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )

    async def _parse_asgi_request(self, scope: dict, receive: Callable) -> Request:
        """Parse ASGI scope into Request object."""
        # Parse headers
        headers = {}
        for name, value in scope.get("headers", []):
            headers[name.decode()] = value.decode()

        # Parse query string
        query_string = scope.get("query_string", b"").decode()
        query_params = dict(parse_qs(query_string))

        # Read body
        body = b""
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body += message.get("body", b"")
                if not message.get("more_body", False):
                    break

        return Request(
            method=scope["method"],
            path=scope["path"],
            headers=headers,
            query_params=query_params,
            body=body,
            client=scope.get("client"),
        )

    async def _handle_lifespan(self, scope: dict, receive: Callable, send: Callable):
        """Handle ASGI lifespan events."""
        while True:
            message = await receive()

            if message["type"] == "lifespan.startup":
                try:
                    await self.startup()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as e:
                    await send({"type": "lifespan.startup.failed", "message": str(e)})

            elif message["type"] == "lifespan.shutdown":
                try:
                    await self.shutdown()
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as e:
                    await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                break

    async def _handle_websocket(self, scope: dict, receive: Callable, send: Callable):
        """Handle WebSocket connections (placeholder)."""
        # WebSocket support would go here


# === Factory Functions ===


def create_app(**kwargs) -> ZeroDependencyApp:
    """Create a zero-dependency CovetPy application."""
    return ZeroDependencyApp(**kwargs)


# === Convenience Aliases ===

CovetPy = ZeroDependencyApp  # Main application class
App = ZeroDependencyApp  # Short alias


# === Export ===

__all__ = [
    "Request",
    "Response",
    "Route",
    "Middleware",
    "ZeroDependencyApp",
    "CovetPy",
    "App",
    "create_app",
]
