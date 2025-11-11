"""
Postman Collection Generator

Export API documentation as Postman Collection v2.1 format.
Includes requests, authentication, environment variables, and
folder organization by tags.

Features:
- Postman Collection v2.1 format
- Automatic request generation from OpenAPI
- Authentication presets (Bearer, Basic, API Key, OAuth2)
- Environment variable support
- Folder organization by tags
- Pre-request scripts
- Test scripts
- Variables and dynamic values
"""

import json
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class PostmanAuthType(str, Enum):
    """Postman authentication types."""

    BEARER = "bearer"
    BASIC = "basic"
    API_KEY = "apikey"
    OAUTH2 = "oauth2"
    NO_AUTH = "noauth"


class PostmanAuth(BaseModel):
    """
    Postman authentication configuration.

    Example:
        # Bearer token
        auth = PostmanAuth(
            type=PostmanAuthType.BEARER,
            bearer=[{"key": "token", "value": "{{bearer_token}}", "type": "string"}]
        )

        # API Key
        auth = PostmanAuth(
            type=PostmanAuthType.API_KEY,
            apikey=[
                {"key": "key", "value": "X-API-Key", "type": "string"},
                {"key": "value", "value": "{{api_key}}", "type": "string"},
                {"key": "in", "value": "header", "type": "string"}
            ]
        )
    """

    type: PostmanAuthType
    bearer: Optional[List[Dict[str, str]]] = None
    basic: Optional[List[Dict[str, str]]] = None
    apikey: Optional[List[Dict[str, str]]] = None
    oauth2: Optional[List[Dict[str, str]]] = None

    class Config:
        use_enum_values = True


class PostmanHeader(BaseModel):
    """Postman request header."""

    key: str
    value: str
    description: Optional[str] = None
    disabled: bool = False


class PostmanBody(BaseModel):
    """Postman request body."""

    mode: str = "raw"  # raw, urlencoded, formdata, file, graphql
    raw: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class PostmanRequest(BaseModel):
    """
    Postman request definition.

    Represents a single API request in a Postman collection.
    """

    method: str
    header: List[PostmanHeader] = Field(default_factory=list)
    body: Optional[PostmanBody] = None
    url: Dict[str, Any]
    description: Optional[str] = None
    auth: Optional[PostmanAuth] = None


class PostmanItem(BaseModel):
    """Postman collection item (request)."""

    name: str
    request: PostmanRequest
    response: List[Dict[str, Any]] = Field(default_factory=list)
    event: Optional[List[Dict[str, Any]]] = None


class PostmanFolder(BaseModel):
    """
    Postman folder (group of requests).

    Organizes requests by tags or custom grouping.
    """

    name: str
    description: Optional[str] = None
    item: List[Any] = Field(default_factory=list)  # Can contain items or folders
    auth: Optional[PostmanAuth] = None


class PostmanVariable(BaseModel):
    """Postman variable definition."""

    key: str
    value: str = ""
    type: str = "string"
    description: Optional[str] = None


class PostmanEnvironment(BaseModel):
    """
    Postman environment configuration.

    Contains variables used across requests in the collection.

    Example:
        env = PostmanEnvironment(
            name="Production",
            values=[
                PostmanVariable(
                    key="base_url",
                    value="https://api.example.com",
                    type="string"
                ),
                PostmanVariable(
                    key="bearer_token",
                    value="",
                    type="string",
                    description="JWT authentication token"
                )
            ]
        )
    """

    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    values: List[PostmanVariable] = Field(default_factory=list)


class PostmanCollection:
    """
    Production-grade Postman Collection v2.1 generator.

    Converts OpenAPI specifications into Postman Collections with full
    support for authentication, environments, and organization.

    Features:
    - Postman Collection v2.1 format
    - Automatic request generation from OpenAPI paths
    - Authentication configuration (Bearer, API Key, OAuth2, etc.)
    - Environment variable support
    - Folder organization by tags
    - Request/response examples
    - Pre-request and test scripts
    - Dynamic variables ({{variable}})

    Example:
        # Create from OpenAPI spec
        collection = PostmanCollection(
            name="My API",
            openapi_spec=spec,
            base_url="https://api.example.com"
        )

        # Add authentication
        collection.set_auth(PostmanAuth(
            type=PostmanAuthType.BEARER,
            bearer=[{"key": "token", "value": "{{bearer_token}}", "type": "string"}]
        ))

        # Generate and save
        collection_json = collection.generate()
        with open("collection.json", "w") as f:
            json.dump(collection_json, f, indent=2)

        # Export environment
        env = collection.generate_environment("Production")
        with open("environment.json", "w") as f:
            json.dump(env, f, indent=2)
    """

    def __init__(
        self,
        name: str,
        openapi_spec: Dict[str, Any],
        base_url: Optional[str] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize Postman collection generator.

        Args:
            name: Collection name
            openapi_spec: OpenAPI specification dictionary
            base_url: Base URL for requests (overrides servers in spec)
            description: Collection description
        """
        self.name = name
        self.spec = openapi_spec
        self.description = description or openapi_spec.get("info", {}).get("description", "")
        self.collection_id = str(uuid4())

        # Determine base URL
        if base_url:
            self.base_url = base_url
        else:
            servers = openapi_spec.get("servers", [{"url": "/"}])
            self.base_url = servers[0]["url"] if servers else "/"

        # Collection structure
        self.auth: Optional[PostmanAuth] = None
        self.variables: List[PostmanVariable] = []
        self.folders: List[PostmanFolder] = []
        self.items: List[PostmanItem] = []

    def set_auth(self, auth: PostmanAuth):
        """
        Set collection-level authentication.

        Args:
            auth: Authentication configuration
        """
        self.auth = auth

    def add_variable(self, key: str, value: str = "", description: Optional[str] = None):
        """
        Add collection variable.

        Args:
            key: Variable key
            value: Variable value (can be empty for user input)
            description: Variable description
        """
        self.variables.append(PostmanVariable(key=key, value=value, description=description))

    def generate(self) -> Dict[str, Any]:
        """
        Generate Postman Collection v2.1 JSON.

        Returns:
            Collection dictionary ready for JSON serialization
        """
        # Parse OpenAPI spec and generate requests
        self._parse_openapi_spec()

        # Build collection structure
        collection = {
            "info": {
                "_postman_id": self.collection_id,
                "name": self.name,
                "description": self.description,
                "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            },
            "item": [],
        }

        # Add authentication
        if self.auth:
            collection["auth"] = self._serialize_auth(self.auth)

        # Add variables
        if self.variables:
            collection["variable"] = [v.dict(exclude_none=True) for v in self.variables]

        # Add folders and items
        for folder in self.folders:
            collection["item"].append(self._serialize_folder(folder))

        # Add ungrouped items
        for item in self.items:
            collection["item"].append(self._serialize_item(item))

        return collection

    def _parse_openapi_spec(self):
        """Parse OpenAPI spec and generate Postman items."""
        # Extract authentication
        self._extract_auth_from_spec()

        # Add base URL variable
        self.add_variable("base_url", self.base_url, "API base URL")

        # Group requests by tags
        tag_folders: Dict[str, PostmanFolder] = {}
        ungrouped_items = []

        paths = self.spec.get("paths", {})
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "options",
                    "head",
                ]:
                    continue

                item = self._create_item_from_operation(path, method, operation)

                # Group by tags
                tags = operation.get("tags", [])
                if tags:
                    tag = tags[0]  # Use first tag
                    if tag not in tag_folders:
                        # Find tag description
                        tag_desc = None
                        for tag_def in self.spec.get("tags", []):
                            if tag_def.get("name") == tag:
                                tag_desc = tag_def.get("description")
                                break

                        tag_folders[tag] = PostmanFolder(name=tag, description=tag_desc)

                    tag_folders[tag].item.append(item)
                else:
                    ungrouped_items.append(item)

        # Add folders
        self.folders = list(tag_folders.values())
        self.items = ungrouped_items

    def _extract_auth_from_spec(self):
        """Extract authentication from OpenAPI security schemes."""
        components = self.spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        if not security_schemes:
            return

        # Use first security scheme
        for name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")

            if scheme_type == "http":
                http_scheme = scheme.get("scheme", "")
                if http_scheme == "bearer":
                    self.set_auth(
                        PostmanAuth(
                            type=PostmanAuthType.BEARER,
                            bearer=[
                                {"key": "token", "value": "{{bearer_token}}", "type": "string"}
                            ],
                        )
                    )
                    self.add_variable("bearer_token", "", "Bearer authentication token")
                elif http_scheme == "basic":
                    self.set_auth(
                        PostmanAuth(
                            type=PostmanAuthType.BASIC,
                            basic=[
                                {"key": "username", "value": "{{username}}", "type": "string"},
                                {"key": "password", "value": "{{password}}", "type": "string"},
                            ],
                        )
                    )
                    self.add_variable("username", "", "Basic auth username")
                    self.add_variable("password", "", "Basic auth password")

            elif scheme_type == "apiKey":
                param_name = scheme.get("name", "X-API-Key")
                location = scheme.get("in", "header")
                self.set_auth(
                    PostmanAuth(
                        type=PostmanAuthType.API_KEY,
                        apikey=[
                            {"key": "key", "value": param_name, "type": "string"},
                            {"key": "value", "value": "{{api_key}}", "type": "string"},
                            {"key": "in", "value": location, "type": "string"},
                        ],
                    )
                )
                self.add_variable("api_key", "", "API key")

            # Only use first scheme
            break

    def _create_item_from_operation(
        self, path: str, method: str, operation: Dict[str, Any]
    ) -> PostmanItem:
        """Create Postman item from OpenAPI operation."""
        name = operation.get("summary", f"{method.upper()} {path}")
        description = operation.get("description", "")

        # Build URL
        url_obj = self._build_url(path, operation)

        # Build headers
        headers = []
        for param in operation.get("parameters", []):
            if param.get("in") == "header":
                headers.append(
                    PostmanHeader(
                        key=param["name"],
                        value=f"{{{{param['name']}}}}",
                        description=param.get("description"),
                    )
                )

        # Add Content-Type header for requests with body
        if method.lower() in ["post", "put", "patch"]:
            if "requestBody" in operation:
                headers.append(PostmanHeader(key="Content-Type", value="application/json"))

        # Build body
        body = None
        if "requestBody" in operation:
            body = self._build_request_body(operation["requestBody"])

        # Create request
        request = PostmanRequest(
            method=method.upper(), header=headers, body=body, url=url_obj, description=description
        )

        # Add response examples
        responses = []
        for status_code, response_def in operation.get("responses", {}).items():
            response_example = {
                "name": f"{status_code} - {response_def.get('description', '')}",
                "originalRequest": request.dict(exclude_none=True),
                "status": response_def.get("description", ""),
                "code": int(status_code) if status_code.isdigit() else 200,
                "_postman_previewlanguage": "json",
                "header": [],
                "body": "",
            }

            # Add example body if available
            content = response_def.get("content", {})
            if "application/json" in content:
                media_type = content["application/json"]
                if "example" in media_type:
                    response_example["body"] = json.dumps(media_type["example"], indent=2)
                elif "examples" in media_type:
                    examples = media_type["examples"]
                    if examples:
                        first_example = list(examples.values())[0]
                        if "value" in first_example:
                            response_example["body"] = json.dumps(first_example["value"], indent=2)

            responses.append(response_example)

        return PostmanItem(name=name, request=request, response=responses)

    def _build_url(self, path: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Build Postman URL object."""
        # Parse path segments
        path_segments = [seg for seg in path.split("/") if seg]

        # Build path with variables
        path_list = []
        for segment in path_segments:
            if segment.startswith("{") and segment.endswith("}"):
                # Path parameter - use variable
                param_name = segment[1:-1]
                path_list.append(f":{param_name}")
            else:
                path_list.append(segment)

        # Extract query parameters
        query_params = []
        for param in operation.get("parameters", []):
            if param.get("in") == "query":
                query_params.append(
                    {
                        "key": param["name"],
                        "value": f"{{{{{param['name']}}}}}",
                        "description": param.get("description"),
                        "disabled": not param.get("required", False),
                    }
                )

        # Extract path parameters for variable
        path_variables = []
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                path_variables.append(
                    {
                        "key": param["name"],
                        "value": f"{{{{{param['name']}}}}}",
                        "description": param.get("description"),
                    }
                )

        url_obj = {
            "raw": f"{{{{base_url}}}}/{'/'.join(path_list)}",
            "host": ["{{base_url}}"],
            "path": path_list,
        }

        if query_params:
            url_obj["query"] = query_params

        if path_variables:
            url_obj["variable"] = path_variables

        return url_obj

    def _build_request_body(self, request_body: Dict[str, Any]) -> PostmanBody:
        """Build Postman request body."""
        content = request_body.get("content", {})

        # Use application/json if available
        if "application/json" in content:
            media_type = content["application/json"]

            # Get example
            example = None
            if "example" in media_type:
                example = media_type["example"]
            elif "examples" in media_type:
                examples = media_type["examples"]
                if examples:
                    first_example = list(examples.values())[0]
                    if "value" in first_example:
                        example = first_example["value"]

            # Build raw body
            raw_body = "{}"
            if example:
                raw_body = json.dumps(example, indent=2)

            return PostmanBody(mode="raw", raw=raw_body, options={"raw": {"language": "json"}})

        return PostmanBody(mode="raw", raw="{}")

    def _serialize_auth(self, auth: PostmanAuth) -> Dict[str, Any]:
        """Serialize auth to Postman format."""
        result = {"type": auth.type}

        if auth.type == PostmanAuthType.BEARER and auth.bearer:
            result["bearer"] = auth.bearer
        elif auth.type == PostmanAuthType.BASIC and auth.basic:
            result["basic"] = auth.basic
        elif auth.type == PostmanAuthType.API_KEY and auth.apikey:
            result["apikey"] = auth.apikey
        elif auth.type == PostmanAuthType.OAUTH2 and auth.oauth2:
            result["oauth2"] = auth.oauth2

        return result

    def _serialize_folder(self, folder: PostmanFolder) -> Dict[str, Any]:
        """Serialize folder to Postman format."""
        result = {"name": folder.name, "item": [self._serialize_item(item) for item in folder.item]}

        if folder.description:
            result["description"] = folder.description

        if folder.auth:
            result["auth"] = self._serialize_auth(folder.auth)

        return result

    def _serialize_item(self, item: PostmanItem) -> Dict[str, Any]:
        """Serialize item to Postman format."""
        return item.dict(exclude_none=True)

    def generate_environment(
        self, name: str, additional_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Generate Postman environment file.

        Args:
            name: Environment name (e.g., "Production", "Staging")
            additional_vars: Additional variables to include

        Returns:
            Environment dictionary ready for JSON serialization
        """
        env = PostmanEnvironment(name=name)

        # Add collection variables
        env.values.extend(self.variables)

        # Add additional variables
        if additional_vars:
            for key, value in additional_vars.items():
                env.values.append(PostmanVariable(key=key, value=value))

        return {
            "id": env.id,
            "name": env.name,
            "values": [v.dict(exclude_none=True) for v in env.values],
            "_postman_variable_scope": "environment",
        }


__all__ = [
    "PostmanCollection",
    "PostmanRequest",
    "PostmanFolder",
    "PostmanAuth",
    "PostmanAuthType",
    "PostmanEnvironment",
    "PostmanVariable",
]
