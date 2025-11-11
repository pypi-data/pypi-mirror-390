"""
Swagger UI Integration

Embedded Swagger UI for interactive API documentation. Provides a complete
web-based interface for exploring and testing APIs with OAuth2 authentication
support, request/response visualization, and try-it-out functionality.

Features:
- Full Swagger UI 5.x integration
- OAuth2 authorization flow support
- Try-it-out functionality with request execution
- Custom branding and theming
- Persistent authentication
- Request/response examples
- Model schema visualization
- Dark mode support
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class SwaggerUITheme(str, Enum):
    """Swagger UI color themes."""

    LIGHT = "light"
    DARK = "dark"


class SwaggerUIConfig(BaseModel):
    """
    Configuration for Swagger UI.

    Provides comprehensive customization options for the Swagger UI interface
    including theming, authentication, validation, and behavior.

    Example:
        config = SwaggerUIConfig(
            spec_url="/openapi.json",
            title="My API Documentation",
            oauth2_redirect_url="https://api.example.com/docs/oauth2-redirect",
            persist_authorization=True,
            display_request_duration=True,
            theme=SwaggerUITheme.DARK
        )
    """

    spec_url: str = Field(default="/openapi.json", description="URL to OpenAPI specification")
    title: str = Field(default="API Documentation", description="Page title")
    persist_authorization: bool = Field(
        default=True, description="Persist authorization between page refreshes"
    )
    display_request_duration: bool = Field(
        default=True, description="Display request execution duration"
    )
    display_operation_id: bool = Field(default=True, description="Display operation IDs")
    deep_linking: bool = Field(default=True, description="Enable deep linking for operations")
    default_models_expand_depth: int = Field(
        default=1, ge=-1, le=5, description="Default expansion depth for models (-1 for all)"
    )
    default_model_expand_depth: int = Field(
        default=1,
        ge=-1,
        le=5,
        description="Default expansion depth for model on model-example section",
    )
    filter: Optional[str] = Field(
        default=None, description="Enable filtering by tags (true/false/string)"
    )
    show_extensions: bool = Field(default=False, description="Show vendor extension (x-) fields")
    show_common_extensions: bool = Field(
        default=False, description="Show common extension (pattern, maxLength, etc.) fields"
    )
    try_it_out_enabled: bool = Field(
        default=True, description="Enable try-it-out section by default"
    )
    request_snippets_enabled: bool = Field(
        default=True, description="Enable request snippets section"
    )
    supported_submit_methods: List[str] = Field(
        default=["get", "put", "post", "delete", "options", "head", "patch", "trace"],
        description="List of HTTP methods that can be tried out",
    )
    oauth2_redirect_url: Optional[str] = Field(default=None, description="OAuth2 redirect URL")
    with_credentials: bool = Field(default=False, description="Send cookies with requests")
    validator_url: Optional[str] = Field(
        default=None, description="URL to validate spec (null to disable)"
    )
    theme: SwaggerUITheme = Field(default=SwaggerUITheme.LIGHT, description="UI color theme")
    syntax_highlight_theme: str = Field(
        default="agate", description="Syntax highlighting theme (agate, arta, monokai, etc.)"
    )
    # Custom branding
    custom_css: Optional[str] = Field(default=None, description="Custom CSS to inject")
    custom_js: Optional[str] = Field(default=None, description="Custom JavaScript to inject")
    custom_favicon: Optional[str] = Field(default=None, description="URL to custom favicon")
    custom_site_title: Optional[str] = Field(
        default=None, description="Custom site title (overrides title in <title> tag)"
    )

    class Config:
        use_enum_values = True


class SwaggerUI:
    """
    Swagger UI renderer with full customization support.

    Provides methods to generate HTML for embedding Swagger UI in web applications
    with comprehensive configuration options, OAuth2 support, and custom branding.

    Example:
        # Basic usage
        swagger = SwaggerUI(
            config=SwaggerUIConfig(
                spec_url="/openapi.json",
                title="My API"
            )
        )
        html = swagger.get_html()

        # With OAuth2
        swagger = SwaggerUI(
            config=SwaggerUIConfig(
                spec_url="/openapi.json",
                oauth2_redirect_url="https://api.example.com/docs/oauth2-redirect",
                persist_authorization=True
            )
        )

        # Serve in ASGI app
        @app.route("/docs")
        async def docs(request):
            return HTMLResponse(swagger.get_html())
    """

    def __init__(
        self,
        config: Optional[SwaggerUIConfig] = None,
        swagger_ui_version: str = "5.11.0",
    ):
        """
        Initialize Swagger UI.

        Args:
            config: Swagger UI configuration
            swagger_ui_version: Version of Swagger UI to use
        """
        self.config = config or SwaggerUIConfig()
        self.swagger_ui_version = swagger_ui_version

    def get_html(self) -> str:
        """
        Generate complete HTML page with embedded Swagger UI.

        Returns:
            HTML string ready to serve
        """
        # Build Swagger UI configuration
        ui_config = self._build_ui_config()

        # Build custom CSS
        custom_css = self._build_custom_css()

        # Build custom JS
        custom_js = self._build_custom_js()

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.config.custom_site_title or self.config.title}</title>
    {self._get_favicon_tag()}
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui.css">
    {custom_css}
    <style>
        html {{ box-sizing: border-box; overflow-y: scroll; }}
        *, *:before, *:after {{ box-sizing: inherit; }}
        body {{
            margin: 0;
            padding: 0;
            {self._get_theme_styles()}
        }}
        .swagger-ui .topbar {{ display: none; }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "{self.config.spec_url}",
                dom_id: '#swagger-ui',
                deepLinking: {str(self.config.deep_linking).lower()},
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                {ui_config}
            }});

            window.ui = ui;

            {self._get_oauth2_init()}
        }};
    </script>
    {custom_js}
</body>
</html>"""
        return html

    def _build_ui_config(self) -> str:
        """Build JavaScript configuration object for Swagger UI."""
        config_parts = []

        if self.config.persist_authorization:
            config_parts.append(
                f"persistAuthorization: {str(self.config.persist_authorization).lower()}"
            )

        if self.config.display_request_duration:
            config_parts.append(
                f"displayRequestDuration: {str(self.config.display_request_duration).lower()}"
            )

        if self.config.display_operation_id:
            config_parts.append(
                f"displayOperationId: {str(self.config.display_operation_id).lower()}"
            )

        if self.config.default_models_expand_depth is not None:
            config_parts.append(
                f"defaultModelsExpandDepth: {self.config.default_models_expand_depth}"
            )

        if self.config.default_model_expand_depth is not None:
            config_parts.append(
                f"defaultModelExpandDepth: {self.config.default_model_expand_depth}"
            )

        if self.config.filter:
            config_parts.append(f"filter: {self.config.filter}")

        if self.config.show_extensions:
            config_parts.append(f"showExtensions: {str(self.config.show_extensions).lower()}")

        if self.config.show_common_extensions:
            config_parts.append(
                f"showCommonExtensions: {str(self.config.show_common_extensions).lower()}"
            )

        if self.config.try_it_out_enabled:
            config_parts.append(f"tryItOutEnabled: {str(self.config.try_it_out_enabled).lower()}")

        if self.config.request_snippets_enabled:
            config_parts.append(
                f"requestSnippetsEnabled: {str(self.config.request_snippets_enabled).lower()}"
            )

        if self.config.supported_submit_methods:
            methods = ", ".join([f'"{m}"' for m in self.config.supported_submit_methods])
            config_parts.append(f"supportedSubmitMethods: [{methods}]")

        if self.config.with_credentials:
            config_parts.append(f"withCredentials: {str(self.config.with_credentials).lower()}")

        if self.config.validator_url is not None:
            if self.config.validator_url:
                config_parts.append(f'validatorUrl: "{self.config.validator_url}"')
            else:
                config_parts.append("validatorUrl: null")

        return ",\n                ".join(config_parts)

    def _get_oauth2_init(self) -> str:
        """Generate OAuth2 initialization code."""
        if not self.config.oauth2_redirect_url:
            return ""

        return f"""
            // OAuth2 configuration
            ui.initOAuth({{
                clientId: "your-client-id",
                clientSecret: "your-client-secret-if-required",
                realm: "your-realms",
                appName: "{self.config.title}",
                scopeSeparator: " ",
                scopes: "openid profile email",
                additionalQueryStringParams: {{}},
                useBasicAuthenticationWithAccessCodeGrant: false,
                usePkceWithAuthorizationCodeGrant: true
            }});"""

    def _get_theme_styles(self) -> str:
        """Get CSS for selected theme."""
        if self.config.theme == SwaggerUITheme.DARK:
            return """
            background-color: #1f1f1f;
            color: #f0f0f0;
        """
        return ""

    def _get_favicon_tag(self) -> str:
        """Get favicon link tag."""
        if self.config.custom_favicon:
            return f'<link rel="icon" type="image/png" href="{self.config.custom_favicon}">'
        return '<link rel="icon" type="image/png" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{}/favicon-32x32.png">'.format(
            self.swagger_ui_version
        )

    def _build_custom_css(self) -> str:
        """Build custom CSS injection."""
        if not self.config.custom_css:
            return ""

        return f"""
    <style>
        {self.config.custom_css}
    </style>"""

    def _build_custom_js(self) -> str:
        """Build custom JavaScript injection."""
        if not self.config.custom_js:
            return ""

        return f"""
    <script>
        {self.config.custom_js}
    </script>"""

    def get_oauth2_redirect_html(self) -> str:
        """
        Generate OAuth2 redirect page.

        This page handles the OAuth2 redirect flow and must be served
        at the URL specified in oauth2_redirect_url.

        Returns:
            HTML string for OAuth2 redirect page
        """
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>OAuth2 Redirect</title>
</head>
<body>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@{self.swagger_ui_version}/swagger-ui-standalone-preset.js"></script>
    <script>
        'use strict';
        (function() {{
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {{
                qp = window.location.hash.substring(1).replace('?', '&');
            }} else {{
                qp = location.search.substring(1);
            }}

            arr = qp.split("&");
            arr.forEach(function (v,i,_arr) {{ _arr[i] = '"' + v.replace('=', '":"') + '"';}});
            qp = qp ? JSON.parse('{{' + arr.join() + '}}',
                    function (key, value) {{
                        return key === "" ? value : decodeURIComponent(value);
                    }}
            ) : {{}};

            isValid = qp.state === sentState;

            if ((
              oauth2.auth.schema.get("flow") === "accessCode" ||
              oauth2.auth.schema.get("flow") === "authorizationCode" ||
              oauth2.auth.schema.get("flow") === "authorization_code"
            ) && !oauth2.auth.code) {{
                if (!isValid) {{
                    oauth2.errCb({{
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                    }});
                }}

                if (qp.code) {{
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({{auth: oauth2.auth, redirectUrl: redirectUrl}});
                }} else {{
                    let oauthErrorMsg;
                    if (qp.error) {{
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }}

                    oauth2.errCb({{
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                    }});
                }}
            }} else {{
                oauth2.callback({{auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl}});
            }}
            window.close();
        }})();
    </script>
</body>
</html>"""


__all__ = [
    "SwaggerUI",
    "SwaggerUIConfig",
    "SwaggerUITheme",
]
