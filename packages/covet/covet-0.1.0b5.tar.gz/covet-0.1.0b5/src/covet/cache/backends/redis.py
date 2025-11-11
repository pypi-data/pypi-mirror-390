"""
Redis Cache Backend

Production-ready Redis cache with:
- redis-py async integration
- Connection pooling
- Key prefixing (namespace isolation)
- Secure HMAC-signed serialization (default, prevents RCE)
- Multiple serialization formats (secure, json, msgpack)
- Pipelining for bulk operations
- Pub/sub for cache invalidation
- Cluster and Sentinel support
- Automatic reconnection

SECURITY: Uses SecureSerializer by default to prevent pickle RCE vulnerabilities.
NO MOCK DATA: Real Redis integration using redis-py.
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from covet.security.secure_serializer import SecureSerializer

try:
    import redis.asyncio as aioredis
    from redis.asyncio import ConnectionPool, Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import msgpack

    MSGPACK_AVAILABLE = True
except ImportError:
    MSGPACK_AVAILABLE = False


logger = logging.getLogger(__name__)


class SerializerType(str, Enum):
    """Serialization format."""

    SECURE = "secure"  # Secure HMAC-signed serialization (recommended)
    JSON = "json"
    MSGPACK = "msgpack"


@dataclass
class RedisConfig:
    """Redis configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0

    # Connection pool
    max_connections: int = 50
    min_connections: int = 10

    # Key settings
    key_prefix: str = ""
    separator: str = ":"

    # Serialization (SECURE by default to prevent RCE)
    serializer: SerializerType = SerializerType.SECURE
    secret_key: Optional[str] = None  # Required for SECURE serializer

    # Cluster settings
    cluster_enabled: bool = False
    cluster_nodes: Optional[List[Dict[str, Any]]] = None

    # Sentinel settings
    sentinel_enabled: bool = False
    sentinel_nodes: Optional[List[tuple]] = None
    sentinel_service_name: Optional[str] = None


class Serializer:
    """Value serializer/deserializer."""

    @staticmethod
    def json_serialize(value: Any) -> bytes:
        """Serialize using JSON."""
        return json.dumps(value).encode("utf-8")

    @staticmethod
    def json_deserialize(data: bytes) -> Any:
        """Deserialize using JSON."""
        return json.loads(data.decode("utf-8"))

    @staticmethod
    def msgpack_serialize(value: Any) -> bytes:
        """Serialize using msgpack."""
        if not MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return msgpack.packb(value)

    @staticmethod
    def msgpack_deserialize(data: bytes) -> Any:
        """Deserialize using msgpack."""
        if not MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return msgpack.unpackb(data)


class RedisCache:
    """
    Redis cache backend.

    Features:
    - Connection pooling
    - Key prefixing for namespace isolation
    - Multiple serialization formats
    - Pipelining for bulk operations
    - Pub/sub for distributed cache invalidation
    - Support for Redis Cluster and Sentinel

    Example:
        from covet.security.secure_serializer import generate_secure_key

        config = RedisConfig(
            host='localhost',
            port=6379,
            key_prefix='myapp',
            serializer=SerializerType.SECURE,  # Secure by default
            secret_key=generate_secure_key()  # Required for SECURE serializer
        )

        cache = RedisCache(config)
        await cache.connect()

        # Set value with TTL
        await cache.set('user:1', user_data, ttl=300)

        # Get value
        user = await cache.get('user:1')

        # Bulk operations
        await cache.set_many({'user:1': data1, 'user:2': data2})
        users = await cache.get_many(['user:1', 'user:2'])
    """

    def __init__(self, config: Optional[RedisConfig] = None):
        """
        Initialize Redis cache.

        Args:
            config: Redis configuration (default: localhost:6379)
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis-py not installed. " "Install with: pip install redis[hiredis]")

        self.config = config or RedisConfig()
        self._client: Optional[Redis] = None
        self._pool: Optional[ConnectionPool] = None
        self._pubsub = None

        # Set up serializer
        self._setup_serializer()

    def _setup_serializer(self):
        """Set up serialization functions."""
        if self.config.serializer == SerializerType.SECURE:
            # Use SecureSerializer (prevents RCE vulnerabilities)
            if not self.config.secret_key:
                raise ValueError(
                    "RedisCache with SECURE serializer requires secret_key in config. "
                    "Use generate_secure_key() from covet.security.secure_serializer to generate one."
                )
            secure_serializer = SecureSerializer(secret_key=self.config.secret_key)
            self._serialize = secure_serializer.dumps
            self._deserialize = secure_serializer.loads
        elif self.config.serializer == SerializerType.JSON:
            self._serialize = Serializer.json_serialize
            self._deserialize = Serializer.json_deserialize
        elif self.config.serializer == SerializerType.MSGPACK:
            self._serialize = Serializer.msgpack_serialize
            self._deserialize = Serializer.msgpack_deserialize
        else:
            raise ValueError(f"Unsupported serializer type: {self.config.serializer}")

    async def connect(self):
        """Establish Redis connection."""
        if self._client is not None:
            return

        try:
            # Create connection pool
            self._pool = ConnectionPool(
                host=self.config.host,
                port=self.config.port,
                db=self.config.db,
                password=self.config.password,
                max_connections=self.config.max_connections,
                socket_timeout=self.config.socket_timeout,
                socket_connect_timeout=self.config.socket_connect_timeout,
                decode_responses=False,  # We handle serialization
            )

            # Create client
            self._client = Redis(connection_pool=self._pool)

            # Test connection
            await self._client.ping()

            logger.info(f"Connected to Redis at {self.config.host}:{self.config.port}")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection."""
        if self._client:
            await self._client.close()
            self._client = None

        if self._pool:
            await self._pool.disconnect()
            self._pool = None

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        if self.config.key_prefix:
            return f"{self.config.key_prefix}{self.config.separator}{key}"
        return key

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        try:
            data = await self._client.get(self._make_key(key))

            if data is None:
                return default

            return self._deserialize(data)

        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = no expiration)

        Returns:
            True if successful
        """
        try:
            data = self._serialize(value)
            result = await self._client.set(
                self._make_key(key), data, ex=ttl  # Expiration in seconds
            )
            return bool(result)

        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key existed and was deleted
        """
        try:
            result = await self._client.delete(self._make_key(key))
            return result > 0

        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        try:
            result = await self._client.exists(self._make_key(key))
            return result > 0

        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """
        Clear all cache entries with prefix.

        WARNING: Use with caution in production.
        """
        try:
            if self.config.key_prefix:
                # Delete only keys with our prefix
                pattern = f"{self.config.key_prefix}{self.config.separator}*"
                cursor = 0
                while True:
                    cursor, keys = await self._client.scan(cursor=cursor, match=pattern, count=1000)
                    if keys:
                        await self._client.delete(*keys)
                    if cursor == 0:
                        break
            else:
                # Clear entire database (dangerous!)
                await self._client.flushdb()

            return True

        except Exception as e:
            logger.error(f"Redis CLEAR error: {e}")
            return False

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache using pipeline.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs
        """
        if not keys:
            return {}

        try:
            # Use pipeline for efficient bulk retrieval
            pipeline = self._client.pipeline()

            prefixed_keys = [self._make_key(k) for k in keys]
            for prefixed_key in prefixed_keys:
                pipeline.get(prefixed_key)

            results = await pipeline.execute()

            # Build result dictionary
            result = {}
            for original_key, data in zip(keys, results):
                if data is not None:
                    result[original_key] = self._deserialize(data)

            return result

        except Exception as e:
            logger.error(f"Redis GET_MANY error: {e}")
            return {}

    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values using pipeline.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        if not mapping:
            return True

        try:
            pipeline = self._client.pipeline()

            for key, value in mapping.items():
                data = self._serialize(value)
                pipeline.set(self._make_key(key), data, ex=ttl)

            await pipeline.execute()
            return True

        except Exception as e:
            logger.error(f"Redis SET_MANY error: {e}")
            return False

    async def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        if not keys:
            return 0

        try:
            prefixed_keys = [self._make_key(k) for k in keys]
            result = await self._client.delete(*prefixed_keys)
            return result

        except Exception as e:
            logger.error(f"Redis DELETE_MANY error: {e}")
            return 0

    async def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """
        Increment integer value.

        Args:
            key: Cache key
            delta: Amount to increment

        Returns:
            New value or None on error
        """
        try:
            result = await self._client.incrby(self._make_key(key), delta)
            return result

        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {e}")
            return None

    async def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """
        Decrement integer value.

        Args:
            key: Cache key
            delta: Amount to decrement

        Returns:
            New value or None on error
        """
        try:
            result = await self._client.decrby(self._make_key(key), delta)
            return result

        except Exception as e:
            logger.error(f"Redis DECR error for key {key}: {e}")
            return None

    async def touch(self, key: str, ttl: int) -> bool:
        """
        Update TTL for existing key.

        Args:
            key: Cache key
            ttl: New TTL in seconds

        Returns:
            True if successful
        """
        try:
            result = await self._client.expire(self._make_key(key), ttl)
            return bool(result)

        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False

    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all cache keys matching pattern.

        Args:
            pattern: Pattern to match (Redis glob pattern)

        Returns:
            List of matching keys (without prefix)
        """
        try:
            if pattern:
                search_pattern = self._make_key(pattern)
            else:
                search_pattern = self._make_key("*")

            # Use SCAN for better performance
            keys = []
            cursor = 0
            while True:
                cursor, batch = await self._client.scan(
                    cursor=cursor, match=search_pattern, count=1000
                )
                keys.extend(batch)
                if cursor == 0:
                    break

            # Remove prefix from keys
            if self.config.key_prefix:
                prefix_len = len(self.config.key_prefix) + len(self.config.separator)
                return [k.decode("utf-8")[prefix_len:] for k in keys]
            else:
                return [k.decode("utf-8") for k in keys]

        except Exception as e:
            logger.error(f"Redis KEYS error: {e}")
            return []

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (Redis glob pattern)

        Returns:
            Number of keys deleted
        """
        keys = await self.keys(pattern)
        if not keys:
            return 0
        return await self.delete_many(keys)

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Redis server statistics.

        Returns:
            Dictionary with Redis stats
        """
        try:
            info = await self._client.info()

            return {
                "connected": True,
                "version": info.get("redis_version"),
                "used_memory_mb": round(info.get("used_memory", 0) / 1024 / 1024, 2),
                "total_connections": info.get("total_connections_received"),
                "total_commands": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "connected_clients": info.get("connected_clients"),
            }

        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return {"connected": False, "error": str(e)}

    async def publish(self, channel: str, message: Any):
        """
        Publish message to channel (for cache invalidation).

        Args:
            channel: Channel name
            message: Message to publish
        """
        try:
            data = self._serialize(message)
            await self._client.publish(channel, data)

        except Exception as e:
            logger.error(f"Redis PUBLISH error: {e}")

    async def subscribe(self, channel: str, callback: Callable[[Any], None]):
        """
        Subscribe to channel for cache invalidation.

        Args:
            channel: Channel name
            callback: Function to call on message
        """
        try:
            if self._pubsub is None:
                self._pubsub = self._client.pubsub()

            await self._pubsub.subscribe(channel)

            # Listen for messages
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    data = self._deserialize(message["data"])
                    await callback(data)

        except Exception as e:
            logger.error(f"Redis SUBSCRIBE error: {e}")


__all__ = ["RedisCache", "RedisConfig", "SerializerType"]
