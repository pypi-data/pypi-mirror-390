"""
Common Table Expressions (CTE) Support

Provides comprehensive CTE functionality including:
- Basic CTEs (WITH clause)
- Multiple CTEs in a single query
- Recursive CTEs for hierarchical data
- LATERAL joins support
- CTE chaining and composition

Supports PostgreSQL 8.4+, MySQL 8.0+, and SQLite 3.8.3+
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Union

from ..core.database_config import DatabaseType

if TYPE_CHECKING:
    from .builder import QueryBuilder


@dataclass
class CTE:
    """
    Represents a single Common Table Expression.

    Attributes:
        name: CTE alias name
        query_builder: QueryBuilder instance for the CTE query
        columns: Optional column list
        recursive: Whether this is a recursive CTE
        materialized: Force materialization (PostgreSQL 12+)
    """

    name: str
    query_builder: "QueryBuilder"
    columns: Optional[List[str]] = None
    recursive: bool = False
    materialized: Optional[bool] = (
        None  # None = default, True = MATERIALIZED, False = NOT MATERIALIZED
    )

    def compile(self, db_type: DatabaseType) -> tuple[str, List[Any]]:
        """
        Compile CTE to SQL.

        Args:
            db_type: Target database type

        Returns:
            Tuple of (SQL string, parameters list)
        """
        parts = []

        # CTE name
        if db_type == DatabaseType.POSTGRESQL:
            cte_name = f'"{self.name}"'
        else:
            cte_name = f"`{self.name}`"

        parts.append(cte_name)

        # Column list (optional)
        if self.columns:
            if db_type == DatabaseType.POSTGRESQL:
                quoted_cols = [f'"{col}"' for col in self.columns]
            else:
                quoted_cols = [f"`{col}`" for col in self.columns]
            parts.append(f"({', '.join(quoted_cols)})")

        # Materialization hint (PostgreSQL 12+)
        if self.materialized is not None and db_type == DatabaseType.POSTGRESQL:
            if self.materialized:
                parts.append("AS MATERIALIZED")
            else:
                parts.append("AS NOT MATERIALIZED")
        else:
            parts.append("AS")

        # Compile subquery
        query = self.query_builder.compile()
        parts.append(f"({query.sql})")

        return " ".join(parts), query.parameters

    def __repr__(self) -> str:
        return f"CTE('{self.name}', recursive={self.recursive})"


@dataclass
class RecursiveCTE(CTE):
    """
    Represents a Recursive Common Table Expression.

    Used for hierarchical queries, tree traversal, and graph operations.

    Example:
        # Employee hierarchy
        base_query = QueryBuilder('employees').where('manager_id', 'IS NULL')
        recursive_query = QueryBuilder('employees')
            .join('employee_hierarchy', 'employees.manager_id = employee_hierarchy.id')

        cte = RecursiveCTE('employee_hierarchy', base_query, recursive_query)
    """

    recursive_query: Optional["QueryBuilder"] = None

    def __init__(
        self,
        name: str,
        base_query: "QueryBuilder",
        recursive_query: Optional["QueryBuilder"] = None,
        columns: Optional[List[str]] = None,
        materialized: Optional[bool] = None,
    ):
        """
        Initialize recursive CTE.

        Args:
            name: CTE alias name
            base_query: Base (anchor) query
            recursive_query: Recursive query (references the CTE)
            columns: Optional column list
            materialized: Force materialization
        """
        super().__init__(
            name=name,
            query_builder=base_query,
            columns=columns,
            recursive=True,
            materialized=materialized,
        )
        self.recursive_query = recursive_query

    def compile(self, db_type: DatabaseType) -> tuple[str, List[Any]]:
        """
        Compile recursive CTE to SQL.

        Args:
            db_type: Target database type

        Returns:
            Tuple of (SQL string, parameters list)

        Raises:
            ValueError: If recursive_query is not provided
        """
        if not self.recursive_query:
            raise ValueError(f"Recursive CTE '{self.name}' requires a recursive_query")

        parts = []
        all_params = []

        # CTE name
        if db_type == DatabaseType.POSTGRESQL:
            cte_name = f'"{self.name}"'
        else:
            cte_name = f"`{self.name}`"

        parts.append(cte_name)

        # Column list (optional but recommended for recursive CTEs)
        if self.columns:
            if db_type == DatabaseType.POSTGRESQL:
                quoted_cols = [f'"{col}"' for col in self.columns]
            else:
                quoted_cols = [f"`{col}`" for col in self.columns]
            parts.append(f"({', '.join(quoted_cols)})")

        parts.append("AS")

        # Open CTE definition
        parts.append("(")

        # Base query
        base_query = self.query_builder.compile()
        parts.append(base_query.sql)
        all_params.extend(base_query.parameters)

        # UNION ALL
        parts.append("UNION ALL")

        # Recursive query
        recursive_query = self.recursive_query.compile()
        parts.append(recursive_query.sql)
        all_params.extend(recursive_query.parameters)

        # Close CTE definition
        parts.append(")")

        return " ".join(parts), all_params


class CTEBuilder:
    """
    Builder for managing multiple CTEs in a query.

    Handles CTE composition, dependency tracking, and SQL generation.
    """

    def __init__(self, db_type: DatabaseType = DatabaseType.POSTGRESQL):
        """
        Initialize CTE builder.

        Args:
            db_type: Target database type
        """
        self.db_type = db_type
        self.ctes: List[CTE] = []
        self.has_recursive = False

    def add_cte(
        self,
        name: str,
        query_builder: "QueryBuilder",
        columns: Optional[List[str]] = None,
        materialized: Optional[bool] = None,
    ) -> "CTEBuilder":
        """
        Add a simple CTE.

        Args:
            name: CTE alias name
            query_builder: QueryBuilder instance
            columns: Optional column list
            materialized: Force materialization

        Returns:
            Self for chaining
        """
        cte = CTE(
            name=name, query_builder=query_builder, columns=columns, materialized=materialized
        )
        self.ctes.append(cte)
        return self

    def add_recursive_cte(
        self,
        name: str,
        base_query: "QueryBuilder",
        recursive_query: "QueryBuilder",
        columns: Optional[List[str]] = None,
        materialized: Optional[bool] = None,
    ) -> "CTEBuilder":
        """
        Add a recursive CTE.

        Args:
            name: CTE alias name
            base_query: Base (anchor) query
            recursive_query: Recursive query
            columns: Optional column list
            materialized: Force materialization

        Returns:
            Self for chaining
        """
        cte = RecursiveCTE(
            name=name,
            base_query=base_query,
            recursive_query=recursive_query,
            columns=columns,
            materialized=materialized,
        )
        self.ctes.append(cte)
        self.has_recursive = True
        return self

    def compile(self) -> tuple[str, List[Any]]:
        """
        Compile all CTEs to SQL WITH clause.

        Returns:
            Tuple of (WITH clause SQL, all parameters)

        Raises:
            ValueError: If no CTEs defined
        """
        if not self.ctes:
            raise ValueError("No CTEs defined")

        parts = []
        all_params = []

        # WITH keyword (with RECURSIVE if needed)
        if self.has_recursive:
            parts.append("WITH RECURSIVE")
        else:
            parts.append("WITH")

        # Compile each CTE
        cte_sqls = []
        for cte in self.ctes:
            cte_sql, cte_params = cte.compile(self.db_type)
            cte_sqls.append(cte_sql)
            all_params.extend(cte_params)

        # Join CTEs with commas
        parts.append(",\n".join(cte_sqls))

        return " ".join(parts), all_params

    def clear(self) -> None:
        """Clear all CTEs."""
        self.ctes.clear()
        self.has_recursive = False

    def count(self) -> int:
        """Get number of CTEs."""
        return len(self.ctes)

    def get_cte_names(self) -> List[str]:
        """Get list of all CTE names."""
        return [cte.name for cte in self.ctes]

    def has_cte(self, name: str) -> bool:
        """Check if CTE with given name exists."""
        return name in self.get_cte_names()


class LateralJoin:
    """
    Represents a LATERAL join (PostgreSQL, MySQL 8.0.14+).

    LATERAL joins allow a subquery in the FROM clause to reference
    columns from preceding tables in the same FROM clause.

    Example:
        # Get top 3 orders for each customer
        QueryBuilder('customers')
            .lateral_join(
                'top_orders',
                QueryBuilder('orders')
                    .select('*')
                    .where('customer_id', '=', Field('customers.id'))
                    .order_by('created_at', 'DESC')
                    .limit(3)
            )
    """

    def __init__(self, alias: str, query_builder: "QueryBuilder", join_type: str = "LEFT"):
        """
        Initialize LATERAL join.

        Args:
            alias: Alias for the lateral subquery
            query_builder: QueryBuilder instance
            join_type: Type of join (LEFT, INNER)
        """
        self.alias = alias
        self.query_builder = query_builder
        self.join_type = join_type.upper()

        if self.join_type not in ("LEFT", "INNER"):
            raise ValueError(f"Invalid LATERAL join type: {self.join_type}. Must be LEFT or INNER")

    def compile(self, db_type: DatabaseType) -> tuple[str, List[Any]]:
        """
        Compile LATERAL join to SQL.

        Args:
            db_type: Target database type

        Returns:
            Tuple of (SQL string, parameters)

        Raises:
            ValueError: If database doesn't support LATERAL
        """
        # Check database support
        if db_type == DatabaseType.SQLITE:
            raise ValueError("SQLite does not support LATERAL joins")

        if db_type == DatabaseType.MYSQL:
            # MySQL 8.0.14+ supports LATERAL
            # We assume if they're using MySQL, it's 8.0.14+
            pass

        # Compile subquery
        query = self.query_builder.compile()

        # Quote alias
        if db_type == DatabaseType.POSTGRESQL:
            quoted_alias = f'"{self.alias}"'
        else:
            quoted_alias = f"`{self.alias}`"

        # Build LATERAL join SQL
        sql = f"{self.join_type} JOIN LATERAL ({query.sql}) AS {quoted_alias} ON TRUE"

        return sql, query.parameters

    def __repr__(self) -> str:
        return f"LateralJoin('{self.alias}', type={self.join_type})"


# Helper functions for common CTE patterns


def create_hierarchy_cte(
    table: str,
    id_column: str = "id",
    parent_column: str = "parent_id",
    root_condition: Optional[Dict[str, Any]] = None,
    db_type: DatabaseType = DatabaseType.POSTGRESQL,
) -> RecursiveCTE:
    """
    Create a recursive CTE for hierarchical data traversal.

    Args:
        table: Table name
        id_column: Primary key column
        parent_column: Parent reference column
        root_condition: Condition for root nodes (default: parent IS NULL)
        db_type: Database type

    Returns:
        RecursiveCTE instance

    Example:
        # Categories hierarchy
        cte = create_hierarchy_cte('categories', 'id', 'parent_id')
    """
    from .builder import QueryBuilder

    # Base query: select root nodes
    base_query = QueryBuilder(table, db_type)
    if root_condition:
        base_query.where(root_condition)
    else:
        base_query.where(f"{parent_column} IS NULL")

    # Recursive query: join children to parents
    recursive_query = QueryBuilder(table, db_type)
    recursive_query.join("hierarchy", f"{table}.{parent_column} = hierarchy.{id_column}")

    return RecursiveCTE(name="hierarchy", base_query=base_query, recursive_query=recursive_query)


def create_graph_traversal_cte(
    edge_table: str,
    from_column: str,
    to_column: str,
    start_node: Any,
    db_type: DatabaseType = DatabaseType.POSTGRESQL,
    max_depth: Optional[int] = None,
) -> RecursiveCTE:
    """
    Create a recursive CTE for graph traversal.

    Args:
        edge_table: Table containing edges
        from_column: Source node column
        to_column: Target node column
        start_node: Starting node ID
        db_type: Database type
        max_depth: Maximum traversal depth

    Returns:
        RecursiveCTE instance

    Example:
        # Follow social network connections
        cte = create_graph_traversal_cte(
            'connections', 'user_id', 'friend_id', 123
        )
    """
    from .builder import QueryBuilder

    # Base query: start node
    base_query = QueryBuilder(edge_table, db_type)
    base_query.select(from_column, to_column, "1 AS depth")
    base_query.where({from_column: start_node})

    # Recursive query: follow edges
    recursive_query = QueryBuilder(edge_table, db_type)
    recursive_query.select(
        f"{edge_table}.{from_column}", f"{edge_table}.{to_column}", "path.depth + 1 AS depth"
    )
    recursive_query.join("path", f"{edge_table}.{from_column} = path.{to_column}")

    if max_depth:
        recursive_query.where(f"path.depth < {max_depth}")

    return RecursiveCTE(
        name="path",
        base_query=base_query,
        recursive_query=recursive_query,
        columns=[from_column, to_column, "depth"],
    )


__all__ = [
    "CTE",
    "RecursiveCTE",
    "CTEBuilder",
    "LateralJoin",
    "create_hierarchy_cte",
    "create_graph_traversal_cte",
]
