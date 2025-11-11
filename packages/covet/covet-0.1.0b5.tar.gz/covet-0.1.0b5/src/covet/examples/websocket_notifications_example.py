"""
Real-time Notifications System Example

This example demonstrates a production-ready notification system using
CovetPy's WebSocket implementation with user targeting, priority levels,
and delivery tracking.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
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

logger = logging.getLogger(__name__)


class NotificationType(Enum):
    """Notification types."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    SYSTEM = "system"
    USER_ACTION = "user_action"
    REMINDER = "reminder"
    ALERT = "alert"


class NotificationPriority(Enum):
    """Notification priorities."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5


@dataclass
class Notification:
    """Notification data structure."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    user_id: Optional[str] = None
    target_groups: Set[str] = field(default_factory=set)
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    read_by: Set[str] = field(default_factory=set)
    delivered_to: Set[str] = field(default_factory=set)
    actions: List[Dict[str, Any]] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    persistent: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type.value,
            "priority": self.priority.value,
            "user_id": self.user_id,
            "target_groups": list(self.target_groups),
            "data": self.data,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "read_by": list(self.read_by),
            "delivered_to": list(self.delivered_to),
            "actions": self.actions,
            "tags": list(self.tags),
            "persistent": self.persistent,
            "formatted_time": datetime.fromtimestamp(self.created_at).strftime("%Y-%m-%d %H:%M:%S"),
            "is_expired": self.is_expired(),
            "age_seconds": time.time() - self.created_at,
        }

    def is_expired(self) -> bool:
        """Check if notification has expired."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def mark_read(self, user_id: str) -> None:
        """Mark notification as read by user."""
        self.read_by.add(user_id)

    def mark_delivered(self, user_id: str) -> None:
        """Mark notification as delivered to user."""
        self.delivered_to.add(user_id)

    def is_read_by(self, user_id: str) -> bool:
        """Check if notification is read by user."""
        return user_id in self.read_by

    def is_delivered_to(self, user_id: str) -> bool:
        """Check if notification is delivered to user."""
        return user_id in self.delivered_to


@dataclass
class NotificationSubscription:
    """User notification subscription preferences."""

    user_id: str
    notification_types: Set[NotificationType] = field(default_factory=lambda: set(NotificationType))
    priority_filter: NotificationPriority = NotificationPriority.LOW
    tags_filter: Set[str] = field(default_factory=set)
    groups: Set[str] = field(default_factory=set)
    quiet_hours_start: Optional[int] = None  # Hour 0-23
    quiet_hours_end: Optional[int] = None  # Hour 0-23
    enabled: bool = True
    max_notifications_per_hour: int = 100

    def should_receive(self, notification: Notification) -> bool:
        """Check if user should receive this notification."""
        if not self.enabled:
            return False

        # Check notification type
        if notification.notification_type not in self.notification_types:
            return False

        # Check priority
        if notification.priority.value < self.priority_filter.value:
            return False

        # Check tags filter
        if self.tags_filter and not (notification.tags & self.tags_filter):
            return False

        # Check quiet hours
        if self.quiet_hours_start is not None and self.quiet_hours_end is not None:
            current_hour = datetime.now().hour
            if self.quiet_hours_start <= self.quiet_hours_end:
                # Same day range
                if self.quiet_hours_start <= current_hour <= self.quiet_hours_end:
                    # Allow only critical notifications during quiet hours
                    if notification.priority != NotificationPriority.CRITICAL:
                        return False
            else:
                # Overnight range
                if current_hour >= self.quiet_hours_start or current_hour <= self.quiet_hours_end:
                    if notification.priority != NotificationPriority.CRITICAL:
                        return False

        return True


class NotificationManager:
    """Manages notifications, subscriptions, and delivery."""

    def __init__(self):
        self.notifications: Dict[str, Notification] = {}
        self.subscriptions: Dict[str, NotificationSubscription] = {}
        self.user_notifications: Dict[str, List[str]] = {}  # user_id -> notification_ids
        self.delivery_stats: Dict[str, Dict[str, int]] = {}
        self.cleanup_task: Optional[asyncio.Task] = None

        # Start cleanup task
        self._start_cleanup_task()

    def _start_cleanup_task(self):
        """Start background cleanup task."""
        if self.cleanup_task is None or self.cleanup_task.done():
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_notifications())

    async def _cleanup_expired_notifications(self):
        """Clean up expired notifications periodically."""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes

                time.time()
                expired_ids = []

                for notification_id, notification in self.notifications.items():
                    if notification.is_expired():
                        expired_ids.append(notification_id)

                for notification_id in expired_ids:
                    self._remove_notification(notification_id)

                if expired_ids:
                    logger.info(f"Cleaned up {len(expired_ids)} expired notifications")

            except Exception as e:
                logger.error(f"Error in notification cleanup: {e}")

    def create_notification(
        self,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        user_id: Optional[str] = None,
        target_groups: Optional[Set[str]] = None,
        data: Optional[Dict[str, Any]] = None,
        expires_in: Optional[int] = None,  # seconds
        actions: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[Set[str]] = None,
        persistent: bool = True,
    ) -> Notification:
        """Create a new notification."""
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            user_id=user_id,
            target_groups=target_groups or set(),
            data=data or {},
            expires_at=time.time() + expires_in if expires_in else None,
            actions=actions or [],
            tags=tags or set(),
            persistent=persistent,
        )

        self.notifications[notification.id] = notification

        # Add to user notifications if targeted to specific user
        if user_id:
            if user_id not in self.user_notifications:
                self.user_notifications[user_id] = []
            self.user_notifications[user_id].append(notification.id)

        logger.info(f"Created notification: {notification.id} - {title}")
        return notification

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Get notification by ID."""
        return self.notifications.get(notification_id)

    def _remove_notification(self, notification_id: str) -> None:
        """Remove notification from all storage."""
        notification = self.notifications.pop(notification_id, None)
        if not notification:
            return

        # Remove from user notifications
        for user_id, notification_ids in self.user_notifications.items():
            if notification_id in notification_ids:
                notification_ids.remove(notification_id)

    def get_user_subscription(self, user_id: str) -> NotificationSubscription:
        """Get user notification subscription preferences."""
        if user_id not in self.subscriptions:
            self.subscriptions[user_id] = NotificationSubscription(user_id=user_id)
        return self.subscriptions[user_id]

    def update_user_subscription(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> NotificationSubscription:
        """Update user notification preferences."""
        subscription = self.get_user_subscription(user_id)

        if "notification_types" in preferences:
            subscription.notification_types = {
                NotificationType(t) for t in preferences["notification_types"]
            }

        if "priority_filter" in preferences:
            subscription.priority_filter = NotificationPriority(preferences["priority_filter"])

        if "tags_filter" in preferences:
            subscription.tags_filter = set(preferences["tags_filter"])

        if "groups" in preferences:
            subscription.groups = set(preferences["groups"])

        if "quiet_hours_start" in preferences:
            subscription.quiet_hours_start = preferences["quiet_hours_start"]

        if "quiet_hours_end" in preferences:
            subscription.quiet_hours_end = preferences["quiet_hours_end"]

        if "enabled" in preferences:
            subscription.enabled = preferences["enabled"]

        if "max_notifications_per_hour" in preferences:
            subscription.max_notifications_per_hour = preferences["max_notifications_per_hour"]

        logger.info(f"Updated subscription preferences for user {user_id}")
        return subscription

    async def send_notification(self, notification: Notification) -> Dict[str, int]:
        """Send notification to appropriate users."""
        sent_count = 0
        delivered_count = 0
        filtered_count = 0

        # Determine target users
        target_users = set()

        if notification.user_id:
            target_users.add(notification.user_id)

        if notification.target_groups:
            for group in notification.target_groups:
                # Get users in groups (implementation depends on your user
                # management)
                group_users = self._get_users_in_group(group)
                target_users.update(group_users)

        # If no specific targets, broadcast to all connected users
        if not target_users:
            connections = default_connection_manager._connections.values()
            target_users = {
                conn.info.user_id
                for conn in connections
                if conn.info.authenticated and conn.info.user_id
            }

        # Send to each target user
        for user_id in target_users:
            subscription = self.get_user_subscription(user_id)

            # Check if user should receive this notification
            if not subscription.should_receive(notification):
                filtered_count += 1
                continue

            # Check rate limits
            if not self._check_rate_limit(user_id, subscription.max_notifications_per_hour):
                filtered_count += 1
                continue

            # Send notification
            success = await self._send_to_user(user_id, notification)
            if success:
                sent_count += 1
                notification.mark_delivered(user_id)
                delivered_count += 1

        # Update delivery stats
        stats = {
            "sent": sent_count,
            "delivered": delivered_count,
            "filtered": filtered_count,
            "total_targets": len(target_users),
        }

        self.delivery_stats[notification.id] = stats

        logger.info(f"Notification {notification.id} delivery: {stats}")
        return stats

    async def _send_to_user(self, user_id: str, notification: Notification) -> bool:
        """Send notification to a specific user."""
        try:
            message_data = {
                "type": "notification",
                "notification": notification.to_dict(),
            }

            await default_connection_manager.broadcast_to_user(
                user_id, JSONMessage(data=message_data)
            )
            return True

        except Exception as e:
            logger.error(f"Error sending notification to user {user_id}: {e}")
            return False

    def _get_users_in_group(self, group: str) -> Set[str]:
        """Get users in a specific group."""
        # This is a simple implementation - in practice, you'd integrate with
        # your user management system
        users = set()

        for user_id, subscription in self.subscriptions.items():
            if group in subscription.groups:
                users.add(user_id)

        return users

    def _check_rate_limit(self, user_id: str, max_per_hour: int) -> bool:
        """Check if user is within notification rate limits."""
        # Simple rate limiting - in practice, you might use a more
        # sophisticated approach
        current_time = time.time()
        one_hour_ago = current_time - 3600

        # Count notifications sent to user in the last hour
        user_notification_ids = self.user_notifications.get(user_id, [])
        recent_count = 0

        for notification_id in user_notification_ids:
            notification = self.notifications.get(notification_id)
            if notification and notification.created_at > one_hour_ago:
                if user_id in notification.delivered_to:
                    recent_count += 1

        return recent_count < max_per_hour

    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 50,
        include_read: bool = True,
        types_filter: Optional[List[NotificationType]] = None,
        priority_filter: Optional[NotificationPriority] = None,
    ) -> List[Dict[str, Any]]:
        """Get notifications for a specific user."""
        user_notification_ids = self.user_notifications.get(user_id, [])
        notifications = []

        for notification_id in reversed(user_notification_ids[-limit:]):
            notification = self.notifications.get(notification_id)
            if not notification or notification.is_expired():
                continue

            # Apply filters
            if not include_read and notification.is_read_by(user_id):
                continue

            if types_filter and notification.notification_type not in types_filter:
                continue

            if priority_filter and notification.priority.value < priority_filter.value:
                continue

            notifications.append(notification.to_dict())

        return notifications

    def mark_notification_read(self, user_id: str, notification_id: str) -> bool:
        """Mark notification as read by user."""
        notification = self.notifications.get(notification_id)
        if not notification:
            return False

        notification.mark_read(user_id)
        logger.info(f"Notification {notification_id} marked as read by {user_id}")
        return True

    def mark_all_read(self, user_id: str) -> int:
        """Mark all notifications as read for user."""
        user_notification_ids = self.user_notifications.get(user_id, [])
        marked_count = 0

        for notification_id in user_notification_ids:
            notification = self.notifications.get(notification_id)
            if notification and not notification.is_read_by(user_id):
                notification.mark_read(user_id)
                marked_count += 1

        logger.info(f"Marked {marked_count} notifications as read for user {user_id}")
        return marked_count

    def get_statistics(self) -> Dict[str, Any]:
        """Get notification system statistics."""
        total_notifications = len(self.notifications)
        active_notifications = sum(1 for n in self.notifications.values() if not n.is_expired())

        return {
            "total_notifications": total_notifications,
            "active_notifications": active_notifications,
            "expired_notifications": total_notifications - active_notifications,
            "total_users": len(self.subscriptions),
            "notification_types": {
                t.value: sum(1 for n in self.notifications.values() if n.notification_type == t)
                for t in NotificationType
            },
            "priority_distribution": {
                p.value: sum(1 for n in self.notifications.values() if n.priority == p)
                for p in NotificationPriority
            },
            "delivery_stats": self.delivery_stats,
        }


# Global notification manager
notification_manager = NotificationManager()


class NotificationEndpoint(WebSocketEndpoint):
    """WebSocket endpoint for notification functionality."""

    def __init__(self):
        super().__init__()
        self.notification_manager = notification_manager

    @on_connect
    async def handle_connect(self, connection: WebSocketConnection):
        """Handle new connection."""
        await connection.accept()

        # Send welcome message
        await connection.send_json(
            {
                "type": "connected",
                "message": "Connected to notification service",
                "server_time": time.time(),
            }
        )

        logger.info(f"New notification connection: {connection.info.id}")

    @on_disconnect
    async def handle_disconnect(self, connection: WebSocketConnection):
        """Handle connection disconnect."""
        logger.info(f"Notification connection disconnected: {connection.info.id}")

    @on_json
    async def handle_message(self, connection: WebSocketConnection, message):
        """Handle JSON message."""
        try:
            data = message.data
            msg_type = data.get("type")

            if msg_type == "authenticate":
                await self._handle_authenticate(connection, data)
            elif msg_type == "get_notifications":
                await self._handle_get_notifications(connection, data)
            elif msg_type == "mark_read":
                await self._handle_mark_read(connection, data)
            elif msg_type == "mark_all_read":
                await self._handle_mark_all_read(connection, data)
            elif msg_type == "update_preferences":
                await self._handle_update_preferences(connection, data)
            elif msg_type == "get_preferences":
                await self._handle_get_preferences(connection, data)
            elif msg_type == "send_notification":
                await self._handle_send_notification(connection, data)
            elif msg_type == "get_statistics":
                await self._handle_get_statistics(connection, data)
            else:
                await connection.send_json(
                    {"type": "error", "message": f"Unknown message type: {msg_type}"}
                )

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await connection.send_json({"type": "error", "message": "Failed to process message"})

    async def _handle_authenticate(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle user authentication."""
        user_id = data.get("user_id")

        if not user_id:
            await connection.send_json({"type": "error", "message": "User ID required"})
            return

        # Simple authentication (in production, validate credentials)
        connection.authenticate(user_id, metadata={"user_id": user_id})

        # Get user preferences
        subscription = self.notification_manager.get_user_subscription(user_id)

        await connection.send_json(
            {
                "type": "authenticated",
                "user_id": user_id,
                "preferences": {
                    "notification_types": [t.value for t in subscription.notification_types],
                    "priority_filter": subscription.priority_filter.value,
                    "tags_filter": list(subscription.tags_filter),
                    "groups": list(subscription.groups),
                    "quiet_hours_start": subscription.quiet_hours_start,
                    "quiet_hours_end": subscription.quiet_hours_end,
                    "enabled": subscription.enabled,
                    "max_notifications_per_hour": subscription.max_notifications_per_hour,
                },
            }
        )

        # Send pending notifications
        pending_notifications = self.notification_manager.get_user_notifications(
            user_id, limit=10, include_read=False
        )

        if pending_notifications:
            await connection.send_json(
                {
                    "type": "pending_notifications",
                    "notifications": pending_notifications,
                    "count": len(pending_notifications),
                }
            )

        logger.info(f"User authenticated for notifications: {user_id}")

    async def _handle_get_notifications(
        self, connection: WebSocketConnection, data: Dict[str, Any]
    ):
        """Handle get notifications request."""
        if not connection.info.authenticated:
            await connection.send_json({"type": "error", "message": "Authentication required"})
            return

        limit = data.get("limit", 50)
        include_read = data.get("include_read", True)
        types_filter = data.get("types_filter")
        priority_filter = data.get("priority_filter")

        # Convert string filters to enums
        enum_types_filter = None
        if types_filter:
            enum_types_filter = [NotificationType(t) for t in types_filter]

        enum_priority_filter = None
        if priority_filter:
            enum_priority_filter = NotificationPriority(priority_filter)

        notifications = self.notification_manager.get_user_notifications(
            connection.info.user_id,
            limit=limit,
            include_read=include_read,
            types_filter=enum_types_filter,
            priority_filter=enum_priority_filter,
        )

        await connection.send_json(
            {
                "type": "notifications",
                "notifications": notifications,
                "count": len(notifications),
            }
        )

    async def _handle_mark_read(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle mark notification as read."""
        if not connection.info.authenticated:
            return

        notification_id = data.get("notification_id")
        if not notification_id:
            return

        success = self.notification_manager.mark_notification_read(
            connection.info.user_id, notification_id
        )

        await connection.send_json(
            {
                "type": "marked_read",
                "notification_id": notification_id,
                "success": success,
            }
        )

    async def _handle_mark_all_read(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle mark all notifications as read."""
        if not connection.info.authenticated:
            return

        marked_count = self.notification_manager.mark_all_read(connection.info.user_id)

        await connection.send_json({"type": "marked_all_read", "count": marked_count})

    async def _handle_update_preferences(
        self, connection: WebSocketConnection, data: Dict[str, Any]
    ):
        """Handle update notification preferences."""
        if not connection.info.authenticated:
            return

        preferences = data.get("preferences", {})
        subscription = self.notification_manager.update_user_subscription(
            connection.info.user_id, preferences
        )

        await connection.send_json(
            {
                "type": "preferences_updated",
                "preferences": {
                    "notification_types": [t.value for t in subscription.notification_types],
                    "priority_filter": subscription.priority_filter.value,
                    "tags_filter": list(subscription.tags_filter),
                    "groups": list(subscription.groups),
                    "quiet_hours_start": subscription.quiet_hours_start,
                    "quiet_hours_end": subscription.quiet_hours_end,
                    "enabled": subscription.enabled,
                    "max_notifications_per_hour": subscription.max_notifications_per_hour,
                },
            }
        )

    async def _handle_get_preferences(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get notification preferences."""
        if not connection.info.authenticated:
            return

        subscription = self.notification_manager.get_user_subscription(connection.info.user_id)

        await connection.send_json(
            {
                "type": "preferences",
                "preferences": {
                    "notification_types": [t.value for t in subscription.notification_types],
                    "priority_filter": subscription.priority_filter.value,
                    "tags_filter": list(subscription.tags_filter),
                    "groups": list(subscription.groups),
                    "quiet_hours_start": subscription.quiet_hours_start,
                    "quiet_hours_end": subscription.quiet_hours_end,
                    "enabled": subscription.enabled,
                    "max_notifications_per_hour": subscription.max_notifications_per_hour,
                },
            }
        )

    async def _handle_send_notification(
        self, connection: WebSocketConnection, data: Dict[str, Any]
    ):
        """Handle send notification request (for admins/system)."""
        # In production, add proper authorization checks

        title = data.get("title", "")
        message = data.get("message", "")
        notification_type = NotificationType(data.get("type", "info"))
        priority = NotificationPriority(data.get("priority", 2))
        user_id = data.get("user_id")
        target_groups = set(data.get("target_groups", []))
        expires_in = data.get("expires_in")

        if not title or not message:
            await connection.send_json({"type": "error", "message": "Title and message required"})
            return

        # Create and send notification
        notification = self.notification_manager.create_notification(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            user_id=user_id,
            target_groups=target_groups,
            expires_in=expires_in,
        )

        delivery_stats = await self.notification_manager.send_notification(notification)

        await connection.send_json(
            {
                "type": "notification_sent",
                "notification_id": notification.id,
                "delivery_stats": delivery_stats,
            }
        )

    async def _handle_get_statistics(self, connection: WebSocketConnection, data: Dict[str, Any]):
        """Handle get statistics request."""
        stats = self.notification_manager.get_statistics()

        await connection.send_json({"type": "statistics", "stats": stats})


# Create router and add notification endpoint
def create_notification_router() -> WebSocketRouter:
    """Create WebSocket router with notification endpoint."""
    router = WebSocketRouter()

    # Add notification endpoint
    router.add_route("/ws/notifications", NotificationEndpoint())

    return router


# Helper functions for creating common notifications
async def send_user_notification(
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    data: Optional[Dict[str, Any]] = None,
) -> Notification:
    """Send a notification to a specific user."""
    notification = notification_manager.create_notification(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        user_id=user_id,
        data=data,
    )

    await notification_manager.send_notification(notification)
    return notification


async def send_group_notification(
    target_groups: Set[str],
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    priority: NotificationPriority = NotificationPriority.NORMAL,
    data: Optional[Dict[str, Any]] = None,
) -> Notification:
    """Send a notification to specific groups."""
    notification = notification_manager.create_notification(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        target_groups=target_groups,
        data=data,
    )

    await notification_manager.send_notification(notification)
    return notification


async def send_broadcast_notification(
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.SYSTEM,
    priority: NotificationPriority = NotificationPriority.HIGH,
    data: Optional[Dict[str, Any]] = None,
) -> Notification:
    """Send a broadcast notification to all users."""
    notification = notification_manager.create_notification(
        title=title,
        message=message,
        notification_type=notification_type,
        priority=priority,
        data=data,
    )

    await notification_manager.send_notification(notification)
    return notification


# Example usage
async def run_notification_example():
    """Run the notification example."""
    from ..core.asgi import CovetPyASGI

    # Create router
    router = create_notification_router()

    # Example of sending some test notifications
    async def send_test_notifications():
        await asyncio.sleep(5)  # Wait for connections

        # Send some example notifications
        await send_broadcast_notification(
            "System Maintenance",
            "The system will undergo maintenance in 30 minutes",
            NotificationType.WARNING,
            NotificationPriority.HIGH,
        )

        await send_user_notification(
            "user_123",
            "Welcome!",
            "Welcome to our notification system!",
            NotificationType.SUCCESS,
            NotificationPriority.NORMAL,
        )

    # Start test notification task
    asyncio.create_task(send_test_notifications())

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
    logger.info("Notification WebSocket server ready at ws://localhost:8000/ws/notifications")
    logger.info("Connect and authenticate to receive real-time notifications!")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run example
    asyncio.run(run_notification_example())
