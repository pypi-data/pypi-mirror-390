"""Ultra-fast router."""

class UltraRouter:
    """High-performance router."""
    
    def __init__(self):
        self.routes = {}
    
    def add_route(self, path, handler):
        """Add route."""
        self.routes[path] = handler

__all__ = ["UltraRouter", "benchmark_router"]



class RouteMatch:
    """Route match result."""
    def __init__(self, handler, params):
        self.handler = handler
        self.params = params


# Auto-generated stubs for missing exports

def benchmark_router(*args, **kwargs):
    """Stub function for benchmark_router."""
    pass

