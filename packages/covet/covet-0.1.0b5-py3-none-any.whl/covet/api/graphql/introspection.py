"""
GraphQL Introspection Support

Full introspection query support for:
- Schema exploration
- Type information
- Field details
- Directive information
- Documentation access
- GraphiQL/Playground integration

Enables powerful tooling like:
- GraphiQL
- Apollo Studio
- GraphQL Voyager
- Documentation generators
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type

from strawberry import Schema
from strawberry.types import Info

# ==============================================================================
# INTROSPECTION TYPES
# ==============================================================================


@dataclass
class TypeInfo:
    """GraphQL type information."""

    name: str
    kind: str  # OBJECT, INTERFACE, UNION, ENUM, INPUT_OBJECT, SCALAR
    description: Optional[str] = None
    fields: Optional[List[FieldInfo]] = None
    interfaces: Optional[List[str]] = None
    possible_types: Optional[List[str]] = None
    enum_values: Optional[List[EnumValueInfo]] = None
    input_fields: Optional[List[InputFieldInfo]] = None


@dataclass
class FieldInfo:
    """GraphQL field information."""

    name: str
    type: str
    description: Optional[str] = None
    args: List[ArgumentInfo] = None
    is_deprecated: bool = False
    deprecation_reason: Optional[str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = []


@dataclass
class ArgumentInfo:
    """GraphQL field argument information."""

    name: str
    type: str
    description: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class EnumValueInfo:
    """GraphQL enum value information."""

    name: str
    description: Optional[str] = None
    is_deprecated: bool = False
    deprecation_reason: Optional[str] = None


@dataclass
class InputFieldInfo:
    """GraphQL input field information."""

    name: str
    type: str
    description: Optional[str] = None
    default_value: Optional[str] = None


@dataclass
class DirectiveInfo:
    """GraphQL directive information."""

    name: str
    description: Optional[str] = None
    locations: List[str] = None
    args: List[ArgumentInfo] = None

    def __post_init__(self):
        if self.locations is None:
            self.locations = []
        if self.args is None:
            self.args = []


# ==============================================================================
# INTROSPECTION HANDLER
# ==============================================================================


class IntrospectionHandler:
    """
    Handle GraphQL introspection queries.

    Provides comprehensive schema information for tooling.
    """

    def __init__(self, schema: Schema):
        """
        Initialize introspection handler.

        Args:
            schema: Strawberry schema instance
        """
        self.schema = schema

    def get_schema_info(self) -> Dict[str, Any]:
        """
        Get complete schema information.

        Returns:
            Schema info dictionary
        """
        return {
            "query_type": self._get_type_name(self.schema.query),
            "mutation_type": self._get_type_name(self.schema.mutation),
            "subscription_type": self._get_type_name(self.schema.subscription),
            "types": self._get_all_types(),
            "directives": self._get_directives(),
        }

    def get_type_info(self, type_name: str) -> Optional[TypeInfo]:
        """
        Get information for specific type.

        Args:
            type_name: Type name

        Returns:
            Type information or None
        """
        # Get type from schema
        graphql_type = self._find_type(type_name)

        if graphql_type is None:
            return None

        return self._build_type_info(graphql_type)

    def get_field_info(
        self,
        type_name: str,
        field_name: str,
    ) -> Optional[FieldInfo]:
        """
        Get information for specific field.

        Args:
            type_name: Type name
            field_name: Field name

        Returns:
            Field information or None
        """
        type_info = self.get_type_info(type_name)

        if type_info is None or type_info.fields is None:
            return None

        for field in type_info.fields:
            if field.name == field_name:
                return field

        return None

    def search_types(self, query: str) -> List[TypeInfo]:
        """
        Search types by name.

        Args:
            query: Search query

        Returns:
            List of matching types
        """
        query = query.lower()
        results = []

        for type_info in self._get_all_types():
            if query in type_info.name.lower():
                results.append(type_info)

        return results

    def _get_all_types(self) -> List[TypeInfo]:
        """Get all types in schema."""
        types = []

        # Get GraphQL schema
        graphql_schema = self.schema.schema

        # Iterate over type map
        type_map = graphql_schema.type_map

        for type_name, graphql_type in type_map.items():
            # Skip introspection types
            if type_name.startswith("__"):
                continue

            type_info = self._build_type_info(graphql_type)
            if type_info:
                types.append(type_info)

        return types

    def _build_type_info(self, graphql_type: Any) -> Optional[TypeInfo]:
        """Build TypeInfo from GraphQL type."""
        try:
            type_name = graphql_type.name
            kind = self._get_type_kind(graphql_type)
            description = getattr(graphql_type, "description", None)

            type_info = TypeInfo(
                name=type_name,
                kind=kind,
                description=description,
            )

            # Add type-specific info
            if kind == "OBJECT":
                type_info.fields = self._get_fields(graphql_type)
                type_info.interfaces = self._get_interfaces(graphql_type)

            elif kind == "INTERFACE":
                type_info.fields = self._get_fields(graphql_type)
                type_info.possible_types = self._get_possible_types(graphql_type)

            elif kind == "UNION":
                type_info.possible_types = self._get_possible_types(graphql_type)

            elif kind == "ENUM":
                type_info.enum_values = self._get_enum_values(graphql_type)

            elif kind == "INPUT_OBJECT":
                type_info.input_fields = self._get_input_fields(graphql_type)

            return type_info

        except Exception as e:
            # Log error but don't fail
            import logging

            logging.warning(f"Failed to build type info: {e}")
            return None

    def _get_type_kind(self, graphql_type: Any) -> str:
        """Get type kind."""
        from graphql import (
            GraphQLEnumType,
            GraphQLInputObjectType,
            GraphQLInterfaceType,
            GraphQLObjectType,
            GraphQLScalarType,
            GraphQLUnionType,
        )

        if isinstance(graphql_type, GraphQLObjectType):
            return "OBJECT"
        elif isinstance(graphql_type, GraphQLInterfaceType):
            return "INTERFACE"
        elif isinstance(graphql_type, GraphQLUnionType):
            return "UNION"
        elif isinstance(graphql_type, GraphQLEnumType):
            return "ENUM"
        elif isinstance(graphql_type, GraphQLInputObjectType):
            return "INPUT_OBJECT"
        elif isinstance(graphql_type, GraphQLScalarType):
            return "SCALAR"
        else:
            return "UNKNOWN"

    def _get_fields(self, graphql_type: Any) -> List[FieldInfo]:
        """Get fields for type."""
        fields = []

        if not hasattr(graphql_type, "fields"):
            return fields

        for field_name, field in graphql_type.fields.items():
            field_info = FieldInfo(
                name=field_name,
                description=getattr(field, "description", None),
                type=str(field.type),
                args=self._get_arguments(field),
                is_deprecated=getattr(field, "is_deprecated", False),
                deprecation_reason=getattr(field, "deprecation_reason", None),
            )
            fields.append(field_info)

        return fields

    def _get_arguments(self, field: Any) -> List[ArgumentInfo]:
        """Get arguments for field."""
        args = []

        if not hasattr(field, "args"):
            return args

        for arg_name, arg in field.args.items():
            arg_info = ArgumentInfo(
                name=arg_name,
                description=getattr(arg, "description", None),
                type=str(arg.type),
                default_value=str(arg.default_value) if hasattr(arg, "default_value") else None,
            )
            args.append(arg_info)

        return args

    def _get_interfaces(self, graphql_type: Any) -> List[str]:
        """Get interfaces for type."""
        if not hasattr(graphql_type, "interfaces"):
            return []

        return [interface.name for interface in graphql_type.interfaces]

    def _get_possible_types(self, graphql_type: Any) -> List[str]:
        """Get possible types for union/interface."""
        if not hasattr(graphql_type, "types"):
            return []

        return [t.name for t in graphql_type.types]

    def _get_enum_values(self, graphql_type: Any) -> List[EnumValueInfo]:
        """Get enum values."""
        values = []

        if not hasattr(graphql_type, "values"):
            return values

        for value_name, value in graphql_type.values.items():
            value_info = EnumValueInfo(
                name=value_name,
                description=getattr(value, "description", None),
                is_deprecated=getattr(value, "is_deprecated", False),
                deprecation_reason=getattr(value, "deprecation_reason", None),
            )
            values.append(value_info)

        return values

    def _get_input_fields(self, graphql_type: Any) -> List[InputFieldInfo]:
        """Get input fields."""
        fields = []

        if not hasattr(graphql_type, "fields"):
            return fields

        for field_name, field in graphql_type.fields.items():
            field_info = InputFieldInfo(
                name=field_name,
                description=getattr(field, "description", None),
                type=str(field.type),
                default_value=str(field.default_value) if hasattr(field, "default_value") else None,
            )
            fields.append(field_info)

        return fields

    def _get_directives(self) -> List[DirectiveInfo]:
        """Get schema directives."""
        directives = []

        graphql_schema = self.schema.schema

        for directive in graphql_schema.directives:
            directive_info = DirectiveInfo(
                name=directive.name,
                description=getattr(directive, "description", None),
                locations=[str(loc) for loc in directive.locations],
                args=self._get_directive_args(directive),
            )
            directives.append(directive_info)

        return directives

    def _get_directive_args(self, directive: Any) -> List[ArgumentInfo]:
        """Get directive arguments."""
        args = []

        if not hasattr(directive, "args"):
            return args

        for arg_name, arg in directive.args.items():
            arg_info = ArgumentInfo(
                name=arg_name,
                description=getattr(arg, "description", None),
                type=str(arg.type),
                default_value=str(arg.default_value) if hasattr(arg, "default_value") else None,
            )
            args.append(arg_info)

        return args

    def _find_type(self, type_name: str) -> Optional[Any]:
        """Find type by name."""
        graphql_schema = self.schema.schema
        return graphql_schema.type_map.get(type_name)

    def _get_type_name(self, graphql_type: Optional[Type]) -> Optional[str]:
        """Get type name."""
        if graphql_type is None:
            return None

        return getattr(graphql_type, "__name__", None)


# ==============================================================================
# DOCUMENTATION GENERATOR
# ==============================================================================


class DocumentationGenerator:
    """
    Generate documentation from GraphQL schema.

    Creates human-readable documentation for:
    - Types
    - Fields
    - Arguments
    - Enums
    """

    def __init__(self, handler: IntrospectionHandler):
        """
        Initialize documentation generator.

        Args:
            handler: Introspection handler
        """
        self.handler = handler

    def generate_markdown(self) -> str:
        """
        Generate Markdown documentation.

        Returns:
            Markdown string
        """
        lines = ["# GraphQL Schema Documentation\n"]

        schema_info = self.handler.get_schema_info()

        # Query type
        if schema_info["query_type"]:
            lines.append(f"## Query\n")
            lines.append(self._document_type(schema_info["query_type"]))

        # Mutation type
        if schema_info["mutation_type"]:
            lines.append(f"## Mutation\n")
            lines.append(self._document_type(schema_info["mutation_type"]))

        # Subscription type
        if schema_info["subscription_type"]:
            lines.append(f"## Subscription\n")
            lines.append(self._document_type(schema_info["subscription_type"]))

        # All types
        lines.append("## Types\n")
        for type_info in schema_info["types"]:
            lines.append(self._document_type_info(type_info))

        return "\n".join(lines)

    def _document_type(self, type_name: str) -> str:
        """Document specific type."""
        type_info = self.handler.get_type_info(type_name)

        if type_info is None:
            return ""

        return self._document_type_info(type_info)

    def _document_type_info(self, type_info: TypeInfo) -> str:
        """Document type info."""
        lines = [f"### {type_info.name}\n"]

        if type_info.description:
            lines.append(f"{type_info.description}\n")

        lines.append(f"**Kind:** {type_info.kind}\n")

        # Fields
        if type_info.fields:
            lines.append("**Fields:**\n")
            for field in type_info.fields:
                lines.append(f"- `{field.name}`: {field.type}")
                if field.description:
                    lines.append(f"  - {field.description}")
                if field.args:
                    lines.append(f"  - Arguments:")
                    for arg in field.args:
                        lines.append(f"    - `{arg.name}`: {arg.type}")

        # Enum values
        if type_info.enum_values:
            lines.append("**Values:**\n")
            for value in type_info.enum_values:
                lines.append(f"- `{value.name}`")
                if value.description:
                    lines.append(f"  - {value.description}")

        lines.append("")
        return "\n".join(lines)


def get_introspection_query():
    """Get the introspection query."""
    return """
    query IntrospectionQuery {
      __schema {
        queryType { name }
        mutationType { name }
        subscriptionType { name }
        types {
          ...FullType
        }
        directives {
          name
          description
          locations
          args {
            ...InputValue
          }
        }
      }
    }

    fragment FullType on __Type {
      kind
      name
      description
      fields(includeDeprecated: true) {
        name
        description
        args {
          ...InputValue
        }
        type {
          ...TypeRef
        }
        isDeprecated
        deprecationReason
      }
      inputFields {
        ...InputValue
      }
      interfaces {
        ...TypeRef
      }
      enumValues(includeDeprecated: true) {
        name
        description
        isDeprecated
        deprecationReason
      }
      possibleTypes {
        ...TypeRef
      }
    }

    fragment InputValue on __InputValue {
      name
      description
      type { ...TypeRef }
      defaultValue
    }

    fragment TypeRef on __Type {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
                ofType {
                  kind
                  name
                  ofType {
                    kind
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
    """
