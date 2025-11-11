"""
CovetPy Deserialization Protection Module

Protection against insecure deserialization through:
- Safe JSON parsing
- Pickle prevention
- YAML safe loading
- Object validation after deserialization
- Type checking

Author: CovetPy Security Team
License: MIT
"""

import json
import logging
from typing import Any, Dict, Optional, Type

import yaml

logger = logging.getLogger(__name__)


class DeserializationError(Exception):
    """Deserialization security error."""

    pass


class SafeDeserializer:
    """
    Safe deserialization with validation.
    """

    # Dangerous modules/classes to block
    DANGEROUS_MODULES = {
        "os",
        "subprocess",
        "sys",
        "builtins",
        "__builtin__",
        "pickle",
        "shelve",
        "marshal",
    }

    @staticmethod
    def load_json(json_string: str, max_depth: int = 10) -> Any:
        """
        Safely load JSON.

        Args:
            json_string: JSON string
            max_depth: Maximum nesting depth

        Returns:
            Parsed JSON data

        Raises:
            DeserializationError: If JSON is invalid or too deeply nested
        """
        try:
            data = json.loads(json_string)
            if not SafeDeserializer._check_depth(data, max_depth):
                raise DeserializationError("JSON nesting too deep")
            return data
        except json.JSONDecodeError as e:
            raise DeserializationError(f"Invalid JSON: {e}")

    @staticmethod
    def load_yaml_safe(yaml_string: str) -> Any:
        """
        Safely load YAML using safe_load.

        Args:
            yaml_string: YAML string

        Returns:
            Parsed YAML data

        Raises:
            DeserializationError: If YAML is invalid
        """
        try:
            return yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise DeserializationError(f"Invalid YAML: {e}")

    @staticmethod
    def _check_depth(obj: Any, max_depth: int, current_depth: int = 0) -> bool:
        """Check object nesting depth."""
        if current_depth > max_depth:
            return False

        if isinstance(obj, dict):
            return all(
                SafeDeserializer._check_depth(v, max_depth, current_depth + 1) for v in obj.values()
            )
        elif isinstance(obj, (list, tuple)):
            return all(
                SafeDeserializer._check_depth(item, max_depth, current_depth + 1) for item in obj
            )

        return True

    @staticmethod
    def validate_object_type(obj: Any, expected_type: Type) -> bool:
        """Validate deserialized object type."""
        return isinstance(obj, expected_type)

    @staticmethod
    def block_pickle():
        """
        Block pickle usage (raise exception if attempted).
        """
        import builtins

        original_import = builtins.__import__

        def secure_import(name, *args, **kwargs):
            if name == "pickle":
                raise ImportError("Pickle is disabled for security reasons")
            return original_import(name, *args, **kwargs)

        builtins.__import__ = secure_import


__all__ = ["DeserializationError", "SafeDeserializer"]
