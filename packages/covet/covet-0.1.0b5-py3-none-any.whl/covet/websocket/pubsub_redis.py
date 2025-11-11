"""
Redis-Backed WebSocket Pub/Sub System

This module provides Redis-backed pub/sub for multi-server WebSocket deployments:
- Redis backend for message passing across servers
- Subscribe to topics with pattern matching
- Publish to topics (cross-server broadcast)
- Pattern subscriptions with wildcards
- Message serialization and deserialization
- Connection pooling
- Failover and reconnection
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set

try:
    import redis.asyncio as redis
    from redis.asyncio.client import PubSub

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None
    PubSub = None

from .connection import WebSocketConnectionManager
from .protocol import BinaryMessage, JSONMessage, TextMessage

logger = logging.getLogger(__name__)


@dataclass
class RedisConfig:
    """Redis configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 50
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    retry_on_timeout: bool = True
    health_check_interval: int = 30


class RedisBackendError(Exception):
    """Redis backend error."""

    pass


class RedisWebSocketPubSub:
    """
    Redis-backed pub/sub system for WebSocket connections.

    Enables horizontal scaling by allowing multiple WebSocket servers
    to share state and broadcast messages via Redis.

    Example:
        # Server 1
        pubsub = RedisWebSocketPubSub(connection_manager, redis_config)
        await pubsub.subscribe("chat:*")
        await pubsub.publish("chat:room1", {"message": "Hello!"})

        # Server 2 (different server)
        # Will receive the message from Server 1
        pubsub2 = RedisWebSocketPubSub(connection_manager2, redis_config)
        await pubsub2.subscribe("chat:*")
    """

    def __init__(
        self,
        connection_manager: WebSocketConnectionManager,
        redis_config: Optional[RedisConfig] = None,
    ):
        """
        Initialize Redis-backed pub/sub.

        Args:
            connection_manager: WebSocket connection manager
            redis_config: Redis configuration

        Raises:
            ImportError: If redis package not installed
        """
        if not HAS_REDIS:
            raise ImportError(
                "redis package required for Redis pub/sub. " "Install with: pip install redis"
            )

        self.connection_manager = connection_manager
        self.config = redis_config or RedisConfig()

        # Redis clients
        self._redis: Optional[redis.Redis] = None
        self._pubsub: Optional[PubSub] = None

        # Subscriptions
        self._subscriptions: Set[str] = set()
        self._pattern_subscriptions: Set[str] = set()
        self._message_handlers: Dict[str, List[Callable]] = {}

        # Background tasks
        self._listener_task: Optional[asyncio.Task] = None
        self._shutdown = False

        # Statistics
        self.messages_published = 0
        self.messages_received = 0
        self.connection_errors = 0

    async def connect(self):
        """Connect to Redis."""
        try:
            self._redis = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                retry_on_timeout=self.config.retry_on_timeout,
                health_check_interval=self.config.health_check_interval,
                decode_responses=False,  # We handle encoding/decoding
            )

            # Test connection
            await self._redis.ping()

            # Create pub/sub
            self._pubsub = self._redis.pubsub()

            # Start listener task
            self._listener_task = asyncio.create_task(self._message_listener())

            logger.info(
                f"Connected to Redis at {self.config.host}:{self.config.port} "
                f"(db={self.config.db})"
            )

        except Exception as e:
            self.connection_errors += 1
            logger.error(f"Failed to connect to Redis: {e}")
            raise RedisBackendError(f"Redis connection failed: {e}")

    async def disconnect(self):
        """Disconnect from Redis."""
        self._shutdown = True

        # Cancel listener task
        if self._listener_task:
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass

        # Unsubscribe from all channels
        if self._pubsub:
            await self._pubsub.unsubscribe(*self._subscriptions)
            await self._pubsub.punsubscribe(*self._pattern_subscriptions)
            await self._pubsub.close()

        # Close Redis connection
        if self._redis:
            await self._redis.close()
            await self._redis.connection_pool.disconnect()

        logger.info("Disconnected from Redis")

    async def subscribe(self, channel: str, handler: Optional[Callable] = None):
        """
        Subscribe to a Redis channel.

        Args:
            channel: Channel name (can include wildcards for patterns)
            handler: Optional message handler (called for each message)
        """
        if not self._pubsub:
            raise RedisBackendError("Not connected to Redis")

        try:
            # Check if pattern subscription
            if "*" in channel or "?" in channel or "[" in channel:
                await self._pubsub.psubscribe(channel)
                self._pattern_subscriptions.add(channel)
                logger.info(f"Subscribed to pattern: {channel}")
            else:
                await self._pubsub.subscribe(channel)
                self._subscriptions.add(channel)
                logger.info(f"Subscribed to channel: {channel}")

            # Register handler
            if handler:
                if channel not in self._message_handlers:
                    self._message_handlers[channel] = []
                self._message_handlers[channel].append(handler)

        except Exception as e:
            logger.error(f"Failed to subscribe to {channel}: {e}")
            raise RedisBackendError(f"Subscribe failed: {e}")

    async def unsubscribe(self, channel: str):
        """
        Unsubscribe from a Redis channel.

        Args:
            channel: Channel name
        """
        if not self._pubsub:
            return

        try:
            if channel in self._pattern_subscriptions:
                await self._pubsub.punsubscribe(channel)
                self._pattern_subscriptions.discard(channel)
            elif channel in self._subscriptions:
                await self._pubsub.unsubscribe(channel)
                self._subscriptions.discard(channel)

            # Remove handlers
            self._message_handlers.pop(channel, None)

            logger.info(f"Unsubscribed from channel: {channel}")

        except Exception as e:
            logger.error(f"Failed to unsubscribe from {channel}: {e}")

    async def publish(
        self,
        channel: str,
        message: Any,
        serialize: bool = True,
    ) -> int:
        """
        Publish message to a Redis channel.

        Args:
            channel: Channel name
            message: Message to publish
            serialize: Whether to JSON-serialize the message

        Returns:
            Number of subscribers who received the message

        Raises:
            RedisBackendError: If publish fails
        """
        if not self._redis:
            raise RedisBackendError("Not connected to Redis")

        try:
            # Serialize message
            if serialize:
                if isinstance(message, (dict, list)):
                    serialized = json.dumps(message)
                elif isinstance(message, str):
                    serialized = message
                else:
                    serialized = str(message)
            else:
                serialized = message

            # Publish to Redis
            subscriber_count = await self._redis.publish(channel, serialized)

            self.messages_published += 1

            logger.debug(f"Published to {channel}: {subscriber_count} subscribers")

            return subscriber_count

        except Exception as e:
            logger.error(f"Failed to publish to {channel}: {e}")
            raise RedisBackendError(f"Publish failed: {e}")

    async def publish_json(self, channel: str, data: Dict[str, Any]) -> int:
        """
        Publish JSON data to a channel.

        Args:
            channel: Channel name
            data: Dictionary to publish

        Returns:
            Number of subscribers
        """
        return await self.publish(channel, data, serialize=True)

    async def broadcast_to_channel(
        self,
        channel: str,
        message: Any,
    ) -> int:
        """
        Broadcast message to all local WebSocket connections and Redis.

        This publishes to Redis (for other servers) and also broadcasts
        to local connections immediately.

        Args:
            channel: Channel name
            message: Message to broadcast

        Returns:
            Number of local connections who received the message
        """
        # Publish to Redis (for other servers)
        await self.publish(channel, message)

        # Broadcast to local connections
        # Map channel to room (assuming channel == room name)
        if isinstance(message, str):
            ws_message = TextMessage(message)
        elif isinstance(message, bytes):
            ws_message = BinaryMessage(message)
        elif isinstance(message, dict):
            ws_message = JSONMessage(message)
        else:
            ws_message = TextMessage(str(message))

        return await self.connection_manager.broadcast_to_room(channel, ws_message)

    async def _message_listener(self):
        """Background task to listen for Redis messages."""
        logger.info("Started Redis message listener")

        while not self._shutdown:
            try:
                if not self._pubsub:
                    await asyncio.sleep(1)
                    continue

                # Get message with timeout
                message = await asyncio.wait_for(
                    self._pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0),
                    timeout=2.0,
                )

                if message and message["type"] in ["message", "pmessage"]:
                    await self._handle_redis_message(message)

            except asyncio.TimeoutError:
                # No message, continue
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in message listener: {e}")
                await asyncio.sleep(1)

        logger.info("Stopped Redis message listener")

    async def _handle_redis_message(self, redis_message: Dict[str, Any]):
        """Handle incoming Redis message."""
        try:
            self.messages_received += 1

            # Extract channel and data
            if redis_message["type"] == "pmessage":
                # Pattern subscription
                pattern = redis_message["pattern"].decode("utf-8")
                channel = redis_message["channel"].decode("utf-8")
                data = redis_message["data"]
            else:
                # Regular subscription
                channel = redis_message["channel"].decode("utf-8")
                data = redis_message["data"]
                pattern = None

            # Decode data
            if isinstance(data, bytes):
                data = data.decode("utf-8")

            # Try to parse as JSON
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                # Not JSON, keep as string
                pass

            logger.debug(f"Received Redis message on {channel}: {data}")

            # Call registered handlers
            handlers = []
            if channel in self._message_handlers:
                handlers.extend(self._message_handlers[channel])
            if pattern and pattern in self._message_handlers:
                handlers.extend(self._message_handlers[pattern])

            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(channel, data)
                    else:
                        handler(channel, data)
                except Exception as e:
                    logger.error(f"Error in message handler: {e}")

            # Broadcast to local WebSocket connections
            # Map Redis channel to room name
            await self._broadcast_to_local_connections(channel, data)

        except Exception as e:
            logger.error(f"Error handling Redis message: {e}")

    async def _broadcast_to_local_connections(self, channel: str, data: Any):
        """Broadcast Redis message to local WebSocket connections."""
        try:
            # Map channel to room (assuming channel == room name)
            # Convert data to WebSocket message
            if isinstance(data, str):
                ws_message = TextMessage(data)
            elif isinstance(data, bytes):
                ws_message = BinaryMessage(data)
            elif isinstance(data, dict):
                ws_message = JSONMessage(data)
            else:
                ws_message = TextMessage(str(data))

            # Broadcast to room
            sent_count = await self.connection_manager.broadcast_to_room(channel, ws_message)

            logger.debug(
                f"Broadcast Redis message to {sent_count} local connections " f"in room {channel}"
            )

        except Exception as e:
            logger.error(f"Error broadcasting to local connections: {e}")

    def get_subscriptions(self) -> Dict[str, Any]:
        """Get current subscriptions."""
        return {
            "channels": list(self._subscriptions),
            "patterns": list(self._pattern_subscriptions),
            "total": len(self._subscriptions) + len(self._pattern_subscriptions),
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get pub/sub statistics."""
        return {
            "connected": self._redis is not None and not self._shutdown,
            "redis_host": f"{self.config.host}:{self.config.port}",
            "redis_db": self.config.db,
            "subscriptions": self.get_subscriptions(),
            "messages_published": self.messages_published,
            "messages_received": self.messages_received,
            "connection_errors": self.connection_errors,
        }


# Convenience functions
async def create_redis_pubsub(
    connection_manager: WebSocketConnectionManager,
    redis_host: str = "localhost",
    redis_port: int = 6379,
    redis_password: Optional[str] = None,
) -> RedisWebSocketPubSub:
    """
    Create and connect Redis pub/sub system.

    Args:
        connection_manager: WebSocket connection manager
        redis_host: Redis host
        redis_port: Redis port
        redis_password: Optional Redis password

    Returns:
        Connected RedisWebSocketPubSub instance
    """
    config = RedisConfig(
        host=redis_host,
        port=redis_port,
        password=redis_password,
    )

    pubsub = RedisWebSocketPubSub(connection_manager, config)
    await pubsub.connect()
    return pubsub


__all__ = [
    "RedisConfig",
    "RedisBackendError",
    "RedisWebSocketPubSub",
    "create_redis_pubsub",
    "HAS_REDIS",
]
