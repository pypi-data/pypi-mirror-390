"""
GraphQL Authentication and Authorization

Integrates JWT authentication with GraphQL resolvers.
Provides decorators and utilities for securing GraphQL operations.
"""

import sys
from functools import wraps
from typing import Any, Callable, List, Optional

import jwt
import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info

from covet.security.jwt_auth import JWTAuthenticator, TokenType

sys.path.append("/Users/vipin/Downloads/NeutrinoPy/src")


class AuthContext:
    """
    Authentication context for GraphQL.

    Attached to execution context and provides user info.
    """

    def __init__(self, user: Optional[dict] = None, token: Optional[str] = None):
        """
        Initialize auth context.

        Args:
            user: User info dict
            token: JWT token
        """
        self.user = user
        self.token = token
        self.is_authenticated = user is not None

    def get_user_id(self) -> Optional[str]:
        """Get current user ID."""
        if self.user:
            return self.user.get("id")
        return None

    def get_roles(self) -> List[str]:
        """Get current user roles."""
        if self.user:
            return self.user.get("roles", [])
        return []

    def get_permissions(self) -> List[str]:
        """Get current user permissions."""
        if self.user:
            return self.user.get("permissions", [])
        return []

    def has_role(self, role: str) -> bool:
        """Check if user has role."""
        return role in self.get_roles()

    def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        return permission in self.get_permissions()


class GraphQLAuth:
    """
    GraphQL authentication system.

    Handles JWT verification and user context creation.
    """

    def __init__(self, authenticator: JWTAuthenticator):
        """
        Initialize GraphQL auth.

        Args:
            authenticator: JWT authenticator instance
        """
        self.authenticator = authenticator

    def extract_token_from_headers(self, headers: dict) -> Optional[str]:
        """
        Extract JWT from Authorization header.

        Args:
            headers: Request headers

        Returns:
            JWT token or None
        """
        auth_header = headers.get("authorization", "")

        if not auth_header:
            return None

        # Parse "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    async def create_context_from_request(self, request: Any) -> AuthContext:
        """
        Create auth context from HTTP request.

        Args:
            request: HTTP request object

        Returns:
            Auth context
        """
        # Extract headers (format depends on ASGI server)
        headers = {}
        if hasattr(request, "headers"):
            headers = request.headers
        elif hasattr(request, "scope"):
            # ASGI format
            for name, value in request.scope.get("headers", []):
                headers[name.decode("utf-8").lower()] = value.decode("utf-8")

        # Extract and verify token
        token = self.extract_token_from_headers(headers)
        if not token:
            return AuthContext()

        try:
            # Verify token
            claims = self.authenticator.verify_token(token, token_type=TokenType.ACCESS)

            # Create user dict from claims
            user = {
                "id": claims["sub"],
                "roles": claims.get("roles", []),
                "permissions": claims.get("permissions", []),
                "scopes": claims.get("scopes", []),
                "claims": claims,
            }

            return AuthContext(user=user, token=token)

        except (jwt.InvalidTokenError, jwt.ExpiredSignatureError, ValueError):
            # Invalid token
            return AuthContext()


# Strawberry permission classes
class IsAuthenticated(BasePermission):
    """Permission that requires authentication."""

    message = "User must be authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is authenticated."""
        context = info.context
        if hasattr(context, "is_authenticated"):
            return context.is_authenticated
        if hasattr(context, "user"):
            return context.user is not None
        return False


class HasRole(BasePermission):
    """Permission that requires specific role."""

    def __init__(self, role: str):
        """
        Initialize permission.

        Args:
            role: Required role
        """
        self.role = role
        self.message = f"User must have role: {role}"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has role."""
        context = info.context
        if hasattr(context, "has_role"):
            return context.has_role(self.role)
        return False


class HasPermission(BasePermission):
    """Permission that requires specific permission."""

    def __init__(self, permission: str):
        """
        Initialize permission.

        Args:
            permission: Required permission
        """
        self.permission = permission
        self.message = f"User must have permission: {permission}"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has permission."""
        context = info.context
        if hasattr(context, "has_permission"):
            return context.has_permission(self.permission)
        return False


class HasAnyRole(BasePermission):
    """Permission that requires any of the specified roles."""

    def __init__(self, roles: List[str]):
        """
        Initialize permission.

        Args:
            roles: List of acceptable roles
        """
        self.roles = roles
        self.message = f"User must have one of: {', '.join(roles)}"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has any role."""
        context = info.context
        if hasattr(context, "get_roles"):
            user_roles = set(context.get_roles())
            return bool(user_roles.intersection(self.roles))
        return False


# Decorator functions
def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication.

    Example:
        @strawberry.field
        @require_auth
        async def me(self, info: Info) -> User:
            user_id = info.context.get_user_id()
            return await get_user(user_id)
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Extract info from args
        info = None
        for arg in args:
            if isinstance(arg, Info):
                info = arg
                break

        if info is None:
            raise ValueError("Info object not found in arguments")

        # Check authentication
        context = info.context
        if not hasattr(context, "is_authenticated") or not context.is_authenticated:
            raise PermissionError("Authentication required")

        return await func(*args, **kwargs)

    return wrapper


def require_roles(*roles: str):
    """
    Decorator to require specific roles.

    Example:
        @strawberry.field
        @require_roles('admin', 'moderator')
        async def delete_user(self, id: int, info: Info) -> bool:
            return await delete_user_by_id(id)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract info
            info = None
            for arg in args:
                if isinstance(arg, Info):
                    info = arg
                    break

            if info is None:
                raise ValueError("Info object not found in arguments")

            # Check roles
            context = info.context
            if not hasattr(context, "get_roles"):
                raise PermissionError("User not authenticated")

            user_roles = set(context.get_roles())
            required_roles = set(roles)

            if not user_roles.intersection(required_roles):
                raise PermissionError(f"Requires one of: {', '.join(roles)}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(*permissions: str):
    """
    Decorator to require specific permissions.

    Example:
        @strawberry.field
        @require_permissions('users:write', 'users:delete')
        async def update_user(self, id: int, data: UserInput, info: Info) -> User:
            return await update_user_by_id(id, data)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract info
            info = None
            for arg in args:
                if isinstance(arg, Info):
                    info = arg
                    break

            if info is None:
                raise ValueError("Info object not found in arguments")

            # Check permissions
            context = info.context
            if not hasattr(context, "get_permissions"):
                raise PermissionError("User not authenticated")

            user_permissions = set(context.get_permissions())
            required_permissions = set(permissions)

            if not required_permissions.issubset(user_permissions):
                missing = required_permissions - user_permissions
                raise PermissionError(f"Missing permissions: {', '.join(missing)}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user(info: Info) -> Optional[dict]:
    """
    Get current user from context.

    Args:
        info: Strawberry Info object

    Returns:
        User dict or None
    """
    context = info.context
    if hasattr(context, "user"):
        return context.user
    return None


__all__ = [
    "GraphQLAuth",
    "AuthContext",
    "IsAuthenticated",
    "HasRole",
    "HasPermission",
    "HasAnyRole",
    "require_auth",
    "require_roles",
    "require_permissions",
    "get_current_user",
]
