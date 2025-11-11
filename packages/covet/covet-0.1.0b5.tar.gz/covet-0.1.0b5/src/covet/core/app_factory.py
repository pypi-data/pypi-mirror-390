"""
Application Factory for CovetPy

Provides intelligent app creation using pure Python implementation (zero dependencies).
This factory simplifies application creation and provides a clean, consistent API.
"""

import os
from typing import Any, Optional


def create_covet_app(backend: Optional[str] = None, **kwargs) -> Any:
    """
    Create a CovetPy application with pure Python backend.

    Args:
        backend: Backend to use (only "pure" is supported; deprecated parameter for backwards compatibility)
        **kwargs: Additional arguments passed to the app constructor

    Returns:
        CovetPy application instance

    Note:
        The 'backend' parameter is deprecated and maintained only for backwards compatibility.
        CovetPy now uses a pure Python implementation exclusively.
    """
    # Check for legacy parameters and provide deprecation warnings
    if backend is not None and backend != "pure":
        import warnings

        warnings.warn(
            f"Backend '{backend}' is no longer supported. CovetPy now uses pure Python implementation only. "
            f"The 'backend' parameter will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2,
        )

    # Check environment variable for backwards compatibility
    env_backend = os.environ.get("COVET_BACKEND")
    if env_backend is not None and env_backend != "pure":
        import warnings

        warnings.warn(
            f"COVET_BACKEND environment variable set to '{env_backend}' is no longer supported. "
            f"CovetPy now uses pure Python implementation only.",
            DeprecationWarning,
            stacklevel=2,
        )

    # Import the CovetPy wrapper from main __init__
    import sys

    from .app_pure import CovetApplication

    parent = sys.modules[__name__.rsplit(".", 1)[0]]
    if hasattr(parent, "CovetPy"):
        # Use the wrapper class that provides the simple API
        return parent.CovetPy(**kwargs)
    else:
        # Direct app creation
        return CovetApplication(**kwargs)


# Convenience alias
def create_pure_app(**kwargs) -> Any:
    """Create a pure Python CovetPy app (zero dependencies)."""
    return create_covet_app(**kwargs)


# Export the factory
__all__ = [
    "create_covet_app",
    "create_pure_app",
]
