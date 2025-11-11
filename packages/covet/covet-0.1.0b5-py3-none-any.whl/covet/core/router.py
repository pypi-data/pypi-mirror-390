"""
CovetPy Router System
Simple router mixin for the core application
"""

import asyncio
from typing import Any, Callable, Dict, List, Optional, Union

from covet.core.routing import CovetRouter, RouteMatch


class RouterMixin:
    """
    Router mixin that provides routing functionality to the main application.

    This mixin adds route registration and handling capabilities to the
    main CovetApplication class.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._router = CovetRouter()

    def route(
        self, path: str, methods: List[str] = None, name: Optional[str] = None, **kwargs
    ) -> Callable:
        """
        Register a route with the application.

        Args:
            path: The URL path pattern
            methods: List of allowed HTTP methods
            name: Optional route name
            **kwargs: Additional route configuration

        Returns:
            Decorator function
        """
        methods = methods or ["GET"]

        def decorator(func: Callable) -> Callable:
            self._router.add_route(path, func, methods, name, **kwargs)
            return func

        return decorator

    def get(self, path: str, **kwargs) -> Callable:
        """Register a GET route."""
        return self.route(path, methods=["GET"], **kwargs)

    def post(self, path: str, **kwargs) -> Callable:
        """Register a POST route."""
        return self.route(path, methods=["POST"], **kwargs)

    def put(self, path: str, **kwargs) -> Callable:
        """Register a PUT route."""
        return self.route(path, methods=["PUT"], **kwargs)

    def delete(self, path: str, **kwargs) -> Callable:
        """Register a DELETE route."""
        return self.route(path, methods=["DELETE"], **kwargs)

    def patch(self, path: str, **kwargs) -> Callable:
        """Register a PATCH route."""
        return self.route(path, methods=["PATCH"], **kwargs)

    def head(self, path: str, **kwargs) -> Callable:
        """Register a HEAD route."""
        return self.route(path, methods=["HEAD"], **kwargs)

    def options(self, path: str, **kwargs) -> Callable:
        """Register an OPTIONS route."""
        return self.route(path, methods=["OPTIONS"], **kwargs)

    def match_route(self, path: str, method: str) -> Optional[RouteMatch]:
        """
        Find a matching route for the given path and method.

        Args:
            path: The request path
            method: The HTTP method

        Returns:
            RouteMatch object if found, None otherwise
        """
        return self._router.match(path, method)

    async def handle_route(self, match: RouteMatch, request: Any) -> Any:
        """
        Handle a matched route by calling the handler function.

        Args:
            match: The matched route
            request: The request object

        Returns:
            Response from the handler
        """
        handler = match.handler

        try:
            # Call the handler (async or sync)
            if asyncio.iscoroutinefunction(handler):
                return await handler(request)
            else:
                return handler(request)
        except Exception as e:
            # Let the main application handle the error
            raise e

    def get_routes(self) -> List[Dict[str, Any]]:
        """
        Get all registered routes.

        Returns:
            List of route information dictionaries
        """
        return self._router.get_routes()
