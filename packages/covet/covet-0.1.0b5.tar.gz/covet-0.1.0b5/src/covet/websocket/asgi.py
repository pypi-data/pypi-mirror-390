"""
ASGI Integration for WebSocket

This module provides ASGI application and middleware for integrating
WebSocket functionality with the CovetPy framework.
"""

import asyncio
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional

from .connection import WebSocketConnectionManager, default_connection_manager
from .protocol import CloseCode
from .routing import WebSocketRouter, default_router
from .security import SecurityConfig, SecurityViolation, WebSocketSecurity

logger = logging.getLogger(__name__)

ASGIApp = Callable[[Dict[str, Any], Callable, Callable], Awaitable[None]]


class WebSocketASGI:
    """
    ASGI application for WebSocket handling.

    This class provides a complete ASGI application that can handle
    WebSocket connections alongside HTTP requests.
    """

    def __init__(
        self,
        router: WebSocketRouter = None,
        connection_manager: WebSocketConnectionManager = None,
        security: WebSocketSecurity = None,
        debug: bool = False,
    ):
        self.router = router or default_router
        self.connection_manager = connection_manager or default_connection_manager
        self.security = security
        self.debug = debug

        # Statistics
        self.total_connections = 0
        self.active_connections = 0
        self.total_errors = 0

        logger.info("WebSocket ASGI application initialized")

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """ASGI application callable."""
        if scope["type"] == "websocket":
            await self.handle_websocket(scope, receive, send)
        else:
            # Not a WebSocket, return 404
            await self.handle_not_websocket(scope, receive, send)

    async def handle_websocket(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """Handle WebSocket connection."""
        self.total_connections += 1
        self.active_connections += 1

        websocket = None
        connection = None

        try:
            # Create WebSocket wrapper
            websocket = ASGIWebSocketAdapter(scope, receive, send)

            # Extract connection info
            path = scope.get("path", "/")
            client = scope.get("client", ["unknown", 0])
            headers = dict(scope.get("headers", []))
            query_string = scope.get("query_string", b"").decode()

            # Parse query parameters
            from urllib.parse import parse_qs

            query_params = parse_qs(query_string)

            # Security checks
            if self.security:
                try:
                    # Check origin if provided
                    origin = headers.get(b"origin", b"").decode()
                    if origin and not self.security.validate_origin(origin):
                        await websocket.close(4003, "Origin not allowed")
                        return

                    # Check connection rate limit
                    if not self.security.check_connection_limit(client[0]):
                        await websocket.close(4029, "Rate limit exceeded")
                        return

                except SecurityViolation as e:
                    await websocket.close(e.code, e.message)
                    return

            # Create connection ID
            import uuid

            connection_id = str(uuid.uuid4())

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
                    "scope": scope,
                },
            )

            # Apply security middleware
            if self.security:
                try:
                    if not await self.security.authenticate_connection(connection):
                        await connection.close(4001, "Authentication failed")
                        return
                except SecurityViolation as e:
                    await connection.close(e.code, e.message)
                    return

            # Handle with router
            await self.router.handle_websocket(scope, receive, send)

        except Exception as e:
            self.total_errors += 1
            logger.error(f"WebSocket error: {e}")

            if websocket and not websocket._closed:
                try:
                    await websocket.close(1011, "Internal server error")
                except Exception:
                    # TODO: Add proper exception handling

                    pass
        finally:
            self.active_connections -= 1

            # Ensure connection is cleaned up
            if connection:
                try:
                    await self.connection_manager.remove_connection(connection.id)
                except Exception:
                    # TODO: Add proper exception handling

                    pass

    async def handle_not_websocket(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """Handle non-WebSocket requests."""
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [
                    [b"content-type", b"text/plain"],
                    [b"content-length", b"23"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"WebSocket endpoint only",
            }
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get ASGI application statistics."""
        connection_manager_stats = self.connection_manager.get_statistics()

        stats = {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "total_errors": self.total_errors,
            "router_stats": {
                "routes": len(self.router.routes),
                "middleware": len(self.router.middleware),
            },
            "connection_manager_stats": connection_manager_stats,
            "security_stats": (self.security.get_security_stats() if self.security else None),
        }

        # Merge connection manager stats at top level for backwards
        # compatibility
        stats.update(connection_manager_stats)

        return stats


class ASGIWebSocketAdapter:
    """Adapter to make ASGI WebSocket compatible with our WebSocket interface."""

    def __init__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        self.scope = scope
        self.receive = receive
        self.send = send
        self._accepted = False
        self._closed = False

    async def accept(self, subprotocol: str = None):
        """Accept the WebSocket connection."""
        if self._accepted:
            return

        message = {"type": "websocket.accept"}
        if subprotocol:
            message["subprotocol"] = subprotocol

        await self.send(message)
        self._accepted = True

    async def send_text(self, text: str):
        """Send text message."""
        if not self._accepted or self._closed:
            raise RuntimeError("WebSocket not connected")

        await self.send({"type": "websocket.send", "text": text})

    async def send_bytes(self, data: bytes):
        """Send binary message."""
        if not self._accepted or self._closed:
            raise RuntimeError("WebSocket not connected")

        await self.send({"type": "websocket.send", "bytes": data})

    async def send_json(self, data: Any):
        """Send JSON message."""
        import json

        await self.send_text(json.dumps(data, separators=(",", ":")))

    async def receive_text(self) -> str:
        """Receive text message."""
        message = await self.receive()

        if message["type"] == "websocket.receive":
            if "text" in message:
                return message["text"]
            else:
                raise RuntimeError("Expected text message")
        elif message["type"] == "websocket.disconnect":
            self._closed = True
            raise ConnectionError("WebSocket disconnected")
        else:
            raise RuntimeError(f"Unexpected message type: {message['type']}")

    async def receive_bytes(self) -> bytes:
        """Receive binary message."""
        message = await self.receive()

        if message["type"] == "websocket.receive":
            if "bytes" in message:
                return message["bytes"]
            elif "text" in message:
                return message["text"].encode("utf-8")
            else:
                raise RuntimeError("Expected binary message")
        elif message["type"] == "websocket.disconnect":
            self._closed = True
            raise ConnectionError("WebSocket disconnected")
        else:
            raise RuntimeError(f"Unexpected message type: {message['type']}")

    async def receive_json(self) -> Any:
        """Receive JSON message."""
        import json

        text = await self.receive_text()
        return json.loads(text)

    async def close(self, code: int = 1000, reason: str = ""):
        """Close the WebSocket connection."""
        if self._closed:
            return

        await self.send({"type": "websocket.close", "code": code, "reason": reason})
        self._closed = True


class WebSocketMiddleware:
    """
    ASGI middleware for adding WebSocket support to existing applications.

    This middleware can be added to any ASGI application to provide
    WebSocket functionality.
    """

    def __init__(
        self,
        app: ASGIApp,
        websocket_app: WebSocketASGI = None,
        websocket_path_prefix: str = "/ws",
    ):
        self.app = app
        self.websocket_app = websocket_app or WebSocketASGI()
        self.websocket_path_prefix = websocket_path_prefix

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """ASGI middleware callable."""
        if scope["type"] == "websocket":
            path = scope.get("path", "/")

            # Check if path starts with WebSocket prefix
            if path.startswith(self.websocket_path_prefix):
                await self.websocket_app(scope, receive, send)
                return

        # Pass through to the original application
        await self.app(scope, receive, send)


def create_websocket_asgi_app(
    router: WebSocketRouter = None,
    connection_manager: WebSocketConnectionManager = None,
    security_config: SecurityConfig = None,
    debug: bool = False,
) -> WebSocketASGI:
    """Create a WebSocket ASGI application."""
    security = None
    if security_config:
        security = WebSocketSecurity(security_config)

    return WebSocketASGI(
        router=router,
        connection_manager=connection_manager,
        security=security,
        debug=debug,
    )


def add_websocket_to_asgi_app(
    app: ASGIApp,
    router: WebSocketRouter = None,
    connection_manager: WebSocketConnectionManager = None,
    security_config: SecurityConfig = None,
    websocket_path_prefix: str = "/ws",
    debug: bool = False,
) -> ASGIApp:
    """Add WebSocket support to an existing ASGI application."""
    websocket_app = create_websocket_asgi_app(
        router=router,
        connection_manager=connection_manager,
        security_config=security_config,
        debug=debug,
    )

    return WebSocketMiddleware(
        app=app,
        websocket_app=websocket_app,
        websocket_path_prefix=websocket_path_prefix,
    )


# Integration with CovetPy framework
def integrate_with_covet_app(covet_app, websocket_config: Dict[str, Any] = None):
    """
    Integrate WebSocket functionality with a CovetPy application.

    Args:
        covet_app: The CovetPy application instance
        websocket_config: Configuration dictionary for WebSocket
    """
    config = websocket_config or {}

    # Create WebSocket components
    router = WebSocketRouter()
    connection_manager = WebSocketConnectionManager(
        max_connections=config.get("max_connections", 1000)
    )

    # Security configuration
    security_config = None
    if config.get("security"):
        security_config = SecurityConfig(**config["security"])

    # Create WebSocket ASGI app
    websocket_app = create_websocket_asgi_app(
        router=router,
        connection_manager=connection_manager,
        security_config=security_config,
        debug=config.get("debug", False),
    )

    # Add WebSocket routes from config
    if "routes" in config:
        for route_config in config["routes"]:
            path = route_config["path"]
            handler = route_config["handler"]
            middleware = route_config.get("middleware", [])
            router.add_route(path, handler, middleware)

    # Store WebSocket components on the app
    covet_app.websocket_router = router
    covet_app.websocket_connection_manager = connection_manager
    covet_app.websocket_app = websocket_app

    # Add WebSocket middleware to the app
    original_asgi = covet_app.asgi_app if hasattr(covet_app, "asgi_app") else covet_app
    covet_app.asgi_app = add_websocket_to_asgi_app(
        original_asgi,
        router=router,
        connection_manager=connection_manager,
        security_config=security_config,
        websocket_path_prefix=config.get("path_prefix", "/ws"),
        debug=config.get("debug", False),
    )

    # Add convenience methods to the app
    def websocket_route(path: str, **kwargs):
        """Decorator for WebSocket routes."""
        return router.websocket(path, **kwargs)

    def add_websocket_route(path: str, handler, **kwargs):
        """Add WebSocket route."""
        router.add_route(path, handler, **kwargs)

    async def broadcast_to_room(room: str, message):
        """Broadcast to room."""
        from .connection import send_to_room

        return await send_to_room(room, message, connection_manager)

    async def broadcast_to_user(user_id: str, message):
        """Broadcast to user."""
        from .connection import send_to_user

        return await send_to_user(user_id, message, connection_manager)

    async def broadcast_to_all(message):
        """Broadcast to all."""
        from .connection import send_to_all

        return await send_to_all(message, connection_manager)

    # Attach methods to app
    covet_app.websocket = websocket_route
    covet_app.add_websocket_route = add_websocket_route
    covet_app.broadcast_to_room = broadcast_to_room
    covet_app.broadcast_to_user = broadcast_to_user
    covet_app.broadcast_to_all = broadcast_to_all

    logger.info("WebSocket support integrated with CovetPy application")

    return covet_app


# Utility functions for CovetPy integration
def setup_websocket_monitoring(app, monitor_path: str = "/ws/monitor"):
    """Set up WebSocket monitoring endpoint."""
    from .routing import WebSocketEndpoint, on_connect, on_json

    class MonitoringEndpoint(WebSocketEndpoint):
        @on_connect
        async def handle_connect(self, connection):
            await connection.accept()

            # Send initial stats
            stats = app.websocket_connection_manager.get_statistics()
            await connection.send_json({"type": "stats", "data": stats})

        @on_json
        async def handle_json(self, connection, message):
            data = message.data

            if data.get("type") == "get_stats":
                stats = app.websocket_connection_manager.get_statistics()
                await connection.send_json({"type": "stats", "data": stats})
            elif data.get("type") == "get_connections":
                connections = []
                for conn in app.websocket_connection_manager._connections.values():
                    connections.append(conn.get_stats())

                await connection.send_json({"type": "connections", "data": connections})

    app.add_websocket_route(monitor_path, MonitoringEndpoint())
    logger.info(f"WebSocket monitoring endpoint added at {monitor_path}")


def setup_websocket_health_check(app, health_path: str = "/ws/health"):
    """Set up WebSocket health check endpoint."""
    from .routing import WebSocketEndpoint, on_connect

    class HealthCheckEndpoint(WebSocketEndpoint):
        @on_connect
        async def handle_connect(self, connection):
            await connection.accept()

            # Send health status
            stats = app.websocket_connection_manager.get_statistics()
            health_status = {
                "status": "healthy",
                "timestamp": time.time(),
                "connections": stats["current_connections"],
                "uptime": time.time() - getattr(app, "_start_time", time.time()),
            }

            await connection.send_json(health_status)
            await connection.close()

    app.add_websocket_route(health_path, HealthCheckEndpoint())
    logger.info(f"WebSocket health check endpoint added at {health_path}")


# Background tasks for WebSocket management
async def websocket_cleanup_task(
    connection_manager: WebSocketConnectionManager, interval: int = 300
):
    """Background task to clean up stale connections."""
    while True:
        try:
            await asyncio.sleep(interval)

            # Check for stale connections
            current_time = time.time()
            stale_connections = []

            for connection in connection_manager._connections.values():
                if current_time - connection.info.last_activity > 600:  # 10 minutes
                    stale_connections.append(connection)

            # Close stale connections
            for connection in stale_connections:
                try:
                    await connection.close(CloseCode.GOING_AWAY, "Stale connection")
                except Exception as e:
                    logger.debug(f"Error closing stale connection {connection.id}: {e}")

            if stale_connections:
                logger.info(f"Cleaned up {len(stale_connections)} stale connections")

        except Exception as e:
            logger.error(f"Error in WebSocket cleanup task: {e}")


async def websocket_stats_task(connection_manager: WebSocketConnectionManager, interval: int = 60):
    """Background task to log WebSocket statistics."""
    while True:
        try:
            await asyncio.sleep(interval)

            stats = connection_manager.get_statistics()
            logger.info(
                f"WebSocket Stats: {stats['current_connections']} active, "
                f"{stats['total_messages_sent']} sent, "
                f"{stats['total_messages_received']} received"
            )

        except Exception as e:
            logger.error(f"Error in WebSocket stats task: {e}")
