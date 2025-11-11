"""
WebSocket Pub/Sub System

Real-time pub/sub system for WebSocket broadcasting.
Integrates with existing WebSocket framework and GraphQL subscriptions.
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Set

from .connection import WebSocketConnection, WebSocketConnectionManager

logger = logging.getLogger(__name__)


@dataclass
class Channel:
    """Pub/sub channel."""

    name: str
    subscribers: Set[str] = field(default_factory=set)  # connection IDs
    message_count: int = 0

    def add_subscriber(self, connection_id: str):
        """Add subscriber to channel."""
        self.subscribers.add(connection_id)

    def remove_subscriber(self, connection_id: str):
        """Remove subscriber from channel."""
        self.subscribers.discard(connection_id)

    @property
    def subscriber_count(self) -> int:
        """Get number of subscribers."""
        return len(self.subscribers)


class WebSocketPubSub:
    """
    WebSocket-based pub/sub system.

    Provides real-time broadcasting to WebSocket clients via channels.
    Integrates with WebSocketConnectionManager for connection management.

    Example:
        pubsub = WebSocketPubSub(connection_manager)

        # Subscribe connection to channel
        await pubsub.subscribe(connection_id, 'news')

        # Publish message to channel
        await pubsub.publish('news', {'title': 'Breaking News!'})

        # Publish with filter
        await pubsub.publish(
            'notifications',
            {'message': 'Hello'},
            filter_fn=lambda conn: conn.user_id == 'user123'
        )
    """

    def __init__(self, connection_manager: WebSocketConnectionManager):
        """
        Initialize pub/sub system.

        Args:
            connection_manager: WebSocket connection manager
        """
        self.connection_manager = connection_manager
        self.channels: Dict[str, Channel] = {}
        self._lock = asyncio.Lock()

    def _get_channel(self, channel_name: str) -> Channel:
        """Get or create channel."""
        if channel_name not in self.channels:
            self.channels[channel_name] = Channel(name=channel_name)
        return self.channels[channel_name]

    async def subscribe(self, connection_id: str, channel: str):
        """
        Subscribe connection to channel.

        Args:
            connection_id: Connection ID
            channel: Channel name
        """
        async with self._lock:
            ch = self._get_channel(channel)
            ch.add_subscriber(connection_id)

        logger.debug(f"Connection {connection_id} subscribed to {channel}")

    async def unsubscribe(self, connection_id: str, channel: str):
        """
        Unsubscribe connection from channel.

        Args:
            connection_id: Connection ID
            channel: Channel name
        """
        async with self._lock:
            if channel in self.channels:
                self.channels[channel].remove_subscriber(connection_id)

        logger.debug(f"Connection {connection_id} unsubscribed from {channel}")

    async def unsubscribe_all(self, connection_id: str):
        """
        Unsubscribe connection from all channels.

        Args:
            connection_id: Connection ID
        """
        async with self._lock:
            for channel in self.channels.values():
                channel.remove_subscriber(connection_id)

    async def publish(
        self,
        channel: str,
        message: Any,
        filter_fn: Optional[Callable[[WebSocketConnection], bool]] = None,
    ):
        """
        Publish message to channel.

        Args:
            channel: Channel name
            message: Message to publish (will be JSON serialized)
            filter_fn: Optional filter function for subscribers
        """
        async with self._lock:
            if channel not in self.channels:
                logger.debug(f"No subscribers for channel {channel}")
                return

            ch = self.channels[channel]
            subscribers = list(ch.subscribers)
            ch.message_count += 1

        # Serialize message
        if isinstance(message, (dict, list)):
            serialized = json.dumps(message)
        elif isinstance(message, str):
            serialized = message
        else:
            serialized = str(message)

        # Send to subscribers
        sent_count = 0
        for connection_id in subscribers:
            connection = self.connection_manager.get_connection(connection_id)
            if connection is None:
                # Connection no longer exists, cleanup
                async with self._lock:
                    ch.remove_subscriber(connection_id)
                continue

            # Apply filter if provided
            if filter_fn and not filter_fn(connection):
                continue

            try:
                await connection.send(serialized)
                sent_count += 1
            except Exception as e:
                logger.error(f"Error sending to {connection_id}: {e}")

        logger.debug(f"Published to {channel}: {sent_count} recipients")

    async def publish_json(
        self,
        channel: str,
        data: Dict[str, Any],
        filter_fn: Optional[Callable[[WebSocketConnection], bool]] = None,
    ):
        """
        Publish JSON data to channel.

        Args:
            channel: Channel name
            data: Dictionary to publish
            filter_fn: Optional filter function
        """
        await self.publish(channel, data, filter_fn)

    async def publish_to_user(self, user_id: str, message: Any):
        """
        Publish message to all connections of a user.

        Args:
            user_id: User ID
            message: Message to publish
        """
        connections = self.connection_manager.get_user_connections(user_id)

        # Serialize message
        if isinstance(message, (dict, list)):
            serialized = json.dumps(message)
        elif isinstance(message, str):
            serialized = message
        else:
            serialized = str(message)

        # Send to all user connections
        for connection in connections:
            try:
                await connection.send(serialized)
            except Exception as e:
                logger.error(f"Error sending to connection {connection.id}: {e}")

    def get_channel_info(self, channel: str) -> Optional[Dict[str, Any]]:
        """Get channel information."""
        if channel in self.channels:
            ch = self.channels[channel]
            return {
                "name": ch.name,
                "subscribers": ch.subscriber_count,
                "messages": ch.message_count,
            }
        return None

    def get_all_channels(self) -> List[Dict[str, Any]]:
        """Get information about all channels."""
        return [self.get_channel_info(name) for name in self.channels.keys()]

    def get_connection_channels(self, connection_id: str) -> List[str]:
        """Get channels a connection is subscribed to."""
        channels = []
        for channel_name, channel in self.channels.items():
            if connection_id in channel.subscribers:
                channels.append(channel_name)
        return channels


# Integration with GraphQL subscriptions
def create_graphql_subscription_pubsub(connection_manager: WebSocketConnectionManager):
    """
    Create pub/sub system for GraphQL subscriptions.

    Args:
        connection_manager: WebSocket connection manager

    Returns:
        WebSocketPubSub instance configured for GraphQL
    """
    return WebSocketPubSub(connection_manager)


__all__ = [
    "WebSocketPubSub",
    "Channel",
    "create_graphql_subscription_pubsub",
]
