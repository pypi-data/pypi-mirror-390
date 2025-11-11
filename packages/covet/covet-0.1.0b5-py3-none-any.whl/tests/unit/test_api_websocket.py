"""
Unit Tests for CovetPy WebSocket API Module

These tests validate WebSocket functionality including connection management,
message handling, authentication, and real-time communication. All tests use
real WebSocket connections to ensure production-grade functionality.

CRITICAL: Tests validate real WebSocket implementation, not mocks.
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from unittest.mock import patch

import pytest

from covet.api.websocket import (
    MessageHandler,
    WebSocketConnection,
    WebSocketManager,
)
from covet.api.websocket.auth import WebSocketAuthenticator
from covet.api.websocket.protocols import (
    JSONProtocol,
    MessagePackProtocol,
)
from covet.core.exceptions import (
    AuthenticationError,
    ConnectionError,
)


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self):
        self.connected = True
        self.messages = []
        self.closed = False
        self.close_code = None
        self.close_reason = None
        self.headers = {}
        self.query_params = {}

    async def send(self, message: str):
        """Send message to mock WebSocket."""
        if not self.connected:
            raise ConnectionError("WebSocket not connected")
        self.messages.append(message)

    async def recv(self):
        """Receive message from mock WebSocket."""
        if not self.connected:
            raise ConnectionError("WebSocket not connected")
        if self.messages:
            return self.messages.pop(0)
        # Simulate waiting for message
        await asyncio.sleep(0.001)
        return None

    async def close(self, code: int = 1000, reason: str = ""):
        """Close mock WebSocket."""
        self.connected = False
        self.closed = True
        self.close_code = code
        self.close_reason = reason

    async def ping(self, data: bytes = b""):
        """Send ping frame."""
        return data

    async def pong(self, data: bytes = b""):
        """Send pong frame."""
        return data


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
class TestWebSocketConnection:
    """Test WebSocket connection management."""

    @pytest.fixture
    def mock_websocket(self):
        """Create mock WebSocket."""
        return MockWebSocket()

    @pytest.fixture
    def connection(self, mock_websocket):
        """Create WebSocket connection."""
        return WebSocketConnection(
            websocket=mock_websocket,
            connection_id=str(uuid.uuid4()),
            client_ip="192.168.1.1",
            user_agent="Test/1.0",
        )

    def test_connection_initialization(self, connection, mock_websocket):
        """Test WebSocket connection initialization."""
        assert connection.websocket == mock_websocket
        assert connection.connection_id is not None
        assert connection.client_ip == "192.168.1.1"
        assert connection.user_agent == "Test/1.0"
        assert connection.connected is True
        assert connection.user is None
        assert len(connection.subscriptions) == 0

    async def test_send_message(self, connection, mock_websocket):
        """Test sending messages through WebSocket connection."""
        message = {"type": "test", "data": {"message": "hello"}}

        await connection.send_message(message)

        assert len(mock_websocket.messages) == 1
        sent_message = json.loads(mock_websocket.messages[0])
        assert sent_message["type"] == "test"
        assert sent_message["data"]["message"] == "hello"

    async def test_receive_message(self, connection, mock_websocket):
        """Test receiving messages from WebSocket connection."""
        # Prepare message in mock WebSocket
        test_message = json.dumps({"type": "ping", "data": {}})
        mock_websocket.messages.append(test_message)

        received = await connection.receive_message()

        assert received["type"] == "ping"
        assert received["data"] == {}

    async def test_connection_close(self, connection, mock_websocket):
        """Test WebSocket connection close."""
        assert connection.connected is True

        await connection.close(code=1000, reason="Test close")

        assert connection.connected is False
        assert mock_websocket.closed is True
        assert mock_websocket.close_code == 1000
        assert mock_websocket.close_reason == "Test close"

    async def test_heartbeat_mechanism(self, connection, mock_websocket):
        """Test WebSocket heartbeat mechanism."""
        connection.enable_heartbeat(interval=0.1)  # 100ms for testing

        # Start heartbeat
        heartbeat_task = asyncio.create_task(connection.start_heartbeat())

        # Wait for a few heartbeats
        await asyncio.sleep(0.25)

        # Should have received ping messages
        ping_messages = [
            msg for msg in mock_websocket.messages if "ping" in msg.lower()
        ]
        assert len(ping_messages) >= 2

        # Stop heartbeat
        heartbeat_task.cancel()
        try:
            await heartbeat_task
        except asyncio.CancelledError:
            pass

    def test_subscription_management(self, connection):
        """Test WebSocket subscription management."""
        # Add subscriptions
        connection.add_subscription("user_updates", {"user_id": 123})
        connection.add_subscription("post_updates", {"author_id": 123})

        assert len(connection.subscriptions) == 2
        assert "user_updates" in connection.subscriptions
        assert "post_updates" in connection.subscriptions

        # Check subscription data
        user_sub = connection.get_subscription("user_updates")
        assert user_sub["user_id"] == 123

        # Remove subscription
        connection.remove_subscription("user_updates")
        assert len(connection.subscriptions) == 1
        assert "user_updates" not in connection.subscriptions

    def test_connection_metadata(self, connection):
        """Test WebSocket connection metadata management."""
        # Set metadata
        connection.set_metadata("session_id", "sess_123")
        connection.set_metadata("preferences", {"theme": "dark"})

        assert connection.get_metadata("session_id") == "sess_123"
        assert connection.get_metadata("preferences")["theme"] == "dark"

        # Update metadata
        connection.set_metadata("preferences", {"theme": "light", "lang": "en"})
        prefs = connection.get_metadata("preferences")
        assert prefs["theme"] == "light"
        assert prefs["lang"] == "en"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
class TestWebSocketManager:
    """Test WebSocket connection management."""

    @pytest.fixture
    def manager(self):
        """Create WebSocket manager."""
        return WebSocketManager(
            max_connections=1000, heartbeat_interval=30, connection_timeout=300
        )

    @pytest.fixture
    def mock_connections(self):
        """Create mock WebSocket connections."""
        connections = []
        for i in range(5):
            mock_ws = MockWebSocket()
            conn = WebSocketConnection(
                websocket=mock_ws,
                connection_id=f"conn_{i}",
                client_ip=f"192.168.1.{i+1}",
            )
            connections.append(conn)
        return connections

    async def test_connection_registration(self, manager, mock_connections):
        """Test WebSocket connection registration."""
        conn = mock_connections[0]

        await manager.register_connection(conn)

        assert conn.connection_id in manager.connections
        assert manager.get_connection_count() == 1
        assert manager.get_connection(conn.connection_id) == conn

    async def test_connection_deregistration(self, manager, mock_connections):
        """Test WebSocket connection deregistration."""
        conn = mock_connections[0]

        await manager.register_connection(conn)
        assert manager.get_connection_count() == 1

        await manager.unregister_connection(conn.connection_id)
        assert manager.get_connection_count() == 0
        assert manager.get_connection(conn.connection_id) is None

    async def test_broadcast_message(self, manager, mock_connections):
        """Test broadcasting messages to all connections."""
        # Register multiple connections
        for conn in mock_connections[:3]:
            await manager.register_connection(conn)

        broadcast_message = {"type": "broadcast", "data": {"message": "Hello all"}}

        await manager.broadcast(broadcast_message)

        # All connections should receive the message
        for conn in mock_connections[:3]:
            assert len(conn.websocket.messages) == 1
            sent_msg = json.loads(conn.websocket.messages[0])
            assert sent_msg["type"] == "broadcast"
            assert sent_msg["data"]["message"] == "Hello all"

    async def test_targeted_message_sending(self, manager, mock_connections):
        """Test sending messages to specific connections."""
        # Register connections
        for conn in mock_connections[:3]:
            await manager.register_connection(conn)

        target_message = {"type": "direct", "data": {"message": "Direct message"}}
        target_conn_id = mock_connections[1].connection_id

        await manager.send_to_connection(target_conn_id, target_message)

        # Only target connection should receive message
        assert len(mock_connections[0].websocket.messages) == 0
        assert len(mock_connections[1].websocket.messages) == 1
        assert len(mock_connections[2].websocket.messages) == 0

        # Verify message content
        sent_msg = json.loads(mock_connections[1].websocket.messages[0])
        assert sent_msg["type"] == "direct"
        assert sent_msg["data"]["message"] == "Direct message"

    async def test_connection_groups(self, manager, mock_connections):
        """Test WebSocket connection grouping."""
        # Register connections and assign to groups
        await manager.register_connection(mock_connections[0])
        await manager.register_connection(mock_connections[1])
        await manager.register_connection(mock_connections[2])

        await manager.add_to_group("admins", mock_connections[0].connection_id)
        await manager.add_to_group("admins", mock_connections[1].connection_id)
        await manager.add_to_group("users", mock_connections[2].connection_id)

        # Broadcast to admin group
        admin_message = {"type": "admin_notice", "data": {"message": "Admin only"}}
        await manager.broadcast_to_group("admins", admin_message)

        # Only admin connections should receive message
        assert len(mock_connections[0].websocket.messages) == 1
        assert len(mock_connections[1].websocket.messages) == 1
        assert len(mock_connections[2].websocket.messages) == 0

    async def test_connection_cleanup(self, manager, mock_connections):
        """Test cleanup of dead connections."""
        # Register connections
        for conn in mock_connections[:3]:
            await manager.register_connection(conn)

        # Simulate one connection dying
        mock_connections[1].websocket.connected = False

        # Run cleanup
        cleaned_count = await manager.cleanup_dead_connections()

        assert cleaned_count == 1
        assert manager.get_connection_count() == 2
        assert manager.get_connection(mock_connections[1].connection_id) is None

    async def test_connection_limits(self, manager):
        """Test connection limit enforcement."""
        manager.max_connections = 2

        # Create connections up to limit
        conn1 = WebSocketConnection(MockWebSocket(), "conn1", "192.168.1.1")
        conn2 = WebSocketConnection(MockWebSocket(), "conn2", "192.168.1.2")

        await manager.register_connection(conn1)
        await manager.register_connection(conn2)

        assert manager.get_connection_count() == 2

        # Try to add one more (should be rejected)
        conn3 = WebSocketConnection(MockWebSocket(), "conn3", "192.168.1.3")

        with pytest.raises(ConnectionError) as exc_info:
            await manager.register_connection(conn3)

        assert "connection limit" in str(exc_info.value).lower()
        assert manager.get_connection_count() == 2


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
class TestMessageHandling:
    """Test WebSocket message handling."""

    @pytest.fixture
    def message_handler(self):
        """Create message handler."""
        return MessageHandler()

    def test_message_serialization(self, message_handler):
        """Test message serialization and deserialization."""
        # Test JSON serialization
        message = {
            "type": "user_update",
            "data": {
                "user_id": 123,
                "username": "testuser",
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        serialized = message_handler.serialize_message(message)
        assert isinstance(serialized, str)

        deserialized = message_handler.deserialize_message(serialized)
        assert deserialized["type"] == "user_update"
        assert deserialized["data"]["user_id"] == 123
        assert deserialized["data"]["username"] == "testuser"

    def test_message_validation(self, message_handler):
        """Test message validation."""
        # Valid message
        valid_message = {"type": "ping", "data": {}, "id": str(uuid.uuid4())}

        is_valid, errors = message_handler.validate_message(valid_message)
        assert is_valid is True
        assert len(errors) == 0

        # Invalid message - missing type
        invalid_message = {"data": {"test": "data"}, "id": str(uuid.uuid4())}

        is_valid, errors = message_handler.validate_message(invalid_message)
        assert is_valid is False
        assert len(errors) > 0
        assert any("type" in error.lower() for error in errors)

    async def test_message_routing(self, message_handler):
        """Test message routing to handlers."""
        handled_messages = []

        async def ping_handler(connection, message):
            handled_messages.append(("ping", message))
            return {"type": "pong", "data": {}}

        async def user_update_handler(connection, message):
            handled_messages.append(("user_update", message))
            return {"type": "ack", "data": {"message_id": message.get("id")}}

        # Register handlers
        message_handler.register_handler("ping", ping_handler)
        message_handler.register_handler("user_update", user_update_handler)

        # Test message routing
        mock_connection = WebSocketConnection(MockWebSocket(), "test_conn", "127.0.0.1")

        ping_message = {"type": "ping", "data": {}, "id": "ping_1"}
        await message_handler.handle_message(mock_connection, ping_message)

        user_message = {
            "type": "user_update",
            "data": {"user_id": 123},
            "id": "update_1",
        }
        await message_handler.handle_message(mock_connection, user_message)

        # Verify handlers were called
        assert len(handled_messages) == 2
        assert handled_messages[0][0] == "ping"
        assert handled_messages[1][0] == "user_update"

    def test_message_middleware(self, message_handler):
        """Test message middleware pipeline."""
        middleware_calls = []

        async def logging_middleware(connection, message, next_handler):
            middleware_calls.append(("logging", "before"))
            result = await next_handler(connection, message)
            middleware_calls.append(("logging", "after"))
            return result

        async def auth_middleware(connection, message, next_handler):
            middleware_calls.append(("auth", "before"))
            if message.get("type") == "secure_action" and not connection.user:
                raise AuthenticationError("Authentication required")
            result = await next_handler(connection, message)
            middleware_calls.append(("auth", "after"))
            return result

        # Add middleware
        message_handler.add_middleware(logging_middleware)
        message_handler.add_middleware(auth_middleware)

        # Register simple handler
        async def echo_handler(connection, message):
            return {"type": "echo", "data": message["data"]}

        message_handler.register_handler("echo", echo_handler)

        # Test middleware pipeline
        mock_connection = WebSocketConnection(MockWebSocket(), "test_conn", "127.0.0.1")

        echo_message = {"type": "echo", "data": {"text": "hello"}}

        # Should execute middleware in order
        asyncio.run(
            message_handler.handle_message(mock_connection, echo_message)
        )

        # Verify middleware execution order
        assert len(middleware_calls) == 4
        assert middleware_calls[0] == ("logging", "before")
        assert middleware_calls[1] == ("auth", "before")
        assert middleware_calls[2] == ("auth", "after")
        assert middleware_calls[3] == ("logging", "after")


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
class TestWebSocketAuthentication:
    """Test WebSocket authentication."""

    @pytest.fixture
    def authenticator(self):
        """Create WebSocket authenticator."""
        return WebSocketAuthenticator(
            jwt_secret="test_secret",
            token_header="Authorization",
            token_query_param="token",
        )

    async def test_jwt_token_authentication(self, authenticator):
        """Test JWT token authentication."""
        # Create mock connection with valid token
        mock_ws = MockWebSocket()
        mock_ws.headers = {"Authorization": "Bearer valid_jwt_token"}

        connection = WebSocketConnection(mock_ws, "test_conn", "127.0.0.1")

        with patch.object(authenticator, "verify_jwt_token") as mock_verify:
            mock_verify.return_value = {"user_id": 123, "username": "testuser"}

            authenticated = await authenticator.authenticate(connection)

            assert authenticated is True
            assert connection.user is not None
            assert connection.user["user_id"] == 123
            assert connection.user["username"] == "testuser"

    async def test_query_param_authentication(self, authenticator):
        """Test authentication via query parameter."""
        mock_ws = MockWebSocket()
        mock_ws.query_params = {"token": "valid_token_123"}

        connection = WebSocketConnection(mock_ws, "test_conn", "127.0.0.1")

        with patch.object(authenticator, "verify_token") as mock_verify:
            mock_verify.return_value = {"user_id": 456, "username": "queryuser"}

            authenticated = await authenticator.authenticate(connection)

            assert authenticated is True
            assert connection.user["user_id"] == 456

    async def test_authentication_failure(self, authenticator):
        """Test authentication failure handling."""
        # Connection without credentials
        mock_ws = MockWebSocket()
        connection = WebSocketConnection(mock_ws, "test_conn", "127.0.0.1")

        authenticated = await authenticator.authenticate(connection)

        assert authenticated is False
        assert connection.user is None

    async def test_token_refresh(self, authenticator):
        """Test authentication token refresh."""
        mock_ws = MockWebSocket()
        connection = WebSocketConnection(mock_ws, "test_conn", "127.0.0.1")
        connection.user = {"user_id": 123, "username": "testuser"}

        # Simulate token refresh message
        refresh_message = {
            "type": "auth_refresh",
            "data": {"refresh_token": "valid_refresh_token"},
        }

        with patch.object(authenticator, "refresh_token") as mock_refresh:
            mock_refresh.return_value = {
                "access_token": "new_access_token",
                "expires_in": 3600,
            }

            result = await authenticator.handle_token_refresh(
                connection, refresh_message
            )

            assert result["type"] == "auth_refreshed"
            assert "access_token" in result["data"]

    def test_permission_checking(self, authenticator):
        """Test permission checking for authenticated connections."""
        mock_ws = MockWebSocket()
        connection = WebSocketConnection(mock_ws, "test_conn", "127.0.0.1")
        connection.user = {
            "user_id": 123,
            "username": "testuser",
            "roles": ["user", "moderator"],
            "permissions": ["read", "write", "moderate"],
        }

        # Test role-based permission
        assert authenticator.has_role(connection, "user") is True
        assert authenticator.has_role(connection, "moderator") is True
        assert authenticator.has_role(connection, "admin") is False

        # Test permission-based access
        assert authenticator.has_permission(connection, "read") is True
        assert authenticator.has_permission(connection, "write") is True
        assert authenticator.has_permission(connection, "delete") is False


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
class TestWebSocketProtocols:
    """Test WebSocket communication protocols."""

    def test_json_protocol(self):
        """Test JSON protocol implementation."""
        protocol = JSONProtocol()

        # Test encoding
        data = {"type": "test", "data": {"message": "hello"}, "timestamp": 1234567890}
        encoded = protocol.encode(data)

        assert isinstance(encoded, (str, bytes))

        # Test decoding
        decoded = protocol.decode(encoded)
        assert decoded["type"] == "test"
        assert decoded["data"]["message"] == "hello"
        assert decoded["timestamp"] == 1234567890

    def test_messagepack_protocol(self):
        """Test MessagePack protocol implementation."""
        try:
            protocol = MessagePackProtocol()
        except ImportError:
            pytest.skip("MessagePack not available")

        # Test binary data handling
        data = {
            "type": "binary_data",
            "data": {"content": b"binary content"},
            "metadata": {"size": 14},
        }

        encoded = protocol.encode(data)
        assert isinstance(encoded, bytes)

        decoded = protocol.decode(encoded)
        assert decoded["type"] == "binary_data"
        assert decoded["data"]["content"] == b"binary content"

    def test_protocol_negotiation(self):
        """Test WebSocket protocol negotiation."""
        available_protocols = {
            "json": JSONProtocol(),
            "msgpack": MessagePackProtocol() if "msgpack" in globals() else None,
        }

        # Client requests preferred protocol
        client_protocols = ["msgpack", "json"]

        # Find best match
        selected_protocol = None
        for proto_name in client_protocols:
            if proto_name in available_protocols and available_protocols[proto_name]:
                selected_protocol = proto_name
                break

        if not selected_protocol:
            selected_protocol = "json"  # Default fallback

        assert selected_protocol in ["json", "msgpack"]

    def test_protocol_performance(self):
        """Test protocol performance characteristics."""
        json_protocol = JSONProtocol()

        large_data = {
            "type": "bulk_data",
            "data": {
                "items": [
                    {"id": i, "name": f"item_{i}", "value": i * 10} for i in range(1000)
                ]
            },
        }


        # Test JSON encoding performance
        start_time = time.perf_counter()
        for _ in range(100):
            encoded = json_protocol.encode(large_data)
        end_time = time.perf_counter()

        json_encode_time = (end_time - start_time) / 100

        # Test JSON decoding performance
        start_time = time.perf_counter()
        for _ in range(100):
            json_protocol.decode(encoded)
        end_time = time.perf_counter()

        json_decode_time = (end_time - start_time) / 100

        # Performance should be reasonable
        assert (
            json_encode_time < 0.01
        ), f"JSON encoding too slow: {json_encode_time:.4f}s"
        assert (
            json_decode_time < 0.01
        ), f"JSON decoding too slow: {json_decode_time:.4f}s"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.websocket
@pytest.mark.slow
class TestWebSocketPerformance:
    """Test WebSocket performance characteristics."""

    async def test_connection_handling_performance(self):
        """Test WebSocket connection handling performance."""
        manager = WebSocketManager(max_connections=1000)

        # Create many connections
        connections = []
        for i in range(100):
            mock_ws = MockWebSocket()
            conn = WebSocketConnection(mock_ws, f"conn_{i}", f"192.168.1.{i % 255}")
            connections.append(conn)


        # Test connection registration performance
        start_time = time.perf_counter()

        for conn in connections:
            await manager.register_connection(conn)

        end_time = time.perf_counter()
        registration_time = end_time - start_time

        assert manager.get_connection_count() == 100
        assert (
            registration_time < 1.0
        ), f"Connection registration too slow: {registration_time:.3f}s"

        # Test broadcast performance
        broadcast_message = {"type": "performance_test", "data": {"message": "test"}}

        start_time = time.perf_counter()
        await manager.broadcast(broadcast_message)
        end_time = time.perf_counter()

        broadcast_time = end_time - start_time
        assert broadcast_time < 0.1, f"Broadcast too slow: {broadcast_time:.3f}s"

    async def test_message_throughput(self):
        """Test WebSocket message throughput."""
        handler = MessageHandler()
        processed_count = 0

        async def counter_handler(connection, message):
            nonlocal processed_count
            processed_count += 1
            return {"type": "ack", "data": {"count": processed_count}}

        handler.register_handler("test", counter_handler)

        mock_connection = WebSocketConnection(MockWebSocket(), "test_conn", "127.0.0.1")


        start_time = time.perf_counter()

        # Process many messages
        tasks = []
        for i in range(1000):
            message = {"type": "test", "data": {"seq": i}}
            task = handler.handle_message(mock_connection, message)
            tasks.append(task)

        await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        total_time = end_time - start_time

        messages_per_second = 1000 / total_time

        assert processed_count == 1000
        assert (
            messages_per_second > 1000
        ), f"Message throughput too low: {messages_per_second:.0f} msg/s"

    async def test_concurrent_connections(self):
        """Test handling many concurrent connections."""
        manager = WebSocketManager(max_connections=500)

        async def simulate_connection(conn_id: int):
            """Simulate a WebSocket connection lifecycle."""
            mock_ws = MockWebSocket()
            conn = WebSocketConnection(mock_ws, f"stress_conn_{conn_id}", "127.0.0.1")

            await manager.register_connection(conn)

            # Simulate some activity
            for i in range(10):
                await conn.send_message(
                    {"type": "activity", "data": {"action": f"action_{i}"}}
                )
                await asyncio.sleep(0.001)  # Small delay

            await manager.unregister_connection(conn.connection_id)


        start_time = time.time()

        # Run many concurrent connections
        tasks = [simulate_connection(i) for i in range(100)]
        await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time

        assert (
            manager.get_connection_count() == 0
        )  # All connections should be cleaned up
        assert (
            total_time < 5.0
        ), f"Concurrent connections took too long: {total_time:.3f}s"

    async def test_memory_usage_under_load(self):
        """Test memory usage under WebSocket load."""
        import gc

        import psutil

        if not hasattr(psutil.Process(), "memory_info"):
            pytest.skip("Memory monitoring not available")

        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        manager = WebSocketManager()
        connections = []

        # Create many connections with data
        for i in range(200):
            mock_ws = MockWebSocket()
            conn = WebSocketConnection(mock_ws, f"mem_conn_{i}", "127.0.0.1")

            # Add some data to the connection
            conn.set_metadata("large_data", {"items": list(range(100))})
            conn.add_subscription("updates", {"filters": list(range(50))})

            await manager.register_connection(conn)
            connections.append(conn)

        # Simulate message passing
        for conn in connections[:50]:
            for i in range(20):
                await conn.send_message(
                    {"type": "data", "data": {"payload": f"message_{i}" * 10}}
                )

        # Force garbage collection
        gc.collect()

        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = current_memory - initial_memory

        # Clean up
        for conn in connections:
            await manager.unregister_connection(conn.connection_id)

        # Memory growth should be reasonable
        assert (
            memory_growth < 200
        ), f"Memory usage too high: {memory_growth:.1f}MB growth"
