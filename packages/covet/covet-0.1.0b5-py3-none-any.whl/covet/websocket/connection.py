"""
WebSocket Connection Management

This module provides comprehensive connection management for WebSocket connections
including individual connections, connection pools, rooms/channels, and broadcasting.
"""

import asyncio
import logging
import time
import weakref
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .protocol import (
    BinaryMessage,
    CloseCode,
    ConnectionClosed,
    JSONMessage,
    OpCode,
    TextMessage,
    WebSocketMessage,
    WebSocketProtocol,
    WebSocketState,
)

logger = logging.getLogger(__name__)


@dataclass
class ConnectionInfo:
    """Information about a WebSocket connection."""

    id: str
    user_id: Optional[str] = None
    ip_address: str = ""
    user_agent: str = ""
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    rooms: Set[str] = field(default_factory=set)


class WebSocketConnection:
    """
    Represents a single WebSocket connection with protocol handling,
    room management, and message queuing.
    """

    def __init__(
        self,
        websocket,
        connection_id: str,
        protocol: WebSocketProtocol,
        info: ConnectionInfo = None,
    ):
        self.websocket = websocket
        self.id = connection_id
        self.protocol = protocol
        self.info = info or ConnectionInfo(id=connection_id)

        # Connection state
        self.is_connected = True
        self.is_authenticated = False

        # Message handling
        self._send_queue = asyncio.Queue(maxsize=1000)
        self._receive_buffer = bytearray()
        self._send_task: Optional[asyncio.Task] = None
        self._heartbeat_task: Optional[asyncio.Task] = None

        # Event handlers
        self.on_message: Optional[Callable] = None
        self.on_close: Optional[Callable] = None
        self.on_error: Optional[Callable] = None

        # Statistics
        self.messages_sent = 0
        self.messages_received = 0
        self.last_ping_time: Optional[float] = None
        self.ping_interval = 30.0  # seconds
        self.ping_timeout = 10.0  # seconds

        # Start background tasks
        self._start_background_tasks()

        logger.debug(f"WebSocket connection {self.id} created")

    def _start_background_tasks(self):
        """Start background tasks for message sending and heartbeat."""
        self._send_task = asyncio.create_task(self._send_worker())
        self._heartbeat_task = asyncio.create_task(self._heartbeat_worker())

    async def _send_worker(self):
        """Background task to process outgoing messages."""
        try:
            while self.is_connected:
                try:
                    # Get message from queue with timeout
                    message = await asyncio.wait_for(self._send_queue.get(), timeout=1.0)

                    if message is None:  # Shutdown signal
                        break

                    # Send the frame
                    await self.websocket.send_bytes(message)
                    self.messages_sent += 1
                    self.info.last_activity = time.time()

                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in send worker for {self.id}: {e}")
                    break
        except Exception as e:
            logger.error(f"Send worker error for {self.id}: {e}")
        finally:
            logger.debug(f"Send worker stopped for {self.id}")

    async def _heartbeat_worker(self):
        """Background task to handle ping/pong heartbeat."""
        try:
            while self.is_connected:
                try:
                    await asyncio.sleep(self.ping_interval)

                    if not self.is_connected:
                        break

                    # Send ping
                    await self.ping()

                    # Wait for pong
                    await asyncio.sleep(self.ping_timeout)

                    # Check if we got a pong (ping_time would be reset)
                    if (
                        self.last_ping_time
                        and time.time() - self.last_ping_time > self.ping_timeout
                    ):
                        logger.warning(f"Ping timeout for connection {self.id}")
                        await self.close(CloseCode.POLICY_VIOLATION, "Ping timeout")
                        break

                except Exception as e:
                    logger.error(f"Heartbeat error for {self.id}: {e}")
                    break
        except Exception as e:
            logger.error(f"Heartbeat worker error for {self.id}: {e}")

    async def accept(self):
        """Accept the WebSocket connection."""
        await self.websocket.accept()
        self.protocol.state = WebSocketState.OPEN
        logger.info(f"WebSocket connection {self.id} accepted")

    async def send_frame(self, frame_data: bytes):
        """Send raw frame data."""
        if not self.is_connected:
            raise ConnectionClosed(CloseCode.ABNORMAL_CLOSURE, "Connection closed")

        try:
            await self._send_queue.put(frame_data)
        except asyncio.QueueFull:
            logger.warning(f"Send queue full for connection {self.id}")
            raise

    async def send_text(self, text: str):
        """Send text message."""
        frame = self.protocol.create_text_frame(text)
        await self.send_frame(frame)

    async def send_bytes(self, data: bytes):
        """Send binary message."""
        frame = self.protocol.create_binary_frame(data)
        await self.send_frame(frame)

    async def send_json(self, data: Any):
        """Send JSON message."""
        message = JSONMessage(data)
        frame = self.protocol.create_text_frame(message.content)
        await self.send_frame(frame)

    async def send_message(self, message: WebSocketMessage):
        """Send a WebSocket message object."""
        if isinstance(message, TextMessage):
            await self.send_text(message.content)
        elif isinstance(message, BinaryMessage):
            await self.send_bytes(message.data)
        elif isinstance(message, JSONMessage):
            await self.send_json(message.data)
        else:
            # Generic message
            frame = self.protocol.create_frame(message.opcode, message.payload)
            await self.send_frame(frame)

    async def receive(self) -> Optional[WebSocketMessage]:
        """Receive a message from the WebSocket."""
        try:
            # Receive raw data
            raw_data = await self.websocket.receive_bytes()
            self._receive_buffer.extend(raw_data)

            # Parse frames from buffer
            while len(self._receive_buffer) >= 2:
                try:
                    frame, consumed = self.protocol.parse_frame(bytes(self._receive_buffer))

                    if frame is None:
                        # Incomplete frame, wait for more data
                        break

                    # Remove consumed bytes
                    del self._receive_buffer[:consumed]

                    # Process frame
                    message_data = self.protocol.process_frame(frame)

                    if message_data is not None:
                        # Complete message received
                        self.messages_received += 1
                        self.info.last_activity = time.time()

                        # Create appropriate message object
                        if frame.opcode == OpCode.TEXT:
                            try:
                                # Try to parse as JSON first
                                import json

                                data = json.loads(message_data.decode("utf-8"))
                                return JSONMessage(data)
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                # Fall back to text message
                                return TextMessage(message_data.decode("utf-8"))
                        elif frame.opcode == OpCode.BINARY:
                            return BinaryMessage(message_data)

                    # Handle ping automatically
                    if frame.opcode == OpCode.PING:
                        pong_frame = self.protocol.create_pong_frame()
                        await self.send_frame(pong_frame)

                    # Handle pong
                    elif frame.opcode == OpCode.PONG:
                        self.last_ping_time = None  # Reset ping timer

                except Exception as e:
                    logger.error(f"Error processing frame for {self.id}: {e}")
                    raise

            return None

        except ConnectionClosed:
            self.is_connected = False
            raise
        except Exception as e:
            logger.error(f"Error receiving message for {self.id}: {e}")
            self.is_connected = False
            raise

    async def ping(self, payload: bytes = b""):
        """Send ping frame."""
        self.last_ping_time = time.time()
        frame = self.protocol.create_ping_frame(payload)
        await self.send_frame(frame)

    async def pong(self, payload: bytes = b""):
        """Send pong frame."""
        frame = self.protocol.create_pong_frame(payload)
        await self.send_frame(frame)

    async def close(self, code: int = CloseCode.NORMAL_CLOSURE, reason: str = ""):
        """Close the WebSocket connection."""
        if not self.is_connected:
            return

        self.is_connected = False
        self.protocol.close(code, reason)

        try:
            # Send close frame
            close_frame = self.protocol.create_close_frame(code, reason)
            await self.websocket.send_bytes(close_frame)
        except Exception as e:
            logger.debug(f"Error sending close frame for {self.id}: {e}")

        try:
            # Close the underlying connection
            await self.websocket.close(code)
        except Exception as e:
            logger.debug(f"Error closing websocket for {self.id}: {e}")

        # Stop background tasks
        if self._send_task:
            self._send_task.cancel()
        if self._heartbeat_task:
            self._heartbeat_task.cancel()

        # Signal send worker to stop
        try:
            await self._send_queue.put(None)
        except Exception:
            # TODO: Add proper exception handling

            # Call close handler
            pass
        if self.on_close:
            try:
                await self.on_close(self)
            except Exception as e:
                logger.error(f"Error in close handler for {self.id}: {e}")

        logger.info(f"WebSocket connection {self.id} closed (code={code}, reason={reason})")

    def join_room(self, room: str):
        """Join a room."""
        self.info.rooms.add(room)
        logger.debug(f"Connection {self.id} joined room {room}")

    def leave_room(self, room: str):
        """Leave a room."""
        self.info.rooms.discard(room)
        logger.debug(f"Connection {self.id} left room {room}")

    def is_in_room(self, room: str) -> bool:
        """Check if connection is in a room."""
        return room in self.info.rooms

    def get_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "id": self.id,
            "user_id": self.info.user_id,
            "connected_at": self.info.connected_at,
            "last_activity": self.info.last_activity,
            "uptime": time.time() - self.info.connected_at,
            "is_connected": self.is_connected,
            "is_authenticated": self.is_authenticated,
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "rooms": list(self.info.rooms),
            "protocol_stats": self.protocol.get_stats(),
        }


class WebSocketConnectionManager:
    """
    Manages all WebSocket connections, rooms, and broadcasting.

    This class provides:
    - Connection lifecycle management
    - Room/channel management
    - Broadcasting to rooms, users, or all connections
    - Connection authentication and authorization
    - Statistics and monitoring
    """

    def __init__(self, max_connections: int = 1000):
        self.max_connections = max_connections

        # Connection storage
        self._connections: Dict[str, WebSocketConnection] = {}
        self._user_connections: Dict[str, Set[str]] = defaultdict(set)
        self._room_connections: Dict[str, Set[str]] = defaultdict(set)
        self._ip_connections: Dict[str, Set[str]] = defaultdict(set)

        # Statistics
        self.total_connections = 0
        self.current_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0

        # Event handlers
        self.on_connect: Optional[Callable] = None
        self.on_disconnect: Optional[Callable] = None
        self.on_message: Optional[Callable] = None

        logger.info(f"WebSocket connection manager initialized (max_connections={max_connections})")

    async def add_connection(
        self,
        websocket,
        connection_id: str,
        user_id: Optional[str] = None,
        ip_address: str = "",
        user_agent: str = "",
        metadata: Dict[str, Any] = None,
    ) -> WebSocketConnection:
        """Add a new WebSocket connection."""

        # Check connection limit
        if len(self._connections) >= self.max_connections:
            raise Exception(f"Maximum connections exceeded ({self.max_connections})")

        # Create connection info
        info = ConnectionInfo(
            id=connection_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {},
        )

        # Create protocol and connection
        protocol = WebSocketProtocol(is_client=False)
        connection = WebSocketConnection(websocket, connection_id, protocol, info)

        # Set up event handlers
        connection.on_close = self._handle_connection_close
        connection.on_message = self._handle_connection_message

        # Store connection
        self._connections[connection_id] = connection

        # Update user mapping
        if user_id:
            self._user_connections[user_id].add(connection_id)

        # Update IP mapping
        if ip_address:
            self._ip_connections[ip_address].add(connection_id)

        # Update statistics
        self.total_connections += 1
        self.current_connections += 1

        # Call connect handler
        if self.on_connect:
            try:
                await self.on_connect(connection)
            except Exception as e:
                logger.error(f"Error in connect handler: {e}")

        logger.info(f"WebSocket connection {connection_id} added (user={user_id}, ip={ip_address})")
        return connection

    async def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection."""
        connection = self._connections.get(connection_id)
        if not connection:
            return

        # Remove from user mapping
        if connection.info.user_id:
            self._user_connections[connection.info.user_id].discard(connection_id)
            if not self._user_connections[connection.info.user_id]:
                del self._user_connections[connection.info.user_id]

        # Remove from IP mapping
        if connection.info.ip_address:
            self._ip_connections[connection.info.ip_address].discard(connection_id)
            if not self._ip_connections[connection.info.ip_address]:
                del self._ip_connections[connection.info.ip_address]

        # Remove from all rooms
        for room in list(connection.info.rooms):
            await self.leave_room(connection_id, room)

        # Remove from connections
        del self._connections[connection_id]

        # Update statistics
        self.current_connections -= 1

        logger.info(f"WebSocket connection {connection_id} removed")

    async def _handle_connection_close(self, connection: WebSocketConnection):
        """Handle connection close event."""
        await self.remove_connection(connection.id)

        if self.on_disconnect:
            try:
                await self.on_disconnect(connection)
            except Exception as e:
                logger.error(f"Error in disconnect handler: {e}")

    async def _handle_connection_message(
        self, connection: WebSocketConnection, message: WebSocketMessage
    ):
        """Handle connection message event."""
        self.total_messages_received += 1

        if self.on_message:
            try:
                await self.on_message(connection, message)
            except Exception as e:
                logger.error(f"Error in message handler: {e}")

    def get_connection(self, connection_id: str) -> Optional[WebSocketConnection]:
        """Get connection by ID."""
        return self._connections.get(connection_id)

    def get_user_connections(self, user_id: str) -> Set[WebSocketConnection]:
        """Get all connections for a user."""
        connection_ids = self._user_connections.get(user_id, set())
        return {self._connections[cid] for cid in connection_ids if cid in self._connections}

    def get_room_connections(self, room: str) -> Set[WebSocketConnection]:
        """Get all connections in a room."""
        connection_ids = self._room_connections.get(room, set())
        return {self._connections[cid] for cid in connection_ids if cid in self._connections}

    def get_ip_connections(self, ip_address: str) -> Set[WebSocketConnection]:
        """Get all connections from an IP address."""
        connection_ids = self._ip_connections.get(ip_address, set())
        return {self._connections[cid] for cid in connection_ids if cid in self._connections}

    async def join_room(self, connection_id: str, room: str):
        """Add connection to a room."""
        connection = self._connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")

        connection.join_room(room)
        self._room_connections[room].add(connection_id)

        logger.debug(f"Connection {connection_id} joined room {room}")

    async def leave_room(self, connection_id: str, room: str):
        """Remove connection from a room."""
        connection = self._connections.get(connection_id)
        if connection:
            connection.leave_room(room)

        self._room_connections[room].discard(connection_id)
        if not self._room_connections[room]:
            del self._room_connections[room]

        logger.debug(f"Connection {connection_id} left room {room}")

    async def broadcast_to_room(self, room: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections in a room."""
        connections = self.get_room_connections(room)
        return await self._broadcast_to_connections(connections, message)

    async def broadcast_to_user(self, user_id: str, message: WebSocketMessage) -> int:
        """Broadcast message to all connections of a user."""
        connections = self.get_user_connections(user_id)
        return await self._broadcast_to_connections(connections, message)

    async def broadcast_to_all(self, message: WebSocketMessage) -> int:
        """Broadcast message to all connections."""
        connections = set(self._connections.values())
        return await self._broadcast_to_connections(connections, message)

    async def _broadcast_to_connections(
        self, connections: Set[WebSocketConnection], message: WebSocketMessage
    ) -> int:
        """Broadcast message to a set of connections."""
        if not connections:
            return 0

        sent_count = 0
        failed_connections = []

        # Send to all connections concurrently
        async def send_to_connection(connection: WebSocketConnection):
            try:
                await connection.send_message(message)
                return True
            except Exception as e:
                logger.warning(f"Failed to send message to {connection.id}: {e}")
                failed_connections.append(connection)
                return False

        # Use asyncio.gather to send concurrently
        tasks = [send_to_connection(conn) for conn in connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Count successful sends
        sent_count = sum(1 for result in results if result is True)

        # Close failed connections
        for connection in failed_connections:
            try:
                await connection.close(CloseCode.ABNORMAL_CLOSURE, "Send failed")
            except Exception as e:
                logger.debug(f"Error closing failed connection {connection.id}: {e}")

        self.total_messages_sent += sent_count

        logger.debug(f"Broadcast message sent to {sent_count}/{len(connections)} connections")
        return sent_count

    async def close_all_connections(
        self, code: int = CloseCode.GOING_AWAY, reason: str = "Server shutdown"
    ):
        """Close all WebSocket connections."""
        connections = list(self._connections.values())

        async def close_connection(connection: WebSocketConnection):
            try:
                await connection.close(code, reason)
            except Exception as e:
                logger.debug(f"Error closing connection {connection.id}: {e}")

        # Close all connections concurrently
        tasks = [close_connection(conn) for conn in connections]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Clear all data structures
        self._connections.clear()
        self._user_connections.clear()
        self._room_connections.clear()
        self._ip_connections.clear()

        self.current_connections = 0

        logger.info(f"All WebSocket connections closed ({len(connections)} connections)")

    def get_statistics(self) -> Dict[str, Any]:
        """Get connection manager statistics."""
        return {
            "current_connections": self.current_connections,
            "total_connections": self.total_connections,
            "max_connections": self.max_connections,
            "total_messages_sent": self.total_messages_sent,
            "total_messages_received": self.total_messages_received,
            "total_rooms": len(self._room_connections),
            "total_users": len(self._user_connections),
            "total_ips": len(self._ip_connections),
        }

    def get_room_list(self) -> List[str]:
        """Get list of all rooms."""
        return list(self._room_connections.keys())

    def get_user_list(self) -> List[str]:
        """Get list of all connected users."""
        return list(self._user_connections.keys())


# Global connection manager instance
default_connection_manager = WebSocketConnectionManager()


@asynccontextmanager
async def connection_context(connection: WebSocketConnection):
    """Context manager for WebSocket connection lifecycle."""
    try:
        yield connection
    finally:
        if connection.is_connected:
            await connection.close()


# Utility functions
async def send_to_room(
    room: str,
    message: Union[str, bytes, dict],
    manager: WebSocketConnectionManager = None,
):
    """Send message to all connections in a room."""
    if manager is None:
        manager = default_connection_manager

    if isinstance(message, str):
        ws_message = TextMessage(message)
    elif isinstance(message, bytes):
        ws_message = BinaryMessage(message)
    else:
        ws_message = JSONMessage(message)

    return await manager.broadcast_to_room(room, ws_message)


async def send_to_user(
    user_id: str,
    message: Union[str, bytes, dict],
    manager: WebSocketConnectionManager = None,
):
    """Send message to all connections of a user."""
    if manager is None:
        manager = default_connection_manager

    if isinstance(message, str):
        ws_message = TextMessage(message)
    elif isinstance(message, bytes):
        ws_message = BinaryMessage(message)
    else:
        ws_message = JSONMessage(message)

    return await manager.broadcast_to_user(user_id, ws_message)


async def send_to_all(message: Union[str, bytes, dict], manager: WebSocketConnectionManager = None):
    """Send message to all connections."""
    if manager is None:
        manager = default_connection_manager

    if isinstance(message, str):
        ws_message = TextMessage(message)
    elif isinstance(message, bytes):
        ws_message = BinaryMessage(message)
    else:
        ws_message = JSONMessage(message)

    return await manager.broadcast_to_all(ws_message)
