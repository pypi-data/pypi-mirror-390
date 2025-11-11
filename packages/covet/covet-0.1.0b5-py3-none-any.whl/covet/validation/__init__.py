"""
Input validation utilities for CovetPy.

Provides validation for request data, forms, and schemas.
"""

from typing import Any, Dict, List, Optional


class Validator:
    """Base validator class."""

    def validate(self, data: Any) -> bool:
        """Validate data."""
        return True

    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return []


class SchemaValidator(Validator):
    """JSON schema validator."""

    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema


__all__ = ["Validator", "SchemaValidator"]


from pydantic import BaseModel

class ValidatedModel(BaseModel):
    """Base model with validation."""
    
    class Config:
        validate_assignment = True
        arbitrary_types_allowed = True

__all__ = ["ValidatedModel"]



from pydantic import Field

__all__ = ["ValidatedModel", "Field"]
