"""
Reverse Relation Optimization

Advanced reverse relation handling with:
- Efficient reverse ForeignKey access
- Reverse ManyToMany access
- Related name configuration
- Prefetch optimization
- Custom accessors
- Lazy loading with caching

Example:
    class Author(Model):
        name = CharField(max_length=100)

    class Book(Model):
        title = CharField(max_length=200)
        author = ForeignKey(Author, on_delete=CASCADE, related_name='books')

    # Reverse access
    author = await Author.objects.get(id=1)
    books = await author.books.all()  # Efficient reverse FK

    # Prefetch for N+1 prevention
    authors = await Author.objects.prefetch_related('books')
    for author in authors:
        # No additional queries
        books = await author.books.all()
"""

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type, Union

if TYPE_CHECKING:
    from ..models import Model

logger = logging.getLogger(__name__)


class ReverseRelationDescriptor:
    """
    Descriptor for reverse ForeignKey/OneToOne access.

    Provides lazy loading and caching for reverse relationships.
    """

    def __init__(
        self,
        related_model: Type["Model"],
        related_field: str,
        relation_type: str = "foreignkey",
        field: Optional[Any] = None,
    ):
        """
        Initialize reverse relation descriptor.

        Args:
            related_model: Model with the FK field
            related_field: Field name on related model
            relation_type: 'foreignkey' or 'onetoone'
            field: The forward field object
        """
        self.related_model = related_model
        self.related_field = related_field
        self.relation_type = relation_type
        self.field = field
        self.cache_name = f"_reverse_{related_field}_cache"

    def __get__(self, instance: Optional["Model"], owner: Type["Model"]) -> Any:
        """Get reverse relation."""
        if instance is None:
            return self

        # For OneToOne, return single instance
        if self.relation_type == "onetoone":
            return self._get_onetoone(instance)

        # For ForeignKey, return manager
        return ReverseRelationManager(
            instance=instance, related_model=self.related_model, related_field=self.related_field
        )

    def __set__(self, instance: "Model", value: Any) -> None:
        """Set is not allowed for reverse relations."""
        if self.relation_type == "onetoone":
            # OneToOne reverse can be set
            setattr(instance, self.cache_name, value)
        else:
            raise AttributeError(
                "Cannot directly assign to reverse ForeignKey relation. "
                "Use the manager methods (add, remove, etc.)"
            )

    def _get_onetoone(self, instance: "Model"):
        """Get OneToOne reverse instance (lazy loaded)."""
        # Check cache
        if hasattr(instance, self.cache_name):
            return getattr(instance, self.cache_name)

        # Return lazy loader
        return _LazyReverseOneToOne(
            instance, self.related_model, self.related_field, self.cache_name
        )


class _LazyReverseOneToOne:
    """Lazy loader for OneToOne reverse relation."""

    def __init__(
        self, instance: "Model", related_model: Type["Model"], related_field: str, cache_name: str
    ):
        self.instance = instance
        self.related_model = related_model
        self.related_field = related_field
        self.cache_name = cache_name

    def __await__(self):
        """Make awaitable."""
        return self._load().__await__()

    async def _load(self) -> Optional["Model"]:
        """Load the related instance."""
        # Check cache
        if hasattr(self.instance, self.cache_name):
            return getattr(self.instance, self.cache_name)

        try:
            pk_field = self.instance._meta.pk_field
            pk_value = getattr(self.instance, pk_field.name)

            # Query related model
            related = await self.related_model.objects.get(**{f"{self.related_field}_id": pk_value})

            setattr(self.instance, self.cache_name, related)
            return related

        except Exception as e:
            logger.debug(f"OneToOne reverse relation not found: {e}")
            setattr(self.instance, self.cache_name, None)
            return None


class ReverseRelationManager:
    """
    Manager for reverse ForeignKey relations.

    Provides QuerySet-like interface for accessing related objects.
    """

    def __init__(self, instance: "Model", related_model: Type["Model"], related_field: str):
        self.instance = instance
        self.related_model = related_model
        self.related_field = related_field

        # Check for prefetch
        self._prefetch_cache = None
        self._prefetch_done = False

    def get_queryset(self):
        """Get QuerySet for related objects."""
        from ..managers import QuerySet

        # Check prefetch cache
        if self._prefetch_done:
            qs = QuerySet(self.related_model)
            qs._result_cache = self._prefetch_cache or []
            qs._fetched = True
            return qs

        # Check instance-level prefetch
        cache_attr = f"_prefetched_{self._get_accessor_name()}"
        if hasattr(self.instance, cache_attr):
            qs = QuerySet(self.related_model)
            qs._result_cache = getattr(self.instance, cache_attr)
            qs._fetched = True
            return qs

        # Build filtered queryset
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        if pk_value is None:
            raise ValueError(
                f"Cannot access reverse relation on unsaved "
                f"{self.instance.__class__.__name__} instance"
            )

        return QuerySet(self.related_model).filter(**{f"{self.related_field}_id": pk_value})

    def _get_accessor_name(self) -> str:
        """Get accessor name for this reverse relation."""
        # Try to find related_name from field
        field = getattr(self.related_model, self.related_field, None)
        if hasattr(field, "field") and hasattr(field.field, "related_name"):
            return field.field.related_name or f"{self.related_model.__name__.lower()}_set"
        return f"{self.related_model.__name__.lower()}_set"

    def all(self):
        """Get all related objects."""
        return self.get_queryset()

    def filter(self, **kwargs):
        """Filter related objects."""
        return self.get_queryset().filter(**kwargs)

    def exclude(self, **kwargs):
        """Exclude related objects."""
        return self.get_queryset().exclude(**kwargs)

    async def count(self) -> int:
        """Count related objects."""
        if self._prefetch_done:
            return len(self._prefetch_cache or [])
        return await self.get_queryset().count()

    async def exists(self) -> bool:
        """Check if any related objects exist."""
        if self._prefetch_done:
            return len(self._prefetch_cache or []) > 0
        return await self.get_queryset().exists()

    async def first(self) -> Optional["Model"]:
        """Get first related object."""
        return await self.get_queryset().first()

    async def last(self) -> Optional["Model"]:
        """Get last related object."""
        return await self.get_queryset().last()

    async def create(self, **kwargs) -> "Model":
        """Create related object."""
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        # Set foreign key
        kwargs[f"{self.related_field}_id"] = pk_value

        obj = self.related_model(**kwargs)
        await obj.save()
        return obj

    async def get_or_create(self, defaults=None, **kwargs) -> tuple:
        """Get or create related object."""
        pk_field = self.instance._meta.pk_field
        pk_value = getattr(self.instance, pk_field.name)

        # Add FK to lookup
        kwargs[f"{self.related_field}_id"] = pk_value

        return await self.related_model.objects.get_or_create(defaults=defaults, **kwargs)

    async def update(self, **kwargs) -> int:
        """Update all related objects."""
        return await self.get_queryset().update(**kwargs)

    async def delete(self) -> int:
        """Delete all related objects."""
        return await self.get_queryset().delete()

    def _set_prefetch_cache(self, objects: List["Model"]):
        """Set prefetched objects cache."""
        self._prefetch_cache = objects
        self._prefetch_done = True


class PrefetchOptimizer:
    """
    Optimizer for prefetching reverse relations.

    Prevents N+1 query problems by bulk loading related objects.
    """

    @staticmethod
    async def prefetch_reverse_fk(
        instances: List["Model"],
        accessor_name: str,
        related_model: Type["Model"],
        related_field: str,
    ):
        """
        Prefetch reverse ForeignKey relation.

        Args:
            instances: List of parent instances
            accessor_name: Name of reverse accessor
            related_model: Related model class
            related_field: Field name on related model

        Example:
            authors = await Author.objects.all()
            await PrefetchOptimizer.prefetch_reverse_fk(
                authors, 'books', Book, 'author'
            )
        """
        if not instances:
            return

        # Collect parent PKs
        parent_model = instances[0].__class__
        pk_field = parent_model._meta.pk_field
        parent_pks = [getattr(inst, pk_field.name) for inst in instances]

        # Bulk fetch related objects
        related_objects = await related_model.objects.filter(
            **{f"{related_field}_id__in": parent_pks}
        )

        # Group by parent PK
        grouped: Dict[Any, List["Model"]] = defaultdict(list)
        for obj in related_objects:
            parent_pk = getattr(obj, f"{related_field}_id")
            grouped[parent_pk].append(obj)

        # Set cache on each instance
        for instance in instances:
            pk_value = getattr(instance, pk_field.name)
            related = grouped.get(pk_value, [])

            # Cache on accessor
            cache_attr = f"_prefetched_{accessor_name}"
            setattr(instance, cache_attr, related)

    @staticmethod
    async def prefetch_reverse_m2m(instances: List["Model"], accessor_name: str, field):
        """
        Prefetch reverse ManyToMany relation.

        Args:
            instances: List of parent instances
            accessor_name: Name of reverse accessor
            field: ManyToManyField object
        """
        if not instances:
            return

        parent_model = instances[0].__class__
        pk_field = parent_model._meta.pk_field
        parent_pks = [getattr(inst, pk_field.name) for inst in instances]

        # Get through model info
        through_model = field.get_through_model()
        source_field = f"{parent_model.__name__.lower()}_id"
        target_field = f"{field.model.__name__.lower()}_id"

        # Fetch through relationships
        adapter = await instances[0]._get_adapter()
        query = f"""  # nosec B608 - table_name validated in config
            SELECT {source_field}, {target_field}
            FROM {through_model.__tablename__}
            WHERE {source_field} = ANY($1)
        """

        # Execute query (placeholder syntax depends on adapter)
        rows = await adapter.fetch_all(query, [parent_pks])

        # Group target IDs by source ID
        grouped: Dict[Any, List[Any]] = defaultdict(list)
        for row in rows:
            source_pk = row[source_field]
            target_pk = row[target_field]
            grouped[source_pk].append(target_pk)

        # Fetch all target objects
        all_target_pks = [pk for pks in grouped.values() for pk in pks]
        if all_target_pks:
            target_objects = await field.model.objects.filter(id__in=all_target_pks)

            # Build lookup dict
            target_dict = {getattr(obj, obj._meta.pk_field.name): obj for obj in target_objects}

            # Set cache on each instance
            for instance in instances:
                pk_value = getattr(instance, pk_field.name)
                target_pks = grouped.get(pk_value, [])
                related = [target_dict[pk] for pk in target_pks if pk in target_dict]

                cache_attr = f"_prefetched_{accessor_name}"
                setattr(instance, cache_attr, related)


class RelatedNameResolver:
    """
    Resolves related_name conflicts and generates unique names.

    Handles:
    - Automatic related_name generation
    - Conflict detection
    - +suffix for disabling reverse relation
    """

    _used_names: Dict[Type["Model"], Set[str]] = defaultdict(set)

    @classmethod
    def resolve_related_name(
        cls,
        source_model: Type["Model"],
        target_model: Type["Model"],
        field_name: str,
        related_name: Optional[str] = None,
    ) -> Optional[str]:
        """
        Resolve related_name for a relationship field.

        Args:
            source_model: Model containing the field
            target_model: Model being referenced
            field_name: Name of the relationship field
            related_name: Explicitly provided related_name

        Returns:
            Resolved related_name or None if disabled
        """
        # Check for + suffix (disables reverse relation)
        if related_name and related_name.endswith("+"):
            return None

        # Use explicit related_name if provided
        if related_name:
            name = related_name
        else:
            # Auto-generate: <model>_set
            name = f"{source_model.__name__.lower()}_set"

        # Check for conflicts
        if name in cls._used_names[target_model]:
            # Add suffix to make unique
            counter = 1
            while f"{name}_{counter}" in cls._used_names[target_model]:
                counter += 1
            name = f"{name}_{counter}"

        # Register name
        cls._used_names[target_model].add(name)

        return name


class RelatedObjectDescriptor:
    """
    Descriptor for accessing related objects with smart caching.

    Provides transparent access to related objects with automatic
    lazy loading and prefetch support.
    """

    def __init__(self, related_manager_class, **kwargs):
        self.related_manager_class = related_manager_class
        self.kwargs = kwargs

    def __get__(self, instance, owner):
        if instance is None:
            return self

        return self.related_manager_class(instance=instance, **self.kwargs)


__all__ = [
    "ReverseRelationDescriptor",
    "ReverseRelationManager",
    "PrefetchOptimizer",
    "RelatedNameResolver",
    "RelatedObjectDescriptor",
]
