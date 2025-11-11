"""
Query Builder Expression Classes

Provides expression building blocks for complex SQL queries including
fields, functions, binary operations, CASE expressions, and subqueries.
"""

from typing import Any, List, Optional, Union

from ..core.database_config import DatabaseType


class Expression:
    """Base class for SQL expressions."""

    def compile(self, db_type: DatabaseType) -> str:
        """
        Compile expression to SQL.

        Args:
            db_type: Target database type

        Returns:
            SQL string representation
        """
        raise NotImplementedError("Subclasses must implement compile()")

    def __eq__(self, other) -> "BinaryOperation":
        """Create equality comparison."""
        return BinaryOperation(self, "=", other)

    def __ne__(self, other) -> "BinaryOperation":
        """Create inequality comparison."""
        return BinaryOperation(self, "!=", other)

    def __lt__(self, other) -> "BinaryOperation":
        """Create less than comparison."""
        return BinaryOperation(self, "<", other)

    def __le__(self, other) -> "BinaryOperation":
        """Create less than or equal comparison."""
        return BinaryOperation(self, "<=", other)

    def __gt__(self, other) -> "BinaryOperation":
        """Create greater than comparison."""
        return BinaryOperation(self, ">", other)

    def __ge__(self, other) -> "BinaryOperation":
        """Create greater than or equal comparison."""
        return BinaryOperation(self, ">=", other)


class Field(Expression):
    """
    Field expression for referencing table columns.

    Example:
        Field('users.id')
        Field('email')
    """

    def __init__(self, name: str):
        """
        Initialize field expression.

        Args:
            name: Field name (can be qualified like 'table.column')
        """
        self.name = name

    def compile(self, db_type: DatabaseType) -> str:
        """Compile field to SQL."""
        # Quote field names based on database type
        if db_type == DatabaseType.POSTGRESQL:
            if "." in self.name:
                # Qualified name like table.column
                parts = self.name.split(".")
                return ".".join([f'"{p}"' for p in parts])
            return f'"{self.name}"'
        elif db_type in (DatabaseType.MYSQL, DatabaseType.SQLITE):
            if "." in self.name:
                parts = self.name.split(".")
                return ".".join([f"`{p}`" for p in parts])
            return f"`{self.name}`"
        return self.name

    def __repr__(self) -> str:
        return f"Field('{self.name}')"


class Value(Expression):
    """
    Value expression for literal values.

    Example:
        Value(42)
        Value('hello')
    """

    def __init__(self, value: Any):
        """
        Initialize value expression.

        Args:
            value: Literal value
        """
        self.value = value

    def compile(self, db_type: DatabaseType) -> str:
        """Compile value to SQL."""
        if isinstance(self.value, str):
            # Escape single quotes
            escaped = self.value.replace("'", "''")
            return f"'{escaped}'"
        elif self.value is None:
            return "NULL"
        elif isinstance(self.value, bool):
            return "TRUE" if self.value else "FALSE"
        else:
            return str(self.value)

    def __repr__(self) -> str:
        return f"Value({self.value!r})"


class Function(Expression):
    """
    Function expression for SQL functions.

    Example:
        Function('COUNT', Field('id'))
        Function('UPPER', Field('name'))
        Function('NOW()')  # No-arg function
    """

    def __init__(self, name: str, *args):
        """
        Initialize function expression.

        Args:
            name: Function name or complete function call
            *args: Function arguments (Field, Value, or other expressions)
        """
        self.name = name
        self.args = args

    def compile(self, db_type: DatabaseType) -> str:
        """Compile function to SQL."""
        # If name already contains parentheses, return as-is
        if "(" in self.name:
            return self.name

        # Build function call
        if not self.args:
            return f"{self.name}()"

        arg_strs = []
        for arg in self.args:
            if hasattr(arg, "compile"):
                arg_strs.append(arg.compile(db_type))
            else:
                arg_strs.append(str(arg))

        return f"{self.name}({', '.join(arg_strs)})"

    def __repr__(self) -> str:
        if self.args:
            args_repr = ", ".join(repr(arg) for arg in self.args)
            return f"Function('{self.name}', {args_repr})"
        return f"Function('{self.name}')"


class BinaryOperation(Expression):
    """
    Binary operation expression (e.g., field = value, field > 10).

    Example:
        BinaryOperation(Field('age'), '>', Value(18))
        Field('age') > 18  # Uses __gt__ operator
    """

    def __init__(self, left: Union[Expression, Any], operator: str, right: Union[Expression, Any]):
        """
        Initialize binary operation.

        Args:
            left: Left operand
            operator: SQL operator (=, !=, <, >, <=, >=, LIKE, etc.)
            right: Right operand
        """
        self.left = left
        self.operator = operator
        self.right = right

    def get_parameters(self) -> List[Any]:
        """
        Extract parameter values from this expression.

        Returns:
            List of values that should be parameterized
        """
        params = []

        # Extract from left side
        if hasattr(self.left, "get_parameters"):
            params.extend(self.left.get_parameters())
        elif not hasattr(self.left, "compile"):
            # Raw value - should be parameterized
            params.append(self.left)

        # Extract from right side
        if hasattr(self.right, "get_parameters"):
            params.extend(self.right.get_parameters())
        elif not hasattr(self.right, "compile"):
            # Raw value - should be parameterized
            params.append(self.right)

        return params

    def compile_with_placeholders(
        self, db_type: DatabaseType, param_offset: int = 0
    ) -> tuple[str, List[Any]]:
        """
        Compile with parameter placeholders.

        Args:
            db_type: Database type
            param_offset: Current parameter count offset

        Returns:
            Tuple of (SQL string, list of parameters)
        """
        params = []

        # Compile left side
        if hasattr(self.left, "compile"):
            left_sql = self.left.compile(db_type)
        else:
            # Literal value - use placeholder
            if db_type == DatabaseType.POSTGRESQL:
                left_sql = f"${param_offset + len(params) + 1}"
            else:
                left_sql = "?"
            params.append(self.left)

        # Compile right side
        if hasattr(self.right, "compile"):
            right_sql = self.right.compile(db_type)
        else:
            # Literal value - use placeholder
            if db_type == DatabaseType.POSTGRESQL:
                right_sql = f"${param_offset + len(params) + 1}"
            else:
                right_sql = "?"
            params.append(self.right)

        sql = f"{left_sql} {self.operator} {right_sql}"
        return sql, params

    def compile(self, db_type: DatabaseType) -> str:
        """Compile binary operation to SQL."""
        # For backwards compatibility, compile without parameterization
        # The query builder should use compile_with_placeholders instead
        sql, _ = self.compile_with_placeholders(db_type, 0)
        return sql

    def __repr__(self) -> str:
        return f"BinaryOperation({self.left!r}, '{self.operator}', {self.right!r})"


class UnaryOperation(Expression):
    """
    Unary operation expression (e.g., NOT, IS NULL).

    Example:
        UnaryOperation('NOT', Field('active'))
        UnaryOperation('IS NULL', Field('deleted_at'))
    """

    def __init__(self, operator: str, operand: Union[Expression, Any]):
        """
        Initialize unary operation.

        Args:
            operator: SQL operator (NOT, IS NULL, IS NOT NULL, etc.)
            operand: Operand expression
        """
        self.operator = operator
        self.operand = operand

    def compile(self, db_type: DatabaseType) -> str:
        """Compile unary operation to SQL."""
        if hasattr(self.operand, "compile"):
            operand_sql = self.operand.compile(db_type)
        else:
            operand_sql = str(self.operand)

        # Handle postfix operators
        if self.operator in ("IS NULL", "IS NOT NULL"):
            return f"{operand_sql} {self.operator}"
        else:
            return f"{self.operator} {operand_sql}"

    def __repr__(self) -> str:
        return f"UnaryOperation('{self.operator}', {self.operand!r})"


class Case(Expression):
    """
    CASE expression for conditional logic.

    Example:
        Case()
            .when(Field('age') < 18, Value('Minor'))
            .when(Field('age') < 65, Value('Adult'))
            .else_(Value('Senior'))
    """

    def __init__(self):
        """Initialize CASE expression."""
        self.conditions: List[tuple] = []
        self.else_value: Optional[Expression] = None

    def when(self, condition: Expression, value: Union[Expression, Any]) -> "Case":
        """
        Add WHEN clause.

        Args:
            condition: Condition expression
            value: Value to return when condition is true

        Returns:
            Self for chaining
        """
        self.conditions.append((condition, value))
        return self

    def else_(self, value: Union[Expression, Any]) -> "Case":
        """
        Add ELSE clause.

        Args:
            value: Default value

        Returns:
            Self for chaining
        """
        self.else_value = value
        return self

    def compile(self, db_type: DatabaseType) -> str:
        """Compile CASE expression to SQL."""
        parts = ["CASE"]

        for condition, value in self.conditions:
            if hasattr(condition, "compile"):
                cond_sql = condition.compile(db_type)
            else:
                cond_sql = str(condition)

            if hasattr(value, "compile"):
                val_sql = value.compile(db_type)
            else:
                val_sql = str(value)

            parts.append(f"WHEN {cond_sql} THEN {val_sql}")

        if self.else_value:
            if hasattr(self.else_value, "compile"):
                else_sql = self.else_value.compile(db_type)
            else:
                else_sql = str(self.else_value)
            parts.append(f"ELSE {else_sql}")

        parts.append("END")

        return " ".join(parts)

    def __repr__(self) -> str:
        return f"Case(conditions={len(self.conditions)}, has_else={self.else_value is not None})"


class Subquery(Expression):
    """
    Subquery expression.

    Example:
        Subquery(
            QueryBuilder('active_sessions')
                .select('user_id')
                .where({'status': 'active'})
        )
    """

    def __init__(self, query_builder: "QueryBuilder"):
        """
        Initialize subquery.

        Args:
            query_builder: QueryBuilder instance
        """
        self.query_builder = query_builder

    def compile(self, db_type: DatabaseType) -> str:
        """Compile subquery to SQL."""
        query = self.query_builder.compile()
        return f"({query.sql})"

    def __repr__(self) -> str:
        return f"Subquery({self.query_builder!r})"


class RawExpression(Expression):
    """
    Raw SQL expression that bypasses parameterization.

    WARNING: Use with caution! This class should ONLY be used for:
    - Database functions and keywords (e.g., COUNT(*), NOW(), CURRENT_TIMESTAMP)
    - Complex SQL expressions that can't be represented with other expression types
    - SQL fragments that are known to be safe

    NEVER use RawExpression with user input as it can lead to SQL injection!

    Example:
        # SAFE - Using with SQL keywords
        RawExpression('COUNT(*)')
        RawExpression('NOW()')
        RawExpression('CURRENT_TIMESTAMP')

        # SAFE - Using with database functions
        RawExpression('EXTRACT(YEAR FROM created_at)')

        # DANGEROUS - NEVER do this!
        # RawExpression(f"'{user_input}'")  # ❌ SQL INJECTION RISK!
    """

    def __init__(self, sql: str):
        """
        Initialize raw SQL expression.

        Args:
            sql: Raw SQL string

        Example:
            RawExpression('COUNT(*)')
            RawExpression('DATE_TRUNC(\\'day\\', created_at)')
        """
        self.sql = sql

    def compile(self, db_type: DatabaseType) -> str:
        """
        Return raw SQL as-is.

        Args:
            db_type: Database type (ignored for raw expressions)

        Returns:
            Raw SQL string unchanged
        """
        return self.sql

    def __repr__(self) -> str:
        return f"RawExpression({self.sql!r})"


__all__ = [
    "Expression",
    "Field",
    "Value",
    "Function",
    "BinaryOperation",
    "UnaryOperation",
    "Case",
    "Subquery",
    "RawExpression",
]
