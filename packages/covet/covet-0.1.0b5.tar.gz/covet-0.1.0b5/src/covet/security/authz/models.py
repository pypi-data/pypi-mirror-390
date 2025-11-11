"""
Authorization Database Models

Production-ready database models for RBAC and ABAC authorization systems.

Models:
- Permission: Individual permission entries
- Role: User roles with permission assignments
- UserRole: Many-to-many relationship between users and roles
- Policy: ABAC policy definitions
- PermissionAuditLog: Audit trail for access decisions

Features:
- Full ORM integration with CovetPy
- Role hierarchy support
- Permission inheritance
- Scoped permissions (global, org, project)
- Policy versioning
- Complete audit trail
- Soft deletes for roles/permissions
"""

import json
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# NOTE: Import from database.orm at end of module to avoid circular dependency
# The circular dependency chain is:
# - database modules import from database.security.sql_validator
# - security.authz.models imports from database.orm
# By deferring the import until after enums, we break the cycle


class PermissionScope(str, Enum):
    """Permission scope levels."""

    GLOBAL = "global"  # System-wide permission
    ORGANIZATION = "organization"  # Organization-level
    PROJECT = "project"  # Project-level
    RESOURCE = "resource"  # Individual resource


class PolicyEffect(str, Enum):
    """Policy decision effect."""

    ALLOW = "allow"
    DENY = "deny"


class PolicyStatus(str, Enum):
    """Policy status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class AuditDecision(str, Enum):
    """Audit log decision."""

    ALLOW = "allow"
    DENY = "deny"
    ERROR = "error"


# Import ORM components after enum definitions to avoid circular imports
from covet.database.orm import (  # noqa: E402
    CASCADE,
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    JSONField,
    ManyToManyField,
    Model,
    TextField,
    UUIDField,
)


class Permission(Model):
    """
    Permission model.

    Represents a single permission that can be assigned to roles or users.

    Attributes:
        name: Unique permission name (e.g., 'users:read', 'posts:write')
        resource: Resource this permission applies to
        action: Action allowed (read, write, delete, etc.)
        scope: Permission scope (global, org, project, resource)
        description: Human-readable description
        is_active: Whether permission is active
        parent_id: Parent permission for inheritance
        metadata: Additional permission metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200, unique=True, db_index=True)
    resource = CharField(max_length=100, db_index=True)
    action = CharField(max_length=50, db_index=True)
    scope = CharField(
        max_length=20, default=PermissionScope.GLOBAL, choices=[s.value for s in PermissionScope]
    )
    description = TextField(null=True, blank=True)
    is_active = BooleanField(default=True, db_index=True)
    parent_id = ForeignKey(
        "self", on_delete=SET_NULL, null=True, blank=True, related_name="children"
    )
    metadata = JSONField(default=dict, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "authz_permissions"
        ordering = ["resource", "action"]
        indexes = [
            ("resource", "action"),
            ("scope", "is_active"),
        ]

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "resource": self.resource,
            "action": self.action,
            "scope": self.scope,
            "description": self.description,
            "is_active": self.is_active,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class Role(Model):
    """
    Role model.

    Represents a role that can be assigned to users with associated permissions.

    Attributes:
        name: Unique role name
        display_name: Human-readable name
        description: Role description
        scope: Role scope (global, org, project)
        is_system: Whether this is a system role (admin, user, guest)
        is_active: Whether role is active
        parent_id: Parent role for hierarchy/inheritance
        priority: Role priority (higher = more privileges)
        metadata: Additional role metadata
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=100, unique=True, db_index=True)
    display_name = CharField(max_length=200)
    description = TextField(null=True, blank=True)
    scope = CharField(
        max_length=20, default=PermissionScope.GLOBAL, choices=[s.value for s in PermissionScope]
    )
    is_system = BooleanField(default=False, db_index=True)
    is_active = BooleanField(default=True, db_index=True)
    parent_id = ForeignKey(
        "self", on_delete=SET_NULL, null=True, blank=True, related_name="child_roles"
    )
    priority = IntegerField(default=0, db_index=True)
    permissions = ManyToManyField(Permission, related_name="roles", through="RolePermission")
    metadata = JSONField(default=dict, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = "authz_roles"
        ordering = ["-priority", "name"]
        indexes = [
            ("scope", "is_active"),
            ("is_system", "is_active"),
        ]

    def __str__(self) -> str:
        return self.display_name or self.name

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "scope": self.scope,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "priority": self.priority,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class RolePermission(Model):
    """
    Role-Permission many-to-many relationship.

    Through model for roles and permissions with additional metadata.
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    role_id = ForeignKey(Role, on_delete=CASCADE, related_name="role_permissions")
    permission_id = ForeignKey(Permission, on_delete=CASCADE, related_name="permission_roles")
    granted_at = DateTimeField(auto_now_add=True)
    granted_by = CharField(max_length=200, null=True, blank=True)
    expires_at = DateTimeField(null=True, blank=True)
    metadata = JSONField(default=dict, null=True)

    class Meta:
        db_table = "authz_role_permissions"
        unique_together = [("role_id", "permission_id")]
        indexes = [
            ("role_id", "permission_id"),
            ("expires_at",),
        ]

    def __str__(self) -> str:
        return f"{self.role_id} -> {self.permission_id}"


class UserRole(Model):
    """
    User-Role assignment model.

    Tracks which roles are assigned to which users with scope information.

    Attributes:
        user_id: User identifier
        role_id: Assigned role
        scope: Assignment scope
        scope_id: Specific scope identifier (org_id, project_id, etc.)
        is_active: Whether assignment is active
        granted_by: Who granted this role
        granted_at: When role was granted
        expires_at: Optional expiration time
        metadata: Additional assignment metadata
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = CharField(max_length=200, db_index=True)
    role_id = ForeignKey(Role, on_delete=CASCADE, related_name="user_assignments")
    scope = CharField(
        max_length=20, default=PermissionScope.GLOBAL, choices=[s.value for s in PermissionScope]
    )
    scope_id = CharField(max_length=200, null=True, blank=True, db_index=True)
    is_active = BooleanField(default=True, db_index=True)
    granted_by = CharField(max_length=200, null=True, blank=True)
    granted_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField(null=True, blank=True, db_index=True)
    metadata = JSONField(default=dict, null=True)

    class Meta:
        db_table = "authz_user_roles"
        unique_together = [("user_id", "role_id", "scope", "scope_id")]
        indexes = [
            ("user_id", "is_active"),
            ("role_id", "is_active"),
            ("scope", "scope_id"),
            ("expires_at",),
        ]

    def __str__(self) -> str:
        return f"User {self.user_id} -> {self.role_id}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "role_id": str(self.role_id),
            "scope": self.scope,
            "scope_id": self.scope_id,
            "is_active": self.is_active,
            "granted_by": self.granted_by,
            "granted_at": self.granted_at.isoformat() if self.granted_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }


class Policy(Model):
    """
    ABAC Policy model.

    Defines attribute-based access control policies with complex rules.

    Attributes:
        name: Unique policy name
        description: Policy description
        effect: Allow or deny
        status: Active, inactive, or draft
        version: Policy version number
        priority: Evaluation priority (higher first)
        rules: JSON policy rules
        subjects: Subject attribute conditions
        resources: Resource attribute conditions
        actions: Action conditions
        environment: Environment conditions
        created_by: Policy creator
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    name = CharField(max_length=200, unique=True, db_index=True)
    description = TextField(null=True, blank=True)
    effect = CharField(
        max_length=10, default=PolicyEffect.ALLOW, choices=[e.value for e in PolicyEffect]
    )
    status = CharField(
        max_length=10,
        default=PolicyStatus.ACTIVE,
        choices=[s.value for s in PolicyStatus],
        db_index=True,
    )
    version = IntegerField(default=1)
    priority = IntegerField(default=0, db_index=True)
    rules = JSONField(default=dict)
    subjects = JSONField(default=dict, null=True)
    resources = JSONField(default=dict, null=True)
    actions = JSONField(default=list, null=True)
    environment = JSONField(default=dict, null=True)
    created_by = CharField(max_length=200, null=True, blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    metadata = JSONField(default=dict, null=True)

    class Meta:
        db_table = "authz_policies"
        ordering = ["-priority", "name"]
        indexes = [
            ("status", "priority"),
            ("effect", "status"),
        ]

    def __str__(self) -> str:
        return f"{self.name} (v{self.version})"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "effect": self.effect,
            "status": self.status,
            "version": self.version,
            "priority": self.priority,
            "rules": self.rules,
            "subjects": self.subjects,
            "resources": self.resources,
            "actions": self.actions,
            "environment": self.environment,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }


class PermissionAuditLog(Model):
    """
    Permission audit log.

    Tracks all authorization decisions for security auditing.

    Attributes:
        user_id: User who attempted action
        resource: Resource accessed
        action: Action attempted
        decision: Allow, deny, or error
        decision_reason: Why decision was made
        policy_id: Policy that made decision (if ABAC)
        role_ids: Roles involved in decision
        permission_ids: Permissions checked
        context: Request context (IP, time, etc.)
        created_at: Timestamp
    """

    id = UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = CharField(max_length=200, db_index=True)
    resource = CharField(max_length=200, db_index=True)
    action = CharField(max_length=100, db_index=True)
    decision = CharField(max_length=10, choices=[d.value for d in AuditDecision], db_index=True)
    decision_reason = TextField(null=True, blank=True)
    policy_id = UUIDField(null=True, blank=True, db_index=True)
    role_ids = JSONField(default=list, null=True)
    permission_ids = JSONField(default=list, null=True)
    context = JSONField(default=dict, null=True)
    created_at = DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "authz_audit_logs"
        ordering = ["-created_at"]
        indexes = [
            ("user_id", "created_at"),
            ("resource", "action", "decision"),
            ("decision", "created_at"),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} -> {self.resource}:{self.action} = {self.decision}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "user_id": self.user_id,
            "resource": self.resource,
            "action": self.action,
            "decision": self.decision,
            "decision_reason": self.decision_reason,
            "policy_id": str(self.policy_id) if self.policy_id else None,
            "role_ids": self.role_ids,
            "permission_ids": self.permission_ids,
            "context": self.context,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = [
    # Enums
    "PermissionScope",
    "PolicyEffect",
    "PolicyStatus",
    "AuditDecision",
    # Models
    "Permission",
    "Role",
    "RolePermission",
    "UserRole",
    "Policy",
    "PermissionAuditLog",
]
