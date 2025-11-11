"""
Connection Pool Monitor

Monitors database connection pool health, metrics, and performance.
Provides real-time dashboards and alerting for pool exhaustion and issues.

Features:
- Real-time pool metrics tracking
- Health checks with automatic ping
- Pool exhaustion detection and alerting
- Text-based dashboard for monitoring
- Historical metrics and trending
- Configurable thresholds and alerts
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PoolSnapshot:
    """A snapshot of pool metrics at a point in time."""

    timestamp: datetime
    pool_size: int
    active_connections: int
    idle_connections: int
    waiting_count: int
    avg_wait_time_ms: float
    checkout_count: int
    checkin_count: int
    timeout_count: int
    error_count: int

    @property
    def utilization_percent(self) -> float:
        """Calculate pool utilization percentage."""
        if self.pool_size == 0:
            return 0.0
        return (self.active_connections / self.pool_size) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "pool_size": self.pool_size,
            "active_connections": self.active_connections,
            "idle_connections": self.idle_connections,
            "waiting_count": self.waiting_count,
            "avg_wait_time_ms": round(self.avg_wait_time_ms, 2),
            "utilization_percent": round(self.utilization_percent, 2),
            "checkout_count": self.checkout_count,
            "checkin_count": self.checkin_count,
            "timeout_count": self.timeout_count,
            "error_count": self.error_count,
        }


@dataclass
class PoolMetrics:
    """Aggregated pool metrics over time."""

    total_checkouts: int = 0
    total_checkins: int = 0
    total_timeouts: int = 0
    total_errors: int = 0
    total_wait_time_ms: float = 0.0
    wait_samples: int = 0
    peak_active_connections: int = 0
    peak_waiting_count: int = 0
    health_check_successes: int = 0
    health_check_failures: int = 0

    @property
    def avg_wait_time_ms(self) -> float:
        """Average wait time across all samples."""
        if self.wait_samples == 0:
            return 0.0
        return self.total_wait_time_ms / self.wait_samples

    @property
    def timeout_rate(self) -> float:
        """Timeout rate as percentage."""
        if self.total_checkouts == 0:
            return 0.0
        return (self.total_timeouts / self.total_checkouts) * 100

    @property
    def error_rate(self) -> float:
        """Error rate as percentage."""
        if self.total_checkouts == 0:
            return 0.0
        return (self.total_errors / self.total_checkouts) * 100

    @property
    def health_check_success_rate(self) -> float:
        """Health check success rate as percentage."""
        total = self.health_check_successes + self.health_check_failures
        if total == 0:
            return 0.0
        return (self.health_check_successes / total) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_checkouts": self.total_checkouts,
            "total_checkins": self.total_checkins,
            "total_timeouts": self.total_timeouts,
            "total_errors": self.total_errors,
            "avg_wait_time_ms": round(self.avg_wait_time_ms, 2),
            "peak_active_connections": self.peak_active_connections,
            "peak_waiting_count": self.peak_waiting_count,
            "timeout_rate": round(self.timeout_rate, 2),
            "error_rate": round(self.error_rate, 2),
            "health_check_success_rate": round(self.health_check_success_rate, 2),
        }


@dataclass
class PoolHealthCheck:
    """Result of a pool health check."""

    timestamp: datetime
    success: bool
    latency_ms: float
    pool_available: bool
    connections_healthy: bool
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "latency_ms": round(self.latency_ms, 2),
            "pool_available": self.pool_available,
            "connections_healthy": self.connections_healthy,
            "error": self.error,
        }


class ConnectionPoolMonitor:
    """
    Monitor connection pool health and performance.

    Features:
    - Track pool metrics (size, active, idle, waiting)
    - Monitor connection checkout/checkin
    - Detect pool exhaustion
    - Periodic health checks with database ping
    - Text-based dashboard
    - Alert on issues

    Usage:
        monitor = ConnectionPoolMonitor(
            pool_size=20,
            health_check_interval=60
        )
        await monitor.start()

        # Track operations
        monitor.record_checkout()
        monitor.record_checkin()
        monitor.record_wait_time(150.5)

        # Get current snapshot
        snapshot = monitor.get_current_snapshot()

        # Display dashboard
        print(monitor.generate_dashboard())
    """

    def __init__(
        self,
        pool_size: int = 20,
        health_check_interval: int = 60,
        snapshot_history_size: int = 1000,
        exhaustion_threshold: float = 0.9,
        high_wait_time_ms: float = 1000.0,
        enable_alerting: bool = True,
    ):
        """
        Initialize connection pool monitor.

        Args:
            pool_size: Maximum pool size
            health_check_interval: Seconds between health checks
            snapshot_history_size: Number of historical snapshots to keep
            exhaustion_threshold: Pool utilization threshold for alerts (0-1)
            high_wait_time_ms: Threshold for high wait time alerts
            enable_alerting: Enable alert generation
        """
        self.pool_size = pool_size
        self.health_check_interval = health_check_interval
        self.snapshot_history_size = snapshot_history_size
        self.exhaustion_threshold = exhaustion_threshold
        self.high_wait_time_ms = high_wait_time_ms
        self.enable_alerting = enable_alerting

        # Current state
        self._active_connections = 0
        self._idle_connections = pool_size
        self._waiting_count = 0

        # Metrics
        self.metrics = PoolMetrics()

        # Wait time tracking
        self._wait_times: Deque[float] = deque(maxlen=100)

        # History
        self._snapshots: Deque[PoolSnapshot] = deque(maxlen=snapshot_history_size)
        self._health_checks: Deque[PoolHealthCheck] = deque(maxlen=100)

        # Alert handlers
        self._alert_handlers: List[Callable[[str, Dict[str, Any]], None]] = []

        # Background tasks
        self._health_check_task: Optional[asyncio.Task] = None
        self._snapshot_task: Optional[asyncio.Task] = None
        self._running = False

        # Health check callback (to be set by user)
        self._health_check_callback: Optional[Callable[[], bool]] = None

        logger.info(f"ConnectionPoolMonitor initialized (pool_size={pool_size})")

    async def start(self) -> None:
        """Start the monitor and background tasks."""
        if self._running:
            return

        self._running = True

        # Start health check task
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        # Start snapshot task
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())

        logger.info("ConnectionPoolMonitor started")

    async def stop(self) -> None:
        """Stop the monitor and cleanup."""
        self._running = False

        # Cancel tasks
        tasks = [self._health_check_task, self._snapshot_task]
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        logger.info("ConnectionPoolMonitor stopped")

    def set_health_check_callback(self, callback: Callable[[], bool]) -> None:
        """
        Set callback for health checks.

        Args:
            callback: Async function that returns True if pool is healthy
        """
        self._health_check_callback = callback

    def record_checkout(self) -> None:
        """Record a connection checkout."""
        self._active_connections += 1
        self._idle_connections = max(0, self._idle_connections - 1)
        self.metrics.total_checkouts += 1

        # Update peak
        if self._active_connections > self.metrics.peak_active_connections:
            self.metrics.peak_active_connections = self._active_connections

        # Check for exhaustion
        self._check_exhaustion()

    def record_checkin(self) -> None:
        """Record a connection checkin."""
        self._active_connections = max(0, self._active_connections - 1)
        self._idle_connections += 1
        self.metrics.total_checkins += 1

    def record_wait_time(self, wait_time_ms: float) -> None:
        """Record a connection wait time."""
        self._wait_times.append(wait_time_ms)
        self.metrics.total_wait_time_ms += wait_time_ms
        self.metrics.wait_samples += 1

        # Check for high wait time
        if wait_time_ms >= self.high_wait_time_ms:
            asyncio.create_task(
                self._send_alert(
                    "high_wait_time",
                    {
                        "wait_time_ms": wait_time_ms,
                        "threshold_ms": self.high_wait_time_ms,
                    },
                )
            )

    def record_timeout(self) -> None:
        """Record a connection timeout."""
        self.metrics.total_timeouts += 1
        asyncio.create_task(self._send_alert("connection_timeout", {}))

    def record_error(self, error: str) -> None:
        """Record a connection error."""
        self.metrics.total_errors += 1
        asyncio.create_task(self._send_alert("connection_error", {"error": error}))

    def record_waiting(self, count: int) -> None:
        """Update waiting connections count."""
        self._waiting_count = count

        # Update peak
        if count > self.metrics.peak_waiting_count:
            self.metrics.peak_waiting_count = count

    def get_current_snapshot(self) -> PoolSnapshot:
        """Get current pool state snapshot."""
        avg_wait_time = sum(self._wait_times) / len(self._wait_times) if self._wait_times else 0.0

        return PoolSnapshot(
            timestamp=datetime.now(),
            pool_size=self.pool_size,
            active_connections=self._active_connections,
            idle_connections=self._idle_connections,
            waiting_count=self._waiting_count,
            avg_wait_time_ms=avg_wait_time,
            checkout_count=self.metrics.total_checkouts,
            checkin_count=self.metrics.total_checkins,
            timeout_count=self.metrics.total_timeouts,
            error_count=self.metrics.total_errors,
        )

    def get_metrics(self) -> PoolMetrics:
        """Get aggregated metrics."""
        return self.metrics

    def get_recent_snapshots(self, count: int = 60) -> List[PoolSnapshot]:
        """Get recent snapshots."""
        return list(self._snapshots)[-count:]

    def get_health_history(self, count: int = 20) -> List[PoolHealthCheck]:
        """Get recent health check results."""
        return list(self._health_checks)[-count:]

    def _check_exhaustion(self) -> None:
        """Check for pool exhaustion and alert if needed."""
        utilization = self._active_connections / self.pool_size

        if utilization >= self.exhaustion_threshold:
            asyncio.create_task(
                self._send_alert(
                    "pool_exhaustion",
                    {
                        "active_connections": self._active_connections,
                        "pool_size": self.pool_size,
                        "utilization_percent": utilization * 100,
                    },
                )
            )

    async def _health_check_loop(self) -> None:
        """Background task for periodic health checks."""
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}", exc_info=True)

    async def _perform_health_check(self) -> None:
        """Perform a health check."""
        start_time = time.time()

        try:
            # Check pool availability
            pool_available = self._idle_connections > 0

            # Check connections if callback provided
            connections_healthy = True
            if self._health_check_callback:
                try:
                    if asyncio.iscoroutinefunction(self._health_check_callback):
                        connections_healthy = await self._health_check_callback()
                    else:
                        connections_healthy = self._health_check_callback()
                except Exception as e:
                    connections_healthy = False
                    logger.error(f"Health check callback failed: {e}")

            latency_ms = (time.time() - start_time) * 1000
            success = pool_available and connections_healthy

            health_check = PoolHealthCheck(
                timestamp=datetime.now(),
                success=success,
                latency_ms=latency_ms,
                pool_available=pool_available,
                connections_healthy=connections_healthy,
            )

            self._health_checks.append(health_check)

            if success:
                self.metrics.health_check_successes += 1
            else:
                self.metrics.health_check_failures += 1
                await self._send_alert("health_check_failed", health_check.to_dict())

            logger.debug(
                f"Health check completed: success={success}, " f"latency={latency_ms:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            self.metrics.health_check_failures += 1

            health_check = PoolHealthCheck(
                timestamp=datetime.now(),
                success=False,
                latency_ms=(time.time() - start_time) * 1000,
                pool_available=False,
                connections_healthy=False,
                error=str(e),
            )
            self._health_checks.append(health_check)

    async def _snapshot_loop(self) -> None:
        """Background task to take periodic snapshots."""
        while self._running:
            try:
                await asyncio.sleep(5)  # Snapshot every 5 seconds
                snapshot = self.get_current_snapshot()
                self._snapshots.append(snapshot)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in snapshot loop: {e}", exc_info=True)

    async def _send_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Send an alert to registered handlers."""
        if not self.enable_alerting:
            return

        alert_data = {
            "type": alert_type,
            "timestamp": datetime.now().isoformat(),
            **data,
        }

        logger.warning(f"Pool alert: {alert_type} - {data}")

        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert_type, alert_data)
                else:
                    handler(alert_type, alert_data)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}", exc_info=True)

    def add_alert_handler(self, handler: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add an alert handler."""
        self._alert_handlers.append(handler)
        logger.info(f"Added alert handler: {handler.__name__}")

    def generate_dashboard(self) -> str:
        """
        Generate a text-based dashboard.

        Returns:
            Formatted dashboard string
        """
        snapshot = self.get_current_snapshot()
        metrics = self.get_metrics()

        # Create visual bar for pool utilization
        utilization = snapshot.utilization_percent
        bar_width = 50
        filled = int(bar_width * (utilization / 100))
        bar = "█" * filled + "░" * (bar_width - filled)

        # Determine status color/symbol
        if utilization >= 90:
            status = "🔴 CRITICAL"
        elif utilization >= 75:
            status = "🟡 WARNING"
        else:
            status = "🟢 HEALTHY"

        dashboard_lines = [
            "=" * 80,
            "CONNECTION POOL DASHBOARD",
            "=" * 80,
            "",
            f"STATUS: {status}",
            "",
            "CURRENT STATE:",
            f"  Pool Size: {snapshot.pool_size}",
            f"  Active: {snapshot.active_connections}",
            f"  Idle: {snapshot.idle_connections}",
            f"  Waiting: {snapshot.waiting_count}",
            f"  Utilization: [{bar}] {utilization:.1f}%",
            "",
            "PERFORMANCE:",
            f"  Avg Wait Time: {snapshot.avg_wait_time_ms:.2f}ms",
            f"  Checkouts: {snapshot.checkout_count:,}",
            f"  Checkins: {snapshot.checkin_count:,}",
            f"  Timeouts: {snapshot.timeout_count:,} ({metrics.timeout_rate:.2f}%)",
            f"  Errors: {snapshot.error_count:,} ({metrics.error_rate:.2f}%)",
            "",
            "STATISTICS:",
            f"  Peak Active: {metrics.peak_active_connections}",
            f"  Peak Waiting: {metrics.peak_waiting_count}",
            f"  Health Checks: {metrics.health_check_success_rate:.1f}% success",
            "",
        ]

        # Add recent health checks
        recent_health = self.get_health_history(count=5)
        if recent_health:
            dashboard_lines.append("RECENT HEALTH CHECKS:")
            for hc in recent_health:
                status_icon = "✓" if hc.success else "✗"
                dashboard_lines.append(
                    f"  {status_icon} {hc.timestamp.strftime('%H:%M:%S')} - "
                    f"{hc.latency_ms:.2f}ms"
                )
            dashboard_lines.append("")

        # Add trend analysis
        if len(self._snapshots) >= 2:
            trend = self._analyze_trend()
            dashboard_lines.extend(
                [
                    "TREND ANALYSIS (last 5 min):",
                    f"  Utilization: {trend['utilization']}",
                    f"  Wait Time: {trend['wait_time']}",
                    "",
                ]
            )

        dashboard_lines.extend(
            [
                "=" * 80,
            ]
        )

        return "\n".join(dashboard_lines)

    def _analyze_trend(self) -> Dict[str, str]:
        """Analyze recent trends."""
        if len(self._snapshots) < 10:
            return {
                "utilization": "Insufficient data",
                "wait_time": "Insufficient data",
            }

        # Last 5 minutes (at 5s intervals)
        recent = list(self._snapshots)[-60:]

        # Calculate average utilization for first and second half
        mid = len(recent) // 2
        first_half_util = sum(s.utilization_percent for s in recent[:mid]) / mid
        second_half_util = sum(s.utilization_percent for s in recent[mid:]) / (len(recent) - mid)

        util_diff = second_half_util - first_half_util

        if util_diff > 5:
            util_trend = f"↗ Increasing ({abs(util_diff):.1f}%)"
        elif util_diff < -5:
            util_trend = f"↘ Decreasing ({abs(util_diff):.1f}%)"
        else:
            util_trend = "→ Stable"

        # Wait time trend
        first_half_wait = sum(s.avg_wait_time_ms for s in recent[:mid]) / mid
        second_half_wait = sum(s.avg_wait_time_ms for s in recent[mid:]) / (len(recent) - mid)

        wait_diff = second_half_wait - first_half_wait

        if wait_diff > 50:
            wait_trend = f"↗ Increasing ({abs(wait_diff):.0f}ms)"
        elif wait_diff < -50:
            wait_trend = f"↘ Decreasing ({abs(wait_diff):.0f}ms)"
        else:
            wait_trend = "→ Stable"

        return {
            "utilization": util_trend,
            "wait_time": wait_trend,
        }

    def __repr__(self) -> str:
        """String representation."""
        snapshot = self.get_current_snapshot()
        return (
            f"ConnectionPoolMonitor("
            f"pool_size={self.pool_size}, "
            f"active={snapshot.active_connections}, "
            f"idle={snapshot.idle_connections}, "
            f"utilization={snapshot.utilization_percent:.1f}%)"
        )


# Global pool monitor instance
_pool_monitor: Optional[ConnectionPoolMonitor] = None


def get_pool_monitor() -> ConnectionPoolMonitor:
    """Get the global pool monitor instance."""
    global _pool_monitor

    if _pool_monitor is None:
        _pool_monitor = ConnectionPoolMonitor()

    return _pool_monitor


async def initialize_pool_monitor(pool_size: int = 20, **kwargs) -> ConnectionPoolMonitor:
    """Initialize the global pool monitor."""
    global _pool_monitor

    if _pool_monitor is not None:
        logger.warning("Pool monitor already initialized")
        return _pool_monitor

    _pool_monitor = ConnectionPoolMonitor(pool_size=pool_size, **kwargs)
    await _pool_monitor.start()

    return _pool_monitor
