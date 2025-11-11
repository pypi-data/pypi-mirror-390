"""
ORM Model Base Class

Django-style Model class with Active Record pattern for intuitive database operations.
Provides comprehensive CRUD operations, validation, signals, and relationship support.

Example:
    from covet.database.orm import Model
    from covet.database.orm.fields import CharField, EmailField, DateTimeField
    from covet.database.orm.relationships import ForeignKey

    class User(Model):
        username = CharField(max_length=100, unique=True)
        email = EmailField(unique=True)
        is_active = BooleanField(default=True)
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            db_table = 'users'
            ordering = ['-created_at']
            indexes = [
                Index(fields=['email']),
                Index(fields=['username', 'email'])
            ]

        def clean(self):
            # Custom validation
            if 'admin' in self.username and not self.is_superuser:
                raise ValueError("Admin username requires superuser flag")

    # Usage
    user = User(username='alice', email='alice@example.com')
    await user.save()

    user = await User.objects.get(id=1)
    user.username = 'alice_updated'
    await user.save()

    await user.delete()
"""

import copy
import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Type, Union

from .fields import (
    ArrayField,
    BigIntegerField,
    BinaryField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    EnumField,
    Field,
    FloatField,
    IntegerField,
    JSONField,
    SmallIntegerField,
    TextField,
    TimeField,
    URLField,
    UUIDField,
)

logger = logging.getLogger(__name__)


class ModelMeta(type):
    """
    Metaclass for Model classes.

    Handles:
    - Field registration and setup
    - Table name auto-generation
    - Manager (objects) setup
    - Meta class processing
    - Primary key detection
    """

    def __new__(mcs, name, bases, namespace, **kwargs):
        """
        Create new Model class.

        Args:
            name: Class name
            bases: Base classes
            namespace: Class attributes
            **kwargs: Additional arguments
        """
        # Don't process the base Model class itself
        if name == "Model" and not bases:
            return super().__new__(mcs, name, bases, namespace)

        # Extract fields
        # Import Field from fields module to check isinstance
        from .fields import Field as FieldBase

        fields = {}
        for key, value in list(namespace.items()):
            if isinstance(value, FieldBase):
                fields[key] = value
                # Remove from namespace (will be added as descriptors)
                namespace.pop(key)

        # Create class
        cls = super().__new__(mcs, name, bases, namespace)

        # Process Meta class
        meta = namespace.get("Meta")
        cls._meta = ModelOptions(cls, meta)

        # Set up fields
        cls._fields = {}
        cls._meta.pk_field = None

        for field_name, field in fields.items():
            field.name = field_name
            field.model = cls

            # Set db_column if not specified
            if field.db_column is None:
                field.db_column = field_name

            # Call contribute_to_class if available (for relations)
            if hasattr(field, "contribute_to_class"):
                field.contribute_to_class(cls, field_name)

            cls._fields[field_name] = field

            # Add field back to class as descriptor
            setattr(cls, field_name, field)

            # Detect primary key
            if field.primary_key:
                if cls._meta.pk_field is not None:
                    raise ValueError(
                        f"Model {name} has multiple primary keys: "
                        f"{cls._meta.pk_field.name} and {field_name}"
                    )
                cls._meta.pk_field = field

        # Add default 'id' primary key if none specified
        if cls._meta.pk_field is None:
            from .fields import IntegerField

            id_field = IntegerField(primary_key=True, auto_increment=True)
            id_field.name = "id"
            id_field.db_column = "id"
            id_field.model = cls
            cls._fields["id"] = id_field
            cls._meta.pk_field = id_field

            # Add id field as descriptor to class
            setattr(cls, "id", id_field)

        # Set table name
        if not hasattr(cls._meta, "db_table") or cls._meta.db_table is None:
            # Auto-generate from class name: User -> users, UserProfile ->
            # user_profiles
            import re

            table_name = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower() + "s"
            cls._meta.db_table = table_name

        # CRITICAL SECURITY: Validate table name to prevent SQL injection
        # Table names must be valid SQL identifiers (alphanumeric + underscores, starting with letter/underscore)
        import re
        tablename = cls._meta.db_table

        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', tablename):
            raise ValueError(
                f"Invalid table name '{tablename}' for model {name}: "
                f"Table names must start with a letter or underscore and contain only "
                f"alphanumeric characters and underscores. This prevents SQL injection attacks."
            )

        cls.__tablename__ = cls._meta.db_table

        # Set database alias
        if not hasattr(cls._meta, "db_alias"):
            cls._meta.db_alias = "default"
        cls.__database__ = cls._meta.db_alias

        # Set up manager
        from .managers import ModelManager

        manager = ModelManager(cls)
        cls.objects = manager

        # Create exception classes
        cls.DoesNotExist = type(
            f"{name}.DoesNotExist",
            (ObjectDoesNotExist,),
            {"__module__": cls.__module__},
        )
        cls.MultipleObjectsReturned = type(
            f"{name}.MultipleObjectsReturned",
            (MultipleObjectsReturned,),
            {"__module__": cls.__module__},
        )

        # Register model for lazy relationship resolution
        from .relationships import register_model

        register_model(cls)

        return cls


class Field:
    """Import Field from fields module."""

    pass  # Placeholder, will be imported


class ModelOptions:
    """
    Model Meta options container.

    Stores configuration from Model.Meta class.
    """

    def __init__(self, model: Type, meta_class=None):
        """
        Initialize model options.

        Args:
            model: Model class
            meta_class: Meta class from model
        """
        self.model = model
        self.pk_field = None
        self.db_table = None
        self.db_alias = "default"
        self.ordering = []
        self.indexes = []
        self.unique_together = []
        self.constraints = []
        self.abstract = False
        self.managed = True
        self.verbose_name = None
        self.verbose_name_plural = None

        # Process meta class
        if meta_class:
            self._process_meta(meta_class)

    def _process_meta(self, meta_class):
        """Extract options from Meta class."""
        for key in dir(meta_class):
            if not key.startswith("_"):
                value = getattr(meta_class, key)
                setattr(self, key, value)


class Model(metaclass=ModelMeta):
    """
    Base class for all ORM models.

    Provides Active Record pattern with:
    - CRUD operations (create, read, update, delete)
    - Field validation
    - Signal support (pre_save, post_save, etc.)
    - Relationship handling
    - Query building via objects manager

    Class Attributes:
        __tablename__: Database table name
        __database__: Database alias
        objects: ModelManager for queries
        _meta: ModelOptions with configuration
        _fields: Dict of field definitions

    Instance Methods:
        save(): Save instance to database
        delete(): Delete instance from database
        refresh(): Reload from database
        validate(): Validate all fields
        clean(): Custom validation hook

    Example:
        class User(Model):
            username = CharField(max_length=100)
            email = EmailField()

            class Meta:
                db_table = 'users'
                ordering = ['-created_at']

        user = User(username='alice', email='alice@example.com')
        await user.save()
    """

    # Class attributes set by metaclass
    __tablename__: str = None
    __database__: str = "default"
    objects = None  # ModelManager
    _meta = None  # ModelOptions
    _fields: Dict[str, "Field"] = {}

    def __init__(self, **kwargs):
        """
        Initialize model instance with field values.

        Args:
            **kwargs: Field values

        Example:
            user = User(username='alice', email='alice@example.com')
        """
        # Send pre_init signal
        from .signals import pre_init

        if hasattr(pre_init, "send"):
            import asyncio

            asyncio.create_task(
                pre_init.send(sender=self.__class__, instance=self, args=(), kwargs=kwargs)
            )

        # Track if instance is saved to database
        self._state = ModelState()

        # Set field values
        for field_name, field in self._fields.items():
            if field_name in kwargs:
                value = kwargs[field_name]
            else:
                value = field.get_default()

            setattr(self, field_name, value)

        # Send post_init signal
        from .signals import post_init

        if hasattr(post_init, "send"):
            import asyncio

            asyncio.create_task(post_init.send(sender=self.__class__, instance=self))

    async def save(
        self,
        force_insert: bool = False,
        force_update: bool = False,
        using: Optional[str] = None,
        update_fields: Optional[List[str]] = None,
    ) -> "Model":
        """
        Save instance to database.

        Performs INSERT for new records or UPDATE for existing records.
        Runs validation and sends pre_save/post_save signals.

        Args:
            force_insert: Force INSERT even if PK exists
            force_update: Force UPDATE even if PK doesn't exist
            using: Database alias to use
            update_fields: Only update specified fields

        Returns:
            Self for chaining

        Raises:
            ValueError: If validation fails or unique constraint violated
            DatabaseError: If database operation fails

        Example:
            user = User(username='alice')
            await user.save()

            user.username = 'alice_updated'
            await user.save(update_fields=['username'])
        """
        using = using or self.__database__

        try:
            # Validate (field validation and custom clean)
            self.full_clean()

            # Check unique constraints (requires database access)
            await self._check_unique_constraints()
        except ValueError as e:
            # Re-raise validation errors with clear context
            logger.error(f"Validation error saving {self.__class__.__name__}: {e}")
            raise ValueError(f"Validation failed for {self.__class__.__name__}: {e}") from e

        # Determine if INSERT or UPDATE
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name, None)

        # Logic: INSERT if:
        # 1. PK is None (new record)
        # 2. force_insert flag is set
        # 3. This is a new record (self._state.adding) even if PK exists (for non-auto-increment PKs)
        is_insert = (
            pk_value is None or force_insert or (self._state.adding and not pk_field.auto_increment)
        )

        # Send pre_save signal
        from .signals import pre_save

        await pre_save.send(sender=self.__class__, instance=self, raw=False, using=using)

        # Get adapter
        try:
            adapter = await self._get_adapter(using)
        except Exception as e:
            logger.error(f"Database connection error for {self.__class__.__name__}: {e}")
            raise RuntimeError(f"Database connection failed: {e}") from e

        # Perform database operation with error handling
        try:
            if is_insert:
                # INSERT
                await self._insert(adapter, update_fields)
                created = True
            else:
                # UPDATE
                await self._update(adapter, update_fields)
                created = False
        except ValueError as e:
            # Validation or constraint errors from database
            logger.error(f"Database constraint error for {self.__class__.__name__}: {e}")
            raise
        except Exception as e:
            # Database errors (connection, syntax, etc.)
            error_msg = str(e).lower()

            # Provide helpful error messages for common database errors
            if 'unique' in error_msg or 'duplicate' in error_msg:
                raise ValueError(
                    f"Unique constraint violation for {self.__class__.__name__}: "
                    f"A record with this value already exists"
                ) from e
            elif 'foreign key' in error_msg or 'constraint' in error_msg:
                raise ValueError(
                    f"Foreign key constraint violation for {self.__class__.__name__}: "
                    f"Referenced record does not exist"
                ) from e
            elif 'not null' in error_msg:
                raise ValueError(
                    f"Required field missing for {self.__class__.__name__}: "
                    f"A required field cannot be null"
                ) from e
            else:
                logger.error(f"Database error saving {self.__class__.__name__}: {e}", exc_info=True)
                raise RuntimeError(
                    f"Database error saving {self.__class__.__name__}: {e}"
                ) from e

        # Update state
        self._state.adding = False
        self._state.db = using

        # Send post_save signal
        from .signals import post_save

        await post_save.send(
            sender=self.__class__,
            instance=self,
            created=created,
            raw=False,
            using=using,
        )

        return self

    async def _insert(self, adapter, fields: Optional[List[str]] = None) -> None:
        """
        Perform INSERT operation.

        Args:
            adapter: Database adapter
            fields: Fields to insert (None = all)
        """
        # Build INSERT query
        field_names = []
        values = []

        pk_field = self._meta.pk_field

        for field_name, field in self._fields.items():
            # Skip auto-increment PK
            if field.primary_key and field.auto_increment:
                continue

            # Skip fields without db_column (e.g., ForeignKey descriptors)
            if field.db_column is None:
                continue

            # Skip if specific fields requested and not in list
            if fields and field_name not in fields:
                continue

            # Handle auto_now_add
            if hasattr(field, "auto_now_add") and field.auto_now_add:
                value = datetime.now()
                setattr(self, field_name, value)
            # Handle auto_now
            elif hasattr(field, "auto_now") and field.auto_now:
                value = datetime.now()
                setattr(self, field_name, value)
            else:
                value = getattr(self, field_name, None)

            # Convert to database value
            db_value = field.to_db(value)

            field_names.append(field.db_column)
            values.append(db_value)

        # Detect database type and build appropriate placeholders
        param_placeholders = self._get_param_placeholders(adapter, len(values))

        # Build query
        if field_names:
            query = (
                f"INSERT INTO {self.__tablename__} "  # nosec B608 - identifiers validated
                f"({', '.join(field_names)}) "
                f"VALUES ({', '.join(param_placeholders)})"
            )
        else:
            # Empty insert - all fields are auto-generated or defaults
            # SQLite syntax: INSERT INTO table DEFAULT VALUES
            from ..adapters.sqlite import SQLiteAdapter
            if isinstance(adapter, SQLiteAdapter):
                query = f"INSERT INTO {self.__tablename__} DEFAULT VALUES"  # nosec B608
            else:
                # PostgreSQL/MySQL: INSERT INTO table () VALUES ()
                query = f"INSERT INTO {self.__tablename__} () VALUES ()"  # nosec B608

        # Add RETURNING clause for auto-increment PK (PostgreSQL)
        if pk_field.auto_increment and self._adapter_supports_returning(adapter):
            query += f" RETURNING {pk_field.db_column}"

        # Execute
        if pk_field.auto_increment:
            if self._adapter_supports_returning(adapter):
                # PostgreSQL-style RETURNING
                result = await adapter.fetch_one(query, values)
                if result:
                    pk_value = result[pk_field.db_column]
                    setattr(self, pk_field.name, pk_value)
            else:
                # MySQL/SQLite-style last_insert_id
                # Use execute_insert() which returns the last insert ID
                if hasattr(adapter, "execute_insert"):
                    last_id = await adapter.execute_insert(query, values)
                    setattr(self, pk_field.name, last_id)
                else:
                    # Fallback for adapters that don't have execute_insert
                    await adapter.execute(query, values)
        else:
            await adapter.execute(query, values)

    async def _update(self, adapter, fields: Optional[List[str]] = None) -> None:
        """
        Perform UPDATE operation.

        Args:
            adapter: Database adapter
            fields: Fields to update (None = all)
        """
        # Build UPDATE query
        set_parts = []
        values = []
        pk_field = self._meta.pk_field

        for field_name, field in self._fields.items():
            # Skip primary key
            if field.primary_key:
                continue

            # Skip fields without db_column (e.g., ForeignKey descriptors)
            if field.db_column is None:
                continue

            # Skip if specific fields requested and not in list
            if fields and field_name not in fields:
                continue

            # Handle auto_now
            if hasattr(field, "auto_now") and field.auto_now:
                value = datetime.now()
                setattr(self, field_name, value)
            else:
                value = getattr(self, field_name, None)

            # Convert to database value
            db_value = field.to_db(value)

            values.append(db_value)

        # Add WHERE clause
        pk_value = getattr(self, pk_field.name)
        values.append(pk_value)

        # Get appropriate placeholders
        placeholders = self._get_param_placeholders(adapter, len(values))

        # Build SET clause
        set_parts = [
            f"{field.db_column} = {placeholders[i]}"
            for i, (field_name, field) in enumerate(
                (fn, f)
                for fn, f in self._fields.items()
                if not f.primary_key and f.db_column is not None and (not fields or fn in fields)
            )
        ]

        query = (
            f"UPDATE {self.__tablename__} "  # nosec B608 - identifiers validated
            f"SET {', '.join(set_parts)} "
            f"WHERE {pk_field.db_column} = {placeholders[-1]}"
        )

        # Execute
        await adapter.execute(query, values)

    async def delete(self, using: Optional[str] = None) -> tuple:
        """
        Delete instance from database.

        Args:
            using: Database alias to use

        Returns:
            Tuple of (num_deleted, {model_name: count})

        Example:
            user = await User.objects.get(id=1)
            await user.delete()
        """
        using = using or self.__database__

        # Send pre_delete signal
        from .signals import pre_delete

        await pre_delete.send(sender=self.__class__, instance=self, using=using)

        # Get adapter
        adapter = await self._get_adapter(using)

        # Build DELETE query
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name)

        # Get appropriate placeholder
        placeholder = self._get_param_placeholders(adapter, 1)[0]

        query = f"DELETE FROM {self.__tablename__} WHERE {pk_field.db_column} = {placeholder}"  # nosec B608 - identifiers validated

        # Execute
        result = await adapter.execute(query, [pk_value])

        # Parse result
        if isinstance(result, str) and result.startswith("DELETE"):
            count = int(result.split()[1])
        else:
            count = 1

        # Send post_delete signal
        from .signals import post_delete

        await post_delete.send(sender=self.__class__, instance=self, using=using)

        return (count, {self.__class__.__name__: count})

    async def refresh(
        self, using: Optional[str] = None, fields: Optional[List[str]] = None
    ) -> "Model":
        """
        Reload instance from database.

        Args:
            using: Database alias to use
            fields: Fields to reload (None = all)

        Returns:
            Self for chaining

        Example:
            user = await User.objects.get(id=1)
            # ... changes in database ...
            await user.refresh()
        """
        using = using or self.__database__

        # Get adapter
        adapter = await self._get_adapter(using)

        # Build SELECT query
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name)

        if fields:
            select_clause = ", ".join(
                self._fields[f].db_column for f in fields if f in self._fields
            )
        else:
            select_clause = "*"

        # Get appropriate placeholder
        placeholder = self._get_param_placeholders(adapter, 1)[0]

        query = (
            f"SELECT {select_clause} FROM {self.__tablename__} "  # nosec B608 - identifiers validated
            f"WHERE {pk_field.db_column} = {placeholder}"
        )

        # Execute
        row = await adapter.fetch_one(query, [pk_value])

        if not row:
            raise self.DoesNotExist(
                f"{self.__class__.__name__} with {pk_field.name}={pk_value} does not exist"
            )

        # Update instance fields
        for field_name, field in self._fields.items():
            if fields and field_name not in fields:
                continue

            if field.db_column in row:
                value = row[field.db_column]
                setattr(self, field_name, field.to_python(value))

        return self

    def validate(self) -> None:
        """
        Validate all field values.

        Raises:
            ValueError: If any field validation fails

        Example:
            user = User(email='invalid')
            user.validate()  # Raises ValueError
        """
        errors = {}

        for field_name, field in self._fields.items():
            # Skip validation for auto-increment primary keys during INSERT
            # They will be populated by the database
            if field.primary_key and hasattr(field, 'auto_increment') and field.auto_increment:
                pk_value = getattr(self, field_name, None)
                if pk_value is None and self._state.adding:
                    continue  # Skip validation for new records with auto-increment PK

            try:
                value = getattr(self, field_name, None)
                field.validate(value)
            except ValueError as e:
                errors[field_name] = str(e)

        if errors:
            raise ValueError(f"Validation errors: {errors}")

    def clean(self) -> None:
        """
        Custom validation hook.

        Override this method to add model-level validation.

        Example:
            class User(Model):
                username = CharField()
                is_admin = BooleanField()

                def clean(self):
                    if 'admin' in self.username and not self.is_admin:
                        raise ValueError("Admin username requires admin flag")
        """
        pass

    def full_clean(self) -> None:
        """
        Run all validation (field + clean).

        Note: Unique constraint checking is performed separately during save()
        as it requires async database access.

        Raises:
            ValueError: If validation fails
        """
        # Field validation
        self.validate()

        # Model validation
        self.clean()

    async def _check_unique_constraints(self) -> None:
        """
        Check unique field constraints.

        Queries the database to ensure unique fields don't conflict with existing records.

        Raises:
            ValueError: If a unique constraint would be violated
        """
        # Get adapter
        adapter = await self._get_adapter()

        # Collect fields with unique constraint
        unique_fields = [
            (field_name, field)
            for field_name, field in self._fields.items()
            if field.unique and not field.primary_key
        ]

        if not unique_fields:
            return

        # Check each unique field
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name, None)

        for field_name, field in unique_fields:
            value = getattr(self, field_name, None)

            # Skip if value is None (will be caught by nullable validation)
            if value is None:
                continue

            # Convert to database value
            db_value = field.to_db(value)

            # Build query to check if value exists
            placeholder = self._get_param_placeholders(adapter, 1)[0]
            query = (
                f"SELECT {pk_field.db_column} FROM {self.__tablename__} "  # nosec B608 - identifiers validated
                f"WHERE {field.db_column} = {placeholder}"
            )

            # If updating existing record, exclude current record from check
            if pk_value is not None and not self._state.adding:
                pk_placeholder = self._get_param_placeholders(adapter, 1)[0]
                query += f" AND {pk_field.db_column} != {pk_placeholder}"
                params = [db_value, pk_value]
            else:
                params = [db_value]

            # Execute query
            result = await adapter.fetch_one(query, params)

            if result:
                raise ValueError(
                    f"{self.__class__.__name__}.{field_name}: "
                    f"Value '{value}' already exists. This field must be unique."
                )

    @classmethod
    async def create(cls, **kwargs) -> "Model":
        """
        Create and save new instance.

        Args:
            **kwargs: Field values

        Returns:
            Saved model instance

        Example:
            user = await User.create(
                username='alice',
                email='alice@example.com'
            )
        """
        instance = cls(**kwargs)
        await instance.save()
        return instance

    async def _get_adapter(self, using: Optional[str] = None):
        """
        Get database adapter.

        Args:
            using: Database alias

        Returns:
            Database adapter
        """
        from .adapter_registry import get_adapter

        alias = using or self.__database__
        adapter = get_adapter(alias)

        # Ensure adapter is connected
        if not adapter._connected:
            await adapter.connect()

        return adapter

    def _get_param_placeholders(self, adapter, count: int) -> List[str]:
        """
        Get parameter placeholders for the adapter's database type.

        Args:
            adapter: Database adapter
            count: Number of placeholders needed

        Returns:
            List of parameter placeholders
        """
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        if isinstance(adapter, PostgreSQLAdapter):
            # PostgreSQL uses $1, $2, $3, ...
            return [f"${i+1}" for i in range(count)]
        elif isinstance(adapter, MySQLAdapter):
            # MySQL uses %s, %s, %s, ...
            return ["%s"] * count
        elif isinstance(adapter, SQLiteAdapter):
            # SQLite uses ?, ?, ?, ...
            return ["?"] * count
        else:
            # Default to PostgreSQL-style
            return [f"${i+1}" for i in range(count)]

    def _adapter_supports_returning(self, adapter) -> bool:
        """
        Check if adapter supports RETURNING clause.

        Args:
            adapter: Database adapter

        Returns:
            True if adapter supports RETURNING
        """
        from ..adapters.postgresql import PostgreSQLAdapter

        return isinstance(adapter, PostgreSQLAdapter)

    def __repr__(self) -> str:
        """String representation."""
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name, None)
        return f"<{self.__class__.__name__}: {pk_value}>"

    def __str__(self) -> str:
        """String representation."""
        return self.__repr__()

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, self.__class__):
            return False

        pk_field = self._meta.pk_field
        my_pk = getattr(self, pk_field.name, None)
        other_pk = getattr(other, pk_field.name, None)

        if my_pk is None or other_pk is None:
            return False

        return my_pk == other_pk

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name, None)

        if pk_value is None:
            return id(self)

        return hash((self.__class__, pk_value))


class ModelState:
    """
    Track model instance state.

    Attributes:
        adding: True if instance not yet saved
        db: Database alias instance was loaded from/saved to
    """

    def __init__(self):
        self.adding = True  # True until first save
        self.db: Optional[str] = None


class ObjectDoesNotExist(Exception):
    """Object does not exist in database."""

    pass


class MultipleObjectsReturned(Exception):
    """Multiple objects returned when one expected."""

    pass


class Index:
    """
    Database index definition.

    Example:
        class User(Model):
            username = CharField()
            email = EmailField()

            class Meta:
                indexes = [
                    Index(fields=['username']),
                    Index(fields=['email', 'username'], name='email_username_idx')
                ]
    """

    def __init__(self, fields: List[str], name: Optional[str] = None, unique: bool = False):
        """
        Initialize index.

        Args:
            fields: Field names
            name: Index name (auto-generated if None)
            unique: Whether index is unique
        """
        self.fields = fields
        self.name = name
        self.unique = unique


# Re-export from fields module


__all__ = [
    "Model",
    "ModelMeta",
    "ModelOptions",
    "ModelState",
    "ObjectDoesNotExist",
    "MultipleObjectsReturned",
    "Index",
    # Fields
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
]
