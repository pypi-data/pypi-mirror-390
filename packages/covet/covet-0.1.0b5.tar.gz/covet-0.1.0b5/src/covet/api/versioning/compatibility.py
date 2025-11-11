"""
CovetPy API Compatibility Testing

Automated backward compatibility testing:
- Schema diff between versions
- Breaking change detection
- Automatic test generation for version compatibility
- Contract testing between API versions

NO MOCK DATA - Real compatibility verification.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type

from covet.api.versioning.schema_evolution import (
    FieldChange,
    FieldTransformation,
    SchemaEvolutionManager,
)
from covet.api.versioning.version_manager import APIVersion

try:
    from pydantic import BaseModel

    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    BaseModel = object

logger = logging.getLogger(__name__)


class ChangeCategory(str, Enum):
    """Categories of API changes."""

    BREAKING = "breaking"  # Breaks existing clients
    NON_BREAKING = "non_breaking"  # Safe for existing clients
    BEHAVIORAL = "behavioral"  # Behavior changed but contract preserved
    UNKNOWN = "unknown"  # Unable to determine


class CompatibilityLevel(str, Enum):
    """Compatibility levels between versions."""

    FULLY_COMPATIBLE = "fully_compatible"  # 100% compatible
    COMPATIBLE = "compatible"  # Compatible with warnings
    PARTIALLY_COMPATIBLE = "partially_compatible"  # Some breaking changes
    INCOMPATIBLE = "incompatible"  # Major breaking changes


@dataclass
class BreakingChange:
    """
    Represents a breaking change between API versions.

    Attributes:
        category: Change category
        severity: Severity level (1-10, 10 being most severe)
        description: Human-readable description
        affected_field: Affected field name
        old_value: Old value/type
        new_value: New value/type
        migration_notes: How to migrate
        metadata: Additional metadata
    """

    category: ChangeCategory
    description: str
    severity: int = 5
    affected_field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    migration_notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "category": self.category.value,
            "severity": self.severity,
            "description": self.description,
            "affected_field": self.affected_field,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "migration_notes": self.migration_notes,
            **self.metadata,
        }


@dataclass
class CompatibilityReport:
    """
    Compatibility report between two API versions.

    Attributes:
        old_version: Older version
        new_version: Newer version
        level: Overall compatibility level
        breaking_changes: List of breaking changes
        non_breaking_changes: List of non-breaking changes
        score: Compatibility score (0-100, 100 being fully compatible)
        recommendations: List of recommendations
        metadata: Additional metadata
    """

    old_version: APIVersion
    new_version: APIVersion
    level: CompatibilityLevel
    breaking_changes: List[BreakingChange] = field(default_factory=list)
    non_breaking_changes: List[Dict[str, Any]] = field(default_factory=list)
    score: int = 100
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_compatible(self) -> bool:
        """Check if versions are compatible."""
        return self.level in (CompatibilityLevel.FULLY_COMPATIBLE, CompatibilityLevel.COMPATIBLE)

    def has_breaking_changes(self) -> bool:
        """Check if there are breaking changes."""
        return len(self.breaking_changes) > 0

    def get_critical_changes(self) -> List[BreakingChange]:
        """Get critical breaking changes (severity >= 8)."""
        return [c for c in self.breaking_changes if c.severity >= 8]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "old_version": str(self.old_version),
            "new_version": str(self.new_version),
            "compatibility_level": self.level.value,
            "compatibility_score": self.score,
            "is_compatible": self.is_compatible(),
            "breaking_changes": [c.to_dict() for c in self.breaking_changes],
            "breaking_change_count": len(self.breaking_changes),
            "critical_change_count": len(self.get_critical_changes()),
            "non_breaking_changes": self.non_breaking_changes,
            "recommendations": self.recommendations,
            **self.metadata,
        }


class CompatibilityChecker:
    """
    Check backward compatibility between API versions.

    Analyzes schema changes, detects breaking changes,
    and generates compatibility reports.

    NO MOCK DATA - Real compatibility analysis.
    """

    def __init__(
        self, schema_manager: Optional[SchemaEvolutionManager] = None, strict_mode: bool = False
    ):
        """
        Initialize compatibility checker.

        Args:
            schema_manager: Schema evolution manager
            strict_mode: If True, treat warnings as breaking changes
        """
        self.schema_manager = schema_manager or SchemaEvolutionManager()
        self.strict_mode = strict_mode

        # Custom rules for detecting breaking changes
        self.custom_rules: List[Callable[[FieldTransformation], Optional[BreakingChange]]] = []

    def check_compatibility(
        self, old_version: APIVersion, new_version: APIVersion
    ) -> CompatibilityReport:
        """
        Check compatibility between two versions.

        Args:
            old_version: Older version
            new_version: Newer version

        Returns:
            Compatibility report
        """
        if old_version >= new_version:
            raise ValueError("old_version must be less than new_version")

        logger.info(f"Checking compatibility: {old_version} -> {new_version}")

        # Get transformations
        transformations = self.schema_manager.get_transformations(old_version, new_version)

        # Analyze changes
        breaking_changes = []
        non_breaking_changes = []

        for trans in transformations:
            change = self._analyze_transformation(trans)
            if change and change.category == ChangeCategory.BREAKING:
                breaking_changes.append(change)
            elif change and change.category == ChangeCategory.NON_BREAKING:
                non_breaking_changes.append(change.to_dict())

        # Apply custom rules
        for trans in transformations:
            for rule in self.custom_rules:
                custom_change = rule(trans)
                if custom_change and custom_change.category == ChangeCategory.BREAKING:
                    breaking_changes.append(custom_change)

        # Calculate compatibility level and score
        level, score = self._calculate_compatibility(breaking_changes)

        # Generate recommendations
        recommendations = self._generate_recommendations(old_version, new_version, breaking_changes)

        # Create report
        report = CompatibilityReport(
            old_version=old_version,
            new_version=new_version,
            level=level,
            breaking_changes=breaking_changes,
            non_breaking_changes=non_breaking_changes,
            score=score,
            recommendations=recommendations,
            metadata={
                "total_transformations": len(transformations),
                "strict_mode": self.strict_mode,
            },
        )

        logger.info(
            f"Compatibility check complete: {level.value} "
            f"(score: {score}, breaking: {len(breaking_changes)})"
        )

        return report

    def _analyze_transformation(self, trans: FieldTransformation) -> Optional[BreakingChange]:
        """Analyze transformation for breaking changes."""

        if trans.change_type == FieldChange.REMOVED:
            return BreakingChange(
                category=ChangeCategory.BREAKING,
                severity=9,
                description=f"Field '{trans.source_field}' was removed",
                affected_field=trans.source_field,
                migration_notes=(
                    f"Remove usage of '{trans.source_field}' field. "
                    f"{trans.deprecation_message or ''}"
                ),
            )

        elif trans.change_type == FieldChange.TYPE_CHANGED:
            old_type = trans.metadata.get("old_type", "unknown")
            new_type = trans.metadata.get("new_type", "unknown")
            return BreakingChange(
                category=ChangeCategory.BREAKING,
                severity=8,
                description=f"Field '{trans.source_field}' type changed from {old_type} to {new_type}",
                affected_field=trans.source_field,
                old_value=old_type,
                new_value=new_type,
                migration_notes=(
                    f"Update '{trans.source_field}' to use {new_type} type. "
                    f"Transformation function available: {trans.transformer is not None}"
                ),
            )

        elif trans.change_type == FieldChange.RENAMED and not trans.metadata.get("keep_old_name"):
            return BreakingChange(
                category=ChangeCategory.BREAKING,
                severity=7,
                description=f"Field '{trans.source_field}' renamed to '{trans.target_field}'",
                affected_field=trans.source_field,
                old_value=trans.source_field,
                new_value=trans.target_field,
                migration_notes=f"Use '{trans.target_field}' instead of '{trans.source_field}'",
            )

        elif trans.change_type == FieldChange.REQUIRED_CHANGED:
            if trans.metadata.get("now_required"):
                return BreakingChange(
                    category=ChangeCategory.BREAKING,
                    severity=8,
                    description=f"Field '{trans.source_field}' is now required",
                    affected_field=trans.source_field,
                    migration_notes=f"Ensure '{trans.source_field}' is always provided",
                )

        elif trans.change_type == FieldChange.ADDED:
            # Adding optional field is non-breaking
            return BreakingChange(
                category=ChangeCategory.NON_BREAKING,
                severity=1,
                description=f"New field '{trans.target_field}' added",
                affected_field=trans.target_field,
                migration_notes=f"Optional: Use new field '{trans.target_field}'",
            )

        elif trans.change_type == FieldChange.DEPRECATED:
            severity = 3 if self.strict_mode else 2
            return BreakingChange(
                category=(
                    ChangeCategory.BREAKING if self.strict_mode else ChangeCategory.NON_BREAKING
                ),
                severity=severity,
                description=f"Field '{trans.source_field}' is deprecated",
                affected_field=trans.source_field,
                migration_notes=trans.deprecation_message
                or f"Field '{trans.source_field}' will be removed in future version",
            )

        return None

    def _calculate_compatibility(
        self, breaking_changes: List[BreakingChange]
    ) -> Tuple[CompatibilityLevel, int]:
        """
        Calculate compatibility level and score.

        Returns:
            Tuple of (CompatibilityLevel, score)
        """
        if not breaking_changes:
            return CompatibilityLevel.FULLY_COMPATIBLE, 100

        # Calculate score based on severity
        total_severity = sum(c.severity for c in breaking_changes)
        critical_count = len([c for c in breaking_changes if c.severity >= 8])

        # Score calculation: max 10 points deduction per breaking change
        score = max(0, 100 - total_severity)

        # Determine level
        if critical_count >= 5:
            level = CompatibilityLevel.INCOMPATIBLE
        elif critical_count >= 2:
            level = CompatibilityLevel.PARTIALLY_COMPATIBLE
        elif score >= 80:
            level = CompatibilityLevel.COMPATIBLE
        else:
            level = CompatibilityLevel.PARTIALLY_COMPATIBLE

        return level, score

    def _generate_recommendations(
        self,
        old_version: APIVersion,
        new_version: APIVersion,
        breaking_changes: List[BreakingChange],
    ) -> List[str]:
        """Generate recommendations based on breaking changes."""
        recommendations = []

        if not breaking_changes:
            recommendations.append(
                f"Upgrade from {old_version} to {new_version} is fully backward compatible."
            )
            return recommendations

        # Group by severity
        critical = [c for c in breaking_changes if c.severity >= 8]
        major = [c for c in breaking_changes if 5 <= c.severity < 8]
        minor = [c for c in breaking_changes if c.severity < 5]

        if critical:
            recommendations.append(
                f"WARNING: {len(critical)} critical breaking change(s) detected. "
                f"Careful migration planning required."
            )
            recommendations.append(
                f"Recommended: Create {new_version.major}.0 version instead of "
                f"minor/patch update."
            )

        if major:
            recommendations.append(
                f"{len(major)} major change(s) require client updates. "
                f"Plan migration timeline accordingly."
            )

        if minor:
            recommendations.append(
                f"{len(minor)} minor change(s) - monitor for deprecation warnings."
            )

        # Version bump recommendation
        if critical:
            recommendations.append(
                "Recommendation: Increment major version number due to breaking changes."
            )
        elif major:
            recommendations.append(
                "Recommendation: Increment minor version number and provide migration guide."
            )

        # Deprecation strategy
        if any(c.affected_field for c in breaking_changes):
            recommendations.append(
                "Consider deprecation period: Mark fields as deprecated before removal."
            )

        return recommendations

    def add_custom_rule(
        self, rule: Callable[[FieldTransformation], Optional[BreakingChange]]
    ) -> None:
        """
        Add custom rule for detecting breaking changes.

        Args:
            rule: Function that takes FieldTransformation and returns
                  BreakingChange if it's a breaking change, None otherwise
        """
        self.custom_rules.append(rule)
        logger.debug(f"Added custom compatibility rule: {rule.__name__}")

    def generate_migration_plan(
        self, old_version: APIVersion, new_version: APIVersion
    ) -> Dict[str, Any]:
        """
        Generate migration plan from old to new version.

        Args:
            old_version: Source version
            new_version: Target version

        Returns:
            Migration plan with steps and timeline
        """
        report = self.check_compatibility(old_version, new_version)

        # Estimate migration effort
        effort_hours = self._estimate_migration_effort(report)

        # Generate migration steps
        steps = []

        # Group changes by field
        field_changes: Dict[str, List[BreakingChange]] = {}
        for change in report.breaking_changes:
            if change.affected_field:
                if change.affected_field not in field_changes:
                    field_changes[change.affected_field] = []
                field_changes[change.affected_field].append(change)

        # Create migration steps
        for field, changes in sorted(field_changes.items()):
            for change in changes:
                step = {
                    "field": field,
                    "action": change.description,
                    "priority": (
                        "HIGH"
                        if change.severity >= 8
                        else "MEDIUM" if change.severity >= 5 else "LOW"
                    ),
                    "migration_notes": change.migration_notes or "No specific notes",
                }
                steps.append(step)

        migration_plan = {
            "from_version": str(old_version),
            "to_version": str(new_version),
            "compatibility_score": report.score,
            "is_compatible": report.is_compatible(),
            "breaking_changes_count": len(report.breaking_changes),
            "estimated_effort_hours": effort_hours,
            "recommended_timeline_weeks": max(1, effort_hours // 40),
            "migration_steps": steps,
            "recommendations": report.recommendations,
            "requires_major_version_bump": len(report.get_critical_changes()) > 0,
        }

        return migration_plan

    def _estimate_migration_effort(self, report: CompatibilityReport) -> int:
        """
        Estimate migration effort in hours.

        Args:
            report: Compatibility report

        Returns:
            Estimated hours
        """
        base_hours = 2  # Minimum effort

        # Add hours based on breaking changes
        for change in report.breaking_changes:
            if change.severity >= 8:
                base_hours += 8  # 1 day per critical change
            elif change.severity >= 5:
                base_hours += 4  # Half day per major change
            else:
                base_hours += 1  # 1 hour per minor change

        # Add overhead
        if len(report.breaking_changes) > 10:
            base_hours *= 1.5  # 50% overhead for complex migrations

        return int(base_hours)


class CompatibilityTestGenerator:
    """
    Generate automated tests for version compatibility.

    Creates test cases to verify that transformations work correctly.
    """

    def __init__(self, schema_manager: SchemaEvolutionManager):
        """
        Initialize test generator.

        Args:
            schema_manager: Schema evolution manager
        """
        self.schema_manager = schema_manager

    def generate_transformation_tests(
        self, old_version: APIVersion, new_version: APIVersion, test_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate test cases for data transformation.

        Args:
            old_version: Source version
            new_version: Target version
            test_data: Sample data for testing

        Returns:
            List of test cases with expected results
        """
        test_cases = []

        for idx, data in enumerate(test_data):
            # Transform data
            try:
                transformed = self.schema_manager.transform_data(data, old_version, new_version)

                test_case = {
                    "test_id": f"transform_{old_version}_{new_version}_{idx}",
                    "description": f"Transform data from {old_version} to {new_version}",
                    "from_version": str(old_version),
                    "to_version": str(new_version),
                    "input_data": data,
                    "expected_output": transformed,
                    "status": "generated",
                }

                test_cases.append(test_case)

            except Exception as e:
                test_cases.append(
                    {
                        "test_id": f"transform_{old_version}_{new_version}_{idx}",
                        "description": f"Transform data from {old_version} to {new_version}",
                        "from_version": str(old_version),
                        "to_version": str(new_version),
                        "input_data": data,
                        "error": str(e),
                        "status": "error",
                    }
                )

        return test_cases

    def generate_roundtrip_tests(
        self, version1: APIVersion, version2: APIVersion, test_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generate roundtrip test cases (v1 -> v2 -> v1).

        Args:
            version1: First version
            version2: Second version
            test_data: Sample data

        Returns:
            List of roundtrip test cases
        """
        test_cases = []

        for idx, data in enumerate(test_data):
            try:
                # Forward transformation
                forward = self.schema_manager.transform_data(data, version1, version2)

                # Backward transformation
                backward = self.schema_manager.transform_data(forward, version2, version1)

                test_case = {
                    "test_id": f"roundtrip_{version1}_{version2}_{idx}",
                    "description": f"Roundtrip: {version1} -> {version2} -> {version1}",
                    "original_data": data,
                    "forward_transform": forward,
                    "backward_transform": backward,
                    "data_preserved": data == backward,
                    "status": "generated",
                }

                test_cases.append(test_case)

            except Exception as e:
                test_cases.append(
                    {
                        "test_id": f"roundtrip_{version1}_{version2}_{idx}",
                        "description": f"Roundtrip: {version1} -> {version2} -> {version1}",
                        "original_data": data,
                        "error": str(e),
                        "status": "error",
                    }
                )

        return test_cases


__all__ = [
    "ChangeCategory",
    "CompatibilityLevel",
    "BreakingChange",
    "CompatibilityReport",
    "CompatibilityChecker",
    "CompatibilityTestGenerator",
]
