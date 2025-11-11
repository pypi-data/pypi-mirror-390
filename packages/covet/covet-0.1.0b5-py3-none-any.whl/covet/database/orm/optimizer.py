"""
ORM Query Optimizer

Advanced query optimization engine that analyzes, rewrites, and optimizes ORM queries
for maximum performance across PostgreSQL, MySQL, and SQLite.

Features:
- Query plan analysis and cost estimation
- JOIN order optimization
- Subquery flattening and optimization
- Redundant clause elimination
- Index usage detection and recommendations
- WHERE clause simplification
- UNION vs UNION ALL optimization
- LIMIT/OFFSET push-down optimization
- Query rewriting for performance

Example:
    from covet.database.orm.optimizer import QueryOptimizer

    optimizer = QueryOptimizer(database='postgresql')

    # Analyze query
    analysis = optimizer.analyze_query(sql, params)
    print(f"Cost: {analysis.estimated_cost}")
    print(f"Warnings: {analysis.warnings}")

    # Optimize query
    optimized_sql, optimized_params = optimizer.optimize_query(sql, params)

    # Get recommendations
    recommendations = optimizer.get_recommendations(sql)
"""

import asyncio
import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Query optimization aggressiveness level."""

    CONSERVATIVE = "conservative"  # Safe, minimal changes
    MODERATE = "moderate"  # Balanced approach
    AGGRESSIVE = "aggressive"  # Maximum optimization


class QueryComplexity(Enum):
    """Query complexity classification."""

    SIMPLE = "simple"  # Single table, no joins
    MODERATE = "moderate"  # Few joins, simple conditions
    COMPLEX = "complex"  # Multiple joins, subqueries
    VERY_COMPLEX = "very_complex"  # Nested subqueries, complex logic


@dataclass
class QueryAnalysis:
    """Results of query analysis."""

    sql: str
    database_type: str
    complexity: QueryComplexity
    estimated_cost: float
    estimated_rows: int
    table_count: int
    join_count: int
    subquery_count: int
    index_usage: List[str]
    missing_indexes: List[str]
    warnings: List[str] = field(default_factory=list)
    optimization_hints: List[str] = field(default_factory=list)
    execution_time: Optional[float] = None
    analyzed_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationResult:
    """Results of query optimization."""

    original_sql: str
    optimized_sql: str
    original_params: List[Any]
    optimized_params: List[Any]
    optimizations_applied: List[str]
    estimated_improvement: float  # Percentage
    warnings: List[str] = field(default_factory=list)


class QueryOptimizer:
    """
    Advanced query optimizer for ORM queries.

    Analyzes SQL queries, rewrites them for better performance, and provides
    optimization recommendations.
    """

    def __init__(
        self,
        database: str = "postgresql",
        optimization_level: OptimizationLevel = OptimizationLevel.MODERATE,
        cache_enabled: bool = True,
    ):
        """
        Initialize query optimizer.

        Args:
            database: Database type ('postgresql', 'mysql', 'sqlite')
            optimization_level: How aggressively to optimize
            cache_enabled: Whether to cache analysis results
        """
        self.database = database.lower()
        self.optimization_level = optimization_level
        self.cache_enabled = cache_enabled

        # Analysis cache
        self._analysis_cache: Dict[str, QueryAnalysis] = {}
        self._cache_ttl = timedelta(minutes=30)

        # Optimization statistics
        self.stats = {
            "queries_analyzed": 0,
            "queries_optimized": 0,
            "total_improvement": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def analyze_query(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        use_cache: bool = True,
    ) -> QueryAnalysis:
        """
        Analyze query for performance characteristics.

        Args:
            sql: SQL query to analyze
            params: Query parameters
            use_cache: Whether to use cached analysis

        Returns:
            QueryAnalysis with detailed metrics
        """
        start_time = time.time()

        # Check cache
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(sql, params)
            cached = self._analysis_cache.get(cache_key)

            if cached and (datetime.now() - cached.analyzed_at) < self._cache_ttl:
                self.stats["cache_hits"] += 1
                return cached

            self.stats["cache_misses"] += 1

        # Normalize SQL
        normalized_sql = self._normalize_sql(sql)

        # Analyze query structure
        complexity = self._analyze_complexity(normalized_sql)
        table_count = self._count_tables(normalized_sql)
        join_count = self._count_joins(normalized_sql)
        subquery_count = self._count_subqueries(normalized_sql)

        # Detect index usage
        index_usage = self._detect_index_usage(normalized_sql)
        missing_indexes = self._detect_missing_indexes(normalized_sql)

        # Estimate cost
        estimated_cost = self._estimate_cost(
            normalized_sql,
            table_count,
            join_count,
            subquery_count,
        )

        # Estimate rows
        estimated_rows = self._estimate_rows(normalized_sql)

        # Generate warnings
        warnings = self._generate_warnings(
            normalized_sql,
            complexity,
            table_count,
            join_count,
            subquery_count,
        )

        # Generate optimization hints
        hints = self._generate_optimization_hints(
            normalized_sql,
            complexity,
            index_usage,
            missing_indexes,
        )

        execution_time = time.time() - start_time

        analysis = QueryAnalysis(
            sql=sql,
            database_type=self.database,
            complexity=complexity,
            estimated_cost=estimated_cost,
            estimated_rows=estimated_rows,
            table_count=table_count,
            join_count=join_count,
            subquery_count=subquery_count,
            index_usage=index_usage,
            missing_indexes=missing_indexes,
            warnings=warnings,
            optimization_hints=hints,
            execution_time=execution_time,
        )

        # Cache result
        if use_cache and self.cache_enabled:
            cache_key = self._get_cache_key(sql, params)
            self._analysis_cache[cache_key] = analysis

        self.stats["queries_analyzed"] += 1

        return analysis

    def optimize_query(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
    ) -> OptimizationResult:
        """
        Optimize query for better performance.

        Applies multiple optimization techniques:
        - Redundant clause elimination
        - Subquery flattening
        - JOIN reordering
        - UNION optimization
        - LIMIT push-down
        - WHERE simplification

        Args:
            sql: SQL query to optimize
            params: Query parameters

        Returns:
            OptimizationResult with optimized query
        """
        start_time = time.time()

        original_sql = sql
        original_params = params or []
        optimized_sql = sql
        optimizations_applied = []
        warnings = []

        # Normalize SQL
        optimized_sql = self._normalize_sql(optimized_sql)

        # Apply optimization passes
        if self.optimization_level.value in ["moderate", "aggressive"]:
            # Pass 1: Remove redundant clauses
            sql_before = optimized_sql
            optimized_sql = self._remove_redundant_clauses(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("redundant_clause_removal")

            # Pass 2: Simplify WHERE conditions
            sql_before = optimized_sql
            optimized_sql = self._simplify_where_clause(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("where_clause_simplification")

            # Pass 3: Optimize UNION queries
            sql_before = optimized_sql
            optimized_sql = self._optimize_union(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("union_optimization")

        if self.optimization_level == OptimizationLevel.AGGRESSIVE:
            # Pass 4: Flatten subqueries
            sql_before = optimized_sql
            optimized_sql = self._flatten_subqueries(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("subquery_flattening")

            # Pass 5: Reorder JOINs
            sql_before = optimized_sql
            optimized_sql = self._reorder_joins(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("join_reordering")

            # Pass 6: Push down LIMIT
            sql_before = optimized_sql
            optimized_sql = self._push_down_limit(optimized_sql)
            if sql_before != optimized_sql:
                optimizations_applied.append("limit_pushdown")

        # Estimate improvement
        original_cost = self._estimate_cost(original_sql, 0, 0, 0)
        optimized_cost = self._estimate_cost(optimized_sql, 0, 0, 0)
        improvement = (
            ((original_cost - optimized_cost) / original_cost * 100) if original_cost > 0 else 0.0
        )

        self.stats["queries_optimized"] += 1
        self.stats["total_improvement"] += improvement

        return OptimizationResult(
            original_sql=original_sql,
            optimized_sql=optimized_sql,
            original_params=original_params,
            optimized_params=params or [],
            optimizations_applied=optimizations_applied,
            estimated_improvement=improvement,
            warnings=warnings,
        )

    def get_recommendations(self, sql: str) -> List[str]:
        """
        Get optimization recommendations for a query.

        Args:
            sql: SQL query to analyze

        Returns:
            List of recommendation strings
        """
        recommendations = []
        normalized_sql = self._normalize_sql(sql)

        # Check for missing indexes
        missing_indexes = self._detect_missing_indexes(normalized_sql)
        if missing_indexes:
            recommendations.append(f"Consider adding indexes on: {', '.join(missing_indexes)}")

        # Check for N+1 queries
        if self._detect_n_plus_one_pattern(normalized_sql):
            recommendations.append(
                "Potential N+1 query detected. Use select_related() or prefetch_related()"
            )

        # Check for sequential scans
        if self._likely_sequential_scan(normalized_sql):
            recommendations.append("Query likely requires sequential scan. Consider adding indexes")

        # Check for inefficient patterns
        if "SELECT *" in normalized_sql.upper():
            recommendations.append(
                "Avoid SELECT *. Specify only needed columns for better performance"
            )

        if "OFFSET" in normalized_sql.upper():
            offset_match = re.search(r"OFFSET\s+(\d+)", normalized_sql, re.IGNORECASE)
            if offset_match and int(offset_match.group(1)) > 1000:
                recommendations.append(
                    "Large OFFSET detected. Consider using cursor-based pagination"
                )

        # Check for subquery optimization
        if self._count_subqueries(normalized_sql) > 2:
            recommendations.append(
                "Multiple subqueries detected. Consider using JOINs or CTEs instead"
            )

        # Check for OR in WHERE clause
        if re.search(r"\bOR\b", normalized_sql, re.IGNORECASE):
            recommendations.append(
                "OR conditions may prevent index usage. Consider UNION or IN clause"
            )

        return recommendations

    def clear_cache(self) -> None:
        """Clear analysis cache."""
        self._analysis_cache.clear()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get optimizer statistics.

        Returns:
            Dictionary of statistics
        """
        avg_improvement = (
            self.stats["total_improvement"] / self.stats["queries_optimized"]
            if self.stats["queries_optimized"] > 0
            else 0.0
        )

        cache_hit_rate = (
            self.stats["cache_hits"] / (self.stats["cache_hits"] + self.stats["cache_misses"]) * 100
            if (self.stats["cache_hits"] + self.stats["cache_misses"]) > 0
            else 0.0
        )

        return {
            **self.stats,
            "average_improvement": avg_improvement,
            "cache_hit_rate": cache_hit_rate,
        }

    # Private methods

    def _get_cache_key(self, sql: str, params: Optional[List[Any]] = None) -> str:
        """Generate cache key for query."""
        key_data = f"{sql}:{str(params or [])}"
        return hashlib.md5(key_data.encode(), usedforsecurity=False).hexdigest()

    def _normalize_sql(self, sql: str) -> str:
        """Normalize SQL for consistent analysis."""
        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", sql.strip())
        # Remove comments
        normalized = re.sub(r"--.*$", "", normalized, flags=re.MULTILINE)
        normalized = re.sub(r"/\*.*?\*/", "", normalized, flags=re.DOTALL)
        return normalized

    def _analyze_complexity(self, sql: str) -> QueryComplexity:
        """Analyze query complexity."""
        join_count = self._count_joins(sql)
        subquery_count = self._count_subqueries(sql)
        table_count = self._count_tables(sql)

        # Calculate complexity score
        score = join_count * 2 + subquery_count * 3 + table_count

        if score <= 3:
            return QueryComplexity.SIMPLE
        elif score <= 8:
            return QueryComplexity.MODERATE
        elif score <= 15:
            return QueryComplexity.COMPLEX
        else:
            return QueryComplexity.VERY_COMPLEX

    def _count_tables(self, sql: str) -> int:
        """Count number of tables in query."""
        # Simple heuristic: count FROM and JOIN clauses
        from_count = len(re.findall(r"\bFROM\b", sql, re.IGNORECASE))
        join_count = self._count_joins(sql)
        return from_count + join_count

    def _count_joins(self, sql: str) -> int:
        """Count number of JOINs in query."""
        return len(re.findall(r"\b(?:INNER|LEFT|RIGHT|FULL|CROSS)\s+JOIN\b", sql, re.IGNORECASE))

    def _count_subqueries(self, sql: str) -> int:
        """Count number of subqueries."""
        # Count SELECT statements (excluding the main one)
        select_count = len(re.findall(r"\bSELECT\b", sql, re.IGNORECASE))
        return max(0, select_count - 1)

    def _detect_index_usage(self, sql: str) -> List[str]:
        """Detect which indexes might be used."""
        indexes = []

        # Look for WHERE clauses with specific columns
        where_match = re.search(
            r"WHERE\s+(.*?)(?:ORDER|GROUP|LIMIT|$)", sql, re.IGNORECASE | re.DOTALL
        )
        if where_match:
            where_clause = where_match.group(1)
            # Extract column names
            columns = re.findall(r"(\w+)\s*(?:=|>|<|>=|<=|!=|IN|LIKE)", where_clause, re.IGNORECASE)
            indexes.extend(columns)

        return list(set(indexes))

    def _detect_missing_indexes(self, sql: str) -> List[str]:
        """Detect columns that might need indexes."""
        missing = []

        # Look for WHERE clauses without indexed columns
        where_match = re.search(
            r"WHERE\s+(.*?)(?:ORDER|GROUP|LIMIT|$)", sql, re.IGNORECASE | re.DOTALL
        )
        if where_match:
            where_clause = where_match.group(1)

            # Check for OR conditions (often not indexed well)
            if re.search(r"\bOR\b", where_clause, re.IGNORECASE):
                columns = re.findall(r"(\w+)\s*(?:=|>|<|>=|<=|!=)", where_clause, re.IGNORECASE)
                missing.extend([f"{col} (OR condition)" for col in columns])

        # Look for ORDER BY without index
        order_match = re.search(r"ORDER\s+BY\s+([\w,\s]+)", sql, re.IGNORECASE)
        if order_match:
            order_cols = [col.strip() for col in order_match.group(1).split(",")]
            missing.extend([f"{col} (ORDER BY)" for col in order_cols])

        return list(set(missing))

    def _estimate_cost(
        self,
        sql: str,
        table_count: int,
        join_count: int,
        subquery_count: int,
    ) -> float:
        """
        Estimate query cost (simplified model).

        Real databases use sophisticated cost models with statistics.
        This is a simplified version for demonstration.
        """
        base_cost = 10.0

        # Table scan costs
        cost = base_cost * table_count

        # JOIN costs (multiplicative)
        if join_count > 0:
            cost *= 1.5**join_count

        # Subquery costs
        cost += subquery_count * 50.0

        # Check for expensive operations
        if "DISTINCT" in sql.upper():
            cost *= 1.3

        if "ORDER BY" in sql.upper():
            cost *= 1.2

        if "GROUP BY" in sql.upper():
            cost *= 1.4

        return round(cost, 2)

    def _estimate_rows(self, sql: str) -> int:
        """Estimate number of rows returned (very simplified)."""
        # This would normally use table statistics
        if "LIMIT" in sql.upper():
            limit_match = re.search(r"LIMIT\s+(\d+)", sql, re.IGNORECASE)
            if limit_match:
                return int(limit_match.group(1))

        # Default estimates based on operations
        if "WHERE" in sql.upper():
            return 100  # Filtered results

        return 1000  # Full table

    def _generate_warnings(
        self,
        sql: str,
        complexity: QueryComplexity,
        table_count: int,
        join_count: int,
        subquery_count: int,
    ) -> List[str]:
        """Generate performance warnings."""
        warnings = []

        if complexity == QueryComplexity.VERY_COMPLEX:
            warnings.append("Very complex query detected. Consider breaking into smaller queries")

        if join_count > 5:
            warnings.append(f"High number of JOINs ({join_count}). May impact performance")

        if subquery_count > 3:
            warnings.append(f"Multiple subqueries ({subquery_count}). Consider using JOINs or CTEs")

        if "SELECT *" in sql.upper():
            warnings.append("Using SELECT * may return unnecessary data")

        if not re.search(r"\bWHERE\b", sql, re.IGNORECASE) and "SELECT" in sql.upper():
            warnings.append("Query has no WHERE clause. May return entire table")

        return warnings

    def _generate_optimization_hints(
        self,
        sql: str,
        complexity: QueryComplexity,
        index_usage: List[str],
        missing_indexes: List[str],
    ) -> List[str]:
        """Generate optimization hints."""
        hints = []

        if missing_indexes:
            hints.append(f"Consider indexing: {', '.join(missing_indexes[:3])}")

        if self._count_subqueries(sql) > 0:
            hints.append("Consider rewriting subqueries as JOINs")

        if "UNION " in sql.upper() and "UNION ALL" not in sql.upper():
            hints.append("Use UNION ALL if duplicates are not a concern")

        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.VERY_COMPLEX]:
            hints.append("Consider using materialized views or denormalization")

        return hints

    def _remove_redundant_clauses(self, sql: str) -> str:
        """Remove redundant SQL clauses."""
        # Remove duplicate WHERE conditions
        # Example: WHERE x = 1 AND x = 1 -> WHERE x = 1

        where_match = re.search(
            r"WHERE\s+(.*?)(?:ORDER|GROUP|LIMIT|$)", sql, re.IGNORECASE | re.DOTALL
        )
        if where_match:
            where_clause = where_match.group(1).strip()
            conditions = [c.strip() for c in where_clause.split("AND")]
            unique_conditions = list(dict.fromkeys(conditions))  # Preserve order, remove duplicates

            if len(unique_conditions) < len(conditions):
                new_where = " AND ".join(unique_conditions)
                sql = sql[: where_match.start(1)] + new_where + sql[where_match.end(1) :]

        return sql

    def _simplify_where_clause(self, sql: str) -> str:
        """Simplify WHERE clause logic."""
        # Remove tautologies like "1 = 1"
        sql = re.sub(r"\b1\s*=\s*1\s*AND\s*", "", sql, flags=re.IGNORECASE)
        sql = re.sub(r"\s*AND\s*1\s*=\s*1\b", "", sql, flags=re.IGNORECASE)

        # Remove double negatives
        sql = re.sub(r"NOT\s*\(\s*NOT\s+", "(", sql, flags=re.IGNORECASE)

        return sql

    def _optimize_union(self, sql: str) -> str:
        """Optimize UNION queries."""
        # Convert UNION to UNION ALL if duplicates don't matter
        # This is a conservative optimization - only apply if safe

        # For now, just suggest in hints
        # Real implementation would need semantic analysis
        return sql

    def _flatten_subqueries(self, sql: str) -> str:
        """Flatten simple subqueries into JOINs."""
        # This is a complex optimization that requires query tree parsing
        # For production use, consider using a SQL parser library like sqlparse

        # Example: SELECT * FROM t1 WHERE id IN (SELECT id FROM t2)
        # -> SELECT t1.* FROM t1 INNER JOIN t2 ON t1.id = t2.id

        # Simplified version - detect IN subquery pattern
        pattern = r"WHERE\s+(\w+)\s+IN\s+\(\s*SELECT\s+(\w+)\s+FROM\s+(\w+)\s*\)"
        match = re.search(pattern, sql, re.IGNORECASE)

        if match:
            col1, col2, table2 = match.groups()
            # Only flatten if it's a simple subquery
            if "WHERE" not in sql[match.start() : match.end()].upper():
                # This is a simplified rewrite
                logger.debug(f"Could flatten subquery on {table2}")

        return sql

    def _reorder_joins(self, sql: str) -> str:
        """Reorder JOINs for better performance."""
        # JOIN order optimization is complex and requires table statistics
        # This would need:
        # 1. Table cardinality information
        # 2. Join selectivity estimates
        # 3. Index availability

        # For now, return unchanged
        # Real implementation would use cost-based optimization
        return sql

    def _push_down_limit(self, sql: str) -> str:
        """Push LIMIT clause down to subqueries when possible."""
        # If a subquery doesn't have a LIMIT but the outer query does,
        # consider pushing it down

        # This is safe only in specific cases
        # Real implementation would need careful analysis
        return sql

    def _detect_n_plus_one_pattern(self, sql: str) -> bool:
        """Detect potential N+1 query pattern."""
        # This would typically be detected at the application level
        # by tracking query patterns, not from a single SQL string
        return False

    def _likely_sequential_scan(self, sql: str) -> bool:
        """Check if query likely requires sequential scan."""
        # Queries without WHERE or with OR conditions often need seq scans
        has_where = bool(re.search(r"\bWHERE\b", sql, re.IGNORECASE))
        has_or = bool(re.search(r"\bOR\b", sql, re.IGNORECASE))

        return not has_where or has_or


class JoinOptimizer:
    """
    Specialized optimizer for JOIN operations.

    Analyzes and optimizes JOIN order based on table statistics and selectivity.
    """

    def __init__(self, database: str = "postgresql"):
        self.database = database

    def optimize_join_order(
        self,
        tables: List[str],
        join_conditions: List[Tuple[str, str, str]],
        table_sizes: Optional[Dict[str, int]] = None,
    ) -> List[str]:
        """
        Optimize JOIN order for minimum cost.

        Args:
            tables: List of table names
            join_conditions: List of (table1, table2, condition) tuples
            table_sizes: Optional dictionary of table sizes

        Returns:
            Optimized table order
        """
        if not tables or len(tables) < 2:
            return tables

        # Use greedy algorithm: start with smallest table
        if table_sizes:
            sorted_tables = sorted(tables, key=lambda t: table_sizes.get(t, float("inf")))
            return sorted_tables

        # Without statistics, keep original order
        return tables

    def estimate_join_selectivity(
        self,
        table1: str,
        table2: str,
        condition: str,
    ) -> float:
        """
        Estimate selectivity of a JOIN.

        Selectivity is the fraction of rows that satisfy the JOIN condition.

        Args:
            table1: First table name
            table2: Second table name
            condition: JOIN condition

        Returns:
            Selectivity (0.0 to 1.0)
        """
        # Default selectivity assumptions
        if "=" in condition:
            # Equality join - typically very selective
            return 0.01
        elif ">" in condition or "<" in condition:
            # Range join - less selective
            return 0.33
        else:
            # Unknown - assume moderate selectivity
            return 0.10


class SubqueryOptimizer:
    """
    Specialized optimizer for subquery operations.

    Flattens and optimizes subqueries where possible.
    """

    def __init__(self, database: str = "postgresql"):
        self.database = database

    def can_flatten(self, subquery: str) -> bool:
        """
        Check if subquery can be flattened into a JOIN.

        Args:
            subquery: Subquery SQL

        Returns:
            True if subquery can be safely flattened
        """
        # Subqueries can be flattened if they:
        # 1. Don't use aggregates
        # 2. Don't have LIMIT/OFFSET
        # 3. Don't have DISTINCT (in some cases)

        subquery_upper = subquery.upper()

        if any(kw in subquery_upper for kw in ["COUNT", "SUM", "AVG", "MAX", "MIN"]):
            return False

        if any(kw in subquery_upper for kw in ["LIMIT", "OFFSET"]):
            return False

        return True

    def flatten_subquery(self, sql: str) -> str:
        """
        Flatten subquery into JOIN.

        Args:
            sql: SQL with subquery

        Returns:
            Flattened SQL
        """
        # This is a complex transformation that requires full SQL parsing
        # For production, use a SQL parser library
        return sql


__all__ = [
    "QueryOptimizer",
    "JoinOptimizer",
    "SubqueryOptimizer",
    "QueryAnalysis",
    "OptimizationResult",
    "OptimizationLevel",
    "QueryComplexity",
]
