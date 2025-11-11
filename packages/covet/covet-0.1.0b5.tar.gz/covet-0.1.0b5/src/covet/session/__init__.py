"""
Distributed Session Management

Production-ready distributed session storage for horizontal scaling.
Supports Redis for distributed state and in-memory fallback.
"""

from .redis_session import (
    RedisSessionStore,
    SessionConfig,
    SessionEncryption,
    SessionManager,
)

__all__ = [
    "RedisSessionStore",
    "SessionConfig",
    "SessionEncryption",
    "SessionManager",
]
