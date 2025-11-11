#!/usr/bin/env python3
"""
CovetPy Hello World HTTP Server
A minimal HTTP server demonstrating CovetPy core functionality on localhost:8000
"""

import asyncio
import json
import socket
import time
from pathlib import Path
import sys

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import core components
import importlib.util

def load_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Load modules directly from file paths
base_path = Path(__file__).parent / "src" / "covet" / "core"
http_module = load_module_from_path("covet_http", base_path / "http.py")
routing_module = load_module_from_path("covet_routing", base_path / "routing.py") 
middleware_module = load_module_from_path("covet_middleware", base_path / "middleware.py")

# Import the classes we need
Request = http_module.Request
Response = http_module.Response
json_response = http_module.json_response
error_response = http_module.error_response
CovetRouter = routing_module.CovetRouter
MiddlewareStack = middleware_module.MiddlewareStack
Middleware = middleware_module.Middleware


class HelloWorldApp:
    """Simple Hello World application for Sprint 1."""
    
    def __init__(self):
        self.router = CovetRouter()
        self.middleware_stack = MiddlewareStack()
        self._setup_routes()
        self._setup_middleware()
    
    def _setup_routes(self):
        """Setup basic routes."""
        
        async def hello_world(request: Request) -> Response:
            return json_response({
                "message": "Hello, World!",
                "framework": "CovetPy",
                "sprint": 1,
                "status": "success",
                "timestamp": time.time()
            })
        
        async def health(request: Request) -> Response:
            return json_response({
                "status": "healthy",
                "framework": "CovetPy",
                "version": "1.0.0-sprint1"
            })
        
        async def echo(request: Request) -> Response:
            text = request.path_params.get("text", "nothing")
            return json_response({
                "echo": text,
                "method": request.method,
                "path": request.path
            })
        
        # Add routes
        self.router.add_route("/", hello_world, ["GET"])
        self.router.add_route("/health", health, ["GET"])
        self.router.add_route("/echo/{text}", echo, ["GET"])
    
    def _setup_middleware(self):
        """Setup basic middleware."""
        
        class RequestLoggingMiddleware(Middleware):
            async def process_request(self, request):
                print(f"[{time.strftime('%H:%M:%S')}] {request.method} {request.path}")
                return request
                
            async def process_response(self, request, response):
                print(f"[{time.strftime('%H:%M:%S')}] {response.status_code} - {request.path}")
                return response
        
        class HeaderMiddleware(Middleware):
            async def process_request(self, request):
                return request
                
            async def process_response(self, request, response):
                response.headers.update({
                    "Server": "CovetPy/1.0.0-sprint1",
                    "X-Framework": "CovetPy",
                    "X-Sprint": "1"
                })
                return response
        
        self.middleware_stack.add(RequestLoggingMiddleware())
        self.middleware_stack.add(HeaderMiddleware())
    
    async def handle_request(self, request: Request) -> Response:
        """Handle a request through the application."""
        
        # Process request through middleware
        request = await self.middleware_stack.process_request(request)
        
        # Try to find a matching route
        match = self.router.match_route(request.path, request.method)
        
        if match:
            # Set path parameters on the request
            request.path_params = match.params
            # Call the handler
            response = await match.handler(request)
        else:
            # Return 404
            response = error_response(
                f"Route not found: {request.method} {request.path}",
                404
            )
        
        # Process response through middleware
        response = await self.middleware_stack.process_response(request, response)
        
        return response


class SimpleHTTPServer:
    """Simple HTTP server implementation."""
    
    def __init__(self, app, host="127.0.0.1", port=8000):
        self.app = app
        self.host = host
        self.port = port
        self.running = False
    
    def parse_http_request(self, data: bytes) -> Request:
        """Parse raw HTTP request data into a Request object."""
        lines = data.decode('utf-8', errors='ignore').split('\r\n')
        if not lines:
            raise ValueError("Empty request")
        
        # Parse request line
        request_line = lines[0].split(' ', 2)
        if len(request_line) < 2:
            raise ValueError("Invalid request line")
        
        method = request_line[0]
        path = request_line[1]
        
        # Parse headers
        headers = {}
        i = 1
        while i < len(lines) and lines[i].strip():
            if ':' in lines[i]:
                key, value = lines[i].split(':', 1)
                headers[key.strip().lower()] = value.strip()
            i += 1
        
        # Create request object
        return Request(
            method=method,
            url=path,
            headers=headers
        )
    
    def format_http_response(self, response: Response) -> bytes:
        """Format Response object into HTTP response bytes."""
        status_text = {
            200: "OK",
            404: "Not Found",
            500: "Internal Server Error"
        }.get(response.status_code, "Unknown")
        
        # Build response
        lines = [f"HTTP/1.1 {response.status_code} {status_text}"]
        
        # Add headers
        for key, value in response.headers.items():
            lines.append(f"{key}: {value}")
        
        # Add content-length
        content = response.get_content_bytes()
        lines.append(f"Content-Length: {len(content)}")
        lines.append("")  # Empty line before body
        
        # Join headers and add body
        header_bytes = '\r\n'.join(lines).encode('utf-8')
        return header_bytes + content
    
    async def handle_client(self, client_socket):
        """Handle a client connection."""
        try:
            # Receive data
            data = client_socket.recv(4096)
            if not data:
                return
            
            # Parse request
            try:
                request = self.parse_http_request(data)
            except Exception as e:
                # Send 400 Bad Request
                bad_response = error_response(f"Bad Request: {e}", 400)
                response_bytes = self.format_http_response(bad_response)
                client_socket.send(response_bytes)
                return
            
            # Handle request through app
            try:
                response = await self.app.handle_request(request)
            except Exception as e:
                # Send 500 Internal Server Error
                error_resp = error_response(f"Internal Server Error: {e}", 500)
                response_bytes = self.format_http_response(error_resp)
                client_socket.send(response_bytes)
                return
            
            # Send response
            response_bytes = self.format_http_response(response)
            client_socket.send(response_bytes)
            
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    async def start(self):
        """Start the HTTP server."""
        print(f"🚀 CovetPy HTTP Server starting...")
        print(f"📍 Listening on http://{self.host}:{self.port}")
        print("Press Ctrl+C to stop")
        print()
        
        # Create socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        server_socket.setblocking(False)
        
        self.running = True
        
        try:
            while self.running:
                try:
                    # Accept connection
                    client_socket, addr = await asyncio.get_event_loop().sock_accept(server_socket)
                    
                    # Handle client in background
                    asyncio.create_task(self.handle_client(client_socket))
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    print(f"Server error: {e}")
                    await asyncio.sleep(0.1)
        finally:
            server_socket.close()
            print("\n🛑 Server stopped")
    
    def stop(self):
        """Stop the server."""
        self.running = False


async def main():
    """Main function to run the server."""
    # Create app
    app = HelloWorldApp()
    
    # Create server
    server = SimpleHTTPServer(app, host="127.0.0.1", port=8000)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n🔴 Shutting down...")
        server.stop()


if __name__ == "__main__":
    asyncio.run(main())