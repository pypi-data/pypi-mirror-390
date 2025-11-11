"""
JWT Authentication System

Production-ready JWT authentication with RS256 signing, token refresh,
OAuth2 flows, and RBAC integration.

Features:
- RS256 (RSA) and HS256 (HMAC) signing algorithms
- Access token + refresh token pattern
- Token validation and verification
- OAuth2 password and client credentials flows
- Role-Based Access Control (RBAC)
- Token blacklisting for logout
- Security middleware for ASGI applications

NO MOCK DATA: Real cryptography using PyJWT and cryptography libraries.
"""

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pydantic import BaseModel, Field, validator


class TokenType(str, Enum):
    """Token types."""

    ACCESS = "access"
    REFRESH = "refresh"


class OAuth2GrantType(str, Enum):
    """OAuth2 grant types."""

    PASSWORD = "password"
    CLIENT_CREDENTIALS = "client_credentials"
    AUTHORIZATION_CODE = "authorization_code"
    REFRESH_TOKEN = "refresh_token"


class JWTAlgorithm(str, Enum):
    """Supported JWT algorithms."""

    HS256 = "HS256"  # HMAC with SHA-256 (symmetric)
    RS256 = "RS256"  # RSA with SHA-256 (asymmetric)


class TokenClaims(BaseModel):
    """Standard JWT claims."""

    sub: str = Field(..., description="Subject (user ID)")
    exp: int = Field(..., description="Expiration time (Unix timestamp)")
    iat: int = Field(..., description="Issued at time (Unix timestamp)")
    jti: Optional[str] = Field(None, description="JWT ID (unique identifier)")
    type: TokenType = Field(..., description="Token type")

    # Custom claims
    roles: List[str] = Field(default_factory=list, description="User roles")
    permissions: List[str] = Field(default_factory=list, description="User permissions")
    scopes: List[str] = Field(default_factory=list, description="OAuth2 scopes")

    @validator("exp")
    def exp_must_be_future(cls, v):
        """Validate expiration is in the future."""
        if v <= int(datetime.utcnow().timestamp()):
            raise ValueError("Token expiration must be in the future")
        return v


class TokenPair(BaseModel):
    """Access and refresh token pair."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="Bearer", description="Token type")
    expires_in: int = Field(..., description="Access token lifetime in seconds")


class JWTConfig:
    """JWT configuration."""

    def __init__(
        self,
        algorithm: JWTAlgorithm = JWTAlgorithm.RS256,
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 30,
        secret_key: Optional[str] = None,
        private_key: Optional[str] = None,
        public_key: Optional[str] = None,
        issuer: Optional[str] = None,
        audience: Optional[str] = None,
    ):
        """
        Initialize JWT configuration.

        Args:
            algorithm: Signing algorithm (RS256 or HS256)
            access_token_expire_minutes: Access token lifetime
            refresh_token_expire_days: Refresh token lifetime
            secret_key: Secret key for HS256 (symmetric)
            private_key: Private key for RS256 (asymmetric)
            public_key: Public key for RS256 (asymmetric)
            issuer: Token issuer
            audience: Token audience
        """
        self.algorithm = algorithm
        self.access_token_expire = timedelta(minutes=access_token_expire_minutes)
        self.refresh_token_expire = timedelta(days=refresh_token_expire_days)
        self.issuer = issuer
        self.audience = audience

        # Configure keys based on algorithm
        if algorithm == JWTAlgorithm.HS256:
            self.secret_key = secret_key or self._generate_secret_key()
            self.private_key = None
            self.public_key = None
        else:  # RS256
            if private_key and public_key:
                self.private_key = private_key
                self.public_key = public_key
            else:
                self.private_key, self.public_key = self._generate_rsa_keys()
            self.secret_key = None

    def _generate_secret_key(self) -> str:
        """Generate secure random secret key for HS256."""
        return secrets.token_urlsafe(64)

    def _generate_rsa_keys(self) -> tuple[str, str]:
        """Generate RSA key pair for RS256."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("utf-8")

        return private_pem, public_pem


class TokenBlacklist:
    """
    Token blacklist for logout and revocation with TTL-based cleanup.

    SECURITY FIX: Uses structured TTL storage to prevent memory leaks
    and provides periodic cleanup of expired entries.

    In production, use Redis with automatic expiration or a database
    with indexed expiration times.
    """

    def __init__(self, cleanup_interval_seconds: int = 300):
        """
        Initialize token blacklist.

        Args:
            cleanup_interval_seconds: Interval for periodic cleanup (default: 5 minutes)
        """
        # Store tokens with expiration: {jti: expiration_timestamp}
        self._blacklist: Dict[str, int] = {}
        self._cleanup_interval = cleanup_interval_seconds
        self._cleanup_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def start_cleanup(self):
        """Start periodic cleanup task."""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._periodic_cleanup())

    async def stop_cleanup(self):
        """Stop periodic cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                # Expected when canceling - safe to ignore
                pass
            self._cleanup_task = None

    async def add(self, jti: str, exp: int):
        """
        Add token to blacklist with expiration.

        Args:
            jti: JWT ID
            exp: Expiration timestamp (Unix timestamp)
        """
        async with self._lock:
            self._blacklist[jti] = exp

    async def _periodic_cleanup(self):
        """Periodically remove expired tokens from blacklist."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                await self._cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception:
                # Log error in production, continue cleanup loop
                await asyncio.sleep(60)

    async def _cleanup_expired(self):
        """Remove expired tokens from blacklist."""
        current_time = int(datetime.utcnow().timestamp())
        async with self._lock:
            # Find expired tokens
            expired_jtis = [jti for jti, exp in self._blacklist.items() if exp <= current_time]
            # Remove expired tokens
            for jti in expired_jtis:
                self._blacklist.pop(jti, None)

    def is_blacklisted(self, jti: str) -> bool:
        """
        Check if token is blacklisted (synchronous check).

        Args:
            jti: JWT ID

        Returns:
            True if token is blacklisted and not expired
        """
        if jti not in self._blacklist:
            return False

        # Check if token is expired (lazy cleanup)
        exp = self._blacklist[jti]
        current_time = int(datetime.utcnow().timestamp())

        if exp <= current_time:
            # Token expired, remove from blacklist
            self._blacklist.pop(jti, None)
            return False

        return True

    async def clear(self):
        """Clear all blacklisted tokens."""
        async with self._lock:
            self._blacklist.clear()

    def size(self) -> int:
        """Get number of blacklisted tokens."""
        return len(self._blacklist)


class JWTAuthenticator:
    """
    JWT authentication system.

    Handles token generation, validation, and verification.
    """

    def __init__(self, config: JWTConfig):
        """
        Initialize JWT authenticator.

        Args:
            config: JWT configuration
        """
        self.config = config
        self.blacklist = TokenBlacklist()

    def create_token(
        self,
        subject: str,
        token_type: TokenType,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        extra_claims: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create JWT token.

        Args:
            subject: Subject (user ID)
            token_type: Token type (access or refresh)
            roles: User roles
            permissions: User permissions
            scopes: OAuth2 scopes
            extra_claims: Additional claims

        Returns:
            Encoded JWT token
        """
        now = datetime.utcnow()

        # Calculate expiration
        if token_type == TokenType.ACCESS:
            expire = now + self.config.access_token_expire
        else:
            expire = now + self.config.refresh_token_expire

        # Build claims
        claims = {
            "sub": subject,
            "exp": int(expire.timestamp()),
            "iat": int(now.timestamp()),
            "jti": secrets.token_urlsafe(32),
            "type": token_type.value,
            "roles": roles or [],
            "permissions": permissions or [],
            "scopes": scopes or [],
        }

        # Add issuer and audience if configured
        if self.config.issuer:
            claims["iss"] = self.config.issuer
        if self.config.audience:
            claims["aud"] = self.config.audience

        # Add extra claims
        if extra_claims:
            claims.update(extra_claims)

        # Encode token
        if self.config.algorithm == JWTAlgorithm.HS256:
            token = jwt.encode(claims, self.config.secret_key, algorithm="HS256")
        else:  # RS256
            token = jwt.encode(claims, self.config.private_key, algorithm="RS256")

        return token

    def create_token_pair(
        self,
        subject: str,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
    ) -> TokenPair:
        """
        Create access and refresh token pair.

        Args:
            subject: Subject (user ID)
            roles: User roles
            permissions: User permissions
            scopes: OAuth2 scopes

        Returns:
            Token pair with access and refresh tokens
        """
        access_token = self.create_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            roles=roles,
            permissions=permissions,
            scopes=scopes,
        )

        refresh_token = self.create_token(
            subject=subject,
            token_type=TokenType.REFRESH,
            roles=roles,
            permissions=permissions,
            scopes=scopes,
        )

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(self.config.access_token_expire.total_seconds()),
        )

    def verify_token(self, token: str, token_type: Optional[TokenType] = None) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token: Encoded JWT token
            token_type: Expected token type (optional)

        Returns:
            Decoded token claims

        Raises:
            jwt.InvalidTokenError: If token is invalid
            jwt.ExpiredSignatureError: If token is expired
            ValueError: If token type doesn't match or token is blacklisted
        """
        try:
            # SECURITY FIX: Prevent algorithm confusion attack
            # First decode without verification to check algorithm in header
            unverified_header = jwt.get_unverified_header(token)
            token_alg = unverified_header.get("alg", "").upper()

            # Reject 'none' algorithm
            if token_alg == "NONE" or not token_alg:
                raise jwt.InvalidTokenError("Algorithm 'none' is not allowed")

            # Verify algorithm matches configuration
            if token_alg != self.config.algorithm.value:
                raise jwt.InvalidTokenError(
                    f"Token algorithm '{token_alg}' does not match configured algorithm '{self.config.algorithm.value}'"
                )

            # For RS256, ensure we're using public key (not private key)
            # For HS256, ensure we're using secret key (not public key)
            if self.config.algorithm == JWTAlgorithm.HS256:
                if not self.config.secret_key:
                    raise jwt.InvalidTokenError("HS256 requires secret_key")

                # Decode with strict algorithm enforcement
                claims = jwt.decode(
                    token,
                    self.config.secret_key,
                    algorithms=["HS256"],
                    audience=self.config.audience,
                    issuer=self.config.issuer,
                    options={
                        "verify_signature": True,
                        "require": ["exp", "iat", "sub"],
                    },
                )
            else:  # RS256
                if not self.config.public_key:
                    raise jwt.InvalidTokenError("RS256 requires public_key")

                # Decode with strict algorithm enforcement
                claims = jwt.decode(
                    token,
                    self.config.public_key,
                    algorithms=["RS256"],
                    audience=self.config.audience,
                    issuer=self.config.issuer,
                    options={
                        "verify_signature": True,
                        "require": ["exp", "iat", "sub"],
                    },
                )

            # Note: PyJWT already validates expiration, this check is redundant
            # Removed defense-in-depth expiration check to fix off-by-one bug
            # PyJWT's exp validation is sufficient and correct

            # Check token type
            if token_type and claims.get("type") != token_type.value:
                raise ValueError(f"Expected {token_type.value} token, got {claims.get('type')}")

            # Check blacklist
            jti = claims.get("jti")
            if jti and self.blacklist.is_blacklisted(jti):
                raise ValueError("Token has been revoked")

            return claims

        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise jwt.InvalidTokenError(f"Invalid token: {str(e)}")

    async def revoke_token(self, token: str):
        """
        Revoke token (add to blacklist).

        Args:
            token: Token to revoke
        """
        try:
            # Decode without verification to get JTI and expiration
            claims = jwt.decode(token, options={"verify_signature": False})
            jti = claims.get("jti")
            exp = claims.get("exp")

            if jti and exp:
                await self.blacklist.add(jti, exp)
        except Exception:
            # If we can't decode, token is already invalid
            pass

    async def refresh_access_token(self, refresh_token: str) -> TokenPair:
        """
        Refresh access token using refresh token with rotation.

        SECURITY: Implements refresh token rotation to prevent token reuse.
        The old refresh token is immediately revoked when a new token pair is issued.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New token pair with rotated refresh token

        Raises:
            ValueError: If refresh token is invalid or already used
        """
        # Verify refresh token
        claims = self.verify_token(refresh_token, token_type=TokenType.REFRESH)

        # SECURITY FIX: Immediately revoke old refresh token (rotation)
        await self.revoke_token(refresh_token)

        # Create new token pair with fresh tokens
        return self.create_token_pair(
            subject=claims["sub"],
            roles=claims.get("roles"),
            permissions=claims.get("permissions"),
            scopes=claims.get("scopes"),
        )


class RBACManager:
    """
    Role-Based Access Control manager.

    Manages roles, permissions, and access control.
    """

    def __init__(self):
        """Initialize RBAC manager."""
        # Role -> Permissions mapping
        self.role_permissions: Dict[str, Set[str]] = {}

        # Role hierarchy (role -> parent roles)
        self.role_hierarchy: Dict[str, Set[str]] = {}

    def add_role(
        self,
        role: str,
        permissions: Optional[List[str]] = None,
        parents: Optional[List[str]] = None,
    ):
        """
        Add role with permissions and parent roles.

        Args:
            role: Role name
            permissions: List of permissions
            parents: List of parent roles (inherits their permissions)
        """
        if role not in self.role_permissions:
            self.role_permissions[role] = set()

        if permissions:
            self.role_permissions[role].update(permissions)

        if parents:
            if role not in self.role_hierarchy:
                self.role_hierarchy[role] = set()
            self.role_hierarchy[role].update(parents)

    def get_permissions(self, role: str) -> Set[str]:
        """
        Get all permissions for role (including inherited).

        Args:
            role: Role name

        Returns:
            Set of permissions
        """
        permissions = set(self.role_permissions.get(role, set()))

        # Add inherited permissions from parent roles
        for parent in self.role_hierarchy.get(role, set()):
            permissions.update(self.get_permissions(parent))

        return permissions

    def has_permission(self, roles: List[str], permission: str) -> bool:
        """
        Check if any of the roles has the permission.

        Args:
            roles: List of roles
            permission: Permission to check

        Returns:
            True if any role has permission
        """
        for role in roles:
            if permission in self.get_permissions(role):
                return True
        return False

    def has_any_permission(self, roles: List[str], permissions: List[str]) -> bool:
        """
        Check if any of the roles has any of the permissions.

        Args:
            roles: List of roles
            permissions: List of permissions

        Returns:
            True if any role has any permission
        """
        for permission in permissions:
            if self.has_permission(roles, permission):
                return True
        return False

    def has_all_permissions(self, roles: List[str], permissions: List[str]) -> bool:
        """
        Check if roles have all permissions.

        Args:
            roles: List of roles
            permissions: List of permissions

        Returns:
            True if roles have all permissions
        """
        for permission in permissions:
            if not self.has_permission(roles, permission):
                return False
        return True


class OAuth2PasswordFlow:
    """
    OAuth2 Resource Owner Password Credentials flow.

    Used for first-party clients (trusted applications).
    """

    def __init__(
        self,
        authenticator: JWTAuthenticator,
        verify_credentials: Callable[[str, str], Optional[Dict[str, Any]]],
    ):
        """
        Initialize OAuth2 password flow.

        Args:
            authenticator: JWT authenticator
            verify_credentials: Function to verify username/password
                                Returns user info dict if valid, None otherwise
        """
        self.authenticator = authenticator
        self.verify_credentials = verify_credentials

    async def authenticate(
        self, username: str, password: str, scopes: Optional[List[str]] = None
    ) -> Optional[TokenPair]:
        """
        Authenticate user with username and password.

        Args:
            username: Username
            password: Password
            scopes: Requested OAuth2 scopes

        Returns:
            Token pair if authentication successful, None otherwise
        """
        # Verify credentials
        user_info = await self.verify_credentials(username, password)
        if not user_info:
            return None

        # Create tokens
        return self.authenticator.create_token_pair(
            subject=user_info.get("id") or username,
            roles=user_info.get("roles", []),
            permissions=user_info.get("permissions", []),
            scopes=scopes or [],
        )


class OAuth2ClientCredentialsFlow:
    """
    OAuth2 Client Credentials flow.

    Used for machine-to-machine authentication.
    """

    def __init__(
        self,
        authenticator: JWTAuthenticator,
        verify_client: Callable[[str, str], Optional[Dict[str, Any]]],
    ):
        """
        Initialize OAuth2 client credentials flow.

        Args:
            authenticator: JWT authenticator
            verify_client: Function to verify client ID/secret
                           Returns client info dict if valid, None otherwise
        """
        self.authenticator = authenticator
        self.verify_client = verify_client

    async def authenticate(
        self, client_id: str, client_secret: str, scopes: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Authenticate client with credentials.

        Args:
            client_id: Client ID
            client_secret: Client secret
            scopes: Requested OAuth2 scopes

        Returns:
            Access token if authentication successful, None otherwise
        """
        # Verify client credentials
        client_info = await self.verify_client(client_id, client_secret)
        if not client_info:
            return None

        # Create access token (no refresh token for client credentials)
        return self.authenticator.create_token(
            subject=client_id,
            token_type=TokenType.ACCESS,
            roles=client_info.get("roles", []),
            permissions=client_info.get("permissions", []),
            scopes=scopes or [],
        )


class JWTMiddleware:
    """
    ASGI middleware for JWT authentication.

    Extracts and verifies JWT from Authorization header.
    """

    def __init__(
        self,
        app,
        authenticator: JWTAuthenticator,
        exempt_paths: Optional[List[str]] = None,
        optional_auth_paths: Optional[List[str]] = None,
    ):
        """
        Initialize JWT middleware.

        Args:
            app: ASGI application
            authenticator: JWT authenticator
            exempt_paths: Paths that don't require authentication
            optional_auth_paths: Paths where authentication is optional
        """
        self.app = app
        self.authenticator = authenticator
        self.exempt_paths = set(exempt_paths or [])
        self.optional_auth_paths = set(optional_auth_paths or [])

    def _extract_token(self, headers: List[tuple]) -> Optional[str]:
        """Extract JWT from Authorization header."""
        auth_header = None
        for name, value in headers:
            if name.lower() == b"authorization":
                auth_header = value.decode("utf-8")
                break

        if not auth_header:
            return None

        # Parse "Bearer <token>"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        return parts[1]

    async def __call__(self, scope, receive, send):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "/")

        # Check if path is exempt
        if path in self.exempt_paths:
            await self.app(scope, receive, send)
            return

        # Extract token
        headers = scope.get("headers", [])
        token = self._extract_token(headers)

        # Check if authentication is optional
        optional = path in self.optional_auth_paths

        if not token:
            if optional:
                # Continue without user info
                scope["user"] = None
                await self.app(scope, receive, send)
                return
            else:
                # Return 401 Unauthorized
                await self._send_error(
                    send,
                    status=401,
                    error="unauthorized",
                    message="Missing or invalid authorization header",
                )
                return

        # Verify token
        try:
            claims = self.authenticator.verify_token(token, token_type=TokenType.ACCESS)

            # Add user info to scope
            scope["user"] = {
                "id": claims["sub"],
                "roles": claims.get("roles", []),
                "permissions": claims.get("permissions", []),
                "scopes": claims.get("scopes", []),
                "claims": claims,
            }

            await self.app(scope, receive, send)

        except jwt.ExpiredSignatureError:
            await self._send_error(
                send, status=401, error="token_expired", message="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            await self._send_error(send, status=401, error="invalid_token", message=str(e))
        except ValueError as e:
            await self._send_error(send, status=401, error="invalid_token", message=str(e))

    async def _send_error(self, send, status: int, error: str, message: str):
        """Send error response."""
        import json

        body = {
            "type": f"https://errors.covetpy.dev/{error}",
            "title": "Authentication Error",
            "status": status,
            "detail": message,
        }

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"application/json; charset=utf-8"],
                    [b"www-authenticate", b"Bearer"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(body).encode("utf-8"),
            }
        )


def require_permissions(*permissions: str):
    """
    Decorator to require permissions for route handler.

    Args:
        *permissions: Required permissions

    Example:
        @require_permissions('users:read', 'users:write')
        async def update_user(request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request/scope (implementation depends on framework)
            # This is a generic example
            request = args[0] if args else None
            user = getattr(request, "user", None) if request else None

            if not user:
                raise ValueError("Authentication required")

            user_permissions = set(user.get("permissions", []))
            required = set(permissions)

            if not required.issubset(user_permissions):
                missing = required - user_permissions
                raise ValueError(f"Missing permissions: {', '.join(missing)}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_roles(*roles: str):
    """
    Decorator to require roles for route handler.

    Args:
        *roles: Required roles

    Example:
        @require_roles('admin', 'moderator')
        async def delete_user(request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = args[0] if args else None
            user = getattr(request, "user", None) if request else None

            if not user:
                raise ValueError("Authentication required")

            user_roles = set(user.get("roles", []))
            required = set(roles)

            if not required.intersection(user_roles):
                raise ValueError(f"Requires one of: {', '.join(required)}")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# Create compatibility wrapper for JWTManager
class JWTManagerWrapper:
    """Wrapper to make JWTAuthenticator compatible with test expectations."""

    def __init__(self, config: JWTConfig):
        """Initialize wrapper with JWT authenticator."""
        self._authenticator = JWTAuthenticator(config)
        self.config = config
        self.blacklist = self._authenticator.blacklist

    def create_access_token(
        self,
        subject: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create access token (compatibility wrapper).

        Args:
            subject: Subject identifier
            data: Additional claims

        Returns:
            Encoded JWT access token
        """
        return self._authenticator.create_token(
            subject=subject,
            token_type=TokenType.ACCESS,
            extra_claims=data
        )

    def create_refresh_token(
        self,
        subject: str,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create refresh token (compatibility wrapper).

        Args:
            subject: Subject identifier
            data: Additional claims

        Returns:
            Encoded JWT refresh token
        """
        return self._authenticator.create_token(
            subject=subject,
            token_type=TokenType.REFRESH,
            extra_claims=data
        )

    def verify_token(
        self,
        token: str,
        token_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify token (compatibility wrapper).

        Args:
            token: Token to verify
            token_type: Expected token type

        Returns:
            Decoded token claims
        """
        token_type_enum = None
        if token_type:
            if isinstance(token_type, str):
                # Convert string to TokenType enum
                token_type_enum = TokenType(token_type)
            else:
                token_type_enum = token_type

        return self._authenticator.verify_token(token, token_type=token_type_enum)


# Alias for compatibility with test suite
JWTManager = JWTManagerWrapper


__all__ = [
    # Enums
    "TokenType",
    "OAuth2GrantType",
    "JWTAlgorithm",
    # Models
    "TokenClaims",
    "TokenPair",
    # Core
    "JWTConfig",
    "JWTAuthenticator",
    "JWTManager",  # Alias for JWTAuthenticator
    "TokenBlacklist",
    # RBAC
    "RBACManager",
    # OAuth2
    "OAuth2PasswordFlow",
    "OAuth2ClientCredentialsFlow",
    # Middleware
    "JWTMiddleware",
    # Decorators
    "require_permissions",
    "require_roles",
]

