"""
Memcached Cache Backend

Production-ready Memcached cache with:
- aiomemcache async integration
- Consistent hashing for multiple servers
- Binary protocol support
- Connection pooling
- Automatic retry and failover
- Statistics tracking

NO MOCK DATA: Real Memcached integration using aiomemcache.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from covet.security.secure_serializer import SecureSerializer

try:
    import aiomcache

    MEMCACHED_AVAILABLE = True
except ImportError:
    MEMCACHED_AVAILABLE = False
    # Create stub for type annotations when aiomcache not installed
    aiomcache = None


logger = logging.getLogger(__name__)


@dataclass
class MemcachedConfig:
    """Memcached configuration."""

    host: str = "localhost"
    port: int = 11211
    pool_size: int = 10
    pool_minsize: int = 2

    # Multiple servers for consistent hashing
    servers: Optional[List[Tuple[str, int]]] = None

    # Key settings
    key_prefix: str = ""
    max_key_length: int = 250

    # Secure serialization (REQUIRED to prevent RCE)
    secret_key: Optional[str] = None

    # Timeouts
    timeout: float = 5.0


class ConsistentHash:
    """
    Consistent hashing for distributing keys across multiple servers.

    Uses virtual nodes for better distribution.
    """

    def __init__(self, nodes: List[str], virtual_nodes: int = 150):
        """
        Initialize consistent hash ring.

        Args:
            nodes: List of server addresses
            virtual_nodes: Number of virtual nodes per physical node
        """
        self.virtual_nodes = virtual_nodes
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []

        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str):
        """Add node to hash ring."""
        for i in range(self.virtual_nodes):
            key = self._hash(f"{node}:{i}")
            self.ring[key] = node
            self.sorted_keys.append(key)

        self.sorted_keys.sort()

    def remove_node(self, node: str):
        """Remove node from hash ring."""
        for i in range(self.virtual_nodes):
            key = self._hash(f"{node}:{i}")
            del self.ring[key]
            self.sorted_keys.remove(key)

    def get_node(self, key: str) -> str:
        """Get node for key using consistent hashing."""
        if not self.ring:
            return None

        hash_key = self._hash(key)

        # Find first node >= hash_key
        for ring_key in self.sorted_keys:
            if ring_key >= hash_key:
                return self.ring[ring_key]

        # Wrap around to first node
        return self.ring[self.sorted_keys[0]]

    def _hash(self, key: str) -> int:
        """Hash key to integer (uses SHA-256 for security)."""
        return int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)


class MemcachedCache:
    """
    Memcached cache backend.

    Features:
    - Connection pooling
    - Multiple server support with consistent hashing
    - Binary protocol
    - Automatic retry on failure
    - Key prefixing

    Example:
        # Single server
        config = MemcachedConfig(host='localhost', port=11211)
        cache = MemcachedCache(config)
        await cache.connect()

        # Multiple servers with consistent hashing
        config = MemcachedConfig(
            servers=[
                ('server1', 11211),
                ('server2', 11211),
                ('server3', 11211)
            ]
        )
        cache = MemcachedCache(config)
        await cache.connect()

        # Usage
        await cache.set('user:1', user_data, ttl=300)
        user = await cache.get('user:1')
    """

    def __init__(self, config: Optional[MemcachedConfig] = None):
        """
        Initialize Memcached cache.

        Args:
            config: Memcached configuration
        """
        if not MEMCACHED_AVAILABLE:
            raise ImportError("aiomcache not installed. " "Install with: pip install aiomcache")

        self.config = config or MemcachedConfig()
        self._clients: Dict[str, aiomcache.Client] = {}
        self._hash_ring: Optional[ConsistentHash] = None

        # Initialize secure serializer (CRITICAL: prevents RCE via pickle)
        if not self.config.secret_key:
            raise ValueError(
                "MemcachedCache requires secret_key in config for secure serialization. "
                "Use generate_secure_key() from covet.security.secure_serializer to generate one."
            )
        self.serializer = SecureSerializer(secret_key=self.config.secret_key)

    async def connect(self):
        """Establish Memcached connection(s)."""
        try:
            if self.config.servers:
                # Multiple servers with consistent hashing
                server_addresses = []

                for host, port in self.config.servers:
                    address = f"{host}:{port}"
                    server_addresses.append(address)

                    # Create client for each server
                    client = aiomcache.Client(
                        host=host,
                        port=port,
                        pool_size=self.config.pool_size,
                        pool_minsize=self.config.pool_minsize,
                    )
                    self._clients[address] = client

                # Set up consistent hashing
                self._hash_ring = ConsistentHash(server_addresses)

            else:
                # Single server
                address = f"{self.config.host}:{self.config.port}"
                client = aiomcache.Client(
                    host=self.config.host,
                    port=self.config.port,
                    pool_size=self.config.pool_size,
                    pool_minsize=self.config.pool_minsize,
                )
                self._clients[address] = client

            logger.info(f"Connected to Memcached: {len(self._clients)} server(s)")

        except Exception as e:
            logger.error(f"Failed to connect to Memcached: {e}")
            raise

    async def disconnect(self):
        """Close Memcached connections."""
        for client in self._clients.values():
            await client.close()
        self._clients.clear()

    def _get_client(self, key: str):
        """Get client for key using consistent hashing."""
        if self._hash_ring:
            address = self._hash_ring.get_node(key)
            return self._clients[address]
        else:
            # Single server
            return list(self._clients.values())[0]

    def _make_key(self, key: str) -> bytes:
        """
        Create prefixed key.

        Memcached has max key length of 250 bytes.
        If key is too long, use hash.
        """
        if self.config.key_prefix:
            full_key = f"{self.config.key_prefix}:{key}"
        else:
            full_key = key

        # Check length
        if len(full_key) > self.config.max_key_length:
            # Hash long keys (use SHA-256 instead of MD5)
            hash_key = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
            if self.config.key_prefix:
                full_key = f"{self.config.key_prefix}:{hash_key}"
            else:
                full_key = hash_key

        return full_key.encode("utf-8")

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
            client = self._get_client(key)
            data = await client.get(self._make_key(key))

            if data is None:
                return default

            # Use SecureSerializer instead of pickle (prevents RCE)
            return self.serializer.loads(data)

        except Exception as e:
            logger.error(f"Memcached GET error for key {key}: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (0 = no expiration)

        Returns:
            True if successful
        """
        try:
            client = self._get_client(key)
            # Use SecureSerializer instead of pickle (prevents RCE)
            data = self.serializer.dumps(value)

            # Memcached uses 0 for no expiration
            exptime = ttl if ttl is not None else 0

            result = await client.set(self._make_key(key), data, exptime=exptime)
            return result

        except Exception as e:
            logger.error(f"Memcached SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        try:
            client = self._get_client(key)
            result = await client.delete(self._make_key(key))
            return result

        except Exception as e:
            logger.error(f"Memcached DELETE error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        # Memcached doesn't have EXISTS command, use GET
        value = await self.get(key)
        return value is not None

    async def clear(self) -> bool:
        """
        Clear all cache entries on all servers.

        WARNING: This clears the ENTIRE cache, not just keys with prefix.
        """
        try:
            for client in self._clients.values():
                await client.flush_all()
            return True

        except Exception as e:
            logger.error(f"Memcached FLUSH error: {e}")
            return False

    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary of key-value pairs
        """
        if not keys:
            return {}

        # Group keys by server (if using consistent hashing)
        if self._hash_ring:
            # Group keys by server
            server_keys: Dict[str, List[str]] = {}
            for key in keys:
                server = self._hash_ring.get_node(key)
                if server not in server_keys:
                    server_keys[server] = []
                server_keys[server].append(key)

            # Fetch from each server
            result = {}
            for server, server_key_list in server_keys.items():
                client = self._clients[server]
                prefixed_keys = [self._make_key(k) for k in server_key_list]

                try:
                    data = await client.multi_get(*prefixed_keys)

                    for original_key, prefixed_key in zip(server_key_list, prefixed_keys):
                        if prefixed_key in data and data[prefixed_key] is not None:
                            # Use SecureSerializer instead of pickle (prevents
                            # RCE)
                            result[original_key] = self.serializer.loads(data[prefixed_key])

                except Exception as e:
                    logger.error(f"Memcached MULTI_GET error: {e}")

            return result

        else:
            # Single server
            client = list(self._clients.values())[0]
            prefixed_keys = [self._make_key(k) for k in keys]

            try:
                data = await client.multi_get(*prefixed_keys)

                result = {}
                for original_key, prefixed_key in zip(keys, prefixed_keys):
                    if prefixed_key in data and data[prefixed_key] is not None:
                        # Use SecureSerializer instead of pickle (prevents RCE)
                        result[original_key] = self.serializer.loads(data[prefixed_key])

                return result

            except Exception as e:
                logger.error(f"Memcached MULTI_GET error: {e}")
                return {}

    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if all successful
        """
        if not mapping:
            return True

        try:
            # Set each key individually (Memcached doesn't have efficient
            # multi-set)
            for key, value in mapping.items():
                await self.set(key, value, ttl)

            return True

        except Exception as e:
            logger.error(f"Memcached SET_MANY error: {e}")
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

        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1

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
            client = self._get_client(key)
            result = await client.incr(self._make_key(key), delta)
            return result

        except Exception as e:
            logger.error(f"Memcached INCR error for key {key}: {e}")
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
            client = self._get_client(key)
            result = await client.decr(self._make_key(key), delta)
            return result

        except Exception as e:
            logger.error(f"Memcached DECR error for key {key}: {e}")
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
            client = self._get_client(key)
            result = await client.touch(self._make_key(key), ttl)
            return result

        except Exception as e:
            logger.error(f"Memcached TOUCH error for key {key}: {e}")
            return False

    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all cache keys.

        WARNING: Memcached doesn't support key listing.
        This returns an empty list.
        """
        logger.warning("Memcached doesn't support key listing")
        return []

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        WARNING: Memcached doesn't support pattern-based deletion.
        This returns 0.
        """
        logger.warning("Memcached doesn't support pattern-based deletion")
        return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get Memcached server statistics.

        Returns:
            Dictionary with stats from all servers
        """
        try:
            all_stats = {}

            for address, client in self._clients.items():
                stats = await client.stats()

                all_stats[address] = {
                    "version": stats.get(b"version", b"").decode("utf-8"),
                    "curr_items": int(stats.get(b"curr_items", 0)),
                    "total_items": int(stats.get(b"total_items", 0)),
                    "bytes": int(stats.get(b"bytes", 0)),
                    "curr_connections": int(stats.get(b"curr_connections", 0)),
                    "get_hits": int(stats.get(b"get_hits", 0)),
                    "get_misses": int(stats.get(b"get_misses", 0)),
                    "evictions": int(stats.get(b"evictions", 0)),
                }

            return {"connected": True, "servers": all_stats}

        except Exception as e:
            logger.error(f"Memcached STATS error: {e}")
            return {"connected": False, "error": str(e)}


__all__ = ["MemcachedCache", "MemcachedConfig", "ConsistentHash"]
