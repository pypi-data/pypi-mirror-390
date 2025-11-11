"""SDK integrations."""

class SDKIntegration:
    """Base SDK integration class."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key
    
    async def call(self, method, *args, **kwargs):
        """Call SDK method."""
        pass

__all__ = ["SDKIntegration"]
