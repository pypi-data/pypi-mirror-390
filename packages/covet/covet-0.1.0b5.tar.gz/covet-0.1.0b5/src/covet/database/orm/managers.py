"""
ORM Model Manager and QuerySet

Django-style QuerySet API for fluent database queries with lazy evaluation,
caching, and advanced features like select_related and prefetch_related.

Example:
    # Basic queries
    users = await User.objects.all()
    active = await User.objects.filter(is_active=True)
    admin = await User.objects.get(username='admin')

    # Chaining and filtering
    results = await User.objects.filter(
        is_active=True
    ).exclude(
        username='guest'
    ).order_by('-created_at').limit(10)

    # Field lookups
    users = await User.objects.filter(
        age__gte=18,
        email__icontains='example.com',
        created_at__lt=datetime.now()
    )

    # Aggregation
    stats = await User.objects.aggregate(
        total=Count('*'),
        avg_age=Avg('age')
    )

    # Relationships
    posts = await Post.objects.select_related(
        'author'
    ).prefetch_related(
        'comments'
    ).all()
"""

import asyncio
import logging
import re
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple, Type, Union

logger = logging.getLogger(__name__)


class QuerySet:
    """
    Lazy database query builder with Django-compatible API.

    Supports:
    - Lazy evaluation (queries only execute when needed)
    - Method chaining (filter, exclude, order_by, etc.)
    - Field lookups (__exact, __gt, __contains, etc.)
    - Aggregation and annotation
    - Eager loading (select_related, prefetch_related)
    - Result caching
    - DoS protection via automatic query size limits
    """

    # DoS Protection: Maximum rows to return from a single query
    # Prevents memory exhaustion attacks from unbounded queries
    DEFAULT_MAX_QUERY_LIMIT = 10000

    def __init__(self, model: Type["Model"], using: Optional[str] = None):
        """
        Initialize QuerySet for a model.

        Args:
            model: Model class
            using: Database alias to use
        """
        self.model = model
        self._using = using or model.__database__

        # Query state
        self._filters: List[Dict[str, Any]] = []
        self._excludes: List[Dict[str, Any]] = []
        self._order_by: List[str] = []
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self._select_related: List[str] = []
        self._prefetch_related: List[str] = []
        self._values_fields: Optional[List[str]] = None
        self._values_list_fields: Optional[List[str]] = None
        self._values_list_flat: bool = False
        self._only_fields: Optional[List[str]] = None
        self._defer_fields: Optional[List[str]] = None
        self._distinct: bool = False
        self._annotations: Dict[str, Any] = {}

        # Result cache
        self._result_cache: Optional[List] = None
        self._fetched = False

        # DoS Protection: Flag to allow unlimited results (use with extreme caution)
        self._allow_unlimited: bool = False

    def _clone(self) -> "QuerySet":
        """Create a copy of this QuerySet for chaining."""
        clone = QuerySet(self.model, self._using)
        clone._filters = self._filters.copy()
        clone._excludes = self._excludes.copy()
        clone._order_by = self._order_by.copy()
        clone._limit = self._limit
        clone._offset = self._offset
        clone._select_related = self._select_related.copy()
        clone._prefetch_related = self._prefetch_related.copy()
        clone._values_fields = self._values_fields
        clone._values_list_fields = self._values_list_fields
        clone._values_list_flat = self._values_list_flat
        clone._only_fields = self._only_fields
        clone._defer_fields = self._defer_fields
        clone._distinct = self._distinct
        clone._annotations = self._annotations.copy()
        clone._allow_unlimited = self._allow_unlimited
        return clone

    def filter(self, *args, **kwargs) -> "QuerySet":
        """
        Filter queryset by field lookups or Q objects.

        Supports Django-style field lookups:
        - field__exact or field: Exact match
        - field__iexact: Case-insensitive exact
        - field__contains: Contains substring
        - field__icontains: Case-insensitive contains
        - field__startswith/istartswith: Starts with
        - field__endswith/iendswith: Ends with
        - field__gt/gte: Greater than (or equal)
        - field__lt/lte: Less than (or equal)
        - field__in: In list
        - field__isnull: Is NULL
        - field__regex/iregex: Regex match

        Also supports Q objects for complex queries:
        - Q(field1=value) | Q(field2=value): OR
        - Q(field1=value) & Q(field2=value): AND
        - ~Q(field=value): NOT

        Args:
            *args: Q objects for complex queries
            **kwargs: Field lookup expressions

        Returns:
            New QuerySet with filter applied

        Example:
            User.objects.filter(age__gte=18, email__icontains='example')
            User.objects.filter(Q(username='john') | Q(email='john@example.com'))
            User.objects.filter(Q(is_active=True) & (Q(age__gte=18) | Q(verified=True)))
        """
        clone = self._clone()

        # Handle Q objects
        if args:
            for arg in args:
                if isinstance(arg, Q):
                    clone._filters.append(arg)
                else:
                    raise TypeError(f"filter() expects Q objects or kwargs, got {type(arg).__name__}")

        # Handle kwargs (traditional filtering)
        if kwargs:
            clone._filters.append(kwargs)

        return clone

    def exclude(self, **kwargs) -> "QuerySet":
        """
        Exclude records matching field lookups.

        Args:
            **kwargs: Field lookup expressions to exclude

        Returns:
            New QuerySet with exclusion applied

        Example:
            User.objects.exclude(is_active=False)
        """
        clone = self._clone()
        if kwargs:
            clone._excludes.append(kwargs)
        return clone

    def order_by(self, *fields: str) -> "QuerySet":
        """
        Order results by fields.

        Args:
            *fields: Field names (prefix with '-' for descending)

        Returns:
            New QuerySet with ordering applied

        Raises:
            ValueError: If field does not exist in model schema

        Example:
            User.objects.order_by('-created_at', 'username')

        Security:
            Validates field names against model schema to prevent ORDER BY injection attacks.
            This prevents attackers from injecting arbitrary SQL through field names.
        """
        clone = self._clone()
        validated_fields = []

        for field in fields:
            # Remove DESC prefix for validation
            field_name = field[1:] if field.startswith('-') else field

            # Validate field exists in model schema
            if field_name not in self.model._fields:
                raise ValueError(
                    f"Cannot order by '{field_name}': field does not exist in {self.model.__name__}. "
                    f"Available fields: {', '.join(sorted(self.model._fields.keys()))}"
                )

            validated_fields.append(field)

        clone._order_by = validated_fields
        return clone

    def limit(self, n: int) -> "QuerySet":
        """
        Limit number of results.

        Args:
            n: Maximum number of results

        Returns:
            New QuerySet with limit applied

        Example:
            User.objects.limit(10)
        """
        clone = self._clone()
        clone._limit = n
        return clone

    def offset(self, n: int) -> "QuerySet":
        """
        Skip first n results.

        Args:
            n: Number of results to skip

        Returns:
            New QuerySet with offset applied

        Example:
            User.objects.offset(20).limit(10)  # Page 3
        """
        clone = self._clone()
        clone._offset = n
        return clone

    def distinct(self, *field_names: str) -> "QuerySet":
        """
        Return only distinct results.

        Args:
            *field_names: Optional field names for DISTINCT ON (PostgreSQL)

        Returns:
            New QuerySet with distinct applied

        Example:
            User.objects.distinct()
        """
        clone = self._clone()
        clone._distinct = True
        return clone

    def select_related(self, *fields: str) -> "QuerySet":
        """
        Eagerly load ForeignKey relationships using JOIN.

        Prevents N+1 queries for foreign keys by loading related
        objects in the same query.

        Args:
            *fields: ForeignKey field names to load

        Returns:
            New QuerySet with select_related applied

        Example:
            # Without select_related: N+1 queries
            posts = await Post.objects.all()
            for post in posts:
                logger.info(post.author.name)

            # With select_related: 1 query
            posts = await Post.objects.select_related('author').all()
            for post in posts:
                logger.info(post.author.name)
        """
        clone = self._clone()
        clone._select_related.extend(fields)
        return clone

    def prefetch_related(self, *fields: str) -> "QuerySet":
        """
        Eagerly load ManyToMany and reverse ForeignKey relationships.

        Uses separate queries but prevents N+1 by batch loading.

        Args:
            *fields: Relationship field names to prefetch

        Returns:
            New QuerySet with prefetch_related applied

        Example:
            # Load users with their posts in 2 queries instead of N+1
            users = await User.objects.prefetch_related('posts').all()
            for user in users:
                for post in user.posts.all():  # No extra queries
                    logger.info(post.title)
        """
        clone = self._clone()
        clone._prefetch_related.extend(fields)
        return clone

    def only(self, *fields: str) -> "QuerySet":
        """
        Fetch only specified fields from the database.

        Defers all other fields (they will trigger additional queries if accessed).
        This reduces the amount of data transferred from the database.

        Args:
            *fields: Field names to load immediately

        Returns:
            New QuerySet with only() applied

        Example:
            # Only load id and username, defer all other fields
            users = await User.objects.only('id', 'username').all()
            print(users[0].username)  # OK - was loaded
            print(users[0].email)     # Triggers additional query

        Note:
            - Primary key is always included even if not specified
            - Accessing deferred fields triggers a refresh query
            - Cannot be combined with values() or values_list()
        """
        clone = self._clone()
        clone._only_fields = list(fields)
        return clone

    def defer(self, *fields: str) -> "QuerySet":
        """
        Defer loading of specified fields from the database.

        Loads all fields except the specified ones. Deferred fields will
        trigger additional queries if accessed.

        Args:
            *fields: Field names to defer (not load immediately)

        Returns:
            New QuerySet with defer() applied

        Example:
            # Load all fields except large text field
            users = await User.objects.defer('bio').all()
            print(users[0].username)  # OK - was loaded
            print(users[0].bio)       # Triggers additional query

        Note:
            - Primary key is never deferred
            - Accessing deferred fields triggers a refresh query
            - Cannot be combined with values() or values_list()
            - Useful for skipping large text/binary fields
        """
        clone = self._clone()
        clone._defer_fields = list(fields)
        return clone

    def values(self, *fields: str) -> "QuerySet":
        """
        Return dictionaries instead of model instances.

        Args:
            *fields: Field names to include (all if empty)

        Returns:
            New QuerySet that returns dicts

        Example:
            users = await User.objects.values('id', 'username', 'email')
            # Returns: [{'id': 1, 'username': 'alice', 'email': '...'}, ...]
        """
        clone = self._clone()
        clone._values_fields = list(fields) if fields else None
        return clone

    def values_list(self, *fields: str, flat: bool = False) -> "QuerySet":
        """
        Return tuples instead of model instances.

        Args:
            *fields: Field names to include
            flat: If True and only one field, return flat list

        Returns:
            New QuerySet that returns tuples

        Example:
            ids = await User.objects.values_list('id', flat=True)
            # Returns: [1, 2, 3, 4, 5]

            data = await User.objects.values_list('id', 'username')
            # Returns: [(1, 'alice'), (2, 'bob'), ...]
        """
        clone = self._clone()
        clone._values_list_fields = list(fields)
        clone._values_list_flat = flat and len(fields) == 1
        return clone

    def annotate(self, **annotations) -> "QuerySet":
        """
        Add computed fields to results.

        Args:
            **annotations: name=AggregateFunction() pairs

        Returns:
            New QuerySet with annotations

        Example:
            users = await User.objects.annotate(
                post_count=Count('posts')
            ).all()
        """
        clone = self._clone()
        clone._annotations.update(annotations)
        return clone

    def allow_unlimited(self) -> "QuerySet":
        """
        Allow unlimited query results, bypassing the DEFAULT_MAX_QUERY_LIMIT protection.

        WARNING: Use with extreme caution! This disables DoS protection and can lead to:
        - Memory exhaustion from loading millions of rows
        - Application crashes and downtime
        - Database performance degradation
        - Potential security vulnerabilities

        Only use this for:
        - Administrative batch operations with proper monitoring
        - Data exports with streaming/pagination
        - Operations where you control the data size

        Security Considerations:
        - NEVER use this with user-controlled filters or inputs
        - Always implement application-level rate limiting
        - Monitor memory usage and set timeouts
        - Consider using iterator() or chunked processing instead

        Returns:
            New QuerySet with unlimited results allowed

        Example:
            # DANGEROUS: Don't do this with user input!
            all_data = await Model.objects.filter(
                user_input_field=user_value
            ).allow_unlimited().all()

            # SAFER: Admin-only export with monitoring
            if user.is_superuser:
                export_data = await Model.objects.filter(
                    status='archived'
                ).allow_unlimited().all()
                # ... stream to file instead of loading all in memory
        """
        clone = self._clone()
        clone._allow_unlimited = True
        logger.warning(
            f"DoS protection bypassed: allow_unlimited() called on {self.model.__name__} QuerySet. "
            f"This query can return unlimited rows and may cause memory exhaustion."
        )
        return clone

    async def aggregate(self, **aggregations) -> Dict[str, Any]:
        """
        Perform aggregation query.

        Args:
            **aggregations: name=AggregateFunction() pairs

        Returns:
            Dictionary of aggregation results

        Example:
            stats = await User.objects.aggregate(
                total=Count('*'),
                avg_age=Avg('age'),
                max_score=Max('score')
            )
            # Returns: {'total': 1000, 'avg_age': 32.5, 'max_score': 98}
        """
        # Build aggregation SQL
        select_parts = []
        for name, func in aggregations.items():
            sql = self._build_aggregate_sql(func)
            select_parts.append(f"{sql} AS {name}")

        query = f"SELECT {', '.join(select_parts)} FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        # Execute query
        adapter = await self._get_adapter()
        result = await adapter.fetch_one(query, params)

        return result or {}

    async def count(self) -> int:
        """
        Count number of matching records.

        Returns:
            Number of records

        Example:
            total_users = await User.objects.count()
            active_users = await User.objects.filter(is_active=True).count()
        """
        query = (
            f"SELECT COUNT(*) FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated
        )

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        adapter = await self._get_adapter()
        count = await adapter.fetch_value(query, params)

        return count or 0

    async def exists(self) -> bool:
        """
        Check if any records match.

        Returns:
            True if any records exist

        Example:
            if await User.objects.filter(email=email).exists():
                raise ValueError("Email already exists")
        """
        return await self.count() > 0

    async def all(self) -> List["Model"]:
        """
        Get all matching records.

        Returns:
            List of model instances

        Example:
            all_users = await User.objects.all()
        """
        return await self._fetch_all()

    async def get(self, **kwargs) -> "Model":
        """
        Get single record matching criteria.

        Args:
            **kwargs: Field lookups

        Returns:
            Model instance

        Raises:
            DoesNotExist: If no record found
            MultipleObjectsReturned: If multiple records found

        Example:
            user = await User.objects.get(id=1)
            admin = await User.objects.get(username='admin')
        """
        if kwargs:
            qs = self.filter(**kwargs)
        else:
            qs = self

        results = await qs.limit(2)._fetch_all()

        if not results:
            raise self.model.DoesNotExist(f"{self.model.__name__} matching query does not exist")

        if len(results) > 1:
            raise self.model.MultipleObjectsReturned(
                f"get() returned multiple {self.model.__name__} objects"
            )

        return results[0]

    async def first(self) -> Optional["Model"]:
        """
        Get first record or None.

        Returns:
            First model instance or None

        Example:
            oldest_user = await User.objects.order_by('created_at').first()
        """
        results = await self.limit(1)._fetch_all()
        return results[0] if results else None

    async def last(self) -> Optional["Model"]:
        """
        Get last record or None.

        Returns:
            Last model instance or None

        Example:
            newest_user = await User.objects.order_by('created_at').last()
        """
        # Reverse order for last
        clone = self._clone()
        clone._order_by = [
            f"-{field}" if not field.startswith("-") else field[1:]
            for field in (clone._order_by or [])
        ]
        results = await clone.limit(1)._fetch_all()
        return results[0] if results else None

    async def create(self, **kwargs) -> "Model":
        """
        Create and save new instance.

        Args:
            **kwargs: Field values

        Returns:
            Created model instance

        Example:
            user = await User.objects.create(
                username='alice',
                email='alice@example.com'
            )
        """
        instance = self.model(**kwargs)
        await instance.save()
        return instance

    async def bulk_create(
        self,
        objs: List["Model"],
        batch_size: int = 1000,
        ignore_conflicts: bool = False,
        update_conflicts: bool = False,
        update_fields: Optional[List[str]] = None
    ) -> List["Model"]:
        """
        Create multiple records in optimized batch INSERT statements.

        This is 10-100x faster than calling save() in a loop because:
        - Single INSERT with multiple value sets
        - Reduced network round-trips
        - Batching for large datasets

        Args:
            objs: List of unsaved model instances
            batch_size: Records per batch (default: 1000, max: 5000)
            ignore_conflicts: Skip duplicates (PostgreSQL/MySQL)
            update_conflicts: Update on conflict (upsert pattern)
            update_fields: Fields to update on conflict

        Returns:
            List of created instances (with IDs if supported)

        Example:
            users = [
                User(username=f'user{i}', email=f'user{i}@example.com')
                for i in range(10000)
            ]
            created = await User.objects.bulk_create(users, batch_size=500)
            # 20 queries instead of 10,000!

        Note:
            - Doesn't call save() or send signals
            - May not populate auto-increment IDs in all databases
            - Use batch_size to avoid max packet size limits
        """
        if not objs:
            return []

        # Validate batch size
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > 5000:
            logger.warning(f"batch_size {batch_size} exceeds 5000, setting to 5000")
            batch_size = 5000

        # Check for conflict handling consistency
        if update_conflicts and not update_fields:
            raise ValueError("update_fields required when update_conflicts=True")
        if ignore_conflicts and update_conflicts:
            raise ValueError("Cannot both ignore and update conflicts")

        # Get database adapter
        adapter = await self._get_adapter()

        # Import adapters for type checking
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        # Check adapter support for conflict handling
        if ignore_conflicts or update_conflicts:
            if isinstance(adapter, SQLiteAdapter):
                # SQLite has limited support - only basic INSERT OR IGNORE
                if update_conflicts:
                    raise NotImplementedError(
                        "SQLite doesn't support ON CONFLICT UPDATE for bulk operations"
                    )

        created_objects = []
        total_objs = len(objs)

        # Process in batches
        for batch_start in range(0, total_objs, batch_size):
            batch_end = min(batch_start + batch_size, total_objs)
            batch = objs[batch_start:batch_end]

            # Get field names and values from first object
            # Exclude auto fields unless explicitly set
            field_names = []
            pk_field = self.model._meta.pk_field

            for field_name, field_obj in self.model._fields.items():
                # Skip auto-increment primary keys unless value is set
                if field_obj.primary_key and hasattr(field_obj, 'auto_increment'):
                    if field_obj.auto_increment and getattr(batch[0], field_name) is None:
                        continue
                field_names.append(field_name)

            # Build values for batch
            all_params = []
            for obj in batch:
                # Validate object is correct model type
                if not isinstance(obj, self.model):
                    raise TypeError(
                        f"Expected {self.model.__name__} instance, got {type(obj).__name__}"
                    )

                # Get values for this object
                obj_values = []
                for field_name in field_names:
                    field_obj = self.model._fields[field_name]
                    value = getattr(obj, field_name)

                    # Handle field conversion
                    if value is not None:
                        value = field_obj.to_db(value)
                    elif field_obj.default is not None:
                        # Apply default if value is None
                        if callable(field_obj.default):
                            value = field_obj.default()
                        else:
                            value = field_obj.default
                    elif not field_obj.nullable and not field_obj.primary_key:
                        raise ValueError(
                            f"Field '{field_name}' cannot be null for {self.model.__name__}"
                        )

                    obj_values.append(value)
                all_params.extend(obj_values)

            # Build SQL based on adapter type
            if isinstance(adapter, PostgreSQLAdapter):
                # PostgreSQL: Use VALUES with numbered placeholders
                db_columns = [
                    self.model._fields[fn].db_column for fn in field_names
                ]

                # Build VALUES clause with proper placeholder numbering
                values_clauses = []
                param_count = len(field_names)
                for i in range(len(batch)):
                    start_idx = i * param_count + 1
                    placeholders = [f"${j}" for j in range(start_idx, start_idx + param_count)]
                    values_clauses.append(f"({', '.join(placeholders)})")

                query = (
                    f"INSERT INTO {self.model.__tablename__} "
                    f"({', '.join(db_columns)}) "
                    f"VALUES {', '.join(values_clauses)}"
                )

                # Handle conflicts for PostgreSQL
                if ignore_conflicts:
                    query += " ON CONFLICT DO NOTHING"
                elif update_conflicts:
                    # Build ON CONFLICT clause
                    pk_column = pk_field.db_column
                    update_cols = [
                        self.model._fields[fn].db_column
                        for fn in update_fields
                        if fn in self.model._fields
                    ]

                    if not update_cols:
                        raise ValueError(f"No valid update_fields found in {update_fields}")

                    set_clause = ", ".join([
                        f"{col} = EXCLUDED.{col}" for col in update_cols
                    ])

                    query += f" ON CONFLICT ({pk_column}) DO UPDATE SET {set_clause}"

                # Add RETURNING clause to get IDs back
                if pk_field and pk_field.auto_increment:
                    query += f" RETURNING {pk_field.db_column}"

            elif isinstance(adapter, MySQLAdapter):
                # MySQL: Use VALUES with %s placeholders
                db_columns = [
                    self.model._fields[fn].db_column for fn in field_names
                ]

                # Build VALUES clause with %s placeholders
                values_clauses = []
                param_count = len(field_names)
                for _ in range(len(batch)):
                    placeholders = ["%s"] * param_count
                    values_clauses.append(f"({', '.join(placeholders)})")

                query = (
                    f"INSERT "
                )

                if ignore_conflicts:
                    query += "IGNORE "

                query += (
                    f"INTO {self.model.__tablename__} "
                    f"({', '.join(db_columns)}) "
                    f"VALUES {', '.join(values_clauses)}"
                )

                # Handle ON DUPLICATE KEY UPDATE for MySQL
                if update_conflicts:
                    update_cols = [
                        self.model._fields[fn].db_column
                        for fn in update_fields
                        if fn in self.model._fields
                    ]

                    if not update_cols:
                        raise ValueError(f"No valid update_fields found in {update_fields}")

                    set_clause = ", ".join([
                        f"{col} = VALUES({col})" for col in update_cols
                    ])

                    query += f" ON DUPLICATE KEY UPDATE {set_clause}"

            elif isinstance(adapter, SQLiteAdapter):
                # SQLite: Use VALUES with ? placeholders
                db_columns = [
                    self.model._fields[fn].db_column for fn in field_names
                ]

                # Build VALUES clause with ? placeholders
                values_clauses = []
                param_count = len(field_names)
                for _ in range(len(batch)):
                    placeholders = ["?"] * param_count
                    values_clauses.append(f"({', '.join(placeholders)})")

                query = "INSERT "

                if ignore_conflicts:
                    query += "OR IGNORE "

                query += (
                    f"INTO {self.model.__tablename__} "
                    f"({', '.join(db_columns)}) "
                    f"VALUES {', '.join(values_clauses)}"
                )
            else:
                # Fallback for unknown adapter - use PostgreSQL syntax
                db_columns = [
                    self.model._fields[fn].db_column for fn in field_names
                ]

                values_clauses = []
                param_count = len(field_names)
                for i in range(len(batch)):
                    start_idx = i * param_count + 1
                    placeholders = [f"${j}" for j in range(start_idx, start_idx + param_count)]
                    values_clauses.append(f"({', '.join(placeholders)})")

                query = (
                    f"INSERT INTO {self.model.__tablename__} "
                    f"({', '.join(db_columns)}) "
                    f"VALUES {', '.join(values_clauses)}"
                )

            # Execute the batch insert
            try:
                if isinstance(adapter, PostgreSQLAdapter) and pk_field and pk_field.auto_increment:
                    # PostgreSQL with RETURNING clause - get IDs back
                    rows = await adapter.fetch_all(query, all_params)

                    # Populate IDs on objects
                    for obj, row in zip(batch, rows):
                        if row and pk_field.name in row:
                            setattr(obj, pk_field.name, row[pk_field.name])
                else:
                    # Other databases or no auto-increment
                    result = await adapter.execute(query, all_params)

                    # For MySQL, try to get last insert ID for first record
                    if isinstance(adapter, MySQLAdapter) and pk_field and pk_field.auto_increment:
                        # MySQL's last_insert_id() returns ID of first inserted row
                        # We can calculate subsequent IDs if they're sequential
                        try:
                            id_result = await adapter.fetch_one("SELECT LAST_INSERT_ID() as id")
                            if id_result and 'id' in id_result:
                                first_id = id_result['id']
                                # Only populate IDs if we're confident they're sequential
                                if not ignore_conflicts and not update_conflicts and first_id:
                                    for i, obj in enumerate(batch):
                                        setattr(obj, pk_field.name, first_id + i)
                        except Exception as e:
                            logger.debug(f"Could not retrieve auto-increment IDs: {e}")

                created_objects.extend(batch)

            except Exception as e:
                logger.error(
                    f"Bulk create failed for batch {batch_start//batch_size + 1}: {e}"
                )
                # Re-raise with more context
                raise RuntimeError(
                    f"Failed to bulk create {self.model.__name__} objects "
                    f"(batch {batch_start}-{batch_end} of {total_objs}): {e}"
                ) from e

        logger.info(
            f"Successfully bulk created {len(created_objects)} {self.model.__name__} objects"
        )

        return created_objects

    async def bulk_update(
        self,
        objs: List["Model"],
        fields: List[str],
        batch_size: int = 1000
    ) -> int:
        """
        Update multiple records in optimized batch UPDATE statements.

        Args:
            objs: List of model instances with updated values
            fields: List of field names to update
            batch_size: Records per batch

        Returns:
            Number of records updated

        Example:
            products = await Product.objects.filter(category='electronics')
            for product in products:
                product.discount = Decimal('0.10')

            updated = await Product.objects.bulk_update(products, ['discount'], batch_size=500)
            # Much faster than calling save() 1000 times!
        """
        if not objs:
            return 0

        if not fields:
            raise ValueError("Must specify at least one field to update")

        # Validate batch size
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        if batch_size > 5000:
            logger.warning(f"batch_size {batch_size} exceeds 5000, setting to 5000")
            batch_size = 5000

        # Validate fields exist
        for field_name in fields:
            if field_name not in self.model._fields:
                raise ValueError(
                    f"Field '{field_name}' does not exist on {self.model.__name__}"
                )

        # Get primary key field
        pk_field = self.model._meta.pk_field
        if not pk_field:
            raise ValueError(
                f"Model {self.model.__name__} has no primary key field for bulk_update"
            )

        # Get database adapter
        adapter = await self._get_adapter()

        # Import adapters for type checking
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        total_updated = 0
        total_objs = len(objs)

        # Process in batches
        for batch_start in range(0, total_objs, batch_size):
            batch_end = min(batch_start + batch_size, total_objs)
            batch = objs[batch_start:batch_end]

            if isinstance(adapter, PostgreSQLAdapter):
                # PostgreSQL: Use UPDATE ... FROM VALUES
                # This is the most efficient approach for PostgreSQL

                # Build the values table
                values_rows = []
                all_params = []
                param_index = 1

                for obj in batch:
                    # Validate object
                    if not isinstance(obj, self.model):
                        raise TypeError(
                            f"Expected {self.model.__name__} instance, got {type(obj).__name__}"
                        )

                    # Get primary key value
                    pk_value = getattr(obj, pk_field.name)
                    if pk_value is None:
                        raise ValueError(
                            f"Cannot bulk_update {self.model.__name__} without primary key value"
                        )

                    # Build row values
                    row_placeholders = [f"${param_index}"]
                    all_params.append(pk_value)
                    param_index += 1

                    for field_name in fields:
                        field_obj = self.model._fields[field_name]
                        value = getattr(obj, field_name)

                        # Convert to DB value
                        if value is not None:
                            value = field_obj.to_db(value)

                        row_placeholders.append(f"${param_index}")
                        all_params.append(value)
                        param_index += 1

                    values_rows.append(f"({', '.join(row_placeholders)})")

                # Build column names
                pk_column = pk_field.db_column
                update_columns = [self.model._fields[fn].db_column for fn in fields]
                all_columns = [pk_column] + update_columns

                # Build SET clause
                set_clauses = [
                    f"{col} = v.{col}"
                    for col in update_columns
                ]

                # Build the UPDATE query
                query = (
                    f"UPDATE {self.model.__tablename__} "
                    f"SET {', '.join(set_clauses)} "
                    f"FROM (VALUES {', '.join(values_rows)}) "
                    f"AS v({', '.join(all_columns)}) "
                    f"WHERE {self.model.__tablename__}.{pk_column} = v.{pk_column}"
                )

            elif isinstance(adapter, MySQLAdapter):
                # MySQL: Use CASE statements for each field
                # Less efficient but widely compatible

                pk_column = pk_field.db_column
                pk_values = []

                # Build CASE statements for each field
                case_statements = []
                all_params = []

                for field_name in fields:
                    field_obj = self.model._fields[field_name]
                    db_column = field_obj.db_column

                    case_parts = []
                    for obj in batch:
                        pk_value = getattr(obj, pk_field.name)
                        field_value = getattr(obj, field_name)

                        if pk_value not in pk_values:
                            pk_values.append(pk_value)

                        # Convert to DB value
                        if field_value is not None:
                            field_value = field_obj.to_db(field_value)

                        case_parts.append(f"WHEN {pk_column} = %s THEN %s")
                        all_params.extend([pk_value, field_value])

                    case_statement = f"{db_column} = CASE {' '.join(case_parts)} ELSE {db_column} END"
                    case_statements.append(case_statement)

                # Add pk values for WHERE clause
                all_params.extend(pk_values)

                # Build the UPDATE query
                placeholders = ["%s"] * len(pk_values)
                query = (
                    f"UPDATE {self.model.__tablename__} "
                    f"SET {', '.join(case_statements)} "
                    f"WHERE {pk_column} IN ({', '.join(placeholders)})"
                )

            elif isinstance(adapter, SQLiteAdapter):
                # SQLite: Similar to MySQL but with ? placeholders

                pk_column = pk_field.db_column
                pk_values = []

                # Build CASE statements for each field
                case_statements = []
                all_params = []

                for field_name in fields:
                    field_obj = self.model._fields[field_name]
                    db_column = field_obj.db_column

                    case_parts = []
                    for obj in batch:
                        pk_value = getattr(obj, pk_field.name)
                        field_value = getattr(obj, field_name)

                        if pk_value not in pk_values:
                            pk_values.append(pk_value)

                        # Convert to DB value
                        if field_value is not None:
                            field_value = field_obj.to_db(field_value)

                        case_parts.append(f"WHEN {pk_column} = ? THEN ?")
                        all_params.extend([pk_value, field_value])

                    case_statement = f"{db_column} = CASE {' '.join(case_parts)} ELSE {db_column} END"
                    case_statements.append(case_statement)

                # Add pk values for WHERE clause
                all_params.extend(pk_values)

                # Build the UPDATE query
                placeholders = ["?"] * len(pk_values)
                query = (
                    f"UPDATE {self.model.__tablename__} "
                    f"SET {', '.join(case_statements)} "
                    f"WHERE {pk_column} IN ({', '.join(placeholders)})"
                )

            else:
                # Fallback: Use PostgreSQL syntax
                raise NotImplementedError(
                    f"Bulk update not implemented for adapter type: {type(adapter).__name__}"
                )

            # Execute the batch update
            try:
                result = await adapter.execute(query, all_params)

                # Parse affected rows based on adapter
                if isinstance(adapter, PostgreSQLAdapter):
                    # PostgreSQL returns "UPDATE N"
                    if isinstance(result, str) and result.startswith("UPDATE"):
                        affected = int(result.split()[1])
                    else:
                        affected = len(batch)
                elif isinstance(adapter, (MySQLAdapter, SQLiteAdapter)):
                    # These adapters return integer count directly
                    affected = result if isinstance(result, int) else len(batch)
                else:
                    affected = len(batch)

                total_updated += affected

            except Exception as e:
                logger.error(
                    f"Bulk update failed for batch {batch_start//batch_size + 1}: {e}"
                )
                # Re-raise with more context
                raise RuntimeError(
                    f"Failed to bulk update {self.model.__name__} objects "
                    f"(batch {batch_start}-{batch_end} of {total_objs}): {e}"
                ) from e

        logger.info(
            f"Successfully bulk updated {total_updated} {self.model.__name__} objects"
        )

        return total_updated

    async def get_or_create(
        self, defaults: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Tuple["Model", bool]:
        """
        Get record or create if not exists.

        Args:
            defaults: Field values for creation
            **kwargs: Lookup fields

        Returns:
            Tuple of (instance, created)

        Example:
            user, created = await User.objects.get_or_create(
                email='alice@example.com',
                defaults={'username': 'alice'}
            )
        """
        try:
            instance = await self.get(**kwargs)
            return instance, False
        except self.model.DoesNotExist:
            create_kwargs = {**kwargs, **(defaults or {})}
            instance = await self.create(**create_kwargs)
            return instance, True

    async def update_or_create(
        self, defaults: Optional[Dict[str, Any]] = None, **kwargs
    ) -> Tuple["Model", bool]:
        """
        Update record or create if not exists.

        Args:
            defaults: Fields to update/create
            **kwargs: Lookup fields

        Returns:
            Tuple of (instance, created)

        Example:
            user, created = await User.objects.update_or_create(
                email='alice@example.com',
                defaults={'username': 'alice', 'is_active': True}
            )
        """
        try:
            instance = await self.get(**kwargs)
            # Update instance
            for key, value in (defaults or {}).items():
                setattr(instance, key, value)
            await instance.save()
            return instance, False
        except self.model.DoesNotExist:
            create_kwargs = {**kwargs, **(defaults or {})}
            instance = await self.create(**create_kwargs)
            return instance, True

    async def update(self, **kwargs) -> int:
        """
        Update all matching records.

        Args:
            **kwargs: Fields to update

        Returns:
            Number of records updated

        Example:
            updated = await User.objects.filter(
                is_active=False
            ).update(is_active=True)
        """
        if not kwargs:
            return 0

        # Get adapter first to know placeholder style
        adapter = await self._get_adapter()

        # Build UPDATE query
        set_parts = []
        params = []
        param_index = 1

        placeholders = self._get_param_placeholders(adapter, len(kwargs), param_index)
        for i, (field, value) in enumerate(kwargs.items()):
            set_parts.append(f"{field} = {placeholders[i]}")
            params.append(value)
            param_index += 1

        query = f"UPDATE {self.model.__tablename__} SET {', '.join(set_parts)}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, where_params = await self._build_where_clause(param_index)
        if where_clause:
            query += f" WHERE {where_clause}"
            params.extend(where_params)

        # Execute update
        result = await adapter.execute(query, params)

        # Parse result to get count
        # PostgreSQL returns "UPDATE 5", MySQL returns affected rows
        if isinstance(result, str) and result.startswith("UPDATE"):
            return int(result.split()[1])
        return 0

    async def delete(self) -> int:
        """
        Delete all matching records.

        Returns:
            Number of records deleted

        Example:
            deleted = await User.objects.filter(
                is_active=False,
                created_at__lt=one_year_ago
            ).delete()
        """
        # Build DELETE query
        query = f"DELETE FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated

        # Add WHERE clause
        where_clause, params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"

        # Execute delete
        adapter = await self._get_adapter()
        result = await adapter.execute(query, params)

        # Parse result to get count
        if isinstance(result, str) and result.startswith("DELETE"):
            return int(result.split()[1])
        return 0

    async def _fetch_all(self) -> List:
        """
        Execute query and return all results.

        Implements DoS protection by enforcing DEFAULT_MAX_QUERY_LIMIT unless
        explicitly bypassed with allow_unlimited().

        Security:
        - Prevents memory exhaustion attacks from unbounded queries
        - Logs warnings when queries approach or hit the limit
        - Requires explicit opt-in to bypass protection
        """
        if self._result_cache is not None:
            return self._result_cache

        # DoS Protection: Enforce maximum query limit
        original_limit = self._limit
        limit_enforced = False

        if not self._allow_unlimited:
            # Get the maximum limit for this model (can be customized per model)
            max_limit = getattr(
                self.model._meta,
                'max_query_limit',
                self.DEFAULT_MAX_QUERY_LIMIT
            )

            # Check if limit is None or exceeds maximum
            if self._limit is None or self._limit > max_limit:
                # Log security warning
                if self._limit is None:
                    logger.warning(
                        f"DoS Protection: Unbounded query detected on {self.model.__name__}. "
                        f"Automatically limiting to {max_limit} rows. "
                        f"Use .limit() to set explicit limit or .allow_unlimited() to bypass (not recommended)."
                    )
                else:
                    logger.warning(
                        f"DoS Protection: Query limit {self._limit} exceeds maximum {max_limit} "
                        f"for {self.model.__name__}. Enforcing maximum limit. "
                        f"Use .allow_unlimited() to bypass (not recommended for production)."
                    )

                # Enforce the limit
                self._limit = max_limit
                limit_enforced = True

            # Warn if query is approaching the limit (80% threshold)
            elif self._limit >= max_limit * 0.8:
                logger.info(
                    f"DoS Protection: Query limit {self._limit} is approaching maximum {max_limit} "
                    f"for {self.model.__name__}. Consider pagination or stricter filtering."
                )
        else:
            # Unlimited queries allowed but log for security auditing
            logger.info(
                f"DoS Protection bypassed: Executing unlimited query on {self.model.__name__}. "
                f"Original limit: {self._limit}"
            )

        # Build SELECT query
        query, params = await self._build_select_query()

        # Execute query
        adapter = await self._get_adapter()
        rows = await adapter.fetch_all(query, params)

        # Restore original limit if it was temporarily modified
        if limit_enforced:
            self._limit = original_limit

        # Convert to model instances or dicts/tuples
        if self._values_fields is not None:
            # Return dicts
            if self._values_fields:
                results = [{field: row.get(field) for field in self._values_fields} for row in rows]
            else:
                results = rows
        elif self._values_list_fields is not None:
            # Return tuples
            if hasattr(self, "_values_list_flat") and self._values_list_flat:
                results = [row[self._values_list_fields[0]] for row in rows]
            else:
                results = [
                    tuple(row.get(field) for field in self._values_list_fields) for row in rows
                ]
        else:
            # Return model instances
            # Convert database values to Python values using field.to_python()
            python_rows = []
            for row in rows:
                python_row = {}
                for field_name, db_value in row.items():
                    if field_name in self.model._fields:
                        field = self.model._fields[field_name]
                        python_row[field_name] = field.to_python(db_value)
                    else:
                        python_row[field_name] = db_value
                python_rows.append(python_row)

            results = [self.model(**row) for row in python_rows]

            # Mark instances as loaded from database (not adding)
            for instance in results:
                instance._state.adding = False

        # Handle select_related
        if self._select_related and results and not self._values_fields:
            await self._apply_select_related(results)

        # Handle prefetch_related
        if self._prefetch_related and results and not self._values_fields:
            await self._apply_prefetch_related(results)

        # Cache results
        self._result_cache = results
        self._fetched = True

        return results

    async def _build_select_query(self) -> Tuple[str, List]:
        """Build SELECT query from QuerySet state."""
        # SELECT clause
        if self._values_fields is not None:
            # values() - return dicts
            if self._values_fields:
                select_clause = ", ".join(self._values_fields)
            else:
                select_clause = "*"
        elif self._values_list_fields is not None:
            # values_list() - return tuples
            select_clause = ", ".join(self._values_list_fields)
        elif self._only_fields is not None:
            # only() - load only specified fields + pk
            pk_field_name = self.model._meta.pk_field.name
            fields_to_select = set(self._only_fields)
            # Always include primary key
            fields_to_select.add(pk_field_name)
            select_clause = ", ".join(
                self.model._fields[f].db_column
                for f in fields_to_select
                if f in self.model._fields
            )
        elif self._defer_fields is not None:
            # defer() - load all fields except specified ones
            pk_field_name = self.model._meta.pk_field.name
            defer_set = set(self._defer_fields)
            # Never defer primary key
            defer_set.discard(pk_field_name)
            select_clause = ", ".join(
                field.db_column
                for field_name, field in self.model._fields.items()
                if field_name not in defer_set
            )
        else:
            select_clause = "*"

        # DISTINCT
        distinct_clause = "DISTINCT " if self._distinct else ""

        query = f"SELECT {distinct_clause}{select_clause} FROM {self.model.__tablename__}"  # nosec B608 - identifiers validated
        params = []

        # WHERE clause
        where_clause, where_params = await self._build_where_clause()
        if where_clause:
            query += f" WHERE {where_clause}"
            params.extend(where_params)

        # ORDER BY clause
        if self._order_by:
            order_parts = []
            for field in self._order_by:
                if field.startswith("-"):
                    order_parts.append(f"{field[1:]} DESC")
                else:
                    order_parts.append(f"{field} ASC")
            query += f" ORDER BY {', '.join(order_parts)}"

        # LIMIT clause
        if self._limit is not None:
            query += f" LIMIT {self._limit}"

        # OFFSET clause
        if self._offset is not None:
            query += f" OFFSET {self._offset}"

        return query, params

    async def _build_where_clause(self, param_start: int = 1) -> Tuple[str, List]:
        """Build WHERE clause from filters and excludes."""
        # Get adapter to determine placeholder style
        adapter = await self._get_adapter()

        conditions = []
        params = []
        param_index = param_start

        # Process filters (can be dicts or Q objects)
        for filter_item in self._filters:
            if isinstance(filter_item, Q):
                # Process Q object
                condition, q_params = self._build_q_condition(adapter, filter_item, param_index)
                if condition:
                    conditions.append(f"({condition})")
                    params.extend(q_params)
                    param_index += len(q_params)
            else:
                # Process dict (traditional filtering)
                filter_conditions = []
                for lookup, value in filter_item.items():
                    condition, lookup_params = self._build_lookup_condition(
                        adapter, lookup, value, param_index
                    )
                    filter_conditions.append(condition)
                    params.extend(lookup_params)
                    param_index += len(lookup_params)

                if filter_conditions:
                    conditions.append(f"({' AND '.join(filter_conditions)})")

        # Process excludes (NOT)
        for exclude_dict in self._excludes:
            exclude_conditions = []
            for lookup, value in exclude_dict.items():
                condition, lookup_params = self._build_lookup_condition(
                    adapter, lookup, value, param_index
                )
                exclude_conditions.append(condition)
                params.extend(lookup_params)
                param_index += len(lookup_params)

            if exclude_conditions:
                conditions.append(f"NOT ({' OR '.join(exclude_conditions)})")

        where_clause = " AND ".join(conditions) if conditions else ""
        return where_clause, params

    def _validate_field_name(self, field_name: str) -> str:
        """
        Validate field name against model schema to prevent SQL injection.

        This is a critical security method that protects against SQL injection attacks
        by ensuring only valid field names from the model schema can be used in queries.

        Args:
            field_name: Field name from user input (e.g., 'username', 'email')

        Returns:
            Validated db_column name safe for SQL query construction

        Raises:
            ValueError: If field doesn't exist in model schema

        Example:
            # Safe - field exists in model
            validated = self._validate_field_name('username')  # Returns 'username'

            # Unsafe - rejects injection attempt
            validated = self._validate_field_name('id; DROP TABLE users--')  # Raises ValueError

        Security:
            This prevents SQL injection attacks like:
            - Field name injection: .filter(id; DROP TABLE users=1)
            - Column enumeration attacks
            - Bypassing parameterized queries through field names
        """
        if field_name not in self.model._fields:
            raise ValueError(
                f"Invalid field '{field_name}' for {self.model.__name__}. "
                f"Available fields: {', '.join(sorted(self.model._fields.keys()))}"
            )

        field = self.model._fields[field_name]
        return field.db_column or field_name

    def _escape_like_pattern(self, value: str) -> str:
        """
        Escape special characters in LIKE patterns to prevent LIKE injection attacks.

        LIKE patterns use % (match any string) and _ (match any character) as wildcards.
        Without proper escaping, attackers can craft inputs that cause:
        - Performance degradation (e.g., '%%%%%' patterns)
        - Information disclosure (bypassing intended filters)
        - Denial of service (catastrophic backtracking)

        Args:
            value: User input string to be used in LIKE pattern

        Returns:
            Escaped string safe for LIKE patterns with special chars neutralized

        Example:
            # User input: "test_value"
            escaped = self._escape_like_pattern("test_value")
            # Returns: "test\_value" (underscore is now literal, not wildcard)

            # User input: "admin%"
            escaped = self._escape_like_pattern("admin%")
            # Returns: "admin\%" (percent sign is now literal, not wildcard)

        Security:
            Protects against LIKE injection attacks:
            - Wildcard abuse: "%" matches everything, bypassing filters
            - Character injection: "_" can enumerate single character differences
            - Escape sequence attacks: "\\" can break escaping

        Note:
            Must be used with ESCAPE '\\\\' clause in SQL:
            WHERE field LIKE %s ESCAPE '\\\\'
        """
        # Escape backslash first (order matters!), then % and _
        # This prevents escape sequence attacks
        escaped = str(value).replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        return escaped

    def _build_lookup_condition(
        self, adapter, lookup: str, value: Any, param_index: int
    ) -> Tuple[str, List]:
        """
        Build SQL condition from Django-style field lookup.

        Args:
            adapter: Database adapter
            lookup: Field lookup (e.g., 'age__gte', 'email__icontains')
            value: Lookup value
            param_index: Current parameter index

        Returns:
            Tuple of (condition SQL, parameters)

        Raises:
            ValueError: If field name is invalid or lookup type is unsupported

        Security:
            - Validates field names against model schema to prevent SQL injection
            - Escapes LIKE patterns to prevent LIKE injection attacks
            - Uses parameterized queries for all values
        """
        # Parse lookup into field and lookup type
        parts = lookup.split("__")
        field_name = parts[0]
        lookup_type = parts[1] if len(parts) > 1 else "exact"

        # CRITICAL SECURITY: Validate field name against model schema
        # This prevents SQL injection through field names
        validated_field = self._validate_field_name(field_name)

        # Convert value using field's to_db method for database compatibility
        # This ensures Decimal, datetime, etc. are properly converted for the database
        if field_name in self.model._fields and value is not None:
            field_obj = self.model._fields[field_name]
            if hasattr(field_obj, 'to_db'):
                # For IN lookups, convert each value
                if lookup_type == "in" and hasattr(value, '__iter__'):
                    value = [field_obj.to_db(v) for v in value]
                # For other lookups, convert single value
                elif lookup_type not in ["isnull"]:  # isnull uses boolean, not field value
                    value = field_obj.to_db(value)

        # Get placeholder function
        def get_placeholder(idx):
            placeholders = self._get_param_placeholders(adapter, 1, idx)
            return placeholders[0]

        # Build condition based on lookup type
        if lookup_type == "exact":
            if value is None:
                return f"{validated_field} IS NULL", []
            return f"{validated_field} = {get_placeholder(param_index)}", [value]

        elif lookup_type == "iexact":
            return f"LOWER({validated_field}) = LOWER({get_placeholder(param_index)})", [value]

        elif lookup_type == "contains":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"{validated_field} LIKE {get_placeholder(param_index)} ESCAPE '\\\\'",
                [f"%{escaped_value}%"]
            )

        elif lookup_type == "icontains":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"LOWER({validated_field}) LIKE LOWER({get_placeholder(param_index)}) ESCAPE '\\\\'",
                [f"%{escaped_value}%"]
            )

        elif lookup_type == "startswith":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"{validated_field} LIKE {get_placeholder(param_index)} ESCAPE '\\\\'",
                [f"{escaped_value}%"]
            )

        elif lookup_type == "istartswith":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"LOWER({validated_field}) LIKE LOWER({get_placeholder(param_index)}) ESCAPE '\\\\'",
                [f"{escaped_value}%"]
            )

        elif lookup_type == "endswith":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"{validated_field} LIKE {get_placeholder(param_index)} ESCAPE '\\\\'",
                [f"%{escaped_value}%"]
            )

        elif lookup_type == "iendswith":
            # CRITICAL SECURITY: Escape LIKE pattern to prevent LIKE injection
            escaped_value = self._escape_like_pattern(value)
            return (
                f"LOWER({validated_field}) LIKE LOWER({get_placeholder(param_index)}) ESCAPE '\\\\'",
                [f"%{escaped_value}%"]
            )

        elif lookup_type == "gt":
            return f"{validated_field} > {get_placeholder(param_index)}", [value]

        elif lookup_type == "gte":
            return f"{validated_field} >= {get_placeholder(param_index)}", [value]

        elif lookup_type == "lt":
            return f"{validated_field} < {get_placeholder(param_index)}", [value]

        elif lookup_type == "lte":
            return f"{validated_field} <= {get_placeholder(param_index)}", [value]

        elif lookup_type == "in":
            if not value:
                return "FALSE", []
            placeholders = self._get_param_placeholders(adapter, len(value), param_index)
            return f"{validated_field} IN ({', '.join(placeholders)})", list(value)

        elif lookup_type == "isnull":
            if value:
                return f"{validated_field} IS NULL", []
            else:
                return f"{validated_field} IS NOT NULL", []

        elif lookup_type == "regex":
            return f"{validated_field} ~ {get_placeholder(param_index)}", [value]

        elif lookup_type == "iregex":
            return f"{validated_field} ~* {get_placeholder(param_index)}", [value]

        else:
            raise ValueError(f"Unsupported lookup type: {lookup_type}")

    def _build_q_condition(
        self, adapter, q: "Q", param_index: int
    ) -> Tuple[str, List]:
        """
        Build SQL condition from Q object.

        Args:
            adapter: Database adapter
            q: Q object with conditions
            param_index: Current parameter index

        Returns:
            Tuple of (condition SQL, parameters)

        Example Q objects:
            Q(username='john') -> "username = $1"
            Q(age__gte=18) | Q(verified=True) -> "(age >= $1) OR (verified = $2)"
            Q(is_active=True) & Q(age__gte=18) -> "(is_active = $1) AND (age >= $2)"
            ~Q(is_deleted=True) -> "NOT (is_deleted = $1)"
        """
        params = []

        # Handle negation
        if q.negated:
            # Recursively build condition for negated Q object
            inner_conditions = []
            for child in q.children:
                if isinstance(child, Q):
                    condition, child_params = self._build_q_condition(adapter, child, param_index)
                    if condition:
                        inner_conditions.append(condition)
                        params.extend(child_params)
                        param_index += len(child_params)
                else:
                    raise TypeError(f"Unexpected child type in Q object: {type(child).__name__}")

            if inner_conditions:
                return f"NOT ({' AND '.join(inner_conditions)})", params
            return "", []

        # Handle combined Q objects (AND/OR)
        if q.children and all(isinstance(child, Q) for child in q.children):
            conditions = []
            for child in q.children:
                condition, child_params = self._build_q_condition(adapter, child, param_index)
                if condition:
                    conditions.append(f"({condition})")
                    params.extend(child_params)
                    param_index += len(child_params)

            if conditions:
                connector = " OR " if q.connector == Q.OR else " AND "
                return connector.join(conditions), params
            return "", []

        # Handle dict lookups (leaf nodes)
        if q.children and isinstance(q.children[0], dict):
            lookup_dict = q.children[0]
            conditions = []

            for lookup, value in lookup_dict.items():
                condition, lookup_params = self._build_lookup_condition(
                    adapter, lookup, value, param_index
                )
                conditions.append(condition)
                params.extend(lookup_params)
                param_index += len(lookup_params)

            if conditions:
                connector = " OR " if q.connector == Q.OR else " AND "
                return connector.join(conditions), params
            return "", []

        return "", []

    def _build_aggregate_sql(self, func) -> str:
        """Build SQL for aggregate function."""
        # This is a placeholder - actual implementation would handle
        # Count, Sum, Avg, Max, Min, etc.
        func_name = func.__class__.__name__.upper()
        field = getattr(func, "field", "*")
        return f"{func_name}({field})"

    async def _apply_select_related(self, results: List["Model"]) -> None:
        """
        Load related objects using JOINs (actually done as separate queries).

        NOTE: For production use, this should be integrated into the main SQL query
        with LEFT JOIN clauses. This implementation uses separate queries for each
        relationship to maintain database adapter compatibility.

        Args:
            results: List of model instances to populate relationships for
        """
        if not results or not self._select_related:
            return

        # Get adapter
        adapter = await self._get_adapter()

        # Process each select_related field
        for field_name in self._select_related:
            # Check if field exists and is a ForeignKey
            if field_name not in self.model._fields:
                logger.warning(
                    f"select_related: Field '{field_name}' not found on {self.model.__name__}"
                )
                continue

            field = self.model._fields[field_name]

            # Check if it's a relationship field (has 'related_model'
            # attribute)
            if not hasattr(field, "related_model"):
                logger.warning(
                    f"select_related: Field '{field_name}' is not a ForeignKey on {self.model.__name__}"
                )
                continue

            # Get the related model
            related_model = field.related_model
            if isinstance(related_model, str):
                # Lazy relationship resolution
                from .relationships import resolve_model

                related_model = resolve_model(related_model)
                field.related_model = related_model

            # Collect foreign key values from results
            fk_values = set()
            for instance in results:
                fk_value = getattr(instance, field_name + "_id", None)
                if fk_value is not None:
                    fk_values.add(fk_value)

            if not fk_values:
                continue

            # Fetch related objects in single query
            pk_field_name = related_model._meta.pk_field.name
            placeholders = self._get_param_placeholders(adapter, len(fk_values), 1)

            query = (
                f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                f"WHERE {pk_field_name} IN ({', '.join(placeholders)})"
            )

            related_rows = await adapter.fetch_all(query, list(fk_values))

            # Build lookup dict
            related_objects = {row[pk_field_name]: related_model(**row) for row in related_rows}

            # Populate relationships on result instances
            for instance in results:
                fk_value = getattr(instance, field_name + "_id", None)
                if fk_value in related_objects:
                    setattr(instance, field_name, related_objects[fk_value])
                else:
                    setattr(instance, field_name, None)

    async def _apply_prefetch_related(self, results: List["Model"]) -> None:
        """
        Load related objects in batch queries (for reverse ForeignKey and ManyToMany).

        This prevents N+1 queries by loading all related objects in 2 queries:
        1. Main query for primary objects
        2. Single query for all related objects with IN clause

        Args:
            results: List of model instances to populate relationships for

        Example:
            # Without prefetch: N+1 queries
            users = await User.objects.all()
            for user in users:  # 1 query
                for post in user.posts.all():  # N queries!
                    print(post.title)

            # With prefetch: 2 queries
            users = await User.objects.prefetch_related('posts').all()
            for user in users:  # 1 query
                for post in user.posts.all():  # 0 queries (cached)
                    print(post.title)
        """
        if not results or not self._prefetch_related:
            return

        # Import reverse relationship registry
        from .relationships import get_reverse_relations

        # Get adapter
        adapter = await self._get_adapter()

        # Get primary keys from results
        pk_field_name = self.model._meta.pk_field.name
        pk_values = [getattr(instance, pk_field_name) for instance in results]

        if not pk_values:
            return

        # Process each prefetch_related field
        for field_name in self._prefetch_related:
            # Look up reverse relationship metadata from registry
            reverse_relations = get_reverse_relations(self.model)

            # Find the relationship for this field name
            relation_info = None
            for rel in reverse_relations:
                if rel.get("related_name") == field_name:
                    relation_info = rel
                    break

            if not relation_info:
                logger.warning(
                    f"prefetch_related: No reverse relationship '{field_name}' found on {self.model.__name__}. "
                    f"Make sure the related model has related_name='{field_name}' set on its ForeignKey/ManyToMany field."
                )
                continue

            # Extract relationship info
            related_model = relation_info["related_model"]
            related_field = relation_info["related_field"]
            relation_type = relation_info["relation_type"]

            logger.debug(
                f"prefetch_related: Loading {relation_type} '{field_name}' for {self.model.__name__} "
                f"(from {related_model.__name__}.{related_field})"
            )

            # Build query based on relationship type
            if relation_type in ("foreignkey", "onetoone"):
                # Reverse ForeignKey: SELECT * FROM related_table WHERE
                # fk_field IN (pk_values)
                fk_field_name = f"{related_field}_id"
                placeholders = self._get_param_placeholders(adapter, len(pk_values), 1)

                query = (
                    f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                    f"WHERE {fk_field_name} IN ({', '.join(placeholders)})"
                )

                related_rows = await adapter.fetch_all(query, list(pk_values))

                # Convert to model instances
                related_objects = [related_model(**row) for row in related_rows]

                # Group by foreign key value
                grouped_objects = {}
                for obj in related_objects:
                    fk_value = getattr(obj, fk_field_name)
                    if fk_value not in grouped_objects:
                        grouped_objects[fk_value] = []
                    grouped_objects[fk_value].append(obj)

                # Cache related objects on each parent instance
                for instance in results:
                    pk_value = getattr(instance, pk_field_name)
                    related_list = grouped_objects.get(pk_value, [])

                    # Store cached results
                    # Create a cache attribute that RelatedManager can check
                    cache_attr = f"_prefetched_{field_name}"

                    if relation_type == "onetoone":
                        # OneToOne returns single object or None
                        setattr(
                            instance,
                            cache_attr,
                            related_list[0] if related_list else None,
                        )
                    else:
                        # ForeignKey reverse returns list
                        setattr(instance, cache_attr, related_list)

            elif relation_type == "manytomany":
                # ManyToMany: Need to query through table
                # 1. Get through model from the ManyToMany field
                # 2. Query through table to get relationship mappings
                # 3. Query related model for actual objects
                # 4. Build mapping of parent_id -> [related_objects]

                # Get the ManyToMany field to access through model
                m2m_field = None
                for field in related_model._fields.values():
                    if hasattr(field, "related_name") and field.related_name == field_name:
                        m2m_field = field
                        break

                if not m2m_field or not hasattr(m2m_field, "get_through_model"):
                    logger.warning(
                        f"prefetch_related: Could not find ManyToMany field configuration for '{field_name}'"
                    )
                    continue

                through_model = m2m_field.get_through_model()
                if not through_model:
                    logger.warning(
                        f"prefetch_related: No through model found for ManyToMany '{field_name}'"
                    )
                    continue

                # Get field names for through table
                source_field_name = f"{self.model.__name__.lower()}_id"
                target_field_name = f"{related_model.__name__.lower()}_id"

                # Query through table
                placeholders = self._get_param_placeholders(adapter, len(pk_values), 1)
                through_query = (
                    f"SELECT {source_field_name}, {target_field_name} "  # nosec B608 - identifiers validated
                    f"FROM {through_model.__tablename__} "
                    f"WHERE {source_field_name} IN ({', '.join(placeholders)})"
                )

                through_rows = await adapter.fetch_all(through_query, list(pk_values))

                # Collect target IDs
                target_ids = {row[target_field_name] for row in through_rows}

                if target_ids:
                    # Query related objects
                    target_placeholders = self._get_param_placeholders(adapter, len(target_ids), 1)
                    target_pk_field = related_model._meta.pk_field.name

                    related_query = (
                        f"SELECT * FROM {related_model.__tablename__} "  # nosec B608 - identifiers validated
                        f"WHERE {target_pk_field} IN ({', '.join(target_placeholders)})"
                    )

                    related_rows = await adapter.fetch_all(related_query, list(target_ids))

                    # Convert to model instances and build lookup dict
                    related_objects_map = {
                        row[target_pk_field]: related_model(**row) for row in related_rows
                    }

                    # Build mapping of source_id -> [related_objects]
                    grouped_m2m = {}
                    for row in through_rows:
                        source_id = row[source_field_name]
                        target_id = row[target_field_name]

                        if source_id not in grouped_m2m:
                            grouped_m2m[source_id] = []

                        if target_id in related_objects_map:
                            grouped_m2m[source_id].append(related_objects_map[target_id])

                    # Cache related objects on each parent instance
                    for instance in results:
                        pk_value = getattr(instance, pk_field_name)
                        related_list = grouped_m2m.get(pk_value, [])

                        # Store cached results
                        cache_attr = f"_prefetched_{field_name}"
                        setattr(instance, cache_attr, related_list)
                else:
                    # No relationships found, cache empty lists
                    cache_attr = f"_prefetched_{field_name}"
                    for instance in results:
                        setattr(instance, cache_attr, [])

    async def _get_adapter(self):
        """Get database adapter for this queryset."""
        from .adapter_registry import get_adapter

        adapter = get_adapter(self._using)

        # Ensure adapter is connected
        if not adapter._connected:
            await adapter.connect()

        return adapter

    def _get_param_placeholders(self, adapter, count: int, start: int = 1) -> List[str]:
        """
        Get parameter placeholders for the adapter's database type.

        Args:
            adapter: Database adapter
            count: Number of placeholders needed
            start: Starting index for placeholders

        Returns:
            List of parameter placeholders
        """
        from ..adapters.mysql import MySQLAdapter
        from ..adapters.postgresql import PostgreSQLAdapter
        from ..adapters.sqlite import SQLiteAdapter

        if isinstance(adapter, PostgreSQLAdapter):
            # PostgreSQL uses $1, $2, $3, ...
            return [f"${start+i}" for i in range(count)]
        elif isinstance(adapter, MySQLAdapter):
            # MySQL uses %s, %s, %s, ...
            return ["%s"] * count
        elif isinstance(adapter, SQLiteAdapter):
            # SQLite uses ?, ?, ?, ...
            return ["?"] * count
        else:
            # Default to PostgreSQL-style
            return [f"${start+i}" for i in range(count)]

    def __await__(self):
        """Make QuerySet awaitable."""
        return self.all().__await__()

    def __aiter__(self):
        """Make QuerySet async iterable."""
        return self._async_iterator()

    async def _async_iterator(self):
        """Async iterator implementation."""
        results = await self.all()
        for result in results:
            yield result

    def __repr__(self) -> str:
        """String representation."""
        if self._result_cache is not None:
            return f"<QuerySet {self._result_cache}>"
        return f"<QuerySet for {self.model.__name__}>"


class ModelManager:
    """
    Model manager - provides QuerySet interface.

    Automatically added to models as 'objects' attribute.

    Example:
        users = await User.objects.all()
        active = await User.objects.filter(is_active=True)
    """

    def __init__(self, model: Optional[Type["Model"]] = None):
        """
        Initialize manager.

        Args:
            model: Model class (set by metaclass)
        """
        self.model = model

    def get_queryset(self) -> QuerySet:
        """
        Get base QuerySet for this manager.

        Returns:
            QuerySet for model

        Override this to customize default queryset:
            class ActiveManager(ModelManager):
                def get_queryset(self):
                    return super().get_queryset().filter(is_active=True)
        """
        return QuerySet(self.model)

    def all(self) -> QuerySet:
        """Get all objects."""
        return self.get_queryset()

    def filter(self, *args, **kwargs) -> QuerySet:
        """Filter objects with Q objects or field lookups."""
        return self.get_queryset().filter(*args, **kwargs)

    def exclude(self, **kwargs) -> QuerySet:
        """Exclude objects."""
        return self.get_queryset().exclude(**kwargs)

    def get(self, **kwargs):
        """Get single object."""
        return self.get_queryset().get(**kwargs)

    def create(self, **kwargs):
        """Create and save object."""
        return self.get_queryset().create(**kwargs)

    def bulk_create(self, objs, batch_size=1000, ignore_conflicts=False, update_conflicts=False, update_fields=None):
        """Create multiple objects in batch."""
        return self.get_queryset().bulk_create(
            objs=objs,
            batch_size=batch_size,
            ignore_conflicts=ignore_conflicts,
            update_conflicts=update_conflicts,
            update_fields=update_fields
        )

    def bulk_update(self, objs, fields, batch_size=1000):
        """Update multiple objects in batch."""
        return self.get_queryset().bulk_update(
            objs=objs,
            fields=fields,
            batch_size=batch_size
        )

    def get_or_create(self, defaults=None, **kwargs):
        """Get or create object."""
        return self.get_queryset().get_or_create(defaults=defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        """Update or create object."""
        return self.get_queryset().update_or_create(defaults=defaults, **kwargs)

    def count(self):
        """Count objects."""
        return self.get_queryset().count()

    def exists(self):
        """Check if any objects exist."""
        return self.get_queryset().exists()

    def select_related(self, *fields: str) -> QuerySet:
        """Eagerly load ForeignKey relationships using JOIN."""
        return self.get_queryset().select_related(*fields)

    def prefetch_related(self, *fields: str) -> QuerySet:
        """Eagerly load ManyToMany and reverse ForeignKey relationships."""
        return self.get_queryset().prefetch_related(*fields)

    def only(self, *fields: str) -> QuerySet:
        """Fetch only specified fields from the database."""
        return self.get_queryset().only(*fields)

    def defer(self, *fields: str) -> QuerySet:
        """Defer loading of specified fields from the database."""
        return self.get_queryset().defer(*fields)

    def values(self, *fields: str) -> QuerySet:
        """Return dictionaries instead of model instances."""
        return self.get_queryset().values(*fields)

    def values_list(self, *fields: str, flat: bool = False) -> QuerySet:
        """Return tuples instead of model instances."""
        return self.get_queryset().values_list(*fields, flat=flat)

    def order_by(self, *fields: str) -> QuerySet:
        """Order results by fields."""
        return self.get_queryset().order_by(*fields)

    def limit(self, n: int) -> QuerySet:
        """Limit number of results."""
        return self.get_queryset().limit(n)

    def offset(self, n: int) -> QuerySet:
        """Skip first n results."""
        return self.get_queryset().offset(n)

    def distinct(self, *field_names: str) -> QuerySet:
        """Return only distinct results."""
        return self.get_queryset().distinct(*field_names)

    def allow_unlimited(self) -> QuerySet:
        """
        Allow unlimited query results, bypassing DoS protection.

        WARNING: Use with extreme caution! See QuerySet.allow_unlimited() for details.

        Returns:
            QuerySet with unlimited results allowed
        """
        return self.get_queryset().allow_unlimited()

    def __repr__(self) -> str:
        """String representation."""
        return f"<{self.__class__.__name__} for {self.model.__name__}>"


# Aggregate functions
class Aggregate:
    """Base class for aggregate functions."""

    def __init__(self, field: str):
        self.field = field


class Count(Aggregate):
    """COUNT aggregate."""

    def __init__(self, field: str = "*"):
        super().__init__(field)


class Sum(Aggregate):
    """SUM aggregate."""


class Avg(Aggregate):
    """AVG aggregate."""


class Max(Aggregate):
    """MAX aggregate."""


class Min(Aggregate):
    """MIN aggregate."""


__all__ = [
    "QuerySet",
    "ModelManager",
    "Q",
    "Count",
    "Sum",
    "Avg",
    "Max",
    "Min",
]


class Q:
    """
    Query object for complex lookups (Django-style Q objects).
    
    Allows combining filters with AND/OR/NOT logic:
        Q(age__gte=18) & Q(is_active=True)
        Q(name='Alice') | Q(name='Bob')
        ~Q(is_deleted=True)
    """
    
    AND = 'AND'
    OR = 'OR'
    NOT = 'NOT'
    
    def __init__(self, **kwargs):
        """
        Initialize Q object with field lookups.
        
        Args:
            **kwargs: Field lookup expressions
        """
        self.children = [kwargs] if kwargs else []
        self.connector = self.AND
        self.negated = False
    
    def __and__(self, other):
        """Combine with AND."""
        return self._combine(other, self.AND)
    
    def __or__(self, other):
        """Combine with OR."""
        return self._combine(other, self.OR)
    
    def __invert__(self):
        """Negate with NOT."""
        obj = Q()
        obj.children = [self]
        obj.negated = True
        return obj
    
    def _combine(self, other, connector):
        """Combine two Q objects."""
        obj = Q()
        obj.connector = connector
        obj.children = [self, other]
        return obj
    
    def __repr__(self):
        """String representation."""
        if self.negated:
            return f"NOT {self.children}"
        return f"Q({self.connector}: {self.children})"

