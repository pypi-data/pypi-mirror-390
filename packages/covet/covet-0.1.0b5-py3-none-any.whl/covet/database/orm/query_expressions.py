"""
ORM Query Expressions - F() and Q() Objects

Django-compatible query expressions for database-side operations and complex queries.

F() expressions allow database-side field operations:
    # Update counter atomically
    await Post.objects.filter(id=1).update(views=F('views') + 1)

    # Filter using field comparisons
    posts = await Post.objects.filter(views__gt=F('likes') * 2).all()

Q() objects enable complex query composition:
    # Complex OR and AND combinations
    results = await User.objects.filter(
        Q(username__startswith='admin') | Q(email__endswith='@admin.com')
    ).all()

    # Nested conditions
    complex_filter = Q(is_active=True) & (Q(role='admin') | Q(role='moderator'))
    users = await User.objects.filter(complex_filter).all()

Author: Senior Python Engineer with Django expertise
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union


class F:
    """
    F() expression for database-side field references and operations.

    Allows referencing model fields in queries and updates, enabling
    database-side calculations without loading data into Python.

    Example:
        # Atomic increment
        await Article.objects.filter(id=1).update(views=F('views') + 1)

        # Field comparisons
        expensive_items = await Product.objects.filter(
            price__gt=F('cost') * Decimal('1.5')
        ).all()

        # Multiple operations
        await Order.objects.update(
            total=F('subtotal') + F('tax') - F('discount')
        )
    """

    def __init__(self, field_name: str):
        """
        Initialize F expression.

        Args:
            field_name: Name of the model field to reference
        """
        self.field_name = field_name
        self._operations: List[tuple] = []  # (operator, value)

    def __add__(self, other: Union["F", Any]) -> "F":
        """Add operation (F('views') + 1)."""
        result = self._clone()
        result._operations.append(("+", other))
        return result

    def __sub__(self, other: Union["F", Any]) -> "F":
        """Subtract operation (F('total') - F('discount'))."""
        result = self._clone()
        result._operations.append(("-", other))
        return result

    def __mul__(self, other: Union["F", Any]) -> "F":
        """Multiply operation (F('price') * 2)."""
        result = self._clone()
        result._operations.append(("*", other))
        return result

    def __truediv__(self, other: Union["F", Any]) -> "F":
        """Divide operation (F('total') / F('quantity'))."""
        result = self._clone()
        result._operations.append(("/", other))
        return result

    def __mod__(self, other: Union["F", Any]) -> "F":
        """Modulo operation (F('id') % 2)."""
        result = self._clone()
        result._operations.append(("%", other))
        return result

    def __pow__(self, other: Union["F", Any]) -> "F":
        """Power operation (F('base') ** 2)."""
        result = self._clone()
        result._operations.append(("**", other))
        return result

    def __neg__(self) -> "F":
        """Negate operation (-F('balance'))."""
        result = self._clone()
        result._operations.append(("NEG", None))
        return result

    def _clone(self) -> "F":
        """Create a copy of this F expression."""
        clone = F(self.field_name)
        clone._operations = self._operations.copy()
        return clone

    def to_sql(self, dialect: str = "postgresql") -> tuple[str, List[Any]]:
        """
        Convert F expression to SQL.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)

        Returns:
            Tuple of (SQL expression, parameters)
        """
        sql = self.field_name
        params = []

        for operator, value in self._operations:
            if operator == "NEG":
                sql = f"-({sql})"
            elif isinstance(value, F):
                # Another F expression
                value_sql, value_params = value.to_sql(dialect)
                sql = f"({sql} {operator} {value_sql})"
                params.extend(value_params)
            else:
                # Literal value - use placeholder
                if dialect == "postgresql":
                    placeholder = f"${len(params) + 1}"
                elif dialect == "mysql":
                    placeholder = "%s"
                else:  # sqlite
                    placeholder = "?"

                sql = f"({sql} {operator} {placeholder})"
                params.append(value)

        return sql, params

    def __repr__(self) -> str:
        """String representation."""
        ops_repr = "".join(f" {op} {val}" for op, val in self._operations)
        return f"<F: {self.field_name}{ops_repr}>"


class Q:
    """
    Q() object for complex query composition.

    Enables building complex queries with AND, OR, and NOT logic that can
    be composed and reused.

    Example:
        # OR condition
        Q(status='active') | Q(status='pending')

        # AND condition
        Q(is_published=True) & Q(views__gt=1000)

        # NOT condition
        ~Q(status='deleted')

        # Complex nested conditions
        (Q(category='tech') & Q(is_featured=True)) | Q(views__gt=10000)
    """

    # Connector types
    AND = "AND"
    OR = "OR"

    def __init__(self, *args, **kwargs):
        """
        Initialize Q object.

        Args:
            *args: Child Q objects for nested conditions
            **kwargs: Field lookup conditions

        Example:
            Q(username='admin')
            Q(age__gte=18, is_active=True)
            Q(Q(role='admin') | Q(role='moderator'))
        """
        self.children: List[Union[tuple, "Q"]] = list(args)
        self.children.extend(kwargs.items())
        self.connector = self.AND
        self.negated = False

    def __and__(self, other: "Q") -> "Q":
        """
        Combine Q objects with AND.

        Example:
            Q(is_active=True) & Q(role='admin')
        """
        return self._combine(other, self.AND)

    def __or__(self, other: "Q") -> "Q":
        """
        Combine Q objects with OR.

        Example:
            Q(status='draft') | Q(status='pending')
        """
        return self._combine(other, self.OR)

    def __invert__(self) -> "Q":
        """
        Negate Q object (NOT).

        Example:
            ~Q(is_deleted=True)
        """
        clone = self._clone()
        clone.negated = not clone.negated
        return clone

    def _combine(self, other: "Q", connector: str) -> "Q":
        """
        Combine two Q objects with given connector.

        Args:
            other: Another Q object
            connector: AND or OR

        Returns:
            New combined Q object
        """
        if not isinstance(other, Q):
            raise TypeError(f"Cannot combine Q with {type(other)}")

        # If self is empty, return other
        if not self.children:
            return other._clone()

        # If other is empty, return self
        if not other.children:
            return self._clone()

        # Create new Q with combined children
        obj = Q()
        obj.connector = connector
        obj.children = [self._clone(), other._clone()]
        return obj

    def _clone(self) -> "Q":
        """Create a deep copy of this Q object."""
        clone = Q()
        clone.children = self.children.copy()
        clone.connector = self.connector
        clone.negated = self.negated
        return clone

    def to_sql(self, adapter, param_index: int = 1) -> tuple[str, List[Any], int]:
        """
        Convert Q object to SQL WHERE clause.

        Args:
            adapter: Database adapter (for placeholder style)
            param_index: Starting parameter index

        Returns:
            Tuple of (SQL string, parameters, next_param_index)
        """
        if not self.children:
            return "", [], param_index

        conditions = []
        params = []

        for child in self.children:
            if isinstance(child, Q):
                # Nested Q object
                child_sql, child_params, param_index = child.to_sql(adapter, param_index)
                if child_sql:
                    conditions.append(f"({child_sql})")
                    params.extend(child_params)
            else:
                # Field lookup tuple
                field_lookup, value = child
                condition_sql, condition_params, param_index = self._build_lookup_sql(
                    adapter, field_lookup, value, param_index
                )
                conditions.append(condition_sql)
                params.extend(condition_params)

        # Join conditions with connector
        connector_str = f" {self.connector} "
        sql = connector_str.join(conditions)

        # Apply negation if needed
        if self.negated:
            sql = f"NOT ({sql})"

        return sql, params, param_index

    def _build_lookup_sql(
        self, adapter, lookup: str, value: Any, param_index: int
    ) -> tuple[str, List[Any], int]:
        """
        Build SQL for a single field lookup.

        Args:
            adapter: Database adapter
            lookup: Field lookup string (e.g., 'age__gte')
            value: Lookup value
            param_index: Current parameter index

        Returns:
            Tuple of (SQL, parameters, next_param_index)
        """
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        # Determine placeholder style
        if isinstance(adapter, PostgreSQLAdapter):
            get_placeholder = lambda idx: f"${idx}"
        elif isinstance(adapter, MySQLAdapter):
            get_placeholder = lambda idx: "%s"
        else:  # SQLite
            get_placeholder = lambda idx: "?"

        # Parse lookup
        parts = lookup.split("__")
        field = parts[0]
        lookup_type = parts[1] if len(parts) > 1 else "exact"

        # Handle F expressions
        if isinstance(value, F):
            value_sql, value_params = value.to_sql(
                "postgresql"
                if isinstance(adapter, PostgreSQLAdapter)
                else "mysql" if isinstance(adapter, MySQLAdapter) else "sqlite"
            )
            params = value_params
            next_index = param_index + len(value_params)
        else:
            value_sql = get_placeholder(param_index)
            params = [value]
            next_index = param_index + 1

        # Build condition based on lookup type
        if lookup_type == "exact":
            if value is None:
                return f"{field} IS NULL", [], param_index
            return f"{field} = {value_sql}", params, next_index

        elif lookup_type == "iexact":
            return f"LOWER({field}) = LOWER({value_sql})", params, next_index

        elif lookup_type == "contains":
            if isinstance(adapter, MySQLAdapter):
                # MySQL increments differently
                return f"{field} LIKE %s", [f"%{value}%"], param_index + 1
            elif isinstance(adapter, SQLiteAdapter):
                return f"{field} LIKE ?", [f"%{value}%"], param_index + 1
            else:  # PostgreSQL
                return f"{field} LIKE ${param_index}", [f"%{value}%"], param_index + 1

        elif lookup_type == "icontains":
            if isinstance(adapter, MySQLAdapter):
                return f"LOWER({field}) LIKE %s", [f"%{value.lower()}%"], param_index + 1
            elif isinstance(adapter, SQLiteAdapter):
                return f"LOWER({field}) LIKE ?", [f"%{value.lower()}%"], param_index + 1
            else:  # PostgreSQL
                return (
                    f"LOWER({field}) LIKE ${param_index}",
                    [f"%{value.lower()}%"],
                    param_index + 1,
                )

        elif lookup_type == "gt":
            return f"{field} > {value_sql}", params, next_index

        elif lookup_type == "gte":
            return f"{field} >= {value_sql}", params, next_index

        elif lookup_type == "lt":
            return f"{field} < {value_sql}", params, next_index

        elif lookup_type == "lte":
            return f"{field} <= {value_sql}", params, next_index

        elif lookup_type == "in":
            if not value:
                return "FALSE", [], param_index
            placeholders = [get_placeholder(param_index + i) for i in range(len(value))]
            return f"{field} IN ({', '.join(placeholders)})", list(value), param_index + len(value)

        elif lookup_type == "isnull":
            if value:
                return f"{field} IS NULL", [], param_index
            else:
                return f"{field} IS NOT NULL", [], param_index

        elif lookup_type == "startswith":
            if isinstance(adapter, MySQLAdapter):
                return f"{field} LIKE %s", [f"{value}%"], param_index + 1
            elif isinstance(adapter, SQLiteAdapter):
                return f"{field} LIKE ?", [f"{value}%"], param_index + 1
            else:  # PostgreSQL
                return f"{field} LIKE ${param_index}", [f"{value}%"], param_index + 1

        elif lookup_type == "endswith":
            if isinstance(adapter, MySQLAdapter):
                return f"{field} LIKE %s", [f"%{value}"], param_index + 1
            elif isinstance(adapter, SQLiteAdapter):
                return f"{field} LIKE ?", [f"%{value}"], param_index + 1
            else:  # PostgreSQL
                return f"{field} LIKE ${param_index}", [f"%{value}"], param_index + 1

        else:
            raise ValueError(f"Unsupported lookup type: {lookup_type}")

    def __repr__(self) -> str:
        """String representation."""
        neg = "~" if self.negated else ""
        if len(self.children) == 1:
            return f"{neg}Q({self.children[0]})"
        return f"{neg}Q({self.connector}: {self.children})"


__all__ = ["F", "Q"]
