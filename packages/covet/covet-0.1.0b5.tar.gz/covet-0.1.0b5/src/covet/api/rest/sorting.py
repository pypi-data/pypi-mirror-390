"""
REST API Sorting System

Production-grade sorting with:
- Multi-field sorting
- Ascending/descending order (- prefix)
- Field validation and whitelisting
- SQL injection prevention
- Integration with ORM
- Sorting configuration per resource

Example:
    from covet.api.rest.sorting import SortingConfig, apply_sorting

    # Define allowed sort fields
    config = SortingConfig(
        allowed_fields=['created_at', 'name', 'email', 'age'],
        default_ordering=['-created_at']  # Newest first
    )

    # Parse sort parameter
    # GET /users?sort=-created_at,name
    sort_fields = request.query_params.get('sort', '').split(',')

    # Apply sorting
    queryset = User.objects.filter(is_active=True)
    queryset = apply_sorting(queryset, sort_fields, config)

    users = await queryset.all()
    # Results ordered by: created_at DESC, name ASC
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class SortDirection(str, Enum):
    """Sort direction."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class SortField:
    """
    Sort field definition.

    Attributes:
        field_name: Database field name
        direction: Sort direction (asc/desc)
        nulls_last: Whether to put NULL values last
    """

    field_name: str
    direction: SortDirection = SortDirection.ASC
    nulls_last: bool = True

    def to_orm_string(self) -> str:
        """
        Convert to ORM order_by string.

        Returns:
            ORM order string (e.g., '-created_at')
        """
        prefix = "-" if self.direction == SortDirection.DESC else ""
        return f"{prefix}{self.field_name}"

    def to_sql_expression(self, dialect: str = "postgresql") -> str:
        """
        Convert to SQL ORDER BY expression.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)

        Returns:
            SQL ORDER BY expression
        """
        direction_str = "DESC" if self.direction == SortDirection.DESC else "ASC"
        nulls_clause = ""

        # PostgreSQL supports NULLS FIRST/LAST
        if dialect == "postgresql":
            nulls_clause = " NULLS LAST" if self.nulls_last else " NULLS FIRST"

        return f"{self.field_name} {direction_str}{nulls_clause}"


@dataclass
class SortingConfig:
    """
    Sorting configuration for a resource.

    Attributes:
        allowed_fields: Fields that can be used for sorting
        field_aliases: Map query param names to database field names
        default_ordering: Default sort order if none specified
        max_sort_fields: Maximum number of sort fields allowed
        case_sensitive: Whether sorting is case-sensitive
        null_handling: How to handle NULL values
    """

    allowed_fields: List[str] = field(default_factory=list)
    field_aliases: Dict[str, str] = field(default_factory=dict)
    default_ordering: List[str] = field(default_factory=list)
    max_sort_fields: int = 5
    case_sensitive: bool = True
    null_handling: str = "last"  # 'first', 'last', or 'ignore'

    def __post_init__(self):
        """Validate configuration."""
        if not self.allowed_fields:
            logger.warning("SortingConfig has no allowed_fields - all sorting will be rejected")

        if self.max_sort_fields < 1:
            raise ValueError("max_sort_fields must be at least 1")

    def is_field_allowed(self, field_name: str) -> bool:
        """
        Check if field is allowed for sorting.

        Args:
            field_name: Field name to check

        Returns:
            True if field is allowed
        """
        # Check if field or its alias is allowed
        resolved_name = self.field_aliases.get(field_name, field_name)
        return resolved_name in self.allowed_fields

    def resolve_field_name(self, query_field: str) -> str:
        """
        Resolve query field name to database field name.

        Args:
            query_field: Field name from query parameter

        Returns:
            Database field name

        Raises:
            ValueError: If field is not allowed
        """
        # Remove direction prefix
        is_descending = query_field.startswith("-")
        field_name = query_field.lstrip("-")

        # Resolve alias
        resolved_name = self.field_aliases.get(field_name, field_name)

        # Check if allowed
        if resolved_name not in self.allowed_fields:
            raise ValueError(
                f"Sorting by '{field_name}' is not allowed. "
                f"Allowed fields: {', '.join(self.allowed_fields)}"
            )

        # Validate field name (security: prevent SQL injection)
        if not self._is_valid_field_name(resolved_name):
            raise ValueError(f"Invalid field name: {resolved_name}")

        return resolved_name

    @staticmethod
    def _is_valid_field_name(field_name: str) -> bool:
        """
        Validate field name to prevent SQL injection.

        Args:
            field_name: Field name to validate

        Returns:
            True if valid
        """
        # Allow only alphanumeric, underscore, and dot (for joins)
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*$"
        return bool(re.match(pattern, field_name))


class SortingParser:
    """
    Parse sorting parameters from query strings.

    Supports multiple formats:
    - Comma-separated: sort=-created_at,name
    - Multiple params: sort[]=-created_at&sort[]=name
    - Django-style: ordering=-created_at,name
    """

    @staticmethod
    def parse_sort_string(sort_param: Optional[str], config: SortingConfig) -> List[SortField]:
        """
        Parse sort parameter string into SortField objects.

        Args:
            sort_param: Sort parameter string (e.g., "-created_at,name")
            config: Sorting configuration

        Returns:
            List of SortField objects

        Raises:
            ValueError: If sort parameter is invalid

        Example:
            fields = parse_sort_string("-created_at,name,age", config)
            # Returns: [
            #     SortField('created_at', DESC),
            #     SortField('name', ASC),
            #     SortField('age', ASC)
            # ]
        """
        if not sort_param or not sort_param.strip():
            # Return default ordering
            return SortingParser._parse_default_ordering(config)

        # Split by comma
        field_strings = [f.strip() for f in sort_param.split(",") if f.strip()]

        # Check max fields limit
        if len(field_strings) > config.max_sort_fields:
            raise ValueError(f"Too many sort fields. Maximum allowed: {config.max_sort_fields}")

        sort_fields = []
        seen_fields = set()

        for field_str in field_strings:
            # Parse field
            sort_field = SortingParser._parse_field_string(field_str, config)

            # Check for duplicates
            if sort_field.field_name in seen_fields:
                logger.warning(f"Duplicate sort field: {sort_field.field_name}")
                continue

            seen_fields.add(sort_field.field_name)
            sort_fields.append(sort_field)

        return sort_fields or SortingParser._parse_default_ordering(config)

    @staticmethod
    def _parse_field_string(field_str: str, config: SortingConfig) -> SortField:
        """
        Parse single field string into SortField.

        Args:
            field_str: Field string (e.g., "-created_at")
            config: Sorting configuration

        Returns:
            SortField object

        Raises:
            ValueError: If field is invalid
        """
        # Check for direction prefix
        is_descending = field_str.startswith("-")
        field_name = field_str.lstrip("-+")

        # Resolve and validate field name
        resolved_name = config.resolve_field_name(field_name)

        # Determine direction
        direction = SortDirection.DESC if is_descending else SortDirection.ASC

        # Null handling
        nulls_last = config.null_handling == "last"

        return SortField(field_name=resolved_name, direction=direction, nulls_last=nulls_last)

    @staticmethod
    def _parse_default_ordering(config: SortingConfig) -> List[SortField]:
        """
        Parse default ordering from config.

        Args:
            config: Sorting configuration

        Returns:
            List of SortField objects
        """
        if not config.default_ordering:
            return []

        sort_fields = []
        for field_str in config.default_ordering:
            try:
                sort_field = SortingParser._parse_field_string(field_str, config)
                sort_fields.append(sort_field)
            except ValueError as e:
                logger.warning(f"Invalid default ordering field '{field_str}': {e}")

        return sort_fields


def apply_sorting(queryset, sort_param: Optional[str], config: SortingConfig):
    """
    Apply sorting to ORM queryset.

    Args:
        queryset: ORM queryset
        sort_param: Sort parameter from query string
        config: Sorting configuration

    Returns:
        Sorted queryset

    Example:
        queryset = User.objects.filter(is_active=True)
        sorted_qs = apply_sorting(queryset, "-created_at,name", config)
    """
    # Parse sort fields
    try:
        sort_fields = SortingParser.parse_sort_string(sort_param, config)
    except ValueError as e:
        logger.warning(f"Invalid sort parameter: {e}")
        # Fall back to default ordering
        sort_fields = SortingParser._parse_default_ordering(config)

    if not sort_fields:
        return queryset

    # Build order_by arguments
    order_by_args = [field.to_orm_string() for field in sort_fields]

    # Apply sorting
    return queryset.order_by(*order_by_args)


class SortingMiddleware:
    """
    Middleware to automatically apply sorting from query parameters.

    Example:
        app = CovetPy()

        sorting_config = SortingConfig(
            allowed_fields=['id', 'created_at', 'name'],
            default_ordering=['-created_at']
        )

        app.add_middleware(SortingMiddleware(config=sorting_config))
    """

    def __init__(self, config: SortingConfig, param_name: str = "sort"):
        """
        Initialize sorting middleware.

        Args:
            config: Sorting configuration
            param_name: Query parameter name for sorting
        """
        self.config = config
        self.param_name = param_name

    async def __call__(self, request, call_next):
        """
        Process request and apply sorting.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            Response
        """
        # Extract sort parameter
        sort_param = request.query_params.get(self.param_name)

        if sort_param:
            # Attach parsed sort fields to request
            try:
                sort_fields = SortingParser.parse_sort_string(sort_param, self.config)
                request.state.sort_fields = sort_fields
            except ValueError as e:
                logger.warning(f"Invalid sort parameter: {e}")
                request.state.sort_fields = []

        return await call_next(request)


def create_sorting_config_from_model(
    model: type,
    allowed_fields: Optional[List[str]] = None,
    exclude_fields: Optional[List[str]] = None,
    default_ordering: Optional[List[str]] = None,
) -> SortingConfig:
    """
    Create sorting configuration from model.

    Args:
        model: Model class
        allowed_fields: Explicitly allowed fields (None = all fields)
        exclude_fields: Fields to exclude
        default_ordering: Default sort order

    Returns:
        SortingConfig

    Example:
        config = create_sorting_config_from_model(
            User,
            exclude_fields=['password_hash'],
            default_ordering=['-created_at']
        )
    """
    exclude_fields = exclude_fields or []

    # Get all model fields
    if hasattr(model, "_fields"):
        model_fields = list(model._fields.keys())
    else:
        logger.warning(f"Model {model.__name__} has no _fields attribute")
        model_fields = []

    # Determine allowed fields
    if allowed_fields is not None:
        # Use explicit whitelist
        final_fields = [f for f in allowed_fields if f in model_fields]
    else:
        # Use all fields except excluded
        final_fields = [f for f in model_fields if f not in exclude_fields]

    return SortingConfig(allowed_fields=final_fields, default_ordering=default_ordering or [])


@dataclass
class SortingMetadata:
    """
    Metadata about applied sorting.

    Can be included in API responses for transparency.
    """

    sort_fields: List[str]
    applied_count: int
    default_used: bool

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "sort_fields": self.sort_fields,
            "applied_count": self.applied_count,
            "default_used": self.default_used,
        }


def get_sorting_metadata(sort_param: Optional[str], config: SortingConfig) -> SortingMetadata:
    """
    Get metadata about sorting that will be applied.

    Args:
        sort_param: Sort parameter
        config: Sorting configuration

    Returns:
        SortingMetadata
    """
    if not sort_param or not sort_param.strip():
        # Default ordering will be used
        sort_fields = SortingParser._parse_default_ordering(config)
        return SortingMetadata(
            sort_fields=[f.to_orm_string() for f in sort_fields],
            applied_count=len(sort_fields),
            default_used=True,
        )

    # Parse requested sorting
    try:
        sort_fields = SortingParser.parse_sort_string(sort_param, config)
        return SortingMetadata(
            sort_fields=[f.to_orm_string() for f in sort_fields],
            applied_count=len(sort_fields),
            default_used=False,
        )
    except ValueError:
        # Invalid sort, fall back to default
        sort_fields = SortingParser._parse_default_ordering(config)
        return SortingMetadata(
            sort_fields=[f.to_orm_string() for f in sort_fields],
            applied_count=len(sort_fields),
            default_used=True,
        )


__all__ = [
    "SortField",
    "SortDirection",
    "SortingConfig",
    "SortingParser",
    "SortingMiddleware",
    "SortingMetadata",
    "apply_sorting",
    "create_sorting_config_from_model",
    "get_sorting_metadata",
]
