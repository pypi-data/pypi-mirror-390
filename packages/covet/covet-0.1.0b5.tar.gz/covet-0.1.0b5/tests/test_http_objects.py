"""
Comprehensive tests for CovetPy HTTP Request and Response objects
================================================================

This test suite demonstrates all features of the production-grade HTTP objects
including lazy parsing, async support, file uploads, compression, caching,
sessions, and more.
"""

import asyncio
import gzip
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest

# Import our HTTP objects
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

from covet.core.http_objects import (
    Request,
    Response,
    StreamingResponse,
    FileResponse,
    Cookie,
    UploadFile,
    CaseInsensitiveDict,
    MemorySessionInterface,
    LazyQueryParser,
    MultipartParser,
    json_response,
    html_response,
    text_response,
    redirect_response,
    error_response,
    HTTPStatus,
)


class TestCaseInsensitiveDict:
    """Test case-insensitive dictionary for headers"""
    
    def test_basic_operations(self):
        headers = CaseInsensitiveDict()
        headers['Content-Type'] = 'application/json'
        
        assert headers['content-type'] == 'application/json'
        assert headers['CONTENT-TYPE'] == 'application/json'
        assert 'content-type' in headers
        assert 'Content-Type' in headers
        
    def test_update_same_key(self):
        headers = CaseInsensitiveDict()
        headers['content-type'] = 'text/plain'
        headers['Content-Type'] = 'application/json'
        
        # Should have only one entry
        assert len(headers) == 1
        assert headers['content-type'] == 'application/json'
        
    def test_initialization_with_data(self):
        data = {'Content-Type': 'application/json', 'Accept': 'text/html'}
        headers = CaseInsensitiveDict(data)
        
        assert headers['content-type'] == 'application/json'
        assert headers['accept'] == 'text/html'
        
    def test_get_method(self):
        headers = CaseInsensitiveDict({'Content-Type': 'application/json'})
        
        assert headers.get('content-type') == 'application/json'
        assert headers.get('accept', 'default') == 'default'
        
    def test_pop_method(self):
        headers = CaseInsensitiveDict({'Content-Type': 'application/json'})
        
        value = headers.pop('content-type')
        assert value == 'application/json'
        assert 'content-type' not in headers
        
        default_value = headers.pop('accept', 'default')
        assert default_value == 'default'


class TestLazyQueryParser:
    """Test lazy query string parsing"""
    
    def test_basic_parsing(self):
        parser = LazyQueryParser('name=john&age=25&city=NYC')
        
        assert parser.get('name') == 'john'
        assert parser.get('age') == '25'
        assert parser.get('city') == 'NYC'
        assert parser.get('missing') is None
        
    def test_multiple_values(self):
        parser = LazyQueryParser('tags=python&tags=web&tags=api')
        
        assert parser.get('tags') == 'python'  # First value
        assert parser.get_list('tags') == ['python', 'web', 'api']
        
    def test_empty_values(self):
        parser = LazyQueryParser('empty=&name=john')
        
        assert parser.get('empty') == ''
        assert parser.get('name') == 'john'
        
    def test_iteration(self):
        parser = LazyQueryParser('a=1&b=2&a=3')
        items = list(parser.items())
        
        assert ('a', '1') in items
        assert ('a', '3') in items
        assert ('b', '2') in items
        
    def test_contains(self):
        parser = LazyQueryParser('name=john&age=25')
        
        assert 'name' in parser
        assert 'age' in parser
        assert 'missing' not in parser


class TestCookie:
    """Test HTTP Cookie functionality"""
    
    def test_basic_cookie(self):
        cookie = Cookie('session_id', 'abc123')
        header = cookie.to_header()
        
        assert header == 'session_id=abc123'
        
    def test_cookie_with_attributes(self):
        cookie = Cookie(
            'session_id', 
            'abc123',
            max_age=3600,
            path='/admin',
            domain='.example.com',
            secure=True,
            http_only=True,
            same_site='Strict'
        )
        header = cookie.to_header()
        
        assert 'session_id=abc123' in header
        assert 'Max-Age=3600' in header
        assert 'Path=/admin' in header
        assert 'Domain=.example.com' in header
        assert 'Secure' in header
        assert 'HttpOnly' in header
        assert 'SameSite=Strict' in header
        
    def test_cookie_from_string(self):
        cookie_str = 'session_id=abc123; Max-Age=3600; Path=/; Secure; HttpOnly'
        cookie = Cookie.from_string(cookie_str)
        
        assert cookie.name == 'session_id'
        assert cookie.value == 'abc123'
        assert cookie.max_age == 3600
        assert cookie.path == '/'
        assert cookie.secure is True
        assert cookie.http_only is True


class TestUploadFile:
    """Test file upload functionality"""
    
    @pytest.mark.asyncio
    async def test_basic_file_operations(self):
        upload = UploadFile(filename='test.txt', content_type='text/plain')
        
        # Write some data
        data = b'Hello, World!'
        await upload.write(data)
        
        # Read it back
        content = await upload.read()
        assert content == data
        assert upload.size == len(data)
        
    @pytest.mark.asyncio
    async def test_save_file(self):
        upload = UploadFile(filename='test.txt', content_type='text/plain')
        data = b'Test file content'
        await upload.write(data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            await upload.save(tmp_path)
            
            # Verify file was saved
            with open(tmp_path, 'rb') as f:
                saved_content = f.read()
            assert saved_content == data
        finally:
            os.unlink(tmp_path)
            
    @pytest.mark.asyncio
    async def test_partial_read(self):
        upload = UploadFile(filename='test.txt')
        data = b'Hello, World! This is a longer message.'
        await upload.write(data)
        
        # Read first 5 bytes
        partial = await upload.read(5)
        assert partial == b'Hello'


class TestMultipartParser:
    """Test multipart form data parsing"""
    
    @pytest.mark.asyncio
    async def test_simple_form_fields(self):
        boundary = 'boundary123'
        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="name"\r\n'
            '\r\n'
            'John Doe\r\n'
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="email"\r\n'
            '\r\n'
            'john@example.com\r\n'
            f'--{boundary}--\r\n'
        ).encode()
        
        parser = MultipartParser(body, boundary)
        form_data = await parser.parse()
        
        assert form_data['name'] == 'John Doe'
        assert form_data['email'] == 'john@example.com'
        
    @pytest.mark.asyncio
    async def test_file_upload(self):
        boundary = 'boundary123'
        file_content = b'Binary file content'
        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="file"; filename="test.bin"\r\n'
            'Content-Type: application/octet-stream\r\n'
            '\r\n'
        ).encode() + file_content + f'\r\n--{boundary}--\r\n'.encode()
        
        parser = MultipartParser(body, boundary)
        form_data = await parser.parse()
        
        assert 'file' in form_data
        upload_file = form_data['file']
        assert isinstance(upload_file, UploadFile)
        assert upload_file.filename == 'test.bin'
        assert upload_file.content_type == 'application/octet-stream'
        
        content = await upload_file.read()
        assert content == file_content


class TestRequest:
    """Test Request object functionality"""
    
    def test_basic_request_creation(self):
        request = Request(
            method='POST',
            url='/api/users?page=1&limit=10',
            headers={'Content-Type': 'application/json'},
            body=b'{"name": "John"}',
            client_addr=('127.0.0.1', 8080)
        )
        
        assert request.method == 'POST'
        assert request.path == '/api/users'
        assert request.query_params.get('page') == '1'
        assert request.query_params.get('limit') == '10'
        assert request.content_type == 'application/json'
        assert request.remote_addr == '127.0.0.1'
        
    def test_header_access(self):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer token123',
            'User-Agent': 'TestClient/1.0'
        }
        request = Request(headers=headers)
        
        assert request.get_header('content-type') == 'application/json'
        assert request.get_header('AUTHORIZATION') == 'Bearer token123'
        assert request.user_agent == 'TestClient/1.0'
        assert request.has_header('authorization')
        assert not request.has_header('missing-header')
        
    def test_cookie_parsing(self):
        request = Request(headers={
            'Cookie': 'session_id=abc123; user_pref=dark_mode; lang=en'
        })
        
        cookies = request.cookies
        assert cookies['session_id'] == 'abc123'
        assert cookies['user_pref'] == 'dark_mode'
        assert cookies['lang'] == 'en'
        
    @pytest.mark.asyncio
    async def test_json_body(self):
        data = {'name': 'John', 'age': 30}
        body = json.dumps(data).encode()
        
        request = Request(
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=body
        )
        
        assert request.is_json()
        parsed_data = await request.json()
        assert parsed_data == data
        
    @pytest.mark.asyncio
    async def test_form_body(self):
        form_data = 'name=John&age=30&city=NYC'
        
        request = Request(
            method='POST',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body=form_data.encode()
        )
        
        assert request.is_form()
        parsed_form = await request.form()
        assert parsed_form['name'] == 'John'
        assert parsed_form['age'] == '30'
        assert parsed_form['city'] == 'NYC'
        
    @pytest.mark.asyncio
    async def test_text_body(self):
        text_content = 'Plain text content'
        
        request = Request(
            method='POST',
            headers={'Content-Type': 'text/plain'},
            body=text_content.encode()
        )
        
        text = await request.text()
        assert text == text_content
        
    def test_content_negotiation(self):
        request = Request(headers={
            'Accept': 'application/json, text/html;q=0.9, */*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8'
        })
        
        assert request.accepts('application/json')
        assert request.accepts('text/html')
        assert request.accepts_encoding('gzip')
        assert request.accepts_encoding('br')
        
        preferred = request.prefers_language(['es', 'en', 'fr'])
        assert preferred == 'en'
        
    def test_websocket_detection(self):
        request = Request(headers={
            'Upgrade': 'websocket',
            'Connection': 'Upgrade',
            'Sec-WebSocket-Key': 'x3JJHMbDL1EzLkh9GBhXDw==',
            'Sec-WebSocket-Version': '13'
        })
        
        assert request.is_websocket()
        
    @pytest.mark.asyncio
    async def test_session_handling(self):
        session_interface = MemorySessionInterface()
        request = Request(session_interface=session_interface)
        
        # Get session (should be empty initially)
        session = await request.session()
        assert session == {}
        
        # Add data to session
        session['user_id'] = 123
        session['username'] = 'john'
        
        # Save session
        session_id = await request.save_session()
        assert session_id is not None
        
        # Create new request with same session ID
        request2 = Request(
            headers={'Cookie': f'session_id={session_id}'},
            session_interface=session_interface
        )
        
        session2 = await request2.session()
        assert session2['user_id'] == 123
        assert session2['username'] == 'john'
        
    def test_forwarded_headers(self):
        request = Request(
            headers={
                'X-Forwarded-For': '203.0.113.195, 70.41.3.18, 150.172.238.178',
                'X-Real-IP': '203.0.113.195'
            },
            client_addr=('192.168.1.1', 8080)
        )
        
        # Should use X-Forwarded-For first
        assert request.remote_addr == '203.0.113.195'


class TestResponse:
    """Test Response object functionality"""
    
    def test_basic_response_creation(self):
        response = Response(
            content='Hello, World!',
            status_code=200,
            headers={'Custom-Header': 'value'}
        )
        
        assert response.status_code == 200
        assert response.headers['custom-header'] == 'value'
        assert response.headers['content-type'] == 'text/plain; charset=utf-8'
        assert response.is_success()
        
    def test_json_response_auto_detection(self):
        data = {'message': 'Hello', 'status': 'success'}
        response = Response(content=data)
        
        assert response.media_type == 'application/json'
        assert response.headers['content-type'] == 'application/json; charset=utf-8'
        
        body = response.get_body_bytes()
        parsed_data = json.loads(body.decode())
        assert parsed_data == data
        
    def test_status_code_helpers(self):
        assert Response(status_code=200).is_success()
        assert Response(status_code=201).is_success()
        assert Response(status_code=302).is_redirect()
        assert Response(status_code=404).is_client_error()
        assert Response(status_code=500).is_server_error()
        assert Response(status_code=100).is_informational()
        
    def test_cookie_handling(self):
        response = Response(content='Hello')
        
        response.set_cookie(
            'session_id',
            'abc123',
            max_age=3600,
            secure=True,
            http_only=True
        )
        
        response.set_cookie('user_pref', 'dark_mode')
        
        assert 'session_id' in response.cookies
        assert 'user_pref' in response.cookies
        assert response.cookies['session_id'].secure is True
        assert response.cookies['session_id'].http_only is True
        
    def test_cookie_deletion(self):
        response = Response(content='Hello')
        response.set_cookie('temp_cookie', 'value')
        
        response.delete_cookie('temp_cookie')
        
        deleted_cookie = response.cookies['temp_cookie']
        assert deleted_cookie.value == ''
        assert deleted_cookie.max_age == 0
        
    def test_compression(self):
        # Create response with large content
        large_content = 'x' * 2000  # Large enough to trigger compression
        response = Response(content=large_content)
        
        # Test gzip compression
        response.compress('gzip')
        
        compressed_body = response.get_compressed_body()
        assert len(compressed_body) < len(large_content.encode())
        assert response.headers.get('content-encoding') == 'gzip'
        assert 'vary' in response.headers
        
        # Verify decompression works
        decompressed = gzip.decompress(compressed_body).decode()
        assert decompressed == large_content
        
    def test_etag_generation(self):
        response = Response(content='Hello, World!')
        
        etag = response.generate_etag()
        assert etag is not None
        assert response.headers['etag'] == f'"{etag}"'
        
        # Same content should generate same ETag
        response2 = Response(content='Hello, World!')
        etag2 = response2.generate_etag()
        assert etag == etag2
        
    def test_cache_control(self):
        response = Response(content='Hello')
        
        response.set_cache_control(
            max_age=3600,
            public=True,
            must_revalidate=True
        )
        
        cache_control = response.headers['cache-control']
        assert 'max-age=3600' in cache_control
        assert 'public' in cache_control
        assert 'must-revalidate' in cache_control
        
    def test_no_cache_response(self):
        response = Response(content='Sensitive data')
        
        response.set_cache_control(
            no_cache=True,
            no_store=True,
            private=True
        )
        
        cache_control = response.headers['cache-control']
        assert 'no-cache' in cache_control
        assert 'no-store' in cache_control
        assert 'private' in cache_control


class TestFileResponse:
    """Test file serving functionality"""
    
    def test_file_response_creation(self):
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Test file content')
            temp_path = f.name
        
        try:
            response = FileResponse(temp_path, filename='download.txt')
            
            assert response.status_code == 200
            assert 'content-length' in response.headers
            assert 'last-modified' in response.headers
            assert 'etag' in response.headers
            assert 'attachment; filename="download.txt"' in response.headers['content-disposition']
            
        finally:
            os.unlink(temp_path)
            
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            FileResponse('/nonexistent/file.txt')
            
    def test_media_type_detection(self):
        # Create temporary files with different extensions
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            f.write(b'{"test": true}')
            json_path = f.name
            
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(b'<html><body>Test</body></html>')
            html_path = f.name
        
        try:
            json_response = FileResponse(json_path)
            html_response = FileResponse(html_path)
            
            assert 'application/json' in json_response.media_type
            assert 'text/html' in html_response.media_type
            
        finally:
            os.unlink(json_path)
            os.unlink(html_path)


class TestStreamingResponse:
    """Test streaming response functionality"""
    
    @pytest.mark.asyncio
    async def test_streaming_response(self):
        async def generate_chunks():
            for i in range(3):
                yield f"chunk {i}\n".encode()
        
        response = StreamingResponse(
            content=generate_chunks(),
            media_type="text/plain"
        )
        
        assert response.status_code == 200
        assert response.headers['transfer-encoding'] == 'chunked'
        assert response.media_type == "text/plain"


class TestConvenienceFunctions:
    """Test convenience response functions"""
    
    def test_json_response_function(self):
        data = {'message': 'success', 'data': [1, 2, 3]}
        response = json_response(data, status_code=201)
        
        assert response.status_code == 201
        assert response.media_type == 'application/json'
        
        body = response.get_body_bytes()
        parsed_data = json.loads(body.decode())
        assert parsed_data == data
        
    def test_html_response_function(self):
        html_content = '<html><body><h1>Hello</h1></body></html>'
        response = html_response(html_content)
        
        assert response.status_code == 200
        assert response.media_type == 'text/html'
        assert response.get_body_bytes().decode() == html_content
        
    def test_text_response_function(self):
        text_content = 'Plain text message'
        response = text_response(text_content, status_code=202)
        
        assert response.status_code == 202
        assert response.media_type == 'text/plain'
        assert response.get_body_bytes().decode() == text_content
        
    def test_redirect_response_function(self):
        redirect_url = 'https://example.com/new-location'
        response = redirect_response(redirect_url, status_code=301)
        
        assert response.status_code == 301
        assert response.headers['location'] == redirect_url
        
    def test_error_response_function(self):
        error_message = 'Something went wrong'
        response = error_response(error_message, status_code=400)
        
        assert response.status_code == 400
        assert response.media_type == 'application/json'
        
        body = response.get_body_bytes()
        error_data = json.loads(body.decode())
        assert error_data['error'] == error_message
        assert error_data['status'] == 400


class TestHTTPStatus:
    """Test HTTP status constants"""
    
    def test_status_constants(self):
        assert HTTPStatus.OK == 200
        assert HTTPStatus.CREATED == 201
        assert HTTPStatus.NOT_FOUND == 404
        assert HTTPStatus.INTERNAL_SERVER_ERROR == 500
        assert HTTPStatus.TEMPORARY_REDIRECT == 307
        assert HTTPStatus.UNPROCESSABLE_ENTITY == 422


class TestPerformanceFeatures:
    """Test performance and optimization features"""
    
    def test_lazy_query_parsing(self):
        # Query parser should not parse until accessed
        parser = LazyQueryParser('a=1&b=2&c=3&d=4&e=5')
        
        # Access only one parameter
        value = parser.get('a')
        assert value == '1'
        
        # Internal parsed data should be cached
        assert parser._parsed is not None
        
    def test_header_case_insensitive_performance(self):
        # Test that repeated access uses cached lowercase keys
        headers = CaseInsensitiveDict()
        headers['Content-Type'] = 'application/json'
        
        # Multiple accesses should be efficient
        for _ in range(10):
            assert headers['content-type'] == 'application/json'
            assert headers['Content-Type'] == 'application/json'
            assert headers['CONTENT-TYPE'] == 'application/json'
            
    def test_response_body_caching(self):
        # Response body should be cached after first access
        response = Response(content={'large': 'data' * 100})
        
        # First access
        body1 = response.get_body_bytes()
        
        # Second access should return cached version
        body2 = response.get_body_bytes()
        
        assert body1 is body2  # Same object reference
        
    @pytest.mark.asyncio
    async def test_request_body_caching(self):
        # Request body parsing should be cached
        data = {'test': 'data'}
        body = json.dumps(data).encode()
        
        request = Request(
            method='POST',
            headers={'Content-Type': 'application/json'},
            body=body
        )
        
        # First JSON parse
        json1 = await request.json()
        
        # Second JSON parse should return cached result
        json2 = await request.json()
        
        assert json1 == json2
        assert request._json_cache is not None


class TestIntegrationScenarios:
    """Test real-world integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_complete_request_response_cycle(self):
        # Simulate a complete HTTP request/response cycle
        
        # 1. Create request with JSON payload
        request_data = {
            'user_id': 123,
            'action': 'update_profile',
            'data': {'name': 'John Doe', 'email': 'john@example.com'}
        }
        
        request = Request(
            method='POST',
            url='/api/users/123?format=json&include=profile',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer token123',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate',
                'User-Agent': 'TestClient/1.0',
                'Cookie': 'session_id=abc123; preferences={}',
            },
            body=json.dumps(request_data).encode(),
            client_addr=('192.168.1.100', 12345)
        )
        
        # 2. Process request
        assert request.method == 'POST'
        assert request.path == '/api/users/123'
        assert request.query_params.get('format') == 'json'
        assert request.query_params.get('include') == 'profile'
        assert request.is_json()
        assert request.accepts('application/json')
        assert request.accepts_encoding('gzip')
        
        # Parse request data
        parsed_data = await request.json()
        assert parsed_data == request_data
        
        # Check authorization
        auth_header = request.get_header('authorization')
        assert auth_header == 'Bearer token123'
        
        # 3. Create response
        response_data = {
            'success': True,
            'user': {
                'id': 123,
                'name': 'John Doe',
                'email': 'john@example.com',
                'profile': {'updated_at': '2023-01-01T00:00:00Z'}
            }
        }
        
        response = Response(
            content=response_data,
            status_code=200,
            headers={'X-API-Version': '1.0'}
        )
        
        # 4. Configure response
        response.set_cookie(
            'last_action',
            'profile_update',
            max_age=3600,
            secure=True,
            http_only=True
        )
        
        response.set_cache_control(max_age=300, public=True)
        response.generate_etag()
        
        # Compress if client supports it
        if request.accepts_encoding('gzip'):
            response.compress('gzip')
        
        # 5. Verify response
        assert response.is_success()
        assert response.media_type == 'application/json'
        assert 'last_action' in response.cookies
        assert 'cache-control' in response.headers
        assert 'etag' in response.headers
        
        if request.accepts_encoding('gzip'):
            assert response.headers.get('content-encoding') == 'gzip'
        
    @pytest.mark.asyncio
    async def test_file_upload_scenario(self):
        # Simulate file upload with form data
        
        boundary = 'boundary123456789'
        file_content = b'Binary file content for testing'
        
        # Create multipart body
        body = (
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="title"\r\n'
            '\r\n'
            'Test Document\r\n'
            f'--{boundary}\r\n'
            'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n'
            'Content-Type: application/pdf\r\n'
            '\r\n'
        ).encode() + file_content + f'\r\n--{boundary}--\r\n'.encode()
        
        request = Request(
            method='POST',
            url='/api/upload',
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary}',
                'Content-Length': str(len(body))
            },
            body=body
        )
        
        # Process upload
        assert request.is_multipart()
        form_data = await request.form()
        
        assert 'title' in form_data
        assert form_data['title'] == 'Test Document'
        
        assert 'file' in form_data
        uploaded_file = form_data['file']
        assert isinstance(uploaded_file, UploadFile)
        assert uploaded_file.filename == 'test.pdf'
        assert uploaded_file.content_type == 'application/pdf'
        
        # Read file content
        file_data = await uploaded_file.read()
        assert file_data == file_content
        
        # Create success response
        response = json_response({
            'success': True,
            'file_id': 'file_123',
            'filename': uploaded_file.filename,
            'size': len(file_data)
        }, status_code=201)
        
        assert response.status_code == 201
        assert response.is_success()


if __name__ == '__main__':
    # Run tests with asyncio support
    pytest.main([__file__, '-v', '--tb=short'])