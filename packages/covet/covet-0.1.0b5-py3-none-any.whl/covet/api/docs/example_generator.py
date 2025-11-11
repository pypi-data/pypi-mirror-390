"""
Automatic Example Generator

Generate realistic request and response examples from Pydantic models
and OpenAPI schemas. Supports field metadata, constraints, and custom
example values.

Features:
- Automatic example generation from Pydantic models
- Respect field constraints (min/max, patterns, etc.)
- Multiple examples per endpoint
- Example values from Field metadata
- Support for nested models and arrays
- Realistic fake data generation
"""

import random
import string
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Union
from uuid import uuid4

from pydantic import BaseModel, Field


class ExampleConfig(BaseModel):
    """
    Configuration for example generation.

    Controls how examples are generated including fake data patterns,
    array sizes, and value ranges.
    """

    use_realistic_data: bool = Field(
        default=True, description="Generate realistic fake data instead of generic values"
    )
    array_min_items: int = Field(default=1, ge=0, description="Minimum items in generated arrays")
    array_max_items: int = Field(default=3, ge=1, description="Maximum items in generated arrays")
    string_pattern: str = Field(
        default="example_{field}", description="Pattern for string field examples"
    )
    include_optional_fields: bool = Field(
        default=True, description="Include optional fields in examples"
    )
    seed: Optional[int] = Field(default=None, description="Random seed for reproducible examples")


class RequestExample(BaseModel):
    """Request example with metadata."""

    summary: str = Field(..., description="Example summary")
    description: Optional[str] = Field(None, description="Example description")
    value: Dict[str, Any] = Field(..., description="Example value")


class ResponseExample(BaseModel):
    """Response example with metadata."""

    summary: str = Field(..., description="Example summary")
    description: Optional[str] = Field(None, description="Example description")
    value: Dict[str, Any] = Field(..., description="Example value")
    status_code: int = Field(..., description="HTTP status code")


class ExampleGenerator:
    """
    Production-grade example generator for API documentation.

    Automatically generates realistic request and response examples from
    Pydantic models, respecting field constraints and custom metadata.

    Features:
    - Automatic example generation from model schemas
    - Realistic fake data (emails, names, URLs, etc.)
    - Respect field constraints (min/max, patterns, etc.)
    - Multiple examples per model
    - Nested model support
    - Array and object handling
    - Custom example values from Field metadata

    Example:
        from pydantic import BaseModel, Field

        class User(BaseModel):
            id: int = Field(..., example=123)
            email: str = Field(..., example="user@example.com")
            name: str
            age: int = Field(..., ge=18, le=100)

        generator = ExampleGenerator()

        # Generate single example
        example = generator.generate_example(User)
        # {"id": 123, "email": "user@example.com", "name": "John Doe", "age": 25}

        # Generate multiple examples
        examples = generator.generate_examples(User, count=3)
    """

    def __init__(self, config: Optional[ExampleConfig] = None):
        """
        Initialize example generator.

        Args:
            config: Example generation configuration
        """
        self.config = config or ExampleConfig()

        if self.config.seed is not None:
            random.seed(self.config.seed)

        # Realistic example data
        self.example_names = [
            "John Doe",
            "Jane Smith",
            "Alice Johnson",
            "Bob Williams",
            "Charlie Brown",
            "Diana Prince",
            "Eve Davis",
            "Frank Miller",
        ]
        self.example_emails = [
            "john@example.com",
            "jane@example.com",
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com",
            "diana@example.com",
        ]
        self.example_urls = [
            "https://example.com",
            "https://api.example.com",
            "https://docs.example.com",
            "https://www.example.org",
        ]

    def generate_example(self, model: Type[BaseModel]) -> Dict[str, Any]:
        """
        Generate single example from Pydantic model.

        Args:
            model: Pydantic model class

        Returns:
            Example dictionary
        """
        if not issubclass(model, BaseModel):
            return {}

        example = {}
        schema = model.model_json_schema()

        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for field_name, field_info in properties.items():
            # Skip optional fields if configured
            is_required = field_name in required
            if not is_required and not self.config.include_optional_fields:
                continue

            # Generate value for field
            example[field_name] = self._generate_field_value(field_name, field_info)

        return example

    def generate_examples(self, model: Type[BaseModel], count: int = 3) -> List[RequestExample]:
        """
        Generate multiple examples from Pydantic model.

        Args:
            model: Pydantic model class
            count: Number of examples to generate

        Returns:
            List of request examples
        """
        examples = []

        for i in range(count):
            example_dict = self.generate_example(model)
            examples.append(
                RequestExample(
                    summary=f"Example {i + 1}",
                    description=f"Sample request payload #{i + 1}",
                    value=example_dict,
                )
            )

        return examples

    def generate_response_examples(
        self, model: Type[BaseModel], status_codes: Optional[List[int]] = None
    ) -> List[ResponseExample]:
        """
        Generate response examples for multiple status codes.

        Args:
            model: Pydantic response model
            status_codes: List of status codes (default: [200, 400, 404, 500])

        Returns:
            List of response examples
        """
        if status_codes is None:
            status_codes = [200, 400, 404, 500]

        examples = []

        for status_code in status_codes:
            if status_code == 200:
                example_dict = self.generate_example(model)
                examples.append(
                    ResponseExample(
                        summary="Success",
                        description="Successful response",
                        value=example_dict,
                        status_code=status_code,
                    )
                )
            elif status_code == 400:
                examples.append(
                    ResponseExample(
                        summary="Bad Request",
                        description="Invalid request parameters",
                        value={
                            "error": "VALIDATION_ERROR",
                            "message": "Invalid input",
                            "details": {"field": "email", "issue": "invalid format"},
                        },
                        status_code=status_code,
                    )
                )
            elif status_code == 404:
                examples.append(
                    ResponseExample(
                        summary="Not Found",
                        description="Resource not found",
                        value={
                            "error": "NOT_FOUND",
                            "message": "The requested resource was not found",
                        },
                        status_code=status_code,
                    )
                )
            elif status_code == 500:
                examples.append(
                    ResponseExample(
                        summary="Server Error",
                        description="Internal server error",
                        value={
                            "error": "INTERNAL_ERROR",
                            "message": "An unexpected error occurred",
                        },
                        status_code=status_code,
                    )
                )

        return examples

    def _generate_field_value(self, field_name: str, field_info: Dict[str, Any]) -> Any:
        """Generate value for a single field."""
        # Check for explicit example
        if "example" in field_info:
            return field_info["example"]

        if "examples" in field_info and field_info["examples"]:
            return random.choice(field_info["examples"])

        # Get field type
        field_type = field_info.get("type")
        field_format = field_info.get("format")

        # Handle different types
        if field_type == "string":
            return self._generate_string_value(field_name, field_info, field_format)
        elif field_type == "integer":
            return self._generate_integer_value(field_info)
        elif field_type == "number":
            return self._generate_number_value(field_info)
        elif field_type == "boolean":
            return random.choice([True, False])
        elif field_type == "array":
            return self._generate_array_value(field_name, field_info)
        elif field_type == "object":
            return self._generate_object_value(field_info)
        elif field_type == "null":
            return None
        elif "enum" in field_info:
            return random.choice(field_info["enum"])
        elif "$ref" in field_info:
            # Referenced schema - return placeholder
            return {"$ref": field_info["$ref"]}
        elif "anyOf" in field_info or "oneOf" in field_info:
            options = field_info.get("anyOf") or field_info.get("oneOf")
            if options:
                return self._generate_field_value(field_name, options[0])

        # Default fallback
        return f"example_{field_name}"

    def _generate_string_value(
        self, field_name: str, field_info: Dict[str, Any], field_format: Optional[str]
    ) -> str:
        """Generate string value based on format and constraints."""
        # Format-specific generation
        if field_format == "email":
            return random.choice(self.example_emails)
        elif field_format == "uri" or field_format == "url":
            return random.choice(self.example_urls)
        elif field_format == "uuid":
            return str(uuid4())
        elif field_format == "date":
            return date.today().isoformat()
        elif field_format == "date-time":
            return datetime.now().isoformat()
        elif field_format == "time":
            return datetime.now().time().isoformat()
        elif field_format == "password":
            return "********"
        elif field_format == "byte":
            return "base64encodedstring=="
        elif field_format == "binary":
            return "<binary data>"

        # Pattern-based generation
        if "pattern" in field_info:
            pattern = field_info["pattern"]
            # Simple pattern matching
            if pattern == r"^\d{3}-\d{3}-\d{4}$":
                return f"{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            elif pattern.startswith("^[A-Z]"):
                return "EXAMPLE123"

        # Length constraints
        min_length = field_info.get("minLength", 1)
        max_length = field_info.get("maxLength", 20)

        # Field name based generation
        field_lower = field_name.lower()
        if self.config.use_realistic_data:
            if "email" in field_lower:
                return random.choice(self.example_emails)
            elif "name" in field_lower or "username" in field_lower:
                return random.choice(self.example_names)
            elif "url" in field_lower or "link" in field_lower:
                return random.choice(self.example_urls)
            elif "phone" in field_lower:
                return f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
            elif "address" in field_lower:
                return f"{random.randint(1, 9999)} Main St"
            elif "city" in field_lower:
                return random.choice(["New York", "Los Angeles", "Chicago", "Houston"])
            elif "country" in field_lower:
                return random.choice(["USA", "UK", "Canada", "Australia"])
            elif "description" in field_lower:
                return "This is a sample description"
            elif "title" in field_lower:
                return "Example Title"

        # Default string
        length = min(max_length, max(min_length, 10))
        return f"example_{field_name}"[:length]

    def _generate_integer_value(self, field_info: Dict[str, Any]) -> int:
        """Generate integer value respecting constraints."""
        minimum = field_info.get("minimum", 1)
        maximum = field_info.get("maximum", 100)

        # Handle exclusive bounds
        if field_info.get("exclusiveMinimum"):
            minimum += 1
        if field_info.get("exclusiveMaximum"):
            maximum -= 1

        # Multiple of constraint
        multiple_of = field_info.get("multipleOf")
        if multiple_of:
            value = random.randint(minimum // multiple_of, maximum // multiple_of) * multiple_of
            return max(minimum, min(maximum, value))

        return random.randint(minimum, maximum)

    def _generate_number_value(self, field_info: Dict[str, Any]) -> float:
        """Generate float/decimal value respecting constraints."""
        minimum = field_info.get("minimum", 0.0)
        maximum = field_info.get("maximum", 100.0)

        # Handle exclusive bounds
        if field_info.get("exclusiveMinimum"):
            minimum += 0.01
        if field_info.get("exclusiveMaximum"):
            maximum -= 0.01

        value = random.uniform(minimum, maximum)

        # Multiple of constraint
        multiple_of = field_info.get("multipleOf")
        if multiple_of:
            value = round(value / multiple_of) * multiple_of

        return round(value, 2)

    def _generate_array_value(self, field_name: str, field_info: Dict[str, Any]) -> List[Any]:
        """Generate array value."""
        min_items = field_info.get("minItems", self.config.array_min_items)
        max_items = field_info.get("maxItems", self.config.array_max_items)

        count = random.randint(min_items, max_items)

        items_schema = field_info.get("items", {})
        if not items_schema:
            return []

        # Generate array items
        result = []
        for i in range(count):
            item_value = self._generate_field_value(f"{field_name}_item", items_schema)
            result.append(item_value)

        return result

    def _generate_object_value(self, field_info: Dict[str, Any]) -> Dict[str, Any]:
        """Generate object value."""
        properties = field_info.get("properties", {})
        required = field_info.get("required", [])

        result = {}
        for prop_name, prop_info in properties.items():
            if prop_name in required or self.config.include_optional_fields:
                result[prop_name] = self._generate_field_value(prop_name, prop_info)

        return result

    def add_examples_to_operation(
        self,
        operation: Dict[str, Any],
        request_model: Optional[Type[BaseModel]] = None,
        response_model: Optional[Type[BaseModel]] = None,
    ):
        """
        Add examples to OpenAPI operation definition.

        Args:
            operation: OpenAPI operation dictionary (modified in place)
            request_model: Pydantic request model
            response_model: Pydantic response model
        """
        # Add request examples
        if request_model and "requestBody" in operation:
            request_examples = self.generate_examples(request_model, count=2)

            content = operation["requestBody"].get("content", {})
            for media_type in content.values():
                media_type["examples"] = {
                    f"example{i+1}": {
                        "summary": ex.summary,
                        "description": ex.description,
                        "value": ex.value,
                    }
                    for i, ex in enumerate(request_examples)
                }

        # Add response examples
        if response_model and "responses" in operation:
            response_examples = self.generate_response_examples(response_model)

            for example in response_examples:
                status_code = str(example.status_code)
                if status_code in operation["responses"]:
                    response_def = operation["responses"][status_code]
                    content = response_def.get("content", {})

                    for media_type in content.values():
                        if "examples" not in media_type:
                            media_type["examples"] = {}

                        media_type["examples"][example.summary.lower().replace(" ", "_")] = {
                            "summary": example.summary,
                            "description": example.description,
                            "value": example.value,
                        }


__all__ = [
    "ExampleGenerator",
    "ExampleConfig",
    "RequestExample",
    "ResponseExample",
]
