"""
Aggregate functions for query builder.
"""

from typing import Union

from .expressions import Expression, Field, Function


def Count(field: Union[str, Expression] = "*") -> Function:
    """COUNT aggregate function."""
    if isinstance(field, str):
        if field == "*":
            from .expressions import RawExpression

            return Function("COUNT", RawExpression("*"))
        else:
            return Function("COUNT", Field(field))
    return Function("COUNT", field)


def Sum(field: Union[str, Expression]) -> Function:
    """SUM aggregate function."""
    if isinstance(field, str):
        field = Field(field)
    return Function("SUM", field)


def Avg(field: Union[str, Expression]) -> Function:
    """AVG aggregate function."""
    if isinstance(field, str):
        field = Field(field)
    return Function("AVG", field)


def Min(field: Union[str, Expression]) -> Function:
    """MIN aggregate function."""
    if isinstance(field, str):
        field = Field(field)
    return Function("MIN", field)


def Max(field: Union[str, Expression]) -> Function:
    """MAX aggregate function."""
    if isinstance(field, str):
        field = Field(field)
    return Function("MAX", field)


def GroupConcat(field: Union[str, Expression], separator: str = ",") -> Function:
    """GROUP_CONCAT aggregate function."""
    if isinstance(field, str):
        field = Field(field)
    # This is a simplified version
    return Function("GROUP_CONCAT", field)
