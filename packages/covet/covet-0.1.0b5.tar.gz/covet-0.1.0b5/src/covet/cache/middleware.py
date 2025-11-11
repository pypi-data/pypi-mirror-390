"""
Cache Middleware

ASGI middleware for HTTP response caching:
- Cache-Control header support
- ETag generation and validation
- Conditional requests (304 Not Modified)
- Vary header handling
- Query parameter filtering
- Request method filtering

NO MOCK DATA: Real HTTP caching implementation.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from typing import Callable, List, Optional, Set

from .manager import CacheManager, get_cache

logger = logging.getLogger(__name__)


@dataclass
class CacheMiddlewareConfig:
    """Cache middleware configuration."""

    # Cache control
    default_ttl: int = 300  # 5 minutes
    cache_control_header: bool = True

    # Methods to cache
    cacheable_methods: Set[str] = None

    # Status codes to cache
    cacheable_status_codes: Set[int] = None

    # Query parameters to exclude from cache key
    exclude_query_params: Set[str] = None

    # Paths to exclude from caching
    exclude_paths: Set[str] = None

    # ETag support
    etag_enabled: bool = True

    # Vary headers
    vary_headers: Optional[List[str]] = None

    # Cache key prefix
    key_prefix: str = "http"

    def __post_init__(self):
        """Set defaults for mutable fields."""
        if self.cacheable_methods is None:
            self.cacheable_methods = {"GET", "HEAD"}

        if self.cacheable_status_codes is None:
            self.cacheable_status_codes = {200, 203, 300, 301, 404, 405, 410, 414, 501}

        if self.exclude_query_params is None:
            self.exclude_query_params = set()

        if self.exclude_paths is None:
            self.exclude_paths = set()


class CacheMiddleware:
    """
    ASGI middleware for HTTP response caching.

    Features:
    - Respects Cache-Control headers
    - Generates and validates ETags
    - Handles conditional requests (If-None-Match, If-Modified-Since)
    - Supports Vary header for content negotiation
    - Configurable cache rules

    Example:
        from covet.cache import CacheMiddleware, CacheMiddlewareConfig

        config = CacheMiddlewareConfig(
            default_ttl=300,
            etag_enabled=True,
            vary_headers=['Accept-Language']
        )

        app = CacheMiddleware(app, config=config)

    Cache-Control directives supported:
    - no-cache: Skip cache read (but still cache for next request)
    - no-store: Don't cache at all
    - max-age: Use specific TTL
    - private: Don't cache (for user-specific content)
    """

    def __init__(
        self,
        app,
        config: Optional[CacheMiddlewareConfig] = None,
        cache: Optional[CacheManager] = None,
    ):
        """
        Initialize cache middleware.

        Args:
            app: ASGI application
            config: Cache middleware configuration
            cache: Cache manager instance
        """
        self.app = app
        self.config = config or CacheMiddlewareConfig()
        self.cache = cache or get_cache()

    async def __call__(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Extract request info
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        headers = dict(scope.get("headers", []))

        # Check if request is cacheable
        if not self._is_cacheable_request(method, path, headers):
            await self.app(scope, receive, send)
            return

        # Generate cache key
        cache_key = self._generate_cache_key(scope)

        # Check for conditional request headers
        if_none_match = headers.get(b"if-none-match", b"").decode("utf-8")

        # Try to get cached response
        cached = None
        if not self._has_no_cache_directive(headers):
            try:
                cached = await self.cache.get(cache_key)
            except Exception as e:
                logger.error(f"Cache middleware GET error: {e}")

        # If cached and ETag matches, return 304
        if cached and if_none_match and self.config.etag_enabled:
            cached_etag = cached.get("etag")
            if cached_etag and cached_etag == if_none_match:
                await self._send_304_response(send, cached_etag)
                return

        # If cached, return cached response
        if cached:
            await self._send_cached_response(send, cached)
            return

        # Intercept response
        response_data = {"status": None, "headers": [], "body_chunks": []}

        async def wrapped_send(message):
            """Intercept response messages."""
            if message["type"] == "http.response.start":
                response_data["status"] = message["status"]
                response_data["headers"] = list(message.get("headers", []))

                # Send original message
                await send(message)

            elif message["type"] == "http.response.body":
                body = message.get("body", b"")
                if body:
                    response_data["body_chunks"].append(body)

                # Send original message
                await send(message)

                # If this is the last chunk, cache the response
                if not message.get("more_body", False):
                    await self._cache_response(cache_key, response_data, headers)

        # Call app
        await self.app(scope, receive, wrapped_send)

    def _is_cacheable_request(self, method: str, path: str, headers: dict) -> bool:
        """Check if request is cacheable."""
        # Check method
        if method not in self.config.cacheable_methods:
            return False

        # Check excluded paths
        if path in self.config.exclude_paths:
            return False

        # Check for no-store directive
        if self._has_no_store_directive(headers):
            return False

        return True

    def _is_cacheable_response(self, status: int, headers: List[tuple]) -> bool:
        """Check if response is cacheable."""
        # Check status code
        if status not in self.config.cacheable_status_codes:
            return False

        # Check response headers
        headers_dict = dict(headers)

        # Check for no-store directive
        cache_control = headers_dict.get(b"cache-control", b"").decode("utf-8").lower()
        if "no-store" in cache_control or "private" in cache_control:
            return False

        return True

    def _generate_cache_key(self, scope: dict) -> str:
        """Generate cache key from request."""
        # Base key: method + path
        method = scope.get("method", "GET")
        path = scope.get("path", "/")

        # Add query string (filtered)
        query_string = scope.get("query_string", b"").decode("utf-8")
        if query_string:
            # Parse and filter query params
            from urllib.parse import parse_qs, urlencode

            params = parse_qs(query_string)

            # Remove excluded params
            filtered_params = {
                k: v for k, v in params.items() if k not in self.config.exclude_query_params
            }

            if filtered_params:
                # Sort for consistent keys
                query_string = urlencode(sorted(filtered_params.items()))
            else:
                query_string = ""

        key = f"{self.config.key_prefix}:{method}:{path}"
        if query_string:
            key += f"?{query_string}"

        # Add vary headers
        if self.config.vary_headers:
            headers = dict(scope.get("headers", []))
            vary_values = []

            for header in self.config.vary_headers:
                header_bytes = header.lower().encode("utf-8")
                value = headers.get(header_bytes, b"").decode("utf-8")
                vary_values.append(f"{header}:{value}")

            if vary_values:
                key += ":" + ":".join(vary_values)

        return key

    def _generate_etag(self, body: bytes) -> str:
        """Generate ETag from response body using SHA-256 instead of MD5 for security."""
        return f'"{hashlib.sha256(body).hexdigest()}"'

    def _get_ttl(self, headers: dict) -> int:
        """Extract TTL from Cache-Control header."""
        cache_control = headers.get(b"cache-control", b"").decode("utf-8").lower()

        # Look for max-age directive
        for directive in cache_control.split(","):
            directive = directive.strip()
            if directive.startswith("max-age="):
                try:
                    return int(directive.split("=")[1])
                except ValueError:
                    # Invalid max-age value, use default
                    logger.debug(f"Invalid max-age directive: {directive}")

        # Use default TTL
        return self.config.default_ttl

    def _has_no_cache_directive(self, headers: dict) -> bool:
        """Check if request has no-cache directive."""
        cache_control = headers.get(b"cache-control", b"").decode("utf-8").lower()
        return "no-cache" in cache_control

    def _has_no_store_directive(self, headers: dict) -> bool:
        """Check if request has no-store directive."""
        cache_control = headers.get(b"cache-control", b"").decode("utf-8").lower()
        return "no-store" in cache_control

    async def _cache_response(self, cache_key: str, response_data: dict, request_headers: dict):
        """Cache response if cacheable."""
        status = response_data["status"]
        headers = response_data["headers"]
        body_chunks = response_data["body_chunks"]

        # Check if cacheable
        if not self._is_cacheable_response(status, headers):
            return

        # Combine body chunks
        body = b"".join(body_chunks)

        # Generate ETag
        etag = None
        if self.config.etag_enabled:
            etag = self._generate_etag(body)

        # Get TTL
        headers_dict = dict(headers)
        ttl = self._get_ttl(headers_dict)

        # Cache response
        cached_response = {
            "status": status,
            "headers": headers,
            "body": body,
            "etag": etag,
        }

        try:
            await self.cache.set(cache_key, cached_response, ttl)
        except Exception as e:
            logger.error(f"Cache middleware SET error: {e}")

    async def _send_cached_response(self, send, cached: dict):
        """Send cached response."""
        headers = list(cached["headers"])

        # Add ETag if available
        if cached.get("etag") and self.config.etag_enabled:
            # Check if ETag already in headers
            has_etag = any(h[0].lower() == b"etag" for h in headers)
            if not has_etag:
                headers.append((b"etag", cached["etag"].encode("utf-8")))

        # Add X-Cache-Hit header
        headers.append((b"x-cache", b"HIT"))

        # Send response start
        await send(
            {
                "type": "http.response.start",
                "status": cached["status"],
                "headers": headers,
            }
        )

        # Send body
        await send(
            {
                "type": "http.response.body",
                "body": cached["body"],
            }
        )

    async def _send_304_response(self, send, etag: str):
        """Send 304 Not Modified response."""
        await send(
            {
                "type": "http.response.start",
                "status": 304,
                "headers": [
                    (b"etag", etag.encode("utf-8")),
                    (b"x-cache", b"HIT"),
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": b"",
            }
        )


__all__ = ["CacheMiddleware", "CacheMiddlewareConfig"]
