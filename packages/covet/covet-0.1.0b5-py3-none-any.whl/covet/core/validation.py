"""
High-Performance Validation Framework for CovetPy

Provides comprehensive data validation without Pydantic dependency.
Features include type validation, constraints, transformations, and
advanced performance optimization.
"""

import builtins
import inspect
import json
import re
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
from typing import (
    Any,
    Callable,
    Optional,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from urllib.parse import urlparse


class ValidationError(Exception):
    """Validation error with field context."""

    def __init__(self, message: str, field_name: str = None, value: Any = None):
        self.message = message
        self.field_name = field_name
        self.value = value
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        if self.field_name:
            return f"Validation error in field '{self.field_name}': {self.message}"
        return f"Validation error: {self.message}"


@dataclass
class FieldMetadata:
    """Metadata for validated fields."""

    name: str
    type_hint: type
    default: Any = None
    is_required: bool = True
    alias: Optional[str] = None
    validators: list["Validator"] = field(default_factory=list)
    transformers: list[Callable] = field(default_factory=list)
    description: Optional[str] = None  # Added for compatibility

    # Constraints
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[Union[int, float, Decimal]] = None
    max_value: Optional[Union[int, float, Decimal]] = None
    allowed_values: Optional[set[Any]] = None

    def __post_init__(self):
        """Compile regex pattern if provided."""
        if self.pattern:
            self._compiled_pattern = re.compile(self.pattern)
        else:
            self._compiled_pattern = None


class Validator(ABC):
    """Base validator interface."""

    @abstractmethod
    def validate(self, value: Any, field: FieldMetadata) -> Any:
        """Validate and potentially transform the value."""

    @abstractmethod
    def __str__(self) -> str:
        """Human-readable description of the validator."""


class TypeValidator(Validator):
    """High-performance type validation with coercion support."""

    def __init__(self, target_type: type, strict: bool = False) -> None:
        self.target_type = target_type
        self.strict = strict
        self._origin = get_origin(target_type)
        self._args = get_args(target_type)

    def validate(self, value: Any, field: FieldMetadata) -> Any:
        """Validate type with optional coercion."""
        if value is None:
            if not field.is_required:
                return field.default
            raise ValidationError("Required field is None", field.name)

        # Handle generic types
        if self._origin is not None:
            return self._validate_generic(value, field)

        # Direct type check for strict mode
        if self.strict:
            if not isinstance(value, self.target_type):
                raise ValidationError(
                    f"Expected {self.target_type.__name__}, got {type(value).__name__}",
                    field.name,
                    value,
                )
            return value

        # Type coercion for non-strict mode
        try:
            if self.target_type == bool:
                return self._coerce_bool(value)
            elif self.target_type == int:
                return self._coerce_int(value)
            elif self.target_type == float:
                return self._coerce_float(value)
            elif self.target_type == str:
                return str(value)
            elif self.target_type == bytes:
                return self._coerce_bytes(value)
            elif self.target_type == datetime:
                return self._coerce_datetime(value)
            else:
                return self.target_type(value)
        except (ValueError, TypeError) as e:
            raise ValidationError(
                f"Cannot convert {type(value).__name__} to {self.target_type.__name__}: {e}",
                field.name,
                value,
            )

    def _validate_generic(self, value: Any, field: FieldMetadata) -> Any:
        """Validate generic types like List, Dict, etc."""
        if self._origin == list:
            if not isinstance(value, (list, tuple)):
                raise ValidationError(f"Expected list, got {type(value).__name__}", field.name)

            if self._args:
                item_type = self._args[0]
                item_validator = TypeValidator(item_type, self.strict)
                item_field = FieldMetadata(name=f"{field.name}[item]", type_hint=item_type)
                return [item_validator.validate(item, item_field) for item in value]
            return list(value)

        elif self._origin == dict:
            if not isinstance(value, dict):
                raise ValidationError(f"Expected dict, got {type(value).__name__}", field.name)

            if len(self._args) == 2:
                key_type, value_type = self._args
                key_validator = TypeValidator(key_type, self.strict)
                value_validator = TypeValidator(value_type, self.strict)

                result = {}
                for k, v in value.items():
                    key_field = FieldMetadata(name=f"{field.name}[key]", type_hint=key_type)
                    value_field = FieldMetadata(name=f"{field.name}[{k}]", type_hint=value_type)
                    validated_key = key_validator.validate(k, key_field)
                    validated_value = value_validator.validate(v, value_field)
                    result[validated_key] = validated_value
                return result
            return dict(value)

        elif self._origin == set:
            if not isinstance(value, (set, list, tuple)):
                raise ValidationError(f"Expected set-like, got {type(value).__name__}", field.name)

            if self._args:
                item_type = self._args[0]
                item_validator = TypeValidator(item_type, self.strict)
                item_field = FieldMetadata(name=f"{field.name}[item]", type_hint=item_type)
                return {item_validator.validate(item, item_field) for item in value}
            return set(value)

        else:
            raise ValidationError(f"Unsupported generic type: {self._origin}", field.name)

    def _coerce_bool(self, value: Any) -> bool:
        """Coerce value to boolean."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            lower = value.lower()
            if lower in ("true", "1", "yes", "on"):
                return True
            elif lower in ("false", "0", "no", "off"):
                return False
        return bool(value)

    def _coerce_int(self, value: Any) -> int:
        """Coerce value to integer."""
        if isinstance(value, bool):
            return int(value)
        return int(value)

    def _coerce_float(self, value: Any) -> float:
        """Coerce value to float."""
        if isinstance(value, bool):
            return float(value)
        return float(value)

    def _coerce_bytes(self, value: Any) -> bytes:
        """Coerce value to bytes."""
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode("utf-8")
        raise TypeError("Cannot convert to bytes")

    def _coerce_datetime(self, value: Any) -> datetime:
        """Coerce value to datetime."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Try common datetime formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%SZ",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue

            raise ValueError(f"Unable to parse datetime: {value}")

        raise TypeError("Cannot convert to datetime")

    def __str__(self) -> str:
        return f"TypeValidator({self.target_type})"


class ConstraintValidator(Validator):
    """Validates field constraints like length, range, pattern."""

    def validate(self, value: Any, field: FieldMetadata) -> Any:
        """Apply constraint validation."""
        # Length constraints
        if field.min_length is not None or field.max_length is not None:
            if hasattr(value, "__len__"):
                length = len(value)
                if field.min_length is not None and length < field.min_length:
                    raise ValidationError(
                        f"Length {length} is less than minimum {field.min_length}",
                        field.name,
                        value,
                    )
                if field.max_length is not None and length > field.max_length:
                    raise ValidationError(
                        f"Length {length} exceeds maximum {field.max_length}",
                        field.name,
                        value,
                    )

        # Numeric range constraints
        if field.min_value is not None or field.max_value is not None:
            if isinstance(value, (int, float, Decimal)):
                if field.min_value is not None and value < field.min_value:
                    raise ValidationError(
                        f"Value {value} is less than minimum {field.min_value}",
                        field.name,
                        value,
                    )
                if field.max_value is not None and value > field.max_value:
                    raise ValidationError(
                        f"Value {value} exceeds maximum {field.max_value}",
                        field.name,
                        value,
                    )

        # Pattern validation
        if field.pattern and isinstance(value, str):
            if not field._compiled_pattern.match(value):
                raise ValidationError(
                    f"Value does not match pattern: {field.pattern}", field.name, value
                )

        # Allowed values constraint
        if field.allowed_values is not None:
            if value not in field.allowed_values:
                raise ValidationError(
                    f"Value must be one of: {field.allowed_values}", field.name, value
                )

        return value

    def __str__(self) -> str:
        return "ConstraintValidator"


# Built-in validators
class EmailValidator(Validator):
    """Validates email addresses."""

    def validate(self, value: Any, field: FieldMetadata) -> str:
        """Validate email format."""
        if not isinstance(value, str):
            raise ValidationError("Email must be a string", field.name, value)

        # Basic email validation
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        if not email_pattern.match(value):
            raise ValidationError("Invalid email format", field.name, value)

        return value

    def __str__(self) -> str:
        return "EmailValidator"


class URLValidator(Validator):
    """Validates URLs."""

    def __init__(self, schemes: Optional[set[str]] = None) -> None:
        self.schemes = schemes or {"http", "https"}

    def validate(self, value: Any, field: FieldMetadata) -> str:
        """Validate URL format."""
        if not isinstance(value, str):
            raise ValidationError("URL must be a string", field.name, value)

        try:
            parsed = urlparse(value)
            if not parsed.scheme:
                raise ValidationError("URL must have a scheme", field.name, value)
            if parsed.scheme not in self.schemes:
                raise ValidationError(
                    f"URL scheme must be one of: {self.schemes}", field.name, value
                )
            if not parsed.netloc:
                raise ValidationError("URL must have a network location", field.name, value)
        except Exception as e:
            raise ValidationError(f"Invalid URL: {e}", field.name, value)

        return value

    def __str__(self) -> str:
        return f"URLValidator({self.schemes})"


class RangeValidator(Validator):
    """Validates numeric ranges."""

    def __init__(
        self, min_value: Optional[float] = None, max_value: Optional[float] = None
    ) -> None:
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any, field: FieldMetadata) -> Any:
        """Validate numeric range."""
        if self.min_value is not None and value < self.min_value:
            raise ValidationError(
                f"Value {value} is less than minimum {self.min_value}",
                field.name,
                value,
            )

        if self.max_value is not None and value > self.max_value:
            raise ValidationError(
                f"Value {value} exceeds maximum {self.max_value}", field.name, value
            )

        return value

    def __str__(self) -> str:
        return f"RangeValidator({self.min_value}, {self.max_value})"


# Field decorator function
def Field(
    default: Any = None,
    alias: Optional[str] = None,
    validators: Optional[list[Validator]] = None,
    transformers: Optional[list[Callable]] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    min_value: Optional[Union[int, float, Decimal]] = None,
    max_value: Optional[Union[int, float, Decimal]] = None,
    allowed_values: Optional[set[Any]] = None,
    description: Optional[str] = None,  # Added for compatibility
    required: Optional[bool] = None,  # Added for compatibility
) -> Any:
    """Field definition with validation metadata."""
    # Determine if field is required
    is_required = required if required is not None else (default is None)

    return FieldMetadata(
        name="",  # Will be set by ValidatedModel
        type_hint=Any,  # Will be set by ValidatedModel
        default=default,
        is_required=is_required,
        alias=alias,
        validators=validators or [],
        transformers=transformers or [],
        description=description,
        min_length=min_length,
        max_length=max_length,
        pattern=pattern,
        min_value=min_value,
        max_value=max_value,
        allowed_values=allowed_values,
    )


def validate_function(**validators: Validator):
    """Decorator to validate function parameters."""

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)

        @lru_cache(maxsize=128)
        def get_param_validators():
            """Cache parameter validators."""
            param_validators = {}

            for param_name, validator in validators.items():
                if param_name in sig.parameters:
                    param_validators[param_name] = validator

            return param_validators

        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()

            param_validators = get_param_validators()

            for param_name, value in bound_args.arguments.items():
                if param_name in param_validators:
                    validator = param_validators[param_name]
                    field_meta = FieldMetadata(
                        name=param_name, type_hint=sig.parameters[param_name].annotation
                    )
                    bound_args.arguments[param_name] = validator.validate(value, field_meta)

            return func(*bound_args.args, **bound_args.kwargs)

        return wrapper

    return decorator


class ValidatedModel:
    """Base class for validated models."""

    _field_metadata: dict[str, FieldMetadata] = {}
    _validators_cache: weakref.WeakKeyDictionary = weakref.WeakKeyDictionary()

    def __init_subclass__(cls, **kwargs):
        """Initialize field metadata for subclass."""
        super().__init_subclass__(**kwargs)
        cls._field_metadata = {}

        # Get type hints
        hints = get_type_hints(cls)

        # Process fields
        for name, type_hint in hints.items():
            if name.startswith("_"):
                continue

            # Get field metadata
            field_value = getattr(cls, name, None)
            if isinstance(field_value, FieldMetadata):
                metadata = field_value
                metadata.name = name
                metadata.type_hint = type_hint
            else:
                metadata = FieldMetadata(
                    name=name,
                    type_hint=type_hint,
                    default=field_value,
                    is_required=field_value is None,
                )

            # Add type validator
            metadata.validators.insert(0, TypeValidator(type_hint))

            cls._field_metadata[name] = metadata

    def __init__(self, **data) -> None:
        """Initialize model with validation."""
        errors = []

        # Validate and set fields
        for field_name, metadata in self._field_metadata.items():
            # Get value from data (check alias too)
            value = data.get(field_name)
            if value is None and metadata.alias:
                value = data.get(metadata.alias)

            try:
                validated_value = self._validate_field(value, metadata)
                setattr(self, field_name, validated_value)
            except ValidationError as e:
                errors.append(e)

        if errors:
            error_messages = [str(e) for e in errors]
            raise ValidationError(f"Validation failed: {'; '.join(error_messages)}")

    def _validate_field(self, value: Any, metadata: FieldMetadata) -> Any:
        """Validate a single field."""
        # Apply validators in order
        for validator in metadata.validators:
            value = validator.validate(value, metadata)

        # Apply transformers
        for transformer in metadata.transformers:
            value = transformer(value)

        return value

    def dict(self, by_alias: bool = False, exclude_none: bool = False) -> dict[str, Any]:
        """Convert model to dictionary."""
        result = {}

        for field_name, metadata in self._field_metadata.items():
            value = getattr(self, field_name)

            if exclude_none and value is None:
                continue

            key = metadata.alias if by_alias and metadata.alias else field_name
            result[key] = value

        return result

    def json(self, by_alias: bool = False, exclude_none: bool = False) -> str:
        """Convert model to JSON string."""

        return json.dumps(self.dict(by_alias=by_alias, exclude_none=exclude_none))

    @classmethod
    def from_dict(cls, data: builtins.dict[str, Any]) -> "ValidatedModel":
        """Create model from dictionary."""
        return cls(**data)

    @classmethod
    def schema(cls) -> builtins.dict[str, Any]:
        """Generate JSON schema for the model."""
        schema = {"type": "object", "properties": {}, "required": []}

        for field_name, metadata in cls._field_metadata.items():
            field_schema = _get_field_schema(metadata)
            schema["properties"][field_name] = field_schema

            if metadata.is_required:
                schema["required"].append(field_name)

        return schema


def _get_field_schema(metadata: FieldMetadata) -> dict[str, Any]:
    """Generate JSON schema for a field."""
    schema = {"type": _get_json_type(metadata.type_hint)}

    if metadata.min_length is not None:
        schema["minLength"] = metadata.min_length
    if metadata.max_length is not None:
        schema["maxLength"] = metadata.max_length
    if metadata.pattern:
        schema["pattern"] = metadata.pattern
    if metadata.min_value is not None:
        schema["minimum"] = metadata.min_value
    if metadata.max_value is not None:
        schema["maximum"] = metadata.max_value
    if metadata.allowed_values:
        schema["enum"] = list(metadata.allowed_values)

    return schema


def _is_optional(type_hint: type) -> bool:
    """Check if type hint is Optional."""
    return get_origin(type_hint) is Union and type(None) in get_args(type_hint)


def _get_json_type(type_hint: type) -> str:
    """Get JSON schema type for Python type."""
    origin = get_origin(type_hint)

    if origin is Union:
        args = get_args(type_hint)
        non_none_args = [arg for arg in args if arg is not type(None)]
        if len(non_none_args) == 1:
            return _get_json_type(non_none_args[0])
        return "object"

    if origin in (list, tuple):
        return "array"
    if origin == dict:
        return "object"

    if type_hint == str:
        return "string"
    elif type_hint in (int, float):
        return "number"
    elif type_hint == bool:
        return "boolean"
    elif type_hint == list:
        return "array"
    elif type_hint == dict:
        return "object"
    else:
        return "object"


# Export all public classes and functions
__all__ = [
    "ValidationError",
    "FieldMetadata",
    "Validator",
    "TypeValidator",
    "ConstraintValidator",
    "EmailValidator",
    "URLValidator",
    "RangeValidator",
    "Field",
    "validate_function",
    "ValidatedModel",
]
