"""
Session Backends

Support for multiple session storage backends:
- Cookie: Client-side signed/encrypted cookies (no server storage)
- Database: Persistent SQL database storage
- Redis: Fast distributed session storage
- Memory: In-memory storage (development only)
"""

from .cookie import CookieSession, CookieSessionConfig, CookieSessionStore
from .database import DatabaseSessionConfig, DatabaseSessionStore
from .memory import MemorySessionConfig, MemorySessionStore, SessionData
from .redis import RedisSessionConfig, RedisSessionStore

__all__ = [
    # Cookie
    "CookieSession",
    "CookieSessionConfig",
    "CookieSessionStore",
    # Database
    "DatabaseSessionStore",
    "DatabaseSessionConfig",
    # Redis
    "RedisSessionStore",
    "RedisSessionConfig",
    # Memory
    "MemorySessionStore",
    "MemorySessionConfig",
    "SessionData",
]
