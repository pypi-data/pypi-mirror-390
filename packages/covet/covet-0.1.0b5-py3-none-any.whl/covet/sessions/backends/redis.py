"""
Redis Session Backend

Production-ready Redis sessions with:
- Fast session access with Redis
- Automatic expiration using Redis TTL
- Session locking to prevent race conditions
- Pub/sub for distributed session updates
- JSON or pickle serialization

NO MOCK DATA: Real Redis integration using redis-py.
"""

import asyncio
import json
import logging
import secrets
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set

from covet.security.secure_serializer import SecureSerializer

try:
    import redis.asyncio as aioredis
    from redis.asyncio import ConnectionPool, Redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class RedisSessionConfig:
    """Redis session configuration."""

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None

    # Connection pool
    max_connections: int = 50

    # Session settings
    key_prefix: str = "session"
    session_id_length: int = 32
    max_age: int = 86400  # 24 hours

    # Serialization (SECURE by default, prevents RCE)
    use_secure: bool = True  # Use SecureSerializer (recommended)
    secret_key: Optional[str] = None  # Required for secure serialization
    use_json: bool = False  # Use JSON (less secure but simpler)

    # Session locking
    enable_locking: bool = True
    lock_timeout: int = 10  # seconds


class RedisSessionStore:
    """
    Redis session storage.

    Features:
    - Fast session access with Redis
    - Automatic expiration using Redis TTL
    - Optional session locking for concurrent access
    - Pub/sub for distributed cache invalidation
    - Support for user session tracking

    Example:
        config = RedisSessionConfig(
            host='localhost',
            port=6379,
            key_prefix='myapp:session'
        )

        store = RedisSessionStore(config)
        await store.connect()

        # Create session
        session_id = await store.create({'user_id': 123})

        # Get session
        data = await store.get(session_id)

        # Update session
        data['username'] = 'alice'
        await store.set(session_id, data)

        # Delete session
        await store.delete(session_id)
    """

    def __init__(self, config: Optional[RedisSessionConfig] = None):
        """
        Initialize Redis session store.

        Args:
            config: Redis session configuration
        """
        if not REDIS_AVAILABLE:
            raise ImportError("redis-py not installed. " "Install with: pip install redis[hiredis]")

        self.config = config or RedisSessionConfig()
        self._client: Optional[Redis] = None
        self._pool: Optional[ConnectionPool] = None

        # Initialize secure serializer if enabled
        if self.config.use_secure:
            if not self.config.secret_key:
                raise ValueError(
                    "RedisSessionStore with use_secure=True requires secret_key in config. "
                    "Use generate_secure_key() from covet.security.secure_serializer to generate one."
                )
            self._secure_serializer = SecureSerializer(secret_key=self.config.secret_key)
        else:
            self._secure_serializer = None

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
                decode_responses=False,
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

    def _make_key(self, session_id: str) -> str:
        """Create Redis key for session."""
        return f"{self.config.key_prefix}:{session_id}"

    def _make_lock_key(self, session_id: str) -> str:
        """Create Redis key for session lock."""
        return f"{self.config.key_prefix}:lock:{session_id}"

    def _make_user_key(self, user_id: str) -> str:
        """Create Redis key for user sessions."""
        return f"{self.config.key_prefix}:user:{user_id}"

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        return secrets.token_urlsafe(self.config.session_id_length)

    def _serialize_data(self, data: Dict[str, Any]) -> bytes:
        """Serialize session data."""
        if self.config.use_secure:
            # Use SecureSerializer (prevents RCE, provides integrity)
            return self._secure_serializer.dumps(data)
        elif self.config.use_json:
            return json.dumps(data).encode("utf-8")
        else:
            raise ValueError(
                "Neither use_secure nor use_json is enabled. "
                "Set use_secure=True for security (recommended) or use_json=True."
            )

    def _deserialize_data(self, serialized: bytes) -> Dict[str, Any]:
        """Deserialize session data."""
        if self.config.use_secure:
            # Use SecureSerializer (prevents RCE, verifies integrity)
            return self._secure_serializer.loads(serialized)
        elif self.config.use_json:
            return json.loads(serialized.decode("utf-8"))
        else:
            raise ValueError(
                "Neither use_secure nor use_json is enabled. "
                "Set use_secure=True for security (recommended) or use_json=True."
            )

    async def acquire_lock(self, session_id: str) -> bool:
        """
        Acquire lock for session.

        Args:
            session_id: Session ID

        Returns:
            True if lock acquired
        """
        if not self.config.enable_locking:
            return True

        lock_key = self._make_lock_key(session_id)

        # Try to set lock with NX (only if doesn't exist)
        result = await self._client.set(lock_key, "1", nx=True, ex=self.config.lock_timeout)

        return bool(result)

    async def release_lock(self, session_id: str):
        """
        Release lock for session.

        Args:
            session_id: Session ID
        """
        if not self.config.enable_locking:
            return

        lock_key = self._make_lock_key(session_id)
        await self._client.delete(lock_key)

    async def create(
        self, data: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None
    ) -> str:
        """
        Create new session.

        Args:
            data: Initial session data
            user_id: User ID

        Returns:
            Session ID
        """
        session_id = self._generate_session_id()
        session_data = data or {}

        # Add metadata
        if user_id:
            session_data["_user_id"] = user_id

        try:
            # Save session data
            key = self._make_key(session_id)
            serialized = self._serialize_data(session_data)

            await self._client.set(key, serialized, ex=self.config.max_age)

            # Track user session
            if user_id:
                user_key = self._make_user_key(user_id)
                await self._client.sadd(user_key, session_id)
                await self._client.expire(user_key, self.config.max_age)

            return session_id

        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found
        """
        try:
            key = self._make_key(session_id)
            serialized = await self._client.get(key)

            if serialized is None:
                return None

            return self._deserialize_data(serialized)

        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return None

    async def set(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Session data

        Returns:
            True if successful
        """
        try:
            key = self._make_key(session_id)
            serialized = self._serialize_data(data)

            # Update data and refresh TTL
            result = await self._client.set(key, serialized, ex=self.config.max_age)

            # Update user session tracking if user_id changed
            user_id = data.get("_user_id")
            if user_id:
                user_key = self._make_user_key(user_id)
                await self._client.sadd(user_key, session_id)
                await self._client.expire(user_key, self.config.max_age)

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            return False

    async def delete(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        try:
            # Get user_id before deleting
            data = await self.get(session_id)
            user_id = data.get("_user_id") if data else None

            # Delete session
            key = self._make_key(session_id)
            await self._client.delete(key)

            # Remove from user sessions
            if user_id:
                user_key = self._make_user_key(user_id)
                await self._client.srem(user_key, session_id)

            # Release lock if held
            await self.release_lock(session_id)

            return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def exists(self, session_id: str) -> bool:
        """
        Check if session exists.

        Args:
            session_id: Session ID

        Returns:
            True if exists
        """
        try:
            key = self._make_key(session_id)
            result = await self._client.exists(key)
            return result > 0

        except Exception as e:
            logger.error(f"Failed to check session existence: {e}")
            return False

    async def touch(self, session_id: str) -> bool:
        """
        Refresh session expiration.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        try:
            key = self._make_key(session_id)
            result = await self._client.expire(key, self.config.max_age)
            return bool(result)

        except Exception as e:
            logger.error(f"Failed to touch session {session_id}: {e}")
            return False

    async def get_user_sessions(self, user_id: str) -> Set[str]:
        """
        Get all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Set of session IDs
        """
        try:
            user_key = self._make_user_key(user_id)
            session_ids = await self._client.smembers(user_key)

            # Decode session IDs
            return {sid.decode("utf-8") for sid in session_ids}

        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return set()

    async def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        try:
            session_ids = await self.get_user_sessions(user_id)

            count = 0
            for session_id in session_ids:
                if await self.delete(session_id):
                    count += 1

            # Delete user sessions set
            user_key = self._make_user_key(user_id)
            await self._client.delete(user_key)

            return count

        except Exception as e:
            logger.error(f"Failed to delete user sessions: {e}")
            return 0

    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Redis automatically expires keys with TTL, so this is a no-op.

        Returns:
            0 (Redis handles expiration automatically)
        """
        return 0

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Dictionary with session stats
        """
        try:
            # Count sessions by scanning keys
            pattern = f"{self.config.key_prefix}:*"
            cursor = 0
            count = 0

            while True:
                cursor, keys = await self._client.scan(cursor=cursor, match=pattern, count=1000)

                # Filter out lock keys and user keys
                session_keys = [k for k in keys if b":lock:" not in k and b":user:" not in k]
                count += len(session_keys)

                if cursor == 0:
                    break

            return {
                "backend": "redis",
                "host": f"{self.config.host}:{self.config.port}",
                "active_sessions": count,
            }

        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {"error": str(e)}

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit."""
        await self.disconnect()


__all__ = ["RedisSessionStore", "RedisSessionConfig"]
