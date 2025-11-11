"""Serialization utilities for integrations."""

class Serializer:
    """Generic serializer."""
    
    def serialize(self, obj):
        """Serialize object."""
        return str(obj)
    
    def deserialize(self, data):
        """Deserialize data."""
        return data

__all__ = ["Serializer"]
