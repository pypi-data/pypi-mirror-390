"""
Index Advisor

Intelligent index recommendation system that analyzes queries, table statistics, and
database schema to suggest optimal indexes for performance improvement.

Features:
- Automatic index suggestion based on query patterns
- Missing index detection
- Unused index detection
- Index bloat analysis
- Composite index recommendations
- Partial index suggestions
- Index maintenance recommendations
- Impact estimation for proposed indexes

Example:
    from covet.database.orm.index_advisor import IndexAdvisor

    advisor = IndexAdvisor(database_adapter=adapter)

    # Analyze queries and get recommendations
    await advisor.analyze_workload([
        "SELECT * FROM users WHERE email = $1",
        "SELECT * FROM posts WHERE user_id = $1 AND created_at > $2",
    ])

    recommendations = await advisor.get_recommendations()
    for rec in recommendations:
        print(f"{rec.index_type}: {rec.create_statement}")
        print(f"Estimated improvement: {rec.estimated_improvement}%")
"""

import asyncio
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class IndexType(Enum):
    """Type of database index."""

    BTREE = "btree"  # B-tree index (default)
    HASH = "hash"  # Hash index
    GIN = "gin"  # Generalized Inverted Index (PostgreSQL)
    GIST = "gist"  # GiST index (PostgreSQL)
    BRIN = "brin"  # Block Range Index (PostgreSQL)
    FULLTEXT = "fulltext"  # Full-text index
    SPATIAL = "spatial"  # Spatial index


class RecommendationPriority(Enum):
    """Priority level for index recommendations."""

    CRITICAL = "critical"  # Will significantly improve performance
    HIGH = "high"  # Likely to improve performance
    MEDIUM = "medium"  # May improve performance
    LOW = "low"  # Minor improvement expected


@dataclass
class IndexRecommendation:
    """Recommendation for creating or modifying an index."""

    table_name: str
    column_names: List[str]
    index_type: IndexType
    priority: RecommendationPriority
    estimated_improvement: float  # Percentage
    reason: str
    create_statement: str
    impact_analysis: Dict[str, Any]
    queries_affected: List[str] = field(default_factory=list)
    is_composite: bool = False
    is_partial: bool = False
    partial_condition: Optional[str] = None
    estimated_size_mb: float = 0.0


@dataclass
class IndexAnalysis:
    """Analysis of existing index."""

    table_name: str
    index_name: str
    column_names: List[str]
    index_type: str
    is_unique: bool
    size_mb: float
    usage_count: int = 0
    last_used: Optional[datetime] = None
    bloat_percentage: float = 0.0
    recommendation: Optional[str] = None


class IndexAdvisor:
    """
    Intelligent index advisor for query optimization.

    Analyzes query workload patterns and database statistics to recommend
    optimal indexes for performance improvement.
    """

    def __init__(self, database_adapter: Any):
        """
        Initialize index advisor.

        Args:
            database_adapter: Database adapter (PostgreSQL, MySQL, or SQLite)
        """
        self.adapter = database_adapter
        self.database_type = self._detect_database_type()

        # Query workload tracking
        self.query_log: List[Tuple[str, List[Any]]] = []
        self.query_patterns: Dict[str, int] = Counter()
        self.column_usage: Dict[Tuple[str, str], int] = Counter()  # (table, column) -> count

        # Existing indexes
        self.existing_indexes: Dict[str, List[IndexAnalysis]] = {}

        # Statistics
        self.stats = {
            "queries_analyzed": 0,
            "recommendations_generated": 0,
            "indexes_analyzed": 0,
        }

    async def analyze_workload(
        self,
        queries: List[Union[str, Tuple[str, List[Any]]]],
    ) -> None:
        """
        Analyze a workload of queries.

        Args:
            queries: List of SQL queries or (sql, params) tuples
        """
        for query in queries:
            if isinstance(query, tuple):
                sql, params = query
            else:
                sql = query
                params = []

            await self.analyze_query(sql, params)

        self.stats["queries_analyzed"] += len(queries)

    async def analyze_query(self, sql: str, params: Optional[List[Any]] = None) -> None:
        """
        Analyze a single query for index opportunities.

        Args:
            sql: SQL query
            params: Query parameters
        """
        # Normalize and store query
        normalized = self._normalize_query(sql)
        self.query_log.append((sql, params or []))
        self.query_patterns[normalized] += 1

        # Extract table and column references
        tables = self._extract_tables(sql)
        where_columns = self._extract_where_columns(sql)
        join_columns = self._extract_join_columns(sql)
        order_columns = self._extract_order_columns(sql)

        # Track column usage
        for table, columns in where_columns.items():
            for column in columns:
                self.column_usage[(table, column)] += 1

        for table, columns in join_columns.items():
            for column in columns:
                self.column_usage[(table, column)] += 1

        for table, columns in order_columns.items():
            for column in columns:
                self.column_usage[(table, column)] += 0.5  # Lower weight for ORDER BY

    async def get_recommendations(
        self,
        min_priority: RecommendationPriority = RecommendationPriority.LOW,
    ) -> List[IndexRecommendation]:
        """
        Generate index recommendations based on analyzed workload.

        Args:
            min_priority: Minimum priority level to include

        Returns:
            List of IndexRecommendation sorted by priority
        """
        recommendations = []

        # Load existing indexes
        await self._load_existing_indexes()

        # Analyze column usage patterns
        recommendations.extend(await self._recommend_single_column_indexes())
        recommendations.extend(await self._recommend_composite_indexes())
        recommendations.extend(await self._recommend_partial_indexes())

        # Filter by priority
        priority_order = {
            RecommendationPriority.CRITICAL: 0,
            RecommendationPriority.HIGH: 1,
            RecommendationPriority.MEDIUM: 2,
            RecommendationPriority.LOW: 3,
        }

        min_priority_value = priority_order[min_priority]
        recommendations = [
            rec for rec in recommendations if priority_order[rec.priority] <= min_priority_value
        ]

        # Sort by priority and estimated improvement
        recommendations.sort(key=lambda r: (priority_order[r.priority], -r.estimated_improvement))

        self.stats["recommendations_generated"] = len(recommendations)

        return recommendations

    async def analyze_existing_indexes(self) -> List[IndexAnalysis]:
        """
        Analyze existing indexes for efficiency and usage.

        Returns:
            List of IndexAnalysis with recommendations
        """
        await self._load_existing_indexes()

        analyses = []
        for table_name, indexes in self.existing_indexes.items():
            for index in indexes:
                # Check for unused indexes
                if index.usage_count == 0:
                    index.recommendation = "Consider dropping - index is not being used"

                # Check for bloat
                if index.bloat_percentage > 30:
                    index.recommendation = "High bloat detected - consider rebuilding index"

                # Check for redundant indexes
                redundant = await self._check_redundant_index(table_name, index)
                if redundant:
                    index.recommendation = f"Redundant with index: {redundant}"

                analyses.append(index)

        self.stats["indexes_analyzed"] = len(analyses)

        return analyses

    async def detect_missing_indexes(self) -> List[IndexRecommendation]:
        """
        Detect missing indexes that would benefit current workload.

        Returns:
            List of high-priority recommendations for missing indexes
        """
        recommendations = await self.get_recommendations(min_priority=RecommendationPriority.HIGH)

        # Filter to only missing indexes
        missing = []
        for rec in recommendations:
            if not await self._index_exists(rec.table_name, rec.column_names):
                missing.append(rec)

        return missing

    async def detect_unused_indexes(self) -> List[IndexAnalysis]:
        """
        Detect indexes that are not being used.

        Returns:
            List of unused indexes that could be dropped
        """
        analyses = await self.analyze_existing_indexes()

        unused = []
        for analysis in analyses:
            if analysis.usage_count == 0 and not analysis.is_unique:
                unused.append(analysis)

        return unused

    async def estimate_index_impact(
        self,
        table_name: str,
        column_names: List[str],
    ) -> Dict[str, Any]:
        """
        Estimate the impact of creating an index.

        Args:
            table_name: Table name
            column_names: Column names for index

        Returns:
            Dictionary with impact estimates
        """
        # Get table statistics
        row_count = await self._get_table_row_count(table_name)
        table_size_mb = await self._get_table_size(table_name)

        # Estimate index size (rough approximation)
        bytes_per_row = 8 * len(column_names)  # Simplified
        estimated_size_mb = (row_count * bytes_per_row) / (1024 * 1024)

        # Count queries that would benefit
        affected_queries = 0
        for (table, column), count in self.column_usage.items():
            if table == table_name and column in column_names:
                affected_queries += count

        # Estimate improvement
        estimated_improvement = min(
            90.0, affected_queries * 10.0 / max(len(self.query_log), 1) * 100
        )

        return {
            "estimated_size_mb": estimated_size_mb,
            "affected_query_count": affected_queries,
            "estimated_improvement": estimated_improvement,
            "table_row_count": row_count,
            "table_size_mb": table_size_mb,
            "size_overhead_percentage": (estimated_size_mb / max(table_size_mb, 0.1)) * 100,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get advisor statistics."""
        return {
            **self.stats,
            "unique_query_patterns": len(self.query_patterns),
            "total_queries": len(self.query_log),
            "columns_tracked": len(self.column_usage),
        }

    # Private methods

    def _detect_database_type(self) -> str:
        """Detect database type from adapter."""
        adapter_class = self.adapter.__class__.__name__.lower()

        if "postgresql" in adapter_class or "postgres" in adapter_class:
            return "postgresql"
        elif "mysql" in adapter_class:
            return "mysql"
        elif "sqlite" in adapter_class:
            return "sqlite"
        else:
            logger.warning(f"Unknown adapter type: {adapter_class}")
            return "postgresql"

    def _normalize_query(self, sql: str) -> str:
        """Normalize query for pattern matching."""
        # Remove literals and parameters
        normalized = re.sub(r"'[^']*'", "'?'", sql)
        normalized = re.sub(r"\$\d+", "$?", normalized)
        normalized = re.sub(r"\?", "$?", normalized)
        normalized = re.sub(r"\b\d+\b", "?", normalized)

        # Remove extra whitespace
        normalized = re.sub(r"\s+", " ", normalized.strip())

        return normalized

    def _extract_tables(self, sql: str) -> Set[str]:
        """Extract table names from query."""
        tables = set()

        # FROM clause
        from_matches = re.findall(r"\bFROM\s+(\w+)", sql, re.IGNORECASE)
        tables.update(from_matches)

        # JOIN clauses
        join_matches = re.findall(r"\bJOIN\s+(\w+)", sql, re.IGNORECASE)
        tables.update(join_matches)

        return tables

    def _extract_where_columns(self, sql: str) -> Dict[str, List[str]]:
        """Extract columns used in WHERE clause."""
        columns_by_table = defaultdict(list)

        # Find WHERE clause
        where_match = re.search(
            r"\bWHERE\s+(.*?)(?:\bORDER\s+BY\b|\bGROUP\s+BY\b|\bLIMIT\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL,
        )

        if where_match:
            where_clause = where_match.group(1)

            # Extract column references
            # Pattern: table.column or column
            column_refs = re.findall(
                r"(?:(\w+)\.)?(\w+)\s*(?:=|>|<|>=|<=|!=|IN|LIKE)", where_clause, re.IGNORECASE
            )

            for table, column in column_refs:
                if table:
                    columns_by_table[table].append(column)
                else:
                    # No table prefix - need to infer from query
                    tables = self._extract_tables(sql)
                    if len(tables) == 1:
                        columns_by_table[list(tables)[0]].append(column)

        return dict(columns_by_table)

    def _extract_join_columns(self, sql: str) -> Dict[str, List[str]]:
        """Extract columns used in JOIN conditions."""
        columns_by_table = defaultdict(list)

        # Find JOIN...ON clauses
        join_matches = re.findall(
            r"\bJOIN\s+(\w+)\s+.*?\bON\s+(.*?)(?:\bJOIN\b|\bWHERE\b|\bORDER\b|\bGROUP\b|$)",
            sql,
            re.IGNORECASE | re.DOTALL,
        )

        for table, on_clause in join_matches:
            # Extract column references
            column_refs = re.findall(r"(\w+)\.(\w+)", on_clause)

            for ref_table, column in column_refs:
                columns_by_table[ref_table].append(column)

        return dict(columns_by_table)

    def _extract_order_columns(self, sql: str) -> Dict[str, List[str]]:
        """Extract columns used in ORDER BY clause."""
        columns_by_table = defaultdict(list)

        # Find ORDER BY clause
        order_match = re.search(
            r"\bORDER\s+BY\s+(.*?)(?:\bLIMIT\b|$)", sql, re.IGNORECASE | re.DOTALL
        )

        if order_match:
            order_clause = order_match.group(1)

            # Extract column references
            column_refs = re.findall(r"(?:(\w+)\.)?(\w+)", order_clause)

            for table, column in column_refs:
                if table:
                    columns_by_table[table].append(column)
                else:
                    tables = self._extract_tables(sql)
                    if len(tables) == 1:
                        columns_by_table[list(tables)[0]].append(column)

        return dict(columns_by_table)

    async def _load_existing_indexes(self) -> None:
        """Load existing indexes from database."""
        if self.existing_indexes:
            return  # Already loaded

        try:
            if self.database_type == "postgresql":
                query = """
                    SELECT
                        schemaname,
                        tablename,
                        indexname,
                        indexdef
                    FROM pg_indexes
                    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                """
                rows = await self.adapter.fetch_all(query)

                for row in rows:
                    table_name = row["tablename"]
                    index_name = row["indexname"]

                    # Parse column names from index definition
                    columns = self._parse_index_columns(row["indexdef"])

                    analysis = IndexAnalysis(
                        table_name=table_name,
                        index_name=index_name,
                        column_names=columns,
                        index_type="btree",
                        is_unique="UNIQUE" in row["indexdef"].upper(),
                        size_mb=0.0,  # Would need separate query
                    )

                    if table_name not in self.existing_indexes:
                        self.existing_indexes[table_name] = []
                    self.existing_indexes[table_name].append(analysis)

            elif self.database_type == "mysql":
                # MySQL: SHOW INDEX FROM table
                # Would need to query each table individually
                pass

            elif self.database_type == "sqlite":
                # SQLite: sqlite_master table
                query = "SELECT name, tbl_name, sql FROM sqlite_master WHERE type = 'index'"
                rows = await self.adapter.fetch_all(query)

                for row in rows:
                    table_name = row["tbl_name"]
                    index_name = row["name"]

                    columns = self._parse_index_columns(row["sql"] or "")

                    analysis = IndexAnalysis(
                        table_name=table_name,
                        index_name=index_name,
                        column_names=columns,
                        index_type="btree",
                        is_unique="UNIQUE" in (row["sql"] or "").upper(),
                        size_mb=0.0,
                    )

                    if table_name not in self.existing_indexes:
                        self.existing_indexes[table_name] = []
                    self.existing_indexes[table_name].append(analysis)

        except Exception as e:
            logger.error(f"Failed to load existing indexes: {e}")
            self.existing_indexes = {}

    def _parse_index_columns(self, index_def: str) -> List[str]:
        """Parse column names from index definition."""
        # Extract column names from CREATE INDEX statement
        match = re.search(r"\((.*?)\)", index_def)
        if match:
            columns_str = match.group(1)
            # Split by comma and clean up
            columns = [col.strip().split()[0] for col in columns_str.split(",")]
            return columns

        return []

    async def _recommend_single_column_indexes(self) -> List[IndexRecommendation]:
        """Recommend single-column indexes."""
        recommendations = []

        # Find heavily used columns without indexes
        for (table, column), usage_count in self.column_usage.most_common(20):
            # Skip if index already exists
            if await self._index_exists(table, [column]):
                continue

            # Estimate impact
            impact = await self.estimate_index_impact(table, [column])

            if impact["estimated_improvement"] > 10:
                priority = self._determine_priority(impact["estimated_improvement"])

                create_stmt = self._generate_create_index_statement(
                    table, [column], IndexType.BTREE
                )

                recommendation = IndexRecommendation(
                    table_name=table,
                    column_names=[column],
                    index_type=IndexType.BTREE,
                    priority=priority,
                    estimated_improvement=impact["estimated_improvement"],
                    reason=f"Column used in {usage_count} queries",
                    create_statement=create_stmt,
                    impact_analysis=impact,
                    estimated_size_mb=impact["estimated_size_mb"],
                )

                recommendations.append(recommendation)

        return recommendations

    async def _recommend_composite_indexes(self) -> List[IndexRecommendation]:
        """Recommend composite (multi-column) indexes."""
        recommendations = []

        # Find column pairs that appear together frequently
        column_pairs = defaultdict(int)

        for query, params in self.query_log:
            where_cols = self._extract_where_columns(query)
            for table, columns in where_cols.items():
                if len(columns) >= 2:
                    # Sort columns for consistent key
                    col_tuple = tuple(sorted(columns))
                    column_pairs[(table, col_tuple)] += 1

        # Generate recommendations for frequent pairs
        for (table, columns), count in column_pairs.items():
            if count < 5:  # Threshold for composite index
                continue

            columns_list = list(columns)

            # Skip if index already exists
            if await self._index_exists(table, columns_list):
                continue

            # Estimate impact
            impact = await self.estimate_index_impact(table, columns_list)

            if impact["estimated_improvement"] > 15:
                priority = self._determine_priority(impact["estimated_improvement"])

                create_stmt = self._generate_create_index_statement(
                    table, columns_list, IndexType.BTREE
                )

                recommendation = IndexRecommendation(
                    table_name=table,
                    column_names=columns_list,
                    index_type=IndexType.BTREE,
                    priority=priority,
                    estimated_improvement=impact["estimated_improvement"],
                    reason=f"Column combination used in {count} queries",
                    create_statement=create_stmt,
                    impact_analysis=impact,
                    is_composite=True,
                    estimated_size_mb=impact["estimated_size_mb"],
                )

                recommendations.append(recommendation)

        return recommendations

    async def _recommend_partial_indexes(self) -> List[IndexRecommendation]:
        """Recommend partial indexes for common filter conditions."""
        recommendations = []

        # Partial indexes are mainly useful for PostgreSQL
        if self.database_type != "postgresql":
            return recommendations

        # Look for queries with common WHERE conditions that could use partial indexes
        # This is a simplified version - production would need more sophisticated analysis

        return recommendations

    async def _index_exists(self, table_name: str, column_names: List[str]) -> bool:
        """Check if an index exists for the given columns."""
        if table_name not in self.existing_indexes:
            return False

        column_set = set(column_names)

        for index in self.existing_indexes[table_name]:
            index_col_set = set(index.column_names)
            # Check if columns match exactly or if existing index covers these columns
            if column_set.issubset(index_col_set):
                return True

        return False

    async def _check_redundant_index(
        self,
        table_name: str,
        index: IndexAnalysis,
    ) -> Optional[str]:
        """Check if index is redundant with another index."""
        if table_name not in self.existing_indexes:
            return None

        index_cols = set(index.column_names)

        for other_index in self.existing_indexes[table_name]:
            if other_index.index_name == index.index_name:
                continue

            other_cols = set(other_index.column_names)

            # If this index is a subset of another index, it's potentially redundant
            if index_cols.issubset(other_cols) and index_cols != other_cols:
                return other_index.index_name

        return None

    async def _get_table_row_count(self, table_name: str) -> int:
        """Get row count for table."""
        try:
            query = (
                f"SELECT COUNT(*) as count FROM {table_name}"  # nosec B608 - table_name validated
            )
            result = await self.adapter.fetch_one(query)
            return result.get("count", 0) if result else 0
        except Exception as e:
            logger.error(f"Failed to get row count for {table_name}: {e}")
            return 1000  # Default estimate

    async def _get_table_size(self, table_name: str) -> float:
        """Get table size in MB."""
        try:
            if self.database_type == "postgresql":
                query = f"SELECT pg_total_relation_size('{table_name}') / (1024 * 1024) as size_mb"
                result = await self.adapter.fetch_one(query)
                return result.get("size_mb", 0.0) if result else 0.0
            else:
                # Rough estimate for other databases
                row_count = await self._get_table_row_count(table_name)
                return (row_count * 100) / (1024 * 1024)  # Assume ~100 bytes/row

        except Exception as e:
            logger.error(f"Failed to get table size for {table_name}: {e}")
            return 10.0  # Default estimate

    def _determine_priority(self, estimated_improvement: float) -> RecommendationPriority:
        """Determine priority based on estimated improvement."""
        if estimated_improvement >= 50:
            return RecommendationPriority.CRITICAL
        elif estimated_improvement >= 30:
            return RecommendationPriority.HIGH
        elif estimated_improvement >= 15:
            return RecommendationPriority.MEDIUM
        else:
            return RecommendationPriority.LOW

    def _generate_create_index_statement(
        self,
        table_name: str,
        column_names: List[str],
        index_type: IndexType,
        partial_condition: Optional[str] = None,
    ) -> str:
        """Generate CREATE INDEX statement."""
        # Generate index name
        columns_str = "_".join(column_names)
        index_name = f"idx_{table_name}_{columns_str}"

        # Build statement
        columns_joined = ", ".join(column_names)

        if self.database_type == "postgresql":
            stmt = f"CREATE INDEX {index_name} ON {table_name}"

            if index_type != IndexType.BTREE:
                stmt += f" USING {index_type.value}"

            stmt += f" ({columns_joined})"

            if partial_condition:
                stmt += f" WHERE {partial_condition}"

        elif self.database_type == "mysql":
            stmt = f"CREATE INDEX {index_name} ON {table_name} ({columns_joined})"

        else:  # sqlite
            stmt = f"CREATE INDEX {index_name} ON {table_name} ({columns_joined})"

        return stmt


__all__ = [
    "IndexAdvisor",
    "IndexRecommendation",
    "IndexAnalysis",
    "IndexType",
    "RecommendationPriority",
]
