"""
ReDoc UI Integration

Embedded ReDoc for beautiful, responsive API documentation. ReDoc provides
a three-panel layout optimized for large APIs with advanced search,
customizable themes, and better readability than Swagger UI.

Features:
- ReDoc 2.x integration
- Three-panel responsive layout
- Advanced search with highlighting
- Dark mode support
- Better for documentation-heavy APIs
- No try-it-out (documentation focused)
- Custom branding and themes
- Markdown rendering
- Code samples in multiple languages
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ReDocTheme(str, Enum):
    """ReDoc color themes."""

    LIGHT = "light"
    DARK = "dark"


class ReDocConfig(BaseModel):
    """
    Configuration for ReDoc.

    Provides comprehensive customization options for ReDoc including
    theming, navigation, search, and display preferences.

    Example:
        config = ReDocConfig(
            spec_url="/openapi.json",
            title="My API Documentation",
            theme=ReDocTheme.DARK,
            hide_download_button=False,
            expand_responses="200,201",
            native_scrollbars=True
        )
    """

    spec_url: str = Field(default="/openapi.json", description="URL to OpenAPI specification")
    title: str = Field(default="API Documentation", description="Page title")
    theme: ReDocTheme = Field(default=ReDocTheme.LIGHT, description="UI color theme")
    # Navigation
    hide_hostname: bool = Field(default=False, description="Hide hostname in method definition")
    expand_responses: Optional[str] = Field(
        default="200,201", description="Comma-separated list of response codes to expand by default"
    )
    required_props_first: bool = Field(default=True, description="Show required properties first")
    sort_props_alphabetically: bool = Field(
        default=False, description="Sort properties alphabetically"
    )
    sort_enum_values_alphabetically: bool = Field(
        default=False, description="Sort enum values alphabetically"
    )
    sort_operations_alphabetically: bool = Field(
        default=False, description="Sort operations alphabetically"
    )
    sort_tags_alphabetically: bool = Field(default=False, description="Sort tags alphabetically")
    # UI Options
    lazy_rendering: bool = Field(
        default=True, description="Enable lazy rendering for better performance"
    )
    hide_download_button: bool = Field(
        default=False, description="Hide download OpenAPI spec button"
    )
    hide_loading: bool = Field(default=False, description="Hide loading animation")
    native_scrollbars: bool = Field(
        default=False, description="Use native scrollbars instead of custom"
    )
    path_in_middle_panel: bool = Field(
        default=False, description="Show path in middle panel instead of right"
    )
    suppress_warnings: bool = Field(default=False, description="Suppress warnings in console")
    hide_schema_pattern: bool = Field(default=False, description="Hide pattern in schema")
    expand_single_schema_field: bool = Field(
        default=False, description="Automatically expand single field in schema"
    )
    schema_expansion_level: int = Field(
        default=1, ge=0, le=10, description="Schema expansion level (0 = all collapsed)"
    )
    # Search
    disable_search: bool = Field(default=False, description="Disable search functionality")
    max_displayed_enum_values: int = Field(
        default=10, ge=1, description="Maximum number of enum values to display"
    )
    # Code Samples
    show_extensions: bool = Field(default=False, description="Show vendor extensions (x-)")
    hide_schema_titles: bool = Field(default=False, description="Hide schema titles")
    simple_one_of_type_label: bool = Field(default=False, description="Show simple label for oneOf")
    payload_sample_idx: int = Field(default=0, ge=0, description="Default payload sample index")
    # Custom branding
    custom_css: Optional[str] = Field(default=None, description="Custom CSS to inject")
    custom_js: Optional[str] = Field(default=None, description="Custom JavaScript to inject")
    custom_favicon: Optional[str] = Field(default=None, description="URL to custom favicon")
    logo_url: Optional[str] = Field(default=None, description="URL to logo image")
    logo_href: Optional[str] = Field(default=None, description="Link when clicking logo")
    # Colors (for custom theming)
    primary_color: Optional[str] = Field(default=None, description="Primary color (hex)")
    text_color: Optional[str] = Field(default=None, description="Text color (hex)")
    background_color: Optional[str] = Field(default=None, description="Background color (hex)")

    class Config:
        use_enum_values = True


class ReDocUI:
    """
    ReDoc renderer with full customization support.

    ReDoc provides a clean, three-panel documentation interface optimized
    for large APIs. It focuses on documentation rather than interactive
    testing, making it ideal for public API documentation sites.

    Features:
    - Three-panel responsive layout
    - Advanced search with highlighting
    - Dark mode support
    - Better typography and readability
    - Sidebar navigation with operation grouping
    - Markdown rendering in descriptions
    - Code samples in multiple languages
    - Mobile-friendly responsive design

    Example:
        # Basic usage
        redoc = ReDocUI(
            config=ReDocConfig(
                spec_url="/openapi.json",
                title="My API Documentation"
            )
        )
        html = redoc.get_html()

        # Dark theme with custom branding
        redoc = ReDocUI(
            config=ReDocConfig(
                spec_url="/openapi.json",
                title="My API",
                theme=ReDocTheme.DARK,
                logo_url="https://example.com/logo.png",
                primary_color="#FF6B6B"
            )
        )

        # Serve in ASGI app
        @app.route("/redoc")
        async def redoc(request):
            return HTMLResponse(redoc.get_html())
    """

    def __init__(
        self,
        config: Optional[ReDocConfig] = None,
        redoc_version: str = "2.1.3",
    ):
        """
        Initialize ReDoc UI.

        Args:
            config: ReDoc configuration
            redoc_version: Version of ReDoc to use
        """
        self.config = config or ReDocConfig()
        self.redoc_version = redoc_version

    def get_html(self) -> str:
        """
        Generate complete HTML page with embedded ReDoc.

        Returns:
            HTML string ready to serve
        """
        # Build ReDoc configuration
        redoc_options = self._build_redoc_options()

        # Build custom CSS
        custom_css = self._build_custom_css()

        # Build custom JS
        custom_js = self._build_custom_js()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    {self._get_favicon_tag()}
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    {custom_css}
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url="{self.config.spec_url}"{redoc_options}></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@{self.redoc_version}/bundles/redoc.standalone.js"></script>
    {custom_js}
</body>
</html>"""
        return html

    def _build_redoc_options(self) -> str:
        """Build HTML attributes for ReDoc element."""
        options = []

        # Theme
        if self.config.theme == ReDocTheme.DARK:
            options.append('theme="dark"')

        # Navigation options
        if self.config.hide_hostname:
            options.append("hide-hostname")

        if self.config.expand_responses:
            options.append(f'expand-responses="{self.config.expand_responses}"')

        if self.config.required_props_first:
            options.append("required-props-first")

        if self.config.sort_props_alphabetically:
            options.append("sort-props-alphabetically")

        if self.config.sort_enum_values_alphabetically:
            options.append("sort-enum-values-alphabetically")

        if self.config.sort_operations_alphabetically:
            options.append("sort-operations-alphabetically")

        if self.config.sort_tags_alphabetically:
            options.append("sort-tags-alphabetically")

        # UI options
        if self.config.lazy_rendering:
            options.append("lazy-rendering")

        if self.config.hide_download_button:
            options.append("hide-download-button")

        if self.config.hide_loading:
            options.append("hide-loading")

        if self.config.native_scrollbars:
            options.append("native-scrollbars")

        if self.config.path_in_middle_panel:
            options.append("path-in-middle-panel")

        if self.config.suppress_warnings:
            options.append("suppress-warnings")

        if self.config.hide_schema_pattern:
            options.append("hide-schema-pattern")

        if self.config.expand_single_schema_field:
            options.append("expand-single-schema-field")

        if self.config.schema_expansion_level != 1:
            options.append(f'schema-expansion-level="{self.config.schema_expansion_level}"')

        # Search
        if self.config.disable_search:
            options.append("disable-search")

        if self.config.max_displayed_enum_values != 10:
            options.append(f'max-displayed-enum-values="{self.config.max_displayed_enum_values}"')

        # Code samples
        if self.config.show_extensions:
            options.append("show-extensions")

        if self.config.hide_schema_titles:
            options.append("hide-schema-titles")

        if self.config.simple_one_of_type_label:
            options.append("simple-one-of-type-label")

        if self.config.payload_sample_idx != 0:
            options.append(f'payload-sample-idx="{self.config.payload_sample_idx}"')

        # Logo
        if self.config.logo_url:
            options.append(f'logo="{self.config.logo_url}"')

        if self.config.logo_href:
            options.append(f'logo-href="{self.config.logo_href}"')

        # Return as space-separated attributes
        if options:
            return " " + " ".join(options)
        return ""

    def _get_favicon_tag(self) -> str:
        """Get favicon link tag."""
        if self.config.custom_favicon:
            return f'<link rel="icon" type="image/png" href="{self.config.custom_favicon}">'
        return ""

    def _build_custom_css(self) -> str:
        """Build custom CSS injection."""
        css_parts = []

        # Theme colors
        if any([self.config.primary_color, self.config.text_color, self.config.background_color]):
            theme_css = []
            if self.config.primary_color:
                theme_css.append(f"--primary-color: {self.config.primary_color};")
            if self.config.text_color:
                theme_css.append(f"--text-color: {self.config.text_color};")
            if self.config.background_color:
                theme_css.append(f"--background-color: {self.config.background_color};")

            css_parts.append(
                f"""
        :root {{
            {chr(10).join('            ' + line for line in theme_css)}
        }}"""
            )

        # Custom CSS
        if self.config.custom_css:
            css_parts.append(f"\n        {self.config.custom_css}")

        if css_parts:
            return f"""
    <style>{"".join(css_parts)}
    </style>"""
        return ""

    def _build_custom_js(self) -> str:
        """Build custom JavaScript injection."""
        if not self.config.custom_js:
            return ""

        return f"""
    <script>
        {self.config.custom_js}
    </script>"""

    def get_standalone_html(self, openapi_spec: Dict[str, Any]) -> str:
        """
        Generate standalone HTML with embedded OpenAPI spec.

        This creates a single HTML file with the OpenAPI spec embedded,
        which can be saved and distributed without needing a separate
        spec file or server.

        Args:
            openapi_spec: OpenAPI specification dictionary

        Returns:
            Complete standalone HTML string
        """
        import json

        spec_json = json.dumps(openapi_spec)
        redoc_options = self._build_redoc_options()
        custom_css = self._build_custom_css()
        custom_js = self._build_custom_js()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.title}</title>
    {self._get_favicon_tag()}
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    {custom_css}
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc@{self.redoc_version}/bundles/redoc.standalone.js"></script>
    <script>
        const spec = {spec_json};
        Redoc.init(spec, {{
            scrollYOffset: 50{self._build_js_options()}
        }}, document.getElementById('redoc-container'));
    </script>
    {custom_js}
</body>
</html>"""
        return html

    def _build_js_options(self) -> str:
        """Build JavaScript options object for Redoc.init()."""
        options = []

        if self.config.theme == ReDocTheme.DARK:
            options.append('theme: { colors: { primary: { main: "#dd5522" } } }')

        if self.config.hide_hostname:
            options.append("hideHostname: true")

        if self.config.expand_responses:
            codes = [f'"{c.strip()}"' for c in self.config.expand_responses.split(",")]
            options.append(f'expandResponses: {",".join(codes)}')

        if self.config.required_props_first:
            options.append("requiredPropsFirst: true")

        if self.config.disable_search:
            options.append("disableSearch: true")

        if self.config.native_scrollbars:
            options.append("nativeScrollbars: true")

        if options:
            return ",\n            " + ",\n            ".join(options)
        return ""


__all__ = [
    "ReDocUI",
    "ReDocConfig",
    "ReDocTheme",
]
