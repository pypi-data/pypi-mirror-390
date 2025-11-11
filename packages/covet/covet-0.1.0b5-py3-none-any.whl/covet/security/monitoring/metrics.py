"""
Security Metrics Collection with Prometheus Integration

Collects and exports security metrics:
- Failed login attempts
- Authorization failures
- Blocked IPs
- Attack attempts by type
- Response times
- Active sessions
- Token usage

Prometheus integration for monitoring and alerting.
"""

import asyncio
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class MetricType(str, Enum):
    """Metric types"""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """Security metric"""

    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str]
    help_text: str
    timestamp: float


class PrometheusExporter:
    """
    Prometheus metrics exporter.

    Formats metrics in Prometheus exposition format.
    """

    def __init__(self):
        """Initialize Prometheus exporter"""
        self.metrics: Dict[str, Metric] = {}
        self._lock = asyncio.Lock()

    async def register_metric(self, name: str, metric_type: MetricType, help_text: str):
        """Register a metric"""
        async with self._lock:
            if name not in self.metrics:
                self.metrics[name] = Metric(
                    name=name,
                    value=0,
                    metric_type=metric_type,
                    labels={},
                    help_text=help_text,
                    timestamp=time.time(),
                )

    async def set_value(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set metric value"""
        async with self._lock:
            key = self._get_metric_key(name, labels or {})
            if name in self.metrics:
                metric = self.metrics[name]
                self.metrics[key] = Metric(
                    name=name,
                    value=value,
                    metric_type=metric.metric_type,
                    labels=labels or {},
                    help_text=metric.help_text,
                    timestamp=time.time(),
                )

    async def increment(
        self, name: str, value: float = 1.0, labels: Optional[Dict[str, str]] = None
    ):
        """Increment counter metric"""
        async with self._lock:
            key = self._get_metric_key(name, labels or {})
            if key in self.metrics:
                self.metrics[key].value += value
                self.metrics[key].timestamp = time.time()

    async def export_metrics(self) -> str:
        """
        Export metrics in Prometheus format.

        Returns:
            Prometheus exposition format
        """
        async with self._lock:
            output = []
            metrics_by_name = defaultdict(list)

            # Group metrics by name
            for key, metric in self.metrics.items():
                metrics_by_name[metric.name].append(metric)

            # Format each metric group
            for name, metrics in metrics_by_name.items():
                if not metrics:
                    continue

                # Add HELP and TYPE
                output.append(f"# HELP {name} {metrics[0].help_text}")
                output.append(f"# TYPE {name} {metrics[0].metric_type.value}")

                # Add metric values
                for metric in metrics:
                    if metric.labels:
                        label_str = ",".join(f'{k}="{v}"' for k, v in metric.labels.items())
                        output.append(f"{name}{{{label_str}}} {metric.value}")
                    else:
                        output.append(f"{name} {metric.value}")

            return "\n".join(output)

    def _get_metric_key(self, name: str, labels: Dict[str, str]) -> str:
        """Generate unique metric key"""
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}:{label_str}" if label_str else name


class SecurityMetrics:
    """
    Security metrics collector.

    Tracks security-related metrics for monitoring.
    """

    def __init__(self, enable_prometheus: bool = True):
        """Initialize security metrics"""
        self.enable_prometheus = enable_prometheus
        self.prometheus = PrometheusExporter() if enable_prometheus else None

        # Metrics storage
        self.metrics = {
            "login_attempts": defaultdict(int),
            "login_failures": defaultdict(int),
            "authorization_failures": defaultdict(int),
            "blocked_ips": set(),
            "attack_attempts": defaultdict(int),
            "active_sessions": 0,
            "token_issuances": 0,
            "token_revocations": 0,
            "response_times": deque(maxlen=1000),
        }

        self._lock = asyncio.Lock()

        # Initialize Prometheus metrics
        if self.prometheus:
            asyncio.create_task(self._init_prometheus_metrics())

    async def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics"""
        await self.prometheus.register_metric(
            "security_login_attempts_total", MetricType.COUNTER, "Total login attempts"
        )
        await self.prometheus.register_metric(
            "security_login_failures_total", MetricType.COUNTER, "Total login failures"
        )
        await self.prometheus.register_metric(
            "security_authorization_failures_total",
            MetricType.COUNTER,
            "Total authorization failures",
        )
        await self.prometheus.register_metric(
            "security_blocked_ips_total", MetricType.GAUGE, "Number of blocked IPs"
        )
        await self.prometheus.register_metric(
            "security_attack_attempts_total", MetricType.COUNTER, "Total attack attempts by type"
        )
        await self.prometheus.register_metric(
            "security_active_sessions", MetricType.GAUGE, "Number of active sessions"
        )
        await self.prometheus.register_metric(
            "security_response_time_seconds", MetricType.HISTOGRAM, "Security check response times"
        )

    async def record_login_attempt(self, success: bool, user_id: Optional[str] = None):
        """Record login attempt"""
        async with self._lock:
            self.metrics["login_attempts"][user_id or "unknown"] += 1

            if not success:
                self.metrics["login_failures"][user_id or "unknown"] += 1

        if self.prometheus:
            await self.prometheus.increment(
                "security_login_attempts_total",
                labels={"status": "success" if success else "failure"},
            )

    async def record_authorization_failure(self, user_id: str, resource: str):
        """Record authorization failure"""
        async with self._lock:
            self.metrics["authorization_failures"][user_id] += 1

        if self.prometheus:
            await self.prometheus.increment(
                "security_authorization_failures_total", labels={"user_id": user_id}
            )

    async def record_blocked_ip(self, ip: str):
        """Record blocked IP"""
        async with self._lock:
            self.metrics["blocked_ips"].add(ip)

        if self.prometheus:
            await self.prometheus.set_value(
                "security_blocked_ips_total", len(self.metrics["blocked_ips"])
            )

    async def record_attack_attempt(self, attack_type: str):
        """Record attack attempt"""
        async with self._lock:
            self.metrics["attack_attempts"][attack_type] += 1

        if self.prometheus:
            await self.prometheus.increment(
                "security_attack_attempts_total", labels={"attack_type": attack_type}
            )

    async def record_active_sessions(self, count: int):
        """Record active session count"""
        async with self._lock:
            self.metrics["active_sessions"] = count

        if self.prometheus:
            await self.prometheus.set_value("security_active_sessions", count)

    async def record_response_time(self, duration_seconds: float):
        """Record security check response time"""
        async with self._lock:
            self.metrics["response_times"].append(duration_seconds)

        if self.prometheus:
            await self.prometheus.set_value("security_response_time_seconds", duration_seconds)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get security statistics"""
        async with self._lock:
            response_times = list(self.metrics["response_times"])

            return {
                "total_login_attempts": sum(self.metrics["login_attempts"].values()),
                "total_login_failures": sum(self.metrics["login_failures"].values()),
                "total_authorization_failures": sum(
                    self.metrics["authorization_failures"].values()
                ),
                "blocked_ips_count": len(self.metrics["blocked_ips"]),
                "attack_attempts_by_type": dict(self.metrics["attack_attempts"]),
                "active_sessions": self.metrics["active_sessions"],
                "avg_response_time": (
                    sum(response_times) / len(response_times) if response_times else 0
                ),
            }

    async def export_prometheus_metrics(self) -> Optional[str]:
        """Export Prometheus metrics"""
        if self.prometheus:
            return await self.prometheus.export_metrics()
        return None


__all__ = [
    "SecurityMetrics",
    "PrometheusExporter",
    "MetricType",
    "Metric",
]
