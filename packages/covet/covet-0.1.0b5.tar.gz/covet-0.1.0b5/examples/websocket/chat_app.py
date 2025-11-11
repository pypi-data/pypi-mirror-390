"""
Real-Time Chat Application using CovetPy WebSocket

This example demonstrates:
- Multiple chat rooms
- User authentication with JWT
- Real-time message broadcasting
- Room management (join/leave)
- User presence tracking
- Message history
- Typing indicators
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Set

from covet import CovetPy
from covet.websocket.connection_manager import ProductionConnectionManager
from covet.websocket.room_manager import RoomManager, RoomType, RoomPermission
from covet.websocket.message_router import MessageRouter, RoutedMessage
from covet.websocket.auth import WebSocketAuthenticator, AuthConfig, AuthStrategy
from covet.websocket.connection import WebSocketConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create app
app = CovetPy(debug=True)

# Initialize WebSocket components
connection_manager = ProductionConnectionManager(
    max_connections=10000,
    max_connections_per_ip=50,
)

room_manager = RoomManager(connection_manager)
message_router = MessageRouter()

auth_config = AuthConfig(
    strategy=AuthStrategy.JWT_QUERY,
    jwt_secret="your-secret-key-change-in-production",
    required=True,
)
authenticator = WebSocketAuthenticator(auth_config)

# Track typing users
typing_users: Dict[str, Set[str]] = {}  # room_name -> set of user_ids


# Message handlers
@message_router.on("join_room")
async def handle_join_room(connection: WebSocketConnection, message: RoutedMessage):
    """Handle user joining a room."""
    room_name = message.data.get("room")
    if not room_name:
        await connection.send_json({
            "error": "room name required",
        })
        return

    # Join room
    success = await room_manager.join_room(
        connection_id=connection.id,
        room_name=room_name,
        user_id=connection.info.user_id,
        auto_create=True,
    )

    if success:
        # Send confirmation
        await connection.send_json({
            "type": "room_joined",
            "room": room_name,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # Broadcast to room
        await room_manager.broadcast_to_room(
            room_name,
            {
                "type": "user_joined",
                "user_id": connection.info.user_id,
                "username": connection.info.metadata.get("username"),
                "room": room_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Send room info (members, history, etc.)
        room = room_manager.get_room(room_name)
        if room:
            members = [
                {
                    "user_id": member.user_id,
                    "joined_at": member.joined_at,
                }
                for member in room.get_all_members()
            ]

            await connection.send_json({
                "type": "room_info",
                "room": room_name,
                "members": members,
                "member_count": len(members),
            })

        logger.info(f"User {connection.info.user_id} joined room {room_name}")
    else:
        await connection.send_json({
            "error": "Failed to join room",
            "room": room_name,
        })


@message_router.on("leave_room")
async def handle_leave_room(connection: WebSocketConnection, message: RoutedMessage):
    """Handle user leaving a room."""
    room_name = message.data.get("room")
    if not room_name:
        return

    # Leave room
    success = await room_manager.leave_room(connection.id, room_name)

    if success:
        # Broadcast to room
        await room_manager.broadcast_to_room(
            room_name,
            {
                "type": "user_left",
                "user_id": connection.info.user_id,
                "username": connection.info.metadata.get("username"),
                "room": room_name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        await connection.send_json({
            "type": "room_left",
            "room": room_name,
        })

        logger.info(f"User {connection.info.user_id} left room {room_name}")


@message_router.on("chat_message")
async def handle_chat_message(connection: WebSocketConnection, message: RoutedMessage):
    """Handle chat message."""
    room_name = message.data.get("room")
    text = message.data.get("message")

    if not room_name or not text:
        await connection.send_json({
            "error": "room and message required",
        })
        return

    # Check if user is in room
    room = room_manager.get_room(room_name)
    if not room or not room.has_member(connection.id):
        await connection.send_json({
            "error": "Not in room",
            "room": room_name,
        })
        return

    # Check if user can send
    can_send, reason = room.can_send_message(connection.id)
    if not can_send:
        await connection.send_json({
            "error": reason,
            "room": room_name,
        })
        return

    # Broadcast message
    await room_manager.broadcast_to_room(
        room_name,
        {
            "type": "chat_message",
            "message_id": message.message_id,
            "user_id": connection.info.user_id,
            "username": connection.info.metadata.get("username"),
            "message": text,
            "room": room_name,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )

    logger.info(f"Chat message from {connection.info.user_id} in {room_name}")


@message_router.on("typing")
async def handle_typing(connection: WebSocketConnection, message: RoutedMessage):
    """Handle typing indicator."""
    room_name = message.data.get("room")
    is_typing = message.data.get("typing", False)

    if not room_name:
        return

    # Update typing status
    if room_name not in typing_users:
        typing_users[room_name] = set()

    if is_typing:
        typing_users[room_name].add(connection.info.user_id)
    else:
        typing_users[room_name].discard(connection.info.user_id)

    # Broadcast typing status
    await room_manager.broadcast_to_room(
        room_name,
        {
            "type": "typing",
            "user_id": connection.info.user_id,
            "username": connection.info.metadata.get("username"),
            "typing": is_typing,
            "room": room_name,
        },
    )


@message_router.on("get_rooms")
async def handle_get_rooms(connection: WebSocketConnection, message: RoutedMessage):
    """Get list of available rooms."""
    rooms = room_manager.get_public_rooms()

    room_list = [
        {
            "name": room.name,
            "type": room.room_type.value,
            "member_count": room.metrics.current_members,
        }
        for room in rooms
    ]

    await connection.send_json({
        "type": "room_list",
        "rooms": room_list,
    })


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket):
    """WebSocket endpoint for chat."""
    # Get ASGI scope
    scope = websocket.scope

    # Add connection
    connection = await connection_manager.add_connection(
        websocket=websocket,
        ip_address=scope.get("client", ["unknown"])[0] if scope.get("client") else "unknown",
        user_agent=dict(scope.get("headers", {})).get(b"user-agent", b"").decode(),
    )

    # Authenticate
    user = await authenticator.authenticate_connection(connection, scope)
    if not user:
        logger.warning(f"Authentication failed for connection {connection.id}")
        return

    try:
        # Accept connection
        await connection.accept()

        # Send welcome message
        await connection.send_json({
            "type": "welcome",
            "user_id": user.user_id,
            "username": user.username,
            "message": "Connected to chat server",
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info(f"User {user.user_id} connected")

        # Message loop
        while connection.is_connected:
            try:
                # Receive message
                raw_message = await asyncio.wait_for(
                    connection.receive(),
                    timeout=60.0
                )

                if raw_message:
                    # Route message
                    await message_router.route_message(connection, raw_message)

            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                await connection.ping()
                continue
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                break

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Leave all rooms
        await room_manager.leave_all_rooms(connection.id)

        # Close connection
        await connection_manager.close_connection(connection.id)

        logger.info(f"User {user.user_id} disconnected")


# HTTP endpoint for generating JWT tokens (for demo)
@app.post("/auth/token")
async def generate_token(request):
    """Generate JWT token for authentication."""
    body = await request.json()
    username = body.get("username")
    user_id = body.get("user_id")

    if not username or not user_id:
        return {"error": "username and user_id required"}, 400

    # Generate token
    from covet.websocket.auth import JWTHandler
    import time

    jwt_handler = JWTHandler(auth_config.jwt_secret)
    token = jwt_handler.encode({
        "sub": user_id,
        "username": username,
        "iat": time.time(),
        "exp": time.time() + 3600,  # 1 hour
    })

    return {
        "token": token,
        "user_id": user_id,
        "username": username,
        "expires_in": 3600,
    }


# Health check endpoint
@app.get("/health")
async def health_check(request):
    """Health check endpoint."""
    stats = connection_manager.get_statistics()
    room_stats = room_manager.get_statistics()

    return {
        "status": "healthy",
        "connections": stats["current_connections"],
        "rooms": room_stats["total_rooms"],
        "timestamp": datetime.utcnow().isoformat(),
    }


# Main entry point
if __name__ == "__main__":
    print("=" * 60)
    print("CovetPy WebSocket Chat Application")
    print("=" * 60)
    print()
    print("Server starting on http://localhost:8000")
    print()
    print("Endpoints:")
    print("  WebSocket: ws://localhost:8000/ws?token=YOUR_JWT_TOKEN")
    print("  Auth:      POST http://localhost:8000/auth/token")
    print("  Health:    GET http://localhost:8000/health")
    print()
    print("=" * 60)
    print()

    app.run(host="0.0.0.0", port=8000)
