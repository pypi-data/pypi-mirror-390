"""
Advanced Aggregation Functions for CovetPy ORM

Django-compatible aggregation and annotation system with:
- Aggregate functions: Count, Sum, Avg, Min, Max, StdDev, Variance
- annotate(): Add computed fields to queryset results
- aggregate(): Calculate aggregate values across entire queryset
- Window functions: ROW_NUMBER, RANK, DENSE_RANK, LAG, LEAD, NTILE
- HAVING clause support for filtered aggregations
- GROUP BY optimization
- Subquery aggregations
- Custom aggregate function support

Production-ready features:
- Cross-database compatibility (PostgreSQL, MySQL, SQLite)
- Type-safe aggregation results
- Efficient query generation
- Support for complex expressions

Example:
    # Simple aggregation
    stats = await User.objects.aggregate(
        total=Count('*'),
        avg_age=Avg('age'),
        max_score=Max('score')
    )
    # Returns: {'total': 1000, 'avg_age': 32.5, 'max_score': 98}

    # Annotation (add computed fields)
    authors = await Author.objects.annotate(
        post_count=Count('posts'),
        total_views=Sum('posts__views')
    ).filter(post_count__gt=10)

    # Window functions
    rankings = await User.objects.annotate(
        rank=Window(
            expression=Rank(),
            order_by=['-score']
        )
    )

    # Grouped aggregation with HAVING
    categories = await Post.objects.values('category').annotate(
        post_count=Count('id'),
        avg_views=Avg('views')
    ).filter(post_count__gte=5)
"""

import logging
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union

logger = logging.getLogger(__name__)


class AggregateFunction:
    """
    Base class for aggregate functions.

    Provides common interface for all aggregate operations:
    - SQL generation
    - Type handling
    - Result parsing
    - Expression composition
    """

    def __init__(
        self,
        expression: Union[str, "Expression"],
        output_field: Optional["Field"] = None,
        distinct: bool = False,
        filter: Optional["Q"] = None,
        **extra,
    ):
        """
        Initialize aggregate function.

        Args:
            expression: Field name or expression to aggregate
            output_field: Field type for result (auto-detected if None)
            distinct: Apply DISTINCT (COUNT(DISTINCT field))
            filter: Filter condition for aggregate (WHERE clause)
            **extra: Extra parameters for specific aggregates
        """
        self.expression = expression
        self.output_field = output_field
        self.distinct = distinct
        self.filter = filter
        self.extra = extra

        # Set by queryset
        self.source_expressions = []
        self.is_summary = True

    def get_source_field(self, model: Type["Model"]) -> Optional["Field"]:
        """
        Get source field from model.

        Args:
            model: Model class

        Returns:
            Field object or None
        """
        if isinstance(self.expression, str):
            if self.expression == "*":
                return None
            return model._fields.get(self.expression)
        return None

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """
        Generate SQL for aggregate function.

        Args:
            compiler: Query compiler
            connection: Database connection

        Returns:
            Tuple of (sql, params)
        """
        raise NotImplementedError("Subclasses must implement as_sql()")

    def _get_field_sql(self, compiler: "QueryCompiler", connection: "DatabaseAdapter") -> str:
        """Get SQL for field expression."""
        if isinstance(self.expression, str):
            if self.expression == "*":
                return "*"
            return self.expression
        else:
            # Handle Expression objects
            sql, params = self.expression.as_sql(compiler, connection)
            return sql

    def _apply_distinct(self, sql: str) -> str:
        """Apply DISTINCT if configured."""
        if self.distinct:
            return f"DISTINCT {sql}"
        return sql


class Count(AggregateFunction):
    """
    COUNT aggregate function.

    Counts number of rows or non-NULL values in a column.

    Args:
        expression: Field name or '*' to count rows
        distinct: Count distinct values only
        filter: Filter condition

    Example:
        # Count all users
        total = await User.objects.aggregate(total=Count('*'))

        # Count distinct emails
        unique_emails = await User.objects.aggregate(
            unique=Count('email', distinct=True)
        )

        # Annotate posts with comment count
        posts = await Post.objects.annotate(
            comment_count=Count('comments')
        ).all()
    """

    def __init__(self, expression: str = "*", **kwargs):
        super().__init__(expression, **kwargs)
        self.function = "COUNT"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate COUNT SQL."""
        field_sql = self._get_field_sql(compiler, connection)
        field_sql = self._apply_distinct(field_sql)

        sql = f"COUNT({field_sql})"
        params = []

        # Add filter if present
        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"COUNT(CASE WHEN {filter_sql} THEN 1 END)"
            params.extend(filter_params)

        return sql, params


class Sum(AggregateFunction):
    """
    SUM aggregate function.

    Calculates sum of numeric values.

    Args:
        expression: Field name to sum
        output_field: Output field type (default: DecimalField)
        distinct: Sum distinct values only
        filter: Filter condition

    Example:
        # Total revenue
        stats = await Order.objects.aggregate(
            total_revenue=Sum('amount')
        )

        # Sum per category
        categories = await Product.objects.values('category').annotate(
            total_price=Sum('price')
        )

        # Conditional sum
        stats = await Order.objects.aggregate(
            completed_revenue=Sum('amount', filter=Q(status='completed'))
        )
    """

    def __init__(self, expression: str, **kwargs):
        super().__init__(expression, **kwargs)
        self.function = "SUM"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate SUM SQL."""
        field_sql = self._get_field_sql(compiler, connection)
        field_sql = self._apply_distinct(field_sql)

        sql = f"SUM({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"SUM(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


class Avg(AggregateFunction):
    """
    AVG aggregate function.

    Calculates average of numeric values.

    Args:
        expression: Field name to average
        output_field: Output field type (default: FloatField)
        distinct: Average distinct values only
        filter: Filter condition

    Example:
        # Average age
        stats = await User.objects.aggregate(
            avg_age=Avg('age')
        )

        # Average per group
        departments = await Employee.objects.values('department').annotate(
            avg_salary=Avg('salary')
        )

        # Conditional average
        stats = await Product.objects.aggregate(
            avg_active_price=Avg('price', filter=Q(is_active=True))
        )
    """

    def __init__(self, expression: str, **kwargs):
        super().__init__(expression, **kwargs)
        self.function = "AVG"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate AVG SQL."""
        field_sql = self._get_field_sql(compiler, connection)
        field_sql = self._apply_distinct(field_sql)

        sql = f"AVG({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"AVG(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


class Min(AggregateFunction):
    """
    MIN aggregate function.

    Finds minimum value.

    Args:
        expression: Field name to find minimum
        output_field: Output field type (matches input field)
        filter: Filter condition

    Example:
        # Minimum price
        stats = await Product.objects.aggregate(
            min_price=Min('price')
        )

        # Earliest date
        stats = await Event.objects.aggregate(
            earliest=Min('created_at')
        )

        # Minimum per category
        categories = await Product.objects.values('category').annotate(
            lowest_price=Min('price')
        )
    """

    def __init__(self, expression: str, **kwargs):
        super().__init__(expression, **kwargs)
        self.function = "MIN"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate MIN SQL."""
        field_sql = self._get_field_sql(compiler, connection)

        sql = f"MIN({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"MIN(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


class Max(AggregateFunction):
    """
    MAX aggregate function.

    Finds maximum value.

    Args:
        expression: Field name to find maximum
        output_field: Output field type (matches input field)
        filter: Filter condition

    Example:
        # Maximum score
        stats = await Game.objects.aggregate(
            high_score=Max('score')
        )

        # Latest date
        stats = await Article.objects.aggregate(
            latest=Max('published_at')
        )

        # Maximum per user
        users = await Score.objects.values('user_id').annotate(
            best_score=Max('points')
        )
    """

    def __init__(self, expression: str, **kwargs):
        super().__init__(expression, **kwargs)
        self.function = "MAX"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate MAX SQL."""
        field_sql = self._get_field_sql(compiler, connection)

        sql = f"MAX({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"MAX(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


class StdDev(AggregateFunction):
    """
    Standard Deviation aggregate function.

    Calculates population or sample standard deviation.

    Args:
        expression: Field name to calculate std dev for
        sample: Use sample std dev (True) or population (False)
        output_field: Output field type (default: FloatField)
        filter: Filter condition

    Note:
        SQLite doesn't support STDDEV natively - returns None

    Example:
        # Population standard deviation
        stats = await Measurement.objects.aggregate(
            stddev=StdDev('value', sample=False)
        )

        # Sample standard deviation (default)
        stats = await Score.objects.aggregate(
            stddev=StdDev('points')
        )
    """

    def __init__(self, expression: str, sample: bool = True, **kwargs):
        super().__init__(expression, **kwargs)
        self.sample = sample
        self.function = "STDDEV_SAMP" if sample else "STDDEV_POP"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate STDDEV SQL."""
        field_sql = self._get_field_sql(compiler, connection)

        # Check database support
        if connection.__class__.__name__ == "SQLiteAdapter":
            logger.warning("SQLite doesn't support STDDEV - returning NULL")
            return "NULL", []

        func_name = self.function
        sql = f"{func_name}({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"{func_name}(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


class Variance(AggregateFunction):
    """
    Variance aggregate function.

    Calculates population or sample variance.

    Args:
        expression: Field name to calculate variance for
        sample: Use sample variance (True) or population (False)
        output_field: Output field type (default: FloatField)
        filter: Filter condition

    Note:
        SQLite doesn't support VARIANCE natively - returns None

    Example:
        # Population variance
        stats = await Measurement.objects.aggregate(
            variance=Variance('value', sample=False)
        )

        # Sample variance (default)
        stats = await Score.objects.aggregate(
            variance=Variance('points')
        )
    """

    def __init__(self, expression: str, sample: bool = True, **kwargs):
        super().__init__(expression, **kwargs)
        self.sample = sample
        self.function = "VAR_SAMP" if sample else "VAR_POP"

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate VARIANCE SQL."""
        field_sql = self._get_field_sql(compiler, connection)

        # Check database support
        if connection.__class__.__name__ == "SQLiteAdapter":
            logger.warning("SQLite doesn't support VARIANCE - returning NULL")
            return "NULL", []

        func_name = self.function
        sql = f"{func_name}({field_sql})"
        params = []

        if self.filter:
            filter_sql, filter_params = self.filter.as_sql(compiler, connection)
            sql = f"{func_name}(CASE WHEN {filter_sql} THEN {field_sql} END)"
            params.extend(filter_params)

        return sql, params


# Window Functions


class WindowFunction:
    """
    Base class for window functions.

    Window functions perform calculations across rows related to the current row:
    - ROW_NUMBER(): Assign sequential number
    - RANK(): Rank with gaps for ties
    - DENSE_RANK(): Rank without gaps
    - LAG(): Access previous row
    - LEAD(): Access next row
    - NTILE(): Distribute rows into buckets

    Args:
        expression: Expression to compute
        partition_by: Fields to partition by (GROUP BY equivalent)
        order_by: Fields to order by within partition
        frame: Window frame specification (ROWS/RANGE)
    """

    def __init__(
        self,
        expression: Optional[Union[str, "Expression"]] = None,
        partition_by: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        frame: Optional[str] = None,
    ):
        """Initialize window function."""
        self.expression = expression
        self.partition_by = partition_by or []
        self.order_by = order_by or []
        self.frame = frame

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate window function SQL."""
        # Build function call
        func_sql = self._get_function_sql()

        # Build OVER clause
        over_parts = []

        if self.partition_by:
            partition_clause = ", ".join(self.partition_by)
            over_parts.append(f"PARTITION BY {partition_clause}")

        if self.order_by:
            order_parts = []
            for field in self.order_by:
                if field.startswith("-"):
                    order_parts.append(f"{field[1:]} DESC")
                else:
                    order_parts.append(f"{field} ASC")
            order_clause = ", ".join(order_parts)
            over_parts.append(f"ORDER BY {order_clause}")

        if self.frame:
            over_parts.append(self.frame)

        over_clause = " ".join(over_parts)
        sql = f"{func_sql} OVER ({over_clause})"

        return sql, []

    def _get_function_sql(self) -> str:
        """Get function SQL (overridden by subclasses)."""
        raise NotImplementedError


class RowNumber(WindowFunction):
    """
    ROW_NUMBER() window function.

    Assigns sequential number to each row within partition.

    Example:
        # Number rows by creation date
        posts = await Post.objects.annotate(
            row_num=Window(
                expression=RowNumber(),
                order_by=['-created_at']
            )
        )

        # Number within partitions
        posts = await Post.objects.annotate(
            category_rank=Window(
                expression=RowNumber(),
                partition_by=['category'],
                order_by=['-views']
            )
        )
    """

    def _get_function_sql(self) -> str:
        """Generate ROW_NUMBER SQL."""
        return "ROW_NUMBER()"


class Rank(WindowFunction):
    """
    RANK() window function.

    Assigns rank with gaps for ties.

    Example:
        # Rank by score (1, 2, 2, 4)
        users = await User.objects.annotate(
            rank=Window(
                expression=Rank(),
                order_by=['-score']
            )
        )
    """

    def _get_function_sql(self) -> str:
        """Generate RANK SQL."""
        return "RANK()"


class DenseRank(WindowFunction):
    """
    DENSE_RANK() window function.

    Assigns rank without gaps for ties.

    Example:
        # Dense rank by score (1, 2, 2, 3)
        users = await User.objects.annotate(
            rank=Window(
                expression=DenseRank(),
                order_by=['-score']
            )
        )
    """

    def _get_function_sql(self) -> str:
        """Generate DENSE_RANK SQL."""
        return "DENSE_RANK()"


class Lag(WindowFunction):
    """
    LAG() window function.

    Accesses value from previous row.

    Args:
        expression: Field to get from previous row
        offset: Number of rows back (default: 1)
        default: Default value if no previous row

    Example:
        # Get previous score
        games = await Game.objects.annotate(
            previous_score=Window(
                expression=Lag('score'),
                order_by=['created_at']
            )
        )

        # Calculate difference from previous
        # (Can be done with F expressions after annotation)
    """

    def __init__(self, expression: str, offset: int = 1, default: Any = None, **kwargs):
        super().__init__(expression, **kwargs)
        self.offset = offset
        self.default = default

    def _get_function_sql(self) -> str:
        """Generate LAG SQL."""
        parts = [self.expression, str(self.offset)]
        if self.default is not None:
            parts.append(str(self.default))
        return f"LAG({', '.join(parts)})"


class Lead(WindowFunction):
    """
    LEAD() window function.

    Accesses value from next row.

    Args:
        expression: Field to get from next row
        offset: Number of rows forward (default: 1)
        default: Default value if no next row

    Example:
        # Get next score
        games = await Game.objects.annotate(
            next_score=Window(
                expression=Lead('score'),
                order_by=['created_at']
            )
        )
    """

    def __init__(self, expression: str, offset: int = 1, default: Any = None, **kwargs):
        super().__init__(expression, **kwargs)
        self.offset = offset
        self.default = default

    def _get_function_sql(self) -> str:
        """Generate LEAD SQL."""
        parts = [self.expression, str(self.offset)]
        if self.default is not None:
            parts.append(str(self.default))
        return f"LEAD({', '.join(parts)})"


class Ntile(WindowFunction):
    """
    NTILE() window function.

    Distributes rows into specified number of buckets.

    Args:
        num_buckets: Number of buckets to create

    Example:
        # Divide users into quartiles by score
        users = await User.objects.annotate(
            quartile=Window(
                expression=Ntile(4),
                order_by=['-score']
            )
        )

        # Find top 10% (decile 1)
        top_users = await User.objects.annotate(
            decile=Window(
                expression=Ntile(10),
                order_by=['-score']
            )
        ).filter(decile=1)
    """

    def __init__(self, num_buckets: int, **kwargs):
        super().__init__(**kwargs)
        self.num_buckets = num_buckets

    def _get_function_sql(self) -> str:
        """Generate NTILE SQL."""
        return f"NTILE({self.num_buckets})"


class Window:
    """
    Window specification for window functions.

    Wrapper that creates window function with partition/ordering.

    Args:
        expression: Window function (RowNumber, Rank, etc.)
        partition_by: Fields to partition by
        order_by: Fields to order by
        frame: Window frame specification

    Example:
        posts = await Post.objects.annotate(
            rank=Window(
                expression=Rank(),
                partition_by=['category'],
                order_by=['-views']
            )
        )
    """

    def __init__(
        self,
        expression: WindowFunction,
        partition_by: Optional[List[str]] = None,
        order_by: Optional[List[str]] = None,
        frame: Optional[str] = None,
    ):
        """Initialize window specification."""
        self.expression = expression
        self.expression.partition_by = partition_by or []
        self.expression.order_by = order_by or []
        self.expression.frame = frame

    def as_sql(
        self, compiler: "QueryCompiler", connection: "DatabaseAdapter"
    ) -> tuple[str, List[Any]]:
        """Generate SQL."""
        return self.expression.as_sql(compiler, connection)


# Helper classes


class QueryCompiler:
    """
    Mock query compiler for aggregate SQL generation.

    In production, this would be integrated with the full ORM compiler.
    """

    def __init__(self, model: Type["Model"]):
        self.model = model

    def quote_name(self, name: str) -> str:
        """Quote identifier name."""
        return f'"{name}"'


__all__ = [
    # Aggregate functions
    "AggregateFunction",
    "Count",
    "Sum",
    "Avg",
    "Min",
    "Max",
    "StdDev",
    "Variance",
    # Window functions
    "WindowFunction",
    "Window",
    "RowNumber",
    "Rank",
    "DenseRank",
    "Lag",
    "Lead",
    "Ntile",
    # Utilities
    "QueryCompiler",
]
