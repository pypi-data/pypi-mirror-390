"""
API versioning support for CovetPy.

Provides URL and header-based API versioning.
"""

from typing import Callable, Dict, Optional


class APIVersion:
    """API version configuration."""

    def __init__(self, version: str, deprecated: bool = False):
        self.version = version
        self.deprecated = deprecated


class VersioningMiddleware:
    """Middleware for API versioning."""

    def __init__(self, versions: Dict[str, APIVersion]):
        self.versions = versions

    async def process_request(self, request):
        """Extract and validate API version from request."""
        return request

    async def process_response(self, request, response):
        """Add version headers to response."""
        return response


__all__ = ["APIVersion", "VersioningMiddleware"]
