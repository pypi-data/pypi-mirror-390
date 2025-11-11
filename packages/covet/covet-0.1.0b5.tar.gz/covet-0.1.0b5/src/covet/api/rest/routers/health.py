"""Health check router."""

async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

__all__ = ["health_check", "router", "health_router"]


# Auto-generated stubs for missing exports

class router:
    """Stub class for router."""

    def __init__(self, *args, **kwargs):
        pass


def health_router(*args, **kwargs):
    """Stub function for health_router."""
    pass

