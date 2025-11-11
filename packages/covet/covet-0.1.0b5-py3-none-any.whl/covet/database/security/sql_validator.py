"""
SQL Identifier Validation Module

Provides comprehensive validation for SQL identifiers (table names, column names, etc.)
to prevent SQL injection attacks. Implements strict whitelisting and validation rules.

Security Features:
- Alphanumeric + underscore validation
- Length restrictions
- Reserved keyword detection
- SQL injection pattern detection
- Database-specific identifier rules

Author: CovetPy Security Team
"""

import re
from enum import Enum
from typing import List, Optional, Set


class SQLIdentifierError(Exception):
    """Base exception for SQL identifier validation errors."""


class InvalidIdentifierError(SQLIdentifierError):
    """Raised when an identifier contains invalid characters or patterns."""


class IdentifierTooLongError(SQLIdentifierError):
    """Raised when an identifier exceeds maximum length."""


class IllegalCharacterError(SQLIdentifierError):
    """Raised when an identifier contains illegal characters."""


class DatabaseDialect(Enum):
    """Supported database dialects with different identifier rules."""

    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    GENERIC = "generic"


# SQL Reserved Keywords - Common across databases
SQL_RESERVED_KEYWORDS: Set[str] = {
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
    "TRIGGER",
    "PROCEDURE",
    "FUNCTION",
    "DATABASE",
    "SCHEMA",
    "FROM",
    "WHERE",
    "JOIN",
    "INNER",
    "OUTER",
    "LEFT",
    "RIGHT",
    "FULL",
    "CROSS",
    "ON",
    "USING",
    "GROUP",
    "BY",
    "HAVING",
    "ORDER",
    "LIMIT",
    "OFFSET",
    "UNION",
    "INTERSECT",
    "EXCEPT",
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
    "AS",
    "DISTINCT",
    "ALL",
    "ANY",
    "SOME",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
    "CAST",
    "CONVERT",
    "EXTRACT",
    "SUBSTRING",
    "TRIM",
    "COALESCE",
    "PRIMARY",
    "FOREIGN",
    "KEY",
    "REFERENCES",
    "CONSTRAINT",
    "UNIQUE",
    "CHECK",
    "DEFAULT",
    "CASCADE",
    "RESTRICT",
    "SET",
    "NULL",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "SAVEPOINT",
    "TRANSACTION",
    "GRANT",
    "REVOKE",
    "DENY",
    "EXECUTE",
    "ADMIN",
    "USAGE",
}

# SQL Injection attack patterns
SQL_INJECTION_PATTERNS: List[re.Pattern] = [
    re.compile(r"--"),  # SQL comment
    re.compile(r"/\*"),  # Multi-line comment start
    re.compile(r"\*/"),  # Multi-line comment end
    re.compile(r";"),  # Statement terminator
    re.compile(r"\bxp_\w+"),  # Extended stored procedures (MSSQL)
    re.compile(r"\bsp_\w+"),  # System stored procedures
    re.compile(r"\bEXEC\b", re.IGNORECASE),
    re.compile(r"\bEXECUTE\b", re.IGNORECASE),
    re.compile(r"\bUNION\b", re.IGNORECASE),
    re.compile(r"\bCHAR\b", re.IGNORECASE),
    re.compile(r"\bDECLARE\b", re.IGNORECASE),
    re.compile(r"0x[0-9a-f]+", re.IGNORECASE),  # Hex encoding
    re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]"),  # Control characters
]

# Maximum identifier lengths per database
MAX_IDENTIFIER_LENGTH = {
    DatabaseDialect.POSTGRESQL: 63,
    DatabaseDialect.MYSQL: 64,
    DatabaseDialect.SQLITE: 1024,
    DatabaseDialect.GENERIC: 64,
}


def validate_identifier(
    identifier: str,
    max_length: Optional[int] = None,
    allow_dots: bool = False,
    dialect: DatabaseDialect = DatabaseDialect.GENERIC,
) -> str:
    """
    Validate a SQL identifier (table name, column name, etc.).

    This is the primary defense against SQL injection in identifier positions.
    Uses strict whitelisting approach.

    Args:
        identifier: The identifier to validate
        max_length: Maximum allowed length (defaults to dialect-specific)
        allow_dots: Whether to allow dots (for schema.table notation)
        dialect: Database dialect for specific validation rules

    Returns:
        The validated identifier (stripped and lowercased)

    Raises:
        InvalidIdentifierError: If identifier is invalid
        IdentifierTooLongError: If identifier is too long
        IllegalCharacterError: If identifier contains illegal characters

    Security:
        - Only allows alphanumeric characters and underscores
        - Optionally allows dots for qualified names
        - Checks against reserved keywords
        - Detects SQL injection patterns
        - Enforces length limits

    Examples:
        >>> validate_identifier("users")
        'users'
        >>> validate_identifier("user_profiles")
        'user_profiles'
        >>> validate_identifier("public.users", allow_dots=True)
        'public.users'
        >>> validate_identifier("users; DROP TABLE users--")
        Traceback (most recent call last):
        InvalidIdentifierError: Identifier contains SQL injection pattern
    """
    if not identifier:
        raise InvalidIdentifierError("Identifier cannot be empty")

    # Strip whitespace
    identifier = identifier.strip()

    # Check length
    max_len = max_length or MAX_IDENTIFIER_LENGTH[dialect]
    if len(identifier) > max_len:
        raise IdentifierTooLongError(
            f"Identifier '{identifier}' exceeds maximum length of {max_len} characters"
        )

    # Check for SQL injection patterns
    for pattern in SQL_INJECTION_PATTERNS:
        if pattern.search(identifier):
            raise InvalidIdentifierError(
                f"Identifier '{identifier}' contains SQL injection pattern: {pattern.pattern}"
            )

    # Validate character set
    if allow_dots:
        # Allow letters, digits, underscores, and dots
        if not re.match(r"^[a-zA-Z0-9_\.]+$", identifier):
            raise IllegalCharacterError(
                f"Identifier '{identifier}' contains illegal characters. "
                "Only alphanumeric, underscore, and dots are allowed."
            )

        # Validate each part if dots are present
        if "." in identifier:
            parts = identifier.split(".")
            if len(parts) > 3:  # catalog.schema.table is max
                raise InvalidIdentifierError(
                    f"Identifier '{identifier}' has too many parts (max 3: catalog.schema.table)"
                )
            for part in parts:
                if not part:
                    raise InvalidIdentifierError(f"Identifier '{identifier}' has empty parts")
                validate_identifier(part, max_length=max_len, allow_dots=False, dialect=dialect)
    else:
        # Allow only letters, digits, and underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", identifier):
            raise IllegalCharacterError(
                f"Identifier '{identifier}' contains illegal characters. "
                "Only alphanumeric and underscore are allowed."
            )

    # Must start with letter or underscore
    if not re.match(r"^[a-zA-Z_]", identifier):
        raise InvalidIdentifierError(
            f"Identifier '{identifier}' must start with a letter or underscore"
        )

    # Check against reserved keywords
    identifier_upper = identifier.upper()
    if not allow_dots and identifier_upper in SQL_RESERVED_KEYWORDS:
        raise InvalidIdentifierError(f"Identifier '{identifier}' is a SQL reserved keyword")

    # Additional database-specific validation
    if dialect == DatabaseDialect.MYSQL:
        # MySQL allows backticks but we don't allow them in input
        if "`" in identifier:
            raise IllegalCharacterError("Backticks are not allowed in identifiers")

    elif dialect == DatabaseDialect.POSTGRESQL:
        # PostgreSQL folds unquoted identifiers to lowercase
        # We return lowercase for consistency
        if not allow_dots:
            identifier = identifier.lower()

    return identifier


def validate_table_name(table_name: str, dialect: DatabaseDialect = DatabaseDialect.GENERIC) -> str:
    """
    Validate a table name.

    Args:
        table_name: Table name to validate
        dialect: Database dialect

    Returns:
        Validated table name

    Raises:
        SQLIdentifierError: If validation fails

    Examples:
        >>> validate_table_name("users")
        'users'
        >>> validate_table_name("user_accounts")
        'user_accounts'
    """
    return validate_identifier(table_name, allow_dots=False, dialect=dialect)


def validate_column_name(
    column_name: str, dialect: DatabaseDialect = DatabaseDialect.GENERIC
) -> str:
    """
    Validate a column name.

    Args:
        column_name: Column name to validate
        dialect: Database dialect

    Returns:
        Validated column name

    Raises:
        SQLIdentifierError: If validation fails

    Examples:
        >>> validate_column_name("user_id")
        'user_id'
        >>> validate_column_name("email_address")
        'email_address'
    """
    return validate_identifier(column_name, allow_dots=False, dialect=dialect)


def validate_schema_name(
    schema_name: str, dialect: DatabaseDialect = DatabaseDialect.GENERIC
) -> str:
    """
    Validate a schema/database name.

    Args:
        schema_name: Schema name to validate
        dialect: Database dialect

    Returns:
        Validated schema name

    Raises:
        SQLIdentifierError: If validation fails

    Examples:
        >>> validate_schema_name("public")
        'public'
        >>> validate_schema_name("my_schema")
        'my_schema'
    """
    return validate_identifier(schema_name, allow_dots=False, dialect=dialect)


def sanitize_identifier(identifier: str, dialect: DatabaseDialect = DatabaseDialect.GENERIC) -> str:
    """
    Sanitize an identifier by removing/replacing invalid characters.

    This is a permissive function that attempts to fix identifiers.
    For security-critical operations, use validate_identifier() instead.

    Args:
        identifier: Identifier to sanitize
        dialect: Database dialect

    Returns:
        Sanitized identifier

    Examples:
        >>> sanitize_identifier("user-profile")
        'user_profile'
        >>> sanitize_identifier("123_users")
        '_123_users'
    """
    if not identifier:
        return "unnamed"

    # Remove/replace invalid characters
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", identifier)

    # Ensure starts with letter or underscore
    if not re.match(r"^[a-zA-Z_]", sanitized):
        sanitized = "_" + sanitized

    # Truncate to max length
    max_len = MAX_IDENTIFIER_LENGTH[dialect]
    if len(sanitized) > max_len:
        sanitized = sanitized[:max_len]

    # Avoid reserved keywords
    if sanitized.upper() in SQL_RESERVED_KEYWORDS:
        sanitized = f"_{sanitized}"

    return sanitized


def quote_identifier(identifier: str, dialect: DatabaseDialect = DatabaseDialect.GENERIC) -> str:
    """
    Quote an identifier for use in SQL queries.

    This should ONLY be used after validation.

    Args:
        identifier: Validated identifier
        dialect: Database dialect

    Returns:
        Quoted identifier

    Examples:
        >>> quote_identifier("users", DatabaseDialect.MYSQL)
        '`users`'
        >>> quote_identifier("users", DatabaseDialect.POSTGRESQL)
        '"users"'
    """
    # First validate
    validate_identifier(identifier, dialect=dialect)

    if dialect == DatabaseDialect.MYSQL:
        return f"`{identifier}`"
    elif dialect == DatabaseDialect.POSTGRESQL:
        return f'"{identifier}"'
    elif dialect == DatabaseDialect.SQLITE:
        return f'"{identifier}"'
    else:
        # Generic: use double quotes
        return f'"{identifier}"'


def is_safe_identifier(identifier: str) -> bool:
    """
    Check if an identifier is safe without raising exceptions.

    Args:
        identifier: Identifier to check

    Returns:
        True if safe, False otherwise

    Examples:
        >>> is_safe_identifier("users")
        True
        >>> is_safe_identifier("users; DROP TABLE users--")
        False
    """
    try:
        validate_identifier(identifier)
        return True
    except SQLIdentifierError:
        return False


# Whitelist of common safe table names for additional validation
COMMON_TABLE_NAMES: Set[str] = {
    "users",
    "accounts",
    "profiles",
    "sessions",
    "tokens",
    "posts",
    "comments",
    "likes",
    "follows",
    "messages",
    "products",
    "orders",
    "payments",
    "invoices",
    "customers",
    "logs",
    "events",
    "metrics",
    "analytics",
    "audit",
}


def is_whitelisted_table(table_name: str) -> bool:
    """
    Check if a table name is in the common whitelist.

    This provides an additional layer of validation for sensitive operations.

    Args:
        table_name: Table name to check

    Returns:
        True if whitelisted

    Examples:
        >>> is_whitelisted_table("users")
        True
        >>> is_whitelisted_table("malicious_table")
        False
    """
    return table_name.lower() in COMMON_TABLE_NAMES


__all__ = [
    "validate_identifier",
    "validate_table_name",
    "validate_column_name",
    "validate_schema_name",
    "sanitize_identifier",
    "quote_identifier",
    "is_safe_identifier",
    "is_whitelisted_table",
    "SQLIdentifierError",
    "InvalidIdentifierError",
    "IdentifierTooLongError",
    "IllegalCharacterError",
    "DatabaseDialect",
    "SQL_RESERVED_KEYWORDS",
]
