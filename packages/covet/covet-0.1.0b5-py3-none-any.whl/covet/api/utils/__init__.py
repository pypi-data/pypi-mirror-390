"""API utilities."""

def serialize_datetime(dt):
    """Serialize datetime to ISO format."""
    if dt is None:
        return None
    return dt.isoformat()

__all__ = ["serialize_datetime"]
