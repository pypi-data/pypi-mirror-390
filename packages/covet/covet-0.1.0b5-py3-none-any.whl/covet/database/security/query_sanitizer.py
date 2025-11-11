"""
Query Sanitization Module

Provides utilities for sanitizing query parameters and preventing SQL injection
through parameter validation and escaping.

Author: CovetPy Security Team
"""

import re
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union


class QuerySanitizer:
    """
    Query sanitizer for SQL parameters.

    Provides methods to validate and sanitize query parameters to prevent
    SQL injection attacks.
    """

    # Dangerous patterns in string values
    DANGEROUS_PATTERNS = [
        re.compile(r"'.*?--"),  # Quote followed by comment
        re.compile(r"'.*?;.*?'"),  # Quote with statement separator
        re.compile(r"'.*?\bUNION\b", re.IGNORECASE),
        re.compile(r"'.*?\bSELECT\b", re.IGNORECASE),
        re.compile(r"'.*?\bINSERT\b", re.IGNORECASE),
        re.compile(r"'.*?\bUPDATE\b", re.IGNORECASE),
        re.compile(r"'.*?\bDELETE\b", re.IGNORECASE),
        re.compile(r"'.*?\bDROP\b", re.IGNORECASE),
    ]

    @staticmethod
    def sanitize_string(value: str) -> str:
        """
        Sanitize a string value for use in SQL.

        Note: This should NOT be used as a replacement for parameterized queries.
        Always use parameterized queries when possible.

        Args:
            value: String to sanitize

        Returns:
            Sanitized string

        Raises:
            ValueError: If the string contains dangerous patterns
        """
        if not isinstance(value, str):
            raise TypeError(f"Expected string, got {type(value).__name__}")

        # Check for dangerous patterns
        for pattern in QuerySanitizer.DANGEROUS_PATTERNS:
            if pattern.search(value):
                raise ValueError(f"String contains dangerous SQL pattern: {pattern.pattern}")

        # Escape single quotes by doubling them (SQL standard)
        return value.replace("'", "''")

    @staticmethod
    def validate_integer(value: Any) -> int:
        """
        Validate and convert to integer.

        Args:
            value: Value to validate

        Returns:
            Integer value

        Raises:
            ValueError: If value cannot be converted to integer
        """
        try:
            return int(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid integer value: {value}") from e

    @staticmethod
    def validate_float(value: Any) -> float:
        """
        Validate and convert to float.

        Args:
            value: Value to validate

        Returns:
            Float value

        Raises:
            ValueError: If value cannot be converted to float
        """
        try:
            return float(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid float value: {value}") from e

    @staticmethod
    def validate_boolean(value: Any) -> bool:
        """
        Validate and convert to boolean.

        Args:
            value: Value to validate

        Returns:
            Boolean value
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ("true", "1", "yes", "on"):
                return True
            elif value.lower() in ("false", "0", "no", "off"):
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        raise ValueError(f"Invalid boolean value: {value}")

    @staticmethod
    def validate_param_type(value: Any) -> Any:
        """
        Validate parameter type for safe SQL usage.

        Args:
            value: Parameter value

        Returns:
            Validated value

        Raises:
            TypeError: If value type is not safe for SQL
        """
        # Safe types for SQL parameters
        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float, Decimal)):
            return value

        if isinstance(value, str):
            # Additional string validation
            if len(value) > 10000:  # Prevent DOS via huge strings
                raise ValueError("String parameter too long (max 10000 characters)")
            return value

        if isinstance(value, (datetime, date, time)):
            return value

        if isinstance(value, bytes):
            return value

        # Reject unsafe types
        raise TypeError(
            f"Unsafe parameter type: {type(value).__name__}. "
            "Only None, bool, int, float, Decimal, str, datetime, date, time, and bytes are allowed."
        )


def sanitize_query_params(params: Union[Tuple, List, Dict]) -> Union[Tuple, List, Dict]:
    """
    Sanitize query parameters.

    Validates all parameters are safe types for SQL queries.

    Args:
        params: Query parameters (tuple, list, or dict)

    Returns:
        Sanitized parameters

    Raises:
        TypeError: If any parameter is unsafe
        ValueError: If any parameter is invalid

    Examples:
        >>> sanitize_query_params((1, 'test', True))
        (1, 'test', True)
        >>> sanitize_query_params({'id': 1, 'name': 'test'})
        {'id': 1, 'name': 'test'}
    """
    if isinstance(params, (tuple, list)):
        return type(params)(QuerySanitizer.validate_param_type(p) for p in params)
    elif isinstance(params, dict):
        return {k: QuerySanitizer.validate_param_type(v) for k, v in params.items()}
    else:
        raise TypeError(
            f"Invalid params type: {type(params).__name__}. " "Must be tuple, list, or dict."
        )


def escape_like_pattern(pattern: str) -> str:
    """
    Escape special characters in LIKE patterns.

    Escapes %, _, [, ], and \\ characters to prevent LIKE injection.

    Args:
        pattern: LIKE pattern to escape

    Returns:
        Escaped pattern

    Examples:
        >>> escape_like_pattern("user%")
        'user\\\\%'
        >>> escape_like_pattern("user_test")
        'user\\\\_test'
    """
    if not isinstance(pattern, str):
        raise TypeError("LIKE pattern must be a string")

    # Escape special LIKE characters
    pattern = pattern.replace("\\", "\\\\")  # Escape backslash first
    pattern = pattern.replace("%", "\\%")
    pattern = pattern.replace("_", "\\_")
    pattern = pattern.replace("[", "\\[")
    pattern = pattern.replace("]", "\\]")

    return pattern


def validate_limit_offset(
    limit: Optional[int] = None, offset: Optional[int] = None
) -> Tuple[Optional[int], Optional[int]]:
    """
    Validate LIMIT and OFFSET values.

    Args:
        limit: LIMIT value
        offset: OFFSET value

    Returns:
        Validated (limit, offset) tuple

    Raises:
        ValueError: If values are invalid

    Examples:
        >>> validate_limit_offset(10, 20)
        (10, 20)
        >>> validate_limit_offset(-1, 0)
        Traceback (most recent call last):
        ValueError: LIMIT must be non-negative
    """
    if limit is not None:
        try:
            limit = int(limit)
            if limit < 0:
                raise ValueError("LIMIT must be non-negative")
            if limit > 1000000:  # Prevent DOS
                raise ValueError("LIMIT too large (max 1000000)")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid LIMIT value: {limit}") from e

    if offset is not None:
        try:
            offset = int(offset)
            if offset < 0:
                raise ValueError("OFFSET must be non-negative")
            if offset > 1000000:  # Prevent DOS
                raise ValueError("OFFSET too large (max 1000000)")
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid OFFSET value: {offset}") from e

    return limit, offset


def validate_order_by(
    column_name: str,
    direction: str = "ASC",
    allowed_columns: Optional[List[str]] = None,
) -> Tuple[str, str]:
    """
    Validate ORDER BY parameters.

    Args:
        column_name: Column to order by
        direction: Sort direction ('ASC' or 'DESC')
        allowed_columns: Whitelist of allowed column names

    Returns:
        Validated (column_name, direction) tuple

    Raises:
        ValueError: If parameters are invalid

    Examples:
        >>> validate_order_by('created_at', 'DESC', ['id', 'created_at'])
        ('created_at', 'DESC')
        >>> validate_order_by('created_at', 'INVALID')
        Traceback (most recent call last):
        ValueError: Invalid ORDER BY direction. Must be ASC or DESC
    """
    # Validate direction
    direction = direction.upper()
    if direction not in ("ASC", "DESC"):
        raise ValueError("Invalid ORDER BY direction. Must be ASC or DESC")

    # Validate column name against whitelist if provided
    if allowed_columns is not None:
        if column_name not in allowed_columns:
            raise ValueError(f"Column '{column_name}' not in allowed columns: {allowed_columns}")

    # Additional validation of column name
    from .sql_validator import validate_column_name

    column_name = validate_column_name(column_name)

    return column_name, direction


__all__ = [
    "QuerySanitizer",
    "sanitize_query_params",
    "escape_like_pattern",
    "validate_limit_offset",
    "validate_order_by",
]
