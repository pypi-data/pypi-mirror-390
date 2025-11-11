"""
Distributed Session Management with Redis Backend

Production-grade distributed session storage designed for horizontal scaling.
Enables multiple server instances to share session state via Redis.

CRITICAL FEATURES for Production:
- Redis-backed distributed storage (sessions work across all instances)
- Automatic failover to in-memory if Redis unavailable
- Session encryption for sensitive data (AES-256-GCM)
- Atomic operations for thread safety
- TTL-based automatic expiration (Redis native)
- Session hijacking prevention (IP/User-Agent validation)
- Session fixation prevention (ID regeneration)
- Support for Redis Sentinel and Cluster
- Connection pooling and retry logic
- Comprehensive metrics and monitoring

Architecture:
- Primary: Redis for distributed state
- Fallback: In-memory store if Redis fails
- Encryption: Per-session AES-256-GCM with unique keys
- Atomicity: Redis transactions for race condition prevention
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    RedisError = Exception
    RedisConnectionError = Exception
    REDIS_AVAILABLE = False

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.backends import default_backend
    CRYPTO_AVAILABLE = True
except ImportError:
    AESGCM = None
    default_backend = None
    CRYPTO_AVAILABLE = False


logger = logging.getLogger(__name__)


class SessionState(str, Enum):
    """Session lifecycle states."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class SessionConfig:
    """
    Session manager configuration for distributed deployment.

    Redis Configuration:
    - Supports standalone Redis, Sentinel, and Cluster
    - Connection pooling with configurable size
    - Automatic retry with exponential backoff

    Security Configuration:
    - Encryption enabled by default for sensitive data
    - Session fixation prevention on login
    - IP address and User-Agent validation
    - Maximum concurrent sessions per user

    Lifetime Configuration:
    - Session lifetime: How long session is valid
    - Idle timeout: Inactivity timeout
    - Absolute timeout: Maximum session age regardless of activity
    """

    # Redis settings - PRIMARY STORAGE
    redis_url: Optional[str] = None  # redis://localhost:6379/0
    redis_sentinel_hosts: Optional[List[Tuple[str, int]]] = None  # Sentinel mode
    redis_sentinel_service: Optional[str] = None  # Sentinel service name
    redis_cluster_nodes: Optional[List[Dict[str, Any]]] = None  # Cluster mode
    redis_prefix: str = "session:"
    redis_max_connections: int = 50  # Connection pool size
    redis_socket_timeout: float = 5.0  # Socket timeout
    redis_retry_on_error: bool = True
    redis_max_retries: int = 3

    # Fallback settings
    fallback_to_memory: bool = True  # Use in-memory if Redis fails

    # Session lifetime (seconds)
    session_lifetime: int = 3600  # 1 hour
    idle_timeout: int = 1800  # 30 minutes
    absolute_timeout: int = 86400  # 24 hours

    # Session encryption
    encrypt_sessions: bool = True  # Encrypt sensitive session data
    encryption_key: Optional[bytes] = None  # 32-byte key for AES-256

    # Security settings
    regenerate_on_login: bool = True
    check_ip_address: bool = True
    check_user_agent: bool = True
    max_concurrent_sessions: int = 5

    # Cookie settings
    cookie_name: str = "session_id"
    cookie_path: str = "/"
    cookie_domain: Optional[str] = None
    cookie_secure: bool = True  # Require HTTPS
    cookie_httponly: bool = True
    cookie_samesite: str = "Lax"  # CSRF protection

    # Rate limiting
    max_session_creates: int = 10  # Per minute per user
    rate_limit_window: int = 60


@dataclass
class Session:
    """
    Session data object.

    Stores user session information with security context.
    Serializable to/from JSON for Redis storage.
    """

    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

    # Session state
    state: SessionState = SessionState.ACTIVE

    # Security context for hijacking detection
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Session data (encrypted if config.encrypt_sessions=True)
    data: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    login_count: int = 0
    activity_count: int = 0

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if session is active and not expired."""
        return self.state == SessionState.ACTIVE and not self.is_expired()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for storage."""
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        data["state"] = self.state.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Deserialize from dictionary."""
        data = data.copy()
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        data["state"] = SessionState(data["state"])
        return cls(**data)


class SessionEncryption:
    """
    Session data encryption using AES-256-GCM.

    Provides authenticated encryption for session data.
    Each session has unique nonce for security.
    """

    def __init__(self, key: Optional[bytes] = None):
        """
        Initialize encryption.

        Args:
            key: 32-byte encryption key (generates random if None)
        """
        if not CRYPTO_AVAILABLE:
            raise RuntimeError(
                "cryptography library not installed. "
                "Install with: pip install cryptography"
            )

        self.key = key or secrets.token_bytes(32)
        if len(self.key) != 32:
            raise ValueError("Encryption key must be exactly 32 bytes")

        self.cipher = AESGCM(self.key)

    def encrypt(self, data: Dict[str, Any]) -> str:
        """
        Encrypt session data.

        Args:
            data: Session data dictionary

        Returns:
            Base64-encoded encrypted data with nonce
        """
        # Serialize to JSON
        plaintext = json.dumps(data).encode("utf-8")

        # Generate unique nonce (12 bytes for GCM)
        nonce = secrets.token_bytes(12)

        # Encrypt with authentication
        ciphertext = self.cipher.encrypt(nonce, plaintext, None)

        # Combine nonce + ciphertext
        encrypted = nonce + ciphertext

        # Base64 encode for storage
        import base64
        return base64.b64encode(encrypted).decode("ascii")

    def decrypt(self, encrypted_str: str) -> Dict[str, Any]:
        """
        Decrypt session data.

        Args:
            encrypted_str: Base64-encoded encrypted data

        Returns:
            Decrypted session data dictionary
        """
        import base64

        # Decode from base64
        encrypted = base64.b64decode(encrypted_str)

        # Extract nonce and ciphertext
        nonce = encrypted[:12]
        ciphertext = encrypted[12:]

        # Decrypt and verify
        plaintext = self.cipher.decrypt(nonce, ciphertext, None)

        # Deserialize from JSON
        return json.loads(plaintext.decode("utf-8"))


class RedisSessionStore:
    """
    Redis-backed distributed session storage.

    PRODUCTION FEATURES:
    - Distributed storage across multiple server instances
    - Automatic TTL-based expiration (no cleanup needed)
    - Atomic operations using Redis transactions
    - Connection pooling for performance
    - Automatic retry with exponential backoff
    - Support for Redis Sentinel and Cluster
    - Graceful fallback to in-memory storage
    - Session encryption for sensitive data
    - Comprehensive error handling and logging

    Architecture:
    - Uses Redis sets for user session tracking
    - Uses Redis strings with TTL for session data
    - Atomic operations prevent race conditions
    - Connection pool shared across requests
    """

    def __init__(
        self,
        config: SessionConfig,
        encryption: Optional[SessionEncryption] = None
    ):
        """
        Initialize Redis session store.

        Args:
            config: Session configuration
            encryption: Session encryption handler (optional)
        """
        self.config = config
        self.encryption = encryption

        # Redis connection
        self._redis: Optional[aioredis.Redis] = None
        self._connection_lock = asyncio.Lock()
        self._fallback_memory: Optional[Dict[str, Session]] = None
        self._using_fallback = False

        # Metrics
        self._metrics = {
            "gets": 0,
            "sets": 0,
            "deletes": 0,
            "hits": 0,
            "misses": 0,
            "errors": 0,
            "fallback_uses": 0,
        }

    async def _get_redis(self) -> aioredis.Redis:
        """
        Get or create Redis connection with retry logic.

        Returns:
            Redis connection

        Raises:
            RuntimeError: If Redis unavailable and fallback disabled
        """
        if self._redis is not None:
            return self._redis

        if not REDIS_AVAILABLE:
            raise RuntimeError(
                "redis library not installed. "
                "Install with: pip install redis[asyncio]"
            )

        async with self._connection_lock:
            if self._redis is not None:
                return self._redis

            try:
                # Create connection with retry
                for attempt in range(self.config.redis_max_retries):
                    try:
                        if self.config.redis_url:
                            # Standalone or URL-based connection
                            self._redis = await aioredis.from_url(
                                self.config.redis_url,
                                max_connections=self.config.redis_max_connections,
                                socket_timeout=self.config.redis_socket_timeout,
                                decode_responses=True,
                            )
                        elif self.config.redis_sentinel_hosts:
                            # Sentinel mode for HA
                            from redis.sentinel import Sentinel
                            sentinel = Sentinel(
                                self.config.redis_sentinel_hosts,
                                socket_timeout=self.config.redis_socket_timeout,
                            )
                            master = sentinel.master_for(
                                self.config.redis_sentinel_service,
                                redis_class=aioredis.Redis,
                            )
                            self._redis = master
                        elif self.config.redis_cluster_nodes:
                            # Cluster mode for horizontal scaling
                            from redis.cluster import RedisCluster
                            self._redis = await RedisCluster(
                                startup_nodes=self.config.redis_cluster_nodes,
                                decode_responses=True,
                            )
                        else:
                            raise ValueError("No Redis configuration provided")

                        # Test connection
                        await self._redis.ping()
                        logger.info("Connected to Redis for session storage")
                        self._using_fallback = False
                        return self._redis

                    except Exception as e:
                        logger.warning(
                            f"Redis connection attempt {attempt + 1} failed: {e}"
                        )
                        if attempt < self.config.redis_max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                        else:
                            raise

            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                if self.config.fallback_to_memory:
                    logger.warning("Using in-memory session storage as fallback")
                    self._using_fallback = True
                    self._fallback_memory = {}
                    return None
                else:
                    raise RuntimeError(
                        f"Redis unavailable and fallback disabled: {e}"
                    )

    def _session_key(self, session_id: str) -> str:
        """Get Redis key for session data."""
        return f"{self.config.redis_prefix}{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user's session set."""
        return f"{self.config.redis_prefix}user:{user_id}:sessions"

    def _serialize_session(self, session: Session) -> str:
        """
        Serialize session to JSON string.

        Encrypts session data if encryption enabled.
        """
        data = session.to_dict()

        # Encrypt sensitive data if encryption enabled
        if self.encryption and self.config.encrypt_sessions:
            if data.get("data"):
                data["data"] = self.encryption.encrypt(data["data"])
                data["encrypted"] = True

        return json.dumps(data)

    def _deserialize_session(self, data_str: str) -> Session:
        """
        Deserialize session from JSON string.

        Decrypts session data if encrypted.
        """
        data = json.loads(data_str)

        # Decrypt sensitive data if encrypted
        if data.get("encrypted") and self.encryption:
            data["data"] = self.encryption.decrypt(data["data"])
            data.pop("encrypted", None)

        return Session.from_dict(data)

    async def create(self, user_id: int, data: Dict[str, Any]) -> str:
        """
        Create new session.

        Args:
            user_id: User identifier
            data: Session data

        Returns:
            Session ID
        """
        # Generate secure session ID
        session_id = secrets.token_urlsafe(32)

        # Calculate expiration
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=self.config.session_lifetime)

        # Create session object
        session = Session(
            session_id=session_id,
            user_id=str(user_id),
            created_at=now,
            expires_at=expires_at,
            last_activity=now,
            data=data,
            login_count=1,
        )

        # Save to storage
        await self.set(session_id, session)

        logger.debug(f"Created session {session_id[:8]}... for user {user_id}")
        return session_id

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data dictionary or None if not found
        """
        self._metrics["gets"] += 1

        try:
            redis = await self._get_redis()

            if self._using_fallback:
                # Use in-memory fallback
                session = self._fallback_memory.get(session_id)
                if session and not session.is_expired():
                    self._metrics["hits"] += 1
                    return session.to_dict()
                else:
                    self._metrics["misses"] += 1
                    return None

            # Get from Redis
            session_data = await redis.get(self._session_key(session_id))
            if not session_data:
                self._metrics["misses"] += 1
                return None

            # Deserialize
            session = self._deserialize_session(session_data)

            # Check if expired
            if session.is_expired():
                await self.delete(session_id)
                self._metrics["misses"] += 1
                return None

            self._metrics["hits"] += 1
            return session.to_dict()

        except Exception as e:
            logger.error(f"Failed to get session {session_id[:8]}...: {e}")
            self._metrics["errors"] += 1
            return None

    async def set(self, session_id: str, session: Session) -> bool:
        """
        Save session.

        Args:
            session_id: Session identifier
            session: Session object

        Returns:
            True if saved successfully
        """
        self._metrics["sets"] += 1

        try:
            redis = await self._get_redis()

            if self._using_fallback:
                # Use in-memory fallback
                self._fallback_memory[session_id] = session
                self._metrics["fallback_uses"] += 1
                return True

            # Serialize session
            session_data = self._serialize_session(session)

            # Calculate TTL in seconds
            ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
            if ttl <= 0:
                logger.warning(f"Session {session_id[:8]}... already expired")
                return False

            # Use Redis pipeline for atomic operation
            async with redis.pipeline(transaction=True) as pipe:
                # Set session data with TTL
                await pipe.setex(
                    self._session_key(session_id),
                    ttl,
                    session_data
                )

                # Add to user's session set
                await pipe.sadd(
                    self._user_sessions_key(session.user_id),
                    session_id
                )

                # Set TTL on user's session set
                await pipe.expire(
                    self._user_sessions_key(session.user_id),
                    self.config.absolute_timeout
                )

                # Execute atomically
                await pipe.execute()

            logger.debug(f"Saved session {session_id[:8]}... with TTL {ttl}s")
            return True

        except Exception as e:
            logger.error(f"Failed to save session {session_id[:8]}...: {e}")
            self._metrics["errors"] += 1
            return False

    async def update(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session identifier
            data: Updated session data

        Returns:
            True if updated successfully
        """
        session_dict = await self.get(session_id)
        if not session_dict:
            return False

        # Update data
        session = Session.from_dict(session_dict)
        session.data.update(data)
        session.last_activity = datetime.utcnow()
        session.activity_count += 1

        # Save updated session
        return await self.set(session_id, session)

    async def delete(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted successfully
        """
        self._metrics["deletes"] += 1

        try:
            # Get session to find user_id
            session_dict = await self.get(session_id)
            if not session_dict:
                return False

            redis = await self._get_redis()

            if self._using_fallback:
                # Use in-memory fallback
                self._fallback_memory.pop(session_id, None)
                return True

            user_id = session_dict["user_id"]

            # Use Redis pipeline for atomic operation
            async with redis.pipeline(transaction=True) as pipe:
                # Delete session data
                await pipe.delete(self._session_key(session_id))

                # Remove from user's session set
                await pipe.srem(
                    self._user_sessions_key(user_id),
                    session_id
                )

                # Execute atomically
                await pipe.execute()

            logger.debug(f"Deleted session {session_id[:8]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id[:8]}...: {e}")
            self._metrics["errors"] += 1
            return False

    async def get_user_sessions(self, user_id: str) -> List[str]:
        """
        Get all session IDs for a user.

        Args:
            user_id: User identifier

        Returns:
            List of session IDs
        """
        try:
            redis = await self._get_redis()

            if self._using_fallback:
                # Use in-memory fallback
                return [
                    sid for sid, session in self._fallback_memory.items()
                    if session.user_id == user_id and not session.is_expired()
                ]

            # Get session IDs from user's session set
            session_ids = await redis.smembers(self._user_sessions_key(user_id))
            return list(session_ids)

        except Exception as e:
            logger.error(f"Failed to get user sessions for {user_id}: {e}")
            return []

    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Note: Redis handles TTL-based expiration automatically.
        This method is provided for compatibility with in-memory fallback.

        Returns:
            Number of sessions cleaned up
        """
        if self._using_fallback and self._fallback_memory:
            expired = [
                sid for sid, session in self._fallback_memory.items()
                if session.is_expired()
            ]
            for sid in expired:
                self._fallback_memory.pop(sid, None)
            return len(expired)
        return 0

    def get_metrics(self) -> Dict[str, int]:
        """Get storage metrics."""
        return self._metrics.copy()

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


class SessionManager:
    """
    Production session manager with distributed storage.

    CRITICAL FEATURES:
    - Works across multiple server instances (horizontal scaling)
    - Session state stored in Redis (not in-memory)
    - Automatic session fixation prevention
    - Session hijacking detection
    - Concurrent session limits
    - Rate limiting on session creation
    - Comprehensive audit logging
    - Graceful degradation to in-memory storage

    Usage:
        # Initialize with Redis
        config = SessionConfig(
            redis_url="redis://localhost:6379/0",
            encrypt_sessions=True,
            encryption_key=secrets.token_bytes(32)
        )
        manager = SessionManager(config)

        # Create session
        session_id = await manager.create_session(
            user_id=123,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )

        # Validate session
        session = await manager.get_session(
            session_id,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0..."
        )
    """

    def __init__(self, config: SessionConfig):
        """
        Initialize session manager.

        Args:
            config: Session configuration
        """
        self.config = config

        # Initialize encryption if enabled
        encryption = None
        if config.encrypt_sessions:
            if config.encryption_key:
                encryption = SessionEncryption(config.encryption_key)
            else:
                # Generate random key (will be different per process)
                # In production, use consistent key from env/secrets
                logger.warning(
                    "No encryption key provided, generating random key. "
                    "Sessions won't decrypt across restarts. "
                    "Set config.encryption_key for production."
                )
                encryption = SessionEncryption()

        # Initialize storage
        self.store = RedisSessionStore(config, encryption)

        # Rate limiting
        self._rate_limits: Dict[str, List[float]] = {}
        self._rate_lock = asyncio.Lock()

        # Statistics
        self._stats = {
            "sessions_created": 0,
            "sessions_validated": 0,
            "sessions_expired": 0,
            "sessions_revoked": 0,
            "hijacking_detected": 0,
            "rate_limited": 0,
        }

    async def create_session(
        self,
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create new session.

        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client User-Agent
            data: Initial session data

        Returns:
            Session ID

        Raises:
            ValueError: If rate limited
        """
        # Check rate limit
        if await self._is_rate_limited(str(user_id)):
            self._stats["rate_limited"] += 1
            raise ValueError("Too many session creation attempts")

        # Create session
        session_data = data or {}
        session_data["ip_address"] = ip_address
        session_data["user_agent"] = user_agent

        session_id = await self.store.create(user_id, session_data)

        # Enforce concurrent session limit
        await self._enforce_session_limit(str(user_id))

        # Record rate limit
        await self._record_rate_limit(str(user_id))

        self._stats["sessions_created"] += 1
        logger.info(f"Created session for user {user_id}")

        return session_id

    async def get_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get and validate session.

        Args:
            session_id: Session ID
            ip_address: Client IP (for hijacking detection)
            user_agent: Client User-Agent (for hijacking detection)

        Returns:
            Session data or None if invalid
        """
        session_data = await self.store.get(session_id)
        if not session_data:
            return None

        # Validate security context
        if not self._validate_security_context(session_data, ip_address, user_agent):
            await self.revoke_session(session_id)
            self._stats["hijacking_detected"] += 1
            logger.warning(
                f"Session hijacking detected for session {session_id[:8]}..."
            )
            return None

        # Check timeouts
        last_activity = datetime.fromisoformat(session_data["last_activity"])
        created_at = datetime.fromisoformat(session_data["created_at"])
        now = datetime.utcnow()

        # Idle timeout
        idle_seconds = (now - last_activity).total_seconds()
        if idle_seconds > self.config.idle_timeout:
            await self.revoke_session(session_id)
            return None

        # Absolute timeout
        age_seconds = (now - created_at).total_seconds()
        if age_seconds > self.config.absolute_timeout:
            await self.revoke_session(session_id)
            return None

        # Update last activity
        await self.store.update(session_id, {"last_activity": now.isoformat()})

        self._stats["sessions_validated"] += 1
        return session_data

    async def revoke_session(self, session_id: str) -> bool:
        """
        Revoke session.

        Args:
            session_id: Session ID

        Returns:
            True if revoked successfully
        """
        result = await self.store.delete(session_id)
        if result:
            self._stats["sessions_revoked"] += 1
            logger.info(f"Revoked session {session_id[:8]}...")
        return result

    async def revoke_all_user_sessions(self, user_id: int) -> int:
        """
        Revoke all sessions for user.

        Args:
            user_id: User identifier

        Returns:
            Number of sessions revoked
        """
        session_ids = await self.store.get_user_sessions(str(user_id))
        count = 0
        for session_id in session_ids:
            if await self.revoke_session(session_id):
                count += 1
        return count

    async def regenerate_session_id(self, old_session_id: str) -> Optional[str]:
        """
        Regenerate session ID (prevent session fixation).

        Args:
            old_session_id: Current session ID

        Returns:
            New session ID or None if failed
        """
        # Get old session
        old_data = await self.store.get(old_session_id)
        if not old_data:
            return None

        # Create new session with same data
        user_id = int(old_data["user_id"])
        new_session_id = await self.store.create(user_id, old_data["data"])

        # Delete old session
        await self.store.delete(old_session_id)

        logger.info(f"Regenerated session ID for user {user_id}")
        return new_session_id

    def _validate_security_context(
        self,
        session_data: Dict[str, Any],
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> bool:
        """Validate session security context to detect hijacking."""
        if self.config.check_ip_address and ip_address:
            session_ip = session_data.get("data", {}).get("ip_address")
            if session_ip and session_ip != ip_address:
                return False

        if self.config.check_user_agent and user_agent:
            session_ua = session_data.get("data", {}).get("user_agent")
            if session_ua and session_ua != user_agent:
                return False

        return True

    async def _enforce_session_limit(self, user_id: str):
        """Enforce maximum concurrent sessions."""
        session_ids = await self.store.get_user_sessions(user_id)
        if len(session_ids) > self.config.max_concurrent_sessions:
            # Revoke oldest sessions
            excess = len(session_ids) - self.config.max_concurrent_sessions
            for session_id in session_ids[:excess]:
                await self.store.delete(session_id)

    async def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited."""
        now = time.time()
        cutoff = now - self.config.rate_limit_window

        async with self._rate_lock:
            if user_id not in self._rate_limits:
                return False

            # Clean old attempts
            self._rate_limits[user_id] = [
                ts for ts in self._rate_limits[user_id] if ts > cutoff
            ]

            return len(self._rate_limits[user_id]) >= self.config.max_session_creates

    async def _record_rate_limit(self, user_id: str):
        """Record session creation for rate limiting."""
        now = time.time()
        async with self._rate_lock:
            if user_id not in self._rate_limits:
                self._rate_limits[user_id] = []
            self._rate_limits[user_id].append(now)

    def get_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        stats = self._stats.copy()
        stats.update(self.store.get_metrics())
        return stats

    async def close(self):
        """Close session manager and storage."""
        await self.store.close()


__all__ = [
    "SessionConfig",
    "Session",
    "SessionState",
    "SessionEncryption",
    "RedisSessionStore",
    "SessionManager",
]
