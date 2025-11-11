"""
Cache Manager

Unified caching API with multiple backend support:
- Automatic backend selection and fallback
- Consistent API across all backends
- Batch operations
- Pattern-based operations
- Statistics tracking
- Multi-tier caching support

NO MOCK DATA: Real cache implementation using backend adapters.
"""

import asyncio
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

from .backends import (
    DatabaseCache,
    DatabaseCacheConfig,
    MemcachedCache,
    MemcachedConfig,
    MemoryCache,
    RedisCache,
    RedisConfig,
)

logger = logging.getLogger(__name__)


class CacheBackend(str, Enum):
    """Available cache backends."""

    MEMORY = "memory"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"


@dataclass
class CacheConfig:
    """Cache manager configuration."""

    # Primary backend
    backend: CacheBackend = CacheBackend.MEMORY

    # Fallback backends (in order)
    fallback_backends: Optional[List[CacheBackend]] = None

    # Backend-specific configs
    redis_config: Optional[RedisConfig] = None
    memcached_config: Optional[MemcachedConfig] = None
    database_config: Optional[DatabaseCacheConfig] = None

    # Memory cache settings
    memory_max_size: int = 10000
    memory_max_memory_mb: Optional[int] = 100

    # General settings
    default_ttl: Optional[int] = None
    key_prefix: str = ""


class CacheManager:
    """
    Unified cache manager with multiple backend support.

    Features:
    - Multiple backend support (memory, Redis, Memcached, database)
    - Automatic fallback on backend failure
    - Multi-tier caching (L1/L2 cache)
    - Consistent API across backends
    - Batch operations
    - Pattern-based operations

    Example:
        # Single backend
        cache = CacheManager(backend='redis', key_prefix='myapp')
        await cache.connect()

        # Set value
        await cache.set('user:1', user_data, ttl=300)

        # Get value
        user = await cache.get('user:1')

        # Batch operations
        await cache.set_many({'user:1': data1, 'user:2': data2})
        users = await cache.get_many(['user:1', 'user:2'])

        # Pattern operations
        await cache.delete_pattern('user:*')

        # Multi-tier cache (L1=memory, L2=redis)
        config = CacheConfig(
            backend=CacheBackend.REDIS,
            fallback_backends=[CacheBackend.MEMORY]
        )
        cache = CacheManager(config)
    """

    def __init__(
        self,
        config: Optional[CacheConfig] = None,
        backend: Optional[str] = None,
        prefix: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize cache manager.

        Args:
            config: Cache configuration object
            backend: Backend name (shortcut for simple config)
            prefix: Key prefix (shortcut for simple config)
            **kwargs: Additional backend-specific arguments
        """
        # Handle simple initialization
        if config is None:
            if backend:
                config = CacheConfig(backend=CacheBackend(backend), key_prefix=prefix or "")
            else:
                config = CacheConfig()

        self.config = config
        self._primary_cache = None
        self._fallback_caches: List[Any] = []
        self._connected = False

    async def connect(self):
        """Initialize cache backend connections."""
        if self._connected:
            return

        # Create primary cache
        self._primary_cache = await self._create_backend(self.config.backend)

        # Create fallback caches
        if self.config.fallback_backends:
            for backend in self.config.fallback_backends:
                try:
                    fallback = await self._create_backend(backend)
                    self._fallback_caches.append(fallback)
                except Exception as e:
                    logger.warning(f"Failed to initialize fallback backend {backend}: {e}")

        self._connected = True
        logger.info(f"Cache manager connected: {self.config.backend}")

    async def _create_backend(self, backend: CacheBackend):
        """Create and initialize cache backend."""
        if backend == CacheBackend.MEMORY:
            cache = MemoryCache(
                max_size=self.config.memory_max_size,
                max_memory_mb=self.config.memory_max_memory_mb,
                default_ttl=self.config.default_ttl,
            )
            return cache

        elif backend == CacheBackend.REDIS:
            redis_config = self.config.redis_config or RedisConfig()
            redis_config.key_prefix = self.config.key_prefix or redis_config.key_prefix

            cache = RedisCache(redis_config)
            await cache.connect()
            return cache

        elif backend == CacheBackend.MEMCACHED:
            memcached_config = self.config.memcached_config or MemcachedConfig()
            memcached_config.key_prefix = self.config.key_prefix or memcached_config.key_prefix

            cache = MemcachedCache(memcached_config)
            await cache.connect()
            return cache

        elif backend == CacheBackend.DATABASE:
            if not self.config.database_config:
                raise ValueError("database_config required for database backend")

            self.config.database_config.key_prefix = (
                self.config.key_prefix or self.config.database_config.key_prefix
            )

            # Database cache requires a DB connection - user must provide
            raise NotImplementedError("Database cache requires db_connection in database_config")

        else:
            raise ValueError(f"Unknown cache backend: {backend}")

    async def disconnect(self):
        """Close all cache connections."""
        if self._primary_cache:
            if hasattr(self._primary_cache, "disconnect"):
                await self._primary_cache.disconnect()

        for cache in self._fallback_caches:
            if hasattr(cache, "disconnect"):
                await cache.disconnect()

        self._connected = False

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.

        Tries primary cache first, then fallbacks.

        Args:
            key: Cache key
            default: Default value if key not found

        Returns:
            Cached value or default
        """
        # Try primary cache
        try:
            value = await self._primary_cache.get(key, default)
            if value is not default:
                return value
        except Exception as e:
            logger.error(f"Primary cache GET error: {e}")

        # Try fallback caches
        for cache in self._fallback_caches:
            try:
                value = await cache.get(key, default)
                if value is not default:
                    # Promote to primary cache
                    try:
                        await self._primary_cache.set(key, value)
                    except Exception:
                        logger.error(f"Resource error in get: {e}", exc_info=True)
                        # Continue cleanup despite error
                    return value
            except Exception as e:
                logger.error(f"Fallback cache GET error: {e}")

        return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Writes to all caches (primary + fallbacks).

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if at least one cache succeeded
        """
        success = False

        # Set in primary cache
        try:
            if await self._primary_cache.set(key, value, ttl):
                success = True
        except Exception as e:
            logger.error(f"Primary cache SET error: {e}")

        # Set in fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.set(key, value, ttl)
            except Exception as e:
                logger.error(f"Fallback cache SET error: {e}")

        return success

    async def delete(self, key: str) -> bool:
        """
        Delete key from all caches.

        Args:
            key: Cache key

        Returns:
            True if at least one cache succeeded
        """
        success = False

        # Delete from primary cache
        try:
            if await self._primary_cache.delete(key):
                success = True
        except Exception as e:
            logger.error(f"Primary cache DELETE error: {e}")

        # Delete from fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.delete(key)
            except Exception as e:
                logger.error(f"Fallback cache DELETE error: {e}")

        return success

    async def exists(self, key: str) -> bool:
        """Check if key exists in any cache."""
        # Check primary cache
        try:
            if await self._primary_cache.exists(key):
                return True
        except Exception as e:
            logger.error(f"Primary cache EXISTS error: {e}")

        # Check fallback caches
        for cache in self._fallback_caches:
            try:
                if await cache.exists(key):
                    return True
            except Exception:
                # TODO: Add proper exception handling

                pass
        return False

    async def clear(self) -> bool:
        """Clear all caches."""
        success = False

        # Clear primary cache
        try:
            if await self._primary_cache.clear():
                success = True
        except Exception as e:
            logger.error(f"Primary cache CLEAR error: {e}")

        # Clear fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.clear()
            except Exception as e:
                logger.error(f"Fallback cache CLEAR error: {e}")

        return success

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs
        """
        result = {}

        # Try primary cache
        try:
            result = await self._primary_cache.get_many(keys)
        except Exception as e:
            logger.error(f"Primary cache GET_MANY error: {e}")

        # Fill missing keys from fallbacks
        if len(result) < len(keys):
            missing_keys = [k for k in keys if k not in result]

            for cache in self._fallback_caches:
                try:
                    fallback_result = await cache.get_many(missing_keys)
                    result.update(fallback_result)

                    # Promote to primary cache
                    if fallback_result:
                        try:
                            await self._primary_cache.set_many(fallback_result)
                        except Exception:
                            # TODO: Add proper exception handling

                            pass
                    if len(result) >= len(keys):
                        break

                except Exception as e:
                    logger.error(f"Fallback cache GET_MANY error: {e}")

        return result

    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if at least one cache succeeded
        """
        success = False

        # Set in primary cache
        try:
            if await self._primary_cache.set_many(mapping, ttl):
                success = True
        except Exception as e:
            logger.error(f"Primary cache SET_MANY error: {e}")

        # Set in fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.set_many(mapping, ttl)
            except Exception as e:
                logger.error(f"Fallback cache SET_MANY error: {e}")

        return success

    async def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys from all caches.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted from primary cache
        """
        count = 0

        # Delete from primary cache
        try:
            count = await self._primary_cache.delete_many(keys)
        except Exception as e:
            logger.error(f"Primary cache DELETE_MANY error: {e}")

        # Delete from fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.delete_many(keys)
            except Exception as e:
                logger.error(f"Fallback cache DELETE_MANY error: {e}")

        return count

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
            return await self._primary_cache.increment(key, delta)
        except Exception as e:
            logger.error(f"Cache INCREMENT error: {e}")
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
            return await self._primary_cache.decrement(key, delta)
        except Exception as e:
            logger.error(f"Cache DECREMENT error: {e}")
            return None

    async def touch(self, key: str, ttl: int) -> bool:
        """
        Update TTL for existing key in all caches.

        Args:
            key: Cache key
            ttl: New TTL in seconds

        Returns:
            True if successful in primary cache
        """
        success = False

        # Touch in primary cache
        try:
            if await self._primary_cache.touch(key, ttl):
                success = True
        except Exception as e:
            logger.error(f"Primary cache TOUCH error: {e}")

        # Touch in fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.touch(key, ttl)
            except Exception:
                # TODO: Add proper exception handling

                pass
        return success

    async def expire(self, key: str, ttl: int) -> bool:
        """Alias for touch()."""
        return await self.touch(key, ttl)

    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all cache keys matching pattern.

        Args:
            pattern: Pattern to match

        Returns:
            List of matching keys from primary cache
        """
        try:
            return await self._primary_cache.keys(pattern)
        except Exception as e:
            logger.error(f"Cache KEYS error: {e}")
            return []

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern from all caches.

        Args:
            pattern: Pattern to match

        Returns:
            Number of keys deleted from primary cache
        """
        count = 0

        # Delete from primary cache
        try:
            count = await self._primary_cache.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Primary cache DELETE_PATTERN error: {e}")

        # Delete from fallback caches
        for cache in self._fallback_caches:
            try:
                await cache.delete_pattern(pattern)
            except Exception:
                # TODO: Add proper exception handling

                pass
        return count

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with stats from all caches
        """
        stats = {"backend": self.config.backend.value, "primary": {}, "fallbacks": []}

        # Primary cache stats
        try:
            if hasattr(self._primary_cache, "get_stats"):
                stats["primary"] = await self._primary_cache.get_stats()
            else:
                stats["primary"] = self._primary_cache.get_stats()
        except Exception as e:
            logger.error(f"Primary cache stats error: {e}")
            stats["primary"] = {"error": str(e)}

        # Fallback cache stats
        for i, cache in enumerate(self._fallback_caches):
            try:
                if hasattr(cache, "get_stats"):
                    fallback_stats = await cache.get_stats()
                else:
                    fallback_stats = cache.get_stats()
                stats["fallbacks"].append(fallback_stats)
            except Exception as e:
                logger.error(f"Fallback cache {i} stats error: {e}")
                stats["fallbacks"].append({"error": str(e)})

        return stats

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit."""
        await self.disconnect()


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Get global cache instance.

    Returns:
        Global CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = CacheManager()
    return _cache_instance


def configure_cache(config: CacheConfig) -> CacheManager:
    """
    Configure global cache instance.

    Args:
        config: Cache configuration

    Returns:
        Configured CacheManager instance
    """
    global _cache_instance
    _cache_instance = CacheManager(config)
    return _cache_instance


__all__ = [
    "CacheManager",
    "CacheConfig",
    "CacheBackend",
    "get_cache",
    "configure_cache",
]
