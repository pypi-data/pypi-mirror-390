#!/usr/bin/env python3
"""
Minimal CovetPy Implementation
A truly working "Hello World" web framework
"""

import asyncio
import json
import urllib.parse
from typing import Any, Callable, Dict, List, Optional


class Request:
    """Simple HTTP Request object"""
    
    def __init__(self, method: str, path: str, headers: Dict[str, str], body: bytes, query_params: Dict[str, str]):
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params
        self.path_params = {}
        self._json_cache = None

    def json(self) -> Dict[str, Any]:
        """Parse request body as JSON"""
        if self._json_cache is None:
            try:
                self._json_cache = json.loads(self.body.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                self._json_cache = {}
        return self._json_cache

    def text(self) -> str:
        """Get request body as text"""
        return self.body.decode("utf-8")


class Response:
    """Simple HTTP Response object"""
    
    def __init__(self, content: Any, status: int = 200, headers: Optional[Dict[str, str]] = None, content_type: str = "text/html"):
        self.status = status
        self.headers = headers or {}
        self.content_type = content_type

        # Process content
        if isinstance(content, dict):
            self.body = json.dumps(content).encode("utf-8")
            self.content_type = "application/json"
        elif isinstance(content, str):
            self.body = content.encode("utf-8")
        elif isinstance(content, bytes):
            self.body = content
        else:
            self.body = str(content).encode("utf-8")

        # Set content type header
        self.headers["Content-Type"] = self.content_type
        self.headers["Content-Length"] = str(len(self.body))

    def to_bytes(self) -> bytes:
        """Convert response to HTTP bytes"""
        # Status line
        response = f"HTTP/1.1 {self.status} OK\r\n"

        # Headers
        for name, value in self.headers.items():
            response += f"{name}: {value}\r\n"

        # End of headers
        response += "\r\n"

        return response.encode("utf-8") + self.body


class Router:
    """Simple router implementation"""
    
    def __init__(self):
        self.routes: Dict[str, Dict[str, Callable]] = {}

    def add_route(self, method: str, path: str, handler: Callable):
        """Add route"""
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = handler

    def get(self, path: str):
        """Add GET route"""
        def decorator(handler):
            self.add_route("GET", path, handler)
            return handler
        return decorator

    def post(self, path: str):
        """Add POST route"""
        def decorator(handler):
            self.add_route("POST", path, handler)
            return handler
        return decorator

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming request"""
        # First try exact match
        if request.path in self.routes and request.method in self.routes[request.path]:
            handler = self.routes[request.path][request.method]

            # Call handler
            if asyncio.iscoroutinefunction(handler):
                return await handler(request)
            else:
                return handler(request)

        # Try path parameters
        for route_path, methods in self.routes.items():
            if request.method in methods:
                params = self._match_path_params(route_path, request.path)
                if params is not None:
                    request.path_params = params
                    handler = methods[request.method]
                    
                    # Call handler
                    if asyncio.iscoroutinefunction(handler):
                        return await handler(request)
                    else:
                        return handler(request)

        # 404 Not Found
        return Response("Not Found", status=404, content_type="text/plain")
    
    def _match_path_params(self, route_path: str, request_path: str) -> Optional[Dict[str, str]]:
        """Match path parameters like /users/{id}"""
        route_parts = route_path.split('/')
        request_parts = request_path.split('/')
        
        if len(route_parts) != len(request_parts):
            return None
        
        params = {}
        for route_part, request_part in zip(route_parts, request_parts):
            if route_part.startswith('{') and route_part.endswith('}'):
                # This is a parameter
                param_name = route_part[1:-1]
                params[param_name] = request_part
            elif route_part != request_part:
                # Static part doesn't match
                return None
        
        return params


class MinimalCovet:
    """Minimal CovetPy application"""
    
    def __init__(self):
        self.router = Router()

    # Route decorators
    def get(self, path: str):
        """Add GET route"""
        return self.router.get(path)

    def post(self, path: str):
        """Add POST route"""
        return self.router.post(path)

    # Response helpers
    def json_response(self, data: Dict[str, Any], status: int = 200) -> Response:
        """Create JSON response"""
        return Response(data, status=status)

    def text_response(self, text: str, status: int = 200) -> Response:
        """Create text response"""
        return Response(text, status=status, content_type="text/plain")

    def html_response(self, html: str, status: int = 200) -> Response:
        """Create HTML response"""
        return Response(html, status=status, content_type="text/html")

    async def _parse_request(self, data: bytes) -> Request:
        """Parse HTTP request from raw bytes"""
        try:
            # Split headers and body
            header_end = data.find(b"\r\n\r\n")
            if header_end == -1:
                raise ValueError("Invalid HTTP request")

            headers_data = data[:header_end].decode("utf-8")
            body = data[header_end + 4:]

            # Parse request line and headers
            lines = headers_data.split("\r\n")
            request_line = lines[0]
            method, path_query, version = request_line.split(" ", 2)

            # Parse path and query
            if "?" in path_query:
                path, query_string = path_query.split("?", 1)
                query_params = dict(urllib.parse.parse_qsl(query_string))
            else:
                path = path_query
                query_params = {}

            # Parse headers
            headers = {}
            for line in lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key.lower()] = value

            return Request(method, path, headers, body, query_params)

        except Exception as e:
            print(f"Failed to parse request: {e}")
            raise

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle client connection"""
        try:
            # Read request
            data = await reader.read(65536)  # 64KB max
            if not data:
                return

            # Parse request
            request = await self._parse_request(data)

            # Route request
            response = await self.router.handle_request(request)

            # Send response
            writer.write(response.to_bytes())
            await writer.drain()

        except Exception as e:
            # Send error response
            error_response = Response("Internal Server Error", status=500, content_type="text/plain")
            writer.write(error_response.to_bytes())
            await writer.drain()
            print(f"Request handling error: {e}")

        finally:
            writer.close()
            await writer.wait_closed()

    async def _run_server_async(self, host: str = "127.0.0.1", port: int = 8000):
        """Run async server"""
        server = await asyncio.start_server(self._handle_client, host, port)

        print(f"Minimal CovetPy server started on {host}:{port}")
        print(f"Visit http://{host}:{port} to test")

        async with server:
            await server.serve_forever()

    def run(self, host: str = "127.0.0.1", port: int = 8000):
        """Run the application"""
        try:
            asyncio.run(self._run_server_async(host, port))
        except KeyboardInterrupt:
            print("\nServer stopped")


def create_app() -> MinimalCovet:
    """Create minimal CovetPy application"""
    return MinimalCovet()


# Example usage
if __name__ == "__main__":
    app = create_app()

    @app.get("/")
    async def hello_world(request: Request) -> Response:
        return app.json_response({
            "message": "Hello World from Minimal CovetPy!",
            "framework": "CovetPy",
            "path": request.path,
            "method": request.method
        })

    @app.get("/health")
    async def health_check(request: Request) -> Response:
        return app.json_response({
            "status": "healthy",
            "message": "Minimal CovetPy is running!"
        })

    @app.post("/echo")
    async def echo(request: Request) -> Response:
        try:
            data = request.json()
            return app.json_response({
                "echo": data,
                "method": request.method,
                "path": request.path
            })
        except Exception:
            return app.json_response({
                "echo": request.text(),
                "method": request.method,
                "path": request.path
            })

    print("Starting Minimal CovetPy server...")
    app.run()