"""
CovetPy Monitoring Module

Comprehensive monitoring and observability for production deployments:
- Prometheus metrics (50+ metrics)
- Health check endpoints
- Structured logging
- Distributed tracing with OpenTelemetry
"""

from .health import HealthCheck, health_check_endpoints
from .logging import configure_structured_logging, get_logger
from .metrics import MetricsCollector, metrics_middleware
from .tracing import configure_tracing, trace_middleware

__all__ = [
    "HealthChecker",
    "MetricsCollector",
    "metrics_middleware",
    "HealthCheck",
    "health_check_endpoints",
    "configure_structured_logging",
    "get_logger",
    "configure_tracing",
    "trace_middleware",
]


class HealthChecker:
    """Health check system for monitoring application health."""
    
    def __init__(self):
        self.checks = {}
        self.status = "healthy"
    
    def register_check(self, name: str, check_fn):
        """Register a health check function."""
        self.checks[name] = check_fn
    
    async def run_checks(self):
        """Run all registered health checks."""
        results = {}
        for name, check_fn in self.checks.items():
            try:
                result = await check_fn() if callable(check_fn) else check_fn
                results[name] = {"status": "pass", "output": result}
            except Exception as e:
                results[name] = {"status": "fail", "output": str(e)}
                self.status = "unhealthy"
        return results
    
    async def check_health(self):
        """Get current health status."""
        return {"status": self.status, "checks": await self.run_checks()}



class PerformanceMonitor:
    """Monitor performance metrics."""
    def __init__(self):
        self.metrics = {}
