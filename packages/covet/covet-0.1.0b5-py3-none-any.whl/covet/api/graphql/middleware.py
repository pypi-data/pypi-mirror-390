"""
GraphQL Middleware

Middleware for logging, performance tracking, and error handling.
"""

import logging
import time
from typing import Any, Callable, Optional

from strawberry.types import Info

logger = logging.getLogger(__name__)


class GraphQLMiddleware:
    """Base GraphQL middleware."""

    async def process(self, next: Callable, root: Any, info: Info, **kwargs) -> Any:
        """
        Process GraphQL request.

        Args:
            next: Next resolver in chain
            root: Root value
            info: GraphQL info
            **kwargs: Field arguments

        Returns:
            Resolver result
        """
        return await next(root, info, **kwargs)


class LoggingMiddleware(GraphQLMiddleware):
    """Logs GraphQL operations."""

    async def process(self, next: Callable, root: Any, info: Info, **kwargs) -> Any:
        """Log and execute resolver."""
        operation = info.operation.operation.value
        field_name = info.field_name

        logger.info(f"GraphQL {operation}: {field_name}")

        try:
            result = await next(root, info, **kwargs)
            return result
        except Exception as e:
            logger.error(f"GraphQL error in {field_name}: {str(e)}")
            raise


class PerformanceMiddleware(GraphQLMiddleware):
    """Tracks resolver performance."""

    def __init__(self, slow_threshold_ms: float = 100.0):
        """
        Initialize middleware.

        Args:
            slow_threshold_ms: Log warning if resolver takes longer
        """
        self.slow_threshold_ms = slow_threshold_ms

    async def process(self, next: Callable, root: Any, info: Info, **kwargs) -> Any:
        """Track and execute resolver."""
        start = time.time()

        try:
            result = await next(root, info, **kwargs)
            return result
        finally:
            duration_ms = (time.time() - start) * 1000

            if duration_ms > self.slow_threshold_ms:
                logger.warning(f"Slow resolver: {info.field_name} took {duration_ms:.2f}ms")


class ErrorHandlerMiddleware(GraphQLMiddleware):
    """Handles and formats errors."""

    async def process(self, next: Callable, root: Any, info: Info, **kwargs) -> Any:
        """Handle errors in resolver."""
        try:
            return await next(root, info, **kwargs)
        except PermissionError:
            # Re-raise permission errors
            raise
        except Exception:
            # Log unexpected errors
            logger.exception(f"Unexpected error in {info.field_name}")
            raise


class AuthMiddleware(GraphQLMiddleware):
    """Adds authentication context."""

    async def process(self, next: Callable, root: Any, info: Info, **kwargs) -> Any:
        """Add auth context and execute."""
        # Auth context should be added by ASGI middleware
        # This middleware just ensures it's available

        if not hasattr(info.context, "user"):
            logger.warning("No auth context in GraphQL request")

        return await next(root, info, **kwargs)


__all__ = [
    "GraphQLMiddleware",
    "LoggingMiddleware",
    "PerformanceMiddleware",
    "ErrorHandlerMiddleware",
    "AuthMiddleware",
]
