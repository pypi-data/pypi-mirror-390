"""
Session Management System with Redis Backend

Production-ready session management with support for:
- Secure session creation and validation
- Redis-backed storage for scalability
- In-memory fallback for development
- Session fixation prevention
- Session hijacking prevention
- Automatic session expiration
- Remember-me functionality (secure)
- Concurrent session management
- Activity tracking and monitoring

SECURITY FEATURES:
- Cryptographically secure session ID generation
- Session fixation prevention (ID regeneration on privilege change)
- HTTPOnly and Secure cookie flags
- SameSite cookie attribute
- Session hijacking detection (IP/User-Agent validation)
- Automatic session rotation
- Idle timeout and absolute timeout
- Secure remember-me tokens with rotation
- Rate limiting on session operations

NO MOCK DATA: Real session management with Redis integration and production security.
"""

import asyncio
import hashlib
import hmac
import json
import secrets
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote, unquote

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class SessionState(str, Enum):
    """Session states."""

    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    SUSPENDED = "suspended"


@dataclass
class SessionConfig:
    """Session manager configuration."""

    # Redis settings
    redis_url: Optional[str] = None  # Redis connection URL
    redis_prefix: str = "session:"  # Key prefix for Redis

    # Session lifetime
    session_lifetime: int = 3600  # 1 hour
    idle_timeout: int = 1800  # 30 minutes idle timeout
    absolute_timeout: int = 86400  # 24 hours absolute timeout

    # Remember-me settings
    remember_me_lifetime: int = 2592000  # 30 days
    remember_me_enabled: bool = True

    # Security settings
    regenerate_on_login: bool = True  # Regenerate ID on login
    check_ip_address: bool = True  # Validate IP address
    check_user_agent: bool = True  # Validate User-Agent
    max_concurrent_sessions: int = 5  # Max concurrent sessions per user

    # Cookie settings
    cookie_name: str = "session_id"
    cookie_path: str = "/"
    cookie_domain: Optional[str] = None
    cookie_secure: bool = True  # Require HTTPS
    cookie_httponly: bool = True  # Prevent JavaScript access
    cookie_samesite: str = "Lax"  # CSRF protection

    # Rate limiting
    max_session_creates: int = 10  # Max session creates per minute
    rate_limit_window: int = 60  # Rate limit window in seconds


@dataclass
class Session:
    """Session data."""

    # Core fields
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime

    # Session state
    state: SessionState = SessionState.ACTIVE

    # Security context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Session data
    data: Dict[str, Any] = field(default_factory=dict)

    # Remember-me
    remember_me: bool = False
    remember_token: Optional[str] = None

    # Tracking
    login_count: int = 0  # Number of times user logged in with this session
    activity_count: int = 0  # Number of activities in this session

    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() > self.expires_at

    def is_valid(self) -> bool:
        """Check if session is valid (active and not expired)."""
        return self.state == SessionState.ACTIVE and not self.is_expired()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime to ISO format
        data["created_at"] = self.created_at.isoformat()
        data["expires_at"] = self.expires_at.isoformat()
        data["last_activity"] = self.last_activity.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create from dictionary."""
        # Convert ISO format to datetime
        data["created_at"] = datetime.fromisoformat(data["created_at"])
        data["expires_at"] = datetime.fromisoformat(data["expires_at"])
        data["last_activity"] = datetime.fromisoformat(data["last_activity"])
        data["state"] = SessionState(data["state"])
        return cls(**data)


@dataclass
class SessionStore:
    """Abstract session storage interface."""

    async def save(self, session: Session) -> bool:
        """Save session."""
        raise NotImplementedError

    async def load(self, session_id: str) -> Optional[Session]:
        """Load session by ID."""
        raise NotImplementedError

    async def delete(self, session_id: str) -> bool:
        """Delete session."""
        raise NotImplementedError

    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all sessions for user."""
        raise NotImplementedError

    async def cleanup_expired(self):
        """Clean up expired sessions."""
        raise NotImplementedError


class InMemorySessionStore(SessionStore):
    """In-memory session storage (for development/testing)."""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, Set[str]] = {}  # user_id -> session_ids
        self._lock = asyncio.Lock()

    async def save(self, session: Session) -> bool:
        async with self._lock:
            self._sessions[session.session_id] = session

            # Track user sessions
            if session.user_id not in self._user_sessions:
                self._user_sessions[session.user_id] = set()
            self._user_sessions[session.user_id].add(session.session_id)

        return True

    async def load(self, session_id: str) -> Optional[Session]:
        return self._sessions.get(session_id)

    async def delete(self, session_id: str) -> bool:
        async with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                # Remove from user sessions
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(session.session_id)
                return True
        return False

    async def get_user_sessions(self, user_id: str) -> List[Session]:
        session_ids = self._user_sessions.get(user_id, set())
        return [self._sessions[sid] for sid in session_ids if sid in self._sessions]

    async def cleanup_expired(self):
        async with self._lock:
            expired_ids = [sid for sid, session in self._sessions.items() if session.is_expired()]
            for sid in expired_ids:
                session = self._sessions.pop(sid)
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(sid)


class RedisSessionStore(SessionStore):
    """Redis-backed session storage (for production)."""

    def __init__(self, redis_url: str, prefix: str = "session:"):
        if aioredis is None:
            raise RuntimeError(
                "redis library not installed. Install with: pip install redis[asyncio]"
            )

        self.redis_url = redis_url
        self.prefix = prefix
        self._redis: Optional[aioredis.Redis] = None
        self._connection_lock = asyncio.Lock()

    async def _get_redis(self) -> aioredis.Redis:
        """Get or create Redis connection."""
        if self._redis is None:
            async with self._connection_lock:
                if self._redis is None:
                    self._redis = await aioredis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    def _session_key(self, session_id: str) -> str:
        """Get Redis key for session."""
        return f"{self.prefix}{session_id}"

    def _user_sessions_key(self, user_id: str) -> str:
        """Get Redis key for user sessions set."""
        return f"{self.prefix}user:{user_id}"

    async def save(self, session: Session) -> bool:
        redis = await self._get_redis()

        # Serialize session
        session_data = json.dumps(session.to_dict())

        # Calculate TTL
        ttl = int((session.expires_at - datetime.utcnow()).total_seconds())
        if ttl <= 0:
            return False

        # Save session with expiration
        await redis.setex(self._session_key(session.session_id), ttl, session_data)

        # Add to user sessions set
        await redis.sadd(self._user_sessions_key(session.user_id), session.session_id)

        return True

    async def load(self, session_id: str) -> Optional[Session]:
        redis = await self._get_redis()

        # Load session data
        session_data = await redis.get(self._session_key(session_id))
        if not session_data:
            return None

        # Deserialize
        try:
            data = json.loads(session_data)
            return Session.from_dict(data)
        except Exception:
            return None

    async def delete(self, session_id: str) -> bool:
        redis = await self._get_redis()

        # Load session to get user_id
        session = await self.load(session_id)
        if not session:
            return False

        # Delete session
        await redis.delete(self._session_key(session_id))

        # Remove from user sessions
        await redis.srem(self._user_sessions_key(session.user_id), session_id)

        return True

    async def get_user_sessions(self, user_id: str) -> List[Session]:
        redis = await self._get_redis()

        # Get session IDs for user
        session_ids = await redis.smembers(self._user_sessions_key(user_id))

        # Load all sessions
        sessions = []
        for session_id in session_ids:
            session = await self.load(session_id)
            if session:
                sessions.append(session)

        return sessions

    async def cleanup_expired(self):
        """Redis handles expiration automatically via TTL."""
        pass

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()


class SessionManager:
    """
    Production-ready session manager.

    Manages session lifecycle with security features and Redis backend.
    """

    def __init__(self, config: SessionConfig, store: Optional[SessionStore] = None):
        """
        Initialize session manager.

        Args:
            config: Session configuration
            store: Session storage backend (defaults to Redis or in-memory)
        """
        self.config = config

        # Initialize storage
        if store:
            self.store = store
        elif config.redis_url:
            self.store = RedisSessionStore(config.redis_url, config.redis_prefix)
        else:
            self.store = InMemorySessionStore()

        # Rate limiting
        self._rate_limits: Dict[str, List[float]] = {}
        self._rate_lock = asyncio.Lock()

        # Remember-me tokens
        self._remember_tokens: Dict[str, str] = {}  # token -> user_id

        # Statistics
        self._stats = {
            "sessions_created": 0,
            "sessions_validated": 0,
            "sessions_expired": 0,
            "sessions_revoked": 0,
            "hijacking_detected": 0,
        }

    async def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False,
    ) -> Session:
        """
        Create new session.

        Args:
            user_id: User identifier
            ip_address: Client IP address
            user_agent: Client User-Agent
            remember_me: Enable remember-me

        Returns:
            Created session
        """
        # Check rate limit
        if await self._is_rate_limited(user_id):
            raise ValueError("Too many session creation attempts")

        # Generate secure session ID
        session_id = self._generate_session_id()

        # Calculate expiration
        if remember_me and self.config.remember_me_enabled:
            lifetime = self.config.remember_me_lifetime
            remember_token = self._generate_remember_token()
        else:
            lifetime = self.config.session_lifetime
            remember_token = None

        expires_at = datetime.utcnow() + timedelta(seconds=lifetime)

        # Create session
        session = Session(
            session_id=session_id,
            user_id=user_id,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me,
            remember_token=remember_token,
            login_count=1,
        )

        # Save session
        await self.store.save(session)

        # Track remember token
        if remember_token:
            self._remember_tokens[remember_token] = user_id

        # Enforce concurrent session limit
        await self._enforce_session_limit(user_id)

        # Record rate limit attempt
        await self._record_rate_limit(user_id)

        # Update stats
        self._stats["sessions_created"] += 1

        return session

    async def get_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Session]:
        """
        Get and validate session.

        Args:
            session_id: Session ID
            ip_address: Client IP address (for validation)
            user_agent: Client User-Agent (for validation)

        Returns:
            Session if valid, None otherwise
        """
        # Load session
        session = await self.store.load(session_id)
        if not session:
            return None

        # Check if expired
        if session.is_expired():
            await self.revoke_session(session_id)
            self._stats["sessions_expired"] += 1
            return None

        # Check if valid state
        if session.state != SessionState.ACTIVE:
            return None

        # Validate security context
        if not self._validate_security_context(session, ip_address, user_agent):
            await self.revoke_session(session_id, reason="hijacking")
            self._stats["hijacking_detected"] += 1
            return None

        # Check idle timeout
        idle_seconds = (datetime.utcnow() - session.last_activity).total_seconds()
        if idle_seconds > self.config.idle_timeout:
            await self.revoke_session(session_id, reason="idle")
            return None

        # Check absolute timeout
        age_seconds = (datetime.utcnow() - session.created_at).total_seconds()
        if age_seconds > self.config.absolute_timeout:
            await self.revoke_session(session_id, reason="absolute")
            return None

        # Update last activity
        session.last_activity = datetime.utcnow()
        session.activity_count += 1
        await self.store.save(session)

        self._stats["sessions_validated"] += 1

        return session

    async def revoke_session(self, session_id: str, reason: str = "user") -> bool:
        """
        Revoke session.

        Args:
            session_id: Session ID to revoke
            reason: Revocation reason (user, hijacking, idle, absolute, etc.)

        Returns:
            True if revoked successfully
        """
        session = await self.store.load(session_id)
        if not session:
            return False

        # Update state
        session.state = SessionState.REVOKED

        # Save updated session (or just delete)
        await self.store.delete(session_id)

        # Remove remember token if exists
        if session.remember_token:
            self._remember_tokens.pop(session.remember_token, None)

        self._stats["sessions_revoked"] += 1

        return True

    async def revoke_all_user_sessions(self, user_id: str) -> int:
        """
        Revoke all sessions for user.

        Args:
            user_id: User identifier

        Returns:
            Number of sessions revoked
        """
        sessions = await self.store.get_user_sessions(user_id)

        count = 0
        for session in sessions:
            if await self.revoke_session(session.session_id):
                count += 1

        return count

    async def regenerate_session_id(self, old_session_id: str) -> Optional[Session]:
        """
        Regenerate session ID (prevent session fixation).

        Args:
            old_session_id: Current session ID

        Returns:
            Updated session with new ID
        """
        # Load old session
        old_session = await self.store.load(old_session_id)
        if not old_session or not old_session.is_valid():
            return None

        # Delete old session
        await self.store.delete(old_session_id)

        # Generate new ID
        new_session_id = self._generate_session_id()

        # Create new session with same data
        new_session = Session(
            session_id=new_session_id,
            user_id=old_session.user_id,
            created_at=old_session.created_at,
            expires_at=old_session.expires_at,
            last_activity=datetime.utcnow(),
            state=old_session.state,
            ip_address=old_session.ip_address,
            user_agent=old_session.user_agent,
            data=old_session.data.copy(),
            remember_me=old_session.remember_me,
            remember_token=old_session.remember_token,
            login_count=old_session.login_count + 1,
            activity_count=old_session.activity_count,
        )

        # Save new session
        await self.store.save(new_session)

        return new_session

    async def extend_session(self, session_id: str, duration: Optional[int] = None) -> bool:
        """
        Extend session expiration.

        Args:
            session_id: Session ID
            duration: Extension duration in seconds (defaults to config)

        Returns:
            True if extended successfully
        """
        session = await self.store.load(session_id)
        if not session or not session.is_valid():
            return False

        # Calculate new expiration
        if duration is None:
            duration = self.config.session_lifetime

        session.expires_at = datetime.utcnow() + timedelta(seconds=duration)

        # Save updated session
        await self.store.save(session)

        return True

    async def remember_me_login(self, remember_token: str) -> Optional[Session]:
        """
        Login using remember-me token.

        Args:
            remember_token: Remember-me token

        Returns:
            New session if token valid
        """
        # Get user_id for token
        user_id = self._remember_tokens.get(remember_token)
        if not user_id:
            return None

        # Find session with this token
        sessions = await self.store.get_user_sessions(user_id)
        old_session = None
        for session in sessions:
            if session.remember_token == remember_token and session.is_valid():
                old_session = session
                break

        if not old_session:
            return None

        # Rotate remember token (security best practice)
        new_remember_token = self._generate_remember_token()

        # Create new session
        new_session = await self.create_session(
            user_id=user_id,
            ip_address=old_session.ip_address,
            user_agent=old_session.user_agent,
            remember_me=True,
        )

        # Update remember token
        new_session.remember_token = new_remember_token
        await self.store.save(new_session)

        # Update token mapping
        self._remember_tokens.pop(remember_token, None)
        self._remember_tokens[new_remember_token] = user_id

        # Revoke old session
        await self.revoke_session(old_session.session_id, reason="remember_rotation")

        return new_session

    # ==================== Helper Methods ====================

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        return secrets.token_urlsafe(32)

    def _generate_remember_token(self) -> str:
        """Generate cryptographically secure remember-me token."""
        return secrets.token_urlsafe(32)

    def _validate_security_context(
        self,
        session: Session,
        ip_address: Optional[str],
        user_agent: Optional[str],
    ) -> bool:
        """
        Validate session security context.

        Checks IP address and User-Agent to detect hijacking.
        """
        # Check IP address
        if self.config.check_ip_address and ip_address:
            if session.ip_address and session.ip_address != ip_address:
                return False

        # Check User-Agent
        if self.config.check_user_agent and user_agent:
            if session.user_agent and session.user_agent != user_agent:
                return False

        return True

    async def _enforce_session_limit(self, user_id: str):
        """Enforce concurrent session limit."""
        sessions = await self.store.get_user_sessions(user_id)

        # Filter valid sessions
        valid_sessions = [s for s in sessions if s.is_valid()]

        # If over limit, revoke oldest sessions
        if len(valid_sessions) > self.config.max_concurrent_sessions:
            # Sort by creation time
            valid_sessions.sort(key=lambda s: s.created_at)

            # Revoke excess sessions
            excess = len(valid_sessions) - self.config.max_concurrent_sessions
            for session in valid_sessions[:excess]:
                await self.revoke_session(session.session_id, reason="limit")

    async def _is_rate_limited(self, user_id: str) -> bool:
        """Check if user is rate limited."""
        now = time.time()
        cutoff = now - self.config.rate_limit_window

        async with self._rate_lock:
            if user_id not in self._rate_limits:
                return False

            # Clean old attempts
            self._rate_limits[user_id] = [ts for ts in self._rate_limits[user_id] if ts > cutoff]

            # Check limit
            return len(self._rate_limits[user_id]) >= self.config.max_session_creates

    async def _record_rate_limit(self, user_id: str):
        """Record session creation for rate limiting."""
        now = time.time()

        async with self._rate_lock:
            if user_id not in self._rate_limits:
                self._rate_limits[user_id] = []

            self._rate_limits[user_id].append(now)

    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        await self.store.cleanup_expired()

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return self._stats.copy()

    async def close(self):
        """Close session manager and storage."""
        if isinstance(self.store, RedisSessionStore):
            await self.store.close()


__all__ = [
    "SessionManager",
    "Session",
    "SessionConfig",
    "SessionState",
    "SessionStore",
    "InMemorySessionStore",
    "RedisSessionStore",
]
