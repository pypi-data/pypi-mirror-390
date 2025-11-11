"""
Error Handling Middleware for CovetPy
======================================

Provides comprehensive error handling middleware that catches all uncaught exceptions
and returns appropriate HTTP error responses without leaking internal details.

Features:
- Catches all uncaught exceptions
- Returns appropriate status codes (400, 401, 403, 404, 500, etc.)
- Logs errors with stack traces for debugging
- Prevents information leakage to clients
- Supports custom error handlers per exception type
- Production-safe error messages

Usage:
    from covet import Covet
    from covet.middleware.error_handler import error_handling_middleware

    app = Covet()
    app.middleware('http')(error_handling_middleware)
"""

import logging
import traceback
from typing import Callable, Dict, Type, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class HTTPException(Exception):
    """Base HTTP exception with status code."""

    def __init__(self, status_code: int, detail: str, headers: Optional[Dict[str, str]] = None):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers or {}
        super().__init__(detail)


class ValidationError(HTTPException):
    """400 Bad Request - Validation error."""

    def __init__(self, detail: str, headers: Optional[Dict[str, str]] = None):
        super().__init__(400, detail, headers)


class UnauthorizedError(HTTPException):
    """401 Unauthorized - Authentication required."""

    def __init__(self, detail: str = "Unauthorized", headers: Optional[Dict[str, str]] = None):
        super().__init__(401, detail, headers)


class ForbiddenError(HTTPException):
    """403 Forbidden - Insufficient permissions."""

    def __init__(self, detail: str = "Forbidden", headers: Optional[Dict[str, str]] = None):
        super().__init__(403, detail, headers)


class NotFoundError(HTTPException):
    """404 Not Found - Resource not found."""

    def __init__(self, detail: str = "Not Found", headers: Optional[Dict[str, str]] = None):
        super().__init__(404, detail, headers)


class ConflictError(HTTPException):
    """409 Conflict - Resource conflict (e.g., duplicate)."""

    def __init__(self, detail: str = "Conflict", headers: Optional[Dict[str, str]] = None):
        super().__init__(409, detail, headers)


class InternalServerError(HTTPException):
    """500 Internal Server Error."""

    def __init__(self, detail: str = "Internal Server Error", headers: Optional[Dict[str, str]] = None):
        super().__init__(500, detail, headers)


class ErrorHandler:
    """
    Error handler with custom exception mappings.

    Allows registration of custom error handlers for specific exception types.
    """

    def __init__(self):
        """Initialize error handler with default mappings."""
        self.handlers: Dict[Type[Exception], Callable] = {}
        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Set up default exception handlers."""
        # HTTPException and subclasses
        self.register(HTTPException, self._handle_http_exception)

        # Validation errors
        self.register(ValueError, self._handle_validation_error)

        # Database errors
        self.register(RuntimeError, self._handle_runtime_error)

        # JSON decode errors
        try:
            import json
            self.register(json.JSONDecodeError, self._handle_json_error)
        except ImportError:
            pass

    def register(self, exception_type: Type[Exception], handler: Callable):
        """
        Register a custom error handler.

        Args:
            exception_type: Exception class to handle
            handler: Function that takes (exception, request) and returns Response
        """
        self.handlers[exception_type] = handler

    async def handle(self, exc: Exception, request) -> Dict[str, Any]:
        """
        Handle exception and return error response data.

        Args:
            exc: Exception to handle
            request: Request object

        Returns:
            Dict with error response data including status_code and body
        """
        # Check for exact match first
        handler = self.handlers.get(type(exc))

        # If no exact match, check inheritance
        if not handler:
            for exc_type, exc_handler in self.handlers.items():
                if isinstance(exc, exc_type):
                    handler = exc_handler
                    break

        # Use default handler if no match found
        if not handler:
            handler = self._handle_generic_error

        return await handler(exc, request)

    async def _handle_http_exception(self, exc: HTTPException, request) -> Dict[str, Any]:
        """Handle HTTPException and subclasses."""
        return {
            'status_code': exc.status_code,
            'body': {
                'error': exc.detail,
                'status': exc.status_code,
                'timestamp': datetime.utcnow().isoformat()
            },
            'headers': exc.headers
        }

    async def _handle_validation_error(self, exc: ValueError, request) -> Dict[str, Any]:
        """Handle validation errors (ValueError)."""
        logger.warning(f"Validation error: {exc}")
        return {
            'status_code': 400,
            'body': {
                'error': str(exc),
                'status': 400,
                'timestamp': datetime.utcnow().isoformat()
            },
            'headers': {}
        }

    async def _handle_runtime_error(self, exc: RuntimeError, request) -> Dict[str, Any]:
        """Handle runtime errors (database, connection, etc.)."""
        logger.error(f"Runtime error: {exc}", exc_info=True)
        return {
            'status_code': 500,
            'body': {
                'error': 'Internal server error',
                'status': 500,
                'timestamp': datetime.utcnow().isoformat()
            },
            'headers': {}
        }

    async def _handle_json_error(self, exc: Exception, request) -> Dict[str, Any]:
        """Handle JSON decode errors."""
        logger.warning(f"JSON decode error: {exc}")
        return {
            'status_code': 400,
            'body': {
                'error': 'Invalid JSON in request body',
                'status': 400,
                'timestamp': datetime.utcnow().isoformat()
            },
            'headers': {}
        }

    async def _handle_generic_error(self, exc: Exception, request) -> Dict[str, Any]:
        """Handle all other uncaught exceptions."""
        # Log with full stack trace
        logger.error(
            f"Uncaught exception: {type(exc).__name__}: {exc}",
            exc_info=True,
            extra={
                'exception_type': type(exc).__name__,
                'exception_message': str(exc),
                'traceback': traceback.format_exc(),
                'request_path': getattr(request, 'path', 'unknown'),
                'request_method': getattr(request, 'method', 'unknown'),
            }
        )

        # Don't leak internal details to client
        return {
            'status_code': 500,
            'body': {
                'error': 'Internal server error',
                'status': 500,
                'timestamp': datetime.utcnow().isoformat()
            },
            'headers': {}
        }


# Global error handler instance
_error_handler = ErrorHandler()


def register_error_handler(exception_type: Type[Exception], handler: Callable):
    """
    Register a custom error handler globally.

    Args:
        exception_type: Exception class to handle
        handler: Async function that takes (exception, request) and returns Response
    """
    _error_handler.register(exception_type, handler)


async def error_handling_middleware(request, call_next):
    """
    Error handling middleware for CovetPy applications.

    Catches all uncaught exceptions and returns appropriate error responses.

    Args:
        request: Incoming request
        call_next: Next middleware/handler in chain

    Returns:
        Response object

    Usage:
        app.middleware('http')(error_handling_middleware)
    """
    try:
        # Process request through middleware chain
        response = await call_next(request)
        return response

    except Exception as exc:
        # Handle exception
        error_data = await _error_handler.handle(exc, request)

        # Import Response here to avoid circular imports
        from ..core import Response

        # Create error response
        import json
        response = Response(
            content=json.dumps(error_data['body']),
            status_code=error_data['status_code'],
            media_type='application/json'
        )

        # Add custom headers if any
        for key, value in error_data.get('headers', {}).items():
            response.headers[key] = value

        return response


__all__ = [
    'error_handling_middleware',
    'ErrorHandler',
    'register_error_handler',
    'HTTPException',
    'ValidationError',
    'UnauthorizedError',
    'ForbiddenError',
    'NotFoundError',
    'ConflictError',
    'InternalServerError',
]
