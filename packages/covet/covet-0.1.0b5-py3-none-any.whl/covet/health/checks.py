"""
Health Check Endpoints for CovetPy v1.0

Provides comprehensive health monitoring for production deployments.
"""

import asyncio
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import psutil


class HealthStatus(str, Enum):
    """Health check status values."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthCheck:
    """Individual health check result."""

    name: str
    status: HealthStatus
    message: str = ""
    duration_ms: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthResponse:
    """Overall health check response."""

    status: HealthStatus
    timestamp: float
    version: str = "1.0.0"
    checks: List[HealthCheck] = field(default_factory=list)
    system: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "version": self.version,
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "duration_ms": check.duration_ms,
                    "details": check.details,
                }
                for check in self.checks
            ],
            "system": self.system,
        }


class HealthCheckManager:
    """Manages health checks for the application."""

    def __init__(self):
        self.checks: List[callable] = []
        self.start_time = time.time()

    def register(self, check_func: callable):
        """Register a health check function."""
        self.checks.append(check_func)

    async def check_basic(self) -> HealthCheck:
        """Basic health check - always returns healthy if app is running."""
        return HealthCheck(
            name="basic",
            status=HealthStatus.HEALTHY,
            message="Application is running",
            details={
                "uptime_seconds": time.time() - self.start_time,
                "python_version": sys.version.split()[0],
            },
        )

    async def check_database(self) -> HealthCheck:
        """Check database connectivity."""
        start = time.time()
        try:
            # Import here to avoid circular dependencies
            from covet.database import get_database

            db = get_database()
            if db:
                # Try a simple query
                await db.execute("SELECT 1")
                duration_ms = (time.time() - start) * 1000

                # Get connection pool stats
                pool_size = getattr(db, "pool_size", 0)
                active = getattr(db, "active_connections", 0)

                return HealthCheck(
                    name="database",
                    status=HealthStatus.HEALTHY,
                    message="Database connection successful",
                    duration_ms=duration_ms,
                    details={
                        "pool_size": pool_size,
                        "active_connections": active,
                        "query_time_ms": duration_ms,
                    },
                )
            else:
                return HealthCheck(
                    name="database",
                    status=HealthStatus.DEGRADED,
                    message="Database not configured",
                )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return HealthCheck(
                name="database",
                status=HealthStatus.UNHEALTHY,
                message=f"Database check failed: {str(e)}",
                duration_ms=duration_ms,
            )

    async def check_cache(self) -> HealthCheck:
        """Check cache (Redis/Memcached) connectivity."""
        start = time.time()
        try:
            from covet.cache import get_cache

            cache = get_cache()
            if cache:
                # Try set and get
                test_key = "_health_check"
                test_value = str(time.time())

                await cache.set(test_key, test_value, timeout=10)
                result = await cache.get(test_key)
                await cache.delete(test_key)

                duration_ms = (time.time() - start) * 1000

                if result == test_value:
                    return HealthCheck(
                        name="cache",
                        status=HealthStatus.HEALTHY,
                        message="Cache connection successful",
                        duration_ms=duration_ms,
                        details={"backend": cache.backend, "ping_ms": duration_ms},
                    )
                else:
                    return HealthCheck(
                        name="cache",
                        status=HealthStatus.DEGRADED,
                        message="Cache read/write inconsistent",
                    )
            else:
                return HealthCheck(
                    name="cache",
                    status=HealthStatus.DEGRADED,
                    message="Cache not configured",
                )
        except Exception as e:
            duration_ms = (time.time() - start) * 1000
            return HealthCheck(
                name="cache",
                status=HealthStatus.UNHEALTHY,
                message=f"Cache check failed: {str(e)}",
                duration_ms=duration_ms,
            )

    async def check_disk_space(self) -> HealthCheck:
        """Check disk space availability."""
        try:
            disk = psutil.disk_usage("/")
            percent_used = disk.percent

            if percent_used < 80:
                status = HealthStatus.HEALTHY
                message = "Disk space healthy"
            elif percent_used < 90:
                status = HealthStatus.DEGRADED
                message = "Disk space usage high"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Disk space critical"

            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "percent_used": disk.percent,
                },
            )
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNHEALTHY,
                message=f"Disk check failed: {str(e)}",
            )

    async def check_memory(self) -> HealthCheck:
        """Check memory usage."""
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent

            if percent_used < 80:
                status = HealthStatus.HEALTHY
                message = "Memory usage healthy"
            elif percent_used < 90:
                status = HealthStatus.DEGRADED
                message = "Memory usage high"
            else:
                status = HealthStatus.UNHEALTHY
                message = "Memory usage critical"

            return HealthCheck(
                name="memory",
                status=status,
                message=message,
                details={
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "percent_used": memory.percent,
                    "process_rss_mb": round(psutil.Process().memory_info().rss / (1024**2), 2),
                },
            )
        except Exception as e:
            return HealthCheck(
                name="memory",
                status=HealthStatus.UNHEALTHY,
                message=f"Memory check failed: {str(e)}",
            )

    async def check_cpu(self) -> HealthCheck:
        """Check CPU usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)

            if cpu_percent < 70:
                status = HealthStatus.HEALTHY
                message = "CPU usage healthy"
            elif cpu_percent < 85:
                status = HealthStatus.DEGRADED
                message = "CPU usage high"
            else:
                status = HealthStatus.UNHEALTHY
                message = "CPU usage critical"

            return HealthCheck(
                name="cpu",
                status=status,
                message=message,
                details={
                    "percent_used": cpu_percent,
                    "cpu_count": psutil.cpu_count(),
                    "load_average": (
                        psutil.getloadavg() if hasattr(psutil, "getloadavg") else None
                    ),
                },
            )
        except Exception as e:
            return HealthCheck(
                name="cpu",
                status=HealthStatus.UNHEALTHY,
                message=f"CPU check failed: {str(e)}",
            )

    async def run_all_checks(self) -> HealthResponse:
        """Run all health checks and return aggregated response."""
        checks = await asyncio.gather(
            self.check_basic(),
            self.check_database(),
            self.check_cache(),
            self.check_disk_space(),
            self.check_memory(),
            self.check_cpu(),
            return_exceptions=True,
        )

        # Filter out exceptions and convert to HealthCheck objects
        valid_checks = []
        for check in checks:
            if isinstance(check, HealthCheck):
                valid_checks.append(check)
            elif isinstance(check, Exception):
                valid_checks.append(
                    HealthCheck(
                        name="unknown",
                        status=HealthStatus.UNHEALTHY,
                        message=f"Check failed: {str(check)}",
                    )
                )

        # Determine overall status
        if any(c.status == HealthStatus.UNHEALTHY for c in valid_checks):
            overall_status = HealthStatus.UNHEALTHY
        elif any(c.status == HealthStatus.DEGRADED for c in valid_checks):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.HEALTHY

        # System info
        system_info = {
            "hostname": (psutil.os.uname().nodename if hasattr(psutil.os, "uname") else "unknown"),
            "platform": sys.platform,
            "uptime_seconds": time.time() - self.start_time,
        }

        return HealthResponse(
            status=overall_status,
            timestamp=time.time(),
            checks=valid_checks,
            system=system_info,
        )


# Global health check manager
health_manager = HealthCheckManager()


# Simplified endpoints
async def health_check() -> Dict[str, Any]:
    """Simple health check endpoint - /health"""
    return {"status": "healthy", "timestamp": time.time(), "version": "1.0.0"}


async def liveness_check() -> Dict[str, Any]:
    """Liveness check - /health/live"""
    return {"status": "alive", "timestamp": time.time()}


async def readiness_check() -> Dict[str, Any]:
    """Readiness check - /health/ready"""
    result = await health_manager.run_all_checks()

    # Ready only if healthy or degraded (not unhealthy)
    is_ready = result.status in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]

    return {
        "status": "ready" if is_ready else "not_ready",
        "timestamp": result.timestamp,
        "details": result.to_dict(),
    }


async def comprehensive_health() -> Dict[str, Any]:
    """Comprehensive health check - /health/detailed"""
    result = await health_manager.run_all_checks()
    return result.to_dict()
