"""
Enhanced JWT Security Utilities for CovetPy Framework.

This module provides production-ready JWT token management with security best practices,
including RS256/HS256 algorithms, token rotation, revocation, and proper expiration handling.

Example:
    from covet.security.secure_jwt import SecureJWTManager, JWTAuth, create_access_token

    # Simple usage
    configure_jwt(secret_key="your-secret-key", algorithm="HS256")
    token = create_access_token(subject="user123", expires_in=3600)
    payload = verify_token(token)

    # Advanced usage
    jwt_manager = SecureJWTManager(secret_key="your-secret", algorithm="RS256")
    token = jwt_manager.encode({"user_id": "123"}, expires_in=7200)
    decoded = jwt_manager.decode(token)
"""

import hashlib
import hmac
import json
import secrets
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Set

try:
    import jwt
    from jwt.exceptions import (
        DecodeError,
        ExpiredSignatureError,
        InvalidAlgorithmError,
        InvalidKeyError,
        InvalidSignatureError,
        InvalidTokenError,
    )

    HAS_PYJWT = True
except ImportError:
    HAS_PYJWT = False

    # Provide fallback exception classes
    class InvalidTokenError(Exception):
        """Invalid token error."""

        pass

    class ExpiredSignatureError(InvalidTokenError):
        """Expired signature error."""

        pass

    class DecodeError(InvalidTokenError):
        """Decode error."""

        pass


class SecureJWTManager:
    """
    Enhanced JWT token management with security best practices.

    Features:
    - Support for RS256 and HS256 algorithms
    - Automatic expiration, issued-at, and not-before claims
    - Token rotation for refresh flows
    - Token revocation via blacklist
    - Proper exception handling

    Args:
        secret_key: Secret key for signing tokens (for HS256) or private key (for RS256)
        algorithm: Algorithm to use (RS256 recommended for production, HS256 for simplicity)

    Security Notes:
        - RS256 is recommended for production (uses public/private key pairs)
        - HS256 is simpler but requires sharing secret between services
        - Always use strong, randomly generated keys (32+ bytes for HS256)
        - Store keys securely (environment variables, key management systems)
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Initialize JWT manager with secret key and algorithm."""
        if not secret_key:
            raise ValueError("secret_key cannot be empty")

        if algorithm not in ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self._blacklist: Set[str] = set()

        if not HAS_PYJWT:
            import warnings

            warnings.warn(
                "PyJWT not installed. Using basic JWT implementation. "
                "Install PyJWT for production use: pip install PyJWT"
            )

    def encode(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """
        Encode JWT with expiration and security claims.

        Automatically adds:
        - exp: Expiration time (current time + expires_in)
        - iat: Issued at time (current time)
        - nbf: Not before time (current time)

        Args:
            payload: Dictionary of claims to encode
            expires_in: Token expiration time in seconds (default: 3600 = 1 hour)

        Returns:
            Encoded JWT token string

        Raises:
            ValueError: If payload is invalid

        Example:
            token = jwt_manager.encode({"user_id": "123", "role": "admin"}, expires_in=7200)
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary")

        now = datetime.utcnow()

        # Create enhanced payload with security claims
        enhanced_payload = payload.copy()
        enhanced_payload.update(
            {
                "exp": now + timedelta(seconds=expires_in),
                "iat": now,
                "nbf": now,
                "jti": secrets.token_hex(16),  # JWT ID for tracking/revocation
            }
        )

        if HAS_PYJWT:
            return jwt.encode(enhanced_payload, self.secret_key, algorithm=self.algorithm)
        else:
            # Basic fallback implementation (NOT for production)
            return self._basic_encode(enhanced_payload)

    def decode(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """
        Decode and validate JWT token with proper error handling.

        Args:
            token: JWT token string to decode
            verify_exp: Whether to verify expiration (default: True)

        Returns:
            Decoded payload dictionary

        Raises:
            ExpiredSignatureError: If token has expired
            InvalidTokenError: If token is invalid

        Example:
            try:
                payload = jwt_manager.decode(token)
                user_id = payload["user_id"]
            except ExpiredSignatureError:
                # Handle expired token
                pass
        """
        if not token:
            raise InvalidTokenError("Token cannot be empty")

        # Check blacklist
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        if token_hash in self._blacklist:
            raise InvalidTokenError("Token has been revoked")

        if HAS_PYJWT:
            try:
                options = {"verify_exp": verify_exp}
                return jwt.decode(
                    token, self.secret_key, algorithms=[self.algorithm], options=options
                )
            except ExpiredSignatureError:
                raise ExpiredSignatureError("Token has expired")
            except (DecodeError, InvalidSignatureError, InvalidKeyError) as e:
                raise InvalidTokenError(f"Invalid token: {str(e)}")
        else:
            # Basic fallback implementation
            return self._basic_decode(token, verify_exp)

    def rotate_token(self, old_token: str, expires_in: int = 3600) -> str:
        """
        Rotate JWT token with new expiration (for token refresh).

        This creates a new token with the same claims but updated expiration.
        The old token is automatically blacklisted.

        Args:
            old_token: Existing token to rotate
            expires_in: New token expiration time in seconds

        Returns:
            New JWT token string

        Raises:
            InvalidTokenError: If old token is invalid

        Example:
            # User requests token refresh
            new_token = jwt_manager.rotate_token(old_refresh_token, expires_in=7200)
        """
        # Decode old token (verify_exp=False to allow expired tokens to be rotated)
        try:
            old_payload = self.decode(old_token, verify_exp=False)
        except InvalidTokenError:
            # If token is already invalid (not just expired), raise error
            raise

        # Remove standard claims (they'll be regenerated)
        claims_to_remove = ["exp", "iat", "nbf", "jti"]
        new_payload = {k: v for k, v in old_payload.items() if k not in claims_to_remove}

        # Revoke old token
        self.revoke_token(old_token)

        # Create new token
        return self.encode(new_payload, expires_in=expires_in)

    def revoke_token(self, token: str) -> bool:
        """
        Mark token as revoked (store in blacklist).

        Args:
            token: Token to revoke

        Returns:
            True if token was successfully revoked

        Note:
            In production, use Redis or database for blacklist storage.
            This in-memory implementation is for development only.

        Example:
            # User logs out
            jwt_manager.revoke_token(user_token)
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self._blacklist.add(token_hash)
        return True

    def _basic_encode(self, payload: Dict[str, Any]) -> str:
        """Basic JWT encoding (fallback when PyJWT not available)."""
        import base64

        # Convert datetime objects to timestamps
        encoded_payload = {}
        for key, value in payload.items():
            if isinstance(value, datetime):
                encoded_payload[key] = int(value.timestamp())
            else:
                encoded_payload[key] = value

        # Create header
        header = {"alg": self.algorithm, "typ": "JWT"}

        # Base64 encode header and payload
        header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=").decode()

        payload_b64 = (
            base64.urlsafe_b64encode(json.dumps(encoded_payload).encode()).rstrip(b"=").decode()
        )

        # Create signature
        message = f"{header_b64}.{payload_b64}".encode()
        signature = hmac.new(self.secret_key.encode(), message, hashlib.sha256).digest()

        signature_b64 = base64.urlsafe_b64encode(signature).rstrip(b"=").decode()

        return f"{header_b64}.{payload_b64}.{signature_b64}"

    def _basic_decode(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """Basic JWT decoding (fallback when PyJWT not available)."""
        import base64

        try:
            parts = token.split(".")
            if len(parts) != 3:
                raise InvalidTokenError("Invalid token format")

            header_b64, payload_b64, signature_b64 = parts

            # Verify signature
            message = f"{header_b64}.{payload_b64}".encode()
            expected_signature = hmac.new(
                self.secret_key.encode(), message, hashlib.sha256
            ).digest()

            # Add padding
            signature_b64_padded = signature_b64 + "=" * (4 - len(signature_b64) % 4)
            actual_signature = base64.urlsafe_b64decode(signature_b64_padded)

            if not hmac.compare_digest(expected_signature, actual_signature):
                raise InvalidTokenError("Invalid signature")

            # Decode payload
            payload_b64_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
            payload_json = base64.urlsafe_b64decode(payload_b64_padded).decode()
            payload = json.loads(payload_json)

            # Verify expiration
            if verify_exp and "exp" in payload:
                if payload["exp"] < time.time():
                    raise ExpiredSignatureError("Token has expired")

            return payload

        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise InvalidTokenError(f"Invalid token: {str(e)}")


class JWTAuth:
    """
    JWT Authentication helper class.

    Provides high-level authentication operations using JWT tokens.

    Example:
        jwt_auth = JWTAuth(secret_key="your-secret-key")

        # Create token
        payload = {"user_id": "123", "exp": (datetime.utcnow() + timedelta(hours=1)).timestamp()}
        token = jwt_auth.encode_token(payload)

        # Verify token
        decoded = jwt_auth.decode_token(token)
        user_id = decoded["user_id"]
    """

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        """Initialize JWT authentication."""
        self.jwt_manager = SecureJWTManager(secret_key=secret_key, algorithm=algorithm)

    def encode_token(self, payload: Dict[str, Any]) -> str:
        """
        Encode a JWT token.

        Args:
            payload: Dictionary containing token claims (must include 'exp')

        Returns:
            Encoded JWT token
        """
        # Extract expires_in from exp claim if present
        if "exp" in payload:
            exp_timestamp = payload["exp"]
            now_timestamp = datetime.utcnow().timestamp()
            expires_in = int(exp_timestamp - now_timestamp)

            # Remove exp from payload (will be re-added by encode)
            payload_copy = {k: v for k, v in payload.items() if k != "exp"}
            return self.jwt_manager.encode(payload_copy, expires_in=max(1, expires_in))
        else:
            # Default 1 hour expiration
            return self.jwt_manager.encode(payload, expires_in=3600)

    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode a JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded payload dictionary
        """
        return self.jwt_manager.decode(token)


# Global JWT manager instance
_jwt_manager: Optional[SecureJWTManager] = None
_jwt_config = {
    "secret_key": None,
    "algorithm": "HS256",
    "access_token_expire_minutes": 15,
    "refresh_token_expire_days": 7,
}


def configure_jwt(
    secret_key: str,
    algorithm: str = "HS256",
    access_token_expire_minutes: int = 15,
    refresh_token_expire_days: int = 7,
) -> None:
    """
    Configure global JWT settings.

    Args:
        secret_key: Secret key for signing tokens
        algorithm: Algorithm to use (HS256, RS256, etc.)
        access_token_expire_minutes: Access token expiration in minutes
        refresh_token_expire_days: Refresh token expiration in days
    """
    global _jwt_manager, _jwt_config

    _jwt_config.update(
        {
            "secret_key": secret_key,
            "algorithm": algorithm,
            "access_token_expire_minutes": access_token_expire_minutes,
            "refresh_token_expire_days": refresh_token_expire_days,
        }
    )

    _jwt_manager = SecureJWTManager(secret_key=secret_key, algorithm=algorithm)


def create_access_token(
    subject: str,
    expires_in: Optional[int] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create an access token.

    Args:
        subject: Subject of the token (usually user ID)
        expires_in: Expiration time in seconds (if None, uses configured default)
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT access token

    Raises:
        RuntimeError: If JWT not configured (call configure_jwt first)

    Example:
        configure_jwt(secret_key="your-secret-key")
        token = create_access_token(subject="user123", expires_in=3600)
    """
    global _jwt_manager, _jwt_config

    if _jwt_manager is None:
        raise RuntimeError("JWT not configured. Call configure_jwt() first.")

    if expires_in is None:
        expires_in = _jwt_config["access_token_expire_minutes"] * 60

    payload = {"sub": subject, "type": "access"}

    if additional_claims:
        payload.update(additional_claims)

    return _jwt_manager.encode(payload, expires_in=expires_in)


def create_refresh_token(
    subject: str,
    expires_in: Optional[int] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a refresh token.

    Args:
        subject: Subject of the token (usually user ID)
        expires_in: Expiration time in seconds (if None, uses configured default)
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT refresh token

    Raises:
        RuntimeError: If JWT not configured
    """
    global _jwt_manager, _jwt_config

    if _jwt_manager is None:
        raise RuntimeError("JWT not configured. Call configure_jwt() first.")

    if expires_in is None:
        expires_in = _jwt_config["refresh_token_expire_days"] * 24 * 60 * 60

    payload = {"sub": subject, "type": "refresh"}

    if additional_claims:
        payload.update(additional_claims)

    return _jwt_manager.encode(payload, expires_in=expires_in)


def verify_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify
        verify_exp: Whether to verify expiration

    Returns:
        Decoded token payload

    Raises:
        RuntimeError: If JWT not configured
        ExpiredSignatureError: If token has expired
        InvalidTokenError: If token is invalid

    Example:
        try:
            payload = verify_token(token)
            user_id = payload["sub"]
        except ExpiredSignatureError:
            # Handle expired token
            pass
    """
    global _jwt_manager

    if _jwt_manager is None:
        raise RuntimeError("JWT not configured. Call configure_jwt() first.")

    return _jwt_manager.decode(token, verify_exp=verify_exp)


def revoke_token(token: str) -> bool:
    """
    Revoke a JWT token.

    Args:
        token: Token to revoke

    Returns:
        True if token was revoked

    Raises:
        RuntimeError: If JWT not configured
    """
    global _jwt_manager

    if _jwt_manager is None:
        raise RuntimeError("JWT not configured. Call configure_jwt() first.")

    return _jwt_manager.revoke_token(token)


# Custom exception classes for better error handling
class JWTError(Exception):
    """Base exception for JWT errors"""
    pass


class ExpiredTokenError(JWTError):
    """Token has expired"""
    pass


# Alias exceptions for compatibility
if HAS_PYJWT:
    # When PyJWT is available, also export its exceptions
    JWTError = InvalidTokenError  # Use PyJWT's exception as base
    ExpiredTokenError = ExpiredSignatureError


class SecureJWT:
    """
    Secure JWT implementation with blacklisting and enhanced security.

    Provides a simplified interface for JWT operations with security best practices.
    Compatible with test suite expectations.

    Example:
        secure_jwt = SecureJWT(secret="your-secret-key")
        token = secure_jwt.create_token({"user_id": "123"})
        claims = secure_jwt.verify_token(token)
        secure_jwt.blacklist_token(token)
    """

    def __init__(self, secret: str, algorithm: str = "HS256"):
        """
        Initialize SecureJWT with secret key.

        Args:
            secret: Secret key for signing tokens
            algorithm: Signing algorithm (default: HS256)
        """
        self._manager = SecureJWTManager(secret_key=secret, algorithm=algorithm)

    def create_token(
        self, payload: Dict[str, Any], expires_in: int = 3600
    ) -> str:
        """
        Create JWT token with payload.

        Args:
            payload: Dictionary of claims
            expires_in: Expiration time in seconds

        Returns:
            Encoded JWT token
        """
        return self._manager.encode(payload, expires_in=expires_in)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Decoded payload

        Raises:
            ExpiredTokenError: If token has expired
            JWTError: If token is invalid
        """
        try:
            return self._manager.decode(token)
        except ExpiredSignatureError as e:
            raise ExpiredTokenError(str(e))
        except InvalidTokenError as e:
            raise JWTError(str(e))

    def blacklist_token(self, token: str) -> bool:
        """
        Add token to blacklist.

        Args:
            token: Token to blacklist

        Returns:
            True if successful
        """
        return self._manager.revoke_token(token)


# Export all public APIs
__all__ = [
    "SecureJWTManager",
    "SecureJWT",
    "JWTAuth",
    "configure_jwt",
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "revoke_token",
    "InvalidTokenError",
    "ExpiredSignatureError",
    "JWTError",
    "ExpiredTokenError",
]
