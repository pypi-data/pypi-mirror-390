"""
CovetPy Template Engine - Production Ready Implementation

A complete Jinja2-like template engine with:
- Template inheritance and inclusion
- Auto-escaping for security
- Custom filters and tags
- Template caching
- Static file handling
"""

import hashlib
import html
import os
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .compiler import TemplateCompiler
from .filters import FilterRegistry
from .loader import TemplateLoader
from .static import StaticFileHandler


class TemplateContext:
    """Template execution context with variable scoping."""

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        self.variables = variables or {}
        self.parent = None
        self.blocks = {}
        self.extended_template = None

    def push_scope(self) -> "TemplateContext":
        """Create new scope inheriting from current context."""
        new_context = TemplateContext(self.variables.copy())
        new_context.parent = self
        new_context.blocks = self.blocks.copy()
        return new_context

    def pop_scope(self) -> "TemplateContext":
        """Return to parent scope."""
        return self.parent or self

    def get(self, name: str, default: Any = None) -> Any:
        """Get variable from context with scope resolution."""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name, default)
        return default

    def set(self, name: str, value: Any):
        """Set variable in current scope."""
        self.variables[name] = value

    def update(self, variables: Dict[str, Any]):
        """Update context with new variables."""
        self.variables.update(variables)


class TemplateEngine:
    """
    Production-ready template engine with comprehensive features.

    Features:
    - Jinja2-like syntax
    - Template inheritance (extends/blocks)
    - Template inclusion
    - Auto-escaping for XSS prevention
    - Custom filters and global functions
    - Template caching with TTL
    - Static file serving
    - Error handling with detailed messages
    """

    def __init__(
        self,
        template_dirs: Optional[List[Union[str, Path]]] = None,
        static_dirs: Optional[List[Union[str, Path]]] = None,
        auto_escape: bool = True,
        cache_size: int = 1000,
        cache_ttl: int = 3600,
        debug: bool = False,
    ):
        """
        Initialize template engine.

        Args:
            template_dirs: Directories to search for templates
            static_dirs: Directories to serve static files from
            auto_escape: Enable automatic HTML escaping
            cache_size: Maximum number of cached templates
            cache_ttl: Cache time-to-live in seconds
            debug: Enable debug mode with detailed error messages
        """
        self.template_dirs = [Path(d) for d in (template_dirs or ["templates"])]
        self.static_dirs = [Path(d) for d in (static_dirs or ["static"])]
        self.auto_escape = auto_escape
        self.debug = debug

        # Initialize components
        self.loader = TemplateLoader(self.template_dirs, cache_size, cache_ttl)
        self.compiler = TemplateCompiler(self)
        self.filter_registry = FilterRegistry()
        self.static_handler = StaticFileHandler(self.static_dirs)

        # Global functions and variables
        self.globals = {
            "range": range,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "now": datetime.now,
            "url_for": self._url_for,
            "static": self._static_url,
        }

        # Thread-safe template cache
        self._compiled_cache = {}
        self._cache_lock = threading.RLock()

    def render(self, template_name: str, context: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        """
        Render template with given context.

        Args:
            template_name: Name of template to render
            context: Template context variables
            **kwargs: Additional context variables

        Returns:
            Rendered template as string

        Raises:
            TemplateNotFound: If template doesn't exist
            TemplateSyntaxError: If template has syntax errors
            TemplateRuntimeError: If error occurs during rendering
        """
        try:
            # Prepare context
            template_context = TemplateContext()
            template_context.update(self.globals)
            if context:
                template_context.update(context)
            template_context.update(kwargs)

            # Get compiled template
            compiled_template = self._get_compiled_template(template_name)

            # Execute template
            return compiled_template(template_context)

        except Exception as e:
            if self.debug:
                raise TemplateRuntimeError(
                    f"Error rendering template '{template_name}': {str(e)}"
                ) from e
            else:
                raise TemplateRuntimeError(f"Template rendering failed: {template_name}")

    def render_string(
        self, template_string: str, context: Optional[Dict[str, Any]] = None, **kwargs
    ) -> str:
        """
        Render template from string.

        Args:
            template_string: Template content as string
            context: Template context variables
            **kwargs: Additional context variables

        Returns:
            Rendered template as string
        """
        try:
            # Create cache key for string template using SHA-256 instead of MD5
            # for security
            cache_key = f"string:{hashlib.sha256(template_string.encode()).hexdigest()}"

            # Check cache
            with self._cache_lock:
                if cache_key in self._compiled_cache:
                    compiled_template = self._compiled_cache[cache_key]
                else:
                    # Compile string template
                    compiled_template = self.compiler.compile_string(template_string)
                    self._compiled_cache[cache_key] = compiled_template

            # Prepare context
            template_context = TemplateContext()
            template_context.update(self.globals)
            if context:
                template_context.update(context)
            template_context.update(kwargs)

            # Execute template
            return compiled_template(template_context)

        except Exception as e:
            if self.debug:
                raise TemplateRuntimeError(f"Error rendering string template: {str(e)}") from e
            else:
                raise TemplateRuntimeError("String template rendering failed")

    def add_filter(self, name: str, filter_func: Callable):
        """Add custom filter function."""
        self.filter_registry.add_filter(name, filter_func)

    def add_global(self, name: str, value: Any):
        """Add global variable or function."""
        self.globals[name] = value

    def clear_cache(self):
        """Clear compiled template cache."""
        with self._cache_lock:
            self._compiled_cache.clear()
        self.loader.clear_cache()

    def get_static_url(self, filename: str) -> str:
        """Get URL for static file."""
        return self._static_url(filename)

    def serve_static(self, path: str) -> Optional[Dict[str, Any]]:
        """Serve static file content."""
        return self.static_handler.serve(path)

    def _get_compiled_template(self, template_name: str):
        """Get compiled template with caching."""
        with self._cache_lock:
            # Check cache first
            if template_name in self._compiled_cache:
                return self._compiled_cache[template_name]

            # Load and compile template
            template_content = self.loader.load(template_name)
            compiled_template = self.compiler.compile(template_content, template_name)

            # Cache compiled template
            self._compiled_cache[template_name] = compiled_template

            return compiled_template

    def _url_for(self, endpoint: str, **params) -> str:
        """Generate URL for endpoint (placeholder implementation)."""
        # This would integrate with CovetPy's routing system
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            return f"/{endpoint}?{query_string}"
        return f"/{endpoint}"

    def _static_url(self, filename: str) -> str:
        """Generate URL for static file."""
        return f"/static/{filename}"


class TemplateError(Exception):
    """Base exception for template errors."""


class TemplateNotFound(TemplateError):
    """Exception raised when template is not found."""


class TemplateSyntaxError(TemplateError):
    """Exception raised for template syntax errors."""

    def __init__(
        self,
        message: str,
        line_number: Optional[int] = None,
        template_name: Optional[str] = None,
    ):
        self.line_number = line_number
        self.template_name = template_name

        if line_number and template_name:
            message = f"Template '{template_name}', line {line_number}: {message}"
        elif template_name:
            message = f"Template '{template_name}': {message}"

        super().__init__(message)


class TemplateRuntimeError(TemplateError):
    """Exception raised during template execution."""


# Helper functions for template operations
def escape_html(value: Any) -> str:
    """Escape HTML characters for security."""
    if value is None:
        return ""
    return html.escape(str(value), quote=True)


def safe_string(value: str) -> "SafeString":
    """Mark string as safe (no auto-escaping)."""
    return SafeString(value)


class SafeString(str):
    """String marked as safe from auto-escaping."""

    def __html__(self):
        return str(self)

    def __add__(self, other):
        if isinstance(other, SafeString):
            return SafeString(str(self) + str(other))
        return SafeString(str(self) + escape_html(other))

    def __radd__(self, other):
        if isinstance(other, SafeString):
            return SafeString(str(other) + str(self))
        return SafeString(escape_html(other) + str(self))


# Export main classes
__all__ = [
    "TemplateEngine",
    "TemplateContext",
    "TemplateError",
    "TemplateNotFound",
    "TemplateSyntaxError",
    "TemplateRuntimeError",
    "SafeString",
    "escape_html",
    "safe_string",
]


# Backward compatibility alias
Environment = TemplateEngine


__all__ = ["TemplateEngine", "Environment", "render_template", "render_string"]


class DictLoader:
    """Load templates from dictionary."""
    
    def __init__(self, templates_dict=None):
        self.templates = templates_dict or {}
    
    def get_source(self, name):
        """Get template source by name."""
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")
        return self.templates[name]
    
    def load(self, name):
        """Load and return template."""
        return self.get_source(name)

__all__ = ["DictLoader"]
