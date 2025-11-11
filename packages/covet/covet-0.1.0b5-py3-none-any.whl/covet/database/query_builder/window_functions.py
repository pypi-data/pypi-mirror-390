"""
Window Functions Support

Comprehensive window function implementation for advanced analytics:
- Ranking functions: ROW_NUMBER, RANK, DENSE_RANK, NTILE, PERCENT_RANK
- Offset functions: LAG, LEAD, FIRST_VALUE, LAST_VALUE, NTH_VALUE
- Aggregate functions: SUM, AVG, COUNT, MIN, MAX over windows
- Frame specifications: ROWS, RANGE, GROUPS
- Window partitioning and ordering

Supports PostgreSQL 8.4+, MySQL 8.0+, and SQLite 3.25+
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, List, Optional, Union

from ..core.database_config import DatabaseType

if TYPE_CHECKING:
    from .expressions import Expression


@dataclass
class WindowFrame:
    """
    Represents a window frame specification.

    Frame types:
    - ROWS: Physical row-based frame
    - RANGE: Logical value-based frame
    - GROUPS: Group-based frame (PostgreSQL 11+)

    Bounds:
    - UNBOUNDED PRECEDING
    - N PRECEDING
    - CURRENT ROW
    - N FOLLOWING
    - UNBOUNDED FOLLOWING
    """

    frame_type: str = "RANGE"  # ROWS, RANGE, GROUPS
    start_bound: str = "UNBOUNDED PRECEDING"
    end_bound: Optional[str] = None  # None means only start is specified

    def __post_init__(self):
        """Validate frame specification."""
        valid_types = ("ROWS", "RANGE", "GROUPS")
        if self.frame_type not in valid_types:
            raise ValueError(f"Invalid frame type: {self.frame_type}. Must be one of {valid_types}")

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile frame specification to SQL.

        Args:
            db_type: Target database type

        Returns:
            Frame specification SQL

        Raises:
            ValueError: If GROUPS is used with unsupported database
        """
        if self.frame_type == "GROUPS" and db_type != DatabaseType.POSTGRESQL:
            raise ValueError(f"{db_type.value} does not support GROUPS frame type")

        parts = [self.frame_type]

        if self.end_bound:
            # Two-bound specification
            parts.append(f"BETWEEN {self.start_bound} AND {self.end_bound}")
        else:
            # Single-bound specification
            parts.append(self.start_bound)

        return " ".join(parts)

    @classmethod
    def rows_between(cls, start: str, end: str) -> "WindowFrame":
        """Create ROWS BETWEEN frame."""
        return cls(frame_type="ROWS", start_bound=start, end_bound=end)

    @classmethod
    def range_between(cls, start: str, end: str) -> "WindowFrame":
        """Create RANGE BETWEEN frame."""
        return cls(frame_type="RANGE", start_bound=start, end_bound=end)

    @classmethod
    def rows_unbounded(cls) -> "WindowFrame":
        """Create ROWS UNBOUNDED PRECEDING frame."""
        return cls(frame_type="ROWS", start_bound="UNBOUNDED PRECEDING")

    @classmethod
    def rows_current(cls) -> "WindowFrame":
        """Create ROWS CURRENT ROW frame."""
        return cls(frame_type="ROWS", start_bound="CURRENT ROW")

    @classmethod
    def rows_preceding(cls, n: int) -> "WindowFrame":
        """Create ROWS N PRECEDING frame."""
        return cls(frame_type="ROWS", start_bound=f"{n} PRECEDING")

    @classmethod
    def rows_following(cls, n: int) -> "WindowFrame":
        """Create ROWS N FOLLOWING frame."""
        return cls(frame_type="ROWS", start_bound=f"{n} FOLLOWING")


@dataclass
class WindowSpec:
    """
    Represents a window specification (OVER clause).

    Components:
    - partition_by: Columns to partition by
    - order_by: Ordering specification
    - frame: Frame specification (optional)
    """

    partition_by: List[Union[str, "Expression"]] = field(default_factory=list)
    order_by: List[tuple[Union[str, "Expression"], str]] = field(default_factory=list)
    frame: Optional[WindowFrame] = None
    window_name: Optional[str] = None  # For named windows

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile window specification to SQL.

        Args:
            db_type: Target database type

        Returns:
            OVER clause SQL
        """
        if self.window_name:
            # Reference to a named window
            return f"OVER {self._quote_identifier(self.window_name, db_type)}"

        parts = []

        # PARTITION BY clause
        if self.partition_by:
            partition_cols = []
            for col in self.partition_by:
                if hasattr(col, "compile"):
                    partition_cols.append(col.compile(db_type))
                else:
                    partition_cols.append(self._quote_identifier(str(col), db_type))
            parts.append(f"PARTITION BY {', '.join(partition_cols)}")

        # ORDER BY clause
        if self.order_by:
            order_cols = []
            for col, direction in self.order_by:
                if hasattr(col, "compile"):
                    col_sql = col.compile(db_type)
                else:
                    col_sql = self._quote_identifier(str(col), db_type)
                order_cols.append(f"{col_sql} {direction}")
            parts.append(f"ORDER BY {', '.join(order_cols)}")

        # Frame specification
        if self.frame:
            parts.append(self.frame.compile(db_type))

        if parts:
            return f"OVER ({' '.join(parts)})"
        else:
            return "OVER ()"

    def _quote_identifier(self, identifier: str, db_type: DatabaseType) -> str:
        """Quote identifier based on database type."""
        if db_type == DatabaseType.POSTGRESQL:
            return f'"{identifier}"'
        else:
            return f"`{identifier}`"

    def clone(self) -> "WindowSpec":
        """Create a copy of this window spec."""
        from copy import deepcopy

        return deepcopy(self)


class WindowFunction:
    """
    Base class for window functions.

    All window functions compile to: FUNCTION(...) OVER (...)
    """

    def __init__(
        self,
        function_name: str,
        args: Optional[List[Union[str, "Expression"]]] = None,
        window_spec: Optional[WindowSpec] = None,
    ):
        """
        Initialize window function.

        Args:
            function_name: Name of the window function
            args: Function arguments
            window_spec: Window specification (OVER clause)
        """
        self.function_name = function_name
        self.args = args or []
        self.window_spec = window_spec or WindowSpec()

    def partition_by(self, *columns: Union[str, "Expression"]) -> "WindowFunction":
        """
        Set PARTITION BY clause.

        Args:
            *columns: Columns to partition by

        Returns:
            Self for chaining
        """
        self.window_spec.partition_by = list(columns)
        return self

    def order_by(
        self, column: Union[str, "Expression"], direction: str = "ASC"
    ) -> "WindowFunction":
        """
        Add ORDER BY clause.

        Args:
            column: Column to order by
            direction: ASC or DESC

        Returns:
            Self for chaining
        """
        direction = direction.upper()
        if direction not in ("ASC", "DESC"):
            raise ValueError(f"Invalid direction: {direction}. Must be ASC or DESC")

        self.window_spec.order_by.append((column, direction))
        return self

    def frame(self, frame: WindowFrame) -> "WindowFunction":
        """
        Set frame specification.

        Args:
            frame: WindowFrame instance

        Returns:
            Self for chaining
        """
        self.window_spec.frame = frame
        return self

    def over(self, window_spec: WindowSpec) -> "WindowFunction":
        """
        Set complete window specification.

        Args:
            window_spec: WindowSpec instance

        Returns:
            Self for chaining
        """
        self.window_spec = window_spec
        return self

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile window function to SQL.

        Args:
            db_type: Target database type

        Returns:
            Complete window function SQL
        """
        # Compile function arguments
        arg_strs = []
        for arg in self.args:
            if hasattr(arg, "compile"):
                arg_strs.append(arg.compile(db_type))
            else:
                # Quote identifiers
                if db_type == DatabaseType.POSTGRESQL:
                    arg_strs.append(f'"{arg}"')
                else:
                    arg_strs.append(f"`{arg}`")

        # Build function call
        if arg_strs:
            func_call = f"{self.function_name}({', '.join(arg_strs)})"
        else:
            func_call = f"{self.function_name}()"

        # Add window specification
        over_clause = self.window_spec.compile(db_type)

        return f"{func_call} {over_clause}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


# Ranking Functions


class RowNumber(WindowFunction):
    """
    ROW_NUMBER() window function.

    Assigns a unique sequential integer to rows within a partition.

    Example:
        RowNumber().partition_by('department').order_by('salary', 'DESC')
        # Generates: ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC)
    """

    def __init__(self, window_spec: Optional[WindowSpec] = None):
        super().__init__("ROW_NUMBER", [], window_spec)


class Rank(WindowFunction):
    """
    RANK() window function.

    Assigns a rank with gaps for tied values.

    Example:
        Rank().partition_by('department').order_by('salary', 'DESC')
    """

    def __init__(self, window_spec: Optional[WindowSpec] = None):
        super().__init__("RANK", [], window_spec)


class DenseRank(WindowFunction):
    """
    DENSE_RANK() window function.

    Assigns a rank without gaps for tied values.

    Example:
        DenseRank().partition_by('department').order_by('salary', 'DESC')
    """

    def __init__(self, window_spec: Optional[WindowSpec] = None):
        super().__init__("DENSE_RANK", [], window_spec)


class NTile(WindowFunction):
    """
    NTILE(n) window function.

    Divides rows into n buckets.

    Example:
        NTile(4).order_by('salary', 'DESC')  # Quartiles
    """

    def __init__(self, n: int, window_spec: Optional[WindowSpec] = None):
        if n < 1:
            raise ValueError(f"NTILE bucket count must be >= 1, got {n}")
        super().__init__("NTILE", [str(n)], window_spec)


class PercentRank(WindowFunction):
    """
    PERCENT_RANK() window function.

    Calculates relative rank as a percentage (0.0 to 1.0).

    Example:
        PercentRank().partition_by('category').order_by('score', 'DESC')
    """

    def __init__(self, window_spec: Optional[WindowSpec] = None):
        super().__init__("PERCENT_RANK", [], window_spec)


class CumeDist(WindowFunction):
    """
    CUME_DIST() window function.

    Calculates cumulative distribution.

    Example:
        CumeDist().partition_by('category').order_by('score', 'DESC')
    """

    def __init__(self, window_spec: Optional[WindowSpec] = None):
        super().__init__("CUME_DIST", [], window_spec)


# Offset Functions


class Lag(WindowFunction):
    """
    LAG(expr [, offset [, default]]) window function.

    Accesses value from a previous row.

    Example:
        Lag('price', 1, 0).partition_by('product_id').order_by('date')
    """

    def __init__(
        self,
        column: Union[str, "Expression"],
        offset: int = 1,
        default: Any = None,
        window_spec: Optional[WindowSpec] = None,
    ):
        args = [column]
        if offset != 1:
            args.append(str(offset))
            if default is not None:
                args.append(str(default))
        elif default is not None:
            args.extend([str(offset), str(default)])

        super().__init__("LAG", args, window_spec)


class Lead(WindowFunction):
    """
    LEAD(expr [, offset [, default]]) window function.

    Accesses value from a following row.

    Example:
        Lead('price', 1, 0).partition_by('product_id').order_by('date')
    """

    def __init__(
        self,
        column: Union[str, "Expression"],
        offset: int = 1,
        default: Any = None,
        window_spec: Optional[WindowSpec] = None,
    ):
        args = [column]
        if offset != 1:
            args.append(str(offset))
            if default is not None:
                args.append(str(default))
        elif default is not None:
            args.extend([str(offset), str(default)])

        super().__init__("LEAD", args, window_spec)


class FirstValue(WindowFunction):
    """
    FIRST_VALUE(expr) window function.

    Returns the first value in the window frame.

    Example:
        FirstValue('price').partition_by('product').order_by('date')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("FIRST_VALUE", [column], window_spec)


class LastValue(WindowFunction):
    """
    LAST_VALUE(expr) window function.

    Returns the last value in the window frame.

    Example:
        LastValue('price').partition_by('product').order_by('date')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("LAST_VALUE", [column], window_spec)


class NthValue(WindowFunction):
    """
    NTH_VALUE(expr, n) window function.

    Returns the nth value in the window frame.

    Example:
        NthValue('price', 2).partition_by('product').order_by('date')
    """

    def __init__(
        self, column: Union[str, "Expression"], n: int, window_spec: Optional[WindowSpec] = None
    ):
        if n < 1:
            raise ValueError(f"NTH_VALUE position must be >= 1, got {n}")
        super().__init__("NTH_VALUE", [column, str(n)], window_spec)


# Aggregate Window Functions


class WindowSum(WindowFunction):
    """
    SUM(expr) OVER (...) window aggregate.

    Example:
        WindowSum('amount').partition_by('account_id').order_by('date')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("SUM", [column], window_spec)


class WindowAvg(WindowFunction):
    """
    AVG(expr) OVER (...) window aggregate.

    Example:
        WindowAvg('price').partition_by('category')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("AVG", [column], window_spec)


class WindowCount(WindowFunction):
    """
    COUNT(expr) OVER (...) window aggregate.

    Example:
        WindowCount('*').partition_by('department')
    """

    def __init__(
        self, column: Union[str, "Expression"] = "*", window_spec: Optional[WindowSpec] = None
    ):
        super().__init__("COUNT", [column], window_spec)


class WindowMin(WindowFunction):
    """
    MIN(expr) OVER (...) window aggregate.

    Example:
        WindowMin('price').partition_by('category')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("MIN", [column], window_spec)


class WindowMax(WindowFunction):
    """
    MAX(expr) OVER (...) window aggregate.

    Example:
        WindowMax('price').partition_by('category')
    """

    def __init__(self, column: Union[str, "Expression"], window_spec: Optional[WindowSpec] = None):
        super().__init__("MAX", [column], window_spec)


# Helper functions


def row_number() -> RowNumber:
    """Create ROW_NUMBER() window function."""
    return RowNumber()


def rank() -> Rank:
    """Create RANK() window function."""
    return Rank()


def dense_rank() -> DenseRank:
    """Create DENSE_RANK() window function."""
    return DenseRank()


def ntile(n: int) -> NTile:
    """Create NTILE(n) window function."""
    return NTile(n)


def percent_rank() -> PercentRank:
    """Create PERCENT_RANK() window function."""
    return PercentRank()


def cume_dist() -> CumeDist:
    """Create CUME_DIST() window function."""
    return CumeDist()


def lag(column: Union[str, "Expression"], offset: int = 1, default: Any = None) -> Lag:
    """Create LAG() window function."""
    return Lag(column, offset, default)


def lead(column: Union[str, "Expression"], offset: int = 1, default: Any = None) -> Lead:
    """Create LEAD() window function."""
    return Lead(column, offset, default)


def first_value(column: Union[str, "Expression"]) -> FirstValue:
    """Create FIRST_VALUE() window function."""
    return FirstValue(column)


def last_value(column: Union[str, "Expression"]) -> LastValue:
    """Create LAST_VALUE() window function."""
    return LastValue(column)


def nth_value(column: Union[str, "Expression"], n: int) -> NthValue:
    """Create NTH_VALUE() window function."""
    return NthValue(column, n)


__all__ = [
    # Frame and spec
    "WindowFrame",
    "WindowSpec",
    # Base
    "WindowFunction",
    # Ranking
    "RowNumber",
    "Rank",
    "DenseRank",
    "NTile",
    "PercentRank",
    "CumeDist",
    # Offset
    "Lag",
    "Lead",
    "FirstValue",
    "LastValue",
    "NthValue",
    # Aggregates
    "WindowSum",
    "WindowAvg",
    "WindowCount",
    "WindowMin",
    "WindowMax",
    # Helpers
    "row_number",
    "rank",
    "dense_rank",
    "ntile",
    "percent_rank",
    "cume_dist",
    "lag",
    "lead",
    "first_value",
    "last_value",
    "nth_value",
]
