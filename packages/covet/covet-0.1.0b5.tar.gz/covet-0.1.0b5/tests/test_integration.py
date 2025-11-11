#!/usr/bin/env python3
"""
Integration test for HTTP objects with the server and router
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from covet.core.http_objects import (
    Request,
    Response,
    json_response,
    error_response,
    HTTPStatus,
)
from covet.core.routing import CovetRouter


class TestApp:
    """Test application using new HTTP objects with router"""
    
    def __init__(self):
        self.router = CovetRouter()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup test routes"""
        self.router.add_route('/', self.home, ['GET'])
        self.router.add_route('/api/users', self.get_users, ['GET'])
        self.router.add_route('/api/users', self.create_user, ['POST'])
        self.router.add_route('/api/users/{user_id}', self.get_user, ['GET'])
    
    async def home(self, request: Request) -> Response:
        """Home endpoint"""
        return Response(
            content="Welcome to CovetPy HTTP Objects!",
            headers={'X-Test': 'integration'}
        )
    
    async def get_users(self, request: Request) -> Response:
        """Get users with query parameters"""
        page = int(request.query_params.get('page', '1'))
        limit = int(request.query_params.get('limit', '10'))
        
        users = [
            {'id': i, 'name': f'User {i}'}
            for i in range((page - 1) * limit + 1, page * limit + 1)
        ]
        
        response = json_response({
            'users': users,
            'page': page,
            'limit': limit
        })
        
        response.set_cache_control(max_age=300)
        return response
    
    async def create_user(self, request: Request) -> Response:
        """Create user from JSON"""
        if not request.is_json():
            return error_response('JSON required', HTTPStatus.BAD_REQUEST)
        
        try:
            user_data = await request.json()
        except (json.JSONDecodeError, ValueError):
            return error_response('Invalid JSON', HTTPStatus.BAD_REQUEST)
        
        if 'name' not in user_data:
            return error_response('Name required', HTTPStatus.BAD_REQUEST)
        
        new_user = {
            'id': 123,
            'name': user_data['name'],
            'email': user_data.get('email', f"{user_data['name'].lower()}@example.com")
        }
        
        return json_response(new_user, HTTPStatus.CREATED)
    
    async def get_user(self, request: Request) -> Response:
        """Get user by ID"""
        user_id = request.path_params['user_id']
        
        user = {
            'id': int(user_id),
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com'
        }
        
        response = json_response(user)
        response.generate_etag()
        return response
    
    async def handle_request(self, method: str, path: str, **kwargs) -> Response:
        """Handle request using router"""
        # Create request
        request = Request(method=method, url=path, **kwargs)
        
        # Route the request
        route_match = self.router.match_route(request.path, request.method)
        
        if not route_match:
            return error_response('Not Found', HTTPStatus.NOT_FOUND)
        
        # Add path parameters
        request.path_params = route_match.params
        
        # Call handler
        return await route_match.handler(request)


async def test_integration():
    """Test integration of HTTP objects with router"""
    print("🧪 Testing HTTP Objects Integration")
    print("=" * 40)
    
    app = TestApp()
    
    # Test 1: Home page
    print("Testing home page...")
    response = await app.handle_request('GET', '/')
    assert response.status_code == 200
    assert response.headers['x-test'] == 'integration'
    assert 'Welcome to CovetPy' in response.get_body_bytes().decode()
    print("✓ Home page works")
    
    # Test 2: GET users with query parameters
    print("Testing GET users with query params...")
    response = await app.handle_request('GET', '/api/users?page=2&limit=5')
    assert response.status_code == 200
    assert 'cache-control' in response.headers
    
    body = json.loads(response.get_body_bytes().decode())
    assert body['page'] == 2
    assert body['limit'] == 5
    assert len(body['users']) == 5
    print("✓ GET users with query params works")
    
    # Test 3: POST create user with JSON
    print("Testing POST create user...")
    user_data = {'name': 'John Doe', 'email': 'john@example.com'}
    response = await app.handle_request(
        'POST', 
        '/api/users',
        headers={'Content-Type': 'application/json'},
        body=json.dumps(user_data).encode()
    )
    assert response.status_code == 201
    
    body = json.loads(response.get_body_bytes().decode())
    assert body['name'] == 'John Doe'
    assert body['email'] == 'john@example.com'
    print("✓ POST create user works")
    
    # Test 4: GET user by ID (path parameters)
    print("Testing GET user by ID...")
    response = await app.handle_request('GET', '/api/users/456')
    assert response.status_code == 200
    assert 'etag' in response.headers
    
    body = json.loads(response.get_body_bytes().decode())
    assert body['id'] == 456
    assert body['name'] == 'User 456'
    print("✓ GET user by ID works")
    
    # Test 5: 404 for unknown route
    print("Testing 404 for unknown route...")
    response = await app.handle_request('GET', '/unknown')
    assert response.status_code == 404
    
    body = json.loads(response.get_body_bytes().decode())
    assert 'Not Found' in body['error']
    print("✓ 404 handling works")
    
    # Test 6: Error handling for invalid JSON
    print("Testing error handling...")
    response = await app.handle_request(
        'POST',
        '/api/users',
        headers={'Content-Type': 'application/json'},
        body=b'invalid json'
    )
    assert response.status_code == 400
    
    body = json.loads(response.get_body_bytes().decode())
    assert 'error' in body
    print("✓ Error handling works")
    
    # Test 7: Content type validation
    print("Testing content type validation...")
    response = await app.handle_request(
        'POST',
        '/api/users',
        headers={'Content-Type': 'text/plain'},
        body=b'not json'
    )
    assert response.status_code == 400
    
    body = json.loads(response.get_body_bytes().decode())
    assert 'JSON required' in body['error']
    print("✓ Content type validation works")
    
    print("=" * 40)
    print("✅ All integration tests passed!")
    print("\n🎯 Integration features verified:")
    print("   ✓ Router integration with new Request/Response objects")
    print("   ✓ Path parameter extraction")
    print("   ✓ Query parameter parsing")
    print("   ✓ JSON request/response handling")
    print("   ✓ HTTP status codes")
    print("   ✓ Headers management")
    print("   ✓ ETag generation")
    print("   ✓ Cache control")
    print("   ✓ Error handling")
    print("   ✓ Content type validation")
    
    return True


async def main():
    """Run integration tests"""
    try:
        await test_integration()
        return 0
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit_code = asyncio.run(main())