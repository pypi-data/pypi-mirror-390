"""
Production-Grade IP Allowlist/Blocklist System

This module implements comprehensive IP filtering with allowlist (whitelist)
and blocklist (blacklist) support, including CIDR notation and automatic
blocking based on suspicious activity.

Security Features:
- IP allowlist (whitelist) for trusted sources
- IP blocklist (blacklist) for malicious sources
- CIDR notation support (192.168.1.0/24)
- Automatic blocking after N failed attempts
- Time-based automatic unblocking
- Redis backend for distributed filtering
- In-memory fallback for single-instance deployments

Use Cases:
- Restrict API access to known partners
- Block attackers performing brute force attacks
- Implement geographic restrictions
- Rate limit specific IP ranges
- Protect against DDoS attacks

Example Usage:
    from covet.security.ip_filter import IPFilter, IPFilterMiddleware

    # Create IP filter
    filter = IPFilter(
        allowlist=["192.168.1.0/24", "10.0.0.1"],
        blocklist=["203.0.113.0/24"]
    )

    # Automatically block IPs with 5 failed auth attempts
    filter.configure_auto_block(
        threshold=5,
        window=300,  # 5 minutes
        duration=3600  # block for 1 hour
    )

    # Add to middleware stack
    app.add_middleware(IPFilterMiddleware(filter))

    # Manual IP management
    filter.block_ip("192.0.2.100", duration=3600, reason="Brute force attack")
    filter.allow_ip("203.0.113.50")
"""

import ipaddress
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from threading import Lock
from typing import Deque, Dict, List, Optional, Set, Union

try:
    import redis.asyncio as aioredis
    from redis.exceptions import ConnectionError as RedisConnectionError
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    aioredis = None
    RedisConnectionError = Exception


@dataclass
class IPFilterRule:
    """IP filter rule configuration."""

    ip_or_cidr: str  # IP address or CIDR notation
    rule_type: str  # "allow" or "block"
    reason: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        # Validate IP or CIDR
        try:
            ipaddress.ip_network(self.ip_or_cidr, strict=False)
        except ValueError:
            raise ValueError(f"Invalid IP or CIDR notation: {self.ip_or_cidr}")

    def is_expired(self) -> bool:
        """Check if rule has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def matches(self, ip: str) -> bool:
        """Check if IP matches this rule."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            network = ipaddress.ip_network(self.ip_or_cidr, strict=False)
            return ip_obj in network
        except ValueError:
            return False


class InMemoryIPFilter:
    """
    In-memory IP filter with allowlist/blocklist support.

    Thread-safe implementation for single-instance deployments.
    """

    def __init__(
        self,
        allowlist: Optional[List[str]] = None,
        blocklist: Optional[List[str]] = None,
        default_action: str = "allow",
    ):
        """
        Initialize in-memory IP filter.

        Args:
            allowlist: List of allowed IPs/CIDRs
            blocklist: List of blocked IPs/CIDRs
            default_action: "allow" or "block" for unmatched IPs
        """
        self.default_action = default_action
        self._lock = Lock()

        # Initialize rules
        self.allow_rules: List[IPFilterRule] = []
        self.block_rules: List[IPFilterRule] = []

        # Load initial rules
        for ip in (allowlist or []):
            self.allow_ip(ip)

        for ip in (blocklist or []):
            self.block_ip(ip)

        # Auto-block tracking
        self.auto_block_enabled = False
        self.auto_block_threshold = 5
        self.auto_block_window = 300  # 5 minutes
        self.auto_block_duration = 3600  # 1 hour
        self._violation_counts: Dict[str, Deque[float]] = defaultdict(
            lambda: deque(maxlen=100)
        )

    def allow_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """
        Add IP to allowlist.

        Args:
            ip_or_cidr: IP address or CIDR notation
            reason: Reason for allowing
            duration: Duration in seconds (None = permanent)
        """
        expires_at = None
        if duration:
            expires_at = datetime.utcnow() + timedelta(seconds=duration)

        rule = IPFilterRule(
            ip_or_cidr=ip_or_cidr,
            rule_type="allow",
            reason=reason,
            expires_at=expires_at,
        )

        with self._lock:
            # Remove from blocklist if present
            self.block_rules = [
                r for r in self.block_rules
                if not self._rules_overlap(r, rule)
            ]
            self.allow_rules.append(rule)

    def block_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """
        Add IP to blocklist.

        Args:
            ip_or_cidr: IP address or CIDR notation
            reason: Reason for blocking
            duration: Duration in seconds (None = permanent)
        """
        expires_at = None
        if duration:
            expires_at = datetime.utcnow() + timedelta(seconds=duration)

        rule = IPFilterRule(
            ip_or_cidr=ip_or_cidr,
            rule_type="block",
            reason=reason,
            expires_at=expires_at,
        )

        with self._lock:
            self.block_rules.append(rule)

    def unblock_ip(self, ip_or_cidr: str):
        """
        Remove IP from blocklist.

        Args:
            ip_or_cidr: IP address or CIDR notation
        """
        with self._lock:
            self.block_rules = [
                r for r in self.block_rules
                if r.ip_or_cidr != ip_or_cidr
            ]

    def is_allowed(self, ip: str) -> tuple[bool, Optional[str]]:
        """
        Check if IP is allowed.

        Args:
            ip: IP address to check

        Returns:
            Tuple of (allowed: bool, reason: Optional[str])
        """
        with self._lock:
            # Clean up expired rules
            self._cleanup_expired_rules()

            # Check blocklist first (explicit blocks override default allow)
            for rule in self.block_rules:
                if rule.matches(ip):
                    return False, rule.reason or "IP blocked"

            # Check allowlist
            for rule in self.allow_rules:
                if rule.matches(ip):
                    return True, None

            # Apply default action
            if self.default_action == "allow":
                return True, None
            else:
                return False, "IP not in allowlist"

    def configure_auto_block(
        self,
        threshold: int = 5,
        window: int = 300,
        duration: int = 3600,
    ):
        """
        Configure automatic IP blocking.

        Args:
            threshold: Number of violations before blocking
            window: Time window in seconds for counting violations
            duration: Block duration in seconds
        """
        self.auto_block_enabled = True
        self.auto_block_threshold = threshold
        self.auto_block_window = window
        self.auto_block_duration = duration

    def record_violation(self, ip: str) -> bool:
        """
        Record a violation for an IP.

        Automatically blocks IP if threshold exceeded.

        Args:
            ip: IP address that violated policy

        Returns:
            True if IP was auto-blocked, False otherwise
        """
        if not self.auto_block_enabled:
            return False

        with self._lock:
            # Record violation timestamp
            now = time.time()
            self._violation_counts[ip].append(now)

            # Count recent violations
            cutoff = now - self.auto_block_window
            recent_violations = sum(
                1 for ts in self._violation_counts[ip]
                if ts > cutoff
            )

            # Auto-block if threshold exceeded
            if recent_violations >= self.auto_block_threshold:
                self.block_ip(
                    ip,
                    reason=f"Auto-blocked: {recent_violations} violations",
                    duration=self.auto_block_duration,
                )
                return True

            return False

    def _cleanup_expired_rules(self):
        """Remove expired rules."""
        self.allow_rules = [r for r in self.allow_rules if not r.is_expired()]
        self.block_rules = [r for r in self.block_rules if not r.is_expired()]

    def _rules_overlap(self, rule1: IPFilterRule, rule2: IPFilterRule) -> bool:
        """Check if two rules overlap."""
        try:
            net1 = ipaddress.ip_network(rule1.ip_or_cidr, strict=False)
            net2 = ipaddress.ip_network(rule2.ip_or_cidr, strict=False)
            return net1.overlaps(net2)
        except ValueError:
            return False

    def get_stats(self) -> Dict[str, int]:
        """Get filter statistics."""
        with self._lock:
            self._cleanup_expired_rules()
            return {
                "allow_rules": len(self.allow_rules),
                "block_rules": len(self.block_rules),
                "tracked_ips": len(self._violation_counts),
            }

    def list_blocked_ips(self) -> List[Dict[str, any]]:
        """Get list of blocked IPs with details."""
        with self._lock:
            self._cleanup_expired_rules()
            return [
                {
                    "ip": rule.ip_or_cidr,
                    "reason": rule.reason,
                    "created_at": rule.created_at.isoformat(),
                    "expires_at": (
                        rule.expires_at.isoformat()
                        if rule.expires_at else None
                    ),
                }
                for rule in self.block_rules
            ]


class RedisIPFilter:
    """
    Redis-backed IP filter for distributed deployments.

    Shares blocklist/allowlist across multiple application instances.
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        allowlist: Optional[List[str]] = None,
        blocklist: Optional[List[str]] = None,
        default_action: str = "allow",
        key_prefix: str = "ipfilter",
    ):
        """
        Initialize Redis IP filter.

        Args:
            redis_url: Redis connection URL
            allowlist: Initial allowlist
            blocklist: Initial blocklist
            default_action: Default action for unmatched IPs
            key_prefix: Redis key prefix
        """
        if not HAS_REDIS:
            raise ImportError("redis required for RedisIPFilter")

        self.redis_url = redis_url
        self.default_action = default_action
        self.key_prefix = key_prefix
        self._redis: Optional[aioredis.Redis] = None
        self._fallback = InMemoryIPFilter(allowlist, blocklist, default_action)
        self._redis_available = True

        # Auto-block configuration
        self.auto_block_enabled = False
        self.auto_block_threshold = 5
        self.auto_block_window = 300
        self.auto_block_duration = 3600

    async def connect(self):
        """Establish Redis connection."""
        if self._redis is None:
            try:
                self._redis = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                self._redis_available = True
            except Exception:
                self._redis_available = False

    async def close(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None

    def _get_key(self, key_type: str) -> str:
        """Generate Redis key."""
        return f"{self.key_prefix}:{key_type}"

    async def allow_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """Add IP to allowlist."""
        await self.connect()

        if not self._redis_available:
            return self._fallback.allow_ip(ip_or_cidr, reason, duration)

        try:
            key = self._get_key("allowlist")
            value = {
                "reason": reason,
                "created_at": datetime.utcnow().isoformat(),
            }

            import json
            await self._redis.hset(key, ip_or_cidr, json.dumps(value))

            if duration:
                # Set expiration
                ttl_key = f"{key}:{ip_or_cidr}:ttl"
                await self._redis.setex(ttl_key, duration, "1")

            # Remove from blocklist
            await self._redis.hdel(self._get_key("blocklist"), ip_or_cidr)

        except Exception:
            self._redis_available = False
            return self._fallback.allow_ip(ip_or_cidr, reason, duration)

    async def block_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """Add IP to blocklist."""
        await self.connect()

        if not self._redis_available:
            return self._fallback.block_ip(ip_or_cidr, reason, duration)

        try:
            key = self._get_key("blocklist")
            value = {
                "reason": reason,
                "created_at": datetime.utcnow().isoformat(),
            }

            import json
            await self._redis.hset(key, ip_or_cidr, json.dumps(value))

            if duration:
                # Set expiration
                ttl_key = f"{key}:{ip_or_cidr}:ttl"
                await self._redis.setex(ttl_key, duration, "1")

        except Exception:
            self._redis_available = False
            return self._fallback.block_ip(ip_or_cidr, reason, duration)

    async def unblock_ip(self, ip_or_cidr: str):
        """Remove IP from blocklist."""
        await self.connect()

        if not self._redis_available:
            return self._fallback.unblock_ip(ip_or_cidr)

        try:
            key = self._get_key("blocklist")
            await self._redis.hdel(key, ip_or_cidr)

            # Remove TTL key
            ttl_key = f"{key}:{ip_or_cidr}:ttl"
            await self._redis.delete(ttl_key)

        except Exception:
            self._redis_available = False
            return self._fallback.unblock_ip(ip_or_cidr)

    async def is_allowed(self, ip: str) -> tuple[bool, Optional[str]]:
        """Check if IP is allowed."""
        await self.connect()

        if not self._redis_available:
            return self._fallback.is_allowed(ip)

        try:
            import json

            # Check blocklist
            blocklist_key = self._get_key("blocklist")
            blocklist = await self._redis.hgetall(blocklist_key)

            for ip_or_cidr, value_str in blocklist.items():
                # Check TTL
                ttl_key = f"{blocklist_key}:{ip_or_cidr}:ttl"
                if await self._redis.exists(ttl_key):
                    # Rule exists, check if IP matches
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        network = ipaddress.ip_network(ip_or_cidr, strict=False)
                        if ip_obj in network:
                            value = json.loads(value_str)
                            return False, value.get("reason", "IP blocked")
                    except ValueError:
                        continue

            # Check allowlist
            allowlist_key = self._get_key("allowlist")
            allowlist = await self._redis.hgetall(allowlist_key)

            for ip_or_cidr, _ in allowlist.items():
                # Check TTL
                ttl_key = f"{allowlist_key}:{ip_or_cidr}:ttl"
                if not await self._redis.exists(ttl_key) or await self._redis.ttl(ttl_key) > 0:
                    try:
                        ip_obj = ipaddress.ip_address(ip)
                        network = ipaddress.ip_network(ip_or_cidr, strict=False)
                        if ip_obj in network:
                            return True, None
                    except ValueError:
                        continue

            # Default action
            if self.default_action == "allow":
                return True, None
            else:
                return False, "IP not in allowlist"

        except Exception:
            self._redis_available = False
            return self._fallback.is_allowed(ip)

    def configure_auto_block(
        self,
        threshold: int = 5,
        window: int = 300,
        duration: int = 3600,
    ):
        """Configure automatic IP blocking."""
        self.auto_block_enabled = True
        self.auto_block_threshold = threshold
        self.auto_block_window = window
        self.auto_block_duration = duration
        self._fallback.configure_auto_block(threshold, window, duration)

    async def record_violation(self, ip: str) -> bool:
        """Record a violation and auto-block if threshold exceeded."""
        if not self.auto_block_enabled:
            return False

        await self.connect()

        if not self._redis_available:
            return self._fallback.record_violation(ip)

        try:
            key = f"{self.key_prefix}:violations:{ip}"

            # Increment violation count
            count = await self._redis.incr(key)

            # Set expiration on first violation
            if count == 1:
                await self._redis.expire(key, self.auto_block_window)

            # Auto-block if threshold exceeded
            if count >= self.auto_block_threshold:
                await self.block_ip(
                    ip,
                    reason=f"Auto-blocked: {count} violations",
                    duration=self.auto_block_duration,
                )
                # Reset counter
                await self._redis.delete(key)
                return True

            return False

        except Exception:
            self._redis_available = False
            return self._fallback.record_violation(ip)


class IPFilter:
    """
    Unified IP filter with automatic backend selection.

    Uses Redis if available, falls back to in-memory otherwise.
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        allowlist: Optional[List[str]] = None,
        blocklist: Optional[List[str]] = None,
        default_action: str = "allow",
        use_redis: bool = True,
    ):
        """
        Initialize IP filter.

        Args:
            redis_url: Redis URL (uses default if None and use_redis=True)
            allowlist: Initial allowlist
            blocklist: Initial blocklist
            default_action: Default action for unmatched IPs
            use_redis: Whether to attempt using Redis
        """
        self.backend: Union[RedisIPFilter, InMemoryIPFilter]

        if use_redis and HAS_REDIS:
            try:
                redis_url = redis_url or "redis://localhost:6379"
                self.backend = RedisIPFilter(
                    redis_url, allowlist, blocklist, default_action
                )
            except Exception:
                self.backend = InMemoryIPFilter(
                    allowlist, blocklist, default_action
                )
        else:
            self.backend = InMemoryIPFilter(
                allowlist, blocklist, default_action
            )

    async def allow_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """Add IP to allowlist."""
        if isinstance(self.backend, RedisIPFilter):
            await self.backend.allow_ip(ip_or_cidr, reason, duration)
        else:
            self.backend.allow_ip(ip_or_cidr, reason, duration)

    async def block_ip(
        self,
        ip_or_cidr: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None,
    ):
        """Add IP to blocklist."""
        if isinstance(self.backend, RedisIPFilter):
            await self.backend.block_ip(ip_or_cidr, reason, duration)
        else:
            self.backend.block_ip(ip_or_cidr, reason, duration)

    async def unblock_ip(self, ip_or_cidr: str):
        """Remove IP from blocklist."""
        if isinstance(self.backend, RedisIPFilter):
            await self.backend.unblock_ip(ip_or_cidr)
        else:
            self.backend.unblock_ip(ip_or_cidr)

    async def is_allowed(self, ip: str) -> tuple[bool, Optional[str]]:
        """Check if IP is allowed."""
        if isinstance(self.backend, RedisIPFilter):
            return await self.backend.is_allowed(ip)
        else:
            return self.backend.is_allowed(ip)

    def configure_auto_block(
        self,
        threshold: int = 5,
        window: int = 300,
        duration: int = 3600,
    ):
        """Configure automatic IP blocking."""
        self.backend.configure_auto_block(threshold, window, duration)

    async def record_violation(self, ip: str) -> bool:
        """Record a violation."""
        if isinstance(self.backend, RedisIPFilter):
            return await self.backend.record_violation(ip)
        else:
            return self.backend.record_violation(ip)

    async def close(self):
        """Close connections."""
        if isinstance(self.backend, RedisIPFilter):
            await self.backend.close()


class IPFilterMiddleware:
    """
    ASGI middleware for IP filtering.

    Blocks requests from blocked IPs, allows requests from allowed IPs.
    """

    def __init__(
        self,
        ip_filter: IPFilter,
        trust_forwarded: bool = False,
    ):
        """
        Initialize IP filter middleware.

        Args:
            ip_filter: IP filter instance
            trust_forwarded: Trust X-Forwarded-For header
        """
        self.ip_filter = ip_filter
        self.trust_forwarded = trust_forwarded

    def _get_client_ip(self, scope: dict) -> str:
        """Extract client IP from ASGI scope."""
        if self.trust_forwarded:
            headers = dict(scope.get("headers", []))
            forwarded = headers.get(b"x-forwarded-for", b"").decode()
            if forwarded:
                return forwarded.split(",")[0].strip()

        client = scope.get("client")
        if client:
            return client[0]

        return "0.0.0.0"

    async def __call__(self, scope, receive, send):
        """ASGI middleware implementation."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Get client IP
        ip = self._get_client_ip(scope)

        # Check if allowed
        allowed, reason = await self.ip_filter.is_allowed(ip)

        if not allowed:
            # Block request
            await send({
                "type": "http.response.start",
                "status": 403,
                "headers": [(b"content-type", b"application/json")],
            })

            import json
            body = {
                "error": "Forbidden",
                "message": reason or "Your IP address is blocked",
            }

            await send({
                "type": "http.response.body",
                "body": json.dumps(body).encode(),
            })
            return

        # Allow request
        return await self.app(scope, receive, send)


__all__ = [
    "IPFilter",
    "IPFilterMiddleware",
    "IPFilterRule",
    "InMemoryIPFilter",
    "RedisIPFilter",
]
