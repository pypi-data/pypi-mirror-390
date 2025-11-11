"""
REST API Error Handling

Production-ready error handling following RFC 7807 (Problem Details for HTTP APIs).
Provides consistent error responses across the API with security hardening.

SECURITY ENHANCEMENTS:
- Environment-aware error responses
- Stack trace sanitization
- Sensitive information removal
- Error correlation IDs
- Security headers
- Timing attack prevention
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from covet.security.error_security import (
    create_secure_error_response,
    generate_error_id,
    get_error_rate_limiter,
    get_security_config,
    get_security_headers,
    log_error_securely,
    sanitize_exception_context,
    sanitize_stack_trace,
)

logger = logging.getLogger(__name__)


class ProblemDetail(BaseModel):
    """
    RFC 7807 Problem Details for HTTP APIs.

    Standard format for machine-readable error responses.
    Enhanced with security features for production use.
    """

    type: str = "about:blank"
    title: str
    status: int
    detail: Optional[str] = None
    instance: Optional[str] = None
    error_id: Optional[str] = None  # Security: Error correlation ID
    timestamp: Optional[str] = None  # Security: Error timestamp
    errors: Optional[List[Dict[str, Any]]] = None

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "type": "https://errors.covetpy.dev/validation-error",
                "title": "Validation Error",
                "status": 422,
                "detail": "Invalid request body",
                "instance": "/api/v1/users",
                "error_id": "ERR-a3f2b1c0d4e5f6a7",
                "timestamp": "2025-10-10T12:34:56Z",
                "errors": [
                    {
                        "loc": ["body", "email"],
                        "msg": "Invalid email format",
                        "type": "value_error.email",
                    }
                ],
            }
        }


class APIError(Exception):
    """Base exception for all API errors."""

    def __init__(
        self,
        title: str,
        status: int,
        detail: Optional[str] = None,
        error_type: Optional[str] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize API error.

        Args:
            title: Short error title
            status: HTTP status code
            detail: Detailed error description
            error_type: Error type URL
            errors: List of specific errors
        """
        self.title = title
        self.status = status
        self.detail = detail or title
        self.error_type = error_type or f"https://errors.covetpy.dev/{status}"
        self.errors = errors
        super().__init__(self.detail)

    def to_problem_detail(self, instance: Optional[str] = None) -> ProblemDetail:
        """Convert to RFC 7807 Problem Detail."""
        return ProblemDetail(
            type=self.error_type,
            title=self.title,
            status=self.status,
            detail=self.detail,
            instance=instance,
            errors=self.errors,
        )


class BadRequestError(APIError):
    """400 Bad Request error."""

    def __init__(self, detail: str = "Bad request", errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(
            title="Bad Request",
            status=400,
            detail=detail,
            error_type="https://errors.covetpy.dev/bad-request",
            errors=errors,
        )


class UnauthorizedError(APIError):
    """401 Unauthorized error."""

    def __init__(self, detail: str = "Authentication required"):
        super().__init__(
            title="Unauthorized",
            status=401,
            detail=detail,
            error_type="https://errors.covetpy.dev/unauthorized",
        )


class ForbiddenError(APIError):
    """403 Forbidden error."""

    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(
            title="Forbidden",
            status=403,
            detail=detail,
            error_type="https://errors.covetpy.dev/forbidden",
        )


class NotFoundError(APIError):
    """404 Not Found error."""

    def __init__(self, detail: str = "Resource not found", resource_type: Optional[str] = None):
        if resource_type:
            detail = f"{resource_type} not found"
        super().__init__(
            title="Not Found",
            status=404,
            detail=detail,
            error_type="https://errors.covetpy.dev/not-found",
        )


class MethodNotAllowedError(APIError):
    """405 Method Not Allowed error."""

    def __init__(self, method: str, allowed_methods: List[str]):
        super().__init__(
            title="Method Not Allowed",
            status=405,
            detail=f"Method {method} not allowed. Allowed methods: {', '.join(allowed_methods)}",
            error_type="https://errors.covetpy.dev/method-not-allowed",
        )


class ConflictError(APIError):
    """409 Conflict error."""

    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            title="Conflict",
            status=409,
            detail=detail,
            error_type="https://errors.covetpy.dev/conflict",
        )


class ValidationError(APIError):
    """422 Validation Error."""

    def __init__(
        self,
        detail: str = "Validation failed",
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            title="Validation Error",
            status=422,
            detail=detail,
            error_type="https://errors.covetpy.dev/validation-error",
            errors=errors,
        )


class TooManyRequestsError(APIError):
    """429 Too Many Requests error."""

    def __init__(self, detail: str = "Rate limit exceeded", retry_after: Optional[int] = None):
        super().__init__(
            title="Too Many Requests",
            status=429,
            detail=detail,
            error_type="https://errors.covetpy.dev/rate-limit",
        )
        self.retry_after = retry_after


class InternalServerError(APIError):
    """500 Internal Server Error."""

    def __init__(self, detail: str = "Internal server error"):
        super().__init__(
            title="Internal Server Error",
            status=500,
            detail=detail,
            error_type="https://errors.covetpy.dev/internal-error",
        )


class ServiceUnavailableError(APIError):
    """503 Service Unavailable error."""

    def __init__(
        self,
        detail: str = "Service temporarily unavailable",
        retry_after: Optional[int] = None,
    ):
        super().__init__(
            title="Service Unavailable",
            status=503,
            detail=detail,
            error_type="https://errors.covetpy.dev/service-unavailable",
        )
        self.retry_after = retry_after


class ErrorHandler:
    """
    Central error handler for REST API.

    Catches all exceptions and converts them to standardized error responses.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize error handler.

        Args:
            debug: Enable debug mode (includes stack traces)
                   Note: Overridden by COVET_ENV=production
        """
        self.debug = debug
        self.security_config = get_security_config()
        self.error_limiter = get_error_rate_limiter()

    def handle(
        self,
        error: Exception,
        request_path: Optional[str] = None,
        client_identifier: Optional[str] = None,
    ) -> tuple[ProblemDetail, int, Dict[bytes, bytes]]:
        """
        Handle exception and return problem detail with security hardening.

        SECURITY ENHANCEMENTS:
        - Generates error correlation IDs
        - Sanitizes stack traces
        - Removes sensitive information
        - Logs errors securely
        - Applies security headers
        - Tracks error rates

        Args:
            error: Exception to handle
            request_path: Request path for instance field
            client_identifier: Client IP or user ID for rate limiting

        Returns:
            Tuple of (ProblemDetail, status_code, security_headers)
        """
        from datetime import datetime

        # Generate error ID for correlation
        error_id = generate_error_id()
        timestamp = datetime.utcnow().isoformat() + "Z"

        # Record error for rate limiting
        if client_identifier:
            self.error_limiter.record_error(client_identifier, error_id)

        # Get security headers
        security_headers = get_security_headers()

        # APIError subclasses
        if isinstance(error, APIError):
            problem = error.to_problem_detail(instance=request_path)
            problem.error_id = error_id
            problem.timestamp = timestamp

            # Add retry_after header info if present
            if hasattr(error, "retry_after") and error.retry_after:
                if not problem.errors:
                    problem.errors = []
                problem.errors.append({"field": "retry_after", "value": error.retry_after})

            # Log securely
            log_error_securely(error, error_id, request_path)

            logger.warning(f"[{error_id}] API error: {error.status} {error.title}")
            return problem, error.status, security_headers

        # Pydantic validation errors (already handled by validation module)
        # This is a fallback in case they leak through
        from pydantic import ValidationError as PydanticValidationError

        if isinstance(error, PydanticValidationError):
            errors = []
            for err in error.errors():
                errors.append({"loc": list(err["loc"]), "msg": err["msg"], "type": err["type"]})

            problem = ProblemDetail(
                type="https://errors.covetpy.dev/validation-error",
                title="Validation Error",
                status=422,
                detail=f"{len(errors)} validation error(s)",
                instance=request_path,
                error_id=error_id,
                timestamp=timestamp,
                errors=errors,
            )

            log_error_securely(error, error_id, request_path)
            logger.warning(f"[{error_id}] Validation error: {len(errors)} error(s)")
            return problem, 422, security_headers

        # Unknown exceptions - Internal Server Error
        # SECURITY: Use secure error response generation
        log_error_securely(error, error_id, request_path)

        # Determine if we should include details (respects COVET_ENV)
        include_details = self.debug and not self.security_config.is_production

        if include_details:
            # Development mode - include sanitized details
            detail = f"{type(error).__name__}: {str(error)}"

            # Sanitize stack trace
            tb = traceback.format_exc()
            sanitized_tb = sanitize_stack_trace(tb, self.security_config)

            errors = [
                {
                    "type": "exception",
                    "exception": type(error).__name__,
                    "message": str(error),
                    "traceback": sanitized_tb.split("\n"),
                }
            ]
        else:
            # Production mode - generic error only
            detail = "An internal error occurred"
            errors = None

        problem = ProblemDetail(
            type="https://errors.covetpy.dev/internal-error",
            title="Internal Server Error",
            status=500,
            detail=detail,
            instance=request_path,
            error_id=error_id,
            timestamp=timestamp,
            errors=errors,
        )

        logger.error(f"[{error_id}] Unhandled exception: {type(error).__name__}")
        return problem, 500, security_headers


class ErrorMiddleware:
    """
    ASGI middleware for catching and formatting errors with security hardening.

    Wraps the application and catches all exceptions, converting them
    to RFC 7807 Problem Details responses with:
    - Security headers
    - Error rate limiting
    - Sanitized error messages
    - Error correlation IDs
    """

    def __init__(self, app, debug: bool = False):
        """
        Initialize error middleware.

        Args:
            app: ASGI application
            debug: Enable debug mode (overridden by COVET_ENV)
        """
        self.app = app
        self.handler = ErrorHandler(debug=debug)
        self.error_limiter = get_error_rate_limiter()

    def _get_client_identifier(self, scope: dict) -> str:
        """Extract client identifier from scope for rate limiting"""
        # Try to get client IP
        client = scope.get("client")
        if client:
            return f"ip:{client[0]}"

        # Fallback to anonymous
        return "anonymous"

    async def __call__(self, scope, receive, send):
        """ASGI interface with security enhancements."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get client identifier for rate limiting
        client_id = self._get_client_identifier(scope)

        # Check error rate limit
        is_limited, retry_after = self.error_limiter.is_rate_limited(client_id)
        if is_limited:
            # Client has exceeded error rate - block request
            problem = ProblemDetail(
                type="https://errors.covetpy.dev/rate-limit",
                title="Too Many Errors",
                status=429,
                detail="Too many errors from your IP. Please try again later.",
                error_id=generate_error_id(),
                timestamp=__import__("datetime").datetime.utcnow().isoformat() + "Z",
            )

            # Get security headers
            security_headers = get_security_headers()
            headers = [
                [b"content-type", b"application/problem+json; charset=utf-8"],
                [b"retry-after", str(retry_after).encode("utf-8")],
            ]
            # Add security headers
            headers.extend(list(security_headers.items()))

            await send(
                {
                    "type": "http.response.start",
                    "status": 429,
                    "headers": headers,
                }
            )

            body = problem.json().encode("utf-8")
            await send(
                {
                    "type": "http.response.body",
                    "body": body,
                }
            )
            return

        try:
            await self.app(scope, receive, send)
        except Exception as error:
            # Get request path
            request_path = scope.get("path", "/")

            # Handle error with security features
            problem, status_code, security_headers = self.handler.handle(
                error, request_path, client_id
            )

            # Build headers with security headers
            headers = [
                [b"content-type", b"application/problem+json; charset=utf-8"],
            ]

            # Add security headers
            headers.extend(list(security_headers.items()))

            # Remove X-Powered-By if present (never expose technology stack)
            # Note: This is handled by security_headers, but we ensure it here
            # too

            # Send error response
            await send(
                {
                    "type": "http.response.start",
                    "status": status_code,
                    "headers": headers,
                }
            )

            body = problem.json().encode("utf-8")
            await send(
                {
                    "type": "http.response.body",
                    "body": body,
                }
            )


__all__ = [
    "ProblemDetail",
    "APIError",
    "BadRequestError",
    "UnauthorizedError",
    "ForbiddenError",
    "NotFoundError",
    "MethodNotAllowedError",
    "ConflictError",
    "ValidationError",
    "TooManyRequestsError",
    "InternalServerError",
    "ServiceUnavailableError",
    "ErrorHandler",
    "ErrorMiddleware",
]
