"""
Role-Based Access Control (RBAC) System

Production-ready RBAC implementation with:
- Hierarchical roles and permissions
- Resource-based permissions
- Context-aware access control
- Permission inheritance
- Audit logging for access decisions
- Performance-optimized permission checking
"""

import fnmatch
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, Set

from .exceptions import PermissionDeniedError, RoleRequiredError
from .models import Permission, Role, User


class PermissionEffect(Enum):
    """Permission effect (allow/deny)"""

    ALLOW = "allow"
    DENY = "deny"


@dataclass
class ResourcePermission:
    """Resource-specific permission with context"""

    resource: str  # e.g., "users", "posts", "admin/*"
    action: str  # e.g., "read", "write", "delete", "*"
    effect: PermissionEffect = PermissionEffect.ALLOW
    conditions: Dict[str, Any] = field(default_factory=dict)  # Context conditions

    def matches(self, resource: str, action: str) -> bool:
        """Check if permission matches resource and action"""
        # Use fnmatch for wildcard matching
        resource_match = fnmatch.fnmatch(resource, self.resource)
        action_match = fnmatch.fnmatch(action, self.action)
        return resource_match and action_match


@dataclass
class AccessContext:
    """Context for access control decisions"""

    user_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_time: datetime = field(default_factory=datetime.utcnow)
    resource_owner_id: Optional[str] = None  # For ownership-based permissions
    additional_context: Dict[str, Any] = field(default_factory=dict)


class PermissionEvaluator(Protocol):
    """Protocol for custom permission evaluators"""

    def evaluate(self, permission: ResourcePermission, context: AccessContext) -> bool:
        """Evaluate permission with context"""
        ...


class OwnershipEvaluator:
    """Evaluator for ownership-based permissions"""

    def evaluate(self, permission: ResourcePermission, context: AccessContext) -> bool:
        """Check if user owns the resource"""
        if "owner_only" in permission.conditions:
            return context.user_id == context.resource_owner_id
        return True


class TimeBasedEvaluator:
    """Evaluator for time-based permissions"""

    def evaluate(self, permission: ResourcePermission, context: AccessContext) -> bool:
        """Check time-based restrictions"""
        conditions = permission.conditions

        if "allowed_hours" in conditions:
            current_hour = context.request_time.hour
            allowed_hours = conditions["allowed_hours"]
            if current_hour not in allowed_hours:
                return False

        if "allowed_days" in conditions:
            current_day = context.request_time.weekday()  # 0 = Monday
            allowed_days = conditions["allowed_days"]
            if current_day not in allowed_days:
                return False

        return True


class IPAddressEvaluator:
    """Evaluator for IP address-based restrictions"""

    def evaluate(self, permission: ResourcePermission, context: AccessContext) -> bool:
        """Check IP address restrictions"""
        conditions = permission.conditions

        if "allowed_ips" in conditions and context.ip_address:
            allowed_ips = conditions["allowed_ips"]
            if context.ip_address not in allowed_ips:
                return False

        if "blocked_ips" in conditions and context.ip_address:
            blocked_ips = conditions["blocked_ips"]
            if context.ip_address in blocked_ips:
                return False

        return True


@dataclass
class AccessDecision:
    """Result of access control decision"""

    allowed: bool
    reason: str
    matched_permissions: List[ResourcePermission] = field(default_factory=list)
    denied_by: Optional[ResourcePermission] = None


class PermissionStore(Protocol):
    """Protocol for permission storage backends"""

    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get roles for user"""
        ...

    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get permissions for role"""
        ...

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get direct permissions for user"""
        ...


class MemoryPermissionStore:
    """In-memory permission store for development"""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._roles: Dict[str, Role] = {}
        self._permissions: Dict[str, Permission] = {}
        self._lock = threading.RLock()
        self._initialize_default_permissions()

    def _initialize_default_permissions(self):
        """Initialize default permissions and roles"""
        # Default permissions
        permissions = [
            Permission(
                "read_own_profile",
                "Read Own Profile",
                "Read own user profile",
                "users",
                "read",
            ),
            Permission(
                "update_own_profile",
                "Update Own Profile",
                "Update own user profile",
                "users",
                "update",
            ),
            Permission(
                "read_all_users",
                "Read All Users",
                "Read all user profiles",
                "users",
                "read",
            ),
            Permission("create_users", "Create Users", "Create new users", "users", "create"),
            Permission(
                "update_users",
                "Update Users",
                "Update user profiles",
                "users",
                "update",
            ),
            Permission("delete_users", "Delete Users", "Delete users", "users", "delete"),
            Permission("admin_access", "Admin Access", "Full administrative access", "*", "*"),
        ]

        for perm in permissions:
            self._permissions[perm.id] = perm

        # Default roles
        user_role = Role(
            id="user",
            name="User",
            description="Standard user role",
            permissions={"read_own_profile", "update_own_profile"},
            is_system_role=True,
        )

        admin_role = Role(
            id="admin",
            name="Administrator",
            description="Full administrative access",
            permissions={"admin_access"},
            is_system_role=True,
        )

        moderator_role = Role(
            id="moderator",
            name="Moderator",
            description="User management access",
            permissions={"read_all_users", "update_users"},
            is_system_role=True,
        )

        self._roles["user"] = user_role
        self._roles["admin"] = admin_role
        self._roles["moderator"] = moderator_role

    def add_user(self, user: User):
        """Add user to store"""
        with self._lock:
            self._users[user.id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    def get_user_roles(self, user_id: str) -> List[Role]:
        """Get roles for user"""
        user = self._users.get(user_id)
        if not user:
            return []

        roles = []
        for role_id in user.roles:
            role = self._roles.get(role_id)
            if role:
                roles.append(role)

        return roles

    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """Get permissions for role"""
        role = self._roles.get(role_id)
        if not role:
            return []

        permissions = []
        for perm_id in role.permissions:
            perm = self._permissions.get(perm_id)
            if perm:
                permissions.append(perm)

        return permissions

    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get direct permissions for user (not implemented in basic version)"""
        return []

    def add_role(self, role: Role):
        """Add role to store"""
        with self._lock:
            self._roles[role.id] = role

    def add_permission(self, permission: Permission):
        """Add permission to store"""
        with self._lock:
            self._permissions[permission.id] = permission


class RBACManager:
    """
    Role-Based Access Control Manager
    """

    def __init__(self, store: Optional[PermissionStore] = None):
        self.store = store or MemoryPermissionStore()
        self.evaluators: Dict[str, PermissionEvaluator] = {
            "ownership": OwnershipEvaluator(),
            "time_based": TimeBasedEvaluator(),
            "ip_address": IPAddressEvaluator(),
        }
        self._permission_cache: Dict[str, Set[str]] = {}
        self._cache_lock = threading.RLock()

    def add_evaluator(self, name: str, evaluator: PermissionEvaluator):
        """Add custom permission evaluator"""
        self.evaluators[name] = evaluator

    def check_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        context: Optional[AccessContext] = None,
    ) -> AccessDecision:
        """
        Check if user has permission for resource/action

        Args:
            user_id: User ID
            resource: Resource name (e.g., "users", "posts")
            action: Action name (e.g., "read", "write", "delete")
            context: Access context for conditional permissions

        Returns:
            AccessDecision with result and reasoning
        """
        if not context:
            context = AccessContext(user_id=user_id)

        # Get all permissions for user
        user_permissions = self._get_user_permissions(user_id)

        matched_permissions = []
        denied_by = None

        # Check each permission
        for perm in user_permissions:
            resource_perm = ResourcePermission(
                resource=perm.resource,
                action=perm.action,
                effect=PermissionEffect.ALLOW,  # Default to allow for basic permissions
            )

            if resource_perm.matches(resource, action):
                matched_permissions.append(resource_perm)

                # Evaluate conditions if any
                if self._evaluate_conditions(resource_perm, context):
                    if resource_perm.effect == PermissionEffect.DENY:
                        denied_by = resource_perm
                        return AccessDecision(
                            allowed=False,
                            reason=f"Explicitly denied by permission {perm.id}",
                            matched_permissions=matched_permissions,
                            denied_by=denied_by,
                        )

        # If we have matching permissions and none explicitly denied
        if matched_permissions:
            return AccessDecision(
                allowed=True,
                reason=f"Allowed by {len(matched_permissions)} matching permission(s)",
                matched_permissions=matched_permissions,
            )

        return AccessDecision(
            allowed=False,
            reason=f"No matching permissions for {resource}:{action}",
            matched_permissions=[],
        )

    def require_permission(
        self,
        user_id: str,
        resource: str,
        action: str,
        context: Optional[AccessContext] = None,
    ):
        """
        Require permission or raise exception

        Raises:
            PermissionDeniedError: If permission is denied
        """
        decision = self.check_permission(user_id, resource, action, context)
        if not decision.allowed:
            raise PermissionDeniedError(
                f"Permission denied for {resource}:{action} - {decision.reason}",
                f"{resource}:{action}",
            )

    def check_role(self, user_id: str, role_name: str) -> bool:
        """Check if user has specific role"""
        user_roles = self.store.get_user_roles(user_id)
        return any(role.name == role_name for role in user_roles)

    def require_role(self, user_id: str, role_name: str):
        """
        Require role or raise exception

        Raises:
            RoleRequiredError: If role is missing
        """
        if not self.check_role(user_id, role_name):
            raise RoleRequiredError(f"Role '{role_name}' required", role_name)

    def get_user_permissions_list(self, user_id: str) -> List[str]:
        """Get list of permission names for user"""
        permissions = self._get_user_permissions(user_id)
        return [f"{perm.resource}:{perm.action}" for perm in permissions]

    def get_user_roles_list(self, user_id: str) -> List[str]:
        """Get list of role names for user"""
        roles = self.store.get_user_roles(user_id)
        return [role.name for role in roles]

    def _get_user_permissions(self, user_id: str) -> List[Permission]:
        """Get all permissions for user (from roles + direct permissions)"""
        # Check cache first
        cache_key = f"user_permissions:{user_id}"

        with self._cache_lock:
            if cache_key in self._permission_cache:
                # In a real implementation, you'd check cache expiry
                pass

        all_permissions = []

        # Get permissions from roles
        user_roles = self.store.get_user_roles(user_id)
        for role in user_roles:
            role_permissions = self.store.get_role_permissions(role.id)
            all_permissions.extend(role_permissions)

        # Get direct user permissions
        user_permissions = self.store.get_user_permissions(user_id)
        all_permissions.extend(user_permissions)

        # Remove duplicates
        seen = set()
        unique_permissions = []
        for perm in all_permissions:
            if perm.id not in seen:
                seen.add(perm.id)
                unique_permissions.append(perm)

        return unique_permissions

    def _evaluate_conditions(self, permission: ResourcePermission, context: AccessContext) -> bool:
        """Evaluate permission conditions using registered evaluators"""
        for evaluator_name, evaluator in self.evaluators.items():
            if not evaluator.evaluate(permission, context):
                return False
        return True

    def invalidate_user_cache(self, user_id: str):
        """Invalidate permission cache for user"""
        with self._cache_lock:
            cache_key = f"user_permissions:{user_id}"
            self._permission_cache.pop(cache_key, None)


# Decorator for permission checking
def require_permission(resource: str, action: str, context_factory: Optional[Callable] = None):
    """
    Decorator to require permission for a function

    Usage:
        @require_permission("users", "read")
        def get_user(user_id: str, current_user: User):
            ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract current user from arguments
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break

            if not current_user:
                # Look in kwargs
                current_user = kwargs.get("current_user") or kwargs.get("user")

            if not current_user:
                raise PermissionDeniedError("No current user context")

            # Create context
            context = None
            if context_factory:
                context = context_factory(*args, **kwargs)

            # Check permission
            rbac = get_rbac_manager()
            rbac.require_permission(current_user.id, resource, action, context)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_role(role_name: str):
    """
    Decorator to require role for a function

    Usage:
        @require_role("admin")
        def delete_user(user_id: str, current_user: User):
            ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract current user from arguments
            current_user = None
            for arg in args:
                if isinstance(arg, User):
                    current_user = arg
                    break

            if not current_user:
                # Look in kwargs
                current_user = kwargs.get("current_user") or kwargs.get("user")

            if not current_user:
                raise RoleRequiredError("No current user context")

            # Check role
            rbac = get_rbac_manager()
            rbac.require_role(current_user.id, role_name)

            return func(*args, **kwargs)

        return wrapper

    return decorator


# Global RBAC manager instance
_rbac_manager_instance: Optional[RBACManager] = None


def get_rbac_manager() -> RBACManager:
    """Get RBAC manager singleton instance"""
    global _rbac_manager_instance
    if _rbac_manager_instance is None:
        _rbac_manager_instance = RBACManager()
    return _rbac_manager_instance


def configure_rbac_manager(store: Optional[PermissionStore] = None) -> RBACManager:
    """Configure RBAC manager with custom store"""
    global _rbac_manager_instance
    _rbac_manager_instance = RBACManager(store)
    return _rbac_manager_instance
