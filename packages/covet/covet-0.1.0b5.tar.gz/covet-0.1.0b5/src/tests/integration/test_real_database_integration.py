"""
Real Database Integration Tests for CovetPy

These tests validate database operations against REAL database instances,
not mocks. They test actual CRUD operations, transactions, connection pooling,
and performance characteristics with real data flows.

CRITICAL: These tests use real databases with test schemas to ensure
production-grade database integration functionality.
"""

import asyncio
import time
import uuid
from datetime import datetime, timedelta

import pytest

from covet.testing import DatabaseTestHelper, PerformanceTestHelper


@pytest.mark.database
@pytest.mark.integration
@pytest.mark.real_backend
class TestRealDatabaseCRUD:
    """Test real CRUD operations against actual database."""

    async def test_user_crud_operations(
        self, database_helper: DatabaseTestHelper, database_connection
    ):
        """Test complete user CRUD cycle with real database."""
        # Create user
        user_data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password_hash": "$2b$12$test_hash",
            "is_active": True,
        }

        # INSERT - Create user
        async with database_connection.transaction():
            user_id = await database_connection.fetchval(
                """
                INSERT INTO users (username, email, password_hash, is_active)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                user_data["username"],
                user_data["email"],
                user_data["password_hash"],
                user_data["is_active"],
            )

        assert user_id is not None
        assert isinstance(user_id, int)

        # SELECT - Read user
        user_record = await database_connection.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )

        assert user_record is not None
        assert user_record["username"] == user_data["username"]
        assert user_record["email"] == user_data["email"]
        assert user_record["is_active"] is True
        assert user_record["created_at"] is not None

        # UPDATE - Modify user
        new_email = f"updated_{uuid.uuid4().hex[:8]}@example.com"
        updated_rows = await database_connection.execute(
            """
            UPDATE users
            SET email = $1, updated_at = NOW()
            WHERE id = $2
            """,
            new_email,
            user_id,
        )

        assert updated_rows == "UPDATE 1"

        # Verify update
        updated_user = await database_connection.fetchrow(
            "SELECT email, updated_at FROM users WHERE id = $1", user_id
        )

        assert updated_user["email"] == new_email
        assert updated_user["updated_at"] > user_record["created_at"]

        # DELETE - Remove user
        deleted_rows = await database_connection.execute(
            "DELETE FROM users WHERE id = $1", user_id
        )

        assert deleted_rows == "DELETE 1"

        # Verify deletion
        deleted_user = await database_connection.fetchrow(
            "SELECT * FROM users WHERE id = $1", user_id
        )

        assert deleted_user is None

    async def test_complex_queries_with_joins(
        self, database_helper: DatabaseTestHelper, database_connection
    ):
        """Test complex queries with JOINs using real data."""
        # Create test users
        users = await database_helper.create_test_users(count=3)
        user_ids = [user["id"] for user in users]

        # Create test projects for users
        await database_helper.create_test_projects(
            user_ids, projects_per_user=2
        )

        # Complex query with JOIN
        results = await database_connection.fetch(
            """
            SELECT
                u.username,
                u.email,
                COUNT(p.id) as project_count,
                ARRAY_AGG(p.name) as project_names
            FROM users u
            LEFT JOIN projects p ON u.id = p.owner_id
            WHERE u.id = ANY($1)
            GROUP BY u.id, u.username, u.email
            ORDER BY u.username
            """,
            user_ids,
        )

        assert len(results) == 3

        for result in results:
            assert result["project_count"] == 2
            assert len(result["project_names"]) == 2
            assert all(name is not None for name in result["project_names"])

    async def test_database_transactions_real(self, database_connection):
        """Test real database transactions with rollback scenarios."""
        # Test successful transaction
        async with database_connection.transaction():
            user_id = await database_connection.fetchval(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                f"tx_user_{uuid.uuid4().hex[:8]}",
                f"tx_{uuid.uuid4().hex[:8]}@example.com",
                "$2b$12$test_hash",
            )

            project_id = await database_connection.fetchval(
                """
                INSERT INTO projects (name, description, owner_id)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                f"Test Project {uuid.uuid4().hex[:8]}",
                "Transaction test project",
                user_id,
            )

        # Verify both records exist
        user_exists = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE id = $1", user_id
        )
        project_exists = await database_connection.fetchval(
            "SELECT COUNT(*) FROM projects WHERE id = $1", project_id
        )

        assert user_exists == 1
        assert project_exists == 1

        # Test transaction rollback
        rollback_user_id = None
        rollback_project_id = None

        try:
            async with database_connection.transaction():
                rollback_user_id = await database_connection.fetchval(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    f"rollback_user_{uuid.uuid4().hex[:8]}",
                    f"rollback_{uuid.uuid4().hex[:8]}@example.com",
                    "$2b$12$test_hash",
                )

                rollback_project_id = await database_connection.fetchval(
                    """
                    INSERT INTO projects (name, description, owner_id)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    f"Rollback Project {uuid.uuid4().hex[:8]}",
                    "This should be rolled back",
                    rollback_user_id,
                )

                # Force rollback by raising exception
                raise ValueError("Intentional rollback")

        except ValueError:
            pass  # Expected

        # Verify rollback - records should not exist
        user_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE id = $1", rollback_user_id
        )
        project_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM projects WHERE id = $1", rollback_project_id
        )

        assert user_count == 0
        assert project_count == 0

    async def test_concurrent_database_access(self, database_connection):
        """Test concurrent database access and connection handling."""

        async def create_user_concurrently(index: int):
            """Create a user concurrently."""
            username = f"concurrent_user_{index}_{uuid.uuid4().hex[:8]}"
            email = f"concurrent_{index}_{uuid.uuid4().hex[:8]}@example.com"

            user_id = await database_connection.fetchval(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                username,
                email,
                "$2b$12$test_hash",
            )

            return user_id

        # Create multiple users concurrently
        num_concurrent = 10
        tasks = [create_user_concurrently(i) for i in range(num_concurrent)]

        start_time = time.time()
        user_ids = await asyncio.gather(*tasks)
        end_time = time.time()

        # Verify all users were created
        assert len(user_ids) == num_concurrent
        assert all(user_id is not None for user_id in user_ids)
        assert len(set(user_ids)) == num_concurrent  # All unique

        # Verify performance - should complete reasonably quickly
        total_time = end_time - start_time
        assert total_time < 5.0, f"Concurrent operations too slow: {total_time:.2f}s"

        # Verify all users exist in database
        existing_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE id = ANY($1)", user_ids
        )

        assert existing_count == num_concurrent

    async def test_database_performance_benchmarks(
        self, database_connection, performance_helper: PerformanceTestHelper
    ):
        """Test database performance benchmarks with real operations."""

        # Benchmark INSERT performance
        insert_durations = []
        for i in range(100):
            start_time = time.perf_counter()

            await database_connection.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                """,
                f"perf_user_{i}_{uuid.uuid4().hex[:8]}",
                f"perf_{i}_{uuid.uuid4().hex[:8]}@example.com",
                "$2b$12$test_hash",
            )

            end_time = time.perf_counter()
            insert_durations.append((end_time - start_time) * 1000)

        # Analyze performance
        avg_insert_time = sum(insert_durations) / len(insert_durations)
        max_insert_time = max(insert_durations)
        p95_insert_time = sorted(insert_durations)[int(len(insert_durations) * 0.95)]

        # Performance assertions
        assert (
            avg_insert_time < 10.0
        ), f"Average insert too slow: {avg_insert_time:.2f}ms"
        assert p95_insert_time < 50.0, f"P95 insert too slow: {p95_insert_time:.2f}ms"

        # Record performance metrics
        performance_helper.measurements.append(
            {
                "test": "database_insert_performance",
                "avg_ms": avg_insert_time,
                "max_ms": max_insert_time,
                "p95_ms": p95_insert_time,
                "operations": len(insert_durations),
            }
        )

    async def test_database_bulk_operations(self, database_connection):
        """Test bulk database operations for efficiency."""
        # Prepare bulk data
        users_data = [
            (
                f"bulk_user_{i}_{uuid.uuid4().hex[:8]}",
                f"bulk_{i}_{uuid.uuid4().hex[:8]}@example.com",
                "$2b$12$test_hash",
                True,
            )
            for i in range(1000)
        ]

        # Benchmark bulk insert
        start_time = time.perf_counter()

        await database_connection.executemany(
            """
            INSERT INTO users (username, email, password_hash, is_active)
            VALUES ($1, $2, $3, $4)
            """,
            users_data,
        )

        end_time = time.perf_counter()
        bulk_insert_time = end_time - start_time

        # Verify all records inserted
        bulk_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE username LIKE 'bulk_user_%'"
        )

        assert bulk_count == 1000

        # Performance assertion - bulk operations should be efficient
        assert bulk_insert_time < 5.0, f"Bulk insert too slow: {bulk_insert_time:.2f}s"

        # Calculate operations per second
        ops_per_second = 1000 / bulk_insert_time
        assert (
            ops_per_second > 200
        ), f"Bulk insert throughput too low: {ops_per_second:.0f} ops/s"

    async def test_database_connection_pooling(self, database_connection):
        """Test database connection pooling behavior."""

        # Simulate multiple concurrent database operations
        async def perform_database_work(worker_id: int):
            """Perform database work to test connection pooling."""
            for i in range(10):
                # Each operation should get a connection from the pool
                user_id = await database_connection.fetchval(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    f"pool_worker_{worker_id}_op_{i}_{uuid.uuid4().hex[:8]}",
                    f"pool_{worker_id}_{i}_{uuid.uuid4().hex[:8]}@example.com",
                    "$2b$12$test_hash",
                )

                # Verify the insert
                user_exists = await database_connection.fetchval(
                    "SELECT COUNT(*) FROM users WHERE id = $1", user_id
                )
                assert user_exists == 1

                # Small delay to simulate work
                await asyncio.sleep(0.001)

        # Run multiple workers concurrently
        num_workers = 20
        tasks = [perform_database_work(worker_id) for worker_id in range(num_workers)]

        start_time = time.time()
        await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time
        total_operations = num_workers * 10

        # Verify all operations completed
        pool_user_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE username LIKE 'pool_worker_%'"
        )

        assert pool_user_count == total_operations

        # Performance check - should handle concurrent load efficiently
        ops_per_second = total_operations / total_time
        assert (
            ops_per_second > 50
        ), f"Connection pool throughput too low: {ops_per_second:.0f} ops/s"

    async def test_database_error_handling(self, database_connection):
        """Test database error handling with real constraints."""
        # Test unique constraint violation
        username = f"unique_test_{uuid.uuid4().hex[:8]}"
        email = f"unique_{uuid.uuid4().hex[:8]}@example.com"

        # First insert should succeed
        user_id = await database_connection.fetchval(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            username,
            email,
            "$2b$12$test_hash",
        )

        assert user_id is not None

        # Second insert with same username should fail
        with pytest.raises(Exception) as exc_info:
            await database_connection.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                """,
                username,  # Duplicate username
                f"different_{uuid.uuid4().hex[:8]}@example.com",
                "$2b$12$test_hash",
            )

        # Should be a unique constraint violation
        assert (
            "unique" in str(exc_info.value).lower()
            or "duplicate" in str(exc_info.value).lower()
        )

    async def test_database_data_types_handling(self, database_connection):
        """Test handling of various PostgreSQL data types."""
        # Test JSONB data type
        metadata = {
            "preferences": {"theme": "dark", "language": "en"},
            "settings": {"notifications": True},
            "tags": ["python", "api", "web"],
        }

        user_id = await database_connection.fetchval(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            f"json_test_{uuid.uuid4().hex[:8]}",
            f"json_{uuid.uuid4().hex[:8]}@example.com",
            "$2b$12$test_hash",
        )

        # Create API key with JSONB permissions
        api_key_id = await database_connection.fetchval(
            """
            INSERT INTO api_keys (key_hash, user_id, name, permissions, expires_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            f"hash_{uuid.uuid4().hex}",
            user_id,
            "Test API Key",
            metadata,  # JSONB field
            datetime.utcnow() + timedelta(days=30),
        )

        # Retrieve and verify JSONB data
        api_key_record = await database_connection.fetchrow(
            "SELECT permissions FROM api_keys WHERE id = $1", api_key_id
        )

        assert api_key_record["permissions"] == metadata
        assert api_key_record["permissions"]["preferences"]["theme"] == "dark"
        assert "python" in api_key_record["permissions"]["tags"]

    async def test_database_aggregate_functions(
        self, database_helper: DatabaseTestHelper, database_connection
    ):
        """Test database aggregate functions with real data."""
        # Create test users and projects
        users = await database_helper.create_test_users(count=5)
        user_ids = [user["id"] for user in users]
        await database_helper.create_test_projects(
            user_ids, projects_per_user=3
        )

        # Insert test metrics
        await database_helper.insert_test_metrics(count=100)

        # Test various aggregate functions
        stats = await database_connection.fetchrow(
            """
            SELECT
                COUNT(*) as total_users,
                (SELECT COUNT(*) FROM projects) as total_projects,
                (SELECT COUNT(*) FROM metrics) as total_metrics,
                (SELECT AVG(metric_value) FROM metrics) as avg_metric_value,
                (SELECT MAX(metric_value) FROM metrics) as max_metric_value,
                (SELECT MIN(metric_value) FROM metrics) as min_metric_value
            FROM users
            WHERE id = ANY($1)
            """,
            user_ids,
        )

        assert stats["total_users"] == 5
        assert stats["total_projects"] == 15  # 5 users * 3 projects each
        assert stats["total_metrics"] >= 100
        assert stats["avg_metric_value"] is not None
        assert stats["max_metric_value"] >= stats["min_metric_value"]

    async def test_database_text_search(self, database_connection):
        """Test full-text search capabilities."""
        # Create projects with searchable content
        search_projects = [
            ("Python Web Framework", "A modern web framework built with Python"),
            ("API Documentation Tool", "Generate beautiful API documentation"),
            ("Database Migration Utility", "Handle database schema migrations"),
            ("JavaScript Testing Library", "Comprehensive testing tools for JS"),
        ]

        user_id = await database_connection.fetchval(
            """
            INSERT INTO users (username, email, password_hash)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            f"search_user_{uuid.uuid4().hex[:8]}",
            f"search_{uuid.uuid4().hex[:8]}@example.com",
            "$2b$12$test_hash",
        )

        project_ids = []
        for name, description in search_projects:
            project_id = await database_connection.fetchval(
                """
                INSERT INTO projects (name, description, owner_id)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                name,
                description,
                user_id,
            )
            project_ids.append(project_id)

        # Test text search queries
        python_projects = await database_connection.fetch(
            """
            SELECT name, description
            FROM projects
            WHERE to_tsvector('english', name || ' ' || description) @@ plainto_tsquery('english', 'Python')
            AND id = ANY($1)
            """,
            project_ids,
        )

        assert len(python_projects) >= 1
        assert any("Python" in project["name"] for project in python_projects)

        # Test partial word search
        api_projects = await database_connection.fetch(
            """
            SELECT name, description
            FROM projects
            WHERE name ILIKE '%API%' OR description ILIKE '%API%'
            AND id = ANY($1)
            """,
            project_ids,
        )

        assert len(api_projects) >= 1
        assert any("API" in project["name"] for project in api_projects)


@pytest.mark.database
@pytest.mark.integration
@pytest.mark.slow
class TestDatabaseStressTests:
    """Stress tests for database operations."""

    async def test_high_volume_inserts(self, database_connection):
        """Test high-volume insert operations."""
        num_inserts = 10000
        batch_size = 1000

        start_time = time.time()

        for batch_start in range(0, num_inserts, batch_size):
            batch_data = [
                (
                    f"stress_user_{i}_{uuid.uuid4().hex[:8]}",
                    f"stress_{i}_{uuid.uuid4().hex[:8]}@example.com",
                    "$2b$12$test_hash",
                )
                for i in range(batch_start, min(batch_start + batch_size, num_inserts))
            ]

            await database_connection.executemany(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                """,
                batch_data,
            )

        end_time = time.time()
        total_time = end_time - start_time

        # Verify all records inserted
        stress_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE username LIKE 'stress_user_%'"
        )

        assert stress_count == num_inserts

        # Performance assertion
        ops_per_second = num_inserts / total_time
        assert (
            ops_per_second > 1000
        ), f"High-volume insert throughput too low: {ops_per_second:.0f} ops/s"

    async def test_connection_exhaustion_recovery(self, database_connection):
        """Test recovery from connection exhaustion scenarios."""
        # This test would require access to connection pool configuration
        # For now, we'll test graceful handling of many concurrent operations

        async def intensive_database_work(worker_id: int):
            """Perform intensive database work."""
            for i in range(50):
                await database_connection.execute(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES ($1, $2, $3)
                    """,
                    f"intensive_worker_{worker_id}_op_{i}",
                    f"intensive_{worker_id}_{i}@example.com",
                    "$2b$12$test_hash",
                )

        # Launch many concurrent workers
        num_workers = 50
        tasks = [intensive_database_work(worker_id) for worker_id in range(num_workers)]

        # Should complete without connection errors
        await asyncio.gather(*tasks)

        # Verify all operations completed
        intensive_count = await database_connection.fetchval(
            "SELECT COUNT(*) FROM users WHERE username LIKE 'intensive_worker_%'"
        )

        assert intensive_count == num_workers * 50
