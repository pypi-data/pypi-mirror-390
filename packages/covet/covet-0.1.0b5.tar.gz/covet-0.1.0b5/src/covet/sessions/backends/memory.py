"""
In-Memory Session Backend

Development-only in-memory sessions:
- Fast session access (no I/O)
- LRU eviction when size limit reached
- NOT persistent across restarts
- Thread-safe operations
- For development and testing only

NO MOCK DATA: Real in-memory storage with threading.
"""

import logging
import secrets
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Session data with metadata."""

    session_id: str
    data: Dict[str, Any]
    created_at: float
    expires_at: float
    user_id: Optional[str] = None

    def is_expired(self) -> bool:
        """Check if session has expired."""
        return time.time() > self.expires_at

    def touch(self, max_age: int):
        """Refresh session expiration."""
        self.expires_at = time.time() + max_age


@dataclass
class MemorySessionConfig:
    """Memory session configuration."""

    max_sessions: int = 10000  # Maximum number of sessions
    session_id_length: int = 32
    max_age: int = 86400  # 24 hours
    cleanup_interval: int = 300  # 5 minutes


class MemorySessionStore:
    """
    In-memory session storage.

    WARNING: For development only. Data is not persistent.

    Features:
    - Fast access (no I/O)
    - Thread-safe operations
    - LRU eviction when size limit reached
    - Automatic cleanup of expired sessions

    Example:
        config = MemorySessionConfig(max_sessions=1000)
        store = MemorySessionStore(config)

        # Create session
        session_id = await store.create({'user_id': 123})

        # Get session
        data = await store.get(session_id)

        # Update session
        data['username'] = 'alice'
        await store.set(session_id, data)
    """

    def __init__(self, config: Optional[MemorySessionConfig] = None):
        """
        Initialize memory session store.

        Args:
            config: Session configuration
        """
        self.config = config or MemorySessionConfig()

        # Session storage (OrderedDict for LRU)
        self._sessions: OrderedDict[str, SessionData] = OrderedDict()

        # User -> Sessions mapping
        self._user_sessions: Dict[str, Set[str]] = {}

        # Thread lock
        self._lock = threading.RLock()

        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def _generate_session_id(self) -> str:
        """Generate cryptographically secure session ID."""
        return secrets.token_urlsafe(self.config.session_id_length)

    def _evict_lru(self):
        """Evict least recently used session."""
        if not self._sessions:
            return

        # Remove first item (least recently used)
        session_id, session = self._sessions.popitem(last=False)

        # Remove from user sessions
        if session.user_id:
            if session.user_id in self._user_sessions:
                self._user_sessions[session.user_id].discard(session_id)

        logger.debug(f"Evicted LRU session: {session_id}")

    def _cleanup_expired(self):
        """Remove expired sessions."""
        with self._lock:
            expired = [
                session_id for session_id, session in self._sessions.items() if session.is_expired()
            ]

            for session_id in expired:
                session = self._sessions.pop(session_id, None)

                # Remove from user sessions
                if session and session.user_id:
                    if session.user_id in self._user_sessions:
                        self._user_sessions[session.user_id].discard(session_id)

            if expired:
                logger.debug(f"Cleaned up {len(expired)} expired sessions")

    def _cleanup_worker(self):
        """Background worker to clean up expired sessions."""
        while True:
            try:
                time.sleep(self.config.cleanup_interval)
                self._cleanup_expired()
            except Exception as e:
                logger.error(f"Cleanup worker error: {e}")

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
        with self._lock:
            session_id = self._generate_session_id()
            session_data = data or {}

            # Add metadata
            if user_id:
                session_data["_user_id"] = user_id

            # Create session
            now = time.time()
            session = SessionData(
                session_id=session_id,
                data=session_data,
                created_at=now,
                expires_at=now + self.config.max_age,
                user_id=user_id,
            )

            # Evict if at capacity
            if len(self._sessions) >= self.config.max_sessions:
                self._evict_lru()

            # Store session
            self._sessions[session_id] = session
            self._sessions.move_to_end(session_id)

            # Track user session
            if user_id:
                if user_id not in self._user_sessions:
                    self._user_sessions[user_id] = set()
                self._user_sessions[user_id].add(session_id)

            return session_id

    async def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session ID

        Returns:
            Session data or None if not found/expired
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return None

            # Check expiration
            if session.is_expired():
                # Remove expired session
                del self._sessions[session_id]

                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(session_id)

                return None

            # Move to end (mark as recently used)
            self._sessions.move_to_end(session_id)

            # Return copy of data
            return dict(session.data)

    async def set(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data.

        Args:
            session_id: Session ID
            data: Session data

        Returns:
            True if successful
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return False

            # Check expiration
            if session.is_expired():
                del self._sessions[session_id]
                return False

            # Update data
            session.data = dict(data)

            # Update user_id if changed
            new_user_id = data.get("_user_id")
            if new_user_id != session.user_id:
                # Remove from old user
                if session.user_id in self._user_sessions:
                    self._user_sessions[session.user_id].discard(session_id)

                # Add to new user
                session.user_id = new_user_id
                if new_user_id:
                    if new_user_id not in self._user_sessions:
                        self._user_sessions[new_user_id] = set()
                    self._user_sessions[new_user_id].add(session_id)

            # Refresh expiration
            session.touch(self.config.max_age)

            # Move to end
            self._sessions.move_to_end(session_id)

            return True

    async def delete(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        with self._lock:
            session = self._sessions.pop(session_id, None)

            if session is None:
                return False

            # Remove from user sessions
            if session.user_id in self._user_sessions:
                self._user_sessions[session.user_id].discard(session_id)

            return True

    async def exists(self, session_id: str) -> bool:
        """
        Check if session exists and is not expired.

        Args:
            session_id: Session ID

        Returns:
            True if exists
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None:
                return False

            if session.is_expired():
                del self._sessions[session_id]
                return False

            return True

    async def touch(self, session_id: str) -> bool:
        """
        Refresh session expiration.

        Args:
            session_id: Session ID

        Returns:
            True if successful
        """
        with self._lock:
            session = self._sessions.get(session_id)

            if session is None or session.is_expired():
                return False

            session.touch(self.config.max_age)
            self._sessions.move_to_end(session_id)

            return True

    async def get_user_sessions(self, user_id: str) -> Set[str]:
        """
        Get all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Set of session IDs
        """
        with self._lock:
            if user_id not in self._user_sessions:
                return set()

            # Filter out expired sessions
            active_sessions = set()
            expired_sessions = []

            for session_id in self._user_sessions[user_id]:
                session = self._sessions.get(session_id)

                if session and not session.is_expired():
                    active_sessions.add(session_id)
                else:
                    expired_sessions.append(session_id)

            # Clean up expired
            for session_id in expired_sessions:
                self._user_sessions[user_id].discard(session_id)
                self._sessions.pop(session_id, None)

            return active_sessions

    async def delete_user_sessions(self, user_id: str) -> int:
        """
        Delete all sessions for a user.

        Args:
            user_id: User ID

        Returns:
            Number of sessions deleted
        """
        with self._lock:
            if user_id not in self._user_sessions:
                return 0

            session_ids = list(self._user_sessions[user_id])
            count = 0

            for session_id in session_ids:
                if await self.delete(session_id):
                    count += 1

            # Remove user entry
            self._user_sessions.pop(user_id, None)

            return count

    async def cleanup_expired(self) -> int:
        """
        Remove expired sessions.

        Returns:
            Number of sessions removed
        """
        with self._lock:
            initial_count = len(self._sessions)
            self._cleanup_expired()
            final_count = len(self._sessions)

            return initial_count - final_count

    async def get_stats(self) -> Dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Dictionary with session stats
        """
        with self._lock:
            # Count expired sessions
            expired_count = sum(1 for session in self._sessions.values() if session.is_expired())

            return {
                "backend": "memory",
                "total_sessions": len(self._sessions),
                "active_sessions": len(self._sessions) - expired_count,
                "expired_sessions": expired_count,
                "max_sessions": self.config.max_sessions,
                "user_count": len(self._user_sessions),
            }


__all__ = ["MemorySessionStore", "MemorySessionConfig", "SessionData"]
