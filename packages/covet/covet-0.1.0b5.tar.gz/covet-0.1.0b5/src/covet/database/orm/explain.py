"""
Query EXPLAIN Plan Analyzer

Executes and analyzes EXPLAIN plans across PostgreSQL, MySQL, and SQLite to identify
performance bottlenecks and optimization opportunities.

Features:
- EXPLAIN and EXPLAIN ANALYZE execution
- Query cost estimation
- Index usage visualization
- Sequential scan detection
- Performance hotspot identification
- Execution time tracking
- Cross-database plan parsing

Example:
    from covet.database.orm.explain import ExplainAnalyzer

    analyzer = ExplainAnalyzer(database_adapter=adapter)

    # Analyze query plan
    plan = await analyzer.explain_query(sql, params)
    print(f"Cost: {plan.estimated_cost}")
    print(f"Uses index: {plan.uses_index}")

    # Analyze with actual execution
    analysis = await analyzer.explain_analyze(sql, params)
    print(f"Actual time: {analysis.actual_time}ms")
    print(f"Rows: {analysis.actual_rows}")
"""

import asyncio
import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class ScanType(Enum):
    """Type of table scan used."""

    SEQUENTIAL = "seq_scan"  # Full table scan
    INDEX = "index_scan"  # Index scan
    INDEX_ONLY = "index_only_scan"  # Index-only scan
    BITMAP = "bitmap_scan"  # Bitmap index scan
    PRIMARY_KEY = "primary_key"  # Primary key lookup


class JoinType(Enum):
    """Type of JOIN algorithm used."""

    NESTED_LOOP = "nested_loop"  # Nested loop join
    HASH = "hash"  # Hash join
    MERGE = "merge"  # Merge join
    SEMI = "semi"  # Semi join
    ANTI = "anti"  # Anti join


@dataclass
class ExplainNode:
    """Single node in query execution plan."""

    node_type: str
    operation: str
    table_name: Optional[str] = None
    index_name: Optional[str] = None
    scan_type: Optional[ScanType] = None
    join_type: Optional[JoinType] = None
    estimated_cost: float = 0.0
    estimated_rows: int = 0
    actual_time: Optional[float] = None
    actual_rows: Optional[int] = None
    filter_condition: Optional[str] = None
    children: List["ExplainNode"] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExplainPlan:
    """Complete query execution plan analysis."""

    database_type: str
    sql: str
    root_node: ExplainNode
    total_cost: float
    estimated_rows: int
    uses_index: bool
    index_names: List[str]
    sequential_scans: List[str]  # Tables with seq scans
    warnings: List[str]
    execution_time: Optional[float] = None
    actual_rows: Optional[int] = None
    analyzed_at: datetime = field(default_factory=datetime.now)

    @property
    def has_sequential_scan(self) -> bool:
        """Check if plan includes sequential scans."""
        return len(self.sequential_scans) > 0

    @property
    def cost_per_row(self) -> float:
        """Calculate cost per row."""
        return self.total_cost / max(self.estimated_rows, 1)


class ExplainAnalyzer:
    """
    Query plan analyzer using EXPLAIN.

    Executes EXPLAIN and EXPLAIN ANALYZE commands to understand query performance
    characteristics across different database systems.
    """

    def __init__(self, database_adapter: Any):
        """
        Initialize explain analyzer.

        Args:
            database_adapter: Database adapter (PostgreSQL, MySQL, or SQLite)
        """
        self.adapter = database_adapter
        self.database_type = self._detect_database_type()

        # Statistics
        self.stats = {
            "plans_analyzed": 0,
            "total_time": 0.0,
            "avg_cost": 0.0,
            "sequential_scans_detected": 0,
        }

    async def explain_query(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        verbose: bool = False,
    ) -> ExplainPlan:
        """
        Execute EXPLAIN to analyze query plan.

        Does not execute the actual query - only analyzes the plan.

        Args:
            sql: SQL query to analyze
            params: Query parameters
            verbose: Whether to include verbose output

        Returns:
            ExplainPlan with cost estimates
        """
        start_time = time.time()

        # Build EXPLAIN query
        explain_sql = self._build_explain_query(sql, analyze=False, verbose=verbose)

        # Execute EXPLAIN
        try:
            if self.database_type == "postgresql":
                result = await self.adapter.fetch_one(explain_sql, params)
                plan_data = result.get("QUERY PLAN") if result else []
            elif self.database_type == "mysql":
                result = await self.adapter.fetch_all(explain_sql, params)
                plan_data = result
            else:  # sqlite
                result = await self.adapter.fetch_all(explain_sql, params)
                plan_data = result

        except Exception as e:
            logger.error(f"Failed to execute EXPLAIN: {e}")
            raise

        # Parse plan
        plan = self._parse_plan(plan_data, sql)

        execution_time = time.time() - start_time
        plan.execution_time = execution_time

        # Update statistics
        self.stats["plans_analyzed"] += 1
        self.stats["total_time"] += execution_time
        self.stats["avg_cost"] = (
            self.stats["avg_cost"] * (self.stats["plans_analyzed"] - 1) + plan.total_cost
        ) / self.stats["plans_analyzed"]
        self.stats["sequential_scans_detected"] += len(plan.sequential_scans)

        return plan

    async def explain_analyze(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        verbose: bool = False,
    ) -> ExplainPlan:
        """
        Execute EXPLAIN ANALYZE to get actual execution statistics.

        WARNING: This executes the actual query, including writes!
        Use with caution on production databases.

        Args:
            sql: SQL query to analyze
            params: Query parameters
            verbose: Whether to include verbose output

        Returns:
            ExplainPlan with actual execution statistics
        """
        start_time = time.time()

        # Build EXPLAIN ANALYZE query
        explain_sql = self._build_explain_query(sql, analyze=True, verbose=verbose)

        # Execute EXPLAIN ANALYZE
        try:
            if self.database_type == "postgresql":
                result = await self.adapter.fetch_one(explain_sql, params)
                plan_data = result.get("QUERY PLAN") if result else []
            elif self.database_type == "mysql":
                # MySQL doesn't support EXPLAIN ANALYZE in older versions
                # Fall back to regular EXPLAIN
                result = await self.adapter.fetch_all(explain_sql, params)
                plan_data = result
            else:  # sqlite
                # SQLite has EXPLAIN QUERY PLAN
                result = await self.adapter.fetch_all(explain_sql, params)
                plan_data = result

        except Exception as e:
            logger.error(f"Failed to execute EXPLAIN ANALYZE: {e}")
            raise

        # Parse plan with actual statistics
        plan = self._parse_plan(plan_data, sql, has_actual_stats=True)

        execution_time = time.time() - start_time
        plan.execution_time = execution_time

        # Update statistics
        self.stats["plans_analyzed"] += 1
        self.stats["total_time"] += execution_time

        return plan

    async def compare_queries(
        self,
        queries: List[Tuple[str, str, Optional[List[Any]]]],
    ) -> Dict[str, ExplainPlan]:
        """
        Compare execution plans for multiple queries.

        Args:
            queries: List of (name, sql, params) tuples

        Returns:
            Dictionary mapping query names to their plans
        """
        results = {}

        for name, sql, params in queries:
            plan = await self.explain_query(sql, params)
            results[name] = plan

        return results

    def visualize_plan(self, plan: ExplainPlan) -> str:
        """
        Create text visualization of execution plan.

        Args:
            plan: ExplainPlan to visualize

        Returns:
            Multi-line string visualization
        """
        lines = []
        lines.append(f"Query Plan for: {plan.sql[:80]}...")
        lines.append(f"Database: {plan.database_type}")
        lines.append(f"Total Cost: {plan.total_cost:.2f}")
        lines.append(f"Estimated Rows: {plan.estimated_rows}")
        lines.append(f"Uses Index: {plan.uses_index}")

        if plan.sequential_scans:
            lines.append(f"WARNING: Sequential scans on: {', '.join(plan.sequential_scans)}")

        lines.append("\nExecution Plan Tree:")
        lines.append("-" * 80)
        self._visualize_node(plan.root_node, lines, 0)

        if plan.warnings:
            lines.append("\nWarnings:")
            for warning in plan.warnings:
                lines.append(f"  - {warning}")

        return "\n".join(lines)

    def get_statistics(self) -> Dict[str, Any]:
        """Get analyzer statistics."""
        return self.stats.copy()

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
            logger.warning(f"Unknown adapter type: {adapter_class}, defaulting to postgresql")
            return "postgresql"

    def _build_explain_query(
        self,
        sql: str,
        analyze: bool = False,
        verbose: bool = False,
    ) -> str:
        """Build EXPLAIN query for database type."""
        if self.database_type == "postgresql":
            options = []
            if analyze:
                options.append("ANALYZE")
            if verbose:
                options.append("VERBOSE")
            options.append("FORMAT JSON")

            options_str = ", ".join(options)
            return f"EXPLAIN ({options_str}) {sql}"

        elif self.database_type == "mysql":
            if analyze:
                # MySQL 8.0+ supports EXPLAIN ANALYZE
                return f"EXPLAIN ANALYZE {sql}"
            else:
                return f"EXPLAIN FORMAT=JSON {sql}"

        else:  # sqlite
            return f"EXPLAIN QUERY PLAN {sql}"

    def _parse_plan(
        self,
        plan_data: Any,
        sql: str,
        has_actual_stats: bool = False,
    ) -> ExplainPlan:
        """Parse EXPLAIN output into structured plan."""
        if self.database_type == "postgresql":
            return self._parse_postgresql_plan(plan_data, sql, has_actual_stats)
        elif self.database_type == "mysql":
            return self._parse_mysql_plan(plan_data, sql, has_actual_stats)
        else:  # sqlite
            return self._parse_sqlite_plan(plan_data, sql)

    def _parse_postgresql_plan(
        self,
        plan_data: Any,
        sql: str,
        has_actual_stats: bool = False,
    ) -> ExplainPlan:
        """Parse PostgreSQL EXPLAIN JSON output."""
        try:
            # PostgreSQL returns JSON format
            if isinstance(plan_data, str):
                plan_json = json.loads(plan_data)
            elif isinstance(plan_data, list):
                plan_json = plan_data[0] if plan_data else {}
            else:
                plan_json = plan_data

            # Extract root plan
            plan = plan_json.get("Plan", {})

            # Parse plan tree
            root_node = self._parse_postgresql_node(plan)

            # Extract metadata
            total_cost = plan.get("Total Cost", 0.0)
            estimated_rows = plan.get("Plan Rows", 0)
            actual_time = plan.get("Actual Total Time") if has_actual_stats else None
            actual_rows = plan.get("Actual Rows") if has_actual_stats else None

            # Find index usage
            index_names = self._find_indexes_in_node(root_node)
            uses_index = len(index_names) > 0

            # Find sequential scans
            sequential_scans = self._find_sequential_scans(root_node)

            # Generate warnings
            warnings = []
            if sequential_scans:
                warnings.append(f"Sequential scans detected on: {', '.join(sequential_scans)}")
            if total_cost > 1000:
                warnings.append(f"High query cost: {total_cost:.2f}")

            return ExplainPlan(
                database_type="postgresql",
                sql=sql,
                root_node=root_node,
                total_cost=total_cost,
                estimated_rows=estimated_rows,
                uses_index=uses_index,
                index_names=index_names,
                sequential_scans=sequential_scans,
                warnings=warnings,
                execution_time=actual_time,
                actual_rows=actual_rows,
            )

        except Exception as e:
            logger.error(f"Failed to parse PostgreSQL plan: {e}")
            # Return minimal plan
            return self._create_minimal_plan(sql, "postgresql")

    def _parse_postgresql_node(self, node_data: Dict[str, Any]) -> ExplainNode:
        """Parse a single node from PostgreSQL plan."""
        node_type = node_data.get("Node Type", "Unknown")
        relation_name = node_data.get("Relation Name")
        index_name = node_data.get("Index Name")

        # Determine scan type
        scan_type = None
        if "Seq Scan" in node_type:
            scan_type = ScanType.SEQUENTIAL
        elif "Index Scan" in node_type:
            scan_type = ScanType.INDEX
        elif "Index Only Scan" in node_type:
            scan_type = ScanType.INDEX_ONLY
        elif "Bitmap" in node_type:
            scan_type = ScanType.BITMAP

        # Determine join type
        join_type = None
        if "Nested Loop" in node_type:
            join_type = JoinType.NESTED_LOOP
        elif "Hash Join" in node_type:
            join_type = JoinType.HASH
        elif "Merge Join" in node_type:
            join_type = JoinType.MERGE

        # Create node
        node = ExplainNode(
            node_type=node_type,
            operation=node_data.get("Operation", node_type),
            table_name=relation_name,
            index_name=index_name,
            scan_type=scan_type,
            join_type=join_type,
            estimated_cost=node_data.get("Total Cost", 0.0),
            estimated_rows=node_data.get("Plan Rows", 0),
            actual_time=node_data.get("Actual Total Time"),
            actual_rows=node_data.get("Actual Rows"),
            filter_condition=node_data.get("Filter"),
            metadata=node_data,
        )

        # Parse child nodes
        for child_data in node_data.get("Plans", []):
            child_node = self._parse_postgresql_node(child_data)
            node.children.append(child_node)

        return node

    def _parse_mysql_plan(
        self,
        plan_data: Any,
        sql: str,
        has_actual_stats: bool = False,
    ) -> ExplainPlan:
        """Parse MySQL EXPLAIN output."""
        try:
            # MySQL EXPLAIN returns rows with columns
            if isinstance(plan_data, list) and plan_data:
                first_row = plan_data[0]

                # Extract cost information
                total_cost = first_row.get("filtered", 100.0)
                estimated_rows = first_row.get("rows", 0)

                # Check for index usage
                key = first_row.get("key")
                uses_index = key is not None and key != "NULL"
                index_names = [key] if uses_index else []

                # Check for sequential scans
                table = first_row.get("table", "unknown")
                scan_type_str = first_row.get("type", "")
                sequential_scans = []
                if scan_type_str in ["ALL", "FULL"]:
                    sequential_scans.append(table)

                # Create simplified node
                root_node = ExplainNode(
                    node_type=scan_type_str,
                    operation=scan_type_str,
                    table_name=table,
                    index_name=key,
                    estimated_cost=total_cost,
                    estimated_rows=estimated_rows,
                    metadata=first_row,
                )

                warnings = []
                if sequential_scans:
                    warnings.append(f"Full table scan on: {', '.join(sequential_scans)}")

                return ExplainPlan(
                    database_type="mysql",
                    sql=sql,
                    root_node=root_node,
                    total_cost=total_cost,
                    estimated_rows=estimated_rows,
                    uses_index=uses_index,
                    index_names=index_names,
                    sequential_scans=sequential_scans,
                    warnings=warnings,
                )

        except Exception as e:
            logger.error(f"Failed to parse MySQL plan: {e}")

        return self._create_minimal_plan(sql, "mysql")

    def _parse_sqlite_plan(
        self,
        plan_data: Any,
        sql: str,
    ) -> ExplainPlan:
        """Parse SQLite EXPLAIN QUERY PLAN output."""
        try:
            # SQLite returns simple text rows
            if isinstance(plan_data, list):
                # Look for index usage
                uses_index = False
                index_names = []
                sequential_scans = []

                for row in plan_data:
                    detail = row.get("detail", "")

                    if "USING INDEX" in detail.upper():
                        uses_index = True
                        # Extract index name
                        match = re.search(r"USING INDEX (\w+)", detail, re.IGNORECASE)
                        if match:
                            index_names.append(match.group(1))

                    if "SCAN TABLE" in detail.upper():
                        # Extract table name
                        match = re.search(r"SCAN TABLE (\w+)", detail, re.IGNORECASE)
                        if match:
                            sequential_scans.append(match.group(1))

                # Create simplified node
                root_node = ExplainNode(
                    node_type="SQLite Plan",
                    operation="query",
                    estimated_cost=10.0 if sequential_scans else 1.0,
                    estimated_rows=100,
                    metadata={"plan_rows": plan_data},
                )

                warnings = []
                if sequential_scans:
                    warnings.append(f"Table scan on: {', '.join(sequential_scans)}")

                return ExplainPlan(
                    database_type="sqlite",
                    sql=sql,
                    root_node=root_node,
                    total_cost=10.0 if sequential_scans else 1.0,
                    estimated_rows=100,
                    uses_index=uses_index,
                    index_names=index_names,
                    sequential_scans=sequential_scans,
                    warnings=warnings,
                )

        except Exception as e:
            logger.error(f"Failed to parse SQLite plan: {e}")

        return self._create_minimal_plan(sql, "sqlite")

    def _create_minimal_plan(self, sql: str, database_type: str) -> ExplainPlan:
        """Create minimal plan when parsing fails."""
        root_node = ExplainNode(
            node_type="Unknown",
            operation="unknown",
            estimated_cost=0.0,
            estimated_rows=0,
        )

        return ExplainPlan(
            database_type=database_type,
            sql=sql,
            root_node=root_node,
            total_cost=0.0,
            estimated_rows=0,
            uses_index=False,
            index_names=[],
            sequential_scans=[],
            warnings=["Failed to parse execution plan"],
        )

    def _find_indexes_in_node(self, node: ExplainNode) -> List[str]:
        """Find all index names used in plan tree."""
        indexes = []

        if node.index_name:
            indexes.append(node.index_name)

        for child in node.children:
            indexes.extend(self._find_indexes_in_node(child))

        return list(set(indexes))

    def _find_sequential_scans(self, node: ExplainNode) -> List[str]:
        """Find all tables with sequential scans."""
        tables = []

        if node.scan_type == ScanType.SEQUENTIAL and node.table_name:
            tables.append(node.table_name)

        for child in node.children:
            tables.extend(self._find_sequential_scans(child))

        return list(set(tables))

    def _visualize_node(
        self,
        node: ExplainNode,
        lines: List[str],
        depth: int,
    ) -> None:
        """Recursively visualize plan node tree."""
        indent = "  " * depth
        prefix = "└─ " if depth > 0 else ""

        # Build node description
        parts = [node.node_type]

        if node.table_name:
            parts.append(f"on {node.table_name}")

        if node.index_name:
            parts.append(f"using {node.index_name}")

        description = " ".join(parts)

        # Add cost information
        cost_info = f"cost={node.estimated_cost:.2f}, rows={node.estimated_rows}"

        if node.actual_time is not None:
            cost_info += f", actual_time={node.actual_time:.2f}ms"

        if node.actual_rows is not None:
            cost_info += f", actual_rows={node.actual_rows}"

        line = f"{indent}{prefix}{description} ({cost_info})"
        lines.append(line)

        # Visualize children
        for child in node.children:
            self._visualize_node(child, lines, depth + 1)


__all__ = [
    "ExplainAnalyzer",
    "ExplainPlan",
    "ExplainNode",
    "ScanType",
    "JoinType",
]
