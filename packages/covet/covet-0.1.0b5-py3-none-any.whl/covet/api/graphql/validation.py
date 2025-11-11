
from enum import Enum

class SecurityThreatLevel(str, Enum):
    """Security threat level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


"""
GraphQL Query Validation

Validates GraphQL queries for complexity, depth, and other constraints.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ValidationRule:
    """Base validation rule."""

    name: str
    enabled: bool = True

    def validate(self, query: str, variables: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Validate query.

        Args:
            query: GraphQL query string
            variables: Query variables

        Returns:
            List of validation errors
        """
        return []


class QueryComplexityValidator(ValidationRule):
    """
    Validates query complexity.

    Prevents expensive queries from overloading the server.
    """

    def __init__(self, max_complexity: int = 1000, enabled: bool = True):
        """
        Initialize validator.

        Args:
            max_complexity: Maximum allowed complexity
            enabled: Whether validation is enabled
        """
        super().__init__(name="query_complexity", enabled=enabled)
        self.max_complexity = max_complexity

    def calculate_complexity(self, query: str) -> int:
        """
        Calculate query complexity.

        Simple heuristic: count fields and nesting.
        In production, use proper AST analysis.

        Args:
            query: GraphQL query

        Returns:
            Complexity score
        """
        # Count opening braces (nesting depth)
        depth = query.count("{")

        # Count field selections (rough approximation)
        lines = [
            l.strip() for l in query.split("\n") if l.strip() and not l.strip().startswith("#")
        ]
        fields = sum(1 for l in lines if ":" in l or ("{" not in l and "}" not in l and l))

        # Complexity = fields * depth
        return fields * max(depth, 1)

    def validate(self, query: str, variables: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate query complexity."""
        if not self.enabled:
            return []

        complexity = self.calculate_complexity(query)

        if complexity > self.max_complexity:
            return [f"Query complexity {complexity} exceeds maximum {self.max_complexity}"]

        return []


class DepthLimitValidator(ValidationRule):
    """
    Validates query depth.

    Prevents deeply nested queries.
    """

    def __init__(self, max_depth: int = 10, enabled: bool = True):
        """
        Initialize validator.

        Args:
            max_depth: Maximum allowed depth
            enabled: Whether validation is enabled
        """
        super().__init__(name="depth_limit", enabled=enabled)
        self.max_depth = max_depth

    def calculate_depth(self, query: str) -> int:
        """
        Calculate query depth.

        Args:
            query: GraphQL query

        Returns:
            Maximum depth
        """
        max_depth = 0
        current_depth = 0

        for char in query:
            if char == "{":
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char == "}":
                current_depth -= 1

        return max_depth

    def validate(self, query: str, variables: Optional[Dict[str, Any]] = None) -> List[str]:
        """Validate query depth."""
        if not self.enabled:
            return []

        depth = self.calculate_depth(query)

        if depth > self.max_depth:
            return [f"Query depth {depth} exceeds maximum {self.max_depth}"]

        return []


def validate_query(
    query: str,
    variables: Optional[Dict[str, Any]] = None,
    rules: Optional[List[ValidationRule]] = None,
) -> List[str]:
    """
    Validate query with multiple rules.

    Args:
        query: GraphQL query
        variables: Query variables
        rules: Validation rules

    Returns:
        List of validation errors
    """
    if rules is None:
        rules = [
            QueryComplexityValidator(),
            DepthLimitValidator(),
        ]

    errors = []
    for rule in rules:
        if rule.enabled:
            errors.extend(rule.validate(query, variables))

    return errors


__all__ = [
    "ValidationRule",
    "QueryComplexityValidator",
    "DepthLimitValidator",
    "validate_query",
]

__all__ = ["SecurityThreatLevel"]



class SecurityMetrics:
    """Security validation metrics."""
    def __init__(self):
        self.threats_detected = 0
        self.validations_passed = 0
