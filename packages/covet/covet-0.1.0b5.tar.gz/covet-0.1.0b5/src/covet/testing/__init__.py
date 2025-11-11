"""
CovetPy Testing Framework

Comprehensive testing framework for CovetPy applications providing:
- TestClient for HTTP and WebSocket testing
- Test fixtures for databases, authentication, and mock services
- Pytest integration with async support
- Performance testing utilities
- Security testing helpers
- Test data builders and assertion helpers

All components support real backend integration testing without mock data.
"""

from .client import (
    HTTPError,
    SyncTestClient,
    TestClient,
    TestRequest,
    TestResponse,
    TestWebSocket,
    create_test_client,
)
from .fixtures import (
    MockService,
    TestDatabase,
    TestDataFactory,
    TestEnvironment,
    TestUser,
    assert_forbidden,
    assert_not_found,
    assert_response_json,
    assert_unauthorized,
    assert_validation_error,
    temporary_database,
    test_environment,
)
from .utilities import (
    DatabaseTestUtils,
    FileTestUtils,
    PerformanceMetrics,
    PerformanceTester,
    ResponseAssertions,
    SecurityTestUtils,
    TestDataBuilder,
    TestReportGenerator,
    TestResult,
    WebSocketTestUtils,
    assert_json_contains,
    assert_json_equals,
    assert_response_error,
    assert_response_success,
    build_test_data,
)

# Import pytest fixtures if pytest is available
try:
    from .pytest_fixtures import *
except ImportError:
    # pytest not available, skip fixtures

    # Main testing API
    pass
__all__ = [
    # Test Client
    "TestClient",
    "SyncTestClient",
    "TestResponse",
    "TestRequest",
    "TestWebSocket",
    "HTTPError",
    "create_test_client",
    # Test Fixtures
    "TestDatabase",
    "TestUser",
    "MockService",
    "TestDataFactory",
    "TestEnvironment",
    "temporary_database",
    "test_environment",
    # Utilities
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
    # Convenience Functions
    "build_test_data",
    "assert_response_success",
    "assert_response_error",
    "assert_json_equals",
    "assert_json_contains",
    "assert_response_json",
    "assert_validation_error",
    "assert_unauthorized",
    "assert_forbidden",
    "assert_not_found",
]


# Version info
__version__ = "1.0.0"
__author__ = "CovetPy Team"
__description__ = "Comprehensive testing framework for CovetPy applications"
