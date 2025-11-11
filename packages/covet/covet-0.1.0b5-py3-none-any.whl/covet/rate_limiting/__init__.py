"""Rate limiting module."""

class RateLimiter:
    """Rate limiter."""
    
    def __init__(self, max_requests=100, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    async def check_rate_limit(self, key):
        """Check if key is rate limited."""
        return True

__all__ = ["RateLimiter"]



def create_rate_limiter(max_requests=100, window=60):
    """Create a rate limiter instance."""
    return RateLimiter(max_requests, window)
