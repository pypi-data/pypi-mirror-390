"""
CovetPy Simple Middleware System
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional


@dataclass
class MiddlewareConfig:
    """Configuration for middleware."""

    enabled: bool = True
    priority: int = 100
    dependencies: List[str] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)


class Middleware(ABC):
    """Base middleware class."""

    def __init__(self, config: Optional[MiddlewareConfig] = None):
        self.config = config or MiddlewareConfig()

    @abstractmethod
    async def process_request(self, request: Any) -> Any:
        """Process incoming request."""

    @abstractmethod
    async def process_response(self, request: Any, response: Any) -> Any:
        """Process outgoing response."""


# Backward compatibility alias
BaseMiddleware = Middleware


class MiddlewareStack:
    """Simple middleware stack."""

    def __init__(self):
        self.middlewares: List[Middleware] = []

    def add(self, middleware: Middleware) -> None:
        """Add middleware to stack."""
        self.middlewares.append(middleware)

    async def process_request(self, request: Any) -> Any:
        """Process request through middleware stack."""
        for middleware in self.middlewares:
            request = await middleware.process_request(request)
        return request

    async def process_response(self, request: Any, response: Any) -> Any:
        """Process response through middleware stack."""
        for middleware in reversed(self.middlewares):
            response = await middleware.process_response(request, response)
        return response


def create_default_middleware_stack() -> MiddlewareStack:
    """Create default middleware stack."""
    return MiddlewareStack()


class SecurityHeadersMiddleware:
    """Add security headers to responses."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        async def send_wrapper(message):
            if message['type'] == 'http.response.start':
                headers = dict(message.get('headers', []))
                headers.setdefault(b'X-Content-Type-Options', b'nosniff')
                headers.setdefault(b'X-Frame-Options', b'DENY')
                headers.setdefault(b'X-XSS-Protection', b'1; mode=block')
                message['headers'] = list(headers.items())
            await send(message)
        
        return await self.app(scope, receive, send_wrapper)

__all__ = ["SecurityHeadersMiddleware", "CompressionMiddleware", "GZipMiddleware"]



class CORSMiddleware:
    """CORS middleware."""
    def __init__(self, app, allow_origins=None):
        self.app = app
        self.allow_origins = allow_origins or ["*"]


# Auto-generated stubs for missing exports

class CompressionMiddleware:
    """Stub class for CompressionMiddleware."""

    def __init__(self, *args, **kwargs):
        pass


class GZipMiddleware:
    """Stub class for GZipMiddleware."""

    def __init__(self, *args, **kwargs):
        pass

