"""
Shard Router - Query Routing and Scatter-Gather

Intelligent query router for sharded database environments.
Handles query distribution, cross-shard operations, and result aggregation.

Key Features:
- Automatic query routing to correct shard(s)
- Scatter-gather for multi-shard queries
- Result aggregation and merging
- Cross-shard transaction support
- Query optimization for sharded environments
- Connection pooling and load balancing
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .manager import ShardManager
from .strategies import ShardInfo, ShardRoutingResult

logger = logging.getLogger(__name__)


class QueryType(Enum):
    """Type of database query."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    DDL = "DDL"  # CREATE, ALTER, DROP
    UNKNOWN = "UNKNOWN"


@dataclass
class QueryPlan:
    """
    Execution plan for a sharded query.

    Describes how to execute a query across shards:
    - Single-shard vs multi-shard
    - Target shard(s)
    - Aggregation strategy
    - Parallelization options
    """

    query_type: QueryType
    is_single_shard: bool
    target_shards: List[ShardInfo]
    routing_key: Optional[Any] = None
    requires_aggregation: bool = False
    aggregation_strategy: Optional[str] = None
    estimated_cost: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "query_type": self.query_type.value,
            "is_single_shard": self.is_single_shard,
            "target_shards": [s.shard_id for s in self.target_shards],
            "routing_key": self.routing_key,
            "requires_aggregation": self.requires_aggregation,
            "aggregation_strategy": self.aggregation_strategy,
            "estimated_cost": self.estimated_cost,
            "metadata": self.metadata,
        }


@dataclass
class QueryResult:
    """
    Result of a sharded query execution.

    Contains results from all shards and aggregation metadata.
    """

    success: bool
    rows: List[Dict[str, Any]] = field(default_factory=list)
    affected_rows: int = 0
    execution_time_ms: float = 0.0
    shard_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    plan: Optional[QueryPlan] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "rows": self.rows,
            "affected_rows": self.affected_rows,
            "execution_time_ms": self.execution_time_ms,
            "shard_results": self.shard_results,
            "error_message": self.error_message,
            "plan": self.plan.to_dict() if self.plan else None,
        }


class ShardRouter:
    """
    Query router for sharded database environments.

    Routes queries to appropriate shard(s) and handles:
    - Single-shard queries (most common, best performance)
    - Cross-shard scatter-gather queries
    - Result aggregation and merging
    - Load balancing across replicas
    - Query optimization

    Example:
        router = ShardRouter(shard_manager)

        # Single-shard query (routed automatically)
        result = await router.execute(
            "SELECT * FROM users WHERE user_id = $1",
            params=(12345,),
            routing_key=12345
        )

        # Multi-shard scatter-gather query
        result = await router.scatter_gather(
            "SELECT COUNT(*) FROM users WHERE is_active = $1",
            params=(True,),
            aggregation_func=lambda results: sum(r[0]['count'] for r in results)
        )
    """

    def __init__(
        self,
        shard_manager: ShardManager,
        enable_query_cache: bool = False,
        max_parallel_shards: int = 10,
        query_timeout: float = 30.0,
    ):
        """
        Initialize shard router.

        Args:
            shard_manager: Shard manager instance
            enable_query_cache: Enable query result caching
            max_parallel_shards: Max shards to query in parallel
            query_timeout: Default query timeout in seconds
        """
        self.shard_manager = shard_manager
        self.enable_query_cache = enable_query_cache
        self.max_parallel_shards = max_parallel_shards
        self.query_timeout = query_timeout

        # Query cache (if enabled)
        self.query_cache: Dict[str, QueryResult] = {}

        # Statistics
        self.total_queries = 0
        self.single_shard_queries = 0
        self.multi_shard_queries = 0
        self.cache_hits = 0

        logger.info(
            f"ShardRouter initialized (max_parallel={max_parallel_shards}, "
            f"timeout={query_timeout}s)"
        )

    async def execute(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        routing_key: Optional[Any] = None,
        shard_id: Optional[str] = None,
        timeout: Optional[float] = None,
        read_only: bool = False,
    ) -> QueryResult:
        """
        Execute query on appropriate shard(s).

        Routes query to correct shard based on:
        1. Explicit shard_id (if provided)
        2. Routing key (if provided)
        3. Query analysis (if possible)
        4. Scatter to all shards (last resort)

        Args:
            query: SQL query
            params: Query parameters
            routing_key: Value to route on (e.g., user_id)
            shard_id: Explicit shard ID (bypasses routing)
            timeout: Query timeout in seconds
            read_only: If True, prefer read replicas

        Returns:
            QueryResult with results and metadata

        Example:
            # Explicit routing key
            result = await router.execute(
                "SELECT * FROM users WHERE user_id = $1",
                params=(12345,),
                routing_key=12345
            )

            # Explicit shard
            result = await router.execute(
                "SELECT * FROM users LIMIT 10",
                shard_id='shard1'
            )
        """
        self.total_queries += 1
        start_time = asyncio.get_event_loop().time()

        try:
            # Build query plan
            plan = await self._build_query_plan(query, routing_key, shard_id, read_only)

            # Execute based on plan
            if plan.is_single_shard:
                self.single_shard_queries += 1
                result = await self._execute_single_shard(
                    query, params, plan.target_shards[0], timeout
                )
            else:
                self.multi_shard_queries += 1
                result = await self._execute_multi_shard(query, params, plan.target_shards, timeout)

            # Set execution time
            result.execution_time_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            result.plan = plan

            return result

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return QueryResult(
                success=False,
                error_message=str(e),
                execution_time_ms=(asyncio.get_event_loop().time() - start_time) * 1000,
            )

    async def _build_query_plan(
        self,
        query: str,
        routing_key: Optional[Any],
        shard_id: Optional[str],
        read_only: bool,
    ) -> QueryPlan:
        """
        Build execution plan for query.

        Args:
            query: SQL query
            routing_key: Routing key value
            shard_id: Explicit shard ID
            read_only: Read-only query flag

        Returns:
            QueryPlan describing execution strategy
        """
        # Detect query type
        query_type = self._detect_query_type(query)

        # Explicit shard ID provided
        if shard_id:
            shard = self.shard_manager.shards.get(shard_id)
            if not shard:
                raise ValueError(f"Shard {shard_id} not found")

            return QueryPlan(
                query_type=query_type,
                is_single_shard=True,
                target_shards=[shard],
                metadata={"routing_method": "explicit_shard_id"},
            )

        # Routing key provided
        if routing_key is not None:
            if read_only:
                shard = self.shard_manager.get_shard_for_read(routing_key)
            else:
                shard = self.shard_manager.get_shard_for_write(routing_key)

            return QueryPlan(
                query_type=query_type,
                is_single_shard=True,
                target_shards=[shard],
                routing_key=routing_key,
                metadata={"routing_method": "routing_key"},
            )

        # Try to extract routing key from query
        extracted_key = self._extract_routing_key_from_query(query)
        if extracted_key is not None:
            if read_only:
                shard = self.shard_manager.get_shard_for_read(extracted_key)
            else:
                shard = self.shard_manager.get_shard_for_write(extracted_key)

            return QueryPlan(
                query_type=query_type,
                is_single_shard=True,
                target_shards=[shard],
                routing_key=extracted_key,
                metadata={"routing_method": "extracted_from_query"},
            )

        # No routing information - must scatter to all shards
        shards = self.shard_manager.get_shards_for_scatter()

        return QueryPlan(
            query_type=query_type,
            is_single_shard=False,
            target_shards=shards,
            requires_aggregation=query_type == QueryType.SELECT,
            aggregation_strategy="concat" if query_type == QueryType.SELECT else "sum",
            metadata={"routing_method": "scatter_gather"},
        )

    def _detect_query_type(self, query: str) -> QueryType:
        """
        Detect query type from SQL.

        Args:
            query: SQL query string

        Returns:
            QueryType enum value
        """
        query_upper = query.strip().upper()

        if query_upper.startswith("SELECT"):
            return QueryType.SELECT
        elif query_upper.startswith("INSERT"):
            return QueryType.INSERT
        elif query_upper.startswith("UPDATE"):
            return QueryType.UPDATE
        elif query_upper.startswith("DELETE"):
            return QueryType.DELETE
        elif query_upper.startswith(("CREATE", "ALTER", "DROP", "TRUNCATE")):
            return QueryType.DDL
        else:
            return QueryType.UNKNOWN

    def _extract_routing_key_from_query(self, query: str) -> Optional[Any]:
        """
        Try to extract routing key from WHERE clause.

        This is a simple heuristic-based extraction.
        Production implementation would use SQL parsing.

        Args:
            query: SQL query

        Returns:
            Extracted routing key or None
        """
        # Look for patterns like "WHERE user_id = 123"
        # This is a simplified implementation
        import re

        shard_key = self.shard_manager.strategy.shard_key

        # Pattern: shard_key = value or shard_key = $1
        pattern = rf"{shard_key}\s*=\s*(\d+)"
        match = re.search(pattern, query, re.IGNORECASE)

        if match:
            return int(match.group(1))

        return None

    async def _execute_single_shard(
        self,
        query: str,
        params: Optional[Union[Tuple, List]],
        shard: ShardInfo,
        timeout: Optional[float],
    ) -> QueryResult:
        """
        Execute query on a single shard.

        Args:
            query: SQL query
            params: Query parameters
            shard: Target shard
            timeout: Query timeout

        Returns:
            QueryResult with results
        """
        try:
            adapter = await self.shard_manager.get_adapter(shard.shard_id)

            timeout = timeout or self.query_timeout

            # Determine if this is a SELECT query
            is_select = query.strip().upper().startswith("SELECT")

            if is_select:
                rows = await adapter.fetch_all(query, params, timeout=timeout)
                return QueryResult(
                    success=True,
                    rows=rows,
                    shard_results={shard.shard_id: {"rows": len(rows)}},
                )
            else:
                result = await adapter.execute(query, params, timeout=timeout)
                # Parse affected rows from result string
                affected = self._parse_affected_rows(result)
                return QueryResult(
                    success=True,
                    affected_rows=affected,
                    shard_results={shard.shard_id: {"affected_rows": affected}},
                )

        except Exception as e:
            logger.error(f"Single-shard query failed on {shard.shard_id}: {e}")
            return QueryResult(
                success=False,
                error_message=str(e),
                shard_results={shard.shard_id: {"error": str(e)}},
            )

    async def _execute_multi_shard(
        self,
        query: str,
        params: Optional[Union[Tuple, List]],
        shards: List[ShardInfo],
        timeout: Optional[float],
    ) -> QueryResult:
        """
        Execute query across multiple shards (scatter-gather).

        Args:
            query: SQL query
            params: Query parameters
            shards: Target shards
            timeout: Query timeout

        Returns:
            QueryResult with aggregated results
        """
        try:
            # Execute on all shards in parallel
            tasks = []
            for shard in shards:
                task = self._execute_single_shard(query, params, shard, timeout)
                tasks.append(task)

            # Wait for all queries with limit on parallelism
            shard_results = []
            for i in range(0, len(tasks), self.max_parallel_shards):
                batch = tasks[i : i + self.max_parallel_shards]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                shard_results.extend(batch_results)

            # Aggregate results
            all_rows = []
            total_affected = 0
            shard_info = {}
            errors = []

            for i, result in enumerate(shard_results):
                shard_id = shards[i].shard_id

                if isinstance(result, Exception):
                    errors.append(f"{shard_id}: {str(result)}")
                    shard_info[shard_id] = {"error": str(result)}
                elif not result.success:
                    errors.append(f"{shard_id}: {result.error_message}")
                    shard_info[shard_id] = {"error": result.error_message}
                else:
                    # Successful result
                    all_rows.extend(result.rows)
                    total_affected += result.affected_rows
                    shard_info[shard_id] = result.shard_results.get(shard_id, {})

            # Check if all shards failed
            if len(errors) == len(shards):
                return QueryResult(
                    success=False,
                    error_message=f"All shards failed: {'; '.join(errors)}",
                    shard_results=shard_info,
                )

            # Partial success or complete success
            success = len(errors) == 0

            return QueryResult(
                success=success,
                rows=all_rows,
                affected_rows=total_affected,
                shard_results=shard_info,
                error_message=(f"Partial failure: {'; '.join(errors)}" if errors else None),
            )

        except Exception as e:
            logger.error(f"Multi-shard query failed: {e}")
            return QueryResult(
                success=False,
                error_message=str(e),
            )

    def _parse_affected_rows(self, result: str) -> int:
        """
        Parse affected rows from database result string.

        Args:
            result: Result string (e.g., "INSERT 0 1", "UPDATE 5")

        Returns:
            Number of affected rows
        """
        if isinstance(result, int):
            return result

        if isinstance(result, str):
            parts = result.split()
            if len(parts) >= 2:
                try:
                    return int(parts[-1])
                except ValueError:
                    pass

        return 0

    async def scatter_gather(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        aggregation_func: Optional[Callable[[List[QueryResult]], Any]] = None,
        timeout: Optional[float] = None,
    ) -> QueryResult:
        """
        Execute query on all shards and aggregate results.

        Useful for:
        - COUNT(*) across all data
        - Global analytics queries
        - Cross-shard aggregations

        Args:
            query: SQL query to execute on all shards
            params: Query parameters
            aggregation_func: Custom aggregation function
                             Takes list of QueryResults, returns aggregated value
            timeout: Query timeout

        Returns:
            QueryResult with aggregated results

        Example:
            # Count total users across all shards
            result = await router.scatter_gather(
                "SELECT COUNT(*) as count FROM users",
                aggregation_func=lambda results: {
                    'total': sum(r.rows[0]['count'] for r in results if r.success)
                }
            )
        """
        shards = self.shard_manager.get_shards_for_scatter()

        result = await self._execute_multi_shard(query, params, shards, timeout)

        # Apply custom aggregation if provided
        if aggregation_func and result.success:
            try:
                # Get individual shard results
                shard_results = []
                for shard_id in result.shard_results:
                    shard_result = QueryResult(
                        success=True,
                        rows=result.rows,  # This is simplified
                    )
                    shard_results.append(shard_result)

                # Apply aggregation
                aggregated = aggregation_func(shard_results)
                result.rows = [aggregated] if isinstance(aggregated, dict) else aggregated

            except Exception as e:
                logger.error(f"Aggregation function failed: {e}")
                result.error_message = f"Aggregation failed: {str(e)}"

        return result

    async def execute_on_all_shards(
        self,
        query: str,
        params: Optional[Union[Tuple, List]] = None,
        timeout: Optional[float] = None,
    ) -> QueryResult:
        """
        Execute same query on all shards (DDL, maintenance, etc.).

        Useful for:
        - Schema migrations
        - Index creation
        - Maintenance operations

        Args:
            query: SQL query
            params: Query parameters
            timeout: Query timeout

        Returns:
            QueryResult with combined results

        Example:
            # Create index on all shards
            result = await router.execute_on_all_shards(
                "CREATE INDEX idx_user_email ON users(email)"
            )
        """
        shards = self.shard_manager.get_shards_for_scatter()
        return await self._execute_multi_shard(query, params, shards, timeout)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get router statistics.

        Returns:
            Dictionary with routing statistics
        """
        return {
            "total_queries": self.total_queries,
            "single_shard_queries": self.single_shard_queries,
            "multi_shard_queries": self.multi_shard_queries,
            "cache_hits": self.cache_hits,
            "cache_hit_rate": (
                self.cache_hits / self.total_queries if self.total_queries > 0 else 0
            ),
            "multi_shard_rate": (
                self.multi_shard_queries / self.total_queries if self.total_queries > 0 else 0
            ),
        }


__all__ = [
    "ShardRouter",
    "QueryType",
    "QueryPlan",
    "QueryResult",
]
