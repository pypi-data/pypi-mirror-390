"""
ORM Model System

Production-ready model system with metaclass magic, field management,
and comprehensive model functionality.
"""

import asyncio
import inspect
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

from .exceptions import (
    DoesNotExist,
    IntegrityError,
    MultipleObjectsReturned,
    ORMError,
    ValidationError,
)
from .fields import AutoField, Field, RelationshipField
from .query import Q, QuerySet


class ModelRegistry:
    """Registry for all model classes."""

    _models: Dict[str, Type["Model"]] = {}

    @classmethod
    def register_model(cls, model_class: Type["Model"]):
        """Register a model class."""
        cls._models[model_class.__name__] = model_class

    @classmethod
    def get_model(cls, name: str) -> Optional[Type["Model"]]:
        """Get a model class by name."""
        return cls._models.get(name)

    @classmethod
    def get_all_models(cls) -> List[Type["Model"]]:
        """Get all registered models."""
        return list(cls._models.values())


class ModelOptions:
    """Model metadata and options."""

    def __init__(self, meta=None, model_name: str = None):
        self.model_name = model_name
        self.table_name = getattr(meta, "table_name", None)
        self.db_table = getattr(meta, "db_table", None)
        self.ordering = getattr(meta, "ordering", [])
        self.indexes = getattr(meta, "indexes", [])
        self.constraints = getattr(meta, "constraints", [])
        self.unique_together = getattr(meta, "unique_together", [])
        self.abstract = getattr(meta, "abstract", False)
        self.managed = getattr(meta, "managed", True)
        self.proxy = getattr(meta, "proxy", False)
        self.verbose_name = getattr(meta, "verbose_name", None)
        self.verbose_name_plural = getattr(meta, "verbose_name_plural", None)

        # Field collections
        self.fields: OrderedDict[str, Field] = OrderedDict()
        self.pk_field: Optional[Field] = None
        self.relationship_fields: Dict[str, RelationshipField] = {}

        # Set defaults
        if not self.table_name and not self.db_table:
            if model_name:
                self.table_name = self._get_default_table_name(model_name)

    def _get_default_table_name(self, model_name: str) -> str:
        """Convert model name to default table name."""
        # Convert CamelCase to snake_case
        import re

        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", model_name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def get_table_name(self) -> str:
        """Get the database table name."""
        return self.db_table or self.table_name

    def add_field(self, field: Field, name: str):
        """Add a field to the model."""
        self.fields[name] = field

        if field.primary_key:
            self.pk_field = field

        if isinstance(field, RelationshipField):
            self.relationship_fields[name] = field

    def get_field(self, name: str) -> Optional[Field]:
        """Get a field by name."""
        return self.fields.get(name)

    def get_all_fields(self) -> List[Field]:
        """Get all fields."""
        return list(self.fields.values())

    def get_database_fields(self) -> List[Field]:
        """Get fields that have database columns."""
        return [
            f
            for f in self.fields.values()
            if not isinstance(f, RelationshipField) or hasattr(f, "db_field_name")
        ]


class ModelMeta(type):
    """Metaclass for Model classes."""

    def __new__(mcs, name: str, bases: tuple, namespace: dict):
        # Don't process the base Model class
        if name == "Model" and not bases:
            return super().__new__(mcs, name, bases, namespace)

        # Create the class
        cls = super().__new__(mcs, name, bases, namespace)

        # Process Meta class
        meta = namespace.get("Meta", None)
        opts = ModelOptions(meta, name)
        cls._meta = opts

        # Collect fields from the class and its parents
        fields = {}

        # Get fields from parent classes
        for base in bases:
            if hasattr(base, "_meta"):
                fields.update(base._meta.fields)

        # Get fields from this class
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                fields[key] = value

        # Add auto primary key if none exists
        has_pk = any(field.primary_key for field in fields.values())
        if not has_pk and not opts.abstract:
            fields["id"] = AutoField()

        # Process fields
        for field_name, field in fields.items():
            field.contribute_to_class(cls, field_name)
            opts.add_field(field, field_name)

        # Register the model
        if not opts.abstract:
            ModelRegistry.register_model(cls)

        return cls

    def __call__(cls, *args, **kwargs):
        """Custom instantiation."""
        instance = super().__call__(*args, **kwargs)
        instance._state = ModelState()
        return instance


class ModelState:
    """Track model instance state."""

    def __init__(self):
        self.adding = True  # True if this is a new instance
        self.db = None  # Database alias
        self.fields_cache = {}  # Cached field values


class Model(metaclass=ModelMeta):
    """Base model class."""

    def __init__(self, **kwargs):
        # Set field values
        for field_name, field in self._meta.fields.items():
            if field_name in kwargs:
                value = kwargs[field_name]
            elif field.default is not None:
                value = field.get_default()
            else:
                value = None

            setattr(self, field_name, value)

        # Remove processed kwargs
        for field_name in self._meta.fields:
            kwargs.pop(field_name, None)

        # Handle extra kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        if self._meta.pk_field:
            pk_value = getattr(self, self._meta.pk_field.name, "new")
            return f"<{self.__class__.__name__}(pk={pk_value})>"
        return f"<{self.__class__.__name__}()>"

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False
        if self._meta.pk_field:
            self_pk = getattr(self, self._meta.pk_field.name, None)
            other_pk = getattr(other, self._meta.pk_field.name, None)
            return self_pk is not None and self_pk == other_pk
        return super().__eq__(other)

    def __hash__(self) -> int:
        if self._meta.pk_field:
            pk_value = getattr(self, self._meta.pk_field.name, None)
            if pk_value is not None:
                return hash(pk_value)
        return super().__hash__()

    def clean(self):
        """Validate the model instance."""
        errors = {}

        for field_name, field in self._meta.fields.items():
            try:
                value = getattr(self, field_name)
                field.validate(value, self)
            except ValidationError as e:
                errors[field_name] = str(e)

        if errors:
            raise ValidationError(errors)

    def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        validate: bool = True,
        **kwargs,
    ):
        """Save the model instance."""
        if validate:
            self.clean()

        # Use the default manager
        return self.__class__.objects.save_instance(
            self, force_insert=force_insert, force_update=force_update, **kwargs
        )

    async def asave(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        validate: bool = True,
        **kwargs,
    ):
        """Async save the model instance."""
        if validate:
            self.clean()

        return await self.__class__.objects.asave_instance(
            self, force_insert=force_insert, force_update=force_update, **kwargs
        )

    def delete(self, **kwargs):
        """Delete the model instance."""
        if not self._meta.pk_field:
            raise ORMError("Cannot delete instance without primary key")

        pk_value = getattr(self, self._meta.pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot delete instance with null primary key")

        return self.__class__.objects.filter(**{self._meta.pk_field.name: pk_value}).delete()

    async def adelete(self, **kwargs):
        """Async delete the model instance."""
        if not self._meta.pk_field:
            raise ORMError("Cannot delete instance without primary key")

        pk_value = getattr(self, self._meta.pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot delete instance with null primary key")

        return await self.__class__.objects.filter(**{self._meta.pk_field.name: pk_value}).adelete()

    def refresh_from_db(self, fields: Optional[List[str]] = None, **kwargs):
        """Reload the instance from the database."""
        if not self._meta.pk_field:
            raise ORMError("Cannot refresh instance without primary key")

        pk_value = getattr(self, self._meta.pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot refresh instance with null primary key")

        fresh_instance = self.__class__.objects.get(**{self._meta.pk_field.name: pk_value})

        fields_to_update = fields or [f.name for f in self._meta.get_database_fields()]
        for field_name in fields_to_update:
            if hasattr(fresh_instance, field_name):
                setattr(self, field_name, getattr(fresh_instance, field_name))

    async def arefresh_from_db(self, fields: Optional[List[str]] = None, **kwargs):
        """Async reload the instance from the database."""
        if not self._meta.pk_field:
            raise ORMError("Cannot refresh instance without primary key")

        pk_value = getattr(self, self._meta.pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot refresh instance with null primary key")

        fresh_instance = await self.__class__.objects.aget(**{self._meta.pk_field.name: pk_value})

        fields_to_update = fields or [f.name for f in self._meta.get_database_fields()]
        for field_name in fields_to_update:
            if hasattr(fresh_instance, field_name):
                setattr(self, field_name, getattr(fresh_instance, field_name))

    def to_dict(self, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """Convert instance to dictionary."""
        result = {}
        fields_to_include = fields or list(self._meta.fields.keys())

        for field_name in fields_to_include:
            if field_name in self._meta.fields:
                value = getattr(self, field_name, None)
                if hasattr(value, "isoformat"):  # datetime objects
                    value = value.isoformat()
                result[field_name] = value

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Model":
        """Create instance from dictionary."""
        return cls(**data)

    # Class-level query methods

    @classmethod
    def get_manager(cls):
        """Get the model manager."""
        if not hasattr(cls, "_default_manager"):
            from .managers import Manager

            cls._default_manager = Manager(cls)
        return cls._default_manager

    def __init_subclass__(cls, **kwargs):
        """Set up manager when class is created."""
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "objects"):
            from .managers import Manager

            cls.objects = Manager(cls)


# Abstract models


class AbstractModel(Model):
    """Abstract base model."""

    class Meta:
        abstract = True


# Utility functions


def get_model(app_label: str, model_name: str) -> Optional[Type[Model]]:
    """Get a model by app label and model name."""
    return ModelRegistry.get_model(model_name)


def get_models(app_label: Optional[str] = None) -> List[Type[Model]]:
    """Get all models, optionally filtered by app label."""
    return ModelRegistry.get_all_models()
