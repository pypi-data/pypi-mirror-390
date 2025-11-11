"""
Transaction Monitoring Dashboard for CovetPy

Provides real-time monitoring and visualization of transaction metrics:
- Live transaction statistics (count, success rate, duration)
- Active transaction tracking
- Deadlock and timeout detection
- Performance trends
- Health indicators
- Alert management

Features:
- Web-based dashboard (HTML/JavaScript)
- REST API for metrics
- Real-time updates via WebSocket (optional)
- Historical data tracking
- Exportable reports (JSON, CSV)
- Alerting system

Author: CovetPy Framework
License: MIT
"""

import asyncio
import csv
import json
import logging
from collections import deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from io import StringIO
from typing import Any, Deque, Dict, List, Optional

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents a monitoring alert."""

    level: AlertLevel
    message: str
    timestamp: datetime
    metric: str
    value: Any
    threshold: Any = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "level": self.level.value,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "metric": self.metric,
            "value": self.value,
            "threshold": self.threshold,
        }


@dataclass
class TransactionSnapshot:
    """Point-in-time snapshot of transaction metrics."""

    timestamp: datetime
    total_transactions: int
    active_transactions: int
    committed_transactions: int
    rolled_back_transactions: int
    failed_transactions: int
    deadlock_count: int
    timeout_count: int
    retry_count: int
    average_duration_ms: float
    success_rate: float
    failure_rate: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class TransactionDashboard:
    """
    Real-time transaction monitoring dashboard.

    Features:
    - Live metrics tracking
    - Historical data retention
    - Alert management
    - Performance trends
    - Health monitoring

    Usage:
        dashboard = TransactionDashboard(transaction_manager)
        await dashboard.start()

        # Get current metrics
        metrics = dashboard.get_current_metrics()

        # Get historical data
        history = dashboard.get_history(minutes=60)

        # Generate report
        report = dashboard.generate_report()
    """

    def __init__(
        self,
        transaction_manager: "TransactionManager",
        history_retention: int = 3600,  # seconds (1 hour)
        snapshot_interval: float = 10.0,  # seconds
        alert_thresholds: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize transaction dashboard.

        Args:
            transaction_manager: TransactionManager to monitor
            history_retention: How long to retain historical data (seconds)
            snapshot_interval: How often to take snapshots (seconds)
            alert_thresholds: Dictionary of alert thresholds
        """
        self.transaction_manager = transaction_manager
        self.history_retention = history_retention
        self.snapshot_interval = snapshot_interval

        # Set default alert thresholds
        self.alert_thresholds = alert_thresholds or {
            "max_active_transactions": 100,
            "max_transaction_duration_ms": 30000,  # 30 seconds
            "min_success_rate": 95.0,  # 95%
            "max_deadlock_count": 10,
            "max_timeout_count": 5,
        }

        # Historical data storage (circular buffer)
        max_snapshots = int(history_retention / snapshot_interval)
        self.snapshots: Deque[TransactionSnapshot] = deque(maxlen=max_snapshots)

        # Alert history (last 1000 alerts)
        self.alerts: Deque[Alert] = deque(maxlen=1000)

        # Dashboard state
        self._running = False
        self._snapshot_task: Optional[asyncio.Task] = None
        self._alert_task: Optional[asyncio.Task] = None

        logger.info(
            f"TransactionDashboard initialized "
            f"(retention={history_retention}s, interval={snapshot_interval}s)"
        )

    async def start(self) -> None:
        """
        Start the dashboard monitoring.

        Begins taking periodic snapshots and checking alert conditions.
        """
        if self._running:
            logger.warning("Dashboard already running")
            return

        self._running = True

        # Start snapshot collection
        self._snapshot_task = asyncio.create_task(self._snapshot_loop())

        # Start alert monitoring
        self._alert_task = asyncio.create_task(self._alert_loop())

        logger.info("TransactionDashboard started")

    async def stop(self) -> None:
        """
        Stop the dashboard monitoring.

        Stops all background tasks and preserves current data.
        """
        if not self._running:
            return

        self._running = False

        # Cancel tasks
        if self._snapshot_task:
            self._snapshot_task.cancel()
            try:
                await self._snapshot_task
            except asyncio.CancelledError:
                pass

        if self._alert_task:
            self._alert_task.cancel()
            try:
                await self._alert_task
            except asyncio.CancelledError:
                pass

        logger.info("TransactionDashboard stopped")

    async def _snapshot_loop(self) -> None:
        """Background task for taking periodic snapshots."""
        try:
            while self._running:
                # Take snapshot
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)

                # Wait for next snapshot
                await asyncio.sleep(self.snapshot_interval)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Snapshot loop error: {e}")

    async def _alert_loop(self) -> None:
        """Background task for checking alert conditions."""
        try:
            while self._running:
                # Check alert conditions
                await self._check_alerts()

                # Check alerts more frequently than snapshots
                await asyncio.sleep(self.snapshot_interval / 2)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Alert loop error: {e}")

    def _take_snapshot(self) -> TransactionSnapshot:
        """
        Take a point-in-time snapshot of transaction metrics.

        Returns:
            TransactionSnapshot with current metrics
        """
        metrics = self.transaction_manager.get_metrics()

        return TransactionSnapshot(
            timestamp=datetime.now(),
            total_transactions=metrics["total_transactions"],
            active_transactions=metrics["active_transactions"],
            committed_transactions=metrics["committed_transactions"],
            rolled_back_transactions=metrics["rolled_back_transactions"],
            failed_transactions=metrics["failed_transactions"],
            deadlock_count=metrics["deadlock_count"],
            timeout_count=metrics["timeout_count"],
            retry_count=metrics["retry_count"],
            average_duration_ms=metrics["average_duration_ms"],
            success_rate=metrics["success_rate"],
            failure_rate=metrics["failure_rate"],
        )

    async def _check_alerts(self) -> None:
        """Check current metrics against alert thresholds."""
        metrics = self.transaction_manager.get_metrics()
        now = datetime.now()

        # Check active transaction count
        if metrics["active_transactions"] > self.alert_thresholds["max_active_transactions"]:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"High number of active transactions: {metrics['active_transactions']}",
                timestamp=now,
                metric="active_transactions",
                value=metrics["active_transactions"],
                threshold=self.alert_thresholds["max_active_transactions"],
            )
            self._add_alert(alert)

        # Check success rate
        if (
            metrics["total_transactions"] > 0
            and metrics["success_rate"] < self.alert_thresholds["min_success_rate"]
        ):
            alert = Alert(
                level=AlertLevel.ERROR,
                message=f"Low transaction success rate: {metrics['success_rate']:.1f}%",
                timestamp=now,
                metric="success_rate",
                value=metrics["success_rate"],
                threshold=self.alert_thresholds["min_success_rate"],
            )
            self._add_alert(alert)

        # Check deadlock count
        if metrics["deadlock_count"] > self.alert_thresholds["max_deadlock_count"]:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                message=f"High deadlock count: {metrics['deadlock_count']}",
                timestamp=now,
                metric="deadlock_count",
                value=metrics["deadlock_count"],
                threshold=self.alert_thresholds["max_deadlock_count"],
            )
            self._add_alert(alert)

        # Check timeout count
        if metrics["timeout_count"] > self.alert_thresholds["max_timeout_count"]:
            alert = Alert(
                level=AlertLevel.ERROR,
                message=f"High timeout count: {metrics['timeout_count']}",
                timestamp=now,
                metric="timeout_count",
                value=metrics["timeout_count"],
                threshold=self.alert_thresholds["max_timeout_count"],
            )
            self._add_alert(alert)

        # Check for long-running transactions
        active_txns = self.transaction_manager.get_active_transactions()
        max_duration = self.alert_thresholds["max_transaction_duration_ms"]

        for txn in active_txns:
            if txn["duration_ms"] > max_duration:
                alert = Alert(
                    level=AlertLevel.WARNING,
                    message=(
                        f"Long-running transaction: {txn['transaction_id']} "
                        f"({txn['duration_ms']:.0f}ms)"
                    ),
                    timestamp=now,
                    metric="transaction_duration",
                    value=txn["duration_ms"],
                    threshold=max_duration,
                )
                self._add_alert(alert)

    def _add_alert(self, alert: Alert) -> None:
        """
        Add an alert if not duplicate.

        Prevents alert spam by checking for recent similar alerts.
        """
        # Check for duplicate alerts in last 5 minutes
        cutoff = datetime.now() - timedelta(minutes=5)
        recent_similar = [
            a
            for a in self.alerts
            if a.metric == alert.metric and a.level == alert.level and a.timestamp > cutoff
        ]

        if not recent_similar:
            self.alerts.append(alert)
            logger.log(
                logging.WARNING if alert.level == AlertLevel.WARNING else logging.ERROR,
                alert.message,
            )

    def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get current transaction metrics.

        Returns:
            Dictionary with current metrics
        """
        return self.transaction_manager.get_metrics()

    def get_active_transactions(self) -> List[Dict[str, Any]]:
        """
        Get list of currently active transactions.

        Returns:
            List of active transaction info dictionaries
        """
        return self.transaction_manager.get_active_transactions()

    def get_history(
        self,
        minutes: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get historical transaction metrics.

        Args:
            minutes: Number of minutes of history to retrieve
            limit: Maximum number of snapshots to return

        Returns:
            List of historical snapshots as dictionaries
        """
        snapshots = list(self.snapshots)

        # Filter by time if specified
        if minutes:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            snapshots = [s for s in snapshots if s.timestamp > cutoff]

        # Apply limit if specified
        if limit:
            snapshots = snapshots[-limit:]

        return [s.to_dict() for s in snapshots]

    def get_alerts(
        self,
        minutes: Optional[int] = None,
        level: Optional[AlertLevel] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get historical alerts.

        Args:
            minutes: Number of minutes of alerts to retrieve
            level: Filter by alert level
            limit: Maximum number of alerts to return

        Returns:
            List of alerts as dictionaries
        """
        alerts = list(self.alerts)

        # Filter by time if specified
        if minutes:
            cutoff = datetime.now() - timedelta(minutes=minutes)
            alerts = [a for a in alerts if a.timestamp > cutoff]

        # Filter by level if specified
        if level:
            alerts = [a for a in alerts if a.level == level]

        # Apply limit if specified
        if limit:
            alerts = alerts[-limit:]

        return [a.to_dict() for a in alerts]

    def get_performance_trends(self, minutes: int = 60) -> Dict[str, Any]:
        """
        Calculate performance trends over specified time period.

        Args:
            minutes: Time period for trend calculation

        Returns:
            Dictionary with trend analysis
        """
        history = self.get_history(minutes=minutes)

        if len(history) < 2:
            return {
                "period_minutes": minutes,
                "data_points": len(history),
                "trends": {},
            }

        # Calculate trends
        first = history[0]
        last = history[-1]

        trends = {
            "transaction_count_change": (last["total_transactions"] - first["total_transactions"]),
            "success_rate_change": last["success_rate"] - first["success_rate"],
            "average_duration_change": (last["average_duration_ms"] - first["average_duration_ms"]),
            "deadlock_count_change": last["deadlock_count"] - first["deadlock_count"],
            "timeout_count_change": last["timeout_count"] - first["timeout_count"],
        }

        # Calculate averages over period
        averages = {
            "avg_active_transactions": sum(h["active_transactions"] for h in history)
            / len(history),
            "avg_success_rate": sum(h["success_rate"] for h in history) / len(history),
            "avg_duration_ms": sum(h["average_duration_ms"] for h in history) / len(history),
        }

        return {
            "period_minutes": minutes,
            "data_points": len(history),
            "trends": trends,
            "averages": averages,
        }

    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status of transaction system.

        Returns:
            Dictionary with health indicators and status
        """
        metrics = self.get_current_metrics()
        recent_alerts = self.get_alerts(minutes=30)

        # Calculate health score (0-100)
        score = 100

        # Deduct points for issues
        if metrics["success_rate"] < 95:
            score -= (95 - metrics["success_rate"]) * 2

        if metrics["deadlock_count"] > 0:
            score -= min(metrics["deadlock_count"] * 5, 20)

        if metrics["timeout_count"] > 0:
            score -= min(metrics["timeout_count"] * 5, 20)

        if metrics["active_transactions"] > 50:
            score -= min((metrics["active_transactions"] - 50) / 2, 20)

        # Alert-based deductions
        critical_alerts = len([a for a in recent_alerts if a["level"] == "critical"])
        error_alerts = len([a for a in recent_alerts if a["level"] == "error"])

        score -= critical_alerts * 10
        score -= error_alerts * 5

        score = max(0, score)

        # Determine status
        if score >= 90:
            status = "healthy"
        elif score >= 70:
            status = "degraded"
        elif score >= 50:
            status = "warning"
        else:
            status = "critical"

        return {
            "status": status,
            "health_score": score,
            "issues": {
                "success_rate_below_95": metrics["success_rate"] < 95,
                "deadlocks_detected": metrics["deadlock_count"] > 0,
                "timeouts_detected": metrics["timeout_count"] > 0,
                "high_active_count": metrics["active_transactions"] > 50,
                "recent_critical_alerts": critical_alerts,
                "recent_error_alerts": error_alerts,
            },
            "recommendations": self._generate_recommendations(metrics, recent_alerts),
        }

    def _generate_recommendations(
        self,
        metrics: Dict[str, Any],
        alerts: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Generate recommendations based on current state.

        Args:
            metrics: Current metrics
            alerts: Recent alerts

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if metrics["success_rate"] < 95:
            recommendations.append(
                "Low success rate detected. Review failed transactions and error logs."
            )

        if metrics["deadlock_count"] > 5:
            recommendations.append(
                "High deadlock count. Review transaction isolation levels and lock ordering."
            )

        if metrics["timeout_count"] > 3:
            recommendations.append(
                "Multiple transaction timeouts. Check for long-running queries and optimize."
            )

        if metrics["active_transactions"] > 50:
            recommendations.append(
                "High number of active transactions. Consider scaling connection pool or optimizing transaction duration."
            )

        if metrics["average_duration_ms"] > 5000:
            recommendations.append(
                "High average transaction duration. Profile slow transactions and optimize queries."
            )

        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        if critical_alerts:
            recommendations.append(
                f"Critical alerts detected ({len(critical_alerts)}). Immediate attention required."
            )

        return recommendations

    def generate_report(
        self,
        format: str = "json",
        include_history: bool = True,
        history_minutes: int = 60,
    ) -> str:
        """
        Generate comprehensive monitoring report.

        Args:
            format: Report format ('json' or 'csv')
            include_history: Include historical data
            history_minutes: How many minutes of history to include

        Returns:
            Report as string in specified format
        """
        # Gather report data
        report_data = {
            "generated_at": datetime.now().isoformat(),
            "current_metrics": self.get_current_metrics(),
            "active_transactions": self.get_active_transactions(),
            "health_status": self.get_health_status(),
            "recent_alerts": self.get_alerts(minutes=history_minutes),
            "performance_trends": self.get_performance_trends(minutes=history_minutes),
        }

        if include_history:
            report_data["history"] = self.get_history(minutes=history_minutes)

        # Format output
        if format == "json":
            return json.dumps(report_data, indent=2)
        elif format == "csv":
            return self._generate_csv_report(report_data)
        else:
            raise ValueError(f"Unsupported report format: {format}")

    def _generate_csv_report(self, report_data: Dict[str, Any]) -> str:
        """
        Generate CSV report from report data.

        Args:
            report_data: Report data dictionary

        Returns:
            CSV formatted string
        """
        output = StringIO()

        # Write metrics summary
        writer = csv.writer(output)
        writer.writerow(["Transaction Metrics Summary"])
        writer.writerow(["Metric", "Value"])

        metrics = report_data["current_metrics"]
        for key, value in metrics.items():
            writer.writerow([key, value])

        writer.writerow([])

        # Write health status
        writer.writerow(["Health Status"])
        health = report_data["health_status"]
        writer.writerow(["Status", health["status"]])
        writer.writerow(["Score", health["health_score"]])

        writer.writerow([])

        # Write recent alerts
        writer.writerow(["Recent Alerts"])
        writer.writerow(["Level", "Metric", "Message", "Timestamp"])

        for alert in report_data["recent_alerts"]:
            writer.writerow(
                [
                    alert["level"],
                    alert["metric"],
                    alert["message"],
                    alert["timestamp"],
                ]
            )

        return output.getvalue()

    def get_dashboard_html(self) -> str:
        """
        Generate HTML dashboard for web viewing.

        Returns:
            HTML string with embedded JavaScript for dashboard
        """
        metrics = self.get_current_metrics()
        health = self.get_health_status()
        active_txns = self.get_active_transactions()
        recent_alerts = self.get_alerts(minutes=60, limit=10)

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CovetPy Transaction Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #333;
            margin-bottom: 30px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .metric-unit {{
            font-size: 14px;
            color: #999;
        }}
        .health-status {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .health-score {{
            font-size: 48px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .status-healthy {{ color: #4caf50; }}
        .status-degraded {{ color: #ff9800; }}
        .status-warning {{ color: #ff5722; }}
        .status-critical {{ color: #f44336; }}
        .section {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            margin-bottom: 15px;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        th {{
            background: #f9f9f9;
            font-weight: 600;
        }}
        .alert-info {{ color: #2196f3; }}
        .alert-warning {{ color: #ff9800; }}
        .alert-error {{ color: #f44336; }}
        .alert-critical {{ color: #b71c1c; font-weight: bold; }}
        .refresh-notice {{
            text-align: center;
            color: #666;
            margin-top: 20px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>CovetPy Transaction Dashboard</h1>

        <!-- Health Status -->
        <div class="health-status">
            <h2>System Health</h2>
            <div class="health-score status-{health['status']}">
                {health['health_score']}/100
            </div>
            <div style="font-size: 18px; color: #666;">
                Status: <span class="status-{health['status']}" style="font-weight: bold; text-transform: uppercase;">{health['status']}</span>
            </div>
        </div>

        <!-- Metrics Grid -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Transactions</div>
                <div class="metric-value">{metrics['total_transactions']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Active Transactions</div>
                <div class="metric-value">{metrics['active_transactions']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{metrics['success_rate']:.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Duration</div>
                <div class="metric-value">{metrics['average_duration_ms']:.0f}<span class="metric-unit">ms</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Deadlocks</div>
                <div class="metric-value">{metrics['deadlock_count']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Timeouts</div>
                <div class="metric-value">{metrics['timeout_count']}</div>
            </div>
        </div>

        <!-- Active Transactions -->
        <div class="section">
            <h2>Active Transactions ({len(active_txns)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Transaction ID</th>
                        <th>Level</th>
                        <th>Duration</th>
                        <th>Isolation</th>
                        <th>State</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr>
                        <td>{txn['transaction_id'][:12]}...</td>
                        <td>{txn['level']}</td>
                        <td>{txn['duration_ms']:.0f}ms</td>
                        <td>{txn['isolation']}</td>
                        <td>{txn['state']}</td>
                    </tr>
                    ''' for txn in active_txns[:10]) if active_txns else '<tr><td colspan="5" style="text-align: center; color: #999;">No active transactions</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- Recent Alerts -->
        <div class="section">
            <h2>Recent Alerts ({len(recent_alerts)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Level</th>
                        <th>Message</th>
                        <th>Metric</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr>
                        <td class="alert-{alert['level']}">{alert['level'].upper()}</td>
                        <td>{alert['message']}</td>
                        <td>{alert['metric']}</td>
                        <td>{alert['timestamp'].split('T')[1][:8]}</td>
                    </tr>
                    ''' for alert in recent_alerts) if recent_alerts else '<tr><td colspan="4" style="text-align: center; color: #999;">No recent alerts</td></tr>'}
                </tbody>
            </table>
        </div>

        <!-- Recommendations -->
        {f'''
        <div class="section">
            <h2>Recommendations</h2>
            <ul style="padding-left: 20px;">
                {''.join(f'<li style="margin: 10px 0; color: #666;">{rec}</li>' for rec in health['recommendations'])}
            </ul>
        </div>
        ''' if health['recommendations'] else ''}

        <div class="refresh-notice">
            Dashboard generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Refresh page for updates
        </div>
    </div>
</body>
</html>
"""
        return html

    def __repr__(self) -> str:
        """String representation of dashboard."""
        return (
            f"TransactionDashboard("
            f"snapshots={len(self.snapshots)}, "
            f"alerts={len(self.alerts)}, "
            f"running={self._running}"
            f")"
        )


__all__ = [
    "TransactionDashboard",
    "Alert",
    "AlertLevel",
    "TransactionSnapshot",
]
