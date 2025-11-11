"""
CovetPy Testing Utilities

Comprehensive utilities for test data creation, assertion helpers,
performance testing, and test execution helpers. Built for real backend testing.
"""

import asyncio
import inspect
import json
import os
import tempfile
import time
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

# Import CovetPy components
from covet.testing.client import TestClient, TestResponse
from covet.testing.fixtures import TestDatabase, TestUser


@dataclass
class PerformanceMetrics:
    """Performance metrics for test execution"""

    duration_ms: float
    memory_usage_mb: float
    requests_per_second: float
    average_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate: float
    concurrent_users: int = 1


@dataclass
class TestResult:
    """Test execution result with metrics"""

    success: bool
    response: Optional[TestResponse]
    error: Optional[str]
    duration_ms: float
    metadata: Dict[str, Any] = None


class TestDataBuilder:
    """Builder pattern for creating complex test data"""

    def __init__(self):
        self.data = {}

    def with_user(self, username: str = None, email: str = None, **kwargs) -> "TestDataBuilder":
        """Add user data"""
        user = TestUser(username=username, email=email, **kwargs)
        self.data["user"] = user.to_dict()
        return self

    def with_post(self, title: str = None, content: str = None, **kwargs) -> "TestDataBuilder":
        """Add post data"""
        self.data["post"] = {
            "title": title or f"Test Post {uuid.uuid4().hex[:8]}",
            "content": content or f"Test content {uuid.uuid4().hex[:16]}",
            **kwargs,
        }
        return self

    def with_api_key(self, name: str = None, scopes: List[str] = None) -> "TestDataBuilder":
        """Add API key data"""
        self.data["api_key"] = {
            "name": name or f"test_key_{uuid.uuid4().hex[:8]}",
            "key": f"test_{uuid.uuid4().hex}",
            "scopes": scopes or ["read", "write"],
            "is_active": True,
        }
        return self

    def with_custom(self, key: str, value: Any) -> "TestDataBuilder":
        """Add custom data"""
        self.data[key] = value
        return self

    def build(self) -> Dict[str, Any]:
        """Build the test data"""
        return self.data.copy()


class ResponseAssertions:
    """Advanced response assertion helpers"""

    @staticmethod
    def assert_success(response: TestResponse, expected_status: int = 200) -> None:
        """Assert successful response with specific status"""
        assert (
            response.status_code == expected_status
        ), f"Expected {expected_status}, got {response.status_code}: {response.text}"

    @staticmethod
    def assert_json_equals(response: TestResponse, expected: Any) -> None:
        """Assert JSON response equals expected data"""
        ResponseAssertions.assert_success(response)
        actual = response.json()
        assert actual == expected, f"JSON mismatch:\nExpected: {expected}\nActual: {actual}"

    @staticmethod
    def assert_json_contains(response: TestResponse, expected_subset: Dict[str, Any]) -> None:
        """Assert JSON response contains expected subset"""
        ResponseAssertions.assert_success(response)
        actual = response.json()
        for key, value in expected_subset.items():
            assert key in actual, f"Key '{key}' not found in response"
            assert actual[key] == value, f"Key '{key}': expected {value}, got {actual[key]}"

    @staticmethod
    def assert_json_schema(response: TestResponse, schema: Dict[str, Any]) -> None:
        """Assert JSON response matches schema structure"""
        ResponseAssertions.assert_success(response)
        actual = response.json()

        def validate_schema(data, schema_def, path=""):
            for key, expected_type in schema_def.items():
                full_path = f"{path}.{key}" if path else key
                assert key in data, f"Missing required field: {full_path}"

                if isinstance(expected_type, type):
                    assert isinstance(
                        data[key], expected_type
                    ), f"Field {full_path}: expected {expected_type.__name__}, got {type(data[key]).__name__}"
                elif isinstance(expected_type, dict):
                    validate_schema(data[key], expected_type, full_path)

        validate_schema(actual, schema)

    @staticmethod
    def assert_error_response(
        response: TestResponse, status_code: int, error_message: str = None
    ) -> None:
        """Assert error response with specific status and message"""
        assert (
            response.status_code == status_code
        ), f"Expected {status_code}, got {response.status_code}"

        data = response.json()
        assert "error" in data, "No error field in response"

        if error_message:
            actual_error = data["error"].lower()
            assert (
                error_message.lower() in actual_error
            ), f"Error message '{error_message}' not found in '{data['error']}'"

    @staticmethod
    def assert_headers_present(response: TestResponse, headers: List[str]) -> None:
        """Assert required headers are present"""
        for header in headers:
            assert header.lower() in (
                h.lower() for h in response.headers.keys()
            ), f"Header '{header}' not found in response"

    @staticmethod
    def assert_cookie_set(
        response: TestResponse, cookie_name: str, cookie_value: str = None
    ) -> None:
        """Assert cookie was set in response"""
        set_cookie = response.headers.get("set-cookie", "")
        assert cookie_name in set_cookie, f"Cookie '{cookie_name}' not set"

        if cookie_value:
            assert (
                f"{cookie_name}={cookie_value}" in set_cookie
            ), f"Cookie '{cookie_name}' value mismatch"


class PerformanceTester:
    """Performance testing utilities"""

    def __init__(self, client: TestClient):
        self.client = client
        self.metrics = []

    async def measure_request(self, method: str, url: str, **kwargs) -> TestResult:
        """Measure single request performance"""
        start_time = time.time()

        try:
            if method.upper() == "GET":
                response = await self.client.get(url, **kwargs)
            elif method.upper() == "POST":
                response = await self.client.post(url, **kwargs)
            elif method.upper() == "PUT":
                response = await self.client.put(url, **kwargs)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, **kwargs)
            else:
                raise ValueError(f"Unsupported method: {method}")

            duration_ms = (time.time() - start_time) * 1000

            return TestResult(
                success=response.status_code < 400,
                response=response,
                error=None,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(success=False, response=None, error=str(e), duration_ms=duration_ms)

    async def load_test(
        self,
        method: str,
        url: str,
        concurrent_users: int = 10,
        requests_per_user: int = 10,
        **kwargs,
    ) -> PerformanceMetrics:
        """Run load test with multiple concurrent users"""
        start_time = time.time()
        all_results = []

        async def user_session():
            """Single user session"""
            user_results = []
            for _ in range(requests_per_user):
                result = await self.measure_request(method, url, **kwargs)
                user_results.append(result)
                # Small delay to avoid overwhelming
                await asyncio.sleep(0.01)
            return user_results

        # Run concurrent users
        tasks = [user_session() for _ in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)

        # Flatten results
        for user_result in user_results:
            all_results.extend(user_result)

        total_duration = time.time() - start_time

        # Calculate metrics
        successful_requests = [r for r in all_results if r.success]
        failed_requests = [r for r in all_results if not r.success]

        response_times = [r.duration_ms for r in successful_requests]
        response_times.sort()

        metrics = PerformanceMetrics(
            duration_ms=total_duration * 1000,
            memory_usage_mb=0.0,  # Would need memory profiling
            requests_per_second=len(all_results) / total_duration,
            average_response_time_ms=(
                sum(response_times) / len(response_times) if response_times else 0
            ),
            p95_response_time_ms=(
                response_times[int(len(response_times) * 0.95)] if response_times else 0
            ),
            p99_response_time_ms=(
                response_times[int(len(response_times) * 0.99)] if response_times else 0
            ),
            error_rate=len(failed_requests) / len(all_results) if all_results else 0,
            concurrent_users=concurrent_users,
        )

        self.metrics.append(metrics)
        return metrics

    def assert_performance_threshold(
        self,
        metrics: PerformanceMetrics,
        max_response_time_ms: float = 1000,
        min_requests_per_second: float = 100,
        max_error_rate: float = 0.01,
    ) -> None:
        """Assert performance meets thresholds"""
        assert (
            metrics.average_response_time_ms <= max_response_time_ms
        ), f"Average response time {metrics.average_response_time_ms}ms exceeds {max_response_time_ms}ms"

        assert (
            metrics.requests_per_second >= min_requests_per_second
        ), f"Requests per second {metrics.requests_per_second} below {min_requests_per_second}"

        assert (
            metrics.error_rate <= max_error_rate
        ), f"Error rate {metrics.error_rate:.2%} exceeds {max_error_rate:.2%}"


class DatabaseTestUtils:
    """Database testing utilities"""

    @staticmethod
    async def populate_test_data(
        db: TestDatabase, num_users: int = 5, num_posts_per_user: int = 3
    ) -> Dict[str, List[int]]:
        """Populate database with test data"""
        user_ids = []
        post_ids = []

        for i in range(num_users):
            user_id = await db.insert_user(
                username=f"testuser{i}", email=f"testuser{i}@example.com"
            )
            user_ids.append(user_id)

            for j in range(num_posts_per_user):
                post_id = await db.insert_post(
                    title=f"Post {j} by User {i}",
                    content=f"Content for post {j} by user {i}",
                    user_id=user_id,
                    published=j % 2 == 0,  # Alternate published status
                )
                post_ids.append(post_id)

        return {"user_ids": user_ids, "post_ids": post_ids}

    @staticmethod
    async def assert_database_state(
        db: TestDatabase, expected_users: int = None, expected_posts: int = None
    ) -> None:
        """Assert database state matches expectations"""
        if expected_users is not None:
            users = await db.fetch_all("SELECT COUNT(*) as count FROM users")
            actual_users = users[0]["count"]
            assert (
                actual_users == expected_users
            ), f"Expected {expected_users} users, found {actual_users}"

        if expected_posts is not None:
            posts = await db.fetch_all("SELECT COUNT(*) as count FROM posts")
            actual_posts = posts[0]["count"]
            assert (
                actual_posts == expected_posts
            ), f"Expected {expected_posts} posts, found {actual_posts}"


class WebSocketTestUtils:
    """WebSocket testing utilities"""

    @staticmethod
    async def echo_test(websocket, message: str, timeout: float = 5.0) -> str:
        """Test WebSocket echo functionality"""
        await websocket.send_text(message)

        try:
            response = await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
            return response
        except asyncio.TimeoutError:
            raise AssertionError(f"No response received within {timeout} seconds")

    @staticmethod
    async def binary_echo_test(websocket, data: bytes, timeout: float = 5.0) -> bytes:
        """Test WebSocket binary echo functionality"""
        await websocket.send_bytes(data)

        try:
            response = await asyncio.wait_for(websocket.receive_bytes(), timeout=timeout)
            return response
        except asyncio.TimeoutError:
            raise AssertionError(f"No binary response received within {timeout} seconds")

    @staticmethod
    async def message_sequence_test(
        websocket,
        messages: List[str],
        expected_responses: List[str] = None,
        timeout: float = 5.0,
    ) -> List[str]:
        """Test sequence of WebSocket messages"""
        responses = []

        for i, message in enumerate(messages):
            await websocket.send_text(message)

            try:
                response = await asyncio.wait_for(websocket.receive_text(), timeout=timeout)
                responses.append(response)

                if expected_responses and i < len(expected_responses):
                    assert (
                        response == expected_responses[i]
                    ), f"Message {i}: expected '{expected_responses[i]}', got '{response}'"

            except asyncio.TimeoutError:
                raise AssertionError(f"No response for message {i} within {timeout} seconds")

        return responses


class FileTestUtils:
    """File testing utilities"""

    @staticmethod
    def create_test_file(content: str = "Test file content", suffix: str = ".txt") -> str:
        """Create temporary test file"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
            f.write(content)
            return f.name

    @staticmethod
    def create_test_binary_file(data: bytes, suffix: str = ".bin") -> str:
        """Create temporary binary test file"""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=suffix, delete=False) as f:
            f.write(data)
            return f.name

    @staticmethod
    def cleanup_test_file(filepath: str) -> None:
        """Clean up test file"""
        if os.path.exists(filepath):
            os.unlink(filepath)

    @staticmethod
    @asynccontextmanager
    async def temporary_test_file(content: str = "Test content", suffix: str = ".txt"):
        """Context manager for temporary test file"""
        filepath = FileTestUtils.create_test_file(content, suffix)
        try:
            yield filepath
        finally:
            FileTestUtils.cleanup_test_file(filepath)


class SecurityTestUtils:
    """Security testing utilities"""

    @staticmethod
    async def test_sql_injection(
        client: TestClient,
        endpoint: str,
        parameter: str,
        payload: str = "'; DROP TABLE users; --",
    ) -> TestResponse:
        """Test SQL injection vulnerability"""
        malicious_data = {parameter: payload}
        response = await client.post(endpoint, json=malicious_data)

        # Should not succeed with injection
        assert response.status_code >= 400, f"SQL injection may be possible: {response.status_code}"

        return response

    @staticmethod
    async def test_xss_protection(
        client: TestClient,
        endpoint: str,
        parameter: str,
        payload: str = "<script>alert('xss')</script>",
    ) -> TestResponse:
        """Test XSS protection"""
        malicious_data = {parameter: payload}
        response = await client.post(endpoint, json=malicious_data)

        # Check response doesn't include unescaped script
        if response.status_code == 200:
            content = response.text
            assert "<script>" not in content, "XSS vulnerability detected"

        return response

    @staticmethod
    async def test_authentication_bypass(
        client: TestClient, protected_endpoint: str
    ) -> TestResponse:
        """Test authentication bypass attempts"""
        # Try without authentication
        response = await client.get(protected_endpoint)
        assert response.status_code in [
            401,
            403,
        ], f"Protected endpoint accessible without auth: {response.status_code}"

        return response

    @staticmethod
    async def test_authorization_escalation(
        client: TestClient, admin_endpoint: str, user_token: str
    ) -> TestResponse:
        """Test privilege escalation"""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = await client.get(admin_endpoint, headers=headers)

        assert response.status_code == 403, f"Privilege escalation possible: {response.status_code}"

        return response


class TestReportGenerator:
    """Generate comprehensive test reports"""

    def __init__(self):
        self.results = []
        self.performance_metrics = []
        self.security_results = []

    def add_result(self, test_name: str, result: TestResult) -> None:
        """Add test result"""
        self.results.append(
            {
                "test_name": test_name,
                "success": result.success,
                "duration_ms": result.duration_ms,
                "error": result.error,
                "metadata": result.metadata or {},
            }
        )

    def add_performance_metrics(self, test_name: str, metrics: PerformanceMetrics) -> None:
        """Add performance metrics"""
        self.performance_metrics.append(
            {
                "test_name": test_name,
                "metrics": {
                    "duration_ms": metrics.duration_ms,
                    "requests_per_second": metrics.requests_per_second,
                    "average_response_time_ms": metrics.average_response_time_ms,
                    "p95_response_time_ms": metrics.p95_response_time_ms,
                    "p99_response_time_ms": metrics.p99_response_time_ms,
                    "error_rate": metrics.error_rate,
                    "concurrent_users": metrics.concurrent_users,
                },
            }
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        successful_tests = len([r for r in self.results if r["success"]])
        failed_tests = total_tests - successful_tests

        avg_duration = (
            sum(r["duration_ms"] for r in self.results) / total_tests if total_tests > 0 else 0
        )

        return {
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": (successful_tests / total_tests if total_tests > 0 else 0),
                "average_duration_ms": avg_duration,
            },
            "test_results": self.results,
            "performance_metrics": self.performance_metrics,
            "security_results": self.security_results,
        }

    def save_report(self, filepath: str) -> None:
        """Save report to file"""
        report = self.generate_report()
        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)


# Convenience functions
def build_test_data() -> TestDataBuilder:
    """Create new test data builder"""
    return TestDataBuilder()


def assert_response_success(response: TestResponse, status_code: int = 200) -> None:
    """Quick success assertion"""
    ResponseAssertions.assert_success(response, status_code)


def assert_response_error(response: TestResponse, status_code: int, message: str = None) -> None:
    """Quick error assertion"""
    ResponseAssertions.assert_error_response(response, status_code, message)


def assert_json_equals(response: TestResponse, expected: Any) -> None:
    """Quick JSON equality assertion"""
    ResponseAssertions.assert_json_equals(response, expected)


def assert_json_contains(response: TestResponse, expected_subset: Dict[str, Any]) -> None:
    """Quick JSON contains assertion"""
    ResponseAssertions.assert_json_contains(response, expected_subset)


# Export all utilities
__all__ = [
    "PerformanceMetrics",
    "TestResult",
    "TestDataBuilder",
    "ResponseAssertions",
    "PerformanceTester",
    "DatabaseTestUtils",
    "WebSocketTestUtils",
    "FileTestUtils",
    "SecurityTestUtils",
    "TestReportGenerator",
    # Convenience functions
    "build_test_data",
    "assert_response_success",
    "assert_response_error",
    "assert_json_equals",
    "assert_json_contains",
]
