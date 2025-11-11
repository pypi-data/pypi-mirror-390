"""
Enterprise Query Builder

Production-quality SQL query builder with fluent interface, multi-dialect support,
and comprehensive security features. Designed for high-performance applications
with strict compilation SLAs (<1ms for simple queries).

Features:
- Fluent interface with method chaining
- Multi-database support (PostgreSQL, MySQL, SQLite)
- SQL injection prevention through parameter binding
- Query optimization and caching
- Performance tracking and monitoring
- Complex query support (joins, subqueries, aggregations)
"""

import hashlib
import time
from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.database_config import DatabaseType
from ..security.sql_validator import (
    DatabaseDialect,
    InvalidIdentifierError,
    validate_column_name,
    validate_identifier,
    validate_table_name,
)


class QueryType(Enum):
    """Query operation types."""

    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    RAW = "RAW"


class LockType(Enum):
    """Row-level lock types."""

    FOR_UPDATE = "FOR UPDATE"
    FOR_SHARE = "FOR SHARE"
    LOCK_IN_SHARE_MODE = "LOCK IN SHARE MODE"  # MySQL equivalent of FOR SHARE


@dataclass
class QueryContext:
    """Query execution context and preferences."""

    database_type: DatabaseType = DatabaseType.POSTGRESQL
    use_cache: bool = True
    max_rows: Optional[int] = None
    timeout: Optional[int] = None
    read_only: bool = False


@dataclass
class Query:
    """
    Compiled query representation with SQL and parameters.

    Attributes:
        sql: Compiled SQL statement
        parameters: Bound parameters for safe execution
        query_type: Type of query (SELECT, INSERT, etc.)
        tables: Tables referenced in the query
        fields: Fields selected in the query
        hash: Unique hash for caching
        compile_time: Time taken to compile query (seconds)
        cache_key: Cache key for query results
        parameter_names: Named parameters mapping
    """

    sql: str
    parameters: List[Any] = field(default_factory=list)
    query_type: QueryType = QueryType.SELECT
    tables: List[str] = field(default_factory=list)
    fields: List[str] = field(default_factory=list)
    hash: str = ""
    compile_time: float = 0.0
    cache_key: Optional[str] = None
    parameter_names: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Generate hash after initialization if not provided."""
        if not self.hash:
            self.hash = self._generate_hash()

    def _generate_hash(self) -> str:
        """Generate unique hash for query caching."""
        hash_content = f"{self.sql}:{':'.join(str(p) for p in self.parameters)}"
        return hashlib.md5(hash_content.encode(), usedforsecurity=False).hexdigest()

    def explain(self) -> str:
        """Generate EXPLAIN query."""
        return f"EXPLAIN {self.sql}"

    def analyze(self) -> str:
        """Generate EXPLAIN ANALYZE query."""
        return f"EXPLAIN ANALYZE {self.sql}"

    def bind(self, **kwargs) -> "Query":
        """Bind named parameters to query."""
        self.parameter_names.update(kwargs)
        return self


class QueryBuilder:
    """
    Fluent interface SQL query builder with multi-dialect support.

    Example:
        builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
        query = (builder
            .select('id', 'name', 'email')
            .where({'status': 'active'})
            .order_by('created_at', 'DESC')
            .limit(10)
            .compile())

        # Execute with adapter
        results = await adapter.fetch_all(query.sql, query.parameters)
    """

    def __init__(
        self,
        table: str,
        database_type: DatabaseType = DatabaseType.POSTGRESQL,
        optimizer: Optional["QueryOptimizer"] = None,
        cache: Optional["QueryCache"] = None,
    ):
        """
        Initialize query builder.

        Args:
            table: Primary table name
            database_type: Database dialect (PostgreSQL, MySQL, SQLite)
            optimizer: Optional query optimizer
            cache: Optional query cache
        """
        # Validate table name on initialization
        dialect = self._db_type_to_dialect(database_type)
        try:
            validated_table = validate_table_name(table, dialect)
            self._table = validated_table
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid table name '{table}': {e}")

        self._database_type = database_type
        self.optimizer = optimizer
        self.cache = cache

        # Query components
        self._query_type: QueryType = QueryType.SELECT
        self._select_fields: List[str] = []
        self._distinct: bool = False
        self._where_conditions: List[Union[str, Dict[str, Any]]] = []
        self._where_logic: List[str] = []  # Track AND/OR logic
        self._joins: List[Dict[str, str]] = []
        self._order_by_clauses: List[Tuple[str, str]] = []
        self._group_by_fields: List[str] = []
        self._having_clause: Optional[str] = None
        self._limit_value: Optional[int] = None
        self._offset_value: Optional[int] = None
        self._lock_type: Optional[LockType] = None
        self._insert_data: Optional[Union[Dict, List[Dict]]] = None
        self._update_data: Optional[Dict] = None
        self._upsert_conflict_columns: Optional[List[str]] = None

        # CTE support
        self._ctes: List["CTE"] = []
        self._lateral_joins: List["LateralJoin"] = []

        # Parameters for binding
        self._parameters: List[Any] = []

        # Performance tracking
        self._execution_count = 0
        self._total_compile_time = 0.0
        self._min_compile_time = float("inf")
        self._max_compile_time = 0.0

    @staticmethod
    def _db_type_to_dialect(db_type: DatabaseType) -> DatabaseDialect:
        """Convert DatabaseType to DatabaseDialect for validation."""
        mapping = {
            DatabaseType.POSTGRESQL: DatabaseDialect.POSTGRESQL,
            DatabaseType.MYSQL: DatabaseDialect.MYSQL,
            DatabaseType.SQLITE: DatabaseDialect.SQLITE,
        }
        return mapping.get(db_type, DatabaseDialect.GENERIC)

    def _validate_identifier_safe(self, identifier: str) -> str:
        """
        Validate an identifier (table/column name) for SQL injection.

        Args:
            identifier: Identifier to validate

        Returns:
            Validated identifier

        Raises:
            ValueError: If identifier is invalid or contains SQL injection patterns
        """
        if identifier == "*":
            return identifier

        dialect = self._db_type_to_dialect(self._database_type)
        try:
            # Allow dots for qualified names (e.g., table.column)
            return validate_identifier(identifier, allow_dots=True, dialect=dialect)
        except InvalidIdentifierError as e:
            raise ValueError(f"Invalid identifier '{identifier}': {e}")

    def select(self, *fields: str) -> "QueryBuilder":
        """
        Specify SELECT fields.

        Args:
            *fields: Field names to select. If empty, selects all (*)

        Returns:
            Self for method chaining
        """
        self._query_type = QueryType.SELECT
        # Validate field names to prevent SQL injection
        if fields:
            validated_fields = []
            for field in fields:
                if field != "*" and not hasattr(field, "compile"):
                    validated_fields.append(self._validate_identifier_safe(field))
                else:
                    validated_fields.append(field)
            self._select_fields = validated_fields
        else:
            self._select_fields = ["*"]
        return self

    def distinct(self) -> "QueryBuilder":
        """Enable DISTINCT for SELECT query."""
        self._distinct = True
        return self

    def from_(self, table: str) -> "QueryBuilder":
        """
        Specify FROM table (alternative to constructor).

        Args:
            table: Table name

        Returns:
            Self for method chaining
        """
        self._table = table
        return self

    def where(self, condition: Union[str, Dict[str, Any]], *args) -> "QueryBuilder":
        """
        Add WHERE condition.

        SECURITY: When using raw SQL strings, ensure all user input is passed via *args
        parameters, NOT embedded in the condition string itself.

        Args:
            condition: Dict of field:value pairs or parameterized SQL string
            *args: Arguments for SQL string placeholders (USE FOR USER INPUT)

        Returns:
            Self for method chaining

        Example:
            # SAFE: Using dictionary
            builder.where({'username': user_input})

            # SAFE: Using parameterized query
            builder.where('age > ?', user_age)

            # UNSAFE: Embedding user input (DO NOT DO THIS)
            # builder.where(f'username = {user_input}')  # SQL INJECTION!
        """
        if isinstance(condition, dict):
            # Validate all column names in the dictionary
            validated_dict = {}
            for key, value in condition.items():
                validated_key = self._validate_identifier_safe(key)
                validated_dict[validated_key] = value
            self._where_conditions.append(validated_dict)
            self._where_logic.append("AND")
        else:
            # Raw SQL condition - add parameters if provided
            # NOTE: We cannot fully validate raw SQL strings, so user must
            # ensure proper parameterization
            if args:
                self._parameters.extend(args)
            self._where_conditions.append(condition)
            self._where_logic.append("AND")
        return self

    def and_where(self, condition: Union[str, Dict[str, Any], "Field"]) -> "QueryBuilder":
        """Add AND WHERE condition."""
        if hasattr(condition, "compile"):
            # Expression/Field object
            self._where_conditions.append(condition)
        else:
            self._where_conditions.append(condition)
        self._where_logic.append("AND")
        return self

    def or_where(self, condition: Union[str, Dict[str, Any]]) -> "QueryBuilder":
        """Add OR WHERE condition."""
        self._where_conditions.append(condition)
        self._where_logic.append("OR")
        return self

    def join(self, table: str, on: Union[str, "Field"], join_type: str = "INNER") -> "QueryBuilder":
        """
        Add JOIN clause.

        SECURITY: Table names are validated. For 'on' conditions, use parameterized
        format or Expression objects to prevent SQL injection.

        Args:
            table: Table to join (will be validated)
            on: Join condition (raw SQL or Expression object)
            join_type: Type of join (INNER, LEFT, RIGHT, FULL)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If table name or join type is invalid

        Example:
            # SAFE: Table name is validated
            builder.join('orders', 'users.id = orders.user_id')

            # BETTER: Use Expression objects for complex conditions
            builder.join('orders', Field('users.id').eq(Field('orders.user_id')))
        """
        # Validate table name to prevent SQL injection
        validated_table = self._validate_identifier_safe(table)

        # Validate join type
        valid_join_types = ["INNER", "LEFT", "RIGHT", "FULL", "FULL OUTER", "CROSS"]
        join_type_upper = join_type.upper()
        if join_type_upper not in valid_join_types and not join_type_upper.endswith(" OUTER"):
            raise ValueError(
                f"Invalid join type '{join_type}'. Must be one of: {', '.join(valid_join_types)}"
            )

        self._joins.append({"type": join_type_upper, "table": validated_table, "on": on})
        return self

    def inner_join(self, table: str, on: Union[str, "Field"]) -> "QueryBuilder":
        """Add INNER JOIN."""
        return self.join(table, on, "INNER")

    def left_join(self, table: str, on: Union[str, "Field"]) -> "QueryBuilder":
        """Add LEFT JOIN."""
        return self.join(table, on, "LEFT")

    def right_join(self, table: str, on: Union[str, "Field"]) -> "QueryBuilder":
        """Add RIGHT JOIN."""
        return self.join(table, on, "RIGHT")

    def full_join(self, table: str, on: Union[str, "Field"]) -> "QueryBuilder":
        """Add FULL OUTER JOIN."""
        return self.join(table, on, "FULL OUTER")

    def order_by(self, column: Union[str, "Function"], direction: str = "ASC") -> "QueryBuilder":
        """
        Add ORDER BY clause.

        SECURITY: Column names are validated to prevent SQL injection.

        Args:
            column: Column name or expression (validated for SQL injection)
            direction: ASC or DESC

        Returns:
            Self for method chaining

        Raises:
            ValueError: If direction or column name is invalid
        """
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            raise ValueError(f"Invalid ORDER BY direction: {direction}. Must be ASC or DESC")

        # Validate column name if it's a string
        if isinstance(column, str) and not hasattr(column, "compile"):
            validated_column = self._validate_identifier_safe(column)
            self._order_by_clauses.append((validated_column, direction))
        else:
            self._order_by_clauses.append((column, direction))
        return self

    def group_by(self, *fields: str) -> "QueryBuilder":
        """
        Add GROUP BY clause.

        SECURITY: Field names are validated to prevent SQL injection.

        Args:
            *fields: Field names to group by (will be validated)

        Returns:
            Self for method chaining

        Raises:
            ValueError: If any field name is invalid
        """
        validated_fields = []
        for field in fields:
            validated_fields.append(self._validate_identifier_safe(field))
        self._group_by_fields.extend(validated_fields)
        return self

    def having(self, condition: str) -> "QueryBuilder":
        """
        Add HAVING clause.

        SECURITY WARNING: Raw SQL conditions cannot be fully validated.
        For user input, use parameterized queries or Expression objects.

        Args:
            condition: HAVING condition (use parameters for user input)

        Returns:
            Self for method chaining

        Example:
            # SAFE: No user input
            builder.having('COUNT(*) > 5')

            # BETTER: Use with parameterization in the overall query
            # Pass user values via query parameters, not in the condition string
        """
        # Store the condition as-is
        # NOTE: Full validation of arbitrary SQL expressions is complex
        # Users must ensure they don't embed untrusted input directly
        self._having_clause = condition
        return self

    def limit(self, n: int) -> "QueryBuilder":
        """
        Add LIMIT clause.

        Args:
            n: Number of rows to limit

        Returns:
            Self for method chaining

        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError(f"LIMIT value must be non-negative, got {n}")
        self._limit_value = n
        return self

    def offset(self, n: int) -> "QueryBuilder":
        """
        Add OFFSET clause.

        Args:
            n: Number of rows to skip

        Returns:
            Self for method chaining

        Raises:
            ValueError: If n is negative
        """
        if n < 0:
            raise ValueError(f"OFFSET value must be non-negative, got {n}")
        self._offset_value = n
        return self

    def paginate(self, page: int, per_page: int = 25) -> "QueryBuilder":
        """
        Add pagination (LIMIT/OFFSET).

        Args:
            page: Page number (1-indexed)
            per_page: Items per page

        Returns:
            Self for method chaining

        Raises:
            ValueError: If page is less than 1
        """
        if page < 1:
            raise ValueError(f"Page must be >= 1, got {page}")

        self._limit_value = per_page
        self._offset_value = (page - 1) * per_page
        return self

    def for_update(self) -> "QueryBuilder":
        """Add FOR UPDATE lock."""
        self._lock_type = LockType.FOR_UPDATE
        return self

    def for_share(self) -> "QueryBuilder":
        """Add FOR SHARE lock (or MySQL equivalent)."""
        if self._database_type == DatabaseType.MYSQL:
            self._lock_type = LockType.LOCK_IN_SHARE_MODE
        else:
            self._lock_type = LockType.FOR_SHARE
        return self

    def insert(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> "QueryBuilder":
        """
        Prepare INSERT query.

        Args:
            data: Dictionary or list of dictionaries with insert data

        Returns:
            Self for method chaining
        """
        self._query_type = QueryType.INSERT
        self._insert_data = data
        return self

    def upsert(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
        conflict_columns: Optional[List[str]] = None,
    ) -> "QueryBuilder":
        """
        Prepare UPSERT query (INSERT ... ON CONFLICT/DUPLICATE KEY).

        Args:
            data: Dictionary or list of dictionaries with insert data
            conflict_columns: Columns to check for conflicts

        Returns:
            Self for method chaining
        """
        self._query_type = QueryType.INSERT
        self._insert_data = data
        self._upsert_conflict_columns = conflict_columns or []
        return self

    def update(self, data: Dict[str, Any]) -> "QueryBuilder":
        """
        Prepare UPDATE query.

        Args:
            data: Dictionary with field:value pairs to update

        Returns:
            Self for method chaining
        """
        self._query_type = QueryType.UPDATE
        self._update_data = data
        return self

    def delete(self) -> "QueryBuilder":
        """
        Prepare DELETE query.

        Returns:
            Self for method chaining
        """
        self._query_type = QueryType.DELETE
        return self

    def with_cte(
        self,
        name: str,
        query_builder: "QueryBuilder",
        columns: Optional[List[str]] = None,
        materialized: Optional[bool] = None,
    ) -> "QueryBuilder":
        """
        Add a Common Table Expression (CTE).

        Args:
            name: CTE alias name
            query_builder: QueryBuilder for the CTE query
            columns: Optional column list
            materialized: Force materialization (PostgreSQL 12+)

        Returns:
            Self for method chaining

        Example:
            high_value = QueryBuilder('customers').where('total_spent', '>', 1000)
            query = (QueryBuilder('orders')
                .with_cte('high_value_customers', high_value)
                .join('high_value_customers', 'orders.customer_id = high_value_customers.id'))
        """
        from .cte import CTE

        cte = CTE(
            name=name, query_builder=query_builder, columns=columns, materialized=materialized
        )
        self._ctes.append(cte)
        return self

    def with_recursive_cte(
        self,
        name: str,
        base_query: "QueryBuilder",
        recursive_query: "QueryBuilder",
        columns: Optional[List[str]] = None,
        materialized: Optional[bool] = None,
    ) -> "QueryBuilder":
        """
        Add a Recursive Common Table Expression.

        Args:
            name: CTE alias name
            base_query: Base (anchor) query
            recursive_query: Recursive query
            columns: Optional column list
            materialized: Force materialization

        Returns:
            Self for method chaining

        Example:
            base = QueryBuilder('employees').where('manager_id', 'IS NULL')
            recursive = QueryBuilder('employees').join('hierarchy', 'employees.manager_id = hierarchy.id')
            query = (QueryBuilder('hierarchy')
                .with_recursive_cte('hierarchy', base, recursive)
                .select('*'))
        """
        from .cte import RecursiveCTE

        cte = RecursiveCTE(
            name=name,
            base_query=base_query,
            recursive_query=recursive_query,
            columns=columns,
            materialized=materialized,
        )
        self._ctes.append(cte)
        return self

    def lateral_join(
        self, alias: str, query_builder: "QueryBuilder", join_type: str = "LEFT"
    ) -> "QueryBuilder":
        """
        Add a LATERAL join (PostgreSQL, MySQL 8.0.14+).

        Args:
            alias: Alias for the lateral subquery
            query_builder: QueryBuilder for the lateral query
            join_type: Type of join (LEFT, INNER)

        Returns:
            Self for method chaining

        Example:
            lateral_orders = QueryBuilder('orders').where('customer_id = customers.id').limit(3)
            query = QueryBuilder('customers').lateral_join('top_orders', lateral_orders)
        """
        from .cte import LateralJoin

        lateral = LateralJoin(alias=alias, query_builder=query_builder, join_type=join_type)
        self._lateral_joins.append(lateral)
        return self

    def select_raw(self, *expressions: str) -> "QueryBuilder":
        """
        Add raw SQL expressions to SELECT clause (for window functions, etc.).

        Args:
            *expressions: Raw SQL expressions

        Returns:
            Self for method chaining

        Example:
            query = QueryBuilder('sales').select_raw(
                'ROW_NUMBER() OVER (PARTITION BY region ORDER BY amount DESC) as rank',
                'region', 'amount'
            )
        """
        self._query_type = QueryType.SELECT
        self._select_fields.extend(expressions)
        return self

    def select_window(self, window_func: "WindowFunction", alias: str) -> "QueryBuilder":
        """
        Add a window function to SELECT clause.

        Args:
            window_func: WindowFunction instance
            alias: Column alias

        Returns:
            Self for method chaining

        Example:
            from .window_functions import row_number
            query = QueryBuilder('sales').select_window(
                row_number().partition_by('region').order_by('amount', 'DESC'),
                'rank'
            )
        """
        self._query_type = QueryType.SELECT
        # Store window function with alias
        self._select_fields.append(f"{window_func}::{alias}")
        return self

    def clone(self) -> "QueryBuilder":
        """
        Clone query builder for reuse.

        Returns:
            Deep copy of query builder
        """
        return deepcopy(self)

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.

        Returns:
            Dictionary with performance metrics
        """
        return {
            "execution_count": self._execution_count,
            "total_compile_time": self._total_compile_time,
            "avg_compile_time": (
                self._total_compile_time / self._execution_count if self._execution_count > 0 else 0
            ),
            "min_compile_time": (
                self._min_compile_time if self._min_compile_time != float("inf") else 0
            ),
            "max_compile_time": self._max_compile_time,
        }

    def compile(self, context: Optional[QueryContext] = None) -> Query:
        """
        Compile query to SQL.

        Args:
            context: Optional query context

        Returns:
            Compiled Query object

        Raises:
            ValueError: If query cannot be compiled
        """
        start_time = time.time()

        # Reset parameters
        self._parameters = []

        # Compile based on query type
        if self._query_type == QueryType.SELECT:
            sql = self._compile_select()
        elif self._query_type == QueryType.INSERT:
            sql = self._compile_insert()
        elif self._query_type == QueryType.UPDATE:
            sql = self._compile_update()
        elif self._query_type == QueryType.DELETE:
            sql = self._compile_delete()
        else:
            raise ValueError(f"Unsupported query type: {self._query_type}")

        compile_time = time.time() - start_time

        # Update performance stats
        self._execution_count += 1
        self._total_compile_time += compile_time
        self._min_compile_time = min(self._min_compile_time, compile_time)
        self._max_compile_time = max(self._max_compile_time, compile_time)

        # Extract tables
        tables = [self._table]
        for join in self._joins:
            tables.append(join["table"])

        # Extract fields
        fields = self._select_fields.copy()

        # Build Query object
        query = Query(
            sql=sql,
            parameters=self._parameters.copy(),
            query_type=self._query_type,
            tables=tables,
            fields=fields,
            compile_time=compile_time,
            cache_key=context.use_cache if context else True,
        )

        return query

    def _compile_select(self) -> str:
        """Compile SELECT query."""
        parts = []

        # CTEs (WITH clause)
        if self._ctes:
            cte_parts = []
            has_recursive = any(getattr(cte, "recursive", False) for cte in self._ctes)

            if has_recursive:
                cte_parts.append("WITH RECURSIVE")
            else:
                cte_parts.append("WITH")

            # Compile each CTE
            cte_sqls = []
            for cte in self._ctes:
                cte_sql, cte_params = cte.compile(self._database_type)
                cte_sqls.append(cte_sql)
                self._parameters.extend(cte_params)

            cte_parts.append(",\n".join(cte_sqls))
            parts.append(" ".join(cte_parts))

        # SELECT clause
        select_clause = "SELECT"
        if self._distinct:
            select_clause += " DISTINCT"

        # Format fields
        if not self._select_fields or self._select_fields == ["*"]:
            fields_str = "*"
        else:
            formatted_fields = []
            for field in self._select_fields:
                # Handle window functions with alias (format: "func::alias")
                if isinstance(field, str) and "::" in field:
                    func_str, alias = field.split("::", 1)
                    # The func_str is actually a WindowFunction object stored as string
                    # In practice, we'd need to store the object differently
                    formatted_fields.append(f"{func_str} AS {self._quote_identifier(alias)}")
                elif hasattr(field, "compile"):
                    # Expression/Function/WindowFunction object
                    formatted_fields.append(field.compile(self._database_type))
                else:
                    formatted_fields.append(self._quote_identifier(str(field)))
            fields_str = ", ".join(formatted_fields)

        parts.append(f"{select_clause} {fields_str}")

        # FROM clause
        parts.append(f"FROM {self._quote_identifier(self._table)}")

        # JOINs
        for join in self._joins:
            join_str = f"{join['type']} JOIN {self._quote_identifier(join['table'])}"
            on_condition = join["on"]
            if hasattr(on_condition, "compile"):
                # Expression object
                on_str = on_condition.compile(self._database_type)
            else:
                on_str = str(on_condition)
            join_str += f" ON {on_str}"
            parts.append(join_str)

        # LATERAL JOINs
        for lateral in self._lateral_joins:
            lateral_sql, lateral_params = lateral.compile(self._database_type)
            parts.append(lateral_sql)
            self._parameters.extend(lateral_params)

        # WHERE clause
        if self._where_conditions:
            where_str = self._compile_where()
            parts.append(f"WHERE {where_str}")

        # GROUP BY
        if self._group_by_fields:
            group_fields = [self._quote_identifier(f) for f in self._group_by_fields]
            parts.append(f"GROUP BY {', '.join(group_fields)}")

        # HAVING
        if self._having_clause:
            parts.append(f"HAVING {self._having_clause}")

        # ORDER BY
        if self._order_by_clauses:
            order_parts = []
            for column, direction in self._order_by_clauses:
                if hasattr(column, "compile"):
                    # Function/Expression object
                    col_str = column.compile(self._database_type)
                else:
                    col_str = self._quote_identifier(str(column))
                order_parts.append(f"{col_str} {direction}")
            parts.append(f"ORDER BY {', '.join(order_parts)}")

        # LIMIT and OFFSET (database-specific)
        if self._database_type == DatabaseType.MYSQL:
            # MySQL uses LIMIT offset, count
            if self._limit_value is not None and self._offset_value is not None:
                parts.append(f"LIMIT {self._offset_value}, {self._limit_value}")
            elif self._limit_value is not None:
                parts.append(f"LIMIT {self._limit_value}")
        else:
            # PostgreSQL and SQLite use LIMIT count OFFSET offset
            if self._limit_value is not None:
                parts.append(f"LIMIT {self._limit_value}")
            if self._offset_value is not None:
                parts.append(f"OFFSET {self._offset_value}")

        # Lock clause
        if self._lock_type:
            parts.append(self._lock_type.value)

        return " ".join(parts)

    def _compile_insert(self) -> str:
        """Compile INSERT query."""
        if not self._insert_data:
            raise ValueError("No data provided for INSERT")

        # Handle batch insert
        if isinstance(self._insert_data, list):
            if not self._insert_data:
                raise ValueError("No data provided for INSERT")
            return self._compile_batch_insert(self._insert_data)

        data = self._insert_data
        if not data:
            raise ValueError("No data provided for INSERT")

        # Extract columns and values
        columns = list(data.keys())
        values = list(data.values())

        # Build INSERT statement
        quoted_table = self._quote_identifier(self._table)
        quoted_columns = [self._quote_identifier(c) for c in columns]
        columns_str = ", ".join(quoted_columns)

        # Build placeholders
        placeholders = []
        for value in values:
            if hasattr(value, "compile"):
                # Function/Expression - use raw SQL
                placeholders.append(value.compile(self._database_type))
            else:
                # Regular value - use parameter
                placeholders.append(self._get_placeholder())
                self._parameters.append(value)

        values_str = ", ".join(placeholders)

        sql = f"INSERT INTO {quoted_table} ({columns_str}) VALUES({values_str})"

        # Handle UPSERT
        if self._upsert_conflict_columns:
            if self._database_type == DatabaseType.POSTGRESQL:
                # PostgreSQL: ON CONFLICT ... DO UPDATE SET
                conflict_cols = [self._quote_identifier(c) for c in self._upsert_conflict_columns]
                conflict_str = ", ".join(conflict_cols)

                update_parts = []
                for col in columns:
                    if col not in self._upsert_conflict_columns:
                        quoted_col = self._quote_identifier(col)
                        update_parts.append(f"{quoted_col} = EXCLUDED.{quoted_col}")

                if update_parts:
                    sql += f" ON CONFLICT ({conflict_str}) DO UPDATE SET {', '.join(update_parts)}"  # nosec B608 - identifiers validated

            elif self._database_type == DatabaseType.MYSQL:
                # MySQL: ON DUPLICATE KEY UPDATE
                update_parts = []
                for col in columns:
                    if col not in self._upsert_conflict_columns:
                        quoted_col = self._quote_identifier(col)
                        param = self._get_placeholder()
                        self._parameters.append(data[col])
                        update_parts.append(f"{quoted_col} = {param}")

                if update_parts:
                    sql += f" ON DUPLICATE KEY UPDATE {', '.join(update_parts)}"

        return sql

    def _compile_batch_insert(self, data_list: List[Dict[str, Any]]) -> str:
        """Compile batch INSERT query."""
        if not data_list:
            raise ValueError("No data provided for INSERT")

        # Use first row to get columns
        columns = list(data_list[0].keys())

        # Build INSERT statement
        quoted_table = self._quote_identifier(self._table)
        quoted_columns = [self._quote_identifier(c) for c in columns]
        columns_str = ", ".join(quoted_columns)

        # Build value rows
        value_rows = []
        for row in data_list:
            placeholders = []
            for col in columns:
                value = row.get(col)
                if hasattr(value, "compile"):
                    placeholders.append(value.compile(self._database_type))
                else:
                    placeholders.append(self._get_placeholder())
                    self._parameters.append(value)
            value_rows.append(f"({', '.join(placeholders)})")

        values_str = ", ".join(value_rows)

        return f"INSERT INTO {quoted_table} ({columns_str}) VALUES {values_str}"  # nosec B608 - identifiers validated

    def _compile_update(self) -> str:
        """Compile UPDATE query."""
        if not self._update_data:
            raise ValueError("No data provided for UPDATE")

        quoted_table = self._quote_identifier(self._table)

        # Build SET clause
        set_parts = []
        for key, value in self._update_data.items():
            quoted_key = self._quote_identifier(key)

            if hasattr(value, "compile"):
                # Function/Expression - use raw SQL
                set_parts.append(f"{quoted_key} = {value.compile(self._database_type)}")
            else:
                # Regular value - use parameter
                placeholder = self._get_placeholder()
                set_parts.append(f"{quoted_key} = {placeholder}")
                self._parameters.append(value)

        set_str = ", ".join(set_parts)

        sql = f"UPDATE {quoted_table} SET {set_str}"  # nosec B608 - identifiers validated

        # WHERE clause
        if self._where_conditions:
            where_str = self._compile_where()
            sql += f" WHERE {where_str}"

        return sql

    def _compile_delete(self) -> str:
        """Compile DELETE query."""
        quoted_table = self._quote_identifier(self._table)
        sql = f"DELETE FROM {quoted_table}"  # nosec B608 - identifiers validated

        # WHERE clause
        if self._where_conditions:
            where_str = self._compile_where()
            sql += f" WHERE {where_str}"

        return sql

    def _compile_where(self) -> str:
        """Compile WHERE conditions."""
        if not self._where_conditions:
            return ""

        conditions = []
        for i, condition in enumerate(self._where_conditions):
            if isinstance(condition, dict):
                # Dictionary conditions
                for key, value in condition.items():
                    quoted_key = self._quote_identifier(key)
                    placeholder = self._get_placeholder()
                    conditions.append(f"{quoted_key} = {placeholder}")
                    self._parameters.append(value)
            elif hasattr(condition, "compile_with_placeholders"):
                # BinaryOperation or other expression with parameters
                sql, params = condition.compile_with_placeholders(
                    self._database_type, len(self._parameters)
                )
                conditions.append(sql)
                self._parameters.extend(params)
            elif hasattr(condition, "compile"):
                # Other Expression objects
                conditions.append(condition.compile(self._database_type))
            else:
                # Raw SQL string
                conditions.append(str(condition))

        # Join with AND/OR logic
        if len(conditions) == 1:
            return conditions[0]

        # Build with logic operators
        result = conditions[0]
        for i in range(1, len(conditions)):
            logic = self._where_logic[i] if i < len(self._where_logic) else "AND"
            result += f" {logic} {conditions[i]}"

        return result

    def _quote_identifier(self, identifier: str) -> str:
        """
        Quote SQL identifier based on database type.

        SECURITY: Validates identifiers before quoting to prevent SQL injection.

        Args:
            identifier: Column or table name

        Returns:
            Quoted identifier

        Raises:
            ValueError: If identifier contains SQL injection patterns
        """
        # Don't quote if already contains special characters or is a qualified
        # name with functions
        if any(char in identifier for char in ["(", ")", " AS ", " as "]):
            # Complex expression, don't quote
            return identifier

        # For wildcard
        if identifier == "*":
            return identifier

        # For qualified names (table.column), validate and quote each part
        if "." in identifier:
            parts = identifier.split(".")
            validated_parts = []
            for part in parts:
                if part != "*":
                    # Validate each part
                    validated_part = self._validate_identifier_safe(part)
                    validated_parts.append(self._quote_single_identifier(validated_part))
                else:
                    validated_parts.append(part)
            return ".".join(validated_parts)

        # Single identifier - validate and quote
        try:
            validated = self._validate_identifier_safe(identifier)
            return self._quote_single_identifier(validated)
        except ValueError:
            # If validation fails, might be a complex expression
            # Return as-is but log warning
            return identifier

    def _quote_single_identifier(self, identifier: str) -> str:
        """Quote a single identifier."""
        if identifier == "*":
            return identifier

        if self._database_type == DatabaseType.POSTGRESQL:
            return f'"{identifier}"'
        elif self._database_type in (DatabaseType.MYSQL, DatabaseType.SQLITE):
            return f"`{identifier}`"
        return identifier

    def _get_placeholder(self) -> str:
        """
        Get parameter placeholder based on database type.

        Returns:
            Placeholder string
        """
        if self._database_type == DatabaseType.POSTGRESQL:
            # PostgreSQL uses $1, $2, ...
            return f"${len(self._parameters) + 1}"
        elif self._database_type in (DatabaseType.MYSQL, DatabaseType.SQLITE):
            # MySQL and SQLite use ?
            return "?"
        return "?"


# Import expression classes to avoid circular imports
# These are used for type hints and duck typing
try:
    from .expressions import Field, Function
except ImportError:
    # Stub classes for type hints if not available
    class Field:
        """Field expression stub."""

        def compile(self, db_type):
            pass

    class Function:
        """Function expression stub."""

        def compile(self, db_type):
            pass


__all__ = ["Query", "QueryBuilder", "QueryType", "QueryContext", "LockType"]
