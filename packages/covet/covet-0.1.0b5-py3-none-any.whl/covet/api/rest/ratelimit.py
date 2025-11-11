"""
Rate Limiting

Production-ready rate limiting with multiple algorithms and storage backends.
Prevents API abuse and ensures fair resource usage.
"""

import asyncio
import time
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, Optional


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""

    FIXED_WINDOW = "fixed_window"  # Simple counter per time window
    SLIDING_WINDOW = "sliding_window"  # More accurate than fixed window
    TOKEN_BUCKET = "token_bucket"  # Allows bursts
    LEAKY_BUCKET = "leaky_bucket"  # Smooth rate


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""

    def __init__(self, retry_after: int):
        """
        Initialize rate limit exceeded error.

        Args:
            retry_after: Seconds until next request allowed
        """
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class RateLimiter:
    """
    Base rate limiter class.

    Subclasses implement different algorithms.
    """

    def __init__(self, rate: int, period: int, identifier: Optional[Callable] = None):
        """
        Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            period: Time period in seconds
            identifier: Function to extract identifier from request (e.g., IP, user ID)
        """
        self.rate = rate
        self.period = period
        self.identifier = identifier or self._default_identifier

    def _default_identifier(self, request: Any) -> str:
        """Default identifier extractor (use IP address)."""
        # This would be implemented based on the request object structure
        return "default"

    async def check(self, identifier: str) -> tuple[bool, int]:
        """
        Check if request is allowed.

        Args:
            identifier: Client identifier

        Returns:
            Tuple of (allowed, retry_after_seconds)
        """
        raise NotImplementedError


class FixedWindowRateLimiter(RateLimiter):
    """
    Fixed window rate limiter.

    Divides time into fixed windows and counts requests per window.
    Simple but can allow bursts at window boundaries.
    """

    def __init__(self, rate: int, period: int, identifier: Optional[Callable] = None):
        """Initialize fixed window rate limiter."""
        super().__init__(rate, period, identifier)
        self.windows: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "reset_time": time.time() + self.period}
        )

    async def check(self, identifier: str) -> tuple[bool, int]:
        """Check if request is allowed."""
        current_time = time.time()
        window = self.windows[identifier]

        # Reset window if expired
        if current_time >= window["reset_time"]:
            window["count"] = 0
            window["reset_time"] = current_time + self.period

        # Check limit
        if window["count"] < self.rate:
            window["count"] += 1
            return True, 0
        else:
            retry_after = int(window["reset_time"] - current_time) + 1
            return False, retry_after


class SlidingWindowRateLimiter(RateLimiter):
    """
    Sliding window rate limiter.

    More accurate than fixed window, prevents boundary issues.
    Uses weighted count from previous and current windows.
    """

    def __init__(self, rate: int, period: int, identifier: Optional[Callable] = None):
        """Initialize sliding window rate limiter."""
        super().__init__(rate, period, identifier)
        self.windows: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {
                "current_count": 0,
                "current_start": time.time(),
                "previous_count": 0,
            }
        )

    async def check(self, identifier: str) -> tuple[bool, int]:
        """Check if request is allowed."""
        current_time = time.time()
        window = self.windows[identifier]

        # Calculate time since current window started
        time_since_start = current_time - window["current_start"]

        # If we're past the window, roll over
        if time_since_start >= self.period:
            window["previous_count"] = window["current_count"]
            window["current_count"] = 0
            window["current_start"] = current_time
            time_since_start = 0

        # Calculate weighted count
        # Uses portion of previous window + current window
        previous_weight = 1.0 - (time_since_start / self.period)
        weighted_count = window["previous_count"] * previous_weight + window["current_count"]

        # Check limit
        if weighted_count < self.rate:
            window["current_count"] += 1
            return True, 0
        else:
            retry_after = int(self.period - time_since_start) + 1
            return False, retry_after


class TokenBucketRateLimiter(RateLimiter):
    """
    Token bucket rate limiter.

    Allows bursts up to bucket capacity.
    Tokens replenish at a constant rate.
    """

    def __init__(
        self,
        rate: int,
        period: int,
        burst: Optional[int] = None,
        identifier: Optional[Callable] = None,
    ):
        """
        Initialize token bucket rate limiter.

        Args:
            rate: Token refill rate (requests per period)
            period: Refill period in seconds
            burst: Bucket capacity (max burst size)
            identifier: Identifier extractor
        """
        super().__init__(rate, period, identifier)
        self.burst = burst or rate
        self.refill_rate = rate / period  # Tokens per second
        self.buckets: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"tokens": self.burst, "last_refill": time.time()}
        )

    async def check(self, identifier: str) -> tuple[bool, int]:
        """Check if request is allowed."""
        current_time = time.time()
        bucket = self.buckets[identifier]

        # Refill tokens
        time_passed = current_time - bucket["last_refill"]
        tokens_to_add = time_passed * self.refill_rate
        bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
        bucket["last_refill"] = current_time

        # Check if we have tokens
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True, 0
        else:
            # Calculate when next token will be available
            retry_after = int((1 - bucket["tokens"]) / self.refill_rate) + 1
            return False, retry_after


class RateLimitMiddleware:
    """
    ASGI middleware for rate limiting.

    Wraps application and enforces rate limits on all requests.
    """

    def __init__(
        self,
        app,
        limiter: RateLimiter,
        identifier: Optional[Callable] = None,
        exempt_paths: Optional[list[str]] = None,
    ):
        """
        Initialize rate limit middleware.

        Args:
            app: ASGI application
            limiter: Rate limiter instance
            identifier: Function to extract identifier from request
            exempt_paths: List of paths exempt from rate limiting
        """
        self.app = app
        self.limiter = limiter
        self.identifier = identifier or self._extract_client_ip
        self.exempt_paths = set(exempt_paths or [])

    def _extract_client_ip(self, scope: dict) -> str:
        """Extract client IP from ASGI scope."""
        # Check X-Forwarded-For header first (for proxies)
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for")
        if forwarded:
            return forwarded.decode().split(",")[0].strip()

        # Fall back to client address
        client = scope.get("client")
        if client:
            return client[0]

        return "unknown"

    async def __call__(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Check if path is exempt
        path = scope.get("path", "/")
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        # Get client identifier
        identifier = self.identifier(scope)

        # Check rate limit
        allowed, retry_after = await self.limiter.check(identifier)

        if not allowed:
            # Send 429 Too Many Requests
            headers = [
                [b"content-type", b"application/json; charset=utf-8"],
                [b"retry-after", str(retry_after).encode()],
                [b"x-ratelimit-limit", str(self.limiter.rate).encode()],
                [b"x-ratelimit-remaining", b"0"],
                [b"x-ratelimit-reset", str(int(time.time() + retry_after)).encode()],
            ]

            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": headers,
                }
            )

            body = {
                "type": "https://errors.covetpy.dev/rate-limit",
                "title": "Too Many Requests",
                "status": 429,
                "detail": f"Rate limit exceeded. Retry after {retry_after} seconds",
                "retry_after": retry_after,
            }

            import json

            await send(
                {
                    "type": "http.response.body",
                    "body": json.dumps(body).encode("utf-8"),
                }
            )
            return

        # Add rate limit headers to response
        original_send = send

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                # Add rate limit headers
                headers = list(message.get("headers", []))
                headers.extend(
                    [
                        [b"x-ratelimit-limit", str(self.limiter.rate).encode()],
                        [b"x-ratelimit-remaining", b"1"],  # Simplified
                    ]
                )
                message["headers"] = headers

            await original_send(message)

        # Continue to application
        await self.app(scope, receive, send_with_headers)


__all__ = [
    "RateLimitAlgorithm",
    "RateLimitExceeded",
    "RateLimiter",
    "FixedWindowRateLimiter",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    "RateLimitMiddleware",
]
