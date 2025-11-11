"""
CovetPy Caching Layer

Production-ready caching system with multiple backend support:
- In-memory cache with LRU eviction
- Redis cache with pub/sub
- Memcached with consistent hashing
- Database cache for fallback

Features:
- Unified cache API
- Automatic fallback
- Batch operations
- Pattern-based operations
- Function/page caching decorators
- HTTP response caching middleware
- Statistics tracking

Example:
    from covet.cache import CacheManager, cache_result

    # Create cache
    cache = CacheManager(backend='redis', prefix='myapp')
    await cache.connect()

    # Use cache
    await cache.set('user:1', user_data, ttl=300)
    user = await cache.get('user:1')

    # Decorator caching
    @cache_result(ttl=300, key_prefix='user')
    async def get_user(user_id: int):
        return await db.query(User).get(user_id)

    # HTTP caching
    app = CacheMiddleware(app, config=CacheMiddlewareConfig(
        default_ttl=300,
        etag_enabled=True
    ))
"""

from .backends import (
    CacheStats,
    DatabaseCache,
    DatabaseCacheConfig,
    MemcachedCache,
    MemcachedConfig,
    MemoryCache,
    RedisCache,
    RedisConfig,
    SerializerType,
)
from .redis_cache import (
    CacheConfig as RedisCacheConfig,
    RedisCache as DistributedRedisCache,
    LRUCache,
    get_cache as get_distributed_cache,
    cache as distributed_cache,
)
from .decorators import (
    cache_invalidate,
    cache_invalidate_pattern,
    cache_page,
    cache_result,
    cache_unless,
    memoize,
)
from .manager import (
    CacheBackend,
    CacheConfig,
    CacheManager,
    configure_cache,
    get_cache,
)
from .middleware import (
    CacheMiddleware,
    CacheMiddlewareConfig,
)

__all__ = [
    # Backends
    "MemoryCache",
    "RedisCache",
    "RedisConfig",
    "SerializerType",
    "MemcachedCache",
    "MemcachedConfig",
    "DatabaseCache",
    "DatabaseCacheConfig",
    "CacheStats",
    # Distributed Cache (for horizontal scaling)
    "RedisCacheConfig",
    "DistributedRedisCache",
    "LRUCache",
    "get_distributed_cache",
    "distributed_cache",
    # Manager
    "CacheManager",
    "CacheConfig",
    "CacheBackend",
    "get_cache",
    "configure_cache",
    # Decorators
    "cache_result",
    "cache_page",
    "cache_unless",
    "cache_invalidate",
    "cache_invalidate_pattern",
    "memoize",
    # Middleware
    "CacheMiddleware",
    "CacheMiddlewareConfig",
]


__version__ = "1.0.0"
