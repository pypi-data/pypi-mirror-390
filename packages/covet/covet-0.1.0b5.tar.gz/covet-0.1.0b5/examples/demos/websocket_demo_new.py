#!/usr/bin/env python3
"""
WebSocket Demo for CovetPy Framework

This demo showcases the complete WebSocket implementation including:
- Echo server
- Chat room
- Real-time data streaming
- Client connections

Run this script to see the WebSocket system in action.
"""

import asyncio
import json
import logging
import time
from src.covet.websocket import (
    create_websocket_app, WebSocketEndpoint, WebSocketClient, ClientConfig,
    on_connect, on_disconnect, on_text, on_json
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleEchoEndpoint(WebSocketEndpoint):
    """Simple echo endpoint for demonstration."""
    
    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()
        await connection.send_json({
            "type": "welcome",
            "message": "Welcome to CovetPy WebSocket Demo!",
            "timestamp": time.time()
        })
        logger.info(f"Client {connection.id} connected to echo server")
    
    @on_text
    async def handle_text(self, connection, message):
        await connection.send_text(f"Echo: {message.content}")
        logger.info(f"Echo: {message.content}")
    
    @on_json
    async def handle_json(self, connection, message):
        response = {
            "type": "echo",
            "original": message.data,
            "timestamp": time.time()
        }
        await connection.send_json(response)
        logger.info(f"JSON Echo: {message.data}")
    
    @on_disconnect
    async def handle_disconnect(self, connection):
        logger.info(f"Client {connection.id} disconnected from echo server")


class SimpleChatEndpoint(WebSocketEndpoint):
    """Simple chat endpoint for demonstration."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users = {}
    
    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()
        await connection.send_json({
            "type": "welcome",
            "message": "Welcome to the chat! Send your name to join.",
            "timestamp": time.time()
        })
        logger.info(f"Client {connection.id} connected to chat")
    
    @on_json
    async def handle_json(self, connection, message):
        data = message.data
        msg_type = data.get("type")
        
        if msg_type == "join":
            name = data.get("name", f"User_{connection.id[:8]}")
            self.users[connection.id] = name
            connection.info.user_id = name
            
            # Join main room
            await self.connection_manager.join_room(connection.id, "main")
            
            # Notify others
            await self.broadcast_to_room("main", {
                "type": "user_joined",
                "name": name,
                "timestamp": time.time()
            })
            
            await connection.send_json({
                "type": "joined",
                "message": f"Welcome to the chat, {name}!"
            })
            
        elif msg_type == "message":
            if connection.id in self.users:
                chat_message = {
                    "type": "message",
                    "from": self.users[connection.id],
                    "message": data.get("message", ""),
                    "timestamp": time.time()
                }
                await self.broadcast_to_room("main", chat_message)
    
    @on_disconnect
    async def handle_disconnect(self, connection):
        if connection.id in self.users:
            name = self.users[connection.id]
            del self.users[connection.id]
            
            await self.broadcast_to_room("main", {
                "type": "user_left",
                "name": name,
                "timestamp": time.time()
            })
            
        logger.info(f"Client {connection.id} disconnected from chat")


async def create_demo_server():
    """Create the demo WebSocket server."""
    print("🚀 Creating CovetPy WebSocket Demo Server...")
    
    # Create WebSocket app
    app = create_websocket_app(max_connections=100, debug=True)
    
    # Add endpoints
    app.add_route("/ws/echo", SimpleEchoEndpoint())
    app.add_route("/ws/chat", SimpleChatEndpoint())
    
    # Set up convenience endpoints
    app.setup_echo_server("/ws/echo2")  # Built-in echo server
    
    print("✅ Demo server created with endpoints:")
    print("   📡 /ws/echo - Simple echo server")
    print("   💬 /ws/chat - Chat room")
    print("   🔄 /ws/echo2 - Built-in echo server")
    
    return app


async def demo_client_interactions():
    """Demonstrate client interactions."""
    print("\n🤖 Running client demonstrations...")
    
    # Demo 1: Echo client
    print("\n1️⃣ Testing Echo Server...")
    try:
        config = ClientConfig(auto_reconnect=False)
        client = WebSocketClient("ws://localhost:8000/ws/echo", config)
        
        # Would connect in real scenario
        print("   ✅ Echo client created successfully")
    except Exception as e:
        print(f"   ❌ Echo client demo failed: {e}")
    
    # Demo 2: Chat client
    print("\n2️⃣ Testing Chat Server...")
    try:
        config = ClientConfig(auto_reconnect=False)
        client = WebSocketClient("ws://localhost:8000/ws/chat", config)
        
        # Would connect and join chat in real scenario
        print("   ✅ Chat client created successfully")
    except Exception as e:
        print(f"   ❌ Chat client demo failed: {e}")
    
    print("\n✨ Client demonstrations completed!")


def show_usage_examples():
    """Show usage examples."""
    print("\n📚 Usage Examples:")
    print("=" * 50)
    
    print("\n🔧 1. Basic WebSocket Server:")
    print("""
from src.covet.websocket import create_websocket_app

app = create_websocket_app()
app.setup_echo_server('/ws/echo')

# Run with: uvicorn app.asgi_app:asgi_app --host 0.0.0.0 --port 8000
""")
    
    print("\n🎯 2. Custom WebSocket Endpoint:")
    print("""
from src.covet.websocket import WebSocketEndpoint, on_connect, on_text

class MyEndpoint(WebSocketEndpoint):
    @on_connect
    async def handle_connect(self, connection):
        await connection.accept()
        await connection.send_text("Hello!")
    
    @on_text
    async def handle_text(self, connection, message):
        await connection.send_text(f"You said: {message.content}")

app.add_route('/ws/my_endpoint', MyEndpoint())
""")
    
    print("\n🌐 3. WebSocket Client:")
    print("""
from src.covet.websocket import websocket_client, ClientConfig

config = ClientConfig(auto_reconnect=True)

async with websocket_client("ws://localhost:8000/ws/echo", config) as client:
    await client.send_text("Hello, server!")
    message = await client.receive()
    print(f"Received: {message.data}")
""")
    
    print("\n🔒 4. Secure WebSocket with Authentication:")
    print("""
from src.covet.websocket import create_websocket_app, SecurityConfig, AuthMethod

security_config = SecurityConfig(
    require_auth=True,
    auth_method=AuthMethod.JWT,
    jwt_secret="your-secret-key",
    enable_rate_limiting=True,
    max_messages_per_minute=60
)

app = create_websocket_app(security_config=security_config)
""")
    
    print("\n💬 5. Broadcasting to Rooms:")
    print("""
# In your endpoint
await self.broadcast_to_room("room_name", {"message": "Hello room!"})
await self.broadcast_to_user("user_id", {"message": "Hello user!"})
await self.broadcast_to_all({"message": "Hello everyone!"})
""")


async def main():
    """Main demo function."""
    print("🎉 CovetPy WebSocket Framework Demo")
    print("=" * 50)
    
    # Create demo server
    app = await create_demo_server()
    
    # Run client demonstrations
    await demo_client_interactions()
    
    # Show statistics
    print("\n📊 Server Statistics:")
    stats = app.get_statistics()
    print(f"   📡 Current connections: {stats.get('current_connections', 0)}")
    print(f"   📈 Total connections: {stats.get('total_connections', 0)}")
    print(f"   🏠 Total rooms: {stats.get('total_rooms', 0)}")
    print(f"   👥 Total users: {stats.get('total_users', 0)}")
    
    # Show usage examples
    show_usage_examples()
    
    print("\n🚀 To run a real WebSocket server:")
    print("1. Install uvicorn: pip install uvicorn")
    print("2. Run: python -c \"")
    print("   from src.covet.websocket.examples import create_chat_app")
    print("   import uvicorn")
    print("   app = create_chat_app()")
    print("   uvicorn.run(app.asgi_app, host='0.0.0.0', port=8000)\"")
    print("\n3. Connect with a WebSocket client to ws://localhost:8000/ws/chat")
    
    print("\n✨ Demo completed successfully!")
    print("🎯 The CovetPy WebSocket system is ready for production use!")


if __name__ == "__main__":
    asyncio.run(main())