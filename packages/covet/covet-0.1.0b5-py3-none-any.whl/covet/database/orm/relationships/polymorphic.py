"""
Polymorphic Model Support

Implements three inheritance strategies:
1. Single Table Inheritance (STI) - All models in one table with discriminator
2. Multi-Table Inheritance (MTI) - Each model gets its own table, joined via foreign key
3. Abstract Base Classes - No table for base, each child has full schema

Example:
    # Abstract Base Class
    class Animal(Model):
        name = CharField(max_length=100)
        age = IntegerField()

        class Meta:
            abstract = True

    class Dog(Animal):
        breed = CharField(max_length=50)

    class Cat(Animal):
        indoor = BooleanField(default=True)

    # Single Table Inheritance
    class Vehicle(Model):
        model_name = CharField(max_length=100)
        year = IntegerField()

        class Meta:
            polymorphic_on = 'vehicle_type'
            polymorphic_identity = 'vehicle'

    class Car(Vehicle):
        num_doors = IntegerField()

        class Meta:
            polymorphic_identity = 'car'

    class Motorcycle(Vehicle):
        has_sidecar = BooleanField()

        class Meta:
            polymorphic_identity = 'motorcycle'

    # Multi-Table Inheritance
    class Person(Model):
        name = CharField(max_length=100)
        email = EmailField()

        class Meta:
            inheritance = 'multi_table'

    class Employee(Person):
        employee_id = CharField(max_length=20)
        department = CharField(max_length=50)

    class Customer(Person):
        customer_since = DateTimeField()
        loyalty_points = IntegerField(default=0)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type

if TYPE_CHECKING:
    from ..models import Model

logger = logging.getLogger(__name__)


class PolymorphicModelMixin:
    """
    Mixin for polymorphic model support.

    Handles type discrimination and query filtering for inherited models.
    """

    _polymorphic_on: Optional[str] = None
    _polymorphic_identity: Optional[str] = None
    _polymorphic_models: Dict[str, Type["Model"]] = {}
    _base_model: Optional[Type["Model"]] = None

    @classmethod
    def _get_polymorphic_discriminator(cls) -> Optional[str]:
        """Get discriminator field name for STI."""
        return getattr(cls._meta, "polymorphic_on", cls._polymorphic_on)

    @classmethod
    def _get_polymorphic_identity(cls) -> Optional[str]:
        """Get identity value for this model type."""
        return getattr(cls._meta, "polymorphic_identity", cls._polymorphic_identity)

    @classmethod
    def _register_polymorphic_model(cls, identity: str, model: Type["Model"]):
        """Register subclass for polymorphic queries."""
        if not hasattr(cls, "_polymorphic_models"):
            cls._polymorphic_models = {}
        cls._polymorphic_models[identity] = model

    @classmethod
    def _get_polymorphic_model(cls, identity: str) -> Optional[Type["Model"]]:
        """Get model class for identity value."""
        return cls._polymorphic_models.get(identity)

    @classmethod
    def _is_polymorphic_base(cls) -> bool:
        """Check if this is the polymorphic base model."""
        return cls._get_polymorphic_discriminator() is not None

    @classmethod
    def _get_base_model(cls) -> Type["Model"]:
        """Get the base model in inheritance chain."""
        if hasattr(cls, "_base_model") and cls._base_model:
            return cls._base_model

        # Walk up inheritance chain
        for base in cls.__mro__:
            if hasattr(base, "_is_polymorphic_base") and base._is_polymorphic_base():
                return base

        return cls


class SingleTableInheritance:
    """
    Single Table Inheritance (STI) implementation.

    All models in hierarchy share one table with a discriminator column.

    Advantages:
    - Simple schema
    - Fast queries (no joins)
    - Easy to query across types

    Disadvantages:
    - Sparse tables (many NULL values)
    - No per-type constraints
    - Table can become very wide
    """

    @staticmethod
    def setup_model(model: Type["Model"]):
        """Set up STI for a model."""
        discriminator = model._get_polymorphic_discriminator()
        identity = model._get_polymorphic_identity()

        if not discriminator:
            return

        # Add discriminator field if not exists
        if discriminator not in model._fields:
            from ..fields import CharField

            disc_field = CharField(max_length=50, nullable=False, db_index=True)
            disc_field.name = discriminator
            disc_field.db_column = discriminator
            disc_field.model = model
            model._fields[discriminator] = disc_field

        # Register this type
        if identity:
            base_model = model._get_base_model()
            base_model._register_polymorphic_model(identity, model)
            model._base_model = base_model

    @staticmethod
    def filter_query(model: Type["Model"], query: str, params: list) -> tuple:
        """
        Add discriminator filter to query.

        Returns:
            (modified_query, modified_params)
        """
        identity = model._get_polymorphic_identity()
        discriminator = model._get_polymorphic_discriminator()

        if not identity or not discriminator:
            return query, params

        # Add WHERE clause for discriminator
        if "WHERE" in query.upper():
            query = query.replace("WHERE", f"WHERE {discriminator} = ? AND", 1)
        else:
            # Add WHERE before ORDER BY or LIMIT
            if "ORDER BY" in query.upper():
                query = query.replace("ORDER BY", f"WHERE {discriminator} = ? ORDER BY", 1)
            elif "LIMIT" in query.upper():
                query = query.replace("LIMIT", f"WHERE {discriminator} = ? LIMIT", 1)
            else:
                query += f" WHERE {discriminator} = ?"

        # Add identity param at beginning
        params.insert(0, identity)

        return query, params

    @staticmethod
    def set_discriminator(instance: "Model"):
        """Set discriminator value on instance."""
        model = instance.__class__
        discriminator = model._get_polymorphic_discriminator()
        identity = model._get_polymorphic_identity()

        if discriminator and identity:
            setattr(instance, discriminator, identity)


class MultiTableInheritance:
    """
    Multi-Table Inheritance (MTI) implementation.

    Each model gets its own table. Child tables have FK to parent.

    Advantages:
    - Clean schema (no NULLs)
    - Per-type constraints possible
    - Type-specific indexing

    Disadvantages:
    - Requires joins for full object
    - More complex queries
    - More tables to manage
    """

    @staticmethod
    def setup_model(model: Type["Model"], parent: Type["Model"]):
        """
        Set up MTI for a model.

        Args:
            model: Child model
            parent: Parent model
        """
        # Add implicit FK to parent
        from ..relationships import CASCADE, ForeignKey

        parent_field_name = f"{parent.__name__.lower()}_ptr"

        if parent_field_name not in model._fields:
            parent_fk = ForeignKey(
                parent,
                on_delete=CASCADE,
                related_name=f"{model.__name__.lower()}_set",
                primary_key=True,  # Share PK with parent
                db_column=f"{parent_field_name}_id",
            )
            parent_fk.name = parent_field_name
            parent_fk.model = model
            parent_fk.contribute_to_class(model, parent_field_name)
            model._fields[parent_field_name] = parent_fk

        # Store parent reference
        model._mti_parent = parent

    @staticmethod
    async def save_instance(instance: "Model"):
        """
        Save MTI instance (saves to parent table first).

        Args:
            instance: Model instance to save
        """
        model = instance.__class__

        if not hasattr(model, "_mti_parent"):
            return

        parent_model = model._mti_parent
        parent_field_name = f"{parent_model.__name__.lower()}_ptr"

        # Create parent instance with parent fields
        parent_data = {}
        for field_name, field in parent_model._fields.items():
            if hasattr(instance, field_name):
                parent_data[field_name] = getattr(instance, field_name)

        # Check if parent already exists
        parent_pk_field = parent_model._meta.pk_field
        parent_pk = getattr(instance, parent_field_name + "_id", None)

        if parent_pk:
            # Update parent
            parent_instance = await parent_model.objects.get(id=parent_pk)
            for key, value in parent_data.items():
                setattr(parent_instance, key, value)
            await parent_instance.save()
        else:
            # Create parent
            parent_instance = parent_model(**parent_data)
            await parent_instance.save()

            # Set parent FK on child
            parent_pk = getattr(parent_instance, parent_pk_field.name)
            setattr(instance, parent_field_name + "_id", parent_pk)

    @staticmethod
    async def load_instance(instance: "Model"):
        """
        Load parent fields into MTI instance.

        Args:
            instance: Model instance to populate
        """
        model = instance.__class__

        if not hasattr(model, "_mti_parent"):
            return

        parent_model = model._mti_parent
        parent_field_name = f"{parent_model.__name__.lower()}_ptr"

        # Get parent ID
        parent_pk = getattr(instance, parent_field_name + "_id", None)
        if not parent_pk:
            return

        # Load parent
        try:
            parent = await parent_model.objects.get(id=parent_pk)

            # Copy parent fields to child
            for field_name, field in parent_model._fields.items():
                if field_name != parent_model._meta.pk_field.name:
                    value = getattr(parent, field_name, None)
                    setattr(instance, field_name, value)
        except Exception as e:
            logger.error(f"Error loading MTI parent: {e}")


class AbstractBaseClass:
    """
    Abstract Base Class implementation.

    Base model has no table. Each child has complete schema.

    Advantages:
    - No joins needed
    - Complete independence of child models
    - Simple and fast

    Disadvantages:
    - No way to query across types
    - Schema duplication
    - No polymorphic queries
    """

    @staticmethod
    def is_abstract(model: Type["Model"]) -> bool:
        """Check if model is abstract."""
        return getattr(model._meta, "abstract", False)

    @staticmethod
    def inherit_fields(child: Type["Model"], parent: Type["Model"]):
        """
        Copy fields from abstract parent to child.

        Args:
            child: Child model class
            parent: Abstract parent model class
        """
        # Copy fields that aren't overridden
        for field_name, field in parent._fields.items():
            if field_name not in child._fields:
                # Clone field
                import copy

                cloned_field = copy.deepcopy(field)
                cloned_field.model = child
                child._fields[field_name] = cloned_field


class ProxyModel:
    """
    Proxy Model implementation.

    Creates alternative interface to existing model without new table.

    Example:
        class Person(Model):
            name = CharField(max_length=100)
            age = IntegerField()

        class Adult(Person):
            class Meta:
                proxy = True

            @classmethod
            def get_adults(cls):
                return cls.objects.filter(age__gte=18)

        # Adult and Person share same table
        adults = await Adult.get_adults()
    """

    @staticmethod
    def is_proxy(model: Type["Model"]) -> bool:
        """Check if model is a proxy."""
        return getattr(model._meta, "proxy", False)

    @staticmethod
    def setup_proxy(proxy_model: Type["Model"], concrete_model: Type["Model"]):
        """
        Set up proxy model.

        Args:
            proxy_model: Proxy model class
            concrete_model: Concrete model being proxied
        """
        # Share table and fields
        proxy_model.__tablename__ = concrete_model.__tablename__
        proxy_model._fields = concrete_model._fields
        proxy_model._meta.db_table = concrete_model._meta.db_table

        # Store reference to concrete model
        proxy_model._concrete_model = concrete_model


def setup_polymorphic_model(model: Type["Model"]):
    """
    Set up polymorphic behavior for a model.

    Called by metaclass during model creation.

    Args:
        model: Model class to set up
    """
    meta = model._meta

    # Check for abstract
    if AbstractBaseClass.is_abstract(model):
        # Don't create table for abstract models
        return

    # Check for proxy
    if ProxyModel.is_proxy(model):
        # Find concrete model in parent chain
        for base in model.__mro__:
            if (
                hasattr(base, "__tablename__")
                and base.__tablename__
                and not ProxyModel.is_proxy(base)
            ):
                ProxyModel.setup_proxy(model, base)
                return
        raise ValueError(f"Proxy model {model.__name__} has no concrete parent")

    # Check inheritance type
    inheritance_type = getattr(meta, "inheritance", None)

    if inheritance_type == "multi_table":
        # Set up MTI
        for base in model.__mro__:
            if (
                hasattr(base, "__tablename__")
                and base.__tablename__
                and base != model
                and not AbstractBaseClass.is_abstract(base)
            ):
                MultiTableInheritance.setup_model(model, base)
                break

    elif hasattr(meta, "polymorphic_on"):
        # Set up STI
        SingleTableInheritance.setup_model(model)

    # Check for abstract parent (inherit fields)
    for base in model.__bases__:
        if hasattr(base, "_meta") and hasattr(base._meta, "abstract") and base._meta.abstract:
            AbstractBaseClass.inherit_fields(model, base)


class PolymorphicQuerySet:
    """
    Enhanced QuerySet for polymorphic queries.

    Automatically handles type discrimination and proper object instantiation.
    """

    @staticmethod
    def wrap_queryset(qs, model: Type["Model"]):
        """Wrap QuerySet with polymorphic behavior."""
        original_filter = qs.filter

        def polymorphic_filter(*args, **kwargs):
            result = original_filter(*args, **kwargs)
            # Add discriminator filter if STI
            identity = model._get_polymorphic_identity()
            discriminator = model._get_polymorphic_discriminator()

            if identity and discriminator:
                result = result.filter(**{discriminator: identity})

            return result

        qs.filter = polymorphic_filter
        return qs


__all__ = [
    "PolymorphicModelMixin",
    "SingleTableInheritance",
    "MultiTableInheritance",
    "AbstractBaseClass",
    "ProxyModel",
    "setup_polymorphic_model",
    "PolymorphicQuerySet",
]
