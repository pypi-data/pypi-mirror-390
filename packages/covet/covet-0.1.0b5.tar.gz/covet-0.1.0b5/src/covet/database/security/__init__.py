"""
CovetPy Database Security Module

This module provides SQL injection prevention utilities and security middleware
for database operations. It implements defense-in-depth principles to protect
against SQL injection attacks.

Author: CovetPy Security Team
Version: 1.0.0
"""

from .query_sanitizer import QuerySanitizer, escape_like_pattern, sanitize_query_params
from .sql_validator import (
    IdentifierTooLongError,
    IllegalCharacterError,
    InvalidIdentifierError,
    SQLIdentifierError,
    sanitize_identifier,
    validate_column_name,
    validate_identifier,
    validate_schema_name,
    validate_table_name,
)

__all__ = [
    # Identifier validation
    "validate_identifier",
    "validate_table_name",
    "validate_column_name",
    "validate_schema_name",
    "sanitize_identifier",
    # Exceptions
    "SQLIdentifierError",
    "InvalidIdentifierError",
    "IdentifierTooLongError",
    "IllegalCharacterError",
    # Query sanitization
    "QuerySanitizer",
    "sanitize_query_params",
    "escape_like_pattern",
]
