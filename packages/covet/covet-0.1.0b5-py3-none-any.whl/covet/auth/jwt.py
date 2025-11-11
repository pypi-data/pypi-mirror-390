"""
Simplified JWT Authentication Module

A simple, secure JWT implementation designed for easy integration with Covet apps.
Provides Flask-like API for authentication with production-grade security.

Security Features:
- HS256/RS256 signing algorithms
- Secure token generation with secrets module
- Token expiration and refresh
- Token blacklist support
- Automatic key rotation warnings
- Protection against timing attacks

Usage:
    from covet.auth import JWTAuth, JWTConfig

    jwt_auth = JWTAuth(secret_key='your-secret-key')
    token = jwt_auth.create_token(user_id='123', username='john')
    payload = jwt_auth.verify_token(token)
"""

import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from .exceptions import TokenExpiredError, TokenInvalidError


class SimpleJWTAuth:
    """
    Simplified JWT authentication for Covet apps.

    This is a streamlined version designed for easy integration while maintaining
    production-grade security.

    Security Considerations:
    - Uses HS256 by default for simplicity (RS256 recommended for production)
    - Automatic secret key generation if not provided (not recommended for production)
    - Token blacklist for logout functionality
    - Configurable token expiration
    - Protection against token manipulation
    """

    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30,
        issuer: str = "covet-app",
        audience: str = "covet-api"
    ):
        """
        Initialize JWT authentication.

        Args:
            secret_key: Secret key for signing tokens (auto-generated if None)
            algorithm: Signing algorithm (HS256, HS512, RS256, RS512)
            access_token_expire_minutes: Access token expiration in minutes
            refresh_token_expire_days: Refresh token expiration in days
            issuer: Token issuer identifier
            audience: Token audience identifier

        Security Notes:
            - For production, ALWAYS provide a strong secret_key
            - Use RS256/RS512 for multi-service architectures
            - Store secret_key in environment variables, never in code
            - Rotate keys regularly (every 90 days recommended)
        """
        # Generate secure key if not provided (with warning)
        if secret_key is None:
            secret_key = secrets.token_urlsafe(64)
            import warnings
            warnings.warn(
                "No secret_key provided. Auto-generated key will not persist across restarts. "
                "For production, provide a secure secret_key.",
                SecurityWarning,
                stacklevel=2
            )

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.issuer = issuer
        self.audience = audience

        # Token blacklist for logout
        self._blacklist: Set[str] = set()
        self._blacklist_cleanup_counter = 0

        # Key rotation tracking
        self._key_created_at = time.time()
        self._max_key_age_days = 90

    def create_token(
        self,
        user_id: str,
        username: Optional[str] = None,
        roles: Optional[list] = None,
        **additional_claims
    ) -> str:
        """
        Create access token for user.

        Args:
            user_id: Unique user identifier (required)
            username: Username (optional)
            roles: User roles list (optional)
            **additional_claims: Additional JWT claims

        Returns:
            JWT token string

        Example:
            >>> token = jwt_auth.create_token(user_id='123', username='john', roles=['admin'])
            >>> print(token)
            'eyJ0eXAiOiJKV1QiLCJhbGc...'
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=self.access_token_expire_minutes)

        # Build payload with standard claims
        payload = {
            'sub': str(user_id),  # Subject (user ID)
            'iat': int(now.timestamp()),  # Issued at
            'exp': int(expires_at.timestamp()),  # Expiration
            'nbf': int(now.timestamp()),  # Not before
            'iss': self.issuer,  # Issuer
            'aud': self.audience,  # Audience
            'jti': secrets.token_urlsafe(16),  # JWT ID for blacklisting
            'token_type': 'access',
        }

        # Add optional claims
        if username:
            payload['username'] = username
        if roles:
            payload['roles'] = roles

        # Add any additional claims
        payload.update(additional_claims)

        # Check for key rotation warning
        self._check_key_rotation()

        # Encode token
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token string

        Returns:
            Token payload as dictionary

        Raises:
            TokenExpiredError: Token has expired
            TokenInvalidError: Token is invalid or blacklisted

        Example:
            >>> payload = jwt_auth.verify_token(token)
            >>> print(payload['sub'])  # User ID
            '123'
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                audience=self.audience,
                options={
                    'verify_exp': True,
                    'verify_iat': True,
                    'verify_nbf': True,
                }
            )

            # Check blacklist
            jti = payload.get('jti')
            if jti and jti in self._blacklist:
                raise TokenInvalidError('Token has been revoked')

            return payload

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise TokenInvalidError(f'Invalid token: {str(e)}')
        except Exception as e:
            raise TokenInvalidError(f'Token verification failed: {str(e)}')

    def create_refresh_token(self, user_id: str) -> str:
        """
        Create refresh token for long-term authentication.

        Args:
            user_id: Unique user identifier

        Returns:
            Refresh token string

        Security Note:
            Refresh tokens should be stored securely and transmitted over HTTPS only.
        """
        now = datetime.utcnow()
        expires_at = now + timedelta(days=self.refresh_token_expire_days)

        payload = {
            'sub': str(user_id),
            'iat': int(now.timestamp()),
            'exp': int(expires_at.timestamp()),
            'nbf': int(now.timestamp()),
            'iss': self.issuer,
            'aud': self.audience,
            'jti': secrets.token_urlsafe(16),
            'token_type': 'refresh',
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create new access token from refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token

        Raises:
            TokenExpiredError: Refresh token expired
            TokenInvalidError: Invalid refresh token
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token)

        # Ensure it's a refresh token
        if payload.get('token_type') != 'refresh':
            raise TokenInvalidError('Expected refresh token')

        # Create new access token
        user_id = payload['sub']
        username = payload.get('username')
        roles = payload.get('roles')

        return self.create_token(user_id=user_id, username=username, roles=roles)

    def revoke_token(self, token: str):
        """
        Revoke a token by adding it to blacklist.

        Args:
            token: Token to revoke

        Note:
            This blacklist is in-memory. For production, use Redis or database.
        """
        try:
            # Decode without verification (to get jti even if expired)
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': False, 'verify_signature': True}
            )

            jti = payload.get('jti')
            if jti:
                self._blacklist.add(jti)

                # Periodic cleanup of old blacklist entries
                self._blacklist_cleanup_counter += 1
                if self._blacklist_cleanup_counter >= 1000:
                    self._cleanup_blacklist()
                    self._blacklist_cleanup_counter = 0

        except Exception:
            # Ignore errors for revocation
            pass

    def _cleanup_blacklist(self):
        """Clean up expired tokens from blacklist."""
        # In production, implement proper expiration tracking
        # For now, keep blacklist size reasonable
        if len(self._blacklist) > 10000:
            # Keep only recent 5000 entries (FIFO)
            self._blacklist = set(list(self._blacklist)[-5000:])

    def _check_key_rotation(self):
        """Check if key rotation is recommended."""
        key_age_days = (time.time() - self._key_created_at) / (24 * 3600)
        if key_age_days > self._max_key_age_days:
            import warnings
            warnings.warn(
                f"Secret key is {key_age_days:.0f} days old. "
                f"Key rotation recommended every {self._max_key_age_days} days.",
                SecurityWarning,
                stacklevel=3
            )

    def get_user_id(self, token: str) -> str:
        """
        Extract user ID from token without full verification.

        Args:
            token: JWT token

        Returns:
            User ID (subject claim)

        Raises:
            TokenInvalidError: Invalid token

        Security Warning:
            This method still verifies the signature. Use verify_token() for full validation.
        """
        try:
            # Decode with signature verification but without expiration check
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': False}
            )
            return payload.get('sub', '')
        except Exception as e:
            raise TokenInvalidError(f'Cannot extract user ID: {str(e)}')


# Backward compatibility with existing code
class JWTAuth(SimpleJWTAuth):
    """Alias for SimpleJWTAuth for backward compatibility."""
    pass


# Utility functions for RSA key generation (for RS256/RS512)
def generate_rsa_keypair(key_size: int = 2048) -> tuple[str, str]:
    """
    Generate RSA key pair for RS256/RS512 signing.

    Args:
        key_size: Key size in bits (2048 or 4096 recommended)

    Returns:
        Tuple of (private_key_pem, public_key_pem)

    Security Note:
        - Use 2048 bits minimum, 4096 for high security
        - Store private key securely (HSM, KMS, or encrypted storage)
        - Never commit keys to version control
    """
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )

    # Serialize private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    # Serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem


class SecurityWarning(UserWarning):
    """Warning for security-related issues."""
    pass


__all__ = [
    'SimpleJWTAuth',
    'JWTAuth',
    'generate_rsa_keypair',
    'SecurityWarning',
]
