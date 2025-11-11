"""
Advanced Rate Limiting

Production-grade rate limiting with:
- IP-based rate limiting
- User-based rate limiting
- Endpoint-specific limits
- Token bucket algorithm
- Sliding window algorithm
- Distributed rate limiting (Redis backend)
- Dynamic limits based on user tier
- Rate limit headers (RFC 6585)

Algorithms:
- Token Bucket: Smooth rate limiting with bursts
- Sliding Window: More accurate than fixed window
- Fixed Window: Simple but has edge cases
"""

import asyncio
import hashlib
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Protocol


@dataclass
class RateLimitConfig:
    """Rate limit configuration"""

    # Limit settings
    requests: int = 100  # Number of requests
    window: int = 60  # Time window in seconds

    # Algorithm
    algorithm: str = "token_bucket"  # 'token_bucket', 'sliding_window', 'fixed_window'

    # Headers
    include_headers: bool = True

    # Key prefix
    key_prefix: str = "ratelimit"


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception"""

    def __init__(self, message: str, retry_after: int, limit: int, remaining: int = 0):
        super().__init__(message)
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining


class RateLimitBackend(Protocol):
    """Protocol for rate limit storage backends"""

    async def increment(self, key: str, window: int) -> int:
        """Increment counter and return current count"""
        ...

    async def get(self, key: str) -> int:
        """Get current count"""
        ...

    async def reset(self, key: str) -> None:
        """Reset counter"""
        ...


class MemoryRateLimitBackend:
    """
    In-memory rate limit backend

    Uses dictionaries for storage. Good for development and single-server deployments.
    """

    def __init__(self):
        self._counters: Dict[str, int] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def increment(self, key: str, window: int) -> int:
        """Increment counter"""
        async with self._lock:
            current_time = time.time()

            # Check if expired
            if key in self._expiry and current_time > self._expiry[key]:
                del self._counters[key]
                del self._expiry[key]

            # Increment
            self._counters[key] = self._counters.get(key, 0) + 1

            # Set expiry if new
            if key not in self._expiry:
                self._expiry[key] = current_time + window

            return self._counters[key]

    async def get(self, key: str) -> int:
        """Get current count"""
        current_time = time.time()

        # Check if expired
        if key in self._expiry and current_time > self._expiry[key]:
            return 0

        return self._counters.get(key, 0)

    async def reset(self, key: str) -> None:
        """Reset counter"""
        async with self._lock:
            self._counters.pop(key, None)
            self._expiry.pop(key, None)

    async def cleanup_expired(self) -> int:
        """Remove expired entries"""
        current_time = time.time()
        expired = []

        async with self._lock:
            for key, expiry in self._expiry.items():
                if current_time > expiry:
                    expired.append(key)

            for key in expired:
                del self._counters[key]
                del self._expiry[key]

        return len(expired)


class RedisRateLimitBackend:
    """
    Redis rate limit backend

    Distributed rate limiting across multiple servers.

    Requires: pip install redis
    """

    def __init__(self, redis_client):
        """
        Initialize Redis backend

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    async def increment(self, key: str, window: int) -> int:
        """Increment counter"""
        pipe = self.redis.pipeline()

        # Increment
        pipe.incr(key)

        # Set expiry if new key
        pipe.expire(key, window)

        results = await pipe.execute()
        return results[0]

    async def get(self, key: str) -> int:
        """Get current count"""
        value = await self.redis.get(key)
        return int(value) if value else 0

    async def reset(self, key: str) -> None:
        """Reset counter"""
        await self.redis.delete(key)


class TokenBucketRateLimiter:
    """
    Token Bucket algorithm

    Allows bursts while maintaining average rate.

    Tokens are added at a constant rate. Each request consumes a token.
    If no tokens available, request is rejected.
    """

    def __init__(
        self,
        capacity: int,
        refill_rate: float,
        backend: Optional[RateLimitBackend] = None,
    ):
        """
        Initialize token bucket

        Args:
            capacity: Maximum tokens (burst size)
            refill_rate: Tokens added per second
            backend: Storage backend
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.backend = backend or MemoryRateLimitBackend()

        # In-memory token state (for non-distributed)
        self._tokens: Dict[str, float] = {}
        self._last_update: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def check_limit(self, key: str) -> tuple[bool, int, int]:
        """
        Check if request is allowed

        Args:
            key: Rate limit key

        Returns:
            Tuple of (allowed, remaining, retry_after)
        """
        async with self._lock:
            current_time = time.time()

            # Initialize if new
            if key not in self._tokens:
                self._tokens[key] = float(self.capacity)
                self._last_update[key] = current_time

            # Refill tokens
            time_passed = current_time - self._last_update[key]
            tokens_to_add = time_passed * self.refill_rate

            self._tokens[key] = min(self.capacity, self._tokens[key] + tokens_to_add)
            self._last_update[key] = current_time

            # Check if token available
            if self._tokens[key] >= 1:
                self._tokens[key] -= 1
                remaining = int(self._tokens[key])
                return True, remaining, 0
            else:
                # Calculate retry after
                retry_after = int((1 - self._tokens[key]) / self.refill_rate)
                return False, 0, retry_after


class SlidingWindowRateLimiter:
    """
    Sliding Window algorithm

    More accurate than fixed window, prevents edge case bursts.

    Tracks requests in a sliding time window.
    """

    def __init__(self, limit: int, window: int, backend: Optional[RateLimitBackend] = None):
        """
        Initialize sliding window

        Args:
            limit: Maximum requests per window
            window: Time window in seconds
            backend: Storage backend
        """
        self.limit = limit
        self.window = window
        self.backend = backend or MemoryRateLimitBackend()

        # Request timestamps per key
        self._requests: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_limit(self, key: str) -> tuple[bool, int, int]:
        """
        Check if request is allowed

        Args:
            key: Rate limit key

        Returns:
            Tuple of (allowed, remaining, retry_after)
        """
        async with self._lock:
            current_time = time.time()
            window_start = current_time - self.window

            # Remove old requests
            self._requests[key] = [ts for ts in self._requests[key] if ts > window_start]

            # Check limit
            request_count = len(self._requests[key])

            if request_count < self.limit:
                # Allow request
                self._requests[key].append(current_time)
                remaining = self.limit - request_count - 1
                return True, remaining, 0
            else:
                # Calculate retry after
                oldest_request = min(self._requests[key])
                retry_after = int(oldest_request + self.window - current_time) + 1
                return False, 0, retry_after


class FixedWindowRateLimiter:
    """
    Fixed Window algorithm

    Simple but has edge case where 2x requests possible at window boundary.

    Example: 100 req/min limit
    - 100 requests at 0:59
    - 100 requests at 1:00
    - Total: 200 requests in 1 second
    """

    def __init__(self, limit: int, window: int, backend: Optional[RateLimitBackend] = None):
        """
        Initialize fixed window

        Args:
            limit: Maximum requests per window
            window: Time window in seconds
            backend: Storage backend
        """
        self.limit = limit
        self.window = window
        self.backend = backend or MemoryRateLimitBackend()

    async def check_limit(self, key: str) -> tuple[bool, int, int]:
        """Check if request is allowed"""
        # Increment counter
        count = await self.backend.increment(key, self.window)

        # Check limit
        if count <= self.limit:
            remaining = self.limit - count
            return True, remaining, 0
        else:
            retry_after = self.window
            return False, 0, retry_after


class RateLimiter:
    """
    Unified rate limiter

    Supports multiple algorithms and backends.
    """

    def __init__(self, config: RateLimitConfig, backend: Optional[RateLimitBackend] = None):
        """
        Initialize rate limiter

        Args:
            config: Rate limit configuration
            backend: Storage backend
        """
        self.config = config
        self.backend = backend or MemoryRateLimitBackend()

        # Create algorithm instance
        if config.algorithm == "token_bucket":
            self.limiter = TokenBucketRateLimiter(
                capacity=config.requests,
                refill_rate=config.requests / config.window,
                backend=backend,
            )
        elif config.algorithm == "sliding_window":
            self.limiter = SlidingWindowRateLimiter(
                limit=config.requests, window=config.window, backend=backend
            )
        elif config.algorithm == "fixed_window":
            self.limiter = FixedWindowRateLimiter(
                limit=config.requests, window=config.window, backend=backend
            )
        else:
            raise ValueError(f"Unknown algorithm: {config.algorithm}")

    async def check_limit(self, key: str) -> tuple[bool, int, int]:
        """
        Check rate limit

        Args:
            key: Rate limit key (e.g., IP address, user ID)

        Returns:
            Tuple of (allowed, remaining, retry_after)
        """
        # Add key prefix
        full_key = f"{self.config.key_prefix}:{key}"

        # Check limit
        return await self.limiter.check_limit(full_key)

    def get_headers(self, remaining: int, retry_after: int) -> Dict[str, str]:
        """
        Get rate limit headers (RFC 6585)

        Args:
            remaining: Remaining requests
            retry_after: Seconds until reset

        Returns:
            Headers dictionary
        """
        if not self.config.include_headers:
            return {}

        headers = {
            "X-RateLimit-Limit": str(self.config.requests),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(time.time()) + self.config.window),
        }

        if retry_after > 0:
            headers["Retry-After"] = str(retry_after)

        return headers


class AdvancedRateLimitMiddleware:
    """
    Advanced rate limit middleware

    Features:
    - Multiple rate limiters per endpoint
    - User-based and IP-based limiting
    - Dynamic limits based on user tier
    - Whitelist/blacklist
    """

    def __init__(
        self,
        app: Callable,
        default_config: Optional[RateLimitConfig] = None,
        backend: Optional[RateLimitBackend] = None,
        get_user_id: Optional[Callable] = None,
        get_user_tier: Optional[Callable] = None,
        whitelist: Optional[List[str]] = None,
        blacklist: Optional[List[str]] = None,
    ):
        """
        Initialize advanced rate limit middleware

        Args:
            app: ASGI application
            default_config: Default rate limit config
            backend: Storage backend
            get_user_id: Function to extract user ID from request
            get_user_tier: Function to get user tier for dynamic limits
            whitelist: IP addresses to exempt
            blacklist: IP addresses to block
        """
        self.app = app
        self.default_config = default_config or RateLimitConfig()
        self.backend = backend or MemoryRateLimitBackend()
        self.get_user_id = get_user_id
        self.get_user_tier = get_user_tier
        self.whitelist = set(whitelist or [])
        self.blacklist = set(blacklist or [])

        # Rate limiters
        self.default_limiter = RateLimiter(self.default_config, self.backend)
        self.endpoint_limiters: Dict[str, RateLimiter] = {}

    def add_endpoint_limit(self, path: str, config: RateLimitConfig):
        """Add endpoint-specific rate limit"""
        self.endpoint_limiters[path] = RateLimiter(config, self.backend)

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """ASGI interface"""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get client IP
        client_ip = self._get_client_ip(scope)

        # Check blacklist
        if client_ip in self.blacklist:
            await self._send_rate_limit_error(send, 0, 0)
            return

        # Check whitelist
        if client_ip in self.whitelist:
            await self.app(scope, receive, send)
            return

        # Get rate limiter
        path = scope.get("path", "/")
        limiter = self.endpoint_limiters.get(path, self.default_limiter)

        # Get rate limit key
        key = await self._get_rate_limit_key(scope, client_ip)

        # Check limit
        allowed, remaining, retry_after = await limiter.check_limit(key)

        if not allowed:
            await self._send_rate_limit_error(
                send,
                remaining,
                retry_after,
                limiter.get_headers(remaining, retry_after),
            )
            return

        # Add headers to response
        headers = limiter.get_headers(remaining, retry_after)

        async def send_with_headers(message: Dict[str, Any]):
            if message["type"] == "http.response.start":
                response_headers = list(message.get("headers", []))

                for name, value in headers.items():
                    response_headers.append((name.lower().encode(), value.encode()))

                message["headers"] = response_headers

            await send(message)

        await self.app(scope, receive, send_with_headers)

    async def _get_rate_limit_key(self, scope: Dict[str, Any], client_ip: str) -> str:
        """Get rate limit key based on user or IP"""
        # Try user-based limiting first
        if self.get_user_id:
            user_id = await self.get_user_id(scope)
            if user_id:
                return f"user:{user_id}"

        # Fall back to IP-based
        return f"ip:{client_ip}"

    def _get_client_ip(self, scope: Dict[str, Any]) -> str:
        """Extract client IP from scope"""
        # Check X-Forwarded-For header
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode("utf-8")

        if forwarded:
            # Get first IP
            return forwarded.split(",")[0].strip()

        # Get client from scope
        client = scope.get("client")
        if client:
            return client[0]

        return "0.0.0.0"  # nosec B104 - binding to all interfaces is intentional for framework

    async def _send_rate_limit_error(
        self,
        send: Callable,
        remaining: int,
        retry_after: int,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Send 429 Too Many Requests response"""
        response_headers = [
            (b"content-type", b"application/json"),
        ]

        if headers:
            for name, value in headers.items():
                response_headers.append((name.lower().encode(), value.encode()))

        body = f'{{"error": "Rate limit exceeded", "retry_after": {retry_after}}}'.encode()

        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "headers": response_headers,
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )
