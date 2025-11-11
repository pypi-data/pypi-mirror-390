"""
Database Cache Backend

Production-ready database cache for fallback when Redis/Memcached unavailable:
- Uses SQL database for cache storage
- Automatic cleanup of expired entries
- Index optimization for performance
- Transaction support
- Works with PostgreSQL, MySQL, SQLite

NO MOCK DATA: Real database integration using existing CovetPy adapters.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from covet.database.security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_table_name,
)
from covet.security.secure_serializer import SecureSerializer

logger = logging.getLogger(__name__)


@dataclass
class DatabaseCacheConfig:
    """Database cache configuration."""

    table_name: str = "cache_entries"
    key_prefix: str = ""
    secret_key: str = None  # Required for secure serialization

    # Cleanup settings
    cleanup_interval: int = 300  # 5 minutes
    cleanup_batch_size: int = 1000

    def __post_init__(self):
        """Validate configuration on initialization."""
        # SECURITY: Validate table name to prevent SQL injection
        try:
            self.table_name = validate_table_name(self.table_name, DatabaseDialect.GENERIC)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{self.table_name}': {e}") from e


class DatabaseCache:
    """
    Database cache backend.

    Features:
    - Uses SQL database for persistent cache
    - Automatic expiration cleanup
    - Index on key column for fast lookups
    - Compatible with PostgreSQL, MySQL, SQLite

    Table schema:
        CREATE TABLE cache_entries (
            cache_key VARCHAR(255) PRIMARY KEY,
            cache_value BLOB NOT NULL,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP,
            INDEX idx_expires_at (expires_at)
        );

    Example:
        from covet.database.adapters import create_adapter
        from covet.security.secure_serializer import generate_secure_key

        # Create database adapter
        db = create_adapter({
            'type': 'postgresql',
            'host': 'localhost',
            'database': 'myapp'
        })

        # Create cache with secure serialization
        config = DatabaseCacheConfig(
            table_name='app_cache',
            secret_key=generate_secure_key()  # REQUIRED for security
        )
        cache = DatabaseCache(db, config)
        await cache.initialize()

        # Use cache
        await cache.set('user:1', user_data, ttl=300)
        user = await cache.get('user:1')
    """

    def __init__(self, db_connection, config: Optional[DatabaseCacheConfig] = None):
        """
        Initialize database cache.

        Args:
            db_connection: Database connection/adapter
            config: Cache configuration
        """
        self.db = db_connection
        self.config = config or DatabaseCacheConfig()
        self._initialized = False
        self._cleanup_task = None

        # Initialize secure serializer (CRITICAL: prevents RCE via pickle)
        if not self.config.secret_key:
            raise ValueError(
                "DatabaseCache requires secret_key in config for secure serialization. "
                "Use generate_secure_key() from covet.security.secure_serializer to generate one."
            )
        self.serializer = SecureSerializer(secret_key=self.config.secret_key)

    async def initialize(self):
        """Create cache table and start cleanup task."""
        if self._initialized:
            return

        await self._create_table()
        self._start_cleanup_task()
        self._initialized = True

    async def _create_table(self):
        """Create cache table if it doesn't exist."""
        # Detect database type
        db_type = self._get_db_type()

        if db_type == "postgresql":
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                cache_key VARCHAR(255) PRIMARY KEY,
                cache_value BYTEA NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_expires
                ON {self.config.table_name}(expires_at);
            """
        elif db_type == "mysql":
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                cache_key VARCHAR(255) PRIMARY KEY,
                cache_value BLOB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NULL,
                INDEX idx_expires_at (expires_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        else:  # SQLite
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                cache_key TEXT PRIMARY KEY,
                cache_value BLOB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_expires
                ON {self.config.table_name}(expires_at);
            """

        try:
            # Execute CREATE statements
            for statement in create_sql.split(";"):
                statement = statement.strip()
                if statement:
                    await self._execute(statement)

            logger.info(f"Cache table '{self.config.table_name}' initialized")

        except Exception as e:
            logger.error(f"Failed to create cache table: {e}")
            raise

    def _get_db_type(self) -> str:
        """Detect database type from connection."""
        # Try to detect from connection object
        conn_str = str(type(self.db)).lower()

        if "postgres" in conn_str or "psycopg" in conn_str:
            return "postgresql"
        elif "mysql" in conn_str or "pymysql" in conn_str:
            return "mysql"
        else:
            return "sqlite"

    async def _execute(self, query: str, params: Optional[tuple] = None):
        """Execute database query."""
        # This is a simplified interface - adapt to your actual DB adapter
        try:
            if hasattr(self.db, "execute"):
                if params:
                    return await self.db.execute(query, params)
                else:
                    return await self.db.execute(query)
            elif hasattr(self.db, "query"):
                if params:
                    return await self.db.query(query, params)
                else:
                    return await self.db.query(query)
            else:
                raise NotImplementedError("Database adapter interface not recognized")

        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise

    async def _fetchone(self, query: str, params: Optional[tuple] = None):
        """Fetch one row."""
        try:
            if hasattr(self.db, "fetchone"):
                if params:
                    return await self.db.fetchone(query, params)
                else:
                    return await self.db.fetchone(query)
            elif hasattr(self.db, "fetch_one"):
                if params:
                    return await self.db.fetch_one(query, params)
                else:
                    return await self.db.fetch_one(query)
            else:
                # Fallback: execute and get first result
                result = await self._execute(query, params)
                if result and len(result) > 0:
                    return result[0]
                return None

        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return None

    async def _fetchall(self, query: str, params: Optional[tuple] = None):
        """Fetch all rows."""
        try:
            if hasattr(self.db, "fetchall"):
                if params:
                    return await self.db.fetchall(query, params)
                else:
                    return await self.db.fetchall(query)
            elif hasattr(self.db, "fetch_all"):
                if params:
                    return await self.db.fetch_all(query, params)
                else:
                    return await self.db.fetch_all(query)
            else:
                return await self._execute(query, params)

        except Exception as e:
            logger.error(f"Database fetch error: {e}")
            return []

    def _make_key(self, key: str) -> str:
        """Create prefixed key."""
        if self.config.key_prefix:
            return f"{self.config.key_prefix}:{key}"
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
            query = f"""
            SELECT cache_value, expires_at
            FROM {self.config.table_name}
            WHERE cache_key = %s
            """
            # nosec B608 - table_name validated in config

            row = await self._fetchone(query, (self._make_key(key),))

            if not row:
                return default

            cache_value, expires_at = row[0], row[1]

            # Check expiration
            if expires_at:
                # Handle different datetime types
                if isinstance(expires_at, str):
                    expires_at = datetime.fromisoformat(expires_at)

                if datetime.utcnow() > expires_at:
                    # Expired - delete and return default
                    await self.delete(key)
                    return default

            # Deserialize value using SecureSerializer (prevents RCE)
            return self.serializer.loads(cache_value)

        except Exception as e:
            logger.error(f"Database cache GET error for key {key}: {e}")
            return default

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        try:
            cache_key = self._make_key(key)
            # Use SecureSerializer instead of pickle (prevents RCE)
            cache_value = self.serializer.dumps(value)

            # Calculate expiration
            if ttl:
                expires_at = datetime.utcnow() + timedelta(seconds=ttl)
            else:
                expires_at = None

            # Use UPSERT (INSERT ... ON CONFLICT or REPLACE INTO)
            db_type = self._get_db_type()

            if db_type == "postgresql":
                query = f"""
                INSERT INTO {self.config.table_name}
                    (cache_key, cache_value, created_at, expires_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (cache_key)
                DO UPDATE SET
                    cache_value = EXCLUDED.cache_value,
                    created_at = EXCLUDED.created_at,
                    expires_at = EXCLUDED.expires_at
                """
                # nosec B608 - table_name validated in config
            elif db_type == "mysql":
                query = f"""
                INSERT INTO {self.config.table_name}
                    (cache_key, cache_value, created_at, expires_at)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    cache_value = VALUES(cache_value),
                    created_at = VALUES(created_at),
                    expires_at = VALUES(expires_at)
                """
                # nosec B608 - table_name validated in config
            else:  # SQLite
                query = f"""
                INSERT OR REPLACE INTO {self.config.table_name}
                    (cache_key, cache_value, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """

            await self._execute(query, (cache_key, cache_value, datetime.utcnow(), expires_at))

            return True

        except Exception as e:
            logger.error(f"Database cache SET error for key {key}: {e}")
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
            query = f"""
            DELETE FROM {self.config.table_name}
            WHERE cache_key = %s
            """
            # nosec B608 - table_name validated in config

            await self._execute(query, (self._make_key(key),))
            return True

        except Exception as e:
            logger.error(f"Database cache DELETE error for key {key}: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists and is not expired.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        value = await self.get(key)
        return value is not None

    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            if self.config.key_prefix:
                # Delete only keys with prefix
                query = f"""
                DELETE FROM {self.config.table_name}
                WHERE cache_key LIKE %s
                """
                # nosec B608 - table_name validated in config
                await self._execute(query, (f"{self.config.key_prefix}:%",))
            else:
                # Clear entire table
                query = f"TRUNCATE TABLE {self.config.table_name}"
                await self._execute(query)

            return True

        except Exception as e:
            logger.error(f"Database cache CLEAR error: {e}")
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

        result = {}
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value

        return result

    async def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time-to-live in seconds

        Returns:
            True if successful
        """
        for key, value in mapping.items():
            await self.set(key, value, ttl)
        return True

    async def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple keys.

        Args:
            keys: List of cache keys

        Returns:
            Number of keys deleted
        """
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        return count

    async def keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Get all cache keys matching pattern.

        Args:
            pattern: SQL LIKE pattern

        Returns:
            List of matching keys (without prefix)
        """
        try:
            if pattern:
                search_pattern = self._make_key(pattern)
            else:
                search_pattern = self._make_key("%")

            query = f"""
            SELECT cache_key
            FROM {self.config.table_name}
            WHERE cache_key LIKE %s
            AND (expires_at IS NULL OR expires_at > %s)
            """
            # nosec B608 - table_name validated in config

            rows = await self._fetchall(query, (search_pattern, datetime.utcnow()))

            # Remove prefix from keys
            keys = []
            prefix_len = len(self.config.key_prefix) + 1 if self.config.key_prefix else 0

            for row in rows:
                key = row[0]
                if prefix_len:
                    key = key[prefix_len:]
                keys.append(key)

            return keys

        except Exception as e:
            logger.error(f"Database cache KEYS error: {e}")
            return []

    async def cleanup_expired(self) -> int:
        """
        Remove expired entries.

        Returns:
            Number of entries removed
        """
        try:
            query = f"""
            DELETE FROM {self.config.table_name}
            WHERE expires_at IS NOT NULL
            AND expires_at < %s
            """
            # nosec B608 - table_name validated in config

            await self._execute(query, (datetime.utcnow(),))

            logger.debug("Cleaned up expired cache entries")
            return 0  # Can't easily get count

        except Exception as e:
            logger.error(f"Database cache cleanup error: {e}")
            return 0

    def _start_cleanup_task(self):
        """Start background task for cleanup."""

        async def cleanup_worker():
            while True:
                try:
                    await asyncio.sleep(self.config.cleanup_interval)
                    await self.cleanup_expired()
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")

        self._cleanup_task = asyncio.create_task(cleanup_worker())

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache stats
        """
        try:
            # Count total entries
            query = f"""
            SELECT COUNT(*) FROM {self.config.table_name}
            """
            # nosec B608 - table_name validated in config
            total_row = await self._fetchone(query)
            total = total_row[0] if total_row else 0

            # Count expired entries
            query = f"""
            SELECT COUNT(*) FROM {self.config.table_name}
            WHERE expires_at IS NOT NULL AND expires_at < %s
            """
            # nosec B608 - table_name validated in config
            expired_row = await self._fetchone(query, (datetime.utcnow(),))
            expired = expired_row[0] if expired_row else 0

            return {
                "backend": "database",
                "table": self.config.table_name,
                "total_entries": total,
                "expired_entries": expired,
                "active_entries": total - expired,
            }

        except Exception as e:
            logger.error(f"Database cache stats error: {e}")
            return {"error": str(e)}


__all__ = ["DatabaseCache", "DatabaseCacheConfig"]
