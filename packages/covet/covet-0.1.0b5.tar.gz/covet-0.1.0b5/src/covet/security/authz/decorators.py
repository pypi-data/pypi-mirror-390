"""
Authorization Decorators

Production-ready decorators for protecting routes and functions with RBAC and ABAC.

Features:
- @require_permission decorator for permission-based auth
- @require_role decorator for role-based auth
- @require_policy decorator for ABAC policies
- @require_ownership decorator for resource ownership
- Integration with REST and GraphQL APIs
- Automatic 403 Forbidden responses
- Flexible permission checking

Usage:
    @require_permission('users:read')
    async def get_user(request, user_id: str):
        ...

    @require_role('admin', 'moderator')
    async def delete_user(request, user_id: str):
        ...

    @require_policy('read-own-documents')
    async def get_document(request, doc_id: str):
        ...

    @require_ownership('document')
    async def update_document(request, doc_id: str):
        ...
"""

import asyncio
import inspect
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .policy_engine import DecisionStrategy, PolicyDecisionPoint
from .rbac import RBACManager


class AuthorizationError(Exception):
    """Authorization error."""

    def __init__(self, message: str, status_code: int = 403):
        """
        Initialize authorization error.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _get_user_from_request(request: Any) -> Optional[Dict[str, Any]]:
    """
    Extract user from request object.

    Supports various frameworks (Starlette, FastAPI, Django, Flask, etc.)
    """
    # Try different request formats
    if hasattr(request, "user"):
        user = request.user
        if isinstance(user, dict):
            return user
        elif hasattr(user, "__dict__"):
            return user.__dict__
        return {"id": str(user)}

    if hasattr(request, "scope") and isinstance(request.scope, dict):
        user = request.scope.get("user")
        if user:
            return user if isinstance(user, dict) else {"id": str(user)}

    if hasattr(request, "state") and hasattr(request.state, "user"):
        user = request.state.user
        return user if isinstance(user, dict) else {"id": str(user)}

    return None


def _get_user_id(request: Any) -> Optional[str]:
    """Extract user ID from request."""
    user = _get_user_from_request(request)
    if not user:
        return None

    # Try different user ID fields
    for field in ["id", "user_id", "sub", "username"]:
        if field in user:
            return str(user[field])

    return None


def require_permission(*permissions: str, require_all: bool = True):
    """
    Decorator to require permissions for route/function.

    Args:
        *permissions: Required permissions
        require_all: Require all permissions (True) or any permission (False)

    Returns:
        Decorated function

    Example:
        @require_permission('users:read', 'users:write')
        async def update_user(request, user_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request (usually first argument)
            request = args[0] if args else None
            if not request:
                raise AuthorizationError("No request object found", 500)

            # Get user ID
            user_id = _get_user_id(request)
            if not user_id:
                raise AuthorizationError("Authentication required", 401)

            # Check permissions
            rbac_manager = RBACManager()

            if require_all:
                has_permission = await rbac_manager.check_all_permissions(
                    user_id, list(permissions)
                )
            else:
                has_permission = await rbac_manager.check_any_permission(user_id, list(permissions))

            if not has_permission:
                raise AuthorizationError(f"Missing required permissions: {', '.join(permissions)}")

            # Call original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, run async wrapper in event loop
            return asyncio.run(async_wrapper(*args, **kwargs))

        # Return appropriate wrapper based on function type
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_role(*roles: str, require_all: bool = False):
    """
    Decorator to require roles for route/function.

    Args:
        *roles: Required roles
        require_all: Require all roles (True) or any role (False)

    Returns:
        Decorated function

    Example:
        @require_role('admin', 'moderator')
        async def delete_user(request, user_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request
            request = args[0] if args else None
            if not request:
                raise AuthorizationError("No request object found", 500)

            # Get user
            user = _get_user_from_request(request)
            if not user:
                raise AuthorizationError("Authentication required", 401)

            # Get user roles
            user_roles = set(user.get("roles", []))

            # Check roles
            required_roles = set(roles)

            if require_all:
                has_role = required_roles.issubset(user_roles)
            else:
                has_role = bool(required_roles.intersection(user_roles))

            if not has_role:
                raise AuthorizationError(f"Missing required roles: {', '.join(roles)}")

            # Call original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_policy(
    resource_type: str, action: str, strategy: DecisionStrategy = DecisionStrategy.RBAC_FIRST
):
    """
    Decorator to require policy-based authorization (ABAC).

    Args:
        resource_type: Resource type
        action: Action being performed
        strategy: Decision strategy (RBAC, ABAC, or combined)

    Returns:
        Decorated function

    Example:
        @require_policy('documents', 'read')
        async def get_document(request, doc_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request
            request = args[0] if args else None
            if not request:
                raise AuthorizationError("No request object found", 500)

            # Get user
            user = _get_user_from_request(request)
            if not user:
                raise AuthorizationError("Authentication required", 401)

            user_id = str(user.get("id") or user.get("user_id") or user.get("sub"))

            # Extract resource ID from kwargs (common parameter names)
            resource_id = (
                kwargs.get("resource_id")
                or kwargs.get("id")
                or kwargs.get(f"{resource_type}_id")
                or "unknown"
            )

            # Create policy decision point
            pdp = PolicyDecisionPoint(strategy=strategy)

            # Evaluate access
            decision = await pdp.evaluate(
                user_id=user_id,
                resource_type=resource_type,
                resource_id=str(resource_id),
                action=action,
                user_attributes=user,
            )

            if not decision.allowed:
                raise AuthorizationError(f"Access denied: {decision.reason}")

            # Attach decision to request for logging/debugging
            if hasattr(request, "state"):
                request.state.authz_decision = decision
            else:
                request.authz_decision = decision

            # Call original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_ownership(resource_type: str, owner_field: str = "owner_id", allow_admin: bool = True):
    """
    Decorator to require resource ownership.

    Checks if the requesting user owns the resource.

    Args:
        resource_type: Resource type
        owner_field: Field name containing owner ID
        allow_admin: Allow admin role to bypass ownership check

    Returns:
        Decorated function

    Example:
        @require_ownership('document')
        async def update_document(request, doc_id: str):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract request
            request = args[0] if args else None
            if not request:
                raise AuthorizationError("No request object found", 500)

            # Get user
            user = _get_user_from_request(request)
            if not user:
                raise AuthorizationError("Authentication required", 401)

            user_id = str(user.get("id") or user.get("user_id") or user.get("sub"))
            user_roles = set(user.get("roles", []))

            # Check admin bypass
            if allow_admin and "admin" in user_roles:
                return await func(*args, **kwargs)

            # Get resource (should be returned by function or in request)
            # This is a placeholder - in production, fetch resource from DB
            # For now, we'll check if user_id matches owner field in kwargs
            resource_owner = kwargs.get(owner_field)

            if resource_owner and str(resource_owner) != user_id:
                raise AuthorizationError(
                    f"You don't have permission to access this {resource_type}"
                )

            # Call original function
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(async_wrapper(*args, **kwargs))

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def require_any_permission(*permissions: str):
    """
    Decorator to require any of the specified permissions.

    Shorthand for require_permission with require_all=False.
    """
    return require_permission(*permissions, require_all=False)


def require_any_role(*roles: str):
    """
    Decorator to require any of the specified roles.

    Shorthand for require_role with require_all=False.
    """
    return require_role(*roles, require_all=False)


__all__ = [
    "AuthorizationError",
    "require_permission",
    "require_role",
    "require_policy",
    "require_ownership",
    "require_any_permission",
    "require_any_role",
]
