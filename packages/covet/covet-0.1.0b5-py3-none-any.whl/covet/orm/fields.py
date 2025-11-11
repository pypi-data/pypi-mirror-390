"""
ORM Field Types and Relationships

Comprehensive field system supporting all major SQL data types and relationships.
"""

import datetime
import json
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, Union

from .exceptions import RelationshipError, ValidationError


class Field:
    """Base field class for all database columns."""

    def __init__(
        self,
        primary_key: bool = False,
        unique: bool = False,
        null: bool = True,
        blank: bool = True,
        default: Any = None,
        validators: Optional[List[Callable]] = None,
        db_column: Optional[str] = None,
        db_index: bool = False,
        help_text: str = "",
        verbose_name: str = "",
        choices: Optional[List[tuple]] = None,
        **kwargs,
    ):
        self.primary_key = primary_key
        self.unique = unique
        self.null = null
        self.blank = blank
        self.default = default
        self.validators = validators or []
        self.db_column = db_column
        self.db_index = db_index
        self.help_text = help_text
        self.verbose_name = verbose_name
        self.choices = choices

        self.name = None  # Set by ModelMeta
        self.model_class = None  # Set by ModelMeta

    def contribute_to_class(self, cls, name):
        """Called when field is added to a model class."""
        self.name = name
        self.model_class = cls
        if self.db_column is None:
            self.db_column = name

    def get_db_column(self) -> str:
        """Get the database column name."""
        return self.db_column or self.name

    def get_sql_type(self, engine: str) -> str:
        """Get SQL data type for specific database engine."""
        return self.sql_types.get(engine, self.sql_types["default"])

    def validate(self, value: Any, instance=None) -> Any:
        """Validate field value."""
        if value is None:
            if not self.null:
                raise ValidationError(f"Field '{self.name}' cannot be null")
            return value

        # Check choices
        if self.choices:
            choice_values = [choice[0] for choice in self.choices]
            if value not in choice_values:
                raise ValidationError(f"Value must be one of {choice_values}")

        # Run custom validators
        for validator in self.validators:
            validator(value)

        return self.to_python(value)

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python value."""
        return value

    def to_database(self, value: Any) -> Any:
        """Convert Python value to database value."""
        if value is None:
            return None
        return value

    def get_default(self):
        """Get default value."""
        if callable(self.default):
            return self.default()
        return self.default

    @property
    def sql_types(self) -> Dict[str, str]:
        """SQL type mapping for different databases."""
        return {
            "postgresql": "TEXT",
            "mysql": "TEXT",
            "sqlite": "TEXT",
            "default": "TEXT",
        }


class CharField(Field):
    """String field with maximum length."""

    def __init__(self, max_length: int = 255, **kwargs):
        self.max_length = max_length
        super().__init__(**kwargs)

    def validate(self, value: Any, instance=None) -> Any:
        value = super().validate(value, instance)
        if value is not None and len(str(value)) > self.max_length:
            raise ValidationError(f"Field '{self.name}' cannot exceed {self.max_length} characters")
        return value

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": f"VARCHAR({self.max_length})",
            "mysql": f"VARCHAR({self.max_length})",
            "sqlite": "TEXT",
            "default": f"VARCHAR({self.max_length})",
        }


class TextField(Field):
    """Large text field."""

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "TEXT",
            "mysql": "LONGTEXT",
            "sqlite": "TEXT",
            "default": "TEXT",
        }


class IntegerField(Field):
    """Integer field."""

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer value: {value}")

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "INTEGER",
            "mysql": "INT",
            "sqlite": "INTEGER",
            "default": "INTEGER",
        }


class BigIntegerField(Field):
    """Big integer field."""

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid integer value: {value}")

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "BIGINT",
            "mysql": "BIGINT",
            "sqlite": "INTEGER",
            "default": "BIGINT",
        }


class FloatField(Field):
    """Floating point field."""

    def to_python(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            raise ValidationError(f"Invalid float value: {value}")

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "REAL",
            "mysql": "FLOAT",
            "sqlite": "REAL",
            "default": "FLOAT",
        }


class DecimalField(Field):
    """Decimal field with precision."""

    def __init__(self, max_digits: int = 10, decimal_places: int = 2, **kwargs):
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        super().__init__(**kwargs)

    @property
    def sql_types(self) -> Dict[str, str]:
        precision = f"({self.max_digits},{self.decimal_places})"
        return {
            "postgresql": f"DECIMAL{precision}",
            "mysql": f"DECIMAL{precision}",
            "sqlite": "REAL",
            "default": f"DECIMAL{precision}",
        }


class BooleanField(Field):
    """Boolean field."""

    def to_python(self, value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, str)):
            return bool(int(value))
        raise ValidationError(f"Invalid boolean value: {value}")

    def to_database(self, value: Any) -> Any:
        if value is None:
            return None
        return int(bool(value))

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "BOOLEAN",
            "mysql": "TINYINT(1)",
            "sqlite": "INTEGER",
            "default": "BOOLEAN",
        }


class DateTimeField(Field):
    """DateTime field."""

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        super().__init__(**kwargs)

    def to_python(self, value: Any) -> Optional[datetime.datetime]:
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                raise ValidationError(f"Invalid datetime value: {value}")
        raise ValidationError(f"Invalid datetime value: {value}")

    def to_database(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        return str(value)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "TIMESTAMP",
            "mysql": "DATETIME",
            "sqlite": "TEXT",
            "default": "TIMESTAMP",
        }


class DateField(Field):
    """Date field."""

    def to_python(self, value: Any) -> Optional[datetime.date]:
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            try:
                return datetime.datetime.fromisoformat(value).date()
            except ValueError:
                raise ValidationError(f"Invalid date value: {value}")
        raise ValidationError(f"Invalid date value: {value}")

    def to_database(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value.isoformat()
        return str(value)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "DATE",
            "mysql": "DATE",
            "sqlite": "TEXT",
            "default": "DATE",
        }


class TimeField(Field):
    """Time field."""

    def to_python(self, value: Any) -> Optional[datetime.time]:
        if value is None:
            return None
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, str):
            try:
                return datetime.time.fromisoformat(value)
            except ValueError:
                raise ValidationError(f"Invalid time value: {value}")
        raise ValidationError(f"Invalid time value: {value}")

    def to_database(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, datetime.time):
            return value.isoformat()
        return str(value)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "TIME",
            "mysql": "TIME",
            "sqlite": "TEXT",
            "default": "TIME",
        }


class JSONField(Field):
    """JSON field."""

    def to_python(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(f"Invalid JSON value: {value}")
        return value

    def to_database(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "JSONB",
            "mysql": "JSON",
            "sqlite": "TEXT",
            "default": "TEXT",
        }


class BinaryField(Field):
    """Binary data field."""

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "BYTEA",
            "mysql": "LONGBLOB",
            "sqlite": "BLOB",
            "default": "BLOB",
        }


class UUIDField(Field):
    """UUID field."""

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "UUID",
            "mysql": "CHAR(36)",
            "sqlite": "TEXT",
            "default": "CHAR(36)",
        }


# Relationship Fields


class RelationshipField(Field):
    """Base class for relationship fields."""

    def __init__(self, to: Union[str, Type], **kwargs):
        self.to = to
        self.related_name = kwargs.pop("related_name", None)
        super().__init__(**kwargs)

    def get_related_model(self):
        """Get the related model class."""
        if isinstance(self.to, str):
            # Handle string references (for lazy loading)
            from .models import ModelRegistry

            return ModelRegistry.get_model(self.to)
        return self.to


class ForeignKey(RelationshipField):
    """Foreign key relationship."""

    def __init__(self, to: Union[str, Type], on_delete: str = "CASCADE", **kwargs):
        self.on_delete = on_delete
        super().__init__(to, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)

        # Store the database field name
        self.db_field_name = f"{name}_id"

        # Add reverse relationship to related model
        if self.related_name:
            related_model = self.get_related_model()
            if related_model:
                setattr(
                    related_model,
                    self.related_name,
                    OneToManyField(cls, foreign_key=name),
                )

    def get_db_column(self) -> str:
        """Get the database column name for FK."""
        return self.db_field_name

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "INTEGER REFERENCES",
            "mysql": "INT",
            "sqlite": "INTEGER",
            "default": "INTEGER",
        }


class OneToManyField(RelationshipField):
    """One-to-many relationship (reverse of ForeignKey)."""

    def __init__(self, to: Union[str, Type], foreign_key: str, **kwargs):
        self.foreign_key = foreign_key
        super().__init__(to, **kwargs)

    def contribute_to_class(self, cls, name):
        # This is a virtual field, doesn't create database column
        super().contribute_to_class(cls, name)


class ManyToManyField(RelationshipField):
    """Many-to-many relationship."""

    def __init__(self, to: Union[str, Type], through: Optional[str] = None, **kwargs):
        self.through = through
        super().__init__(to, **kwargs)

    def contribute_to_class(self, cls, name):
        super().contribute_to_class(cls, name)

        # Create through table if not specified
        if not self.through:
            related_model = self.get_related_model()
            table_name = f"{cls._meta.table_name}_{related_model._meta.table_name}"
            self.through = table_name


# Auto fields


class AutoField(IntegerField):
    """Auto-incrementing integer field."""

    def __init__(self, **kwargs):
        kwargs["primary_key"] = True
        kwargs["null"] = True  # Allow null before DB assigns value
        super().__init__(**kwargs)

    def validate(self, value: Any, instance=None) -> Any:
        """Auto fields don't need validation during creation."""
        if value is None and instance and hasattr(instance, "_state") and instance._state.adding:
            return None  # Allow null for new instances
        return super().validate(value, instance)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "SERIAL PRIMARY KEY",
            "mysql": "INT AUTO_INCREMENT PRIMARY KEY",
            "sqlite": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "default": "INTEGER PRIMARY KEY AUTO_INCREMENT",
        }


class BigAutoField(BigIntegerField):
    """Auto-incrementing big integer field."""

    def __init__(self, **kwargs):
        kwargs["primary_key"] = True
        kwargs["null"] = False
        super().__init__(**kwargs)

    @property
    def sql_types(self) -> Dict[str, str]:
        return {
            "postgresql": "BIGSERIAL PRIMARY KEY",
            "mysql": "BIGINT AUTO_INCREMENT PRIMARY KEY",
            "sqlite": "INTEGER PRIMARY KEY AUTOINCREMENT",
            "default": "BIGINT PRIMARY KEY AUTO_INCREMENT",
        }
