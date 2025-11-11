"""
ORM Manager System

Model managers for query execution, database operations, and relationship handling.
"""

import asyncio
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from .connection import DatabaseConnection, TransactionManager, get_connection_pool
from .exceptions import (
    DoesNotExist,
    IntegrityError,
    MultipleObjectsReturned,
    ORMError,
    QueryError,
)
from .fields import AutoField, Field, ForeignKey, RelationshipField
from .query import Aggregate, Q, QuerySet


class SQLCompiler:
    """SQL query compilation."""

    def __init__(self, engine: str):
        self.engine = engine

    def compile_select(self, queryset: QuerySet) -> Tuple[str, List[Any]]:
        """Compile SELECT query."""
        model_class = queryset.model_class
        table_name = model_class._meta.get_table_name()

        # SELECT clause
        if hasattr(queryset, "_values_fields"):
            # VALUES query
            if queryset._values_fields:
                select_fields = ", ".join(queryset._values_fields)
            else:
                select_fields = "*"
        elif hasattr(queryset, "_only_fields"):
            # ONLY query
            select_fields = ", ".join(queryset._only_fields)
        else:
            # All fields
            db_fields = [f.get_db_column() for f in model_class._meta.get_database_fields()]
            select_fields = ", ".join(db_fields)

        sql_parts = [f"SELECT {select_fields}"]
        params = []

        # FROM clause
        sql_parts.append(f"FROM {table_name}")

        # JOIN clauses for select_related
        for related_field in queryset._select_related:
            join_sql, join_params = self._compile_join(model_class, related_field)
            sql_parts.append(join_sql)
            params.extend(join_params)

        # WHERE clause
        where_sql, where_params = self._compile_where(queryset)
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        # GROUP BY clause
        if queryset._group_by:
            group_fields = ", ".join(queryset._group_by)
            sql_parts.append(f"GROUP BY {group_fields}")

        # HAVING clause
        if queryset._having:
            having_sql, having_params = self._compile_conditions(queryset._having)
            sql_parts.append(f"HAVING {having_sql}")
            params.extend(having_params)

        # ORDER BY clause
        if queryset._order_by:
            order_fields = []
            for field in queryset._order_by:
                if field.startswith("-"):
                    order_fields.append(f"{field[1:]} DESC")
                else:
                    order_fields.append(f"{field} ASC")
            sql_parts.append(f"ORDER BY {', '.join(order_fields)}")

        # LIMIT and OFFSET
        if queryset._limit is not None:
            if self.engine == "mysql":
                if queryset._offset:
                    sql_parts.append(f"LIMIT {queryset._offset}, {queryset._limit}")
                else:
                    sql_parts.append(f"LIMIT {queryset._limit}")
            else:
                sql_parts.append(f"LIMIT {queryset._limit}")
                if queryset._offset:
                    sql_parts.append(f"OFFSET {queryset._offset}")

        return " ".join(sql_parts), params

    def compile_insert(self, model_class, instances: List[Any]) -> Tuple[str, List[Any]]:
        """Compile INSERT query."""
        table_name = model_class._meta.get_table_name()
        db_fields = [
            f
            for f in model_class._meta.get_database_fields()
            if not f.primary_key or not isinstance(f, AutoField)
        ]

        field_names = [f.get_db_column() for f in db_fields]
        placeholders = ", ".join(["?" for _ in field_names])
        fields_sql = ", ".join(field_names)

        sql = f"INSERT INTO {table_name} ({fields_sql}) VALUES ({placeholders})"  # nosec B608 - table_name validated

        params = []
        for instance in instances:
            row_params = []
            for field in db_fields:
                if isinstance(field, ForeignKey):
                    # For ForeignKey, get the ID of the related object
                    related_obj = getattr(instance, field.name, None)
                    if related_obj is not None:
                        if hasattr(related_obj, "id"):
                            value = related_obj.id
                        elif hasattr(related_obj, "_meta") and related_obj._meta.pk_field:
                            value = getattr(related_obj, related_obj._meta.pk_field.name)
                        else:
                            value = related_obj  # Assume it's already an ID
                    else:
                        value = None
                else:
                    value = getattr(instance, field.name, None)
                row_params.append(field.to_database(value))
            params.append(row_params)

        return sql, params

    def compile_update(self, queryset: QuerySet, values: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Compile UPDATE query."""
        model_class = queryset.model_class
        table_name = model_class._meta.get_table_name()

        # SET clause
        set_clauses = []
        params = []

        for field_name, value in values.items():
            field = model_class._meta.get_field(field_name)
            if field:
                set_clauses.append(f"{field.get_db_column()} = ?")
                params.append(field.to_database(value))

        set_sql = ", ".join(set_clauses)
        sql_parts = [f"UPDATE {table_name} SET {set_sql}"]  # nosec B608 - table_name validated

        # WHERE clause
        where_sql, where_params = self._compile_where(queryset)
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        return " ".join(sql_parts), params

    def compile_delete(self, queryset: QuerySet) -> Tuple[str, List[Any]]:
        """Compile DELETE query."""
        table_name = queryset.model_class._meta.get_table_name()
        sql_parts = [f"DELETE FROM {table_name}"]  # nosec B608 - table_name validated
        params = []

        # WHERE clause
        where_sql, where_params = self._compile_where(queryset)
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        return " ".join(sql_parts), params

    def compile_count(self, queryset: QuerySet) -> Tuple[str, List[Any]]:
        """Compile COUNT query."""
        table_name = queryset.model_class._meta.get_table_name()
        sql_parts = ["SELECT COUNT(*)"]
        params = []

        sql_parts.append(f"FROM {table_name}")

        # WHERE clause
        where_sql, where_params = self._compile_where(queryset)
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        return " ".join(sql_parts), params

    def compile_aggregate(
        self, queryset: QuerySet, aggregates: Dict[str, Aggregate]
    ) -> Tuple[str, List[Any]]:
        """Compile aggregate query."""
        table_name = queryset.model_class._meta.get_table_name()

        # SELECT clause with aggregates
        select_parts = []
        params = []

        for alias, aggregate in aggregates.items():
            agg_sql, agg_params = aggregate.as_sql(self.engine)
            select_parts.append(f"{agg_sql} AS {alias}")
            params.extend(agg_params)

        select_sql = ", ".join(select_parts)
        sql_parts = [f"SELECT {select_sql}"]

        sql_parts.append(f"FROM {table_name}")

        # WHERE clause
        where_sql, where_params = self._compile_where(queryset)
        if where_sql:
            sql_parts.append(f"WHERE {where_sql}")
            params.extend(where_params)

        # GROUP BY clause
        if queryset._group_by:
            group_fields = ", ".join(queryset._group_by)
            sql_parts.append(f"GROUP BY {group_fields}")

        return " ".join(sql_parts), params

    def _compile_where(self, queryset: QuerySet) -> Tuple[str, List[Any]]:
        """Compile WHERE clause."""
        conditions = queryset._filters + [~q for q in queryset._excludes]
        if not conditions:
            return "", []

        return self._compile_conditions(conditions)

    def _compile_conditions(self, conditions: List[Q]) -> Tuple[str, List[Any]]:
        """Compile Q objects to SQL conditions."""
        if not conditions:
            return "", []

        condition_parts = []
        params = []

        for condition in conditions:
            cond_sql, cond_params = self._compile_q_object(condition)
            if cond_sql:
                condition_parts.append(cond_sql)
                params.extend(cond_params)

        if not condition_parts:
            return "", []

        sql = " AND ".join(f"({part})" for part in condition_parts)
        return sql, params

    def _compile_q_object(self, q: Q) -> Tuple[str, List[Any]]:
        """Compile a Q object to SQL."""
        parts = []
        params = []

        # Handle kwargs (direct field lookups)
        for field_name, value in q.kwargs.items():
            if "__" in field_name:
                field_path, lookup_type = field_name.rsplit("__", 1)
            else:
                field_path, lookup_type = field_name, "exact"

            # For now, simple field lookups
            if lookup_type == "exact":
                parts.append(f"{field_path} = ?")
                params.append(value)
            elif lookup_type == "isnull":
                if value:
                    parts.append(f"{field_path} IS NULL")
                else:
                    parts.append(f"{field_path} IS NOT NULL")
            elif lookup_type == "in":
                if value:
                    placeholders = ", ".join(["?" for _ in value])
                    parts.append(f"{field_path} IN ({placeholders})")
                    params.extend(value)
                else:
                    parts.append("1=0")  # Empty IN clause
            elif lookup_type == "gt":
                parts.append(f"{field_path} > ?")
                params.append(value)
            elif lookup_type == "gte":
                parts.append(f"{field_path} >= ?")
                params.append(value)
            elif lookup_type == "lt":
                parts.append(f"{field_path} < ?")
                params.append(value)
            elif lookup_type == "lte":
                parts.append(f"{field_path} <= ?")
                params.append(value)
            elif lookup_type == "contains":
                parts.append(f"{field_path} LIKE ?")
                params.append(f"%{value}%")
            elif lookup_type == "startswith":
                parts.append(f"{field_path} LIKE ?")
                params.append(f"{value}%")
            elif lookup_type == "endswith":
                parts.append(f"{field_path} LIKE ?")
                params.append(f"%{value}")

        # Handle child Q objects
        for child in q.children:
            if isinstance(child, Q):
                child_sql, child_params = self._compile_q_object(child)
                if child_sql:
                    parts.append(child_sql)
                    params.extend(child_params)

        if not parts:
            return "", []

        # Join with connector
        if q.connector == Q.AND:
            sql = " AND ".join(f"({part})" for part in parts)
        else:  # OR
            sql = " OR ".join(f"({part})" for part in parts)

        # Apply negation
        if q.negated:
            sql = f"NOT ({sql})"

        return sql, params

    def _compile_join(self, model_class, related_field: str) -> Tuple[str, List[Any]]:
        """Compile JOIN clause for select_related."""
        # Simplified JOIN compilation
        # In a full implementation, this would handle complex relationships
        return "", []


class Manager:
    """Model manager for database operations."""

    def __init__(self, model_class: Type["Model"]):
        self.model_class = model_class
        self.db = "default"

    def get_queryset(self) -> QuerySet:
        """Get a new QuerySet for this manager."""
        return QuerySet(self.model_class, using=self.db)

    def all(self) -> QuerySet:
        """Get all objects."""
        return self.get_queryset()

    def filter(self, *args, **kwargs) -> QuerySet:
        """Filter objects."""
        return self.get_queryset().filter(*args, **kwargs)

    def exclude(self, *args, **kwargs) -> QuerySet:
        """Exclude objects."""
        return self.get_queryset().exclude(*args, **kwargs)

    def get(self, *args, **kwargs):
        """Get a single object."""
        return self.get_queryset().get(*args, **kwargs)

    async def aget(self, *args, **kwargs):
        """Get a single object asynchronously."""
        return await self.get_queryset().aget(*args, **kwargs)

    def create(self, **kwargs):
        """Create and save a new object."""
        instance = self.model_class(**kwargs)
        return self.save_instance(instance)

    async def acreate(self, **kwargs):
        """Create and save a new object asynchronously."""
        instance = self.model_class(**kwargs)
        return await self.asave_instance(instance)

    def get_or_create(self, defaults=None, **kwargs):
        """Get object or create if it doesn't exist."""
        return self.get_queryset().get_or_create(defaults, **kwargs)

    async def aget_or_create(self, defaults=None, **kwargs):
        """Get object or create if it doesn't exist asynchronously."""
        return await self.get_queryset().aget_or_create(defaults, **kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        """Update object or create if it doesn't exist."""
        try:
            obj = self.get(**kwargs)
            if defaults:
                for key, value in defaults.items():
                    setattr(obj, key, value)
            return self.save_instance(obj), False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            return self.create(**create_kwargs), True

    async def aupdate_or_create(self, defaults=None, **kwargs):
        """Update object or create if it doesn't exist asynchronously."""
        try:
            obj = await self.aget(**kwargs)
            if defaults:
                for key, value in defaults.items():
                    setattr(obj, key, value)
            return await self.asave_instance(obj), False
        except DoesNotExist:
            create_kwargs = kwargs.copy()
            if defaults:
                create_kwargs.update(defaults)
            return await self.acreate(**create_kwargs), True

    def count(self, queryset: QuerySet = None) -> int:
        """Get count of objects."""
        if queryset is None:
            return self.get_queryset().count()

        pool = get_connection_pool(self.db)
        with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_count(queryset)
            cursor = conn.execute(sql, params)
            row = cursor.fetchone()
            return row[0] if row else 0

    async def acount(self, queryset: QuerySet = None) -> int:
        """Get count of objects asynchronously."""
        if queryset is None:
            return await self.get_queryset().acount()

        pool = get_connection_pool(self.db)
        async with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_count(queryset)
            cursor = await conn.aexecute(sql, params)
            row = await cursor.fetchone()
            return row[0] if row else 0

    def exists(self, queryset: QuerySet = None) -> bool:
        """Check if any objects exist."""
        if queryset is None:
            return self.get_queryset().exists()

        # Simplified exists check using count
        return self.count(queryset) > 0

    async def aexists(self, queryset: QuerySet = None) -> bool:
        """Check if any objects exist asynchronously."""
        if queryset is None:
            return await self.get_queryset().aexists()

        # Simplified exists check using count
        return await self.acount(queryset) > 0

    def execute_query(self, queryset: QuerySet) -> List[Any]:
        """Execute a queryset and return results."""
        pool = get_connection_pool(self.db)

        with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_select(queryset)

            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

            # Convert rows to model instances
            instances = []
            for row in rows:
                instance_data = dict(row)
                instance = self.model_class(**instance_data)
                instance._state.adding = False
                instances.append(instance)

            return instances

    async def aexecute_query(self, queryset: QuerySet) -> List[Any]:
        """Execute a queryset asynchronously and return results."""
        pool = get_connection_pool(self.db)

        async with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_select(queryset)

            cursor = await conn.aexecute(sql, params)
            rows = await cursor.fetchall()

            # Convert rows to model instances
            instances = []
            for row in rows:
                instance_data = dict(row)
                instance = self.model_class(**instance_data)
                instance._state.adding = False
                instances.append(instance)

            return instances

    def save_instance(self, instance, force_insert=False, force_update=False):
        """Save a model instance."""
        pool = get_connection_pool(self.db)

        with pool.connection() as conn:
            tx = TransactionManager(conn)

            with tx.transaction():
                if force_insert or instance._state.adding:
                    return self._insert_instance(instance, conn)
                elif force_update or not instance._state.adding:
                    return self._update_instance(instance, conn)
                else:
                    # Determine if insert or update
                    pk_field = self.model_class._meta.pk_field
                    if pk_field:
                        pk_value = getattr(instance, pk_field.name)
                        if pk_value is None:
                            return self._insert_instance(instance, conn)
                        else:
                            # Check if exists
                            existing = self.filter(**{pk_field.name: pk_value}).first()
                            if existing:
                                return self._update_instance(instance, conn)
                            else:
                                return self._insert_instance(instance, conn)
                    else:
                        return self._insert_instance(instance, conn)

    async def asave_instance(self, instance, force_insert=False, force_update=False):
        """Save a model instance asynchronously."""
        pool = get_connection_pool(self.db)

        async with pool.connection() as conn:
            tx = TransactionManager(conn)

            async with tx.atransaction():
                if force_insert or instance._state.adding:
                    return await self._ainsert_instance(instance, conn)
                elif force_update or not instance._state.adding:
                    return await self._aupdate_instance(instance, conn)
                else:
                    # Determine if insert or update
                    pk_field = self.model_class._meta.pk_field
                    if pk_field:
                        pk_value = getattr(instance, pk_field.name)
                        if pk_value is None:
                            return await self._ainsert_instance(instance, conn)
                        else:
                            # Check if exists
                            existing = await self.filter(**{pk_field.name: pk_value}).afirst()
                            if existing:
                                return await self._aupdate_instance(instance, conn)
                            else:
                                return await self._ainsert_instance(instance, conn)
                    else:
                        return await self._ainsert_instance(instance, conn)

    def _insert_instance(self, instance, conn: DatabaseConnection):
        """Insert a new instance."""
        compiler = SQLCompiler(conn.config.engine)
        sql, params = compiler.compile_insert(self.model_class, [instance])

        cursor = conn.execute(sql, params[0])

        # Set primary key if auto-generated
        pk_field = self.model_class._meta.pk_field
        if pk_field and pk_field.primary_key and hasattr(cursor, "lastrowid"):
            setattr(instance, pk_field.name, cursor.lastrowid)

        instance._state.adding = False
        return instance

    async def _ainsert_instance(self, instance, conn: DatabaseConnection):
        """Insert a new instance asynchronously."""
        compiler = SQLCompiler(conn.config.engine)
        sql, params = compiler.compile_insert(self.model_class, [instance])

        cursor = await conn.aexecute(sql, params[0])

        # Set primary key if auto-generated
        pk_field = self.model_class._meta.pk_field
        if pk_field and pk_field.primary_key and hasattr(cursor, "lastrowid"):
            setattr(instance, pk_field.name, cursor.lastrowid)

        instance._state.adding = False
        return instance

    def _update_instance(self, instance, conn: DatabaseConnection):
        """Update an existing instance."""
        pk_field = self.model_class._meta.pk_field
        if not pk_field:
            raise ORMError("Cannot update instance without primary key")

        pk_value = getattr(instance, pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot update instance with null primary key")

        # Build update values
        values = {}
        for field_name, field in self.model_class._meta.fields.items():
            if field_name != pk_field.name and not isinstance(field, RelationshipField):
                values[field_name] = getattr(instance, field_name)

        # Create queryset for this instance
        queryset = self.filter(**{pk_field.name: pk_value})

        # Execute update
        self.update(queryset, values)
        return instance

    async def _aupdate_instance(self, instance, conn: DatabaseConnection):
        """Update an existing instance asynchronously."""
        pk_field = self.model_class._meta.pk_field
        if not pk_field:
            raise ORMError("Cannot update instance without primary key")

        pk_value = getattr(instance, pk_field.name)
        if pk_value is None:
            raise ORMError("Cannot update instance with null primary key")

        # Build update values
        values = {}
        for field_name, field in self.model_class._meta.fields.items():
            if field_name != pk_field.name and not isinstance(field, RelationshipField):
                values[field_name] = getattr(instance, field_name)

        # Create queryset for this instance
        queryset = self.filter(**{pk_field.name: pk_value})

        # Execute update
        await self.aupdate(queryset, values)
        return instance

    def update(self, queryset: QuerySet, values: Dict[str, Any]) -> int:
        """Update multiple objects."""
        pool = get_connection_pool(self.db)

        with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_update(queryset, values)

            cursor = conn.execute(sql, params)
            conn.commit()

            return cursor.rowcount

    async def aupdate(self, queryset: QuerySet, values: Dict[str, Any]) -> int:
        """Update multiple objects asynchronously."""
        pool = get_connection_pool(self.db)

        async with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_update(queryset, values)

            cursor = await conn.aexecute(sql, params)
            await conn.acommit()

            return cursor.rowcount

    def delete(self, queryset: QuerySet) -> int:
        """Delete multiple objects."""
        pool = get_connection_pool(self.db)

        with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_delete(queryset)

            cursor = conn.execute(sql, params)
            conn.commit()

            return cursor.rowcount

    async def adelete(self, queryset: QuerySet) -> int:
        """Delete multiple objects asynchronously."""
        pool = get_connection_pool(self.db)

        async with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_delete(queryset)

            cursor = await conn.aexecute(sql, params)
            await conn.acommit()

            return cursor.rowcount

    def aggregate(self, queryset: QuerySet, aggregates: Dict[str, Aggregate]) -> Dict[str, Any]:
        """Perform aggregation."""
        pool = get_connection_pool(self.db)

        with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_aggregate(queryset, aggregates)

            cursor = conn.execute(sql, params)
            row = cursor.fetchone()

            return dict(row) if row else {}

    async def aaggregate(
        self, queryset: QuerySet, aggregates: Dict[str, Aggregate]
    ) -> Dict[str, Any]:
        """Perform aggregation asynchronously."""
        pool = get_connection_pool(self.db)

        async with pool.connection() as conn:
            compiler = SQLCompiler(conn.config.engine)
            sql, params = compiler.compile_aggregate(queryset, aggregates)

            cursor = await conn.aexecute(sql, params)
            row = await cursor.fetchone()

            return dict(row) if row else {}

    def bulk_create(
        self, objects: List[Any], batch_size: int = None, ignore_conflicts: bool = False
    ) -> List[Any]:
        """Bulk create objects."""
        if not objects:
            return []

        pool = get_connection_pool(self.db)
        batch_size = batch_size or 1000

        with pool.connection() as conn:
            tx = TransactionManager(conn)

            with tx.transaction():
                created_objects = []

                for i in range(0, len(objects), batch_size):
                    batch = objects[i : i + batch_size]

                    compiler = SQLCompiler(conn.config.engine)
                    sql, params = compiler.compile_insert(self.model_class, batch)

                    if ignore_conflicts:
                        if conn.config.engine == "postgresql":
                            sql += " ON CONFLICT DO NOTHING"
                        elif conn.config.engine == "mysql":
                            sql = sql.replace("INSERT INTO", "INSERT IGNORE INTO")
                        elif conn.config.engine == "sqlite":
                            sql = sql.replace("INSERT INTO", "INSERT OR IGNORE INTO")

                    for obj_params in params:
                        conn.execute(sql, obj_params)

                    created_objects.extend(batch)

                return created_objects

    async def abulk_create(
        self, objects: List[Any], batch_size: int = None, ignore_conflicts: bool = False
    ) -> List[Any]:
        """Bulk create objects asynchronously."""
        if not objects:
            return []

        pool = get_connection_pool(self.db)
        batch_size = batch_size or 1000

        async with pool.connection() as conn:
            tx = TransactionManager(conn)

            async with tx.atransaction():
                created_objects = []

                for i in range(0, len(objects), batch_size):
                    batch = objects[i : i + batch_size]

                    compiler = SQLCompiler(conn.config.engine)
                    sql, params = compiler.compile_insert(self.model_class, batch)

                    if ignore_conflicts:
                        if conn.config.engine == "postgresql":
                            sql += " ON CONFLICT DO NOTHING"
                        elif conn.config.engine == "mysql":
                            sql = sql.replace("INSERT INTO", "INSERT IGNORE INTO")
                        elif conn.config.engine == "sqlite":
                            sql = sql.replace("INSERT INTO", "INSERT OR IGNORE INTO")

                    for obj_params in params:
                        await conn.aexecute(sql, obj_params)

                    created_objects.extend(batch)

                return created_objects
