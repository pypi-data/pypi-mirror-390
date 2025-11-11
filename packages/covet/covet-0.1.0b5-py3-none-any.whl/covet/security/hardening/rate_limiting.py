"""
CovetPy Advanced Rate Limiting Module

Production-grade rate limiting with multiple algorithms and distributed support:
- Token Bucket Algorithm
- Leaky Bucket Algorithm
- Fixed Window Counter
- Sliding Window Log
- Sliding Window Counter

Implements OWASP API Security Top 10 - API4:2023 Unrestricted Resource Consumption
protection with comprehensive rate limiting strategies.

Features:
- Multiple rate limiting algorithms
- Per-IP, per-user, per-endpoint limiting
- Redis-backed distributed rate limiting
- Custom limit handlers
- Rate limit headers (X-RateLimit-*)
- Burst protection
- Adaptive rate limiting
- Cost-based rate limiting (API credits)

Author: CovetPy Security Team
License: MIT
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(Enum):
    """Rate limiting algorithms."""

    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW_LOG = "sliding_window_log"
    SLIDING_WINDOW_COUNTER = "sliding_window_counter"


class RateLimitScope(Enum):
    """Scope for rate limiting."""

    GLOBAL = "global"
    PER_IP = "per_ip"
    PER_USER = "per_user"
    PER_ENDPOINT = "per_endpoint"
    PER_API_KEY = "per_api_key"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    max_requests: int  # Maximum requests
    window_seconds: int  # Time window in seconds
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.TOKEN_BUCKET
    scope: RateLimitScope = RateLimitScope.PER_IP
    burst_size: Optional[int] = None  # Maximum burst size (for token bucket)
    cost_per_request: float = 1.0  # Cost of each request (for cost-based limiting)
    key_prefix: str = "ratelimit"

    def __post_init__(self):
        """Set default burst size if not specified."""
        if self.burst_size is None:
            self.burst_size = self.max_requests


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    limit: int  # Total limit
    remaining: int  # Remaining requests
    reset_at: datetime  # When limit resets
    retry_after: Optional[int] = None  # Seconds until retry (if blocked)
    current_cost: float = 0.0  # Current cost consumed

    def to_headers(self) -> Dict[str, str]:
        """Convert to HTTP headers."""
        headers = {
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.remaining),
            "X-RateLimit-Reset": str(int(self.reset_at.timestamp())),
        }

        if self.retry_after is not None:
            headers["Retry-After"] = str(self.retry_after)

        return headers


@dataclass
class RateLimitViolation:
    """Rate limit violation details."""

    identifier: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    limit: int = 0
    window_seconds: int = 0
    requests_made: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "identifier": self.identifier,
            "timestamp": self.timestamp.isoformat(),
            "limit": self.limit,
            "window_seconds": self.window_seconds,
            "requests_made": self.requests_made,
            "metadata": self.metadata,
        }


class TokenBucketLimiter:
    """
    Token Bucket rate limiting algorithm.

    Tokens are added at a constant rate. Each request consumes tokens.
    Allows bursts up to bucket capacity.

    Best for: APIs that need to allow occasional bursts
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize token bucket limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config
        self.buckets: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_update)
        self.refill_rate = config.max_requests / config.window_seconds

    def _refill_bucket(self, key: str, current_time: float) -> float:
        """Refill bucket based on elapsed time."""
        if key not in self.buckets:
            return float(self.config.burst_size)

        tokens, last_update = self.buckets[key]
        elapsed = current_time - last_update
        new_tokens = min(float(self.config.burst_size), tokens + (elapsed * self.refill_rate))

        return new_tokens

    def check_limit(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """
        Check if request is allowed.

        Args:
            key: Rate limit key (IP, user ID, etc.)
            cost: Cost of this request

        Returns:
            RateLimitResult
        """
        current_time = time.time()
        tokens = self._refill_bucket(key, current_time)

        # Check if enough tokens available
        if tokens >= cost:
            # Consume tokens
            self.buckets[key] = (tokens - cost, current_time)

            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=int(tokens - cost),
                reset_at=datetime.fromtimestamp(
                    current_time + (self.config.burst_size - tokens + cost) / self.refill_rate
                ),
                current_cost=cost,
            )
        else:
            # Not enough tokens - blocked
            self.buckets[key] = (tokens, current_time)
            retry_after = int((cost - tokens) / self.refill_rate) + 1

            return RateLimitResult(
                allowed=False,
                limit=self.config.max_requests,
                remaining=0,
                reset_at=datetime.fromtimestamp(current_time + retry_after),
                retry_after=retry_after,
                current_cost=cost,
            )


class LeakyBucketLimiter:
    """
    Leaky Bucket rate limiting algorithm.

    Requests are added to a queue and processed at a constant rate.
    Smooths out bursts.

    Best for: APIs that need consistent request rates
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize leaky bucket limiter."""
        self.config = config
        self.queues: Dict[str, deque] = {}
        self.leak_rate = config.max_requests / config.window_seconds

    def _leak_bucket(self, key: str, current_time: float) -> int:
        """Leak (process) requests from bucket."""
        if key not in self.queues:
            return 0

        queue = self.queues[key]
        cutoff_time = current_time - self.config.window_seconds

        # Remove old requests
        while queue and queue[0] < cutoff_time:
            queue.popleft()

        return len(queue)

    def check_limit(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """Check if request is allowed."""
        current_time = time.time()
        queue_size = self._leak_bucket(key, current_time)

        if queue_size < self.config.max_requests:
            # Add to queue
            if key not in self.queues:
                self.queues[key] = deque()
            self.queues[key].append(current_time)

            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=self.config.max_requests - queue_size - 1,
                reset_at=datetime.fromtimestamp(current_time + self.config.window_seconds),
            )
        else:
            # Queue full - blocked
            retry_after = int(self.queues[key][0] + self.config.window_seconds - current_time) + 1

            return RateLimitResult(
                allowed=False,
                limit=self.config.max_requests,
                remaining=0,
                reset_at=datetime.fromtimestamp(current_time + retry_after),
                retry_after=retry_after,
            )


class FixedWindowLimiter:
    """
    Fixed Window Counter rate limiting algorithm.

    Counts requests in fixed time windows.
    Simple but can allow 2x limit at window boundaries.

    Best for: Simple use cases with acceptable burst at boundaries
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize fixed window limiter."""
        self.config = config
        self.windows: Dict[str, Tuple[int, float]] = {}  # key -> (count, window_start)

    def _get_current_window(self, current_time: float) -> float:
        """Get start time of current window."""
        return (int(current_time) // self.config.window_seconds) * self.config.window_seconds

    def check_limit(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """Check if request is allowed."""
        current_time = time.time()
        window_start = self._get_current_window(current_time)

        # Get or create window
        if key not in self.windows or self.windows[key][1] < window_start:
            # New window
            count = 0
        else:
            count = self.windows[key][0]

        # Check limit
        if count + cost <= self.config.max_requests:
            # Allowed
            self.windows[key] = (count + cost, window_start)

            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=int(self.config.max_requests - count - cost),
                reset_at=datetime.fromtimestamp(window_start + self.config.window_seconds),
                current_cost=cost,
            )
        else:
            # Blocked
            retry_after = int(window_start + self.config.window_seconds - current_time) + 1

            return RateLimitResult(
                allowed=False,
                limit=self.config.max_requests,
                remaining=0,
                reset_at=datetime.fromtimestamp(window_start + self.config.window_seconds),
                retry_after=retry_after,
                current_cost=cost,
            )


class SlidingWindowLogLimiter:
    """
    Sliding Window Log rate limiting algorithm.

    Stores timestamp of each request. Accurate but memory-intensive.

    Best for: When accuracy is critical and memory is available
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize sliding window log limiter."""
        self.config = config
        self.logs: Dict[str, deque] = {}

    def check_limit(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """Check if request is allowed."""
        current_time = time.time()
        cutoff_time = current_time - self.config.window_seconds

        # Initialize log if needed
        if key not in self.logs:
            self.logs[key] = deque()

        log = self.logs[key]

        # Remove old entries
        while log and log[0] < cutoff_time:
            log.popleft()

        # Check limit
        if len(log) + cost <= self.config.max_requests:
            # Allowed - add entry
            for _ in range(int(cost)):
                log.append(current_time)

            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=int(self.config.max_requests - len(log)),
                reset_at=datetime.fromtimestamp(
                    log[0] + self.config.window_seconds
                    if log
                    else current_time + self.config.window_seconds
                ),
                current_cost=cost,
            )
        else:
            # Blocked
            retry_after = int(log[0] + self.config.window_seconds - current_time) + 1 if log else 1

            return RateLimitResult(
                allowed=False,
                limit=self.config.max_requests,
                remaining=0,
                reset_at=datetime.fromtimestamp(current_time + retry_after),
                retry_after=retry_after,
                current_cost=cost,
            )


class SlidingWindowCounterLimiter:
    """
    Sliding Window Counter rate limiting algorithm.

    Interpolates between two fixed windows. Good balance of accuracy and memory.

    Best for: Production use - good accuracy with reasonable memory usage
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize sliding window counter limiter."""
        self.config = config
        self.windows: Dict[str, Dict[float, int]] = {}  # key -> {window_start: count}

    def _get_window_start(self, timestamp: float) -> float:
        """Get start time of window for timestamp."""
        return (int(timestamp) // self.config.window_seconds) * self.config.window_seconds

    def check_limit(self, key: str, cost: float = 1.0) -> RateLimitResult:
        """Check if request is allowed."""
        current_time = time.time()
        current_window = self._get_window_start(current_time)
        previous_window = current_window - self.config.window_seconds

        # Initialize windows if needed
        if key not in self.windows:
            self.windows[key] = {}

        windows = self.windows[key]

        # Clean old windows
        old_windows = [w for w in windows.keys() if w < previous_window]
        for w in old_windows:
            del windows[w]

        # Calculate weighted count
        previous_count = windows.get(previous_window, 0)
        current_count = windows.get(current_window, 0)

        # Weight based on position in current window
        elapsed_in_current = current_time - current_window
        weight = elapsed_in_current / self.config.window_seconds
        estimated_count = (previous_count * (1 - weight)) + current_count

        # Check limit
        if estimated_count + cost <= self.config.max_requests:
            # Allowed
            windows[current_window] = current_count + cost

            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=int(self.config.max_requests - estimated_count - cost),
                reset_at=datetime.fromtimestamp(current_window + self.config.window_seconds),
                current_cost=cost,
            )
        else:
            # Blocked
            retry_after = int(current_window + self.config.window_seconds - current_time) + 1

            return RateLimitResult(
                allowed=False,
                limit=self.config.max_requests,
                remaining=0,
                reset_at=datetime.fromtimestamp(current_window + self.config.window_seconds),
                retry_after=retry_after,
                current_cost=cost,
            )


class RateLimiter:
    """
    Main rate limiter with support for multiple algorithms.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limit configuration
        """
        self.config = config

        # Create appropriate limiter based on algorithm
        if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            self.limiter = TokenBucketLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.LEAKY_BUCKET:
            self.limiter = LeakyBucketLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            self.limiter = FixedWindowLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
            self.limiter = SlidingWindowLogLimiter(config)
        elif config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_COUNTER:
            self.limiter = SlidingWindowCounterLimiter(config)
        else:
            raise ValueError(f"Unsupported algorithm: {config.algorithm}")

        self._violations: List[RateLimitViolation] = []

    def check_limit(self, identifier: str, cost: float = 1.0) -> RateLimitResult:
        """
        Check rate limit for identifier.

        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            cost: Cost of this request

        Returns:
            RateLimitResult
        """
        # Generate key
        key = f"{self.config.key_prefix}:{identifier}"

        # Check limit
        result = self.limiter.check_limit(key, cost=cost)

        # Log violation if blocked
        if not result.allowed:
            violation = RateLimitViolation(
                identifier=identifier,
                limit=self.config.max_requests,
                window_seconds=self.config.window_seconds,
                requests_made=self.config.max_requests + int(cost),
                metadata={
                    "algorithm": self.config.algorithm.value,
                    "scope": self.config.scope.value,
                },
            )
            self._violations.append(violation)

            logger.warning(
                f"Rate limit exceeded for {identifier}", extra={"violation": violation.to_dict()}
            )

        return result

    def get_violations(self) -> List[RateLimitViolation]:
        """Get list of rate limit violations."""
        return self._violations.copy()

    def clear_violations(self) -> None:
        """Clear violation history."""
        self._violations.clear()


class RedisRateLimiter:
    """
    Redis-backed distributed rate limiter.

    Allows rate limiting across multiple application instances.
    """

    def __init__(self, redis_client: Any, config: RateLimitConfig):
        """
        Initialize Redis rate limiter.

        Args:
            redis_client: Redis client instance (redis-py)
            config: Rate limit configuration
        """
        self.redis = redis_client
        self.config = config

    async def check_limit(self, identifier: str, cost: float = 1.0) -> RateLimitResult:
        """
        Check rate limit using Redis.

        Args:
            identifier: Unique identifier
            cost: Cost of this request

        Returns:
            RateLimitResult
        """
        key = f"{self.config.key_prefix}:{identifier}"
        current_time = time.time()

        if self.config.algorithm == RateLimitAlgorithm.FIXED_WINDOW:
            return await self._fixed_window_redis(key, current_time, cost)
        elif self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW_LOG:
            return await self._sliding_window_log_redis(key, current_time, cost)
        else:
            # Default to token bucket for Redis
            return await self._token_bucket_redis(key, current_time, cost)

    async def _token_bucket_redis(
        self, key: str, current_time: float, cost: float
    ) -> RateLimitResult:
        """Token bucket algorithm with Redis."""
        # Use Lua script for atomic operations
        lua_script = """
        local key = KEYS[1]
        local max_tokens = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local cost = tonumber(ARGV[3])
        local current_time = tonumber(ARGV[4])
        local ttl = tonumber(ARGV[5])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_update')
        local tokens = tonumber(bucket[1]) or max_tokens
        local last_update = tonumber(bucket[2]) or current_time

        -- Refill tokens
        local elapsed = current_time - last_update
        tokens = math.min(max_tokens, tokens + (elapsed * refill_rate))

        if tokens >= cost then
            -- Allow request
            tokens = tokens - cost
            redis.call('HMSET', key, 'tokens', tokens, 'last_update', current_time)
            redis.call('EXPIRE', key, ttl)
            return {1, math.floor(tokens)}
        else
            -- Deny request
            return {0, math.floor(tokens)}
        end
        """

        refill_rate = self.config.max_requests / self.config.window_seconds

        try:
            result = await self.redis.eval(
                lua_script,
                1,
                key,
                self.config.burst_size,
                refill_rate,
                cost,
                current_time,
                self.config.window_seconds * 2,
            )

            allowed = bool(result[0])
            remaining = int(result[1])

            return RateLimitResult(
                allowed=allowed,
                limit=self.config.max_requests,
                remaining=remaining,
                reset_at=datetime.fromtimestamp(
                    current_time + (self.config.burst_size - remaining) / refill_rate
                ),
                retry_after=None if allowed else int((cost - remaining) / refill_rate) + 1,
            )
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            # Fail open (allow request) on Redis errors
            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=self.config.max_requests,
                reset_at=datetime.fromtimestamp(current_time + self.config.window_seconds),
            )

    async def _fixed_window_redis(
        self, key: str, current_time: float, cost: float
    ) -> RateLimitResult:
        """Fixed window algorithm with Redis."""
        window_key = f"{key}:{int(current_time) // self.config.window_seconds}"

        try:
            # Increment counter
            count = await self.redis.incrbyfloat(window_key, cost)

            # Set expiry on first request
            if count == cost:
                await self.redis.expire(window_key, self.config.window_seconds * 2)

            allowed = count <= self.config.max_requests
            remaining = max(0, int(self.config.max_requests - count))

            window_start = (
                int(current_time) // self.config.window_seconds
            ) * self.config.window_seconds

            return RateLimitResult(
                allowed=allowed,
                limit=self.config.max_requests,
                remaining=remaining,
                reset_at=datetime.fromtimestamp(window_start + self.config.window_seconds),
                retry_after=(
                    None
                    if allowed
                    else int(window_start + self.config.window_seconds - current_time) + 1
                ),
            )
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=self.config.max_requests,
                reset_at=datetime.fromtimestamp(current_time + self.config.window_seconds),
            )

    async def _sliding_window_log_redis(
        self, key: str, current_time: float, cost: float
    ) -> RateLimitResult:
        """Sliding window log algorithm with Redis."""
        cutoff_time = current_time - self.config.window_seconds

        try:
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, cutoff_time)

            # Count current requests
            count = await self.redis.zcard(key)

            if count + cost <= self.config.max_requests:
                # Add new entry
                for i in range(int(cost)):
                    await self.redis.zadd(key, {f"{current_time}:{i}": current_time})

                # Set expiry
                await self.redis.expire(key, self.config.window_seconds * 2)

                return RateLimitResult(
                    allowed=True,
                    limit=self.config.max_requests,
                    remaining=int(self.config.max_requests - count - cost),
                    reset_at=datetime.fromtimestamp(current_time + self.config.window_seconds),
                )
            else:
                # Get oldest entry for retry_after
                oldest = await self.redis.zrange(key, 0, 0, withscores=True)
                retry_after = (
                    int(oldest[0][1] + self.config.window_seconds - current_time) + 1
                    if oldest
                    else 1
                )

                return RateLimitResult(
                    allowed=False,
                    limit=self.config.max_requests,
                    remaining=0,
                    reset_at=datetime.fromtimestamp(current_time + retry_after),
                    retry_after=retry_after,
                )
        except Exception as e:
            logger.error(f"Redis rate limit error: {e}")
            return RateLimitResult(
                allowed=True,
                limit=self.config.max_requests,
                remaining=self.config.max_requests,
                reset_at=datetime.fromtimestamp(current_time + self.config.window_seconds),
            )


class RateLimitMiddleware:
    """
    Rate limiting middleware for CovetPy applications.
    """

    def __init__(
        self,
        limiter: Union[RateLimiter, RedisRateLimiter],
        identifier_func: Optional[Callable] = None,
        cost_func: Optional[Callable] = None,
        exempt_paths: Optional[List[str]] = None,
        audit_callback: Optional[Callable[[RateLimitViolation], None]] = None,
    ):
        """
        Initialize rate limit middleware.

        Args:
            limiter: Rate limiter instance
            identifier_func: Function to extract identifier from request
            cost_func: Function to calculate cost of request
            exempt_paths: Paths exempt from rate limiting
            audit_callback: Callback for rate limit violations
        """
        self.limiter = limiter
        self.identifier_func = identifier_func or self._default_identifier
        self.cost_func = cost_func or self._default_cost
        self.exempt_paths = set(exempt_paths or [])
        self.audit_callback = audit_callback

    def _default_identifier(self, scope: Dict[str, Any]) -> str:
        """Default identifier extraction (IP address)."""
        # Get client IP
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"x-forwarded-for":
                return header_value.decode().split(",")[0].strip()

        client = scope.get("client")
        if client:
            return client[0]  # IP address

        return "unknown"

    def _default_cost(self, scope: Dict[str, Any]) -> float:
        """Default cost calculation (1.0 per request)."""
        return 1.0

    async def __call__(self, scope, receive, send):
        """ASGI middleware interface."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        path = scope["path"]

        # Skip rate limiting for exempt paths
        if path in self.exempt_paths:
            return await self.app(scope, receive, send)

        # Get identifier and cost
        identifier = self.identifier_func(scope)
        cost = self.cost_func(scope)

        # Check rate limit
        result = await self._check_limit(identifier, cost)

        # Add rate limit headers
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))

                # Add rate limit headers
                for header_name, header_value in result.to_headers().items():
                    headers.append((header_name.encode(), header_value.encode()))

                message["headers"] = headers

            await send(message)

        # Block if limit exceeded
        if not result.allowed:
            # Audit callback
            if self.audit_callback and isinstance(self.limiter, RateLimiter):
                violations = self.limiter.get_violations()
                if violations:
                    self.audit_callback(violations[-1])

            await self._send_rate_limited(send, result)
            return

        # Continue to application
        await self.app(scope, receive, send_with_headers)

    async def _check_limit(self, identifier: str, cost: float) -> RateLimitResult:
        """Check rate limit (handles both sync and async limiters)."""
        if isinstance(self.limiter, RedisRateLimiter):
            return await self.limiter.check_limit(identifier, cost)
        else:
            return self.limiter.check_limit(identifier, cost)

    async def _send_rate_limited(self, send, result: RateLimitResult):
        """Send 429 Too Many Requests response."""
        headers = [
            (b"content-type", b"application/json"),
        ]

        # Add rate limit headers
        for header_name, header_value in result.to_headers().items():
            headers.append((header_name.encode(), header_value.encode()))

        await send({"type": "http.response.start", "status": 429, "headers": headers})

        body = json.dumps(
            {
                "error": "Rate limit exceeded",
                "limit": result.limit,
                "retry_after": result.retry_after,
            }
        ).encode()

        await send({"type": "http.response.body", "body": body})


__all__ = [
    # Enums
    "RateLimitAlgorithm",
    "RateLimitScope",
    # Data classes
    "RateLimitConfig",
    "RateLimitResult",
    "RateLimitViolation",
    # Limiters
    "TokenBucketLimiter",
    "LeakyBucketLimiter",
    "FixedWindowLimiter",
    "SlidingWindowLogLimiter",
    "SlidingWindowCounterLimiter",
    # Main classes
    "RateLimiter",
    "RedisRateLimiter",
    # Middleware
    "RateLimitMiddleware",
]
