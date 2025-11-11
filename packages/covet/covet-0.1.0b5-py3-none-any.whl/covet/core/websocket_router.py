"""
WebSocket Routing and Decorators

This module provides routing and decorator support for WebSocket endpoints
that integrate seamlessly with the CovetPy ASGI framework.
"""

import asyncio
import functools
import inspect
import logging
import re
from typing import Any, Callable, Dict, List, Optional, Pattern, Union

from .websocket_connection import (
    WebSocketConnection,
    WebSocketConnectionManager,
    default_connection_manager,
)
from .websocket_impl import BinaryMessage, JSONMessage, TextMessage, WebSocketMessage

logger = logging.getLogger(__name__)


class WebSocketRoute:
    """WebSocket route definition."""

    def __init__(
        self,
        path: str,
        handler: Callable,
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
    ):
        self.path = path
        self.handler = handler
        self.name = name or f"websocket_{handler.__name__}"
        self.middleware = middleware or []

        # Compile path pattern
        self.path_pattern, self.param_names = self._compile_path(path)

    def _compile_path(self, path: str) -> tuple[Pattern[str], List[str]]:
        """Compile path pattern with parameter extraction."""
        param_names = []
        pattern_parts = []

        # Split path into segments
        segments = path.split("/")

        for segment in segments:
            if not segment:
                continue

            if segment.startswith("{") and segment.endswith("}"):
                # Path parameter
                param_name = segment[1:-1]
                if ":" in param_name:
                    param_name, param_type = param_name.split(":", 1)
                    if param_type == "int":
                        pattern_parts.append(r"(\d+)")
                    elif param_type == "float":
                        pattern_parts.append(r"(\d+\.?\d*)")
                    elif param_type == "str":
                        pattern_parts.append(r"([^/]+)")
                    else:
                        pattern_parts.append(r"([^/]+)")
                else:
                    pattern_parts.append(r"([^/]+)")

                param_names.append(param_name)
            else:
                # Literal segment
                pattern_parts.append(re.escape(segment))

        pattern = "^/" + "/".join(pattern_parts) + "/?$"
        return re.compile(pattern), param_names

    def match(self, path: str) -> Optional[Dict[str, str]]:
        """Match path and extract parameters."""
        match = self.path_pattern.match(path)
        if not match:
            return None

        params = {}
        for i, param_name in enumerate(self.param_names):
            params[param_name] = match.group(i + 1)

        return params

    def __repr__(self) -> str:
        return f"WebSocketRoute(path='{self.path}', name='{self.name}')"


class WebSocketRouter:
    """
    WebSocket router with pattern matching and middleware support.
    """

    def __init__(self, connection_manager: Optional[WebSocketConnectionManager] = None):
        self.connection_manager = connection_manager or default_connection_manager
        self.routes: List[WebSocketRoute] = []
        self.middleware: List[Callable] = []

    def websocket(
        self,
        path: str,
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
    ):
        """
        Decorator for WebSocket route handlers.

        Usage:
            @router.websocket("/ws")
            async def websocket_handler(websocket):
                await websocket.accept()
                while True:
                    message = await websocket.receive_text()
                    await websocket.send_text(f"Echo: {message}")
        """

        def decorator(handler: Callable) -> Callable:
            route = WebSocketRoute(path=path, handler=handler, name=name, middleware=middleware)
            self.routes.append(route)
            return handler

        return decorator

    def add_route(
        self,
        path: str,
        handler: Callable,
        name: Optional[str] = None,
        middleware: Optional[List[Callable]] = None,
    ) -> None:
        """Add a WebSocket route programmatically."""
        route = WebSocketRoute(path=path, handler=handler, name=name, middleware=middleware)
        self.routes.append(route)

    def add_middleware(self, middleware: Callable) -> None:
        """Add global WebSocket middleware."""
        self.middleware.append(middleware)

    def find_route(self, path: str) -> Optional[tuple[WebSocketRoute, Dict[str, str]]]:
        """Find matching route for path."""
        for route in self.routes:
            params = route.match(path)
            if params is not None:
                return route, params

        return None

    async def handle_websocket(
        self, scope: Dict[str, Any], receive: Callable, send: Callable
    ) -> None:
        """Handle WebSocket connection."""
        path = scope.get("path", "/")

        # Find matching route
        route_match = self.find_route(path)
        if not route_match:
            # No route found - reject connection
            await send({"type": "websocket.close", "code": 404})
            return

        route, path_params = route_match

        # Create connection
        connection = WebSocketConnection(
            scope=scope,
            receive=receive,
            send=send,
            connection_manager=self.connection_manager,
        )

        # Set path parameters
        connection.path_params = path_params

        try:
            # Apply middleware
            handler = route.handler
            for middleware in reversed(self.middleware + route.middleware):
                handler = await self._apply_middleware(middleware, handler)

            # Call handler
            await handler(connection)

        except Exception as e:
            logger.error(f"Error in WebSocket handler: {e}", exc_info=True)
            if connection.state.value in ["connecting", "open"]:
                await connection.close(1011, "Internal server error")

    async def _apply_middleware(self, middleware: Callable, handler: Callable) -> Callable:
        """Apply middleware to handler."""
        if asyncio.iscoroutinefunction(middleware):

            async def wrapped_handler(connection: WebSocketConnection):
                return await middleware(connection, handler)

        else:

            def wrapped_handler(connection: WebSocketConnection):
                return middleware(connection, handler)

        return wrapped_handler


# Decorators for message handling
def on_connect(func: Callable) -> Callable:
    """Decorator for connection event handler."""
    func._websocket_event = "connect"
    return func


def on_disconnect(func: Callable) -> Callable:
    """Decorator for disconnection event handler."""
    func._websocket_event = "disconnect"
    return func


def on_message(message_type: Optional[str] = None):
    """
    Decorator for message event handler.

    Usage:
        @on_message("chat")
        async def handle_chat(connection, message):
            # Handle chat message
    """

    def decorator(func: Callable) -> Callable:
        func._websocket_event = "message"
        func._message_type = message_type
        return func

    return decorator


def on_text(func: Callable) -> Callable:
    """Decorator for text message handler."""
    func._websocket_event = "message"
    func._message_type = "text"
    return func


def on_binary(func: Callable) -> Callable:
    """Decorator for binary message handler."""
    func._websocket_event = "message"
    func._message_type = "binary"
    return func


def on_json(func: Callable) -> Callable:
    """Decorator for JSON message handler."""
    func._websocket_event = "message"
    func._message_type = "json"
    return func


class WebSocketEndpoint:
    """
    Base class for WebSocket endpoints with automatic event handler registration.

    Usage:
        class ChatEndpoint(WebSocketEndpoint):
            async def on_connect(self, connection):
                await connection.accept()
                await connection.join_room("general")

            @on_json
            async def handle_message(self, connection, message):
                await self.broadcast_to_room("general", message.data)
    """

    def __init__(self, connection_manager: Optional[WebSocketConnectionManager] = None):
        self.connection_manager = connection_manager or default_connection_manager
        self._register_handlers()

    def _register_handlers(self) -> None:
        """Register event handlers from decorated methods."""
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, "_websocket_event"):
                event = method._websocket_event
                if event == "connect":
                    self.on_connect_handler = method
                elif event == "disconnect":
                    self.on_disconnect_handler = method
                elif event == "message":
                    message_type = getattr(method, "_message_type", None)
                    if not hasattr(self, "_message_handlers"):
                        self._message_handlers = {}
                    self._message_handlers[message_type] = method

    async def __call__(self, connection: WebSocketConnection) -> None:
        """Handle WebSocket connection."""
        # Set up event handlers
        if hasattr(self, "on_connect_handler"):
            connection.on_connect = self.on_connect_handler

        if hasattr(self, "on_disconnect_handler"):
            connection.on_disconnect = self.on_disconnect_handler

        if hasattr(self, "_message_handlers"):
            for message_type, handler in self._message_handlers.items():
                connection.set_message_handler(message_type, handler)

        # Accept connection if not explicitly handled
        if not hasattr(self, "on_connect_handler"):
            await connection.accept()

        # Keep connection alive
        try:
            while connection.state.value == "open":
                await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in WebSocket endpoint: {e}", exc_info=True)

    async def broadcast_to_room(self, room: str, data: Any) -> int:
        """Broadcast data to all connections in a room."""
        if isinstance(data, str):
            message = TextMessage(content=data)
        elif isinstance(data, bytes):
            message = BinaryMessage(data=data)
        else:
            message = JSONMessage(data=data)

        return await self.connection_manager.broadcast_to_room(room, message)

    async def broadcast_to_user(self, user_id: str, data: Any) -> int:
        """Broadcast data to all connections of a user."""
        if isinstance(data, str):
            message = TextMessage(content=data)
        elif isinstance(data, bytes):
            message = BinaryMessage(data=data)
        else:
            message = JSONMessage(data=data)

        return await self.connection_manager.broadcast_to_user(user_id, message)

    async def broadcast_to_all(self, data: Any) -> int:
        """Broadcast data to all connections."""
        if isinstance(data, str):
            message = TextMessage(content=data)
        elif isinstance(data, bytes):
            message = BinaryMessage(data=data)
        else:
            message = JSONMessage(data=data)

        return await self.connection_manager.broadcast_to_all(message)


# Middleware decorators
def require_authentication(connection: WebSocketConnection, handler: Callable):
    """Middleware to require authentication."""

    async def wrapper():
        if not connection.info.authenticated:
            await connection.close(1008, "Authentication required")
            return

        return await handler()

    return wrapper


def rate_limit(max_messages: int = 100, window_seconds: int = 60):
    """Middleware for rate limiting."""

    def middleware(connection: WebSocketConnection, handler: Callable):
        # Rate limiting is handled in the connection itself
        return handler

    return middleware


def cors_websocket(allowed_origins: List[str]):
    """CORS middleware for WebSocket connections."""

    def middleware(connection: WebSocketConnection, handler: Callable):
        async def wrapper():
            origin = connection.info.headers.get("origin")
            if origin and origin not in allowed_origins:
                await connection.close(1008, "Origin not allowed")
                return

            return await handler()

        return wrapper

    return middleware


# Simple wrapper functions for common patterns
def websocket_handler(
    path: str,
    router: Optional[WebSocketRouter] = None,
    name: Optional[str] = None,
    middleware: Optional[List[Callable]] = None,
):
    """
    Simple decorator for WebSocket handlers.

    Usage:
        @websocket_handler("/ws/chat")
        async def chat_handler(connection):
            await connection.accept()
            while True:
                message = await connection.receive_text()
                await connection.send_text(f"Echo: {message}")
    """
    if router is None:
        # Create a default router
        router = WebSocketRouter()

    return router.websocket(path, name=name, middleware=middleware)


# Export main components
__all__ = [
    "WebSocketRoute",
    "WebSocketRouter",
    "WebSocketEndpoint",
    "on_connect",
    "on_disconnect",
    "on_message",
    "on_text",
    "on_binary",
    "on_json",
    "require_authentication",
    "rate_limit",
    "cors_websocket",
    "websocket_handler",
]
