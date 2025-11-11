"""
Lag Monitor - Replication Lag Detection and Alerting

Enterprise lag monitoring system with:
- Real-time lag measurement
- Threshold-based alerting
- Historical lag tracking
- Automatic replica removal on excessive lag
- Predictive lag analysis

Production Features:
- Multi-level threshold alerting
- Lag trend detection
- Automatic remediation
- Integration with monitoring systems
- Detailed lag metrics
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from statistics import mean, stdev
from typing import Any, Callable, Deque, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LagThreshold(Enum):
    """Predefined lag thresholds."""

    LOW = 1.0  # 1 second
    MEDIUM = 5.0  # 5 seconds
    HIGH = 10.0  # 10 seconds
    CRITICAL = 30.0  # 30 seconds


@dataclass
class LagMeasurement:
    """Single lag measurement."""

    replica_id: str
    timestamp: datetime
    lag_seconds: float
    lag_bytes: Optional[int] = None
    replication_state: Optional[str] = None
    sync_state: Optional[str] = None

    def is_acceptable(self, threshold: float) -> bool:
        """Check if lag is within acceptable threshold."""
        return self.lag_seconds <= threshold


@dataclass
class LagAlert:
    """Replication lag alert."""

    alert_id: str
    replica_id: str
    severity: AlertSeverity
    lag_seconds: float
    threshold: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    def resolve(self) -> None:
        """Mark alert as resolved."""
        self.resolved = True
        self.resolved_at = datetime.now()


@dataclass
class LagStatistics:
    """Statistical analysis of replication lag."""

    replica_id: str
    mean_lag: float
    median_lag: float
    min_lag: float
    max_lag: float
    std_dev: float
    p95_lag: float
    p99_lag: float
    measurement_count: int
    time_window_seconds: float

    def is_trending_up(self, rate_threshold: float = 0.1) -> bool:
        """Check if lag is trending upward."""
        # Simplified - would use linear regression in production
        return self.std_dev > self.mean_lag * rate_threshold


class LagMonitor:
    """
    Enterprise Replication Lag Monitor

    Continuously monitors replication lag and generates alerts.

    Example:
        monitor = LagMonitor(
            replica_manager=replica_manager,
            thresholds={
                AlertSeverity.WARNING: 5.0,
                AlertSeverity.ERROR: 10.0,
                AlertSeverity.CRITICAL: 30.0,
            }
        )

        # Register alert callback
        async def handle_alert(alert: LagAlert):
            logger.error(f"Lag alert: {alert.message}")

        monitor.register_alert_callback(handle_alert)

        await monitor.start()
    """

    def __init__(
        self,
        replica_manager,
        thresholds: Optional[Dict[AlertSeverity, float]] = None,
        check_interval: float = 5.0,
        history_size: int = 1000,
        auto_remediate: bool = True,
        remediation_threshold: float = 60.0,
    ):
        """
        Initialize lag monitor.

        Args:
            replica_manager: ReplicaManager instance
            thresholds: Alert thresholds by severity
            check_interval: Lag check interval in seconds
            history_size: Number of measurements to keep
            auto_remediate: Enable automatic remediation
            remediation_threshold: Lag threshold for auto-remediation
        """
        self.replica_manager = replica_manager
        self.check_interval = check_interval
        self.history_size = history_size
        self.auto_remediate = auto_remediate
        self.remediation_threshold = remediation_threshold

        # Set default thresholds
        self.thresholds = thresholds or {
            AlertSeverity.INFO: 1.0,
            AlertSeverity.WARNING: 5.0,
            AlertSeverity.ERROR: 10.0,
            AlertSeverity.CRITICAL: 30.0,
        }

        # State
        self._running = False
        self._monitor_task: Optional[asyncio.Task] = None

        # Lag history per replica
        self._lag_history: Dict[str, Deque[LagMeasurement]] = {}

        # Active alerts
        self._active_alerts: Dict[str, List[LagAlert]] = {}
        self._alert_counter = 0

        # Callbacks
        self._alert_callbacks: List[Callable[[LagAlert], None]] = []
        self._remediation_callbacks: List[Callable[[str, float], None]] = []

        # Metrics
        self._total_measurements = 0
        self._total_alerts = 0
        self._total_remediations = 0

        logger.info("LagMonitor initialized")

    async def start(self) -> None:
        """Start lag monitoring."""
        if self._running:
            logger.warning("LagMonitor already running")
            return

        logger.info("Starting LagMonitor...")

        self._running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())

        logger.info("LagMonitor started")

    async def stop(self) -> None:
        """Stop lag monitoring."""
        if not self._running:
            return

        logger.info("Stopping LagMonitor...")

        self._running = False

        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("LagMonitor stopped")

    async def _monitor_loop(self) -> None:
        """Continuous lag monitoring loop."""
        logger.info(f"Starting lag monitoring (interval: {self.check_interval}s)")

        while self._running:
            try:
                await self._check_all_replicas()
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in lag monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

    async def _check_all_replicas(self) -> None:
        """Check lag for all replicas."""
        replicas = self.replica_manager.get_all_replicas(include_unhealthy=True)

        tasks = [
            self._check_replica_lag(replica_id, config) for replica_id, config, health in replicas
        ]

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _check_replica_lag(self, replica_id: str, config) -> None:
        """Check lag for a single replica."""
        try:
            # Get adapter
            adapter = self.replica_manager._adapters.get(replica_id)
            if not adapter:
                logger.debug(f"No adapter for replica {replica_id}")
                return

            # Measure lag
            measurement = await self._measure_lag(replica_id, adapter)

            if measurement:
                # Store in history
                self._add_measurement(measurement)

                # Check thresholds and generate alerts
                await self._check_thresholds(measurement)

                # Auto-remediate if needed
                if self.auto_remediate:
                    await self._auto_remediate(measurement)

                self._total_measurements += 1

        except Exception as e:
            logger.error(f"Error checking lag for {replica_id}: {e}")

    async def _measure_lag(self, replica_id: str, adapter: Any) -> Optional[LagMeasurement]:
        """
        Measure replication lag for a replica.

        Uses PostgreSQL-specific lag measurement queries.
        """
        try:
            # Check if this is a replica
            is_replica = await adapter.fetch_value("SELECT pg_is_in_recovery()")

            if not is_replica:
                # Not a replica (might be primary)
                return LagMeasurement(
                    replica_id=replica_id,
                    timestamp=datetime.now(),
                    lag_seconds=0.0,
                    replication_state="primary",
                )

            # Get lag in seconds
            lag_query = """
                SELECT
                    EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) AS lag_seconds,
                    pg_is_in_recovery() AS is_replica
            """

            result = await adapter.fetch_one(lag_query)

            if result:
                lag_seconds = result.get("lag_seconds") or 0.0

                return LagMeasurement(
                    replica_id=replica_id,
                    timestamp=datetime.now(),
                    lag_seconds=max(0.0, lag_seconds),
                    replication_state="streaming",
                )

        except Exception as e:
            logger.debug(f"Could not measure lag for {replica_id}: {e}")

        return None

    def _add_measurement(self, measurement: LagMeasurement) -> None:
        """Add measurement to history."""
        if measurement.replica_id not in self._lag_history:
            self._lag_history[measurement.replica_id] = deque(maxlen=self.history_size)

        self._lag_history[measurement.replica_id].append(measurement)

    async def _check_thresholds(self, measurement: LagMeasurement) -> None:
        """Check if measurement exceeds thresholds and generate alerts."""
        replica_id = measurement.replica_id
        lag = measurement.lag_seconds

        # Determine severity
        severity = None
        threshold = 0.0

        for sev, thresh in sorted(self.thresholds.items(), key=lambda x: x[1], reverse=True):
            if lag >= thresh:
                severity = sev
                threshold = thresh
                break

        if severity:
            # Check if alert already exists
            existing_alerts = self._active_alerts.get(replica_id, [])
            has_active_alert = any(
                not alert.resolved and alert.severity == severity for alert in existing_alerts
            )

            if not has_active_alert:
                # Create new alert
                alert = LagAlert(
                    alert_id=f"lag_{self._alert_counter}",
                    replica_id=replica_id,
                    severity=severity,
                    lag_seconds=lag,
                    threshold=threshold,
                    message=f"Replication lag {severity.value}: {replica_id} is {lag:.2f}s behind (threshold: {threshold}s)",
                )

                self._alert_counter += 1
                self._total_alerts += 1

                # Store alert
                if replica_id not in self._active_alerts:
                    self._active_alerts[replica_id] = []

                self._active_alerts[replica_id].append(alert)

                logger.warning(alert.message)

                # Call alert callbacks
                for callback in self._alert_callbacks:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(alert)
                        else:
                            callback(alert)
                    except Exception as e:
                        logger.error(f"Error in alert callback: {e}")

        else:
            # Lag is acceptable - resolve any active alerts
            await self._resolve_alerts(replica_id)

    async def _resolve_alerts(self, replica_id: str) -> None:
        """Resolve active alerts for a replica."""
        if replica_id in self._active_alerts:
            for alert in self._active_alerts[replica_id]:
                if not alert.resolved:
                    alert.resolve()
                    logger.info(f"Resolved alert: {alert.alert_id}")

    async def _auto_remediate(self, measurement: LagMeasurement) -> None:
        """
        Automatically remediate excessive lag.

        Removes replica from rotation if lag exceeds threshold.
        """
        if measurement.lag_seconds >= self.remediation_threshold:
            replica_id = measurement.replica_id

            logger.warning(
                f"Auto-remediation triggered for {replica_id}: "
                f"lag={measurement.lag_seconds:.2f}s (threshold={self.remediation_threshold}s)"
            )

            # Mark replica as unhealthy in manager
            health = self.replica_manager.health_status.get(replica_id)
            if health:
                from .manager import ReplicaStatus

                health.status = ReplicaStatus.UNHEALTHY

            self._total_remediations += 1

            # Call remediation callbacks
            for callback in self._remediation_callbacks:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(replica_id, measurement.lag_seconds)
                    else:
                        callback(replica_id, measurement.lag_seconds)
                except Exception as e:
                    logger.error(f"Error in remediation callback: {e}")

    def get_current_lag(self, replica_id: str) -> Optional[float]:
        """Get current lag for a replica."""
        history = self._lag_history.get(replica_id)
        if history and len(history) > 0:
            return history[-1].lag_seconds
        return None

    def get_lag_statistics(
        self, replica_id: str, time_window_seconds: Optional[float] = None
    ) -> Optional[LagStatistics]:
        """
        Get lag statistics for a replica.

        Args:
            replica_id: Replica identifier
            time_window_seconds: Time window for statistics (None = all history)

        Returns:
            LagStatistics or None
        """
        history = self._lag_history.get(replica_id)
        if not history or len(history) == 0:
            return None

        # Filter by time window
        measurements = list(history)
        if time_window_seconds:
            cutoff = datetime.now() - timedelta(seconds=time_window_seconds)
            measurements = [m for m in measurements if m.timestamp >= cutoff]

        if not measurements:
            return None

        lags = [m.lag_seconds for m in measurements]
        lags_sorted = sorted(lags)

        # Calculate percentiles
        count = len(lags_sorted)
        p95_idx = int(count * 0.95)
        p99_idx = int(count * 0.99)

        return LagStatistics(
            replica_id=replica_id,
            mean_lag=mean(lags),
            median_lag=lags_sorted[count // 2],
            min_lag=min(lags),
            max_lag=max(lags),
            std_dev=stdev(lags) if len(lags) > 1 else 0.0,
            p95_lag=lags_sorted[p95_idx] if p95_idx < count else lags_sorted[-1],
            p99_lag=lags_sorted[p99_idx] if p99_idx < count else lags_sorted[-1],
            measurement_count=count,
            time_window_seconds=time_window_seconds or 0.0,
        )

    def get_active_alerts(
        self, replica_id: Optional[str] = None, severity: Optional[AlertSeverity] = None
    ) -> List[LagAlert]:
        """
        Get active alerts.

        Args:
            replica_id: Filter by replica (None = all)
            severity: Filter by severity (None = all)

        Returns:
            List of active alerts
        """
        alerts = []

        if replica_id:
            alerts = self._active_alerts.get(replica_id, [])
        else:
            for replica_alerts in self._active_alerts.values():
                alerts.extend(replica_alerts)

        # Filter by severity
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        # Filter unresolved
        alerts = [a for a in alerts if not a.resolved]

        return alerts

    def get_lag_history(self, replica_id: str, limit: Optional[int] = None) -> List[LagMeasurement]:
        """Get lag measurement history for a replica."""
        history = self._lag_history.get(replica_id)
        if not history:
            return []

        measurements = list(history)
        if limit:
            measurements = measurements[-limit:]

        return measurements

    def register_alert_callback(self, callback: Callable[[LagAlert], None]) -> None:
        """Register callback for lag alerts."""
        self._alert_callbacks.append(callback)

    def register_remediation_callback(self, callback: Callable[[str, float], None]) -> None:
        """Register callback for auto-remediation events."""
        self._remediation_callbacks.append(callback)

    def get_metrics(self) -> Dict[str, Any]:
        """Get monitoring metrics."""
        active_alert_count = sum(
            sum(1 for a in alerts if not a.resolved) for alerts in self._active_alerts.values()
        )

        return {
            "total_measurements": self._total_measurements,
            "total_alerts": self._total_alerts,
            "active_alerts": active_alert_count,
            "total_remediations": self._total_remediations,
            "monitored_replicas": len(self._lag_history),
            "check_interval": self.check_interval,
            "auto_remediate_enabled": self.auto_remediate,
        }

    def reset_metrics(self) -> None:
        """Reset monitoring metrics."""
        self._total_measurements = 0
        self._total_alerts = 0
        self._total_remediations = 0

    def clear_history(self, replica_id: Optional[str] = None) -> None:
        """
        Clear lag history.

        Args:
            replica_id: Clear specific replica (None = all)
        """
        if replica_id:
            if replica_id in self._lag_history:
                self._lag_history[replica_id].clear()
        else:
            self._lag_history.clear()


__all__ = [
    "LagMonitor",
    "LagAlert",
    "LagThreshold",
    "LagMeasurement",
    "LagStatistics",
    "AlertSeverity",
]
