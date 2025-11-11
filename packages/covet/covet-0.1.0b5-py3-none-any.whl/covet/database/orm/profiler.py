"""
Query Profiler

Advanced profiling system for tracking query performance, detecting N+1 queries,
monitoring connection pools, and identifying performance regressions.

Features:
- Query execution time tracking
- Slow query detection and logging
- N+1 query pattern detection
- Memory usage monitoring
- Connection pool statistics
- Performance regression detection
- Query execution statistics
- Real-time alerting

Example:
    from covet.database.orm.profiler import QueryProfiler, ProfilerConfig

    config = ProfilerConfig(
        slow_query_threshold=100,  # 100ms
        enable_n_plus_one_detection=True,
    )

    profiler = QueryProfiler(config)

    # Profile queries
    with profiler.profile_query("get_user"):
        user = await User.objects.get(id=1)

    # Get statistics
    stats = profiler.get_statistics()
    print(f"Slow queries: {stats['slow_query_count']}")
"""

import asyncio
import logging
import time
import traceback
from collections import defaultdict, deque
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Deque, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Type of query operation."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    OTHER = "other"


class AlertLevel(Enum):
    """Alert severity level."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class QueryProfile:
    """Profile data for a single query execution."""

    query_id: str
    sql: str
    query_type: QueryType
    started_at: datetime
    duration_ms: float
    success: bool
    error: Optional[str] = None
    stack_trace: Optional[str] = None
    rows_affected: int = 0
    connection_id: Optional[str] = None
    memory_delta_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfilerConfig:
    """Profiler configuration."""

    slow_query_threshold: float = 100.0  # milliseconds
    enable_slow_query_logging: bool = True
    enable_n_plus_one_detection: bool = True
    enable_memory_tracking: bool = True
    enable_connection_tracking: bool = True
    max_history_size: int = 10000
    alert_thresholds: Dict[str, float] = field(
        default_factory=lambda: {
            "slow_query_rate": 0.1,  # 10% slow queries
            "error_rate": 0.05,  # 5% error rate
            "n_plus_one_rate": 0.02,  # 2% N+1 queries
        }
    )


@dataclass
class QueryStatistics:
    """Aggregated statistics for queries."""

    total_queries: int = 0
    slow_queries: int = 0
    failed_queries: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    min_duration_ms: float = float("inf")
    max_duration_ms: float = 0.0
    n_plus_one_detected: int = 0
    queries_by_type: Dict[QueryType, int] = field(default_factory=dict)


class QueryProfiler:
    """
    Advanced query profiler for performance monitoring.

    Tracks all query executions, detects performance issues, and provides
    detailed statistics and alerting.
    """

    def __init__(self, config: Optional[ProfilerConfig] = None):
        """
        Initialize query profiler.

        Args:
            config: Profiler configuration
        """
        self.config = config or ProfilerConfig()

        # Query history
        self.query_history: Deque[QueryProfile] = deque(maxlen=self.config.max_history_size)

        # Statistics
        self.stats = QueryStatistics()

        # N+1 detection state
        self.recent_queries: Deque[Tuple[str, datetime]] = deque(maxlen=100)
        self.potential_n_plus_one: List[str] = []

        # Connection pool tracking
        self.connection_pool_stats: Dict[str, Any] = {}

        # Alerts
        self.alerts: Deque[Tuple[AlertLevel, str, datetime]] = deque(maxlen=1000)

        # Performance baselines
        self.baselines: Dict[str, float] = {}  # query_pattern -> baseline_ms

        # Active profiles
        self._active_profiles: Dict[str, float] = {}  # profile_id -> start_time

    @contextmanager
    def profile_query(
        self,
        query_id: str,
        sql: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Context manager for profiling query execution (sync version).

        Args:
            query_id: Unique identifier for this query
            sql: SQL statement (optional)
            metadata: Additional metadata

        Example:
            with profiler.profile_query("get_user", sql="SELECT * FROM users WHERE id = $1"):
                # Execute query
                pass
        """
        profile_id = f"{query_id}:{time.time()}"
        start_time = time.time()
        start_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0.0

        error = None
        success = True

        try:
            yield
        except Exception as e:
            error = str(e)
            success = False
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            end_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0.0
            memory_delta = end_memory - start_memory

            # Create profile
            profile = QueryProfile(
                query_id=query_id,
                sql=sql or "",
                query_type=self._detect_query_type(sql or ""),
                started_at=datetime.fromtimestamp(start_time),
                duration_ms=duration_ms,
                success=success,
                error=error,
                stack_trace=traceback.format_stack() if error else None,
                memory_delta_mb=memory_delta,
                metadata=metadata or {},
            )

            # Record profile
            self._record_profile(profile)

    @asynccontextmanager
    async def profile_query_async(
        self,
        query_id: str,
        sql: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Async context manager for profiling query execution.

        Args:
            query_id: Unique identifier for this query
            sql: SQL statement (optional)
            metadata: Additional metadata

        Example:
            async with profiler.profile_query_async("get_user", sql="SELECT ..."):
                user = await User.objects.get(id=1)
        """
        profile_id = f"{query_id}:{time.time()}"
        start_time = time.time()
        start_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0.0

        error = None
        success = True

        try:
            yield
        except Exception as e:
            error = str(e)
            success = False
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            end_memory = self._get_memory_usage() if self.config.enable_memory_tracking else 0.0
            memory_delta = end_memory - start_memory

            # Create profile
            profile = QueryProfile(
                query_id=query_id,
                sql=sql or "",
                query_type=self._detect_query_type(sql or ""),
                started_at=datetime.fromtimestamp(start_time),
                duration_ms=duration_ms,
                success=success,
                error=error,
                stack_trace=traceback.format_stack() if error else None,
                memory_delta_mb=memory_delta,
                metadata=metadata or {},
            )

            # Record profile
            self._record_profile(profile)

    def get_slow_queries(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[QueryProfile]:
        """
        Get slow queries.

        Args:
            limit: Maximum number of queries to return
            since: Only return queries after this time

        Returns:
            List of slow query profiles
        """
        slow_queries = []

        for profile in self.query_history:
            if profile.duration_ms >= self.config.slow_query_threshold:
                if since and profile.started_at < since:
                    continue
                slow_queries.append(profile)

        # Sort by duration (slowest first)
        slow_queries.sort(key=lambda p: p.duration_ms, reverse=True)

        if limit:
            slow_queries = slow_queries[:limit]

        return slow_queries

    def get_failed_queries(
        self,
        limit: Optional[int] = None,
        since: Optional[datetime] = None,
    ) -> List[QueryProfile]:
        """
        Get failed queries.

        Args:
            limit: Maximum number of queries to return
            since: Only return queries after this time

        Returns:
            List of failed query profiles
        """
        failed_queries = []

        for profile in self.query_history:
            if not profile.success:
                if since and profile.started_at < since:
                    continue
                failed_queries.append(profile)

        # Sort by time (most recent first)
        failed_queries.sort(key=lambda p: p.started_at, reverse=True)

        if limit:
            failed_queries = failed_queries[:limit]

        return failed_queries

    def detect_n_plus_one(self) -> List[Dict[str, Any]]:
        """
        Detect N+1 query patterns in recent queries.

        Returns:
            List of detected N+1 patterns with details
        """
        if not self.config.enable_n_plus_one_detection:
            return []

        patterns = []
        query_groups = defaultdict(list)

        # Group similar queries by normalized SQL
        for profile in list(self.query_history)[-100:]:  # Check last 100 queries
            normalized = self._normalize_sql(profile.sql)
            query_groups[normalized].append(profile)

        # Look for repeated queries in short time windows
        for normalized_sql, profiles in query_groups.items():
            if len(profiles) < 3:  # Need at least 3 repetitions
                continue

            # Check if queries happened in quick succession
            time_window = timedelta(seconds=1)
            clustered = []

            for i, profile in enumerate(profiles[:-1]):
                next_profile = profiles[i + 1]
                time_diff = next_profile.started_at - profile.started_at

                if time_diff < time_window:
                    if not clustered or clustered[-1] != profile:
                        clustered.append(profile)
                    clustered.append(next_profile)

            if len(clustered) >= 3:
                patterns.append(
                    {
                        "query": normalized_sql,
                        "count": len(clustered),
                        "avg_duration_ms": sum(p.duration_ms for p in clustered) / len(clustered),
                        "total_duration_ms": sum(p.duration_ms for p in clustered),
                        "first_occurrence": clustered[0].started_at,
                        "last_occurrence": clustered[-1].started_at,
                    }
                )

        return patterns

    def get_statistics(
        self,
        since: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get profiling statistics.

        Args:
            since: Calculate statistics for queries after this time

        Returns:
            Dictionary of statistics
        """
        if since:
            profiles = [p for p in self.query_history if p.started_at >= since]
        else:
            profiles = list(self.query_history)

        if not profiles:
            return {
                "total_queries": 0,
                "slow_queries": 0,
                "failed_queries": 0,
                "avg_duration_ms": 0.0,
                "queries_by_type": {},
            }

        total_queries = len(profiles)
        slow_queries = sum(1 for p in profiles if p.duration_ms >= self.config.slow_query_threshold)
        failed_queries = sum(1 for p in profiles if not p.success)

        durations = [p.duration_ms for p in profiles]
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        queries_by_type = defaultdict(int)
        for profile in profiles:
            queries_by_type[profile.query_type.value] += 1

        n_plus_one_patterns = self.detect_n_plus_one()

        return {
            "total_queries": total_queries,
            "slow_queries": slow_queries,
            "failed_queries": failed_queries,
            "slow_query_rate": slow_queries / total_queries if total_queries > 0 else 0,
            "error_rate": failed_queries / total_queries if total_queries > 0 else 0,
            "avg_duration_ms": avg_duration,
            "min_duration_ms": min_duration,
            "max_duration_ms": max_duration,
            "queries_by_type": dict(queries_by_type),
            "n_plus_one_patterns": len(n_plus_one_patterns),
            "n_plus_one_details": n_plus_one_patterns,
        }

    def set_baseline(self, query_pattern: str, baseline_ms: float) -> None:
        """
        Set performance baseline for a query pattern.

        Args:
            query_pattern: Normalized query pattern
            baseline_ms: Expected duration in milliseconds
        """
        self.baselines[query_pattern] = baseline_ms

    def detect_regressions(
        self,
        threshold_factor: float = 1.5,
    ) -> List[Dict[str, Any]]:
        """
        Detect performance regressions compared to baselines.

        Args:
            threshold_factor: Consider it a regression if query is this many times slower

        Returns:
            List of detected regressions
        """
        regressions = []

        # Group queries by normalized SQL
        query_groups = defaultdict(list)
        for profile in self.query_history:
            normalized = self._normalize_sql(profile.sql)
            query_groups[normalized].append(profile)

        # Check against baselines
        for normalized_sql, profiles in query_groups.items():
            if normalized_sql not in self.baselines:
                continue

            baseline = self.baselines[normalized_sql]
            recent_profiles = profiles[-10:]  # Check last 10 executions

            avg_duration = sum(p.duration_ms for p in recent_profiles) / len(recent_profiles)

            if avg_duration > baseline * threshold_factor:
                regressions.append(
                    {
                        "query": normalized_sql,
                        "baseline_ms": baseline,
                        "current_avg_ms": avg_duration,
                        "slowdown_factor": avg_duration / baseline,
                        "sample_count": len(recent_profiles),
                    }
                )

        return regressions

    def add_alert(
        self,
        level: AlertLevel,
        message: str,
    ) -> None:
        """
        Add an alert.

        Args:
            level: Alert severity level
            message: Alert message
        """
        self.alerts.append((level, message, datetime.now()))
        logger.log(self._alert_level_to_log_level(level), f"[PROFILER ALERT] {message}")

    def get_alerts(
        self,
        level: Optional[AlertLevel] = None,
        since: Optional[datetime] = None,
    ) -> List[Tuple[AlertLevel, str, datetime]]:
        """
        Get alerts.

        Args:
            level: Filter by alert level
            since: Only return alerts after this time

        Returns:
            List of (level, message, timestamp) tuples
        """
        alerts = list(self.alerts)

        if level:
            alerts = [(l, m, t) for l, m, t in alerts if l == level]

        if since:
            alerts = [(l, m, t) for l, m, t in alerts if t >= since]

        return alerts

    def clear_history(self) -> None:
        """Clear query history and statistics."""
        self.query_history.clear()
        self.stats = QueryStatistics()
        self.potential_n_plus_one.clear()
        logger.info("Query profiler history cleared")

    # Private methods

    def _record_profile(self, profile: QueryProfile) -> None:
        """Record a query profile."""
        # Add to history
        self.query_history.append(profile)

        # Update statistics
        self.stats.total_queries += 1

        if profile.duration_ms >= self.config.slow_query_threshold:
            self.stats.slow_queries += 1

            if self.config.enable_slow_query_logging:
                logger.warning(
                    f"Slow query detected ({profile.duration_ms:.2f}ms): {profile.sql[:100]}"
                )

        if not profile.success:
            self.stats.failed_queries += 1
            logger.error(f"Query failed: {profile.sql[:100]} - Error: {profile.error}")

        self.stats.total_duration_ms += profile.duration_ms

        if self.stats.total_queries > 0:
            self.stats.avg_duration_ms = self.stats.total_duration_ms / self.stats.total_queries

        self.stats.min_duration_ms = min(self.stats.min_duration_ms, profile.duration_ms)
        self.stats.max_duration_ms = max(self.stats.max_duration_ms, profile.duration_ms)

        # Update query type stats
        if profile.query_type not in self.stats.queries_by_type:
            self.stats.queries_by_type[profile.query_type] = 0
        self.stats.queries_by_type[profile.query_type] += 1

        # Check alert thresholds
        self._check_alert_thresholds()

    def _detect_query_type(self, sql: str) -> QueryType:
        """Detect query type from SQL."""
        sql_upper = sql.strip().upper()

        if sql_upper.startswith("SELECT"):
            return QueryType.SELECT
        elif sql_upper.startswith("INSERT"):
            return QueryType.INSERT
        elif sql_upper.startswith("UPDATE"):
            return QueryType.UPDATE
        elif sql_upper.startswith("DELETE"):
            return QueryType.DELETE
        else:
            return QueryType.OTHER

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for pattern matching."""
        import re

        # Remove literals
        normalized = re.sub(r"'[^']*'", "'?'", sql)
        normalized = re.sub(r"\$\d+", "$?", normalized)
        normalized = re.sub(r"\?", "?", normalized)
        normalized = re.sub(r"\b\d+\b", "?", normalized)

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized.strip())

        return normalized

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            import os

            import psutil

            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            return 0.0
        except Exception as e:
            logger.debug(f"Failed to get memory usage: {e}")
            return 0.0

    def _check_alert_thresholds(self) -> None:
        """Check if any alert thresholds have been exceeded."""
        if self.stats.total_queries < 100:
            return  # Need enough data

        # Check slow query rate
        slow_rate = self.stats.slow_queries / self.stats.total_queries
        threshold = self.config.alert_thresholds.get("slow_query_rate", 0.1)

        if slow_rate > threshold:
            self.add_alert(
                AlertLevel.WARNING,
                f"High slow query rate: {slow_rate*100:.1f}% (threshold: {threshold*100:.1f}%)",
            )

        # Check error rate
        error_rate = self.stats.failed_queries / self.stats.total_queries
        threshold = self.config.alert_thresholds.get("error_rate", 0.05)

        if error_rate > threshold:
            self.add_alert(
                AlertLevel.ERROR,
                f"High error rate: {error_rate*100:.1f}% (threshold: {threshold*100:.1f}%)",
            )

    def _alert_level_to_log_level(self, level: AlertLevel) -> int:
        """Convert alert level to logging level."""
        mapping = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL,
        }
        return mapping.get(level, logging.INFO)


__all__ = [
    "QueryProfiler",
    "ProfilerConfig",
    "QueryProfile",
    "QueryStatistics",
    "QueryType",
    "AlertLevel",
]
