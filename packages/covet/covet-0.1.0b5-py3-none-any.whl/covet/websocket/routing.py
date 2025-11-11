"""
WebSocket Routing System

This module provides a comprehensive routing system for WebSocket connections
with decorators, middleware support, and endpoint classes.
"""

import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import wraps
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union
from urllib.parse import parse_qs

from .connection import (
    WebSocketConnection,
    WebSocketConnectionManager,
    default_connection_manager,
)
from .protocol import BinaryMessage, JSONMessage, OpCode, TextMessage, WebSocketMessage

logger = logging.getLogger(__name__)


@dataclass
class WebSocketRoute:
    """Represents a WebSocket route."""

    path: str
    handler: Callable
    middleware: List[Callable] = None
    name: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.middleware is None:
            self.middleware = []
        if self.metadata is None:
            self.metadata = {}


class WebSocketEndpoint(ABC):
    """
    Base class for WebSocket endpoints.

    Provides a class-based approach to handling WebSocket connections
    with lifecycle methods and automatic event routing.
    """

    def __init__(self, connection_manager: WebSocketConnectionManager = None):
        self.connection_manager = connection_manager or default_connection_manager
        self._handlers: Dict[str, Callable] = {}
        self._middleware: List[Callable] = []

        # Register event handlers from decorated methods
        self._register_handlers()

    def _register_handlers(self):
        """Register event handlers from decorated methods."""
        for name in dir(self):
            method = getattr(self, name)
            if hasattr(method, "_ws_event_type"):
                event_type = method._ws_event_type
                self._handlers[event_type] = method
                logger.debug(f"Registered handler for {event_type}: {name}")

    async def handle_connection(self, connection: WebSocketConnection):
        """Handle a WebSocket connection."""
        try:
            # Call connect handler
            if "connect" in self._handlers:
                await self._handlers["connect"](connection)

            # Message loop
            while connection.is_connected:
                try:
                    message = await connection.receive()
                    if message:
                        await self._handle_message(connection, message)
                except Exception as e:
                    logger.error(f"Error handling message: {e}")
                    if "error" in self._handlers:
                        await self._handlers["error"](connection, e)
                    break

        except Exception as e:
            logger.error(f"Error in connection handler: {e}")
            if "error" in self._handlers:
                try:
                    await self._handlers["error"](connection, e)
                except Exception:
                    # TODO: Add proper exception handling

                    pass
        finally:
            # Call disconnect handler
            if "disconnect" in self._handlers:
                try:
                    await self._handlers["disconnect"](connection)
                except Exception as e:
                    logger.error(f"Error in disconnect handler: {e}")

    async def _handle_message(self, connection: WebSocketConnection, message: WebSocketMessage):
        """Route message to appropriate handler."""
        handler_name = None

        # Determine handler based on message type
        if isinstance(message, TextMessage):
            if "text" in self._handlers:
                handler_name = "text"
            elif isinstance(message, JSONMessage) and "json" in self._handlers:
                handler_name = "json"
        elif isinstance(message, BinaryMessage):
            if "binary" in self._handlers:
                handler_name = "binary"

        # Fall back to generic message handler
        if not handler_name and "message" in self._handlers:
            handler_name = "message"

        # Call handler
        if handler_name:
            try:
                await self._handlers[handler_name](connection, message)
            except Exception as e:
                logger.error(f"Error in {handler_name} handler: {e}")
                raise
        else:
            logger.warning(f"No handler for message type: {type(message)}")

    # Utility methods for endpoints
    async def broadcast_to_room(self, room: str, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections in a room."""
        if isinstance(message, str):
            ws_message = TextMessage(message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(message)
        else:
            ws_message = JSONMessage(message)

        return await self.connection_manager.broadcast_to_room(room, ws_message)

    async def broadcast_to_user(self, user_id: str, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections of a user."""
        if isinstance(message, str):
            ws_message = TextMessage(message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(message)
        else:
            ws_message = JSONMessage(message)

        return await self.connection_manager.broadcast_to_user(user_id, ws_message)

    async def broadcast_to_all(self, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections."""
        if isinstance(message, str):
            ws_message = TextMessage(message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(message)
        else:
            ws_message = JSONMessage(message)

        return await self.connection_manager.broadcast_to_all(ws_message)


class WebSocketRouter:
    """
    WebSocket router that handles routing WebSocket connections to endpoints.

    Supports:
    - Path-based routing
    - Middleware
    - Query parameter parsing
    - Connection lifecycle management
    """

    def __init__(self, connection_manager: WebSocketConnectionManager = None):
        self.connection_manager = connection_manager or default_connection_manager
        self.routes: List[WebSocketRoute] = []
        self.middleware: List[Callable] = []
        self._route_map: Dict[str, WebSocketRoute] = {}

    def add_route(
        self,
        path: str,
        handler: Union[Callable, WebSocketEndpoint],
        middleware: List[Callable] = None,
        name: Optional[str] = None,
        **metadata,
    ):
        """Add a WebSocket route."""
        route = WebSocketRoute(
            path=path,
            handler=handler,
            middleware=middleware or [],
            name=name,
            metadata=metadata,
        )

        self.routes.append(route)
        self._route_map[path] = route

        logger.info(f"Added WebSocket route: {path}")

    def websocket(self, path: str, **kwargs):
        """Decorator for WebSocket route handlers."""

        def decorator(func):
            self.add_route(path, func, **kwargs)
            return func

        return decorator

    def add_middleware(self, middleware: Callable):
        """Add middleware to the router."""
        self.middleware.append(middleware)
        logger.debug(f"Added middleware: {middleware.__name__}")

    def middleware_decorator(self, func: Callable):
        """Decorator to add middleware."""
        self.add_middleware(func)
        return func

    async def handle_websocket(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """Handle incoming WebSocket connection."""
        # Extract connection info
        path = scope.get("path", "/")
        query_string = scope.get("query_string", b"").decode()
        headers = dict(scope.get("headers", []))
        client = scope.get("client", ["unknown", 0])

        # Parse query parameters
        query_params = parse_qs(query_string)

        # Find matching route
        route = self._find_route(path)
        if not route:
            # No route found, close connection
            await send({"type": "websocket.close", "code": 4004, "reason": "No route found"})
            return

        # Create connection ID
        import uuid

        connection_id = str(uuid.uuid4())

        # Create ASGI WebSocket wrapper
        websocket = ASGIWebSocket(scope, receive, send)

        try:
            # Create connection
            connection = await self.connection_manager.add_connection(
                websocket=websocket,
                connection_id=connection_id,
                ip_address=client[0],
                user_agent=headers.get(b"user-agent", b"").decode(),
                metadata={
                    "path": path,
                    "query_params": query_params,
                    "headers": headers,
                },
            )

            # Apply middleware
            await self._apply_middleware(connection, route)

            # Handle connection
            if isinstance(route.handler, WebSocketEndpoint):
                await route.handler.handle_connection(connection)
            else:
                await route.handler(connection)

        except Exception as e:
            logger.error(f"Error handling WebSocket connection: {e}")
            try:
                await websocket.close(code=1011, reason="Internal server error")
            except Exception:
                # TODO: Add proper exception handling

                pass
        finally:
            # Ensure connection is removed
            try:
                await self.connection_manager.remove_connection(connection_id)
            except Exception:
                # TODO: Add proper exception handling

                pass

    def _find_route(self, path: str) -> Optional[WebSocketRoute]:
        """Find matching route for path."""
        # For now, do exact match. Could add pattern matching later
        return self._route_map.get(path)

    async def _apply_middleware(self, connection: WebSocketConnection, route: WebSocketRoute):
        """Apply middleware to connection."""
        # Apply global middleware
        for middleware in self.middleware:
            try:
                await middleware(connection)
            except Exception as e:
                logger.error(f"Error in global middleware: {e}")
                raise

        # Apply route-specific middleware
        for middleware in route.middleware:
            try:
                await middleware(connection)
            except Exception as e:
                logger.error(f"Error in route middleware: {e}")
                raise


class ASGIWebSocket:
    """ASGI WebSocket wrapper to provide a consistent interface."""

    def __init__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        self.scope = scope
        self.receive_callable = receive
        self.send_callable = send
        self._accepted = False
        self._closed = False

    async def accept(self):
        """Accept the WebSocket connection."""
        if self._accepted:
            return

        await self.send_callable({"type": "websocket.accept"})
        self._accepted = True

    async def send_text(self, text: str):
        """Send text message."""
        if not self._accepted or self._closed:
            return

        await self.send_callable({"type": "websocket.send", "text": text})

    async def send_bytes(self, data: bytes):
        """Send binary message."""
        if not self._accepted or self._closed:
            return

        await self.send_callable({"type": "websocket.send", "bytes": data})

    async def send_json(self, data: Any):
        """Send JSON message."""
        import json

        text = json.dumps(data, separators=(",", ":"))
        await self.send_text(text)

    async def receive_text(self) -> str:
        """Receive text message."""
        message = await self.receive_callable()

        if message["type"] == "websocket.receive":
            if "text" in message:
                return message["text"]
            else:
                raise ValueError("Expected text message")
        elif message["type"] == "websocket.disconnect":
            self._closed = True
            raise ConnectionError("WebSocket disconnected")
        else:
            raise ValueError(f"Unexpected message type: {message['type']}")

    async def receive_bytes(self) -> bytes:
        """Receive binary message."""
        message = await self.receive_callable()

        if message["type"] == "websocket.receive":
            if "bytes" in message:
                return message["bytes"]
            elif "text" in message:
                return message["text"].encode("utf-8")
            else:
                raise ValueError("Expected binary message")
        elif message["type"] == "websocket.disconnect":
            self._closed = True
            raise ConnectionError("WebSocket disconnected")
        else:
            raise ValueError(f"Unexpected message type: {message['type']}")

    async def receive_json(self) -> Any:
        """Receive JSON message."""
        import json

        text = await self.receive_text()
        return json.loads(text)

    async def close(self, code: int = 1000, reason: str = ""):
        """Close the WebSocket connection."""
        if self._closed:
            return

        await self.send_callable({"type": "websocket.close", "code": code, "reason": reason})
        self._closed = True


# Event handler decorators
def on_connect(func):
    """Decorator for connection event handler."""
    func._ws_event_type = "connect"
    return func


def on_disconnect(func):
    """Decorator for disconnection event handler."""
    func._ws_event_type = "disconnect"
    return func


def on_message(func):
    """Decorator for generic message event handler."""
    func._ws_event_type = "message"
    return func


def on_text(func):
    """Decorator for text message event handler."""
    func._ws_event_type = "text"
    return func


def on_binary(func):
    """Decorator for binary message event handler."""
    func._ws_event_type = "binary"
    return func


def on_json(func):
    """Decorator for JSON message event handler."""
    func._ws_event_type = "json"
    return func


def on_error(func):
    """Decorator for error event handler."""
    func._ws_event_type = "error"
    return func


def websocket_handler(path: str, router: WebSocketRouter = None):
    """Decorator to register a WebSocket handler function."""

    def decorator(func):
        if router is None:
            # Use default router (need to create one)
            pass
        else:
            router.add_route(path, func)
        return func

    return decorator


# Middleware helpers
def cors_middleware(allowed_origins: List[str] = None):
    """CORS middleware for WebSocket connections."""

    async def middleware(connection: WebSocketConnection):
        # CORS is handled during HTTP upgrade, so this is mostly a placeholder
        # Real CORS handling should be done in the HTTP layer
        pass

    return middleware


def auth_middleware(auth_func: Callable):
    """Authentication middleware."""

    async def middleware(connection: WebSocketConnection):
        # Extract auth info from connection metadata
        headers = connection.info.metadata.get("headers", {})
        query_params = connection.info.metadata.get("query_params", {})

        # Call auth function
        is_authenticated = await auth_func(connection, headers, query_params)

        if not is_authenticated:
            await connection.close(code=4001, reason="Authentication failed")
            raise Exception("Authentication failed")

        connection.is_authenticated = True

    return middleware


def rate_limit_middleware(max_messages_per_minute: int = 60):
    """Rate limiting middleware."""
    import time
    from collections import defaultdict, deque

    # Store message timestamps per connection
    message_timestamps = defaultdict(deque)

    async def middleware(connection: WebSocketConnection):
        # This would be called on connection, but rate limiting
        # is better done per message. This is a placeholder.
        pass

    return middleware


# Example endpoint implementations
class EchoEndpoint(WebSocketEndpoint):
    """Simple echo WebSocket endpoint."""

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        await connection.accept()
        await connection.send_text("Echo server connected! Send me a message.")
        logger.info(f"Echo connection established: {connection.id}")

    @on_text
    async def handle_text(self, connection: WebSocketConnection, message: TextMessage):
        echo_response = f"Echo: {message.content}"
        await connection.send_text(echo_response)
        logger.debug(f"Echo text: {message.content}")

    @on_binary
    async def handle_binary(self, connection: WebSocketConnection, message: BinaryMessage):
        echo_response = b"Echo: " + message.data
        await connection.send_bytes(echo_response)
        logger.debug(f"Echo binary: {len(message.data)} bytes")

    @on_json
    async def handle_json(self, connection: WebSocketConnection, message: JSONMessage):
        echo_response = {"echo": message.data, "timestamp": message.timestamp}
        await connection.send_json(echo_response)
        logger.debug(f"Echo JSON: {message.data}")

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        logger.info(f"Echo connection closed: {connection.id}")


class ChatEndpoint(WebSocketEndpoint):
    """Chat room WebSocket endpoint."""

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        await connection.accept()

        # Join default room
        await self.connection_manager.join_room(connection.id, "general")

        # Notify room
        await self.broadcast_to_room(
            "general",
            {
                "type": "user_joined",
                "user_id": connection.id,
                "message": f"User {connection.id} joined the chat",
            },
        )

        # Send welcome message
        await connection.send_json(
            {
                "type": "welcome",
                "message": "Welcome to the chat! You're in the 'general' room.",
            }
        )

        logger.info(f"Chat connection established: {connection.id}")

    @on_json
    async def handle_json(self, connection: WebSocketConnection, message: JSONMessage):
        data = message.data

        if data.get("type") == "chat_message":
            # Broadcast chat message to room
            room = data.get("room", "general")

            broadcast_message = {
                "type": "chat_message",
                "user_id": connection.id,
                "room": room,
                "message": data.get("message", ""),
                "timestamp": message.timestamp,
            }

            await self.broadcast_to_room(room, broadcast_message)
            logger.debug(f"Chat message in {room}: {data.get('message', '')}")

        elif data.get("type") == "join_room":
            # Join a different room
            old_room = data.get("old_room", "general")
            new_room = data.get("new_room", "general")

            if old_room != new_room:
                await self.connection_manager.leave_room(connection.id, old_room)
                await self.connection_manager.join_room(connection.id, new_room)

                # Notify rooms
                await self.broadcast_to_room(
                    old_room,
                    {"type": "user_left", "user_id": connection.id, "room": old_room},
                )

                await self.broadcast_to_room(
                    new_room,
                    {"type": "user_joined", "user_id": connection.id, "room": new_room},
                )

                await connection.send_json(
                    {"type": "room_changed", "old_room": old_room, "new_room": new_room}
                )

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        # Notify all rooms the user was in
        for room in connection.info.rooms:
            await self.broadcast_to_room(
                room, {"type": "user_left", "user_id": connection.id, "room": room}
            )

        logger.info(f"Chat connection closed: {connection.id}")


# Global router instance
default_router = WebSocketRouter()


# Convenience functions
def create_router(
    connection_manager: WebSocketConnectionManager = None,
) -> WebSocketRouter:
    """Create a new WebSocket router."""
    return WebSocketRouter(connection_manager)


def setup_echo_endpoint(router: WebSocketRouter = None, path: str = "/ws/echo"):
    """Set up echo endpoint."""
    if router is None:
        router = default_router

    router.add_route(path, EchoEndpoint())
    logger.info(f"Echo endpoint set up at {path}")


def setup_chat_endpoint(router: WebSocketRouter = None, path: str = "/ws/chat"):
    """Set up chat endpoint."""
    if router is None:
        router = default_router

    router.add_route(path, ChatEndpoint())
    logger.info(f"Chat endpoint set up at {path}")
