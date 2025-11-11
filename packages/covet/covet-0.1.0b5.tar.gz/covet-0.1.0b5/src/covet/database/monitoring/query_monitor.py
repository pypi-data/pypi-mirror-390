"""
Query Performance Monitor

Tracks query execution times, identifies slow queries, and provides alerting
for performance issues. Integrates with logging and external monitoring systems.

Features:
- Automatic slow query detection
- Query statistics aggregation
- Configurable thresholds
- Multiple alert channels (webhook, email, logging)
- Query pattern analysis
- Historical performance tracking
"""

import asyncio
import hashlib
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from statistics import mean, median, stdev
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class QueryExecution:
    """Represents a single query execution."""

    sql: str
    duration_ms: float
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

    @property
    def query_hash(self) -> str:
        """Generate a hash for the query pattern (ignoring parameters)."""
        # Normalize query for pattern matching
        normalized = " ".join(self.sql.split())
        return hashlib.md5(normalized.encode(), usedforsecurity=False).hexdigest()


@dataclass
class QueryStats:
    """Aggregated statistics for a query pattern."""

    query_pattern: str
    query_hash: str
    execution_count: int = 0
    total_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    durations: List[float] = field(default_factory=list)
    error_count: int = 0
    last_executed: Optional[datetime] = None

    @property
    def avg_duration_ms(self) -> float:
        """Calculate average duration."""
        if self.execution_count == 0:
            return 0.0
        return self.total_duration_ms / self.execution_count

    @property
    def median_duration_ms(self) -> float:
        """Calculate median duration."""
        if not self.durations:
            return 0.0
        return median(self.durations)

    @property
    def std_deviation_ms(self) -> float:
        """Calculate standard deviation."""
        if len(self.durations) < 2:
            return 0.0
        return stdev(self.durations)

    @property
    def p95_duration_ms(self) -> float:
        """Calculate 95th percentile duration."""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * 0.95)
        return sorted_durations[min(index, len(sorted_durations) - 1)]

    @property
    def p99_duration_ms(self) -> float:
        """Calculate 99th percentile duration."""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * 0.99)
        return sorted_durations[min(index, len(sorted_durations) - 1)]

    @property
    def error_rate(self) -> float:
        """Calculate error rate as percentage."""
        if self.execution_count == 0:
            return 0.0
        return (self.error_count / self.execution_count) * 100

    def update(self, execution: QueryExecution) -> None:
        """Update statistics with new execution."""
        self.execution_count += 1
        self.total_duration_ms += execution.duration_ms
        self.min_duration_ms = min(self.min_duration_ms, execution.duration_ms)
        self.max_duration_ms = max(self.max_duration_ms, execution.duration_ms)
        self.last_executed = execution.timestamp

        # Keep recent durations (limit to 1000 for memory)
        self.durations.append(execution.duration_ms)
        if len(self.durations) > 1000:
            self.durations = self.durations[-1000:]

        if not execution.success:
            self.error_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            # Truncate for readability
            "query_pattern": self.query_pattern[:200],
            "query_hash": self.query_hash,
            "execution_count": self.execution_count,
            "avg_duration_ms": round(self.avg_duration_ms, 2),
            "median_duration_ms": round(self.median_duration_ms, 2),
            "min_duration_ms": round(self.min_duration_ms, 2),
            "max_duration_ms": round(self.max_duration_ms, 2),
            "p95_duration_ms": round(self.p95_duration_ms, 2),
            "p99_duration_ms": round(self.p99_duration_ms, 2),
            "std_deviation_ms": round(self.std_deviation_ms, 2),
            "error_count": self.error_count,
            "error_rate": round(self.error_rate, 2),
            "last_executed": (self.last_executed.isoformat() if self.last_executed else None),
        }


@dataclass
class SlowQueryAlert:
    """Alert for a slow query."""

    query: str
    duration_ms: float
    threshold_ms: float
    timestamp: datetime
    query_hash: str
    parameters: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "query": self.query[:500],  # Truncate long queries
            "duration_ms": round(self.duration_ms, 2),
            "threshold_ms": self.threshold_ms,
            "timestamp": self.timestamp.isoformat(),
            "query_hash": self.query_hash,
            "parameters": self.parameters,
            "severity": self._get_severity(),
        }

    def _get_severity(self) -> str:
        """Determine alert severity based on how much threshold was exceeded."""
        ratio = self.duration_ms / self.threshold_ms
        if ratio >= 10:
            return "critical"
        elif ratio >= 5:
            return "high"
        elif ratio >= 2:
            return "medium"
        else:
            return "low"


class QueryMonitor:
    """
    Monitor query performance and detect slow queries.

    Features:
    - Track all query executions
    - Detect slow queries based on configurable thresholds
    - Aggregate statistics per query pattern
    - Send alerts via multiple channels
    - Provide performance insights

    Usage:
        monitor = QueryMonitor(slow_query_threshold_ms=1000)

        # Track query
        await monitor.track_query(
            sql="SELECT * FROM users WHERE id = ?",
            duration_ms=1500,
            success=True,
            parameters={'id': 123}
        )

        # Get slow queries
        slow_queries = monitor.get_slow_queries(threshold_ms=500)

        # Get statistics
        stats = monitor.get_query_stats()
    """

    def __init__(
        self,
        slow_query_threshold_ms: float = 1000.0,
        enable_alerting: bool = True,
        enable_logging: bool = True,
        max_history_size: int = 10000,
        stats_retention_hours: int = 24,
    ):
        """
        Initialize query monitor.

        Args:
            slow_query_threshold_ms: Threshold in milliseconds for slow query detection
            enable_alerting: Enable alert generation
            enable_logging: Log slow queries automatically
            max_history_size: Maximum number of query executions to keep
            stats_retention_hours: How long to keep statistics
        """
        self.slow_query_threshold_ms = slow_query_threshold_ms
        self.enable_alerting = enable_alerting
        self.enable_logging = enable_logging
        self.max_history_size = max_history_size
        self.stats_retention_hours = stats_retention_hours

        # Storage
        self._query_history: List[QueryExecution] = []
        self._query_stats: Dict[str, QueryStats] = {}
        self._slow_queries: List[SlowQueryAlert] = []

        # Alert handlers
        self._alert_handlers: List[Callable[[SlowQueryAlert], None]] = []

        # Metrics
        self._total_queries = 0
        self._total_slow_queries = 0
        self._total_errors = 0

        # Pattern tracking
        self._known_patterns: Set[str] = set()

        # Cleanup task
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

        logger.info(f"QueryMonitor initialized with threshold: {slow_query_threshold_ms}ms")

    async def start(self) -> None:
        """Start the monitor and background tasks."""
        if self._running:
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("QueryMonitor started")

    async def stop(self) -> None:
        """Stop the monitor and cleanup."""
        self._running = False

        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        logger.info("QueryMonitor stopped")

    async def track_query(
        self,
        sql: str,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """
        Track a query execution.

        Args:
            sql: SQL query string
            duration_ms: Execution duration in milliseconds
            success: Whether query succeeded
            error: Error message if failed
            parameters: Query parameters
            stack_trace: Stack trace for debugging
        """
        # Create execution record
        execution = QueryExecution(
            sql=sql,
            duration_ms=duration_ms,
            timestamp=datetime.now(),
            success=success,
            error=error,
            parameters=parameters,
            stack_trace=stack_trace,
        )

        # Update metrics
        self._total_queries += 1
        if not success:
            self._total_errors += 1

        # Add to history
        self._query_history.append(execution)
        if len(self._query_history) > self.max_history_size:
            self._query_history = self._query_history[-self.max_history_size :]

        # Update statistics
        query_hash = execution.query_hash
        if query_hash not in self._query_stats:
            self._query_stats[query_hash] = QueryStats(
                query_pattern=sql,
                query_hash=query_hash,
            )
            self._known_patterns.add(query_hash)

        self._query_stats[query_hash].update(execution)

        # Check for slow query
        if duration_ms >= self.slow_query_threshold_ms:
            await self._handle_slow_query(execution)

    async def _handle_slow_query(self, execution: QueryExecution) -> None:
        """Handle a slow query detection."""
        self._total_slow_queries += 1

        # Create alert
        alert = SlowQueryAlert(
            query=execution.sql,
            duration_ms=execution.duration_ms,
            threshold_ms=self.slow_query_threshold_ms,
            timestamp=execution.timestamp,
            query_hash=execution.query_hash,
            parameters=execution.parameters,
            stack_trace=execution.stack_trace,
        )

        self._slow_queries.append(alert)

        # Log if enabled
        if self.enable_logging:
            logger.warning(
                f"Slow query detected: {execution.duration_ms:.2f}ms "
                f"(threshold: {self.slow_query_threshold_ms}ms) - "
                f"{execution.sql[:200]}"
            )

        # Send alerts if enabled
        if self.enable_alerting:
            await self._send_alerts(alert)

    async def _send_alerts(self, alert: SlowQueryAlert) -> None:
        """Send alerts to registered handlers."""
        for handler in self._alert_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(alert)
                else:
                    handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}", exc_info=True)

    def add_alert_handler(self, handler: Callable[[SlowQueryAlert], None]) -> None:
        """
        Add an alert handler.

        Args:
            handler: Callable that receives SlowQueryAlert
        """
        self._alert_handlers.append(handler)
        logger.info(f"Added alert handler: {handler.__name__}")

    def get_slow_queries(
        self,
        threshold_ms: Optional[float] = None,
        limit: int = 100,
    ) -> List[SlowQueryAlert]:
        """
        Get slow queries.

        Args:
            threshold_ms: Custom threshold (uses default if None)
            limit: Maximum number of results

        Returns:
            List of slow query alerts
        """
        threshold = threshold_ms or self.slow_query_threshold_ms

        # Filter by threshold
        queries = [alert for alert in self._slow_queries if alert.duration_ms >= threshold]

        # Sort by duration (slowest first)
        queries.sort(key=lambda x: x.duration_ms, reverse=True)

        return queries[:limit]

    def get_query_stats(
        self,
        order_by: str = "avg_duration",
        limit: int = 50,
    ) -> List[QueryStats]:
        """
        Get aggregated query statistics.

        Args:
            order_by: Sort field (avg_duration, execution_count, error_rate)
            limit: Maximum number of results

        Returns:
            List of query statistics
        """
        stats_list = list(self._query_stats.values())

        # Sort based on order_by
        if order_by == "avg_duration":
            stats_list.sort(key=lambda x: x.avg_duration_ms, reverse=True)
        elif order_by == "execution_count":
            stats_list.sort(key=lambda x: x.execution_count, reverse=True)
        elif order_by == "error_rate":
            stats_list.sort(key=lambda x: x.error_rate, reverse=True)
        elif order_by == "max_duration":
            stats_list.sort(key=lambda x: x.max_duration_ms, reverse=True)

        return stats_list[:limit]

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get overall monitoring metrics.

        Returns:
            Dictionary with metrics
        """
        return {
            "total_queries": self._total_queries,
            "total_slow_queries": self._total_slow_queries,
            "total_errors": self._total_errors,
            "slow_query_rate": (
                (self._total_slow_queries / self._total_queries * 100)
                if self._total_queries > 0
                else 0.0
            ),
            "error_rate": (
                (self._total_errors / self._total_queries * 100) if self._total_queries > 0 else 0.0
            ),
            "unique_query_patterns": len(self._known_patterns),
            "threshold_ms": self.slow_query_threshold_ms,
            "history_size": len(self._query_history),
        }

    def get_top_slow_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top slowest query patterns.

        Args:
            limit: Number of queries to return

        Returns:
            List of query statistics dictionaries
        """
        stats = self.get_query_stats(order_by="avg_duration", limit=limit)
        return [s.to_dict() for s in stats]

    def get_most_frequent_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most frequently executed queries.

        Args:
            limit: Number of queries to return

        Returns:
            List of query statistics dictionaries
        """
        stats = self.get_query_stats(order_by="execution_count", limit=limit)
        return [s.to_dict() for s in stats]

    def get_error_prone_queries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get queries with highest error rates.

        Args:
            limit: Number of queries to return

        Returns:
            List of query statistics dictionaries
        """
        stats = self.get_query_stats(order_by="error_rate", limit=limit)
        return [s.to_dict() for s in stats if s.error_count > 0]

    def clear_history(self) -> None:
        """Clear query history and statistics."""
        self._query_history.clear()
        self._query_stats.clear()
        self._slow_queries.clear()
        self._known_patterns.clear()
        self._total_queries = 0
        self._total_slow_queries = 0
        self._total_errors = 0
        logger.info("Query history cleared")

    async def _cleanup_loop(self) -> None:
        """Background task to cleanup old data."""
        while self._running:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_data()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}", exc_info=True)

    async def _cleanup_old_data(self) -> None:
        """Remove old query data based on retention policy."""
        cutoff_time = datetime.now() - timedelta(hours=self.stats_retention_hours)

        # Clean history
        self._query_history = [
            execution for execution in self._query_history if execution.timestamp >= cutoff_time
        ]

        # Clean slow queries
        self._slow_queries = [
            alert for alert in self._slow_queries if alert.timestamp >= cutoff_time
        ]

        logger.debug(f"Cleaned up old query data (retention: {self.stats_retention_hours}h)")

    def generate_report(self) -> str:
        """
        Generate a text-based performance report.

        Returns:
            Formatted report string
        """
        metrics = self.get_metrics()
        top_slow = self.get_top_slow_queries(limit=5)
        top_frequent = self.get_most_frequent_queries(limit=5)
        error_prone = self.get_error_prone_queries(limit=5)

        report_lines = [
            "=" * 80,
            "QUERY PERFORMANCE REPORT",
            "=" * 80,
            "",
            "OVERALL METRICS:",
            f"  Total Queries: {metrics['total_queries']:,}",
            f"  Slow Queries: {metrics['total_slow_queries']:,} ({metrics['slow_query_rate']:.2f}%)",
            f"  Errors: {metrics['total_errors']:,} ({metrics['error_rate']:.2f}%)",
            f"  Unique Patterns: {metrics['unique_query_patterns']}",
            f"  Threshold: {metrics['threshold_ms']:.0f}ms",
            "",
            "TOP 5 SLOWEST QUERIES (by avg duration):",
        ]

        for i, query in enumerate(top_slow, 1):
            report_lines.extend(
                [
                    f"  {i}. {query['query_pattern'][:100]}...",
                    f"     Avg: {query['avg_duration_ms']:.2f}ms, "
                    f"P95: {query['p95_duration_ms']:.2f}ms, "
                    f"Executions: {query['execution_count']}",
                ]
            )

        report_lines.extend(
            [
                "",
                "TOP 5 MOST FREQUENT QUERIES:",
            ]
        )

        for i, query in enumerate(top_frequent, 1):
            report_lines.extend(
                [
                    f"  {i}. {query['query_pattern'][:100]}...",
                    f"     Executions: {query['execution_count']}, "
                    f"Avg: {query['avg_duration_ms']:.2f}ms",
                ]
            )

        if error_prone:
            report_lines.extend(
                [
                    "",
                    "ERROR-PRONE QUERIES:",
                ]
            )

            for i, query in enumerate(error_prone, 1):
                report_lines.extend(
                    [
                        f"  {i}. {query['query_pattern'][:100]}...",
                        f"     Errors: {query['error_count']}/{query['execution_count']} "
                        f"({query['error_rate']:.2f}%)",
                    ]
                )

        report_lines.extend(
            [
                "",
                "=" * 80,
            ]
        )

        return "\n".join(report_lines)

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"QueryMonitor(queries={self._total_queries}, "
            f"slow={self._total_slow_queries}, "
            f"threshold={self.slow_query_threshold_ms}ms)"
        )


# Global query monitor instance
_query_monitor: Optional[QueryMonitor] = None


def get_query_monitor() -> QueryMonitor:
    """Get the global query monitor instance."""
    global _query_monitor

    if _query_monitor is None:
        _query_monitor = QueryMonitor()

    return _query_monitor


async def initialize_query_monitor(
    slow_query_threshold_ms: float = 1000.0, **kwargs
) -> QueryMonitor:
    """Initialize the global query monitor."""
    global _query_monitor

    if _query_monitor is not None:
        logger.warning("Query monitor already initialized")
        return _query_monitor

    _query_monitor = QueryMonitor(slow_query_threshold_ms=slow_query_threshold_ms, **kwargs)
    await _query_monitor.start()

    return _query_monitor
