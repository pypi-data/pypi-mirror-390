"""
High-Performance Query Builder

Enterprise-grade query builder with <1ms latency optimization,
SQL injection protection, and multi-database compatibility.
"""

from .aggregates import Avg, Count, GroupConcat, Max, Min, Sum
from .builder import Query, QueryBuilder
from .cache import QueryCache
from .conditions import And, Condition, Not, Or
from .expressions import (
    BinaryOperation,
    Case,
    Expression,
    Field,
    Function,
    RawExpression,
    Subquery,
    UnaryOperation,
    Value,
)
from .joins import Join, JoinType
from .optimizer import QueryOptimizer

__all__ = [
    # Core components
    "QueryBuilder",
    "Query",
    # Expressions
    "Expression",
    "Field",
    "Value",
    "BinaryOperation",
    "UnaryOperation",
    "Function",
    "Case",
    "Subquery",
    "RawExpression",
    # Conditions
    "Condition",
    "And",
    "Or",
    "Not",
    # Joins
    "Join",
    "JoinType",
    # Aggregates
    "Count",
    "Sum",
    "Avg",
    "Min",
    "Max",
    "GroupConcat",
    # Optimization
    "QueryOptimizer",
    "QueryCache",
]
