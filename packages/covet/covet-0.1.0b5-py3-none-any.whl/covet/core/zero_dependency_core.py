"""
Zero-Dependency Core Implementation
Pure Python web framework using ONLY standard library

This module provides the core CovetPy functionality with TRUE zero dependencies.
"""

import asyncio
import json
import logging
import os
import socket
import ssl
import sys
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

# Import our zero-dependency implementations
from ..database.zero_dependency_database import DatabaseConfig, ZeroDepDatabase
from ..http.client import HTTPClient, HTTPResponse
from ..security.zero_dependency_crypto import CryptoConfig, ZeroDepCrypto
from ..validation.zero_dependency_validation import ValidatedModel, ValidationError
from ..websocket.protocol import OpCode, WebSocketConnection, WebSocketFrame


@dataclass
class AppConfig:
    """Application configuration"""

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    secret_key: str = field(default_factory=lambda: "your-secret-key-change-in-production")

    # Database
    database_path: str = ":memory:"

    # Security
    enable_csrf: bool = True
    enable_rate_limiting: bool = True

    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class Request:
    """HTTP Request object"""

    def __init__(
        self,
        method: str,
        path: str,
        headers: Dict[str, str],
        body: bytes,
        query_params: Dict[str, str],
    ) -> None:
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body
        self.query_params = query_params
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

    def form(self) -> Dict[str, str]:
        """Parse form data"""
        if self.headers.get("content-type", "").startswith("application/x-www-form-urlencoded"):
            return dict(urllib.parse.parse_qsl(self.body.decode("utf-8")))
        return {}


class Response:
    """HTTP Response object"""

    def __init__(
        self,
        content: Union[str, bytes, Dict],
        status: int = 200,
        headers: Optional[Dict[str, str]] = None,
        content_type: str = "text/html",
    ) -> None:
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

    def __init__(self) -> None:
        self.routes: Dict[str, Dict[str, Callable]] = {}
        self.middleware: List[Callable] = []

    def add_route(self, method: str, path: str, handler: Callable) -> Any:
        """Add route"""
        if path not in self.routes:
            self.routes[path] = {}
        self.routes[path][method.upper()] = handler

    def get(self, path: str) -> Any:
        """Add GET route"""

        def decorator(handler) -> Any:
            self.add_route("GET", path, handler)
            return handler

        return decorator

    def post(self, path: str) -> Any:
        """Add POST route"""

        def decorator(handler) -> Any:
            self.add_route("POST", path, handler)
            return handler

        return decorator

    def put(self, path: str) -> Any:
        """Add PUT route"""

        def decorator(handler) -> Any:
            self.add_route("PUT", path, handler)
            return handler

        return decorator

    def delete(self, path: str) -> Any:
        """Add DELETE route"""

        def decorator(handler) -> Any:
            self.add_route("DELETE", path, handler)
            return handler

        return decorator

    def add_middleware(self, middleware: Callable) -> Any:
        """Add middleware"""
        self.middleware.append(middleware)

    async def handle_request(self, request: Request) -> Response:
        """Handle incoming request"""
        # Find route
        if request.path in self.routes and request.method in self.routes[request.path]:
            handler = self.routes[request.path][request.method]

            # Apply middleware
            for middleware in self.middleware:
                if asyncio.iscoroutinefunction(middleware):
                    request = await middleware(request)
                else:
                    request = middleware(request)

            # Call handler
            if asyncio.iscoroutinefunction(handler):
                return await handler(request)
            else:
                return handler(request)

        # 404 Not Found
        return Response("Not Found", status=404, content_type="text/plain")


class ZeroDepApp:
    """Zero-dependency web application"""

    def __init__(self, config: Optional[AppConfig] = None) -> None:
        self.config = config or AppConfig()
        self.router = Router()
        self.database = ZeroDepDatabase(DatabaseConfig(path=self.config.database_path))
        self.crypto = ZeroDepCrypto(CryptoConfig())
        self.http_client = HTTPClient()
        self._setup_logging()

    def _setup_logging(self) -> Any:
        """Setup logging"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format=self.config.log_format,
        )
        self.logger = logging.getLogger(__name__)

    # Route decorators
    def route(self, path: str, methods: List[str] = None) -> Any:
        """Add route with multiple methods"""
        if methods is None:
            methods = ["GET"]

        def decorator(handler) -> Any:
            for method in methods:
                self.router.add_route(method, path, handler)
            return handler

        return decorator

    def get(self, path: str) -> Any:
        """Add GET route"""
        return self.router.get(path)

    def post(self, path: str) -> Any:
        """Add POST route"""
        return self.router.post(path)

    def put(self, path: str) -> Any:
        """Add PUT route"""
        return self.router.put(path)

    def delete(self, path: str) -> Any:
        """Add DELETE route"""
        return self.router.delete(path)

    def middleware(self, middleware: Callable) -> Any:
        """Add middleware"""
        self.router.add_middleware(middleware)
        return middleware

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

    def error_response(self, message: str, status: int = 400) -> Response:
        """Create error response"""
        return Response({"error": message}, status=status)

    # Server implementation
    async def _parse_request(self, data: bytes) -> Request:
        """Parse HTTP request from raw bytes"""
        try:
            # Split headers and body
            header_end = data.find(b"\r\n\r\n")
            if header_end == -1:
                raise ValueError("Invalid HTTP request")

            headers_data = data[:header_end].decode("utf-8")
            body = data[header_end + 4 :]

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

            return Request(
                method=method,
                url=path,
                headers=headers,
                body=body,
                query_string=query_params if isinstance(query_params, str) else ""
            )

        except Exception as e:
            self.logger.error(f"Failed to parse request: {e}")
            raise

    async def _handle_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> Any:
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
            error_response = Response(
                "Internal Server Error", status=500, content_type="text/plain"
            )
            writer.write(error_response.to_bytes())
            await writer.drain()
            self.logger.error(f"Request handling error: {e}")

        finally:
            writer.close()
            await writer.wait_closed()

    async def _run_server_async(self) -> Any:
        """Run async server"""
        server = await asyncio.start_server(self._handle_client, self.config.host, self.config.port)

        self.logger.info(f"Server started on {self.config.host}:{self.config.port}")

        async with server:
            await server.serve_forever()

    def run(self, host: str = None, port: int = None, debug: bool = None) -> Any:
        """Run the application"""
        if host:
            self.config.host = host
        if port:
            self.config.port = port
        if debug is not None:
            self.config.debug = debug

        try:
            asyncio.run(self._run_server_async())
        except KeyboardInterrupt:
            self.logger.info("Server stopped")

    # WebSocket support
    async def websocket_handler(self, websocket_handler: Callable) -> Any:
        """Add WebSocket support"""

        @self.get("/ws")
        async def ws_endpoint(request: Request) -> Any:
            # Upgrade to WebSocket
            if request.headers.get("upgrade", "").lower() != "websocket":
                return self.error_response("WebSocket upgrade required", 400)

            # This is a simplified implementation
            # In practice, you'd need to handle the full WebSocket handshake
            return self.text_response("WebSocket endpoint", 200)

    # Database helpers
    async def db_execute(self, sql: str, params: Any = None) -> Any:
        """Execute database query"""
        return await self.database.execute(sql, params)

    async def db_fetch_one(self, sql: str, params: Any = None) -> Any:
        """Fetch one record"""
        return await self.database.fetch_one(sql, params)

    async def db_fetch_all(self, sql: str, params: Any = None) -> Any:
        """Fetch all records"""
        return await self.database.fetch_all(sql, params)

    # Crypto helpers
    def hash_password(self, password: str) -> str:
        """Hash password"""
        return self.crypto.hash_password(password)

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password"""
        return self.crypto.verify_password(password, hashed)

    def generate_token(self, length: int = 32) -> str:
        """Generate secure token"""
        return self.crypto.generate_token(length)

    def create_jwt(self, payload: Dict[str, Any], expiry_minutes: int = 30) -> str:
        """Create JWT token"""
        return self.crypto.create_jwt(payload, self.config.secret_key, expiry_minutes)

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        return self.crypto.verify_jwt(token, self.config.secret_key)


# Factory functions
def create_app(config: Optional[AppConfig] = None) -> ZeroDepApp:
    """Create zero-dependency application"""
    return ZeroDepApp(config)


def create_zero_dependency_app(debug: bool = False, secret_key: str = None) -> ZeroDepApp:
    """Create zero-dependency app with minimal config"""
    config = AppConfig(debug=debug, secret_key=secret_key or "dev-secret-key-change-in-production")
    return ZeroDepApp(config)


# Example usage
def create_example_app() -> Any:
    """Create example application"""
    app = create_zero_dependency_app(debug=True)

    @app.get("/")
    async def home(request: Request) -> Any:
        return app.json_response(
            {
                "message": "Hello from Zero-Dependency CovetPy!",
                "framework": "CovetPy",
                "dependencies": "ZERO - Standard library only!",
                "timestamp": datetime.now().isoformat(),
            }
        )

    @app.get("/health")
    async def health(request: Request) -> Any:
        return app.json_response(
            {
                "status": "healthy",
                "dependencies": 0,
                "message": "Pure Python standard library implementation",
            }
        )

    @app.post("/echo")
    async def echo(request: Request) -> Any:
        data = request.json()
        return app.json_response({"echo": data, "method": request.method, "path": request.path})

    @app.get("/crypto-test")
    async def crypto_test(request: Request) -> Any:
        # Demo crypto functionality
        password = "test_password"
        hashed = app.hash_password(password)
        is_valid = app.verify_password(password, hashed)
        token = app.generate_token()
        jwt_token = app.create_jwt({"user_id": 123})

        return app.json_response(
            {
                "password_hash": hashed[:20] + "...",
                "password_valid": is_valid,
                "secure_token": token,
                "jwt_token": jwt_token[:20] + "...",
                "crypto_backend": "Python standard library only",
            }
        )

    return app


if __name__ == "__main__":
    # Run example app
    app = create_example_app()
    logger.info("Starting Zero-Dependency CovetPy server...")
    logger.info("Visit http://127.0.0.1:8000 to test")
    app.run()
