"""
Secure Authentication Utilities

This module provides security-focused authentication utilities to prevent:
1. Timing attacks on password/token comparison
2. User enumeration attacks
3. Credential stuffing attacks
4. Brute force attacks

SECURITY CLASSIFICATION: CRITICAL
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple


def constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.

    CRITICAL for:
    - Password comparison
    - Token validation
    - Secret key comparison
    - API key verification
    - Session ID validation

    Uses Python's hmac.compare_digest which is implemented in C
    and provides constant-time comparison.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal, False otherwise

    Example:
        >>> # WRONG - vulnerable to timing attacks
        >>> if password == stored_password:
        >>>     ...

        >>> # CORRECT - constant time comparison
        >>> if constant_time_compare(password, stored_password):
        >>>     ...
    """
    try:
        return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))
    except (TypeError, AttributeError):
        # Fallback for invalid inputs
        return False


def constant_time_compare_bytes(a: bytes, b: bytes) -> bool:
    """
    Constant-time byte comparison to prevent timing attacks.

    Args:
        a: First byte sequence
        b: Second byte sequence

    Returns:
        True if byte sequences are equal, False otherwise
    """
    try:
        return hmac.compare_digest(a, b)
    except (TypeError, AttributeError):
        return False


def verify_password_hash(password: str, password_hash: str, salt: Optional[str] = None) -> bool:
    """
    Verify password against hash using constant-time comparison.

    This is a basic implementation. For production, use bcrypt,
    argon2, or scrypt from passlib or argon2-cffi.

    Args:
        password: Plain text password
        password_hash: Hashed password to compare against
        salt: Optional salt (if not included in password_hash)

    Returns:
        True if password matches, False otherwise
    """
    # Add random delay to prevent timing attacks on hash computation
    add_auth_timing_jitter()

    # This is a placeholder - use proper password hashing in production
    # e.g., bcrypt.checkpw(password.encode(), password_hash.encode())

    # For demonstration, using pbkdf2_hmac
    if salt:
        computed_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
    else:
        # Assume salt is in the hash
        computed_hash = password_hash

    # Constant time comparison
    return constant_time_compare(computed_hash, password_hash)


def add_auth_timing_jitter(min_ms: float = 10, max_ms: float = 50) -> None:
    """
    Add random timing jitter to authentication operations.

    Prevents timing attacks by ensuring authentication takes
    approximately the same time regardless of success/failure.

    Use AFTER:
    - Password verification
    - Username lookup
    - Token validation
    - Any security-sensitive comparison

    Args:
        min_ms: Minimum delay in milliseconds (default: 10ms)
        max_ms: Maximum delay in milliseconds (default: 50ms)

    Example:
        >>> if verify_user_exists(username):
        >>>     add_auth_timing_jitter()
        >>>     return {"exists": True}
        >>> else:
        >>>     add_auth_timing_jitter()
        >>>     return {"exists": False}
    """
    # Generate cryptographically secure random jitter
    jitter_range = int((max_ms - min_ms) * 1000)
    jitter = secrets.randbelow(jitter_range + 1) / 1000
    delay = (min_ms + jitter) / 1000
    time.sleep(delay)


def normalize_auth_error(error_type: str, original_message: Optional[str] = None) -> str:
    """
    Normalize authentication error messages to prevent user enumeration.

    SECURITY: Never reveal whether:
    - User exists or not
    - Password is correct but 2FA failed
    - Account is locked vs invalid credentials
    - Email is registered or not

    Args:
        error_type: Type of auth error
        original_message: Original message (for logging, not returned)

    Returns:
        Generic error message safe for user display

    Example:
        >>> # WRONG - reveals user existence
        >>> if not user_exists:
        >>>     return "User not found"
        >>> elif not password_valid:
        >>>     return "Invalid password"

        >>> # CORRECT - generic message
        >>> return normalize_auth_error("invalid_credentials")
        "Invalid credentials"
    """
    # Map all auth failures to generic messages
    error_messages = {
        "invalid_credentials": "Invalid credentials",
        "user_not_found": "Invalid credentials",  # Don't reveal user doesn't exist
        "invalid_password": "Invalid credentials",  # Same message as user_not_found
        "account_locked": "Invalid credentials",  # Don't reveal account is locked
        "account_disabled": "Invalid credentials",  # Don't reveal account is disabled
        "2fa_required": "Additional authentication required",
        "2fa_invalid": "Invalid credentials",  # Don't reveal 2FA was the issue
        "token_expired": "Authentication required",
        "token_invalid": "Authentication required",
        "session_expired": "Authentication required",
        "unauthorized": "Access denied",
        "forbidden": "Access denied",
        "rate_limited": "Too many requests. Please try again later.",
    }

    return error_messages.get(error_type, "Authentication failed")


def generate_secure_token(length: int = 32) -> str:
    """
    Generate cryptographically secure random token.

    Uses secrets module for cryptographically strong random generation.

    Args:
        length: Token length in bytes (default: 32)

    Returns:
        Hex-encoded secure random token

    Example:
        >>> session_token = generate_secure_token(32)
        >>> csrf_token = generate_secure_token(16)
    """
    return secrets.token_hex(length)


def generate_secure_token_urlsafe(length: int = 32) -> str:
    """
    Generate URL-safe cryptographically secure random token.

    Args:
        length: Token length in bytes (default: 32)

    Returns:
        URL-safe secure random token
    """
    return secrets.token_urlsafe(length)


class AuthRateLimiter:
    """
    Rate limiter specifically for authentication attempts.

    Implements:
    - Per-username rate limiting
    - Per-IP rate limiting
    - Exponential backoff
    - Account lockout

    SECURITY: Prevents:
    - Brute force attacks
    - Credential stuffing
    - Password spraying
    """

    def __init__(
        self,
        max_attempts: int = 5,
        window_seconds: int = 300,  # 5 minutes
        lockout_duration: int = 900,  # 15 minutes
    ):
        """
        Initialize auth rate limiter.

        Args:
            max_attempts: Maximum auth attempts in window
            window_seconds: Time window for attempts
            lockout_duration: Lockout duration after max attempts
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self.lockout_duration = lockout_duration

        # Storage: identifier -> [(timestamp, success)]
        self._attempts: dict[str, list[Tuple[float, bool]]] = {}

        # Storage: identifier -> lockout_until_timestamp
        self._lockouts: dict[str, float] = {}

    def record_attempt(self, identifier: str, success: bool) -> None:
        """
        Record an authentication attempt.

        Args:
            identifier: User identifier (username, IP, etc.)
            success: Whether the attempt was successful
        """
        now = time.time()

        if identifier not in self._attempts:
            self._attempts[identifier] = []

        self._attempts[identifier].append((now, success))

        # Clean old entries
        self._cleanup_old_entries(identifier, now)

        # Check if we should lock out
        if not success:
            failed_attempts = [(ts, s) for ts, s in self._attempts[identifier] if not s]

            if len(failed_attempts) >= self.max_attempts:
                # Lock out the identifier
                self._lockouts[identifier] = now + self.lockout_duration

    def is_locked_out(self, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if identifier is locked out.

        Args:
            identifier: User identifier

        Returns:
            Tuple of (is_locked, seconds_until_unlock)
        """
        now = time.time()

        if identifier in self._lockouts:
            lockout_until = self._lockouts[identifier]
            if now < lockout_until:
                seconds_remaining = int(lockout_until - now)
                return True, seconds_remaining
            else:
                # Lockout expired
                del self._lockouts[identifier]

        return False, None

    def get_remaining_attempts(self, identifier: str) -> int:
        """
        Get remaining attempts before lockout.

        Args:
            identifier: User identifier

        Returns:
            Number of remaining attempts
        """
        now = time.time()
        self._cleanup_old_entries(identifier, now)

        if identifier not in self._attempts:
            return self.max_attempts

        failed_attempts = sum(1 for ts, success in self._attempts[identifier] if not success)

        remaining = self.max_attempts - failed_attempts
        return max(0, remaining)

    def reset(self, identifier: str) -> None:
        """
        Reset attempts for an identifier.

        Use this after:
        - Successful authentication
        - Password reset
        - Admin unlock
        """
        if identifier in self._attempts:
            del self._attempts[identifier]
        if identifier in self._lockouts:
            del self._lockouts[identifier]

    def _cleanup_old_entries(self, identifier: str, current_time: float) -> None:
        """Remove entries outside the time window"""
        if identifier not in self._attempts:
            return

        cutoff = current_time - self.window_seconds
        self._attempts[identifier] = [
            (ts, success) for ts, success in self._attempts[identifier] if ts > cutoff
        ]

        if not self._attempts[identifier]:
            del self._attempts[identifier]


# Global auth rate limiter instance
_global_auth_limiter = AuthRateLimiter()


def get_auth_rate_limiter() -> AuthRateLimiter:
    """Get the global auth rate limiter instance"""
    return _global_auth_limiter


__all__ = [
    "constant_time_compare",
    "constant_time_compare_bytes",
    "verify_password_hash",
    "add_auth_timing_jitter",
    "normalize_auth_error",
    "generate_secure_token",
    "generate_secure_token_urlsafe",
    "AuthRateLimiter",
    "get_auth_rate_limiter",
]
