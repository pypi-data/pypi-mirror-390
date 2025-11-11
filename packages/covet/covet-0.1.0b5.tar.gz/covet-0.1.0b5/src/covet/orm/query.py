"""
ORM Query System

Advanced query builder with filtering, ordering, aggregation, and optimization.
"""

import asyncio
import operator
from abc import ABC, abstractmethod
from collections import OrderedDict
from functools import reduce
from typing import Any, Dict, Iterator, List, Optional, Set, Tuple, Union

from .exceptions import DoesNotExist, MultipleObjectsReturned, ORMError, QueryError


class Q:
    """Query object for complex lookups."""

    AND = "AND"
    OR = "OR"

    def __init__(self, *args, **kwargs):
        self.children = list(args)
        self.kwargs = kwargs
        self.connector = self.AND
        self.negated = False

    def __and__(self, other):
        """Combine with AND."""
        if not isinstance(other, Q):
            raise TypeError("Can only combine Q objects")
        result = Q()
        result.children = [self, other]
        result.connector = self.AND
        return result

    def __or__(self, other):
        """Combine with OR."""
        if not isinstance(other, Q):
            raise TypeError("Can only combine Q objects")
        result = Q()
        result.children = [self, other]
        result.connector = self.OR
        return result

    def __invert__(self):
        """Negate the Q object."""
        result = self._clone()
        result.negated = not result.negated
        return result

    def _clone(self):
        """Create a copy of this Q object."""
        clone = Q()
        clone.children = self.children[:]
        clone.kwargs = self.kwargs.copy()
        clone.connector = self.connector
        clone.negated = self.negated
        return clone


class F:
    """Field reference for database expressions."""

    def __init__(self, name: str):
        self.name = name

    def __add__(self, other):
        return Expression(self, "+", other)

    def __sub__(self, other):
        return Expression(self, "-", other)

    def __mul__(self, other):
        return Expression(self, "*", other)

    def __truediv__(self, other):
        return Expression(self, "/", other)

    def __repr__(self):
        return f"F('{self.name}')"


class Expression:
    """Database expression."""

    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def __repr__(self):
        return f"Expression({self.left} {self.operator} {self.right})"


class Lookup:
    """Base class for field lookups."""

    def __init__(self, field_name: str, value: Any):
        self.field_name = field_name
        self.value = value

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        """Convert to SQL."""
        raise NotImplementedError


class ExactLookup(Lookup):
    """Exact match lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} = ?", [self.value]


class IExactLookup(Lookup):
    """Case-insensitive exact match."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        if engine == "postgresql":
            return f"LOWER({self.field_name}) = LOWER(?)", [self.value]
        return f"UPPER({self.field_name}) = UPPER(?)", [self.value]


class ContainsLookup(Lookup):
    """Contains substring lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} LIKE ?", [f"%{self.value}%"]


class IContainsLookup(Lookup):
    """Case-insensitive contains lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        if engine == "postgresql":
            return f"{self.field_name} ILIKE ?", [f"%{self.value}%"]
        return f"UPPER({self.field_name}) LIKE UPPER(?)", [f"%{self.value}%"]


class StartsWithLookup(Lookup):
    """Starts with lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} LIKE ?", [f"{self.value}%"]


class EndsWithLookup(Lookup):
    """Ends with lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} LIKE ?", [f"%{self.value}"]


class InLookup(Lookup):
    """In lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        if not self.value:
            return "1=0", []  # Empty IN clause
        placeholders = ",".join(["?" for _ in self.value])
        return f"{self.field_name} IN ({placeholders})", list(self.value)


class RangeLookup(Lookup):
    """Range lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        start, end = self.value
        return f"{self.field_name} BETWEEN ? AND ?", [start, end]


class GtLookup(Lookup):
    """Greater than lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} > ?", [self.value]


class GteLookup(Lookup):
    """Greater than or equal lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} >= ?", [self.value]


class LtLookup(Lookup):
    """Less than lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} < ?", [self.value]


class LteLookup(Lookup):
    """Less than or equal lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"{self.field_name} <= ?", [self.value]


class IsNullLookup(Lookup):
    """Is null lookup."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        if self.value:
            return f"{self.field_name} IS NULL", []
        return f"{self.field_name} IS NOT NULL", []


# Lookup registry
LOOKUP_TYPES = {
    "exact": ExactLookup,
    "iexact": IExactLookup,
    "contains": ContainsLookup,
    "icontains": IContainsLookup,
    "startswith": StartsWithLookup,
    "endswith": EndsWithLookup,
    "in": InLookup,
    "range": RangeLookup,
    "gt": GtLookup,
    "gte": GteLookup,
    "lt": LtLookup,
    "lte": LteLookup,
    "isnull": IsNullLookup,
}


class QuerySet:
    """QuerySet for database queries."""

    def __init__(self, model_class, using=None):
        self.model_class = model_class
        self.using = using
        self._filters = []
        self._excludes = []
        self._order_by = []
        self._select_related = []
        self._prefetch_related = []
        self._limit = None
        self._offset = None
        self._distinct = False
        self._annotations = {}
        self._group_by = []
        self._having = []
        self._result_cache = None
        self._fetched_all = False

    def __repr__(self):
        if self._result_cache is not None:
            return f"<QuerySet {list(self._result_cache)}>"
        return f"<QuerySet for {self.model_class.__name__}>"

    def __len__(self):
        """Get count of results."""
        if self._result_cache is not None:
            return len(self._result_cache)
        return self.count()

    def __iter__(self):
        """Iterate over results."""
        self._fetch_all()
        return iter(self._result_cache)

    def __getitem__(self, k):
        """Get item by index or slice."""
        if not isinstance(k, (int, slice)):
            raise TypeError("QuerySet indices must be integers or slices")

        if isinstance(k, slice):
            # Handle slice
            start, stop, step = k.indices(self.count())
            if step != 1:
                raise TypeError("QuerySet slicing with step is not supported")
            return self._clone()._slice(start, stop - start)
        else:
            # Handle index
            if k < 0:
                k = self.count() + k
            return list(self)[k]

    def __bool__(self):
        """Check if queryset has results."""
        if self._result_cache is not None:
            return bool(self._result_cache)
        return self.exists()

    def _clone(self):
        """Create a copy of this queryset."""
        clone = self.__class__(self.model_class, self.using)
        clone._filters = self._filters[:]
        clone._excludes = self._excludes[:]
        clone._order_by = self._order_by[:]
        clone._select_related = self._select_related[:]
        clone._prefetch_related = self._prefetch_related[:]
        clone._limit = self._limit
        clone._offset = self._offset
        clone._distinct = self._distinct
        clone._annotations = self._annotations.copy()
        clone._group_by = self._group_by[:]
        clone._having = self._having[:]
        return clone

    def _slice(self, start: int, length: int):
        """Apply slice to queryset."""
        clone = self._clone()
        clone._offset = start
        clone._limit = length
        return clone

    def _fetch_all(self):
        """Fetch all results."""
        if self._result_cache is None:
            self._result_cache = list(self._execute())
            self._fetched_all = True

    def _execute(self):
        """Execute the query."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.execute_query(self)

    async def _aexecute(self):
        """Execute the query asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.aexecute_query(self)

    def filter(self, *args, **kwargs):
        """Filter the queryset."""
        clone = self._clone()

        # Handle Q objects
        for arg in args:
            if isinstance(arg, Q):
                clone._filters.append(arg)
            else:
                raise TypeError("filter() arguments must be Q objects or keyword arguments")

        # Handle keyword arguments
        for key, value in kwargs.items():
            clone._filters.append(self._parse_lookup(key, value))

        return clone

    def exclude(self, *args, **kwargs):
        """Exclude from the queryset."""
        clone = self._clone()

        # Handle Q objects
        for arg in args:
            if isinstance(arg, Q):
                clone._excludes.append(arg)
            else:
                raise TypeError("exclude() arguments must be Q objects or keyword arguments")

        # Handle keyword arguments
        for key, value in kwargs.items():
            clone._excludes.append(self._parse_lookup(key, value))

        return clone

    def _parse_lookup(self, key: str, value: Any) -> Q:
        """Parse a lookup into a Q object."""
        if "__" in key:
            field_name, lookup_type = key.rsplit("__", 1)
        else:
            field_name, lookup_type = key, "exact"

        if lookup_type not in LOOKUP_TYPES:
            raise QueryError(f"Unknown lookup type: {lookup_type}")

        lookup_class = LOOKUP_TYPES[lookup_type]
        lookup = lookup_class(field_name, value)

        q = Q()
        q.children = [lookup]
        return q

    def order_by(self, *fields):
        """Order the queryset."""
        clone = self._clone()
        clone._order_by = list(fields)
        return clone

    def reverse(self):
        """Reverse the ordering."""
        clone = self._clone()
        reversed_ordering = []
        for field in clone._order_by:
            if field.startswith("-"):
                reversed_ordering.append(field[1:])
            else:
                reversed_ordering.append("-" + field)
        clone._order_by = reversed_ordering
        return clone

    def distinct(self, *fields):
        """Add distinct clause."""
        clone = self._clone()
        clone._distinct = True
        if fields:
            clone._distinct_fields = fields
        return clone

    def select_related(self, *fields):
        """Select related objects."""
        clone = self._clone()
        clone._select_related.extend(fields)
        return clone

    def prefetch_related(self, *fields):
        """Prefetch related objects."""
        clone = self._clone()
        clone._prefetch_related.extend(fields)
        return clone

    def annotate(self, **kwargs):
        """Add annotations."""
        clone = self._clone()
        clone._annotations.update(kwargs)
        return clone

    def aggregate(self, **kwargs):
        """Perform aggregation."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.aggregate(self, kwargs)

    async def aaggregate(self, **kwargs):
        """Perform aggregation asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.aaggregate(self, kwargs)

    def values(self, *fields):
        """Return dictionaries instead of model instances."""
        clone = self._clone()
        clone._values_fields = fields
        return clone

    def values_list(self, *fields, flat=False):
        """Return tuples of values."""
        clone = self._clone()
        clone._values_list_fields = fields
        clone._values_list_flat = flat
        return clone

    def only(self, *fields):
        """Only load specified fields."""
        clone = self._clone()
        clone._only_fields = fields
        return clone

    def defer(self, *fields):
        """Defer loading of specified fields."""
        clone = self._clone()
        clone._defer_fields = fields
        return clone

    def exists(self):
        """Check if any results exist."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.exists(self)

    async def aexists(self):
        """Check if any results exist asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.aexists(self)

    def count(self):
        """Get count of results."""
        if self._result_cache is not None:
            return len(self._result_cache)
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.count(self)

    async def acount(self):
        """Get count of results asynchronously."""
        if self._result_cache is not None:
            return len(self._result_cache)
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.acount(self)

    def first(self):
        """Get first result."""
        try:
            return self[0]
        except IndexError:
            return None

    async def afirst(self):
        """Get first result asynchronously."""
        results = await self._aexecute()
        try:
            return results[0]
        except IndexError:
            return None

    def last(self):
        """Get last result."""
        try:
            return self.reverse()[0]
        except IndexError:
            return None

    async def alast(self):
        """Get last result asynchronously."""
        reversed_qs = self.reverse()
        results = await reversed_qs._aexecute()
        try:
            return results[0]
        except IndexError:
            return None

    def get(self, *args, **kwargs):
        """Get single object."""
        if args or kwargs:
            clone = self.filter(*args, **kwargs)
        else:
            clone = self

        results = list(clone[:2])  # Limit to 2 to detect multiple objects

        if not results:
            raise DoesNotExist(f"{self.model_class.__name__} matching query does not exist")
        if len(results) > 1:
            raise MultipleObjectsReturned(
                f"get() returned more than one {self.model_class.__name__}"
            )

        return results[0]

    async def aget(self, *args, **kwargs):
        """Get single object asynchronously."""
        if args or kwargs:
            clone = self.filter(*args, **kwargs)
        else:
            clone = self

        results = await clone._aexecute()
        results = results[:2]  # Limit to 2 to detect multiple objects

        if not results:
            raise DoesNotExist(f"{self.model_class.__name__} matching query does not exist")
        if len(results) > 1:
            raise MultipleObjectsReturned(
                f"aget() returned more than one {self.model_class.__name__}"
            )

        return results[0]

    def get_or_create(self, defaults=None, **kwargs):
        """Get object or create if it doesn't exist."""
        try:
            return self.get(**kwargs), False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            return self.model_class.objects.create(**create_kwargs), True

    async def aget_or_create(self, defaults=None, **kwargs):
        """Get object or create if it doesn't exist asynchronously."""
        try:
            return await self.aget(**kwargs), False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            return await self.model_class.objects.acreate(**create_kwargs), True

    def update(self, **kwargs):
        """Update all matching objects."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.update(self, kwargs)

    async def aupdate(self, **kwargs):
        """Update all matching objects asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.aupdate(self, kwargs)

    def delete(self):
        """Delete all matching objects."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.delete(self)

    async def adelete(self):
        """Delete all matching objects asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.adelete(self)

    def bulk_create(self, objects, batch_size=None, ignore_conflicts=False):
        """Bulk create objects."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.bulk_create(objects, batch_size, ignore_conflicts)

    async def abulk_create(self, objects, batch_size=None, ignore_conflicts=False):
        """Bulk create objects asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.abulk_create(objects, batch_size, ignore_conflicts)

    def bulk_update(self, objects, fields, batch_size=None):
        """Bulk update objects."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return manager.bulk_update(objects, fields, batch_size)

    async def abulk_update(self, objects, fields, batch_size=None):
        """Bulk update objects asynchronously."""
        from .managers import Manager

        manager = Manager(self.model_class)
        return await manager.abulk_update(objects, fields, batch_size)


# Aggregation functions
class Aggregate:
    """Base aggregation function."""

    def __init__(self, field_name: str, **extra):
        self.field_name = field_name
        self.extra = extra

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        """Convert to SQL."""
        raise NotImplementedError


class Count(Aggregate):
    """Count aggregation."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        if self.field_name == "*":
            return "COUNT(*)", []
        return f"COUNT({self.field_name})", []


class Sum(Aggregate):
    """Sum aggregation."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"SUM({self.field_name})", []


class Avg(Aggregate):
    """Average aggregation."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"AVG({self.field_name})", []


class Max(Aggregate):
    """Maximum aggregation."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"MAX({self.field_name})", []


class Min(Aggregate):
    """Minimum aggregation."""

    def as_sql(self, engine: str) -> Tuple[str, List[Any]]:
        return f"MIN({self.field_name})", []
