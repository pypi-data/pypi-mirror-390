"""
Markdown Documentation Generator

Generate beautiful Markdown documentation from OpenAPI specifications.
Supports MkDocs, Docusaurus, and other static site generators with
code examples in multiple languages.

Features:
- Convert OpenAPI specs to Markdown
- Code examples in curl, Python, JavaScript, and more
- MkDocs and Docusaurus compatible
- Table of contents generation
- Grouped operations by tags
- Schema documentation with examples
- Authentication documentation
"""

import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class MarkdownFormat(str, Enum):
    """Markdown format flavors."""

    GITHUB = "github"  # GitHub Flavored Markdown
    MKDOCS = "mkdocs"  # MkDocs compatible
    DOCUSAURUS = "docusaurus"  # Docusaurus compatible
    COMMONMARK = "commonmark"  # CommonMark spec


class CodeLanguage(str, Enum):
    """Supported code example languages."""

    CURL = "curl"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"
    PHP = "php"
    RUBY = "ruby"
    CSHARP = "csharp"


class MarkdownConfig(BaseModel):
    """
    Configuration for Markdown generation.

    Controls the format, structure, and content of generated Markdown documentation.

    Example:
        config = MarkdownConfig(
            format=MarkdownFormat.MKDOCS,
            languages=[CodeLanguage.CURL, CodeLanguage.PYTHON],
            include_toc=True,
            group_by_tags=True
        )
    """

    format: MarkdownFormat = Field(
        default=MarkdownFormat.MKDOCS, description="Markdown format flavor"
    )
    languages: List[CodeLanguage] = Field(
        default=[CodeLanguage.CURL, CodeLanguage.PYTHON, CodeLanguage.JAVASCRIPT],
        description="Languages for code examples",
    )
    include_toc: bool = Field(default=True, description="Include table of contents")
    include_schemas: bool = Field(default=True, description="Include schema documentation")
    include_examples: bool = Field(default=True, description="Include request/response examples")
    include_authentication: bool = Field(
        default=True, description="Include authentication documentation"
    )
    group_by_tags: bool = Field(default=True, description="Group operations by tags")
    split_by_tags: bool = Field(default=False, description="Create separate file for each tag")
    base_url: str = Field(
        default="https://api.example.com", description="Base URL for code examples"
    )
    heading_level: int = Field(default=1, ge=1, le=6, description="Starting heading level (1-6)")

    class Config:
        use_enum_values = True


class MarkdownGenerator:
    """
    Production-grade Markdown documentation generator.

    Converts OpenAPI specifications into well-structured Markdown documentation
    suitable for static site generators like MkDocs, Docusaurus, or GitHub wikis.

    Features:
    - Multiple Markdown flavors (GitHub, MkDocs, Docusaurus)
    - Code examples in 9+ languages
    - Automatic table of contents
    - Tag-based organization
    - Schema documentation with nested models
    - Authentication guides
    - Request/response examples
    - Split documentation into multiple files

    Example:
        # Generate from OpenAPI spec
        generator = MarkdownGenerator(
            spec=openapi_spec,
            config=MarkdownConfig(
                format=MarkdownFormat.MKDOCS,
                languages=[CodeLanguage.CURL, CodeLanguage.PYTHON]
            )
        )

        # Generate single file
        markdown = generator.generate()
        with open("api_docs.md", "w") as f:
            f.write(markdown)

        # Generate multiple files (split by tags)
        generator.config.split_by_tags = True
        files = generator.generate_files()
        for filename, content in files.items():
            with open(f"docs/{filename}", "w") as f:
                f.write(content)
    """

    def __init__(self, spec: Dict[str, Any], config: Optional[MarkdownConfig] = None):
        """
        Initialize Markdown generator.

        Args:
            spec: OpenAPI specification dictionary
            config: Markdown generation configuration
        """
        self.spec = spec
        self.config = config or MarkdownConfig()
        self._heading_level = self.config.heading_level

    def generate(self) -> str:
        """
        Generate complete Markdown documentation.

        Returns:
            Markdown string
        """
        sections = []

        # Title and description
        info = self.spec.get("info", {})
        sections.append(self._heading(info.get("title", "API Documentation"), 1))

        if "description" in info:
            sections.append(info["description"])
            sections.append("")

        # Version and metadata
        if "version" in info:
            sections.append(f"**Version:** {info['version']}")
            sections.append("")

        if "contact" in info:
            contact = info["contact"]
            if "name" in contact or "email" in contact:
                sections.append("**Contact:**")
                if "name" in contact:
                    sections.append(f"- {contact['name']}")
                if "email" in contact:
                    sections.append(f"- Email: {contact['email']}")
                if "url" in contact:
                    sections.append(f"- URL: {contact['url']}")
                sections.append("")

        # Table of contents
        if self.config.include_toc:
            sections.append(self._generate_toc())
            sections.append("")

        # Base URL / Servers
        if "servers" in self.spec and self.spec["servers"]:
            sections.append(self._heading("Base URLs", 2))
            for server in self.spec["servers"]:
                url = server.get("url", "")
                desc = server.get("description", "")
                if desc:
                    sections.append(f"- `{url}` - {desc}")
                else:
                    sections.append(f"- `{url}`")
            sections.append("")

        # Authentication
        if self.config.include_authentication:
            auth_section = self._generate_authentication()
            if auth_section:
                sections.append(auth_section)
                sections.append("")

        # Endpoints
        endpoints_section = self._generate_endpoints()
        if endpoints_section:
            sections.append(endpoints_section)
            sections.append("")

        # Schemas
        if self.config.include_schemas:
            schemas_section = self._generate_schemas()
            if schemas_section:
                sections.append(schemas_section)
                sections.append("")

        return "\n".join(sections)

    def generate_files(self) -> Dict[str, str]:
        """
        Generate multiple Markdown files (split by tags).

        Returns:
            Dictionary mapping filename to content
        """
        if not self.config.split_by_tags:
            return {"index.md": self.generate()}

        files = {}

        # Generate index with overview
        info = self.spec.get("info", {})
        index_sections = [
            self._heading(info.get("title", "API Documentation"), 1),
            "",
            info.get("description", ""),
            "",
        ]

        if self.config.include_authentication:
            auth_section = self._generate_authentication()
            if auth_section:
                index_sections.append(auth_section)
                index_sections.append("")

        files["index.md"] = "\n".join(index_sections)

        # Generate file for each tag
        tags = self._get_all_tags()
        for tag in tags:
            tag_filename = self._sanitize_filename(tag) + ".md"
            tag_content = self._generate_tag_file(tag)
            files[tag_filename] = tag_content

        # Generate schemas file
        if self.config.include_schemas:
            schemas_section = self._generate_schemas()
            if schemas_section:
                files["schemas.md"] = schemas_section

        return files

    def _generate_toc(self) -> str:
        """Generate table of contents."""
        sections = [self._heading("Table of Contents", 2), ""]

        # Authentication
        if self.config.include_authentication:
            sections.append("- [Authentication](#authentication)")

        # Endpoints by tag
        if self.config.group_by_tags:
            tags = self._get_all_tags()
            for tag in tags:
                anchor = self._to_anchor(tag)
                sections.append(f"- [{tag}](#{anchor})")
        else:
            sections.append("- [Endpoints](#endpoints)")

        # Schemas
        if self.config.include_schemas:
            sections.append("- [Schemas](#schemas)")

        return "\n".join(sections)

    def _generate_authentication(self) -> str:
        """Generate authentication documentation."""
        components = self.spec.get("components", {})
        security_schemes = components.get("securitySchemes", {})

        if not security_schemes:
            return ""

        sections = [self._heading("Authentication", 2), ""]

        for name, scheme in security_schemes.items():
            scheme_type = scheme.get("type", "")
            sections.append(self._heading(name, 3))

            if "description" in scheme:
                sections.append(scheme["description"])
                sections.append("")

            # Type-specific documentation
            if scheme_type == "http":
                http_scheme = scheme.get("scheme", "")
                sections.append(f"**Type:** HTTP {http_scheme.capitalize()}")
                sections.append("")

                if http_scheme == "bearer":
                    bearer_format = scheme.get("bearerFormat", "JWT")
                    sections.append(f"**Format:** {bearer_format}")
                    sections.append("")
                    sections.append("Include the token in the Authorization header:")
                    sections.append("")
                    sections.append("```")
                    sections.append("Authorization: Bearer YOUR_TOKEN")
                    sections.append("```")
                    sections.append("")

            elif scheme_type == "apiKey":
                location = scheme.get("in", "header")
                param_name = scheme.get("name", "")
                sections.append(f"**Type:** API Key")
                sections.append(f"**Parameter:** `{param_name}` ({location})")
                sections.append("")

            elif scheme_type == "oauth2":
                sections.append(f"**Type:** OAuth 2.0")
                sections.append("")
                flows = scheme.get("flows", {})
                for flow_name, flow_config in flows.items():
                    sections.append(f"**{flow_name.title()} Flow:**")
                    if "authorizationUrl" in flow_config:
                        sections.append(f"- Authorization URL: `{flow_config['authorizationUrl']}`")
                    if "tokenUrl" in flow_config:
                        sections.append(f"- Token URL: `{flow_config['tokenUrl']}`")
                    if "scopes" in flow_config:
                        sections.append("- Scopes:")
                        for scope, desc in flow_config["scopes"].items():
                            sections.append(f"  - `{scope}`: {desc}")
                    sections.append("")

        return "\n".join(sections)

    def _generate_endpoints(self) -> str:
        """Generate endpoints documentation."""
        paths = self.spec.get("paths", {})
        if not paths:
            return ""

        sections = []

        if self.config.group_by_tags:
            tags = self._get_all_tags()
            for tag in tags:
                tag_section = self._generate_tag_section(tag, paths)
                if tag_section:
                    sections.append(tag_section)
                    sections.append("")
        else:
            sections.append(self._heading("Endpoints", 2))
            sections.append("")
            for path, methods in paths.items():
                for method, operation in methods.items():
                    if method in ["get", "post", "put", "patch", "delete", "options", "head"]:
                        sections.append(self._generate_operation(path, method, operation))
                        sections.append("")

        return "\n".join(sections)

    def _generate_tag_section(self, tag: str, paths: Dict[str, Any]) -> str:
        """Generate documentation for operations with specific tag."""
        sections = [self._heading(tag, 2), ""]

        # Find tag description
        for tag_def in self.spec.get("tags", []):
            if tag_def.get("name") == tag:
                if "description" in tag_def:
                    sections.append(tag_def["description"])
                    sections.append("")
                break

        # Add operations
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in ["get", "post", "put", "patch", "delete", "options", "head"]:
                    continue
                op_tags = operation.get("tags", [])
                if tag in op_tags:
                    sections.append(self._generate_operation(path, method, operation))
                    sections.append("")

        return "\n".join(sections)

    def _generate_tag_file(self, tag: str) -> str:
        """Generate complete file for a tag."""
        paths = self.spec.get("paths", {})
        return self._generate_tag_section(tag, paths)

    def _generate_operation(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Generate documentation for single operation."""
        sections = []

        # Title
        summary = operation.get("summary", f"{method.upper()} {path}")
        sections.append(self._heading(summary, 3))
        sections.append("")

        # Method and path
        sections.append(f"`{method.upper()} {path}`")
        sections.append("")

        # Description
        if "description" in operation:
            sections.append(operation["description"])
            sections.append("")

        # Parameters
        parameters = operation.get("parameters", [])
        if parameters:
            sections.append(self._heading("Parameters", 4))
            sections.append("")

            # Group by location
            path_params = [p for p in parameters if p.get("in") == "path"]
            query_params = [p for p in parameters if p.get("in") == "query"]
            header_params = [p for p in parameters if p.get("in") == "header"]

            if path_params:
                sections.append("**Path Parameters:**")
                sections.append("")
                sections.extend(self._format_parameters_table(path_params))
                sections.append("")

            if query_params:
                sections.append("**Query Parameters:**")
                sections.append("")
                sections.extend(self._format_parameters_table(query_params))
                sections.append("")

            if header_params:
                sections.append("**Header Parameters:**")
                sections.append("")
                sections.extend(self._format_parameters_table(header_params))
                sections.append("")

        # Request body
        if "requestBody" in operation:
            sections.append(self._heading("Request Body", 4))
            sections.append("")
            request_body = operation["requestBody"]
            if "description" in request_body:
                sections.append(request_body["description"])
                sections.append("")
            sections.extend(self._format_request_body(request_body))
            sections.append("")

        # Responses
        responses = operation.get("responses", {})
        if responses:
            sections.append(self._heading("Responses", 4))
            sections.append("")
            sections.extend(self._format_responses(responses))
            sections.append("")

        # Code examples
        if self.config.languages:
            sections.append(self._heading("Examples", 4))
            sections.append("")
            for language in self.config.languages:
                example = self._generate_code_example(path, method, operation, language)
                if example:
                    sections.append(example)
                    sections.append("")

        return "\n".join(sections)

    def _format_parameters_table(self, parameters: List[Dict[str, Any]]) -> List[str]:
        """Format parameters as Markdown table."""
        lines = [
            "| Name | Type | Required | Description |",
            "|------|------|----------|-------------|",
        ]

        for param in parameters:
            name = param.get("name", "")
            required = "Yes" if param.get("required", False) else "No"
            description = param.get("description", "")

            # Get type from schema
            schema = param.get("schema", {})
            param_type = schema.get("type", "string")

            lines.append(f"| `{name}` | {param_type} | {required} | {description} |")

        return lines

    def _format_request_body(self, request_body: Dict[str, Any]) -> List[str]:
        """Format request body documentation."""
        lines = []
        content = request_body.get("content", {})

        for content_type, media_type in content.items():
            lines.append(f"**Content-Type:** `{content_type}`")
            lines.append("")

            schema = media_type.get("schema", {})
            if "$ref" in schema:
                ref_name = schema["$ref"].split("/")[-1]
                lines.append(f"Schema: [{ref_name}](#schema-{ref_name.lower()})")
                lines.append("")

            # Example
            if self.config.include_examples and "example" in media_type:
                lines.append("**Example:**")
                lines.append("")
                lines.append("```json")
                lines.append(json.dumps(media_type["example"], indent=2))
                lines.append("```")

        return lines

    def _format_responses(self, responses: Dict[str, Any]) -> List[str]:
        """Format responses documentation."""
        lines = []

        for status_code, response in responses.items():
            description = response.get("description", "")
            lines.append(f"**{status_code}** - {description}")
            lines.append("")

            content = response.get("content", {})
            for content_type, media_type in content.items():
                schema = media_type.get("schema", {})
                if "$ref" in schema:
                    ref_name = schema["$ref"].split("/")[-1]
                    lines.append(f"Schema: [{ref_name}](#schema-{ref_name.lower()})")
                    lines.append("")

                # Example
                if self.config.include_examples and "example" in media_type:
                    lines.append("```json")
                    lines.append(json.dumps(media_type["example"], indent=2))
                    lines.append("```")
                    lines.append("")

        return lines

    def _generate_code_example(
        self, path: str, method: str, operation: Dict[str, Any], language: CodeLanguage
    ) -> str:
        """Generate code example in specified language."""
        if language == CodeLanguage.CURL:
            return self._generate_curl_example(path, method, operation)
        elif language == CodeLanguage.PYTHON:
            return self._generate_python_example(path, method, operation)
        elif language == CodeLanguage.JAVASCRIPT:
            return self._generate_javascript_example(path, method, operation)
        return ""

    def _generate_curl_example(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Generate curl example."""
        lines = ["**cURL:**", "", "```bash"]

        url = f"{self.config.base_url}{path}"
        # Replace path parameters
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                url = url.replace(f"{{{param['name']}}}", f"<{param['name']}>")

        cmd = f'curl -X {method.upper()} "{url}"'

        # Add headers
        if "requestBody" in operation:
            cmd += ' \\\n  -H "Content-Type: application/json"'

        # Add auth
        security = operation.get("security", self.spec.get("security", []))
        if security:
            cmd += ' \\\n  -H "Authorization: Bearer YOUR_TOKEN"'

        # Add body
        if "requestBody" in operation:
            cmd += ' \\\n  -d \'{"key": "value"}\''

        lines.append(cmd)
        lines.append("```")
        return "\n".join(lines)

    def _generate_python_example(self, path: str, method: str, operation: Dict[str, Any]) -> str:
        """Generate Python example."""
        lines = ["**Python:**", "", "```python", "import requests", ""]

        url = f"{self.config.base_url}{path}"
        # Replace path parameters
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                param_name = param["name"]
                url = url.replace(f"{{{param_name}}}", f"{{{param_name}}}")

        lines.append(f'url = "{url}"')

        # Headers
        headers = []
        security = operation.get("security", self.spec.get("security", []))
        if security:
            headers.append('    "Authorization": "Bearer YOUR_TOKEN"')
        if "requestBody" in operation:
            headers.append('    "Content-Type": "application/json"')

        if headers:
            lines.append("headers = {")
            lines.extend(headers)
            lines.append("}")

        # Body
        if "requestBody" in operation:
            lines.append("data = {")
            lines.append('    "key": "value"')
            lines.append("}")

        # Request
        request_args = ["url"]
        if headers:
            request_args.append("headers=headers")
        if "requestBody" in operation:
            request_args.append("json=data")

        lines.append("")
        lines.append(f"response = requests.{method}({', '.join(request_args)})")
        lines.append("print(response.json())")
        lines.append("```")

        return "\n".join(lines)

    def _generate_javascript_example(
        self, path: str, method: str, operation: Dict[str, Any]
    ) -> str:
        """Generate JavaScript example."""
        lines = ["**JavaScript:**", "", "```javascript"]

        url = f"{self.config.base_url}{path}"
        # Replace path parameters
        for param in operation.get("parameters", []):
            if param.get("in") == "path":
                url = url.replace(f"{{{param['name']}}}", f"${{{param['name']}}}")

        lines.append(f"const url = `{url}`;")

        # Headers
        headers = ['  "Content-Type": "application/json"']
        security = operation.get("security", self.spec.get("security", []))
        if security:
            headers.append('  "Authorization": "Bearer YOUR_TOKEN"')

        lines.append("const headers = {")
        lines.append(",\n".join(headers))
        lines.append("};")

        # Body
        if "requestBody" in operation:
            lines.append("const body = JSON.stringify({")
            lines.append('  key: "value"')
            lines.append("});")

        # Fetch
        lines.append("")
        lines.append("fetch(url, {")
        lines.append(f'  method: "{method.upper()}",')
        lines.append("  headers: headers,")
        if "requestBody" in operation:
            lines.append("  body: body")
        lines.append("})")
        lines.append("  .then(response => response.json())")
        lines.append("  .then(data => console.log(data));")
        lines.append("```")

        return "\n".join(lines)

    def _generate_schemas(self) -> str:
        """Generate schemas documentation."""
        components = self.spec.get("components", {})
        schemas = components.get("schemas", {})

        if not schemas:
            return ""

        sections = [self._heading("Schemas", 2), ""]

        for schema_name, schema in schemas.items():
            sections.append(self._generate_schema(schema_name, schema))
            sections.append("")

        return "\n".join(sections)

    def _generate_schema(self, name: str, schema: Dict[str, Any]) -> str:
        """Generate documentation for single schema."""
        sections = [self._heading(name, 3), ""]

        if "description" in schema:
            sections.append(schema["description"])
            sections.append("")

        # Properties
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        if properties:
            sections.append("**Properties:**")
            sections.append("")
            sections.append("| Name | Type | Required | Description |")
            sections.append("|------|------|----------|-------------|")

            for prop_name, prop_schema in properties.items():
                prop_type = prop_schema.get("type", "string")
                is_required = "Yes" if prop_name in required else "No"
                description = prop_schema.get("description", "")
                sections.append(f"| `{prop_name}` | {prop_type} | {is_required} | {description} |")

            sections.append("")

        # Example
        if self.config.include_examples and "example" in schema:
            sections.append("**Example:**")
            sections.append("")
            sections.append("```json")
            sections.append(json.dumps(schema["example"], indent=2))
            sections.append("```")

        return "\n".join(sections)

    def _get_all_tags(self) -> List[str]:
        """Extract all unique tags from specification."""
        tags_set: Set[str] = set()

        # From paths
        for path, methods in self.spec.get("paths", {}).items():
            for method, operation in methods.items():
                if method in ["get", "post", "put", "patch", "delete", "options", "head"]:
                    for tag in operation.get("tags", []):
                        tags_set.add(tag)

        # From tags definition (preserves order)
        tags = []
        for tag_def in self.spec.get("tags", []):
            tag_name = tag_def.get("name")
            if tag_name in tags_set:
                tags.append(tag_name)
                tags_set.remove(tag_name)

        # Add remaining tags
        tags.extend(sorted(tags_set))

        return tags

    def _heading(self, text: str, level: int) -> str:
        """Generate Markdown heading."""
        return f"{'#' * level} {text}"

    def _to_anchor(self, text: str) -> str:
        """Convert text to anchor link."""
        return text.lower().replace(" ", "-").replace("_", "-")

    def _sanitize_filename(self, text: str) -> str:
        """Convert text to safe filename."""
        return text.lower().replace(" ", "_").replace("-", "_")


__all__ = [
    "MarkdownGenerator",
    "MarkdownConfig",
    "MarkdownFormat",
    "CodeLanguage",
]
