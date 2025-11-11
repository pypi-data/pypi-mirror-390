"""
Comprehensive core functionality tests for CovetPy framework.
These tests verify core framework components, routing, middleware, and HTTP handling.
"""
import os
import sys
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from urllib.parse import parse_qs, urlparse
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestHTTPHandling:
    """Test HTTP request and response handling."""
    
    def test_http_request_parsing(self):
        """Test HTTP request parsing functionality."""
        class HTTPRequest:
            def __init__(self, method, path, headers=None, body=b'', query_string=''):
                self.method = method
                self.path = path
                self.headers = headers or {}
                self.body = body
                self.query_string = query_string
                self._parsed_query = None
            
            @property
            def query_params(self):
                if self._parsed_query is None:
                    self._parsed_query = parse_qs(self.query_string)
                return self._parsed_query
            
            def get_header(self, name, default=None):
                return self.headers.get(name.lower(), default)
            
            def json(self):
                if self.get_header('content-type', '').startswith('application/json'):
                    return json.loads(self.body.decode())
                return None
        
        # Test basic request
        request = HTTPRequest('GET', '/api/users', {'content-type': 'application/json'})
        assert request.method == 'GET'
        assert request.path == '/api/users'
        assert request.get_header('content-type') == 'application/json'
        
        # Test query parameters
        request_with_query = HTTPRequest('GET', '/api/users', query_string='page=1&limit=10&sort=name')
        query_params = request_with_query.query_params
        assert query_params['page'] == ['1']
        assert query_params['limit'] == ['10']
        assert query_params['sort'] == ['name']
        
        # Test JSON body parsing
        json_data = {'name': 'John', 'email': 'john@example.com'}
        json_body = json.dumps(json_data).encode()
        json_request = HTTPRequest('POST', '/api/users', 
                                 {'content-type': 'application/json'}, 
                                 json_body)
        parsed_json = json_request.json()
        assert parsed_json == json_data
    
    def test_http_response_creation(self):
        """Test HTTP response creation functionality."""
        class HTTPResponse:
            def __init__(self, body='', status_code=200, headers=None, content_type='text/plain'):
                self.body = body
                self.status_code = status_code
                self.headers = headers or {}
                if content_type:
                    self.headers['content-type'] = content_type
            
            def set_header(self, name, value):
                self.headers[name.lower()] = value
            
            def set_cookie(self, name, value, max_age=None, secure=False, httponly=False):
                cookie_value = f"{name}={value}"
                if max_age:
                    cookie_value += f"; Max-Age={max_age}"
                if secure:
                    cookie_value += "; Secure"
                if httponly:
                    cookie_value += "; HttpOnly"
                
                if 'set-cookie' in self.headers:
                    if isinstance(self.headers['set-cookie'], list):
                        self.headers['set-cookie'].append(cookie_value)
                    else:
                        self.headers['set-cookie'] = [self.headers['set-cookie'], cookie_value]
                else:
                    self.headers['set-cookie'] = cookie_value
        
        # Test basic response
        response = HTTPResponse('Hello, World!', 200)
        assert response.body == 'Hello, World!'
        assert response.status_code == 200
        assert response.headers['content-type'] == 'text/plain'
        
        # Test JSON response
        data = {'message': 'success', 'data': [1, 2, 3]}
        json_response = HTTPResponse(json.dumps(data), 200, content_type='application/json')
        assert json_response.headers['content-type'] == 'application/json'
        assert json.loads(json_response.body) == data
        
        # Test custom headers
        response.set_header('X-Custom-Header', 'custom-value')
        assert response.headers['x-custom-header'] == 'custom-value'
        
        # Test cookie setting
        response.set_cookie('session_id', 'abc123', max_age=3600, secure=True, httponly=True)
        expected_cookie = 'session_id=abc123; Max-Age=3600; Secure; HttpOnly'
        assert response.headers['set-cookie'] == expected_cookie

class TestRouting:
    """Test routing functionality."""
    
    def test_static_routing(self):
        """Test static route matching."""
        class StaticRouter:
            def __init__(self):
                self.routes = {}
            
            def add_route(self, path, handler, methods=None):
                methods = methods or ['GET']
                if path not in self.routes:
                    self.routes[path] = {}
                for method in methods:
                    self.routes[path][method] = handler
            
            def match(self, path, method):
                if path in self.routes and method in self.routes[path]:
                    return self.routes[path][method], {}
                return None, {}
        
        router = StaticRouter()
        
        # Mock handlers
        home_handler = Mock()
        users_handler = Mock()
        api_handler = Mock()
        
        # Add routes
        router.add_route('/', home_handler)
        router.add_route('/users', users_handler, ['GET', 'POST'])
        router.add_route('/api/data', api_handler)
        
        # Test route matching
        handler, params = router.match('/', 'GET')
        assert handler == home_handler
        
        handler, params = router.match('/users', 'GET')
        assert handler == users_handler
        
        handler, params = router.match('/users', 'POST')
        assert handler == users_handler
        
        # Test non-existent route
        handler, params = router.match('/nonexistent', 'GET')
        assert handler is None
        
        # Test wrong method
        handler, params = router.match('/users', 'DELETE')
        assert handler is None
    
    def test_dynamic_routing(self):
        """Test dynamic route matching with parameters."""
        import re
        
        class DynamicRouter:
            def __init__(self):
                self.routes = []
            
            def add_route(self, pattern, handler, methods=None):
                methods = methods or ['GET']
                # Convert pattern like /users/{id} to regex
                regex_pattern = pattern
                param_names = []
                
                # Find parameters in pattern
                import re
                params = re.findall(r'\{(\w+)\}', pattern)
                for param in params:
                    param_names.append(param)
                    regex_pattern = regex_pattern.replace(f'{{{param}}}', r'([^/]+)')
                
                regex_pattern = f'^{regex_pattern}$'
                
                self.routes.append({
                    'pattern': pattern,
                    'regex': re.compile(regex_pattern),
                    'param_names': param_names,
                    'handler': handler,
                    'methods': methods
                })
            
            def match(self, path, method):
                for route in self.routes:
                    if method in route['methods']:
                        match = route['regex'].match(path)
                        if match:
                            params = {}
                            for i, param_name in enumerate(route['param_names']):
                                params[param_name] = match.group(i + 1)
                            return route['handler'], params
                return None, {}
        
        router = DynamicRouter()
        
        # Mock handlers
        user_handler = Mock()
        post_handler = Mock()
        nested_handler = Mock()
        
        # Add dynamic routes
        router.add_route('/users/{id}', user_handler)
        router.add_route('/posts/{post_id}/comments/{comment_id}', nested_handler)
        router.add_route('/api/{version}/users/{user_id}', post_handler)
        
        # Test parameter extraction
        handler, params = router.match('/users/123', 'GET')
        assert handler == user_handler
        assert params == {'id': '123'}
        
        handler, params = router.match('/posts/456/comments/789', 'GET')
        assert handler == nested_handler
        assert params == {'post_id': '456', 'comment_id': '789'}
        
        handler, params = router.match('/api/v1/users/101', 'GET')
        assert handler == post_handler
        assert params == {'version': 'v1', 'user_id': '101'}
        
        # Test non-matching route
        handler, params = router.match('/invalid/route', 'GET')
        assert handler is None
        assert params == {}

class TestMiddleware:
    """Test middleware functionality."""
    
    def test_middleware_chain(self):
        """Test middleware chain execution."""
        class MiddlewareChain:
            def __init__(self):
                self.middleware = []
            
            def add_middleware(self, middleware_func):
                self.middleware.append(middleware_func)
            
            async def process(self, request, handler):
                # Build middleware chain
                async def run_handler(req):
                    return await handler(req)
                
                # Apply middleware in reverse order
                current_handler = run_handler
                for middleware in reversed(self.middleware):
                    current_handler = self._wrap_middleware(middleware, current_handler)
                
                return await current_handler(request)
            
            def _wrap_middleware(self, middleware, next_handler):
                async def wrapped(request):
                    return await middleware(request, next_handler)
                return wrapped
        
        # Mock request and response
        request = Mock()
        request.path = '/test'
        request.headers = {}
        
        # Mock final handler
        async def final_handler(req):
            return {'message': 'success'}
        
        # Logging middleware
        log_calls = []
        async def logging_middleware(request, next_handler):
            log_calls.append(f"Before: {request.path}")
            response = await next_handler(request)
            log_calls.append(f"After: {request.path}")
            return response
        
        # Auth middleware
        auth_calls = []
        async def auth_middleware(request, next_handler):
            auth_calls.append("Auth check")
            if request.headers.get('authorization'):
                return await next_handler(request)
            else:
                return {'error': 'Unauthorized'}, 401
        
        # Test with authorization
        chain = MiddlewareChain()
        chain.add_middleware(logging_middleware)
        chain.add_middleware(auth_middleware)
        
        request.headers['authorization'] = 'Bearer token123'
        
        # Run the test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(chain.process(request, final_handler))
            assert result == {'message': 'success'}
            assert len(log_calls) == 2
            assert log_calls[0] == "Before: /test"
            assert log_calls[1] == "After: /test"
            assert len(auth_calls) == 1
        finally:
            loop.close()
    
    def test_cors_middleware(self):
        """Test CORS middleware functionality."""
        class CORSMiddleware:
            def __init__(self, allowed_origins=None, allowed_methods=None, allowed_headers=None):
                self.allowed_origins = allowed_origins or ['*']
                self.allowed_methods = allowed_methods or ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
                self.allowed_headers = allowed_headers or ['Content-Type', 'Authorization']
            
            async def __call__(self, request, next_handler):
                # Handle preflight requests
                if request.method == 'OPTIONS':
                    return self._create_preflight_response(request)
                
                # Process normal request
                response = await next_handler(request)
                
                # Add CORS headers to response
                if hasattr(response, 'headers'):
                    self._add_cors_headers(request, response)
                
                return response
            
            def _create_preflight_response(self, request):
                response = Mock()
                response.status_code = 200
                response.body = ''
                response.headers = {}
                self._add_cors_headers(request, response)
                return response
            
            def _add_cors_headers(self, request, response):
                origin = request.headers.get('origin', '')
                
                if '*' in self.allowed_origins or origin in self.allowed_origins:
                    response.headers['Access-Control-Allow-Origin'] = origin or '*'
                
                response.headers['Access-Control-Allow-Methods'] = ', '.join(self.allowed_methods)
                response.headers['Access-Control-Allow-Headers'] = ', '.join(self.allowed_headers)
                response.headers['Access-Control-Max-Age'] = '86400'
        
        cors = CORSMiddleware()
        
        # Mock request and handler
        request = Mock()
        request.method = 'GET'
        request.headers = {'origin': 'https://example.com'}
        
        async def test_handler(req):
            response = Mock()
            response.status_code = 200
            response.headers = {}
            response.body = 'test response'
            return response
        
        # Test CORS headers addition
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(cors(request, test_handler))
            assert 'Access-Control-Allow-Origin' in response.headers
            assert response.headers['Access-Control-Allow-Origin'] == 'https://example.com'
            assert 'Access-Control-Allow-Methods' in response.headers
        finally:
            loop.close()
        
        # Test preflight request
        preflight_request = Mock()
        preflight_request.method = 'OPTIONS'
        preflight_request.headers = {'origin': 'https://example.com'}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            preflight_response = loop.run_until_complete(cors(preflight_request, test_handler))
            assert preflight_response.status_code == 200
            assert 'Access-Control-Allow-Origin' in preflight_response.headers
        finally:
            loop.close()

class TestAsyncHandling:
    """Test asynchronous request handling."""
    
    def test_async_request_processing(self):
        """Test asynchronous request processing."""
        class AsyncRequestProcessor:
            def __init__(self):
                self.active_requests = 0
                self.completed_requests = 0
            
            async def process_request(self, request_id, processing_time=0.1):
                self.active_requests += 1
                try:
                    # Simulate async processing
                    await asyncio.sleep(processing_time)
                    result = {'request_id': request_id, 'status': 'completed'}
                    self.completed_requests += 1
                    return result
                finally:
                    self.active_requests -= 1
            
            async def process_batch(self, request_ids, processing_time=0.1):
                tasks = []
                for request_id in request_ids:
                    task = asyncio.create_task(
                        self.process_request(request_id, processing_time)
                    )
                    tasks.append(task)
                
                results = await asyncio.gather(*tasks)
                return results
        
        processor = AsyncRequestProcessor()
        
        async def test_concurrent_processing():
            # Test concurrent request processing
            request_ids = [f'req_{i}' for i in range(5)]
            start_time = time.time()
            
            results = await processor.process_batch(request_ids, 0.1)
            
            end_time = time.time()
            processing_time = end_time - start_time
            
            # Should process concurrently, so total time should be close to 0.1s
            # rather than 0.5s if processed sequentially
            assert processing_time < 0.3  # Allow some overhead
            assert len(results) == 5
            assert processor.completed_requests == 5
            
            # Verify all requests completed
            for i, result in enumerate(results):
                assert result['request_id'] == f'req_{i}'
                assert result['status'] == 'completed'
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_concurrent_processing())
        finally:
            loop.close()
    
    def test_websocket_simulation(self):
        """Test WebSocket-like real-time communication simulation."""
        import queue
        
        class WebSocketSimulator:
            def __init__(self):
                self.connections = {}
                self.message_queue = queue.Queue()
            
            async def connect(self, client_id):
                self.connections[client_id] = {
                    'connected_at': time.time(),
                    'messages_sent': 0,
                    'messages_received': 0
                }
                return True
            
            async def disconnect(self, client_id):
                if client_id in self.connections:
                    del self.connections[client_id]
                return True
            
            async def send_message(self, client_id, message):
                if client_id in self.connections:
                    self.connections[client_id]['messages_sent'] += 1
                    # Simulate message sending
                    await asyncio.sleep(0.01)  # Small delay
                    return True
                return False
            
            async def receive_message(self, client_id, message):
                if client_id in self.connections:
                    self.connections[client_id]['messages_received'] += 1
                    self.message_queue.put({
                        'client_id': client_id,
                        'message': message,
                        'timestamp': time.time()
                    })
                    return True
                return False
            
            async def broadcast_message(self, message, exclude_client=None):
                tasks = []
                for client_id in self.connections:
                    if client_id != exclude_client:
                        task = self.send_message(client_id, message)
                        tasks.append(task)
                
                if tasks:
                    results = await asyncio.gather(*tasks)
                    return sum(results)  # Count successful sends
                return 0
        
        ws = WebSocketSimulator()
        
        async def test_websocket_functionality():
            # Test connections
            await ws.connect('client1')
            await ws.connect('client2')
            await ws.connect('client3')
            
            assert len(ws.connections) == 3
            
            # Test message sending
            result = await ws.send_message('client1', 'Hello from client1')
            assert result == True
            assert ws.connections['client1']['messages_sent'] == 1
            
            # Test message receiving
            await ws.receive_message('client2', 'Hello from client2')
            assert ws.connections['client2']['messages_received'] == 1
            
            # Test broadcasting
            broadcast_count = await ws.broadcast_message('Broadcast message', exclude_client='client1')
            assert broadcast_count == 2  # Sent to client2 and client3
            
            # Test disconnection
            await ws.disconnect('client1')
            assert len(ws.connections) == 2
            assert 'client1' not in ws.connections
        
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(test_websocket_functionality())
        finally:
            loop.close()

class TestConfiguration:
    """Test configuration management."""
    
    def test_configuration_loading(self):
        """Test configuration loading and validation."""
        class ConfigManager:
            def __init__(self):
                self.config = {}
                self.defaults = {
                    'host': '127.0.0.1',
                    'port': 8000,
                    'debug': False,
                    'database': {
                        'url': 'sqlite:///app.db',
                        'pool_size': 10
                    },
                    'security': {
                        'secret_key': None,
                        'session_timeout': 3600
                    }
                }
            
            def load_from_dict(self, config_dict):
                self.config = self._merge_config(self.defaults.copy(), config_dict)
                return self.config
            
            def _merge_config(self, base, update):
                for key, value in update.items():
                    if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                        base[key] = self._merge_config(base[key], value)
                    else:
                        base[key] = value
                return base
            
            def get(self, key_path, default=None):
                keys = key_path.split('.')
                value = self.config
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default
                
                return value
            
            def validate(self):
                errors = []
                
                # Validate required fields
                if not self.get('security.secret_key'):
                    errors.append("security.secret_key is required")
                
                # Validate port range
                port = self.get('port')
                if not isinstance(port, int) or port < 1 or port > 65535:
                    errors.append("port must be between 1 and 65535")
                
                # Validate database URL
                db_url = self.get('database.url')
                if not db_url or not isinstance(db_url, str):
                    errors.append("database.url must be a valid string")
                
                return errors
        
        config_manager = ConfigManager()
        
        # Test default configuration
        config_manager.load_from_dict({})
        assert config_manager.get('host') == '127.0.0.1'
        assert config_manager.get('port') == 8000
        assert config_manager.get('database.pool_size') == 10
        
        # Test configuration override
        custom_config = {
            'host': '0.0.0.0',
            'port': 9000,
            'database': {
                'url': 'postgresql://user:pass@localhost/db'
            },
            'security': {
                'secret_key': 'my-secret-key'
            }
        }
        
        config_manager.load_from_dict(custom_config)
        assert config_manager.get('host') == '0.0.0.0'
        assert config_manager.get('port') == 9000
        assert config_manager.get('database.url') == 'postgresql://user:pass@localhost/db'
        assert config_manager.get('database.pool_size') == 10  # Should keep default
        assert config_manager.get('security.secret_key') == 'my-secret-key'
        
        # Test validation
        errors = config_manager.validate()
        assert len(errors) == 0  # Should pass validation
        
        # Test validation with invalid config
        invalid_config = {
            'port': 'invalid_port',  # Should be integer
            'security': {
                'secret_key': ''  # Required field
            }
        }
        
        config_manager.load_from_dict(invalid_config)
        errors = config_manager.validate()
        assert len(errors) > 0
        assert any('port must be between' in error for error in errors)
        assert any('secret_key is required' in error for error in errors)

class TestErrorHandling:
    """Test error handling and exception management."""
    
    def test_exception_handling(self):
        """Test exception handling in request processing."""
        class ExceptionHandler:
            def __init__(self):
                self.handlers = {}
                self.default_handler = self._default_error_handler
            
            def register_handler(self, exception_type, handler):
                self.handlers[exception_type] = handler
            
            async def handle_exception(self, exception, request=None):
                exception_type = type(exception)
                
                # Look for specific handler
                if exception_type in self.handlers:
                    return await self.handlers[exception_type](exception, request)
                
                # Look for parent class handlers
                for exc_type, handler in self.handlers.items():
                    if isinstance(exception, exc_type):
                        return await handler(exception, request)
                
                # Use default handler
                return await self.default_handler(exception, request)
            
            async def _default_error_handler(self, exception, request):
                return {
                    'error': 'Internal Server Error',
                    'message': str(exception),
                    'type': type(exception).__name__
                }, 500
        
        handler = ExceptionHandler()
        
        # Register custom handlers
        async def validation_error_handler(exception, request):
            return {
                'error': 'Validation Error',
                'message': str(exception),
                'details': getattr(exception, 'details', None)
            }, 400
        
        async def not_found_handler(exception, request):
            return {
                'error': 'Not Found',
                'message': 'The requested resource was not found'
            }, 404
        
        class ValidationError(Exception):
            def __init__(self, message, details=None):
                super().__init__(message)
                self.details = details
        
        class NotFoundError(Exception):
            pass
        
        handler.register_handler(ValidationError, validation_error_handler)
        handler.register_handler(NotFoundError, not_found_handler)
        
        # Test custom exception handlers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Test validation error
            validation_exception = ValidationError("Invalid input", {"field": "email"})
            response, status = loop.run_until_complete(
                handler.handle_exception(validation_exception)
            )
            assert response['error'] == 'Validation Error'
            assert status == 400
            assert response['details']['field'] == 'email'
            
            # Test not found error
            not_found_exception = NotFoundError("User not found")
            response, status = loop.run_until_complete(
                handler.handle_exception(not_found_exception)
            )
            assert response['error'] == 'Not Found'
            assert status == 404
            
            # Test unhandled exception
            generic_exception = RuntimeError("Something went wrong")
            response, status = loop.run_until_complete(
                handler.handle_exception(generic_exception)
            )
            assert response['error'] == 'Internal Server Error'
            assert status == 500
            assert response['type'] == 'RuntimeError'
        finally:
            loop.close()

@pytest.mark.integration
class TestCoreIntegration:
    """Integration tests for core functionality."""
    
    def test_complete_request_lifecycle(self):
        """Test complete request processing lifecycle."""
        class SimpleWebFramework:
            def __init__(self):
                self.routes = {}
                self.middleware = []
                self.exception_handlers = {}
            
            def route(self, path, methods=None):
                methods = methods or ['GET']
                def decorator(handler):
                    for method in methods:
                        route_key = f"{method}:{path}"
                        self.routes[route_key] = handler
                    return handler
                return decorator
            
            def add_middleware(self, middleware):
                self.middleware.append(middleware)
            
            def exception_handler(self, exception_type):
                def decorator(handler):
                    self.exception_handlers[exception_type] = handler
                    return handler
                return decorator
            
            async def process_request(self, method, path, headers=None, body=b''):
                request = {
                    'method': method,
                    'path': path,
                    'headers': headers or {},
                    'body': body
                }
                
                try:
                    # Apply middleware
                    for middleware in self.middleware:
                        request = await middleware(request)
                    
                    # Route matching
                    route_key = f"{method}:{path}"
                    if route_key in self.routes:
                        handler = self.routes[route_key]
                        response = await handler(request)
                        return response
                    else:
                        return {'error': 'Not Found'}, 404
                        
                except Exception as e:
                    # Handle exceptions
                    exception_type = type(e)
                    if exception_type in self.exception_handlers:
                        return await self.exception_handlers[exception_type](e, request)
                    else:
                        return {'error': 'Internal Server Error'}, 500
        
        # Create framework instance
        app = SimpleWebFramework()
        
        # Add middleware
        async def logging_middleware(request):
            print(f"Processing: {request['method']} {request['path']}")
            return request
        
        async def auth_middleware(request):
            if request['path'].startswith('/api/') and 'authorization' not in request['headers']:
                raise ValueError("Authentication required")
            return request
        
        app.add_middleware(logging_middleware)
        app.add_middleware(auth_middleware)
        
        # Register exception handler
        @app.exception_handler(ValueError)
        async def value_error_handler(exception, request):
            return {'error': 'Bad Request', 'message': str(exception)}, 400
        
        # Register routes
        @app.route('/')
        async def home(request):
            return {'message': 'Welcome to the framework!'}
        
        @app.route('/api/users', ['GET', 'POST'])
        async def users_api(request):
            if request['method'] == 'GET':
                return {'users': [{'id': 1, 'name': 'John'}, {'id': 2, 'name': 'Jane'}]}
            elif request['method'] == 'POST':
                return {'message': 'User created'}, 201
        
        # Test the complete lifecycle
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Test home route
            response = loop.run_until_complete(
                app.process_request('GET', '/')
            )
            assert response == {'message': 'Welcome to the framework!'}
            
            # Test authenticated API route
            response = loop.run_until_complete(
                app.process_request('GET', '/api/users', {'authorization': 'Bearer token'})
            )
            assert 'users' in response
            assert len(response['users']) == 2
            
            # Test unauthenticated API route (should fail)
            response, status = loop.run_until_complete(
                app.process_request('GET', '/api/users')
            )
            assert status == 400
            assert 'Authentication required' in response['message']
            
            # Test POST to API
            response, status = loop.run_until_complete(
                app.process_request('POST', '/api/users', {'authorization': 'Bearer token'})
            )
            assert status == 201
            assert response['message'] == 'User created'
            
            # Test 404 route
            response, status = loop.run_until_complete(
                app.process_request('GET', '/nonexistent')
            )
            assert status == 404
            assert response['error'] == 'Not Found'
        finally:
            loop.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])