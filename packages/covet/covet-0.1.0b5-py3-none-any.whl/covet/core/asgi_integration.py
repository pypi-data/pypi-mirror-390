"""
ASGI Integration Module for CovetPy
==================================

This module provides seamless integration between the new ASGI 3.0 implementation
and the existing CovetPy application architecture. It enables existing CovetPy
applications to run with uvicorn and other ASGI servers without code changes.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from .asgi_app import ASGIRequest, ASGIWebSocket, CovetASGIApp
from .http import Request, Response
from .middleware import MiddlewareStack
from .routing import CovetRouter

logger = logging.getLogger(__name__)


class CovetApplicationASGIAdapter:
    """
    Adapter that makes any CovetApplication ASGI 3.0 compatible.

    This allows existing CovetPy applications to work with uvicorn
    and other ASGI servers without any modifications.
    """

    def __init__(self, covet_app):
        """
        Initialize the adapter with a CovetApplication instance.

        Args:
            covet_app: An instance of CovetApplication or similar
        """
        self.covet_app = covet_app
        self.asgi_app = CovetASGIApp(
            router=getattr(covet_app, "router", CovetRouter()),
            middleware_stack=getattr(covet_app, "middleware_stack", MiddlewareStack()),
            debug=getattr(covet_app, "debug", False),
        )

        # Copy startup/shutdown handlers if they exist
        if hasattr(covet_app, "_startup_handlers"):
            for handler in covet_app._startup_handlers:
                self.asgi_app.add_startup_handler(handler)

        if hasattr(covet_app, "_shutdown_handlers"):
            for handler in covet_app._shutdown_handlers:
                self.asgi_app.add_shutdown_handler(handler)

        # Copy exception handlers
        if hasattr(covet_app, "_exception_handlers"):
            self._setup_exception_handlers()

    def _setup_exception_handlers(self):
        """Setup exception handlers from CovetApplication."""
        exception_handlers = getattr(self.covet_app, "_exception_handlers", {})

        # Wrap the original ASGI handler to include exception handling
        original_handle_http = self.asgi_app._handle_http

        async def handle_http_with_exceptions(scope, receive, send):
            try:
                await original_handle_http(scope, receive, send)
            except Exception as exc:
                # Check for specific exception handlers
                for exc_type, handler in exception_handlers.items():
                    if isinstance(exc, exc_type):
                        try:
                            # Create a request object for the handler
                            asgi_request = ASGIRequest(scope, receive)
                            request = asgi_request.to_covet_request()

                            # Call the exception handler
                            if asyncio.iscoroutinefunction(handler):
                                response = await handler(request, exc)
                            else:
                                response = handler(request, exc)

                            # Send the response
                            await self.asgi_app._send_response(response, send)
                            return

                        except Exception as handler_exc:
                            logger.error(f"Exception handler failed: {handler_exc}")

                # Fall back to default handling
                await self.asgi_app._handle_exception(exc, send)

        self.asgi_app._handle_http = handle_http_with_exceptions

    async def __call__(self, scope, receive, send):
        """ASGI 3.0 interface."""
        return await self.asgi_app(scope, receive, send)


class EnhancedASGIRequest(ASGIRequest):
    """
    Enhanced ASGI Request with better compatibility for CovetPy features.
    """

    def __init__(self, scope, receive):
        super().__init__(scope, receive)
        self._path_params = {}

    def to_covet_request(self) -> Request:
        """Create enhanced CovetPy Request with all ASGI scope information."""
        # Parse headers more thoroughly
        headers = {}
        raw_headers = {}

        for name_bytes, value_bytes in self.scope.get("headers", []):
            name = name_bytes.decode("latin1").lower()
            value = value_bytes.decode("latin1")
            headers[name] = value
            raw_headers[name_bytes] = value_bytes

        # Parse query parameters
        query_string = self.scope.get("query_string", b"").decode("latin1")

        # Extract all scope information
        client = self.scope.get("client")
        server = self.scope.get("server")

        # Create the request
        request = Request(
            method=self.scope.get("method", "GET"),
            url=self.scope.get("path", "/"),
            headers=headers,
            query_string=query_string,
            remote_addr=client[0] if client else "",
            scheme=self.scope.get("scheme", "http"),
            server_name=server[0] if server else "localhost",
            server_port=server[1] if server and len(server) > 1 else 80,
        )

        # Add ASGI-specific attributes
        request.scope = self.scope
        request.asgi_receive = self.receive
        request._raw_headers = raw_headers
        request.path_params = self._path_params

        # Add HTTP version info
        request.http_version = self.scope.get("http_version", "1.1")

        return request


class ASGIMiddlewareAdapter:
    """
    Adapter to use standard ASGI middleware with CovetPy.
    """

    def __init__(self, asgi_middleware_class, **options):
        self.middleware_class = asgi_middleware_class
        self.options = options

    def __call__(self, app: CovetASGIApp):
        """Apply ASGI middleware to CovetPy ASGI app."""
        return self.middleware_class(app, **self.options)


def make_asgi_compatible(covet_app) -> CovetASGIApp:
    """
    Make any CovetPy application ASGI 3.0 compatible.

    Args:
        covet_app: CovetApplication or compatible instance

    Returns:
        ASGI 3.0 compatible application
    """
    if hasattr(covet_app, "__call__") and hasattr(covet_app, "router"):
        # It's already a CovetApplication, wrap it
        adapter = CovetApplicationASGIAdapter(covet_app)
        return adapter
    elif isinstance(covet_app, CovetASGIApp):
        # Already ASGI compatible
        return covet_app
    else:
        # Try to create a new ASGI app from components
        router = getattr(covet_app, "router", None)
        middleware = getattr(covet_app, "middleware_stack", None)
        debug = getattr(covet_app, "debug", False)

        return CovetASGIApp(router=router, middleware_stack=middleware, debug=debug)


def integrate_with_uvicorn(app, **uvicorn_config):
    """
    Helper function to run CovetPy app with uvicorn.

    Args:
        app: CovetPy application
        **uvicorn_config: Configuration for uvicorn
    """
    try:
        import uvicorn

        # Make app ASGI compatible
        asgi_app = make_asgi_compatible(app)

        # Default uvicorn configuration
        config = {
            "host": "127.0.0.1",
            "port": 8000,
            "log_level": "info",
            "access_log": True,
            **uvicorn_config,
        }

        # Run with uvicorn
        uvicorn.run(asgi_app, **config)

    except ImportError:
        raise RuntimeError(
            "uvicorn is required for ASGI integration. " "Install it with: pip install uvicorn"
        )


class ASGITestClient:
    """
    Test client for ASGI applications with CovetPy integration.
    """

    def __init__(self, app):
        self.app = make_asgi_compatible(app)

    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        **kwargs,
    ):
        """Make a test request to the ASGI app."""
        # Create ASGI scope
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method.upper(),
            "scheme": "http",
            "path": path,
            "raw_path": path.encode("utf-8"),
            "root_path": "",
            "query_string": b"",
            "headers": [
                [name.lower().encode("latin1"), value.encode("latin1")]
                for name, value in (headers or {}).items()
            ],
            "server": ("testserver", 80),
            "client": ("127.0.0.1", 0),
        }

        # Receive callable
        body_sent = False

        async def receive():
            nonlocal body_sent
            if not body_sent:
                body_sent = True
                return {"type": "http.request", "body": body or b"", "more_body": False}
            return {"type": "http.disconnect"}

        # Send callable and response collector
        response_data = {"status_code": None, "headers": [], "body": b""}

        async def send(message):
            if message["type"] == "http.response.start":
                response_data["status_code"] = message["status"]
                response_data["headers"] = message.get("headers", [])
            elif message["type"] == "http.response.body":
                response_data["body"] += message.get("body", b"")

        # Call the app
        await self.app(scope, receive, send)

        return response_data

    async def get(self, path: str, **kwargs):
        """Make GET request."""
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        """Make POST request."""
        return await self.request("POST", path, **kwargs)

    async def put(self, path: str, **kwargs):
        """Make PUT request."""
        return await self.request("PUT", path, **kwargs)

    async def delete(self, path: str, **kwargs):
        """Make DELETE request."""
        return await self.request("DELETE", path, **kwargs)


__all__ = [
    "CovetApplicationASGIAdapter",
    "EnhancedASGIRequest",
    "ASGIMiddlewareAdapter",
    "make_asgi_compatible",
    "integrate_with_uvicorn",
    "ASGITestClient",
]
