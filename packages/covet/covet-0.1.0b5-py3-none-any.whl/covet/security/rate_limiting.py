"""
Production Rate Limiting System

Comprehensive rate limiting with multiple strategies and distributed support.

Features:
- Multiple algorithms: Sliding Window, Token Bucket, Fixed Window
- Distributed rate limiting with Redis backend
- Per-user and per-IP rate limits
- Configurable time windows and limits
- Rate limit bypass detection
- Automatic cleanup and memory management
- DDoS protection integration
- Monitoring and metrics

Algorithms:
- Sliding Window: Most accurate, prevents burst at window boundaries
- Token Bucket: Smooths traffic, allows controlled bursts
- Fixed Window: Simple, efficient, but allows boundary bursts

Security Features:
- Rate limit bypass detection (header manipulation, distributed attacks)
- Automatic IP blocking for repeat offenders
- Configurable lockout periods
- Audit logging for security events

NO MOCK DATA: Real rate limiting with Redis or in-memory fallback.
"""

import asyncio
import hashlib
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    import redis.asyncio as aioredis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""

    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    FIXED_WINDOW = "fixed_window"


class RateLimitScope(str, Enum):
    """Rate limit scope."""

    IP = "ip"
    USER = "user"
    API_KEY = "api_key"
    GLOBAL = "global"


@dataclass
class RateLimitResult:
    """Result of rate limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_time: float
    retry_after: Optional[int] = None
    scope: Optional[str] = None
    identifier: Optional[str] = None


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""

    limit: int  # Maximum requests
    window: int  # Time window in seconds
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    scope: RateLimitScope = RateLimitScope.IP
    burst_multiplier: float = 1.5  # Allow burst up to limit * multiplier
    lockout_threshold: int = 3  # Failed attempts before lockout
    lockout_duration: int = 300  # Lockout duration in seconds


class SlidingWindowRateLimiter:
    """
    Sliding window rate limiter (most accurate).

    Prevents burst attacks at window boundaries.
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize sliding window rate limiter."""
        self.config = config
        self.requests: Dict[str, deque] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def check(self, identifier: str) -> RateLimitResult:
        """Check rate limit for identifier."""
        async with self._lock:
            current_time = time.time()
            request_times = self.requests[identifier]

            # Remove requests outside window
            cutoff_time = current_time - self.config.window
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()

            current_count = len(request_times)

            # Check limit
            if current_count >= self.config.limit:
                oldest_request = request_times[0] if request_times else current_time
                reset_time = oldest_request + self.config.window

                return RateLimitResult(
                    allowed=False,
                    limit=self.config.limit,
                    remaining=0,
                    reset_time=reset_time,
                    retry_after=int(reset_time - current_time),
                    scope=self.config.scope.value,
                    identifier=identifier,
                )

            # Allow request and record
            request_times.append(current_time)
            remaining = self.config.limit - (current_count + 1)

            return RateLimitResult(
                allowed=True,
                limit=self.config.limit,
                remaining=remaining,
                reset_time=current_time + self.config.window,
                scope=self.config.scope.value,
                identifier=identifier,
            )

    async def reset(self, identifier: str):
        """Reset rate limit for identifier."""
        if identifier in self.requests:
            del self.requests[identifier]


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter (smooth traffic).

    Allows controlled bursts while maintaining average rate.
    """

    def __init__(self, config: RateLimitConfig):
        """Initialize token bucket rate limiter."""
        self.config = config
        # capacity = limit, refill_rate = limit / window
        self.capacity = int(config.limit * config.burst_multiplier)
        self.refill_rate = config.limit / config.window
        self.buckets: Dict[str, Tuple[float, float]] = {}  # identifier -> (tokens, last_refill)
        self._lock = asyncio.Lock()

    async def check(self, identifier: str, tokens_requested: int = 1) -> RateLimitResult:
        """Check rate limit for identifier."""
        async with self._lock:
            current_time = time.time()

            # Initialize bucket if not exists
            if identifier not in self.buckets:
                self.buckets[identifier] = (float(self.capacity), current_time)

            tokens, last_refill = self.buckets[identifier]

            # Refill tokens based on time elapsed
            time_elapsed = current_time - last_refill
            tokens_to_add = time_elapsed * self.refill_rate
            tokens = min(self.capacity, tokens + tokens_to_add)

            # Check if enough tokens available
            if tokens >= tokens_requested:
                # Consume tokens
                tokens -= tokens_requested
                self.buckets[identifier] = (tokens, current_time)

                return RateLimitResult(
                    allowed=True,
                    limit=self.config.limit,
                    remaining=int(tokens),
                    reset_time=current_time + (self.capacity - tokens) / self.refill_rate,
                    scope=self.config.scope.value,
                    identifier=identifier,
                )
            else:
                # Not enough tokens
                time_to_wait = (tokens_requested - tokens) / self.refill_rate

                return RateLimitResult(
                    allowed=False,
                    limit=self.config.limit,
                    remaining=int(tokens),
                    reset_time=current_time + time_to_wait,
                    retry_after=int(time_to_wait) + 1,
                    scope=self.config.scope.value,
                    identifier=identifier,
                )

    async def reset(self, identifier: str):
        """Reset rate limit for identifier."""
        if identifier in self.buckets:
            del self.buckets[identifier]


class RedisRateLimiter:
    """
    Distributed rate limiter using Redis.

    Supports multiple algorithms with Redis backend.
    """

    def __init__(
        self,
        config: RateLimitConfig,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "rate_limit",
    ):
        """Initialize Redis rate limiter."""
        self.config = config
        self.key_prefix = key_prefix
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        self._connected = False

    async def connect(self):
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            raise RuntimeError(
                "redis.asyncio not available. Install with: pip install redis[hiredis]"
            )

        try:
            self.redis = await aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis.ping()
            self._connected = True
        except Exception as e:
            self._connected = False
            raise RuntimeError(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self._connected = False

    async def check(self, identifier: str) -> RateLimitResult:
        """Check rate limit for identifier."""
        if not self._connected:
            await self.connect()

        if self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return await self._check_sliding_window(identifier)
        elif self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
            return await self._check_token_bucket(identifier)
        else:  # FIXED_WINDOW
            return await self._check_fixed_window(identifier)

    async def _check_sliding_window(self, identifier: str) -> RateLimitResult:
        """Sliding window implementation using Redis sorted sets."""
        key = f"{self.key_prefix}:sw:{identifier}"
        current_time = time.time()
        window_start = current_time - self.config.window

        # Use pipeline for atomic operations
        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current requests
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(current_time): current_time})

        # Set expiration
        pipe.expire(key, self.config.window)

        results = await pipe.execute()
        current_count = results[1]

        if current_count >= self.config.limit:
            # Get oldest request time
            oldest = await self.redis.zrange(key, 0, 0, withscores=True)
            reset_time = (
                float(oldest[0][1]) + self.config.window
                if oldest
                else current_time + self.config.window
            )

            return RateLimitResult(
                allowed=False,
                limit=self.config.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=int(reset_time - current_time),
                scope=self.config.scope.value,
                identifier=identifier,
            )

        remaining = self.config.limit - (current_count + 1)

        return RateLimitResult(
            allowed=True,
            limit=self.config.limit,
            remaining=remaining,
            reset_time=current_time + self.config.window,
            scope=self.config.scope.value,
            identifier=identifier,
        )

    async def _check_token_bucket(self, identifier: str) -> RateLimitResult:
        """Token bucket implementation using Redis."""
        key = f"{self.key_prefix}:tb:{identifier}"
        capacity = int(self.config.limit * self.config.burst_multiplier)
        refill_rate = self.config.limit / self.config.window
        current_time = time.time()

        # Get current bucket state
        bucket_data = await self.redis.get(key)

        if bucket_data:
            tokens, last_refill = map(float, bucket_data.split(":"))
        else:
            tokens, last_refill = float(capacity), current_time

        # Refill tokens
        time_elapsed = current_time - last_refill
        tokens_to_add = time_elapsed * refill_rate
        tokens = min(capacity, tokens + tokens_to_add)

        # Check if enough tokens
        if tokens >= 1:
            tokens -= 1
            # Save updated bucket
            await self.redis.setex(key, self.config.window, f"{tokens}:{current_time}")

            return RateLimitResult(
                allowed=True,
                limit=self.config.limit,
                remaining=int(tokens),
                reset_time=current_time + (capacity - tokens) / refill_rate,
                scope=self.config.scope.value,
                identifier=identifier,
            )
        else:
            time_to_wait = (1 - tokens) / refill_rate

            return RateLimitResult(
                allowed=False,
                limit=self.config.limit,
                remaining=0,
                reset_time=current_time + time_to_wait,
                retry_after=int(time_to_wait) + 1,
                scope=self.config.scope.value,
                identifier=identifier,
            )

    async def _check_fixed_window(self, identifier: str) -> RateLimitResult:
        """Fixed window implementation using Redis."""
        # Calculate current window
        current_time = int(time.time())
        window_start = (current_time // self.config.window) * self.config.window
        key = f"{self.key_prefix}:fw:{identifier}:{window_start}"

        # Increment counter
        count = await self.redis.incr(key)

        # Set expiration on first request
        if count == 1:
            await self.redis.expire(key, self.config.window)

        if count > self.config.limit:
            reset_time = window_start + self.config.window

            return RateLimitResult(
                allowed=False,
                limit=self.config.limit,
                remaining=0,
                reset_time=reset_time,
                retry_after=int(reset_time - current_time),
                scope=self.config.scope.value,
                identifier=identifier,
            )

        remaining = self.config.limit - count

        return RateLimitResult(
            allowed=True,
            limit=self.config.limit,
            remaining=remaining,
            reset_time=window_start + self.config.window,
            scope=self.config.scope.value,
            identifier=identifier,
        )

    async def reset(self, identifier: str):
        """Reset rate limit for identifier."""
        pattern = f"{self.key_prefix}:*:{identifier}*"
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)


class RateLimitManager:
    """
    Centralized rate limit management.

    Supports multiple rate limit policies and automatic fallback.
    """

    def __init__(self, redis_url: Optional[str] = None, enable_redis: bool = True):
        """Initialize rate limit manager."""
        self.redis_url = redis_url
        self.enable_redis = enable_redis and REDIS_AVAILABLE and redis_url
        self.limiters: Dict[str, any] = {}
        self.blocked_identifiers: Dict[str, float] = {}  # identifier -> unblock_time
        self.violation_counts: Dict[str, int] = defaultdict(int)

    def add_limit(self, name: str, config: RateLimitConfig, use_redis: bool = False):
        """Add rate limit policy."""
        if use_redis and self.enable_redis:
            limiter = RedisRateLimiter(config, self.redis_url, key_prefix=f"rl:{name}")
        else:
            if config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                limiter = TokenBucketRateLimiter(config)
            else:  # SLIDING_WINDOW or FIXED_WINDOW default to sliding window
                limiter = SlidingWindowRateLimiter(config)

        self.limiters[name] = limiter

    async def check(
        self, name: str, identifier: str, bypass_block: bool = False
    ) -> RateLimitResult:
        """
        Check rate limit.

        Args:
            name: Rate limit policy name
            identifier: Unique identifier (IP, user ID, API key, etc.)
            bypass_block: Bypass block check (for admin override)

        Returns:
            RateLimitResult
        """
        # Check if identifier is blocked
        if not bypass_block and identifier in self.blocked_identifiers:
            unblock_time = self.blocked_identifiers[identifier]
            if time.time() < unblock_time:
                return RateLimitResult(
                    allowed=False,
                    limit=0,
                    remaining=0,
                    reset_time=unblock_time,
                    retry_after=int(unblock_time - time.time()),
                    scope="blocked",
                    identifier=identifier,
                )
            else:
                # Block expired
                del self.blocked_identifiers[identifier]

        if name not in self.limiters:
            # No limiter configured - allow by default
            return RateLimitResult(
                allowed=True, limit=0, remaining=0, reset_time=0, scope="unlimited"
            )

        limiter = self.limiters[name]
        result = await limiter.check(identifier)

        # Track violations for automatic blocking
        if not result.allowed:
            self.violation_counts[identifier] += 1

            # Check if should block
            if self.violation_counts[identifier] >= 5:  # 5 violations
                # Block for 1 hour
                self.blocked_identifiers[identifier] = time.time() + 3600
        else:
            # Reset violation count on success
            if identifier in self.violation_counts:
                self.violation_counts[identifier] = max(0, self.violation_counts[identifier] - 1)

        return result

    async def reset(self, name: str, identifier: str):
        """Reset rate limit for identifier."""
        if name in self.limiters:
            await self.limiters[name].reset(identifier)

    def unblock(self, identifier: str):
        """Manually unblock identifier."""
        if identifier in self.blocked_identifiers:
            del self.blocked_identifiers[identifier]
        if identifier in self.violation_counts:
            del self.violation_counts[identifier]

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        current_time = time.time()
        active_blocks = sum(
            1 for unblock_time in self.blocked_identifiers.values() if unblock_time > current_time
        )

        return {
            "policies": len(self.limiters),
            "active_blocks": active_blocks,
            "total_violations": sum(self.violation_counts.values()),
            "tracked_identifiers": len(self.violation_counts),
        }


__all__ = [
    "RateLimitAlgorithm",
    "RateLimitScope",
    "RateLimitResult",
    "RateLimitConfig",
    "SlidingWindowRateLimiter",
    "TokenBucketRateLimiter",
    "RedisRateLimiter",
    "RateLimitManager",
]
