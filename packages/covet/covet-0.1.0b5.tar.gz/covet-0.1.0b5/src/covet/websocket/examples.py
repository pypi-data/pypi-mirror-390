"""
Comprehensive WebSocket Examples for CovetPy

This module provides real-world examples of how to use the CovetPy WebSocket
framework for various use cases including chat applications, real-time data
streaming, gaming, notifications, and more.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, List, Optional

from . import (
    AuthMethod,
    ClientConfig,
    CovetWebSocket,
    SecurityConfig,
    WebSocketClient,
    WebSocketEndpoint,
    create_websocket_app,
    on_binary,
    on_connect,
    on_disconnect,
    on_json,
    on_text,
    websocket_client,
)

logger = logging.getLogger(__name__)


# Example 1: Real-time Chat Application
class ChatRoomEndpoint(WebSocketEndpoint):
    """
    Advanced chat room with multiple features:
    - Multiple rooms
    - User authentication
    - Message history
    - Typing indicators
    - User presence
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message_history: Dict[str, List[Dict]] = {}
        self.typing_users: Dict[str, set] = {}
        self.user_names: Dict[str, str] = {}

    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()

        # Send welcome message
        await connection.send_json(
            {
                "type": "welcome",
                "message": "Welcome to the chat! Please authenticate.",
                "timestamp": time.time(),
            }
        )

    @on_json
    async def handle_json(self, connection, message):
        data = message.data
        msg_type = data.get("type")

        if msg_type == "auth":
            await self._handle_auth(connection, data)
        elif msg_type == "join_room":
            await self._handle_join_room(connection, data)
        elif msg_type == "leave_room":
            await self._handle_leave_room(connection, data)
        elif msg_type == "chat_message":
            await self._handle_chat_message(connection, data)
        elif msg_type == "typing_start":
            await self._handle_typing_start(connection, data)
        elif msg_type == "typing_stop":
            await self._handle_typing_stop(connection, data)
        elif msg_type == "get_history":
            await self._handle_get_history(connection, data)
        elif msg_type == "get_users":
            await self._handle_get_users(connection, data)

    async def _handle_auth(self, connection, data):
        """Handle user authentication."""
        username = data.get("username", "").strip()

        if not username:
            await connection.send_json({"type": "auth_error", "message": "Username is required"})
            return

        # Store user info
        connection.info.user_id = username
        self.user_names[connection.id] = username

        await connection.send_json(
            {"type": "auth_success", "username": username, "user_id": connection.id}
        )

    async def _handle_join_room(self, connection, data):
        """Handle joining a room."""
        if not connection.info.user_id:
            await connection.send_json({"type": "error", "message": "Please authenticate first"})
            return

        room = data.get("room", "general")

        # Leave current rooms
        for current_room in list(connection.info.rooms):
            await self.connection_manager.leave_room(connection.id, current_room)
            await self._notify_room_leave(current_room, connection)

        # Join new room
        await self.connection_manager.join_room(connection.id, room)

        # Initialize room history if needed
        if room not in self.message_history:
            self.message_history[room] = []

        if room not in self.typing_users:
            self.typing_users[room] = set()

        # Notify room
        await self._notify_room_join(room, connection)

        # Send join confirmation
        await connection.send_json(
            {
                "type": "room_joined",
                "room": room,
                "user_count": len(self.connection_manager.get_room_connections(room)),
            }
        )

        # Send recent message history
        recent_messages = self.message_history[room][-50:]  # Last 50 messages
        await connection.send_json(
            {"type": "message_history", "room": room, "messages": recent_messages}
        )

    async def _handle_leave_room(self, connection, data):
        """Handle leaving a room."""
        room = data.get("room")
        if room and room in connection.info.rooms:
            await self.connection_manager.leave_room(connection.id, room)
            await self._notify_room_leave(room, connection)

    async def _handle_chat_message(self, connection, data):
        """Handle chat message."""
        if not connection.info.user_id:
            return

        room = data.get("room", "general")
        message_text = data.get("message", "").strip()

        if not message_text or room not in connection.info.rooms:
            return

        # Create message
        chat_message = {
            "type": "chat_message",
            "room": room,
            "user_id": connection.info.user_id,
            "username": self.user_names.get(connection.id, connection.info.user_id),
            "message": message_text,
            "timestamp": time.time(),
            "message_id": f"{connection.id}_{time.time()}",
        }

        # Store in history
        self.message_history[room].append(chat_message)

        # Keep only last 1000 messages per room
        if len(self.message_history[room]) > 1000:
            self.message_history[room] = self.message_history[room][-1000:]

        # Broadcast to room
        await self.broadcast_to_room(room, chat_message)

    async def _handle_typing_start(self, connection, data):
        """Handle typing start indicator."""
        if not connection.info.user_id:
            return

        room = data.get("room", "general")
        if room in connection.info.rooms:
            self.typing_users[room].add(connection.info.user_id)

            await self.broadcast_to_room(
                room,
                {
                    "type": "typing_start",
                    "room": room,
                    "user_id": connection.info.user_id,
                    "username": self.user_names.get(connection.id, connection.info.user_id),
                },
            )

    async def _handle_typing_stop(self, connection, data):
        """Handle typing stop indicator."""
        if not connection.info.user_id:
            return

        room = data.get("room", "general")
        if room in connection.info.rooms:
            self.typing_users[room].discard(connection.info.user_id)

            await self.broadcast_to_room(
                room,
                {
                    "type": "typing_stop",
                    "room": room,
                    "user_id": connection.info.user_id,
                    "username": self.user_names.get(connection.id, connection.info.user_id),
                },
            )

    async def _handle_get_history(self, connection, data):
        """Send message history."""
        room = data.get("room", "general")
        limit = min(data.get("limit", 50), 100)  # Max 100 messages

        if room in self.message_history:
            messages = self.message_history[room][-limit:]
            await connection.send_json(
                {"type": "message_history", "room": room, "messages": messages}
            )

    async def _handle_get_users(self, connection, data):
        """Send list of users in room."""
        room = data.get("room", "general")

        if room in connection.info.rooms:
            room_connections = self.connection_manager.get_room_connections(room)
            users = []

            for conn in room_connections:
                if conn.info.user_id:
                    users.append(
                        {
                            "user_id": conn.info.user_id,
                            "username": self.user_names.get(conn.id, conn.info.user_id),
                            "connected_at": conn.info.connected_at,
                        }
                    )

            await connection.send_json({"type": "room_users", "room": room, "users": users})

    async def _notify_room_join(self, room, connection):
        """Notify room about user joining."""
        await self.broadcast_to_room(
            room,
            {
                "type": "user_joined",
                "room": room,
                "user_id": connection.info.user_id,
                "username": self.user_names.get(connection.id, connection.info.user_id),
                "timestamp": time.time(),
            },
        )

    async def _notify_room_leave(self, room, connection):
        """Notify room about user leaving."""
        await self.broadcast_to_room(
            room,
            {
                "type": "user_left",
                "room": room,
                "user_id": connection.info.user_id,
                "username": self.user_names.get(connection.id, connection.info.user_id),
                "timestamp": time.time(),
            },
        )

    @on_disconnect
    async def handle_disconnect(self, connection):
        """Handle user disconnect."""
        if connection.info.user_id:
            # Notify all rooms
            for room in connection.info.rooms:
                await self._notify_room_leave(room, connection)
                # Remove from typing users
                if room in self.typing_users:
                    self.typing_users[room].discard(connection.info.user_id)

            # Clean up user data
            self.user_names.pop(connection.id, None)


# Example 2: Real-time Data Streaming
class DataStreamEndpoint(WebSocketEndpoint):
    """
    Real-time data streaming endpoint for live updates:
    - Stock prices
    - System metrics
    - Sensor data
    - Live statistics
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subscriptions: Dict[str, set] = {}
        self.stream_tasks: Dict[str, asyncio.Task] = {}

    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()

        await connection.send_json(
            {
                "type": "connected",
                "available_streams": ["stock_prices", "system_metrics", "sensor_data"],
                "message": "Send subscribe message to start receiving data",
            }
        )

    @on_json
    async def handle_json(self, connection, message):
        data = message.data
        msg_type = data.get("type")

        if msg_type == "subscribe":
            await self._handle_subscribe(connection, data)
        elif msg_type == "unsubscribe":
            await self._handle_unsubscribe(connection, data)
        elif msg_type == "get_streams":
            await self._handle_get_streams(connection)

    async def _handle_subscribe(self, connection, data):
        """Handle stream subscription."""
        stream_name = data.get("stream")

        if not stream_name:
            await connection.send_json({"type": "error", "message": "Stream name is required"})
            return

        # Initialize subscription set
        if stream_name not in self.subscriptions:
            self.subscriptions[stream_name] = set()

        # Add connection to subscription
        self.subscriptions[stream_name].add(connection.id)
        connection.info.metadata[f"subscribed_{stream_name}"] = True

        # Start stream if first subscriber
        if len(self.subscriptions[stream_name]) == 1:
            await self._start_stream(stream_name)

        await connection.send_json(
            {
                "type": "subscribed",
                "stream": stream_name,
                "message": f"Subscribed to {stream_name} stream",
            }
        )

    async def _handle_unsubscribe(self, connection, data):
        """Handle stream unsubscription."""
        stream_name = data.get("stream")

        if stream_name and stream_name in self.subscriptions:
            self.subscriptions[stream_name].discard(connection.id)
            connection.info.metadata.pop(f"subscribed_{stream_name}", None)

            # Stop stream if no subscribers
            if not self.subscriptions[stream_name]:
                await self._stop_stream(stream_name)

            await connection.send_json({"type": "unsubscribed", "stream": stream_name})

    async def _handle_get_streams(self, connection):
        """Send available streams."""
        await connection.send_json(
            {
                "type": "available_streams",
                "streams": ["stock_prices", "system_metrics", "sensor_data"],
            }
        )

    async def _start_stream(self, stream_name):
        """Start data stream."""
        if stream_name in self.stream_tasks:
            return

        if stream_name == "stock_prices":
            self.stream_tasks[stream_name] = asyncio.create_task(self._stock_price_stream())
        elif stream_name == "system_metrics":
            self.stream_tasks[stream_name] = asyncio.create_task(self._system_metrics_stream())
        elif stream_name == "sensor_data":
            self.stream_tasks[stream_name] = asyncio.create_task(self._sensor_data_stream())

    async def _stop_stream(self, stream_name):
        """Stop data stream."""
        task = self.stream_tasks.pop(stream_name, None)
        if task:
            task.cancel()

    async def _stock_price_stream(self):
        """Simulate stock price data stream."""
        import random

        stocks = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
        prices = {stock: random.uniform(100, 1000) for stock in stocks}

        try:
            while True:
                # Update prices
                for stock in stocks:
                    change = random.uniform(-5, 5)
                    prices[stock] = max(0.01, prices[stock] + change)

                # Send update
                await self._broadcast_to_stream(
                    "stock_prices",
                    {
                        "type": "stock_update",
                        "data": {"timestamp": time.time(), "prices": prices.copy()},
                    },
                )

                await asyncio.sleep(1)  # Update every second

        except asyncio.CancelledError:
            # TODO: Add proper exception handling

            pass

    async def _system_metrics_stream(self):
        """Simulate system metrics stream."""
        import random

        try:
            while True:
                metrics = {
                    "cpu_usage": random.uniform(0, 100),
                    "memory_usage": random.uniform(0, 100),
                    "disk_usage": random.uniform(0, 100),
                    "network_in": random.uniform(0, 1000),
                    "network_out": random.uniform(0, 1000),
                    "timestamp": time.time(),
                }

                await self._broadcast_to_stream(
                    "system_metrics", {"type": "metrics_update", "data": metrics}
                )

                await asyncio.sleep(2)  # Update every 2 seconds

        except asyncio.CancelledError:
            # TODO: Add proper exception handling

            pass

    async def _sensor_data_stream(self):
        """Simulate sensor data stream."""
        import math
        import random

        try:
            while True:
                sensors = []
                for i in range(5):
                    sensors.append(
                        {
                            "sensor_id": f"sensor_{i+1}",
                            "temperature": 20
                            + 10 * math.sin(time.time() / 10)
                            + random.uniform(-2, 2),
                            "humidity": 50
                            + 20 * math.cos(time.time() / 15)
                            + random.uniform(-5, 5),
                            "pressure": 1013 + random.uniform(-10, 10),
                        }
                    )

                await self._broadcast_to_stream(
                    "sensor_data",
                    {
                        "type": "sensor_update",
                        "data": {"timestamp": time.time(), "sensors": sensors},
                    },
                )

                await asyncio.sleep(0.5)  # Update every 500ms

        except asyncio.CancelledError:
            # TODO: Add proper exception handling

            pass

    async def _broadcast_to_stream(self, stream_name, data):
        """Broadcast data to stream subscribers."""
        if stream_name not in self.subscriptions:
            return

        subscriber_ids = list(self.subscriptions[stream_name])

        for connection_id in subscriber_ids:
            connection = self.connection_manager.get_connection(connection_id)
            if connection:
                try:
                    await connection.send_json(data)
                except Exception as e:
                    logger.warning(f"Failed to send to {connection_id}: {e}")
                    self.subscriptions[stream_name].discard(connection_id)

    @on_disconnect
    async def handle_disconnect(self, connection):
        """Handle disconnect - clean up subscriptions."""
        # Remove from all subscriptions
        for stream_name, subscribers in self.subscriptions.items():
            subscribers.discard(connection.id)

            # Stop stream if no subscribers
            if not subscribers:
                await self._stop_stream(stream_name)


# Example 3: Multiplayer Game Server
class GameServerEndpoint(WebSocketEndpoint):
    """
    Simple multiplayer game server:
    - Player positioning
    - Game state synchronization
    - Real-time updates
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_state = {"players": {}, "game_started": False, "game_id": "game_1"}
        self.update_task = None

    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()

        # Join game room
        await self.connection_manager.join_room(connection.id, "game_room")

        await connection.send_json(
            {
                "type": "connected",
                "game_id": self.game_state["game_id"],
                "message": "Connected to game server",
            }
        )

    @on_json
    async def handle_json(self, connection, message):
        data = message.data
        msg_type = data.get("type")

        if msg_type == "join_game":
            await self._handle_join_game(connection, data)
        elif msg_type == "player_move":
            await self._handle_player_move(connection, data)
        elif msg_type == "player_action":
            await self._handle_player_action(connection, data)
        elif msg_type == "get_game_state":
            await self._handle_get_game_state(connection)

    async def _handle_join_game(self, connection, data):
        """Handle player joining the game."""
        player_name = data.get("player_name", f"Player_{connection.id[:8]}")

        # Add player to game state
        self.game_state["players"][connection.id] = {
            "name": player_name,
            "x": 0,
            "y": 0,
            "score": 0,
            "health": 100,
            "joined_at": time.time(),
        }

        connection.info.user_id = player_name

        # Notify other players
        await self.broadcast_to_room(
            "game_room",
            {
                "type": "player_joined",
                "player_id": connection.id,
                "player_name": player_name,
                "game_state": self.game_state,
            },
        )

        # Send initial state to new player
        await connection.send_json(
            {
                "type": "game_joined",
                "player_id": connection.id,
                "game_state": self.game_state,
            }
        )

        # Start game loop if first player
        if len(self.game_state["players"]) == 1 and not self.update_task:
            self.update_task = asyncio.create_task(self._game_update_loop())

    async def _handle_player_move(self, connection, data):
        """Handle player movement."""
        if connection.id not in self.game_state["players"]:
            return

        x = data.get("x", 0)
        y = data.get("y", 0)

        # Update player position
        self.game_state["players"][connection.id]["x"] = x
        self.game_state["players"][connection.id]["y"] = y

        # Broadcast movement to other players
        await self.broadcast_to_room(
            "game_room",
            {"type": "player_moved", "player_id": connection.id, "x": x, "y": y},
        )

    async def _handle_player_action(self, connection, data):
        """Handle player action."""
        if connection.id not in self.game_state["players"]:
            return

        action = data.get("action")

        if action == "shoot":
            # Handle shooting action
            await self.broadcast_to_room(
                "game_room",
                {
                    "type": "player_action",
                    "player_id": connection.id,
                    "action": "shoot",
                    "timestamp": time.time(),
                },
            )

    async def _handle_get_game_state(self, connection):
        """Send current game state."""
        await connection.send_json({"type": "game_state", "data": self.game_state})

    async def _game_update_loop(self):
        """Game update loop - runs at 30 FPS."""
        try:
            while self.game_state["players"]:
                # Game logic here (AI, physics, etc.)

                # Send periodic state updates
                await self.broadcast_to_room(
                    "game_room",
                    {
                        "type": "game_update",
                        "timestamp": time.time(),
                        "players": self.game_state["players"],
                    },
                )

                await asyncio.sleep(1 / 30)  # 30 FPS

        except asyncio.CancelledError:
            # TODO: Add proper exception handling

            pass

    @on_disconnect
    async def handle_disconnect(self, connection):
        """Handle player disconnect."""
        if connection.id in self.game_state["players"]:
            player_name = self.game_state["players"][connection.id]["name"]
            del self.game_state["players"][connection.id]

            # Notify other players
            await self.broadcast_to_room(
                "game_room",
                {
                    "type": "player_left",
                    "player_id": connection.id,
                    "player_name": player_name,
                },
            )

            # Stop game loop if no players
            if not self.game_state["players"] and self.update_task:
                self.update_task.cancel()
                self.update_task = None


# Example 4: Notification System
class NotificationEndpoint(WebSocketEndpoint):
    """
    Real-time notification system:
    - User-specific notifications
    - Broadcast notifications
    - Notification history
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_history: Dict[str, List[Dict]] = {}

    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()

        await connection.send_json(
            {"type": "connected", "message": "Connected to notification service"}
        )

    @on_json
    async def handle_json(self, connection, message):
        data = message.data
        msg_type = data.get("type")

        if msg_type == "register_user":
            await self._handle_register_user(connection, data)
        elif msg_type == "send_notification":
            await self._handle_send_notification(connection, data)
        elif msg_type == "get_history":
            await self._handle_get_history(connection, data)
        elif msg_type == "mark_read":
            await self._handle_mark_read(connection, data)

    async def _handle_register_user(self, connection, data):
        """Register user for notifications."""
        user_id = data.get("user_id")

        if not user_id:
            await connection.send_json({"type": "error", "message": "User ID is required"})
            return

        connection.info.user_id = user_id

        # Initialize history if needed
        if user_id not in self.notification_history:
            self.notification_history[user_id] = []

        await connection.send_json(
            {
                "type": "registered",
                "user_id": user_id,
                "message": "Registered for notifications",
            }
        )

    async def _handle_send_notification(self, connection, data):
        """Send notification to user(s)."""
        target_user = data.get("target_user")
        notification = {
            "id": f"notif_{int(time.time())}_{connection.id}",
            "title": data.get("title", "Notification"),
            "message": data.get("message", ""),
            "sender": connection.info.user_id,
            "timestamp": time.time(),
            "read": False,
            "type": data.get("notification_type", "info"),
        }

        if target_user:
            # Send to specific user
            await self._send_to_user(target_user, notification)
        else:
            # Broadcast to all users
            await self._broadcast_notification(notification)

    async def _send_to_user(self, user_id: str, notification: Dict):
        """Send notification to specific user."""
        # Add to history
        if user_id not in self.notification_history:
            self.notification_history[user_id] = []

        self.notification_history[user_id].append(notification)

        # Keep only last 100 notifications
        if len(self.notification_history[user_id]) > 100:
            self.notification_history[user_id] = self.notification_history[user_id][-100:]

        # Send to user connections
        user_connections = self.connection_manager.get_user_connections(user_id)
        for connection in user_connections:
            try:
                await connection.send_json({"type": "notification", "data": notification})
            except Exception as e:
                logger.warning(f"Failed to send notification to {user_id}: {e}")

    async def _broadcast_notification(self, notification: Dict):
        """Broadcast notification to all users."""
        # Add to all user histories
        for user_id in self.notification_history:
            self.notification_history[user_id].append(notification.copy())

        # Broadcast to all connections
        await self.broadcast_to_all({"type": "notification", "data": notification})

    async def _handle_get_history(self, connection, data):
        """Get notification history."""
        user_id = connection.info.user_id

        if not user_id:
            await connection.send_json({"type": "error", "message": "Not registered"})
            return

        limit = min(data.get("limit", 20), 50)
        notifications = self.notification_history.get(user_id, [])[-limit:]

        await connection.send_json({"type": "notification_history", "notifications": notifications})

    async def _handle_mark_read(self, connection, data):
        """Mark notification as read."""
        user_id = connection.info.user_id
        notification_id = data.get("notification_id")

        if not user_id or not notification_id:
            return

        # Find and mark notification as read
        for notification in self.notification_history.get(user_id, []):
            if notification.get("id") == notification_id:
                notification["read"] = True
                break


# Example application setups
def create_chat_app(port: int = 8000):
    """Create a complete chat application."""
    app = create_websocket_app(debug=True)
    app.add_route("/ws/chat", ChatRoomEndpoint())
    return app


def create_data_streaming_app(port: int = 8001):
    """Create a data streaming application."""
    app = create_websocket_app(debug=True)
    app.add_route("/ws/stream", DataStreamEndpoint())
    return app


def create_game_server_app(port: int = 8002):
    """Create a game server application."""
    app = create_websocket_app(debug=True)
    app.add_route("/ws/game", GameServerEndpoint())
    return app


def create_notification_app(port: int = 8003):
    """Create a notification service application."""
    app = create_websocket_app(debug=True)
    app.add_route("/ws/notifications", NotificationEndpoint())
    return app


# Client examples
async def chat_client_example():
    """Example chat client."""
    config = ClientConfig(auto_reconnect=True)

    async with websocket_client("ws://localhost:8000/ws/chat", config) as client:
        # Authenticate
        await client.send_json({"type": "auth", "username": "example_user"})

        # Join room
        await client.send_json({"type": "join_room", "room": "general"})

        # Send message
        await client.send_json(
            {
                "type": "chat_message",
                "room": "general",
                "message": "Hello from Python client!",
            }
        )

        # Listen for messages
        while client.is_connected():
            try:
                message = await client.receive(timeout=5.0)
                if message:
                    logger.info("Received: {message.data}")
            except Exception as e:
                logger.error("Error: {e}")
                break


async def data_stream_client_example():
    """Example data streaming client."""
    config = ClientConfig(auto_reconnect=True)

    async with websocket_client("ws://localhost:8001/ws/stream", config) as client:
        # Subscribe to stock prices
        await client.send_json({"type": "subscribe", "stream": "stock_prices"})

        # Listen for updates
        for _ in range(10):  # Listen for 10 updates
            try:
                message = await client.receive(timeout=5.0)
                if message and message.data.get("type") == "stock_update":
                    prices = message.data["data"]["prices"]
                    logger.info("Stock prices: {prices}")
            except Exception as e:
                logger.error("Error: {e}")
                break


# Performance test client
async def websocket_load_test(url: str, num_clients: int = 100, duration: int = 60):
    """Load test WebSocket server."""
    clients = []
    stats = {"connected": 0, "messages_sent": 0, "messages_received": 0, "errors": 0}

    async def client_worker(client_id: int):
        try:
            config = ClientConfig(auto_reconnect=False)
            async with websocket_client(url, config) as client:
                stats["connected"] += 1

                # Send test messages
                start_time = time.time()
                while time.time() - start_time < duration:
                    try:
                        await client.send_json(
                            {
                                "type": "test_message",
                                "client_id": client_id,
                                "timestamp": time.time(),
                            }
                        )
                        stats["messages_sent"] += 1

                        # Try to receive
                        message = await client.receive(timeout=0.1)
                        if message:
                            stats["messages_received"] += 1

                        await asyncio.sleep(1.0)  # Send every second

                    except Exception as e:
                        stats["errors"] += 1
                        logger.debug(f"Client {client_id} error: {e}")

        except Exception as e:
            stats["errors"] += 1
            logger.error(f"Client {client_id} failed: {e}")

    # Start all clients
    tasks = [client_worker(i) for i in range(num_clients)]
    await asyncio.gather(*tasks, return_exceptions=True)

    return stats


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "chat":
            import uvicorn

            app = create_chat_app()
            uvicorn.run(
                app.asgi_app, host="0.0.0.0", port=8000
            )  # nosec B104 - binding to all interfaces is intentional for framework

        elif sys.argv[1] == "stream":
            import uvicorn

            app = create_data_streaming_app()
            uvicorn.run(
                app.asgi_app, host="0.0.0.0", port=8001
            )  # nosec B104 - binding to all interfaces is intentional for framework

        elif sys.argv[1] == "game":
            import uvicorn

            app = create_game_server_app()
            uvicorn.run(
                app.asgi_app, host="0.0.0.0", port=8002
            )  # nosec B104 - binding to all interfaces is intentional for framework

        elif sys.argv[1] == "notifications":
            import uvicorn

            app = create_notification_app()
            uvicorn.run(
                app.asgi_app, host="0.0.0.0", port=8003
            )  # nosec B104 - binding to all interfaces is intentional for framework

    else:
        logger.info("Usage: python examples.py [chat|stream|game|notifications]")
