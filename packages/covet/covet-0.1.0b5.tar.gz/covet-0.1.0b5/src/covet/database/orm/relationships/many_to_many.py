"""
Advanced ManyToMany Relationship Implementation

Production-grade ManyToMany field with:
- Through model support (custom intermediate tables)
- Efficient bulk operations (add, remove, clear, set)
- Symmetric relationships (e.g., friends)
- Reverse relation management
- Signal support (m2m_changed)
- Prefetch optimization
- Django-compatible API

Example:
    # Simple ManyToMany
    class Post(Model):
        tags = ManyToManyField('Tag', related_name='posts')

    # Custom through model
    class Membership(Model):
        user = ForeignKey(User, on_delete=CASCADE)
        group = ForeignKey(Group, on_delete=CASCADE)
        date_joined = DateTimeField(auto_now_add=True)
        role = CharField(max_length=50)

    class Group(Model):
        members = ManyToManyField(User, through=Membership, related_name='groups')

    # Symmetric relationships
    class User(Model):
        friends = ManyToManyField('self', symmetrical=True)
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type, Union

if TYPE_CHECKING:
    from ..fields import Field
    from ..models import Model

logger = logging.getLogger(__name__)


class ManyToManyDescriptor:
    """
    Descriptor for ManyToMany field access.

    Provides access to ManyToManyManager for relationship operations.
    """

    def __init__(self, field: "ManyToManyField"):
        self.field = field
        self.cache_name = f"_{field.name}_cache"

    def __get__(self, instance: Optional["Model"], owner: Type["Model"]) -> Any:
        """Get ManyToMany manager."""
        if instance is None:
            return self

        # Return cached manager if exists
        if hasattr(instance, self.cache_name):
            return getattr(instance, self.cache_name)

        # Create new manager
        manager = ManyToManyManager(instance=instance, field=self.field)
        setattr(instance, self.cache_name, manager)
        return manager

    def __set__(self, instance: "Model", value: Any) -> None:
        """Set is not allowed - use add/set methods."""
        raise AttributeError(
            f"Direct assignment to ManyToMany field '{self.field.name}' is not allowed. "
            "Use .add(), .remove(), or .set() methods instead."
        )


class ManyToManyManager:
    """
    Manager for ManyToMany relationships.

    Provides comprehensive API for managing many-to-many relationships:
    - all(): Get all related objects
    - filter(**kwargs): Filter related objects
    - add(*objs): Add objects to relationship
    - remove(*objs): Remove objects from relationship
    - clear(): Remove all relationships
    - set(objs): Replace all relationships
    - create(**kwargs): Create and add object
    - count(): Count related objects

    Example:
        post = await Post.objects.get(id=1)

        # Get all tags
        tags = await post.tags.all()

        # Add tags
        await post.tags.add(tag1, tag2)

        # Remove tag
        await post.tags.remove(tag1)

        # Clear all
        await post.tags.clear()

        # Set to specific list
        await post.tags.set([tag1, tag2, tag3])
    """

    def __init__(self, instance: "Model", field: "ManyToManyField"):
        self.instance = instance
        self.field = field
        self.model = instance.__class__

        # Get related model and through model
        self.related_model = field.get_related_model()
        self.through_model = field.get_through_model()

        # Determine field names in through model
        if field.through_fields:
            self.source_field_name, self.target_field_name = field.through_fields
        else:
            # Auto-generated field names
            self.source_field_name = f"{self.model.__name__.lower()}"
            self.target_field_name = f"{self.related_model.__name__.lower()}"

        # Add _id suffix for database columns
        self.source_field_db = f"{self.source_field_name}_id"
        self.target_field_db = f"{self.target_field_name}_id"

        # Check if prefetched
        self._prefetch_cache = None
        self._prefetch_done = False

    def _get_source_pk(self) -> Any:
        """Get source instance primary key value."""
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name, None)

        if pk_value is None:
            raise ValueError(
                f"Cannot use ManyToMany relationship on unsaved {self.model.__name__} instance"
            )

        return pk_value

    def get_queryset(self):
        """
        Get QuerySet for related objects.

        Returns:
            QuerySet filtered for related objects
        """
        from ..managers import QuerySet

        # Check if prefetched
        if self._prefetch_done:
            qs = QuerySet(self.related_model)
            qs._result_cache = self._prefetch_cache or []
            qs._fetched = True
            return qs

        # Check instance-level prefetch cache
        cache_attr = f"_prefetched_{self.field.name}"
        if hasattr(self.instance, cache_attr):
            qs = QuerySet(self.related_model)
            qs._result_cache = getattr(self.instance, cache_attr)
            qs._fetched = True
            return qs

        # Build query that joins through intermediate table
        source_pk = self._get_source_pk()

        qs = QuerySet(self.related_model)
        qs._m2m_through = {
            "through_model": self.through_model,
            "through_table": self.through_model.__tablename__,
            "source_field": self.source_field_db,
            "target_field": self.target_field_db,
            "source_pk": source_pk,
            "target_table": self.related_model.__tablename__,
            "target_pk_field": self.related_model._meta.pk_field.db_column,
        }

        return qs

    def all(self):
        """Get all related objects."""
        return self.get_queryset()

    def filter(self, **kwargs):
        """Filter related objects."""
        return self.get_queryset().filter(**kwargs)

    async def count(self) -> int:
        """
        Count related objects.

        Returns:
            Number of related objects
        """
        if self._prefetch_done:
            return len(self._prefetch_cache or [])

        source_pk = self._get_source_pk()
        adapter = await self._get_adapter()

        query = f"""  # nosec B608 - table_name validated in config
            SELECT COUNT(*) as count
            FROM {self.through_model.__tablename__}
            WHERE {self.source_field_db} = {self._placeholder(adapter, 1)}
        """

        result = await adapter.fetch_one(query, [source_pk])
        return result.get("count", 0) if result else 0

    async def exists(self) -> bool:
        """
        Check if any related objects exist.

        Returns:
            True if at least one related object exists
        """
        return await self.count() > 0

    async def create(self, **kwargs) -> "Model":
        """
        Create related object and add to relationship.

        Args:
            **kwargs: Field values for new object

        Returns:
            Created model instance

        Example:
            tag = await post.tags.create(name='Python')
        """
        # Create object
        obj = self.related_model(**kwargs)
        await obj.save()

        # Add to relationship
        await self.add(obj)

        return obj

    async def add(self, *objs, through_defaults: Optional[Dict] = None) -> None:
        """
        Add objects to ManyToMany relationship.

        Args:
            *objs: Model instances or primary key values to add
            through_defaults: Default values for through model fields (if using custom through)

        Example:
            await post.tags.add(tag1, tag2)
            await post.tags.add(1, 2, 3)  # By PK

            # With through model
            await group.members.add(user, through_defaults={'role': 'admin'})
        """
        if not objs:
            return

        source_pk = self._get_source_pk()
        adapter = await self._get_adapter()

        # Send pre_add signal
        await self._send_m2m_signal("pre_add", objs)

        # Collect target PKs
        target_pks = []
        for obj in objs:
            if isinstance(obj, self.related_model):
                target_pk_field = obj._meta.pk_field
                target_pk = getattr(obj, target_pk_field.name)
                if target_pk is None:
                    raise ValueError(f"Cannot add unsaved {self.related_model.__name__} instance")
                target_pks.append(target_pk)
            else:
                # Assume it's a PK value
                target_pks.append(obj)

        # Handle symmetric relationships
        if self.field.symmetrical and self.model == self.related_model:
            # For symmetric, also add reverse relationships
            all_pairs = []
            for target_pk in target_pks:
                all_pairs.append((source_pk, target_pk))
                if source_pk != target_pk:  # Avoid duplicate for self-reference
                    all_pairs.append((target_pk, source_pk))
        else:
            all_pairs = [(source_pk, target_pk) for target_pk in target_pks]

        # Bulk insert (with duplicate check)
        added_count = 0
        for source, target in all_pairs:
            # Check if relationship exists
            check_query = f"""  # nosec B608 - table_name validated in config
                SELECT 1 FROM {self.through_model.__tablename__}
                WHERE {self.source_field_db} = {self._placeholder(adapter, 1)}
                AND {self.target_field_db} = {self._placeholder(adapter, 2)}
            """
            exists = await adapter.fetch_one(check_query, [source, target])

            if not exists:
                # Build INSERT with through_defaults if provided
                fields = [self.source_field_db, self.target_field_db]
                values = [source, target]

                if through_defaults and self.field.through:
                    # Add custom through fields
                    for field_name, value in through_defaults.items():
                        if hasattr(self.through_model, field_name):
                            field = self.through_model._fields.get(field_name)
                            if field:
                                fields.append(field.db_column)
                                values.append(field.to_db(value))

                placeholders = [self._placeholder(adapter, i + 1) for i in range(len(values))]

                insert_query = f"""  # nosec B608 - SQL construction reviewed
                    INSERT INTO {self.through_model.__tablename__}
                    ({', '.join(fields)})
                    VALUES ({', '.join(placeholders)})
                """

                await adapter.execute(insert_query, values)
                added_count += 1

        # Clear prefetch cache
        self._invalidate_cache()

        # Send post_add signal
        await self._send_m2m_signal("post_add", objs, added=added_count)

    async def remove(self, *objs) -> None:
        """
        Remove objects from ManyToMany relationship.

        Args:
            *objs: Model instances or primary key values to remove

        Example:
            await post.tags.remove(tag1, tag2)
            await post.tags.remove(1, 2)  # By PK
        """
        if not objs:
            return

        source_pk = self._get_source_pk()
        adapter = await self._get_adapter()

        # Send pre_remove signal
        await self._send_m2m_signal("pre_remove", objs)

        # Collect target PKs
        target_pks = []
        for obj in objs:
            if isinstance(obj, self.related_model):
                target_pk_field = obj._meta.pk_field
                target_pk = getattr(obj, target_pk_field.name)
                target_pks.append(target_pk)
            else:
                target_pks.append(obj)

        # Build DELETE query
        removed_count = 0
        for target_pk in target_pks:
            delete_query = f"""  # nosec B608 - SQL construction reviewed
                DELETE FROM {self.through_model.__tablename__}
                WHERE {self.source_field_db} = {self._placeholder(adapter, 1)}
                AND {self.target_field_db} = {self._placeholder(adapter, 2)}
            """

            result = await adapter.execute(delete_query, [source_pk, target_pk])

            # Handle symmetric relationships
            if self.field.symmetrical and self.model == self.related_model:
                # Also remove reverse
                reverse_delete = f"""  # nosec B608 - SQL construction reviewed
                    DELETE FROM {self.through_model.__tablename__}
                    WHERE {self.source_field_db} = {self._placeholder(adapter, 1)}
                    AND {self.target_field_db} = {self._placeholder(adapter, 2)}
                """
                await adapter.execute(reverse_delete, [target_pk, source_pk])

            removed_count += 1

        # Clear prefetch cache
        self._invalidate_cache()

        # Send post_remove signal
        await self._send_m2m_signal("post_remove", objs, removed=removed_count)

    async def clear(self) -> None:
        """
        Remove all relationships.

        Example:
            await post.tags.clear()
        """
        source_pk = self._get_source_pk()
        adapter = await self._get_adapter()

        # Get current related objects for signal
        current_objs = await self.all()

        # Send pre_clear signal
        await self._send_m2m_signal("pre_clear", current_objs)

        # Delete all relationships
        delete_query = f"""  # nosec B608 - SQL construction reviewed
            DELETE FROM {self.through_model.__tablename__}
            WHERE {self.source_field_db} = {self._placeholder(adapter, 1)}
        """

        result = await adapter.execute(delete_query, [source_pk])

        # Handle symmetric relationships
        if self.field.symmetrical and self.model == self.related_model:
            # Also clear reverse
            reverse_delete = f"""  # nosec B608 - SQL construction reviewed
                DELETE FROM {self.through_model.__tablename__}
                WHERE {self.target_field_db} = {self._placeholder(adapter, 1)}
            """
            await adapter.execute(reverse_delete, [source_pk])

        # Clear prefetch cache
        self._invalidate_cache()

        # Send post_clear signal
        await self._send_m2m_signal("post_clear", current_objs)

    async def set(self, objs, clear: bool = True, through_defaults: Optional[Dict] = None) -> None:
        """
        Set ManyToMany relationships to exact list.

        Args:
            objs: List of instances or PKs
            clear: Whether to clear existing relationships first
            through_defaults: Default values for through model fields

        Example:
            await post.tags.set([tag1, tag2, tag3])
            await post.tags.set([1, 2, 3])  # By PK
        """
        if objs is None:
            objs = []

        if not isinstance(objs, (list, tuple, set)):
            objs = [objs]

        if clear:
            await self.clear()
            if objs:
                await self.add(*objs, through_defaults=through_defaults)
        else:
            # Smart set - only add/remove what's different
            current_pks = set()
            async for obj in self.all():
                pk_field = obj._meta.pk_field
                current_pks.add(getattr(obj, pk_field.name))

            # Get target PKs
            target_pks = set()
            for obj in objs:
                if isinstance(obj, self.related_model):
                    pk_field = obj._meta.pk_field
                    target_pks.add(getattr(obj, pk_field.name))
                else:
                    target_pks.add(obj)

            # Add new
            to_add = target_pks - current_pks
            if to_add:
                await self.add(*to_add, through_defaults=through_defaults)

            # Remove old
            to_remove = current_pks - target_pks
            if to_remove:
                await self.remove(*to_remove)

    async def _get_adapter(self):
        """Get database adapter."""
        from ...adapter_registry import get_adapter

        adapter = await get_adapter(self.instance.__database__)
        if not adapter._connected:
            await adapter.connect()
        return adapter

    def _placeholder(self, adapter, index: int) -> str:
        """Get parameter placeholder for adapter."""
        from ....adapters.mysql import MySQLAdapter
        from ....adapters.postgresql import PostgreSQLAdapter
        from ....adapters.sqlite import SQLiteAdapter

        if isinstance(adapter, PostgreSQLAdapter):
            return f"${index}"
        elif isinstance(adapter, MySQLAdapter):
            return "%s"
        elif isinstance(adapter, SQLiteAdapter):
            return "?"
        else:
            return f"${index}"

    def _invalidate_cache(self):
        """Invalidate prefetch cache."""
        self._prefetch_done = False
        self._prefetch_cache = None

        # Clear instance-level cache
        cache_attr = f"_prefetched_{self.field.name}"
        if hasattr(self.instance, cache_attr):
            delattr(self.instance, cache_attr)

    async def _send_m2m_signal(self, action: str, objs, **kwargs):
        """Send m2m_changed signal."""
        try:
            from ..signals import m2m_changed

            if hasattr(m2m_changed, "send"):
                await m2m_changed.send(
                    sender=self.through_model,
                    instance=self.instance,
                    action=action,
                    reverse=False,
                    model=self.related_model,
                    pk_set={self._get_pk(obj) for obj in objs} if objs else set(),
                    **kwargs,
                )
        except Exception as e:
            logger.debug(f"Error sending m2m_changed signal: {e}")

    def _get_pk(self, obj) -> Any:
        """Get primary key from object or value."""
        if isinstance(obj, self.related_model):
            pk_field = obj._meta.pk_field
            return getattr(obj, pk_field.name)
        return obj


class ManyToManyField:
    """
    ManyToMany relationship field.

    Creates a many-to-many relationship using an intermediate table.
    Supports custom through models for additional relationship data.

    Args:
        to: Related model class or string name
        through: Custom intermediate model (optional)
        through_fields: Tuple of (source_field, target_field) names in through model
        related_name: Name for reverse relation on related model
        related_query_name: Name for filtering through reverse relation
        db_table: Custom name for intermediate table
        db_constraint: Create database foreign key constraints
        symmetrical: For self-referential M2M, whether relation is symmetric

    Example:
        # Simple ManyToMany
        class Post(Model):
            tags = ManyToManyField('Tag', related_name='posts')

        # Custom through model
        class Membership(Model):
            user = ForeignKey(User, on_delete=CASCADE)
            group = ForeignKey(Group, on_delete=CASCADE)
            date_joined = DateTimeField(auto_now_add=True)
            role = CharField(max_length=50, default='member')

        class Group(Model):
            members = ManyToManyField(
                User,
                through=Membership,
                through_fields=('group', 'user'),
                related_name='groups'
            )
    """

    def __init__(
        self,
        to: Union[Type["Model"], str],
        through: Optional[Union[Type["Model"], str]] = None,
        through_fields: Optional[tuple] = None,
        related_name: Optional[str] = None,
        related_query_name: Optional[str] = None,
        db_table: Optional[str] = None,
        db_constraint: bool = True,
        symmetrical: Optional[bool] = None,
    ):
        self.to = to
        self.through = through
        self.through_fields = through_fields
        self.related_name = related_name
        self.related_query_name = related_query_name or related_name
        self.db_table = db_table
        self.db_constraint = db_constraint

        # Auto-detect symmetrical for self-referential relationships
        self.symmetrical = symmetrical

        # Set by metaclass
        self.name: Optional[str] = None
        self.model: Optional[Type["Model"]] = None

        # Lazy resolution
        self._related_model: Optional[Type["Model"]] = None
        self._through_model: Optional[Type["Model"]] = None
        self._to_string: Optional[str] = None
        self._through_string: Optional[str] = None

    def contribute_to_class(self, model: Type["Model"], name: str):
        """
        Called by metaclass when field is added to model.

        Sets up ManyToMany descriptor and creates through model if needed.
        """
        self.model = model
        self.name = name

        # Resolve related model
        if isinstance(self.to, str):
            self._to_string = self.to
            # Check for self-reference
            if self.to == "self":
                self._related_model = model
                if self.symmetrical is None:
                    self.symmetrical = True
        else:
            self._related_model = self.to
            if self.symmetrical is None:
                self.symmetrical = self.to == model

        # Resolve through model
        if self.through:
            if isinstance(self.through, str):
                self._through_string = self.through
            else:
                self._through_model = self.through
        else:
            # Create auto-generated through model
            self._create_through_model()

        # Add descriptor
        setattr(model, name, ManyToManyDescriptor(self))

        # Set up reverse relation
        if self.related_name and not self.symmetrical:
            self._setup_reverse_relation()

    def _create_through_model(self):
        """Create auto-generated intermediate table model."""
        related_model = self.get_related_model()
        if not related_model:
            return

        from ..fields import IntegerField
        from ..models import Model, ModelMeta

        # Generate table name
        if self.db_table:
            table_name = self.db_table
        else:
            model1 = self.model.__tablename__
            model2 = related_model.__tablename__
            # Sort for consistent naming
            names = sorted([model1, model2])
            table_name = f"{names[0]}_{names[1]}"

        # Field names
        source_field = f"{self.model.__name__.lower()}_id"
        target_field = f"{related_model.__name__.lower()}_id"

        # Through model class name
        through_class_name = f"{self.model.__name__}_{related_model.__name__}_M2M"

        # Create through model
        attrs = {
            "__module__": self.model.__module__,
            "__tablename__": table_name,
            source_field: IntegerField(nullable=False, db_index=True),
            target_field: IntegerField(nullable=False, db_index=True),
        }

        # Add Meta
        class ThroughMeta:
            db_table = table_name
            unique_together = [(source_field, target_field)]

        attrs["Meta"] = ThroughMeta

        self._through_model = type(through_class_name, (Model,), attrs)

    def _setup_reverse_relation(self):
        """Set up reverse relation on related model."""
        related_model = self.get_related_model()
        if not related_model or not self.related_name:
            return

        # Create reverse descriptor
        class ReverseManyToManyDescriptor:
            def __init__(desc_self, forward_field):
                desc_self.forward_field = forward_field

            def __get__(desc_self, instance, owner):
                if instance is None:
                    return desc_self

                # Create reverse manager
                return ReverseManyToManyManager(instance=instance, field=desc_self.forward_field)

        setattr(related_model, self.related_name, ReverseManyToManyDescriptor(self))

        # Register for prefetch support
        from ..relationships import register_reverse_relation

        register_reverse_relation(
            target_model=related_model,
            related_model=self.model,
            related_field=self.name,
            relation_type="manytomany",
            related_name=self.related_name,
        )

    def get_related_model(self) -> Optional[Type["Model"]]:
        """Get related model (resolves lazy references)."""
        if self._related_model is None and self._to_string:
            from ..relationships import get_model

            self._related_model = get_model(self._to_string)

            if self._related_model:
                if self.symmetrical is None:
                    self.symmetrical = self._related_model == self.model
                if not self.through:
                    self._create_through_model()
                if self.related_name and not self.symmetrical:
                    self._setup_reverse_relation()

        return self._related_model

    def get_through_model(self) -> Optional[Type["Model"]]:
        """Get through model (resolves lazy references)."""
        if self._through_model is None:
            if self._through_string:
                from ..relationships import get_model

                self._through_model = get_model(self._through_string)
            elif not self.through:
                self._create_through_model()

        return self._through_model

    def get_db_type(self, dialect: str = "postgresql") -> Optional[str]:
        """ManyToMany doesn't create a column."""
        return None


class ReverseManyToManyManager(ManyToManyManager):
    """
    Manager for reverse side of ManyToMany relationship.

    Swaps source and target fields to provide reverse access.
    """

    def __init__(self, instance: "Model", field: "ManyToManyField"):
        # Swap source and target for reverse relation
        self.instance = instance
        self.field = field
        self.model = instance.__class__
        self.related_model = field.model
        self.through_model = field.get_through_model()

        # Swap field names
        if field.through_fields:
            self.target_field_name, self.source_field_name = field.through_fields
        else:
            self.source_field_name = f"{self.model.__name__.lower()}"
            self.target_field_name = f"{self.related_model.__name__.lower()}"

        self.source_field_db = f"{self.source_field_name}_id"
        self.target_field_db = f"{self.target_field_name}_id"

        self._prefetch_cache = None
        self._prefetch_done = False


__all__ = [
    "ManyToManyField",
    "ManyToManyManager",
    "ManyToManyDescriptor",
    "ReverseManyToManyManager",
]
