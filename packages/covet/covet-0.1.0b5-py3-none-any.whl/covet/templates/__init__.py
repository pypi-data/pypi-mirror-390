"""
CovetPy Template Engine - Production Ready Template System

A complete Jinja2-like template engine with enterprise features:
- Template inheritance and inclusion
- Comprehensive filter system
- Auto-escaping for security
- Template caching and performance optimization
- Static file serving with compression
- Development and production modes

Usage:
    from covet.templates import TemplateEngine

    # Initialize engine
    engine = TemplateEngine(
        template_dirs=['templates'],
        static_dirs=['static'],
        auto_escape=True,
        debug=False
    )

    # Render template
    html = engine.render('index.html', {
        'title': 'Welcome',
        'users': [{'name': 'John'}, {'name': 'Jane'}]
    })

    # Add custom filter
    engine.add_filter('custom_format', lambda x: f"Custom: {x}")

    # Serve static files
    response = engine.serve_static('css/style.css')
"""

from covet.templates.compiler import (
    BlockNode,
    CommentNode,
    ExtendsNode,
    ForNode,
    IfNode,
    IncludeNode,
    MacroNode,
    TemplateCompiler,
    TemplateNode,
    TextNode,
    VariableNode,
)
from covet.templates.engine import (
    SafeString,
    TemplateContext,
    TemplateEngine,
    TemplateError,
    TemplateNotFound,
    TemplateRuntimeError,
    TemplateSyntaxError,
    escape_html,
    safe_string,
)
from covet.templates.filters import FilterRegistry
from covet.templates.loader import (
    TemplateCache,
    TemplateLoader,
    TemplateSecurityError,
    TemplateWatcher,
    discover_templates,
    validate_template_syntax,
)
from covet.templates.static import (
    AssetVersioning,
    StaticFileCache,
    StaticFileHandler,
    StaticFileMiddleware,
    generate_etag,
    is_fresh,
)


# Convenience function for quick template rendering
def render_template(template_name: str, context: dict = None, **kwargs) -> str:
    """
    Quick template rendering with default engine.

    Args:
        template_name: Name of template to render
        context: Template context variables
        **kwargs: Additional context variables

    Returns:
        Rendered template as string
    """
    engine = TemplateEngine()
    return engine.render(template_name, context, **kwargs)


def render_string(template_string: str, context: dict = None, **kwargs) -> str:
    """
    Quick string template rendering with default engine.

    Args:
        template_string: Template content as string
        context: Template context variables
        **kwargs: Additional context variables

    Returns:
        Rendered template as string
    """
    engine = TemplateEngine()
    return engine.render_string(template_string, context, **kwargs)


# Template engine factory for common configurations
class TemplateEngineFactory:
    """Factory for creating pre-configured template engines."""

    @staticmethod
    def create_development_engine(
        template_dirs: list = None, static_dirs: list = None
    ) -> TemplateEngine:
        """Create engine optimized for development."""
        return TemplateEngine(
            template_dirs=template_dirs or ["templates"],
            static_dirs=static_dirs or ["static"],
            auto_escape=True,
            cache_size=100,  # Smaller cache for development
            cache_ttl=60,  # Short TTL for auto-reload
            debug=True,
        )

    @staticmethod
    def create_production_engine(
        template_dirs: list = None, static_dirs: list = None
    ) -> TemplateEngine:
        """Create engine optimized for production."""
        return TemplateEngine(
            template_dirs=template_dirs or ["templates"],
            static_dirs=static_dirs or ["static"],
            auto_escape=True,
            cache_size=10000,  # Large cache for production
            cache_ttl=3600,  # Long TTL for performance
            debug=False,
        )

    @staticmethod
    def create_secure_engine(
        template_dirs: list = None, static_dirs: list = None
    ) -> TemplateEngine:
        """Create engine with enhanced security settings."""
        engine = TemplateEngine(
            template_dirs=template_dirs or ["templates"],
            static_dirs=static_dirs or ["static"],
            auto_escape=True,
            cache_size=5000,
            cache_ttl=1800,
            debug=False,
        )

        # Add security-focused global functions
        engine.add_global("csrf_token", lambda: "secure-csrf-token")
        engine.add_global("user_is_authenticated", lambda: False)

        return engine


# Integration helpers for CovetPy framework
class CovetTemplateIntegration:
    """Integration helpers for CovetPy framework."""

    def __init__(self, app=None):
        self.app = app
        self.engine = None

    def init_app(self, app, config: dict = None):
        """Initialize template engine with CovetPy app."""
        self.app = app
        config = config or {}

        # Get configuration from app or use defaults
        template_dirs = config.get("TEMPLATE_DIRS", ["templates"])
        static_dirs = config.get("STATIC_DIRS", ["static"])
        config.get("AUTO_ESCAPE", True)
        debug = config.get("DEBUG", False)

        # Create engine
        if debug:
            self.engine = TemplateEngineFactory.create_development_engine(
                template_dirs, static_dirs
            )
        else:
            self.engine = TemplateEngineFactory.create_production_engine(template_dirs, static_dirs)

        # Add app-specific globals
        self.engine.add_global("app", app)
        self.engine.add_global("config", getattr(app, "config", {}))

        # Store engine in app
        if hasattr(app, "template_engine"):
            app.template_engine = self.engine

    def render_template(self, template_name: str, **context) -> str:
        """Render template with app context."""
        if not self.engine:
            raise RuntimeError("Template engine not initialized")

        # Add app-specific context
        if self.app and hasattr(self.app, "get_template_context"):
            app_context = self.app.get_template_context()
            context.update(app_context)

        return self.engine.render(template_name, context)


# Error handling utilities
class TemplateErrorHandler:
    """Centralized template error handling."""

    def __init__(self, debug: bool = False):
        self.debug = debug

    def handle_template_error(self, error: Exception, template_name: str = None) -> str:
        """Handle template errors gracefully."""
        if self.debug:
            return self._render_debug_error(error, template_name)
        else:
            return self._render_production_error(error, template_name)

    def _render_debug_error(self, error: Exception, template_name: str = None) -> str:
        """Render detailed error for development."""
        error_html = f"""
        <div style="background: #f8f8f8; border: 1px solid #ddd; padding: 20px; margin: 20px; font-family: monospace;">
            <h2 style="color: #d32f2f;">Template Error</h2>
            <p><strong>Template:</strong> {template_name or 'Unknown'}</p>
            <p><strong>Error Type:</strong> {type(error).__name__}</p>
            <p><strong>Message:</strong> {str(error)}</p>
            {self._get_traceback_html(error)}
        </div>
        """
        return error_html

    def _render_production_error(self, error: Exception, template_name: str = None) -> str:
        """Render minimal error for production."""
        return """
        <div style="background: #ffebee; border: 1px solid #f44336; padding: 10px; color: #c62828;">
            Template rendering error. Please try again later.
        </div>
        """

    def _get_traceback_html(self, error: Exception) -> str:
        """Get HTML-formatted traceback."""
        import traceback

        tb = traceback.format_exc()
        return (
            f"<pre style='background: #fff; padding: 10px; overflow: auto;'>{html.escape(tb)}</pre>"
        )


# Performance monitoring
class TemplatePerformanceMonitor:
    """Monitor template rendering performance."""

    def __init__(self):
        self.render_times = {}
        self.render_counts = {}

    def record_render(self, template_name: str, render_time: float):
        """Record template render time."""
        if template_name not in self.render_times:
            self.render_times[template_name] = []
            self.render_counts[template_name] = 0

        self.render_times[template_name].append(render_time)
        self.render_counts[template_name] += 1

        # Keep only last 100 renders per template
        if len(self.render_times[template_name]) > 100:
            self.render_times[template_name] = self.render_times[template_name][-100:]

    def get_stats(self) -> dict:
        """Get performance statistics."""
        stats = {}
        for template_name in self.render_times:
            times = self.render_times[template_name]
            if times:
                stats[template_name] = {
                    "count": self.render_counts[template_name],
                    "avg_time": sum(times) / len(times),
                    "min_time": min(times),
                    "max_time": max(times),
                    "total_time": sum(times),
                }
        return stats


# Export all public classes and functions
__all__ = [
    # Core engine
    "TemplateEngine",
    "TemplateContext",
    # Errors
    "TemplateError",
    "TemplateNotFound",
    "TemplateSyntaxError",
    "TemplateRuntimeError",
    "TemplateSecurityError",
    # Components
    "TemplateLoader",
    "TemplateCompiler",
    "FilterRegistry",
    "StaticFileHandler",
    # Utilities
    "SafeString",
    "escape_html",
    "safe_string",
    "render_template",
    "render_string",
    # Factory and integration
    "TemplateEngineFactory",
    "CovetTemplateIntegration",
    "TemplateErrorHandler",
    "TemplatePerformanceMonitor",
    # Static file handling
    "StaticFileCache",
    "AssetVersioning",
    "StaticFileMiddleware",
    # Discovery and validation
    "discover_templates",
    "validate_template_syntax",
]


# Version information
__version__ = "1.0.0"
__author__ = "CovetPy Team"
__description__ = "Production-ready template engine for CovetPy"
