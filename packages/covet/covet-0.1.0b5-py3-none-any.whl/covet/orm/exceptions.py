"""
ORM Exception Classes

Comprehensive exception hierarchy for the CovetPy ORM system.
"""


class ORMError(Exception):
    """Base exception for all ORM-related errors."""


class DoesNotExist(ORMError):
    """Raised when a database query returns no results."""


class MultipleObjectsReturned(ORMError):
    """Raised when a query expected to return a single object returns multiple."""


class IntegrityError(ORMError):
    """Raised when database integrity constraints are violated."""


class TransactionError(ORMError):
    """Raised when transaction-related operations fail."""


class ValidationError(ORMError):
    """Raised when field validation fails."""


class ConnectionError(ORMError):
    """Raised when database connection fails."""


class MigrationError(ORMError):
    """Raised when migration operations fail."""


class RelationshipError(ORMError):
    """Raised when relationship operations fail."""


class QueryError(ORMError):
    """Raised when query construction or execution fails."""
