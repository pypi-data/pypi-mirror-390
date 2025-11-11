"""
GraphQL Error Types

Custom error types with RFC 7807 problem details.
"""

from typing import Any, Dict, List, Optional


class GraphQLHTTPError(Exception):
    """Base GraphQL HTTP error with RFC 7807 format."""

    def __init__(
        self,
        message: str,
        status: int = 500,
        code: str = "INTERNAL_SERVER_ERROR",
        extensions: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize error.

        Args:
            message: Error message
            status: HTTP status code
            code: Error code
            extensions: Additional error data
        """
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.extensions = extensions or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        error_dict = {
            "type": f"https://errors.covetpy.dev/graphql/{self.code.lower()}",
            "title": self.code.replace("_", " ").title(),
            "status": self.status,
            "detail": self.message,
        }
        if self.extensions:
            error_dict["extensions"] = self.extensions
        return error_dict


class AuthenticationError(GraphQLHTTPError):
    """Authentication error (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status=401,
            code="UNAUTHENTICATED",
        )


class AuthorizationError(GraphQLHTTPError):
    """Authorization error (403)."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            status=403,
            code="FORBIDDEN",
        )


class ValidationError(GraphQLHTTPError):
    """Validation error (400)."""

    def __init__(self, message: str, field: Optional[str] = None):
        extensions = {}
        if field:
            extensions["field"] = field

        super().__init__(
            message=message,
            status=400,
            code="BAD_USER_INPUT",
            extensions=extensions,
        )


class NotFoundError(GraphQLHTTPError):
    """Not found error (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status=404,
            code="NOT_FOUND",
        )


class BadRequestError(GraphQLHTTPError):
    """Bad request error (400)."""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status=400,
            code="BAD_REQUEST",
        )


__all__ = [
    "GraphQLHTTPError",
    "AuthenticationError",
    "AuthorizationError",
    "ValidationError",
    "NotFoundError",
    "BadRequestError",
]
