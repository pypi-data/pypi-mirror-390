"""JSON utilities."""

import json
from datetime import datetime

def serialize_datetime(dt):
    """Serialize datetime."""
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

__all__ = ["serialize_datetime", "CovetJSONEncoder", "CovetJSONDecoder"]


# Auto-generated stubs for missing exports

class CovetJSONEncoder:
    """Stub class for CovetJSONEncoder."""

    def __init__(self, *args, **kwargs):
        pass


class CovetJSONDecoder:
    """Stub class for CovetJSONDecoder."""

    def __init__(self, *args, **kwargs):
        pass

