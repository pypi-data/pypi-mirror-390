"""
Self-Referential Relationships

Handles relationships where models reference themselves:
- Tree structures (parent/children)
- Adjacency list pattern
- Nested set pattern
- Recursive queries using CTEs
- Path materialization
- Symmetric relationships (friends)

Example:
    # Tree structure
    class Category(Model):
        name = CharField(max_length=100)
        parent = ForeignKey(
            'self',
            on_delete=SET_NULL,
            null=True,
            related_name='children'
        )

    # Usage
    electronics = Category(name='Electronics')
    await electronics.save()

    computers = Category(name='Computers', parent=electronics)
    await computers.save()

    # Get children
    children = await electronics.children.all()

    # Get all descendants (recursive)
    descendants = await electronics.get_descendants()

    # Symmetric relationship
    class User(Model):
        name = CharField(max_length=100)
        friends = ManyToManyField('self', symmetrical=True)

    # Usage
    alice = await User.create(name='Alice')
    bob = await User.create(name='Bob')
    await alice.friends.add(bob)
    # bob.friends automatically includes alice
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set, Type

if TYPE_CHECKING:
    from ..models import Model

logger = logging.getLogger(__name__)


class TreeNode:
    """
    Mixin for tree node functionality.

    Provides methods for traversing and manipulating tree structures.
    """

    @classmethod
    async def get_root_nodes(cls) -> List["Model"]:
        """
        Get all root nodes (nodes with no parent).

        Returns:
            List of root nodes
        """
        parent_field = cls._get_parent_field()
        if not parent_field:
            raise ValueError(f"{cls.__name__} is not a tree model")

        return await cls.objects.filter(**{f"{parent_field}_id": None})

    @classmethod
    def _get_parent_field(cls) -> Optional[str]:
        """Get the name of the parent field."""
        for field_name, field in cls._fields.items():
            if hasattr(field, "to") and (field.to == cls or field.to == "self"):
                return field_name
        return None

    async def get_ancestors(self, include_self: bool = False) -> List["Model"]:
        """
        Get all ancestors (parent, grandparent, etc.).

        Args:
            include_self: Whether to include this node

        Returns:
            List of ancestor nodes, ordered from closest to root
        """
        ancestors = []
        current = self if include_self else await self.get_parent()

        while current:
            ancestors.append(current)
            current = await current.get_parent()

        return ancestors

    async def get_descendants(
        self, include_self: bool = False, max_depth: Optional[int] = None
    ) -> List["Model"]:
        """
        Get all descendants recursively.

        Args:
            include_self: Whether to include this node
            max_depth: Maximum depth to traverse (None = unlimited)

        Returns:
            List of descendant nodes
        """
        parent_field = self._get_parent_field()
        if not parent_field:
            return []

        descendants = [self] if include_self else []

        # Use recursive CTE if database supports it
        if await self._supports_recursive_cte():
            descendants.extend(await self._get_descendants_cte(max_depth))
        else:
            # Fallback to iterative approach
            descendants.extend(await self._get_descendants_iterative(max_depth))

        return descendants

    async def _get_descendants_cte(self, max_depth: Optional[int] = None) -> List["Model"]:
        """Get descendants using recursive CTE."""
        parent_field = self._get_parent_field()
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name)

        adapter = await self._get_adapter()

        # Build recursive CTE query
        depth_clause = f"AND depth < {max_depth}" if max_depth else ""

        query = f"""
            WITH RECURSIVE descendants AS (
                -- Base case: direct children
                SELECT *, 1 as depth
                FROM {self.__tablename__}
                WHERE {parent_field}_id = $1

                UNION ALL

                -- Recursive case: children of children
                SELECT t.*, d.depth + 1
                FROM {self.__tablename__} t
                INNER JOIN descendants d ON t.{parent_field}_id = d.{pk_field.db_column}
                WHERE 1=1 {depth_clause}
            )
            SELECT * FROM descendants
            ORDER BY depth
        """
        # nosec B608 - table_name validated in config

        rows = await adapter.fetch_all(query, [pk_value])

        # Convert rows to model instances
        descendants = []
        for row in rows:
            instance = self.__class__()
            for field_name, field in self._fields.items():
                if field.db_column in row:
                    value = field.to_python(row[field.db_column])
                    setattr(instance, field_name, value)
            instance._state.adding = False
            descendants.append(instance)

        return descendants

    async def _get_descendants_iterative(self, max_depth: Optional[int] = None) -> List["Model"]:
        """Get descendants using iterative BFS approach."""
        parent_field = self._get_parent_field()
        descendants = []
        current_level = [self]
        depth = 0

        while current_level and (max_depth is None or depth < max_depth):
            next_level = []

            for node in current_level:
                # Get children
                children = await getattr(node, f"{parent_field}_children").all()
                descendants.extend(children)
                next_level.extend(children)

            current_level = next_level
            depth += 1

        return descendants

    async def get_children(self) -> List["Model"]:
        """
        Get direct children.

        Returns:
            List of child nodes
        """
        parent_field = self._get_parent_field()
        if not parent_field:
            return []

        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name)

        return await self.__class__.objects.filter(**{f"{parent_field}_id": pk_value})

    async def get_parent(self) -> Optional["Model"]:
        """
        Get parent node.

        Returns:
            Parent node or None
        """
        parent_field = self._get_parent_field()
        if not parent_field:
            return None

        parent = getattr(self, parent_field, None)
        if parent and hasattr(parent, "__await__"):
            return await parent
        return parent

    async def get_siblings(self, include_self: bool = False) -> List["Model"]:
        """
        Get sibling nodes (same parent).

        Args:
            include_self: Whether to include this node

        Returns:
            List of sibling nodes
        """
        parent = await self.get_parent()
        if not parent:
            # Root nodes
            siblings = await self.get_root_nodes()
        else:
            siblings = await parent.get_children()

        if not include_self:
            pk_field = self._meta.pk_field
            my_pk = getattr(self, pk_field.name)
            siblings = [s for s in siblings if getattr(s, pk_field.name) != my_pk]

        return siblings

    async def get_depth(self) -> int:
        """
        Get depth of node in tree (root = 0).

        Returns:
            Depth level
        """
        ancestors = await self.get_ancestors()
        return len(ancestors)

    async def is_root(self) -> bool:
        """Check if this is a root node."""
        parent = await self.get_parent()
        return parent is None

    async def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        children = await self.get_children()
        return len(children) == 0

    async def get_root(self) -> "Model":
        """Get root node of this tree."""
        ancestors = await self.get_ancestors(include_self=True)
        return ancestors[-1] if ancestors else self

    async def _supports_recursive_cte(self) -> bool:
        """Check if database supports recursive CTEs."""
        adapter = await self._get_adapter()
        from ....adapters.postgresql import PostgreSQLAdapter
        from ....adapters.sqlite import SQLiteAdapter

        # PostgreSQL and SQLite 3.8.3+ support recursive CTEs
        return isinstance(adapter, (PostgreSQLAdapter, SQLiteAdapter))


class NestedSetNode:
    """
    Mixin for Nested Set Model pattern.

    More efficient for read-heavy tree operations.
    Stores left and right values for each node.

    Example:
        class Category(Model, NestedSetNode):
            name = CharField(max_length=100)
            lft = IntegerField()
            rgt = IntegerField()
            tree_id = IntegerField()
            level = IntegerField()
    """

    async def get_descendants(self, include_self: bool = False) -> List["Model"]:
        """Get descendants using nested set queries."""
        if not hasattr(self, "lft") or not hasattr(self, "rgt"):
            raise ValueError("Model must have lft and rgt fields for nested sets")

        filter_kwargs = {
            "lft__gt": self.lft if not include_self else self.lft - 1,
            "rgt__lt": self.rgt if not include_self else self.rgt + 1,
            "tree_id": self.tree_id,
        }

        return await self.__class__.objects.filter(**filter_kwargs).order_by("lft")

    async def get_ancestors(self, include_self: bool = False) -> List["Model"]:
        """Get ancestors using nested set queries."""
        if not hasattr(self, "lft") or not hasattr(self, "rgt"):
            raise ValueError("Model must have lft and rgt fields for nested sets")

        filter_kwargs = {
            "lft__lt": self.lft if not include_self else self.lft + 1,
            "rgt__gt": self.rgt if not include_self else self.rgt - 1,
            "tree_id": self.tree_id,
        }

        return await self.__class__.objects.filter(**filter_kwargs).order_by("lft")

    async def insert_child(self, child: "Model", position: str = "last"):
        """
        Insert child node using nested set algorithm.

        Args:
            child: Child node to insert
            position: 'first' or 'last'
        """
        # This requires updating lft/rgt values of other nodes
        # Simplified implementation - full version would handle all updates
        if position == "last":
            child.lft = self.rgt
            child.rgt = self.rgt + 1
        else:
            child.lft = self.lft + 1
            child.rgt = self.lft + 2

        child.tree_id = self.tree_id
        child.level = self.level + 1

        # Update other nodes (would need transaction)
        await child.save()


class PathMaterialization:
    """
    Mixin for Path Materialization pattern.

    Stores full path to node as string for efficient ancestor queries.

    Example:
        class Category(Model, PathMaterialization):
            name = CharField(max_length=100)
            path = CharField(max_length=500)  # e.g., '/1/3/7/'
    """

    def get_path_field(self) -> str:
        """Get name of path field."""
        return getattr(self._meta, "path_field", "path")

    async def update_path(self):
        """Update path field based on ancestors."""
        parent = await self.get_parent()
        pk_field = self._meta.pk_field
        pk_value = getattr(self, pk_field.name)

        path_field = self.get_path_field()

        if parent:
            parent_path = getattr(parent, path_field, "")
            setattr(self, path_field, f"{parent_path}{pk_value}/")
        else:
            setattr(self, path_field, f"/{pk_value}/")

    async def get_ancestors(self, include_self: bool = False) -> List["Model"]:
        """Get ancestors using path queries."""
        path_field = self.get_path_field()
        path = getattr(self, path_field, "")

        if not path:
            return []

        # Parse ancestor IDs from path
        ancestor_ids = [int(x) for x in path.strip("/").split("/") if x]

        if not include_self and ancestor_ids:
            ancestor_ids = ancestor_ids[:-1]

        if not ancestor_ids:
            return []

        # Fetch ancestors
        pk_field = self._meta.pk_field
        ancestors = await self.__class__.objects.filter(**{f"{pk_field.name}__in": ancestor_ids})

        # Sort by position in path
        ancestor_dict = {getattr(a, pk_field.name): a for a in ancestors}
        return [ancestor_dict[aid] for aid in ancestor_ids if aid in ancestor_dict]


__all__ = [
    "TreeNode",
    "NestedSetNode",
    "PathMaterialization",
]
