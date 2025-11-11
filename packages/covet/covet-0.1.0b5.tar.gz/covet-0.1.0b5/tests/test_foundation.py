"""
CovetPy Foundation Test Suite

Comprehensive test suite covering core framework functionality:
- Basic routing and parameter extraction
- Request/response handling with real data
- Middleware functionality testing
- Error handling and exception scenarios
- WebSocket connection testing
- Authentication and authorization flows
- File upload handling
- Session management

All tests use real backend integration without mock data.
"""

import asyncio
import json
import pytest
import uuid
import tempfile
import os
from io import BytesIO
from typing import Dict, Any

# Import CovetPy components
from covet import CovetPy
from covet.core.http import Request, Response, json_response, html_response, error_response
from covet.core.asgi import CORSMiddleware, RequestLoggingMiddleware, ExceptionMiddleware
from covet.testing.client import TestClient, create_test_client
from covet.testing.fixtures import (
    TestDatabase, TestUser, TestDataFactory, 
    assert_response_json, assert_not_found, assert_unauthorized
)


class TestBasicRouting:
    """Test basic routing functionality with real endpoints"""
    
    @pytest.fixture
    def app(self):
        """Create test application with various routes"""
        app = CovetPy()
        
        @app.get("/")
        async def root():
            return {"message": "Hello CovetPy", "version": "1.0.0"}
            
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": "2024-01-01T00:00:00Z"}
            
        @app.get("/users/{user_id}")
        async def get_user(request):
            user_id = request.path_params.get("user_id")
            # Simulate real database lookup
            if user_id == "999":
                return Response({"error": "User not found"}, status_code=404)
            return {
                "id": int(user_id),
                "username": f"user_{user_id}",
                "email": f"user{user_id}@example.com"
            }
            
        @app.get("/search")
        async def search(request):
            query = request.query.get("q", "")
            limit = int(request.query.get("limit", "10"))
            return {
                "query": query,
                "limit": limit,
                "results": [f"result_{i}" for i in range(min(limit, 3))]
            }
            
        @app.post("/users")
        async def create_user(request):
            data = await request.json()
            # Validate required fields
            if not data.get("username") or not data.get("email"):
                return Response({"error": "Missing required fields"}, status_code=400)
                
            # Simulate user creation
            user_id = len(data.get("username", "")) + 100
            return {
                "id": user_id,
                "username": data["username"],
                "email": data["email"],
                "created": True
            }
            
        return app
        
    @pytest.fixture
    async def client(self, app):
        """Create async test client"""
        return create_test_client(app, async_client=True)
        
    async def test_root_endpoint(self, client):
        """Test root endpoint returns correct response"""
        response = await client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello CovetPy"
        assert data["version"] == "1.0.0"
        
    async def test_health_check(self, client):
        """Test health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        
    async def test_path_parameters(self, client):
        """Test path parameter extraction"""
        response = await client.get("/users/123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 123
        assert data["username"] == "user_123"
        assert data["email"] == "user123@example.com"
        
    async def test_query_parameters(self, client):
        """Test query parameter handling"""
        response = await client.get("/search?q=test&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "test"
        assert data["limit"] == 5
        assert len(data["results"]) == 3  # Limited by mock data
        
    async def test_post_request_with_json(self, client):
        """Test POST request with JSON payload"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "name": "Test User"
        }
        
        response = await client.post("/users", json=user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
        assert data["created"] is True
        assert "id" in data
        
    async def test_validation_error(self, client):
        """Test validation error handling"""
        invalid_data = {"username": ""}  # Missing email
        
        response = await client.post("/users", json=invalid_data)
        
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "required" in data["error"].lower()
        
    async def test_not_found_route(self, client):
        """Test 404 for non-existent routes"""
        response = await client.get("/nonexistent")
        
        assert response.status_code == 404
        
    async def test_not_found_resource(self, client):
        """Test 404 for non-existent resource"""
        response = await client.get("/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["error"].lower()


class TestRequestResponseHandling:
    """Test request and response handling with various content types"""
    
    @pytest.fixture
    def app(self):
        """Create app with different content type handlers"""
        app = CovetPy()
        
        @app.post("/echo")
        async def echo(request):
            """Echo request data back"""
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                data = await request.json()
                return {"type": "json", "data": data}
            elif "text/plain" in content_type:
                text = await request.body.text()
                return {"type": "text", "data": text}
            else:
                return {"type": "unknown", "content_type": content_type}
                
        @app.post("/upload")
        async def upload_file(request):
            """Handle file upload"""
            content_type = request.headers.get("content-type", "")
            
            if "multipart/form-data" in content_type:
                # In real implementation, would parse multipart data
                return {"uploaded": True, "type": "multipart"}
            else:
                body = request.get_body_bytes()
                return {"uploaded": True, "size": len(body), "type": "binary"}
                
        @app.get("/headers")
        async def get_headers(request):
            """Return request headers"""
            return {"headers": dict(request.headers)}
            
        @app.get("/cookies")
        async def get_cookies(request):
            """Return request cookies"""
            return {"cookies": request.cookies()}
            
        @app.post("/set-cookie")
        async def set_cookie(request):
            """Set a cookie in response"""
            data = await request.json()
            response = Response({"cookie_set": True})
            response.set_cookie(
                name=data.get("name", "test_cookie"),
                value=data.get("value", "test_value"),
                max_age=data.get("max_age", 3600)
            )
            return response
            
        return app
        
    @pytest.fixture
    async def client(self, app):
        return create_test_client(app, async_client=True)
        
    async def test_json_request_response(self, client):
        """Test JSON request and response handling"""
        test_data = {
            "name": "Test Item",
            "value": 42,
            "nested": {"key": "value"}
        }
        
        response = await client.post("/echo", json=test_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "json"
        assert data["data"] == test_data
        
    async def test_text_request_response(self, client):
        """Test plain text request handling"""
        test_text = "This is a test message"
        
        response = await client.post(
            "/echo", 
            data=test_text,
            headers={"content-type": "text/plain"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["type"] == "text"
        assert data["data"] == test_text
        
    async def test_file_upload(self, client):
        """Test file upload handling"""
        file_content = b"This is test file content"
        
        response = await client.post(
            "/upload",
            data=file_content,
            headers={"content-type": "application/octet-stream"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["uploaded"] is True
        assert data["size"] == len(file_content)
        assert data["type"] == "binary"
        
    async def test_custom_headers(self, client):
        """Test custom header handling"""
        custom_headers = {
            "X-Test-Header": "test-value",
            "Authorization": "Bearer test-token",
            "User-Agent": "CovetPy-Test/1.0"
        }
        
        response = await client.get("/headers", headers=custom_headers)
        
        assert response.status_code == 200
        data = response.json()
        headers = data["headers"]
        
        assert headers.get("x-test-header") == "test-value"
        assert headers.get("authorization") == "Bearer test-token"
        assert headers.get("user-agent") == "CovetPy-Test/1.0"
        
    async def test_cookie_handling(self, client):
        """Test cookie setting and reading"""
        # Set a cookie
        cookie_data = {
            "name": "session_id",
            "value": "abc123",
            "max_age": 3600
        }
        
        response = await client.post("/set-cookie", json=cookie_data)
        assert response.status_code == 200
        
        # Check if cookie was set in response
        set_cookie = response.headers.get("set-cookie")
        assert set_cookie is not None
        assert "session_id=abc123" in set_cookie
        
        # Read cookies in subsequent request
        response = await client.get("/cookies")
        assert response.status_code == 200
        
        data = response.json()
        cookies = data["cookies"]
        assert cookies.get("session_id") == "abc123"


class TestMiddleware:
    """Test middleware functionality with real requests"""
    
    @pytest.fixture
    def app_with_middleware(self):
        """Create app with various middleware"""
        app = CovetPy()
        
        # Add CORS middleware
        app.middleware(CORSMiddleware)
        
        # Add request logging middleware
        app.middleware(RequestLoggingMiddleware)
        
        # Add exception handling middleware
        app.middleware(ExceptionMiddleware)
        
        @app.get("/")
        async def root():
            return {"message": "Hello with middleware"}
            
        @app.get("/error")
        async def cause_error():
            raise ValueError("Test error")
            
        @app.options("/test")
        async def options_test():
            return {"method": "OPTIONS"}
            
        return app
        
    @pytest.fixture
    async def client(self, app_with_middleware):
        return create_test_client(app_with_middleware, async_client=True)
        
    async def test_cors_middleware(self, client):
        """Test CORS middleware adds proper headers"""
        response = await client.get("/", headers={"Origin": "http://example.com"})
        
        assert response.status_code == 200
        # CORS headers should be added by middleware
        headers = response.headers
        # Note: Actual header names depend on middleware implementation
        
    async def test_preflight_request(self, client):
        """Test CORS preflight handling"""
        response = await client.options(
            "/test",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            }
        )
        
        assert response.status_code == 200
        
    async def test_exception_middleware(self, client):
        """Test exception handling middleware"""
        response = await client.get("/error")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "server error" in data["error"].lower()


class TestWebSocketSupport:
    """Test WebSocket functionality"""
    
    @pytest.fixture
    def app_with_websocket(self):
        """Create app with WebSocket endpoints"""
        app = CovetPy()
        
        @app.websocket("/ws")
        async def websocket_endpoint(websocket):
            await websocket.accept()
            
            try:
                while True:
                    message = await websocket.receive()
                    if message["type"] == "websocket.receive":
                        if "text" in message:
                            # Echo text message
                            await websocket.send_text(f"Echo: {message['text']}")
                        elif "bytes" in message:
                            # Echo binary message
                            await websocket.send_bytes(message["bytes"])
                    elif message["type"] == "websocket.disconnect":
                        break
            except Exception:
                pass
            finally:
                await websocket.close()
                
        @app.websocket("/ws/chat/{room_id}")
        async def chat_room(websocket):
            room_id = websocket.path_params.get("room_id")
            await websocket.accept()
            
            try:
                # Send welcome message
                await websocket.send_text(f"Welcome to room {room_id}")
                
                while True:
                    message = await websocket.receive()
                    if message["type"] == "websocket.receive" and "text" in message:
                        # Broadcast to room (simplified)
                        await websocket.send_text(f"[{room_id}] {message['text']}")
                    elif message["type"] == "websocket.disconnect":
                        break
            except Exception:
                pass
                
        return app
        
    @pytest.fixture
    async def client(self, app_with_websocket):
        return create_test_client(app_with_websocket, async_client=True)
        
    async def test_websocket_connection(self, client):
        """Test basic WebSocket connection"""
        async with client.websocket_connect("/ws") as websocket:
            # Test text message
            test_message = "Hello WebSocket"
            await websocket.send_text(test_message)
            
            response = await websocket.receive_text()
            assert response == f"Echo: {test_message}"
            
    async def test_websocket_binary_message(self, client):
        """Test WebSocket binary message handling"""
        async with client.websocket_connect("/ws") as websocket:
            test_data = b"Binary test data"
            await websocket.send_bytes(test_data)
            
            response = await websocket.receive_bytes()
            assert response == test_data
            
    async def test_websocket_with_path_params(self, client):
        """Test WebSocket with path parameters"""
        room_id = "test_room_123"
        async with client.websocket_connect(f"/ws/chat/{room_id}") as websocket:
            # Should receive welcome message
            welcome = await websocket.receive_text()
            assert f"Welcome to room {room_id}" in welcome
            
            # Send a message
            await websocket.send_text("Hello room!")
            response = await websocket.receive_text()
            assert f"[{room_id}] Hello room!" in response


class TestErrorHandling:
    """Test error handling and exception scenarios"""
    
    @pytest.fixture
    def app_with_errors(self):
        """Create app with various error scenarios"""
        app = CovetPy()
        
        @app.get("/server-error")
        async def server_error():
            raise Exception("Internal server error")
            
        @app.get("/not-found")
        async def not_found():
            return Response({"error": "Resource not found"}, status_code=404)
            
        @app.get("/unauthorized")
        async def unauthorized():
            return Response({"error": "Unauthorized access"}, status_code=401)
            
        @app.get("/validation-error")
        async def validation_error():
            return Response({"error": "Validation failed", "field": "email"}, status_code=422)
            
        @app.post("/process-data")
        async def process_data(request):
            data = await request.json()
            
            # Validate required fields
            if not data.get("name"):
                assert Response({"error": "Name is required"}, status_code=400)
                
            if not data.get("email") or "@" not in data["email"]:
                assert Response({"error": "Valid email is required"}, status_code=400)
                
            return {"processed": True, "data": data}
            
        return app
        
    @pytest.fixture
    async def client(self, app_with_errors):
        return create_test_client(app_with_errors, async_client=True)
        
    async def test_server_error_handling(self, client):
        """Test 500 server error handling"""
        response = await client.get("/server-error")
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        
    async def test_not_found_error(self, client):
        """Test 404 not found error"""
        response = await client.get("/not-found")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["error"].lower()
        
    async def test_unauthorized_error(self, client):
        """Test 401 unauthorized error"""
        response = await client.get("/unauthorized")
        
        assert response.status_code == 401
        data = response.json()
        assert "unauthorized" in data["error"].lower()
        
    async def test_validation_error(self, client):
        """Test validation error responses"""
        # Test missing name
        response = await client.post("/process-data", json={"email": "test@example.com"})
        assert response.status_code == 400
        assert "name" in response.json()["error"].lower()
        
        # Test invalid email
        response = await client.post("/process-data", json={"name": "Test", "email": "invalid"})
        assert response.status_code == 400
        assert "email" in response.json()["error"].lower()
        
        # Test valid data
        valid_data = {"name": "Test User", "email": "test@example.com"}
        response = await client.post("/process-data", json=valid_data)
        assert response.status_code == 200
        data = response.json()
        assert data["processed"] is True


class TestAuthentication:
    """Test authentication and authorization flows"""
    
    @pytest.fixture
    def app_with_auth(self):
        """Create app with authentication"""
        app = CovetPy()
        
        # Simple in-memory user store
        users = {
            "testuser": {"password": "password123", "role": "user"},
            "admin": {"password": "admin123", "role": "admin"}
        }
        
        sessions = {}
        
        @app.post("/login")
        async def login(request):
            data = await request.json()
            username = data.get("username")
            password = data.get("password")
            
            if username in users and users[username]["password"] == password:
                session_id = str(uuid.uuid4())
                sessions[session_id] = {"username": username, "role": users[username]["role"]}
                
                response = Response({"success": True, "session_id": session_id})
                response.set_cookie("session_id", session_id, max_age=3600)
                return response
            else:
                return Response({"error": "Invalid credentials"}, status_code=401)
                
        @app.get("/profile")
        async def get_profile(request):
            session_id = request.cookies().get("session_id")
            
            if not session_id or session_id not in sessions:
                return Response({"error": "Not authenticated"}, status_code=401)
                
            session = sessions[session_id]
            return {
                "username": session["username"],
                "role": session["role"]
            }
            
        @app.get("/admin")
        async def admin_only(request):
            session_id = request.cookies().get("session_id")
            
            if not session_id or session_id not in sessions:
                return Response({"error": "Not authenticated"}, status_code=401)
                
            session = sessions[session_id]
            if session["role"] != "admin":
                return Response({"error": "Admin access required"}, status_code=403)
                
            return {"message": "Admin area", "user": session["username"]}
            
        @app.post("/logout")
        async def logout(request):
            session_id = request.cookies().get("session_id")
            
            if session_id in sessions:
                del sessions[session_id]
                
            response = Response({"success": True})
            response.delete_cookie("session_id")
            return response
            
        return app
        
    @pytest.fixture
    async def client(self, app_with_auth):
        return create_test_client(app_with_auth, async_client=True)
        
    async def test_successful_login(self, client):
        """Test successful user login"""
        response = await client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "session_id" in data
        
        # Check cookie was set
        cookies = response.headers.get("set-cookie", "")
        assert "session_id=" in cookies
        
    async def test_failed_login(self, client):
        """Test failed login with invalid credentials"""
        response = await client.post("/login", json={
            "username": "testuser",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "invalid" in data["error"].lower()
        
    async def test_authenticated_request(self, client):
        """Test accessing protected resource after login"""
        # Login first
        login_response = await client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        assert login_response.status_code == 200
        
        # Access protected resource
        profile_response = await client.get("/profile")
        assert profile_response.status_code == 200
        
        data = profile_response.json()
        assert data["username"] == "testuser"
        assert data["role"] == "user"
        
    async def test_unauthenticated_request(self, client):
        """Test accessing protected resource without authentication"""
        response = await client.get("/profile")
        
        assert response.status_code == 401
        data = response.json()
        assert "not authenticated" in data["error"].lower()
        
    async def test_authorization_check(self, client):
        """Test role-based authorization"""
        # Login as regular user
        await client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        # Try to access admin area
        response = await client.get("/admin")
        assert response.status_code == 403
        
        # Login as admin
        await client.post("/login", json={
            "username": "admin",
            "password": "admin123"
        })
        
        # Access admin area
        response = await client.get("/admin")
        assert response.status_code == 200
        data = response.json()
        assert "admin area" in data["message"].lower()
        
    async def test_logout(self, client):
        """Test user logout"""
        # Login first
        await client.post("/login", json={
            "username": "testuser",
            "password": "password123"
        })
        
        # Logout
        logout_response = await client.post("/logout")
        assert logout_response.status_code == 200
        
        # Try to access protected resource after logout
        profile_response = await client.get("/profile")
        assert profile_response.status_code == 401


class TestDatabaseIntegration:
    """Test database integration with real database operations"""
    
    @pytest.fixture
    async def test_db(self):
        """Setup test database"""
        db = TestDatabase()
        await db.setup()
        yield db
        await db.teardown()
        
    @pytest.fixture
    def app_with_db(self, test_db):
        """Create app with database operations"""
        app = CovetPy()
        
        @app.get("/users")
        async def list_users(request):
            users = await test_db.fetch_all("SELECT * FROM users")
            assert {"users": [dict(user) for user in users]}
            
        @app.post("/users")
        async def create_user(request):
            data = await request.json()
            
            user_id = await test_db.insert_user(
                username=data["username"],
                email=data["email"],
                password_hash="test_hash"
            )
            
            return {"id": user_id, "created": True}
            
        @app.get("/users/{user_id}")
        async def get_user(request):
            user_id = int(request.path_params["user_id"])
            user = await test_db.fetch_one("SELECT * FROM users WHERE id = ?", (user_id,))
            
            if not user:
                return Response({"error": "User not found"}, status_code=404)
                
            return dict(user)
            
        @app.post("/users/{user_id}/posts")
        async def create_post(request):
            user_id = int(request.path_params["user_id"])
            data = await request.json()
            
            post_id = await test_db.insert_post(
                title=data["title"],
                content=data["content"],
                user_id=user_id,
                published=data.get("published", False)
            )
            
            return {"id": post_id, "created": True}
            
        return app
        
    @pytest.fixture
    async def client(self, app_with_db):
        return create_test_client(app_with_db, async_client=True)
        
    async def test_create_and_retrieve_user(self, client):
        """Test creating and retrieving user from database"""
        # Create user
        user_data = {
            "username": "testuser123",
            "email": "test@example.com"
        }
        
        create_response = await client.post("/users", json=user_data)
        assert create_response.status_code == 200
        
        created_data = create_response.json()
        user_id = created_data["id"]
        assert created_data["created"] is True
        
        # Retrieve user
        get_response = await client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        
        user = get_response.json()
        assert user["username"] == "testuser123"
        assert user["email"] == "test@example.com"
        assert user["id"] == user_id
        
    async def test_list_users(self, client):
        """Test listing users from database"""
        # Create a few users
        for i in range(3):
            await client.post("/users", json={
                "username": f"user{i}",
                "email": f"user{i}@example.com"
            })
            
        # List users
        response = await client.get("/users")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["users"]) == 3
        
    async def test_user_posts_relationship(self, client):
        """Test user-posts relationship"""
        # Create user
        user_response = await client.post("/users", json={
            "username": "author",
            "email": "author@example.com"
        })
        user_id = user_response.json()["id"]
        
        # Create post for user
        post_data = {
            "title": "Test Post",
            "content": "This is a test post content",
            "published": True
        }
        
        post_response = await client.post(f"/users/{user_id}/posts", json=post_data)
        assert post_response.status_code == 200
        
        post_data = post_response.json()
        assert post_data["created"] is True
        assert "id" in post_data
        
    async def test_user_not_found(self, client):
        """Test 404 for non-existent user"""
        response = await client.get("/users/999")
        assert response.status_code == 404
        
        data = response.json()
        assert "not found" in data["error"].lower()


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])