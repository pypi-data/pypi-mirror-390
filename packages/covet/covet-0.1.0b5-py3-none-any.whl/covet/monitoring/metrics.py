"""
Prometheus Metrics for CovetPy

This module implements 50+ production-ready metrics for comprehensive observability.
"""

import os
import time
from typing import Callable, Optional

import psutil
from prometheus_client import (
    CONTENT_TYPE_LATEST,
)
from prometheus_client import CollectorRegistry
from prometheus_client import CollectorRegistry as BaseRegistry
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    Summary,
    generate_latest,
    multiprocess,
)

# ==============================================================================
# Metrics Registry Setup (supports multi-process mode)
# ==============================================================================


def get_registry() -> BaseRegistry:
    """Get Prometheus registry (multi-process aware)."""
    prom_dir = os.environ.get("PROMETHEUS_MULTIPROC_DIR")
    if prom_dir:
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)
        return registry
    return BaseRegistry()


registry = get_registry()

# ==============================================================================
# HTTP Metrics (13 metrics)
# ==============================================================================

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

http_request_size_bytes = Summary(
    "http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint"],
    registry=registry,
)

http_response_size_bytes = Summary(
    "http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint"],
    registry=registry,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"],
    registry=registry,
)

http_exceptions_total = Counter(
    "http_exceptions_total",
    "Total HTTP exceptions",
    ["method", "endpoint", "exception_type"],
    registry=registry,
)

http_4xx_responses = Counter(
    "http_4xx_responses",
    "Total 4xx HTTP responses",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_5xx_responses = Counter(
    "http_5xx_responses",
    "Total 5xx HTTP responses",
    ["method", "endpoint", "status"],
    registry=registry,
)

http_request_duration_summary = Summary(
    "http_request_duration_summary",
    "Summary of HTTP request durations",
    ["method", "endpoint"],
    registry=registry,
)

websocket_connections_total = Gauge(
    "websocket_connections_total",
    "Current number of WebSocket connections",
    registry=registry,
)

websocket_messages_sent = Counter(
    "websocket_messages_sent",
    "Total WebSocket messages sent",
    ["endpoint"],
    registry=registry,
)

websocket_messages_received = Counter(
    "websocket_messages_received",
    "Total WebSocket messages received",
    ["endpoint"],
    registry=registry,
)

http_requests_by_user_agent = Counter(
    "http_requests_by_user_agent",
    "HTTP requests grouped by user agent",
    ["user_agent_type"],
    registry=registry,
)

# ==============================================================================
# Database Metrics (15 metrics)
# ==============================================================================

db_queries_total = Counter(
    "db_queries_total",
    "Total database queries",
    ["operation", "table", "status"],
    registry=registry,
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query latency",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    registry=registry,
)

db_connections_active = Gauge(
    "db_connections_active", "Number of active database connections", registry=registry
)

db_connections_idle = Gauge(
    "db_connections_idle", "Number of idle database connections", registry=registry
)

db_connection_pool_size = Gauge(
    "db_connection_pool_size", "Total database connection pool size", registry=registry
)

db_connection_pool_overflow = Gauge(
    "db_connection_pool_overflow",
    "Database connection pool overflow count",
    registry=registry,
)

db_transaction_duration_seconds = Histogram(
    "db_transaction_duration_seconds",
    "Database transaction duration",
    ["status"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=registry,
)

db_transactions_total = Counter(
    "db_transactions_total",
    "Total database transactions",
    ["status"],
    registry=registry,
)

db_deadlocks_total = Counter("db_deadlocks_total", "Total database deadlocks", registry=registry)

db_rows_affected = Counter(
    "db_rows_affected",
    "Total rows affected by queries",
    ["operation"],
    registry=registry,
)

db_cache_hits = Counter("db_cache_hits", "Database cache hits", registry=registry)

db_cache_misses = Counter("db_cache_misses", "Database cache misses", registry=registry)

db_connection_errors = Counter(
    "db_connection_errors",
    "Database connection errors",
    ["error_type"],
    registry=registry,
)

db_query_errors = Counter(
    "db_query_errors",
    "Database query errors",
    ["error_type", "operation"],
    registry=registry,
)

db_slow_queries_total = Counter(
    "db_slow_queries_total",
    "Total slow database queries (>1s)",
    ["operation", "table"],
    registry=registry,
)

# ==============================================================================
# Cache Metrics (10 metrics)
# ==============================================================================

cache_hits_total = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type", "key_prefix"],
    registry=registry,
)

cache_misses_total = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type", "key_prefix"],
    registry=registry,
)

cache_evictions_total = Counter(
    "cache_evictions_total", "Total cache evictions", ["cache_type"], registry=registry
)

cache_size_bytes = Gauge(
    "cache_size_bytes", "Current cache size in bytes", ["cache_type"], registry=registry
)

cache_keys_total = Gauge(
    "cache_keys_total",
    "Total number of keys in cache",
    ["cache_type"],
    registry=registry,
)

cache_operation_duration_seconds = Histogram(
    "cache_operation_duration_seconds",
    "Cache operation duration",
    ["operation", "cache_type"],
    buckets=(0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1),
    registry=registry,
)

cache_connection_errors = Counter(
    "cache_connection_errors",
    "Cache connection errors",
    ["cache_type", "error_type"],
    registry=registry,
)

cache_memory_usage_bytes = Gauge(
    "cache_memory_usage_bytes",
    "Cache memory usage in bytes",
    ["cache_type"],
    registry=registry,
)

cache_ttl_seconds = Histogram(
    "cache_ttl_seconds",
    "Cache entry TTL in seconds",
    ["cache_type"],
    buckets=(60, 300, 600, 1800, 3600, 7200, 14400, 28800, 86400),
    registry=registry,
)

cache_hit_ratio = Gauge(
    "cache_hit_ratio",
    "Cache hit ratio (hits / (hits + misses))",
    ["cache_type"],
    registry=registry,
)

# ==============================================================================
# System Metrics (12 metrics)
# ==============================================================================

system_cpu_usage_percent = Gauge(
    "system_cpu_usage_percent", "System CPU usage percentage", registry=registry
)

system_memory_usage_bytes = Gauge(
    "system_memory_usage_bytes",
    "System memory usage in bytes",
    ["type"],
    registry=registry,
)

system_disk_usage_bytes = Gauge(
    "system_disk_usage_bytes",
    "System disk usage in bytes",
    ["mountpoint", "type"],
    registry=registry,
)

system_network_bytes_sent = Counter(
    "system_network_bytes_sent",
    "System network bytes sent",
    ["interface"],
    registry=registry,
)

system_network_bytes_received = Counter(
    "system_network_bytes_received",
    "System network bytes received",
    ["interface"],
    registry=registry,
)

process_cpu_usage_percent = Gauge(
    "process_cpu_usage_percent", "Process CPU usage percentage", registry=registry
)

process_memory_usage_bytes = Gauge(
    "process_memory_usage_bytes",
    "Process memory usage in bytes",
    ["type"],
    registry=registry,
)

process_open_file_descriptors = Gauge(
    "process_open_file_descriptors",
    "Number of open file descriptors",
    registry=registry,
)

process_threads_total = Gauge("process_threads_total", "Total number of threads", registry=registry)

process_start_time_seconds = Gauge(
    "process_start_time_seconds",
    "Process start time in unix seconds",
    registry=registry,
)

system_load_average = Gauge(
    "system_load_average", "System load average", ["period"], registry=registry
)

garbage_collection_duration_seconds = Histogram(
    "garbage_collection_duration_seconds",
    "Garbage collection duration",
    ["generation"],
    registry=registry,
)

# ==============================================================================
# Application Metrics (10 metrics)
# ==============================================================================

app_info = Info("app", "Application information", registry=registry)

app_uptime_seconds = Gauge("app_uptime_seconds", "Application uptime in seconds", registry=registry)

app_requests_queue_depth = Gauge(
    "app_requests_queue_depth", "Number of requests waiting in queue", registry=registry
)

app_workers_total = Gauge(
    "app_workers_total", "Total number of workers", ["state"], registry=registry
)

app_background_tasks_total = Gauge(
    "app_background_tasks_total",
    "Number of background tasks running",
    ["task_type"],
    registry=registry,
)

app_background_task_duration_seconds = Histogram(
    "app_background_task_duration_seconds",
    "Background task duration",
    ["task_type", "status"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
    registry=registry,
)

app_rate_limit_exceeded = Counter(
    "app_rate_limit_exceeded",
    "Number of rate limit violations",
    ["endpoint", "client_id"],
    registry=registry,
)

app_auth_attempts_total = Counter(
    "app_auth_attempts_total",
    "Total authentication attempts",
    ["method", "status"],
    registry=registry,
)

app_auth_failures_total = Counter(
    "app_auth_failures_total",
    "Total authentication failures",
    ["method", "reason"],
    registry=registry,
)

app_version_info = Info("app_version", "Application version information", registry=registry)

# ==============================================================================
# Metrics Collector Class
# ==============================================================================


class MetricsCollector:
    """Centralized metrics collection and management."""

    def __init__(self):
        self.start_time = time.time()
        self._process = psutil.Process()

        # Set application info
        app_info.info(
            {
                "name": "covetpy",
                "environment": os.getenv("COVET_ENV", "development"),
            }
        )

        app_version_info.info(
            {
                "version": "1.0.0",
                "python_version": os.sys.version.split()[0],
            }
        )

        process_start_time_seconds.set(self.start_time)

    def update_system_metrics(self):
        """Update all system-level metrics."""
        try:
            # CPU metrics
            system_cpu_usage_percent.set(psutil.cpu_percent(interval=0.1))
            process_cpu_usage_percent.set(self._process.cpu_percent())

            # Memory metrics
            mem = psutil.virtual_memory()
            system_memory_usage_bytes.labels(type="used").set(mem.used)
            system_memory_usage_bytes.labels(type="available").set(mem.available)
            system_memory_usage_bytes.labels(type="total").set(mem.total)

            proc_mem = self._process.memory_info()
            process_memory_usage_bytes.labels(type="rss").set(proc_mem.rss)
            process_memory_usage_bytes.labels(type="vms").set(proc_mem.vms)

            # Disk metrics
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    system_disk_usage_bytes.labels(
                        mountpoint=partition.mountpoint, type="used"
                    ).set(usage.used)
                    system_disk_usage_bytes.labels(
                        mountpoint=partition.mountpoint, type="total"
                    ).set(usage.total)
                except (PermissionError, OSError):
                    pass

            # Network metrics
            net_io = psutil.net_io_counters(pernic=True)
            for interface, counters in net_io.items():
                system_network_bytes_sent.labels(interface=interface).inc(0)
                system_network_bytes_received.labels(interface=interface).inc(0)

            # Process metrics
            try:
                process_open_file_descriptors.set(self._process.num_fds())
            except AttributeError:
                # num_fds() not available on Windows
                pass

            process_threads_total.set(self._process.num_threads())

            # Load average
            if hasattr(os, "getloadavg"):
                load1, load5, load15 = os.getloadavg()
                system_load_average.labels(period="1m").set(load1)
                system_load_average.labels(period="5m").set(load5)
                system_load_average.labels(period="15m").set(load15)

            # Uptime
            app_uptime_seconds.set(time.time() - self.start_time)

        except Exception as e:
            print(f"Error updating system metrics: {e}")

    def export_metrics(self) -> bytes:
        """Export metrics in Prometheus format."""
        self.update_system_metrics()
        return generate_latest(registry)


# Global metrics collector instance
metrics_collector = MetricsCollector()

# ==============================================================================
# Middleware for Automatic Metrics Collection
# ==============================================================================


async def metrics_middleware(app, handler):
    """ASGI middleware that automatically collects HTTP metrics."""

    async def middleware(scope, receive, send):
        if scope["type"] != "http":
            return await handler(scope, receive, send)

        method = scope["method"]
        path = scope["path"]

        # Skip metrics endpoint itself
        if path == "/metrics":
            return await handler(scope, receive, send)

        start_time = time.time()
        http_requests_in_progress.labels(method=method, endpoint=path).inc()

        status_code = 200
        response_size = 0

        async def send_wrapper(message):
            nonlocal status_code, response_size
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body":
                response_size += len(message.get("body", b""))
            await send(message)

        try:
            await handler(scope, receive, send_wrapper)
        except Exception as exc:
            http_exceptions_total.labels(
                method=method, endpoint=path, exception_type=type(exc).__name__
            ).inc()
            raise
        finally:
            duration = time.time() - start_time

            # Record metrics
            http_requests_total.labels(method=method, endpoint=path, status=status_code).inc()

            http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration)

            http_request_duration_summary.labels(method=method, endpoint=path).observe(duration)

            http_response_size_bytes.labels(method=method, endpoint=path).observe(response_size)

            http_requests_in_progress.labels(method=method, endpoint=path).dec()

            # Track 4xx and 5xx responses
            if 400 <= status_code < 500:
                http_4xx_responses.labels(method=method, endpoint=path, status=status_code).inc()
            elif 500 <= status_code < 600:
                http_5xx_responses.labels(method=method, endpoint=path, status=status_code).inc()

    return middleware


__all__ = [
    "MetricsCollector",
    "metrics_collector",
    "metrics_middleware",
    "registry",
]
