"""
Kubernetes-Ready Health Check Endpoints

Implements the three health check endpoints required by Kubernetes:
- /health/liveness  - Is the application alive? (restart if fails)
- /health/readiness - Can the application handle traffic? (remove from load balancer if fails)
- /health/startup   - Has the application finished starting? (used for slow-starting apps)

Follows Kubernetes best practices:
https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/
"""

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from covet.health.checks import HealthStatus, HealthCheck, HealthCheckManager


class ProbeResult(str, Enum):
    """Health probe result status."""
    PASS = "pass"
    FAIL = "fail"


@dataclass
class ProbeResponse:
    """Health probe response."""
    status: ProbeResult
    timestamp: float
    message: Optional[str] = None
    checks: List[HealthCheck] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            'status': self.status.value,
            'timestamp': self.timestamp,
        }

        if self.message:
            response['message'] = self.message

        if self.checks:
            response['checks'] = [
                {
                    'name': check.name,
                    'status': check.status.value,
                    'message': check.message,
                    'duration_ms': check.duration_ms,
                }
                for check in self.checks
            ]

        if self.details:
            response['details'] = self.details

        return response


class KubernetesHealthProbes:
    """
    Kubernetes health probe manager.

    Provides liveness, readiness, and startup probes for Kubernetes deployments.
    """

    def __init__(
        self,
        startup_timeout: int = 60,
        readiness_checks: Optional[List[Callable]] = None,
    ):
        """
        Initialize Kubernetes health probes.

        Args:
            startup_timeout: Maximum time for startup (seconds)
            readiness_checks: Custom readiness check functions
        """
        self.start_time = time.time()
        self.startup_timeout = startup_timeout
        self.startup_completed = False
        self.readiness_checks = readiness_checks or []
        self.health_manager = HealthCheckManager()

    def mark_startup_complete(self):
        """Mark application startup as complete."""
        self.startup_completed = True
        elapsed = time.time() - self.start_time
        print(f"Application startup completed in {elapsed:.2f} seconds")

    async def liveness_probe(self) -> ProbeResponse:
        """
        Liveness probe - checks if application is alive.

        Kubernetes will restart the container if this fails.

        The liveness probe should be simple and fast:
        - Check if the application process is running
        - Check if critical threads are responsive
        - DO NOT check external dependencies (database, cache, etc.)

        Returns:
            ProbeResponse with PASS if alive, FAIL if dead
        """
        try:
            # Simple liveness check - if we can respond, we're alive
            # You can add custom liveness checks here

            # Example: Check if event loop is responsive
            await asyncio.sleep(0)

            return ProbeResponse(
                status=ProbeResult.PASS,
                timestamp=time.time(),
                message="Application is alive",
                details={
                    'uptime_seconds': time.time() - self.start_time,
                }
            )

        except Exception as e:
            # Liveness check failed - application is dead
            return ProbeResponse(
                status=ProbeResult.FAIL,
                timestamp=time.time(),
                message=f"Liveness check failed: {str(e)}",
            )

    async def readiness_probe(self) -> ProbeResponse:
        """
        Readiness probe - checks if application can handle traffic.

        Kubernetes will remove the container from service if this fails.

        The readiness probe should check:
        - Database connectivity
        - Cache connectivity
        - Critical external dependencies
        - Queue connectivity (if applicable)

        Returns:
            ProbeResponse with PASS if ready, FAIL if not ready
        """
        checks = []

        try:
            # Run all readiness checks in parallel
            check_tasks = [
                self.health_manager.check_database(),
                self.health_manager.check_cache(),
                self.health_manager.check_memory(),
                self.health_manager.check_disk_space(),
            ]

            # Add custom readiness checks
            for custom_check in self.readiness_checks:
                if asyncio.iscoroutinefunction(custom_check):
                    check_tasks.append(custom_check())

            results = await asyncio.gather(*check_tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, HealthCheck):
                    checks.append(result)
                elif isinstance(result, Exception):
                    checks.append(
                        HealthCheck(
                            name="unknown",
                            status=HealthStatus.UNHEALTHY,
                            message=f"Check failed: {str(result)}",
                        )
                    )

            # Determine overall readiness
            # Ready if all checks are HEALTHY or DEGRADED (not UNHEALTHY)
            failed_checks = [c for c in checks if c.status == HealthStatus.UNHEALTHY]

            if failed_checks:
                # Not ready - critical dependencies unavailable
                return ProbeResponse(
                    status=ProbeResult.FAIL,
                    timestamp=time.time(),
                    message="Application not ready - dependencies unavailable",
                    checks=checks,
                    details={
                        'failed_checks': [c.name for c in failed_checks],
                    }
                )
            else:
                # Ready to handle traffic
                return ProbeResponse(
                    status=ProbeResult.PASS,
                    timestamp=time.time(),
                    message="Application is ready",
                    checks=checks,
                )

        except Exception as e:
            return ProbeResponse(
                status=ProbeResult.FAIL,
                timestamp=time.time(),
                message=f"Readiness check failed: {str(e)}",
                checks=checks,
            )

    async def startup_probe(self) -> ProbeResponse:
        """
        Startup probe - checks if application has finished starting.

        Kubernetes will wait for this to succeed before running liveness/readiness probes.

        The startup probe should check:
        - Initial database migrations completed
        - Application initialization completed
        - Required resources loaded

        Useful for slow-starting applications (e.g., loading large models).

        Returns:
            ProbeResponse with PASS if started, FAIL if startup failed/timeout
        """
        try:
            elapsed = time.time() - self.start_time

            # Check if startup completed
            if self.startup_completed:
                return ProbeResponse(
                    status=ProbeResult.PASS,
                    timestamp=time.time(),
                    message="Application startup completed",
                    details={
                        'startup_time_seconds': elapsed,
                    }
                )

            # Check if startup timeout exceeded
            if elapsed > self.startup_timeout:
                return ProbeResponse(
                    status=ProbeResult.FAIL,
                    timestamp=time.time(),
                    message=f"Startup timeout exceeded ({self.startup_timeout}s)",
                    details={
                        'elapsed_seconds': elapsed,
                        'timeout_seconds': self.startup_timeout,
                    }
                )

            # Still starting
            return ProbeResponse(
                status=ProbeResult.FAIL,
                timestamp=time.time(),
                message="Application is still starting",
                details={
                    'elapsed_seconds': elapsed,
                    'timeout_seconds': self.startup_timeout,
                }
            )

        except Exception as e:
            return ProbeResponse(
                status=ProbeResult.FAIL,
                timestamp=time.time(),
                message=f"Startup check failed: {str(e)}",
            )


# Global health probe instance
_health_probes: Optional[KubernetesHealthProbes] = None


def get_health_probes(
    startup_timeout: int = 60,
    readiness_checks: Optional[List[Callable]] = None,
) -> KubernetesHealthProbes:
    """
    Get global health probes instance (singleton).

    Args:
        startup_timeout: Maximum startup timeout
        readiness_checks: Custom readiness checks

    Returns:
        Health probes instance
    """
    global _health_probes

    if _health_probes is None:
        _health_probes = KubernetesHealthProbes(
            startup_timeout=startup_timeout,
            readiness_checks=readiness_checks or [],
        )

    return _health_probes


# Convenience functions for route handlers

async def liveness_endpoint() -> Dict[str, Any]:
    """
    Liveness endpoint handler.

    Returns:
        Liveness probe response
    """
    probes = get_health_probes()
    result = await probes.liveness_probe()
    return result.to_dict()


async def readiness_endpoint() -> Dict[str, Any]:
    """
    Readiness endpoint handler.

    Returns:
        Readiness probe response
    """
    probes = get_health_probes()
    result = await probes.readiness_probe()
    return result.to_dict()


async def startup_endpoint() -> Dict[str, Any]:
    """
    Startup endpoint handler.

    Returns:
        Startup probe response
    """
    probes = get_health_probes()
    result = await probes.startup_probe()
    return result.to_dict()


__all__ = [
    'KubernetesHealthProbes',
    'ProbeResult',
    'ProbeResponse',
    'get_health_probes',
    'liveness_endpoint',
    'readiness_endpoint',
    'startup_endpoint',
]
