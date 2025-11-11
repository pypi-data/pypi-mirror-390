"""
CovetPy Core Exceptions

Comprehensive exception hierarchy for the CovetPy framework providing
detailed error information and proper exception handling patterns.

SECURITY ENHANCEMENTS:
- Sanitized error responses
- Context sanitization
- Secure logging
- Information disclosure prevention
"""

from typing import Any, Optional

# Import security utilities
try:
    from covet.security.error_security import (
        get_security_config,
        sanitize_exception_context,
    )

    _SECURITY_AVAILABLE = True
except ImportError:
    _SECURITY_AVAILABLE = False


class CovetError(Exception):
    """
    Base exception for all CovetPy framework errors.

    Provides context information and error codes for better debugging
    and error handling in production systems.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        context: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.context = context or {}
        self.cause = cause

        super().__init__(self.message)

    def __str__(self) -> str:
        error_msg = f"[{self.error_code}] {self.message}"

        # In production, don't include context in string representation
        # (it may contain sensitive data)
        if _SECURITY_AVAILABLE:
            config = get_security_config()
            if not config.is_production and self.context:
                # Development: include sanitized context
                sanitized_context = sanitize_exception_context(self.context)
                error_msg += f" Context: {sanitized_context}"
        elif self.context:
            # Fallback if security module unavailable
            error_msg += f" Context: {self.context}"

        if self.cause:
            error_msg += f" Caused by: {type(self.cause).__name__}"

        return error_msg

    def to_dict(self, include_sensitive: bool = False) -> dict[str, Any]:
        """
        Convert exception to dictionary for serialization.

        SECURITY: Sanitizes context to prevent information disclosure.

        Args:
            include_sensitive: If False (default), sanitizes context.
                              Only set True in secure logging contexts.

        Returns:
            Dictionary representation of the exception
        """
        # Sanitize context before serialization
        if _SECURITY_AVAILABLE and not include_sensitive:
            sanitized_context = sanitize_exception_context(self.context)
        else:
            sanitized_context = self.context

        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": sanitized_context if self.context else None,
            "cause": type(self.cause).__name__ if self.cause else None,
            "type": self.__class__.__name__,
        }


class ConfigurationError(CovetError):
    """
    Raised when there are configuration-related errors.

    This includes missing configuration files, invalid values,
    environment variable issues, etc.
    """


class ContainerError(CovetError):
    """
    Raised when dependency injection container operations fail.

    This includes service registration failures, circular dependencies,
    missing dependencies, etc.
    """


class MiddlewareError(CovetError):
    """
    Raised when middleware processing encounters errors.

    This includes middleware initialization failures, execution errors,
    and pipeline configuration issues.
    """


class PluginError(CovetError):
    """
    Raised when plugin system operations fail.

    This includes plugin loading failures, dependency issues,
    initialization errors, etc.
    """


class ValidationError(CovetError):
    """
    Raised when input validation fails.

    This includes request validation, configuration validation,
    and data model validation errors.
    """


class AuthenticationError(CovetError):
    """
    Raised when authentication fails.

    This includes invalid credentials, token validation failures,
    and authentication provider errors.
    """


class AuthorizationError(CovetError):
    """
    Raised when authorization checks fail.

    This includes insufficient permissions, role validation failures,
    and access control errors.
    """


class DatabaseError(CovetError):
    """
    Raised when database operations fail.

    This includes connection failures, query errors,
    migration issues, etc.
    """


class NetworkError(CovetError):
    """
    Raised when network operations fail.

    This includes HTTP request failures, connection timeouts,
    service unavailability, etc.
    """


class SerializationError(CovetError):
    """
    Raised when serialization/deserialization fails.

    This includes JSON parsing errors, protocol buffer issues,
    and data format conversion errors.
    """


class RateLimitError(CovetError):
    """
    Raised when rate limiting is triggered.

    This includes API rate limiting, connection throttling,
    and resource usage limits.
    """

    def __init__(
        self,
        message: str,
        limit: int,
        window: int,
        retry_after: Optional[int] = None,
        **kwargs,
    ) -> None:
        self.limit = limit
        self.window = window
        self.retry_after = retry_after

        context = kwargs.get("context", {})
        context.update({"limit": limit, "window": window, "retry_after": retry_after})

        super().__init__(message, context=context, **kwargs)


class ServiceUnavailableError(CovetError):
    """
    Raised when a required service is unavailable.

    This includes external service downtime, dependency failures,
    and resource exhaustion.
    """


class SecurityError(CovetError):
    """
    Raised when security violations are detected.

    This includes security policy violations, suspicious activity,
    and potential attack attempts.
    """


class HTTPException(CovetError):
    """
    HTTP-specific exception with status code and headers.

    This is used for HTTP error responses with specific status codes,
    headers, and response bodies.
    """

    def __init__(
        self,
        status_code: int,
        detail: str = "Internal Server Error",
        headers: Optional[dict[str, str]] = None,
        **kwargs,
    ) -> None:
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}

        super().__init__(message=detail, error_code=f"HTTP_{status_code}", **kwargs)


# Exception handling utilities
def handle_exception(
    exception: Exception,
    context: Optional[dict[str, Any]] = None,
    reraise_as: Optional[type] = None,
) -> None:
    """
    Utility function for consistent exception handling.

    Args:
        exception: The original exception
        context: Additional context information
        reraise_as: Exception class to reraise as
    """
    if isinstance(exception, CovetError):
        # Already a CovetError, just update context if provided
        if context:
            exception.context.update(context)
        raise exception

    # Convert to CovetError or specified type
    error_class = reraise_as or CovetError
    raise error_class(message=str(exception), context=context, cause=exception)


def create_error_response(
    exception: CovetError,
    include_context: bool = False,
    include_traceback: bool = False,
) -> dict[str, Any]:
    """
    Create standardized error response dictionary with security hardening.

    SECURITY ENHANCEMENTS:
    - Sanitizes context to remove sensitive data
    - Sanitizes stack traces
    - Respects production environment settings

    Args:
        exception: The CovetError to convert
        include_context: Whether to include context information
        include_traceback: Whether to include stack trace

    Returns:
        Dictionary suitable for API error responses
    """
    import traceback

    # Get security config
    if _SECURITY_AVAILABLE:
        config = get_security_config()
        # Override include_traceback in production
        if config.is_production:
            include_traceback = False
    else:
        config = None

    response = {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "type": exception.__class__.__name__,
        }
    }

    if include_context and exception.context:
        # Sanitize context before including
        if _SECURITY_AVAILABLE:
            from covet.security.error_security import sanitize_exception_context

            response["error"]["context"] = sanitize_exception_context(exception.context)
        else:
            response["error"]["context"] = exception.context

    if include_traceback:
        tb = traceback.format_exc()
        # Sanitize stack trace
        if _SECURITY_AVAILABLE:
            from covet.security.error_security import sanitize_stack_trace

            response["error"]["traceback"] = sanitize_stack_trace(tb, config)
        else:
            response["error"]["traceback"] = tb

    return response
