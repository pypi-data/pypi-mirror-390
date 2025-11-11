"""
PCI DSS Access Control Implementation

Requirement 7: Restrict access to cardholder data by business need to know
Requirement 8: Identify and authenticate access to system components

SECURITY FEATURES:
- Principle of least privilege enforcement
- Need-to-know access control
- Time-based access restrictions
- Location-based access control
- Emergency break-glass procedures
- Access reviews and recertification
- Comprehensive audit logging
"""

import secrets
import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class AccessDecision(str, Enum):
    """Access control decision."""

    ALLOW = "allow"
    DENY = "deny"
    DENY_EXPLICIT = "deny_explicit"  # Explicitly denied by policy
    DENY_IMPLICIT = "deny_implicit"  # No matching allow rule


class AccessAction(str, Enum):
    """Access control actions."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"
    EXPORT = "export"


@dataclass
class AccessPolicy:
    """Access control policy."""

    policy_id: str
    name: str
    description: str
    resource_pattern: str  # Glob pattern for resource matching
    actions: Set[AccessAction]
    effect: AccessDecision  # ALLOW or DENY_EXPLICIT
    principals: Set[str]  # User IDs or role names
    conditions: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def matches_resource(self, resource: str) -> bool:
        """Check if policy matches resource."""
        import fnmatch

        return fnmatch.fnmatch(resource, self.resource_pattern)

    def matches_action(self, action: AccessAction) -> bool:
        """Check if policy matches action."""
        return action in self.actions or AccessAction.ADMIN in self.actions

    def matches_principal(self, principal: str, roles: Set[str]) -> bool:
        """Check if policy matches principal or their roles."""
        if principal in self.principals:
            return True
        return bool(roles & self.principals)

    def evaluate_conditions(self, context: Dict[str, Any]) -> bool:
        """Evaluate policy conditions."""
        if not self.conditions:
            return True

        # Time-based restrictions
        if "time_range" in self.conditions:
            time_range = self.conditions["time_range"]
            now = datetime.utcnow()
            start = datetime.fromisoformat(time_range["start"])
            end = datetime.fromisoformat(time_range["end"])
            if not (start <= now <= end):
                return False

        # IP-based restrictions
        if "ip_ranges" in self.conditions:
            allowed_ips = self.conditions["ip_ranges"]
            client_ip = context.get("ip_address")
            if client_ip and client_ip not in allowed_ips:
                return False

        # MFA requirement
        if self.conditions.get("require_mfa") and not context.get("mfa_verified"):
            return False

        # Location-based restrictions
        if "allowed_locations" in self.conditions:
            location = context.get("location")
            if location not in self.conditions["allowed_locations"]:
                return False

        return True


@dataclass
class AccessRequest:
    """Access control request."""

    request_id: str
    principal: str
    roles: Set[str]
    action: AccessAction
    resource: str
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AccessResult:
    """Access control decision result."""

    decision: AccessDecision
    request: AccessRequest
    matched_policies: List[AccessPolicy]
    reason: str
    evaluation_time_ms: float


class LeastPrivilegeEnforcer:
    """
    Enforces principle of least privilege.

    Tracks access patterns and recommends policy adjustments
    to minimize unnecessary privileges.
    """

    def __init__(self):
        """Initialize least privilege enforcer."""
        self.access_history: List[AccessRequest] = []
        self.unused_privileges: Dict[str, Set[str]] = {}
        self.lock = threading.RLock()

    def record_access(self, request: AccessRequest, granted: bool):
        """Record access request for analysis."""
        with self.lock:
            self.access_history.append(request)

            # Track unused privileges
            if not granted:
                key = f"{request.principal}:{request.resource}"
                if key not in self.unused_privileges:
                    self.unused_privileges[key] = set()
                self.unused_privileges[key].add(request.action.value)

    def get_unused_privileges(
        self,
        principal: str,
        lookback_days: int = 90,
    ) -> Dict[str, Set[str]]:
        """Get privileges that haven't been used."""
        cutoff = datetime.utcnow() - timedelta(days=lookback_days)

        with self.lock:
            unused = {}
            for key, actions in self.unused_privileges.items():
                if key.startswith(f"{principal}:"):
                    # Check if any access in lookback period
                    recent_access = any(
                        r.principal == principal
                        and r.timestamp >= cutoff
                        and r.action.value in actions
                        for r in self.access_history
                    )
                    if not recent_access:
                        unused[key] = actions

            return unused

    def recommend_policy_adjustments(
        self,
        principal: str,
        lookback_days: int = 90,
    ) -> List[str]:
        """Recommend policy adjustments based on usage patterns."""
        unused = self.get_unused_privileges(principal, lookback_days)

        recommendations = []
        for key, actions in unused.items():
            resource = key.split(":", 1)[1]
            recommendations.append(
                f"Remove unused {', '.join(actions)} access for {principal} "
                f"on resource {resource}"
            )

        return recommendations


class AccessControlManager:
    """
    Comprehensive access control manager for PCI DSS compliance.

    FEATURES:
    - Policy-based access control
    - Least privilege enforcement
    - Need-to-know restrictions
    - Emergency access procedures
    - Comprehensive audit logging
    """

    def __init__(self, audit_logger=None):
        """
        Initialize access control manager.

        Args:
            audit_logger: Audit logger for access decisions
        """
        self.policies: List[AccessPolicy] = []
        self.audit_logger = audit_logger
        self.least_privilege = LeastPrivilegeEnforcer()
        self.emergency_access: Dict[str, datetime] = {}
        self.lock = threading.RLock()

    def add_policy(self, policy: AccessPolicy):
        """Add access control policy."""
        with self.lock:
            self.policies.append(policy)
            # Sort by priority (higher priority first)
            self.policies.sort(key=lambda p: p.priority, reverse=True)

    def remove_policy(self, policy_id: str) -> bool:
        """Remove access control policy."""
        with self.lock:
            for i, policy in enumerate(self.policies):
                if policy.policy_id == policy_id:
                    self.policies.pop(i)
                    return True
            return False

    def check_access(
        self,
        principal: str,
        action: AccessAction,
        resource: str,
        roles: Optional[Set[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> AccessResult:
        """
        Check if access should be granted.

        Args:
            principal: User or service identifier
            action: Requested action
            resource: Resource being accessed
            roles: Principal's roles
            context: Request context (IP, time, MFA status, etc.)

        Returns:
            Access control decision
        """
        start_time = datetime.utcnow()

        roles = roles or set()
        context = context or {}

        # Create request
        request = AccessRequest(
            request_id=f"req_{secrets.token_hex(16)}",
            principal=principal,
            roles=roles,
            action=action,
            resource=resource,
            context=context,
        )

        # Check emergency access
        if self._check_emergency_access(principal):
            result = AccessResult(
                decision=AccessDecision.ALLOW,
                request=request,
                matched_policies=[],
                reason="Emergency break-glass access granted",
                evaluation_time_ms=self._elapsed_ms(start_time),
            )
            self._audit_decision(result)
            return result

        # Evaluate policies
        matched_policies = []
        decision = AccessDecision.DENY_IMPLICIT

        with self.lock:
            for policy in self.policies:
                if not policy.enabled:
                    continue

                # Check if policy matches
                if not policy.matches_resource(resource):
                    continue

                if not policy.matches_action(action):
                    continue

                if not policy.matches_principal(principal, roles):
                    continue

                if not policy.evaluate_conditions(context):
                    continue

                # Policy matches
                matched_policies.append(policy)

                # Explicit deny takes precedence
                if policy.effect == AccessDecision.DENY_EXPLICIT:
                    decision = AccessDecision.DENY_EXPLICIT
                    break

                # Allow if not explicitly denied
                if policy.effect == AccessDecision.ALLOW:
                    decision = AccessDecision.ALLOW

        # Determine reason
        if decision == AccessDecision.ALLOW:
            reason = f"Access granted by {len(matched_policies)} policy(ies)"
        elif decision == AccessDecision.DENY_EXPLICIT:
            reason = "Access explicitly denied by policy"
        else:
            reason = "No matching allow policy (implicit deny)"

        result = AccessResult(
            decision=decision,
            request=request,
            matched_policies=matched_policies,
            reason=reason,
            evaluation_time_ms=self._elapsed_ms(start_time),
        )

        # Record for least privilege analysis
        self.least_privilege.record_access(request, decision == AccessDecision.ALLOW)

        # Audit decision
        self._audit_decision(result)

        return result

    def grant_emergency_access(
        self,
        principal: str,
        duration_minutes: int = 60,
        reason: str = "",
    ):
        """
        Grant emergency break-glass access.

        Args:
            principal: User to grant access
            duration_minutes: Access duration in minutes
            reason: Justification for emergency access
        """
        expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)

        with self.lock:
            self.emergency_access[principal] = expires_at

        # Audit emergency access
        if self.audit_logger:
            from .audit_logger import AuditEventType, AuditLevel

            self.audit_logger.log(
                event_type=AuditEventType.ADMIN_CONFIG_CHANGE,
                action="grant_emergency_access",
                result="success",
                user_id=principal,
                level=AuditLevel.CRITICAL,
                details={
                    "duration_minutes": duration_minutes,
                    "expires_at": expires_at.isoformat(),
                    "reason": reason,
                },
            )

    def revoke_emergency_access(self, principal: str):
        """Revoke emergency access."""
        with self.lock:
            if principal in self.emergency_access:
                del self.emergency_access[principal]

                # Audit revocation
                if self.audit_logger:
                    from .audit_logger import AuditEventType, AuditLevel

                    self.audit_logger.log(
                        event_type=AuditEventType.ADMIN_CONFIG_CHANGE,
                        action="revoke_emergency_access",
                        result="success",
                        user_id=principal,
                        level=AuditLevel.WARNING,
                    )

    def _check_emergency_access(self, principal: str) -> bool:
        """Check if principal has active emergency access."""
        with self.lock:
            if principal not in self.emergency_access:
                return False

            expires_at = self.emergency_access[principal]
            if datetime.utcnow() >= expires_at:
                # Expired, remove
                del self.emergency_access[principal]
                return False

            return True

    def _audit_decision(self, result: AccessResult):
        """Audit access control decision."""
        if not self.audit_logger:
            return

        from .audit_logger import AuditEventType, AuditLevel

        event_type = (
            AuditEventType.AUTHZ_GRANTED
            if result.decision == AccessDecision.ALLOW
            else AuditEventType.AUTHZ_DENIED
        )

        level = AuditLevel.INFO if result.decision == AccessDecision.ALLOW else AuditLevel.WARNING

        self.audit_logger.log(
            event_type=event_type,
            action=result.request.action.value,
            result="granted" if result.decision == AccessDecision.ALLOW else "denied",
            user_id=result.request.principal,
            resource=result.request.resource,
            level=level,
            details={
                "decision": result.decision,
                "reason": result.reason,
                "matched_policies": [p.policy_id for p in result.matched_policies],
                "evaluation_time_ms": result.evaluation_time_ms,
            },
        )

    def _elapsed_ms(self, start_time: datetime) -> float:
        """Calculate elapsed time in milliseconds."""
        elapsed = datetime.utcnow() - start_time
        return elapsed.total_seconds() * 1000


__all__ = [
    "AccessControlManager",
    "AccessPolicy",
    "AccessDecision",
    "AccessAction",
    "AccessRequest",
    "AccessResult",
    "LeastPrivilegeEnforcer",
]
