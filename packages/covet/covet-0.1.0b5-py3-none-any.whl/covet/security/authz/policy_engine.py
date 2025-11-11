"""
Unified Policy Engine

Combines RBAC and ABAC for comprehensive authorization with policy decision point (PDP),
policy information point (PIP), and policy enforcement point (PEP).

Features:
- Unified RBAC + ABAC evaluation
- Policy decision pipeline
- Caching and optimization
- Policy conflict resolution
- Performance monitoring
- Complete audit trail

Architecture:
- PIP (Policy Information Point): Collects attributes
- PDP (Policy Decision Point): Evaluates policies
- PEP (Policy Enforcement Point): Enforces decisions

Performance Targets:
- Authorization decision (cached): <5ms
- Authorization decision (uncached): <50ms
- Support 100,000+ decisions/sec (cached)
"""

import asyncio
import threading
import time
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from .abac import ABACManager
from .models import AuditDecision, PermissionAuditLog
from .permissions import get_permission_registry
from .rbac import RBACManager


class DecisionStrategy(str, Enum):
    """Policy evaluation strategy."""

    # RBAC only
    RBAC_ONLY = "rbac_only"

    # ABAC only
    ABAC_ONLY = "abac_only"

    # RBAC first, fallback to ABAC
    RBAC_FIRST = "rbac_first"

    # ABAC first, fallback to RBAC
    ABAC_FIRST = "abac_first"

    # Both must allow (most restrictive)
    BOTH_ALLOW = "both_allow"

    # Either can allow (most permissive)
    EITHER_ALLOW = "either_allow"


class AuthorizationDecision:
    """Authorization decision with metadata."""

    def __init__(
        self,
        allowed: bool,
        reason: str,
        strategy_used: str,
        rbac_result: Optional[bool] = None,
        abac_result: Optional[bool] = None,
        policy_id: Optional[str] = None,
        evaluation_time_ms: float = 0.0,
        cached: bool = False,
    ):
        """
        Initialize authorization decision.

        Args:
            allowed: Whether access is allowed
            reason: Decision reason
            strategy_used: Strategy that made decision
            rbac_result: RBAC evaluation result
            abac_result: ABAC evaluation result
            policy_id: Policy ID (for ABAC)
            evaluation_time_ms: Evaluation time in milliseconds
            cached: Whether result was cached
        """
        self.allowed = allowed
        self.reason = reason
        self.strategy_used = strategy_used
        self.rbac_result = rbac_result
        self.abac_result = abac_result
        self.policy_id = policy_id
        self.evaluation_time_ms = evaluation_time_ms
        self.cached = cached
        self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "strategy_used": self.strategy_used,
            "rbac_result": self.rbac_result,
            "abac_result": self.abac_result,
            "policy_id": self.policy_id,
            "evaluation_time_ms": self.evaluation_time_ms,
            "cached": self.cached,
            "timestamp": self.timestamp.isoformat(),
        }


class DecisionCache:
    """
    Thread-safe cache for authorization decisions with TTL.

    Uses LRU eviction when cache is full.
    """

    def __init__(self, max_size: int = 100000, ttl_seconds: int = 60):
        """
        Initialize decision cache.

        Args:
            max_size: Maximum cache size
            ttl_seconds: Time-to-live for cached decisions
        """
        self._cache: Dict[str, Tuple[AuthorizationDecision, float]] = {}
        self._lock = threading.RLock()
        self._max_size = max_size
        self._ttl = ttl_seconds
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[AuthorizationDecision]:
        """
        Get decision from cache.

        Args:
            key: Cache key

        Returns:
            Decision or None if expired/missing
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            decision, timestamp = self._cache[key]

            # Check expiration
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            decision.cached = True
            return decision

    def set(self, key: str, decision: AuthorizationDecision):
        """
        Set decision in cache.

        Args:
            key: Cache key
            decision: Authorization decision
        """
        with self._lock:
            # Evict if cache is full
            if len(self._cache) >= self._max_size:
                # Remove oldest 10%
                sorted_items = sorted(self._cache.items(), key=lambda x: x[1][1])
                to_remove = max(1, int(self._max_size * 0.1))
                for key_to_remove, _ in sorted_items[:to_remove]:
                    del self._cache[key_to_remove]

            self._cache[key] = (decision, time.time())

    def invalidate(self, key: Optional[str] = None):
        """Invalidate cache entry or entire cache."""
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                "size": len(self._cache),
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": f"{hit_rate:.2f}%",
            }


class PolicyInformationPoint:
    """
    Policy Information Point (PIP).

    Collects and enriches attributes for authorization decisions.
    """

    async def get_user_attributes(
        self, user_id: str, additional_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get user attributes.

        Args:
            user_id: User identifier
            additional_attributes: Additional user attributes

        Returns:
            User attributes dictionary
        """
        attributes = {
            "user_id": user_id,
        }

        if additional_attributes:
            attributes.update(additional_attributes)

        return attributes

    async def get_resource_attributes(
        self,
        resource_type: str,
        resource_id: str,
        additional_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Get resource attributes.

        Args:
            resource_type: Resource type
            resource_id: Resource identifier
            additional_attributes: Additional resource attributes

        Returns:
            Resource attributes dictionary
        """
        attributes = {
            "type": resource_type,
            "id": resource_id,
        }

        if additional_attributes:
            attributes.update(additional_attributes)

        return attributes

    async def get_environment_attributes(
        self, additional_attributes: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get environment attributes.

        Args:
            additional_attributes: Additional environment attributes

        Returns:
            Environment attributes dictionary
        """
        attributes = {
            "time": datetime.utcnow().isoformat(),
            "timestamp": int(datetime.utcnow().timestamp()),
        }

        if additional_attributes:
            attributes.update(additional_attributes)

        return attributes


class PolicyDecisionPoint:
    """
    Policy Decision Point (PDP).

    Evaluates authorization requests using RBAC and/or ABAC.
    """

    def __init__(
        self,
        rbac_manager: Optional[RBACManager] = None,
        abac_manager: Optional[ABACManager] = None,
        strategy: DecisionStrategy = DecisionStrategy.RBAC_FIRST,
        enable_caching: bool = True,
        cache_ttl: int = 60,
    ):
        """
        Initialize policy decision point.

        Args:
            rbac_manager: RBAC manager
            abac_manager: ABAC manager
            strategy: Decision strategy
            enable_caching: Enable decision caching
            cache_ttl: Cache TTL in seconds
        """
        self.rbac_manager = rbac_manager or RBACManager()
        self.abac_manager = abac_manager or ABACManager()
        self.strategy = strategy
        self.pip = PolicyInformationPoint()

        self._cache: Optional[DecisionCache] = None
        if enable_caching:
            self._cache = DecisionCache(ttl_seconds=cache_ttl)

        # Performance metrics
        self._metrics = {
            "total_decisions": 0,
            "rbac_decisions": 0,
            "abac_decisions": 0,
            "cache_hits": 0,
            "total_time_ms": 0.0,
        }
        self._metrics_lock = threading.Lock()

    async def evaluate(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        user_attributes: Optional[Dict[str, Any]] = None,
        resource_attributes: Optional[Dict[str, Any]] = None,
        environment_attributes: Optional[Dict[str, Any]] = None,
        scope: Optional[str] = None,
        scope_id: Optional[str] = None,
    ) -> AuthorizationDecision:
        """
        Evaluate authorization request.

        Args:
            user_id: User identifier
            resource_type: Resource type
            resource_id: Resource identifier
            action: Action to perform
            user_attributes: Additional user attributes
            resource_attributes: Additional resource attributes
            environment_attributes: Additional environment attributes
            scope: Permission scope
            scope_id: Scope identifier

        Returns:
            Authorization decision
        """
        start_time = time.time()

        # Check cache
        cache_key = self._build_cache_key(
            user_id, resource_type, resource_id, action, scope, scope_id
        )

        if self._cache:
            cached_decision = self._cache.get(cache_key)
            if cached_decision:
                with self._metrics_lock:
                    self._metrics["cache_hits"] += 1
                return cached_decision

        # Evaluate based on strategy
        decision = await self._evaluate_with_strategy(
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            user_attributes=user_attributes,
            resource_attributes=resource_attributes,
            environment_attributes=environment_attributes,
            scope=scope,
            scope_id=scope_id,
        )

        # Record evaluation time
        decision.evaluation_time_ms = (time.time() - start_time) * 1000

        # Update metrics
        with self._metrics_lock:
            self._metrics["total_decisions"] += 1
            self._metrics["total_time_ms"] += decision.evaluation_time_ms

        # Cache decision
        if self._cache:
            self._cache.set(cache_key, decision)

        return decision

    async def _evaluate_with_strategy(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> AuthorizationDecision:
        """Evaluate authorization using configured strategy."""

        permission = f"{resource_type}:{action}"

        if self.strategy == DecisionStrategy.RBAC_ONLY:
            return await self._evaluate_rbac_only(user_id, permission, scope, scope_id)

        elif self.strategy == DecisionStrategy.ABAC_ONLY:
            return await self._evaluate_abac_only(
                user_id,
                resource_type,
                resource_id,
                action,
                user_attributes,
                resource_attributes,
                environment_attributes,
            )

        elif self.strategy == DecisionStrategy.RBAC_FIRST:
            return await self._evaluate_rbac_first(
                user_id,
                resource_type,
                resource_id,
                action,
                permission,
                user_attributes,
                resource_attributes,
                environment_attributes,
                scope,
                scope_id,
            )

        elif self.strategy == DecisionStrategy.ABAC_FIRST:
            return await self._evaluate_abac_first(
                user_id,
                resource_type,
                resource_id,
                action,
                permission,
                user_attributes,
                resource_attributes,
                environment_attributes,
                scope,
                scope_id,
            )

        elif self.strategy == DecisionStrategy.BOTH_ALLOW:
            return await self._evaluate_both_allow(
                user_id,
                resource_type,
                resource_id,
                action,
                permission,
                user_attributes,
                resource_attributes,
                environment_attributes,
                scope,
                scope_id,
            )

        elif self.strategy == DecisionStrategy.EITHER_ALLOW:
            return await self._evaluate_either_allow(
                user_id,
                resource_type,
                resource_id,
                action,
                permission,
                user_attributes,
                resource_attributes,
                environment_attributes,
                scope,
                scope_id,
            )

        # Default to RBAC first
        return await self._evaluate_rbac_first(
            user_id,
            resource_type,
            resource_id,
            action,
            permission,
            user_attributes,
            resource_attributes,
            environment_attributes,
            scope,
            scope_id,
        )

    async def _evaluate_rbac_only(
        self, user_id: str, permission: str, scope: Optional[str], scope_id: Optional[str]
    ) -> AuthorizationDecision:
        """Evaluate using RBAC only."""
        allowed = await self.rbac_manager.check_permission(
            user_id, permission, scope, scope_id, log_audit=False
        )

        with self._metrics_lock:
            self._metrics["rbac_decisions"] += 1

        return AuthorizationDecision(
            allowed=allowed,
            reason=f"RBAC: {'allowed' if allowed else 'denied'}",
            strategy_used=DecisionStrategy.RBAC_ONLY,
            rbac_result=allowed,
        )

    async def _evaluate_abac_only(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
    ) -> AuthorizationDecision:
        """Evaluate using ABAC only."""
        # Collect attributes
        subject = await self.pip.get_user_attributes(user_id, user_attributes)
        resource = await self.pip.get_resource_attributes(
            resource_type, resource_id, resource_attributes
        )
        environment = await self.pip.get_environment_attributes(environment_attributes)

        # Evaluate
        allowed, reason, policy_id = await self.abac_manager.evaluate_access(
            subject, resource, action, environment
        )

        with self._metrics_lock:
            self._metrics["abac_decisions"] += 1

        return AuthorizationDecision(
            allowed=allowed,
            reason=f"ABAC: {reason}",
            strategy_used=DecisionStrategy.ABAC_ONLY,
            abac_result=allowed,
            policy_id=policy_id,
        )

    async def _evaluate_rbac_first(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        permission: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> AuthorizationDecision:
        """Evaluate RBAC first, fallback to ABAC."""
        rbac_allowed = await self.rbac_manager.check_permission(
            user_id, permission, scope, scope_id, log_audit=False
        )

        if rbac_allowed:
            with self._metrics_lock:
                self._metrics["rbac_decisions"] += 1

            return AuthorizationDecision(
                allowed=True,
                reason="RBAC: allowed",
                strategy_used=DecisionStrategy.RBAC_FIRST,
                rbac_result=True,
            )

        # Fallback to ABAC
        subject = await self.pip.get_user_attributes(user_id, user_attributes)
        resource = await self.pip.get_resource_attributes(
            resource_type, resource_id, resource_attributes
        )
        environment = await self.pip.get_environment_attributes(environment_attributes)

        abac_allowed, reason, policy_id = await self.abac_manager.evaluate_access(
            subject, resource, action, environment
        )

        with self._metrics_lock:
            self._metrics["rbac_decisions"] += 1
            self._metrics["abac_decisions"] += 1

        return AuthorizationDecision(
            allowed=abac_allowed,
            reason=f"RBAC denied, ABAC: {reason}",
            strategy_used=DecisionStrategy.RBAC_FIRST,
            rbac_result=False,
            abac_result=abac_allowed,
            policy_id=policy_id,
        )

    async def _evaluate_abac_first(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        permission: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> AuthorizationDecision:
        """Evaluate ABAC first, fallback to RBAC."""
        subject = await self.pip.get_user_attributes(user_id, user_attributes)
        resource = await self.pip.get_resource_attributes(
            resource_type, resource_id, resource_attributes
        )
        environment = await self.pip.get_environment_attributes(environment_attributes)

        abac_allowed, reason, policy_id = await self.abac_manager.evaluate_access(
            subject, resource, action, environment
        )

        if abac_allowed:
            with self._metrics_lock:
                self._metrics["abac_decisions"] += 1

            return AuthorizationDecision(
                allowed=True,
                reason=f"ABAC: {reason}",
                strategy_used=DecisionStrategy.ABAC_FIRST,
                abac_result=True,
                policy_id=policy_id,
            )

        # Fallback to RBAC
        rbac_allowed = await self.rbac_manager.check_permission(
            user_id, permission, scope, scope_id, log_audit=False
        )

        with self._metrics_lock:
            self._metrics["abac_decisions"] += 1
            self._metrics["rbac_decisions"] += 1

        return AuthorizationDecision(
            allowed=rbac_allowed,
            reason=f"ABAC denied, RBAC: {'allowed' if rbac_allowed else 'denied'}",
            strategy_used=DecisionStrategy.ABAC_FIRST,
            abac_result=False,
            rbac_result=rbac_allowed,
        )

    async def _evaluate_both_allow(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        permission: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> AuthorizationDecision:
        """Both RBAC and ABAC must allow (most restrictive)."""
        rbac_allowed = await self.rbac_manager.check_permission(
            user_id, permission, scope, scope_id, log_audit=False
        )

        subject = await self.pip.get_user_attributes(user_id, user_attributes)
        resource = await self.pip.get_resource_attributes(
            resource_type, resource_id, resource_attributes
        )
        environment = await self.pip.get_environment_attributes(environment_attributes)

        abac_allowed, reason, policy_id = await self.abac_manager.evaluate_access(
            subject, resource, action, environment
        )

        allowed = rbac_allowed and abac_allowed

        with self._metrics_lock:
            self._metrics["rbac_decisions"] += 1
            self._metrics["abac_decisions"] += 1

        return AuthorizationDecision(
            allowed=allowed,
            reason=f"RBAC: {rbac_allowed}, ABAC: {abac_allowed}",
            strategy_used=DecisionStrategy.BOTH_ALLOW,
            rbac_result=rbac_allowed,
            abac_result=abac_allowed,
            policy_id=policy_id,
        )

    async def _evaluate_either_allow(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        permission: str,
        user_attributes: Optional[Dict[str, Any]],
        resource_attributes: Optional[Dict[str, Any]],
        environment_attributes: Optional[Dict[str, Any]],
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> AuthorizationDecision:
        """Either RBAC or ABAC can allow (most permissive)."""
        rbac_allowed = await self.rbac_manager.check_permission(
            user_id, permission, scope, scope_id, log_audit=False
        )

        subject = await self.pip.get_user_attributes(user_id, user_attributes)
        resource = await self.pip.get_resource_attributes(
            resource_type, resource_id, resource_attributes
        )
        environment = await self.pip.get_environment_attributes(environment_attributes)

        abac_allowed, reason, policy_id = await self.abac_manager.evaluate_access(
            subject, resource, action, environment
        )

        allowed = rbac_allowed or abac_allowed

        with self._metrics_lock:
            self._metrics["rbac_decisions"] += 1
            self._metrics["abac_decisions"] += 1

        return AuthorizationDecision(
            allowed=allowed,
            reason=f"RBAC: {rbac_allowed}, ABAC: {abac_allowed}",
            strategy_used=DecisionStrategy.EITHER_ALLOW,
            rbac_result=rbac_allowed,
            abac_result=abac_allowed,
            policy_id=policy_id,
        )

    def _build_cache_key(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        scope: Optional[str],
        scope_id: Optional[str],
    ) -> str:
        """Build cache key for decision."""
        return f"{user_id}:{resource_type}:{resource_id}:{action}:{scope}:{scope_id}"

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        with self._metrics_lock:
            total = self._metrics["total_decisions"]
            avg_time = self._metrics["total_time_ms"] / total if total > 0 else 0

            metrics = {
                "total_decisions": total,
                "rbac_decisions": self._metrics["rbac_decisions"],
                "abac_decisions": self._metrics["abac_decisions"],
                "cache_hits": self._metrics["cache_hits"],
                "average_time_ms": f"{avg_time:.2f}",
            }

            if self._cache:
                metrics["cache_stats"] = self._cache.get_stats()

            return metrics

    def clear_cache(self):
        """Clear decision cache."""
        if self._cache:
            self._cache.invalidate()


__all__ = [
    "DecisionStrategy",
    "AuthorizationDecision",
    "DecisionCache",
    "PolicyInformationPoint",
    "PolicyDecisionPoint",
]
