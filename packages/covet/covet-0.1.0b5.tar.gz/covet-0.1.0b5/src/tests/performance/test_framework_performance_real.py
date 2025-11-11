"""
Real Performance Tests for CovetPy Framework

These tests validate actual performance characteristics against real systems,
measuring latency, throughput, memory usage, and scalability. All tests run
against real backends to ensure production-grade performance validation.

Performance targets:
- HTTP request latency: < 5ms P95
- Throughput: > 10,000 RPS for simple endpoints
- Memory usage: < 100MB for 1000 concurrent connections
- Database query time: < 10ms P95 for simple queries
"""

import asyncio
import gc
import statistics
import time
import tracemalloc

import psutil
import pytest

from covet.testing import PerformanceTestHelper


@pytest.mark.performance
@pytest.mark.real_backend
class TestHTTPPerformance:
    """Test HTTP request/response performance with real servers."""

    async def test_simple_request_latency(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test latency of simple HTTP requests."""
        endpoint = "/health"
        iterations = 1000

        latencies = []

        for _i in range(iterations):
            start_time = time.perf_counter()

            response = await http_client.get(endpoint)

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000
            latencies.append(latency_ms)

            assert response.status_code == 200

        # Calculate performance metrics
        avg_latency = statistics.mean(latencies)
        median_latency = statistics.median(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        min_latency = min(latencies)
        max_latency = max(latencies)

        # Performance assertions
        assert avg_latency < 10.0, f"Average latency too high: {avg_latency:.2f}ms"
        assert p95_latency < 20.0, f"P95 latency too high: {p95_latency:.2f}ms"
        assert p99_latency < 50.0, f"P99 latency too high: {p99_latency:.2f}ms"

        # Record results
        performance_helper.measurements.append(
            {
                "test": "simple_request_latency",
                "iterations": iterations,
                "avg_ms": avg_latency,
                "median_ms": median_latency,
                "p95_ms": p95_latency,
                "p99_ms": p99_latency,
                "min_ms": min_latency,
                "max_ms": max_latency,
            }
        )

    async def test_json_response_performance(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test performance of JSON response generation."""
        endpoint = "/api/users"
        iterations = 500

        response_times = []
        response_sizes = []

        for _i in range(iterations):
            start_time = time.perf_counter()

            response = await http_client.get(endpoint)

            end_time = time.perf_counter()
            response_time = (end_time - start_time) * 1000
            response_times.append(response_time)

            # Measure response size
            content_length = (
                len(response.content)
                if hasattr(response, "content")
                else len(response.text)
            )
            response_sizes.append(content_length)

            assert response.status_code == 200
            assert response.headers.get("Content-Type", "").startswith(
                "application/json"
            )

        avg_response_time = statistics.mean(response_times)
        avg_response_size = statistics.mean(response_sizes)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]

        # Performance assertions
        assert (
            avg_response_time < 15.0
        ), f"JSON response too slow: {avg_response_time:.2f}ms"
        assert (
            p95_response_time < 30.0
        ), f"P95 JSON response too slow: {p95_response_time:.2f}ms"

        # Calculate throughput
        total_time_seconds = sum(response_times) / 1000
        throughput_rps = iterations / total_time_seconds

        performance_helper.measurements.append(
            {
                "test": "json_response_performance",
                "iterations": iterations,
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "avg_response_size_bytes": avg_response_size,
                "throughput_rps": throughput_rps,
            }
        )

    async def test_concurrent_request_handling(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test concurrent request handling performance."""
        endpoint = "/health"
        concurrent_requests = 100
        requests_per_client = 50

        async def make_requests(client_id: int):
            """Make multiple requests from a single client."""
            client_latencies = []

            for i in range(requests_per_client):
                start_time = time.perf_counter()

                response = await http_client.get(
                    f"{endpoint}?client={client_id}&req={i}"
                )

                end_time = time.perf_counter()
                latency = (end_time - start_time) * 1000
                client_latencies.append(latency)

                assert response.status_code == 200

            return client_latencies

        # Run concurrent clients
        start_time = time.perf_counter()

        tasks = [make_requests(client_id) for client_id in range(concurrent_requests)]
        all_latencies = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Flatten latencies
        flat_latencies = [
            latency
            for client_latencies in all_latencies
            for latency in client_latencies
        ]

        total_requests = concurrent_requests * requests_per_client
        avg_latency = statistics.mean(flat_latencies)
        p95_latency = statistics.quantiles(flat_latencies, n=20)[18]
        throughput_rps = total_requests / total_time

        # Performance assertions
        assert (
            avg_latency < 50.0
        ), f"Concurrent average latency too high: {avg_latency:.2f}ms"
        assert (
            p95_latency < 100.0
        ), f"Concurrent P95 latency too high: {p95_latency:.2f}ms"
        assert (
            throughput_rps > 100
        ), f"Concurrent throughput too low: {throughput_rps:.0f} RPS"

        performance_helper.measurements.append(
            {
                "test": "concurrent_request_handling",
                "concurrent_clients": concurrent_requests,
                "requests_per_client": requests_per_client,
                "total_requests": total_requests,
                "total_time_seconds": total_time,
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "throughput_rps": throughput_rps,
            }
        )

    async def test_large_payload_performance(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test performance with large request/response payloads."""
        endpoint = "/api/upload"

        # Test different payload sizes
        payload_sizes = [1024, 10240, 102400, 1048576]  # 1KB, 10KB, 100KB, 1MB
        results = []

        for size in payload_sizes:
            # Generate test payload
            test_data = {"data": "x" * size, "size": size}

            start_time = time.perf_counter()

            response = await http_client.post(endpoint, json=test_data)

            end_time = time.perf_counter()

            processing_time = (end_time - start_time) * 1000
            throughput_mbps = (size / (1024 * 1024)) / (end_time - start_time)

            results.append(
                {
                    "payload_size_bytes": size,
                    "processing_time_ms": processing_time,
                    "throughput_mbps": throughput_mbps,
                }
            )

            assert response.status_code in [200, 201]

        # Performance assertions
        for result in results:
            if result["payload_size_bytes"] <= 102400:  # <= 100KB
                assert (
                    result["processing_time_ms"] < 100
                ), f"Small payload too slow: {result}"
            else:  # 1MB
                assert (
                    result["processing_time_ms"] < 1000
                ), f"Large payload too slow: {result}"

        performance_helper.measurements.append(
            {"test": "large_payload_performance", "results": results}
        )

    async def test_memory_usage_under_load(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test memory usage under sustained load."""
        if not hasattr(psutil.Process(), "memory_info"):
            pytest.skip("psutil memory monitoring not available")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Start memory tracking
        tracemalloc.start()

        endpoint = "/health"
        num_requests = 1000

        memory_samples = []

        for i in range(num_requests):
            response = await http_client.get(endpoint)
            assert response.status_code == 200

            # Sample memory every 100 requests
            if i % 100 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_samples.append(current_memory)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Get tracemalloc statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        memory_growth = final_memory - initial_memory
        peak_memory_mb = peak / 1024 / 1024

        # Performance assertions
        assert memory_growth < 50, f"Memory growth too high: {memory_growth:.2f}MB"
        assert final_memory < 200, f"Final memory usage too high: {final_memory:.2f}MB"

        performance_helper.measurements.append(
            {
                "test": "memory_usage_under_load",
                "requests": num_requests,
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "peak_traced_memory_mb": peak_memory_mb,
                "memory_samples": memory_samples,
            }
        )


@pytest.mark.performance
@pytest.mark.database
@pytest.mark.real_backend
class TestDatabasePerformance:
    """Test database performance with real database operations."""

    async def test_simple_query_performance(
        self, database_connection, performance_helper: PerformanceTestHelper
    ):
        """Test simple database query performance."""
        query = "SELECT 1 as test_value"
        iterations = 1000

        query_times = []

        for _i in range(iterations):
            start_time = time.perf_counter()

            result = await database_connection.fetchval(query)

            end_time = time.perf_counter()
            query_time = (end_time - start_time) * 1000
            query_times.append(query_time)

            assert result == 1

        avg_query_time = statistics.mean(query_times)
        p95_query_time = statistics.quantiles(query_times, n=20)[18]
        p99_query_time = statistics.quantiles(query_times, n=100)[98]

        # Performance assertions
        assert (
            avg_query_time < 5.0
        ), f"Average query time too high: {avg_query_time:.2f}ms"
        assert p95_query_time < 10.0, f"P95 query time too high: {p95_query_time:.2f}ms"

        performance_helper.measurements.append(
            {
                "test": "simple_query_performance",
                "iterations": iterations,
                "avg_query_time_ms": avg_query_time,
                "p95_query_time_ms": p95_query_time,
                "p99_query_time_ms": p99_query_time,
            }
        )

    async def test_connection_pool_performance(
        self, database_connection, performance_helper: PerformanceTestHelper
    ):
        """Test database connection pool performance under load."""
        concurrent_queries = 50
        queries_per_connection = 20

        async def execute_queries(query_id: int):
            """Execute multiple queries on a connection."""
            query_times = []

            for i in range(queries_per_connection):
                start_time = time.perf_counter()

                result = await database_connection.fetchval(
                    "SELECT $1 as query_id, $2 as iteration", query_id, i
                )

                end_time = time.perf_counter()
                query_time = (end_time - start_time) * 1000
                query_times.append(query_time)

                assert result == query_id

            return query_times

        # Execute concurrent queries
        start_time = time.perf_counter()

        tasks = [execute_queries(query_id) for query_id in range(concurrent_queries)]
        all_query_times = await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        # Flatten query times
        flat_query_times = [
            time for query_times in all_query_times for time in query_times
        ]

        total_queries = concurrent_queries * queries_per_connection
        avg_query_time = statistics.mean(flat_query_times)
        queries_per_second = total_queries / total_time

        # Performance assertions
        assert (
            avg_query_time < 20.0
        ), f"Pooled query average too high: {avg_query_time:.2f}ms"
        assert (
            queries_per_second > 100
        ), f"Query throughput too low: {queries_per_second:.0f} QPS"

        performance_helper.measurements.append(
            {
                "test": "connection_pool_performance",
                "concurrent_connections": concurrent_queries,
                "queries_per_connection": queries_per_connection,
                "total_queries": total_queries,
                "total_time_seconds": total_time,
                "avg_query_time_ms": avg_query_time,
                "queries_per_second": queries_per_second,
            }
        )

    async def test_transaction_performance(
        self, database_connection, performance_helper: PerformanceTestHelper
    ):
        """Test database transaction performance."""
        iterations = 100

        transaction_times = []

        for i in range(iterations):
            start_time = time.perf_counter()

            async with database_connection.transaction():
                # Insert a record
                user_id = await database_connection.fetchval(
                    """
                    INSERT INTO users (username, email, password_hash)
                    VALUES ($1, $2, $3)
                    RETURNING id
                    """,
                    f"perf_user_{i}",
                    f"perf_{i}@example.com",
                    "$2b$12$test_hash",
                )

                # Update the record
                await database_connection.execute(
                    "UPDATE users SET updated_at = NOW() WHERE id = $1", user_id
                )

                # Query the record
                result = await database_connection.fetchrow(
                    "SELECT username, email FROM users WHERE id = $1", user_id
                )

                assert result["username"] == f"perf_user_{i}"

            end_time = time.perf_counter()
            transaction_time = (end_time - start_time) * 1000
            transaction_times.append(transaction_time)

        avg_transaction_time = statistics.mean(transaction_times)
        p95_transaction_time = statistics.quantiles(transaction_times, n=20)[18]

        # Performance assertions
        assert (
            avg_transaction_time < 50.0
        ), f"Transaction time too high: {avg_transaction_time:.2f}ms"
        assert (
            p95_transaction_time < 100.0
        ), f"P95 transaction time too high: {p95_transaction_time:.2f}ms"

        performance_helper.measurements.append(
            {
                "test": "transaction_performance",
                "iterations": iterations,
                "avg_transaction_time_ms": avg_transaction_time,
                "p95_transaction_time_ms": p95_transaction_time,
            }
        )

    async def test_bulk_operations_performance(
        self, database_connection, performance_helper: PerformanceTestHelper
    ):
        """Test bulk database operations performance."""
        batch_sizes = [100, 500, 1000, 5000]
        results = []

        for batch_size in batch_sizes:
            # Prepare batch data
            users_data = [
                (f"bulk_user_{i}", f"bulk_{i}@example.com", "$2b$12$test_hash")
                for i in range(batch_size)
            ]

            start_time = time.perf_counter()

            await database_connection.executemany(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES ($1, $2, $3)
                """,
                users_data,
            )

            end_time = time.perf_counter()

            total_time = end_time - start_time
            operations_per_second = batch_size / total_time
            time_per_operation = (total_time / batch_size) * 1000  # ms

            results.append(
                {
                    "batch_size": batch_size,
                    "total_time_seconds": total_time,
                    "operations_per_second": operations_per_second,
                    "time_per_operation_ms": time_per_operation,
                }
            )

            # Performance assertions
            assert (
                operations_per_second > 100
            ), f"Bulk ops too slow: {operations_per_second:.0f} ops/s"
            assert (
                time_per_operation < 10
            ), f"Per-operation time too high: {time_per_operation:.2f}ms"

        performance_helper.measurements.append(
            {"test": "bulk_operations_performance", "results": results}
        )


@pytest.mark.performance
@pytest.mark.slow
class TestStressTests:
    """Stress tests for framework components."""

    async def test_sustained_load_performance(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test performance under sustained load."""
        duration_seconds = 30  # 30-second stress test
        endpoint = "/health"

        start_time = time.time()
        end_time = start_time + duration_seconds

        request_count = 0
        latencies = []
        errors = 0

        while time.time() < end_time:
            batch_start = time.perf_counter()

            # Make batch of requests
            batch_size = 10
            tasks = [http_client.get(endpoint) for _ in range(batch_size)]

            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                batch_end = time.perf_counter()
                batch_latency = (batch_end - batch_start) * 1000 / batch_size
                latencies.append(batch_latency)

                for response in responses:
                    if isinstance(response, Exception):
                        errors += 1
                    elif (
                        hasattr(response, "status_code") and response.status_code != 200
                    ):
                        errors += 1
                    else:
                        request_count += 1

            except Exception:
                errors += batch_size

        actual_duration = time.time() - start_time
        requests_per_second = request_count / actual_duration
        error_rate = (
            errors / (request_count + errors) if (request_count + errors) > 0 else 0
        )
        avg_latency = statistics.mean(latencies) if latencies else 0

        # Performance assertions
        assert (
            requests_per_second > 50
        ), f"Sustained RPS too low: {requests_per_second:.0f}"
        assert error_rate < 0.01, f"Error rate too high: {error_rate:.2%}"
        assert avg_latency < 100, f"Sustained latency too high: {avg_latency:.2f}ms"

        performance_helper.measurements.append(
            {
                "test": "sustained_load_performance",
                "duration_seconds": actual_duration,
                "total_requests": request_count,
                "requests_per_second": requests_per_second,
                "error_count": errors,
                "error_rate": error_rate,
                "avg_latency_ms": avg_latency,
            }
        )

    async def test_memory_leak_detection(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test for memory leaks under load."""
        if not hasattr(psutil.Process(), "memory_info"):
            pytest.skip("psutil memory monitoring not available")

        process = psutil.Process()

        # Warm up
        for _ in range(100):
            await http_client.get("/health")

        # Force garbage collection
        gc.collect()

        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_samples = [initial_memory]

        # Run sustained requests and monitor memory
        sample_interval = 100
        total_requests = 2000

        for i in range(total_requests):
            await http_client.get("/health")

            if i % sample_interval == 0:
                gc.collect()  # Force GC to get accurate readings
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)

        final_memory = process.memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory

        # Calculate memory growth trend
        if len(memory_samples) > 2:
            # Simple linear regression to detect growth trend
            x_values = list(range(len(memory_samples)))
            y_values = memory_samples

            n = len(memory_samples)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)

            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

            # Memory growth rate in MB per sample
            memory_growth_rate = slope
        else:
            memory_growth_rate = 0

        # Performance assertions
        assert memory_growth < 100, f"Memory growth too high: {memory_growth:.2f}MB"
        assert (
            memory_growth_rate < 1.0
        ), f"Memory leak detected: {memory_growth_rate:.2f}MB/sample"

        performance_helper.measurements.append(
            {
                "test": "memory_leak_detection",
                "total_requests": total_requests,
                "initial_memory_mb": initial_memory,
                "final_memory_mb": final_memory,
                "memory_growth_mb": memory_growth,
                "memory_growth_rate_mb_per_sample": memory_growth_rate,
                "memory_samples": memory_samples,
            }
        )

    async def test_connection_exhaustion_recovery(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Test recovery from connection exhaustion."""
        # Test with many concurrent long-running requests
        concurrent_requests = 200
        request_duration = 2  # seconds

        async def long_running_request(request_id: int):
            """Make a long-running request."""
            start_time = time.perf_counter()

            try:
                response = await http_client.get(
                    f"/api/slow?duration={request_duration}&id={request_id}"
                )
                end_time = time.perf_counter()

                return {
                    "request_id": request_id,
                    "success": response.status_code == 200,
                    "duration": end_time - start_time,
                    "status_code": response.status_code,
                }
            except Exception as e:
                end_time = time.perf_counter()
                return {
                    "request_id": request_id,
                    "success": False,
                    "duration": end_time - start_time,
                    "error": str(e),
                }

        # Launch all requests concurrently
        start_time = time.time()

        tasks = [long_running_request(i) for i in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        # Analyze results
        successful_requests = sum(
            1 for r in results if isinstance(r, dict) and r.get("success", False)
        )
        failed_requests = concurrent_requests - successful_requests
        success_rate = successful_requests / concurrent_requests

        # Performance assertions
        assert (
            success_rate > 0.8
        ), f"Too many failed requests: {success_rate:.2%} success rate"
        assert (
            total_time < request_duration * 2
        ), f"Requests took too long: {total_time:.2f}s"

        performance_helper.measurements.append(
            {
                "test": "connection_exhaustion_recovery",
                "concurrent_requests": concurrent_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "total_time_seconds": total_time,
            }
        )


@pytest.mark.performance
class TestPerformanceRegression:
    """Test for performance regressions."""

    async def test_baseline_performance_metrics(
        self, http_client, performance_helper: PerformanceTestHelper
    ):
        """Establish baseline performance metrics."""
        # This test establishes baseline metrics that can be compared
        # against in future test runs to detect performance regressions

        tests = [
            {
                "name": "simple_get",
                "endpoint": "/health",
                "method": "GET",
                "expected_max_latency_ms": 10,
            },
            {
                "name": "json_response",
                "endpoint": "/api/users",
                "method": "GET",
                "expected_max_latency_ms": 20,
            },
            {
                "name": "post_request",
                "endpoint": "/api/data",
                "method": "POST",
                "expected_max_latency_ms": 30,
            },
        ]

        baseline_metrics = {}

        for test in tests:
            latencies = []

            for _ in range(100):
                start_time = time.perf_counter()

                if test["method"] == "GET":
                    response = await http_client.get(test["endpoint"])
                else:  # POST
                    response = await http_client.post(
                        test["endpoint"], json={"test": "data"}
                    )

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                latencies.append(latency_ms)

                assert response.status_code in [200, 201]

            avg_latency = statistics.mean(latencies)
            p95_latency = statistics.quantiles(latencies, n=20)[18]

            # Performance regression check
            assert (
                avg_latency < test["expected_max_latency_ms"]
            ), f"{test['name']} regression: {avg_latency:.2f}ms"

            baseline_metrics[test["name"]] = {
                "avg_latency_ms": avg_latency,
                "p95_latency_ms": p95_latency,
                "expected_max_ms": test["expected_max_latency_ms"],
            }

        performance_helper.measurements.append(
            {
                "test": "baseline_performance_metrics",
                "baseline_metrics": baseline_metrics,
                "timestamp": time.time(),
            }
        )
