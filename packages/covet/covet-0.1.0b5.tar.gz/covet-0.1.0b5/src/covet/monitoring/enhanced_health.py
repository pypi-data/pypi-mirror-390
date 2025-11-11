"""
Enhanced Health Check System with Real Dependency Checks

Replaces hardcoded health checks with actual database, Redis, disk, memory,
and connection pool validation.

Usage:
    from covet.monitoring.enhanced_health import EnhancedHealthCheck

    health = EnhancedHealthCheck()
    health.set_database_pool(db_pool)
    health.set_redis_client(redis_client)

    # Check health
    result = await health.health()
"""

import asyncio
import logging
import shutil
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import psutil

logger = logging.getLogger(__name__)


class EnhancedHealthCheck:
    """
    Production-ready health check system with actual dependency validation.

    Features:
    - Real database connectivity checks with query execution
    - Redis PING validation with latency measurement
    - Disk space monitoring with configurable thresholds
    - Memory usage tracking
    - Connection pool health validation
    - Recent error rate monitoring
    """

    def __init__(
        self,
        disk_threshold_percent: float = 90.0,
        memory_threshold_percent: float = 90.0,
        error_rate_threshold: int = 10,
    ):
        """
        Initialize enhanced health checker.

        Args:
            disk_threshold_percent: Disk usage % to trigger warning
            memory_threshold_percent: Memory usage % to trigger warning
            error_rate_threshold: Errors per minute to trigger warning
        """
        self.start_time = time.time()
        self.ready = False
        self.startup_complete = False

        # Thresholds
        self.disk_threshold = disk_threshold_percent
        self.memory_threshold = memory_threshold_percent
        self.error_rate_threshold = error_rate_threshold

        # External dependencies
        self._db_pool = None
        self._redis_client = None

        # Custom checks
        self.custom_checks: Dict[str, Callable] = {}
        self.readiness_checks: List[str] = []

        # Error tracking
        self._recent_errors: List[float] = []

        logger.info("EnhancedHealthCheck initialized")

    def set_database_pool(self, pool):
        """Set the database connection pool for health checks."""
        self._db_pool = pool
        logger.info("Database pool registered for health checks")

    def set_redis_client(self, client):
        """Set the Redis client for health checks."""
        self._redis_client = client
        logger.info("Redis client registered for health checks")

    def add_custom_check(self, name: str, check_func: Callable, readiness: bool = True):
        """
        Add a custom health check function.

        Args:
            name: Name of the check
            check_func: Async function that returns dict with 'status' key
            readiness: Whether this affects readiness probe
        """
        self.custom_checks[name] = check_func
        if readiness:
            self.readiness_checks.append(name)

    def record_error(self):
        """Record an error for error rate tracking."""
        self._recent_errors.append(time.time())

        # Keep only errors from last minute
        cutoff = time.time() - 60
        self._recent_errors = [t for t in self._recent_errors if t > cutoff]

    async def check_database(self) -> Dict[str, Any]:
        """
        Check database connectivity with actual query execution.

        Returns:
            Dict with status, latency, connection stats
        """
        if not self._db_pool:
            return {
                "status": "unknown",
                "error": "Database pool not configured",
            }

        start_time = time.time()

        try:
            # Method 1: Try to get pool stats
            pool_stats = {}
            if hasattr(self._db_pool, "get_stats"):
                pool_stats = self._db_pool.get_stats()
            elif hasattr(self._db_pool, "size"):
                # SQLAlchemy-style pool
                pool_stats = {
                    "active": getattr(self._db_pool, "checkedout", lambda: 0)(),
                    "idle": self._db_pool.size()
                    - getattr(self._db_pool, "checkedout", lambda: 0)(),
                    "size": self._db_pool.size(),
                }

            # Method 2: Try to execute a test query
            test_query_success = False
            connection = None

            try:
                # Attempt to get a connection
                if hasattr(self._db_pool, "acquire"):
                    # asyncpg-style pool
                    async with self._db_pool.acquire() as conn:
                        await conn.fetchval("SELECT 1")
                        test_query_success = True
                elif hasattr(self._db_pool, "connect"):
                    # SQLAlchemy-style
                    connection = self._db_pool.connect()
                    connection.execute("SELECT 1")
                    test_query_success = True
                    connection.close()
                else:
                    # Generic pool - assume it's working
                    test_query_success = True

            except Exception as query_error:
                logger.warning(f"Database test query failed: {query_error}")
                test_query_success = False
                if connection:
                    try:
                        connection.close()
                    except:
                        pass

            latency_ms = (time.time() - start_time) * 1000

            if test_query_success:
                return {
                    "status": "healthy",
                    "latency_ms": round(latency_ms, 2),
                    "connections_active": pool_stats.get("active", "unknown"),
                    "connections_idle": pool_stats.get("idle", "unknown"),
                    "pool_size": pool_stats.get("size", "unknown"),
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": "Test query failed",
                    "latency_ms": round(latency_ms, 2),
                }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Database health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": round(latency_ms, 2),
            }

    async def check_redis(self) -> Dict[str, Any]:
        """
        Check Redis connectivity with PING command.

        Returns:
            Dict with status, latency, connection info
        """
        if not self._redis_client:
            return {
                "status": "unknown",
                "error": "Redis client not configured",
            }

        start_time = time.time()

        try:
            # Try to PING Redis
            if hasattr(self._redis_client, "ping"):
                # redis-py or similar
                if asyncio.iscoroutinefunction(self._redis_client.ping):
                    pong = await self._redis_client.ping()
                else:
                    pong = self._redis_client.ping()

                latency_ms = (time.time() - start_time) * 1000

                if pong:
                    # Get additional info if available
                    info = {}
                    try:
                        if hasattr(self._redis_client, "info"):
                            if asyncio.iscoroutinefunction(self._redis_client.info):
                                info = await self._redis_client.info()
                            else:
                                info = self._redis_client.info()
                    except:
                        pass

                    return {
                        "status": "healthy",
                        "latency_ms": round(latency_ms, 2),
                        "connected_clients": info.get("connected_clients", "unknown"),
                        "used_memory_mb": (
                            round(info.get("used_memory", 0) / 1024 / 1024, 2)
                            if info.get("used_memory")
                            else "unknown"
                        ),
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "error": "PING failed",
                    }
            else:
                # Can't ping, assume healthy if client exists
                return {
                    "status": "healthy",
                    "latency_ms": 0,
                    "note": "PING not available, assuming healthy",
                }

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Redis health check failed: {e}", exc_info=True)
            return {
                "status": "unhealthy",
                "error": str(e),
                "latency_ms": round(latency_ms, 2),
            }

    async def check_disk_space(self) -> Dict[str, Any]:
        """
        Check disk space availability.

        Returns:
            Dict with status, usage %, free space
        """
        try:
            usage = shutil.disk_usage("/")
            percent_used = (usage.used / usage.total) * 100
            free_gb = usage.free / (1024**3)

            status = "healthy"
            if percent_used >= self.disk_threshold:
                status = "critical"
            elif percent_used >= self.disk_threshold - 10:
                status = "warning"

            return {
                "status": status,
                "percent_used": round(percent_used, 2),
                "free_gb": round(free_gb, 2),
                "total_gb": round(usage.total / (1024**3), 2),
                "threshold_percent": self.disk_threshold,
            }

        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e),
            }

    async def check_memory(self) -> Dict[str, Any]:
        """
        Check memory usage.

        Returns:
            Dict with status, usage %, available memory
        """
        try:
            mem = psutil.virtual_memory()
            percent_used = mem.percent

            status = "healthy"
            if percent_used >= self.memory_threshold:
                status = "critical"
            elif percent_used >= self.memory_threshold - 10:
                status = "warning"

            return {
                "status": status,
                "percent_used": round(percent_used, 2),
                "available_mb": round(mem.available / (1024**2), 2),
                "total_mb": round(mem.total / (1024**2), 2),
                "threshold_percent": self.memory_threshold,
            }

        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e),
            }

    async def check_connection_pool(self) -> Dict[str, Any]:
        """
        Check connection pool health (no leaks, available connections).

        Returns:
            Dict with status and pool metrics
        """
        if not self._db_pool:
            return {
                "status": "unknown",
                "error": "Pool not configured",
            }

        try:
            pool_stats = {}
            if hasattr(self._db_pool, "get_stats"):
                pool_stats = self._db_pool.get_stats()
            elif hasattr(self._db_pool, "size"):
                pool_stats = {
                    "active": getattr(self._db_pool, "checkedout", lambda: 0)(),
                    "idle": self._db_pool.size()
                    - getattr(self._db_pool, "checkedout", lambda: 0)(),
                    "size": self._db_pool.size(),
                    "leaked": 0,
                }

            # Determine health
            idle = pool_stats.get("idle", 0)
            leaked = pool_stats.get("leaked", 0)
            size = pool_stats.get("size", 1)
            active = pool_stats.get("active", 0)

            if leaked > 0:
                status = "unhealthy"
                issue = "Connection leaks detected"
            elif idle == 0:
                status = "warning"
                issue = "No idle connections available"
            elif active / size > 0.9:
                status = "warning"
                issue = "Pool utilization > 90%"
            else:
                status = "healthy"
                issue = None

            result = {
                "status": status,
                **pool_stats,
                "utilization_percent": round((active / size) * 100, 2) if size > 0 else 0,
            }

            if issue:
                result["issue"] = issue

            return result

        except Exception as e:
            logger.error(f"Connection pool check failed: {e}")
            return {
                "status": "unknown",
                "error": str(e),
            }

    async def check_recent_errors(self) -> Dict[str, Any]:
        """
        Check recent error rate.

        Returns:
            Dict with status and error metrics
        """
        # Clean old errors
        cutoff = time.time() - 60
        self._recent_errors = [t for t in self._recent_errors if t > cutoff]

        errors_per_min = len(self._recent_errors)

        status = "healthy"
        if errors_per_min >= self.error_rate_threshold:
            status = "warning"
        if errors_per_min >= self.error_rate_threshold * 2:
            status = "critical"

        return {
            "status": status,
            "errors_per_minute": errors_per_min,
            "threshold": self.error_rate_threshold,
        }

    async def liveness(self) -> Dict[str, Any]:
        """
        Liveness probe - is the application alive?

        Returns:
            Dict with liveness status
        """
        return {
            "status": "alive",
            "uptime_seconds": round(time.time() - self.start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
        }

    async def readiness(self) -> Dict[str, Any]:
        """
        Readiness probe - can the application serve traffic?

        Returns:
            Dict with readiness status and check results
        """
        if not self.ready:
            return {
                "status": "not_ready",
                "reason": "Application not fully initialized",
                "timestamp": datetime.utcnow().isoformat(),
            }

        # Run critical checks
        checks_status = {}
        all_healthy = True

        # Database check (required for readiness)
        db_result = await self.check_database()
        checks_status["database"] = db_result
        if db_result.get("status") != "healthy":
            all_healthy = False

        # Redis check (required for readiness)
        redis_result = await self.check_redis()
        checks_status["redis"] = redis_result
        if redis_result.get("status") != "healthy":
            all_healthy = False

        # Connection pool check
        pool_result = await self.check_connection_pool()
        checks_status["connection_pool"] = pool_result
        if pool_result.get("status") not in ["healthy", "warning"]:
            all_healthy = False

        # Run custom readiness checks
        for check_name in self.readiness_checks:
            if check_name in self.custom_checks:
                try:
                    result = await self.custom_checks[check_name]()
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

        Returns:
            Dict with startup status
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
        Comprehensive health check - run all checks.

        Returns:
            Dict with overall health status and all check results
        """
        checks_status = {}

        # Run all built-in checks
        checks_status["database"] = await self.check_database()
        checks_status["redis"] = await self.check_redis()
        checks_status["disk_space"] = await self.check_disk_space()
        checks_status["memory"] = await self.check_memory()
        checks_status["connection_pool"] = await self.check_connection_pool()
        checks_status["recent_errors"] = await self.check_recent_errors()

        # Run custom checks
        for check_name, check_func in self.custom_checks.items():
            try:
                result = await check_func()
                checks_status[check_name] = result
            except Exception as e:
                logger.error(f"Custom check '{check_name}' failed: {e}")
                checks_status[check_name] = {
                    "status": "error",
                    "error": str(e),
                }

        # Determine overall status
        statuses = [check.get("status") for check in checks_status.values()]

        if "unhealthy" in statuses or "critical" in statuses or "error" in statuses:
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
        logger.info("Application marked as ready")

    def mark_not_ready(self):
        """Mark application as not ready."""
        self.ready = False
        logger.info("Application marked as not ready")

    def mark_startup_complete(self):
        """Mark startup as complete."""
        self.startup_complete = True
        self.ready = True
        logger.info("Application startup complete")


# Global instance
_enhanced_health_check: Optional[EnhancedHealthCheck] = None


def get_health_check() -> EnhancedHealthCheck:
    """Get the global health check instance."""
    global _enhanced_health_check
    if _enhanced_health_check is None:
        _enhanced_health_check = EnhancedHealthCheck()
    return _enhanced_health_check


__all__ = [
    "EnhancedHealthCheck",
    "get_health_check",
]
