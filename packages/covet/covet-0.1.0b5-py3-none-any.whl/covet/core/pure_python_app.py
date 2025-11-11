"""
Pure Python CovetPy Core - Zero Dependencies

This is the TRUE core of CovetPy without ANY web framework dependencies.
No FastAPI, No Flask, just pure Python with optional SQLAlchemy.
"""

import asyncio
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Pattern, Tuple, Union


@dataclass
class Request:
    """Pure Python HTTP request representation."""

    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    path_params: Dict[str, str]
    body: bytes

    async def json(self) -> Any:
        """Parse request body as JSON."""
        if self.body:
            return json.loads(self.body.decode("utf-8"))
        return None

    async def text(self) -> str:
        """Get request body as text."""
        return self.body.decode("utf-8") if self.body else ""


@dataclass
class Response:
    """Pure Python HTTP response representation."""

    body: Union[str, bytes, Dict[str, Any]]
    status_code: int = 200
    headers: Dict[str, str] = None
    content_type: str = "application/json"

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

        # Auto-set content type
        if isinstance(self.body, dict):
            self.content_type = "application/json"
            self.body = json.dumps(self.body)
        elif isinstance(self.body, str) and self.body.strip().startswith("<"):
            self.content_type = "text/html"

        self.headers["Content-Type"] = self.content_type


class Route:
    """Pure Python route representation."""

    def __init__(self, path: str, handler: Callable, methods: List[str]):
        self.path = path
        self.handler = handler
        self.methods = methods
        self.pattern, self.param_names = self._compile_path(path)

    def _compile_path(self, path: str) -> Tuple[Pattern, List[str]]:
        """Convert path with {param} to regex pattern."""
        param_names = []
        pattern = path

        # Find all {param} placeholders
        for match in re.finditer(r"\{(\w+)\}", path):
            param_name = match.group(1)
            param_names.append(param_name)
            # Replace {param} with named group
            pattern = pattern.replace(match.group(0), f"(?P<{param_name}>[^/]+)")

        # Exact match
        pattern = f"^{pattern}$"
        return re.compile(pattern), param_names

    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Check if path matches this route and extract params."""
        match = self.pattern.match(path)
        if match:
            return match.groupdict()
        return None


class PurePythonApp:
    """
    Pure Python web application - zero framework dependencies.

    This is the REAL core of CovetPy, implemented in pure Python
    without any external web frameworks.
    """

    def __init__(self, debug: bool = False):
        self.debug = debug
        self.routes: List[Route] = []
        self.middleware: List[Callable] = []
        self.before_request_handlers: List[Callable] = []
        self.after_request_handlers: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}

        # Optional database integration
        self.db = None

    def route(self, path: str, methods: Optional[List[str]] = None) -> Callable:
        """Register a route handler."""
        methods = methods or ["GET"]

        def decorator(func: Callable) -> Callable:
            route = Route(path, func, methods)
            self.routes.append(route)
            return func

        return decorator

    def get(self, path: str) -> Callable:
        """Register GET route."""
        return self.route(path, methods=["GET"])

    def post(self, path: str) -> Callable:
        """Register POST route."""
        return self.route(path, methods=["POST"])

    def put(self, path: str) -> Callable:
        """Register PUT route."""
        return self.route(path, methods=["PUT"])

    def delete(self, path: str) -> Callable:
        """Register DELETE route."""
        return self.route(path, methods=["DELETE"])

    def before_request(self, func: Callable) -> Callable:
        """Register a before request handler."""
        self.before_request_handlers.append(func)
        return func

    def after_request(self, func: Callable) -> Callable:
        """Register an after request handler."""
        self.after_request_handlers.append(func)
        return func

    def error_handler(self, status_code: int) -> Callable:
        """Register an error handler for status code."""

        def decorator(func: Callable) -> Callable:
            self.error_handlers[status_code] = func
            return func

        return decorator

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming HTTP request - pure Python logic."""
        try:
            # Run before request handlers
            for handler in self.before_request_handlers:
                result = await handler(request)
                if result is not None:
                    return self._make_response(result)

            # Find matching route
            for route in self.routes:
                if request.method not in route.methods:
                    continue

                params = route.match(request.path)
                if params is not None:
                    # Found match
                    request.path_params = params

                    # Call handler
                    result = await route.handler(request)

                    # Make response
                    response = self._make_response(result)

                    # Run after request handlers
                    for handler in self.after_request_handlers:
                        response = await handler(request, response)

                    return response

            # No route found
            return await self._handle_error(404, request)

        except Exception as e:
            if self.debug:
                import traceback

                body = {"error": str(e), "traceback": traceback.format_exc()}
            else:
                body = {"error": "Internal Server Error"}

            return Response(body=body, status_code=500)

    def _make_response(self, result: Any) -> Response:
        """Convert handler result to Response."""
        if isinstance(result, Response):
            return result
        elif isinstance(result, dict):
            return Response(body=result)
        elif isinstance(result, str):
            return Response(body=result, content_type="text/plain")
        elif isinstance(result, tuple) and len(result) == 2:
            body, status = result
            return Response(body=body, status_code=status)
        else:
            return Response(body=str(result), content_type="text/plain")

    async def _handle_error(self, status_code: int, request: Request) -> Response:
        """Handle HTTP errors."""
        if status_code in self.error_handlers:
            result = await self.error_handlers[status_code](request)
            return self._make_response(result)
        else:
            return Response(body={"error": f"Error {status_code}"}, status_code=status_code)

    def set_database(self, db: Any):
        """Set database adapter (optional SQLAlchemy integration)."""
        self.db = db

    async def startup(self):
        """Run startup tasks."""
        if self.db:
            # Connect to database if configured
            await self.db.connect()

    async def shutdown(self):
        """Run shutdown tasks."""
        if self.db:
            # Disconnect from database
            await self.db.disconnect()


# Pure Python ASGI adapter (no framework dependencies)
class PurePythonASGI:
    """ASGI adapter for pure Python app."""

    def __init__(self, app: PurePythonApp):
        self.app = app

    async def __call__(self, scope: dict, receive: Callable, send: Callable):
        """ASGI application interface."""
        if scope["type"] != "http":
            return

        # Parse request from ASGI scope
        request = Request(
            method=scope["method"],
            path=scope["path"],
            headers=dict(scope["headers"]),
            query_params=dict(scope.get("query_string", b"").decode()),
            path_params={},
            body=b"",
        )

        # Read body
        body_parts = []
        while True:
            message = await receive()
            if message["type"] == "http.request":
                body_parts.append(message.get("body", b""))
                if not message.get("more_body", False):
                    break

        request.body = b"".join(body_parts)

        # Handle request
        response = await self.app.handle_request(request)

        # Send response
        await send(
            {
                "type": "http.response.start",
                "status": response.status_code,
                "headers": [[k.encode(), v.encode()] for k, v in response.headers.items()],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": (
                    response.body.encode() if isinstance(response.body, str) else response.body
                ),
            }
        )


# Factory function
def create_app(**kwargs) -> PurePythonApp:
    """Create a pure Python CovetPy application."""
    return PurePythonApp(**kwargs)


# This is the TRUE CovetPy - pure Python, zero web framework dependencies
CovetPy = PurePythonApp
