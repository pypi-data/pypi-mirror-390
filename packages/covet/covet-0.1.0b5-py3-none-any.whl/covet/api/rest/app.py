from covet import CovetPy


def create_app(config: dict = None) -> CovetPy:
    """Create a new CovetPy application."""
    app = CovetPy()
    return app


class CovetAPI:
    """Main REST API application."""
    
    def __init__(self):
        self.routes = []
        self.middleware = []
    
    def add_route(self, path, handler, methods=None):
        """Add a route."""
        self.routes.append({'path': path, 'handler': handler, 'methods': methods or ['GET']})
    
    async def __call__(self, scope, receive, send):
        """ASGI callable."""
        pass

__all__ = ["CovetAPI"]



async def lifespan(app):
    """Application lifespan manager."""
    # Startup
    yield
    # Shutdown
