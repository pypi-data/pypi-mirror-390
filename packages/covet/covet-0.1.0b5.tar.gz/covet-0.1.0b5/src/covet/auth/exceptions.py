"""
Authentication and Authorization Exceptions

Secure exception handling with minimal information disclosure
to prevent enumeration attacks.
"""

from typing import Any, Dict, Optional


class AuthException(Exception):
    """Base authentication exception"""

    def __init__(self, message: str, code: str = "AUTH_ERROR", status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


class InvalidCredentialsError(AuthException):
    """Invalid username/password - generic message to prevent enumeration"""

    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, "INVALID_CREDENTIALS", 401)


class TokenExpiredError(AuthException):
    """JWT or session token has expired"""

    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "TOKEN_EXPIRED", 401)


class TokenInvalidError(AuthException):
    """JWT token is invalid or malformed"""

    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, "TOKEN_INVALID", 401)


class PermissionDeniedError(AuthException):
    """User lacks required permissions"""

    def __init__(
        self,
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
    ):
        super().__init__(message, "PERMISSION_DENIED", 403)
        self.required_permission = required_permission


class RoleRequiredError(AuthException):
    """User lacks required role"""

    def __init__(
        self,
        message: str = "Required role missing",
        required_role: Optional[str] = None,
    ):
        super().__init__(message, "ROLE_REQUIRED", 403)
        self.required_role = required_role


class TwoFactorRequiredError(AuthException):
    """2FA verification required"""

    def __init__(self, message: str = "Two-factor authentication required"):
        super().__init__(message, "TWO_FACTOR_REQUIRED", 401)


class TwoFactorInvalidError(AuthException):
    """Invalid 2FA code"""

    def __init__(self, message: str = "Invalid two-factor authentication code"):
        super().__init__(message, "TWO_FACTOR_INVALID", 401)


class AccountLockedError(AuthException):
    """Account is locked due to too many failed attempts"""

    def __init__(
        self,
        message: str = "Account is temporarily locked",
        lockout_until: Optional[int] = None,
    ):
        super().__init__(message, "ACCOUNT_LOCKED", 423)
        self.lockout_until = lockout_until


class PasswordResetRequiredError(AuthException):
    """Password reset is required"""

    def __init__(self, message: str = "Password reset required"):
        super().__init__(message, "PASSWORD_RESET_REQUIRED", 401)


class OAuth2Error(AuthException):
    """OAuth2 authentication error"""

    def __init__(
        self,
        message: str,
        error_code: str = "oauth2_error",
        provider: Optional[str] = None,
    ):
        super().__init__(message, error_code.upper(), 401)
        self.provider = provider


class SessionExpiredError(AuthException):
    """Session has expired"""

    def __init__(self, message: str = "Session has expired"):
        super().__init__(message, "SESSION_EXPIRED", 401)


class RateLimitExceededError(AuthException):
    """Rate limit exceeded for authentication attempts"""

    def __init__(self, message: str = "Too many requests", retry_after: Optional[int] = None):
        super().__init__(message, "RATE_LIMIT_EXCEEDED", 429)
        self.retry_after = retry_after


class SecurityViolationError(AuthException):
    """Security policy violation detected"""

    def __init__(
        self,
        message: str = "Security violation detected",
        violation_type: Optional[str] = None,
    ):
        super().__init__(message, "SECURITY_VIOLATION", 403)
        self.violation_type = violation_type


def to_dict(exception: AuthException) -> Dict[str, Any]:
    """Convert exception to secure dictionary for API responses"""
    result = {
        "error": exception.code,
        "message": exception.message,
        "status_code": exception.status_code,
    }

    # Add specific fields for certain exceptions
    if isinstance(exception, PermissionDeniedError) and exception.required_permission:
        result["required_permission"] = exception.required_permission
    elif isinstance(exception, RoleRequiredError) and exception.required_role:
        result["required_role"] = exception.required_role
    elif isinstance(exception, AccountLockedError) and exception.lockout_until:
        result["lockout_until"] = exception.lockout_until
    elif isinstance(exception, OAuth2Error) and exception.provider:
        result["provider"] = exception.provider
    elif isinstance(exception, RateLimitExceededError) and exception.retry_after:
        result["retry_after"] = exception.retry_after
    elif isinstance(exception, SecurityViolationError) and exception.violation_type:
        result["violation_type"] = exception.violation_type

    return result
