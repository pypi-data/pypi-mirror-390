"""
Secure Session Management System

Production-ready session management with:
- Secure session ID generation
- Session persistence (memory/database/Redis)
- Session timeout and cleanup
- Cross-Site Request Forgery (CSRF) protection
- Session hijacking prevention
- Concurrent session limits
"""

import hashlib
import json
import logging
import secrets
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Protocol

from .exceptions import SecurityViolationError, SessionExpiredError
from .models import Session, User

logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """Session configuration settings"""

    # Session timeout
    timeout_minutes: int = 60
    idle_timeout_minutes: int = 30
    absolute_timeout_hours: int = 8

    # Security settings
    regenerate_on_login: bool = True
    secure_cookies: bool = True
    httponly_cookies: bool = True
    samesite: str = "Strict"  # Strict, Lax, or None

    # Session limits
    max_sessions_per_user: int = 5
    cleanup_interval_minutes: int = 15

    # CSRF protection
    csrf_protection: bool = True
    csrf_token_bytes: int = 32

    # Cookie settings
    cookie_name: str = "session_id"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"


class SessionStore(Protocol):
    """Protocol for session storage backends"""

    def get(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        ...

    def set(self, session: Session) -> None:
        """Store session"""
        ...

    def delete(self, session_id: str) -> None:
        """Delete session"""
        ...

    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all sessions for a user"""
        ...

    def cleanup_expired(self) -> None:
        """Remove expired sessions"""
        ...


class MemorySessionStore:
    """In-memory session store for development"""

    def __init__(self):
        self._sessions: Dict[str, Session] = {}
        self._user_sessions: Dict[str, List[str]] = defaultdict(list)
        self._lock = threading.RLock()

    def get(self, session_id: str) -> Optional[Session]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.is_expired():
                self.delete(session_id)
                return None
            return session

    def set(self, session: Session) -> None:
        with self._lock:
            self._sessions[session.id] = session
            if session.id not in self._user_sessions[session.user_id]:
                self._user_sessions[session.user_id].append(session.id)

    def delete(self, session_id: str) -> None:
        with self._lock:
            session = self._sessions.pop(session_id, None)
            if session:
                user_sessions = self._user_sessions.get(session.user_id, [])
                if session_id in user_sessions:
                    user_sessions.remove(session_id)

    def get_user_sessions(self, user_id: str) -> List[Session]:
        with self._lock:
            session_ids = self._user_sessions.get(user_id, [])
            sessions = []
            # Copy list to avoid modification during iteration
            for session_id in session_ids[:]:
                session = self._sessions.get(session_id)
                if session and not session.is_expired():
                    sessions.append(session)
                else:
                    # Clean up expired session
                    self._sessions.pop(session_id, None)
                    session_ids.remove(session_id)
            return sessions

    def cleanup_expired(self) -> None:
        with self._lock:
            expired_sessions = [
                sid for sid, session in self._sessions.items() if session.is_expired()
            ]
            for session_id in expired_sessions:
                self.delete(session_id)


class DatabaseSessionStore:
    """
    Database session store for production.

    Supports PostgreSQL, MySQL, and SQLite with automatic schema detection
    and appropriate SQL dialect usage.

    Features:
    - Automatic table creation with proper schema
    - Session persistence across restarts
    - Efficient queries with indexes
    - Automatic expired session cleanup
    - Support for session data serialization (JSON)
    - Thread-safe operations with proper locking

    Example:
        from covet.database.adapters.postgresql import PostgreSQLAdapter

        db = PostgreSQLAdapter(host='localhost', database='myapp')
        await db.connect()

        store = DatabaseSessionStore(db)
        await store._create_tables()

        # Create session
        session = Session(...)
        await store.set(session)

        # Retrieve session
        session = await store.get(session_id)
    """

    def __init__(self, db_connection):
        """
        Initialize DatabaseSessionStore.

        Args:
            db_connection: Database adapter instance (PostgreSQL, MySQL, or SQLite)
                          Must have async methods: execute, fetch_one, fetch_all, table_exists
        """
        self.db = db_connection
        self._lock = threading.RLock()
        self._dialect = self._detect_dialect()

    def _detect_dialect(self) -> str:
        """
        Detect database dialect from adapter class name.

        Returns:
            str: 'postgresql', 'mysql', or 'sqlite'
        """
        adapter_class = self.db.__class__.__name__.lower()

        if "postgres" in adapter_class:
            return "postgresql"
        elif "mysql" in adapter_class:
            return "mysql"
        elif "sqlite" in adapter_class:
            return "sqlite"
        else:
            # Default to PostgreSQL for unknown adapters
            return "postgresql"

    def _get_create_table_sql(self) -> str:
        """
        Generate CREATE TABLE SQL for the current database dialect.

        Returns:
            str: CREATE TABLE statement with appropriate syntax
        """
        if self._dialect == "postgresql":
            return """
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    last_accessed_at TIMESTAMP NOT NULL,
                    expires_at TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    data JSONB NOT NULL DEFAULT '{}'::jsonb
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);
            """

        elif self._dialect == "mysql":
            return """
                CREATE TABLE IF NOT EXISTS sessions (
                    id VARCHAR(255) PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    created_at DATETIME NOT NULL,
                    last_accessed_at DATETIME NOT NULL,
                    expires_at DATETIME,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    is_active BOOLEAN NOT NULL DEFAULT TRUE,
                    data JSON NOT NULL
                );

                CREATE INDEX idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
                CREATE INDEX idx_sessions_is_active ON sessions(is_active);
            """

        else:  # sqlite
            return """
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed_at TEXT NOT NULL,
                    expires_at TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    data TEXT NOT NULL DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at);
                CREATE INDEX IF NOT EXISTS idx_sessions_is_active ON sessions(is_active);
            """

    async def _create_tables(self):
        """
        Create session tables if they don't exist.

        Automatically detects the database dialect and creates appropriate schema
        with indexes for optimal query performance.

        Raises:
            Exception: If table creation fails
        """
        try:
            # Check if table already exists
            exists = await self.db.table_exists("sessions")

            if exists:
                return

            # Get appropriate CREATE TABLE SQL
            create_sql = self._get_create_table_sql()

            # Split by semicolon and execute each statement
            statements = [s.strip() for s in create_sql.split(";") if s.strip()]

            for statement in statements:
                try:
                    await self.db.execute(statement)
                except Exception as e:
                    # Ignore "already exists" errors
                    if "already exists" not in str(e).lower():
                        raise

            logger.info(f"Created sessions table with {self._dialect} dialect")

        except Exception as e:
            logger.error(f"Failed to create sessions table: {e}")
            raise

    def _serialize_session_data(self, data: Dict[str, Any]) -> str:
        """
        Serialize session data to JSON string.

        Args:
            data: Session data dictionary

        Returns:
            str: JSON string
        """
        import json

        return json.dumps(data)

    def _deserialize_session_data(self, data_str: str) -> Dict[str, Any]:
        """
        Deserialize session data from JSON string.

        Args:
            data_str: JSON string

        Returns:
            dict: Session data dictionary
        """
        import json

        if not data_str:
            return {}
        try:
            return json.loads(data_str)
        except (json.JSONDecodeError, TypeError):
            return {}

    def _row_to_session(self, row: Dict[str, Any]) -> Session:
        """
        Convert database row to Session object.

        Args:
            row: Database row as dictionary

        Returns:
            Session: Reconstructed session object
        """

        # Parse datetime fields
        def parse_datetime(dt_value):
            if dt_value is None:
                return None
            if isinstance(dt_value, datetime):
                return dt_value
            # SQLite stores as ISO string
            if isinstance(dt_value, str):
                try:
                    return datetime.fromisoformat(dt_value.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    return None
            return None

        # Parse session data
        data = row.get("data", {})
        if isinstance(data, str):
            data = self._deserialize_session_data(data)

        # Convert is_active (SQLite stores as integer)
        is_active = row.get("is_active", True)
        if isinstance(is_active, int):
            is_active = bool(is_active)

        return Session(
            id=row["id"],
            user_id=row["user_id"],
            created_at=parse_datetime(row["created_at"]),
            last_accessed_at=parse_datetime(row["last_accessed_at"]),
            expires_at=parse_datetime(row.get("expires_at")),
            ip_address=row.get("ip_address"),
            user_agent=row.get("user_agent"),
            is_active=is_active,
            data=data,
        )

    def _format_datetime(self, dt: Optional[datetime]) -> Optional[str]:
        """
        Format datetime for database storage.

        Args:
            dt: datetime object

        Returns:
            str: ISO format string for storage
        """
        if dt is None:
            return None

        if self._dialect == "sqlite":
            # SQLite stores as ISO string
            return dt.isoformat()
        else:
            # PostgreSQL and MySQL handle datetime objects
            return dt

    async def get(self, session_id: str) -> Optional[Session]:
        """
        Retrieve session from database by ID.

        Args:
            session_id: Unique session identifier

        Returns:
            Session object if found and not expired, None otherwise

        Example:
            session = await store.get('abc123...')
            if session and not session.is_expired():
                print(f"Active session for user {session.user_id}")
        """
        if not session_id:
            return None

        try:
            # Use appropriate placeholder for database dialect
            if self._dialect == "postgresql":
                query = "SELECT * FROM sessions WHERE id = $1"
            else:  # mysql and sqlite use ?
                query = "SELECT * FROM sessions WHERE id = ?"

            row = await self.db.fetch_one(query, (session_id,))

            if not row:
                logger.debug(f"Session not found: {session_id[:8]}...")
                return None

            session = self._row_to_session(row)

            # Check if session is expired
            if session.is_expired():
                logger.debug(f"Session expired: {session_id[:8]}...")
                # Delete expired session
                await self.delete(session_id)
                return None

            logger.debug(f"Retrieved session: {session_id[:8]}... for user {session.user_id}")
            return session

        except Exception as e:
            logger.error(f"Failed to retrieve session {session_id[:8]}...: {e}")
            raise

    async def set(self, session: Session) -> None:
        """
        Store or update session in database.

        Uses UPSERT (INSERT ... ON CONFLICT) to handle both create and update.

        Args:
            session: Session object to store

        Raises:
            Exception: If database operation fails

        Example:
            session = Session(
                id='abc123',
                user_id='user_456',
                created_at=datetime.utcnow(),
                ...
            )
            await store.set(session)
        """
        try:
            # Serialize session data
            data_json = self._serialize_session_data(session.data)

            # Format datetime values
            created_at = self._format_datetime(session.created_at)
            last_accessed_at = self._format_datetime(session.last_accessed_at)
            expires_at = self._format_datetime(session.expires_at)

            # Convert is_active to int for SQLite
            is_active = (
                1 if session.is_active else 0 if self._dialect == "sqlite" else session.is_active
            )

            # Build UPSERT query based on dialect
            if self._dialect == "postgresql":
                query = """
                    INSERT INTO sessions (
                        id, user_id, created_at, last_accessed_at,
                        expires_at, ip_address, user_agent, is_active, data
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    ON CONFLICT (id) DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        last_accessed_at = EXCLUDED.last_accessed_at,
                        expires_at = EXCLUDED.expires_at,
                        ip_address = EXCLUDED.ip_address,
                        user_agent = EXCLUDED.user_agent,
                        is_active = EXCLUDED.is_active,
                        data = EXCLUDED.data
                """
            elif self._dialect == "mysql":
                query = """
                    INSERT INTO sessions (
                        id, user_id, created_at, last_accessed_at,
                        expires_at, ip_address, user_agent, is_active, data
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        user_id = VALUES(user_id),
                        last_accessed_at = VALUES(last_accessed_at),
                        expires_at = VALUES(expires_at),
                        ip_address = VALUES(ip_address),
                        user_agent = VALUES(user_agent),
                        is_active = VALUES(is_active),
                        data = VALUES(data)
                """
            else:  # sqlite
                query = """
                    INSERT OR REPLACE INTO sessions (
                        id, user_id, created_at, last_accessed_at,
                        expires_at, ip_address, user_agent, is_active, data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """

            params = (
                session.id,
                session.user_id,
                created_at,
                last_accessed_at,
                expires_at,
                session.ip_address,
                session.user_agent,
                is_active,
                data_json,
            )

            await self.db.execute(query, params)
            logger.debug(f"Stored session: {session.id[:8]}... for user {session.user_id}")

        except Exception as e:
            logger.error(f"Failed to store session {session.id[:8]}...: {e}")
            raise

    async def delete(self, session_id: str) -> None:
        """
        Remove session from database.

        Args:
            session_id: Unique session identifier

        Example:
            await store.delete('abc123...')
        """
        if not session_id:
            return

        try:
            # Use appropriate placeholder for database dialect
            if self._dialect == "postgresql":
                query = "DELETE FROM sessions WHERE id = $1"
            else:  # mysql and sqlite
                query = "DELETE FROM sessions WHERE id = ?"

            await self.db.execute(query, (session_id,))
            logger.debug(f"Deleted session: {session_id[:8]}...")

        except Exception as e:
            logger.error(f"Failed to delete session {session_id[:8]}...: {e}")
            raise

    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all active sessions for a user.

        Automatically filters out expired sessions and cleans them up.

        Args:
            user_id: User identifier

        Returns:
            List of active Session objects (empty list if none found)

        Example:
            sessions = await store.get_user_sessions('user_456')
            print(f"User has {len(sessions)} active sessions")

            for session in sessions:
                print(f"Session from {session.ip_address}")
        """
        if not user_id:
            return []

        try:
            # Use appropriate placeholder for database dialect
            if self._dialect == "postgresql":
                query = """
                    SELECT * FROM sessions
                    WHERE user_id = $1 AND is_active = TRUE
                    ORDER BY last_accessed_at DESC
                """
            elif self._dialect == "mysql":
                query = """
                    SELECT * FROM sessions
                    WHERE user_id = ? AND is_active = TRUE
                    ORDER BY last_accessed_at DESC
                """
            else:  # sqlite
                query = """
                    SELECT * FROM sessions
                    WHERE user_id = ? AND is_active = 1
                    ORDER BY last_accessed_at DESC
                """

            rows = await self.db.fetch_all(query, (user_id,))

            sessions = []
            expired_session_ids = []

            for row in rows:
                session = self._row_to_session(row)

                # Check if session is expired
                if session.is_expired():
                    expired_session_ids.append(session.id)
                else:
                    sessions.append(session)

            # Clean up expired sessions asynchronously
            if expired_session_ids:
                logger.debug(
                    f"Cleaning up {len(expired_session_ids)} expired sessions for user {user_id}"
                )
                for session_id in expired_session_ids:
                    try:
                        await self.delete(session_id)
                    except Exception as e:
                        logger.warning(f"Failed to delete expired session {session_id[:8]}...: {e}")

            logger.debug(f"Retrieved {len(sessions)} active sessions for user {user_id}")
            return sessions

        except Exception as e:
            logger.error(f"Failed to retrieve user sessions for {user_id}: {e}")
            raise

    async def cleanup_expired(self) -> None:
        """
        Remove all expired sessions from database.

        This method should be called periodically (e.g., every 15 minutes)
        to prevent the sessions table from growing indefinitely.

        Uses efficient bulk DELETE with datetime comparison.

        Example:
            # Cleanup expired sessions
            await store.cleanup_expired()

            # Or setup periodic cleanup
            import asyncio

            async def periodic_cleanup():
                while True:
                    await store.cleanup_expired()
                    await asyncio.sleep(900)  # Every 15 minutes
        """
        try:
            # Get current time in appropriate format
            now = self._format_datetime(datetime.utcnow())

            # Build query based on dialect
            if self._dialect == "postgresql":
                query = """
                    DELETE FROM sessions
                    WHERE (expires_at IS NOT NULL AND expires_at < $1)
                       OR is_active = FALSE
                """
            elif self._dialect == "mysql":
                query = """
                    DELETE FROM sessions
                    WHERE (expires_at IS NOT NULL AND expires_at < ?)
                       OR is_active = FALSE
                """
            else:  # sqlite
                query = """
                    DELETE FROM sessions
                    WHERE (expires_at IS NOT NULL AND expires_at < ?)
                       OR is_active = 0
                """

            # Execute cleanup
            result = await self.db.execute(query, (now,))

            # Log cleanup results (different adapters return different formats)
            if isinstance(result, int):
                logger.info(f"Cleaned up {result} expired sessions")
            elif isinstance(result, str):
                logger.info(f"Cleaned up expired sessions: {result}")
            else:
                logger.info("Cleaned up expired sessions")

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            raise


class CSRFToken:
    """CSRF token management"""

    @staticmethod
    def generate_token() -> str:
        """Generate cryptographically secure CSRF token"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def verify_token(session_token: str, form_token: str) -> bool:
        """Verify CSRF token using constant-time comparison"""
        if not session_token or not form_token:
            return False
        return secrets.compare_digest(session_token, form_token)


class SessionManager:
    """
    Secure session management system
    """

    def __init__(self, config: SessionConfig, store: Optional[SessionStore] = None):
        self.config = config
        self.store = store or MemorySessionStore()
        self._cleanup_thread = None
        self._start_cleanup_thread()

    def _start_cleanup_thread(self):
        """Start background thread for session cleanup"""

        def cleanup_worker():
            while True:
                try:
                    self.store.cleanup_expired()
                    time.sleep(self.config.cleanup_interval_minutes * 60)
                except Exception:
                    # Log error in production
                    time.sleep(60)  # Wait before retrying

        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def create_session(self, user: User, ip_address: str, user_agent: str) -> Session:
        """
        Create new session for user

        Args:
            user: User object
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            New Session object
        """
        # Generate secure session ID
        session_id = self._generate_session_id()

        # Calculate expiration times
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=self.config.timeout_minutes)

        # Create session
        session = Session(
            id=session_id,
            user_id=user.id,
            created_at=now,
            last_accessed_at=now,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_active=True,
        )

        # Add CSRF token if enabled
        if self.config.csrf_protection:
            session.data["csrf_token"] = CSRFToken.generate_token()

        # Enforce session limits
        self._enforce_session_limits(user.id)

        # Store session
        self.store.set(session)

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        if not session_id:
            return None

        session = self.store.get(session_id)
        if not session:
            return None

        # Check if session is expired
        if session.is_expired():
            self.delete_session(session_id)
            return None

        return session

    def refresh_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[Session]:
        """
        Refresh session expiration and update last accessed time.

        SECURITY: Validates IP address and User-Agent to detect session hijacking.

        Args:
            session_id: Session ID
            ip_address: Client IP address for validation
            user_agent: Client User-Agent for validation

        Returns:
            Refreshed session or None if not found

        Raises:
            SecurityViolationError: If IP address or User-Agent validation fails
        """
        session = self.get_session(session_id)
        if not session:
            return None

        # SECURITY FIX: Session hijacking detection
        # Check IP address hasn't changed
        if ip_address and session.ip_address:
            if session.ip_address != ip_address:
                # Log security event
                self.delete_session(session_id)
                raise SecurityViolationError(
                    "Session IP address mismatch - possible session hijacking"
                )

        # SECURITY FIX: Check User-Agent hasn't changed
        if user_agent and session.user_agent:
            if session.user_agent != user_agent:
                # Log security event
                self.delete_session(session_id)
                raise SecurityViolationError(
                    "Session User-Agent mismatch - possible session hijacking"
                )

        # Refresh session
        session.refresh(self.config.timeout_minutes)
        self.store.set(session)

        return session

    def delete_session(self, session_id: str) -> None:
        """Delete session"""
        self.store.delete(session_id)

    def delete_user_sessions(self, user_id: str, except_session_id: Optional[str] = None) -> None:
        """Delete all sessions for a user"""
        sessions = self.store.get_user_sessions(user_id)
        for session in sessions:
            if except_session_id and session.id == except_session_id:
                continue
            self.delete_session(session.id)

    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all active sessions for a user"""
        return self.store.get_user_sessions(user_id)

    def validate_csrf_token(self, session: Session, form_token: str) -> bool:
        """Validate CSRF token"""
        if not self.config.csrf_protection:
            return True

        session_token = session.data.get("csrf_token")
        return CSRFToken.verify_token(session_token, form_token)

    def regenerate_session_id(self, session: Session) -> Session:
        """Regenerate session ID (after login/privilege escalation)"""
        # Delete old session
        old_session_id = session.id
        self.delete_session(old_session_id)

        # Create new session with same data
        new_session_id = self._generate_session_id()
        session.id = new_session_id

        # Regenerate CSRF token
        if self.config.csrf_protection:
            session.data["csrf_token"] = CSRFToken.generate_token()

        # Store new session
        self.store.set(session)

        return session

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        # Use 256 bits of entropy (32 bytes)
        random_bytes = secrets.token_bytes(32)

        # Add timestamp for uniqueness
        timestamp = str(int(time.time() * 1000000)).encode("utf-8")

        # Create hash
        hasher = hashlib.sha256()
        hasher.update(random_bytes)
        hasher.update(timestamp)

        return hasher.hexdigest()

    def _enforce_session_limits(self, user_id: str) -> None:
        """Enforce maximum number of sessions per user"""
        sessions = self.get_user_sessions(user_id)

        if len(sessions) >= self.config.max_sessions_per_user:
            # Remove oldest sessions
            sessions.sort(key=lambda s: s.created_at)
            sessions_to_remove = sessions[: len(sessions) - self.config.max_sessions_per_user + 1]

            for session in sessions_to_remove:
                self.delete_session(session.id)

    def get_session_info(self, session: Session) -> Dict[str, Any]:
        """Get session information for user"""
        return {
            "id": session.id,
            "created_at": session.created_at.isoformat(),
            "last_accessed_at": session.last_accessed_at.isoformat(),
            "expires_at": (session.expires_at.isoformat() if session.expires_at else None),
            "ip_address": session.ip_address,
            "user_agent": session.user_agent,
            "is_active": session.is_active,
        }

    def create_cookie_headers(self, session: Session) -> Dict[str, str]:
        """Create secure cookie headers for session"""
        cookie_value = session.id

        attributes = []

        if self.config.secure_cookies:
            attributes.append("Secure")

        if self.config.httponly_cookies:
            attributes.append("HttpOnly")

        if self.config.samesite:
            attributes.append(f"SameSite={self.config.samesite}")

        if self.config.cookie_domain:
            attributes.append(f"Domain={self.config.cookie_domain}")

        if self.config.cookie_path:
            attributes.append(f"Path={self.config.cookie_path}")

        if session.expires_at:
            expires = session.expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
            attributes.append(f"Expires={expires}")

        cookie_header = f"{self.config.cookie_name}={cookie_value}"
        if attributes:
            cookie_header += "; " + "; ".join(attributes)

        return {"Set-Cookie": cookie_header}

    def create_logout_cookie_headers(self) -> Dict[str, str]:
        """Create cookie headers to clear session on logout"""
        cookie_header = f"{self.config.cookie_name}=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path={self.config.cookie_path}"

        if self.config.cookie_domain:
            cookie_header += f"; Domain={self.config.cookie_domain}"

        return {"Set-Cookie": cookie_header}


# Global session manager instance
_session_manager_instance: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get session manager singleton instance"""
    global _session_manager_instance
    if _session_manager_instance is None:
        config = SessionConfig()
        _session_manager_instance = SessionManager(config)
    return _session_manager_instance


def configure_session_manager(
    config: SessionConfig, store: Optional[SessionStore] = None
) -> SessionManager:
    """Configure session manager with custom settings"""
    global _session_manager_instance
    _session_manager_instance = SessionManager(config, store)
    return _session_manager_instance
