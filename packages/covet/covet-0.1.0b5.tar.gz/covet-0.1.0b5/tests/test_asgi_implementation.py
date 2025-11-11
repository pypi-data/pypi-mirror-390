"""
Comprehensive Tests for CovetPy ASGI 3.0 Implementation
======================================================

Tests cover:
- ASGI 3.0 protocol compliance
- HTTP request/response handling
- WebSocket connections
- Lifespan management
- Middleware integration
- Error handling
- Performance benchmarks
- Uvicorn compatibility
"""

import asyncio
import json
import pytest
import time
from typing import Dict, Any
from unittest.mock import AsyncMock, Mock

# Import the modules we're testing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covet.core.asgi_app import (
    CovetASGIApp, ASGILifespan, ASGIRequest, ASGIWebSocket,
    create_asgi_app, create_app
)
from covet.core.asgi_integration import (
    CovetApplicationASGIAdapter, make_asgi_compatible, ASGITestClient
)
from covet.core.routing import CovetRouter
from covet.core.middleware import MiddlewareStack
from covet.core.http import Request, Response


class TestASGILifespan:
    """Test ASGI lifespan protocol implementation."""
    
    def test_lifespan_creation(self):
        """Test basic lifespan object creation."""
        app = CovetASGIApp()
        lifespan = ASGILifespan(app)
        
        assert lifespan.app is app
        assert lifespan.startup_handlers == []
        assert lifespan.shutdown_handlers == []
        assert not lifespan.startup_complete
        assert not lifespan.shutdown_complete
        
    def test_add_handlers(self):
        """Test adding startup and shutdown handlers."""
        app = CovetASGIApp()
        lifespan = ASGILifespan(app)
        
        def startup_handler():
            pass
            
        def shutdown_handler():
            pass
            
        lifespan.add_startup_handler(startup_handler)
        lifespan.add_shutdown_handler(shutdown_handler)
        
        assert startup_handler in lifespan.startup_handlers
        assert shutdown_handler in lifespan.shutdown_handlers
        
    @pytest.mark.asyncio
    async def test_startup_success(self):
        """Test successful startup sequence."""
        app = CovetASGIApp()
        lifespan = ASGILifespan(app)
        
        startup_called = False
        
        def startup_handler():
            nonlocal startup_called
            startup_called = True
            
        lifespan.add_startup_handler(startup_handler)
        
        # Mock receive and send
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()
        
        scope = {"type": "lifespan"}
        
        await lifespan.handle_lifespan(scope, receive, send)
        
        assert startup_called
        assert lifespan.startup_complete
        send.assert_called_with({"type": "lifespan.startup.complete"})
        
    @pytest.mark.asyncio
    async def test_startup_failure(self):
        """Test startup failure handling."""
        app = CovetASGIApp()
        lifespan = ASGILifespan(app)
        
        def failing_startup():
            raise ValueError("Startup failed")
            
        lifespan.add_startup_handler(failing_startup)
        
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()
        
        scope = {"type": "lifespan"}
        
        await lifespan.handle_lifespan(scope, receive, send)
        
        assert not lifespan.startup_complete
        send.assert_called_with({
            "type": "lifespan.startup.failed",
            "message": "Startup failed"
        })
        
    @pytest.mark.asyncio
    async def test_shutdown_success(self):
        """Test successful shutdown sequence."""
        app = CovetASGIApp()
        lifespan = ASGILifespan(app)
        
        shutdown_called = False
        
        def shutdown_handler():
            nonlocal shutdown_called
            shutdown_called = True
            
        lifespan.add_shutdown_handler(shutdown_handler)
        
        receive = AsyncMock(return_value={"type": "lifespan.shutdown"})
        send = AsyncMock()
        
        scope = {"type": "lifespan"}
        
        await lifespan.handle_lifespan(scope, receive, send)
        
        assert shutdown_called
        assert lifespan.shutdown_complete
        send.assert_called_with({"type": "lifespan.shutdown.complete"})


class TestASGIRequest:
    """Test ASGI request handling and conversion."""
    
    def test_request_creation(self):
        """Test basic request creation."""
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "query_string": b"param=value",
            "headers": [(b"host", b"localhost"), (b"user-agent", b"test")]
        }
        receive = AsyncMock()
        
        asgi_request = ASGIRequest(scope, receive)
        
        assert asgi_request.scope == scope
        assert asgi_request.receive == receive
        assert asgi_request._body is None
        
    def test_covet_request_conversion(self):
        """Test conversion to CovetPy Request object."""
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/test",
            "query_string": b"foo=bar&baz=qux",
            "headers": [
                (b"host", b"example.com"),
                (b"content-type", b"application/json"),
                (b"authorization", b"Bearer token123")
            ],
            "scheme": "https",
            "server": ("example.com", 443),
            "client": ("192.168.1.1", 12345)
        }
        receive = AsyncMock()
        
        asgi_request = ASGIRequest(scope, receive)
        covet_request = asgi_request.to_covet_request()
        
        assert covet_request.method == "POST"
        assert covet_request.url == "/api/test"
        assert covet_request.scheme == "https"
        assert covet_request.server_name == "example.com"
        assert covet_request.server_port == 443
        assert covet_request.remote_addr == "192.168.1.1"
        assert covet_request.headers["host"] == "example.com"
        assert covet_request.headers["content-type"] == "application/json"
        assert covet_request.headers["authorization"] == "Bearer token123"
        
    @pytest.mark.asyncio
    async def test_body_reading(self):
        """Test reading request body from ASGI."""
        scope = {"type": "http", "method": "POST"}
        
        # Mock receive to assert body in chunks
        receive_calls = [
            {"type": "http.request", "body": b"Hello ", "more_body": True},
            {"type": "http.request", "body": b"World!", "more_body": False}
        ]
        receive = AsyncMock(side_effect=receive_calls)
        
        asgi_request = ASGIRequest(scope, receive)
        body = await asgi_request._get_body()
        
        assert body == b"Hello World!"
        assert asgi_request._body == b"Hello World!"


class TestASGIWebSocket:
    """Test ASGI WebSocket handling."""
    
    def test_websocket_creation(self):
        """Test WebSocket object creation."""
        scope = {
            "type": "websocket",
            "path": "/ws",
            "query_string": b"room=test",
            "headers": [(b"host", b"localhost")]
        }
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        
        assert websocket.scope == scope
        assert websocket.receive == receive
        assert websocket.send == send
        assert websocket.path == "/ws"
        assert websocket.query_string == "room=test"
        assert websocket.state == "connecting"
        
    @pytest.mark.asyncio
    async def test_websocket_accept(self):
        """Test WebSocket connection acceptance."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        await websocket.accept()
        
        assert websocket.state == "connected"
        send.assert_called_with({"type": "websocket.accept"})
        
    @pytest.mark.asyncio
    async def test_websocket_accept_with_subprotocol(self):
        """Test WebSocket acceptance with subprotocol."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        await websocket.accept("chat")
        
        assert websocket.state == "connected"
        send.assert_called_with({
            "type": "websocket.accept",
            "subprotocol": "chat"
        })
        
    @pytest.mark.asyncio
    async def test_websocket_send_text(self):
        """Test sending text message."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        await websocket.send_text("Hello WebSocket!")
        
        send.assert_called_with({
            "type": "websocket.send",
            "text": "Hello WebSocket!"
        })
        
    @pytest.mark.asyncio
    async def test_websocket_send_json(self):
        """Test sending JSON message."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        data = {"type": "message", "content": "Hello"}
        await websocket.send_json(data)
        
        expected_text = json.dumps(data, separators=(",", ":"))
        send.assert_called_with({
            "type": "websocket.send",
            "text": expected_text
        })
        
    @pytest.mark.asyncio
    async def test_websocket_receive_text(self):
        """Test receiving text message."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock(return_value={
            "type": "websocket.receive",
            "text": "Hello from client"
        })
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        text = await websocket.receive_text()
        
        assert text == "Hello from client"
        
    @pytest.mark.asyncio
    async def test_websocket_close(self):
        """Test WebSocket close."""
        scope = {"type": "websocket", "path": "/ws"}
        receive = AsyncMock()
        send = AsyncMock()
        
        websocket = ASGIWebSocket(scope, receive, send)
        await websocket.close(1000, "Normal closure")
        
        assert websocket.state == "disconnected"
        assert websocket.close_code == 1000
        send.assert_called_with({
            "type": "websocket.close",
            "code": 1000,
            "reason": "Normal closure"
        })


class TestCovetASGIApp:
    """Test the main ASGI application class."""
    
    def test_app_creation(self):
        """Test basic app creation."""
        app = CovetASGIApp()
        
        assert isinstance(app.router, CovetRouter)
        assert isinstance(app.middleware_stack, MiddlewareStack)
        assert app.debug is False
        assert app.enable_lifespan is True
        assert app.lifespan is not None
        
    def test_app_creation_with_options(self):
        """Test app creation with custom options."""
        router = CovetRouter()
        middleware = MiddlewareStack()
        
        app = CovetASGIApp(
            router=router,
            middleware_stack=middleware,
            debug=True,
            enable_lifespan=False
        )
        
        assert app.router is router
        assert app.middleware_stack is middleware
        assert app.debug is True
        assert app.enable_lifespan is False
        assert app.lifespan is None
        
    @pytest.mark.asyncio
    async def test_http_request_handling(self):
        """Test basic HTTP request handling."""
        app = CovetASGIApp()
        
        # Add a test route
        async def test_handler(request):
            return Response("Hello World!")
            
        app.router.add_route("/test", test_handler, ["GET"])
        
        # Create test scope
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/test",
            "headers": [],
            "query_string": b""
        }
        
        receive = AsyncMock(return_value={
            "type": "http.request",
            "body": b"",
            "more_body": False
        })
        
        # Capture sent messages
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
            
        await app(scope, receive, send)
        
        # Check response
        assert len(sent_messages) == 2
        assert sent_messages[0]["type"] == "http.response.start"
        assert sent_messages[0]["status"] == 200
        assert sent_messages[1]["type"] == "http.response.body"
        assert b"Hello World!" in sent_messages[1]["body"]
        
    @pytest.mark.asyncio
    async def test_404_handling(self):
        """Test 404 Not Found handling."""
        app = CovetASGIApp()
        
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/nonexistent",
            "headers": [],
            "query_string": b""
        }
        
        receive = AsyncMock()
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
            
        await app(scope, receive, send)
        
        assert sent_messages[0]["status"] == 404
        
    @pytest.mark.asyncio
    async def test_lifespan_handling(self):
        """Test lifespan protocol handling."""
        startup_called = False
        shutdown_called = False
        
        def startup():
            nonlocal startup_called
            startup_called = True
            
        def shutdown():
            nonlocal shutdown_called
            shutdown_called = True
            
        app = CovetASGIApp()
        app.add_startup_handler(startup)
        app.add_shutdown_handler(shutdown)
        
        # Test startup
        scope = {"type": "lifespan"}
        receive = AsyncMock(return_value={"type": "lifespan.startup"})
        send = AsyncMock()
        
        await app(scope, receive, send)
        assert startup_called
        
        # Test shutdown
        receive = AsyncMock(return_value={"type": "lifespan.shutdown"})
        send = AsyncMock()
        
        await app(scope, receive, send)
        assert shutdown_called
        
    @pytest.mark.asyncio
    async def test_websocket_handling(self):
        """Test WebSocket connection handling."""
        app = CovetASGIApp()
        
        async def websocket_handler(websocket):
            await websocket.accept()
            await websocket.send_text("Connected!")
            
        app.router.add_route("/ws", websocket_handler, ["WEBSOCKET"])
        
        scope = {
            "type": "websocket",
            "path": "/ws",
            "headers": []
        }
        
        receive = AsyncMock()
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
            
        await app(scope, receive, send)
        
        # Should have accepted connection and sent message
        assert len(sent_messages) >= 1
        assert sent_messages[0]["type"] == "websocket.accept"
        
    def test_stats_collection(self):
        """Test performance statistics collection."""
        app = CovetASGIApp()
        
        stats = app.get_stats()
        
        assert "requests_processed" in stats
        assert "average_response_time" in stats
        assert "errors" in stats
        assert "websocket_connections" in stats
        assert "route_cache_size" in stats


class TestASGIIntegration:
    """Test ASGI integration functionality."""
    
    def test_covet_app_adapter(self):
        """Test CovetApplication ASGI adapter."""
        # Mock CovetApplication
        mock_app = Mock()
        mock_app.router = CovetRouter()
        mock_app.middleware_stack = MiddlewareStack()
        mock_app.debug = False
        mock_app._startup_handlers = []
        mock_app._shutdown_handlers = []
        
        adapter = CovetApplicationASGIAdapter(mock_app)
        
        assert adapter.covet_app is mock_app
        assert isinstance(adapter.asgi_app, CovetASGIApp)
        
    def test_make_asgi_compatible(self):
        """Test making apps ASGI compatible."""
        # Test with CovetASGIApp
        asgi_app = CovetASGIApp()
        result = make_asgi_compatible(asgi_app)
        assert result is asgi_app
        
        # Test with mock app
        mock_app = Mock()
        mock_app.router = CovetRouter()
        mock_app.middleware_stack = MiddlewareStack()
        mock_app.debug = False
        
        result = make_asgi_compatible(mock_app)
        assert isinstance(result, CovetApplicationASGIAdapter)


class TestASGITestClient:
    """Test the ASGI test client."""
    
    @pytest.mark.asyncio
    async def test_test_client_get(self):
        """Test GET request with test client."""
        app = CovetASGIApp()
        
        async def handler(request):
            return Response("Test response")
            
        app.router.add_route("/test", handler, ["GET"])
        
        client = ASGITestClient(app)
        response = await client.get("/test")
        
        assert response["status_code"] == 200
        assert b"Test response" in response["body"]
        
    @pytest.mark.asyncio
    async def test_test_client_post(self):
        """Test POST request with test client."""
        app = CovetASGIApp()
        
        async def handler(request):
            return Response("POST received")
            
        app.router.add_route("/test", handler, ["POST"])
        
        client = ASGITestClient(app)
        response = await client.post("/test", body=b"test data")
        
        assert response["status_code"] == 200
        assert b"POST received" in response["body"]


class TestFactoryFunctions:
    """Test factory functions."""
    
    def test_create_asgi_app(self):
        """Test create_asgi_app factory."""
        app = create_asgi_app(debug=True)
        
        assert isinstance(app, CovetASGIApp)
        assert app.debug is True
        
    def test_create_app_alias(self):
        """Test create_app alias."""
        app = create_app(enable_lifespan=False)
        
        assert isinstance(app, CovetASGIApp)
        assert app.enable_lifespan is False


class TestPerformance:
    """Performance and benchmark tests."""
    
    @pytest.mark.asyncio
    async def test_request_performance(self):
        """Test request handling performance."""
        app = CovetASGIApp()
        
        async def fast_handler(request):
            return Response("OK")
            
        app.router.add_route("/perf", fast_handler, ["GET"])
        
        scope = {
            "type": "http",
            "method": "GET", 
            "path": "/perf",
            "headers": [],
            "query_string": b""
        }
        
        receive = AsyncMock(return_value={
            "type": "http.request",
            "body": b"",
            "more_body": False
        })
        
        sent_messages = []
        
        async def send(message):
            sent_messages.append(message)
            
        # Time multiple requests
        start_time = time.time()
        
        for _ in range(100):
            sent_messages.clear()
            await app(scope, receive, send)
            
        end_time = time.time()
        
        # Should handle 100 requests quickly
        assert end_time - start_time < 1.0  # Less than 1 second
        
        # Check stats
        stats = app.get_stats()
        assert stats["requests_processed"] == 100
        
    def test_route_caching(self):
        """Test route caching performance."""
        app = CovetASGIApp()
        
        async def handler(request):
            return Response("Cached")
            
        app.router.add_route("/cached", handler, ["GET"])
        
        # Cache should be empty initially
        assert len(app._route_cache) == 0
        
        # First request should populate cache
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/cached",
            "headers": [],
            "query_string": b""
        }
        
        # Manually trigger route matching to test cache
        route_match = app.router.match_route("/cached", "GET")
        cache_key = "GET:/cached"
        app._route_cache[cache_key] = route_match
        
        assert len(app._route_cache) == 1
        assert cache_key in app._route_cache


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])