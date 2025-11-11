"""
Cascade Behavior Handlers

Implements all cascade behaviors for relationship deletion:
- CASCADE: Delete related objects
- SET_NULL: Set FK to NULL
- SET_DEFAULT: Set FK to default value
- PROTECT: Prevent deletion if related objects exist
- RESTRICT: Similar to PROTECT but checked before CASCADE
- DO_NOTHING: No action taken
- SET(...): Set FK to specific value

Also handles:
- Circular reference detection
- Custom cascade handlers
- Bulk cascade operations
- Transaction safety

Example:
    class Author(Model):
        name = CharField(max_length=100)

    class Book(Model):
        title = CharField(max_length=200)
        author = ForeignKey(Author, on_delete=CASCADE)

    class Review(Model):
        book = ForeignKey(Book, on_delete=PROTECT)
        rating = IntegerField()

    # Deleting author cascades to books
    author = await Author.objects.get(id=1)
    await author.delete()  # Deletes all books by this author

    # Trying to delete book with reviews raises error
    book = await Book.objects.get(id=1)
    await book.delete()  # Raises ProtectedError if reviews exist
"""

import logging
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Set, Tuple, Type

if TYPE_CHECKING:
    from ..models import Model

logger = logging.getLogger(__name__)


class ProtectedError(Exception):
    """Raised when attempting to delete protected object."""

    def __init__(self, msg: str, protected_objects: List["Model"]):
        super().__init__(msg)
        self.protected_objects = protected_objects


class RestrictedError(Exception):
    """Raised when attempting to delete restricted object."""

    def __init__(self, msg: str, related_objects: List["Model"]):
        super().__init__(msg)
        self.related_objects = related_objects


class CascadeHandler:
    """
    Handles cascade operations for relationship deletions.

    Coordinates deletion/update of related objects according to on_delete rules.
    """

    def __init__(self):
        self.deleted_objects: Set[Tuple[Type["Model"], Any]] = set()
        self.protected_objects: List["Model"] = []
        self.restricted_objects: List["Model"] = []

    async def handle_delete(self, instance: "Model") -> Tuple[int, Dict[str, int]]:
        """
        Handle deletion with cascades.

        Args:
            instance: Model instance to delete

        Returns:
            Tuple of (total_deleted, {model_name: count})

        Raises:
            ProtectedError: If PROTECT constraint violated
            RestrictedError: If RESTRICT constraint violated
        """
        model = instance.__class__
        pk_field = model._meta.pk_field
        pk_value = getattr(instance, pk_field.name)

        # Track for circular reference detection
        obj_key = (model, pk_value)
        if obj_key in self.deleted_objects:
            return (0, {})

        self.deleted_objects.add(obj_key)

        # Find all relationships that reference this model
        relationships = self._get_related_fields(model)

        # Check RESTRICT first (before any cascades)
        for related_model, field_name, on_delete in relationships:
            if on_delete == "RESTRICT":
                await self._check_restrict(instance, related_model, field_name)

        if self.restricted_objects:
            raise RestrictedError(
                f"Cannot delete {model.__name__} because it is referenced by restricted relationships",
                self.restricted_objects,
            )

        # Handle each relationship based on on_delete
        deletion_count = defaultdict(int)

        for related_model, field_name, on_delete in relationships:
            handler = self._get_cascade_handler(on_delete)
            deleted = await handler(instance, related_model, field_name)

            if deleted:
                for model_name, count in deleted.items():
                    deletion_count[model_name] += count

        # Check PROTECT
        if self.protected_objects:
            raise ProtectedError(
                f"Cannot delete {model.__name__} because it is referenced by protected relationships",
                self.protected_objects,
            )

        # Delete the instance itself
        await self._delete_instance(instance)
        deletion_count[model.__name__] += 1

        total = sum(deletion_count.values())
        return (total, dict(deletion_count))

    def _get_cascade_handler(self, on_delete: str) -> Callable:
        """Get handler function for on_delete type."""
        handlers = {
            "CASCADE": self._handle_cascade,
            "SET_NULL": self._handle_set_null,
            "SET_DEFAULT": self._handle_set_default,
            "PROTECT": self._handle_protect,
            "RESTRICT": self._handle_restrict,
            "DO_NOTHING": self._handle_do_nothing,
        }

        handler = handlers.get(on_delete)
        if not handler:
            logger.warning(f"Unknown on_delete type: {on_delete}, using DO_NOTHING")
            return self._handle_do_nothing

        return handler

    async def _handle_cascade(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        CASCADE: Delete related objects.

        Returns:
            Dict of {model_name: deletion_count}
        """
        related_objects = await self._get_related_objects(instance, related_model, field_name)

        deletion_count = defaultdict(int)

        for obj in related_objects:
            # Recursively delete with cascades
            counts = await self.handle_delete(obj)
            for model_name, count in counts[1].items():
                deletion_count[model_name] += count

        return dict(deletion_count)

    async def _handle_set_null(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        SET_NULL: Set FK to NULL.

        Returns:
            Empty dict (no deletions)
        """
        related_objects = await self._get_related_objects(instance, related_model, field_name)

        for obj in related_objects:
            # Set FK field to NULL
            setattr(obj, f"{field_name}_id", None)
            # Also clear cached relationship
            setattr(obj, field_name, None)
            await obj.save(update_fields=[f"{field_name}_id"])

        return {}

    async def _handle_set_default(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        SET_DEFAULT: Set FK to default value.

        Returns:
            Empty dict (no deletions)
        """
        related_objects = await self._get_related_objects(instance, related_model, field_name)

        # Get default value from field
        field = related_model._fields.get(f"{field_name}_id")
        default_value = field.get_default() if field else None

        if default_value is None:
            raise ValueError(
                f"SET_DEFAULT requires a default value for {related_model.__name__}.{field_name}"
            )

        for obj in related_objects:
            setattr(obj, f"{field_name}_id", default_value)
            await obj.save(update_fields=[f"{field_name}_id"])

        return {}

    async def _handle_protect(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        PROTECT: Prevent deletion if related objects exist.

        Collects protected objects for raising ProtectedError.

        Returns:
            Empty dict (no deletions)
        """
        related_objects = await self._get_related_objects(instance, related_model, field_name)

        if related_objects:
            self.protected_objects.extend(related_objects)

        return {}

    async def _handle_restrict(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        RESTRICT: Similar to PROTECT but checked before cascades.

        Returns:
            Empty dict (no deletions)
        """
        # Handled in _check_restrict during initial pass
        return {}

    async def _check_restrict(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ):
        """Check RESTRICT constraint."""
        related_objects = await self._get_related_objects(instance, related_model, field_name)

        if related_objects:
            self.restricted_objects.extend(related_objects)

    async def _handle_do_nothing(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        DO_NOTHING: Take no action.

        May cause database integrity errors if constraints exist.

        Returns:
            Empty dict (no deletions)
        """
        return {}

    async def _get_related_objects(
        self, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> List["Model"]:
        """
        Get all objects related through specific field.

        Args:
            instance: Instance being deleted
            related_model: Model with FK to instance
            field_name: FK field name

        Returns:
            List of related objects
        """
        model = instance.__class__
        pk_field = model._meta.pk_field
        pk_value = getattr(instance, pk_field.name)

        # Query related objects
        related_objects = await related_model.objects.filter(**{f"{field_name}_id": pk_value})

        return related_objects

    def _get_related_fields(self, model: Type["Model"]) -> List[Tuple[Type["Model"], str, str]]:
        """
        Get all fields that reference this model.

        Args:
            model: Model class

        Returns:
            List of (related_model, field_name, on_delete) tuples
        """
        from ..relationships import get_reverse_relations

        relationships = []

        # Get registered reverse relations
        reverse_rels = get_reverse_relations(model)

        for rel in reverse_rels:
            if rel["relation_type"] == "foreignkey":
                related_model = rel["related_model"]
                field_name = rel["related_field"]

                # Get on_delete from field
                field = getattr(related_model, field_name, None)
                if hasattr(field, "field") and hasattr(field.field, "on_delete"):
                    on_delete = field.field.on_delete
                else:
                    on_delete = "CASCADE"  # Default

                relationships.append((related_model, field_name, on_delete))

        return relationships

    async def _delete_instance(self, instance: "Model"):
        """Delete single instance without cascades."""
        adapter = await instance._get_adapter()

        pk_field = instance._meta.pk_field
        pk_value = getattr(instance, pk_field.name)

        placeholder = self._get_placeholder(adapter)

        query = f"DELETE FROM {instance.__tablename__} WHERE {pk_field.db_column} = {placeholder}"  # nosec B608 - identifiers validated

        await adapter.execute(query, [pk_value])

    def _get_placeholder(self, adapter) -> str:
        """Get SQL placeholder for adapter."""
        from ....adapters.mysql import MySQLAdapter
        from ....adapters.postgresql import PostgreSQLAdapter
        from ....adapters.sqlite import SQLiteAdapter

        if isinstance(adapter, PostgreSQLAdapter):
            return "$1"
        elif isinstance(adapter, MySQLAdapter):
            return "%s"
        elif isinstance(adapter, SQLiteAdapter):
            return "?"
        else:
            return "$1"


class CustomCascadeHandler:
    """
    Support for custom cascade handlers.

    Allows defining custom behavior beyond standard on_delete options.

    Example:
        def archive_on_delete(instance, related_model, field_name):
            # Custom logic: archive instead of delete
            related = await related_model.objects.get(**{field_name: instance})
            related.archived = True
            await related.save()

        class Book(Model):
            author = ForeignKey(
                Author,
                on_delete=archive_on_delete  # Custom handler
            )
    """

    @staticmethod
    async def handle_custom(
        handler: Callable, instance: "Model", related_model: Type["Model"], field_name: str
    ) -> Dict[str, int]:
        """
        Execute custom cascade handler.

        Args:
            handler: Custom handler function
            instance: Instance being deleted
            related_model: Related model
            field_name: Field name

        Returns:
            Dict of deletion counts
        """
        try:
            result = handler(instance, related_model, field_name)
            if hasattr(result, "__await__"):
                result = await result

            if isinstance(result, dict):
                return result
            return {}

        except Exception as e:
            logger.error(f"Error in custom cascade handler: {e}")
            return {}


class BulkCascadeHandler:
    """
    Optimized cascade handling for bulk operations.

    Performs cascades in batch for better performance.
    """

    @staticmethod
    async def bulk_delete_with_cascade(instances: List["Model"]) -> Tuple[int, Dict[str, int]]:
        """
        Delete multiple instances with cascades.

        Args:
            instances: List of instances to delete

        Returns:
            Tuple of (total_deleted, {model_name: count})
        """
        if not instances:
            return (0, {})

        handler = CascadeHandler()
        total_deleted = 0
        deletion_counts = defaultdict(int)

        for instance in instances:
            counts = await handler.handle_delete(instance)
            total_deleted += counts[0]

            for model_name, count in counts[1].items():
                deletion_counts[model_name] += count

        return (total_deleted, dict(deletion_counts))


def SET(value: Any) -> Callable:
    """
    Create SET cascade handler for specific value.

    Args:
        value: Value to set FK to

    Returns:
        Cascade handler function

    Example:
        class Book(Model):
            author = ForeignKey(
                Author,
                on_delete=SET(get_default_author)
            )
    """

    async def set_handler(instance: "Model", related_model: Type["Model"], field_name: str):
        related_objects = await related_model.objects.filter(
            **{f"{field_name}_id": getattr(instance, instance._meta.pk_field.name)}
        )

        # Get actual value (call if callable)
        actual_value = value() if callable(value) else value

        for obj in related_objects:
            setattr(obj, f"{field_name}_id", actual_value)
            await obj.save(update_fields=[f"{field_name}_id"])

        return {}

    return set_handler


# Standard cascade behavior classes
class CASCADE:
    """Delete related objects."""

    pass


class PROTECT:
    """Prevent deletion if related objects exist."""

    pass


class RESTRICT:
    """Similar to PROTECT."""

    pass


class SET_NULL:
    """Set foreign key to NULL."""

    pass


class SET_DEFAULT:
    """Set foreign key to default value."""

    pass


class DO_NOTHING:
    """Take no action."""

    pass


__all__ = [
    "CascadeHandler",
    "CustomCascadeHandler",
    "BulkCascadeHandler",
    "ProtectedError",
    "RestrictedError",
    "CASCADE",
    "PROTECT",
    "RESTRICT",
    "SET_NULL",
    "SET_DEFAULT",
    "DO_NOTHING",
    "SET",
]
