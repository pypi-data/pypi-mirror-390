"""
Test WebSocket functionality
"""
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

try:
    from covet.websocket import CovetWebSocket, WebSocketEndpoint, WebSocketConnection
    print("✅ WebSocket imports successful")
except ImportError as e:
    print(f"❌ WebSocket import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1: CovetWebSocket
try:
    ws = CovetWebSocket()
    print("✅ CovetWebSocket instance created")

    # Define websocket route using decorator
    @ws.websocket('/notifications')
    async def notification_handler(websocket):
        await websocket.accept()
        await websocket.send_text("Connected!")
        await websocket.close()

    print("✅ WebSocket route with decorator defined successfully")
except Exception as e:
    print(f"⚠️ CovetWebSocket failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: WebSocket Endpoint
try:
    class NotificationEndpoint(WebSocketEndpoint):
        async def on_connect(self, websocket):
            await websocket.accept()
            print(f"✅ WebSocket connection: {websocket}")

        async def on_receive(self, websocket, message):
            print(f"✅ WebSocket message received: {message}")

        async def on_disconnect(self, websocket, close_code):
            print(f"✅ WebSocket disconnected: {close_code}")

    print("✅ WebSocket endpoint class defined successfully")

except Exception as e:
    print(f"❌ WebSocket setup failed: {e}")
    import traceback
    traceback.print_exc()
