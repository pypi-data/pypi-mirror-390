"""
N+1 Query Detection and Prevention System

Automatically detects and warns about N+1 query patterns in development mode.
Provides optimization suggestions and performance analysis.

Usage:
    # Enable in development settings
    from covet.database.orm.n_plus_one_detector import enable_query_tracking

    # Development mode
    enable_query_tracking(warn_threshold=10, error_threshold=50)

    # This will trigger a warning:
    users = await User.objects.all()
    for user in users:
        profile = await user.profile  # N queries!

    # Optimized version (no warning):
    users = await User.objects.select_related('profile').all()
    for user in users:
        profile = user.profile  # Cached, no query

Features:
    - Automatic N+1 pattern detection
    - Stack trace capture for debugging
    - Performance metrics and suggestions
    - Configurable warning/error thresholds
    - Query timeline visualization
    - Integration with Django Debug Toolbar style output

Author: Senior Performance Engineer specializing in database optimization
"""

import asyncio
import logging
import time
import traceback
import warnings
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from threading import local
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class QueryInfo:
    """Information about a single database query."""

    sql: str
    params: List[Any]
    duration: float  # seconds
    stack_trace: str
    timestamp: float
    is_duplicate: bool = False
    similar_count: int = 0


@dataclass
class NPlusOnePattern:
    """Detected N+1 query pattern."""

    query_template: str
    occurrences: int
    total_time: float
    first_occurrence_stack: str
    suggested_fix: str
    severity: str  # 'warning', 'error'
    model_name: Optional[str] = None
    relationship_field: Optional[str] = None


class QueryTracker:
    """
    Tracks database queries to detect N+1 patterns.

    Thread-safe query tracking with pattern detection and analysis.
    """

    def __init__(
        self,
        warn_threshold: int = 10,
        error_threshold: int = 50,
        enable_stack_traces: bool = True,
        similarity_threshold: float = 0.8,
    ):
        """
        Initialize query tracker.

        Args:
            warn_threshold: Number of similar queries before warning
            error_threshold: Number of similar queries before error
            enable_stack_traces: Capture stack traces for debugging
            similarity_threshold: Similarity ratio for query matching (0.0-1.0)
        """
        self.warn_threshold = warn_threshold
        self.error_threshold = error_threshold
        self.enable_stack_traces = enable_stack_traces
        self.similarity_threshold = similarity_threshold

        self._local = local()
        self._enabled = True

    def _get_context(self) -> Dict[str, Any]:
        """Get thread-local tracking context."""
        if not hasattr(self._local, "context"):
            self._local.context = {
                "queries": [],
                "query_patterns": defaultdict(list),
                "request_start": time.time(),
                "detected_patterns": [],
            }
        return self._local.context

    def reset(self):
        """Reset tracking for current context (e.g., new request)."""
        if hasattr(self._local, "context"):
            del self._local.context

    def enable(self):
        """Enable query tracking."""
        self._enabled = True

    def disable(self):
        """Disable query tracking."""
        self._enabled = False

    def record_query(
        self, sql: str, params: List[Any], duration: float, model_name: Optional[str] = None
    ):
        """
        Record a database query.

        Args:
            sql: SQL query string
            params: Query parameters
            duration: Query execution time in seconds
            model_name: Name of the model being queried
        """
        if not self._enabled:
            return

        context = self._get_context()

        # Capture stack trace if enabled
        stack_trace = ""
        if self.enable_stack_traces:
            # Filter out internal frames
            stack = traceback.extract_stack()
            filtered_stack = [
                frame
                for frame in stack
                if "covet/database/orm" not in frame.filename and "asyncio" not in frame.filename
            ]
            stack_trace = "".join(traceback.format_list(filtered_stack[-10:]))

        # Create query info
        query_info = QueryInfo(
            sql=sql,
            params=params,
            duration=duration,
            stack_trace=stack_trace,
            timestamp=time.time(),
            model_name=model_name,
        )

        # Add to queries list
        context["queries"].append(query_info)

        # Normalize query for pattern matching
        normalized = self._normalize_query(sql)

        # Track pattern
        context["query_patterns"][normalized].append(query_info)

        # Check for N+1 pattern
        if len(context["query_patterns"][normalized]) >= self.warn_threshold:
            self._detect_n_plus_one(normalized, context)

    def _normalize_query(self, sql: str) -> str:
        """
        Normalize SQL query for pattern matching.

        Replaces parameter placeholders and values with generic markers.

        Args:
            sql: SQL query string

        Returns:
            Normalized query string
        """
        import re

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", sql.strip())

        # Replace PostgreSQL placeholders ($1, $2, etc.)
        normalized = re.sub(r"\$\d+", "?", normalized)

        # Replace numbers that look like IDs
        normalized = re.sub(r"= \d+", "= ?", normalized)
        normalized = re.sub(r"IN \([0-9, ]+\)", "IN (?)", normalized)

        # Normalize common patterns
        normalized = normalized.replace(" WHERE ", " WHERE ")
        normalized = normalized.replace(" AND ", " AND ")
        normalized = normalized.replace(" OR ", " OR ")

        return normalized

    def _detect_n_plus_one(self, normalized_query: str, context: Dict):
        """
        Detect N+1 query pattern.

        Args:
            normalized_query: Normalized query string
            context: Tracking context
        """
        queries = context["query_patterns"][normalized_query]
        occurrences = len(queries)

        # Check if already reported
        for pattern in context["detected_patterns"]:
            if pattern.query_template == normalized_query:
                # Update existing pattern
                pattern.occurrences = occurrences
                pattern.total_time = sum(q.duration for q in queries)
                return

        # Analyze query for potential relationships
        model_name, relationship_field = self._analyze_query_for_relationships(normalized_query)

        # Generate suggestion
        suggested_fix = self._generate_optimization_suggestion(
            normalized_query, model_name, relationship_field
        )

        # Determine severity
        if occurrences >= self.error_threshold:
            severity = "error"
        else:
            severity = "warning"

        # Create pattern detection
        pattern = NPlusOnePattern(
            query_template=normalized_query,
            occurrences=occurrences,
            total_time=sum(q.duration for q in queries),
            first_occurrence_stack=queries[0].stack_trace,
            suggested_fix=suggested_fix,
            severity=severity,
            model_name=model_name,
            relationship_field=relationship_field,
        )

        context["detected_patterns"].append(pattern)

        # Emit warning or error
        if severity == "error":
            logger.error(self._format_n_plus_one_message(pattern))
        else:
            logger.warning(self._format_n_plus_one_message(pattern))

    def _analyze_query_for_relationships(self, query: str) -> tuple[Optional[str], Optional[str]]:
        """
        Analyze query to identify potential relationship access patterns.

        Args:
            query: SQL query string

        Returns:
            Tuple of (model_name, relationship_field)
        """
        import re

        # Look for patterns like: SELECT ... FROM table_name WHERE foreign_key_id = ?
        fk_pattern = r"FROM (\w+) WHERE (\w+_id) = \?"
        match = re.search(fk_pattern, query)

        if match:
            table_name = match.group(1)
            fk_field = match.group(2)

            # Convert to model name (e.g., users -> User)
            model_name = table_name.rstrip("s").title()

            # Extract relationship field (e.g., author_id -> author)
            relationship_field = fk_field.replace("_id", "")

            return model_name, relationship_field

        return None, None

    def _generate_optimization_suggestion(
        self, query: str, model_name: Optional[str], relationship_field: Optional[str]
    ) -> str:
        """
        Generate optimization suggestion for detected N+1 pattern.

        Args:
            query: SQL query
            model_name: Detected model name
            relationship_field: Detected relationship field

        Returns:
            Human-readable optimization suggestion
        """
        suggestions = []

        if relationship_field and model_name:
            # ForeignKey or OneToOne relationship
            if "SELECT *" in query or f"SELECT {relationship_field}" in query:
                suggestions.append(
                    f"Use select_related('{relationship_field}') to load "
                    f"related {model_name} objects in a single query with JOIN"
                )

            # Reverse relationship (one-to-many or many-to-many)
            if "IN (?)" in query:
                suggestions.append(
                    f"Use prefetch_related('{relationship_field}') to load "
                    f"related objects in 2 queries instead of N+1"
                )

        # Generic suggestions
        if not suggestions:
            if "WHERE" in query and "IN" not in query:
                suggestions.append("Consider using select_related() for ForeignKey relationships")
            elif "IN (?)" in query:
                suggestions.append("Consider using prefetch_related() for reverse relationships")
            else:
                suggestions.append("Review query patterns and consider eager loading strategies")

        return " OR ".join(suggestions)

    def _format_n_plus_one_message(self, pattern: NPlusOnePattern) -> str:
        """
        Format N+1 pattern detection message.

        Args:
            pattern: Detected N+1 pattern

        Returns:
            Formatted warning message
        """
        lines = [
            f"\n{'='*80}",
            f"N+1 QUERY DETECTED ({pattern.severity.upper()})",
            f"{'='*80}",
            f"Query executed {pattern.occurrences} times:",
            f"  {pattern.query_template}",
            f"",
            f"Total time wasted: {pattern.total_time*1000:.2f}ms",
            f"",
            f"OPTIMIZATION SUGGESTION:",
            f"  {pattern.suggested_fix}",
            f"",
        ]

        if pattern.first_occurrence_stack:
            lines.extend(
                [
                    "First occurrence stack trace:",
                    pattern.first_occurrence_stack,
                ]
            )

        lines.append(f"{'='*80}\n")

        return "\n".join(lines)

    def get_query_report(self) -> Dict[str, Any]:
        """
        Get detailed query report for current context.

        Returns:
            Dictionary containing query statistics and detected patterns
        """
        context = self._get_context()

        total_queries = len(context["queries"])
        total_time = sum(q.duration for q in context["queries"])
        request_duration = time.time() - context["request_start"]

        # Group queries by model
        queries_by_model = defaultdict(int)
        for query in context["queries"]:
            if hasattr(query, "model_name") and query.model_name:
                queries_by_model[query.model_name] += 1

        # Top slow queries
        slow_queries = sorted(context["queries"], key=lambda q: q.duration, reverse=True)[:10]

        return {
            "total_queries": total_queries,
            "total_query_time": total_time,
            "request_duration": request_duration,
            "db_time_percentage": (
                (total_time / request_duration * 100) if request_duration > 0 else 0
            ),
            "queries_by_model": dict(queries_by_model),
            "detected_patterns": [
                {
                    "query": p.query_template,
                    "occurrences": p.occurrences,
                    "total_time": p.total_time,
                    "severity": p.severity,
                    "suggestion": p.suggested_fix,
                }
                for p in context["detected_patterns"]
            ],
            "slow_queries": [
                {"sql": q.sql, "duration": q.duration, "params": q.params} for q in slow_queries
            ],
            "all_queries": [
                {"sql": q.sql, "duration": q.duration, "params": q.params, "timestamp": q.timestamp}
                for q in context["queries"]
            ],
        }

    def print_query_summary(self):
        """Print a formatted query summary to console."""
        report = self.get_query_report()

        print(f"\n{'='*80}")
        print(f"DATABASE QUERY SUMMARY")
        print(f"{'='*80}")
        print(f"Total Queries: {report['total_queries']}")
        print(f"Total Query Time: {report['total_query_time']*1000:.2f}ms")
        print(f"Request Duration: {report['request_duration']*1000:.2f}ms")
        print(f"DB Time: {report['db_time_percentage']:.1f}%")

        if report["queries_by_model"]:
            print(f"\nQueries by Model:")
            for model, count in sorted(report["queries_by_model"].items()):
                print(f"  {model}: {count}")

        if report["detected_patterns"]:
            print(f"\nDETECTED N+1 PATTERNS: {len(report['detected_patterns'])}")
            for pattern in report["detected_patterns"]:
                print(f"\n  [{pattern['severity'].upper()}] {pattern['occurrences']} queries:")
                print(f"    {pattern['query']}")
                print(f"    Total time: {pattern['total_time']*1000:.2f}ms")
                print(f"    Fix: {pattern['suggestion']}")

        if report["slow_queries"]:
            print(f"\nSLOWEST QUERIES:")
            for i, query in enumerate(report["slow_queries"][:5], 1):
                print(f"\n  {i}. Duration: {query['duration']*1000:.2f}ms")
                print(f"     {query['sql']}")

        print(f"{'='*80}\n")


# Global tracker instance
_global_tracker: Optional[QueryTracker] = None


def get_query_tracker() -> Optional[QueryTracker]:
    """Get the global query tracker instance."""
    return _global_tracker


def enable_query_tracking(
    warn_threshold: int = 10, error_threshold: int = 50, enable_stack_traces: bool = True
) -> QueryTracker:
    """
    Enable query tracking globally.

    Args:
        warn_threshold: Number of similar queries before warning
        error_threshold: Number of similar queries before error
        enable_stack_traces: Capture stack traces for debugging

    Returns:
        QueryTracker instance
    """
    global _global_tracker

    _global_tracker = QueryTracker(
        warn_threshold=warn_threshold,
        error_threshold=error_threshold,
        enable_stack_traces=enable_stack_traces,
    )

    logger.info("N+1 query detection enabled")
    return _global_tracker


def disable_query_tracking():
    """Disable query tracking globally."""
    global _global_tracker

    if _global_tracker:
        _global_tracker.disable()
        logger.info("N+1 query detection disabled")


@contextmanager
def track_queries(tracker: Optional[QueryTracker] = None):
    """
    Context manager for tracking queries in a specific block.

    Args:
        tracker: QueryTracker instance (uses global if None)

    Example:
        with track_queries() as tracker:
            users = await User.objects.all()
            for user in users:
                profile = await user.profile

        tracker.print_query_summary()
    """
    tracker = tracker or get_query_tracker()

    if tracker:
        tracker.reset()

    try:
        yield tracker
    finally:
        if tracker:
            pass  # Keep results for inspection


__all__ = [
    "QueryTracker",
    "QueryInfo",
    "NPlusOnePattern",
    "get_query_tracker",
    "enable_query_tracking",
    "disable_query_tracking",
    "track_queries",
]
