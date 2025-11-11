"""Foreign Function Interface."""

class FFIBridge:
    """FFI bridge for calling external libraries."""
    
    def __init__(self):
        self.libraries = {}
    
    def load_library(self, name, path):
        """Load external library."""
        self.libraries[name] = path

__all__ = ["FFIBridge"]
