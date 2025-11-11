"""
Cache Backends

Support for multiple cache backends:
- Memory: Fast in-memory cache with LRU eviction
- Redis: Distributed cache with pub/sub support
- Memcached: High-performance distributed cache
- Database: Persistent cache using SQL database
"""

from .memory import CacheStats, MemoryCache

# Try to import optional backends
try:
    from .database import DatabaseCache, DatabaseCacheConfig

    HAS_DATABASE = True
except ImportError:
    HAS_DATABASE = False
    DatabaseCache = None
    DatabaseCacheConfig = None

try:
    from .memcached import ConsistentHash, MemcachedCache, MemcachedConfig

    HAS_MEMCACHED = True
except ImportError:
    HAS_MEMCACHED = False
    MemcachedCache = None
    MemcachedConfig = None
    ConsistentHash = None

try:
    from .redis import RedisCache, RedisConfig, SerializerType

    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    RedisCache = None
    RedisConfig = None
    SerializerType = None

# Always export - use MemoryBackend as alias for MemoryCache
MemoryBackend = MemoryCache

__all__ = [
    # Memory (always available)
    "MemoryCache",
    "MemoryBackend",
    "CacheStats",
    # Redis (optional)
    "RedisCache",
    "RedisConfig",
    "SerializerType",
    # Memcached (optional)
    "MemcachedCache",
    "MemcachedConfig",
    "ConsistentHash",
    # Database (optional)
    "DatabaseCache",
    "DatabaseCacheConfig",
    # Availability flags
    "HAS_REDIS",
    "HAS_MEMCACHED",
    "HAS_DATABASE",
]
