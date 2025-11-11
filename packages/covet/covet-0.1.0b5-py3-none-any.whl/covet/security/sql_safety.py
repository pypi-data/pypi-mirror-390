"""
SQL Safety Utilities for CovetPy Framework

Provides validation and sanitization functions to prevent SQL injection attacks
while maintaining flexibility for legitimate dynamic SQL construction.

This module implements defense-in-depth security measures including:
- SQL identifier validation (table/column names)
- SQL literal escaping
- Query pattern validation
- Allowlist-based validation

Author: CovetPy Security Team
License: MIT
"""

import re
from enum import Enum
from typing import List, Optional, Set, Union


class SQLIdentifierType(str, Enum):
    """Types of SQL identifiers that can be validated."""

    TABLE = "table"
    COLUMN = "column"
    SCHEMA = "schema"
    INDEX = "index"
    CONSTRAINT = "constraint"


class SQLInjectionError(ValueError):
    """
    Raised when a potential SQL injection attempt is detected.

    This exception is raised when validation detects dangerous patterns
    or invalid characters in SQL identifiers or values.
    """

    pass


class SQLSafetyValidator:
    """
    Validates SQL identifiers and values to prevent SQL injection.

    This class provides comprehensive validation for SQL identifiers
    (table names, column names, etc.) to prevent SQL injection attacks
    while allowing legitimate use cases.

    Security Features:
        - Validates against SQL injection patterns
        - Checks for reserved keywords
        - Enforces naming conventions
        - Supports allowlist validation
        - Detects dangerous SQL constructs

    Example:
        validator = SQLSafetyValidator()

        # Validate table name
        if not validator.is_valid_identifier("users"):
            raise SQLInjectionError("Invalid table name")

        # Validate with allowlist
        validator.validate_table_name("users", allowlist={"users", "posts"})
    """

    # SQL injection patterns that should never appear in identifiers
    DANGEROUS_PATTERNS = [
        r"--",  # SQL comments
        r"/\*",  # Block comment start
        r"\*/",  # Block comment end
        r";",  # Statement terminator
        r"\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b",
        r"'",  # Single quotes
        r'"',  # Double quotes (when not used for escaping)
        r"\\",  # Backslash
        r"\x00",  # Null byte
        r"\b(OR|AND)\b.*=",  # Boolean injection patterns
    ]

    # Valid identifier pattern: alphanumeric, underscore, starts with letter
    VALID_IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")

    # Maximum length for identifiers (most databases support 63-128)
    MAX_IDENTIFIER_LENGTH = 63

    # Common SQL reserved keywords that should be avoided
    RESERVED_KEYWORDS = {
        "SELECT",
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TABLE",
        "INDEX",
        "VIEW",
        "PROCEDURE",
        "FUNCTION",
        "TRIGGER",
        "DATABASE",
        "SCHEMA",
        "USER",
        "GRANT",
        "REVOKE",
        "EXECUTE",
        "UNION",
        "JOIN",
        "WHERE",
        "HAVING",
        "GROUP",
        "ORDER",
        "BY",
        "FROM",
        "INTO",
        "VALUES",
        "SET",
        "AND",
        "OR",
        "NOT",
        "IN",
        "EXISTS",
        "BETWEEN",
        "LIKE",
        "IS",
        "NULL",
        "TRUE",
        "FALSE",
        "CASE",
        "WHEN",
        "THEN",
        "ELSE",
        "END",
        "AS",
        "ON",
        "USING",
    }

    def __init__(
        self,
        strict_mode: bool = True,
        allow_reserved_keywords: bool = False,
        custom_patterns: Optional[List[str]] = None,
    ):
        """
        Initialize SQL safety validator.

        Args:
            strict_mode: If True, apply strict validation rules
            allow_reserved_keywords: If True, allow SQL reserved keywords as identifiers
            custom_patterns: Additional regex patterns to check for
        """
        self.strict_mode = strict_mode
        self.allow_reserved_keywords = allow_reserved_keywords
        self.dangerous_patterns = self.DANGEROUS_PATTERNS.copy()

        if custom_patterns:
            self.dangerous_patterns.extend(custom_patterns)

        # Compile patterns for performance
        self.compiled_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.dangerous_patterns
        ]

    def is_valid_identifier(
        self, identifier: str, identifier_type: SQLIdentifierType = SQLIdentifierType.TABLE
    ) -> bool:
        """
        Check if an identifier is valid and safe.

        Args:
            identifier: The identifier to validate
            identifier_type: Type of identifier (table, column, etc.)

        Returns:
            True if valid and safe, False otherwise
        """
        if not identifier:
            return False

        # Check length
        if len(identifier) > self.MAX_IDENTIFIER_LENGTH:
            return False

        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            if pattern.search(identifier):
                return False

        # Check if it matches valid identifier pattern
        if not self.VALID_IDENTIFIER_PATTERN.match(identifier):
            return False

        # Check for reserved keywords in strict mode
        if self.strict_mode and not self.allow_reserved_keywords:
            if identifier.upper() in self.RESERVED_KEYWORDS:
                return False

        return True

    def validate_identifier(
        self,
        identifier: str,
        identifier_type: SQLIdentifierType = SQLIdentifierType.TABLE,
        allowlist: Optional[Set[str]] = None,
    ) -> str:
        """
        Validate an identifier and return it if safe, raise exception otherwise.

        Args:
            identifier: The identifier to validate
            identifier_type: Type of identifier
            allowlist: Optional set of allowed identifiers

        Returns:
            The validated identifier

        Raises:
            SQLInjectionError: If validation fails
        """
        # Check allowlist first if provided
        if allowlist is not None:
            if identifier not in allowlist:
                raise SQLInjectionError(
                    f"Identifier '{identifier}' is not in allowlist for {identifier_type.value}"
                )
            return identifier

        # Perform standard validation
        if not self.is_valid_identifier(identifier, identifier_type):
            raise SQLInjectionError(
                f"Invalid or unsafe {identifier_type.value} identifier: '{identifier}'"
            )

        return identifier

    def validate_table_name(self, table_name: str, allowlist: Optional[Set[str]] = None) -> str:
        """
        Validate a table name.

        Args:
            table_name: Table name to validate
            allowlist: Optional set of allowed table names

        Returns:
            Validated table name

        Raises:
            SQLInjectionError: If validation fails
        """
        return self.validate_identifier(table_name, SQLIdentifierType.TABLE, allowlist)

    def validate_column_name(self, column_name: str, allowlist: Optional[Set[str]] = None) -> str:
        """
        Validate a column name.

        Args:
            column_name: Column name to validate
            allowlist: Optional set of allowed column names

        Returns:
            Validated column name

        Raises:
            SQLInjectionError: If validation fails
        """
        return self.validate_identifier(column_name, SQLIdentifierType.COLUMN, allowlist)

    def validate_identifier_list(
        self,
        identifiers: List[str],
        identifier_type: SQLIdentifierType = SQLIdentifierType.COLUMN,
        allowlist: Optional[Set[str]] = None,
    ) -> List[str]:
        """
        Validate a list of identifiers.

        Args:
            identifiers: List of identifiers to validate
            identifier_type: Type of identifiers
            allowlist: Optional set of allowed identifiers

        Returns:
            List of validated identifiers

        Raises:
            SQLInjectionError: If any validation fails
        """
        return [
            self.validate_identifier(identifier, identifier_type, allowlist)
            for identifier in identifiers
        ]

    def escape_like_pattern(self, pattern: str, escape_char: str = "\\") -> str:
        """
        Escape special characters in a LIKE pattern.

        Args:
            pattern: The LIKE pattern to escape
            escape_char: The escape character to use

        Returns:
            Escaped pattern
        """
        # Escape the escape character first
        pattern = pattern.replace(escape_char, escape_char + escape_char)
        # Escape LIKE wildcards
        pattern = pattern.replace("%", escape_char + "%")
        pattern = pattern.replace("_", escape_char + "_")
        return pattern

    def is_safe_order_by(self, order_clause: str) -> bool:
        """
        Validate ORDER BY clause.

        Args:
            order_clause: ORDER BY clause to validate

        Returns:
            True if safe, False otherwise
        """
        # Remove whitespace
        clause = order_clause.strip()

        # Check for empty clause
        if not clause:
            return False

        # Split by comma for multiple columns
        parts = clause.split(",")

        for part in parts:
            part = part.strip()

            # Split column name and direction
            tokens = part.split()

            if not tokens:
                return False

            # First token should be valid identifier
            column = tokens[0]
            if not self.is_valid_identifier(column, SQLIdentifierType.COLUMN):
                return False

            # Optional second token should be ASC or DESC
            if len(tokens) > 1:
                direction = tokens[1].upper()
                if direction not in ("ASC", "DESC"):
                    return False

            # No more than 2 tokens per part
            if len(tokens) > 2:
                return False

        return True

    def validate_order_by(self, order_clause: str) -> str:
        """
        Validate and return ORDER BY clause.

        Args:
            order_clause: ORDER BY clause to validate

        Returns:
            Validated ORDER BY clause

        Raises:
            SQLInjectionError: If validation fails
        """
        if not self.is_safe_order_by(order_clause):
            raise SQLInjectionError(f"Unsafe ORDER BY clause: '{order_clause}'")
        return order_clause


# Global validator instance with strict defaults
_default_validator = SQLSafetyValidator(strict_mode=True)


# Convenience functions that use the default validator
def validate_table_name(table_name: str, allowlist: Optional[Set[str]] = None) -> str:
    """
    Validate a table name using default validator.

    Args:
        table_name: Table name to validate
        allowlist: Optional set of allowed table names

    Returns:
        Validated table name

    Raises:
        SQLInjectionError: If validation fails
    """
    return _default_validator.validate_table_name(table_name, allowlist)


def validate_column_name(column_name: str, allowlist: Optional[Set[str]] = None) -> str:
    """
    Validate a column name using default validator.

    Args:
        column_name: Column name to validate
        allowlist: Optional set of allowed column names

    Returns:
        Validated column name

    Raises:
        SQLInjectionError: If validation fails
    """
    return _default_validator.validate_column_name(column_name, allowlist)


def validate_identifier(
    identifier: str,
    identifier_type: SQLIdentifierType = SQLIdentifierType.TABLE,
    allowlist: Optional[Set[str]] = None,
) -> str:
    """
    Validate an identifier using default validator.

    Args:
        identifier: Identifier to validate
        identifier_type: Type of identifier
        allowlist: Optional set of allowed identifiers

    Returns:
        Validated identifier

    Raises:
        SQLInjectionError: If validation fails
    """
    return _default_validator.validate_identifier(identifier, identifier_type, allowlist)


def is_valid_identifier(identifier: str) -> bool:
    """
    Check if identifier is valid using default validator.

    Args:
        identifier: Identifier to check

    Returns:
        True if valid, False otherwise
    """
    return _default_validator.is_valid_identifier(identifier)


def validate_order_by(order_clause: str) -> str:
    """
    Validate ORDER BY clause using default validator.

    Args:
        order_clause: ORDER BY clause to validate

    Returns:
        Validated ORDER BY clause

    Raises:
        SQLInjectionError: If validation fails
    """
    return _default_validator.validate_order_by(order_clause)


__all__ = [
    "SQLSafetyValidator",
    "SQLIdentifierType",
    "SQLInjectionError",
    "validate_table_name",
    "validate_column_name",
    "validate_identifier",
    "is_valid_identifier",
    "validate_order_by",
]
