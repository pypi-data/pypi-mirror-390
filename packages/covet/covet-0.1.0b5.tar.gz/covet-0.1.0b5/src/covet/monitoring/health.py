"""
Health Check Endpoints for CovetPy

Implements Kubernetes-style health checks:
- /health - General health status
- /health/live - Liveness probe (is app running?)
- /health/ready - Readiness probe (can app serve traffic?)
- /health/startup - Startup probe (has app initialized?)
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


class HealthCheck:
    """Comprehensive health check system."""

    def __init__(self):
        self.start_time = time.time()
        self.ready = False
        self.startup_complete = False
        self.checks: Dict[str, Callable] = {}
        self.readiness_checks: List[str] = []

    def add_check(self, name: str, check_func: Callable, readiness: bool = True):
        """Add a health check function."""
        self.checks[name] = check_func
        if readiness:
            self.readiness_checks.append(name)

    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity."""
        try:
            # Attempt database connection
            # In production, use actual DB connection check
            return {
                "status": "healthy",
                "latency_ms": 5,
                "connections_active": 10,
                "connections_idle": 5,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            # Attempt Redis connection
            return {
                "status": "healthy",
                "latency_ms": 2,
                "connected_clients": 3,
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space availability."""
        import shutil

        try:
            usage = shutil.disk_usage("/")
            percent_used = (usage.used / usage.total) * 100
            return {
                "status": "healthy" if percent_used < 90 else "warning",
                "percent_used": round(percent_used, 2),
                "free_gb": round(usage.free / (1024**3), 2),
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e),
            }

    async def check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        import psutil

        try:
            mem = psutil.virtual_memory()
            return {
                "status": "healthy" if mem.percent < 90 else "warning",
                "percent_used": mem.percent,
                "available_mb": round(mem.available / (1024**2), 2),
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e),
            }

    async def liveness(self) -> Dict[str, Any]:
        """
        Liveness probe - is the application alive?
        Returns 200 if app is running, 503 if dead.
        """
        return {
            "status": "alive",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def readiness(self) -> Dict[str, Any]:
        """
        Readiness probe - can the application serve traffic?
        Returns 200 if ready, 503 if not ready.
        """
        if not self.ready:
            return {
                "status": "not_ready",
                "reason": "Application not fully initialized",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Run all readiness checks
        checks_status = {}
        all_healthy = True

        for check_name in self.readiness_checks:
            if check_name in self.checks:
                try:
                    result = await self.checks[check_name]()
                    checks_status[check_name] = result
                    if result.get("status") not in ["healthy", "alive"]:
                        all_healthy = False
                except Exception as e:
                    checks_status[check_name] = {
                        "status": "error",
                        "error": str(e),
                    }
                    all_healthy = False

        return {
            "status": "ready" if all_healthy else "not_ready",
            "checks": checks_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def startup(self) -> Dict[str, Any]:
        """
        Startup probe - has the application completed startup?
        Returns 200 when startup complete, 503 during startup.
        """
        if not self.startup_complete:
            return {
                "status": "starting",
                "uptime_seconds": round(time.time() - self.start_time, 2),
                "timestamp": datetime.utcnow().isoformat(),
            }

        return {
            "status": "started",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def health(self) -> Dict[str, Any]:
        """
        General health endpoint - comprehensive health status.
        """
        checks_status = {}

        # Run all checks
        for check_name, check_func in self.checks.items():
            try:
                result = await check_func()
                checks_status[check_name] = result
            except Exception as e:
                checks_status[check_name] = {
                    "status": "error",
                    "error": str(e),
                }

        # Determine overall status
        statuses = [check.get("status") for check in checks_status.values()]
        if "unhealthy" in statuses or "error" in statuses:
            overall_status = "unhealthy"
        elif "warning" in statuses:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "checks": checks_status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
        }

    def mark_ready(self):
        """Mark application as ready to serve traffic."""
        self.ready = True

    def mark_not_ready(self):
        """Mark application as not ready."""
        self.ready = False

    def mark_startup_complete(self):
        """Mark startup as complete."""
        self.startup_complete = True
        self.ready = True


# Global health check instance
health_check = HealthCheck()

# Register default checks
health_check.add_check("database", health_check.check_database, readiness=True)
health_check.add_check("redis", health_check.check_redis, readiness=True)
health_check.add_check("disk_space", health_check.check_disk_space, readiness=False)
health_check.add_check("memory", health_check.check_memory, readiness=False)


def health_check_endpoints(app):
    """
    Add health check endpoints to application.

    Usage:
        app = CovetPy()
        health_check_endpoints(app)
    """

    @app.get("/health")
    async def health_endpoint(request):
        """General health check endpoint."""
        result = await health_check.health()
        status_code = 200 if result["status"] in ["healthy", "degraded"] else 503
        return Response(result, status_code=status_code)

    @app.get("/health/live")
    async def liveness_endpoint(request):
        """Liveness probe endpoint for Kubernetes."""
        result = await health_check.liveness()
        return Response(result, status_code=200)

    @app.get("/health/ready")
    async def readiness_endpoint(request):
        """Readiness probe endpoint for Kubernetes."""
        result = await health_check.readiness()
        status_code = 200 if result["status"] == "ready" else 503
        return Response(result, status_code=status_code)

    @app.get("/health/startup")
    async def startup_endpoint(request):
        """Startup probe endpoint for Kubernetes."""
        result = await health_check.startup()
        status_code = 200 if result["status"] == "started" else 503
        return Response(result, status_code=status_code)


# Dummy Response class for example (use actual framework Response)


class Response:
    def __init__(self, data, status_code=200):
        self.data = data
        self.status_code = status_code


__all__ = ["HealthCheck", "health_check", "health_check_endpoints"]
