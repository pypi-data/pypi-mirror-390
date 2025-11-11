"""
OpenAPI 3.1 Schema Generation

Automatic OpenAPI 3.1 specification generation from route handlers and Pydantic models.
Provides interactive API documentation (Swagger UI, ReDoc).
"""

import inspect
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints

from pydantic import BaseModel


class OpenAPIGenerator:
    """
    Generate OpenAPI 3.1 specification from application routes.

    Features:
    - Automatic schema generation from Pydantic models
    - Request/response body documentation
    - Path/query parameter documentation
    - Security schemes (JWT, API Key, OAuth2)
    - Tags and operation grouping
    - Examples and descriptions

    Example:
        generator = OpenAPIGenerator(
            title="My API",
            version="1.0.0",
            description="API documentation"
        )
        spec = generator.generate_spec(routes)
    """

    def __init__(
        self,
        title: str,
        version: str,
        description: Optional[str] = None,
        contact: Optional[Dict[str, str]] = None,
        license_info: Optional[Dict[str, str]] = None,
        servers: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Initialize OpenAPI generator.

        Args:
            title: API title
            version: API version
            description: API description
            contact: Contact information
            license_info: License information
            servers: List of server objects
        """
        self.title = title
        self.version = version
        self.description = description or ""
        self.contact = contact
        self.license_info = license_info
        self.servers = servers or [{"url": "/"}]

        self.paths: Dict[str, Dict[str, Any]] = {}
        self.components: Dict[str, Dict[str, Any]] = {
            "schemas": {},
            "securitySchemes": {},
        }
        self.tags: List[Dict[str, str]] = []

    def add_route(
        self,
        path: str,
        method: str,
        handler: Callable,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        responses: Optional[Dict[int, Dict[str, Any]]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
    ):
        """
        Add route to OpenAPI spec.

        Args:
            path: URL path (e.g., "/users/{user_id}")
            method: HTTP method (GET, POST, etc.)
            handler: Route handler function
            summary: Short summary
            description: Detailed description
            tags: Operation tags for grouping
            request_model: Pydantic model for request body
            response_model: Pydantic model for response body
            responses: Additional response definitions
            security: Security requirements
        """
        method = method.lower()

        # Initialize path if not exists
        if path not in self.paths:
            self.paths[path] = {}

        # Extract info from handler
        if not summary:
            summary = handler.__name__.replace("_", " ").title()

        if not description and handler.__doc__:
            description = inspect.cleandoc(handler.__doc__)

        # Build operation object
        operation: Dict[str, Any] = {
            "summary": summary,
            "operationId": f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
        }

        if description:
            operation["description"] = description

        if tags:
            operation["tags"] = tags

        # Parameters (path and query)
        parameters = self._extract_parameters(path, handler)
        if parameters:
            operation["parameters"] = parameters

        # Request body
        if request_model:
            operation["requestBody"] = self._create_request_body(request_model)
            self._add_schema_component(request_model)

        # Responses
        operation["responses"] = {}

        # Success response
        if response_model:
            operation["responses"]["200"] = self._create_response(response_model)
            self._add_schema_component(response_model)
        else:
            operation["responses"]["200"] = {"description": "Successful response"}

        # Additional responses
        if responses:
            operation["responses"].update(responses)

        # Default error responses
        if "400" not in operation["responses"]:
            operation["responses"]["400"] = {"description": "Bad Request"}
        if "500" not in operation["responses"]:
            operation["responses"]["500"] = {"description": "Internal Server Error"}

        # Security
        if security:
            operation["security"] = security

        self.paths[path][method] = operation

    def _extract_parameters(self, path: str, handler: Callable) -> List[Dict[str, Any]]:
        """Extract path and query parameters from route."""
        parameters = []

        # Path parameters
        path_params = [
            p.strip("{}") for p in path.split("/") if p.startswith("{") and p.endswith("}")
        ]

        # Get type hints from handler
        hints = get_type_hints(handler)

        for param in path_params:
            param_type = hints.get(param, str)
            parameters.append(
                {
                    "name": param,
                    "in": "path",
                    "required": True,
                    "schema": self._python_type_to_openapi(param_type),
                }
            )

        # Query parameters (from handler signature)
        sig = inspect.signature(handler)
        for param_name, param in sig.parameters.items():
            if param_name in ["request", "self"]:
                continue

            if param_name not in path_params:
                param_type = hints.get(param_name, str)
                parameters.append(
                    {
                        "name": param_name,
                        "in": "query",
                        "required": param.default == inspect.Parameter.empty,
                        "schema": self._python_type_to_openapi(param_type),
                    }
                )

        return parameters

    def _python_type_to_openapi(self, python_type: Type) -> Dict[str, str]:
        """Convert Python type to OpenAPI schema type."""
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            list: {"type": "array", "items": {"type": "string"}},
            dict: {"type": "object"},
        }
        return type_map.get(python_type, {"type": "string"})

    def _create_request_body(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Create request body definition."""
        return {
            "required": True,
            "content": {
                "application/json": {"schema": {"$ref": f"#/components/schemas/{model.__name__}"}}
            },
        }

    def _create_response(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Create response definition."""
        return {
            "description": "Successful response",
            "content": {
                "application/json": {"schema": {"$ref": f"#/components/schemas/{model.__name__}"}}
            },
        }

    def _add_schema_component(self, model: Type[BaseModel]):
        """Add Pydantic model to components/schemas."""
        if model.__name__ not in self.components["schemas"]:
            self.components["schemas"][model.__name__] = model.schema()

    def add_security_scheme(
        self,
        name: str,
        scheme_type: str,
        scheme: Optional[str] = None,
        bearer_format: Optional[str] = None,
        flows: Optional[Dict[str, Any]] = None,
    ):
        """
        Add security scheme to OpenAPI spec.

        Args:
            name: Security scheme name
            scheme_type: Type (apiKey, http, oauth2, openIdConnect)
            scheme: HTTP scheme (bearer, basic, etc.)
            bearer_format: Bearer token format (e.g., JWT)
            flows: OAuth2 flows
        """
        security_scheme: Dict[str, Any] = {"type": scheme_type}

        if scheme:
            security_scheme["scheme"] = scheme

        if bearer_format:
            security_scheme["bearerFormat"] = bearer_format

        if flows:
            security_scheme["flows"] = flows

        self.components["securitySchemes"][name] = security_scheme

    def add_tag(self, name: str, description: Optional[str] = None):
        """
        Add tag for grouping operations.

        Args:
            name: Tag name
            description: Tag description
        """
        tag = {"name": name}
        if description:
            tag["description"] = description

        if tag not in self.tags:
            self.tags.append(tag)

    def generate_spec(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI 3.1 specification.

        Returns:
            OpenAPI spec dictionary
        """
        spec = {
            "openapi": "3.1.0",
            "info": {
                "title": self.title,
                "version": self.version,
                "description": self.description,
            },
            "servers": self.servers,
            "paths": self.paths,
            "components": self.components,
        }

        if self.contact:
            spec["info"]["contact"] = self.contact

        if self.license_info:
            spec["info"]["license"] = self.license_info

        if self.tags:
            spec["tags"] = self.tags

        return spec


class SwaggerUIConfig:
    """Configuration for Swagger UI."""

    def __init__(
        self,
        url: str = "/openapi.json",
        title: str = "API Documentation",
        persist_authorization: bool = True,
    ):
        """
        Initialize Swagger UI config.

        Args:
            url: URL to OpenAPI spec
            title: Page title
            persist_authorization: Persist auth between refreshes
        """
        self.url = url
        self.title = title
        self.persist_authorization = persist_authorization

    def get_html(self) -> str:
        """Generate Swagger UI HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui.css">
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: "{self.url}",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                persistAuthorization: {str(self.persist_authorization).lower()}
            }});
            window.ui = ui;
        }};
    </script>
</body>
</html>
"""


class ReDocConfig:
    """Configuration for ReDoc."""

    def __init__(self, url: str = "/openapi.json", title: str = "API Documentation"):
        """
        Initialize ReDoc config.

        Args:
            url: URL to OpenAPI spec
            title: Page title
        """
        self.url = url
        self.title = title

    def get_html(self) -> str:
        """Generate ReDoc HTML."""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url="{self.url}"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.3/bundles/redoc.standalone.js"></script>
</body>
</html>
"""


__all__ = [
    "OpenAPIGenerator",
    "SwaggerUIConfig",
    "ReDocConfig",
]
