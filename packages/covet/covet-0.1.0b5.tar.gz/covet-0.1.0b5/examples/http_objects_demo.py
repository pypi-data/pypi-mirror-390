#!/usr/bin/env python3
"""
CovetPy HTTP Objects Integration Demo
====================================

This demo shows how the production-grade Request and Response objects
integrate with CovetPy's HTTP server and routing system.

Features demonstrated:
- Request handling with all features
- Response generation with compression and caching
- File uploads and multipart forms
- Session management
- Content negotiation
- WebSocket upgrade detection
- Performance optimizations
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from covet.core.http_objects import (
    Request,
    Response,
    FileResponse,
    StreamingResponse,
    json_response,
    html_response,
    text_response,
    redirect_response,
    error_response,
    HTTPStatus,
    MemorySessionInterface,
)
from covet.core.routing import CovetRouter
from covet.core.http_server import CovetHTTPServer, ServerConfig


class CovetApp:
    """Enhanced CovetPy application with new HTTP objects"""
    
    def __init__(self):
        self.router = CovetRouter()
        self.session_interface = MemorySessionInterface()
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup demonstration routes"""
        
        # Basic routes
        self.router.add_route('/', self.home, ['GET'])
        self.router.add_route('/api/health', self.health_check, ['GET'])
        
        # JSON API routes
        self.router.add_route('/api/users', self.get_users, ['GET'])
        self.router.add_route('/api/users', self.create_user, ['POST'])
        self.router.add_route('/api/users/{user_id}', self.get_user, ['GET'])
        self.router.add_route('/api/users/{user_id}', self.update_user, ['PUT'])
        self.router.add_route('/api/users/{user_id}', self.delete_user, ['DELETE'])
        
        # File operations
        self.router.add_route('/upload', self.upload_form, ['GET'])
        self.router.add_route('/upload', self.handle_upload, ['POST'])
        self.router.add_route('/download/{filename}', self.download_file, ['GET'])
        
        # Session management
        self.router.add_route('/login', self.login_form, ['GET'])
        self.router.add_route('/login', self.handle_login, ['POST'])
        self.router.add_route('/logout', self.handle_logout, ['POST'])
        self.router.add_route('/profile', self.profile, ['GET'])
        
        # Content negotiation
        self.router.add_route('/api/data', self.content_negotiation, ['GET'])
        
        # Streaming content
        self.router.add_route('/stream', self.stream_data, ['GET'])
        
        # WebSocket upgrade
        self.router.add_route('/ws', self.websocket_upgrade, ['GET'])
        
        # Compression demo
        self.router.add_route('/large-data', self.large_data, ['GET'])
        
        # Caching demo
        self.router.add_route('/cached-content/{content_id}', self.cached_content, ['GET'])
    
    async def __call__(self, scope, receive, send):
        """ASGI application interface"""
        if scope['type'] != 'http':
            await send({
                'type': 'http.response.start',
                'status': 404,
                'headers': [[b'content-type', b'text/plain']],
            })
            await send({
                'type': 'http.response.body',
                'body': b'Not Found',
            })
            return
        
        # Create enhanced Request object
        request = await self._create_request(scope, receive)
        
        # Route the request
        route_match = self.router.match_route(request.path, request.method)
        
        if not route_match:
            response = error_response('Not Found', HTTPStatus.NOT_FOUND)
        else:
            try:
                # Add path parameters to request
                request.path_params = route_match.params
                
                # Call the handler
                response = await route_match.handler(request)
                
                # Ensure we have a Response object
                if not isinstance(response, (Response, StreamingResponse, FileResponse)):
                    response = Response(content=response)
                
            except Exception as e:
                response = error_response(
                    f'Internal Server Error: {str(e)}',
                    HTTPStatus.INTERNAL_SERVER_ERROR
                )
        
        # Apply compression if supported
        if hasattr(response, 'compress') and request.accepts_encoding('gzip'):
            response.compress(request.accept_encoding)
        
        # Send response
        await response(scope, receive, send)
    
    async def _create_request(self, scope, receive):
        """Create Request object from ASGI scope"""
        # Get body
        body = b''
        while True:
            message = await receive()
            if message['type'] == 'http.request':
                body += message.get('body', b'')
                if not message.get('more_body', False):
                    break
            elif message['type'] == 'http.disconnect':
                break
        
        # Extract headers
        headers = {}
        for header_name, header_value in scope.get('headers', []):
            name = header_name.decode('latin-1')
            value = header_value.decode('latin-1')
            headers[name] = value
        
        # Extract query string
        query_string = scope.get('query_string', b'').decode('latin-1')
        
        # Create request
        request = Request(
            method=scope['method'],
            url=scope['path'] + ('?' + query_string if query_string else ''),
            headers=headers,
            body=body,
            query_string=query_string,
            client_addr=scope.get('client'),
            server_addr=scope.get('server'),
            scheme=scope['scheme'],
            session_interface=self.session_interface,
        )
        
        return request
    
    # Route handlers
    
    async def home(self, request: Request) -> Response:
        """Home page with feature overview"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CovetPy HTTP Objects Demo</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .feature { margin: 20px 0; padding: 10px; border-left: 3px solid #007acc; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 5px 0; }
                code { background: #f0f0f0; padding: 2px 4px; }
            </style>
        </head>
        <body>
            <h1>CovetPy HTTP Objects Demo</h1>
            <p>This demo showcases the production-grade HTTP Request and Response objects.</p>
            
            <div class="feature">
                <h3>API Endpoints</h3>
                <div class="endpoint">GET <code>/api/health</code> - Health check</div>
                <div class="endpoint">GET <code>/api/users</code> - List users</div>
                <div class="endpoint">POST <code>/api/users</code> - Create user (JSON)</div>
                <div class="endpoint">GET <code>/api/users/123</code> - Get user by ID</div>
            </div>
            
            <div class="feature">
                <h3>File Operations</h3>
                <div class="endpoint">GET <code>/upload</code> - File upload form</div>
                <div class="endpoint">POST <code>/upload</code> - Handle file upload</div>
                <div class="endpoint">GET <code>/download/filename</code> - Download file</div>
            </div>
            
            <div class="feature">
                <h3>Session Management</h3>
                <div class="endpoint">GET <code>/login</code> - Login form</div>
                <div class="endpoint">POST <code>/login</code> - Handle login</div>
                <div class="endpoint">GET <code>/profile</code> - User profile (requires session)</div>
            </div>
            
            <div class="feature">
                <h3>Advanced Features</h3>
                <div class="endpoint">GET <code>/api/data</code> - Content negotiation demo</div>
                <div class="endpoint">GET <code>/stream</code> - Streaming response</div>
                <div class="endpoint">GET <code>/large-data</code> - Compression demo</div>
                <div class="endpoint">GET <code>/cached-content/123</code> - Caching demo</div>
            </div>
        </body>
        </html>
        """
        
        response = html_response(html_content)
        response.set_cache_control(max_age=300, public=True)
        return response
    
    async def health_check(self, request: Request) -> Response:
        """Health check endpoint"""
        health_data = {
            'status': 'healthy',
            'timestamp': '2023-01-01T00:00:00Z',
            'version': '1.0.0',
            'request_id': request.request_id,
            'client_ip': request.remote_addr,
        }
        
        response = json_response(health_data)
        response.set_cache_control(no_cache=True)
        return response
    
    async def get_users(self, request: Request) -> Response:
        """Get list of users with pagination"""
        page = int(request.query_params.get('page', '1'))
        limit = int(request.query_params.get('limit', '10'))
        
        # Simulate user data
        users = [
            {'id': i, 'name': f'User {i}', 'email': f'user{i}@example.com'}
            for i in range((page - 1) * limit + 1, page * limit + 1)
        ]
        
        response_data = {
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': 100,  # Simulated total
            }
        }
        
        response = json_response(response_data)
        response.set_etag(f'users-page-{page}-limit-{limit}')
        response.set_cache_control(max_age=60, public=True)
        return response
    
    async def create_user(self, request: Request) -> Response:
        """Create a new user"""
        if not request.is_json():
            return error_response('Content-Type must be application/json', HTTPStatus.BAD_REQUEST)
        
        try:
            user_data = await request.json()
            
            # Validate required fields
            if 'name' not in user_data or 'email' not in user_data:
                return error_response('Name and email are required', HTTPStatus.BAD_REQUEST)
            
            # Simulate user creation
            new_user = {
                'id': 12345,  # Simulated new ID
                'name': user_data['name'],
                'email': user_data['email'],
                'created_at': '2023-01-01T00:00:00Z'
            }
            
            response = json_response(new_user, HTTPStatus.CREATED)
            response.headers['location'] = f'/api/users/{new_user["id"]}'
            return response
            
        except json.JSONDecodeError:
            return error_response('Invalid JSON', HTTPStatus.BAD_REQUEST)
    
    async def get_user(self, request: Request) -> Response:
        """Get user by ID"""
        user_id = request.path_params['user_id']
        
        # Simulate user lookup
        user = {
            'id': int(user_id),
            'name': f'User {user_id}',
            'email': f'user{user_id}@example.com',
            'profile': {
                'created_at': '2023-01-01T00:00:00Z',
                'last_login': '2023-01-01T12:00:00Z'
            }
        }
        
        response = json_response(user)
        response.set_etag(f'user-{user_id}')
        response.set_cache_control(max_age=300, public=True)
        return response
    
    async def update_user(self, request: Request) -> Response:
        """Update user by ID"""
        user_id = request.path_params['user_id']
        
        if not request.is_json():
            return error_response('Content-Type must be application/json', HTTPStatus.BAD_REQUEST)
        
        try:
            update_data = await request.json()
            
            # Simulate user update
            updated_user = {
                'id': int(user_id),
                'name': update_data.get('name', f'User {user_id}'),
                'email': update_data.get('email', f'user{user_id}@example.com'),
                'updated_at': '2023-01-01T12:00:00Z'
            }
            
            return json_response(updated_user)
            
        except json.JSONDecodeError:
            return error_response('Invalid JSON', HTTPStatus.BAD_REQUEST)
    
    async def delete_user(self, request: Request) -> Response:
        """Delete user by ID"""
        user_id = request.path_params['user_id']
        
        # Simulate user deletion
        return Response(status_code=HTTPStatus.NO_CONTENT)
    
    async def upload_form(self, request: Request) -> Response:
        """File upload form"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>File Upload Demo</title>
        </head>
        <body>
            <h1>File Upload Demo</h1>
            <form method="post" enctype="multipart/form-data">
                <div>
                    <label for="title">Title:</label>
                    <input type="text" id="title" name="title" required>
                </div>
                <div>
                    <label for="file">Choose file:</label>
                    <input type="file" id="file" name="file" required>
                </div>
                <div>
                    <label for="description">Description:</label>
                    <textarea id="description" name="description"></textarea>
                </div>
                <button type="submit">Upload</button>
            </form>
        </body>
        </html>
        """
        
        return html_response(html_content)
    
    async def handle_upload(self, request: Request) -> Response:
        """Handle file upload"""
        if not request.is_multipart():
            return error_response('Content-Type must be multipart/form-data', HTTPStatus.BAD_REQUEST)
        
        try:
            form_data = await request.form()
            
            title = form_data.get('title', 'Untitled')
            description = form_data.get('description', '')
            uploaded_file = form_data.get('file')
            
            if not uploaded_file:
                return error_response('No file uploaded', HTTPStatus.BAD_REQUEST)
            
            # Read file content
            file_content = await uploaded_file.read()
            
            # Simulate file processing
            response_data = {
                'success': True,
                'file_id': 'file_12345',
                'title': title,
                'description': description,
                'filename': uploaded_file.filename,
                'content_type': uploaded_file.content_type,
                'size': len(file_content),
                'uploaded_at': '2023-01-01T12:00:00Z'
            }
            
            return json_response(response_data, HTTPStatus.CREATED)
            
        except Exception as e:
            return error_response(f'Upload failed: {str(e)}', HTTPStatus.INTERNAL_SERVER_ERROR)
    
    async def download_file(self, request: Request) -> Response:
        """Serve file download"""
        filename = request.path_params['filename']
        
        # For demo, create a temporary file
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f'This is the content of {filename}\n')
            f.write('Generated by CovetPy HTTP Objects Demo\n')
            temp_path = f.name
        
        try:
            return FileResponse(
                temp_path,
                filename=filename,
                media_type='text/plain'
            )
        except FileNotFoundError:
            return error_response('File not found', HTTPStatus.NOT_FOUND)
        finally:
            # Clean up in background
            asyncio.create_task(self._cleanup_temp_file(temp_path))
    
    async def _cleanup_temp_file(self, path: str):
        """Clean up temporary file after a delay"""
        await asyncio.sleep(1)  # Give time for download
        try:
            os.unlink(path)
        except OSError:
            pass
    
    async def login_form(self, request: Request) -> Response:
        """Login form"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Login Demo</title>
        </head>
        <body>
            <h1>Login Demo</h1>
            <form method="post">
                <div>
                    <label for="username">Username:</label>
                    <input type="text" id="username" name="username" required>
                </div>
                <div>
                    <label for="password">Password:</label>
                    <input type="password" id="password" name="password" required>
                </div>
                <button type="submit">Login</button>
            </form>
        </body>
        </html>
        """
        
        return html_response(html_content)
    
    async def handle_login(self, request: Request) -> Response:
        """Handle login"""
        if request.is_form():
            form_data = await request.form()
            username = form_data.get('username')
            password = form_data.get('password')
        elif request.is_json():
            login_data = await request.json()
            username = login_data.get('username')
            password = login_data.get('password')
        else:
            return error_response('Invalid content type', HTTPStatus.BAD_REQUEST)
        
        # Simulate authentication
        if username == 'admin' and password == 'secret':
            # Create session
            session = await request.session()
            session['user_id'] = 123
            session['username'] = username
            session['logged_in'] = True
            
            session_id = await request.save_session()
            
            response = json_response({'success': True, 'message': 'Logged in successfully'})
            response.set_cookie('session_id', session_id, http_only=True, secure=False)  # secure=False for demo
            return response
        else:
            return error_response('Invalid credentials', HTTPStatus.UNAUTHORIZED)
    
    async def handle_logout(self, request: Request) -> Response:
        """Handle logout"""
        await request.clear_session()
        
        response = json_response({'success': True, 'message': 'Logged out successfully'})
        response.delete_cookie('session_id')
        return response
    
    async def profile(self, request: Request) -> Response:
        """User profile (requires session)"""
        session = await request.session()
        
        if not session.get('logged_in'):
            return error_response('Not authenticated', HTTPStatus.UNAUTHORIZED)
        
        profile_data = {
            'user_id': session['user_id'],
            'username': session['username'],
            'session_id': await request.save_session(),
            'login_time': '2023-01-01T12:00:00Z'
        }
        
        response = json_response(profile_data)
        response.set_cache_control(no_cache=True, private=True)
        return response
    
    async def content_negotiation(self, request: Request) -> Response:
        """Content negotiation demo"""
        data = {
            'message': 'Hello, World!',
            'timestamp': '2023-01-01T12:00:00Z',
            'supported_formats': ['json', 'xml', 'csv']
        }
        
        accept = request.accept.lower()
        
        if 'application/json' in accept or 'application/*' in accept:
            return json_response(data)
        elif 'text/html' in accept:
            html = f"""
            <html>
            <body>
                <h1>{data['message']}</h1>
                <p>Timestamp: {data['timestamp']}</p>
                <p>This content was negotiated based on Accept header: {request.accept}</p>
            </body>
            </html>
            """
            return html_response(html)
        elif 'text/plain' in accept:
            text = f"{data['message']}\nTimestamp: {data['timestamp']}"
            return text_response(text)
        else:
            return error_response('Not Acceptable', HTTPStatus.NOT_ACCEPTABLE)
    
    async def stream_data(self, request: Request) -> Response:
        """Streaming response demo"""
        
        async def generate_data():
            for i in range(10):
                yield f"data chunk {i}\n".encode()
                await asyncio.sleep(0.1)  # Simulate processing time
        
        return StreamingResponse(
            content=generate_data(),
            media_type="text/plain"
        )
    
    async def large_data(self, request: Request) -> Response:
        """Large data with compression demo"""
        # Generate large JSON response
        large_data = {
            'items': [
                {
                    'id': i,
                    'name': f'Item {i}',
                    'description': f'This is a detailed description for item {i}. ' * 10,
                    'metadata': {'key': 'value'} * 5
                }
                for i in range(500)  # Large dataset
            ],
            'total': 500,
            'compressed': True
        }
        
        response = json_response(large_data)
        response.set_cache_control(max_age=3600, public=True)
        
        # Compression will be applied automatically if client supports it
        return response
    
    async def cached_content(self, request: Request) -> Response:
        """Caching demo with ETags"""
        content_id = request.path_params['content_id']
        
        # Generate content based on ID
        content = {
            'id': content_id,
            'title': f'Content {content_id}',
            'body': f'This is the body content for item {content_id}.',
            'last_modified': '2023-01-01T12:00:00Z'
        }
        
        response = json_response(content)
        
        # Generate ETag based on content
        etag = response.generate_etag()
        
        # Check if client has cached version
        if_none_match = request.headers.get('if-none-match')
        if if_none_match and f'"{etag}"' in if_none_match:
            return Response(status_code=HTTPStatus.NOT_MODIFIED)
        
        # Set cache headers
        response.set_cache_control(max_age=1800, public=True)
        response.set_expires(1800)  # 30 minutes
        
        return response
    
    async def websocket_upgrade(self, request: Request) -> Response:
        """WebSocket upgrade detection"""
        if request.is_websocket():
            # In a real implementation, this would handle the WebSocket upgrade
            return Response(
                content="WebSocket upgrade detected (not implemented in this demo)",
                status_code=HTTPStatus.NOT_IMPLEMENTED
            )
        else:
            return html_response("""
            <html>
            <body>
                <h1>WebSocket Demo</h1>
                <p>This endpoint detects WebSocket upgrade requests.</p>
                <p>Try connecting with a WebSocket client!</p>
            </body>
            </html>
            """)


async def main():
    """Run the demo server"""
    app = CovetApp()
    
    # Configure server
    config = ServerConfig(
        host='127.0.0.1',
        port=8000,
        debug=True,
        access_log=True,
    )
    
    server = CovetHTTPServer(app, config)
    
    print("🚀 CovetPy HTTP Objects Demo Server Starting...")
    print(f"📍 Server running at http://{config.host}:{config.port}")
    print("📖 Visit http://127.0.0.1:8000 for feature overview")
    print("\n📋 API Endpoints:")
    print("   GET  /api/health          - Health check")
    print("   GET  /api/users           - List users")
    print("   POST /api/users           - Create user (JSON)")
    print("   GET  /api/users/123       - Get user by ID")
    print("   GET  /upload              - File upload form")
    print("   POST /upload              - Handle file upload")
    print("   GET  /login               - Login form")
    print("   GET  /api/data            - Content negotiation demo")
    print("   GET  /stream              - Streaming response")
    print("   GET  /large-data          - Compression demo")
    print("   GET  /cached-content/123  - Caching demo")
    print("\n💡 Features Demonstrated:")
    print("   ✓ Lazy parsing and performance optimizations")
    print("   ✓ File uploads with multipart/form-data")
    print("   ✓ Session management with cookies")
    print("   ✓ Content negotiation")
    print("   ✓ Response compression (gzip)")
    print("   ✓ ETags and caching")
    print("   ✓ Streaming responses")
    print("   ✓ WebSocket upgrade detection")
    print("   ✓ Comprehensive error handling")
    print("\n Press Ctrl+C to stop the server")
    
    try:
        await server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        await server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())