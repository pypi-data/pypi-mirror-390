"""
SQL Injection Prevention Middleware

Provides middleware for intercepting and validating database queries to prevent
SQL injection attacks. This is a defense-in-depth layer that works alongside
parameterized queries and identifier validation.

Author: CovetPy Security Team
"""

import logging
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .query_sanitizer import sanitize_query_params
from .sql_validator import (
    SQL_INJECTION_PATTERNS,
    SQL_RESERVED_KEYWORDS,
    SQLIdentifierError,
    validate_identifier,
)

logger = logging.getLogger(__name__)


class SQLInjectionDetected(Exception):
    """Raised when SQL injection attempt is detected."""


class QuerySecurityMiddleware:
    """
    Middleware for validating SQL queries and preventing injection attacks.

    This middleware provides multiple layers of defense:
    1. Query pattern analysis
    2. Parameter validation
    3. Dangerous keyword detection
    4. Query complexity limits
    5. Audit logging
    """

    def __init__(
        self,
        enable_logging: bool = True,
        enable_blocking: bool = True,
        max_query_length: int = 10000,
        max_params: int = 100,
    ):
        """
        Initialize query security middleware.

        Args:
            enable_logging: Log suspicious queries
            enable_blocking: Block dangerous queries (vs just logging)
            max_query_length: Maximum allowed query length
            max_params: Maximum number of parameters
        """
        self.enable_logging = enable_logging
        self.enable_blocking = enable_blocking
        self.max_query_length = max_query_length
        self.max_params = max_params
        self.blocked_queries = 0
        self.total_queries = 0

    def validate_query(
        self, query: str, params: Optional[Union[Tuple, List, Dict]] = None
    ) -> Tuple[str, Optional[Union[Tuple, List, Dict]]]:
        """
        Validate a SQL query for security issues.

        Args:
            query: SQL query string
            params: Query parameters

        Returns:
            Validated (query, params) tuple

        Raises:
            SQLInjectionDetected: If injection attempt is detected
            ValueError: If query is invalid
        """
        self.total_queries += 1

        # Check query length
        if len(query) > self.max_query_length:
            self._handle_threat("Query exceeds maximum length", query, params)

        # Validate parameters
        if params is not None:
            if isinstance(params, (tuple, list)):
                if len(params) > self.max_params:
                    self._handle_threat("Too many parameters", query, params)
            elif isinstance(params, dict):
                if len(params) > self.max_params:
                    self._handle_threat("Too many parameters", query, params)

            # Sanitize parameters
            try:
                params = sanitize_query_params(params)
            except (TypeError, ValueError) as e:
                self._handle_threat(f"Invalid parameter type: {e}", query, params)

        # Detect dangerous patterns in query
        self._detect_dangerous_patterns(query)

        # Detect SQL injection attempts
        self._detect_sql_injection(query)

        # Check for dangerous operations
        self._check_dangerous_operations(query)

        return query, params

    def _detect_dangerous_patterns(self, query: str) -> None:
        """
        Detect dangerous SQL patterns.

        Args:
            query: SQL query to analyze

        Raises:
            SQLInjectionDetected: If dangerous pattern found
        """
        # Check for multiple statements
        if ";" in query and not query.strip().endswith(";"):
            # Allow single trailing semicolon, but not multiple statements
            parts = query.split(";")
            if len(parts) > 2 or (len(parts) == 2 and parts[1].strip()):
                self._handle_threat("Multiple SQL statements detected", query, None)

        # Check for SQL comments
        if "--" in query or "/*" in query or "*/" in query:
            self._handle_threat("SQL comments detected in query", query, None)

        # Check for UNION-based injection
        if re.search(r"\bUNION\b.*\bSELECT\b", query, re.IGNORECASE):
            # This might be legitimate, but log it
            if self.enable_logging:
                logger.warning(f"UNION SELECT detected in query: {query[:200]}")

    def _detect_sql_injection(self, query: str) -> None:
        """
        Detect SQL injection patterns.

        Args:
            query: SQL query to analyze

        Raises:
            SQLInjectionDetected: If injection pattern found
        """
        for pattern in SQL_INJECTION_PATTERNS:
            if pattern.search(query):
                self._handle_threat(
                    f"SQL injection pattern detected: {pattern.pattern}", query, None
                )

    def _check_dangerous_operations(self, query: str) -> None:
        """
        Check for dangerous SQL operations.

        Args:
            query: SQL query to analyze
        """
        dangerous_operations = [
            (r"\bDROP\s+TABLE\b", "DROP TABLE"),
            (r"\bDROP\s+DATABASE\b", "DROP DATABASE"),
            (r"\bTRUNCATE\b", "TRUNCATE"),
            (r"\bDELETE\s+FROM\s+\w+\s*;?\s*$", "DELETE without WHERE"),
            (r"\bUPDATE\s+\w+\s+SET\s+.*\s*;?\s*$", "UPDATE without WHERE"),
            (r"\bGRANT\b", "GRANT"),
            (r"\bREVOKE\b", "REVOKE"),
            (r"\bALTER\s+TABLE\b", "ALTER TABLE"),
            (r"\bEXEC\b|\bEXECUTE\b", "EXEC/EXECUTE"),
            (r"\bxp_\w+", "Extended stored procedure"),
            (r"\bsp_\w+", "System stored procedure"),
        ]

        for pattern_str, operation_name in dangerous_operations:
            if re.search(pattern_str, query, re.IGNORECASE):
                if self.enable_logging:
                    logger.warning(
                        f"Dangerous operation detected: {operation_name} in query: {query[:200]}"
                    )

    def _handle_threat(
        self, reason: str, query: str, params: Optional[Union[Tuple, List, Dict]]
    ) -> None:
        """
        Handle a detected security threat.

        Args:
            reason: Reason for threat detection
            query: SQL query
            params: Query parameters

        Raises:
            SQLInjectionDetected: If blocking is enabled
        """
        self.blocked_queries += 1

        # Log the threat
        if self.enable_logging:
            logger.error(
                f"SQL Security Threat Detected: {reason}\n"
                f"Query: {query[:200]}...\n"
                f"Params: {params}"
            )

        # Block if enabled
        if self.enable_blocking:
            raise SQLInjectionDetected(f"SQL injection attempt detected: {reason}")

    def get_stats(self) -> Dict[str, int]:
        """
        Get middleware statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_queries": self.total_queries,
            "blocked_queries": self.blocked_queries,
            "block_rate": (
                self.blocked_queries / self.total_queries if self.total_queries > 0 else 0
            ),
        }


def sql_injection_guard(func: Callable) -> Callable:
    """
    Decorator to protect database functions from SQL injection.

    Usage:
        @sql_injection_guard
        async def execute_query(query: str, params=None):
            ...

    Args:
        func: Function to protect

    Returns:
        Protected function
    """
    middleware = QuerySecurityMiddleware()

    @wraps(func)
    async def wrapper(query: str, params=None, *args, **kwargs):
        # Validate query
        validated_query, validated_params = middleware.validate_query(query, params)

        # Call original function
        return await func(validated_query, validated_params, *args, **kwargs)

    return wrapper


class DatabaseSecurityPolicy:
    """
    Configurable security policy for database operations.

    Defines what operations are allowed and under what conditions.
    """

    def __init__(self):
        self.allowed_operations = {"SELECT", "INSERT", "UPDATE", "DELETE"}
        self.blocked_operations = {
            "DROP",
            "TRUNCATE",
            "ALTER",
            "CREATE",
            "GRANT",
            "REVOKE",
        }
        self.require_where_clause = {"DELETE", "UPDATE"}
        self.max_result_limit = 10000

    def validate_operation(self, query: str) -> bool:
        """
        Validate if an operation is allowed by policy.

        Args:
            query: SQL query

        Returns:
            True if allowed

        Raises:
            PermissionError: If operation is not allowed
        """
        query_upper = query.upper().strip()

        # Check blocked operations
        for blocked_op in self.blocked_operations:
            if query_upper.startswith(blocked_op):
                raise PermissionError(f"Operation '{blocked_op}' is blocked by security policy")

        # Check for WHERE clause requirement
        for op in self.require_where_clause:
            if query_upper.startswith(op) and "WHERE" not in query_upper:
                raise PermissionError(f"Operation '{op}' requires WHERE clause")

        return True


__all__ = [
    "QuerySecurityMiddleware",
    "SQLInjectionDetected",
    "sql_injection_guard",
    "DatabaseSecurityPolicy",
]
