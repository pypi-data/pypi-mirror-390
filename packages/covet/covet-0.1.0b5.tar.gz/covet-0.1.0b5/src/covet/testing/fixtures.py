"""
CovetPy Test Fixtures

Comprehensive test fixtures for database testing, authentication, mock services,
and common testing scenarios. Built for real backend integration testing.
"""

import asyncio
import json
import os
import sqlite3
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, Generator, List, Optional
from unittest.mock import MagicMock, Mock

# Import CovetPy components
from covet.core.app import CovetApplication
from covet.core.http import Request, Response
from covet.testing.client import TestClient, create_test_client


class TestDatabase:
    """Test database fixture for isolated testing"""

    def __init__(self, db_type: str = "sqlite", **config):
        self.db_type = db_type
        self.config = config
        self.connection = None
        self.temp_file = None

    async def setup(self):
        """Setup test database"""
        if self.db_type == "sqlite":
            self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
            self.connection = sqlite3.connect(self.temp_file.name)
            self.connection.row_factory = sqlite3.Row

            # Create basic test tables
            await self._create_test_tables()

    async def teardown(self):
        """Cleanup test database"""
        if self.connection:
            self.connection.close()
        if self.temp_file:
            os.unlink(self.temp_file.name)

    async def _create_test_tables(self):
        """Create standard test tables"""
        cursor = self.connection.cursor()

        # Users table
        cursor.execute(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Posts table
        cursor.execute(
            """
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                published BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        # Sessions table
        cursor.execute(
            """
            CREATE TABLE sessions (
                id TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                data TEXT,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """
        )

        self.connection.commit()

    async def execute(self, query: str, params: tuple = None):
        """Execute SQL query"""
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.connection.commit()
        return cursor

    async def fetch_one(self, query: str, params: tuple = None):
        """Fetch one result"""
        cursor = await self.execute(query, params)
        return cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple = None):
        """Fetch all results"""
        cursor = await self.execute(query, params)
        return cursor.fetchall()

    async def insert_user(self, username: str, email: str, password_hash: str = "test_hash") -> int:
        """Insert test user and return ID"""
        cursor = await self.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash),
        )
        return cursor.lastrowid

    async def insert_post(
        self, title: str, content: str, user_id: int, published: bool = False
    ) -> int:
        """Insert test post and return ID"""
        cursor = await self.execute(
            "INSERT INTO posts (title, content, user_id, published) VALUES (?, ?, ?, ?)",
            (title, content, user_id, published),
        )
        return cursor.lastrowid


class TestUser:
    """Test user fixture with authentication data"""

    def __init__(
        self,
        username: str = None,
        email: str = None,
        password: str = "test123",
        is_admin: bool = False,
        is_active: bool = True,
        **extra_data,
    ):
        self.id = str(uuid.uuid4())
        self.username = username or f"testuser_{uuid.uuid4().hex[:8]}"
        self.email = email or f"{self.username}@test.com"
        self.password = password
        self.password_hash = self._hash_password(password)
        self.is_admin = is_admin
        self.is_active = is_active
        self.extra_data = extra_data
        self.tokens = {}

    def _hash_password(self, password: str) -> str:
        """Simple password hashing for testing"""
        import hashlib

        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """
        Verify password using constant-time comparison.

        SECURITY FIX: Uses secrets.compare_digest() to prevent timing attacks.
        """
        import secrets

        expected_hash = self.password_hash
        actual_hash = self._hash_password(password)
        return secrets.compare_digest(expected_hash, actual_hash)

    def generate_token(self, token_type: str = "access") -> str:
        """Generate test JWT token"""
        import base64
        import time

        payload = {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "token_type": token_type,
            "exp": int(time.time()) + 3600,  # 1 hour
            "iat": int(time.time()),
        }

        # Simple base64 encoding for test tokens
        token = base64.b64encode(json.dumps(payload).encode()).decode()
        self.tokens[token_type] = token
        return token

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "is_active": self.is_active,
            **self.extra_data,
        }


class MockService:
    """Mock external service for testing"""

    def __init__(self, name: str, base_url: str = "http://mock-service.test"):
        self.name = name
        self.base_url = base_url
        self.call_history = []
        self.responses = {}
        self.default_response = {"status": "ok"}

    def set_response(self, endpoint: str, response: Dict[str, Any], status_code: int = 200):
        """Set mock response for endpoint"""
        self.responses[endpoint] = {"response": response, "status_code": status_code}

    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Mock request to service"""
        call_record = {
            "method": method,
            "endpoint": endpoint,
            "kwargs": kwargs,
            "timestamp": asyncio.get_event_loop().time(),
        }
        self.call_history.append(call_record)

        # Return configured response or default
        if endpoint in self.responses:
            mock_response = self.responses[endpoint]
            return mock_response["response"]
        return self.default_response

    def assert_called_with(self, method: str, endpoint: str):
        """Assert service was called with specific parameters"""
        calls = [
            call
            for call in self.call_history
            if call["method"] == method and call["endpoint"] == endpoint
        ]
        assert calls, f"No calls found for {method} {endpoint}"

    def assert_call_count(self, expected_count: int):
        """Assert total number of calls"""
        assert (
            len(self.call_history) == expected_count
        ), f"Expected {expected_count} calls, got {len(self.call_history)}"

    def reset(self):
        """Reset call history"""
        self.call_history.clear()


class TestDataFactory:
    """Factory for creating test data"""

    @staticmethod
    def create_user(**kwargs) -> TestUser:
        """Create test user with optional overrides"""
        return TestUser(**kwargs)

    @staticmethod
    def create_admin_user(**kwargs) -> TestUser:
        """Create admin test user"""
        kwargs.setdefault("is_admin", True)
        kwargs.setdefault("username", f"admin_{uuid.uuid4().hex[:8]}")
        return TestUser(**kwargs)

    @staticmethod
    def create_users(count: int, **kwargs) -> List[TestUser]:
        """Create multiple test users"""
        return [TestDataFactory.create_user(**kwargs) for _ in range(count)]

    @staticmethod
    def create_post_data(title: str = None, content: str = None) -> Dict[str, Any]:
        """Create test post data"""
        return {
            "title": title or f"Test Post {uuid.uuid4().hex[:8]}",
            "content": content or f"This is test content {uuid.uuid4().hex[:16]}",
            "published": False,
        }

    @staticmethod
    def create_api_key(name: str = None, scopes: List[str] = None) -> Dict[str, Any]:
        """Create test API key data"""
        return {
            "name": name or f"test_key_{uuid.uuid4().hex[:8]}",
            "key": f"test_{uuid.uuid4().hex}",
            "scopes": scopes or ["read", "write"],
            "is_active": True,
        }


class TestEnvironment:
    """Test environment manager"""

    def __init__(self):
        self.databases = {}
        self.services = {}
        self.users = {}
        self.cleanup_tasks = []

    async def setup_database(self, name: str = "default", **config) -> TestDatabase:
        """Setup test database"""
        db = TestDatabase(**config)
        await db.setup()
        self.databases[name] = db
        self.cleanup_tasks.append(db.teardown)
        return db

    def setup_mock_service(self, name: str, **config) -> MockService:
        """Setup mock service"""
        service = MockService(name, **config)
        self.services[name] = service
        return service

    def create_test_user(self, name: str = None, **kwargs) -> TestUser:
        """Create and register test user"""
        user = TestDataFactory.create_user(**kwargs)
        user_name = name or user.username
        self.users[user_name] = user
        return user

    async def cleanup(self):
        """Cleanup all test resources"""
        for cleanup_task in self.cleanup_tasks:
            if asyncio.iscoroutinefunction(cleanup_task):
                await cleanup_task()
            else:
                cleanup_task()
        self.cleanup_tasks.clear()
        self.databases.clear()
        self.services.clear()
        self.users.clear()


# Pytest fixtures
try:
    import pytest

    @pytest.fixture
    async def test_db():
        """Pytest fixture for test database"""
        db = TestDatabase()
        await db.setup()
        yield db
        await db.teardown()

    @pytest.fixture
    def test_user():
        """Pytest fixture for test user"""
        return TestDataFactory.create_user()

    @pytest.fixture
    def admin_user():
        """Pytest fixture for admin user"""
        return TestDataFactory.create_admin_user()

    @pytest.fixture
    def test_users():
        """Pytest fixture for multiple test users"""
        return TestDataFactory.create_users(3)

    @pytest.fixture
    async def test_env():
        """Pytest fixture for test environment"""
        env = TestEnvironment()
        yield env
        await env.cleanup()

    @pytest.fixture
    def mock_service():
        """Pytest fixture for mock service"""
        return MockService("test_service")

    @pytest.fixture
    def test_app():
        """Pytest fixture for test application"""
        from covet import CovetPy

        app = CovetPy()

        @app.get("/")
        async def root():
            return {"message": "Hello Test"}

        @app.get("/users/{user_id}")
        async def get_user(request):
            user_id = request.path_params.get("user_id")
            return {"user_id": user_id}

        @app.post("/users")
        async def create_user(request):
            data = await request.json()
            return {"created": True, "user": data}

        return app

    @pytest.fixture
    async def test_client(test_app):
        """Pytest fixture for async test client"""
        return create_test_client(test_app, async_client=True)

    @pytest.fixture
    def sync_test_client(test_app):
        """Pytest fixture for sync test client"""
        return create_test_client(test_app, async_client=False)

except ImportError:
    # pytest not available, skip fixtures

    # Context managers for testing
    pass


@asynccontextmanager
async def temporary_database(**config):
    """Context manager for temporary test database"""
    db = TestDatabase(**config)
    await db.setup()
    try:
        yield db
    finally:
        await db.teardown()


@asynccontextmanager
async def test_environment():
    """Context manager for test environment"""
    env = TestEnvironment()
    try:
        yield env
    finally:
        await env.cleanup()


# Utility functions
def assert_response_json(response, expected: Dict[str, Any]):
    """Assert response JSON matches expected"""
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    actual = response.json()
    assert actual == expected, f"JSON mismatch: {actual} != {expected}"


def assert_validation_error(response, field: str = None):
    """Assert response is a validation error"""
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    data = response.json()
    assert "error" in data or "detail" in data, "No error in response"
    if field:
        # Check if field is mentioned in error
        error_text = str(data).lower()
        assert field.lower() in error_text, f"Field '{field}' not in error: {data}"


def assert_unauthorized(response):
    """Assert response is unauthorized"""
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


def assert_forbidden(response):
    """Assert response is forbidden"""
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"


def assert_not_found(response):
    """Assert response is not found"""
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"


# Export main classes and functions
__all__ = [
    "TestDatabase",
    "TestUser",
    "MockService",
    "TestDataFactory",
    "TestEnvironment",
    "temporary_database",
    "test_environment",
    "assert_response_json",
    "assert_validation_error",
    "assert_unauthorized",
    "assert_forbidden",
    "assert_not_found",
]
