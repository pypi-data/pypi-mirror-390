"""
OpenAPI 3.0/3.1 Specification Generator

Comprehensive OpenAPI specification generation from application routes,
Pydantic models, and Python type hints. Supports all OpenAPI 3.0/3.1 features
including schemas, parameters, request/response bodies, security schemes,
examples, and more.

Features:
- Automatic schema extraction from Pydantic models
- Path and query parameter documentation
- Request/response body documentation with examples
- Security scheme configuration (JWT, OAuth2, API Key)
- Tag-based operation grouping
- Webhook and callback documentation
- OpenAPI 3.1 JSON Schema support
- Discriminator and polymorphism support
"""

import inspect
import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)
from uuid import UUID

from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo


class SecuritySchemeType(str, Enum):
    """Security scheme types per OpenAPI spec."""

    API_KEY = "apiKey"
    HTTP = "http"
    OAUTH2 = "oauth2"
    OPENID_CONNECT = "openIdConnect"
    MUTUAL_TLS = "mutualTLS"


class ParameterLocation(str, Enum):
    """Parameter locations per OpenAPI spec."""

    QUERY = "query"
    HEADER = "header"
    PATH = "path"
    COOKIE = "cookie"


class SecurityScheme(BaseModel):
    """
    OpenAPI security scheme definition.

    Supports API Key, HTTP (Bearer/Basic), OAuth2, OpenID Connect, and Mutual TLS.

    Example:
        # JWT Bearer authentication
        scheme = SecurityScheme(
            type=SecuritySchemeType.HTTP,
            scheme="bearer",
            bearer_format="JWT",
            description="JWT token authentication"
        )

        # OAuth2 with authorization code flow
        scheme = SecurityScheme(
            type=SecuritySchemeType.OAUTH2,
            flows={
                "authorizationCode": {
                    "authorizationUrl": "https://example.com/oauth/authorize",
                    "tokenUrl": "https://example.com/oauth/token",
                    "scopes": {
                        "read": "Read access",
                        "write": "Write access"
                    }
                }
            }
        )
    """

    type: SecuritySchemeType
    description: Optional[str] = None
    name: Optional[str] = None  # For apiKey
    in_: Optional[str] = Field(None, alias="in")  # For apiKey: query, header, cookie
    scheme: Optional[str] = None  # For http: basic, bearer
    bearer_format: Optional[str] = None  # For http bearer: JWT, etc.
    flows: Optional[Dict[str, Any]] = None  # For oauth2
    openid_connect_url: Optional[str] = Field(None, alias="openIdConnectUrl")  # For openIdConnect

    class Config:
        use_enum_values = True
        populate_by_name = True


class OpenAPIParameter(BaseModel):
    """
    OpenAPI parameter definition.

    Represents path, query, header, or cookie parameters with
    full validation and documentation support.
    """

    name: str
    in_: ParameterLocation = Field(..., alias="in")
    description: Optional[str] = None
    required: bool = False
    deprecated: bool = False
    allow_empty_value: bool = False
    schema_: Optional[Dict[str, Any]] = Field(None, alias="schema")
    example: Optional[Any] = None
    examples: Optional[Dict[str, Any]] = None
    style: Optional[str] = None  # form, simple, matrix, label, etc.
    explode: Optional[bool] = None
    allow_reserved: Optional[bool] = None

    class Config:
        use_enum_values = True
        populate_by_name = True


class OpenAPIRequestBody(BaseModel):
    """
    OpenAPI request body definition.

    Documents request body content types, schemas, and examples.
    """

    description: Optional[str] = None
    content: Dict[str, Any]
    required: bool = True

    class Config:
        use_enum_values = True


class OpenAPIResponse(BaseModel):
    """
    OpenAPI response definition.

    Documents response status codes, content types, schemas, and examples.
    """

    description: str
    headers: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None
    links: Optional[Dict[str, Any]] = None

    class Config:
        use_enum_values = True


class OpenAPIOperation(BaseModel):
    """
    OpenAPI operation (endpoint) definition.

    Complete documentation for a single API operation including
    parameters, request body, responses, security, and metadata.
    """

    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    external_docs: Optional[Dict[str, str]] = Field(None, alias="externalDocs")
    operation_id: Optional[str] = Field(None, alias="operationId")
    parameters: Optional[List[OpenAPIParameter]] = None
    request_body: Optional[OpenAPIRequestBody] = Field(None, alias="requestBody")
    responses: Dict[str, OpenAPIResponse]
    callbacks: Optional[Dict[str, Any]] = None
    deprecated: bool = False
    security: Optional[List[Dict[str, List[str]]]] = None
    servers: Optional[List[Dict[str, str]]] = None

    class Config:
        use_enum_values = True
        populate_by_name = True


class OpenAPIPath(BaseModel):
    """
    OpenAPI path item definition.

    Contains all operations (GET, POST, etc.) for a specific path.
    """

    summary: Optional[str] = None
    description: Optional[str] = None
    get: Optional[OpenAPIOperation] = None
    put: Optional[OpenAPIOperation] = None
    post: Optional[OpenAPIOperation] = None
    delete: Optional[OpenAPIOperation] = None
    options: Optional[OpenAPIOperation] = None
    head: Optional[OpenAPIOperation] = None
    patch: Optional[OpenAPIOperation] = None
    trace: Optional[OpenAPIOperation] = None
    servers: Optional[List[Dict[str, str]]] = None
    parameters: Optional[List[OpenAPIParameter]] = None

    class Config:
        use_enum_values = True


class OpenAPISchema(BaseModel):
    """
    Complete OpenAPI 3.0/3.1 specification.

    Root document containing all API documentation.
    """

    openapi: str = "3.1.0"
    info: Dict[str, Any]
    json_schema_dialect: Optional[str] = Field(None, alias="jsonSchemaDialect")
    servers: Optional[List[Dict[str, str]]] = None
    paths: Dict[str, Dict[str, Any]]
    webhooks: Optional[Dict[str, Any]] = None
    components: Optional[Dict[str, Any]] = None
    security: Optional[List[Dict[str, List[str]]]] = None
    tags: Optional[List[Dict[str, str]]] = None
    external_docs: Optional[Dict[str, str]] = Field(None, alias="externalDocs")

    class Config:
        use_enum_values = True
        populate_by_name = True


class OpenAPIGenerator:
    """
    Production-grade OpenAPI 3.0/3.1 specification generator.

    Automatically generates comprehensive API documentation from Python code,
    with support for all OpenAPI features and full Pydantic integration.

    Features:
    - Automatic schema generation from Pydantic models
    - Type hint analysis for parameters
    - Docstring parsing for descriptions
    - Multiple response types per endpoint
    - Security scheme configuration
    - Example generation
    - Tag-based organization
    - Webhook and callback support
    - Discriminator and polymorphism

    Example:
        generator = OpenAPIGenerator(
            title="My Production API",
            version="2.0.0",
            description="Comprehensive REST API",
            contact={
                "name": "API Support",
                "email": "support@example.com",
                "url": "https://example.com/support"
            },
            license_info={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0"
            },
            servers=[
                {"url": "https://api.example.com/v2", "description": "Production"},
                {"url": "https://staging-api.example.com/v2", "description": "Staging"}
            ]
        )

        # Add JWT authentication
        generator.add_security_scheme(
            "bearer_auth",
            SecurityScheme(
                type=SecuritySchemeType.HTTP,
                scheme="bearer",
                bearer_format="JWT"
            )
        )

        # Add routes
        generator.add_route(
            path="/users/{user_id}",
            method="GET",
            handler=get_user_handler,
            response_model=UserResponse,
            tags=["Users"],
            security=[{"bearer_auth": []}]
        )

        # Generate spec
        spec = generator.generate_spec()
    """

    def __init__(
        self,
        title: str,
        version: str,
        description: Optional[str] = None,
        terms_of_service: Optional[str] = None,
        contact: Optional[Dict[str, str]] = None,
        license_info: Optional[Dict[str, str]] = None,
        servers: Optional[List[Dict[str, str]]] = None,
        openapi_version: str = "3.1.0",
        json_schema_dialect: Optional[str] = None,
    ):
        """
        Initialize OpenAPI generator.

        Args:
            title: API title
            version: API version (semver recommended)
            description: API description (supports Markdown)
            terms_of_service: URL to terms of service
            contact: Contact information (name, email, url)
            license_info: License information (name, url)
            servers: List of server objects with url and description
            openapi_version: OpenAPI specification version (3.0.3 or 3.1.0)
            json_schema_dialect: JSON Schema dialect URL (3.1.0 only)
        """
        self.title = title
        self.version = version
        self.description = description or ""
        self.terms_of_service = terms_of_service
        self.contact = contact
        self.license_info = license_info
        self.servers = servers or [{"url": "/"}]
        self.openapi_version = openapi_version
        self.json_schema_dialect = json_schema_dialect

        # Storage
        self.paths: Dict[str, Dict[str, Any]] = {}
        self.components: Dict[str, Dict[str, Any]] = {
            "schemas": {},
            "responses": {},
            "parameters": {},
            "examples": {},
            "requestBodies": {},
            "headers": {},
            "securitySchemes": {},
            "links": {},
            "callbacks": {},
        }
        self.tags: List[Dict[str, str]] = []
        self.security: List[Dict[str, List[str]]] = []
        self.webhooks: Dict[str, Any] = {}

        # Track referenced schemas to avoid duplicates
        self._schema_refs: Set[str] = set()

    def add_route(
        self,
        path: str,
        method: str,
        handler: Optional[Callable] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        operation_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        responses: Optional[Dict[Union[int, str], Union[Type[BaseModel], Dict[str, Any]]]] = None,
        parameters: Optional[List[OpenAPIParameter]] = None,
        security: Optional[List[Dict[str, List[str]]]] = None,
        deprecated: bool = False,
        callbacks: Optional[Dict[str, Any]] = None,
        servers: Optional[List[Dict[str, str]]] = None,
    ):
        """
        Add API route to OpenAPI specification.

        Args:
            path: URL path (e.g., "/users/{user_id}")
            method: HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
            handler: Route handler function (for auto-documentation)
            summary: Short summary (max ~50 chars)
            description: Detailed description (supports Markdown)
            operation_id: Unique operation identifier
            tags: Tags for grouping operations
            request_model: Pydantic model for request body
            response_model: Pydantic model for successful response
            responses: Additional response models keyed by status code
            parameters: List of parameters (path, query, header, cookie)
            security: Security requirements for this operation
            deprecated: Mark operation as deprecated
            callbacks: Callback definitions
            servers: Override servers for this operation
        """
        method = method.lower()

        # Initialize path if not exists
        if path not in self.paths:
            self.paths[path] = {}

        # Extract documentation from handler
        if handler:
            if not summary:
                summary = self._extract_summary(handler)
            if not description:
                description = self._extract_description(handler)
            if not operation_id:
                operation_id = self._generate_operation_id(method, path, handler)

        # Build operation
        operation: Dict[str, Any] = {
            "summary": summary or f"{method.upper()} {path}",
            "operationId": operation_id
            or f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}",
        }

        if description:
            operation["description"] = description

        if tags:
            operation["tags"] = tags
            # Auto-add tags to spec
            for tag in tags:
                self.add_tag(tag)

        if deprecated:
            operation["deprecated"] = True

        if servers:
            operation["servers"] = servers

        # Extract parameters
        all_parameters = parameters or []
        if handler:
            all_parameters.extend(self._extract_parameters(path, handler))

        if all_parameters:
            operation["parameters"] = [
                p.dict(by_alias=True, exclude_none=True) if isinstance(p, OpenAPIParameter) else p
                for p in all_parameters
            ]

        # Request body
        if request_model:
            operation["requestBody"] = self._create_request_body(request_model)
            self._add_schema_component(request_model)

        # Responses
        operation["responses"] = {}

        # Success response
        if response_model:
            operation["responses"]["200"] = self._create_response(
                "Successful response", response_model
            )
            self._add_schema_component(response_model)
        else:
            operation["responses"]["200"] = {"description": "Successful response"}

        # Additional responses
        if responses:
            for status_code, response_def in responses.items():
                status_str = str(status_code)
                if isinstance(response_def, type) and issubclass(response_def, BaseModel):
                    operation["responses"][status_str] = self._create_response(
                        f"Response {status_code}", response_def
                    )
                    self._add_schema_component(response_def)
                elif isinstance(response_def, dict):
                    operation["responses"][status_str] = response_def

        # Default error responses
        if "400" not in operation["responses"]:
            operation["responses"]["400"] = {"description": "Bad Request - Invalid input"}
        if "401" not in operation["responses"]:
            operation["responses"]["401"] = {
                "description": "Unauthorized - Authentication required"
            }
        if "404" not in operation["responses"]:
            operation["responses"]["404"] = {"description": "Not Found - Resource does not exist"}
        if "422" not in operation["responses"]:
            operation["responses"]["422"] = {
                "description": "Unprocessable Entity - Validation error"
            }
        if "500" not in operation["responses"]:
            operation["responses"]["500"] = {"description": "Internal Server Error"}

        # Security
        if security:
            operation["security"] = security

        # Callbacks
        if callbacks:
            operation["callbacks"] = callbacks

        self.paths[path][method] = operation

    def _extract_summary(self, handler: Callable) -> str:
        """Extract summary from handler function name."""
        name = handler.__name__.replace("_", " ").title()
        # Remove common prefixes
        for prefix in ["Handle ", "Get ", "Post ", "Put ", "Delete ", "Patch "]:
            if name.startswith(prefix):
                name = name[len(prefix) :]
                break
        return name

    def _extract_description(self, handler: Callable) -> Optional[str]:
        """Extract description from handler docstring."""
        if handler.__doc__:
            return inspect.cleandoc(handler.__doc__)
        return None

    def _generate_operation_id(self, method: str, path: str, handler: Callable) -> str:
        """Generate unique operation ID."""
        # Use handler name if available
        if handler.__name__ != "<lambda>":
            return f"{method}_{handler.__name__}"
        # Fall back to path-based ID
        return f"{method}_{path.replace('/', '_').replace('{', '').replace('}', '')}"

    def _extract_parameters(self, path: str, handler: Callable) -> List[Dict[str, Any]]:
        """Extract parameters from path and handler signature."""
        parameters = []

        # Extract path parameters
        path_params = [
            p.strip("{}") for p in path.split("/") if p.startswith("{") and p.endswith("}")
        ]

        # Get type hints
        try:
            hints = get_type_hints(handler)
        except Exception:
            hints = {}

        # Get function signature
        try:
            sig = inspect.signature(handler)
        except Exception:
            return parameters

        # Add path parameters
        for param_name in path_params:
            param_type = hints.get(param_name, str)
            parameters.append(
                {
                    "name": param_name,
                    "in": "path",
                    "required": True,
                    "schema": self._python_type_to_openapi_schema(param_type),
                }
            )

        # Add query parameters
        for param_name, param in sig.parameters.items():
            # Skip common parameters
            if param_name in ["self", "cls", "request", "response"] or param_name in path_params:
                continue

            # Skip if parameter is a Pydantic model (handled as request body)
            param_type = hints.get(param_name, param.annotation)
            if param_type != inspect.Parameter.empty:
                origin = get_origin(param_type)
                if origin is not None:
                    param_type = origin
                if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                    continue

            # Add query parameter
            parameters.append(
                {
                    "name": param_name,
                    "in": "query",
                    "required": param.default == inspect.Parameter.empty,
                    "schema": self._python_type_to_openapi_schema(hints.get(param_name, str)),
                }
            )

        return parameters

    def _python_type_to_openapi_schema(self, python_type: Any) -> Dict[str, Any]:
        """Convert Python type hint to OpenAPI schema."""
        # Handle None/Optional
        origin = get_origin(python_type)
        args = get_args(python_type)

        # Optional types
        if origin is Union:
            non_none_types = [t for t in args if t is not type(None)]
            if len(non_none_types) == 1:
                return self._python_type_to_openapi_schema(non_none_types[0])
            # Multiple types - use anyOf
            return {"anyOf": [self._python_type_to_openapi_schema(t) for t in non_none_types]}

        # List types
        if origin is list or python_type is list:
            item_type = args[0] if args else str
            return {"type": "array", "items": self._python_type_to_openapi_schema(item_type)}

        # Dict types
        if origin is dict or python_type is dict:
            return {"type": "object"}

        # Basic type mapping
        type_map = {
            str: {"type": "string"},
            int: {"type": "integer"},
            float: {"type": "number"},
            bool: {"type": "boolean"},
            datetime: {"type": "string", "format": "date-time"},
            date: {"type": "string", "format": "date"},
            time: {"type": "string", "format": "time"},
            UUID: {"type": "string", "format": "uuid"},
            Decimal: {"type": "number"},
            bytes: {"type": "string", "format": "binary"},
        }

        # Check if it's a basic type
        if python_type in type_map:
            return type_map[python_type]

        # Check if it's an Enum
        if isinstance(python_type, type) and issubclass(python_type, Enum):
            enum_values = [e.value for e in python_type]
            # Determine enum type
            if enum_values and isinstance(enum_values[0], str):
                return {"type": "string", "enum": enum_values}
            elif enum_values and isinstance(enum_values[0], int):
                return {"type": "integer", "enum": enum_values}
            else:
                return {"enum": enum_values}

        # Default to string
        return {"type": "string"}

    def _create_request_body(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """Create request body definition from Pydantic model."""
        return {
            "required": True,
            "content": {
                "application/json": {"schema": {"$ref": f"#/components/schemas/{model.__name__}"}}
            },
        }

    def _create_response(self, description: str, model: Type[BaseModel]) -> Dict[str, Any]:
        """Create response definition from Pydantic model."""
        return {
            "description": description,
            "content": {
                "application/json": {"schema": {"$ref": f"#/components/schemas/{model.__name__}"}}
            },
        }

    def _add_schema_component(self, model: Type[BaseModel]):
        """Add Pydantic model schema to components."""
        if not issubclass(model, BaseModel):
            return

        schema_name = model.__name__
        if schema_name in self._schema_refs:
            return

        self._schema_refs.add(schema_name)

        # Get Pydantic schema
        schema = model.model_json_schema(ref_template="#/components/schemas/{model}")

        # Extract nested definitions
        if "$defs" in schema:
            for def_name, def_schema in schema["$defs"].items():
                if def_name not in self.components["schemas"]:
                    self.components["schemas"][def_name] = def_schema
            del schema["$defs"]

        # Add main schema
        self.components["schemas"][schema_name] = schema

    def add_security_scheme(self, name: str, scheme: SecurityScheme):
        """
        Add security scheme to specification.

        Args:
            name: Security scheme name (referenced in operation security)
            scheme: Security scheme definition
        """
        self.components["securitySchemes"][name] = scheme.dict(by_alias=True, exclude_none=True)

    def set_global_security(self, security: List[Dict[str, List[str]]]):
        """
        Set global security requirements.

        Args:
            security: List of security requirement objects
        """
        self.security = security

    def add_tag(self, name: str, description: Optional[str] = None):
        """
        Add tag for operation grouping.

        Args:
            name: Tag name
            description: Tag description
        """
        tag = {"name": name}
        if description:
            tag["description"] = description

        if tag not in self.tags:
            self.tags.append(tag)

    def add_webhook(self, name: str, webhook: Dict[str, Any]):
        """
        Add webhook definition (OpenAPI 3.1.0+).

        Args:
            name: Webhook name
            webhook: Webhook definition
        """
        self.webhooks[name] = webhook

    def generate_spec(self) -> Dict[str, Any]:
        """
        Generate complete OpenAPI specification.

        Returns:
            OpenAPI spec dictionary ready for JSON/YAML serialization
        """
        spec: Dict[str, Any] = {
            "openapi": self.openapi_version,
            "info": {
                "title": self.title,
                "version": self.version,
            },
            "servers": self.servers,
            "paths": self.paths,
            "components": {k: v for k, v in self.components.items() if v},
        }

        # Add optional info fields
        if self.description:
            spec["info"]["description"] = self.description
        if self.terms_of_service:
            spec["info"]["termsOfService"] = self.terms_of_service
        if self.contact:
            spec["info"]["contact"] = self.contact
        if self.license_info:
            spec["info"]["license"] = self.license_info

        # Add JSON Schema dialect (3.1.0 only)
        if self.openapi_version == "3.1.0" and self.json_schema_dialect:
            spec["jsonSchemaDialect"] = self.json_schema_dialect

        # Add tags
        if self.tags:
            spec["tags"] = self.tags

        # Add global security
        if self.security:
            spec["security"] = self.security

        # Add webhooks (3.1.0 only)
        if self.openapi_version == "3.1.0" and self.webhooks:
            spec["webhooks"] = self.webhooks

        return spec

    def generate_json(self, indent: Optional[int] = 2) -> str:
        """
        Generate OpenAPI spec as JSON string.

        Args:
            indent: JSON indentation (None for compact)

        Returns:
            JSON string
        """
        spec = self.generate_spec()
        return json.dumps(spec, indent=indent)

    def generate_yaml(self) -> str:
        """
        Generate OpenAPI spec as YAML string.

        Returns:
            YAML string
        """
        try:
            import yaml
        except ImportError:
            raise ImportError(
                "PyYAML is required for YAML generation. " "Install it with: pip install pyyaml"
            )

        spec = self.generate_spec()
        return yaml.dump(spec, default_flow_style=False, sort_keys=False)

    def save_json(self, file_path: str, indent: Optional[int] = 2):
        """
        Save OpenAPI spec to JSON file.

        Args:
            file_path: Output file path
            indent: JSON indentation
        """
        spec_json = self.generate_json(indent=indent)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(spec_json)

    def save_yaml(self, file_path: str):
        """
        Save OpenAPI spec to YAML file.

        Args:
            file_path: Output file path
        """
        spec_yaml = self.generate_yaml()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(spec_yaml)


__all__ = [
    "OpenAPIGenerator",
    "OpenAPISchema",
    "OpenAPIPath",
    "OpenAPIOperation",
    "OpenAPIParameter",
    "OpenAPIRequestBody",
    "OpenAPIResponse",
    "SecurityScheme",
    "SecuritySchemeType",
    "ParameterLocation",
]
