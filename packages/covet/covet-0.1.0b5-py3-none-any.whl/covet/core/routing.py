"""
CovetPy Advanced Routing System
High-performance route matching with parameter extraction
"""

import logging
import re
from dataclasses import dataclass
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


@dataclass
class RouteInfo:
    """Information about a registered route"""

    pattern: str
    handler: Callable
    methods: list[str]
    param_names: list[str]
    regex_pattern: Optional[re.Pattern] = None


@dataclass
class RouteMatch:
    """Result of route matching"""

    handler: Callable
    params: dict[str, Any]


class CovetRouter:
    """Advanced routing system with parameter extraction and middleware support"""

    def __init__(self) -> None:
        self.static_routes: dict[str, dict[str, Callable]] = {}
        self.dynamic_routes: list[RouteInfo] = []
        self.middleware_stack: list[Callable] = []
        self._compiled = False

    def add_route(self, path: str, handler: Callable, methods: list[str]) -> None:
        """Add a route to the router"""
        methods = [m.upper() for m in methods]

        # Check if this is a static route (no parameters)
        if "{" not in path and "<" not in path:
            if path not in self.static_routes:
                self.static_routes[path] = {}
            for method in methods:
                self.static_routes[path][method] = handler
        else:
            # Dynamic route with parameters
            param_names = self._extract_param_names(path)
            route_info = RouteInfo(
                pattern=path, handler=handler, methods=methods, param_names=param_names
            )
            self.dynamic_routes.append(route_info)

        self._compiled = False  # Mark for recompilation

    def _extract_param_names(self, pattern: str) -> list[str]:
        """Extract parameter names from route pattern"""
        params = []

        # Handle {param} style
        import re

        for match in re.finditer(r"\{([^}]+)\}", pattern):
            params.append(match.group(1))

        # Handle <param> style (Flask-like)
        for match in re.finditer(r"<([^>]+)>", pattern):
            param = match.group(1)
            # Handle typed parameters like <int:user_id>
            if ":" in param:
                param = param.split(":", 1)[1]
            params.append(param)

        return params

    def _compile_dynamic_routes(self) -> None:
        """Compile dynamic routes to regex patterns for fast matching"""
        if self._compiled:
            return

        for route in self.dynamic_routes:
            pattern = route.pattern

            # Handle {param} style parameters - replace ALL occurrences
            if "{" in pattern and "}" in pattern:
                # Use a function to do the replacement to avoid backreference issues
                def replace_brace(match):
                    return f"(?P<{match.group(1)}>[^/]+)"
                pattern = re.sub(r"\{([^}]+)\}", replace_brace, pattern)

            # Handle < > style parameters - replace ALL occurrences
            elif "<" in pattern and ">" in pattern:
                # Use functions to handle replacements properly
                def replace_int(match):
                    return f"(?P<{match.group(1)}>\\d+)"
                def replace_str(match):
                    return f"(?P<{match.group(1)}>[^/]+)"
                def replace_float(match):
                    return f"(?P<{match.group(1)}>[\\d.]+)"
                def replace_simple(match):
                    return f"(?P<{match.group(1)}>[^/]+)"

                # First handle typed parameters like <int:param>
                pattern = re.sub(r"<int:([^>]+)>", replace_int, pattern)
                pattern = re.sub(r"<str:([^>]+)>", replace_str, pattern)
                pattern = re.sub(r"<float:([^>]+)>", replace_float, pattern)
                # Then handle simple parameters like <param>
                pattern = re.sub(r"<([^>]+)>", replace_simple, pattern)

            # Ensure exact match
            if not pattern.startswith("^"):
                pattern = "^" + pattern
            if not pattern.endswith("$"):
                pattern = pattern + "$"

            # Debug logging
            logger.debug(f"Compiling route pattern: {route.pattern} -> {pattern}")

            try:
                route.regex_pattern = re.compile(pattern)
            except re.error as e:
                logger.error(f"Failed to compile pattern '{pattern}' for route '{route.pattern}': {e}")
                raise

        self._compiled = True

    def match_route(self, path: str, method: str) -> Optional[RouteMatch]:
        """Find matching route and extract parameters"""
        method = method.upper()

        # Try static routes first (fastest)
        if path in self.static_routes and method in self.static_routes[path]:
            return RouteMatch(handler=self.static_routes[path][method], params={})

        # Compile dynamic routes if needed
        self._compile_dynamic_routes()

        # Try dynamic routes
        for route in self.dynamic_routes:
            if method not in route.methods:
                continue

            if route.regex_pattern:
                match = route.regex_pattern.match(path)
                if match:
                    params = match.groupdict()
                    # Convert string parameters to appropriate types
                    converted_params = {}
                    for key, value in params.items():
                        # Simple type conversion based on pattern
                        if value.isdigit():
                            converted_params[key] = int(value)
                        else:
                            converted_params[key] = value
                    return RouteMatch(handler=route.handler, params=converted_params)

        return None

    def get_all_routes(self) -> list[dict[str, Any]]:
        """Get information about all registered routes"""
        routes = []

        # Static routes
        for path, methods in self.static_routes.items():
            for method, handler in methods.items():
                routes.append(
                    {
                        "path": path,
                        "method": method,
                        "handler": handler.__name__,
                        "type": "static",
                    }
                )

        # Dynamic routes
        for route in self.dynamic_routes:
            for method in route.methods:
                routes.append(
                    {
                        "path": route.pattern,
                        "method": method,
                        "handler": route.handler.__name__,
                        "type": "dynamic",
                        "parameters": route.param_names,
                    }
                )

        return routes


class RouteGroup:
    """Group routes with common prefix and middleware"""

    def __init__(self, prefix: str = "", middleware: list[Callable] = None) -> None:
        self.prefix = prefix.rstrip("/")
        self.middleware = middleware or []
        self.routes: list[tuple[str, Callable, list[str]]] = []

    def route(self, path: str, methods: list[str] = None) -> Callable:
        """Add route to group"""
        if methods is None:
            methods = ["GET"]

        def decorator(handler: Callable) -> Callable:
            full_path = self.prefix + path
            self.routes.append((full_path, handler, methods))
            return handler

        return decorator

    def get(self, path: str) -> Callable:
        """
        Register a GET route in this group.

        Args:
            path: URL path relative to group prefix

        Returns:
            Decorator function for the route handler
        """
        return self.route(path, ["GET"])

    def post(self, path: str) -> Callable:
        """
        Register a POST route in this group.

        Args:
            path: URL path relative to group prefix

        Returns:
            Decorator function for the route handler
        """
        return self.route(path, ["POST"])

    def put(self, path: str) -> Callable:
        """
        Register a PUT route in this group.

        Args:
            path: URL path relative to group prefix

        Returns:
            Decorator function for the route handler
        """
        return self.route(path, ["PUT"])

    def delete(self, path: str) -> Callable:
        """
        Register a DELETE route in this group.

        Args:
            path: URL path relative to group prefix

        Returns:
            Decorator function for the route handler
        """
        return self.route(path, ["DELETE"])

    def include_in_router(self, router: CovetRouter) -> None:
        """Add all routes from this group to a router"""
        for path, handler, methods in self.routes:
            # Wrap handler with group middleware
            if self.middleware:
                original_handler = handler

                async def wrapped_handler(request: Any, *args: Any, **kwargs: Any) -> Any:
                    # Apply middleware in order
                    for middleware in self.middleware:
                        request = await middleware(request) or request
                    return await original_handler(request, *args, **kwargs)

                handler = wrapped_handler

            router.add_route(path, handler, methods)


def create_route_group(prefix: str = "", middleware: list[Callable] = None) -> RouteGroup:
    """Factory function for creating route groups"""
    return RouteGroup(prefix, middleware)


# Example middleware functions
async def cors_middleware(request: Any) -> Any:
    """Simple CORS middleware example"""
    # Add CORS headers to response (would need response object)
    return request


async def auth_middleware(request: Any) -> Any:
    """Simple authentication middleware example"""
    # Check for authentication token
    auth_header = request.headers.get("authorization", "")
    if not auth_header.startswith("Bearer "):
        # Would typically raise an authentication error
        pass
    return request


async def logging_middleware(request: Any) -> Any:
    """Simple logging middleware example"""
    logger.info("Request: {request.method} {request.path}")
    return request


# Backward compatibility alias
Router = CovetRouter

__all__ = [
    "CovetRouter",
    "Router",
    "RouteInfo",
    "RouteMatch",
    "RouteGroup",
    "create_route_group",
    "cors_middleware",
    "auth_middleware",
    "logging_middleware",
]


def create_router() -> CovetRouter:
    """Create a new router instance."""
    return CovetRouter()
