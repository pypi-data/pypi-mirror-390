"""
CovetPy WebSocket Framework

A complete, production-ready WebSocket implementation for CovetPy that provides:
- RFC 6455 compliant WebSocket protocol
- Advanced connection management with rooms/channels
- Comprehensive routing system with decorators
- Auto-reconnecting client with connection pooling
- Security features including authentication and rate limiting
- Full ASGI integration
- Real-time broadcasting and messaging
- Performance monitoring and statistics

This module exports all the components needed to build robust WebSocket applications.
"""

import logging

# ASGI integration
from .asgi import (
    ASGIWebSocketAdapter,
    WebSocketASGI,
    WebSocketMiddleware,
    add_websocket_to_asgi_app,
    create_websocket_asgi_app,
    integrate_with_covet_app,
    setup_websocket_health_check,
    setup_websocket_monitoring,
    websocket_cleanup_task,
    websocket_stats_task,
)

# Client implementation
from .client import (
    ClientConfig,
    ClientState,
    WebSocketClient,
    WebSocketClientPool,
    ping_server,
    test_connection,
    websocket_client,
    websocket_client_pool,
)
from .connection import (
    ConnectionInfo,
    WebSocketConnection,
    WebSocketConnectionManager,
    connection_context,
    default_connection_manager,
    send_to_all,
    send_to_room,
    send_to_user,
)

# Core protocol and connection management
from .protocol import (
    BinaryMessage,
    CloseCode,
    ConnectionClosed,
    JSONMessage,
    OpCode,
    ProtocolError,
    TextMessage,
    WebSocketError,
    WebSocketFrame,
    WebSocketMessage,
    WebSocketProtocol,
    WebSocketState,
    create_message_from_frame,
)

# Routing and endpoint system
from .routing import (
    ASGIWebSocket,
    ChatEndpoint,
    EchoEndpoint,
    WebSocketEndpoint,
    WebSocketRoute,
    WebSocketRouter,
    auth_middleware,
    cors_middleware,
    create_router,
    default_router,
    on_binary,
    on_connect,
    on_disconnect,
    on_error,
    on_json,
    on_message,
    on_text,
    rate_limit_middleware,
    setup_chat_endpoint,
    setup_echo_endpoint,
    websocket_handler,
)

# Security and authentication
from .security import (
    APIKeyValidator,
    AuthMethod,
    GeolocationPolicy,
    IPWhitelistPolicy,
    JWTValidator,
    RateLimiter,
    SecurityConfig,
    SecurityPolicy,
    SecurityViolation,
    TimeBasedPolicy,
    WebSocketSecurity,
    authentication_middleware,
    generate_api_key,
    hash_api_key,
    message_validation_middleware,
    security_middleware,
    verify_api_key,
)

logger = logging.getLogger(__name__)


class CovetWebSocket:
    """
    Main WebSocket framework class that provides a high-level interface
    for all WebSocket functionality in CovetPy.

    This class integrates all components and provides convenience methods
    for common WebSocket operations.
    """

    def __init__(
        self,
        max_connections: int = 1000,
        security_config: SecurityConfig = None,
        debug: bool = False,
    ):
        # Core components
        self.connection_manager = WebSocketConnectionManager(max_connections=max_connections)
        self.router = WebSocketRouter(connection_manager=self.connection_manager)
        self.security = WebSocketSecurity(security_config) if security_config else None

        # ASGI app
        self.asgi_app = WebSocketASGI(
            router=self.router,
            connection_manager=self.connection_manager,
            security=self.security,
            debug=debug,
        )

        # Configuration
        self.debug = debug
        self.max_connections = max_connections

        logger.info(f"CovetWebSocket initialized (max_connections={max_connections})")

    def websocket(self, path: str, **kwargs):
        """Decorator for WebSocket route handlers."""
        return self.router.websocket(path, **kwargs)

    def add_route(self, path: str, handler, **kwargs):
        """Add a WebSocket route."""
        self.router.add_route(path, handler, **kwargs)

    def add_middleware(self, middleware):
        """Add middleware."""
        self.router.add_middleware(middleware)

    async def broadcast_to_room(self, room: str, message):
        """Broadcast message to all connections in a room."""
        return await send_to_room(room, message, self.connection_manager)

    async def broadcast_to_user(self, user_id: str, message):
        """Broadcast message to all connections of a user."""
        return await send_to_user(user_id, message, self.connection_manager)

    async def broadcast_to_all(self, message):
        """Broadcast message to all connections."""
        return await send_to_all(message, self.connection_manager)

    def get_connection(self, connection_id: str):
        """Get connection by ID."""
        return self.connection_manager.get_connection(connection_id)

    def get_user_connections(self, user_id: str):
        """Get all connections for a user."""
        return list(self.connection_manager.get_user_connections(user_id))

    def get_room_connections(self, room: str):
        """Get all connections in a room."""
        return list(self.connection_manager.get_room_connections(room))

    def get_statistics(self):
        """Get comprehensive statistics."""
        return self.asgi_app.get_stats()

    def create_client(self, url: str, config: ClientConfig = None):
        """Create a WebSocket client."""
        return WebSocketClient(url, config or ClientConfig())

    def create_client_pool(self, urls: list, config: ClientConfig = None):
        """Create a WebSocket client pool."""
        return WebSocketClientPool(urls, config or ClientConfig())

    def setup_echo_server(self, path: str = "/ws/echo"):
        """Set up echo server endpoint."""
        setup_echo_endpoint(self.router, path)

    def setup_chat_server(self, path: str = "/ws/chat"):
        """Set up chat server endpoint."""
        setup_chat_endpoint(self.router, path)

    def setup_monitoring(self, path: str = "/ws/monitor"):
        """Set up monitoring endpoint."""
        setup_websocket_monitoring(self, path)

    def setup_health_check(self, path: str = "/ws/health"):
        """Set up health check endpoint."""
        setup_websocket_health_check(self, path)

    async def close_all_connections(
        self, code: int = CloseCode.GOING_AWAY, reason: str = "Server shutdown"
    ):
        """Close all connections."""
        await self.connection_manager.close_all_connections(code, reason)


# Global WebSocket instance for convenience
websocket = CovetWebSocket()


# Legacy compatibility
class WebSocketManager:
    """Legacy WebSocket manager for backward compatibility."""

    def __init__(self):
        self.connections = []
        logger.warning("WebSocketManager is deprecated. Use CovetWebSocket instead.")

    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    async def broadcast(self, message: str):
        """Broadcast message to all connections."""
        await websocket.broadcast_to_all(message)


# Legacy instance
websocket_manager = WebSocketManager()


# Convenience functions
def create_websocket_app(
    max_connections: int = 1000,
    security_config: SecurityConfig = None,
    debug: bool = False,
) -> CovetWebSocket:
    """Create a new WebSocket application."""
    return CovetWebSocket(
        max_connections=max_connections, security_config=security_config, debug=debug
    )


async def quick_echo_server(host: str = "localhost", port: int = 8000, path: str = "/ws/echo"):
    """Quick echo server for testing."""
    app = create_websocket_app(debug=True)
    app.setup_echo_server(path)

    try:
        import uvicorn

        uvicorn.run(app.asgi_app, host=host, port=port)
    except ImportError:
        logger.error("uvicorn is required for quick_echo_server. Install with: pip install uvicorn")


async def quick_chat_server(host: str = "localhost", port: int = 8000, path: str = "/ws/chat"):
    """Quick chat server for testing."""
    app = create_websocket_app(debug=True)
    app.setup_chat_server(path)

    try:
        import uvicorn

        uvicorn.run(app.asgi_app, host=host, port=port)
    except ImportError:
        logger.error("uvicorn is required for quick_chat_server. Install with: pip install uvicorn")


# Export all public components
__all__ = [
    "WebSocketServer",
    # Main classes
    "CovetWebSocket",
    "websocket",
    "WebSocketManager",
    "websocket_manager",
    # Protocol components
    "WebSocketProtocol",
    "WebSocketFrame",
    "WebSocketMessage",
    "TextMessage",
    "BinaryMessage",
    "JSONMessage",
    "OpCode",
    "CloseCode",
    "WebSocketState",
    "WebSocketError",
    "ProtocolError",
    "ConnectionClosed",
    # Connection management
    "WebSocketConnection",
    "WebSocketConnectionManager",
    "ConnectionInfo",
    "default_connection_manager",
    "connection_context",
    "send_to_room",
    "send_to_user",
    "send_to_all",
    # Routing
    "WebSocketRouter",
    "WebSocketRoute",
    "WebSocketEndpoint",
    "default_router",
    "create_router",
    "on_connect",
    "on_disconnect",
    "on_message",
    "on_text",
    "on_binary",
    "on_json",
    "on_error",
    "websocket_handler",
    "cors_middleware",
    "auth_middleware",
    "rate_limit_middleware",
    "EchoEndpoint",
    "ChatEndpoint",
    "setup_echo_endpoint",
    "setup_chat_endpoint",
    # Client
    "WebSocketClient",
    "WebSocketClientPool",
    "ClientConfig",
    "ClientState",
    "websocket_client",
    "websocket_client_pool",
    "test_connection",
    "ping_server",
    # Security
    "WebSocketSecurity",
    "SecurityConfig",
    "SecurityViolation",
    "AuthMethod",
    "RateLimiter",
    "JWTValidator",
    "APIKeyValidator",
    "security_middleware",
    "authentication_middleware",
    "message_validation_middleware",
    "SecurityPolicy",
    "IPWhitelistPolicy",
    "TimeBasedPolicy",
    "GeolocationPolicy",
    "generate_api_key",
    "hash_api_key",
    "verify_api_key",
    # ASGI integration
    "WebSocketASGI",
    "WebSocketMiddleware",
    "ASGIWebSocketAdapter",
    "create_websocket_asgi_app",
    "add_websocket_to_asgi_app",
    "integrate_with_covet_app",
    "setup_websocket_monitoring",
    "setup_websocket_health_check",
    "websocket_cleanup_task",
    "websocket_stats_task",
    # Utility functions
    "create_websocket_app",
    "quick_echo_server",
    "quick_chat_server",
    "create_message_from_frame",
]


class WebSocketServer:
    """WebSocket server implementation."""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.connections = set()
    
    async def start(self):
        """Start the WebSocket server."""
        pass
    
    async def stop(self):
        """Stop the WebSocket server."""
        pass
    
    async def broadcast(self, message):
        """Broadcast message to all connections."""
        for conn in self.connections:
            await conn.send(message)



class WebSocketHandler:
    """WebSocket connection handler."""
    def __init__(self):
        self.connections = []
