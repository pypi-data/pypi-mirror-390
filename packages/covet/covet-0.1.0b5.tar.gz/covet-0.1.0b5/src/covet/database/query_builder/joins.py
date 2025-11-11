"""
Query Builder Join Classes

Provides join types and join condition builders for SQL queries.
"""

from enum import Enum
from typing import Optional, Union

from ..core.database_config import DatabaseType


class JoinType(Enum):
    """SQL JOIN types."""

    INNER = "INNER JOIN"
    LEFT = "LEFT JOIN"
    RIGHT = "RIGHT JOIN"
    FULL = "FULL OUTER JOIN"
    CROSS = "CROSS JOIN"


class Join:
    """
    Represents a SQL JOIN clause.

    Example:
        Join('profiles', 'users.id = profiles.user_id', JoinType.LEFT)
    """

    def __init__(
        self,
        table: str,
        on: Union[str, "Expression"],
        join_type: JoinType = JoinType.INNER,
    ):
        """
        Initialize JOIN clause.

        Args:
            table: Table to join
            on: Join condition
            join_type: Type of join
        """
        self.table = table
        self.on = on
        self.join_type = join_type

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile JOIN to SQL.

        Args:
            db_type: Target database type

        Returns:
            SQL JOIN clause
        """
        # Quote table name
        if db_type == DatabaseType.POSTGRESQL:
            quoted_table = f'"{self.table}"'
        elif db_type in (DatabaseType.MYSQL, DatabaseType.SQLITE):
            quoted_table = f"`{self.table}`"
        else:
            quoted_table = self.table

        # Compile ON condition
        if hasattr(self.on, "compile"):
            on_clause = self.on.compile(db_type)
        else:
            on_clause = str(self.on)

        return f"{self.join_type.value} {quoted_table} ON {on_clause}"

    def __repr__(self) -> str:
        return f"Join('{self.table}', '{self.on}', {self.join_type})"


__all__ = ["Join", "JoinType"]
