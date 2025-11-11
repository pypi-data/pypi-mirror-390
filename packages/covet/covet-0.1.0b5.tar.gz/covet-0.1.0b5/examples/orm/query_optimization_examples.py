"""
Query Optimization Examples

Demonstrates the use of CovetPy's query optimization features including
optimizer, explain analyzer, index advisor, cache, profiler, and batch operations.
"""

import asyncio
from datetime import datetime

# Import ORM and optimization tools
from covet.database.orm import (
    Model,
    CharField,
    EmailField,
    IntegerField,
    DateTimeField,
    ForeignKey,
)

from covet.database.orm.optimizer import QueryOptimizer, OptimizationLevel
from covet.database.orm.explain import ExplainAnalyzer
from covet.database.orm.index_advisor import IndexAdvisor
from covet.database.orm.query_cache import QueryCache, CacheConfig
from covet.database.orm.profiler import QueryProfiler, ProfilerConfig
from covet.database.orm.batch_operations import BatchOperations, BatchConfig


# Define sample models
class User(Model):
    """User model."""

    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    age = IntegerField(null=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]


class Post(Model):
    """Post model."""

    title = CharField(max_length=200)
    content = CharField(max_length=5000)
    author = ForeignKey(User, on_delete="CASCADE", related_name="posts")
    published = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "posts"


# Example 1: Query Optimization
async def example_query_optimization(adapter):
    """Demonstrate query optimizer usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Query Optimization")
    print("=" * 80)

    # Initialize optimizer
    optimizer = QueryOptimizer(
        database="postgresql",
        optimization_level=OptimizationLevel.MODERATE,
    )

    # Analyze a query
    sql = """
        SELECT u.*, p.title, p.content
        FROM users u
        INNER JOIN posts p ON u.id = p.author_id
        WHERE u.is_active = true
        AND p.published = true
        ORDER BY p.created_at DESC
        LIMIT 10
    """

    print("\nAnalyzing query...")
    analysis = optimizer.analyze_query(sql)

    print(f"Complexity: {analysis.complexity.value}")
    print(f"Estimated cost: {analysis.estimated_cost:.2f}")
    print(f"Tables: {analysis.table_count}, JOINs: {analysis.join_count}")
    print(f"Uses index: {analysis.uses_index}")
    print(f"Warnings: {len(analysis.warnings)}")

    for warning in analysis.warnings:
        print(f"  - {warning}")

    # Optimize the query
    print("\nOptimizing query...")
    result = optimizer.optimize_query(sql)

    print(f"Optimizations applied: {', '.join(result.optimizations_applied)}")
    print(f"Estimated improvement: {result.estimated_improvement:.1f}%")

    # Get recommendations
    recommendations = optimizer.get_recommendations(sql)
    print(f"\nRecommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec}")

    # Show statistics
    stats = optimizer.get_statistics()
    print(f"\nOptimizer statistics:")
    print(f"  Queries analyzed: {stats['queries_analyzed']}")
    print(f"  Cache hit rate: {stats['cache_hit_rate']:.1f}%")


# Example 2: EXPLAIN Analysis
async def example_explain_analysis(adapter):
    """Demonstrate EXPLAIN analyzer usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: EXPLAIN Analysis")
    print("=" * 80)

    # Initialize analyzer
    analyzer = ExplainAnalyzer(database_adapter=adapter)

    # Analyze query plan
    sql = "SELECT * FROM users WHERE email = $1"
    params = ["user@example.com"]

    print("\nExecuting EXPLAIN...")
    try:
        plan = await analyzer.explain_query(sql, params)

        print(f"Total cost: {plan.total_cost:.2f}")
        print(f"Estimated rows: {plan.estimated_rows}")
        print(f"Uses index: {plan.uses_index}")

        if plan.index_names:
            print(f"Indexes used: {', '.join(plan.index_names)}")

        if plan.sequential_scans:
            print(f"WARNING: Sequential scans on: {', '.join(plan.sequential_scans)}")

        # Visualize plan
        print("\n" + analyzer.visualize_plan(plan))

    except Exception as e:
        print(f"EXPLAIN analysis failed (adapter may not be connected): {e}")


# Example 3: Index Recommendations
async def example_index_advisor(adapter):
    """Demonstrate index advisor usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Index Advisor")
    print("=" * 80)

    # Initialize advisor
    advisor = IndexAdvisor(database_adapter=adapter)

    # Analyze workload
    workload = [
        "SELECT * FROM users WHERE email = $1",
        "SELECT * FROM users WHERE age > 18",
        "SELECT * FROM posts WHERE author_id = $1 AND published = true",
        "SELECT * FROM posts WHERE author_id = $1 ORDER BY created_at DESC",
    ]

    print(f"\nAnalyzing workload of {len(workload)} queries...")
    await advisor.analyze_workload(workload)

    # Get recommendations
    print("\nGenerating index recommendations...")
    try:
        recommendations = await advisor.get_recommendations()

        print(f"\nFound {len(recommendations)} recommendations:")

        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            print(f"\n{i}. {rec.priority.value.upper()} Priority")
            print(f"   Table: {rec.table_name}")
            print(f"   Columns: {', '.join(rec.column_names)}")
            print(f"   Type: {rec.index_type.value}")
            print(f"   Estimated improvement: {rec.estimated_improvement:.1f}%")
            print(f"   Reason: {rec.reason}")
            print(f"   SQL: {rec.create_statement}")

    except Exception as e:
        print(f"Index recommendations failed (adapter may not be connected): {e}")

    # Show statistics
    stats = advisor.get_statistics()
    print(f"\nAdvisor statistics:")
    print(f"  Queries analyzed: {stats['queries_analyzed']}")
    print(f"  Unique patterns: {stats['unique_query_patterns']}")
    print(f"  Columns tracked: {stats['columns_tracked']}")


# Example 4: Query Caching
async def example_query_cache():
    """Demonstrate query caching usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Query Caching")
    print("=" * 80)

    # Initialize cache
    config = CacheConfig(
        backend="memory",
        default_ttl=300,
        max_size=1000,
    )
    cache = QueryCache(config)

    # Manual caching
    print("\nManual cache operations...")
    await cache.set("user:1", {"id": 1, "name": "Alice"}, ttl=60)
    result = await cache.get("user:1")
    print(f"Cached value: {result}")

    # Using decorator
    print("\nUsing cached decorator...")

    @cache.cached(ttl=120, invalidate_on=["User"])
    async def get_user_by_email(email: str):
        print(f"  [DB] Fetching user with email: {email}")
        # Simulate database query
        await asyncio.sleep(0.1)
        return {"email": email, "name": "Bob"}

    # First call - executes function
    user1 = await get_user_by_email("bob@example.com")
    print(f"Result 1: {user1}")

    # Second call - uses cache
    user2 = await get_user_by_email("bob@example.com")
    print(f"Result 2: {user2}")

    # Invalidate model cache
    print("\nInvalidating User model cache...")
    await cache.invalidate_model("User")

    # Third call - cache miss, re-executes
    user3 = await get_user_by_email("bob@example.com")
    print(f"Result 3: {user3}")

    # Show statistics
    stats = cache.get_statistics()
    print(f"\nCache statistics:")
    print(f"  Hits: {stats['hits']}")
    print(f"  Misses: {stats['misses']}")
    print(f"  Hit rate: {stats['hit_rate']:.1f}%")
    print(f"  Sets: {stats['sets']}")

    await cache.close()


# Example 5: Query Profiling
async def example_query_profiler():
    """Demonstrate query profiler usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Query Profiling")
    print("=" * 80)

    # Initialize profiler
    config = ProfilerConfig(
        slow_query_threshold=50.0,  # 50ms
        enable_n_plus_one_detection=True,
    )
    profiler = QueryProfiler(config)

    # Profile queries
    print("\nProfiling queries...")

    # Fast query
    async with profiler.profile_query_async(
        "get_user",
        sql="SELECT * FROM users WHERE id = $1",
    ):
        await asyncio.sleep(0.01)  # Simulate fast query

    # Slow query
    async with profiler.profile_query_async(
        "complex_report",
        sql="SELECT u.*, COUNT(p.*) FROM users u JOIN posts p ...",
    ):
        await asyncio.sleep(0.06)  # Simulate slow query

    # Simulate N+1 pattern
    print("\nSimulating N+1 query pattern...")
    for i in range(5):
        async with profiler.profile_query_async(
            f"get_posts_{i}",
            sql="SELECT * FROM posts WHERE author_id = $1",
        ):
            await asyncio.sleep(0.005)

    # Get slow queries
    slow_queries = profiler.get_slow_queries()
    print(f"\nSlow queries detected: {len(slow_queries)}")
    for query in slow_queries:
        print(f"  - {query.query_id}: {query.duration_ms:.2f}ms")

    # Detect N+1 patterns
    n_plus_one = profiler.detect_n_plus_one()
    print(f"\nN+1 patterns detected: {len(n_plus_one)}")
    for pattern in n_plus_one:
        print(f"  - {pattern['query'][:60]}...")
        print(f"    Count: {pattern['count']}, Total time: {pattern['total_duration_ms']:.2f}ms")

    # Show statistics
    stats = profiler.get_statistics()
    print(f"\nProfiler statistics:")
    print(f"  Total queries: {stats['total_queries']}")
    print(f"  Slow queries: {stats['slow_queries']} ({stats['slow_query_rate']*100:.1f}%)")
    print(f"  Avg duration: {stats['avg_duration_ms']:.2f}ms")
    print(f"  Query types: {stats['queries_by_type']}")


# Example 6: Batch Operations
async def example_batch_operations(adapter):
    """Demonstrate batch operations usage."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Batch Operations")
    print("=" * 80)

    # Initialize batch operations
    config = BatchConfig(
        batch_size=1000,
        enable_progress_tracking=True,
    )
    batch_ops = BatchOperations(database_adapter=adapter, config=config)

    # Bulk insert
    print("\nBulk insert example...")
    users = [
        {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "age": 20 + (i % 50),
        }
        for i in range(10000)
    ]

    def progress_callback(current, total):
        pct = (current / total) * 100
        print(f"  Progress: {current}/{total} batches ({pct:.1f}%)")

    try:
        result = await batch_ops.bulk_insert(
            table="users",
            records=users,
            batch_size=1000,
            on_progress=progress_callback,
        )

        print(f"\nBulk insert results:")
        print(f"  Success: {result.success}")
        print(f"  Rows affected: {result.rows_affected}")
        print(f"  Duration: {result.duration_seconds:.2f}s")
        print(f"  Throughput: {result.rows_per_second:.0f} rows/sec")
        print(f"  Batches: {result.batches_processed}")

    except Exception as e:
        print(f"Bulk insert failed (adapter may not be connected): {e}")

    # Bulk update
    print("\nBulk update example...")
    updates = [
        {"id": i, "age": 25 + (i % 40)}
        for i in range(1, 1001)
    ]

    try:
        result = await batch_ops.bulk_update(
            table="users",
            updates=updates,
            key_column="id",
            batch_size=500,
        )

        print(f"\nBulk update results:")
        print(f"  Rows updated: {result.rows_affected}")
        print(f"  Duration: {result.duration_seconds:.2f}s")

    except Exception as e:
        print(f"Bulk update failed: {e}")

    # Show statistics
    stats = batch_ops.get_statistics()
    print(f"\nBatch operations statistics:")
    print(f"  Total operations: {stats['total_operations']}")
    print(f"  Rows affected: {stats['total_rows_affected']}")
    print(f"  Avg throughput: {stats['avg_throughput_rows_per_second']:.0f} rows/sec")
    print(f"  Success rate: {stats['success_rate']:.1f}%")


# Main execution
async def main():
    """Run all examples."""
    print("=" * 80)
    print("CovetPy ORM Query Optimization Examples")
    print("=" * 80)

    # Note: In production, you would initialize a real database adapter
    # For this example, we'll use a mock adapter for most operations
    adapter = None  # Would be: PostgreSQLAdapter(config) in production

    # Run examples
    await example_query_optimization(adapter)
    # await example_explain_analysis(adapter)  # Requires real DB connection
    # await example_index_advisor(adapter)  # Requires real DB connection
    await example_query_cache()
    await example_query_profiler()
    # await example_batch_operations(adapter)  # Requires real DB connection

    print("\n" + "=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
