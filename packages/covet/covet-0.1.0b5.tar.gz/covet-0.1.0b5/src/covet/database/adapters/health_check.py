"""
Database Health Check Module

Provides connection health monitoring and automatic recovery.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckConfig:
    """Configuration for health checks."""

    interval: float = 30.0  # Seconds between health checks
    timeout: float = 5.0  # Timeout for health check query
    failure_threshold: int = 3  # Consecutive failures before unhealthy
    # Response time threshold for degraded status (seconds)
    degraded_threshold: float = 1.0


class HealthChecker:
    """
    Database connection health checker.

    Periodically pings the database and tracks health status.
    Provides metrics and automatic reconnection on failure.

    Example:
        checker = HealthChecker(adapter)
        await checker.start()

        # Check health
        is_healthy = await checker.check()

        # Get metrics
        metrics = checker.get_metrics()

        await checker.stop()
    """

    def __init__(
        self,
        adapter: Any,
        config: Optional[HealthCheckConfig] = None,
        on_unhealthy: Optional[Callable] = None,
    ):
        """
        Initialize health checker.

        Args:
            adapter: Database adapter to monitor
            config: Health check configuration
            on_unhealthy: Callback function called when status becomes unhealthy
        """
        self.adapter = adapter
        self.config = config or HealthCheckConfig()
        self.on_unhealthy = on_unhealthy

        self.status = HealthStatus.UNKNOWN
        self.consecutive_failures = 0
        self.last_check_time: Optional[float] = None
        self.last_response_time: Optional[float] = None
        self.total_checks = 0
        self.total_failures = 0
        self.total_response_time = 0.0

        self._task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start background health check task."""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._health_check_loop())
        logger.info(f"Health checker started (interval: {self.config.interval}s)")

    async def stop(self):
        """Stop background health check task."""
        if not self._running:
            return

        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.error(f"Error during cleanup in stop: {e}", exc_info=True)
            self._task = None

        logger.info("Health checker stopped")

    async def _health_check_loop(self):
        """Background task that performs periodic health checks."""
        while self._running:
            try:
                await self.check()
                await asyncio.sleep(self.config.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(self.config.interval)

    async def check(self) -> bool:
        """
        Perform a health check.

        Returns:
            True if healthy, False otherwise
        """
        self.total_checks += 1
        self.last_check_time = time.time()

        try:
            # Execute ping query with timeout
            start_time = time.time()
            await asyncio.wait_for(self._ping_database(), timeout=self.config.timeout)
            response_time = time.time() - start_time

            # Record metrics
            self.last_response_time = response_time
            self.total_response_time += response_time
            self.consecutive_failures = 0

            # Determine status based on response time
            if response_time > self.config.degraded_threshold:
                previous_status = self.status
                self.status = HealthStatus.DEGRADED
                if previous_status != HealthStatus.DEGRADED:
                    logger.warning(
                        f"Database status changed to DEGRADED "
                        f"(response time: {response_time:.3f}s)"
                    )
            else:
                previous_status = self.status
                self.status = HealthStatus.HEALTHY
                if previous_status != HealthStatus.HEALTHY:
                    logger.info("Database status changed to HEALTHY")

            return True

        except asyncio.TimeoutError:
            logger.error(f"Health check timeout after {self.config.timeout}s")
            self._handle_failure()
            return False

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self._handle_failure()
            return False

    async def _ping_database(self):
        """
        Ping database to check connection.

        Executes a simple query to verify database connectivity.
        """
        # Use adapter-specific ping query
        if hasattr(self.adapter, "fetch_value"):
            await self.adapter.fetch_value("SELECT 1")
        elif hasattr(self.adapter, "execute"):
            await self.adapter.execute("SELECT 1")
        else:
            raise RuntimeError("Adapter does not support health checks")

    def _handle_failure(self):
        """Handle health check failure."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_response_time = None

        previous_status = self.status

        if self.consecutive_failures >= self.config.failure_threshold:
            self.status = HealthStatus.UNHEALTHY

            # Call unhealthy callback
            if previous_status != HealthStatus.UNHEALTHY and self.on_unhealthy:
                try:
                    if asyncio.iscoroutinefunction(self.on_unhealthy):
                        asyncio.create_task(self.on_unhealthy())
                    else:
                        self.on_unhealthy()
                except Exception as e:
                    logger.error(f"Error in on_unhealthy callback: {e}")

            if previous_status != HealthStatus.UNHEALTHY:
                logger.error(
                    f"Database status changed to UNHEALTHY "
                    f"({self.consecutive_failures} consecutive failures)"
                )

    def get_status(self) -> HealthStatus:
        """Get current health status."""
        return self.status

    def is_healthy(self) -> bool:
        """Check if database is healthy."""
        return self.status in (HealthStatus.HEALTHY, HealthStatus.DEGRADED)

    def get_metrics(self) -> dict:
        """
        Get health check metrics.

        Returns:
            Dictionary with metrics:
                - status: Current health status
                - consecutive_failures: Number of consecutive failures
                - total_checks: Total number of health checks
                - total_failures: Total number of failures
                - success_rate: Success rate percentage
                - avg_response_time: Average response time in seconds
                - last_check_time: Last check timestamp
                - last_response_time: Last check response time
        """
        success_rate = (
            ((self.total_checks - self.total_failures) / self.total_checks * 100)
            if self.total_checks > 0
            else 0.0
        )

        avg_response_time = (
            (self.total_response_time / (self.total_checks - self.total_failures))
            if (self.total_checks - self.total_failures) > 0
            else 0.0
        )

        return {
            "status": self.status.value,
            "consecutive_failures": self.consecutive_failures,
            "total_checks": self.total_checks,
            "total_failures": self.total_failures,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "last_check_time": self.last_check_time,
            "last_response_time": self.last_response_time,
        }

    async def wait_for_healthy(self, timeout: float = 30.0) -> bool:
        """
        Wait for database to become healthy.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if healthy, False if timeout
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            if await self.check():
                return True
            await asyncio.sleep(1.0)

        return False


__all__ = ["HealthChecker", "HealthCheckConfig", "HealthStatus"]
