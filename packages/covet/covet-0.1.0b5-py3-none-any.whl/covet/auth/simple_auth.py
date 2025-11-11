"""
Simple Authentication System for Covet

Flask-like authentication API that integrates JWT, password hashing,
and decorators into one easy-to-use class.

Features:
- Simple setup with single Auth class
- Automatic middleware integration
- Built-in password management
- User context injection
- Token management
- Role-based access control

Usage:
    from covet import Covet
    from covet.auth import Auth

    app = Covet()
    auth = Auth(app, secret_key='your-secret-key')

    @app.route('/login', methods=['POST'])
    async def login(request):
        data = await request.json()
        if verify_credentials(data['username'], data['password']):
            token = auth.create_token(user_id=data['username'])
            return {'token': token}
        return {'error': 'Invalid credentials'}, 401

    @app.route('/protected')
    @auth.login_required
    async def protected(request):
        return {'user': request.user_id}
"""

from typing import Any, Dict, Optional

from .decorators import (
    configure_auth_decorators,
    login_required as _login_required,
    permission_required as _permission_required,
    roles_required as _roles_required,
)
from .jwt import JWTAuth
from .password import hash_password, verify_password


class Auth:
    """
    Simple authentication system for Covet apps.

    Provides Flask-like API for authentication with JWT tokens
    and secure password hashing.

    Example:
        >>> from covet import Covet
        >>> from covet.auth import Auth
        >>>
        >>> app = Covet()
        >>> auth = Auth(app, secret_key='my-secret-key')
        >>>
        >>> @app.route('/login', methods=['POST'])
        >>> async def login(request):
        ...     data = await request.json()
        ...     token = auth.create_token(user_id=data['user_id'])
        ...     return {'token': token}
    """

    def __init__(
        self,
        app=None,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30,
    ):
        """
        Initialize authentication system.

        Args:
            app: Covet application instance (optional, can be set later)
            secret_key: Secret key for JWT signing
            algorithm: JWT signing algorithm (HS256, HS512, RS256, RS512)
            access_token_expire_minutes: Access token expiration
            refresh_token_expire_days: Refresh token expiration

        Security Notes:
            - ALWAYS provide a secure secret_key in production
            - Use RS256/RS512 for multi-service architectures
            - Store secret_key in environment variables
        """
        # Initialize JWT auth
        self.jwt = JWTAuth(
            secret_key=secret_key,
            algorithm=algorithm,
            access_token_expire_minutes=access_token_expire_minutes,
            refresh_token_expire_days=refresh_token_expire_days,
        )

        # Configure decorators to use this JWT instance
        configure_auth_decorators(self.jwt)

        # Store app reference
        self.app = app

        # User loader callback
        self._user_loader = None

        # Initialize with app if provided
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
        Initialize authentication with Covet app.

        Args:
            app: Covet application instance
        """
        self.app = app

        # Store auth instance in app for access from other components
        if hasattr(app, 'extensions'):
            app.extensions['auth'] = self
        else:
            app.extensions = {'auth': self}

    def create_token(
        self,
        user_id: str,
        username: Optional[str] = None,
        roles: Optional[list] = None,
        **additional_claims
    ) -> str:
        """
        Create JWT access token for user.

        Args:
            user_id: Unique user identifier
            username: Username (optional)
            roles: User roles list (optional)
            **additional_claims: Additional JWT claims

        Returns:
            JWT token string

        Example:
            >>> token = auth.create_token(
            ...     user_id='123',
            ...     username='john',
            ...     roles=['user', 'admin']
            ... )
        """
        return self.jwt.create_token(
            user_id=user_id,
            username=username,
            roles=roles,
            **additional_claims
        )

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload dictionary

        Raises:
            TokenExpiredError: Token expired
            TokenInvalidError: Token invalid
        """
        return self.jwt.verify_token(token)

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create refresh token for user.

        Args:
            user_id: Unique user identifier

        Returns:
            Refresh token string
        """
        return self.jwt.create_refresh_token(user_id)

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token
        """
        return self.jwt.refresh_access_token(refresh_token)

    def revoke_token(self, token: str):
        """
        Revoke token (logout).

        Args:
            token: Token to revoke
        """
        self.jwt.revoke_token(token)

    def hash_password(self, password: str) -> str:
        """
        Hash password securely.

        Args:
            password: Plain text password

        Returns:
            Hashed password string

        Example:
            >>> hashed = auth.hash_password('MyPassword123!')
        """
        return hash_password(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password
            password_hash: Hashed password

        Returns:
            True if password matches

        Example:
            >>> is_valid = auth.verify_password('MyPassword123!', hashed)
        """
        return verify_password(password, password_hash)

    def user_loader(self, callback):
        """
        Decorator to register user loader callback.

        The callback receives user_id and should return user object.

        Example:
            >>> @auth.user_loader
            ... def load_user(user_id):
            ...     return User.get(user_id)
        """
        self._user_loader = callback
        return callback

    def load_user(self, user_id: str) -> Optional[Any]:
        """
        Load user by ID using registered loader.

        Args:
            user_id: User identifier

        Returns:
            User object or None
        """
        if self._user_loader:
            return self._user_loader(user_id)
        return None

    # Decorator properties for convenient access
    @property
    def login_required(self):
        """
        Decorator to require authentication.

        Example:
            >>> @app.route('/protected')
            ... @auth.login_required
            ... async def protected(request):
            ...     return {'user': request.user_id}
        """
        return _login_required

    def roles_required(self, *roles):
        """
        Decorator to require specific roles.

        Example:
            >>> @app.route('/admin')
            ... @auth.login_required
            ... @auth.roles_required('admin')
            ... async def admin_only(request):
            ...     return {'message': 'Admin access'}
        """
        return _roles_required(*roles)

    def permission_required(self, *permissions, require_all: bool = True):
        """
        Decorator to require specific permissions.

        Example:
            >>> @app.route('/users/delete')
            ... @auth.permission_required('users.delete')
            ... async def delete_user(request):
            ...     return {'message': 'User deleted'}
        """
        return _permission_required(*permissions, require_all=require_all)


# Convenience function for quick setup
def create_auth(
    app=None,
    secret_key: Optional[str] = None,
    **kwargs
) -> Auth:
    """
    Create Auth instance with optional app initialization.

    Args:
        app: Covet application (optional)
        secret_key: JWT secret key
        **kwargs: Additional Auth parameters

    Returns:
        Configured Auth instance

    Example:
        >>> from covet import Covet
        >>> from covet.auth import create_auth
        >>>
        >>> app = Covet()
        >>> auth = create_auth(app, secret_key='my-key')
    """
    return Auth(app=app, secret_key=secret_key, **kwargs)


__all__ = [
    'Auth',
    'create_auth',
]
