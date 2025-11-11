"""
CovetPy Pytest Integration

Comprehensive pytest fixtures and configuration for CovetPy testing.
Provides async support, fixture management, and coverage integration.
"""

import asyncio
import sys
from typing import Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, Mock

import pytest

# Import CovetPy components
from covet import CovetPy
from covet.core.asgi import CovetPyASGI
from covet.testing.client import SyncTestClient, TestClient, create_test_client
from covet.testing.fixtures import (
    MockService,
    TestDatabase,
    TestDataFactory,
    TestEnvironment,
    TestUser,
    temporary_database,
    test_environment,
)


# Pytest async configuration
def pytest_configure(config):
    """Configure pytest for async testing"""
    # Add async marker
    config.addinivalue_line("markers", "asyncio: mark test as async")

    # Configure asyncio mode
    config.option.asyncio_mode = "auto"


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    if sys.platform.startswith("win"):
        # Use ProactorEventLoop on Windows for subprocess support
        loop = asyncio.ProactorEventLoop()
    else:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()


@pytest.fixture
def mock_service():
    """Create a mock external service"""
    return MockService("test_service")


@pytest.fixture
async def test_db():
    """Create a test database for the test"""
    async with temporary_database() as db:
        yield db


@pytest.fixture
async def test_env():
    """Create a test environment with cleanup"""
    async with test_environment() as env:
        yield env


@pytest.fixture
def test_user():
    """Create a test user"""
    return TestDataFactory.create_user()


@pytest.fixture
def admin_user():
    """Create an admin test user"""
    return TestDataFactory.create_admin_user()


@pytest.fixture
def test_users():
    """Create multiple test users"""
    return TestDataFactory.create_users(5)


@pytest.fixture
def simple_app():
    """Create a simple CovetPy app for testing"""
    app = CovetPy()

    @app.get("/")
    async def root():
        return {"message": "Hello Test"}

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    @app.post("/echo")
    async def echo(request):
        data = await request.json()
        return {"echo": data}

    return app


@pytest.fixture
async def async_client(simple_app):
    """Create an async test client"""
    return create_test_client(simple_app, async_client=True)


@pytest.fixture
def sync_client(simple_app):
    """Create a sync test client"""
    return create_test_client(simple_app, async_client=False)


@pytest.fixture
def crud_app():
    """Create a CRUD application for testing"""
    app = CovetPy()

    # In-memory storage
    items = {}
    next_id = 1

    @app.get("/items")
    async def list_items():
        return {"items": list(items.values())}

    @app.post("/items")
    async def create_item(request):
        nonlocal next_id
        data = await request.json()

        item = {
            "id": next_id,
            "name": data["name"],
            "description": data.get("description", ""),
        }
        items[next_id] = item
        next_id += 1

        return item

    @app.get("/items/{item_id}")
    async def get_item(request):
        item_id = int(request.path_params["item_id"])
        item = items.get(item_id)

        if not item:
            from covet.core.http import Response

            return Response({"error": "Item not found"}, status_code=404)

        return item

    @app.put("/items/{item_id}")
    async def update_item(request):
        item_id = int(request.path_params["item_id"])
        data = await request.json()

        if item_id not in items:
            from covet.core.http import Response

            return Response({"error": "Item not found"}, status_code=404)

        items[item_id].update(data)
        return items[item_id]

    @app.delete("/items/{item_id}")
    async def delete_item(request):
        item_id = int(request.path_params["item_id"])

        if item_id not in items:
            from covet.core.http import Response

            return Response({"error": "Item not found"}, status_code=404)

        del items[item_id]
        return {"deleted": True}

    return app


@pytest.fixture
async def crud_client(crud_app):
    """Create client for CRUD app"""
    return create_test_client(crud_app, async_client=True)


@pytest.fixture
def auth_app():
    """Create an authentication-enabled app"""
    app = CovetPy()

    # Simple user store
    users = {
        "testuser": {"password": "password123", "role": "user"},
        "admin": {"password": "admin123", "role": "admin"},
    }
    sessions = {}

    @app.post("/login")
    async def login(request):
        data = await request.json()
        username = data.get("username")
        password = data.get("password")

        # SECURITY FIX: Use constant-time comparison to prevent timing attacks
        import secrets

        authenticated = False

        if username in users:
            stored_password = users[username]["password"]
            # Constant-time string comparison
            if secrets.compare_digest(stored_password, password):
                authenticated = True

        if authenticated:
            import uuid

            session_id = str(uuid.uuid4())
            sessions[session_id] = {
                "username": username,
                "role": users[username]["role"],
            }

            from covet.core.http import Response

            response = Response({"success": True, "session_id": session_id})
            response.set_cookie("session_id", session_id, max_age=3600)
            return response
        else:
            from covet.core.http import Response

            return Response({"error": "Invalid credentials"}, status_code=401)

    @app.get("/profile")
    async def get_profile(request):
        session_id = request.cookies().get("session_id")

        if not session_id or session_id not in sessions:
            from covet.core.http import Response

            return Response({"error": "Not authenticated"}, status_code=401)

        session = sessions[session_id]
        return {"username": session["username"], "role": session["role"]}

    @app.get("/admin")
    async def admin_area(request):
        session_id = request.cookies().get("session_id")

        if not session_id or session_id not in sessions:
            from covet.core.http import Response

            return Response({"error": "Not authenticated"}, status_code=401)

        session = sessions[session_id]
        if session["role"] != "admin":
            from covet.core.http import Response

            return Response({"error": "Admin access required"}, status_code=403)

        return {"message": "Admin area"}

    return app


@pytest.fixture
async def auth_client(auth_app):
    """Create client for auth app"""
    return create_test_client(auth_app, async_client=True)


@pytest.fixture
def websocket_app():
    """Create app with WebSocket support"""
    app = CovetPy()

    @app.websocket("/ws")
    async def websocket_endpoint(websocket):
        await websocket.accept()

        try:
            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.receive":
                    if "text" in message:
                        await websocket.send_text(f"Echo: {message['text']}")
                    elif "bytes" in message:
                        await websocket.send_bytes(message["bytes"])
                elif message["type"] == "websocket.disconnect":
                    break
        except Exception:
            logger.error(f"Error in websocket_endpoint: {e}", exc_info=True)
        finally:
            await websocket.close()

    @app.websocket("/ws/room/{room_id}")
    async def room_websocket(websocket):
        room_id = websocket.path_params.get("room_id")
        await websocket.accept()

        try:
            await websocket.send_text(f"Welcome to room {room_id}")

            while True:
                message = await websocket.receive()
                if message["type"] == "websocket.receive" and "text" in message:
                    await websocket.send_text(f"[{room_id}] {message['text']}")
                elif message["type"] == "websocket.disconnect":
                    break
        except Exception:
            # TODO: Add proper exception handling

            pass

    return app


@pytest.fixture
async def websocket_client(websocket_app):
    """Create client for WebSocket app"""
    return create_test_client(websocket_app, async_client=True)


@pytest.fixture
def middleware_app():
    """Create app with middleware for testing"""
    app = CovetPy()

    # Add middleware
    from covet.core.asgi import CORSMiddleware, RequestLoggingMiddleware

    app.middleware(CORSMiddleware)
    app.middleware(RequestLoggingMiddleware)

    @app.get("/")
    async def root():
        return {"message": "With middleware"}

    @app.get("/error")
    async def error_endpoint():
        raise ValueError("Test error")

    return app


@pytest.fixture
async def middleware_client(middleware_app):
    """Create client for middleware app"""
    return create_test_client(middleware_app, async_client=True)


# Helper fixtures for database testing
@pytest.fixture
async def populated_db():
    """Create a database with test data"""
    async with temporary_database() as db:
        # Add test users
        user1_id = await db.insert_user("alice", "alice@example.com")
        user2_id = await db.insert_user("bob", "bob@example.com")

        # Add test posts
        await db.insert_post("Alice's Post", "Content by Alice", user1_id, True)
        await db.insert_post("Bob's Post", "Content by Bob", user2_id, False)

        yield db


@pytest.fixture
def db_app(populated_db):
    """Create app that uses the populated database"""
    app = CovetPy()

    @app.get("/users")
    async def list_users():
        users = await populated_db.fetch_all("SELECT * FROM users")
        return {"users": [dict(user) for user in users]}

    @app.get("/posts")
    async def list_posts():
        posts = await populated_db.fetch_all(
            "SELECT p.*, u.username FROM posts p JOIN users u ON p.user_id = u.id"
        )
        return {"posts": [dict(post) for post in posts]}

    @app.get("/users/{user_id}/posts")
    async def user_posts(request):
        user_id = int(request.path_params["user_id"])
        posts = await populated_db.fetch_all("SELECT * FROM posts WHERE user_id = ?", (user_id,))
        return {"posts": [dict(post) for post in posts]}

    return app


@pytest.fixture
async def db_client(db_app):
    """Create client for database app"""
    return create_test_client(db_app, async_client=True)


# Performance testing fixtures
@pytest.fixture
def performance_app():
    """Create app for performance testing"""
    app = CovetPy()

    @app.get("/fast")
    async def fast_endpoint():
        return {"result": "fast"}

    @app.get("/slow")
    async def slow_endpoint():
        import asyncio

        await asyncio.sleep(0.1)  # Simulate slow operation
        return {"result": "slow"}

    @app.post("/process")
    async def process_data(request):
        data = await request.json()
        # Simulate processing
        result = sum(data.get("numbers", []))
        return {"sum": result}

    return app


@pytest.fixture
async def performance_client(performance_app):
    """Create client for performance testing"""
    return create_test_client(performance_app, async_client=True)


# File upload testing fixtures
@pytest.fixture
def upload_app():
    """Create app for file upload testing"""
    app = CovetPy()

    @app.post("/upload")
    async def upload_file(request):
        content_type = request.headers.get("content-type", "")
        body = request.get_body_bytes()

        return {"uploaded": True, "size": len(body), "content_type": content_type}

    @app.post("/upload/json")
    async def upload_json(request):
        data = await request.json()
        return {"received": data}

    return app


@pytest.fixture
async def upload_client(upload_app):
    """Create client for upload testing"""
    return create_test_client(upload_app, async_client=True)


# Error handling fixtures
@pytest.fixture
def error_app():
    """Create app for error testing"""
    app = CovetPy()

    @app.get("/400")
    async def bad_request():
        from covet.core.http import Response

        return Response({"error": "Bad request"}, status_code=400)

    @app.get("/401")
    async def unauthorized():
        from covet.core.http import Response

        return Response({"error": "Unauthorized"}, status_code=401)

    @app.get("/403")
    async def forbidden():
        from covet.core.http import Response

        return Response({"error": "Forbidden"}, status_code=403)

    @app.get("/404")
    async def not_found():
        from covet.core.http import Response

        return Response({"error": "Not found"}, status_code=404)

    @app.get("/500")
    async def server_error():
        raise Exception("Internal server error")

    return app


@pytest.fixture
async def error_client(error_app):
    """Create client for error testing"""
    return create_test_client(error_app, async_client=True)


# Utility functions for testing
def assert_json_response(response, expected_data, status_code=200):
    """Assert JSON response matches expected data"""
    assert response.status_code == status_code
    assert response.json() == expected_data


def assert_error_response(response, status_code, error_message=None):
    """Assert error response"""
    assert response.status_code == status_code
    data = response.json()
    assert "error" in data
    if error_message:
        assert error_message.lower() in data["error"].lower()


async def assert_websocket_echo(websocket, message):
    """Assert WebSocket echo functionality"""
    await websocket.send_text(message)
    response = await websocket.receive_text()
    assert response == f"Echo: {message}"


# Export all fixtures and utilities
__all__ = [
    # Core fixtures
    "event_loop",
    "test_user",
    "admin_user",
    "test_users",
    "test_db",
    "test_env",
    "mock_service",
    # App fixtures
    "simple_app",
    "crud_app",
    "auth_app",
    "websocket_app",
    "middleware_app",
    "db_app",
    "performance_app",
    "upload_app",
    "error_app",
    # Client fixtures
    "async_client",
    "sync_client",
    "crud_client",
    "auth_client",
    "websocket_client",
    "middleware_client",
    "db_client",
    "performance_client",
    "upload_client",
    "error_client",
    # Database fixtures
    "populated_db",
    # Utility functions
    "assert_json_response",
    "assert_error_response",
    "assert_websocket_echo",
]
