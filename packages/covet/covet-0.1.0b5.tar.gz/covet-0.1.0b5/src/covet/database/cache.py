"""
Database query caching for CovetPy.

Provides caching layer for database queries.
"""

from typing import Any, Optional


class QueryCache:
    """Database query cache."""

    def __init__(self, ttl: int = 300):
        self.ttl = ttl
        self._cache: dict = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get cached query result."""
        return self._cache.get(key)

    async def set(self, key: str, value: Any):
        """Cache query result."""
        self._cache[key] = value

    async def clear(self):
        """Clear cache."""
        self._cache.clear()


__all__ = ["QueryCache"]
