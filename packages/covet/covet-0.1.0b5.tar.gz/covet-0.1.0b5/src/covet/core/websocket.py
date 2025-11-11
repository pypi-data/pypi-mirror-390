"""
CovetPy WebSocket Integration Module

This module provides a unified interface for CovetPy's production-grade WebSocket
implementation, integrating all components into a cohesive API.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional, Union

from covet.core.websocket_client import (
    ClientConfig,
    WebSocketClient,
    WebSocketClientPool,
    websocket_client,
)
from covet.core.websocket_connection import (
    ConnectionInfo,
    WebSocketConnection,
    WebSocketConnectionManager,
    default_connection_manager,
)

# Import core WebSocket components
from covet.core.websocket_impl import (
    BinaryMessage,
    CloseCode,
    ConnectionClosed,
    JSONMessage,
    OpCode,
    ProtocolError,
    TextMessage,
    WebSocketError,
    WebSocketFrame,
    WebSocketHandshake,
    WebSocketMessage,
    WebSocketProtocol,
    WebSocketState,
)
from covet.core.websocket_router import (
    WebSocketEndpoint,
    WebSocketRoute,
    WebSocketRouter,
    on_binary,
    on_connect,
    on_disconnect,
    on_json,
    on_message,
    on_text,
    websocket_handler,
)
from covet.core.websocket_security import (
    RateLimiter,
    SecurityConfig,
    TokenValidator,
    WebSocketSecurity,
    authentication_middleware,
    security_middleware,
)

logger = logging.getLogger(__name__)


class CovetWebSocket:
    """
    Main WebSocket class that integrates all WebSocket functionality.

    This class provides a high-level interface for WebSocket operations
    in CovetPy applications, combining server and client capabilities.
    """

    def __init__(
        self,
        security_config: Optional[SecurityConfig] = None,
        max_connections: int = 1000,
    ):
        # Core components
        self.connection_manager = WebSocketConnectionManager(max_connections=max_connections)
        self.router = WebSocketRouter(connection_manager=self.connection_manager)
        self.security = WebSocketSecurity(security_config) if security_config else None

        # Configuration
        self.max_connections = max_connections
        self.debug = False

        # Statistics
        self.start_time = asyncio.get_event_loop().time()
        self.total_connections = 0
        self.total_messages = 0

        logger.info("CovetWebSocket initialized")

    def websocket(self, path: str, **kwargs):
        """
        Decorator for WebSocket route handlers.

        Usage:
            @websocket.websocket("/ws")
            async def my_handler(websocket):
                await websocket.accept()
                # Handle WebSocket connection
        """
        return self.router.websocket(path, **kwargs)

    def add_route(self, path: str, handler: Callable, **kwargs):
        """Add a WebSocket route programmatically."""
        self.router.add_route(path, handler, **kwargs)

    def add_middleware(self, middleware: Callable):
        """Add WebSocket middleware."""
        self.router.add_middleware(middleware)

    async def handle_websocket(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """Handle incoming WebSocket connection."""
        await self.router.handle_websocket(scope, receive, send)

    def create_client(self, url: str, config: Optional[ClientConfig] = None) -> WebSocketClient:
        """Create a WebSocket client."""
        return WebSocketClient(url, config or ClientConfig())

    def create_client_pool(
        self, urls: List[str], config: Optional[ClientConfig] = None
    ) -> WebSocketClientPool:
        """Create a WebSocket client pool."""
        return WebSocketClientPool(urls, config or ClientConfig())

    async def broadcast_to_room(self, room: str, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections in a room."""
        if isinstance(message, str):
            ws_message = TextMessage(content=message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(data=message)
        else:
            ws_message = JSONMessage(data=message)

        return await self.connection_manager.broadcast_to_room(room, ws_message)

    async def broadcast_to_user(self, user_id: str, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections of a user."""
        if isinstance(message, str):
            ws_message = TextMessage(content=message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(data=message)
        else:
            ws_message = JSONMessage(data=message)

        return await self.connection_manager.broadcast_to_user(user_id, ws_message)

    async def broadcast_to_all(self, message: Union[str, bytes, dict]) -> int:
        """Broadcast message to all connections."""
        if isinstance(message, str):
            ws_message = TextMessage(content=message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(data=message)
        else:
            ws_message = JSONMessage(data=message)

        return await self.connection_manager.broadcast_to_all(ws_message)

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection by ID."""
        return self.connection_manager.get_connection(connection_id)

    def get_user_connections(self, user_id: str) -> List[WebSocketConnection]:
        """Get all connections for a user."""
        return list(self.connection_manager.get_user_connections(user_id))

    def get_room_connections(self, room: str) -> List[WebSocketConnection]:
        """Get all connections in a room."""
        return list(self.connection_manager.get_room_connections(room))

    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket statistics."""
        manager_stats = self.connection_manager.get_statistics()

        uptime = asyncio.get_event_loop().time() - self.start_time

        return {
            **manager_stats,
            "uptime_seconds": uptime,
            "router_routes": len(self.router.routes),
            "router_middleware": len(self.router.middleware),
            "security_enabled": self.security is not None,
        }

    async def close_all_connections(
        self, code: int = CloseCode.GOING_AWAY, reason: str = "Server shutdown"
    ):
        """Close all WebSocket connections."""
        await self.connection_manager.close_all_connections(code, reason)


# Global WebSocket instance
websocket = CovetWebSocket()


# Convenience functions
def create_websocket_app(
    security_config: Optional[SecurityConfig] = None,
    max_connections: int = 1000,
    debug: bool = False,
) -> CovetWebSocket:
    """Create a new WebSocket application."""
    app = CovetWebSocket(security_config=security_config, max_connections=max_connections)
    app.debug = debug
    return app


async def send_to_room(room: str, message: Union[str, bytes, dict]) -> int:
    """Send message to all connections in a room using global instance."""
    return await websocket.broadcast_to_room(room, message)


async def send_to_user(user_id: str, message: Union[str, bytes, dict]) -> int:
    """Send message to all connections of a user using global instance."""
    return await websocket.broadcast_to_user(user_id, message)


async def send_to_all(message: Union[str, bytes, dict]) -> int:
    """Send message to all connections using global instance."""
    return await websocket.broadcast_to_all(message)


# ASGI integration
async def websocket_asgi_handler(scope: Dict[str, Any], receive: Callable, send: Callable):
    """ASGI handler for WebSocket connections."""
    if scope["type"] == "websocket":
        await websocket.handle_websocket(scope, receive, send)
    else:
        # Not a WebSocket request
        await send(
            {
                "type": "http.response.start",
                "status": 404,
                "headers": [[b"content-type", b"text/plain"]],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": b"WebSocket endpoint only",
            }
        )


# Integration with CovetPy ASGI app
def integrate_websocket_with_asgi(asgi_app):
    """
    Integrate WebSocket handling with an existing ASGI application.

    This function modifies the ASGI app to handle WebSocket connections
    alongside HTTP requests.
    """
    original_handler = asgi_app

    async def combined_handler(scope: Dict[str, Any], receive: Callable, send: Callable):
        if scope["type"] == "websocket":
            await websocket.handle_websocket(scope, receive, send)
        else:
            await original_handler(scope, receive, send)

    return combined_handler


# Example endpoint classes
class EchoEndpoint(WebSocketEndpoint):
    """Simple echo WebSocket endpoint."""

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        await connection.accept()
        await connection.send_text("Echo server connected. Send me a message!")

    @on_text
    async def handle_text(self, connection: WebSocketConnection, message: TextMessage):
        await connection.send_text(f"Echo: {message.content}")

    @on_binary
    async def handle_binary(self, connection: WebSocketConnection, message: BinaryMessage):
        await connection.send_bytes(b"Echo: " + message.data)

    @on_json
    async def handle_json(self, connection: WebSocketConnection, message: JSONMessage):
        response = {"echo": message.data, "timestamp": asyncio.get_event_loop().time()}
        await connection.send_json(response)


class BroadcastEndpoint(WebSocketEndpoint):
    """WebSocket endpoint that broadcasts messages to all connected clients."""

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        await connection.accept()
        await connection.join_room("broadcast")
        await self.broadcast_to_room(
            "broadcast",
            {
                "type": "user_joined",
                "message": f"User {connection.info.id} joined the broadcast",
            },
        )

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        await self.broadcast_to_room(
            "broadcast",
            {
                "type": "user_left",
                "message": f"User {connection.info.id} left the broadcast",
            },
        )

    @on_json
    async def handle_json(self, connection: WebSocketConnection, message: JSONMessage):
        # Broadcast the message to all clients in the room
        broadcast_data = {
            "type": "broadcast",
            "from": connection.info.id,
            "data": message.data,
            "timestamp": asyncio.get_event_loop().time(),
        }
        await self.broadcast_to_room("broadcast", broadcast_data)


# Quick setup functions
def setup_echo_server(path: str = "/ws/echo"):
    """Set up a simple echo WebSocket server."""
    websocket.add_route(path, EchoEndpoint())
    logger.info(f"Echo WebSocket server set up at {path}")


def setup_broadcast_server(path: str = "/ws/broadcast"):
    """Set up a broadcast WebSocket server."""
    websocket.add_route(path, BroadcastEndpoint())
    logger.info(f"Broadcast WebSocket server set up at {path}")


def setup_secure_websocket(
    jwt_secret: str,
    allowed_origins: Optional[List[str]] = None,
    max_connections_per_ip: int = 10,
    max_messages_per_minute: int = 60,
):
    """Set up WebSocket with security features."""
    security_config = SecurityConfig(
        require_auth=True,
        jwt_secret=jwt_secret,
        allowed_origins=allowed_origins,
        enable_rate_limiting=True,
        max_connections_per_ip=max_connections_per_ip,
        max_messages_per_minute=max_messages_per_minute,
    )

    websocket.security = WebSocketSecurity(security_config)

    # Add security middleware
    websocket.add_middleware(security_middleware(websocket.security))
    websocket.add_middleware(authentication_middleware(websocket.security))

    logger.info("Secure WebSocket configuration applied")


# Testing utilities
async def test_websocket_connection(url: str, test_message: str = "Hello, WebSocket!") -> bool:
    """Test WebSocket connection to a URL."""
    try:
        async with websocket_client(url) as client:
            # Send test message
            await client.send_text(test_message)

            # Wait for response (simple test)
            await asyncio.sleep(1)

            logger.info(f"WebSocket test successful: {url}")
            return True

    except Exception as e:
        logger.error(f"WebSocket test failed for {url}: {e}")
        return False


async def benchmark_websocket_performance(
    url: str, message_count: int = 1000, concurrent_clients: int = 10
) -> Dict[str, float]:
    """Benchmark WebSocket performance."""

    async def single_client_test(client_id: int):
        try:
            async with websocket_client(url) as client:
                start_time = asyncio.get_event_loop().time()

                for i in range(message_count // concurrent_clients):
                    await client.send_json(
                        {
                            "client_id": client_id,
                            "message_id": i,
                            "data": f"Test message {i} from client {client_id}",
                        }
                    )

                end_time = asyncio.get_event_loop().time()
                return end_time - start_time

        except Exception as e:
            logger.error(f"Client {client_id} benchmark failed: {e}")
            return 0.0

    # Run concurrent clients
    start_time = asyncio.get_event_loop().time()

    tasks = [single_client_test(i) for i in range(concurrent_clients)]
    durations = await asyncio.gather(*tasks, return_exceptions=True)

    total_time = asyncio.get_event_loop().time() - start_time

    # Calculate metrics
    successful_durations = [d for d in durations if isinstance(d, float) and d > 0]

    if successful_durations:
        avg_duration = sum(successful_durations) / len(successful_durations)
        messages_per_second = message_count / total_time

        return {
            "total_time": total_time,
            "average_client_duration": avg_duration,
            "messages_per_second": messages_per_second,
            "successful_clients": len(successful_durations),
            "total_clients": concurrent_clients,
            "total_messages": message_count,
        }
    else:
        return {
            "total_time": total_time,
            "error": "All clients failed",
            "successful_clients": 0,
            "total_clients": concurrent_clients,
        }


# Export all public components
__all__ = [
    # Main classes
    "CovetWebSocket",
    "websocket",
    # Core components
    "WebSocketFrame",
    "WebSocketProtocol",
    "WebSocketHandshake",
    "WebSocketMessage",
    "TextMessage",
    "BinaryMessage",
    "JSONMessage",
    "WebSocketConnection",
    "WebSocketConnectionManager",
    "ConnectionInfo",
    "WebSocketRouter",
    "WebSocketRoute",
    "WebSocketEndpoint",
    "WebSocketSecurity",
    "SecurityConfig",
    "TokenValidator",
    "WebSocketClient",
    "WebSocketClientPool",
    "ClientConfig",
    # Enums and constants
    "OpCode",
    "CloseCode",
    "WebSocketState",
    # Exceptions
    "WebSocketError",
    "ProtocolError",
    "ConnectionClosed",
    # Decorators
    "on_connect",
    "on_disconnect",
    "on_message",
    "on_text",
    "on_binary",
    "on_json",
    "websocket_handler",
    # Utility functions
    "create_websocket_app",
    "send_to_room",
    "send_to_user",
    "send_to_all",
    "websocket_asgi_handler",
    "integrate_websocket_with_asgi",
    "setup_echo_server",
    "setup_broadcast_server",
    "setup_secure_websocket",
    "test_websocket_connection",
    "benchmark_websocket_performance",
    # Example endpoints
    "EchoEndpoint",
    "BroadcastEndpoint",
    # Context managers
    "websocket_client",
    # Middleware
    "security_middleware",
    "authentication_middleware",
]
