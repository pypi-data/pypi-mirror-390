"""
Complete integrated application - The reality test
"""
import sys
import asyncio
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

async def build_complete_app():
    print("=" * 60)
    print("BUILDING COMPLETE BLOG API WITH COVETPY")
    print("=" * 60)

    # Step 1: Create Application
    try:
        from covet.core import CovetApplication
        app = CovetApplication()
        print("✅ Step 1: Application created")
    except Exception as e:
        print(f"❌ Step 1 FAILED: {e}")
        return False

    # Step 2: Setup Database
    try:
        from covet.database import SQLiteAdapter, DatabaseManager
        adapter = SQLiteAdapter('blog.db')
        db = DatabaseManager(adapter)
        await db.connect()
        print("✅ Step 2: Database connected")
    except Exception as e:
        print(f"❌ Step 2 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 3: Define Models
    try:
        from covet.database.orm import Model, CharField, TextField

        class User(Model):
            username = CharField(max_length=50)
            email = CharField(max_length=100)

            class Meta:
                table_name = "users"

        print("✅ Step 3: Models defined")
    except Exception as e:
        print(f"❌ Step 3 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 4: Create API Routes
    try:
        from covet.api.rest import RESTFramework

        api = RESTFramework(title="Blog API", version="1.0.0")

        @api.get('/api/users')
        async def list_users():
            return {'users': [], 'count': 0}

        @api.post('/api/users')
        async def create_user():
            return {'message': 'User created', 'id': 1}

        print("✅ Step 4: API routes created")
    except Exception as e:
        print(f"❌ Step 4 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 5: Add Authentication
    try:
        from covet.security.jwt_auth import JWTAuthenticator, JWTConfig, JWTAlgorithm, TokenType

        config = JWTConfig(
            secret_key="test_secret_key_32_chars_min_length_required!",
            algorithm=JWTAlgorithm.HS256
        )
        auth = JWTAuthenticator(config)
        token = auth.create_token(subject="user123", token_type=TokenType.ACCESS)
        print(f"✅ Step 5: Authentication working (token: {token[:30]}...)")
    except Exception as e:
        print(f"❌ Step 5 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Step 6: Add WebSocket
    try:
        from covet.websocket import CovetWebSocket, WebSocketEndpoint

        ws = CovetWebSocket()

        class ChatEndpoint(WebSocketEndpoint):
            async def on_receive(self, websocket, message):
                await websocket.send_text(f"Echo: {message}")

        print("✅ Step 6: WebSocket endpoint defined")
    except Exception as e:
        print(f"❌ Step 6 FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)
    print("✅ ALL STEPS COMPLETED - FRAMEWORK WORKS!")
    print("=" * 60)

    await db.disconnect()
    return True

if __name__ == "__main__":
    result = asyncio.run(build_complete_app())
    sys.exit(0 if result else 1)
