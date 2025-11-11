"""
Circuit Breaker Pattern Implementation for Database Adapters

Implements fail-fast behavior to prevent cascading failures when database is down.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject all requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening circuit
    timeout: float = 60.0  # Seconds before attempting recovery
    success_threshold: int = 2  # Successes in half-open before closing
    half_open_max_calls: int = 3  # Max calls allowed in half-open state


class CircuitBreaker:
    """
    Circuit breaker for database operations.

    Prevents cascading failures by failing fast when the database is unavailable.

    States:
    - CLOSED: Normal operation, all requests pass through
    - OPEN: Too many failures, all requests fail immediately
    - HALF_OPEN: Testing recovery, limited requests allowed

    Example:
        breaker = CircuitBreaker()

        @breaker.call
        async def database_operation():
            return await adapter.execute("SELECT 1")

        try:
            result = await database_operation()
        except CircuitBreakerOpen:
            # Circuit is open, service unavailable
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        """
        Initialize circuit breaker.

        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerOpen: If circuit is open
            Exception: Original exception from function
        """
        async with self._lock:
            # Check if we should attempt the call
            if self.state == CircuitState.OPEN:
                # Check if timeout has elapsed
                if (time.time() - self.last_failure_time) >= self.config.timeout:
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    self.success_count = 0
                else:
                    raise CircuitBreakerOpen(
                        f"Circuit breaker is OPEN. "
                        f"Retry after {self.config.timeout - (time.time() - self.last_failure_time):.1f}s"
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen("Circuit breaker is HALF_OPEN and max calls exceeded")
                self.half_open_calls += 1

        # Execute the function
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result

        except Exception:
            await self._on_failure()
            raise

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            self.failure_count = 0

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    logger.info("Circuit breaker transitioning to CLOSED")
                    self.state = CircuitState.CLOSED
                    self.success_count = 0
                    self.half_open_calls = 0

    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.state == CircuitState.HALF_OPEN:
                logger.warning("Circuit breaker transitioning to OPEN (failure in HALF_OPEN)")
                self.state = CircuitState.OPEN
                self.half_open_calls = 0
                self.success_count = 0

            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    logger.warning(
                        f"Circuit breaker transitioning to OPEN " f"({self.failure_count} failures)"
                    )
                    self.state = CircuitState.OPEN

    async def reset(self):
        """Manually reset circuit breaker to CLOSED state."""
        async with self._lock:
            logger.info("Circuit breaker manually reset to CLOSED")
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.half_open_calls = 0
            self.last_failure_time = None

    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        return self.state

    def get_metrics(self) -> dict:
        """
        Get circuit breaker metrics.

        Returns:
            Dictionary with metrics:
                - state: Current state
                - failure_count: Number of recent failures
                - success_count: Number of recent successes
                - half_open_calls: Number of calls in half-open state
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "half_open_calls": self.half_open_calls,
            "last_failure_time": self.last_failure_time,
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open."""


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitState",
    "CircuitBreakerOpen",
]
