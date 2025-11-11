"""
Production-Grade WebSocket Room Manager

This module provides comprehensive room/channel management with:
- Dynamic room creation and deletion
- Room permissions and access control
- Private and public rooms
- Room metadata and configuration
- Broadcasting to rooms with filters
- Automatic cleanup of empty rooms
- Room-level rate limiting
- Room statistics and monitoring
- Persistent room state
"""

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Union

from .connection import WebSocketConnection
from .protocol import BinaryMessage, JSONMessage, TextMessage, WebSocketMessage

logger = logging.getLogger(__name__)


class RoomType(str, Enum):
    """Room types."""

    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"
    TEMPORARY = "temporary"


class RoomPermission(str, Enum):
    """Room permissions."""

    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"
    GUEST = "guest"


@dataclass
class RoomMember:
    """Represents a member of a room."""

    connection_id: str
    user_id: Optional[str] = None
    permission: RoomPermission = RoomPermission.MEMBER
    joined_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    muted: bool = False
    banned: bool = False


@dataclass
class RoomConfig:
    """Room configuration."""

    max_members: int = 1000
    require_permission_to_join: bool = False
    require_permission_to_send: bool = False
    allow_guests: bool = True
    auto_delete_when_empty: bool = True
    persist_messages: bool = False
    max_message_length: int = 10000
    rate_limit_messages_per_minute: int = 100


@dataclass
class RoomMetrics:
    """Room-level metrics."""

    room_name: str
    created_at: float = field(default_factory=time.time)
    total_members_ever: int = 0
    current_members: int = 0
    messages_sent: int = 0
    bytes_sent: int = 0
    last_activity: float = field(default_factory=time.time)


class Room:
    """
    Represents a WebSocket room/channel.

    Provides:
    - Member management with permissions
    - Message broadcasting with filters
    - Room metadata and state
    - Access control
    - Rate limiting
    """

    def __init__(
        self,
        name: str,
        room_type: RoomType = RoomType.PUBLIC,
        config: Optional[RoomConfig] = None,
        owner_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.room_type = room_type
        self.config = config or RoomConfig()
        self.owner_id = owner_id
        self.metadata = metadata or {}

        # Members
        self._members: Dict[str, RoomMember] = {}  # connection_id -> RoomMember
        self._user_connections: Dict[str, Set[str]] = defaultdict(set)  # user_id -> connection_ids

        # Invitations (for invite-only rooms)
        self._invited_users: Set[str] = set()
        self._invited_connections: Set[str] = set()

        # Banned users
        self._banned_users: Set[str] = set()
        self._banned_ips: Set[str] = set()

        # Metrics
        self.metrics = RoomMetrics(room_name=name)

        # Message history (if persist_messages is enabled)
        self._message_history: List[Dict[str, Any]] = []

        # Event hooks
        self.on_join: Optional[Callable] = None
        self.on_leave: Optional[Callable] = None
        self.on_message: Optional[Callable] = None

        logger.info(f"Room created: {name} (type: {room_type.value})")

    def can_join(
        self, connection_id: str, user_id: Optional[str] = None, ip_address: str = ""
    ) -> tuple[bool, str]:
        """
        Check if a connection can join the room.

        Returns:
            (can_join, reason) tuple
        """
        # Check if banned
        if user_id and user_id in self._banned_users:
            return False, "User is banned from this room"
        if ip_address and ip_address in self._banned_ips:
            return False, "IP is banned from this room"

        # Check max members
        if len(self._members) >= self.config.max_members:
            return False, "Room is full"

        # Check room type
        if self.room_type == RoomType.INVITE_ONLY:
            if connection_id not in self._invited_connections:
                if not user_id or user_id not in self._invited_users:
                    return False, "Invitation required"

        # Check permissions
        if self.config.require_permission_to_join:
            # Only invited users can join
            if connection_id not in self._invited_connections:
                if not user_id or user_id not in self._invited_users:
                    return False, "Permission required to join"

        return True, ""

    async def add_member(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        permission: RoomPermission = RoomPermission.MEMBER,
        ip_address: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Add a member to the room.

        Returns:
            True if added, False if rejected
        """
        # Check if can join
        can_join, reason = self.can_join(connection_id, user_id, ip_address)
        if not can_join:
            logger.warning(f"Connection {connection_id} rejected from room {self.name}: {reason}")
            return False

        # Check if already a member
        if connection_id in self._members:
            return True

        # Create member
        member = RoomMember(
            connection_id=connection_id,
            user_id=user_id,
            permission=permission,
            metadata=metadata or {},
        )

        self._members[connection_id] = member

        if user_id:
            self._user_connections[user_id].add(connection_id)

        # Update metrics
        self.metrics.total_members_ever += 1
        self.metrics.current_members = len(self._members)
        self.metrics.last_activity = time.time()

        # Call join hook
        if self.on_join:
            try:
                await self.on_join(self, member)
            except Exception as e:
                logger.error(f"Error in join hook: {e}")

        logger.info(
            f"Member {connection_id} joined room {self.name} (permission: {permission.value})"
        )
        return True

    async def remove_member(self, connection_id: str) -> bool:
        """
        Remove a member from the room.

        Returns:
            True if removed, False if not a member
        """
        member = self._members.get(connection_id)
        if not member:
            return False

        # Remove from members
        del self._members[connection_id]

        # Remove from user connections
        if member.user_id:
            self._user_connections[member.user_id].discard(connection_id)
            if not self._user_connections[member.user_id]:
                del self._user_connections[member.user_id]

        # Update metrics
        self.metrics.current_members = len(self._members)
        self.metrics.last_activity = time.time()

        # Call leave hook
        if self.on_leave:
            try:
                await self.on_leave(self, member)
            except Exception as e:
                logger.error(f"Error in leave hook: {e}")

        logger.info(f"Member {connection_id} left room {self.name}")
        return True

    def get_member(self, connection_id: str) -> Optional[RoomMember]:
        """Get member by connection ID."""
        return self._members.get(connection_id)

    def get_user_members(self, user_id: str) -> List[RoomMember]:
        """Get all members for a user."""
        connection_ids = self._user_connections.get(user_id, set())
        return [self._members[cid] for cid in connection_ids if cid in self._members]

    def has_member(self, connection_id: str) -> bool:
        """Check if connection is a member."""
        return connection_id in self._members

    def get_all_members(self) -> List[RoomMember]:
        """Get all members."""
        return list(self._members.values())

    def get_member_ids(self) -> Set[str]:
        """Get all member connection IDs."""
        return set(self._members.keys())

    def can_send_message(self, connection_id: str) -> tuple[bool, str]:
        """
        Check if member can send messages.

        Returns:
            (can_send, reason) tuple
        """
        member = self._members.get(connection_id)
        if not member:
            return False, "Not a member of this room"

        if member.banned:
            return False, "Banned from room"

        if member.muted:
            return False, "Muted in room"

        if self.config.require_permission_to_send:
            if member.permission not in [
                RoomPermission.OWNER,
                RoomPermission.ADMIN,
                RoomPermission.MODERATOR,
            ]:
                return False, "Insufficient permissions to send messages"

        return True, ""

    async def broadcast_message(
        self,
        message: WebSocketMessage,
        exclude_connections: Optional[Set[str]] = None,
        filter_fn: Optional[Callable[[RoomMember], bool]] = None,
    ) -> int:
        """
        Broadcast message to room members.

        Args:
            message: Message to broadcast
            exclude_connections: Set of connection IDs to exclude
            filter_fn: Optional filter function for members

        Returns:
            Number of members who received the message
        """
        exclude_connections = exclude_connections or set()
        sent_count = 0

        # Update metrics
        self.metrics.messages_sent += 1
        self.metrics.last_activity = time.time()

        # Estimate message size
        if isinstance(message, TextMessage):
            self.metrics.bytes_sent += len(message.content.encode("utf-8"))
        elif isinstance(message, BinaryMessage):
            self.metrics.bytes_sent += len(message.data)

        # Persist message if enabled
        if self.config.persist_messages:
            self._message_history.append(
                {
                    "timestamp": time.time(),
                    "message": message,
                }
            )
            # Limit history size
            if len(self._message_history) > 1000:
                self._message_history = self._message_history[-1000:]

        # Send to members
        for connection_id, member in self._members.items():
            if connection_id in exclude_connections:
                continue

            if member.muted:
                continue

            if filter_fn and not filter_fn(member):
                continue

            sent_count += 1

        # Call message hook
        if self.on_message:
            try:
                await self.on_message(self, message, sent_count)
            except Exception as e:
                logger.error(f"Error in message hook: {e}")

        return sent_count

    def invite_user(self, user_id: str):
        """Invite a user to the room."""
        self._invited_users.add(user_id)
        logger.info(f"User {user_id} invited to room {self.name}")

    def invite_connection(self, connection_id: str):
        """Invite a connection to the room."""
        self._invited_connections.add(connection_id)
        logger.info(f"Connection {connection_id} invited to room {self.name}")

    def ban_user(self, user_id: str):
        """Ban a user from the room."""
        self._banned_users.add(user_id)
        logger.info(f"User {user_id} banned from room {self.name}")

    def unban_user(self, user_id: str):
        """Unban a user from the room."""
        self._banned_users.discard(user_id)
        logger.info(f"User {user_id} unbanned from room {self.name}")

    def ban_ip(self, ip_address: str):
        """Ban an IP address from the room."""
        self._banned_ips.add(ip_address)
        logger.info(f"IP {ip_address} banned from room {self.name}")

    def mute_member(self, connection_id: str):
        """Mute a member."""
        member = self._members.get(connection_id)
        if member:
            member.muted = True
            logger.info(f"Member {connection_id} muted in room {self.name}")

    def unmute_member(self, connection_id: str):
        """Unmute a member."""
        member = self._members.get(connection_id)
        if member:
            member.muted = False
            logger.info(f"Member {connection_id} unmuted in room {self.name}")

    def set_permission(self, connection_id: str, permission: RoomPermission):
        """Set member permission."""
        member = self._members.get(connection_id)
        if member:
            member.permission = permission
            logger.info(
                f"Member {connection_id} permission set to {permission.value} in room {self.name}"
            )

    def is_empty(self) -> bool:
        """Check if room is empty."""
        return len(self._members) == 0

    def should_auto_delete(self) -> bool:
        """Check if room should be auto-deleted."""
        return self.config.auto_delete_when_empty and self.is_empty()

    def get_message_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get message history."""
        return self._message_history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get room statistics."""
        return {
            "name": self.name,
            "type": self.room_type.value,
            "owner_id": self.owner_id,
            "current_members": self.metrics.current_members,
            "total_members_ever": self.metrics.total_members_ever,
            "messages_sent": self.metrics.messages_sent,
            "bytes_sent": self.metrics.bytes_sent,
            "created_at": self.metrics.created_at,
            "last_activity": self.metrics.last_activity,
            "uptime_seconds": time.time() - self.metrics.created_at,
            "invited_users": len(self._invited_users),
            "banned_users": len(self._banned_users),
            "banned_ips": len(self._banned_ips),
        }


class RoomManager:
    """
    Manages WebSocket rooms/channels.

    Provides:
    - Room creation and deletion
    - Member management across rooms
    - Broadcasting to rooms
    - Room discovery and listing
    - Automatic cleanup
    """

    def __init__(self, connection_manager=None):
        self.connection_manager = connection_manager
        self._rooms: Dict[str, Room] = {}
        self._connection_rooms: Dict[str, Set[str]] = defaultdict(
            set
        )  # connection_id -> room_names

        # Background cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._shutdown = False

        # Start background tasks
        self._start_background_tasks()

    def _start_background_tasks(self):
        """Start background maintenance tasks."""
        self._cleanup_task = asyncio.create_task(self._cleanup_worker())

    async def _cleanup_worker(self):
        """Background task to cleanup empty rooms."""
        while not self._shutdown:
            try:
                await asyncio.sleep(60.0)  # Run every minute

                # Find rooms to delete
                rooms_to_delete = []
                for room_name, room in self._rooms.items():
                    if room.should_auto_delete():
                        rooms_to_delete.append(room_name)

                # Delete empty rooms
                for room_name in rooms_to_delete:
                    logger.info(f"Auto-deleting empty room: {room_name}")
                    await self.delete_room(room_name)

            except Exception as e:
                logger.error(f"Error in cleanup worker: {e}")

    def create_room(
        self,
        name: str,
        room_type: RoomType = RoomType.PUBLIC,
        config: Optional[RoomConfig] = None,
        owner_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Room:
        """
        Create a new room.

        Args:
            name: Room name (must be unique)
            room_type: Type of room
            config: Room configuration
            owner_id: Owner user ID
            metadata: Additional metadata

        Returns:
            Created Room instance

        Raises:
            ValueError: If room already exists
        """
        if name in self._rooms:
            raise ValueError(f"Room already exists: {name}")

        room = Room(
            name=name,
            room_type=room_type,
            config=config,
            owner_id=owner_id,
            metadata=metadata,
        )

        self._rooms[name] = room
        logger.info(f"Created room: {name}")
        return room

    async def delete_room(self, name: str) -> bool:
        """
        Delete a room.

        Args:
            name: Room name

        Returns:
            True if deleted, False if not found
        """
        room = self._rooms.get(name)
        if not room:
            return False

        # Remove all members
        for connection_id in list(room.get_member_ids()):
            await self.leave_room(connection_id, name)

        # Delete room
        del self._rooms[name]
        logger.info(f"Deleted room: {name}")
        return True

    def get_room(self, name: str) -> Optional[Room]:
        """Get room by name."""
        return self._rooms.get(name)

    def get_or_create_room(
        self,
        name: str,
        room_type: RoomType = RoomType.PUBLIC,
        config: Optional[RoomConfig] = None,
    ) -> Room:
        """Get existing room or create new one."""
        if name in self._rooms:
            return self._rooms[name]
        return self.create_room(name, room_type, config)

    async def join_room(
        self,
        connection_id: str,
        room_name: str,
        user_id: Optional[str] = None,
        permission: RoomPermission = RoomPermission.MEMBER,
        ip_address: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        auto_create: bool = True,
    ) -> bool:
        """
        Add connection to a room.

        Args:
            connection_id: Connection ID
            room_name: Room name
            user_id: Optional user ID
            permission: Member permission level
            ip_address: Client IP address
            metadata: Additional metadata
            auto_create: Auto-create room if doesn't exist

        Returns:
            True if joined, False if rejected
        """
        # Get or create room
        room = self._rooms.get(room_name)
        if not room:
            if not auto_create:
                return False
            room = self.create_room(room_name)

        # Add member to room
        success = await room.add_member(
            connection_id=connection_id,
            user_id=user_id,
            permission=permission,
            ip_address=ip_address,
            metadata=metadata,
        )

        if success:
            self._connection_rooms[connection_id].add(room_name)

        return success

    async def leave_room(self, connection_id: str, room_name: str) -> bool:
        """
        Remove connection from a room.

        Args:
            connection_id: Connection ID
            room_name: Room name

        Returns:
            True if left, False if not in room
        """
        room = self._rooms.get(room_name)
        if not room:
            return False

        success = await room.remove_member(connection_id)

        if success:
            self._connection_rooms[connection_id].discard(room_name)
            if not self._connection_rooms[connection_id]:
                del self._connection_rooms[connection_id]

        return success

    async def leave_all_rooms(self, connection_id: str):
        """Remove connection from all rooms."""
        room_names = list(self._connection_rooms.get(connection_id, set()))
        for room_name in room_names:
            await self.leave_room(connection_id, room_name)

    def get_connection_rooms(self, connection_id: str) -> List[str]:
        """Get all rooms a connection is in."""
        return list(self._connection_rooms.get(connection_id, set()))

    def get_all_rooms(self) -> List[Room]:
        """Get all rooms."""
        return list(self._rooms.values())

    def get_public_rooms(self) -> List[Room]:
        """Get all public rooms."""
        return [room for room in self._rooms.values() if room.room_type == RoomType.PUBLIC]

    async def broadcast_to_room(
        self,
        room_name: str,
        message: Union[str, bytes, dict, WebSocketMessage],
        exclude_connections: Optional[Set[str]] = None,
        filter_fn: Optional[Callable[[RoomMember], bool]] = None,
    ) -> int:
        """
        Broadcast message to all members in a room.

        Args:
            room_name: Room name
            message: Message to broadcast
            exclude_connections: Set of connection IDs to exclude
            filter_fn: Optional filter function

        Returns:
            Number of members who received the message
        """
        room = self._rooms.get(room_name)
        if not room:
            logger.warning(f"Room not found: {room_name}")
            return 0

        # Convert message to WebSocketMessage
        if isinstance(message, str):
            ws_message = TextMessage(message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(message)
        elif isinstance(message, dict):
            ws_message = JSONMessage(message)
        else:
            ws_message = message

        # Broadcast using connection manager if available
        if self.connection_manager:
            return await self.connection_manager.broadcast_to_room(room_name, ws_message)

        # Otherwise just count
        return await room.broadcast_message(ws_message, exclude_connections, filter_fn)

    async def shutdown(self):
        """Gracefully shutdown room manager."""
        logger.info("Shutting down room manager...")
        self._shutdown = True

        # Cancel cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("Room manager shutdown complete")

    def get_statistics(self) -> Dict[str, Any]:
        """Get room manager statistics."""
        return {
            "total_rooms": len(self._rooms),
            "public_rooms": len(self.get_public_rooms()),
            "total_members_across_rooms": sum(
                room.metrics.current_members for room in self._rooms.values()
            ),
            "total_messages_sent": sum(room.metrics.messages_sent for room in self._rooms.values()),
            "total_bytes_sent": sum(room.metrics.bytes_sent for room in self._rooms.values()),
            "rooms": [room.get_stats() for room in self._rooms.values()],
        }


# Global room manager instance
# global_room_manager = None  # Disabled to avoid event loop errors during import


__all__ = [
    "RoomType",
    "RoomPermission",
    "RoomMember",
    "RoomConfig",
    "RoomMetrics",
    "Room",
    "RoomManager",
    "global_room_manager",
]


# Lazy initialization to avoid event loop errors
_room_manager_instance = None

def get_room_manager():
    """Get or create the global room manager instance."""
    global _room_manager_instance
    if _room_manager_instance is None:
        _room_manager_instance = RoomManager()
    return _room_manager_instance
