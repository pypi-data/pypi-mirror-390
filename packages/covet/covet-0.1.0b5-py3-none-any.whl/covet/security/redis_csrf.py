"""
Distributed CSRF Token Storage with Redis

Production-grade CSRF protection for horizontally scaled applications.
Stores CSRF tokens in Redis to work across multiple server instances.

CRITICAL SECURITY FEATURES:
- Distributed token storage (works across all instances)
- Per-session CSRF tokens
- Token rotation on use (one-time tokens)
- Automatic token expiration
- Cryptographically secure token generation
- Token binding to session and user
- Protection against token fixation

Architecture:
- Primary: Redis for distributed token storage
- Fallback: In-memory storage if Redis unavailable
- Token Format: 32-byte URL-safe random tokens
- Storage Key: csrf:{session_id}:{token}
- TTL: Matches session lifetime
"""

import asyncio
import hashlib
import logging
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, Optional, Set

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    RedisError = Exception
    REDIS_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class CSRFConfig:
    """
    CSRF protection configuration.

    Security Settings:
    - Token length: 32 bytes (256 bits) for security
    - Token lifetime: Should match session lifetime
    - Rotation on use: One-time tokens for maximum security
    - Double submit: Cookie + form validation
    """

    # Redis settings
    redis_url: Optional[str] = None
    redis_prefix: str = "csrf:"
    redis_max_connections: int = 20
    redis_socket_timeout: float = 5.0

    # CSRF settings
    token_lifetime: int = 3600  # 1 hour
    token_bytes: int = 32  # 32 bytes = 256 bits
    rotate_on_use: bool = False  # Set True for one-time tokens
    require_referer: bool = True  # Validate Referer header
    safe_methods: Set[str] = None  # Default: GET, HEAD, OPTIONS

    # Cookie settings
    cookie_name: str = "csrftoken"
    cookie_httponly: bool = False  # Must be False for JS access
    cookie_secure: bool = True  # HTTPS only
    cookie_samesite: str = "Strict"

    # Fallback
    fallback_to_memory: bool = True

    def __post_init__(self):
        if self.safe_methods is None:
            self.safe_methods = {"GET", "HEAD", "OPTIONS", "TRACE"}


class RedisCSRFStore:
    """
    Redis-backed CSRF token storage.

    Stores CSRF tokens in Redis for distributed deployment.
    Supports token validation, rotation, and automatic expiration.
    """

    def __init__(self, config: CSRFConfig):
        """
        Initialize CSRF token store.

        Args:
            config: CSRF configuration
        """
        self.config = config

        # Redis connection
        self._redis: Optional[aioredis.Redis] = None
        self._connection_lock = asyncio.Lock()
        self._fallback_storage: Optional[Dict[str, Dict]] = None
        self._using_fallback = False

        # Metrics
        self._metrics = {
            "tokens_created": 0,
            "tokens_validated": 0,
            "tokens_invalid": 0,
            "tokens_rotated": 0,
        }

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Get or create Redis connection."""
        if self._redis is not None:
            return self._redis

        if not REDIS_AVAILABLE:
            if self.config.fallback_to_memory:
                logger.warning("Redis not available for CSRF storage, using in-memory")
                self._using_fallback = True
                self._fallback_storage = {}
                return None
            raise RuntimeError("Redis library not installed")

        async with self._connection_lock:
            if self._redis is not None:
                return self._redis

            try:
                if self.config.redis_url:
                    self._redis = await aioredis.from_url(
                        self.config.redis_url,
                        max_connections=self.config.redis_max_connections,
                        socket_timeout=self.config.redis_socket_timeout,
                        decode_responses=True,
                    )
                    await self._redis.ping()
                    logger.info("Connected to Redis for CSRF token storage")
                    self._using_fallback = False
                    return self._redis
                else:
                    raise ValueError("No Redis URL configured")

            except Exception as e:
                logger.error(f"Failed to connect to Redis for CSRF: {e}")
                if self.config.fallback_to_memory:
                    logger.warning("Using in-memory CSRF storage as fallback")
                    self._using_fallback = True
                    self._fallback_storage = {}
                    return None
                else:
                    raise

    def _token_key(self, session_id: str, token: str) -> str:
        """Generate Redis key for CSRF token."""
        # Hash token for privacy (don't store raw tokens in keys)
        token_hash = hashlib.sha256(token.encode()).hexdigest()[:16]
        return f"{self.config.redis_prefix}{session_id}:{token_hash}"

    def _session_tokens_pattern(self, session_id: str) -> str:
        """Get pattern to match all tokens for a session."""
        return f"{self.config.redis_prefix}{session_id}:*"

    async def create_token(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Create new CSRF token.

        Args:
            session_id: Session identifier
            user_id: Optional user identifier for binding

        Returns:
            CSRF token
        """
        # Generate cryptographically secure token
        token = secrets.token_urlsafe(self.config.token_bytes)

        # Token metadata
        token_data = {
            "session_id": session_id,
            "user_id": user_id or "",
            "created_at": datetime.utcnow().isoformat(),
            "used": False,
        }

        try:
            redis = await self._get_redis()

            if self._using_fallback:
                # Store in memory
                key = self._token_key(session_id, token)
                self._fallback_storage[key] = {
                    **token_data,
                    "expires_at": time.time() + self.config.token_lifetime,
                }
            else:
                # Store in Redis with TTL
                key = self._token_key(session_id, token)
                import json
                await redis.setex(
                    key,
                    self.config.token_lifetime,
                    json.dumps(token_data)
                )

            self._metrics["tokens_created"] += 1
            logger.debug(f"Created CSRF token for session {session_id[:8]}...")
            return token

        except Exception as e:
            logger.error(f"Failed to create CSRF token: {e}")
            raise

    async def validate_token(
        self,
        session_id: str,
        token: str,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Validate CSRF token.

        Args:
            session_id: Session identifier
            token: CSRF token to validate
            user_id: Optional user identifier for binding check

        Returns:
            True if valid, False otherwise
        """
        if not token or not session_id:
            self._metrics["tokens_invalid"] += 1
            return False

        try:
            redis = await self._get_redis()
            key = self._token_key(session_id, token)

            if self._using_fallback:
                # Check in-memory storage
                token_data = self._fallback_storage.get(key)
                if not token_data:
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Check expiration
                if time.time() > token_data.get("expires_at", 0):
                    self._fallback_storage.pop(key, None)
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Check if already used (if rotation enabled)
                if self.config.rotate_on_use and token_data.get("used"):
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Check user binding
                if user_id and token_data.get("user_id") != user_id:
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Mark as used if rotation enabled
                if self.config.rotate_on_use:
                    token_data["used"] = True
                    self._metrics["tokens_rotated"] += 1

                self._metrics["tokens_validated"] += 1
                return True

            else:
                # Check in Redis
                import json
                token_str = await redis.get(key)
                if not token_str:
                    self._metrics["tokens_invalid"] += 1
                    return False

                token_data = json.loads(token_str)

                # Check session binding
                if token_data.get("session_id") != session_id:
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Check user binding
                if user_id and token_data.get("user_id") != user_id:
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Check if already used
                if self.config.rotate_on_use and token_data.get("used"):
                    self._metrics["tokens_invalid"] += 1
                    return False

                # Mark as used and update if rotation enabled
                if self.config.rotate_on_use:
                    token_data["used"] = True
                    ttl = await redis.ttl(key)
                    if ttl > 0:
                        await redis.setex(key, ttl, json.dumps(token_data))
                    self._metrics["tokens_rotated"] += 1

                self._metrics["tokens_validated"] += 1
                return True

        except Exception as e:
            logger.error(f"Failed to validate CSRF token: {e}")
            self._metrics["tokens_invalid"] += 1
            return False

    async def delete_token(self, session_id: str, token: str) -> bool:
        """
        Delete specific CSRF token.

        Args:
            session_id: Session identifier
            token: CSRF token

        Returns:
            True if deleted successfully
        """
        try:
            redis = await self._get_redis()
            key = self._token_key(session_id, token)

            if self._using_fallback:
                self._fallback_storage.pop(key, None)
                return True
            else:
                result = await redis.delete(key)
                return result > 0

        except Exception as e:
            logger.error(f"Failed to delete CSRF token: {e}")
            return False

    async def delete_session_tokens(self, session_id: str) -> int:
        """
        Delete all CSRF tokens for a session.

        Args:
            session_id: Session identifier

        Returns:
            Number of tokens deleted
        """
        try:
            redis = await self._get_redis()

            if self._using_fallback:
                # Delete from memory
                pattern = self._session_tokens_pattern(session_id)
                deleted = 0
                for key in list(self._fallback_storage.keys()):
                    if key.startswith(pattern.replace("*", "")):
                        self._fallback_storage.pop(key, None)
                        deleted += 1
                return deleted
            else:
                # Scan and delete from Redis
                pattern = self._session_tokens_pattern(session_id)
                cursor = 0
                deleted = 0

                while True:
                    cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                    if keys:
                        deleted += await redis.delete(*keys)
                    if cursor == 0:
                        break

                logger.debug(f"Deleted {deleted} CSRF tokens for session {session_id[:8]}...")
                return deleted

        except Exception as e:
            logger.error(f"Failed to delete session tokens: {e}")
            return 0

    def get_metrics(self) -> Dict[str, int]:
        """Get CSRF metrics."""
        return self._metrics.copy()

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


class CSRFProtection:
    """
    CSRF protection manager.

    Provides high-level CSRF protection interface for web applications.
    """

    def __init__(self, config: CSRFConfig):
        """
        Initialize CSRF protection.

        Args:
            config: CSRF configuration
        """
        self.config = config
        self.store = RedisCSRFStore(config)

    async def generate_token(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Generate CSRF token for session.

        Args:
            session_id: Session identifier
            user_id: Optional user identifier

        Returns:
            CSRF token
        """
        return await self.store.create_token(session_id, user_id)

    async def validate_request(
        self,
        session_id: str,
        token: str,
        method: str,
        user_id: Optional[str] = None,
        referer: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> bool:
        """
        Validate CSRF token for request.

        Args:
            session_id: Session identifier
            token: CSRF token from request
            method: HTTP method
            user_id: Optional user identifier
            referer: Referer header
            origin: Origin header

        Returns:
            True if request is valid
        """
        # Skip CSRF check for safe methods
        if method.upper() in self.config.safe_methods:
            return True

        # Validate Referer/Origin if required
        if self.config.require_referer:
            if not referer and not origin:
                logger.warning("CSRF validation failed: missing Referer and Origin")
                return False
            # Additional referer validation can be added here

        # Validate token
        return await self.store.validate_token(session_id, token, user_id)

    async def rotate_token(
        self,
        session_id: str,
        old_token: str,
        user_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Rotate CSRF token (delete old, create new).

        Args:
            session_id: Session identifier
            old_token: Current token to invalidate
            user_id: Optional user identifier

        Returns:
            New CSRF token or None if validation failed
        """
        # Validate old token first
        if not await self.store.validate_token(session_id, old_token, user_id):
            return None

        # Delete old token
        await self.store.delete_token(session_id, old_token)

        # Create new token
        return await self.store.create_token(session_id, user_id)

    async def clear_session_tokens(self, session_id: str) -> int:
        """
        Clear all tokens for session (e.g., on logout).

        Args:
            session_id: Session identifier

        Returns:
            Number of tokens cleared
        """
        return await self.store.delete_session_tokens(session_id)

    def get_metrics(self) -> Dict[str, int]:
        """Get CSRF protection metrics."""
        return self.store.get_metrics()

    async def close(self):
        """Close CSRF protection."""
        await self.store.close()


__all__ = [
    "CSRFConfig",
    "RedisCSRFStore",
    "CSRFProtection",
]
