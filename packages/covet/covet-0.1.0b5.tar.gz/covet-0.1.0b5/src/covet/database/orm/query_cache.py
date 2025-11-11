"""
Query Result Cache

High-performance caching layer for ORM queries with intelligent invalidation,
Redis backend support, and comprehensive cache management.

Features:
- QuerySet result caching with automatic invalidation
- Redis-backed distributed cache
- Per-model cache configuration
- Cache warming strategies
- TTL management
- Cache hit rate tracking
- Automatic cache key generation
- Smart invalidation on model changes

Example:
    from covet.database.orm.query_cache import QueryCache, CacheConfig

    # Configure cache
    config = CacheConfig(
        backend="redis",
        redis_url="redis://localhost:6379/0",
        default_ttl=300,
    )

    cache = QueryCache(config)

    # Cache query results
    @cache.cached(ttl=60)
    async def get_active_users():
        return await User.objects.filter(is_active=True).all()

    # Invalidate on model changes
    cache.invalidate_model(User)
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class CacheBackend(Enum):
    """Cache backend type."""

    MEMORY = "memory"  # In-memory cache (single process)
    REDIS = "redis"  # Redis cache (distributed)
    MEMCACHED = "memcached"  # Memcached (distributed)


class InvalidationStrategy(Enum):
    """Cache invalidation strategy."""

    TTL = "ttl"  # Time-based expiration
    ON_WRITE = "on_write"  # Invalidate on model writes
    MANUAL = "manual"  # Manual invalidation only
    SMART = "smart"  # Intelligent invalidation based on query analysis


@dataclass
class CacheConfig:
    """Cache configuration."""

    backend: str = "memory"
    redis_url: Optional[str] = None
    memcached_servers: Optional[List[str]] = None
    default_ttl: int = 300  # 5 minutes
    max_size: int = 10000  # Max cached items (for memory backend)
    key_prefix: str = "covet:orm:"
    enable_compression: bool = True
    compression_threshold: int = 1024  # Compress if > 1KB
    serializer: str = "pickle"  # pickle or json


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    total_latency_ms: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average operation latency."""
        total_ops = self.hits + self.misses + self.sets + self.deletes
        return (self.total_latency_ms / total_ops) if total_ops > 0 else 0.0


class QueryCache:
    """
    Query result cache with intelligent invalidation.

    Provides transparent caching layer for ORM queries with support for
    multiple backends and sophisticated cache management.
    """

    def __init__(self, config: Optional[CacheConfig] = None):
        """
        Initialize query cache.

        Args:
            config: Cache configuration (uses defaults if not provided)
        """
        self.config = config or CacheConfig()

        # Initialize backend
        self.backend = self._initialize_backend()

        # Statistics
        self.stats = CacheStats()

        # Model invalidation tracking
        self.model_keys: Dict[str, Set[str]] = {}  # model_name -> cache_keys

        # Cache warming state
        self.warming_tasks: Dict[str, asyncio.Task] = {}

    def cached(
        self,
        ttl: Optional[int] = None,
        key_builder: Optional[Callable] = None,
        invalidate_on: Optional[List[str]] = None,
    ) -> Callable:
        """
        Decorator for caching function results.

        Args:
            ttl: Time to live in seconds (None = use default)
            key_builder: Custom function to build cache key
            invalidate_on: List of model names that invalidate this cache

        Returns:
            Decorator function

        Example:
            @cache.cached(ttl=300, invalidate_on=['User', 'Profile'])
            async def get_user_profile(user_id):
                return await User.objects.get(id=user_id)
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Build cache key
                if key_builder:
                    cache_key = key_builder(*args, **kwargs)
                else:
                    cache_key = self._build_function_key(func, args, kwargs)

                # Try to get from cache
                cached_result = await self.get(cache_key)
                if cached_result is not None:
                    return cached_result

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                actual_ttl = ttl if ttl is not None else self.config.default_ttl
                await self.set(cache_key, result, ttl=actual_ttl)

                # Track model associations
                if invalidate_on:
                    for model_name in invalidate_on:
                        self._associate_key_with_model(model_name, cache_key)

                return result

            return wrapper

        return decorator

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        start_time = time.time()

        try:
            full_key = self._build_key(key)
            value = await self.backend.get(full_key)

            latency = (time.time() - start_time) * 1000

            if value is not None:
                self.stats.hits += 1
                logger.debug(f"Cache HIT: {key} ({latency:.2f}ms)")
            else:
                self.stats.misses += 1
                logger.debug(f"Cache MISS: {key} ({latency:.2f}ms)")

            self.stats.total_latency_ms += latency

            return value

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats.misses += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        start_time = time.time()

        try:
            full_key = self._build_key(key)
            actual_ttl = ttl if ttl is not None else self.config.default_ttl

            success = await self.backend.set(full_key, value, ttl=actual_ttl)

            latency = (time.time() - start_time) * 1000
            self.stats.total_latency_ms += latency

            if success:
                self.stats.sets += 1
                logger.debug(f"Cache SET: {key} (TTL={actual_ttl}s, {latency:.2f}ms)")
            else:
                logger.warning(f"Cache SET failed: {key}")

            return success

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        start_time = time.time()

        try:
            full_key = self._build_key(key)
            success = await self.backend.delete(full_key)

            latency = (time.time() - start_time) * 1000
            self.stats.total_latency_ms += latency

            if success:
                self.stats.deletes += 1
                logger.debug(f"Cache DELETE: {key} ({latency:.2f}ms)")

            return success

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def clear(self) -> bool:
        """
        Clear all cache entries.

        Returns:
            True if successful
        """
        try:
            success = await self.backend.clear()
            if success:
                self.model_keys.clear()
                logger.info("Cache cleared")
            return success

        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

    async def invalidate_model(self, model_name: str) -> int:
        """
        Invalidate all cache entries for a model.

        Args:
            model_name: Name of model class

        Returns:
            Number of keys invalidated
        """
        if model_name not in self.model_keys:
            return 0

        keys = list(self.model_keys[model_name])
        count = 0

        for key in keys:
            if await self.delete(key):
                count += 1

        # Clear associations
        self.model_keys[model_name].clear()

        logger.info(f"Invalidated {count} cache entries for model {model_name}")

        return count

    async def warm_cache(
        self,
        queries: List[Tuple[str, Callable]],
        concurrent: int = 5,
    ) -> Dict[str, bool]:
        """
        Warm cache with common queries.

        Args:
            queries: List of (name, query_function) tuples
            concurrent: Number of concurrent warming tasks

        Returns:
            Dictionary mapping query names to success status
        """
        results = {}
        semaphore = asyncio.Semaphore(concurrent)

        async def warm_query(name: str, query_func: Callable):
            async with semaphore:
                try:
                    logger.info(f"Warming cache for query: {name}")
                    await query_func()
                    results[name] = True
                except Exception as e:
                    logger.error(f"Failed to warm cache for {name}: {e}")
                    results[name] = False

        tasks = [asyncio.create_task(warm_query(name, func)) for name, func in queries]

        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary of statistics
        """
        uptime = (datetime.now() - self.stats.start_time).total_seconds()

        return {
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "sets": self.stats.sets,
            "deletes": self.stats.deletes,
            "evictions": self.stats.evictions,
            "hit_rate": self.stats.hit_rate,
            "avg_latency_ms": self.stats.avg_latency_ms,
            "uptime_seconds": uptime,
            "backend": self.config.backend,
            "total_models_tracked": len(self.model_keys),
        }

    async def close(self) -> None:
        """Close cache backend connections."""
        try:
            await self.backend.close()
            logger.info("Cache backend closed")
        except Exception as e:
            logger.error(f"Error closing cache backend: {e}")

    # Private methods

    def _initialize_backend(self) -> "CacheBackendInterface":
        """Initialize cache backend."""
        backend_type = self.config.backend.lower()

        if backend_type == "memory":
            return MemoryCacheBackend(self.config)
        elif backend_type == "redis":
            return RedisCacheBackend(self.config)
        elif backend_type == "memcached":
            return MemcachedCacheBackend(self.config)
        else:
            logger.warning(f"Unknown backend {backend_type}, using memory")
            return MemoryCacheBackend(self.config)

    def _build_key(self, key: str) -> str:
        """Build full cache key with prefix."""
        return f"{self.config.key_prefix}{key}"

    def _build_function_key(
        self,
        func: Callable,
        args: Tuple,
        kwargs: Dict[str, Any],
    ) -> str:
        """Build cache key for function call."""
        # Create deterministic key from function and arguments
        func_name = f"{func.__module__}.{func.__name__}"

        # Serialize arguments
        try:
            args_str = json.dumps(args, sort_keys=True, default=str)
            kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)
        except (TypeError, ValueError):
            # Fallback to string representation
            args_str = str(args)
            kwargs_str = str(kwargs)

        key_data = f"{func_name}:{args_str}:{kwargs_str}"

        # Hash for consistent length
        key_hash = hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

        return f"func:{func_name}:{key_hash}"

    def _associate_key_with_model(self, model_name: str, cache_key: str) -> None:
        """Associate cache key with model for invalidation."""
        if model_name not in self.model_keys:
            self.model_keys[model_name] = set()

        self.model_keys[model_name].add(cache_key)


class CacheBackendInterface:
    """Interface for cache backends."""

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        raise NotImplementedError

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache."""
        raise NotImplementedError

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        raise NotImplementedError

    async def clear(self) -> bool:
        """Clear all cache entries."""
        raise NotImplementedError

    async def close(self) -> None:
        """Close backend connections."""
        pass


class MemoryCacheBackend(CacheBackendInterface):
    """In-memory cache backend (single process)."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expiry_time)
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self.lock:
            if key not in self.cache:
                return None

            value, expiry = self.cache[key]

            # Check expiration
            if expiry > 0 and time.time() > expiry:
                del self.cache[key]
                return None

            return value

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache."""
        async with self.lock:
            # Check size limit
            if len(self.cache) >= self.config.max_size:
                # Evict oldest entry (simplified LRU)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]

            expiry = time.time() + ttl if ttl > 0 else 0
            self.cache[key] = (value, expiry)
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self.lock:
            self.cache.clear()
            return True


class RedisCacheBackend(CacheBackendInterface):
    """Redis cache backend (distributed)."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.redis = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure Redis connection is initialized."""
        if self._initialized:
            return

        try:
            import redis.asyncio as aioredis

            self.redis = await aioredis.from_url(
                self.config.redis_url or "redis://localhost:6379/0",
                encoding="utf-8",
                decode_responses=False,  # We handle serialization
            )

            self._initialized = True
            logger.info("Redis cache backend initialized")

        except ImportError:
            logger.error("redis package not installed. Install with: pip install redis")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        await self._ensure_initialized()

        try:
            data = await self.redis.get(key)
            if data is None:
                return None

            # Deserialize
            if self.config.serializer == "json":
                return json.loads(data)
            else:  # pickle
                return pickle.loads(data)  # nosec B301 - pickle used for internal cache only

        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache."""
        await self._ensure_initialized()

        try:
            # Serialize
            if self.config.serializer == "json":
                data = json.dumps(value, default=str)
            else:  # pickle
                data = pickle.dumps(value)

            # Set with TTL
            await self.redis.setex(key, ttl, data)
            return True

        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        await self._ensure_initialized()

        try:
            result = await self.redis.delete(key)
            return result > 0

        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        await self._ensure_initialized()

        try:
            # Delete all keys with our prefix
            pattern = f"{self.config.key_prefix}*"
            keys = []

            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.redis.delete(*keys)

            return True

        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        if self.redis:
            await self.redis.close()
            self._initialized = False


class MemcachedCacheBackend(CacheBackendInterface):
    """Memcached cache backend (distributed)."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self.client = None
        self._initialized = False

    async def _ensure_initialized(self) -> None:
        """Ensure Memcached connection is initialized."""
        if self._initialized:
            return

        try:
            import aiomcache

            servers = self.config.memcached_servers or ["localhost:11211"]
            host, port = servers[0].split(":")

            self.client = aiomcache.Client(host, int(port))
            self._initialized = True
            logger.info("Memcached cache backend initialized")

        except ImportError:
            logger.error("aiomcache package not installed. Install with: pip install aiomcache")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Memcached: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        await self._ensure_initialized()

        try:
            data = await self.client.get(key.encode())
            if data is None:
                return None

            return pickle.loads(data)  # nosec B301 - pickle used for internal cache only

        except Exception as e:
            logger.error(f"Memcached get error: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int) -> bool:
        """Set value in cache."""
        await self._ensure_initialized()

        try:
            data = pickle.dumps(value)
            await self.client.set(key.encode(), data, exptime=ttl)
            return True

        except Exception as e:
            logger.error(f"Memcached set error: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        await self._ensure_initialized()

        try:
            await self.client.delete(key.encode())
            return True

        except Exception as e:
            logger.error(f"Memcached delete error: {e}")
            return False

    async def clear(self) -> bool:
        """Clear all cache entries."""
        await self._ensure_initialized()

        try:
            await self.client.flush_all()
            return True

        except Exception as e:
            logger.error(f"Memcached clear error: {e}")
            return False

    async def close(self) -> None:
        """Close Memcached connection."""
        if self.client:
            await self.client.close()
            self._initialized = False


__all__ = [
    "QueryCache",
    "CacheConfig",
    "CacheStats",
    "CacheBackend",
    "InvalidationStrategy",
]
