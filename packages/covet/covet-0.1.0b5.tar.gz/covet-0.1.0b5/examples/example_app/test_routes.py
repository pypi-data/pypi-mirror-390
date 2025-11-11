"""
Test REST API routing
"""
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

try:
    from covet.core import CovetApplication, CovetRouter
    from covet.api.rest import RESTFramework
    print("✅ Routing imports successful")
except ImportError as e:
    print(f"❌ Routing import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 1: Core Router
try:
    app = CovetApplication()
    router = CovetRouter()
    print("✅ App and Core Router created")

    # Define routes using router
    @router.route('/users', methods=['GET'])
    async def list_users(request):
        return {'users': [{'id': 1, 'username': 'test'}]}

    print("✅ Core routes defined successfully")
except Exception as e:
    print(f"⚠️ Core router failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: REST Framework
try:
    api = RESTFramework(title="Test API", version="1.0.0")
    print("✅ REST Framework created")

    # Define REST routes
    @api.get('/users')
    async def list_users_rest():
        return {'users': [{'id': 1, 'username': 'test'}]}

    @api.post('/users')
    async def create_user_rest():
        return {'message': 'User created', 'id': 1}

    print("✅ REST routes defined successfully")

except Exception as e:
    print(f"❌ Routing setup failed: {e}")
    import traceback
    traceback.print_exc()
