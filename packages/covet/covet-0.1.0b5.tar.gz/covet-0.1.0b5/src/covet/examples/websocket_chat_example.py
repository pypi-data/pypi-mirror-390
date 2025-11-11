"""
Real-time Chat Application Example

This example demonstrates a production-ready chat application using
CovetPy's WebSocket implementation with rooms, authentication, and moderation.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from ..core.websocket_connection import WebSocketConnection, default_connection_manager
from ..core.websocket_impl import JSONMessage
from ..core.websocket_router import (
    WebSocketEndpoint,
    WebSocketRouter,
    on_connect,
    on_disconnect,
    on_json,
)
from ..core.websocket_security import SecurityConfig, TokenValidator, WebSocketSecurity

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Chat message data structure."""

    id: str
    user_id: str
    username: str
    content: str
    room: str
    timestamp: float = field(default_factory=time.time)
    message_type: str = "chat"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "content": self.content,
            "room": self.room,
            "timestamp": self.timestamp,
            "message_type": self.message_type,
            "metadata": self.metadata,
            "formatted_time": datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
        }


@dataclass
class ChatUser:
    """Chat user information."""

    user_id: str
    username: str
    display_name: str
    avatar_url: Optional[str] = None
    status: str = "online"  # online, away, busy, offline
    roles: Set[str] = field(default_factory=set)
    joined_at: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    is_moderator: bool = False
    is_banned: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "status": self.status,
            "roles": list(self.roles),
            "joined_at": self.joined_at,
            "last_seen": self.last_seen,
            "is_moderator": self.is_moderator,
            "online_duration": time.time() - self.joined_at,
        }


@dataclass
class ChatRoom:
    """Chat room information."""

    room_id: str
    name: str
    description: str = ""
    max_users: int = 100
    is_private: bool = False
    created_at: float = field(default_factory=time.time)
    created_by: str = ""
    moderators: Set[str] = field(default_factory=set)
    banned_users: Set[str] = field(default_factory=set)
    allowed_users: Optional[Set[str]] = None  # For private rooms
    message_history: List[ChatMessage] = field(default_factory=list)
    settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "description": self.description,
            "max_users": self.max_users,
            "is_private": self.is_private,
            "created_at": self.created_at,
            "created_by": self.created_by,
            "moderators": list(self.moderators),
            "user_count": len(default_connection_manager.get_room_connections(self.room_id)),
            "settings": self.settings,
        }


class ChatManager:
    """Manages chat rooms, users, and messages."""

    def __init__(self):
        self.rooms: Dict[str, ChatRoom] = {}
        self.users: Dict[str, ChatUser] = {}
        self.user_connections: Dict[str, Set[WebSocketConnection]] = {}
        self.message_history_limit = 100

        # Create default room
        self.create_room("general", "General Chat", "Welcome to the general chat room!")

    def create_room(
        self,
        room_id: str,
        name: str,
        description: str = "",
        created_by: str = "",
        max_users: int = 100,
        is_private: bool = False,
    ) -> ChatRoom:
        """Create a new chat room."""
        room = ChatRoom(
            room_id=room_id,
            name=name,
            description=description,
            created_by=created_by,
            max_users=max_users,
            is_private=is_private,
        )

        if created_by:
            room.moderators.add(created_by)

        self.rooms[room_id] = room
        logger.info(f"Created chat room: {room_id} ({name})")
        return room

    def get_room(self, room_id: str) -> Optional[ChatRoom]:
        """Get room by ID."""
        return self.rooms.get(room_id)

    def list_rooms(self) -> List[Dict[str, Any]]:
        """List all available rooms."""
        return [room.to_dict() for room in self.rooms.values()]

    def register_user(
        self,
        user_id: str,
        username: str,
        display_name: str,
        avatar_url: Optional[str] = None,
    ) -> ChatUser:
        """Register a new user."""
        user = ChatUser(
            user_id=user_id,
            username=username,
            display_name=display_name,
            avatar_url=avatar_url,
        )

        self.users[user_id] = user
        logger.info(f"Registered user: {username} ({user_id})")
        return user

    def get_user(self, user_id: str) -> Optional[ChatUser]:
        """Get user by ID."""
        return self.users.get(user_id)

    def user_join_room(self, user_id: str, room_id: str, connection: WebSocketConnection) -> bool:
        """User joins a room."""
        room = self.get_room(room_id)
        user = self.get_user(user_id)

        if not room or not user:
            return False

        # Check if user is banned
        if user_id in room.banned_users:
            return False

        # Check room capacity
        current_users = len(default_connection_manager.get_room_connections(room_id))
        if current_users >= room.max_users:
            return False

        # Check private room access
        if room.is_private and room.allowed_users and user_id not in room.allowed_users:
            return False

        # Join room
        connection.join_room(room_id)

        # Track user connection
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection)

        # Update user status
        user.last_seen = time.time()
        user.status = "online"

        logger.info(f"User {user.username} joined room {room_id}")
        return True

    def user_leave_room(self, user_id: str, room_id: str, connection: WebSocketConnection) -> None:
        """User leaves a room."""
        connection.leave_room(room_id)

        # Remove from user connections if no more connections in this room
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

                # Update user status if no connections
                user = self.get_user(user_id)
                if user:
                    user.status = "offline"
                    user.last_seen = time.time()

        logger.info(f"User {user_id} left room {room_id}")

    async def send_message(
        self, user_id: str, room_id: str, content: str, message_type: str = "chat"
    ) -> Optional[ChatMessage]:
        """Send a message to a room."""
        user = self.get_user(user_id)
        room = self.get_room(room_id)

        if not user or not room:
            return None

        # Check if user is banned
        if user.is_banned or user_id in room.banned_users:
            return None

        # Create message
        message = ChatMessage(
            id=f"{room_id}_{user_id}_{int(time.time() * 1000)}",
            user_id=user_id,
            username=user.username,
            content=content,
            room=room_id,
            message_type=message_type,
        )

        # Add to room history
        room.message_history.append(message)

        # Limit history size
        if len(room.message_history) > self.message_history_limit:
            room.message_history = room.message_history[-self.message_history_limit :]

        # Broadcast to room
        await default_connection_manager.broadcast_to_room(
            room_id, JSONMessage(data={"type": "message", "message": message.to_dict()})
        )

        logger.info(f"Message sent by {user.username} to {room_id}: {content[:50]}...")
        return message

    async def send_system_message(
        self, room_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Send a system message to a room."""
        message_data = {
            "type": "system_message",
            "content": content,
            "room": room_id,
            "timestamp": time.time(),
            "formatted_time": datetime.now().strftime("%H:%M:%S"),
            "metadata": metadata or {},
        }

        await default_connection_manager.broadcast_to_room(room_id, JSONMessage(data=message_data))

    def get_room_users(self, room_id: str) -> List[Dict[str, Any]]:
        """Get list of users in a room."""
        connections = default_connection_manager.get_room_connections(room_id)
        users = []

        for conn in connections:
            if conn.info.authenticated and conn.info.user_id:
                user = self.get_user(conn.info.user_id)
                if user:
                    users.append(user.to_dict())

        return users

    def get_room_history(self, room_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent message history for a room."""
        room = self.get_room(room_id)
        if not room:
            return []

        messages = room.message_history[-limit:] if room.message_history else []
        return [msg.to_dict() for msg in messages]

    def ban_user(self, moderator_id: str, room_id: str, user_id: str, reason: str = "") -> bool:
        """Ban a user from a room."""
        room = self.get_room(room_id)
        moderator = self.get_user(moderator_id)

        if not room or not moderator:
            return False

        # Check if moderator has permission
        if not moderator.is_moderator and moderator_id not in room.moderators:
            return False

        # Ban user
        room.banned_users.add(user_id)

        # Disconnect user from room
        user_connections = [
            conn
            for conn in default_connection_manager.get_room_connections(room_id)
            if conn.info.user_id == user_id
        ]

        for conn in user_connections:
            self.user_leave_room(user_id, room_id, conn)

        logger.info(f"User {user_id} banned from room {room_id} by {moderator_id}")
        return True


# Global chat manager
chat_manager = ChatManager()


class ChatEndpoint(WebSocketEndpoint):
    """WebSocket endpoint for chat functionality."""

    def __init__(self):
        super().__init__()
        self.chat_manager = chat_manager

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        """Handle new connection."""
        await connection.accept()

        # Send welcome message
        await connection.send_json(
            {
                "type": "welcome",
                "message": "Welcome to CovetPy Chat!",
                "server_time": time.time(),
                "available_rooms": self.chat_manager.list_rooms(),
            }
        )

        logger.info(f"New chat connection: {connection.info.id}")

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        """Handle connection disconnect."""
        if connection.info.authenticated and connection.info.user_id:
            # Leave all rooms
            for room in list(connection.info.rooms):
                self.chat_manager.user_leave_room(connection.info.user_id, room, connection)

            # Notify rooms about user leaving
            for room_id in connection.info.rooms:
                await self.chat_manager.send_system_message(
                    room_id,
                    f"{connection.info.metadata.get('username', 'User')} left the chat",
                )

        logger.info(f"Chat connection disconnected: {connection.info.id}")

    @on_json
    async def handle_message(self, connection: WebSocketConnection, message):
        """Handle JSON message."""
        try:
            data = message.data
            msg_type = data.get("type")

            if msg_type == "authenticate":
                await self._handle_authenticate(connection, data)
            elif msg_type == "join_room":
                await self._handle_join_room(connection, data)
            elif msg_type == "leave_room":
                await self._handle_leave_room(connection, data)
            elif msg_type == "send_message":
                await self._handle_send_message(connection, data)
            elif msg_type == "get_room_users":
                await self._handle_get_room_users(connection, data)
            elif msg_type == "get_room_history":
                await self._handle_get_room_history(connection, data)
            elif msg_type == "create_room":
                await self._handle_create_room(connection, data)
            elif msg_type == "typing_start":
                await self._handle_typing_start(connection, data)
            elif msg_type == "typing_stop":
                await self._handle_typing_stop(connection, data)
            elif msg_type == "ban_user":
                await self._handle_ban_user(connection, data)
            else:
                await connection.send_json(
                    {"type": "error", "message": f"Unknown message type: {msg_type}"}
                )

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await connection.send_json({"type": "error", "message": "Failed to process message"})

    async def _handle_authenticate(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle user authentication."""
        username = data.get("username")
        display_name = data.get("display_name", username)
        avatar_url = data.get("avatar_url")

        if not username:
            await connection.send_json({"type": "auth_error", "message": "Username required"})
            return

        # Simple authentication (in production, validate credentials)
        user_id = f"user_{username}_{int(time.time())}"

        # Register user
        user = self.chat_manager.register_user(user_id, username, display_name, avatar_url)

        # Authenticate connection
        connection.authenticate(
            user_id,
            metadata={
                "username": username,
                "display_name": display_name,
                "user_data": user.to_dict(),
            },
        )

        await connection.send_json(
            {
                "type": "authenticated",
                "user": user.to_dict(),
                "available_rooms": self.chat_manager.list_rooms(),
            }
        )

        logger.info(f"User authenticated: {username} ({user_id})")

    async def _handle_join_room(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle room join request."""
        if not connection.info.authenticated:
            await connection.send_json({"type": "error", "message": "Authentication required"})
            return

        room_id = data.get("room_id")
        if not room_id:
            await connection.send_json({"type": "error", "message": "Room ID required"})
            return

        # Join room
        success = self.chat_manager.user_join_room(connection.info.user_id, room_id, connection)

        if success:
            # Send join confirmation
            await connection.send_json(
                {
                    "type": "room_joined",
                    "room_id": room_id,
                    "room_info": self.chat_manager.get_room(room_id).to_dict(),
                    "users": self.chat_manager.get_room_users(room_id),
                    "recent_messages": self.chat_manager.get_room_history(room_id, 20),
                }
            )

            # Notify other users
            await self.chat_manager.send_system_message(
                room_id,
                f"{connection.info.metadata.get('display_name', 'User')} joined the chat",
            )

            # Broadcast updated user list
            await self._broadcast_user_list_update(room_id)

        else:
            await connection.send_json({"type": "join_error", "message": "Failed to join room"})

    async def _handle_leave_room(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle room leave request."""
        room_id = data.get("room_id")
        if not room_id:
            return

        if connection.info.authenticated and connection.info.user_id:
            self.chat_manager.user_leave_room(connection.info.user_id, room_id, connection)

            await connection.send_json({"type": "room_left", "room_id": room_id})

            # Notify other users
            await self.chat_manager.send_system_message(
                room_id,
                f"{connection.info.metadata.get('display_name', 'User')} left the chat",
            )

            # Broadcast updated user list
            await self._broadcast_user_list_update(room_id)

    async def _handle_send_message(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle message send request."""
        if not connection.info.authenticated:
            await connection.send_json({"type": "error", "message": "Authentication required"})
            return

        room_id = data.get("room_id")
        content = data.get("content", "").strip()

        if not room_id or not content:
            await connection.send_json({"type": "error", "message": "Room ID and content required"})
            return

        # Check if user is in room
        if room_id not in connection.info.rooms:
            await connection.send_json({"type": "error", "message": "You are not in this room"})
            return

        # Send message
        message = await self.chat_manager.send_message(connection.info.user_id, room_id, content)

        if message:
            await connection.send_json({"type": "message_sent", "message_id": message.id})
        else:
            await connection.send_json({"type": "error", "message": "Failed to send message"})

    async def _handle_get_room_users(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get room users request."""
        room_id = data.get("room_id")
        if not room_id:
            return

        users = self.chat_manager.get_room_users(room_id)
        await connection.send_json({"type": "room_users", "room_id": room_id, "users": users})

    async def _handle_get_room_history(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get room history request."""
        room_id = data.get("room_id")
        limit = data.get("limit", 50)

        if not room_id:
            return

        history = self.chat_manager.get_room_history(room_id, limit)
        await connection.send_json(
            {"type": "room_history", "room_id": room_id, "messages": history}
        )

    async def _handle_create_room(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle create room request."""
        if not connection.info.authenticated:
            await connection.send_json({"type": "error", "message": "Authentication required"})
            return

        name = data.get("name", "").strip()
        description = data.get("description", "")
        is_private = data.get("is_private", False)
        max_users = data.get("max_users", 100)

        if not name:
            await connection.send_json({"type": "error", "message": "Room name required"})
            return

        # Generate room ID
        room_id = f"room_{name.lower().replace(' ', '_')}_{int(time.time())}"

        # Create room
        room = self.chat_manager.create_room(
            room_id=room_id,
            name=name,
            description=description,
            created_by=connection.info.user_id,
            max_users=max_users,
            is_private=is_private,
        )

        await connection.send_json({"type": "room_created", "room": room.to_dict()})

        logger.info(f"Room created: {name} ({room_id}) by {connection.info.user_id}")

    async def _handle_typing_start(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle typing start notification."""
        room_id = data.get("room_id")
        if not room_id or room_id not in connection.info.rooms:
            return

        # Broadcast typing indicator to room (except sender)
        typing_data = {
            "type": "user_typing_start",
            "room_id": room_id,
            "user_id": connection.info.user_id,
            "username": connection.info.metadata.get("display_name", "User"),
        }

        connections = default_connection_manager.get_room_connections(room_id)
        for conn in connections:
            if conn.info.id != connection.info.id:
                await conn.send_json(typing_data)

    async def _handle_typing_stop(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle typing stop notification."""
        room_id = data.get("room_id")
        if not room_id or room_id not in connection.info.rooms:
            return

        # Broadcast typing stop to room (except sender)
        typing_data = {
            "type": "user_typing_stop",
            "room_id": room_id,
            "user_id": connection.info.user_id,
            "username": connection.info.metadata.get("display_name", "User"),
        }

        connections = default_connection_manager.get_room_connections(room_id)
        for conn in connections:
            if conn.info.id != connection.info.id:
                await conn.send_json(typing_data)

    async def _handle_ban_user(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle ban user request."""
        if not connection.info.authenticated:
            return

        room_id = data.get("room_id")
        target_user_id = data.get("user_id")
        reason = data.get("reason", "")

        if not room_id or not target_user_id:
            return

        # Ban user
        success = self.chat_manager.ban_user(
            connection.info.user_id, room_id, target_user_id, reason
        )

        if success:
            await connection.send_json(
                {"type": "user_banned", "room_id": room_id, "user_id": target_user_id}
            )

            # Notify room
            await self.chat_manager.send_system_message(room_id, "User was banned from the room")
        else:
            await connection.send_json({"type": "error", "message": "Failed to ban user"})

    async def _broadcast_user_list_update(self, room_id: str):
        """Broadcast updated user list to room."""
        users = self.chat_manager.get_room_users(room_id)
        user_list_data = {
            "type": "user_list_update",
            "room_id": room_id,
            "users": users,
        }

        await default_connection_manager.broadcast_to_room(
            room_id, JSONMessage(data=user_list_data)
        )


# Create router and add chat endpoint
def create_chat_router() -> WebSocketRouter:
    """Create WebSocket router with chat endpoint."""
    router = WebSocketRouter()

    # Add chat endpoint
    router.add_route("/ws/chat", ChatEndpoint())

    return router


# Example usage
async def run_chat_example():
    """Run the chat example."""
    from ..core.asgi import CovetPyASGI

    # Create router
    router = create_chat_router()

    # Create ASGI app
    CovetPyASGI()

    # Add WebSocket handling
    async def websocket_handler(scope, receive, send):
        if scope["type"] == "websocket":
            await router.handle_websocket(scope, receive, send)
        else:
            await send({"type": "http.response.start", "status": 404, "headers": []})
            await send({"type": "http.response.body", "body": b"Not Found"})

    # Run with uvicorn or similar
    logger.info("Chat WebSocket server ready at ws://localhost:8000/ws/chat")
    logger.info("Use the WebSocket client to connect and start chatting!")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run example
    asyncio.run(run_chat_example())
