"""
REST API Automatic Filtering

Production-grade filtering system with:
- Automatic filtering from query parameters
- Django-style filter operators (eq, ne, gt, gte, lt, lte, in, contains, startswith)
- SQL injection prevention
- Type validation and coercion
- Integration with ORM QuerySet
- Custom filter classes
- Filterset generation from models

Example:
    from covet.api.rest.filtering import FilterSet, CharFilter, IntegerFilter
    from covet.database.orm import User

    # Automatic filtering from query params
    # GET /users?age__gte=18&name__contains=John&is_active=true

    class UserFilterSet(FilterSet):
        age__gte = IntegerFilter(field_name='age', lookup='gte')
        name__contains = CharFilter(field_name='name', lookup='icontains')
        is_active = BooleanFilter(field_name='is_active', lookup='exact')

        class Meta:
            model = User
            fields = ['age', 'name', 'is_active', 'email']

    # In endpoint:
    filterset = UserFilterSet(query_params=request.query_params)
    queryset = filterset.filter(User.objects.all())
    users = await queryset.all()
"""

import logging
from abc import ABC, abstractmethod
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Type, Union
from uuid import UUID

logger = logging.getLogger(__name__)


class FilterLookup(str, Enum):
    """Supported filter lookup types."""

    EXACT = "exact"
    IEXACT = "iexact"
    CONTAINS = "contains"
    ICONTAINS = "icontains"
    IN = "in"
    GT = "gt"
    GTE = "gte"
    LT = "lt"
    LTE = "lte"
    STARTSWITH = "startswith"
    ISTARTSWITH = "istartswith"
    ENDSWITH = "endswith"
    IENDSWITH = "iendswith"
    RANGE = "range"
    ISNULL = "isnull"
    REGEX = "regex"
    IREGEX = "iregex"


class BaseFilter(ABC):
    """
    Base filter class.

    All filters inherit from this and implement:
    - convert_value(): Convert query param string to typed value
    - validate_value(): Validate converted value
    - apply_filter(): Apply filter to queryset
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        lookup: str = FilterLookup.EXACT,
        required: bool = False,
        default: Any = None,
        help_text: Optional[str] = None,
        validators: Optional[List[callable]] = None,
    ):
        """
        Initialize filter.

        Args:
            field_name: Model field name to filter
            lookup: Filter lookup type
            required: Whether filter is required
            default: Default value if not provided
            help_text: Help text for documentation
            validators: Custom validator functions
        """
        self.field_name = field_name
        self.lookup = lookup
        self.required = required
        self.default = default
        self.help_text = help_text
        self.validators = validators or []

    @abstractmethod
    def convert_value(self, value: str) -> Any:
        """
        Convert query parameter string to typed value.

        Args:
            value: String value from query parameter

        Returns:
            Converted typed value

        Raises:
            ValueError: If conversion fails
        """
        pass

    def validate_value(self, value: Any) -> None:
        """
        Validate converted value.

        Args:
            value: Converted value

        Raises:
            ValueError: If validation fails
        """
        for validator in self.validators:
            validator(value)

    def apply_filter(self, queryset, value: Any):
        """
        Apply filter to queryset.

        Args:
            queryset: ORM queryset
            value: Filter value

        Returns:
            Filtered queryset
        """
        # Build filter kwargs
        filter_key = f"{self.field_name}__{self.lookup}"
        return queryset.filter(**{filter_key: value})

    def process(self, queryset, value: str):
        """
        Process filter: convert, validate, and apply.

        Args:
            queryset: ORM queryset
            value: Raw query parameter value

        Returns:
            Filtered queryset
        """
        if value is None:
            if self.required:
                raise ValueError(f"Filter '{self.field_name}' is required")
            if self.default is not None:
                value = self.default
            else:
                return queryset

        # Convert value
        try:
            converted_value = self.convert_value(value)
        except Exception as e:
            raise ValueError(f"Invalid value for filter '{self.field_name}': {e}")

        # Validate value
        try:
            self.validate_value(converted_value)
        except Exception as e:
            raise ValueError(f"Validation failed for filter '{self.field_name}': {e}")

        # Apply filter
        return self.apply_filter(queryset, converted_value)


class CharFilter(BaseFilter):
    """
    Character/string filter.

    Example:
        name__contains = CharFilter(field_name='name', lookup='icontains')
        # Matches: ?name__contains=john
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        lookup: str = FilterLookup.EXACT,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=lookup, **kwargs)
        self.min_length = min_length
        self.max_length = max_length

    def convert_value(self, value: str) -> str:
        """Convert to string."""
        return str(value)

    def validate_value(self, value: str) -> None:
        """Validate string length."""
        super().validate_value(value)

        if self.min_length and len(value) < self.min_length:
            raise ValueError(f"Value must be at least {self.min_length} characters")

        if self.max_length and len(value) > self.max_length:
            raise ValueError(f"Value must be at most {self.max_length} characters")


class IntegerFilter(BaseFilter):
    """
    Integer filter.

    Example:
        age__gte = IntegerFilter(field_name='age', lookup='gte')
        # Matches: ?age__gte=18
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        lookup: str = FilterLookup.EXACT,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=lookup, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def convert_value(self, value: str) -> int:
        """Convert to integer."""
        return int(value)

    def validate_value(self, value: int) -> None:
        """Validate integer range."""
        super().validate_value(value)

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value must be at least {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value must be at most {self.max_value}")


class FloatFilter(BaseFilter):
    """
    Float filter.

    Example:
        price__lte = FloatFilter(field_name='price', lookup='lte')
        # Matches: ?price__lte=99.99
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        lookup: str = FilterLookup.EXACT,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=lookup, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def convert_value(self, value: str) -> float:
        """Convert to float."""
        return float(value)

    def validate_value(self, value: float) -> None:
        """Validate float range."""
        super().validate_value(value)

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"Value must be at least {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"Value must be at most {self.max_value}")


class BooleanFilter(BaseFilter):
    """
    Boolean filter.

    Accepts: true/false, 1/0, yes/no, on/off

    Example:
        is_active = BooleanFilter(field_name='is_active')
        # Matches: ?is_active=true
    """

    TRUE_VALUES = {"true", "1", "yes", "on", "t", "y"}
    FALSE_VALUES = {"false", "0", "no", "off", "f", "n"}

    def convert_value(self, value: str) -> bool:
        """Convert to boolean."""
        value_lower = str(value).lower()

        if value_lower in self.TRUE_VALUES:
            return True
        elif value_lower in self.FALSE_VALUES:
            return False
        else:
            raise ValueError(f"Invalid boolean value: {value}")


class DateFilter(BaseFilter):
    """
    Date filter.

    Accepts ISO 8601 format: YYYY-MM-DD

    Example:
        created_date__gte = DateFilter(field_name='created_at', lookup='gte')
        # Matches: ?created_date__gte=2025-01-01
    """

    def convert_value(self, value: str) -> date:
        """Convert to date."""
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError(f"Invalid date format: {value}. Use YYYY-MM-DD")


class DateTimeFilter(BaseFilter):
    """
    DateTime filter.

    Accepts ISO 8601 format: YYYY-MM-DDTHH:MM:SS

    Example:
        created_at__gte = DateTimeFilter(field_name='created_at', lookup='gte')
        # Matches: ?created_at__gte=2025-01-01T00:00:00
    """

    def convert_value(self, value: str) -> datetime:
        """Convert to datetime."""
        try:
            # Try with timezone
            return datetime.fromisoformat(value)
        except ValueError:
            try:
                # Try without timezone
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError(f"Invalid datetime format: {value}. Use YYYY-MM-DDTHH:MM:SS")


class UUIDFilter(BaseFilter):
    """
    UUID filter.

    Example:
        id = UUIDFilter(field_name='id')
        # Matches: ?id=550e8400-e29b-41d4-a716-446655440000
    """

    def convert_value(self, value: str) -> UUID:
        """Convert to UUID."""
        try:
            return UUID(value)
        except ValueError:
            raise ValueError(f"Invalid UUID format: {value}")


class ChoiceFilter(BaseFilter):
    """
    Choice filter (enum).

    Example:
        status = ChoiceFilter(
            field_name='status',
            choices=['pending', 'active', 'completed']
        )
        # Matches: ?status=active
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        lookup: str = FilterLookup.EXACT,
        choices: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=lookup, **kwargs)
        self.choices = choices or []

    def convert_value(self, value: str) -> str:
        """Convert and validate choice."""
        value = str(value)
        if value not in self.choices:
            raise ValueError(f"Invalid choice: {value}. Must be one of: {', '.join(self.choices)}")
        return value


class MultipleValueFilter(BaseFilter):
    """
    Filter for multiple values (IN lookup).

    Example:
        status__in = MultipleValueFilter(
            field_name='status',
            base_filter=ChoiceFilter(choices=['pending', 'active'])
        )
        # Matches: ?status__in=pending,active
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        base_filter: Optional[BaseFilter] = None,
        separator: str = ",",
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=FilterLookup.IN, **kwargs)
        self.base_filter = base_filter or CharFilter()
        self.separator = separator

    def convert_value(self, value: str) -> List[Any]:
        """Convert comma-separated values to list."""
        if isinstance(value, list):
            values = value
        else:
            values = [v.strip() for v in str(value).split(self.separator)]

        # Convert each value using base filter
        converted = []
        for v in values:
            try:
                converted.append(self.base_filter.convert_value(v))
            except Exception as e:
                raise ValueError(f"Invalid value '{v}': {e}")

        return converted


class RangeFilter(BaseFilter):
    """
    Range filter (between two values).

    Example:
        age__range = RangeFilter(field_name='age', base_filter=IntegerFilter())
        # Matches: ?age__range=18,65
    """

    def __init__(
        self,
        field_name: Optional[str] = None,
        base_filter: Optional[BaseFilter] = None,
        separator: str = ",",
        **kwargs,
    ):
        super().__init__(field_name=field_name, lookup=FilterLookup.RANGE, **kwargs)
        self.base_filter = base_filter or IntegerFilter()
        self.separator = separator

    def convert_value(self, value: str) -> tuple:
        """Convert range values."""
        if isinstance(value, (list, tuple)) and len(value) == 2:
            min_val, max_val = value
        else:
            parts = str(value).split(self.separator)
            if len(parts) != 2:
                raise ValueError("Range filter requires exactly 2 values")
            min_val, max_val = parts

        # Convert using base filter
        min_converted = self.base_filter.convert_value(min_val)
        max_converted = self.base_filter.convert_value(max_val)

        if min_converted > max_converted:
            raise ValueError("Range min value must be less than max value")

        return (min_converted, max_converted)


class FilterSetMeta(type):
    """
    Metaclass for FilterSet.

    Collects filter fields and processes Meta class.
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Don't process base FilterSet class
        if name == "FilterSet" and not bases:
            return super().__new__(mcs, name, bases, namespace)

        # Collect filters from class
        filters = {}
        for key, value in list(namespace.items()):
            if isinstance(value, BaseFilter):
                filters[key] = value
                # Set field_name if not specified
                if value.field_name is None:
                    # Remove lookup suffix if present
                    field_name = key.split("__")[0]
                    value.field_name = field_name

        # Create class
        cls = super().__new__(mcs, name, bases, namespace)
        cls._filters = filters

        # Process Meta class
        if hasattr(cls, "Meta"):
            meta = cls.Meta
            cls._meta_model = getattr(meta, "model", None)
            cls._meta_fields = getattr(meta, "fields", [])
            cls._meta_exclude = getattr(meta, "exclude", [])

            # Auto-generate filters from model if specified
            if cls._meta_model and cls._meta_fields:
                cls._auto_generate_filters()

        return cls

    def _auto_generate_filters(cls):
        """Auto-generate filters from model fields."""
        if not cls._meta_model:
            return

        model = cls._meta_model

        # Get model fields
        for field_name in cls._meta_fields:
            if field_name in cls._meta_exclude:
                continue

            if field_name in cls._filters:
                # Already defined manually
                continue

            # Auto-generate filter based on field type
            if hasattr(model, "_fields") and field_name in model._fields:
                model_field = model._fields[field_name]
                filter_class = cls._get_filter_for_field(model_field)
                if filter_class:
                    cls._filters[field_name] = filter_class(field_name=field_name)

    @staticmethod
    def _get_filter_for_field(field) -> Optional[BaseFilter]:
        """Get appropriate filter class for model field."""
        from covet.database.orm.fields import (
            BooleanField,
            CharField,
            DateField,
            DateTimeField,
            EmailField,
            FloatField,
            IntegerField,
            UUIDField,
        )

        field_type = type(field)

        if field_type in (CharField, EmailField):
            return CharFilter()
        elif field_type == IntegerField:
            return IntegerFilter()
        elif field_type == FloatField:
            return FloatFilter()
        elif field_type == BooleanField:
            return BooleanFilter()
        elif field_type == DateTimeField:
            return DateTimeFilter()
        elif field_type == DateField:
            return DateFilter()
        elif field_type == UUIDField:
            return UUIDFilter()

        return None


class FilterSet(metaclass=FilterSetMeta):
    """
    FilterSet for declarative filtering.

    Example:
        class UserFilterSet(FilterSet):
            age__gte = IntegerFilter(field_name='age', lookup='gte')
            name__icontains = CharFilter(field_name='name', lookup='icontains')
            is_active = BooleanFilter(field_name='is_active')

            class Meta:
                model = User
                fields = ['age', 'name', 'is_active', 'email']

        # Usage:
        filterset = UserFilterSet(query_params=request.query_params)
        queryset = filterset.filter(User.objects.all())
    """

    _filters: Dict[str, BaseFilter] = {}

    def __init__(
        self,
        query_params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize filterset.

        Args:
            query_params: Query parameters from request
            data: Alternative data source (overrides query_params)
        """
        self.query_params = data or query_params or {}
        self.errors = {}

    def filter(self, queryset):
        """
        Apply all matching filters to queryset.

        Args:
            queryset: Base queryset

        Returns:
            Filtered queryset
        """
        for filter_name, filter_obj in self._filters.items():
            # Check if filter parameter exists in query
            if filter_name not in self.query_params:
                continue

            value = self.query_params[filter_name]

            try:
                queryset = filter_obj.process(queryset, value)
            except ValueError as e:
                self.errors[filter_name] = str(e)
                logger.warning(f"Filter error for '{filter_name}': {e}")

        return queryset

    def is_valid(self) -> bool:
        """Check if all filters are valid."""
        return len(self.errors) == 0

    def get_errors(self) -> Dict[str, str]:
        """Get filter validation errors."""
        return self.errors


def create_filterset_from_model(model: Type, fields: List[str]) -> Type[FilterSet]:
    """
    Factory function to create FilterSet from model.

    Args:
        model: Model class
        fields: List of field names to create filters for

    Returns:
        FilterSet class

    Example:
        UserFilterSet = create_filterset_from_model(User, ['age', 'name', 'email'])
        filterset = UserFilterSet(query_params=request.query_params)
    """

    class AutoFilterSet(FilterSet):
        class Meta:
            model = model
            fields = fields

    return AutoFilterSet


__all__ = [
    "BaseFilter",
    "CharFilter",
    "IntegerFilter",
    "FloatFilter",
    "BooleanFilter",
    "DateFilter",
    "DateTimeFilter",
    "UUIDFilter",
    "ChoiceFilter",
    "MultipleValueFilter",
    "RangeFilter",
    "FilterSet",
    "FilterLookup",
    "create_filterset_from_model",
]
