"""
CovetPy API Versioning Module

Production-grade API versioning system with:
- Multiple versioning strategies (URL, header, query param)
- Version lifecycle management (alpha, beta, stable, deprecated, sunset)
- Backward compatibility testing
- Schema evolution helpers
- Deprecation warnings with RFC 8594 Sunset headers

NO MOCK DATA - Real version management and routing.
"""

from covet.api.versioning.compatibility import (
    BreakingChange,
    ChangeCategory,
    CompatibilityChecker,
    CompatibilityLevel,
    CompatibilityReport,
    CompatibilityTestGenerator,
)
from covet.api.versioning.deprecation import (
    DeprecationManager,
    DeprecationNotice,
    DeprecationSeverity,
    EndpointDeprecation,
)
from covet.api.versioning.schema_evolution import (
    FieldChange,
    FieldTransformation,
    SchemaEvolutionManager,
    SchemaVersion,
)
from covet.api.versioning.version_manager import (
    APIVersion,
    RouteVersionMapping,
    VersionInfo,
    VersioningStrategy,
    VersionManager,
    VersionNegotiator,
    VersionStatus,
)

__all__ = [
    # Core version management
    "APIVersion",
    "VersionInfo",
    "VersioningStrategy",
    "VersionStatus",
    "VersionNegotiator",
    "VersionManager",
    "RouteVersionMapping",
    # Deprecation management
    "DeprecationSeverity",
    "DeprecationNotice",
    "EndpointDeprecation",
    "DeprecationManager",
    # Schema evolution
    "FieldChange",
    "FieldTransformation",
    "SchemaVersion",
    "SchemaEvolutionManager",
    # Compatibility testing
    "ChangeCategory",
    "CompatibilityLevel",
    "BreakingChange",
    "CompatibilityReport",
    "CompatibilityChecker",
    "CompatibilityTestGenerator",
]

__version__ = "1.0.0"
