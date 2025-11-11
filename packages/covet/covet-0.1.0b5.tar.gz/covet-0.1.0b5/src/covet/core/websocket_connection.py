"""
WebSocket Connection Management and Lifecycle

This module provides high-performance WebSocket connection management
with lifecycle handling, connection pooling, and state tracking.
"""

import asyncio
import logging
import time
import uuid
import weakref
from collections import defaultdict
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .websocket_impl import (
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
)

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """WebSocket connection information."""

    id: str
    remote_addr: str
    user_agent: str
    path: str
    query_params: Dict[str, Any]
    headers: Dict[str, str]
    connect_time: float
    last_ping: Optional[float] = None
    last_pong: Optional[float] = None
    authenticated: bool = False
    user_id: Optional[str] = None
    rooms: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WebSocketConnection:
    """
    High-performance WebSocket connection handler.

    Manages individual WebSocket connections with:
    - Message sending/receiving
    - Heartbeat handling
    - State management
    - Room membership
    - Rate limiting
    """

    def __init__(
        self,
        scope: Dict[str, Any],
        receive: Callable,
        send: Callable,
        connection_manager: "WebSocketConnectionManager",
        max_message_size: int = 1024 * 1024,
        ping_interval: float = 30.0,
        ping_timeout: float = 10.0,
    ):
        self.scope = scope
        self.receive = receive
        self.send = send
        self.connection_manager = connection_manager

        # Connection info
        self.info = ConnectionInfo(
            id=str(uuid.uuid4()),
            remote_addr=f"{scope.get('client', ['unknown', 0])[0]}:{scope.get('client', ['unknown', 0])[1]}",
            user_agent=dict(scope.get("headers", [])).get(b"user-agent", b"").decode("latin-1"),
            path=scope.get("path", "/"),
            query_params=self._parse_query_string(scope.get("query_string", b"")),
            headers=self._parse_headers(scope.get("headers", [])),
            connect_time=time.time(),
        )

        # Protocol handler
        self.protocol = WebSocketProtocol(is_client=False, max_message_size=max_message_size)
        self.state = WebSocketState.CONNECTING

        # Message queues
        self._send_queue: asyncio.Queue = asyncio.Queue()
        self._message_handlers: Dict[str, Callable] = {}

        # Heartbeat
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self._ping_task: Optional[asyncio.Task] = None
        self._pong_waiter: Optional[asyncio.Future] = None

        # Rate limiting
        self._message_count = 0
        self._message_window_start = time.time()
        self._rate_limit_violations = 0

        # Tasks
        self._tasks: Set[asyncio.Task] = set()

        # Event callbacks
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_message: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

    def _parse_query_string(self, query_string: bytes) -> Dict[str, Any]:
        """Parse query string parameters."""
        if not query_string:
            return {}

        params = {}
        for param in query_string.decode("latin-1").split("&"):
            if "=" in param:
                key, value = param.split("=", 1)
                params[key] = value
            else:
                params[param] = ""

        return params

    def _parse_headers(self, headers: List[List[bytes]]) -> Dict[str, str]:
        """Parse HTTP headers."""
        return {name.decode("latin-1").lower(): value.decode("latin-1") for name, value in headers}

    async def accept(self, subprotocol: Optional[str] = None) -> None:
        """Accept the WebSocket connection."""
        if self.state != WebSocketState.CONNECTING:
            raise WebSocketError("Connection not in connecting state")

        # Send WebSocket accept response
        response = {"type": "websocket.accept"}
        if subprotocol:
            response["subprotocol"] = subprotocol

        await self.send(response)

        self.state = WebSocketState.OPEN
        self.protocol.state = WebSocketState.OPEN

        # Register with connection manager
        self.connection_manager.register_connection(self)

        # Start background tasks
        self._start_tasks()

        # Call connect callback
        if self.on_connect:
            try:
                await self.on_connect(self)
            except Exception as e:
                logger.error(f"Error in on_connect callback: {e}", exc_info=True)

        logger.info(f"WebSocket connection accepted: {self.info.id} from {self.info.remote_addr}")

    async def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = "") -> None:
        """Close the WebSocket connection."""
        if self.state == WebSocketState.CLOSED:
            return

        if self.state == WebSocketState.OPEN:
            self.state = WebSocketState.CLOSING

            # Send close frame
            try:
                close_frame = self.protocol.create_close_frame(code, reason)
                frame_data = self.protocol.send_frame(close_frame)
                await self.send({"type": "websocket.send", "bytes": frame_data})
            except Exception as e:
                logger.warning(f"Error sending close frame: {e}")

        # Close ASGI connection
        try:
            await self.send({"type": "websocket.close", "code": code})
        except Exception as e:
            logger.warning(f"Error closing ASGI connection: {e}")

        self.state = WebSocketState.CLOSED
        self.protocol.state = WebSocketState.CLOSED

        # Clean up
        await self._cleanup()

        logger.info(f"WebSocket connection closed: {self.info.id} (code={code}, reason='{reason}')")

    async def send_text(self, data: str) -> None:
        """Send text message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed()

        message = TextMessage(content=data)
        await self._send_message(message)

    async def send_bytes(self, data: bytes) -> None:
        """Send binary message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed()

        message = BinaryMessage(data=data)
        await self._send_message(message)

    async def send_json(self, data: Any) -> None:
        """Send JSON message."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed()

        message = JSONMessage(data=data)
        await self._send_message(message)

    async def ping(self, data: bytes = b"") -> None:
        """Send ping frame."""
        if self.state != WebSocketState.OPEN:
            raise ConnectionClosed()

        ping_frame = self.protocol.create_ping_frame(data)
        frame_data = self.protocol.send_frame(ping_frame)

        await self.send({"type": "websocket.send", "bytes": frame_data})

        self.info.last_ping = time.time()

    async def _send_message(self, message: WebSocketMessage) -> None:
        """Send a WebSocket message."""
        # Check rate limits
        if not self._check_rate_limit():
            logger.warning(f"Rate limit exceeded for connection {self.info.id}")
            await self.close(CloseCode.POLICY_VIOLATION, "Rate limit exceeded")
            return

        frame = message.to_frame(mask=False)
        frame_data = self.protocol.send_frame(frame)

        await self.send({"type": "websocket.send", "bytes": frame_data})

    def _check_rate_limit(self, max_messages: int = 100, window_seconds: int = 60) -> bool:
        """Check if connection is within rate limits."""
        now = time.time()

        # Reset window if needed
        if now - self._message_window_start > window_seconds:
            self._message_count = 0
            self._message_window_start = now

        self._message_count += 1

        if self._message_count > max_messages:
            self._rate_limit_violations += 1
            return False

        return True

    def _start_tasks(self) -> None:
        """Start background tasks."""
        # Message processing task
        task = asyncio.create_task(self._message_handler())
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

        # Ping task
        if self.ping_interval > 0:
            self._ping_task = asyncio.create_task(self._ping_handler())
            self._tasks.add(self._ping_task)
            self._ping_task.add_done_callback(self._tasks.discard)

    async def _message_handler(self) -> None:
        """Handle incoming messages."""
        try:
            while self.state == WebSocketState.OPEN:
                # Receive message from ASGI
                try:
                    message = await self.receive()
                except Exception as e:
                    logger.error(f"Error receiving message: {e}")
                    break

                if message["type"] == "websocket.receive":
                    await self._handle_receive(message)
                elif message["type"] == "websocket.disconnect":
                    code = message.get("code", CloseCode.NORMAL_CLOSURE)
                    await self.close(code)
                    break

        except Exception as e:
            logger.error(f"Error in message handler: {e}", exc_info=True)
            await self.close(CloseCode.INTERNAL_ERROR, "Internal error")

        finally:
            await self._cleanup()

    async def _handle_receive(self, message: Dict[str, Any]) -> None:
        """Handle received WebSocket message."""
        try:
            # Get raw data
            if "bytes" in message:
                data = message["bytes"]
            elif "text" in message:
                data = message["text"].encode("utf-8")
            else:
                logger.warning("Received message without data")
                return

            # Parse frames
            frames = self.protocol.parse_frames(data)

            for frame in frames:
                await self._handle_frame(frame)

        except ProtocolError as e:
            logger.warning(f"Protocol error: {e}")
            await self.close(CloseCode.PROTOCOL_ERROR, str(e))
        except Exception as e:
            logger.error(f"Error handling receive: {e}", exc_info=True)
            await self.close(CloseCode.INTERNAL_ERROR, "Internal error")

    async def _handle_frame(self, frame: WebSocketFrame) -> None:
        """Handle a WebSocket frame."""
        if frame.opcode == OpCode.PING:
            # Respond with pong
            pong_frame = self.protocol.create_pong_frame(frame.payload)
            frame_data = self.protocol.send_frame(pong_frame)
            await self.send({"type": "websocket.send", "bytes": frame_data})

        elif frame.opcode == OpCode.PONG:
            # Handle pong response
            self.info.last_pong = time.time()
            if self._pong_waiter and not self._pong_waiter.done():
                self._pong_waiter.set_result(frame.payload)

        elif frame.opcode == OpCode.CLOSE:
            # Handle close frame
            if len(frame.payload) >= 2:
                code = int.from_bytes(frame.payload[:2], "big")
                reason = frame.payload[2:].decode("utf-8", errors="ignore")
            else:
                code = CloseCode.NORMAL_CLOSURE
                reason = ""

            await self.close(code, reason)

        else:
            # Data frame - assemble message
            message = self.protocol.assemble_message(frame)
            if message:
                await self._handle_message(message)

    async def _handle_message(self, message: WebSocketMessage) -> None:
        """Handle complete WebSocket message."""
        try:
            # Call message callback
            if self.on_message:
                await self.on_message(self, message)

            # Call specific message handlers
            handler = self._message_handlers.get(message.message_type)
            if handler:
                await handler(self, message)

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            if self.on_error:
                try:
                    await self.on_error(self, e)
                except Exception:
                    # TODO: Add proper exception handling

                    pass

    async def _ping_handler(self) -> None:
        """Handle periodic ping/pong for keepalive."""
        while self.state == WebSocketState.OPEN:
            try:
                await asyncio.sleep(self.ping_interval)

                if self.state != WebSocketState.OPEN:
                    break

                # Send ping
                ping_data = str(int(time.time())).encode()
                await self.ping(ping_data)

                # Wait for pong
                self._pong_waiter = asyncio.Future()
                try:
                    await asyncio.wait_for(self._pong_waiter, timeout=self.ping_timeout)
                except asyncio.TimeoutError:
                    logger.warning(f"Ping timeout for connection {self.info.id}")
                    await self.close(CloseCode.POLICY_VIOLATION, "Ping timeout")
                    break

            except Exception as e:
                logger.error(f"Error in ping handler: {e}", exc_info=True)
                break

    async def _cleanup(self) -> None:
        """Clean up connection resources."""
        # Cancel all tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

        # Unregister from connection manager
        self.connection_manager.unregister_connection(self)

        # Leave all rooms
        for room in list(self.info.rooms):
            self.connection_manager.leave_room(self, room)

        # Call disconnect callback
        if self.on_disconnect:
            try:
                await self.on_disconnect(self)
            except Exception as e:
                logger.error(f"Error in on_disconnect callback: {e}", exc_info=True)

    def join_room(self, room: str) -> None:
        """Join a room."""
        self.info.rooms.add(room)
        self.connection_manager.join_room(self, room)

    def leave_room(self, room: str) -> None:
        """Leave a room."""
        self.info.rooms.discard(room)
        self.connection_manager.leave_room(self, room)

    def set_message_handler(self, message_type: str, handler: Callable) -> None:
        """Set handler for specific message type."""
        self._message_handlers[message_type] = handler

    def authenticate(self, user_id: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Authenticate the connection."""
        self.info.authenticated = True
        self.info.user_id = user_id
        if metadata:
            self.info.metadata.update(metadata)

    def __repr__(self) -> str:
        return f"WebSocketConnection(id={self.info.id}, state={self.state}, addr={self.info.remote_addr})"


class WebSocketConnectionManager:
    """
    Manages multiple WebSocket connections.

    Provides:
    - Connection registration and lifecycle
    - Room-based broadcasting
    - Connection pooling and limits
    - Statistics and monitoring
    """

    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections

        # Connection storage
        self._connections: Dict[str, WebSocketConnection] = {}
        self._connections_by_user: Dict[str, Set[WebSocketConnection]] = defaultdict(set)
        self._rooms: Dict[str, Set[WebSocketConnection]] = defaultdict(set)

        # Statistics
        self.total_connections = 0
        self.total_messages = 0
        self.start_time = time.time()

        # Weak references to avoid circular references
        self._weak_connections: weakref.WeakSet = weakref.WeakSet()

    def register_connection(self, connection: WebSocketConnection) -> None:
        """Register a new connection."""
        if len(self._connections) >= self.max_connections:
            raise WebSocketError("Maximum connections exceeded")

        self._connections[connection.info.id] = connection
        self._weak_connections.add(connection)

        if connection.info.user_id:
            self._connections_by_user[connection.info.user_id].add(connection)

        self.total_connections += 1

        logger.info(
            f"Connection registered: {connection.info.id} (total: {len(self._connections)})"
        )

    def unregister_connection(self, connection: WebSocketConnection) -> None:
        """Unregister a connection."""
        self._connections.pop(connection.info.id, None)

        if connection.info.user_id:
            self._connections_by_user[connection.info.user_id].discard(connection)
            if not self._connections_by_user[connection.info.user_id]:
                del self._connections_by_user[connection.info.user_id]

        # Remove from all rooms
        for room_connections in self._rooms.values():
            room_connections.discard(connection)

        logger.info(
            f"Connection unregistered: {connection.info.id} (total: {len(self._connections)})"
        )

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection by ID."""
        return self._connections.get(connection_id)

    def get_user_connections(self, user_id: str) -> Set[WebSocketConnection]:
        """Get all connections for a user."""
        return self._connections_by_user.get(user_id, set()).copy()

    def join_room(self, connection: WebSocketConnection, room: str) -> None:
        """Add connection to a room."""
        self._rooms[room].add(connection)
        logger.debug(f"Connection {connection.info.id} joined room '{room}'")

    def leave_room(self, connection: WebSocketConnection, room: str) -> None:
        """Remove connection from a room."""
        self._rooms[room].discard(connection)
        if not self._rooms[room]:
            del self._rooms[room]
        logger.debug(f"Connection {connection.info.id} left room '{room}'")

    def get_room_connections(self, room: str) -> Set[WebSocketConnection]:
        """Get all connections in a room."""
        return self._rooms.get(room, set()).copy()

    async def broadcast_to_room(self, room: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections in a room."""
        connections = self.get_room_connections(room)

        if not connections:
            return 0

        # Send to all connections concurrently
        tasks = []
        for conn in connections:
            if conn.state == WebSocketState.OPEN:
                if isinstance(message, TextMessage):
                    tasks.append(conn.send_text(message.content))
                elif isinstance(message, BinaryMessage):
                    tasks.append(conn.send_bytes(message.data))
                elif isinstance(message, JSONMessage):
                    tasks.append(conn.send_json(message.data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.total_messages += len(tasks)

        logger.debug(f"Broadcast to room '{room}': {len(tasks)} messages sent")
        return len(tasks)

    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections of a user."""
        connections = self.get_user_connections(user_id)

        if not connections:
            return 0

        # Send to all connections concurrently
        tasks = []
        for conn in connections:
            if conn.state == WebSocketState.OPEN:
                if isinstance(message, TextMessage):
                    tasks.append(conn.send_text(message.content))
                elif isinstance(message, BinaryMessage):
                    tasks.append(conn.send_bytes(message.data))
                elif isinstance(message, JSONMessage):
                    tasks.append(conn.send_json(message.data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.total_messages += len(tasks)

        logger.debug(f"Broadcast to user '{user_id}': {len(tasks)} messages sent")
        return len(tasks)

    async def broadcast_to_all(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connections."""
        connections = list(self._connections.values())

        if not connections:
            return 0

        # Send to all connections concurrently
        tasks = []
        for conn in connections:
            if conn.state == WebSocketState.OPEN:
                if isinstance(message, TextMessage):
                    tasks.append(conn.send_text(message.content))
                elif isinstance(message, BinaryMessage):
                    tasks.append(conn.send_bytes(message.data))
                elif isinstance(message, JSONMessage):
                    tasks.append(conn.send_json(message.data))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self.total_messages += len(tasks)

        logger.debug(f"Broadcast to all: {len(tasks)} messages sent")
        return len(tasks)

    def get_statistics(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        now = time.time()
        uptime = now - self.start_time

        return {
            "active_connections": len(self._connections),
            "total_connections": self.total_connections,
            "total_messages": self.total_messages,
            "rooms": len(self._rooms),
            "authenticated_users": len(self._connections_by_user),
            "uptime_seconds": uptime,
            "messages_per_second": self.total_messages / uptime if uptime > 0 else 0,
        }

    async def close_all_connections(
        self, code: int = CloseCode.GOING_AWAY, reason: str = "Server shutdown"
    ) -> None:
        """Close all connections."""
        connections = list(self._connections.values())

        if connections:
            tasks = [conn.close(code, reason) for conn in connections]
            await asyncio.gather(*tasks, return_exceptions=True)

        logger.info(f"Closed {len(connections)} connections")

    def __len__(self) -> int:
        return len(self._connections)

    def __contains__(self, connection_id: str) -> bool:
        return connection_id in self._connections


# Global connection manager instance
default_connection_manager = WebSocketConnectionManager()


# Export main components
__all__ = [
    "ConnectionInfo",
    "WebSocketConnection",
    "WebSocketConnectionManager",
    "default_connection_manager",
]
