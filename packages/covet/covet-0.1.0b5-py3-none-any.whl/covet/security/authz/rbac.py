"""
Role-Based Access Control (RBAC) System

Production-grade RBAC implementation with role hierarchy, dynamic evaluation,
scope management, and performance optimization.

Features:
- Role hierarchy with inheritance
- Dynamic role evaluation
- Role scope (global, organization, project)
- Many-to-many user-role assignments
- Default roles (admin, user, guest)
- Permission caching for performance
- Audit logging
- Thread-safe operations

Performance Targets:
- Role permission check (cached): <2ms
- Role permission check (uncached): <10ms
- Role hierarchy resolution: <5ms
- Support 10,000+ roles
"""

import asyncio
import threading
import time
from collections import defaultdict
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import (
    AuditDecision,
    Permission,
    PermissionAuditLog,
    PermissionScope,
    Role,
    RolePermission,
    UserRole,
)
from .permissions import PermissionRegistry, get_permission_registry


class RoleCache:
    """
    Thread-safe cache for role permissions with TTL.

    Caches role permissions to reduce database queries.
    """

    def __init__(self, ttl_seconds: int = 300, max_size: int = 10000):
        """
        Initialize role cache.

        Args:
            ttl_seconds: Time-to-live for cache entries
            max_size: Maximum cache size
        """
        self._cache: Dict[str, Tuple[Set[str], float]] = {}
        self._lock = threading.RLock()
        self._ttl = ttl_seconds
        self._max_size = max_size

    def get(self, key: str) -> Optional[Set[str]]:
        """
        Get permissions from cache.

        Args:
            key: Cache key

        Returns:
            Set of permissions or None if expired/missing
        """
        with self._lock:
            if key not in self._cache:
                return None

            permissions, timestamp = self._cache[key]

            # Check if expired
            if time.time() - timestamp > self._ttl:
                del self._cache[key]
                return None

            return permissions.copy()

    def set(self, key: str, permissions: Set[str]):
        """
        Set permissions in cache.

        Args:
            key: Cache key
            permissions: Set of permissions
        """
        with self._lock:
            # Evict old entries if cache is full
            if len(self._cache) >= self._max_size:
                # Remove oldest 20% of entries
                sorted_items = sorted(self._cache.items(), key=lambda x: x[1][1])
                to_remove = int(self._max_size * 0.2)
                for key_to_remove, _ in sorted_items[:to_remove]:
                    del self._cache[key_to_remove]

            self._cache[key] = (permissions.copy(), time.time())

    def invalidate(self, key: Optional[str] = None):
        """
        Invalidate cache entry or entire cache.

        Args:
            key: Specific key to invalidate, or None for all
        """
        with self._lock:
            if key is None:
                self._cache.clear()
            else:
                self._cache.pop(key, None)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            now = time.time()
            valid_entries = sum(
                1 for _, timestamp in self._cache.values() if now - timestamp <= self._ttl
            )
            return {
                "total_entries": len(self._cache),
                "valid_entries": valid_entries,
                "expired_entries": len(self._cache) - valid_entries,
                "max_size": self._max_size,
                "ttl_seconds": self._ttl,
            }


class RBACManager:
    """
    Role-Based Access Control manager.

    Manages roles, permissions, and user assignments with caching.
    """

    def __init__(
        self,
        permission_registry: Optional[PermissionRegistry] = None,
        enable_audit: bool = True,
        cache_ttl: int = 300,
    ):
        """
        Initialize RBAC manager.

        Args:
            permission_registry: Permission registry (uses global if None)
            enable_audit: Enable audit logging
            cache_ttl: Cache TTL in seconds
        """
        self.permission_registry = permission_registry or get_permission_registry()
        self.enable_audit = enable_audit
        self._role_cache = RoleCache(ttl_seconds=cache_ttl)
        self._user_role_cache = RoleCache(ttl_seconds=cache_ttl)
        self._lock = threading.RLock()

    async def create_role(
        self,
        name: str,
        display_name: str,
        description: Optional[str] = None,
        scope: str = PermissionScope.GLOBAL,
        is_system: bool = False,
        parent_role: Optional[str] = None,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Role:
        """
        Create a new role.

        Args:
            name: Unique role name
            display_name: Human-readable name
            description: Role description
            scope: Role scope
            is_system: Whether this is a system role
            parent_role: Parent role name for inheritance
            priority: Role priority
            metadata: Additional metadata

        Returns:
            Created role

        Raises:
            ValueError: If role already exists
        """
        # Check if role exists
        existing = await Role.objects.filter(name=name).first()
        if existing:
            raise ValueError(f"Role '{name}' already exists")

        # Get parent role if specified
        parent = None
        if parent_role:
            parent = await Role.objects.filter(name=parent_role).first()
            if not parent:
                raise ValueError(f"Parent role '{parent_role}' not found")

        # Create role
        role = await Role.objects.create(
            name=name,
            display_name=display_name,
            description=description,
            scope=scope,
            is_system=is_system,
            parent_id=parent.id if parent else None,
            priority=priority,
            is_active=True,
            metadata=metadata or {},
        )

        # Invalidate cache
        self._role_cache.invalidate()

        return role

    async def get_role(self, role_name: str) -> Optional[Role]:
        """
        Get role by name.

        Args:
            role_name: Role name

        Returns:
            Role or None
        """
        return await Role.objects.filter(name=role_name, is_active=True).first()

    async def delete_role(self, role_name: str) -> bool:
        """
        Delete role (soft delete by setting is_active=False).

        Args:
            role_name: Role name

        Returns:
            True if deleted
        """
        role = await self.get_role(role_name)
        if not role:
            return False

        # Prevent deletion of system roles
        if role.is_system:
            raise ValueError("Cannot delete system role")

        # Soft delete
        role.is_active = False
        await role.save()

        # Invalidate caches
        self._role_cache.invalidate()
        self._user_role_cache.invalidate()

        return True

    async def assign_permission_to_role(
        self,
        role_name: str,
        permission_name: str,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
    ) -> bool:
        """
        Assign permission to role.

        Args:
            role_name: Role name
            permission_name: Permission name
            granted_by: Who granted this permission
            expires_at: Optional expiration time

        Returns:
            True if assigned successfully
        """
        # Get role
        role = await self.get_role(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found")

        # Get or create permission
        permission = await Permission.objects.filter(name=permission_name).first()
        if not permission:
            # Create from registry
            perm_def = self.permission_registry.get(permission_name)
            if not perm_def:
                raise ValueError(f"Permission '{permission_name}' not found")

            permission = await Permission.objects.create(
                name=perm_def.name,
                resource=perm_def.resource,
                action=perm_def.action,
                scope=perm_def.scope,
                description=perm_def.description,
                is_active=True,
                metadata=perm_def.metadata,
            )

        # Check if already assigned
        existing = await RolePermission.objects.filter(
            role_id=role.id, permission_id=permission.id
        ).first()

        if existing:
            return False

        # Create assignment
        await RolePermission.objects.create(
            role_id=role.id,
            permission_id=permission.id,
            granted_by=granted_by,
            expires_at=expires_at,
            metadata={},
        )

        # Invalidate cache
        self._role_cache.invalidate(role_name)

        return True

    async def revoke_permission_from_role(self, role_name: str, permission_name: str) -> bool:
        """
        Revoke permission from role.

        Args:
            role_name: Role name
            permission_name: Permission name

        Returns:
            True if revoked successfully
        """
        # Get role and permission
        role = await self.get_role(role_name)
        if not role:
            return False

        permission = await Permission.objects.filter(name=permission_name).first()
        if not permission:
            return False

        # Delete assignment
        deleted = await RolePermission.objects.filter(
            role_id=role.id, permission_id=permission.id
        ).delete()

        if deleted > 0:
            # Invalidate cache
            self._role_cache.invalidate(role_name)
            return True

        return False

    async def get_role_permissions(
        self, role_name: str, include_inherited: bool = True
    ) -> Set[str]:
        """
        Get all permissions for a role.

        Args:
            role_name: Role name
            include_inherited: Include permissions from parent roles

        Returns:
            Set of permission names
        """
        # Check cache
        cache_key = f"{role_name}:inherited={include_inherited}"
        cached = self._role_cache.get(cache_key)
        if cached is not None:
            return cached

        # Get role
        role = await self.get_role(role_name)
        if not role:
            return set()

        # Get direct permissions
        role_perms = (
            await RolePermission.objects.filter(role_id=role.id)
            .prefetch_related("permission_id")
            .all()
        )

        permissions = set()
        now = datetime.utcnow()

        for rp in role_perms:
            # Check expiration
            if rp.expires_at and rp.expires_at < now:
                continue

            perm = rp.permission_id
            if perm and perm.is_active:
                permissions.add(perm.name)

        # Include inherited permissions from parent roles
        if include_inherited and role.parent_id:
            parent_role = await Role.objects.get(id=role.parent_id)
            if parent_role:
                parent_perms = await self.get_role_permissions(
                    parent_role.name, include_inherited=True
                )
                permissions.update(parent_perms)

        # Cache result
        self._role_cache.set(cache_key, permissions)

        return permissions

    async def assign_role_to_user(
        self,
        user_id: str,
        role_name: str,
        scope: str = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Assign role to user.

        Args:
            user_id: User identifier
            role_name: Role name
            scope: Assignment scope
            scope_id: Specific scope identifier
            granted_by: Who granted this role
            expires_at: Optional expiration time
            metadata: Additional metadata

        Returns:
            True if assigned successfully
        """
        # Get role
        role = await self.get_role(role_name)
        if not role:
            raise ValueError(f"Role '{role_name}' not found")

        # Check if already assigned
        existing = await UserRole.objects.filter(
            user_id=user_id, role_id=role.id, scope=scope, scope_id=scope_id or ""
        ).first()

        if existing:
            # Update if inactive
            if not existing.is_active:
                existing.is_active = True
                existing.granted_by = granted_by
                existing.granted_at = datetime.utcnow()
                existing.expires_at = expires_at
                existing.metadata = metadata or {}
                await existing.save()
                self._user_role_cache.invalidate()
                return True
            return False

        # Create assignment
        await UserRole.objects.create(
            user_id=user_id,
            role_id=role.id,
            scope=scope,
            scope_id=scope_id,
            is_active=True,
            granted_by=granted_by,
            expires_at=expires_at,
            metadata=metadata or {},
        )

        # Invalidate cache
        self._user_role_cache.invalidate()

        return True

    async def revoke_role_from_user(
        self,
        user_id: str,
        role_name: str,
        scope: str = PermissionScope.GLOBAL,
        scope_id: Optional[str] = None,
    ) -> bool:
        """
        Revoke role from user.

        Args:
            user_id: User identifier
            role_name: Role name
            scope: Assignment scope
            scope_id: Specific scope identifier

        Returns:
            True if revoked successfully
        """
        # Get role
        role = await self.get_role(role_name)
        if not role:
            return False

        # Update assignment to inactive
        updated = await UserRole.objects.filter(
            user_id=user_id, role_id=role.id, scope=scope, scope_id=scope_id or ""
        ).update(is_active=False)

        if updated > 0:
            self._user_role_cache.invalidate()
            return True

        return False

    async def get_user_roles(
        self, user_id: str, scope: Optional[str] = None, scope_id: Optional[str] = None
    ) -> List[Role]:
        """
        Get all roles assigned to user.

        Args:
            user_id: User identifier
            scope: Filter by scope
            scope_id: Filter by scope ID

        Returns:
            List of roles
        """
        # Build query
        query = UserRole.objects.filter(user_id=user_id, is_active=True)

        if scope:
            query = query.filter(scope=scope)

        if scope_id:
            query = query.filter(scope_id=scope_id)

        # Get user roles
        user_roles = await query.prefetch_related("role_id").all()

        # Filter expired roles
        now = datetime.utcnow()
        roles = []

        for ur in user_roles:
            if ur.expires_at and ur.expires_at < now:
                continue

            role = ur.role_id
            if role and role.is_active:
                roles.append(role)

        return roles

    async def get_user_permissions(
        self, user_id: str, scope: Optional[str] = None, scope_id: Optional[str] = None
    ) -> Set[str]:
        """
        Get all permissions for user (from assigned roles).

        Args:
            user_id: User identifier
            scope: Filter by scope
            scope_id: Filter by scope ID

        Returns:
            Set of permission names
        """
        # Check cache
        cache_key = f"user:{user_id}:scope={scope}:id={scope_id}"
        cached = self._user_role_cache.get(cache_key)
        if cached is not None:
            return cached

        # Get user roles
        roles = await self.get_user_roles(user_id, scope, scope_id)

        # Collect all permissions from roles
        permissions = set()
        for role in roles:
            role_perms = await self.get_role_permissions(role.name)
            permissions.update(role_perms)

        # Cache result
        self._user_role_cache.set(cache_key, permissions)

        return permissions

    async def check_permission(
        self,
        user_id: str,
        permission: str,
        scope: Optional[str] = None,
        scope_id: Optional[str] = None,
        log_audit: bool = True,
    ) -> bool:
        """
        Check if user has permission.

        Args:
            user_id: User identifier
            permission: Permission to check
            scope: Permission scope
            scope_id: Scope identifier
            log_audit: Log audit trail

        Returns:
            True if user has permission
        """
        # Get user permissions
        user_perms = await self.get_user_permissions(user_id, scope, scope_id)

        # Use permission registry to check (supports wildcards)
        has_permission = self.permission_registry.check_permission(user_perms, permission)

        # Log audit
        if self.enable_audit and log_audit:
            await self._log_audit(
                user_id=user_id,
                resource=permission.split(":")[0] if ":" in permission else permission,
                action=permission.split(":")[1] if ":" in permission else "access",
                decision=AuditDecision.ALLOW if has_permission else AuditDecision.DENY,
                decision_reason=f"RBAC check: {'granted' if has_permission else 'denied'}",
                context={
                    "scope": scope,
                    "scope_id": scope_id,
                    "user_permissions": list(user_perms)[:10],  # First 10 for brevity
                },
            )

        return has_permission

    async def check_any_permission(
        self,
        user_id: str,
        permissions: List[str],
        scope: Optional[str] = None,
        scope_id: Optional[str] = None,
    ) -> bool:
        """
        Check if user has any of the permissions.

        Args:
            user_id: User identifier
            permissions: List of permissions
            scope: Permission scope
            scope_id: Scope identifier

        Returns:
            True if user has any permission
        """
        user_perms = await self.get_user_permissions(user_id, scope, scope_id)
        return self.permission_registry.check_any_permission(user_perms, set(permissions))

    async def check_all_permissions(
        self,
        user_id: str,
        permissions: List[str],
        scope: Optional[str] = None,
        scope_id: Optional[str] = None,
    ) -> bool:
        """
        Check if user has all permissions.

        Args:
            user_id: User identifier
            permissions: List of permissions
            scope: Permission scope
            scope_id: Scope identifier

        Returns:
            True if user has all permissions
        """
        user_perms = await self.get_user_permissions(user_id, scope, scope_id)
        return self.permission_registry.check_all_permissions(user_perms, set(permissions))

    async def _log_audit(
        self,
        user_id: str,
        resource: str,
        action: str,
        decision: AuditDecision,
        decision_reason: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Log authorization decision to audit trail."""
        try:
            await PermissionAuditLog.objects.create(
                user_id=user_id,
                resource=resource,
                action=action,
                decision=decision.value,
                decision_reason=decision_reason,
                context=context or {},
            )
        except Exception:
            # Don't fail authorization if audit logging fails
            pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "role_cache": self._role_cache.get_stats(),
            "user_role_cache": self._user_role_cache.get_stats(),
        }

    def clear_cache(self):
        """Clear all caches."""
        self._role_cache.invalidate()
        self._user_role_cache.invalidate()


async def initialize_default_roles(rbac_manager: RBACManager):
    """
    Initialize default system roles.

    Creates admin, user, and guest roles with standard permissions.
    """
    # Admin role - full access
    try:
        admin_role = await rbac_manager.create_role(
            name="admin",
            display_name="Administrator",
            description="Full system access",
            is_system=True,
            priority=100,
        )
        await rbac_manager.assign_permission_to_role("admin", "admin:*")
    except ValueError:
        pass  # Role already exists

    # User role - standard user permissions
    try:
        user_role = await rbac_manager.create_role(
            name="user",
            display_name="User",
            description="Standard user access",
            is_system=True,
            priority=50,
        )
        await rbac_manager.assign_permission_to_role("user", "users:read")
    except ValueError:
        pass

    # Guest role - minimal permissions
    try:
        guest_role = await rbac_manager.create_role(
            name="guest",
            display_name="Guest",
            description="Guest access (read-only)",
            is_system=True,
            priority=10,
        )
    except ValueError:
        pass


__all__ = [
    "RoleCache",
    "RBACManager",
    "initialize_default_roles",
]
