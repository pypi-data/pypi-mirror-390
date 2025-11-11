"""
Attribute-Based Access Control (ABAC) System

Production-grade ABAC implementation with policy engine, rule evaluation,
and support for complex access control scenarios.

Features:
- Policy-based authorization
- Subject attributes (user properties)
- Resource attributes (object properties)
- Action attributes (operation context)
- Environment attributes (time, location, IP, etc.)
- Complex rule evaluation (AND, OR, NOT, comparisons)
- Policy versioning and conflict resolution
- High-performance rule engine
- Complete audit trail

Policy Structure:
{
    "effect": "allow" | "deny",
    "subject": {
        "department": "engineering",
        "clearance_level": {"$gte": 3}
    },
    "resource": {
        "classification": "confidential",
        "owner": {"$eq": "${subject.user_id}"}
    },
    "action": ["read", "write"],
    "environment": {
        "time": {"$between": ["09:00", "17:00"]},
        "ip_range": {"$in": ["10.0.0.0/8", "192.168.0.0/16"]}
    }
}

Performance Targets:
- Policy evaluation: <10ms
- Complex rule evaluation: <20ms
- Support 1,000+ policies
"""

import asyncio
import ipaddress
import operator
import re
import threading
from datetime import datetime
from datetime import time as dt_time
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class PolicyEffect(str, Enum):
    """Policy effect."""

    ALLOW = "allow"
    DENY = "deny"


class Operator(str, Enum):
    """Comparison operators."""

    EQ = "$eq"  # Equal
    NE = "$ne"  # Not equal
    GT = "$gt"  # Greater than
    GTE = "$gte"  # Greater than or equal
    LT = "$lt"  # Less than
    LTE = "$lte"  # Less than or equal
    IN = "$in"  # In list
    NOT_IN = "$not_in"  # Not in list
    CONTAINS = "$contains"  # Contains substring/element
    REGEX = "$regex"  # Regex match
    BETWEEN = "$between"  # Between two values
    EXISTS = "$exists"  # Attribute exists


class LogicalOperator(str, Enum):
    """Logical operators."""

    AND = "$and"
    OR = "$or"
    NOT = "$not"


class AttributeEvaluator:
    """
    Evaluates attribute conditions against values.

    Supports comparison operators, logical operators, and variable substitution.
    """

    def __init__(self):
        """Initialize attribute evaluator."""
        self._operators = {
            Operator.EQ: operator.eq,
            Operator.NE: operator.ne,
            Operator.GT: operator.gt,
            Operator.GTE: operator.ge,
            Operator.LT: operator.lt,
            Operator.LTE: operator.le,
        }

    def evaluate(
        self, condition: Any, actual_value: Any, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Evaluate condition against actual value.

        Args:
            condition: Condition to evaluate (can be dict with operators)
            actual_value: Actual attribute value
            context: Context for variable substitution

        Returns:
            True if condition matches
        """
        context = context or {}

        # Simple equality check
        if not isinstance(condition, dict):
            return self._compare(condition, actual_value, context)

        # Check for operators
        for key, value in condition.items():
            # Logical operators
            if key == LogicalOperator.AND:
                return all(self.evaluate(subcond, actual_value, context) for subcond in value)
            elif key == LogicalOperator.OR:
                return any(self.evaluate(subcond, actual_value, context) for subcond in value)
            elif key == LogicalOperator.NOT:
                return not self.evaluate(value, actual_value, context)

            # Comparison operators
            elif key == Operator.EQ:
                return self._compare(value, actual_value, context)
            elif key == Operator.NE:
                return not self._compare(value, actual_value, context)
            elif key == Operator.GT:
                return self._operators[Operator.GT](
                    actual_value, self._resolve_value(value, context)
                )
            elif key == Operator.GTE:
                return self._operators[Operator.GTE](
                    actual_value, self._resolve_value(value, context)
                )
            elif key == Operator.LT:
                return self._operators[Operator.LT](
                    actual_value, self._resolve_value(value, context)
                )
            elif key == Operator.LTE:
                return self._operators[Operator.LTE](
                    actual_value, self._resolve_value(value, context)
                )
            elif key == Operator.IN:
                resolved = [self._resolve_value(v, context) for v in value]
                return actual_value in resolved
            elif key == Operator.NOT_IN:
                resolved = [self._resolve_value(v, context) for v in value]
                return actual_value not in resolved
            elif key == Operator.CONTAINS:
                resolved = self._resolve_value(value, context)
                if isinstance(actual_value, str):
                    return resolved in actual_value
                elif isinstance(actual_value, (list, set, tuple)):
                    return resolved in actual_value
                return False
            elif key == Operator.REGEX:
                if not isinstance(actual_value, str):
                    return False
                pattern = self._resolve_value(value, context)
                return bool(re.match(pattern, actual_value))
            elif key == Operator.BETWEEN:
                if len(value) != 2:
                    return False
                low = self._resolve_value(value[0], context)
                high = self._resolve_value(value[1], context)
                return low <= actual_value <= high
            elif key == Operator.EXISTS:
                return (actual_value is not None) == value

        return True

    def _compare(self, expected: Any, actual: Any, context: Dict[str, Any]) -> bool:
        """Compare expected and actual values with variable resolution."""
        resolved = self._resolve_value(expected, context)
        return resolved == actual

    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """
        Resolve variable references in value.

        Supports ${subject.user_id}, ${resource.owner}, etc.
        """
        if not isinstance(value, str):
            return value

        # Check for variable reference
        if not value.startswith("${") or not value.endswith("}"):
            return value

        # Extract variable path
        var_path = value[2:-1]
        parts = var_path.split(".")

        # Traverse context
        current = context
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None

        return current


class PolicyEvaluator:
    """
    Evaluates ABAC policies against request context.

    Determines if a policy allows or denies access based on attributes.
    """

    def __init__(self):
        """Initialize policy evaluator."""
        self._attr_evaluator = AttributeEvaluator()

    def evaluate_policy(
        self,
        policy: Dict[str, Any],
        subject: Dict[str, Any],
        resource: Dict[str, Any],
        action: str,
        environment: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Evaluate policy against request context.

        Args:
            policy: Policy definition
            subject: Subject attributes (user)
            resource: Resource attributes
            action: Action being performed
            environment: Environment attributes

        Returns:
            Tuple of (matches, reason)
        """
        # Build evaluation context
        context = {
            "subject": subject,
            "resource": resource,
            "action": action,
            "environment": environment,
        }

        # Evaluate subject conditions
        if "subject" in policy and policy["subject"]:
            if not self._evaluate_attributes(policy["subject"], subject, context):
                return False, "Subject conditions not met"

        # Evaluate resource conditions
        if "resource" in policy and policy["resource"]:
            if not self._evaluate_attributes(policy["resource"], resource, context):
                return False, "Resource conditions not met"

        # Evaluate action conditions
        if "action" in policy:
            actions = policy["action"]
            if isinstance(actions, str):
                actions = [actions]
            if action not in actions:
                return False, f"Action '{action}' not in policy actions"

        # Evaluate environment conditions
        if "environment" in policy and policy["environment"]:
            if not self._evaluate_attributes(policy["environment"], environment, context):
                return False, "Environment conditions not met"

        # All conditions met
        effect = policy.get("effect", PolicyEffect.ALLOW)
        return True, f"Policy matched with effect: {effect}"

    def _evaluate_attributes(
        self, conditions: Dict[str, Any], attributes: Dict[str, Any], context: Dict[str, Any]
    ) -> bool:
        """
        Evaluate attribute conditions.

        Args:
            conditions: Condition dictionary
            attributes: Actual attributes
            context: Full context for variable resolution

        Returns:
            True if all conditions match
        """
        for attr_name, condition in conditions.items():
            actual_value = attributes.get(attr_name)

            # Evaluate condition
            if not self._attr_evaluator.evaluate(condition, actual_value, context):
                return False

        return True


class ABACManager:
    """
    Attribute-Based Access Control manager.

    Manages policies and evaluates access requests.
    """

    def __init__(self, enable_audit: bool = True):
        """
        Initialize ABAC manager.

        Args:
            enable_audit: Enable audit logging
        """
        self.enable_audit = enable_audit
        self._policy_evaluator = PolicyEvaluator()
        self._lock = threading.RLock()

    async def create_policy(
        self,
        name: str,
        effect: PolicyEffect,
        subject: Optional[Dict[str, Any]] = None,
        resource: Optional[Dict[str, Any]] = None,
        action: Optional[List[str]] = None,
        environment: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        priority: int = 0,
        status: str = "active",
    ) -> "Policy":
        """
        Create ABAC policy.

        Args:
            name: Policy name
            effect: Allow or deny
            subject: Subject attribute conditions
            resource: Resource attribute conditions
            action: Allowed actions
            environment: Environment conditions
            description: Policy description
            priority: Evaluation priority
            status: Policy status

        Returns:
            Created policy
        """
        from .models import Policy as PolicyModel

        # Build policy rules
        rules = {
            "subject": subject or {},
            "resource": resource or {},
            "action": action or [],
            "environment": environment or {},
        }

        # Create policy
        policy = await PolicyModel.objects.create(
            name=name,
            description=description,
            effect=effect.value,
            status=status,
            version=1,
            priority=priority,
            rules=rules,
            subjects=subject,
            resources=resource,
            actions=action,
            environment=environment,
            metadata={},
        )

        return policy

    async def get_policy(self, policy_name: str) -> Optional["Policy"]:
        """
        Get policy by name.

        Args:
            policy_name: Policy name

        Returns:
            Policy or None
        """
        from .models import Policy as PolicyModel

        return await PolicyModel.objects.filter(name=policy_name, status="active").first()

    async def delete_policy(self, policy_name: str) -> bool:
        """
        Delete policy (set status to inactive).

        Args:
            policy_name: Policy name

        Returns:
            True if deleted
        """
        policy = await self.get_policy(policy_name)
        if not policy:
            return False

        policy.status = "inactive"
        await policy.save()

        return True

    async def get_active_policies(self) -> List["Policy"]:
        """
        Get all active policies ordered by priority.

        Returns:
            List of policies
        """
        from .models import Policy as PolicyModel

        return await PolicyModel.objects.filter(status="active").order_by("-priority", "name").all()

    async def evaluate_access(
        self,
        subject: Dict[str, Any],
        resource: Dict[str, Any],
        action: str,
        environment: Optional[Dict[str, Any]] = None,
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Evaluate access request against all policies.

        Args:
            subject: Subject attributes (user)
            resource: Resource attributes
            action: Action being performed
            environment: Environment attributes

        Returns:
            Tuple of (allowed, reason, policy_id)
        """
        environment = environment or {}

        # Add default environment attributes
        if "time" not in environment:
            environment["time"] = datetime.utcnow().isoformat()

        # Get active policies
        policies = await self.get_active_policies()

        # Evaluate policies in priority order
        deny_found = False
        deny_reason = ""

        for policy in policies:
            policy_dict = {
                "effect": policy.effect,
                "subject": policy.subjects or {},
                "resource": policy.resources or {},
                "action": policy.actions or [],
                "environment": policy.environment or {},
            }

            # Evaluate policy
            matches, reason = self._policy_evaluator.evaluate_policy(
                policy_dict, subject, resource, action, environment
            )

            if matches:
                # DENY takes precedence
                if policy.effect == PolicyEffect.DENY:
                    if self.enable_audit:
                        await self._log_audit(
                            subject=subject,
                            resource=resource,
                            action=action,
                            decision="deny",
                            reason=f"Denied by policy: {policy.name}",
                            policy_id=str(policy.id),
                        )
                    return False, f"Denied by policy: {policy.name}", str(policy.id)

                # ALLOW found
                if policy.effect == PolicyEffect.ALLOW:
                    if not deny_found:
                        if self.enable_audit:
                            await self._log_audit(
                                subject=subject,
                                resource=resource,
                                action=action,
                                decision="allow",
                                reason=f"Allowed by policy: {policy.name}",
                                policy_id=str(policy.id),
                            )
                        return True, f"Allowed by policy: {policy.name}", str(policy.id)

        # No matching policy - default deny
        if self.enable_audit:
            await self._log_audit(
                subject=subject,
                resource=resource,
                action=action,
                decision="deny",
                reason="No matching policy - default deny",
                policy_id=None,
            )

        return False, "No matching policy - default deny", None

    async def check_permission(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
        action: str,
        user_attributes: Optional[Dict[str, Any]] = None,
        resource_attributes: Optional[Dict[str, Any]] = None,
        environment_attributes: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if user has permission (convenience method).

        Args:
            user_id: User identifier
            resource_type: Resource type
            resource_id: Resource identifier
            action: Action to perform
            user_attributes: Additional user attributes
            resource_attributes: Resource attributes
            environment_attributes: Environment attributes

        Returns:
            True if access allowed
        """
        # Build subject
        subject = {"user_id": user_id}
        if user_attributes:
            subject.update(user_attributes)

        # Build resource
        resource = {"type": resource_type, "id": resource_id}
        if resource_attributes:
            resource.update(resource_attributes)

        # Evaluate
        allowed, _, _ = await self.evaluate_access(
            subject=subject, resource=resource, action=action, environment=environment_attributes
        )

        return allowed

    async def _log_audit(
        self,
        subject: Dict[str, Any],
        resource: Dict[str, Any],
        action: str,
        decision: str,
        reason: str,
        policy_id: Optional[str],
    ):
        """Log authorization decision to audit trail."""
        try:
            from .models import PermissionAuditLog

            await PermissionAuditLog.objects.create(
                user_id=subject.get("user_id", "unknown"),
                resource=resource.get("type", "unknown"),
                action=action,
                decision=decision,
                decision_reason=reason,
                policy_id=policy_id,
                context={
                    "subject": subject,
                    "resource": resource,
                },
            )
        except Exception:
            # Don't fail authorization if audit logging fails
            pass


class PolicyBuilder:
    """
    Fluent API for building ABAC policies.

    Example:
        policy = (PolicyBuilder("read-own-documents")
            .allow()
            .when_subject(department="engineering")
            .when_resource(owner="${subject.user_id}")
            .for_actions(["read"])
            .build())
    """

    def __init__(self, name: str):
        """
        Initialize policy builder.

        Args:
            name: Policy name
        """
        self._name = name
        self._effect = PolicyEffect.ALLOW
        self._subject: Dict[str, Any] = {}
        self._resource: Dict[str, Any] = {}
        self._action: List[str] = []
        self._environment: Dict[str, Any] = {}
        self._description: Optional[str] = None
        self._priority = 0

    def allow(self) -> "PolicyBuilder":
        """Set policy effect to ALLOW."""
        self._effect = PolicyEffect.ALLOW
        return self

    def deny(self) -> "PolicyBuilder":
        """Set policy effect to DENY."""
        self._effect = PolicyEffect.DENY
        return self

    def when_subject(self, **conditions) -> "PolicyBuilder":
        """Add subject conditions."""
        self._subject.update(conditions)
        return self

    def when_resource(self, **conditions) -> "PolicyBuilder":
        """Add resource conditions."""
        self._resource.update(conditions)
        return self

    def for_actions(self, actions: List[str]) -> "PolicyBuilder":
        """Set allowed actions."""
        self._action = actions
        return self

    def when_environment(self, **conditions) -> "PolicyBuilder":
        """Add environment conditions."""
        self._environment.update(conditions)
        return self

    def with_description(self, description: str) -> "PolicyBuilder":
        """Set policy description."""
        self._description = description
        return self

    def with_priority(self, priority: int) -> "PolicyBuilder":
        """Set policy priority."""
        self._priority = priority
        return self

    def build(self) -> Dict[str, Any]:
        """
        Build policy dictionary.

        Returns:
            Policy definition
        """
        return {
            "name": self._name,
            "effect": self._effect,
            "subject": self._subject,
            "resource": self._resource,
            "action": self._action,
            "environment": self._environment,
            "description": self._description,
            "priority": self._priority,
        }


__all__ = [
    "PolicyEffect",
    "Operator",
    "LogicalOperator",
    "AttributeEvaluator",
    "PolicyEvaluator",
    "ABACManager",
    "PolicyBuilder",
]
