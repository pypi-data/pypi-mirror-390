"""
CovetPy API Documentation Generation

Production-grade API documentation tools for REST and GraphQL APIs.
Provides automatic OpenAPI spec generation, interactive documentation,
and multiple export formats.

Features:
- OpenAPI 3.0/3.1 specification generation
- Swagger UI and ReDoc interfaces
- Markdown documentation export
- Postman collection export
- Automatic example generation
- Multiple language code samples

Example:
    from covet.api.docs import OpenAPIGenerator, SwaggerUI

    generator = OpenAPIGenerator(
        title="My API",
        version="1.0.0",
        description="Production API"
    )

    # Add routes from your application
    generator.add_route(
        path="/users",
        method="GET",
        response_model=UserListResponse
    )

    # Generate OpenAPI spec
    spec = generator.generate_spec()

    # Serve documentation
    swagger = SwaggerUI(spec_url="/openapi.json")
    html = swagger.get_html()
"""

from .example_generator import (
    ExampleConfig,
    ExampleGenerator,
    RequestExample,
    ResponseExample,
)
from .markdown_generator import (
    CodeLanguage,
    MarkdownConfig,
    MarkdownFormat,
    MarkdownGenerator,
)
from .openapi_generator import (
    OpenAPIGenerator,
    OpenAPIOperation,
    OpenAPIParameter,
    OpenAPIPath,
    OpenAPIRequestBody,
    OpenAPIResponse,
    OpenAPISchema,
    ParameterLocation,
    SecurityScheme,
    SecuritySchemeType,
)
from .postman_collection import (
    PostmanAuth,
    PostmanCollection,
    PostmanEnvironment,
    PostmanFolder,
    PostmanRequest,
)
from .redoc_ui import ReDocConfig, ReDocTheme, ReDocUI
from .swagger_ui import SwaggerUI, SwaggerUIConfig, SwaggerUITheme

__all__ = [
    # OpenAPI Generation
    "OpenAPIGenerator",
    "OpenAPISchema",
    "SecurityScheme",
    "SecuritySchemeType",
    "ParameterLocation",
    "OpenAPIParameter",
    "OpenAPIRequestBody",
    "OpenAPIResponse",
    "OpenAPIOperation",
    "OpenAPIPath",
    # Swagger UI
    "SwaggerUI",
    "SwaggerUIConfig",
    "SwaggerUITheme",
    # ReDoc
    "ReDocUI",
    "ReDocConfig",
    "ReDocTheme",
    # Markdown
    "MarkdownGenerator",
    "MarkdownConfig",
    "MarkdownFormat",
    "CodeLanguage",
    # Examples
    "ExampleGenerator",
    "ExampleConfig",
    "RequestExample",
    "ResponseExample",
    # Postman
    "PostmanCollection",
    "PostmanRequest",
    "PostmanFolder",
    "PostmanAuth",
    "PostmanEnvironment",
]

__version__ = "1.0.0"
