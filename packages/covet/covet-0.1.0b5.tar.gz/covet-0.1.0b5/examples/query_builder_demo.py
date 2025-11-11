#!/usr/bin/env python
"""
Query Builder Demo

Demonstrates the production-quality query builder capabilities.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from covet.database.core.database_config import DatabaseType
from covet.database.query_builder.builder import QueryBuilder
from covet.database.query_builder.expressions import Field, Function


def main():
    print("=" * 80)
    print("CovetPy Query Builder Demo")
    print("=" * 80)
    print()

    # Example 1: Simple SELECT query
    print("1. Simple SELECT Query (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .select('id', 'name', 'email')
        .where({'status': 'active'})
        .order_by('name')
        .limit(10)
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 2: Complex query with JOIN
    print("2. Complex Query with JOIN (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .select('users.name', 'profiles.bio', 'orders.total')
        .left_join('profiles', 'users.id = profiles.user_id')
        .left_join('orders', 'users.id = orders.user_id')
        .where({'users.status': 'active'})
        .order_by('users.created_at', 'DESC')
        .limit(50)
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 3: INSERT query
    print("3. INSERT Query (MySQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.MYSQL)
    query = builder.insert({
        'name': 'John Doe',
        'email': 'john@example.com',
        'status': 'active'
    }).compile()

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 4: UPSERT query (PostgreSQL)
    print("4. UPSERT Query (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = builder.upsert(
        {'email': 'john@example.com', 'name': 'John Updated', 'age': 30},
        conflict_columns=['email']
    ).compile()

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 5: UPDATE query
    print("5. UPDATE Query (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .update({'name': 'Jane Doe', 'status': 'inactive'})
        .where({'id': 1})
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 6: DELETE query
    print("6. DELETE Query (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .delete()
        .where({'status': 'deleted'})
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 7: Aggregation with GROUP BY
    print("7. Aggregation with GROUP BY (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .select(
            'department',
            Function('COUNT', Field('id')),
            Function('AVG', Field('salary'))
        )
        .group_by('department')
        .having('COUNT(id) > 5')
        .order_by(Function('COUNT', Field('id')), 'DESC')
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 8: Expression-based WHERE conditions
    print("8. Expression-based WHERE (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .select('name', 'age', 'email')
        .where({'status': 'active'})
        .and_where(Field('age') > 18)
        .or_where({'role': 'admin'})
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print()

    # Example 9: Pagination
    print("9. Pagination (PostgreSQL)")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    query = (builder
        .select('id', 'name')
        .where({'status': 'active'})
        .order_by('created_at', 'DESC')
        .paginate(page=3, per_page=25)
        .compile())

    print(f"SQL: {query.sql}")
    print(f"Parameters: {query.parameters}")
    print(f"Explanation: Shows page 3, with 25 items per page (OFFSET 50, LIMIT 25)")
    print()

    # Example 10: Multi-database compatibility
    print("10. Multi-Database Compatibility")
    print("-" * 40)

    # PostgreSQL
    pg_builder = QueryBuilder('users', DatabaseType.POSTGRESQL)
    pg_query = pg_builder.select('name').where({'id': 1}).limit(10).compile()
    print(f"PostgreSQL: {pg_query.sql}")
    print(f"Parameters: {pg_query.parameters}")

    # MySQL
    mysql_builder = QueryBuilder('users', DatabaseType.MYSQL)
    mysql_query = mysql_builder.select('name').where({'id': 1}).limit(10).compile()
    print(f"MySQL:      {mysql_query.sql}")
    print(f"Parameters: {mysql_query.parameters}")

    # SQLite
    sqlite_builder = QueryBuilder('users', DatabaseType.SQLITE)
    sqlite_query = sqlite_builder.select('name').where({'id': 1}).limit(10).compile()
    print(f"SQLite:     {sqlite_query.sql}")
    print(f"Parameters: {sqlite_query.parameters}")
    print()

    # Performance stats
    print("11. Performance Statistics")
    print("-" * 40)
    builder = QueryBuilder('users', DatabaseType.POSTGRESQL)

    # Compile multiple queries
    for i in range(100):
        builder.select('name').where({'id': i}).compile()

    stats = builder.get_performance_stats()
    print(f"Queries compiled: {stats['execution_count']}")
    print(f"Average compile time: {stats['avg_compile_time']*1000:.3f} ms")
    print(f"Min compile time: {stats['min_compile_time']*1000:.3f} ms")
    print(f"Max compile time: {stats['max_compile_time']*1000:.3f} ms")
    print()

    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == '__main__':
    main()
