"""
Authentication Decorators

Flask-like decorators for protecting routes with authentication.
Provides simple, intuitive API for securing endpoints.

Features:
- @login_required - Require valid JWT token
- @roles_required - Require specific roles
- @permission_required - Require specific permissions
- Automatic token extraction from headers
- User context injection into request
- Configurable error responses

Usage:
    from covet.auth import login_required, roles_required

    @app.route('/protected')
    @login_required
    async def protected(request):
        user = request.user  # Automatically set
        return {'user': user}

    @app.route('/admin')
    @roles_required('admin')
    async def admin_only(request):
        return {'message': 'Admin access granted'}
"""

import functools
from typing import Any, Callable, List, Optional, Union

from covet.core.http import Request, Response

from .exceptions import (
    AuthException,
    PermissionDeniedError,
    RoleRequiredError,
    TokenExpiredError,
    TokenInvalidError,
)
from .jwt import JWTAuth


# Global JWT auth instance for decorators
_jwt_auth: Optional[JWTAuth] = None


def configure_auth_decorators(jwt_auth: JWTAuth):
    """
    Configure JWT auth instance for decorators.

    Args:
        jwt_auth: Configured JWTAuth instance

    Example:
        >>> from covet.auth import JWTAuth, configure_auth_decorators
        >>> jwt = JWTAuth(secret_key='your-key')
        >>> configure_auth_decorators(jwt)
    """
    global _jwt_auth
    _jwt_auth = jwt_auth


def get_auth_instance() -> JWTAuth:
    """Get or create default JWT auth instance."""
    global _jwt_auth
    if _jwt_auth is None:
        # Create default instance (will warn about auto-generated key)
        _jwt_auth = JWTAuth()
    return _jwt_auth


def extract_token_from_request(request: Request) -> Optional[str]:
    """
    Extract JWT token from request.

    Checks multiple locations in order:
    1. Authorization header (Bearer token)
    2. X-API-Token header
    3. Query parameter 'token'
    4. Cookie 'access_token'

    Args:
        request: HTTP request object

    Returns:
        Token string if found, None otherwise

    Security Note:
        Bearer token in Authorization header is most secure.
        Avoid query parameters for sensitive tokens (logged in URLs).
    """
    # Check Authorization header (preferred)
    auth_header = request.headers.get('authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:].strip()

    # Check X-API-Token header
    api_token = request.headers.get('x-api-token', '')
    if api_token:
        return api_token.strip()

    # Check query parameter (least secure, but convenient for some use cases)
    token = request.args.get('token', '')
    if token:
        return token

    # Check cookie
    if hasattr(request, 'cookies'):
        cookie_token = request.cookies.get('access_token', '')
        if cookie_token:
            return cookie_token

    return None


def inject_user_into_request(request: Request, token_payload: dict):
    """
    Inject user information into request object.

    Args:
        request: HTTP request
        token_payload: Decoded JWT payload

    Sets:
        request.user: User info dict
        request.user_id: User ID
        request.username: Username (if available)
        request.roles: User roles list (if available)
    """
    request.user = token_payload
    request.user_id = token_payload.get('sub', '')
    request.username = token_payload.get('username', '')
    request.roles = token_payload.get('roles', [])


def login_required(func: Callable = None, *, optional: bool = False):
    """
    Decorator to require valid JWT token for route access.

    Args:
        func: Function to decorate
        optional: If True, allow access without token but inject user if present

    Raises:
        TokenInvalidError: Invalid or missing token
        TokenExpiredError: Expired token

    Example:
        >>> @app.route('/protected')
        ... @login_required
        ... async def protected(request):
        ...     return {'user_id': request.user_id}

        >>> @app.route('/optional-auth')
        ... @login_required(optional=True)
        ... async def optional_auth(request):
        ...     if request.user_id:
        ...         return {'message': f'Hello {request.username}'}
        ...     return {'message': 'Hello guest'}
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        async def async_wrapper(request: Request, *args, **kwargs):
            jwt_auth = get_auth_instance()

            # Extract token
            token = extract_token_from_request(request)

            if not token:
                if optional:
                    # No token, but optional auth - allow access
                    request.user = None
                    request.user_id = None
                    request.username = None
                    request.roles = []
                else:
                    # No token and required - deny access
                    return Response(
                        content={'error': 'Authentication required', 'code': 'missing_token'},
                        status_code=401,
                        headers={'WWW-Authenticate': 'Bearer'}
                    )
            else:
                try:
                    # Verify token
                    payload = jwt_auth.verify_token(token)

                    # Inject user info into request
                    inject_user_into_request(request, payload)

                except TokenExpiredError:
                    if optional:
                        request.user = None
                        request.user_id = None
                    else:
                        return Response(
                            content={
                                'error': 'Token has expired',
                                'code': 'token_expired'
                            },
                            status_code=401,
                            headers={'WWW-Authenticate': 'Bearer error="invalid_token"'}
                        )

                except TokenInvalidError as e:
                    if optional:
                        request.user = None
                        request.user_id = None
                    else:
                        return Response(
                            content={
                                'error': str(e),
                                'code': 'invalid_token'
                            },
                            status_code=401,
                            headers={'WWW-Authenticate': 'Bearer error="invalid_token"'}
                        )

            # Call wrapped function
            return await f(request, *args, **kwargs)

        @functools.wraps(f)
        def sync_wrapper(request: Request, *args, **kwargs):
            """Synchronous version of wrapper for sync functions."""
            jwt_auth = get_auth_instance()

            # Extract token
            token = extract_token_from_request(request)

            if not token:
                if optional:
                    request.user = None
                    request.user_id = None
                    request.username = None
                    request.roles = []
                else:
                    return Response(
                        content={'error': 'Authentication required', 'code': 'missing_token'},
                        status_code=401,
                        headers={'WWW-Authenticate': 'Bearer'}
                    )
            else:
                try:
                    payload = jwt_auth.verify_token(token)
                    inject_user_into_request(request, payload)

                except TokenExpiredError:
                    if optional:
                        request.user = None
                        request.user_id = None
                    else:
                        return Response(
                            content={'error': 'Token has expired', 'code': 'token_expired'},
                            status_code=401
                        )

                except TokenInvalidError as e:
                    if optional:
                        request.user = None
                        request.user_id = None
                    else:
                        return Response(
                            content={'error': str(e), 'code': 'invalid_token'},
                            status_code=401
                        )

            return f(request, *args, **kwargs)

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(f):
            return async_wrapper
        else:
            return sync_wrapper

    # Support both @login_required and @login_required()
    if func is None:
        return decorator
    else:
        return decorator(func)


def roles_required(*required_roles: str):
    """
    Decorator to require specific roles for route access.

    Args:
        *required_roles: Role names required (user must have ALL roles)

    Raises:
        RoleRequiredError: User missing required role

    Example:
        >>> @app.route('/admin')
        ... @login_required
        ... @roles_required('admin')
        ... async def admin_only(request):
        ...     return {'message': 'Admin access'}

        >>> @app.route('/moderator')
        ... @roles_required('moderator', 'verified')
        ... async def moderator_only(request):
        ...     return {'message': 'Moderator with verified status'}
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        async def async_wrapper(request: Request, *args, **kwargs):
            # Ensure user is authenticated
            if not hasattr(request, 'user') or not request.user:
                return Response(
                    content={'error': 'Authentication required'},
                    status_code=401
                )

            # Get user roles
            user_roles = set(request.roles or [])

            # Check if user has all required roles
            missing_roles = set(required_roles) - user_roles

            if missing_roles:
                return Response(
                    content={
                        'error': 'Insufficient permissions',
                        'code': 'missing_roles',
                        'required_roles': list(required_roles),
                        'missing_roles': list(missing_roles)
                    },
                    status_code=403
                )

            # User has required roles
            return await f(request, *args, **kwargs)

        @functools.wraps(f)
        def sync_wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return Response(
                    content={'error': 'Authentication required'},
                    status_code=401
                )

            user_roles = set(request.roles or [])
            missing_roles = set(required_roles) - user_roles

            if missing_roles:
                return Response(
                    content={
                        'error': 'Insufficient permissions',
                        'code': 'missing_roles',
                        'required_roles': list(required_roles),
                        'missing_roles': list(missing_roles)
                    },
                    status_code=403
                )

            return f(request, *args, **kwargs)

        import inspect
        if inspect.iscoroutinefunction(f):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def permission_required(*required_permissions: str, require_all: bool = True):
    """
    Decorator to require specific permissions for route access.

    Args:
        *required_permissions: Permission names required
        require_all: If True, user must have ALL permissions. If False, ANY permission.

    Raises:
        PermissionDeniedError: User missing required permissions

    Example:
        >>> @app.route('/users/delete')
        ... @permission_required('users.delete')
        ... async def delete_user(request):
        ...     return {'message': 'User deleted'}

        >>> @app.route('/content/moderate')
        ... @permission_required('content.edit', 'content.delete', require_all=False)
        ... async def moderate_content(request):
        ...     return {'message': 'Can edit OR delete content'}
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        async def async_wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return Response(
                    content={'error': 'Authentication required'},
                    status_code=401
                )

            # Get user permissions from token
            user_permissions = set(request.user.get('permissions', []))

            if require_all:
                # Check if user has ALL required permissions
                missing_permissions = set(required_permissions) - user_permissions

                if missing_permissions:
                    return Response(
                        content={
                            'error': 'Insufficient permissions',
                            'code': 'missing_permissions',
                            'required_permissions': list(required_permissions),
                            'missing_permissions': list(missing_permissions)
                        },
                        status_code=403
                    )
            else:
                # Check if user has ANY required permission
                has_permission = any(perm in user_permissions for perm in required_permissions)

                if not has_permission:
                    return Response(
                        content={
                            'error': 'Insufficient permissions',
                            'code': 'missing_permissions',
                            'required_permissions': list(required_permissions)
                        },
                        status_code=403
                    )

            return await f(request, *args, **kwargs)

        @functools.wraps(f)
        def sync_wrapper(request: Request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return Response(
                    content={'error': 'Authentication required'},
                    status_code=401
                )

            user_permissions = set(request.user.get('permissions', []))

            if require_all:
                missing_permissions = set(required_permissions) - user_permissions
                if missing_permissions:
                    return Response(
                        content={
                            'error': 'Insufficient permissions',
                            'code': 'missing_permissions'
                        },
                        status_code=403
                    )
            else:
                has_permission = any(perm in user_permissions for perm in required_permissions)
                if not has_permission:
                    return Response(
                        content={'error': 'Insufficient permissions'},
                        status_code=403
                    )

            return f(request, *args, **kwargs)

        import inspect
        if inspect.iscoroutinefunction(f):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


__all__ = [
    'login_required',
    'roles_required',
    'permission_required',
    'configure_auth_decorators',
    'extract_token_from_request',
    'inject_user_into_request',
]
