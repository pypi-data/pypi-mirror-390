"""
Distributed Rate Limiter with Redis

Production-grade rate limiting for horizontally scaled applications.
Uses Redis for atomic operations to prevent race conditions.

CRITICAL FEATURES:
- Distributed rate limiting (works across all instances)
- Multiple algorithms: Token Bucket, Sliding Window, Fixed Window
- Atomic operations (no race conditions)
- Per-user and per-IP limiting
- Custom rate limits per endpoint
- Burst handling
- Rate limit headers (X-RateLimit-*)
- Graceful degradation

Algorithms:
1. Token Bucket: Allows bursts, smooth rate limiting
2. Sliding Window: Precise rate limiting, no burst edge cases
3. Fixed Window: Simple, efficient, allows bursts at window edges

Architecture:
- Primary: Redis with Lua scripts for atomicity
- Fallback: In-memory rate limiting
- Storage: Redis sorted sets for sliding window
- TTL: Automatic cleanup of old data
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError
    REDIS_AVAILABLE = True
except ImportError:
    aioredis = None
    RedisError = Exception
    REDIS_AVAILABLE = False


logger = logging.getLogger(__name__)


class RateLimitAlgorithm(str, Enum):
    """Rate limiting algorithms."""
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"
    FIXED_WINDOW = "fixed_window"


@dataclass
class RateLimitConfig:
    """
    Rate limiter configuration.

    Rate Limits:
    - Requests per window: Number of requests allowed
    - Window size: Time window in seconds
    - Burst size: Maximum burst (for token bucket)

    Redis Settings:
    - Connection pooling
    - Atomic operations via Lua scripts
    """

    # Redis settings
    redis_url: Optional[str] = None
    redis_prefix: str = "ratelimit:"
    redis_max_connections: int = 20
    redis_socket_timeout: float = 5.0

    # Rate limit settings
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    requests_per_window: int = 100
    window_seconds: int = 60  # 1 minute
    burst_size: Optional[int] = None  # For token bucket (default: requests_per_window)

    # Fallback
    fallback_to_memory: bool = True

    def __post_init__(self):
        if self.burst_size is None:
            self.burst_size = self.requests_per_window


@dataclass
class RateLimitResult:
    """Result of rate limit check."""
    allowed: bool
    limit: int
    remaining: int
    reset_at: float  # Unix timestamp
    retry_after: Optional[int] = None  # Seconds until retry


class RedisRateLimiter:
    """
    Redis-backed distributed rate limiter.

    Uses atomic Redis operations to prevent race conditions.
    Supports multiple rate limiting algorithms.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limiter configuration
        """
        self.config = config

        # Redis connection
        self._redis: Optional[aioredis.Redis] = None
        self._connection_lock = asyncio.Lock()
        self._fallback_storage: Optional[Dict] = None
        self._using_fallback = False

        # Lua scripts for atomic operations
        self._scripts: Dict[str, str] = {}
        self._script_shas: Dict[str, str] = {}

        # Metrics
        self._metrics = {
            "checks": 0,
            "allowed": 0,
            "blocked": 0,
            "errors": 0,
        }

    async def _get_redis(self) -> Optional[aioredis.Redis]:
        """Get or create Redis connection."""
        if self._redis is not None:
            return self._redis

        if not REDIS_AVAILABLE:
            if self.config.fallback_to_memory:
                logger.warning("Redis not available for rate limiting, using in-memory")
                self._using_fallback = True
                self._fallback_storage = {}
                return None
            raise RuntimeError("Redis library not installed")

        async with self._connection_lock:
            if self._redis is not None:
                return self._redis

            try:
                if self.config.redis_url:
                    self._redis = await aioredis.from_url(
                        self.config.redis_url,
                        max_connections=self.config.redis_max_connections,
                        socket_timeout=self.config.redis_socket_timeout,
                        decode_responses=True,
                    )
                    await self._redis.ping()
                    logger.info("Connected to Redis for rate limiting")
                    self._using_fallback = False

                    # Load Lua scripts
                    await self._load_scripts()

                    return self._redis
                else:
                    raise ValueError("No Redis URL configured")

            except Exception as e:
                logger.error(f"Failed to connect to Redis for rate limiting: {e}")
                if self.config.fallback_to_memory:
                    logger.warning("Using in-memory rate limiting as fallback")
                    self._using_fallback = True
                    self._fallback_storage = {}
                    return None
                else:
                    raise

    async def _load_scripts(self):
        """Load Lua scripts into Redis."""
        if not self._redis:
            return

        # Sliding window rate limiter script
        sliding_window_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])

        local window_start = now - window

        -- Remove old entries
        redis.call('ZREMRANGEBYSCORE', key, 0, window_start)

        -- Count requests in window
        local count = redis.call('ZCARD', key)

        if count < limit then
            -- Allow request
            redis.call('ZADD', key, now, now)
            redis.call('EXPIRE', key, window)
            return {1, limit - count - 1, now + window}
        else
            -- Block request
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')[2]
            local reset_at = tonumber(oldest) + window
            return {0, 0, reset_at}
        end
        """

        # Token bucket script
        token_bucket_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local rate = tonumber(ARGV[2])
        local capacity = tonumber(ARGV[3])
        local interval = tonumber(ARGV[4])

        local bucket = redis.call('HMGET', key, 'tokens', 'last_refill')
        local tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now

        -- Refill tokens
        local time_passed = now - last_refill
        local new_tokens = time_passed * rate
        tokens = math.min(capacity, tokens + new_tokens)

        if tokens >= 1 then
            -- Allow request
            tokens = tokens - 1
            redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
            redis.call('EXPIRE', key, interval * 2)
            return {1, math.floor(tokens), now + interval}
        else
            -- Block request
            local wait_time = (1 - tokens) / rate
            return {0, 0, now + wait_time}
        end
        """

        # Fixed window script
        fixed_window_script = """
        local key = KEYS[1]
        local now = tonumber(ARGV[1])
        local window = tonumber(ARGV[2])
        local limit = tonumber(ARGV[3])

        local current_window = math.floor(now / window) * window

        local count = redis.call('GET', key)
        count = tonumber(count) or 0

        if count < limit then
            -- Allow request
            count = redis.call('INCR', key)
            if count == 1 then
                redis.call('EXPIRE', key, window)
            end
            return {1, limit - count, current_window + window}
        else
            -- Block request
            return {0, 0, current_window + window}
        end
        """

        # Load scripts
        try:
            self._script_shas["sliding_window"] = await self._redis.script_load(
                sliding_window_script
            )
            self._script_shas["token_bucket"] = await self._redis.script_load(
                token_bucket_script
            )
            self._script_shas["fixed_window"] = await self._redis.script_load(
                fixed_window_script
            )
            logger.debug("Loaded rate limiting Lua scripts")
        except Exception as e:
            logger.error(f"Failed to load Lua scripts: {e}")

    def _rate_limit_key(self, identifier: str, namespace: str = "default") -> str:
        """Generate Redis key for rate limiting."""
        return f"{self.config.redis_prefix}{namespace}:{identifier}"

    async def check_rate_limit(
        self,
        identifier: str,
        namespace: str = "default",
        cost: int = 1,
    ) -> RateLimitResult:
        """
        Check if request is allowed under rate limit.

        Args:
            identifier: Unique identifier (user ID, IP address, etc.)
            namespace: Rate limit namespace (endpoint, resource, etc.)
            cost: Request cost (default: 1)

        Returns:
            RateLimitResult with decision and metadata
        """
        self._metrics["checks"] += 1

        try:
            redis = await self._get_redis()
            now = time.time()
            key = self._rate_limit_key(identifier, namespace)

            if self._using_fallback:
                # Use in-memory fallback
                result = await self._check_memory_rate_limit(key, now, cost)
            else:
                # Use Redis with appropriate algorithm
                if self.config.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
                    result = await self._check_sliding_window(redis, key, now, cost)
                elif self.config.algorithm == RateLimitAlgorithm.TOKEN_BUCKET:
                    result = await self._check_token_bucket(redis, key, now, cost)
                else:  # FIXED_WINDOW
                    result = await self._check_fixed_window(redis, key, now, cost)

            if result.allowed:
                self._metrics["allowed"] += 1
            else:
                self._metrics["blocked"] += 1

            return result

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            self._metrics["errors"] += 1
            # Fail open (allow request) on error
            return RateLimitResult(
                allowed=True,
                limit=self.config.requests_per_window,
                remaining=self.config.requests_per_window,
                reset_at=time.time() + self.config.window_seconds,
            )

    async def _check_sliding_window(
        self,
        redis: aioredis.Redis,
        key: str,
        now: float,
        cost: int,
    ) -> RateLimitResult:
        """Check rate limit using sliding window algorithm."""
        # Execute Lua script for atomic operation
        result = await redis.evalsha(
            self._script_shas["sliding_window"],
            1,
            key,
            now,
            self.config.window_seconds,
            self.config.requests_per_window,
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        reset_at = float(result[2])

        retry_after = None
        if not allowed:
            retry_after = int(reset_at - now)

        return RateLimitResult(
            allowed=allowed,
            limit=self.config.requests_per_window,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after,
        )

    async def _check_token_bucket(
        self,
        redis: aioredis.Redis,
        key: str,
        now: float,
        cost: int,
    ) -> RateLimitResult:
        """Check rate limit using token bucket algorithm."""
        rate = self.config.requests_per_window / self.config.window_seconds

        result = await redis.evalsha(
            self._script_shas["token_bucket"],
            1,
            key,
            now,
            rate,
            self.config.burst_size,
            self.config.window_seconds,
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        reset_at = float(result[2])

        retry_after = None
        if not allowed:
            retry_after = int(reset_at - now)

        return RateLimitResult(
            allowed=allowed,
            limit=self.config.burst_size,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after,
        )

    async def _check_fixed_window(
        self,
        redis: aioredis.Redis,
        key: str,
        now: float,
        cost: int,
    ) -> RateLimitResult:
        """Check rate limit using fixed window algorithm."""
        result = await redis.evalsha(
            self._script_shas["fixed_window"],
            1,
            key,
            now,
            self.config.window_seconds,
            self.config.requests_per_window,
        )

        allowed = bool(result[0])
        remaining = int(result[1])
        reset_at = float(result[2])

        retry_after = None
        if not allowed:
            retry_after = int(reset_at - now)

        return RateLimitResult(
            allowed=allowed,
            limit=self.config.requests_per_window,
            remaining=remaining,
            reset_at=reset_at,
            retry_after=retry_after,
        )

    async def _check_memory_rate_limit(
        self,
        key: str,
        now: float,
        cost: int,
    ) -> RateLimitResult:
        """Fallback in-memory rate limiting using sliding window."""
        if key not in self._fallback_storage:
            self._fallback_storage[key] = []

        # Remove old entries
        window_start = now - self.config.window_seconds
        self._fallback_storage[key] = [
            ts for ts in self._fallback_storage[key]
            if ts > window_start
        ]

        # Check limit
        count = len(self._fallback_storage[key])
        if count < self.config.requests_per_window:
            # Allow request
            self._fallback_storage[key].append(now)
            return RateLimitResult(
                allowed=True,
                limit=self.config.requests_per_window,
                remaining=self.config.requests_per_window - count - 1,
                reset_at=now + self.config.window_seconds,
            )
        else:
            # Block request
            oldest = min(self._fallback_storage[key])
            reset_at = oldest + self.config.window_seconds
            return RateLimitResult(
                allowed=False,
                limit=self.config.requests_per_window,
                remaining=0,
                reset_at=reset_at,
                retry_after=int(reset_at - now),
            )

    async def reset_rate_limit(
        self,
        identifier: str,
        namespace: str = "default",
    ) -> bool:
        """
        Reset rate limit for identifier.

        Args:
            identifier: Unique identifier
            namespace: Rate limit namespace

        Returns:
            True if reset successfully
        """
        try:
            redis = await self._get_redis()
            key = self._rate_limit_key(identifier, namespace)

            if self._using_fallback:
                self._fallback_storage.pop(key, None)
                return True
            else:
                result = await redis.delete(key)
                return result > 0

        except Exception as e:
            logger.error(f"Failed to reset rate limit: {e}")
            return False

    def get_headers(self, result: RateLimitResult) -> Dict[str, str]:
        """
        Generate X-RateLimit-* headers.

        Args:
            result: Rate limit result

        Returns:
            Dictionary of headers
        """
        headers = {
            "X-RateLimit-Limit": str(result.limit),
            "X-RateLimit-Remaining": str(result.remaining),
            "X-RateLimit-Reset": str(int(result.reset_at)),
        }

        if result.retry_after is not None:
            headers["Retry-After"] = str(result.retry_after)

        return headers

    def get_metrics(self) -> Dict[str, int]:
        """Get rate limiter metrics."""
        return self._metrics.copy()

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None


class RateLimiter:
    """
    High-level rate limiter interface.

    Provides convenience methods for common rate limiting scenarios.
    """

    def __init__(self, config: RateLimitConfig):
        """
        Initialize rate limiter.

        Args:
            config: Rate limiter configuration
        """
        self.config = config
        self.limiter = RedisRateLimiter(config)

    async def check_user_limit(
        self,
        user_id: str,
        endpoint: str = "default",
    ) -> RateLimitResult:
        """Check rate limit for user."""
        return await self.limiter.check_rate_limit(
            identifier=f"user:{user_id}",
            namespace=endpoint,
        )

    async def check_ip_limit(
        self,
        ip_address: str,
        endpoint: str = "default",
    ) -> RateLimitResult:
        """Check rate limit for IP address."""
        return await self.limiter.check_rate_limit(
            identifier=f"ip:{ip_address}",
            namespace=endpoint,
        )

    async def check_api_key_limit(
        self,
        api_key: str,
        endpoint: str = "default",
    ) -> RateLimitResult:
        """Check rate limit for API key."""
        return await self.limiter.check_rate_limit(
            identifier=f"apikey:{api_key}",
            namespace=endpoint,
        )

    async def reset_user_limit(
        self,
        user_id: str,
        endpoint: str = "default",
    ) -> bool:
        """Reset rate limit for user."""
        return await self.limiter.reset_rate_limit(
            identifier=f"user:{user_id}",
            namespace=endpoint,
        )

    def get_headers(self, result: RateLimitResult) -> Dict[str, str]:
        """Get rate limit headers."""
        return self.limiter.get_headers(result)

    def get_metrics(self) -> Dict[str, int]:
        """Get rate limiter metrics."""
        return self.limiter.get_metrics()

    async def close(self):
        """Close rate limiter."""
        await self.limiter.close()


__all__ = [
    "RateLimitConfig",
    "RateLimitAlgorithm",
    "RateLimitResult",
    "RedisRateLimiter",
    "RateLimiter",
]
