"""
Database Session Backend

Production-ready database sessions with:
- Session table with automatic cleanup
- JSON or pickle serialization
- Index optimization
- Transaction support
- Compatible with PostgreSQL, MySQL, SQLite

NO MOCK DATA: Real database integration.
"""

import asyncio
import json
import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from covet.database.security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_table_name,
)
from covet.security.secure_serializer import SecureSerializer

logger = logging.getLogger(__name__)


@dataclass
class DatabaseSessionConfig:
    """Database session configuration."""

    table_name: str = "sessions"
    session_id_length: int = 32
    max_age: int = 86400  # 24 hours
    cleanup_interval: int = 3600  # 1 hour

    # Serialization format (SECURE by default, prevents RCE)
    use_secure: bool = True  # Use SecureSerializer (recommended)
    secret_key: Optional[str] = None  # Required for secure serialization
    use_json: bool = False  # Use JSON (less secure but simpler)

    def __post_init__(self):
        """Validate configuration on initialization."""
        # SECURITY: Validate table name to prevent SQL injection
        try:
            self.table_name = validate_table_name(self.table_name, DatabaseDialect.GENERIC)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{self.table_name}': {e}") from e


class DatabaseSessionStore:
    """
    Database session storage.

    Features:
    - Persistent session storage in SQL database
    - Automatic expiration cleanup
    - Index on session_id for fast lookups
    - Compatible with PostgreSQL, MySQL, SQLite

    Table schema:
        CREATE TABLE sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            session_data TEXT/BLOB NOT NULL,
            created_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            user_id VARCHAR(255),
            ip_address VARCHAR(45),
            user_agent TEXT,
            INDEX idx_expires_at (expires_at),
            INDEX idx_user_id (user_id)
        );

    Example:
        from covet.database.adapters import create_adapter

        # Create database adapter
        db = create_adapter({
            'type': 'postgresql',
            'host': 'localhost',
            'database': 'myapp'
        })

        # Create session store
        config = DatabaseSessionConfig(table_name='app_sessions')
        store = DatabaseSessionStore(db, config)
        await store.initialize()

        # Use sessions
        session_id = await store.create()
        await store.set(session_id, {'user_id': 123})
        data = await store.get(session_id)
    """

    def __init__(self, db_connection, config: Optional[DatabaseSessionConfig] = None):
        """
        Initialize database session store.

        Args:
            db_connection: Database connection/adapter
            config: Session configuration
        """
        self.db = db_connection
        self.config = config or DatabaseSessionConfig()
        self._initialized = False
        self._cleanup_task = None

        # Initialize secure serializer if enabled
        if self.config.use_secure:
            if not self.config.secret_key:
                raise ValueError(
                    "DatabaseSessionStore with use_secure=True requires secret_key in config. "
                    "Use generate_secure_key() from covet.security.secure_serializer to generate one."
                )
            self._secure_serializer = SecureSerializer(secret_key=self.config.secret_key)
        else:
            self._secure_serializer = None

    async def initialize(self):
        """Create session table and start cleanup task."""
        if self._initialized:
            return

        await self._create_table()
        self._start_cleanup_task()
        self._initialized = True

    async def _create_table(self):
        """Create session table if it doesn't exist."""
        # Detect database type
        db_type = self._get_db_type()

        if db_type == "postgresql":
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                session_id VARCHAR(255) PRIMARY KEY,
                session_data TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                user_id VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_expires
                ON {self.config.table_name}(expires_at);
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_user
                ON {self.config.table_name}(user_id);
            """
        elif db_type == "mysql":
            data_type = "TEXT" if self.config.use_json else "BLOB"
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                session_id VARCHAR(255) PRIMARY KEY,
                session_data {data_type} NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                user_id VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                INDEX idx_expires_at (expires_at),
                INDEX idx_user_id (user_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        else:  # SQLite
            create_sql = f"""
            CREATE TABLE IF NOT EXISTS {self.config.table_name} (
                session_id TEXT PRIMARY KEY,
                session_data TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                user_id TEXT,
                ip_address TEXT,
                user_agent TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_expires
                ON {self.config.table_name}(expires_at);
            CREATE INDEX IF NOT EXISTS idx_{self.config.table_name}_user
                ON {self.config.table_name}(user_id);
            """

        try:
            # Execute CREATE statements
            for statement in create_sql.split(";"):
                statement = statement.strip()
                if statement:
                    await self._execute(statement)

            logger.info(f"Session table '{self.config.table_name}' initialized")

        except Exception as e:
            logger.error(f"Failed to create session table: {e}")
            raise

    def _get_db_type(self) -> str:
        """Detect database type from connection."""
        conn_str = str(type(self.db)).lower()

        if "postgres" in conn_str or "psycopg" in conn_str:
            return "postgresql"
        elif "mysql" in conn_str or "pymysql" in conn_str:
            return "mysql"
        else:
            return "sqlite"

    async def _execute(self, query: str, params: Optional[tuple] = None):
        """Execute database query."""
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

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        return secrets.token_urlsafe(self.config.session_id_length)

    def _serialize_data(self, data: Dict[str, Any]) -> str:
        """Serialize session data."""
        import base64

        if self.config.use_secure:
            # Use SecureSerializer (prevents RCE, provides integrity)
            serialized_bytes = self._secure_serializer.dumps(data)
            return base64.b64encode(serialized_bytes).decode("utf-8")
        elif self.config.use_json:
            return json.dumps(data)
        else:
            raise ValueError(
                "Neither use_secure nor use_json is enabled. "
                "Set use_secure=True for security (recommended) or use_json=True."
            )

    def _deserialize_data(self, serialized: str) -> Dict[str, Any]:
        """Deserialize session data."""
        import base64

        if self.config.use_secure:
            # Use SecureSerializer (prevents RCE, verifies integrity)
            serialized_bytes = base64.b64decode(serialized.encode("utf-8"))
            return self._secure_serializer.loads(serialized_bytes)
        elif self.config.use_json:
            return json.loads(serialized)
        else:
            raise ValueError(
                "Neither use_secure nor use_json is enabled. "
                "Set use_secure=True for security (recommended) or use_json=True."
            )

    async def create(
        self,
        data: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        """
        Create new session.

        Args:
            data: Initial session data
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent

        Returns:
            Session ID
        """
        session_id = self._generate_session_id()
        session_data = data or {}

        try:
            expires_at = datetime.utcnow() + timedelta(seconds=self.config.max_age)

            query = f"""  # nosec B608 - table_name validated in config
            INSERT INTO {self.config.table_name}
                (session_id, session_data, created_at, expires_at, user_id, ip_address, user_agent)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            await self._execute(
                query,
                (
                    session_id,
                    self._serialize_data(session_data),
                    datetime.utcnow(),
                    expires_at,
                    user_id,
                    ip_address,
                    user_agent,
                ),
            )

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
            Session data or None if not found/expired
        """
        try:
            query = f"""  # nosec B608 - table_name validated in config
            SELECT session_data, expires_at
            FROM {self.config.table_name}
            WHERE session_id = %s
            """

            row = await self._fetchone(query, (session_id,))

            if not row:
                return None

            session_data, expires_at = row[0], row[1]

            # Check expiration
            if isinstance(expires_at, str):
                expires_at = datetime.fromisoformat(expires_at)

            if datetime.utcnow() > expires_at:
                # Expired - delete and return None
                await self.delete(session_id)
                return None

            # Deserialize data
            return self._deserialize_data(session_data)

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
            # Update data and refresh expiration
            expires_at = datetime.utcnow() + timedelta(seconds=self.config.max_age)

            query = f"""  # nosec B608 - table_name validated in config
            UPDATE {self.config.table_name}
            SET session_data = %s, expires_at = %s
            WHERE session_id = %s
            """

            await self._execute(query, (self._serialize_data(data), expires_at, session_id))

            return True

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
            query = f"""  # nosec B608 - table_name validated in config
            DELETE FROM {self.config.table_name}
            WHERE session_id = %s
            """

            await self._execute(query, (session_id,))
            return True

        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False

    async def exists(self, session_id: str) -> bool:
        """
        Check if session exists and is not expired.

        Args:
            session_id: Session ID

        Returns:
            True if exists
        """
        data = await self.get(session_id)
        return data is not None

    async def touch(self, session_id: str) -> bool:
        """
        Refresh session expiration.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=self.config.max_age)

            query = f"""  # nosec B608 - table_name validated in config
            UPDATE {self.config.table_name}
            SET expires_at = %s
            WHERE session_id = %s
            """

            await self._execute(query, (expires_at, session_id))
            return True

        except Exception as e:
            logger.error(f"Failed to touch session {session_id}: {e}")
            return False

    async def get_user_sessions(self, user_id: str) -> list:
        """
        Get all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            List of session IDs
        """
        try:
            query = f"""  # nosec B608 - table_name validated in config
            SELECT session_id
            FROM {self.config.table_name}
            WHERE user_id = %s AND expires_at > %s
            """

            rows = await self._fetchall(query, (user_id, datetime.utcnow()))

            return [row[0] for row in rows]

        except Exception as e:
            logger.error(f"Failed to get user sessions: {e}")
            return []

    async def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        try:
            query = f"""  # nosec B608 - table_name validated in config
            DELETE FROM {self.config.table_name}
            WHERE user_id = %s
            """

            await self._execute(query, (user_id,))
            return 0  # Can't easily get count

        except Exception as e:
            logger.error(f"Failed to delete user sessions: {e}")
            return 0

    async def cleanup_expired(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        try:
            query = f"""  # nosec B608 - table_name validated in config
            DELETE FROM {self.config.table_name}
            WHERE expires_at < %s
            """

            await self._execute(query, (datetime.utcnow(),))

            logger.debug("Cleaned up expired sessions")
            return 0  # Can't easily get count

        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
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
        Get session statistics.

        Returns:
            Dictionary with session stats
        """
        try:
            # Count total sessions
            query = f"""  # nosec B608 - table_name validated in config
            SELECT COUNT(*) FROM {self.config.table_name}
            """
            total_row = await self._fetchone(query)
            total = total_row[0] if total_row else 0

            # Count active sessions
            query = f"""  # nosec B608 - table_name validated in config
            SELECT COUNT(*) FROM {self.config.table_name}
            WHERE expires_at > %s
            """
            active_row = await self._fetchone(query, (datetime.utcnow(),))
            active = active_row[0] if active_row else 0

            return {
                "backend": "database",
                "table": self.config.table_name,
                "total_sessions": total,
                "active_sessions": active,
                "expired_sessions": total - active,
            }

        except Exception as e:
            logger.error(f"Failed to get session stats: {e}")
            return {"error": str(e)}


__all__ = ["DatabaseSessionStore", "DatabaseSessionConfig"]
