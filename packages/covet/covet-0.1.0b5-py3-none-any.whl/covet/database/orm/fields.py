"""
ORM Field Types

Comprehensive field type definitions for the CovetPy ORM.
Supports 17+ field types with validation, serialization, and database mapping.
"""

import io
import ipaddress
import json
import mimetypes
import os
import re
import uuid
from datetime import date, datetime
from datetime import time as dt_time
from datetime import timedelta
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, BinaryIO, Callable, List, Optional, Type, Union


class Field:
    """
    Base class for all ORM fields.

    Provides common functionality for field definition, validation, and serialization.
    """

    def __init__(
        self,
        primary_key: bool = False,
        unique: bool = False,
        nullable: bool = True,
        null: bool = None,  # Alias for nullable
        default: Any = None,
        default_factory: Optional[Callable] = None,
        db_column: Optional[str] = None,
        db_index: bool = False,
        validators: Optional[List[Callable]] = None,
        verbose_name: Optional[str] = None,
        help_text: Optional[str] = None,
        editable: bool = True,
        choices: Optional[List] = None,
    ):
        """
        Initialize field.

        Args:
            primary_key: Whether this is a primary key
            unique: Whether values must be unique
            nullable: Whether NULL values are allowed (alias: null)
            null: Alias for nullable
            default: Default value
            default_factory: Callable that returns default value
            db_column: Database column name (defaults to field name)
            db_index: Whether to create an index
            validators: List of validation functions
            verbose_name: Human-readable field name
            help_text: Help text for documentation
            editable: Whether field can be edited
            choices: List of valid choices
        """
        self.primary_key = primary_key
        self.unique = unique
        # Support both 'nullable' and 'null' parameters (null takes precedence)
        if null is not None:
            nullable = null
        self.nullable = nullable if not primary_key else False
        self.default = default
        self.default_factory = default_factory
        self.db_column = db_column
        self.db_index = db_index or unique or primary_key
        self.validators = validators or []
        self.verbose_name = verbose_name
        self.help_text = help_text
        self.editable = editable
        self.choices = choices

        self.name: Optional[str] = None  # Set by metaclass
        self.model: Optional[Type] = None  # Set by metaclass

    def get_default(self) -> Any:
        """Get default value for this field."""
        if self.default_factory:
            return self.default_factory()
        return self.default

    def validate(self, value: Any) -> Any:
        """
        Validate field value.

        Args:
            value: Value to validate

        Returns:
            Validated value

        Raises:
            ValueError: If validation fails
        """
        # Check nullable
        if value is None:
            if not self.nullable:
                raise ValueError(f"{self.name}: NULL values not allowed")
            return None

        # Check choices
        if self.choices and value not in [
            choice[0] if isinstance(choice, tuple) else choice for choice in self.choices
        ]:
            raise ValueError(f"{self.name}: Value must be one of {self.choices}")

        # Run custom validators
        for validator in self.validators:
            validator(value)

        # Type-specific validation
        return self.to_python(value)

    def to_python(self, value: Any) -> Any:
        """
        Convert database value to Python value.

        Args:
            value: Database value

        Returns:
            Python value
        """
        return value

    def to_db(self, value: Any) -> Any:
        """
        Convert Python value to database value.

        Args:
            value: Python value

        Returns:
            Database value
        """
        if value is None:
            return None
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """
        Get database column type for this field.

        Args:
            dialect: Database dialect (postgresql, mysql, sqlite)

        Returns:
            SQL column type
        """
        raise NotImplementedError("Subclasses must implement get_db_type()")

    def __get__(self, instance, owner):
        """
        Descriptor protocol: Get field value from instance.

        When accessing Model.field_name, returns the Field object (for class access).
        When accessing instance.field_name, returns the value from instance.__dict__.

        Args:
            instance: Model instance (None for class access)
            owner: Model class

        Returns:
            Field object (class access) or field value (instance access)
        """
        if instance is None:
            # Class access: Model.username -> Field object
            return self

        # Instance access: user.username -> actual value
        # Check instance __dict__ first (where values are stored)
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]

        # Not set yet, return default
        return self.get_default()

    def __set__(self, instance, value):
        """
        Descriptor protocol: Set field value on instance.

        Stores the value in instance.__dict__[field_name].

        Args:
            instance: Model instance
            value: Value to set
        """
        instance.__dict__[self.name] = value


class CharField(Field):
    """Character field for short strings."""

    def __init__(self, max_length: int = 255, min_length: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        if len(value) > self.max_length:
            raise ValueError(
                f"{self.name}: String length {len(value)} exceeds maximum {self.max_length}"
            )

        if len(value) < self.min_length:
            raise ValueError(
                f"{self.name}: String length {len(value)} below minimum {self.min_length}"
            )

        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return f"VARCHAR({self.max_length})"


class TextField(Field):
    """Text field for long strings."""

    def to_python(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        return str(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return "TEXT"


class IntegerField(Field):
    """Integer field."""

    def __init__(
        self,
        auto_increment: bool = False,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.auto_increment = auto_increment
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"{self.name}: Value must be an integer")

        if self.min_value is not None and value < self.min_value:
            raise ValueError(f"{self.name}: Value {value} below minimum {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            raise ValueError(f"{self.name}: Value {value} above maximum {self.max_value}")

        return value

    def to_python(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        return int(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "SERIAL" if self.auto_increment else "INTEGER"
        elif dialect == "mysql":
            return "INT AUTO_INCREMENT" if self.auto_increment else "INT"
        else:  # sqlite
            return "INTEGER"


class BigIntegerField(IntegerField):
    """64-bit integer field."""

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "BIGSERIAL" if self.auto_increment else "BIGINT"
        elif dialect == "mysql":
            return "BIGINT AUTO_INCREMENT" if self.auto_increment else "BIGINT"
        else:  # sqlite
            return "INTEGER"


class SmallIntegerField(IntegerField):
    """16-bit integer field."""

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "SMALLSERIAL" if self.auto_increment else "SMALLINT"
        elif dialect == "mysql":
            return "SMALLINT AUTO_INCREMENT" if self.auto_increment else "SMALLINT"
        else:  # sqlite
            return "INTEGER"


class FloatField(Field):
    """Floating point field."""

    def to_python(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        return float(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "FLOAT"
        return "REAL"


class DecimalField(Field):
    """Decimal field for precise numeric values."""

    def __init__(self, max_digits: int = 10, decimal_places: int = 2, **kwargs):
        super().__init__(**kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def to_python(self, value: Any) -> Optional[Decimal]:
        if value is None:
            return None
        return Decimal(str(value))

    def to_db(self, value: Any) -> Any:
        """Convert Decimal to database value."""
        if value is None:
            return None
        # SQLite doesn't support Decimal, so convert to float
        # For other databases, keep as Decimal
        if isinstance(value, Decimal):
            return float(value)  # SQLite and others can handle float
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return f"NUMERIC({self.max_digits}, {self.decimal_places})"


class BooleanField(Field):
    """Boolean field."""

    def __init__(self, **kwargs):
        if "default" not in kwargs:
            kwargs["default"] = False
        super().__init__(**kwargs)

    def to_python(self, value: Any) -> Optional[bool]:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return bool(value)
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "BOOLEAN"
        elif dialect == "sqlite":
            return "INTEGER"  # SQLite doesn't have native boolean
        return "BOOLEAN"


class DateTimeField(Field):
    """DateTime field."""

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now  # Update on every save
        self.auto_now_add = auto_now_add  # Set on first save only

        if auto_now or auto_now_add:
            self.editable = False

    def to_python(self, value: Any) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            # Try parsing common formats
            try:
                return datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
        raise ValueError(f"{self.name}: Invalid datetime value")

    def to_db(self, value: Any) -> Any:
        """Convert datetime to database value."""
        if value is None:
            return None
        if isinstance(value, datetime):
            # SQLite stores datetime as ISO format string
            return value.isoformat()
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "mysql":
            return "DATETIME"
        elif dialect == "sqlite":
            return "TEXT"  # SQLite stores as text
        return "TIMESTAMP"


class DateField(Field):
    """Date field."""

    def to_python(self, value: Any) -> Optional[date]:
        if value is None:
            return None
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError(f"{self.name}: Invalid date value")

    def to_db(self, value: Any) -> Any:
        """Convert date to database value."""
        if value is None:
            return None
        if isinstance(value, date):
            # SQLite stores date as ISO format string
            return value.isoformat()
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "sqlite":
            return "TEXT"
        return "DATE"


class TimeField(Field):
    """Time field."""

    def to_python(self, value: Any) -> Optional[dt_time]:
        if value is None:
            return None
        if isinstance(value, dt_time):
            return value
        if isinstance(value, str):
            return dt_time.fromisoformat(value)
        raise ValueError(f"{self.name}: Invalid time value")

    def to_db(self, value: Any) -> Any:
        """Convert time to database value."""
        if value is None:
            return None
        if isinstance(value, dt_time):
            # SQLite stores time as ISO format string
            return value.isoformat()
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "sqlite":
            return "TEXT"
        return "TIME"


class JSONField(Field):
    """JSON field for storing structured data with security protections."""

    # Security limits to prevent DoS attacks
    MAX_JSON_SIZE = 1_000_000  # 1MB maximum JSON size
    MAX_JSON_DEPTH = 20  # Maximum nesting depth

    def __init__(self, max_size: int = None, max_depth: int = None, **kwargs):
        """
        Initialize JSONField with optional security limits.

        Args:
            max_size: Maximum JSON string size in bytes (default: 1MB)
            max_depth: Maximum nesting depth (default: 20)
            **kwargs: Additional field parameters
        """
        super().__init__(**kwargs)
        self.max_size = max_size if max_size is not None else self.MAX_JSON_SIZE
        self.max_depth = max_depth if max_depth is not None else self.MAX_JSON_DEPTH

        # Validate limits
        if self.max_size > self.MAX_JSON_SIZE:
            raise ValueError(f"max_size cannot exceed {self.MAX_JSON_SIZE} bytes")
        if self.max_depth > self.MAX_JSON_DEPTH:
            raise ValueError(f"max_depth cannot exceed {self.MAX_JSON_DEPTH}")

    def _check_json_depth(self, obj: Any, current_depth: int = 0) -> int:
        """
        Recursively check JSON nesting depth.

        Args:
            obj: JSON object to check
            current_depth: Current recursion depth

        Returns:
            Maximum depth found

        Raises:
            ValueError: If depth exceeds maximum
        """
        if current_depth > self.max_depth:
            raise ValueError(
                f"{self.name}: JSON nesting too deep (>{self.max_depth} levels). "
                f"Maximum allowed: {self.max_depth} levels"
            )

        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(
                self._check_json_depth(v, current_depth + 1)
                for v in obj.values()
            )
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(
                self._check_json_depth(item, current_depth + 1)
                for item in obj
            )
        else:
            return current_depth

    def to_python(self, value: Any) -> Any:
        if value is None:
            return None

        if isinstance(value, str):
            # Security: Check JSON size before parsing
            if len(value) > self.max_size:
                raise ValueError(
                    f"{self.name}: JSON too large ({len(value)} bytes). "
                    f"Maximum allowed: {self.max_size} bytes"
                )

            # Parse JSON
            try:
                result = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(f"{self.name}: Invalid JSON - {e}")

            # Security: Check nesting depth after parsing
            try:
                self._check_json_depth(result)
            except ValueError:
                raise  # Re-raise depth error

            return result

        return value

    def to_db(self, value: Any) -> Optional[str]:
        if value is None:
            return None

        # Convert to JSON string
        json_str = json.dumps(value)

        # Security: Verify size before returning
        if len(json_str) > self.max_size:
            raise ValueError(
                f"{self.name}: JSON too large ({len(json_str)} bytes). "
                f"Maximum allowed: {self.max_size} bytes"
            )

        return json_str

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "JSONB"
        elif dialect == "mysql":
            return "JSON"
        return "TEXT"


class UUIDField(Field):
    """UUID field."""

    def __init__(self, auto_generate: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.auto_generate = auto_generate
        if auto_generate and not kwargs.get("default_factory"):
            self.default_factory = uuid.uuid4

    def to_python(self, value: Any) -> Optional[uuid.UUID]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(str(value))

    def to_db(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "UUID"
        return "VARCHAR(36)"


class EmailField(CharField):
    """Email field with ReDoS-safe validation."""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 254)
        super().__init__(**kwargs)

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        # Security: Use O(n) validation instead of regex to prevent ReDoS
        # RFC 5321 compliant basic validation without regex

        # Check basic structure
        if '@' not in value:
            raise ValueError(f"{self.name}: Invalid email address (missing @)")

        # Split into local and domain parts
        local, _, domain = value.rpartition('@')

        if not local or not domain:
            raise ValueError(f"{self.name}: Invalid email address (empty local or domain part)")

        # RFC 5321 length limits
        if len(local) > 64:
            raise ValueError(
                f"{self.name}: Email local part too long (max 64 characters, got {len(local)})"
            )

        if len(domain) > 253:
            raise ValueError(
                f"{self.name}: Email domain too long (max 253 characters, got {len(domain)})"
            )

        # Domain must contain at least one dot
        if '.' not in domain:
            raise ValueError(f"{self.name}: Invalid email address (domain must contain a dot)")

        # Domain can't start or end with dot or hyphen
        if domain.startswith('.') or domain.endswith('.'):
            raise ValueError(f"{self.name}: Invalid email address (domain cannot start/end with dot)")

        if domain.startswith('-') or domain.endswith('-'):
            raise ValueError(f"{self.name}: Invalid email address (domain cannot start/end with hyphen)")

        # Check for consecutive dots
        if '..' in domain:
            raise ValueError(f"{self.name}: Invalid email address (consecutive dots in domain)")

        # Validate characters in local part (O(n) character check)
        # Allowed: a-z A-Z 0-9 . _ % + -
        valid_local_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._%+-')
        for char in local:
            if char not in valid_local_chars:
                raise ValueError(
                    f"{self.name}: Invalid character '{char}' in email local part"
                )

        # Validate characters in domain part (O(n) character check)
        # Allowed: a-z A-Z 0-9 . -
        valid_domain_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-')
        for char in domain:
            if char not in valid_domain_chars:
                raise ValueError(
                    f"{self.name}: Invalid character '{char}' in email domain"
                )

        # Domain labels validation (between dots)
        labels = domain.split('.')
        for label in labels:
            if not label:
                raise ValueError(f"{self.name}: Invalid email address (empty domain label)")
            if len(label) > 63:
                raise ValueError(
                    f"{self.name}: Email domain label too long (max 63 characters, got {len(label)})"
                )
            # Label can't start or end with hyphen
            if label.startswith('-') or label.endswith('-'):
                raise ValueError(
                    f"{self.name}: Invalid email address (domain label cannot start/end with hyphen)"
                )

        # TLD (last label) must be at least 2 characters and alphabetic
        tld = labels[-1]
        if len(tld) < 2:
            raise ValueError(
                f"{self.name}: Invalid email address (TLD must be at least 2 characters)"
            )

        # Return normalized (lowercase) email
        return value.lower()


class URLField(CharField):
    """URL field with validation."""

    def __init__(self, **kwargs):
        kwargs.setdefault("max_length", 2048)
        super().__init__(**kwargs)

    def validate(self, value: Any) -> Any:
        value = super().validate(value)
        if value is None:
            return None

        # Simple URL validation
        url_pattern = r"^https?://[^\s]+"
        if not re.match(url_pattern, value):
            raise ValueError(f"{self.name}: Invalid URL")

        return value


class BinaryField(Field):
    """Binary data field."""

    def to_python(self, value: Any) -> Optional[bytes]:
        if value is None:
            return None
        if isinstance(value, bytes):
            return value
        if isinstance(value, str):
            return value.encode("utf-8")
        return bytes(value)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            return "BYTEA"
        elif dialect == "mysql":
            return "BLOB"
        return "BLOB"


class ArrayField(Field):
    """Array/List field (PostgreSQL specific)."""

    def __init__(self, base_field: Field, size: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.base_field = base_field
        self.size = size

    def to_python(self, value: Any) -> Optional[List]:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return json.loads(value)
        return list(value)

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        return value  # PostgreSQL handles arrays natively

    def get_db_type(self, dialect: str = "postgresql") -> str:
        if dialect == "postgresql":
            base_type = self.base_field.get_db_type(dialect)
            size_spec = f"[{self.size}]" if self.size else "[]"
            return f"{base_type}{size_spec}"
        # For non-PostgreSQL, store as JSON
        return "TEXT"


class EnumField(Field):
    """Enum field."""

    def __init__(self, enum_class: Type[Enum], **kwargs):
        super().__init__(**kwargs)
        self.enum_class = enum_class
        if "choices" not in kwargs:
            self.choices = [(e.value, e.name) for e in enum_class]

    def to_python(self, value: Any) -> Optional[Enum]:
        if value is None:
            return None
        if isinstance(value, self.enum_class):
            return value
        return self.enum_class(value)

    def to_db(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, Enum):
            return value.value
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        return "VARCHAR(50)"


class DurationField(Field):
    """
    Duration/Interval field for storing time durations.

    Stores Python timedelta objects with database-specific representations:
    - PostgreSQL: INTERVAL (native support)
    - MySQL: BIGINT (microseconds)
    - SQLite: TEXT (ISO 8601 duration format)
    - MongoDB: NumberLong (milliseconds)

    Example:
        class Video(Model):
            duration = DurationField()  # Store video length
            timeout = DurationField(default=timedelta(hours=2))

        video.duration = timedelta(hours=2, minutes=30)
        await video.save()
    """

    def __init__(
        self,
        min_value: Optional[timedelta] = None,
        max_value: Optional[timedelta] = None,
        **kwargs
    ):
        """
        Initialize DurationField.

        Args:
            min_value: Minimum allowed duration
            max_value: Maximum allowed duration
            **kwargs: Base field parameters
        """
        super().__init__(**kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> Any:
        """Validate duration value."""
        # Check type first (before calling super) for clearer error messages
        if value is not None and not isinstance(value, timedelta):
            raise ValueError(f"{self.name}: Value must be a timedelta object")

        value = super().validate(value)
        if value is None:
            return None

        # Check min/max constraints
        if self.min_value is not None and value < self.min_value:
            raise ValueError(
                f"{self.name}: Duration {value} is less than minimum {self.min_value}"
            )

        if self.max_value is not None and value > self.max_value:
            raise ValueError(
                f"{self.name}: Duration {value} exceeds maximum {self.max_value}"
            )

        return value

    def to_python(self, value: Any) -> Optional[timedelta]:
        """Convert database value to Python timedelta."""
        if value is None:
            return None

        # Already a timedelta (PostgreSQL INTERVAL returns this directly)
        if isinstance(value, timedelta):
            return value

        # MySQL stores as microseconds (BIGINT)
        if isinstance(value, int):
            return timedelta(microseconds=value)

        # SQLite/MongoDB stores as ISO 8601 duration string
        if isinstance(value, str):
            # Parse ISO 8601 duration format: P[n]Y[n]M[n]DT[n]H[n]M[n]S
            # For simplicity, we'll use a basic format: PT[n]H[n]M[n]S
            # Full ISO 8601 parser would require external library

            # Simple duration format: "PT2H30M15S" = 2:30:15
            pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?'
            match = re.match(pattern, value)

            if match:
                hours = int(match.group(1) or 0)
                minutes = int(match.group(2) or 0)
                seconds = float(match.group(3) or 0)

                return timedelta(hours=hours, minutes=minutes, seconds=seconds)

            # Alternative format: total seconds as string
            try:
                total_seconds = float(value)
                return timedelta(seconds=total_seconds)
            except ValueError:
                pass

        raise ValueError(f"{self.name}: Cannot convert {value} to timedelta")

    def to_db(self, value: Any) -> Any:
        """Convert Python timedelta to database value."""
        if value is None:
            return None

        if not isinstance(value, timedelta):
            raise ValueError(f"{self.name}: Expected timedelta, got {type(value)}")

        # PostgreSQL uses INTERVAL natively - can pass timedelta directly
        # For other databases, we need conversion

        # This will be handled per-adapter in get_db_value() if needed
        return value

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type for this field."""
        if dialect == "postgresql":
            return "INTERVAL"
        elif dialect == "mysql":
            # Store as microseconds (max: ~292,000 years)
            return "BIGINT"
        elif dialect == "sqlite":
            # Store as ISO 8601 duration string
            return "TEXT"
        elif dialect == "mongodb":
            # Store as ISO 8601 string (like SQLite) to avoid integer ambiguity
            return "String"
        else:
            return "TEXT"

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """
        Get database-specific representation of value.

        This method is called by adapters to convert the Python value
        to the appropriate database format.
        """
        if value is None:
            return None

        if not isinstance(value, timedelta):
            raise ValueError(f"{self.name}: Expected timedelta, got {type(value)}")

        if dialect == "postgresql":
            # PostgreSQL can handle timedelta directly
            return value

        elif dialect == "mysql":
            # Store as total microseconds
            total_seconds = value.total_seconds()
            microseconds = int(total_seconds * 1_000_000)

            # Check for BIGINT overflow (signed 64-bit: -2^63 to 2^63-1)
            MAX_BIGINT = 9223372036854775807
            if abs(microseconds) > MAX_BIGINT:
                raise ValueError(
                    f"{self.name}: Duration too large for MySQL BIGINT storage. "
                    f"Maximum duration: ~292,471 years"
                )

            return microseconds

        elif dialect == "sqlite":
            # Store as ISO 8601 duration format
            total_seconds = int(value.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            # Format: PT2H30M15S
            parts = []
            if hours:
                parts.append(f"{hours}H")
            if minutes:
                parts.append(f"{minutes}M")
            if seconds or not parts:
                parts.append(f"{seconds}S")

            return f"PT{''.join(parts)}"

        elif dialect == "mongodb":
            # Store as ISO 8601 string (same as SQLite) to avoid integer ambiguity
            return self.get_db_value(value, "sqlite")

        else:
            # Fallback: ISO 8601 format
            return self.get_db_value(value, "sqlite")


class IPAddressField(Field):
    """
    IP Address field for storing IPv4 and IPv6 addresses.

    Uses Python's ipaddress module for validation and supports protocol filtering.

    Database mappings:
    - PostgreSQL: INET (native IP type with network operations)
    - MySQL: VARCHAR(45) (max length for IPv6)
    - SQLite: VARCHAR(45)
    - MongoDB: String

    Example:
        class AccessLog(Model):
            user_ip = IPAddressField()  # Any IP
            server_ip = IPAddressField(protocol='IPv4')  # IPv4 only

        log.user_ip = ipaddress.ip_address('192.168.1.1')
        log.server_ip = '10.0.0.1'  # Auto-converts to IPv4Address
        await log.save()
    """

    def __init__(
        self,
        protocol: str = 'both',  # 'IPv4', 'IPv6', or 'both'
        **kwargs
    ):
        """
        Initialize IPAddressField.

        Args:
            protocol: IP protocol - 'IPv4', 'IPv6', or 'both' (default)
            **kwargs: Base field parameters
        """
        super().__init__(**kwargs)

        if protocol not in ('IPv4', 'IPv6', 'both'):
            raise ValueError(f"protocol must be 'IPv4', 'IPv6', or 'both', got {protocol}")

        self.protocol = protocol

    def validate(self, value: Any) -> Any:
        """Validate IP address value."""
        value = super().validate(value)
        if value is None:
            return None

        # Convert string to IP address object
        if isinstance(value, str):
            try:
                value = ipaddress.ip_address(value)
            except ValueError as e:
                raise ValueError(f"{self.name}: Invalid IP address - {e}")

        # Verify it's an IP address object
        if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            raise ValueError(
                f"{self.name}: Value must be an IP address (string or ipaddress object)"
            )

        # Check protocol restriction
        if self.protocol == 'IPv4' and isinstance(value, ipaddress.IPv6Address):
            raise ValueError(f"{self.name}: Only IPv4 addresses allowed, got IPv6")

        if self.protocol == 'IPv6' and isinstance(value, ipaddress.IPv4Address):
            raise ValueError(f"{self.name}: Only IPv6 addresses allowed, got IPv4")

        return value

    def to_python(self, value: Any) -> Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]:
        """Convert database value to Python IP address object."""
        if value is None:
            return None

        if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return value

        if isinstance(value, str):
            try:
                return ipaddress.ip_address(value)
            except ValueError as e:
                raise ValueError(f"{self.name}: Invalid IP address string - {e}")

        # PostgreSQL INET type might return as bytes
        if isinstance(value, bytes):
            try:
                return ipaddress.ip_address(value.decode('utf-8'))
            except (ValueError, UnicodeDecodeError) as e:
                raise ValueError(f"{self.name}: Invalid IP address bytes - {e}")

        raise ValueError(f"{self.name}: Cannot convert {type(value)} to IP address")

    def to_db(self, value: Any) -> Optional[str]:
        """Convert Python IP address to database value."""
        if value is None:
            return None

        if isinstance(value, str):
            # Validate before storing
            try:
                ipaddress.ip_address(value)
                return value
            except ValueError as e:
                raise ValueError(f"{self.name}: Invalid IP address - {e}")

        if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return str(value)

        raise ValueError(f"{self.name}: Expected IP address, got {type(value)}")

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type for this field."""
        if dialect == "postgresql":
            # PostgreSQL has native INET type with network operations
            return "INET"
        elif dialect in ("mysql", "sqlite", "mongodb"):
            # Max length for IPv6: 45 characters
            # (e.g., "2001:0db8:85a3:0000:0000:8a2e:0370:7334")
            return "VARCHAR(45)"
        else:
            return "VARCHAR(45)"


class SlugField(CharField):
    """
    Slug field for URL-safe strings.

    A slug is a URL-safe, human-readable identifier typically used in URLs:
    - Lowercase letters
    - Numbers
    - Hyphens (no underscores, spaces, or special characters)

    Database mappings: Same as CharField (VARCHAR)

    Example:
        class BlogPost(Model):
            title = CharField(max_length=200)
            slug = SlugField(unique=True, max_length=200)

        post.title = "My Awesome Blog Post!"
        post.slug = "my-awesome-blog-post"
        await post.save()
    """

    def __init__(self, max_length: int = 50, **kwargs):
        """
        Initialize SlugField.

        Args:
            max_length: Maximum length for slug (default: 50)
            **kwargs: Base field parameters
        """
        # Set default to allow empty slugs during object creation
        if 'default' not in kwargs and 'default_factory' not in kwargs:
            kwargs.setdefault('nullable', True)

        super().__init__(max_length=max_length, **kwargs)

    def validate(self, value: Any) -> Any:
        """Validate slug value."""
        value = super().validate(value)
        if value is None or value == '':
            return value

        if not isinstance(value, str):
            raise ValueError(f"{self.name}: Slug must be a string")

        # Character-by-character validation (prevents ReDoS attacks)
        # Valid characters: lowercase letters, numbers, hyphens
        valid_chars = set('abcdefghijklmnopqrstuvwxyz0123456789-')
        if not all(c in valid_chars for c in value):
            raise ValueError(
                f"{self.name}: Invalid slug format. "
                "Slugs must contain only lowercase letters, numbers, and hyphens. "
                "Example: 'my-blog-post'"
            )

        # Check for invalid patterns (leading/trailing hyphens, consecutive hyphens)
        if value.startswith('-') or value.endswith('-'):
            raise ValueError(
                f"{self.name}: Slug cannot start or end with hyphen"
            )

        if '--' in value:
            raise ValueError(
                f"{self.name}: Slug cannot contain consecutive hyphens"
            )

        return value

    @staticmethod
    def slugify(text: str, max_length: Optional[int] = None) -> str:
        """
        Convert text to a valid slug.

        Args:
            text: Input text to convert
            max_length: Maximum length for resulting slug

        Returns:
            URL-safe slug string

        Example:
            >>> SlugField.slugify("My Awesome Blog Post!")
            'my-awesome-blog-post'
            >>> SlugField.slugify("  Hello   World!  ")
            'hello-world'
        """
        # Convert to lowercase
        slug = text.lower()

        # Remove special characters, keep alphanumeric and spaces
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)

        # Replace spaces and multiple hyphens with single hyphen
        slug = re.sub(r'[\s-]+', '-', slug)

        # Remove leading/trailing hyphens
        slug = slug.strip('-')

        # Truncate to max_length if specified
        if max_length:
            slug = slug[:max_length]
            # Remove trailing hyphen if truncation created one
            slug = slug.rstrip('-')

        return slug


class FieldFile:
    """
    Wrapper for files stored by FileField.

    Provides access to file operations through the storage backend.
    """

    def __init__(self, instance, field, name: Optional[str] = None):
        """
        Initialize FieldFile.

        Args:
            instance: Model instance this file belongs to
            field: FileField instance
            name: Stored file name/path
        """
        self.instance = instance
        self.field = field
        self.storage = field.storage
        self._name = name
        self._committed = True

    @property
    def name(self) -> Optional[str]:
        """Get the file name/path."""
        return self._name

    @property
    def url(self) -> str:
        """Get URL for accessing the file."""
        if not self._name:
            raise ValueError("File has no name")
        # Use asyncio to run async storage.url() method
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.storage.url(self._name))

    @property
    def size(self) -> int:
        """Get file size in bytes."""
        if not self._name:
            return 0
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(self.storage.size(self._name))

    async def save(self, content: BinaryIO, name: Optional[str] = None):
        """
        Save file content.

        Args:
            content: File content (binary file object)
            name: Desired file name (optional)
        """
        if name is None:
            name = self._name
        if name is None:
            raise ValueError("File name is required")

        # Save to storage
        self._name = await self.storage.save(name, content)
        self._committed = True

        # Update model instance field value
        setattr(self.instance, self.field.name, self._name)

    async def delete(self):
        """Delete the file from storage."""
        if self._name:
            await self.storage.delete(self._name)
            self._name = None
            self._committed = True

    def __bool__(self):
        """Check if file exists."""
        return bool(self._name)

    def __str__(self):
        """String representation (file name)."""
        return self._name or ''


class FileField(Field):
    """
    File upload field.

    Stores uploaded files using a storage backend and saves the file path
    in the database.

    Database mapping:
    - All databases: VARCHAR(255) (stores file path, not content)

    Example:
        document = FileField(
            upload_to='documents/',
            max_size=5*1024*1024,  # 5MB
            allowed_types=['application/pdf', 'application/msword']
        )

        # Usage in model
        class Document(Model):
            file = FileField(upload_to='docs/')

        # Upload file
        doc = Document()
        doc.file = uploaded_file  # From request
        await doc.save()

        # Access file
        url = doc.file.url
        size = doc.file.size
    """

    def __init__(
        self,
        upload_to: str = '',
        max_size: Optional[int] = None,
        allowed_types: Optional[List[str]] = None,
        storage=None,
        **kwargs
    ):
        """
        Initialize FileField.

        Args:
            upload_to: Subdirectory to upload files to
            max_size: Maximum file size in bytes (None = no limit)
            allowed_types: List of allowed MIME types (None = allow all)
            storage: Storage backend (uses default if None)
            **kwargs: Base field parameters
        """
        # FileField stores the path (max 255 chars)
        self.max_length = kwargs.pop('max_length', 255)
        super().__init__(**kwargs)

        self.upload_to = upload_to.rstrip('/')
        self.max_size = max_size
        self.allowed_types = allowed_types or []

        # Get storage backend
        if storage is None:
            from .storage import get_default_storage
            storage = get_default_storage()
        self.storage = storage

    def validate(self, value: Any) -> Any:
        """Validate file value."""
        # If it's a FieldFile, extract the name
        if isinstance(value, FieldFile):
            value = value.name

        # Allow None/empty for nullable fields
        if value is None or value == '':
            if not self.nullable:
                raise ValueError(f"{self.name}: File is required")
            return value

        # If it's a string (file path), it's already stored
        if isinstance(value, str):
            return value

        # If it's a file-like object, we need to validate and save it
        if hasattr(value, 'read'):
            # This will be handled in to_python()
            return value

        raise ValueError(
            f"{self.name}: Expected file object or file path, got {type(value)}"
        )

    def validate_file(self, file_obj: BinaryIO, filename: str):
        """
        Validate uploaded file.

        Args:
            file_obj: File object to validate
            filename: Original filename

        Raises:
            ValueError: If validation fails
        """
        # Check file size
        if self.max_size is not None:
            # Get current position
            current_pos = file_obj.tell()

            # Seek to end to get size
            file_obj.seek(0, os.SEEK_END)
            size = file_obj.tell()

            # Seek back to original position
            file_obj.seek(current_pos)

            if size > self.max_size:
                max_mb = self.max_size / (1024 * 1024)
                actual_mb = size / (1024 * 1024)
                raise ValueError(
                    f"{self.name}: File size ({actual_mb:.2f}MB) exceeds "
                    f"maximum allowed size ({max_mb:.2f}MB)"
                )

        # Check MIME type
        if self.allowed_types:
            # Guess MIME type from filename
            mime_type, _ = mimetypes.guess_type(filename)

            if mime_type not in self.allowed_types:
                allowed = ', '.join(self.allowed_types)
                raise ValueError(
                    f"{self.name}: File type '{mime_type}' not allowed. "
                    f"Allowed types: {allowed}"
                )

    def to_python(self, value: Any) -> Optional[FieldFile]:
        """Convert database value to FieldFile."""
        if value is None or value == '':
            return None

        # If it's already a FieldFile, return it
        if isinstance(value, FieldFile):
            return value

        # If it's a string (file path from database), wrap in FieldFile
        if isinstance(value, str):
            # Note: We don't have the instance here, so this will be
            # set by the descriptor __get__ method
            return FieldFile(None, self, value)

        # If it's a file-like object, create FieldFile
        # This handles uploaded files
        if hasattr(value, 'read'):
            return FieldFile(None, self, None)

        return None

    def to_db(self, value: Any) -> Optional[str]:
        """Convert Python value to database value."""
        if value is None or value == '':
            return None

        # If it's a FieldFile, get the name
        if isinstance(value, FieldFile):
            return value.name

        # If it's a string (file path), return it
        if isinstance(value, str):
            return value

        # For file-like objects, we need to save them first
        # This is typically handled by the model's save() method
        if hasattr(value, 'read'):
            raise ValueError(
                f"{self.name}: File must be saved before storing in database. "
                "Use model.save() or field.save() to save the file."
            )

        return None

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type."""
        # All databases store the file path as a string
        return "VARCHAR(255)"

    def __get__(self, instance, owner):
        """Descriptor get method."""
        if instance is None:
            return self

        # Get the file path from instance
        file_path = instance.__dict__.get(self.name)

        # If it's already a FieldFile with correct instance, return it
        if isinstance(file_path, FieldFile) and file_path.instance is instance:
            return file_path

        # Create FieldFile with instance
        if isinstance(file_path, FieldFile):
            # Update instance reference
            file_path.instance = instance
            return file_path

        # Create new FieldFile
        field_file = FieldFile(instance, self, file_path if isinstance(file_path, str) else None)
        instance.__dict__[self.name] = field_file
        return field_file

    def __set__(self, instance, value):
        """Descriptor set method."""
        instance.__dict__[self.name] = value


class ImageFieldFile(FieldFile):
    """
    Extension of FieldFile for images.

    Provides image-specific properties and methods.
    """

    def _get_image(self):
        """Get PIL Image object (cached)."""
        if not hasattr(self, '_cached_image'):
            if not self._name:
                return None

            # Import PIL here to avoid dependency if not using ImageField
            try:
                from PIL import Image
            except ImportError:
                raise ImportError("Pillow is required for ImageField. Install with: pip install Pillow")

            # Get file path from storage
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # For LocalFileStorage, we can read directly
            if hasattr(self.storage, 'base_path'):
                file_path = self.storage.base_path / self._name
                self._cached_image = Image.open(file_path)
            else:
                # For other storage backends, would need to download
                # For now, raise error
                raise NotImplementedError(
                    "Image properties only supported for LocalFileStorage"
                )

        return self._cached_image

    @property
    def width(self) -> Optional[int]:
        """Get image width in pixels."""
        img = self._get_image()
        return img.width if img else None

    @property
    def height(self) -> Optional[int]:
        """Get image height in pixels."""
        img = self._get_image()
        return img.height if img else None

    @property
    def format(self) -> Optional[str]:
        """Get image format (JPEG, PNG, etc.)."""
        img = self._get_image()
        return img.format if img else None


class ImageField(FileField):
    """
    Image upload field.

    Extends FileField with image-specific validation and features:
    - Image format validation
    - Dimension validation (min/max width/height)
    - Metadata extraction (width, height, format)
    - Optional thumbnail generation

    Example:
        avatar = ImageField(
            upload_to='avatars/',
            max_size=5*1024*1024,  # 5MB
            allowed_formats=['JPEG', 'PNG', 'WEBP'],
            min_width=200,
            min_height=200,
            max_width=2000,
            max_height=2000
        )

        # Usage
        user.avatar = uploaded_image
        await user.save()

        # Access properties
        width = user.avatar.width
        height = user.avatar.height
        format = user.avatar.format
    """

    def __init__(
        self,
        upload_to: str = '',
        max_size: Optional[int] = None,
        allowed_formats: Optional[List[str]] = None,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None,
        min_height: Optional[int] = None,
        max_height: Optional[int] = None,
        storage=None,
        **kwargs
    ):
        """
        Initialize ImageField.

        Args:
            upload_to: Subdirectory to upload files to
            max_size: Maximum file size in bytes
            allowed_formats: List of allowed image formats (e.g., ['JPEG', 'PNG', 'WEBP'])
            min_width: Minimum image width in pixels
            max_width: Maximum image width in pixels
            min_height: Minimum image height in pixels
            max_height: Maximum image height in pixels
            storage: Storage backend
            **kwargs: Base field parameters
        """
        # Convert formats to MIME types for FileField
        if allowed_formats:
            format_to_mime = {
                'JPEG': 'image/jpeg',
                'JPG': 'image/jpeg',
                'PNG': 'image/png',
                'GIF': 'image/gif',
                'WEBP': 'image/webp',
                'BMP': 'image/bmp',
                'TIFF': 'image/tiff'
            }
            allowed_types = [format_to_mime.get(fmt.upper()) for fmt in allowed_formats]
            allowed_types = [t for t in allowed_types if t]  # Remove None
        else:
            # Default to common image formats
            allowed_types = [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/webp'
            ]

        super().__init__(
            upload_to=upload_to,
            max_size=max_size,
            allowed_types=allowed_types,
            storage=storage,
            **kwargs
        )

        self.allowed_formats = allowed_formats or ['JPEG', 'PNG', 'GIF', 'WEBP']
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def validate_file(self, file_obj: BinaryIO, filename: str):
        """
        Validate uploaded image file with decompression bomb protection.

        Args:
            file_obj: File object to validate
            filename: Original filename

        Raises:
            ValueError: If validation fails
        """
        # Call parent validation (size, MIME type)
        super().validate_file(file_obj, filename)

        # Image-specific validation
        try:
            from PIL import Image, ImageFile
        except ImportError:
            raise ImportError("Pillow is required for ImageField. Install with: pip install Pillow")

        # Security: Enable decompression bomb protection
        # Default PIL limit is 89,478,485 pixels (approximately 89 megapixels)
        # This protects against zip bombs and similar attacks
        if not hasattr(Image, 'MAX_IMAGE_PIXELS'):
            Image.MAX_IMAGE_PIXELS = 89_478_485

        # Security: Reject truncated images
        ImageFile.LOAD_TRUNCATED_IMAGES = False

        # Save current position
        current_pos = file_obj.tell()

        try:
            # Open image
            img = Image.open(file_obj)

            # Verify it's an image
            img.verify()

            # Re-open for dimension checks (verify() closes the file)
            file_obj.seek(current_pos)
            img = Image.open(file_obj)

            # Check format
            if self.allowed_formats and img.format not in self.allowed_formats:
                allowed = ', '.join(self.allowed_formats)
                raise ValueError(
                    f"{self.name}: Image format '{img.format}' not allowed. "
                    f"Allowed formats: {allowed}"
                )

            # Check dimensions
            width, height = img.size
            pixel_count = width * height

            # Security: Check pixel count BEFORE loading full image
            max_pixels = Image.MAX_IMAGE_PIXELS
            if pixel_count > max_pixels:
                raise ValueError(
                    f"{self.name}: Image too large ({width}x{height} = {pixel_count:,} pixels). "
                    f"Maximum allowed: {max_pixels:,} pixels. This may be a decompression bomb."
                )

            if self.min_width and width < self.min_width:
                raise ValueError(
                    f"{self.name}: Image width ({width}px) is less than "
                    f"minimum required width ({self.min_width}px)"
                )

            if self.max_width and width > self.max_width:
                raise ValueError(
                    f"{self.name}: Image width ({width}px) exceeds "
                    f"maximum allowed width ({self.max_width}px)"
                )

            if self.min_height and height < self.min_height:
                raise ValueError(
                    f"{self.name}: Image height ({height}px) is less than "
                    f"minimum required height ({self.min_height}px)"
                )

            if self.max_height and height > self.max_height:
                raise ValueError(
                    f"{self.name}: Image height ({height}px) exceeds "
                    f"maximum allowed height ({self.max_height}px)"
                )

        except Image.DecompressionBombError as e:
            # Security: Catch PIL's built-in decompression bomb detection
            raise ValueError(
                f"{self.name}: Image appears to be a decompression bomb (too many pixels). "
                f"Rejecting for security reasons."
            ) from e

        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"{self.name}: Invalid image file - {e}")

        finally:
            # Restore file position
            file_obj.seek(current_pos)

    def to_python(self, value: Any) -> Optional[ImageFieldFile]:
        """Convert database value to ImageFieldFile."""
        if value is None or value == '':
            return None

        # If it's already an ImageFieldFile, return it
        if isinstance(value, ImageFieldFile):
            return value

        # If it's a string (file path from database), wrap in ImageFieldFile
        if isinstance(value, str):
            return ImageFieldFile(None, self, value)

        # If it's a file-like object, create ImageFieldFile
        if hasattr(value, 'read'):
            return ImageFieldFile(None, self, None)

        return None

    def __get__(self, instance, owner):
        """Descriptor get method."""
        if instance is None:
            return self

        # Get the file path from instance
        file_path = instance.__dict__.get(self.name)

        # If it's already an ImageFieldFile with correct instance, return it
        if isinstance(file_path, ImageFieldFile) and file_path.instance is instance:
            return file_path

        # Create ImageFieldFile with instance
        if isinstance(file_path, ImageFieldFile):
            # Update instance reference
            file_path.instance = instance
            return file_path

        # Create new ImageFieldFile
        field_file = ImageFieldFile(instance, self, file_path if isinstance(file_path, str) else None)
        instance.__dict__[self.name] = field_file
        return field_file


class AutoField(IntegerField):
    """
    Auto-incrementing integer primary key field.

    A convenience field that's clearer than IntegerField(primary_key=True, auto_increment=True).
    Always primary_key=True and auto_increment=True.

    Database mapping:
    - PostgreSQL: SERIAL PRIMARY KEY
    - MySQL: INT AUTO_INCREMENT PRIMARY KEY
    - SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
    - MongoDB: ObjectId (auto-generated)

    Example:
        class User(Model):
            id = AutoField()  # Clearer than IntegerField(primary_key=True, auto_increment=True)
            name = CharField(max_length=100)
    """

    def __init__(self, **kwargs):
        """
        Initialize AutoField.

        Note: primary_key and auto_increment are forced to True.
        """
        # Force primary_key and auto_increment
        kwargs['primary_key'] = True
        kwargs['auto_increment'] = True
        super().__init__(**kwargs)


class BigAutoField(BigIntegerField):
    """
    Auto-incrementing 64-bit integer primary key field.

    Like AutoField but uses BIGINT for larger ID ranges.
    Always primary_key=True and auto_increment=True.

    Database mapping:
    - PostgreSQL: BIGSERIAL PRIMARY KEY
    - MySQL: BIGINT AUTO_INCREMENT PRIMARY KEY
    - SQLite: INTEGER PRIMARY KEY AUTOINCREMENT
    - MongoDB: ObjectId

    Example:
        class LargeTable(Model):
            id = BigAutoField()  # For tables with billions of rows
    """

    def __init__(self, **kwargs):
        """
        Initialize BigAutoField.

        Note: primary_key and auto_increment are forced to True.
        """
        # Force primary_key and auto_increment
        kwargs['primary_key'] = True
        kwargs['auto_increment'] = True
        super().__init__(**kwargs)


class PositiveIntegerField(IntegerField):
    """
    Integer field that only accepts non-negative values (>= 0).

    Database mapping (with CHECK constraint):
    - PostgreSQL: INTEGER CHECK (field >= 0)
    - MySQL: INT UNSIGNED
    - SQLite: INTEGER CHECK (field >= 0)
    - MongoDB: NumberInt with validation

    Example:
        class Product(Model):
            quantity = PositiveIntegerField()  # Stock quantity (can't be negative)
            rating = PositiveIntegerField(max_value=5)  # 0-5 rating
    """

    def __init__(self, **kwargs):
        """
        Initialize PositiveIntegerField.

        Note: min_value is forced to 0.
        """
        # Force min_value to 0
        kwargs['min_value'] = 0
        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type with unsigned/check constraint."""
        if dialect == "postgresql":
            return "INTEGER"  # CHECK constraint added separately
        elif dialect == "mysql":
            return "INT UNSIGNED AUTO_INCREMENT" if self.auto_increment else "INT UNSIGNED"
        elif dialect == "sqlite":
            return "INTEGER"  # CHECK constraint added separately
        elif dialect == "mongodb":
            return "NumberInt"
        else:
            return "INTEGER"


class PositiveSmallIntegerField(SmallIntegerField):
    """
    Small integer field (16-bit) that only accepts non-negative values (>= 0).

    Range: 0 to 32,767

    Database mapping (with CHECK constraint):
    - PostgreSQL: SMALLINT CHECK (field >= 0)
    - MySQL: SMALLINT UNSIGNED
    - SQLite: INTEGER CHECK (field >= 0)
    - MongoDB: NumberInt with validation

    Example:
        class Order(Model):
            item_count = PositiveSmallIntegerField()  # Number of items (0-32767)
    """

    def __init__(self, **kwargs):
        """
        Initialize PositiveSmallIntegerField.

        Note: min_value is forced to 0.
        """
        # Force min_value to 0
        kwargs['min_value'] = 0
        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type with unsigned/check constraint."""
        if dialect == "postgresql":
            return "SMALLINT"  # CHECK constraint added separately
        elif dialect == "mysql":
            return "SMALLINT UNSIGNED"
        elif dialect == "sqlite":
            return "INTEGER"  # CHECK constraint added separately
        elif dialect == "mongodb":
            return "NumberInt"
        else:
            return "SMALLINT"


class Money:
    """
    Represents a monetary value with currency.

    Attributes:
        amount: Decimal amount
        currency: Currency code (ISO 4217, e.g., 'USD', 'EUR')
    """

    def __init__(self, amount: Union[Decimal, float, int, str], currency: str = 'USD'):
        """
        Initialize Money object.

        Args:
            amount: Monetary amount (converted to Decimal for precision)
            currency: Currency code (ISO 4217)
        """
        if isinstance(amount, Decimal):
            self.amount = amount
        else:
            self.amount = Decimal(str(amount))

        self.currency = currency.upper()

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __repr__(self):
        return f"Money({self.amount}, '{self.currency}')"

    def __eq__(self, other):
        if not isinstance(other, Money):
            return False
        return self.amount == other.amount and self.currency == other.currency

    def __add__(self, other):
        """Add two Money objects (must have same currency)."""
        if not isinstance(other, Money):
            raise TypeError("Can only add Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot add {self.currency} to {other.currency}")
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        """Subtract two Money objects (must have same currency)."""
        if not isinstance(other, Money):
            raise TypeError("Can only subtract Money from Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot subtract {other.currency} from {self.currency}")
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, other):
        """Multiply Money by a number."""
        if isinstance(other, Money):
            raise TypeError("Cannot multiply Money by Money")
        return Money(self.amount * Decimal(str(other)), self.currency)

    def __truediv__(self, other):
        """Divide Money by a number."""
        if isinstance(other, Money):
            raise TypeError("Cannot divide Money by Money")
        return Money(self.amount / Decimal(str(other)), self.currency)

    def __lt__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount < other.amount

    def __le__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount <= other.amount

    def __gt__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount > other.amount

    def __ge__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Can only compare Money to Money")
        if self.currency != other.currency:
            raise ValueError(f"Cannot compare {self.currency} to {other.currency}")
        return self.amount >= other.amount


class MoneyField(Field):
    """
    Monetary value field with currency support.

    Stores amount and currency separately. Provides currency-aware
    arithmetic operations and validation.

    Database mapping:
    - PostgreSQL: NUMERIC(19,4) for amount + VARCHAR(3) for currency (2 columns)
    - MySQL: DECIMAL(19,4) for amount + VARCHAR(3) for currency (2 columns)
    - SQLite: TEXT (JSON: {"amount": "29.99", "currency": "USD"})
    - MongoDB: Object with amount and currency fields

    Example:
        class Product(Model):
            price = MoneyField(max_digits=10, decimal_places=2, currency='USD')

        # Usage
        product = Product()
        product.price = Money(29.99, 'USD')
        await product.save()

        # Arithmetic
        total = product.price * 2  # Money(59.98, 'USD')
        discounted = product.price * Decimal('0.9')  # Money(26.99, 'USD')
    """

    def __init__(
        self,
        max_digits: int = 19,
        decimal_places: int = 4,
        currency: str = 'USD',
        **kwargs
    ):
        """
        Initialize MoneyField.

        Args:
            max_digits: Maximum total digits (default: 19)
            decimal_places: Decimal places (default: 4 for sub-cent precision)
            currency: Default currency code (ISO 4217)
            **kwargs: Base field parameters
        """
        super().__init__(**kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.default_currency = currency.upper()

    def validate(self, value: Any) -> Any:
        """Validate Money value."""
        value = super().validate(value)
        if value is None:
            return None

        if not isinstance(value, Money):
            raise ValueError(f"{self.name}: Value must be a Money object")

        # Validate currency code (basic check: 3 uppercase letters)
        if not (len(value.currency) == 3 and value.currency.isupper() and value.currency.isalpha()):
            raise ValueError(
                f"{self.name}: Invalid currency code '{value.currency}'. "
                "Must be 3 uppercase letters (ISO 4217)"
            )

        # Validate amount precision
        # Check total digits
        amount_str = str(abs(value.amount))
        # Remove decimal point for counting
        digits_only = amount_str.replace('.', '').replace('-', '')
        if len(digits_only) > self.max_digits:
            raise ValueError(
                f"{self.name}: Amount has too many digits. "
                f"Maximum: {self.max_digits}, got: {len(digits_only)}"
            )

        return value

    def to_python(self, value: Any) -> Optional[Money]:
        """Convert database value to Money object."""
        if value is None:
            return None

        if isinstance(value, Money):
            return value

        # From Decimal/float (MySQL/PostgreSQL DECIMAL column)
        if isinstance(value, (Decimal, float, int)):
            return Money(Decimal(str(value)), self.default_currency)

        # From JSON (SQLite/MongoDB)
        if isinstance(value, str):
            try:
                data = json.loads(value)
                return Money(Decimal(data['amount']), data['currency'])
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                raise ValueError(f"{self.name}: Invalid money JSON - {e}")

        # From dict (MongoDB)
        if isinstance(value, dict):
            try:
                return Money(Decimal(str(value['amount'])), value['currency'])
            except (KeyError, ValueError) as e:
                raise ValueError(f"{self.name}: Invalid money dict - {e}")

        raise ValueError(f"{self.name}: Cannot convert {type(value)} to Money")

    def to_db(self, value: Any) -> Any:
        """Convert Money to database value."""
        if value is None:
            return None

        if not isinstance(value, Money):
            raise ValueError(f"{self.name}: Expected Money object, got {type(value)}")

        # Extract just the amount (Decimal) for database storage
        # Currency is stored separately or inferred from field configuration
        return value.amount

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database column type."""
        if dialect in ("postgresql", "mysql"):
            # Note: In reality, this would create TWO columns:
            # - amount: NUMERIC/DECIMAL
            # - currency: VARCHAR(3)
            # For simplicity, we return the amount column type
            # (Multi-column field support would need ORM enhancements)
            return f"NUMERIC({self.max_digits},{self.decimal_places})"
        elif dialect == "sqlite":
            # Store as JSON text
            return "TEXT"
        elif dialect == "mongodb":
            # Store as embedded document
            return "Object"
        else:
            return "TEXT"

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Get database-specific representation."""
        if value is None:
            return None

        if not isinstance(value, Money):
            raise ValueError(f"{self.name}: Expected Money object")

        if dialect in ("postgresql", "mysql"):
            # For SQL databases, ideally we'd return a tuple (amount, currency)
            # But for now, return JSON string
            # TODO: Multi-column field support
            return json.dumps({
                'amount': str(value.amount),
                'currency': value.currency
            })
        elif dialect == "sqlite":
            # JSON string
            return json.dumps({
                'amount': str(value.amount),
                'currency': value.currency
            })
        elif dialect == "mongodb":
            # MongoDB document
            return {
                'amount': str(value.amount),  # Store as string to preserve precision
                'currency': value.currency
            }
        else:
            return json.dumps({
                'amount': str(value.amount),
                'currency': value.currency
            })


# =============================================================================
# Phase 3: PostgreSQL-Specific Fields
# =============================================================================


class HStoreField(Field):
    """
    PostgreSQL HSTORE field for storing key-value pairs.

    PostgreSQL: HSTORE (native key-value store)
    Other DBs: JSONB/JSON (fallback with similar functionality)

    Features:
    - Store dictionary/hash map in database
    - Query by specific keys in PostgreSQL
    - Validates all keys and values are strings
    - Atomic updates of individual keys
    - Size limits for security (max keys, key/value lengths)

    Example:
        class Product(Model):
            attributes = HStoreField()

        product.attributes = {'color': 'red', 'size': 'large'}
        await product.save()
    """

    # Security limits to prevent DoS attacks
    MAX_DICT_SIZE = 1000  # Maximum number of key-value pairs
    MAX_KEY_LENGTH = 255  # Maximum key length (bytes)
    MAX_VALUE_LENGTH = 65535  # Maximum value length (PostgreSQL text limit)
    MAX_JSON_SIZE = 1_000_000  # Maximum JSON string size (1MB)

    def __init__(self, max_size: int = None, **kwargs):
        """
        Initialize HStore field.

        Args:
            max_size: Maximum number of key-value pairs (default: 1000)
        """
        self.max_size = max_size if max_size is not None else self.MAX_DICT_SIZE
        if self.max_size > self.MAX_DICT_SIZE:
            raise ValueError(
                f"max_size cannot exceed {self.MAX_DICT_SIZE} (got {self.max_size})"
            )
        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database-specific type for HStore field."""
        if dialect == "postgresql":
            return "HSTORE"
        elif dialect == "mysql":
            return "JSON"
        elif dialect == "sqlite":
            return "TEXT"
        elif dialect == "mongodb":
            return "Object"
        else:
            return "TEXT"

    def validate(self, value: Any) -> Any:
        """Validate HStore value (must be dict with string keys/values)."""
        # Check type first
        if value is not None and not isinstance(value, dict):
            raise ValueError(f"{self.name}: Value must be a dictionary")

        value = super().validate(value)

        if value is None:
            return value

        # Security: Enforce maximum dictionary size
        if len(value) > self.max_size:
            raise ValueError(
                f"{self.name}: Dictionary too large ({len(value)} keys). "
                f"Maximum allowed: {self.max_size}"
            )

        # Validate all keys and values are strings (HSTORE requirement)
        for key, val in value.items():
            # Type validation
            if not isinstance(key, str):
                raise ValueError(
                    f"{self.name}: All keys must be strings, got {type(key).__name__}"
                )

            # Security: Enforce maximum key length
            if len(key.encode('utf-8')) > self.MAX_KEY_LENGTH:
                raise ValueError(
                    f"{self.name}: Key too long ({len(key.encode('utf-8'))} bytes). "
                    f"Maximum allowed: {self.MAX_KEY_LENGTH} bytes"
                )

            # Validate value type and length
            if val is not None:
                if not isinstance(val, str):
                    raise ValueError(
                        f"{self.name}: All values must be strings or None, "
                        f"got {type(val).__name__}"
                    )

                # Security: Enforce maximum value length
                if len(val.encode('utf-8')) > self.MAX_VALUE_LENGTH:
                    raise ValueError(
                        f"{self.name}: Value too long ({len(val.encode('utf-8'))} bytes). "
                        f"Maximum allowed: {self.MAX_VALUE_LENGTH} bytes"
                    )

        return value

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python dict."""
        if value is None:
            return None

        # Already a dict (PostgreSQL HSTORE returns this directly)
        if isinstance(value, dict):
            # Security: Validate dict size even if from database
            if len(value) > self.max_size:
                raise ValueError(
                    f"{self.name}: Dictionary from database too large ({len(value)} keys). "
                    f"Maximum allowed: {self.max_size}"
                )
            return value

        # JSON string (MySQL, SQLite)
        if isinstance(value, str):
            # Security: Check JSON string size before parsing
            if len(value) > self.MAX_JSON_SIZE:
                raise ValueError(
                    f"{self.name}: JSON string too large ({len(value)} bytes). "
                    f"Maximum allowed: {self.MAX_JSON_SIZE} bytes"
                )

            try:
                result = json.loads(value)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"{self.name}: Cannot parse JSON to dict: {str(e)}"
                )

            # Security: Validate parsed dict size
            if not isinstance(result, dict):
                raise ValueError(
                    f"{self.name}: JSON must deserialize to dict, got {type(result).__name__}"
                )

            if len(result) > self.max_size:
                raise ValueError(
                    f"{self.name}: Parsed dictionary too large ({len(result)} keys). "
                    f"Maximum allowed: {self.max_size}"
                )

            return result

        raise ValueError(
            f"{self.name}: Expected dict or JSON string from database, "
            f"got {type(value).__name__}"
        )

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Convert Python dict to database value."""
        if value is None:
            return None

        if dialect == "postgresql":
            # PostgreSQL HSTORE accepts dict directly
            return value
        elif dialect == "mysql":
            # MySQL JSON type accepts dict directly
            return value
        elif dialect == "sqlite":
            # SQLite stores as JSON string
            return json.dumps(value)
        elif dialect == "mongodb":
            # MongoDB stores as document
            return value
        else:
            return json.dumps(value)


class InetField(Field):
    """
    Network address field with optional CIDR notation.

    PostgreSQL: INET (native network type with subnet support)
    Other DBs: VARCHAR(45) (stores as string: "192.168.1.1" or "2001:db8::1/64")

    Features:
    - Validates IPv4 and IPv6 addresses
    - Supports CIDR notation (e.g., "192.168.1.0/24")
    - PostgreSQL provides network operators (<, >, <<, >>, &&)
    - Optional protocol restriction (IPv4 only, IPv6 only)

    Example:
        class Server(Model):
            ip_address = InetField()
            ipv4_only = InetField(protocol='IPv4')

        server.ip_address = "192.168.1.100"
        server.ipv4_only = "10.0.0.1/24"
        await server.save()
    """

    def __init__(self, protocol: str = None, **kwargs):
        """
        Initialize INET field.

        Args:
            protocol: Optional protocol restriction ('IPv4' or 'IPv6')
        """
        self.protocol = protocol
        if protocol not in (None, 'IPv4', 'IPv6'):
            raise ValueError("protocol must be None, 'IPv4', or 'IPv6'")

        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database-specific type for INET field."""
        if dialect == "postgresql":
            return "INET"
        else:
            # All other databases use VARCHAR
            # Max: 45 chars for IPv6 (39) + /128 (4) + padding
            return "VARCHAR(45)"

    def validate(self, value: Any) -> Any:
        """Validate network address (with optional CIDR)."""
        # Check type first
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{self.name}: Value must be a string")

        value = super().validate(value)

        if value is None:
            return value

        # Parse as network address (supports CIDR notation)
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError as e:
            raise ValueError(f"{self.name}: Invalid network address: {e}")

        # Check protocol restriction
        if self.protocol == 'IPv4' and network.version != 4:
            raise ValueError(f"{self.name}: Only IPv4 addresses allowed")
        elif self.protocol == 'IPv6' and network.version != 6:
            raise ValueError(f"{self.name}: Only IPv6 addresses allowed")

        return value

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python string."""
        if value is None:
            return None

        # PostgreSQL INET returns as string
        if isinstance(value, str):
            return value

        raise ValueError(f"Cannot convert {value!r} to network address")

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Convert Python string to database value."""
        if value is None:
            return None

        # All databases store as string
        return value


class CidrField(Field):
    """
    Network range field (CIDR notation required).

    PostgreSQL: CIDR (validates network address, host bits must be zero)
    Other DBs: VARCHAR(45) (stores as string: "192.168.1.0/24")

    Difference from InetField:
    - CIDR requires network address (host bits = 0)
    - INET allows host addresses with subnet (e.g., "192.168.1.100/24")

    Features:
    - Validates CIDR notation
    - Ensures host bits are zero (strict network address)
    - PostgreSQL provides containment operators (<<, >>, &&)
    - Optional protocol restriction

    Example:
        class NetworkRange(Model):
            subnet = CidrField()
            ipv6_range = CidrField(protocol='IPv6')

        range.subnet = "192.168.1.0/24"  # Valid
        range.subnet = "192.168.1.100/24"  # Invalid (host bits non-zero)
        await range.save()
    """

    def __init__(self, protocol: str = None, **kwargs):
        """
        Initialize CIDR field.

        Args:
            protocol: Optional protocol restriction ('IPv4' or 'IPv6')
        """
        self.protocol = protocol
        if protocol not in (None, 'IPv4', 'IPv6'):
            raise ValueError("protocol must be None, 'IPv4', or 'IPv6'")

        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database-specific type for CIDR field."""
        if dialect == "postgresql":
            return "CIDR"
        else:
            # All other databases use VARCHAR
            return "VARCHAR(45)"

    def validate(self, value: Any) -> Any:
        """Validate CIDR notation (strict network address)."""
        # Check type first
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{self.name}: Value must be a string")

        value = super().validate(value)

        if value is None:
            return value

        # Parse as network address (strict=True requires host bits = 0)
        try:
            network = ipaddress.ip_network(value, strict=True)
        except ValueError as e:
            # Check if it's a host bits issue
            if "has host bits set" in str(e):
                raise ValueError(
                    f"{self.name}: CIDR requires network address (host bits must be zero). "
                    f"Use {ipaddress.ip_network(value, strict=False).network_address}/"
                    f"{value.split('/')[-1]} instead of {value}"
                )
            raise ValueError(f"{self.name}: Invalid CIDR notation: {e}")

        # Check protocol restriction
        if self.protocol == 'IPv4' and network.version != 4:
            raise ValueError(f"{self.name}: Only IPv4 networks allowed")
        elif self.protocol == 'IPv6' and network.version != 6:
            raise ValueError(f"{self.name}: Only IPv6 networks allowed")

        return value

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python string."""
        if value is None:
            return None

        # PostgreSQL CIDR returns as string
        if isinstance(value, str):
            return value

        raise ValueError(f"Cannot convert {value!r} to CIDR notation")

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Convert Python string to database value."""
        if value is None:
            return None

        # All databases store as string
        return value


# =============================================================================
# Phase 4: Advanced PostgreSQL and Path Fields
# =============================================================================


class FilePathField(CharField):
    """
    File system path selection field with optional filtering.

    All databases: VARCHAR (stores file paths as strings)

    Features:
    - Validates paths exist on file system
    - Optional directory restriction (path must be within base path)
    - Optional regex pattern matching
    - Optional recursive directory scanning
    - Security: Path traversal protection

    Example:
        class Document(Model):
            template = FilePathField(
                path='/app/templates',
                match=r'.*\.html$',
                recursive=True
            )

        doc.template = '/app/templates/invoice.html'  # Valid if file exists
        await doc.save()
    """

    def __init__(
        self,
        path: str = None,
        match: str = None,
        recursive: bool = False,
        allow_files: bool = True,
        allow_folders: bool = False,
        max_length: int = 255,
        **kwargs
    ):
        """
        Initialize FilePath field.

        Args:
            path: Base directory path (required for validation)
            match: Optional regex pattern for filename matching
            recursive: Allow subdirectories (default: False)
            allow_files: Allow file paths (default: True)
            allow_folders: Allow directory paths (default: False)
            max_length: Maximum path length (default: 255)
        """
        self.base_path = Path(path) if path else None
        self.match = match
        self.recursive = recursive
        self.allow_files = allow_files
        self.allow_folders = allow_folders

        # Compile regex pattern if provided
        self.match_re = None
        if match:
            import re
            try:
                self.match_re = re.compile(match)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")

        super().__init__(max_length=max_length, **kwargs)

    def validate(self, value: Any) -> Any:
        """Validate file path exists and matches criteria."""
        value = super().validate(value)

        if value is None:
            return value

        # Convert to Path object for validation
        file_path = Path(value)

        # Security: If base_path is set, ensure path is within it
        if self.base_path:
            try:
                # Resolve both paths to absolute
                resolved_path = file_path.resolve()
                base_resolved = self.base_path.resolve()

                # Verify path is within base_path
                try:
                    # Python 3.9+
                    is_safe = resolved_path.is_relative_to(base_resolved)
                except AttributeError:
                    # Python < 3.9 fallback
                    try:
                        resolved_path.relative_to(base_resolved)
                        is_safe = True
                    except ValueError:
                        is_safe = False

                if not is_safe:
                    raise ValueError(
                        f"{self.name}: Path must be within {self.base_path}"
                    )

                # Check if path exists
                if not resolved_path.exists():
                    raise ValueError(f"{self.name}: Path does not exist: {value}")

                # Check file vs folder
                if resolved_path.is_file() and not self.allow_files:
                    raise ValueError(f"{self.name}: Files not allowed, got file: {value}")

                if resolved_path.is_dir() and not self.allow_folders:
                    raise ValueError(f"{self.name}: Folders not allowed, got folder: {value}")

                # Check recursive restriction
                if not self.recursive:
                    # Path must be direct child of base_path
                    if resolved_path.parent != base_resolved:
                        raise ValueError(
                            f"{self.name}: Path must be directly within {self.base_path} "
                            "(recursive=False)"
                        )

                # Check regex pattern match
                if self.match_re:
                    filename = resolved_path.name
                    if not self.match_re.match(filename):
                        raise ValueError(
                            f"{self.name}: Filename '{filename}' does not match pattern '{self.match}'"
                        )

            except (OSError, RuntimeError) as e:
                raise ValueError(f"{self.name}: Invalid path: {e}")

        return value


class TSVectorField(Field):
    """
    PostgreSQL full-text search field (TSVECTOR).

    PostgreSQL: TSVECTOR (native full-text search)
    Other DBs: NOT SUPPORTED (raises error)

    Features:
    - Automatic text indexing for full-text search
    - Language-specific stemming
    - Ranking and highlighting support
    - GIN/GIST index support

    Note: This field is PostgreSQL-only and requires:
    1. PostgreSQL database
    2. Proper GIN or GIST index for performance
    3. Trigger or application-level updates

    Example:
        class Article(Model):
            title = CharField(max_length=200)
            content = TextField()
            search_vector = TSVectorField()

        # Usage with PostgreSQL full-text search:
        # SELECT * FROM articles WHERE search_vector @@ to_tsquery('python & database');
    """

    def __init__(self, config: str = 'english', **kwargs):
        """
        Initialize TSVector field.

        Args:
            config: Text search configuration (default: 'english')
                   Supported: 'english', 'simple', 'french', 'german', etc.
        """
        self.config = config
        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database-specific type for TSVector field."""
        if dialect == "postgresql":
            return "TSVECTOR"
        else:
            raise ValueError(
                f"{self.__class__.__name__} is only supported on PostgreSQL, "
                f"not {dialect}"
            )

    def validate(self, value: Any) -> Any:
        """Validate TSVector value (must be string for manual assignment)."""
        # TSVector fields are typically auto-generated, but allow manual string input
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{self.name}: Value must be a string")

        value = super().validate(value)
        return value

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python string."""
        if value is None:
            return None

        # PostgreSQL returns TSVECTOR as string
        if isinstance(value, str):
            return value

        raise ValueError(
            f"{self.name}: Expected string from database, got {type(value).__name__}"
        )

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Convert Python string to database value."""
        if value is None:
            return None

        if dialect != "postgresql":
            raise ValueError(
                f"{self.__class__.__name__} is only supported on PostgreSQL"
            )

        # Return string as-is (PostgreSQL will handle conversion)
        return value


# Geometry field base class and implementations
class GeometryField(Field):
    """
    Base class for PostGIS geometry fields.

    PostgreSQL with PostGIS: GEOMETRY type
    Other DBs: NOT SUPPORTED

    Subclasses:
    - PointField: POINT geometry
    - PolygonField: POLYGON geometry
    - LineStringField: LINESTRING geometry

    Note: Requires PostGIS extension in PostgreSQL.
    """

    geometry_type = "GEOMETRY"  # Override in subclasses

    def __init__(self, srid: int = 4326, **kwargs):
        """
        Initialize Geometry field.

        Args:
            srid: Spatial Reference System Identifier (default: 4326 = WGS84)
        """
        self.srid = srid
        super().__init__(**kwargs)

    def get_db_type(self, dialect: str = "postgresql") -> str:
        """Get database-specific type for Geometry field."""
        if dialect == "postgresql":
            return f"GEOMETRY({self.geometry_type}, {self.srid})"
        else:
            raise ValueError(
                f"{self.__class__.__name__} requires PostgreSQL with PostGIS extension"
            )

    def validate(self, value: Any) -> Any:
        """Validate geometry value (WKT string or tuple)."""
        if value is not None:
            # Accept WKT string or coordinate tuple
            if not isinstance(value, (str, tuple, list)):
                raise ValueError(
                    f"{self.name}: Value must be WKT string, tuple, or list"
                )

        value = super().validate(value)
        return value

    def to_python(self, value: Any) -> Any:
        """Convert database value to Python representation."""
        if value is None:
            return None

        # PostGIS returns WKB (binary) or WKT (text) depending on driver
        # For simplicity, we'll work with WKT strings
        if isinstance(value, str):
            return value

        if isinstance(value, (bytes, memoryview)):
            # WKB format - would need shapely or similar to parse
            # For now, return as-is
            return value

        return value

    def get_db_value(self, value: Any, dialect: str = "postgresql") -> Any:
        """Convert Python value to database representation."""
        if value is None:
            return None

        if dialect != "postgresql":
            raise ValueError(
                f"{self.__class__.__name__} requires PostgreSQL with PostGIS"
            )

        # If it's already WKT, return as-is
        if isinstance(value, str):
            return value

        # If it's a tuple/list of coordinates, convert to WKT
        # This is geometry-specific, so delegate to subclasses
        return self._coordinates_to_wkt(value)

    def _coordinates_to_wkt(self, value: Any) -> str:
        """Convert coordinates to WKT format. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement _coordinates_to_wkt")


class PointField(GeometryField):
    """
    PostGIS POINT geometry field.

    Stores a single point in 2D or 3D space.

    Example:
        class Location(Model):
            name = CharField(max_length=100)
            coordinates = PointField()

        loc.coordinates = "POINT(-122.4194 37.7749)"  # WKT format
        # Or as tuple:
        loc.coordinates = (-122.4194, 37.7749)  # (longitude, latitude)
        await loc.save()
    """

    geometry_type = "POINT"

    def _coordinates_to_wkt(self, value: Any) -> str:
        """Convert point coordinates to WKT."""
        if isinstance(value, (tuple, list)):
            if len(value) == 2:
                return f"POINT({value[0]} {value[1]})"
            elif len(value) == 3:
                return f"POINT({value[0]} {value[1]} {value[2]})"
            else:
                raise ValueError(
                    f"{self.name}: Point must have 2 or 3 coordinates, got {len(value)}"
                )

        raise ValueError(
            f"{self.name}: Cannot convert {type(value).__name__} to POINT WKT"
        )


class PolygonField(GeometryField):
    """
    PostGIS POLYGON geometry field.

    Stores a polygon defined by a closed ring of points.

    Example:
        class Zone(Model):
            name = CharField(max_length=100)
            boundary = PolygonField()

        zone.boundary = "POLYGON((0 0, 10 0, 10 10, 0 10, 0 0))"  # WKT format
        await zone.save()
    """

    geometry_type = "POLYGON"

    def _coordinates_to_wkt(self, value: Any) -> str:
        """Convert polygon coordinates to WKT."""
        if isinstance(value, (tuple, list)):
            # Expect list of rings, each ring is list of points
            if len(value) > 0 and isinstance(value[0], (tuple, list)):
                rings = []
                for ring in value:
                    points = [f"{pt[0]} {pt[1]}" for pt in ring]
                    rings.append(f"({', '.join(points)})")
                return f"POLYGON({', '.join(rings)})"

        raise ValueError(
            f"{self.name}: Cannot convert {type(value).__name__} to POLYGON WKT"
        )


class LineStringField(GeometryField):
    """
    PostGIS LINESTRING geometry field.

    Stores a line defined by a sequence of points.

    Example:
        class Route(Model):
            name = CharField(max_length=100)
            path = LineStringField()

        route.path = "LINESTRING(0 0, 10 10, 20 20)"  # WKT format
        await route.save()
    """

    geometry_type = "LINESTRING"

    def _coordinates_to_wkt(self, value: Any) -> str:
        """Convert linestring coordinates to WKT."""
        if isinstance(value, (tuple, list)):
            # Expect list of points
            if len(value) > 0 and isinstance(value[0], (tuple, list)):
                points = [f"{pt[0]} {pt[1]}" for pt in value]
                return f"LINESTRING({', '.join(points)})"

        raise ValueError(
            f"{self.name}: Cannot convert {type(value).__name__} to LINESTRING WKT"
        )


__all__ = [
    "Field",
    "CharField",
    "TextField",
    "IntegerField",
    "BigIntegerField",
    "SmallIntegerField",
    "FloatField",
    "DecimalField",
    "BooleanField",
    "DateTimeField",
    "DateField",
    "TimeField",
    "JSONField",
    "UUIDField",
    "EmailField",
    "URLField",
    "BinaryField",
    "ArrayField",
    "EnumField",
    "DurationField",
    "IPAddressField",
    "SlugField",
    "FieldFile",
    "FileField",
    "ImageFieldFile",
    "ImageField",
    "AutoField",
    "BigAutoField",
    "PositiveIntegerField",
    "PositiveSmallIntegerField",
    "Money",
    "MoneyField",
    "HStoreField",
    "InetField",
    "CidrField",
    "FilePathField",
    "TSVectorField",
    "GeometryField",
    "PointField",
    "PolygonField",
    "LineStringField",
]
