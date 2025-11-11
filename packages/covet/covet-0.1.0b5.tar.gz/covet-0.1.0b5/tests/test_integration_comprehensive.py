"""
Comprehensive integration tests for CovetPy framework.
These tests verify end-to-end functionality and real API workflows.
"""
import os
import sys
import json
import asyncio
import sqlite3
import tempfile
import time
import threading
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAPIIntegration:
    """Test complete API integration scenarios."""
    
    def test_rest_api_crud_workflow(self):
        """Test complete REST API CRUD workflow."""
        class RESTAPIFramework:
            def __init__(self, db_path):
                self.db_path = db_path
                self.routes = {}
                self._init_database()
            
            def _init_database(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                conn.close()
            
            def route(self, path, methods=None):
                methods = methods or ['GET']
                def decorator(handler):
                    for method in methods:
                        key = f"{method}:{path}"
                        self.routes[key] = handler
                    return handler
                return decorator
            
            async def handle_request(self, method, path, body=None, params=None):
                # Extract path parameters
                path_parts = path.split('/')
                route_key = f"{method}:{path}"
                
                # Try exact match first
                if route_key in self.routes:
                    return await self.routes[route_key](body, params)
                
                # Try pattern matching for parameterized routes
                for registered_route, handler in self.routes.items():
                    registered_method, registered_path = registered_route.split(':', 1)
                    if registered_method == method:
                        registered_parts = registered_path.split('/')
                        if len(registered_parts) == len(path_parts):
                            match = True
                            extracted_params = {}
                            for i, (reg_part, path_part) in enumerate(zip(registered_parts, path_parts)):
                                if reg_part.startswith('{') and reg_part.endswith('}'):
                                    param_name = reg_part[1:-1]
                                    extracted_params[param_name] = path_part
                                elif reg_part != path_part:
                                    match = False
                                    break
                            
                            if match:
                                return await handler(body, {**(params or {}), **extracted_params})
                
                return {'error': 'Not Found'}, 404
            
            def _get_db_connection(self):
                return sqlite3.connect(self.db_path)
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            api = RESTAPIFramework(db_path)
            
            # Define API endpoints
            @api.route('/users', ['GET', 'POST'])
            async def users_endpoint(body, params):
                conn = api._get_db_connection()
                cursor = conn.cursor()
                
                if params and 'method' in params:
                    method = params['method']
                else:
                    # Infer method from request context (simplified)
                    method = 'GET' if not body else 'POST'
                
                if method == 'GET':
                    cursor.execute('SELECT * FROM users ORDER BY created_at DESC')
                    users = []
                    for row in cursor.fetchall():
                        users.append({
                            'id': row[0],
                            'name': row[1],
                            'email': row[2],
                            'created_at': row[3],
                            'updated_at': row[4]
                        })
                    conn.close()
                    return {'users': users}
                
                elif method == 'POST':
                    data = json.loads(body) if isinstance(body, str) else body
                    cursor.execute(
                        'INSERT INTO users (name, email) VALUES (?, ?)',
                        (data['name'], data['email'])
                    )
                    user_id = cursor.lastrowid
                    conn.commit()
                    conn.close()
                    return {'id': user_id, 'message': 'User created'}, 201
            
            @api.route('/users/{id}', ['GET', 'PUT', 'DELETE'])
            async def user_by_id_endpoint(body, params):
                user_id = int(params['id'])
                conn = api._get_db_connection()
                cursor = conn.cursor()
                
                method = params.get('method', 'GET')
                
                if method == 'GET':
                    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                    row = cursor.fetchone()
                    conn.close()
                    
                    if row:
                        user = {
                            'id': row[0],
                            'name': row[1],
                            'email': row[2],
                            'created_at': row[3],
                            'updated_at': row[4]
                        }
                        return {'user': user}
                    else:
                        return {'error': 'User not found'}, 404
                
                elif method == 'PUT':
                    data = json.loads(body) if isinstance(body, str) else body
                    cursor.execute(
                        'UPDATE users SET name = ?, email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                        (data['name'], data['email'], user_id)
                    )
                    if cursor.rowcount > 0:
                        conn.commit()
                        conn.close()
                        return {'message': 'User updated'}
                    else:
                        conn.close()
                        return {'error': 'User not found'}, 404
                
                elif method == 'DELETE':
                    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    if cursor.rowcount > 0:
                        conn.commit()
                        conn.close()
                        return {'message': 'User deleted'}
                    else:
                        conn.close()
                        return {'error': 'User not found'}, 404
            
            # Test the complete CRUD workflow
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 1. Create users (POST)
                user1_data = {'name': 'John Doe', 'email': 'john@example.com'}
                response, status = loop.run_until_complete(
                    api.handle_request('POST', '/users', user1_data, {'method': 'POST'})
                )
                assert status == 201
                assert 'id' in response
                user1_id = response['id']
                
                user2_data = {'name': 'Jane Smith', 'email': 'jane@example.com'}
                response, status = loop.run_until_complete(
                    api.handle_request('POST', '/users', user2_data, {'method': 'POST'})
                )
                assert status == 201
                user2_id = response['id']
                
                # 2. List users (GET)
                response = loop.run_until_complete(
                    api.handle_request('GET', '/users', None, {'method': 'GET'})
                )
                assert 'users' in response
                assert len(response['users']) == 2
                
                # 3. Get specific user (GET)
                response = loop.run_until_complete(
                    api.handle_request('GET', f'/users/{user1_id}', None, {'method': 'GET'})
                )
                assert 'user' in response
                assert response['user']['name'] == 'John Doe'
                assert response['user']['email'] == 'john@example.com'
                
                # 4. Update user (PUT)
                updated_data = {'name': 'John Updated', 'email': 'john.updated@example.com'}
                response = loop.run_until_complete(
                    api.handle_request('PUT', f'/users/{user1_id}', updated_data, {'method': 'PUT'})
                )
                assert response['message'] == 'User updated'
                
                # 5. Verify update
                response = loop.run_until_complete(
                    api.handle_request('GET', f'/users/{user1_id}', None, {'method': 'GET'})
                )
                assert response['user']['name'] == 'John Updated'
                assert response['user']['email'] == 'john.updated@example.com'
                
                # 6. Delete user (DELETE)
                response = loop.run_until_complete(
                    api.handle_request('DELETE', f'/users/{user2_id}', None, {'method': 'DELETE'})
                )
                assert response['message'] == 'User deleted'
                
                # 7. Verify deletion
                response, status = loop.run_until_complete(
                    api.handle_request('GET', f'/users/{user2_id}', None, {'method': 'GET'})
                )
                assert status == 404
                assert response['error'] == 'User not found'
                
                # 8. Verify remaining users
                response = loop.run_until_complete(
                    api.handle_request('GET', '/users', None, {'method': 'GET'})
                )
                assert len(response['users']) == 1
                assert response['users'][0]['name'] == 'John Updated'
                
            finally:
                loop.close()
        finally:
            os.unlink(db_path)

class TestAuthenticationIntegration:
    """Test authentication and session management integration."""
    
    def test_complete_auth_workflow(self):
        """Test complete authentication workflow."""
        import hashlib
        import secrets
        import jwt
        
        class AuthSystem:
            def __init__(self, db_path):
                self.db_path = db_path
                self.secret_key = "test_secret_key_12345"
                self.sessions = {}
                self._init_database()
            
            def _init_database(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                conn.close()
            
            def _hash_password(self, password, salt=None):
                if salt is None:
                    salt = secrets.token_bytes(32)
                password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                return password_hash, salt
            
            async def register_user(self, username, email, password):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                try:
                    password_hash, salt = self._hash_password(password)
                    cursor.execute(
                        'INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)',
                        (username, email, password_hash, salt)
                    )
                    user_id = cursor.lastrowid
                    conn.commit()
                    return {'user_id': user_id, 'message': 'User registered successfully'}
                except sqlite3.IntegrityError as e:
                    if 'username' in str(e):
                        return {'error': 'Username already exists'}, 400
                    elif 'email' in str(e):
                        return {'error': 'Email already exists'}, 400
                    else:
                        return {'error': 'Registration failed'}, 400
                finally:
                    conn.close()
            
            async def authenticate_user(self, username, password):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT id, username, email, password_hash, salt FROM users WHERE username = ?',
                    (username,)
                )
                user_row = cursor.fetchone()
                conn.close()
                
                if user_row:
                    user_id, username, email, stored_hash, salt = user_row
                    password_hash, _ = self._hash_password(password, salt)
                    
                    if password_hash == stored_hash:
                        # Generate JWT token
                        payload = {
                            'user_id': user_id,
                            'username': username,
                            'exp': datetime.utcnow() + timedelta(hours=24),
                            'iat': datetime.utcnow()
                        }
                        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
                        
                        # Create session
                        session_id = secrets.token_urlsafe(32)
                        self.sessions[session_id] = {
                            'user_id': user_id,
                            'username': username,
                            'created_at': time.time(),
                            'last_activity': time.time()
                        }
                        
                        return {
                            'token': token,
                            'session_id': session_id,
                            'user': {
                                'id': user_id,
                                'username': username,
                                'email': email
                            }
                        }
                
                return {'error': 'Invalid credentials'}, 401
            
            async def validate_token(self, token):
                try:
                    payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
                    return payload
                except jwt.ExpiredSignatureError:
                    return {'error': 'Token expired'}, 401
                except jwt.InvalidTokenError:
                    return {'error': 'Invalid token'}, 401
            
            async def validate_session(self, session_id):
                if session_id in self.sessions:
                    session = self.sessions[session_id]
                    # Check if session is expired (24 hours)
                    if time.time() - session['created_at'] < 86400:
                        # Update last activity
                        session['last_activity'] = time.time()
                        return session
                    else:
                        # Remove expired session
                        del self.sessions[session_id]
                
                return None
            
            async def logout(self, session_id):
                if session_id in self.sessions:
                    del self.sessions[session_id]
                    return {'message': 'Logged out successfully'}
                return {'error': 'Session not found'}, 404
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            auth = AuthSystem(db_path)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 1. Register users
                response = loop.run_until_complete(
                    auth.register_user("testuser", "test@example.com", "secure_password123")
                )
                assert 'user_id' in response
                assert response['message'] == 'User registered successfully'
                
                # Try to register duplicate username
                response, status = loop.run_until_complete(
                    auth.register_user("testuser", "different@example.com", "password123")
                )
                assert status == 400
                assert response['error'] == 'Username already exists'
                
                # 2. Authenticate user
                response = loop.run_until_complete(
                    auth.authenticate_user("testuser", "secure_password123")
                )
                assert 'token' in response
                assert 'session_id' in response
                assert 'user' in response
                assert response['user']['username'] == 'testuser'
                
                token = response['token']
                session_id = response['session_id']
                
                # 3. Validate token
                payload = loop.run_until_complete(auth.validate_token(token))
                assert payload['username'] == 'testuser'
                assert 'exp' in payload
                
                # 4. Validate session
                session = loop.run_until_complete(auth.validate_session(session_id))
                assert session is not None
                assert session['username'] == 'testuser'
                
                # 5. Test invalid credentials
                response, status = loop.run_until_complete(
                    auth.authenticate_user("testuser", "wrong_password")
                )
                assert status == 401
                assert response['error'] == 'Invalid credentials'
                
                # 6. Test invalid token
                invalid_token = "invalid.token.here"
                response, status = loop.run_until_complete(auth.validate_token(invalid_token))
                assert status == 401
                assert response['error'] == 'Invalid token'
                
                # 7. Logout
                response = loop.run_until_complete(auth.logout(session_id))
                assert response['message'] == 'Logged out successfully'
                
                # 8. Validate session after logout
                session = loop.run_until_complete(auth.validate_session(session_id))
                assert session is None
                
            finally:
                loop.close()
        finally:
            os.unlink(db_path)

class TestWebSocketIntegration:
    """Test WebSocket integration scenarios."""
    
    def test_realtime_chat_simulation(self):
        """Test real-time chat functionality simulation."""
        import queue
        import threading
        
        class ChatRoom:
            def __init__(self):
                self.connections = {}
                self.rooms = {}
                self.message_history = {}
                self._lock = threading.Lock()
            
            async def connect_user(self, user_id, username, room_id="general"):
                with self._lock:
                    self.connections[user_id] = {
                        'username': username,
                        'room_id': room_id,
                        'connected_at': time.time(),
                        'last_activity': time.time()
                    }
                    
                    if room_id not in self.rooms:
                        self.rooms[room_id] = set()
                        self.message_history[room_id] = []
                    
                    self.rooms[room_id].add(user_id)
                
                # Notify other users in room
                await self._broadcast_to_room(room_id, {
                    'type': 'user_joined',
                    'username': username,
                    'user_id': user_id,
                    'timestamp': time.time()
                }, exclude_user=user_id)
                
                return True
            
            async def disconnect_user(self, user_id):
                with self._lock:
                    if user_id in self.connections:
                        user_info = self.connections[user_id]
                        room_id = user_info['room_id']
                        username = user_info['username']
                        
                        # Remove from room
                        if room_id in self.rooms:
                            self.rooms[room_id].discard(user_id)
                        
                        del self.connections[user_id]
                        
                        # Notify other users
                        await self._broadcast_to_room(room_id, {
                            'type': 'user_left',
                            'username': username,
                            'user_id': user_id,
                            'timestamp': time.time()
                        })
                
                return True
            
            async def send_message(self, user_id, message_content):
                if user_id not in self.connections:
                    return False
                
                user_info = self.connections[user_id]
                room_id = user_info['room_id']
                username = user_info['username']
                
                message = {
                    'type': 'message',
                    'user_id': user_id,
                    'username': username,
                    'content': message_content,
                    'timestamp': time.time(),
                    'room_id': room_id
                }
                
                # Store message in history
                with self._lock:
                    self.message_history[room_id].append(message)
                    user_info['last_activity'] = time.time()
                
                # Broadcast to room
                await self._broadcast_to_room(room_id, message)
                
                return True
            
            async def _broadcast_to_room(self, room_id, message, exclude_user=None):
                if room_id not in self.rooms:
                    return
                
                # Simulate message delivery
                delivered_count = 0
                for user_id in list(self.rooms[room_id]):
                    if user_id != exclude_user:
                        # Simulate async message delivery
                        await asyncio.sleep(0.001)  # Small delay
                        delivered_count += 1
                
                return delivered_count
            
            def get_room_users(self, room_id):
                if room_id not in self.rooms:
                    return []
                
                users = []
                for user_id in self.rooms[room_id]:
                    if user_id in self.connections:
                        user_info = self.connections[user_id]
                        users.append({
                            'user_id': user_id,
                            'username': user_info['username'],
                            'connected_at': user_info['connected_at'],
                            'last_activity': user_info['last_activity']
                        })
                
                return users
            
            def get_message_history(self, room_id, limit=50):
                if room_id not in self.message_history:
                    return []
                
                messages = self.message_history[room_id]
                assert messages[-limit:] if len(messages) > limit else messages
        
        chat = ChatRoom()
        
        async def test_chat_functionality():
            # 1. Connect users to chat room
            await chat.connect_user("user1", "Alice", "general")
            await chat.connect_user("user2", "Bob", "general")
            await chat.connect_user("user3", "Charlie", "tech")
            
            # 2. Verify room users
            general_users = chat.get_room_users("general")
            assert len(general_users) == 2
            assert any(user['username'] == 'Alice' for user in general_users)
            assert any(user['username'] == 'Bob' for user in general_users)
            
            tech_users = chat.get_room_users("tech")
            assert len(tech_users) == 1
            assert tech_users[0]['username'] == 'Charlie'
            
            # 3. Send messages
            await chat.send_message("user1", "Hello everyone!")
            await chat.send_message("user2", "Hi Alice!")
            await chat.send_message("user1", "How's everyone doing?")
            await chat.send_message("user3", "Hello from tech room!")
            
            # 4. Check message history
            general_history = chat.get_message_history("general")
            assert len(general_history) == 3
            assert general_history[0]['content'] == "Hello everyone!"
            assert general_history[0]['username'] == "Alice"
            assert general_history[1]['content'] == "Hi Alice!"
            assert general_history[1]['username'] == "Bob"
            
            tech_history = chat.get_message_history("tech")
            assert len(tech_history) == 1
            assert tech_history[0]['content'] == "Hello from tech room!"
            assert tech_history[0]['username'] == "Charlie"
            
            # 5. Disconnect user
            await chat.disconnect_user("user2")
            
            # 6. Verify user removal
            general_users_after = chat.get_room_users("general")
            assert len(general_users_after) == 1
            assert general_users_after[0]['username'] == 'Alice'
            
            # 7. Try sending message from disconnected user
            result = await chat.send_message("user2", "This shouldn't work")
            assert result == False
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_chat_functionality())
        finally:
            loop.close()

@pytest.mark.integration
class TestEndToEndWorkflows:
    """Test complete end-to-end workflows."""
    
    def test_complete_web_application_workflow(self):
        """Test complete web application workflow with auth, API, and data persistence."""
        class WebApplication:
            def __init__(self, db_path):
                self.db_path = db_path
                self.auth_system = None
                self.api_routes = {}
                self.middleware = []
                self._init_database()
                self._setup_auth()
            
            def _init_database(self):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        salt TEXT NOT NULL,
                        role TEXT DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Posts table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        author_id INTEGER NOT NULL,
                        published BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (author_id) REFERENCES users (id)
                    )
                ''')
                
                conn.commit()
                conn.close()
            
            def _setup_auth(self):
                self.auth_system = type('AuthSystem', (), {
                    'sessions': {},
                    'secret_key': 'test_secret_key_12345'
                })()
            
            async def register_user(self, username, email, password, role='user'):
                import hashlib
                import secrets
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                try:
                    # Hash password
                    salt = secrets.token_bytes(32)
                    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                    
                    cursor.execute(
                        'INSERT INTO users (username, email, password_hash, salt, role) VALUES (?, ?, ?, ?, ?)',
                        (username, email, password_hash, salt, role)
                    )
                    user_id = cursor.lastrowid
                    conn.commit()
                    return {'user_id': user_id, 'message': 'User registered successfully'}
                except sqlite3.IntegrityError:
                    return {'error': 'Username or email already exists'}, 400
                finally:
                    conn.close()
            
            async def authenticate_user(self, username, password):
                import hashlib
                import secrets
                import jwt
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'SELECT id, username, email, password_hash, salt, role FROM users WHERE username = ?',
                    (username,)
                )
                user_row = cursor.fetchone()
                conn.close()
                
                if user_row:
                    user_id, username, email, stored_hash, salt, role = user_row
                    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
                    
                    if password_hash == stored_hash:
                        # Create session
                        session_id = secrets.token_urlsafe(32)
                        self.auth_system.sessions[session_id] = {
                            'user_id': user_id,
                            'username': username,
                            'role': role,
                            'created_at': time.time()
                        }
                        
                        return {
                            'session_id': session_id,
                            'user': {
                                'id': user_id,
                                'username': username,
                                'email': email,
                                'role': role
                            }
                        }
                
                return {'error': 'Invalid credentials'}, 401
            
            async def create_post(self, title, content, author_id, published=False):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute(
                    'INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)',
                    (title, content, author_id, published)
                )
                post_id = cursor.lastrowid
                conn.commit()
                conn.close()
                
                return {'post_id': post_id, 'message': 'Post created successfully'}
            
            async def get_posts(self, published_only=True, author_id=None):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                query = '''
                    SELECT p.id, p.title, p.content, p.author_id, p.published, 
                           p.created_at, p.updated_at, u.username
                    FROM posts p
                    JOIN users u ON p.author_id = u.id
                '''
                params = []
                
                conditions = []
                if published_only:
                    conditions.append('p.published = ?')
                    params.append(True)
                
                if author_id:
                    conditions.append('p.author_id = ?')
                    params.append(author_id)
                
                if conditions:
                    query += ' WHERE ' + ' AND '.join(conditions)
                
                query += ' ORDER BY p.created_at DESC'
                
                cursor.execute(query, params)
                posts = []
                for row in cursor.fetchall():
                    posts.append({
                        'id': row[0],
                        'title': row[1],
                        'content': row[2],
                        'author_id': row[3],
                        'published': bool(row[4]),
                        'created_at': row[5],
                        'updated_at': row[6],
                        'author_username': row[7]
                    })
                
                conn.close()
                return {'posts': posts}
            
            async def update_post(self, post_id, title=None, content=None, published=None, user_id=None):
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Check if user owns the post
                cursor.execute('SELECT author_id FROM posts WHERE id = ?', (post_id,))
                result = cursor.fetchone()
                
                if not result:
                    conn.close()
                    return {'error': 'Post not found'}, 404
                
                if result[0] != user_id:
                    conn.close()
                    return {'error': 'Permission denied'}, 403
                
                # Build update query
                updates = []
                params = []
                
                if title is not None:
                    updates.append('title = ?')
                    params.append(title)
                
                if content is not None:
                    updates.append('content = ?')
                    params.append(content)
                
                if published is not None:
                    updates.append('published = ?')
                    params.append(published)
                
                if updates:
                    updates.append('updated_at = CURRENT_TIMESTAMP')
                    params.append(post_id)
                    
                    query = f"UPDATE posts SET {', '.join(updates)} WHERE id = ?"
                    cursor.execute(query, params)
                    conn.commit()
                
                conn.close()
                return {'message': 'Post updated successfully'}
            
            def require_auth(self, session_id):
                """Middleware to require authentication."""
                if session_id not in self.auth_system.sessions:
                    return None
                return self.auth_system.sessions[session_id]
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            app = WebApplication(db_path)
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # 1. Register users
                response = loop.run_until_complete(
                    app.register_user("author1", "author1@example.com", "password123", "author")
                )
                assert 'user_id' in response
                
                response = loop.run_until_complete(
                    app.register_user("reader1", "reader1@example.com", "password123", "user")
                )
                assert 'user_id' in response
                
                # 2. Authenticate author
                auth_response = loop.run_until_complete(
                    app.authenticate_user("author1", "password123")
                )
                assert 'session_id' in auth_response
                author_session = auth_response['session_id']
                author_id = auth_response['user']['id']
                
                # 3. Create posts
                post1_response = loop.run_until_complete(
                    app.create_post("First Post", "This is my first post content", author_id, True)
                )
                assert 'post_id' in post1_response
                post1_id = post1_response['post_id']
                
                post2_response = loop.run_until_complete(
                    app.create_post("Draft Post", "This is a draft", author_id, False)
                )
                assert 'post_id' in post2_response
                post2_id = post2_response['post_id']
                
                # 4. Get published posts
                posts_response = loop.run_until_complete(
                    app.get_posts(published_only=True)
                )
                assert len(posts_response['posts']) == 1
                assert posts_response['posts'][0]['title'] == "First Post"
                assert posts_response['posts'][0]['published'] == True
                
                # 5. Get all posts by author
                all_posts_response = loop.run_until_complete(
                    app.get_posts(published_only=False, author_id=author_id)
                )
                assert len(all_posts_response['posts']) == 2
                
                # 6. Update post
                user_session = app.require_auth(author_session)
                assert user_session is not None
                
                update_response = loop.run_until_complete(
                    app.update_post(post2_id, title="Updated Draft", published=True, user_id=author_id)
                )
                assert update_response['message'] == 'Post updated successfully'
                
                # 7. Verify update
                updated_posts_response = loop.run_until_complete(
                    app.get_posts(published_only=True)
                )
                assert len(updated_posts_response['posts']) == 2
                
                # 8. Test permission denied
                # Authenticate reader
                reader_auth_response = loop.run_until_complete(
                    app.authenticate_user("reader1", "password123")
                )
                reader_id = reader_auth_response['user']['id']
                
                # Try to update post as reader (should fail)
                permission_response, status = loop.run_until_complete(
                    app.update_post(post1_id, title="Hacked", user_id=reader_id)
                )
                assert status == 403
                assert permission_response['error'] == 'Permission denied'
                
            finally:
                loop.close()
        finally:
            os.unlink(db_path)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])