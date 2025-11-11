"""
Session Manager

Production-ready session management with:
- Multiple backend support
- Security features (CSRF, session fixation prevention, hijacking detection)
- Dictionary-like interface
- Session regeneration
- Flash messages support
- Automatic saving

NO MOCK DATA: Real session management using backends.
"""

import hashlib
import logging
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .backends import (
    CookieSessionConfig,
    CookieSessionStore,
    DatabaseSessionConfig,
    DatabaseSessionStore,
    MemorySessionConfig,
    MemorySessionStore,
    RedisSessionConfig,
    RedisSessionStore,
)

logger = logging.getLogger(__name__)


class SessionBackend(str, Enum):
    """Available session backends."""

    COOKIE = "cookie"
    DATABASE = "database"
    REDIS = "redis"
    MEMORY = "memory"


@dataclass
class SessionConfig:
    """Session manager configuration."""

    # Backend
    backend: SessionBackend = SessionBackend.MEMORY

    # Backend-specific configs
    cookie_config: Optional[CookieSessionConfig] = None
    database_config: Optional[DatabaseSessionConfig] = None
    redis_config: Optional[RedisSessionConfig] = None
    memory_config: Optional[MemorySessionConfig] = None

    # Security settings
    regenerate_on_login: bool = True  # Prevent session fixation
    check_ip_address: bool = True  # Detect session hijacking
    check_user_agent: bool = True  # Detect session hijacking
    csrf_enabled: bool = True  # CSRF protection

    # Session settings
    cookie_name: str = "session_id"
    max_age: int = 86400  # 24 hours


class Session:
    """
    Session object with dictionary-like interface.

    Features:
    - Dictionary-like access (session['key'])
    - Security metadata (IP, user agent)
    - CSRF token management
    - Flash messages
    - Modified tracking for efficient saving

    Example:
        # Set values
        session['user_id'] = 123
        session['username'] = 'alice'

        # Get values
        user_id = session.get('user_id')

        # Delete values
        del session['cart']

        # Check existence
        if 'user_id' in session:
            ...

        # Security
        session.regenerate()  # New session ID
        session.validate_security(request)  # Check IP/UA

        # Flash messages
        session.flash('User created', 'success')
        messages = session.get_flashed_messages()
    """

    def __init__(
        self,
        session_id: Optional[str],
        data: Optional[Dict[str, Any]],
        config: SessionConfig,
        store,
    ):
        """
        Initialize session.

        Args:
            session_id: Session ID (None for new session)
            data: Session data (None for new session)
            config: Session configuration
            store: Session store backend
        """
        self.session_id = session_id
        self._data = data or {}
        self.config = config
        self.store = store

        # Metadata
        self._modified = False
        self._is_new = session_id is None

        # Security metadata
        if "_security" not in self._data:
            self._data["_security"] = {}

        # CSRF token
        if config.csrf_enabled and "_csrf_token" not in self._data:
            self._data["_csrf_token"] = self._generate_csrf_token()
            self._modified = True

        # Flash messages
        if "_flash" not in self._data:
            self._data["_flash"] = []

    def _generate_csrf_token(self) -> str:
        """Generate CSRF token."""
        return secrets.token_urlsafe(32)

    # Dictionary interface
    def __getitem__(self, key: str) -> Any:
        """Get item from session."""
        return self._data[key]

    def __setitem__(self, key: str, value: Any):
        """Set item in session."""
        if not key.startswith("_"):  # Don't allow modifying internal keys
            self._data[key] = value
            self._modified = True

    def __delitem__(self, key: str):
        """Delete item from session."""
        if not key.startswith("_"):
            del self._data[key]
            self._modified = True

    def __contains__(self, key: str) -> bool:
        """Check if key exists in session."""
        return key in self._data

    def get(self, key: str, default: Any = None) -> Any:
        """Get value with default."""
        return self._data.get(key, default)

    def pop(self, key: str, default: Any = None) -> Any:
        """Remove and return value."""
        if not key.startswith("_"):
            value = self._data.pop(key, default)
            self._modified = True
            return value
        return default

    def setdefault(self, key: str, default: Any = None) -> Any:
        """Set default value if key doesn't exist."""
        if key not in self._data and not key.startswith("_"):
            self._data[key] = default
            self._modified = True
        return self._data.get(key, default)

    def keys(self) -> List[str]:
        """Get all keys (excluding internal)."""
        return [k for k in self._data.keys() if not k.startswith("_")]

    def values(self) -> List[Any]:
        """Get all values (excluding internal)."""
        return [v for k, v in self._data.items() if not k.startswith("_")]

    def items(self) -> List[tuple]:
        """Get all items (excluding internal)."""
        return [(k, v) for k, v in self._data.items() if not k.startswith("_")]

    def clear(self):
        """Clear all session data (keep security metadata)."""
        security = self._data.get("_security", {})
        csrf = self._data.get("_csrf_token")
        flash = self._data.get("_flash", [])

        self._data.clear()
        self._data["_security"] = security
        if csrf:
            self._data["_csrf_token"] = csrf
        self._data["_flash"] = flash

        self._modified = True

    # Properties
    @property
    def is_new(self) -> bool:
        """Check if session is new."""
        return self._is_new

    @property
    def modified(self) -> bool:
        """Check if session has been modified."""
        return self._modified

    @property
    def csrf_token(self) -> Optional[str]:
        """Get CSRF token."""
        return self._data.get("_csrf_token")

    # Security methods
    def set_ip_address(self, ip_address: str):
        """Set client IP address for security validation."""
        self._data["_security"]["ip_address"] = ip_address
        self._modified = True

    def set_user_agent(self, user_agent: str):
        """Set client user agent for security validation."""
        # SECURITY FIX: Use SHA-256 instead of MD5
        ua_hash = hashlib.sha256(user_agent.encode("utf-8")).hexdigest()
        self._data["_security"]["user_agent_hash"] = ua_hash
        self._modified = True

    def validate_security(
        self, ip_address: Optional[str] = None, user_agent: Optional[str] = None
    ) -> bool:
        """
        Validate session security.

        Checks IP address and user agent to detect session hijacking.

        Args:
            ip_address: Current client IP address
            user_agent: Current client user agent

        Returns:
            True if validation passes
        """
        security = self._data.get("_security", {})

        # Check IP address
        if self.config.check_ip_address and ip_address:
            stored_ip = security.get("ip_address")
            if stored_ip and stored_ip != ip_address:
                logger.warning(f"Session IP mismatch: {stored_ip} != {ip_address}")
                return False

        # Check user agent
        if self.config.check_user_agent and user_agent:
            stored_hash = security.get("user_agent_hash")
            if stored_hash:
                # SECURITY FIX: Use SHA-256 instead of MD5
                current_hash = hashlib.sha256(user_agent.encode("utf-8")).hexdigest()
                if stored_hash != current_hash:
                    logger.warning("Session user agent mismatch")
                    return False

        return True

    def validate_csrf_token(self, token: str) -> bool:
        """
        Validate CSRF token.

        Args:
            token: Token from form/request

        Returns:
            True if valid
        """
        if not self.config.csrf_enabled:
            return True

        session_token = self._data.get("_csrf_token")
        if not session_token or not token:
            return False

        return secrets.compare_digest(session_token, token)

    async def regenerate(self):
        """
        Regenerate session ID (prevent session fixation).

        Creates new session ID while keeping data.
        Should be called after login/privilege escalation.
        """
        if self.session_id:
            # Delete old session
            await self.store.delete(self.session_id)

        # Generate new session ID
        self.session_id = secrets.token_urlsafe(32)

        # Regenerate CSRF token
        if self.config.csrf_enabled:
            self._data["_csrf_token"] = self._generate_csrf_token()

        self._modified = True
        self._is_new = True

    async def save(self):
        """Save session to backend."""
        if not self.session_id:
            # Create new session
            user_id = self._data.get("user_id")
            self.session_id = await self.store.create(self._data, user_id)
            self._is_new = False
        elif self._modified:
            # Update existing session
            await self.store.set(self.session_id, self._data)

        self._modified = False

    async def destroy(self):
        """Destroy session."""
        if self.session_id:
            await self.store.delete(self.session_id)

        self.session_id = None
        self._data.clear()
        self._modified = False

    # Flash messages
    def flash(self, message: str, category: str = "info"):
        """
        Add flash message.

        Args:
            message: Message text
            category: Message category (info, success, warning, error)
        """
        if "_flash" not in self._data:
            self._data["_flash"] = []

        self._data["_flash"].append({"message": message, "category": category})
        self._modified = True

    def get_flashed_messages(
        self, with_categories: bool = False, category_filter: Optional[List[str]] = None
    ):
        """
        Get and clear flash messages.

        Args:
            with_categories: Include categories in result
            category_filter: Only return messages matching these categories

        Returns:
            List of messages or list of (category, message) tuples
        """
        messages = self._data.get("_flash", [])

        # Filter by category
        if category_filter:
            messages = [m for m in messages if m["category"] in category_filter]

        # Clear messages
        self._data["_flash"] = []
        self._modified = True

        # Format result
        if with_categories:
            return [(m["category"], m["message"]) for m in messages]
        else:
            return [m["message"] for m in messages]


class SessionManager:
    """
    Session manager with multiple backend support.

    Example:
        # Create manager
        config = SessionConfig(
            backend=SessionBackend.REDIS,
            redis_config=RedisSessionConfig(host='localhost'),
            csrf_enabled=True
        )

        manager = SessionManager(config)
        await manager.connect()

        # Load session
        session_id = request.cookies.get('session_id')
        session = await manager.load(session_id)

        # Validate security
        if not session.validate_security(
            ip_address=request.client.host,
            user_agent=request.headers.get('User-Agent')
        ):
            await session.destroy()
            session = await manager.create()

        # Use session
        session['user_id'] = 123
        session.flash('Login successful', 'success')

        # Regenerate on login (prevent fixation)
        await session.regenerate()

        # Save session
        await session.save()
    """

    def __init__(self, config: Optional[SessionConfig] = None):
        """
        Initialize session manager.

        Args:
            config: Session configuration
        """
        self.config = config or SessionConfig()
        self.store = None

    async def connect(self):
        """Initialize session backend."""
        if self.store is not None:
            return

        # Create backend
        if self.config.backend == SessionBackend.COOKIE:
            cookie_config = self.config.cookie_config or CookieSessionConfig(
                secret_key=secrets.token_urlsafe(32)
            )
            self.store = CookieSessionStore(cookie_config)

        elif self.config.backend == SessionBackend.DATABASE:
            if not self.config.database_config:
                raise ValueError("database_config required for database backend")
            self.store = DatabaseSessionStore(
                self.config.database_config.db_connection, self.config.database_config
            )
            await self.store.initialize()

        elif self.config.backend == SessionBackend.REDIS:
            redis_config = self.config.redis_config or RedisSessionConfig()
            self.store = RedisSessionStore(redis_config)
            await self.store.connect()

        elif self.config.backend == SessionBackend.MEMORY:
            memory_config = self.config.memory_config or MemorySessionConfig()
            self.store = MemorySessionStore(memory_config)

        else:
            raise ValueError(f"Unknown session backend: {self.config.backend}")

        logger.info(f"Session manager initialized: {self.config.backend}")

    async def disconnect(self):
        """Close session backend connections."""
        if self.store and hasattr(self.store, "disconnect"):
            await self.store.disconnect()
        self.store = None

    async def create(self, **kwargs) -> Session:
        """
        Create new session.

        Args:
            **kwargs: Additional arguments for session creation

        Returns:
            New Session object
        """
        return Session(None, None, self.config, self.store)

    async def load(self, session_id: Optional[str], cookie_value: Optional[str] = None) -> Session:
        """
        Load session from backend.

        Args:
            session_id: Session ID
            cookie_value: Cookie value (for cookie backend)

        Returns:
            Session object (new if not found)
        """
        if not session_id:
            return await self.create()

        # Load from backend
        if self.config.backend == SessionBackend.COOKIE:
            data = await self.store.get(session_id, cookie_value)
        else:
            data = await self.store.get(session_id)

        if data is None:
            return await self.create()

        return Session(session_id, data, self.config, self.store)

    async def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        if hasattr(self.store, "get_stats"):
            return await self.store.get_stats()
        return {}

    # Context manager support
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, _):
        """Async context manager exit."""
        await self.disconnect()


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


def configure_session_manager(config: SessionConfig) -> SessionManager:
    """Configure global session manager."""
    global _session_manager
    _session_manager = SessionManager(config)
    return _session_manager


__all__ = [
    "Session",
    "SessionManager",
    "SessionConfig",
    "SessionBackend",
    "get_session_manager",
    "configure_session_manager",
]
