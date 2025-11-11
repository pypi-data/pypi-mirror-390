"""
Query Builder Condition Classes

Provides condition building blocks for WHERE clauses including
AND, OR, NOT logic and raw SQL conditions.
"""

from typing import List, Union

from ..core.database_config import DatabaseType


class Condition:
    """Base class for query conditions."""

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile condition to SQL.

        Args:
            db_type: Target database type

        Returns:
            SQL string representation
        """
        raise NotImplementedError("Subclasses must implement compile()")


class RawCondition(Condition):
    """
    Raw SQL condition.

    Example:
        RawCondition("age > 18 AND status = 'active'")
    """

    def __init__(self, sql: str):
        """
        Initialize raw condition.

        Args:
            sql: Raw SQL string
        """
        self.sql = sql

    def compile(self, db_type: DatabaseType) -> str:
        """Compile raw condition to SQL."""
        return self.sql

    def __repr__(self) -> str:
        return f"RawCondition('{self.sql}')"


class And(Condition):
    """
    AND condition for combining multiple conditions.

    Example:
        And(
            RawCondition("age > 18"),
            RawCondition("status = 'active'")
        )
    """

    def __init__(self, *conditions: Condition):
        """
        Initialize AND condition.

        Args:
            *conditions: Conditions to combine with AND
        """
        self.conditions = conditions

    def compile(self, db_type: DatabaseType) -> str:
        """Compile AND condition to SQL."""
        if not self.conditions:
            return ""

        parts = []
        for condition in self.conditions:
            if hasattr(condition, "compile"):
                parts.append(condition.compile(db_type))
            else:
                parts.append(str(condition))

        if len(parts) == 1:
            return parts[0]

        return f"({' AND '.join(parts)})"

    def __repr__(self) -> str:
        return f"And({len(self.conditions)} conditions)"


class Or(Condition):
    """
    OR condition for combining multiple conditions.

    Example:
        Or(
            RawCondition("role = 'admin'"),
            RawCondition("role = 'moderator'")
        )
    """

    def __init__(self, *conditions: Condition):
        """
        Initialize OR condition.

        Args:
            *conditions: Conditions to combine with OR
        """
        self.conditions = conditions

    def compile(self, db_type: DatabaseType) -> str:
        """Compile OR condition to SQL."""
        if not self.conditions:
            return ""

        parts = []
        for condition in self.conditions:
            if hasattr(condition, "compile"):
                parts.append(condition.compile(db_type))
            else:
                parts.append(str(condition))

        if len(parts) == 1:
            return parts[0]

        return f"({' OR '.join(parts)})"

    def __repr__(self) -> str:
        return f"Or({len(self.conditions)} conditions)"


class Not(Condition):
    """
    NOT condition for negating a condition.

    Example:
        Not(RawCondition("deleted = TRUE"))
    """

    def __init__(self, condition: Condition):
        """
        Initialize NOT condition.

        Args:
            condition: Condition to negate
        """
        self.condition = condition

    def compile(self, db_type: DatabaseType) -> str:
        """Compile NOT condition to SQL."""
        if hasattr(self.condition, "compile"):
            inner = self.condition.compile(db_type)
        else:
            inner = str(self.condition)

        return f"NOT ({inner})"

    def __repr__(self) -> str:
        return f"Not({self.condition!r})"


__all__ = ["Condition", "RawCondition", "And", "Or", "Not"]
