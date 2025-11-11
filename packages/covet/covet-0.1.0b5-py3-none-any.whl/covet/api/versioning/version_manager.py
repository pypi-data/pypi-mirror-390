"""
CovetPy API Version Manager

Production-grade API versioning system with multiple strategies:
- URL versioning (/api/v1/users, /api/v2/users)
- Header versioning (Accept: application/vnd.covet.v1+json)
- Query parameter versioning (?version=1)
- Custom header versioning (X-API-Version: 1)

Supports version negotiation, backward compatibility, and automatic routing.
NO MOCK DATA - Real routing and version management.
"""

import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

logger = logging.getLogger(__name__)


class VersioningStrategy(str, Enum):
    """API versioning strategies."""

    URL_PATH = "url_path"  # /api/v1/resource
    HEADER = "header"  # Accept: application/vnd.covet.v1+json
    QUERY_PARAM = "query_param"  # ?version=1
    CUSTOM_HEADER = "custom_header"  # X-API-Version: 1


class VersionStatus(str, Enum):
    """API version lifecycle status."""

    ALPHA = "alpha"  # Under development, unstable
    BETA = "beta"  # Feature complete, testing
    STABLE = "stable"  # Production ready
    DEPRECATED = "deprecated"  # Still works, use newer version
    SUNSET = "sunset"  # Will be removed soon


@dataclass
class APIVersion:
    """
    Represents an API version with semantic versioning.

    Attributes:
        major: Major version number (breaking changes)
        minor: Minor version number (new features)
        patch: Patch version number (bug fixes)
        status: Version lifecycle status
        released_at: When version was released
        deprecated_at: When version was deprecated
        sunset_at: When version will be removed
        metadata: Additional version metadata
    """

    major: int
    minor: int = 0
    patch: int = 0
    status: VersionStatus = VersionStatus.STABLE
    released_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    sunset_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set released_at if not provided."""
        if self.released_at is None:
            self.released_at = datetime.utcnow()

    @classmethod
    def parse(cls, version_str: str) -> "APIVersion":
        """
        Parse version string into APIVersion.

        Args:
            version_str: Version string (e.g., "v1", "1.2", "1.2.3", "v2.1.0")

        Returns:
            APIVersion instance

        Raises:
            ValueError: If version string is invalid
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip("vV")

        # Split by dots
        parts = version_str.split(".")

        try:
            major = int(parts[0]) if len(parts) > 0 else 1
            minor = int(parts[1]) if len(parts) > 1 else 0
            patch = int(parts[2]) if len(parts) > 2 else 0
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid version string: {version_str}") from e

        return cls(major=major, minor=minor, patch=patch)

    def __str__(self) -> str:
        """String representation: '1.2.3'"""
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"APIVersion({self.major}.{self.minor}.{self.patch}, status={self.status.value})"

    def to_url_format(self) -> str:
        """Format for URL path: 'v1' or 'v1.2' or 'v1.2.3'"""
        if self.patch == 0 and self.minor == 0:
            return f"v{self.major}"
        elif self.patch == 0:
            return f"v{self.major}.{self.minor}"
        return f"v{self.major}.{self.minor}.{self.patch}"

    def to_header_format(self) -> str:
        """Format for header: 'application/vnd.covet.v1+json'"""
        return f"application/vnd.covet.{self.to_url_format()}+json"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, APIVersion):
            return False
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, APIVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        if not isinstance(other, APIVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch)

    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        return self == other or self > other

    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((self.major, self.minor, self.patch))

    def is_compatible_with(self, other: "APIVersion") -> bool:
        """
        Check if this version is backward compatible with another.

        Versions are compatible if they have the same major version
        and this version is greater than or equal to the other.

        Args:
            other: Version to check compatibility with

        Returns:
            True if compatible, False otherwise
        """
        return self.major == other.major and self >= other

    def days_until_sunset(self) -> Optional[int]:
        """
        Calculate days until sunset.

        Returns:
            Number of days until sunset, or None if no sunset date
        """
        if self.sunset_at is None:
            return None

        delta = self.sunset_at - datetime.utcnow()
        return max(0, delta.days)


@dataclass
class RouteVersionMapping:
    """Mapping between route path and versioned handlers."""

    path: str
    method: str
    version: APIVersion
    handler: Callable
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self) -> int:
        """Hash for use in sets and dicts."""
        return hash((self.path, self.method, self.version))


class VersionNegotiator:
    """
    Negotiate API version from HTTP requests.

    Supports multiple versioning strategies and falls back to default version.
    """

    def __init__(
        self,
        strategy: VersioningStrategy = VersioningStrategy.URL_PATH,
        default_version: Optional[APIVersion] = None,
        header_name: str = "Accept",
        custom_header_name: str = "X-API-Version",
        param_name: str = "version",
        vendor_string: str = "covet",
    ):
        """
        Initialize version negotiator.

        Args:
            strategy: Primary versioning strategy
            default_version: Default version if none specified (defaults to v1.0.0)
            header_name: Header name for Accept header versioning
            custom_header_name: Custom header name for version
            param_name: Query parameter name
            vendor_string: Vendor string for header versioning
        """
        self.strategy = strategy
        self.default_version = default_version or APIVersion(1, 0, 0)
        self.header_name = header_name
        self.custom_header_name = custom_header_name
        self.param_name = param_name
        self.vendor_string = vendor_string

    def negotiate(
        self, path: str, headers: Dict[str, str], query_params: Dict[str, str]
    ) -> APIVersion:
        """
        Negotiate API version from request.

        Args:
            path: Request path
            headers: Request headers (case-insensitive)
            query_params: Query parameters

        Returns:
            Negotiated API version
        """
        # Convert headers to lowercase keys for case-insensitive lookup
        headers_lower = {k.lower(): v for k, v in headers.items()}

        # Try primary strategy
        version = None

        if self.strategy == VersioningStrategy.URL_PATH:
            version = self._negotiate_url_path(path)
        elif self.strategy == VersioningStrategy.HEADER:
            version = self._negotiate_header(headers_lower)
        elif self.strategy == VersioningStrategy.QUERY_PARAM:
            version = self._negotiate_query_param(query_params)
        elif self.strategy == VersioningStrategy.CUSTOM_HEADER:
            version = self._negotiate_custom_header(headers_lower)

        # Fall back to other strategies if primary didn't work
        if version is None:
            version = (
                self._negotiate_custom_header(headers_lower)
                or self._negotiate_query_param(query_params)
                or self._negotiate_header(headers_lower)
                or self._negotiate_url_path(path)
            )

        return version or self.default_version

    def _negotiate_url_path(self, path: str) -> Optional[APIVersion]:
        """Extract version from URL path."""
        # Match patterns like /v1/, /v2.1/, /api/v1/, etc.
        match = re.search(r"/v?(\d+(?:\.\d+)?(?:\.\d+)?)", path)
        if match:
            try:
                return APIVersion.parse(match.group(1))
            except ValueError:
                logger.warning(f"Invalid version in URL path: {match.group(1)}")
        return None

    def _negotiate_header(self, headers: Dict[str, str]) -> Optional[APIVersion]:
        """Extract version from Accept header."""
        accept_header = headers.get(self.header_name.lower(), "")

        # Match patterns like application/vnd.covet.v1+json, application/vnd.covet.v2.1+json
        pattern = rf"application/vnd\.{self.vendor_string}\.v(\d+(?:\.\d+)?(?:\.\d+)?)\+\w+"
        match = re.search(pattern, accept_header, re.IGNORECASE)

        if match:
            try:
                return APIVersion.parse(match.group(1))
            except ValueError:
                logger.warning(f"Invalid version in Accept header: {match.group(1)}")

        return None

    def _negotiate_query_param(self, query_params: Dict[str, str]) -> Optional[APIVersion]:
        """Extract version from query parameter."""
        version_str = query_params.get(self.param_name)
        if version_str:
            try:
                return APIVersion.parse(version_str)
            except ValueError:
                logger.warning(f"Invalid version in query parameter: {version_str}")
        return None

    def _negotiate_custom_header(self, headers: Dict[str, str]) -> Optional[APIVersion]:
        """Extract version from custom header."""
        version_str = headers.get(self.custom_header_name.lower())
        if version_str:
            try:
                return APIVersion.parse(version_str)
            except ValueError:
                logger.warning(f"Invalid version in custom header: {version_str}")
        return None

    def strip_version_from_path(self, path: str) -> str:
        """
        Remove version from URL path.

        Args:
            path: Request path

        Returns:
            Path without version component
        """
        # Remove version pattern from path
        cleaned_path = re.sub(r"/v?\d+(?:\.\d+)?(?:\.\d+)?", "", path, count=1)

        # Ensure path starts with /
        if not cleaned_path or cleaned_path[0] != "/":
            cleaned_path = "/" + cleaned_path

        return cleaned_path


class VersionManager:
    """
    Central version management for API.

    Handles version registration, routing, and lifecycle management.
    NO MOCK DATA - Real version routing and handler management.
    """

    def __init__(
        self,
        negotiator: Optional[VersionNegotiator] = None,
        default_version: Optional[APIVersion] = None,
    ):
        """
        Initialize version manager.

        Args:
            negotiator: Version negotiator (creates default if None)
            default_version: Default API version
        """
        self.default_version = default_version or APIVersion(1, 0, 0)
        self.negotiator = negotiator or VersionNegotiator(default_version=self.default_version)

        # Version registry: version -> metadata
        self.versions: Dict[APIVersion, Dict[str, Any]] = {}

        # Route registry: (method, path) -> {version -> handler}
        self.routes: Dict[Tuple[str, str], Dict[APIVersion, RouteVersionMapping]] = defaultdict(
            dict
        )

        # Version aliases: alias -> version
        self.aliases: Dict[str, APIVersion] = {}

        # Latest stable version cache
        self._latest_stable: Optional[APIVersion] = None

    def register_version(
        self,
        version: APIVersion,
        description: Optional[str] = None,
        changelog: Optional[str] = None,
        **metadata,
    ) -> None:
        """
        Register an API version.

        Args:
            version: API version to register
            description: Version description
            changelog: Version changelog
            **metadata: Additional metadata
        """
        self.versions[version] = {
            "description": description or f"API version {version}",
            "changelog": changelog or "",
            "registered_at": datetime.utcnow(),
            **metadata,
        }

        # Update latest stable version
        if version.status == VersionStatus.STABLE:
            if self._latest_stable is None or version > self._latest_stable:
                self._latest_stable = version

        logger.info(f"Registered API version {version} with status {version.status.value}")

    def register_route(
        self, path: str, method: str, version: APIVersion, handler: Callable, **metadata
    ) -> None:
        """
        Register a route handler for specific version.

        Args:
            path: Route path (without version)
            method: HTTP method
            version: API version
            handler: Route handler function
            **metadata: Additional route metadata
        """
        # Ensure version is registered
        if version not in self.versions:
            self.register_version(version)

        # Create route mapping
        route_key = (method.upper(), path)
        mapping = RouteVersionMapping(
            path=path, method=method.upper(), version=version, handler=handler, metadata=metadata
        )

        self.routes[route_key][version] = mapping

        logger.debug(f"Registered route {method} {path} for version {version}")

    def set_version_alias(self, alias: str, version: APIVersion) -> None:
        """
        Set version alias (e.g., 'latest', 'stable').

        Args:
            alias: Alias name
            version: Target version
        """
        self.aliases[alias] = version
        logger.debug(f"Set alias '{alias}' -> {version}")

    def get_version_by_alias(self, alias: str) -> Optional[APIVersion]:
        """
        Get version by alias.

        Args:
            alias: Alias name

        Returns:
            Version or None if alias doesn't exist
        """
        return self.aliases.get(alias)

    def get_latest_stable_version(self) -> APIVersion:
        """
        Get latest stable version.

        Returns:
            Latest stable version (defaults to default_version if none registered)
        """
        return self._latest_stable or self.default_version

    def route_request(
        self, path: str, method: str, headers: Dict[str, str], query_params: Dict[str, str]
    ) -> Tuple[Optional[Callable], APIVersion, str, Dict[str, Any]]:
        """
        Route request to appropriate version handler.

        Args:
            path: Request path
            method: HTTP method
            headers: Request headers
            query_params: Query parameters

        Returns:
            Tuple of (handler, version, cleaned_path, metadata)
            handler is None if no matching route found
        """
        # Negotiate version
        requested_version = self.negotiator.negotiate(path, headers, query_params)

        # Strip version from path if using URL strategy
        if self.negotiator.strategy == VersioningStrategy.URL_PATH:
            cleaned_path = self.negotiator.strip_version_from_path(path)
        else:
            cleaned_path = path

        # Find handler
        route_key = (method.upper(), cleaned_path)
        version_handlers = self.routes.get(route_key, {})

        if not version_handlers:
            # No handlers for this route at all
            return None, requested_version, cleaned_path, {}

        # Try exact version match
        if requested_version in version_handlers:
            mapping = version_handlers[requested_version]
            return mapping.handler, requested_version, cleaned_path, mapping.metadata

        # Find compatible version (same major version, >= minor)
        compatible_versions = [
            v for v in version_handlers.keys() if v.is_compatible_with(requested_version)
        ]

        if compatible_versions:
            # Use closest compatible version
            closest_version = min(compatible_versions, key=lambda v: (v.major, v.minor, v.patch))
            mapping = version_handlers[closest_version]

            logger.debug(
                f"Using compatible version {closest_version} "
                f"for requested version {requested_version}"
            )

            return mapping.handler, closest_version, cleaned_path, mapping.metadata

        # No compatible version found
        logger.warning(
            f"No compatible handler found for {method} {cleaned_path} "
            f"version {requested_version}"
        )

        return None, requested_version, cleaned_path, {}

    def get_versions(self, status: Optional[VersionStatus] = None) -> List[APIVersion]:
        """
        Get all registered versions.

        Args:
            status: Filter by status (None for all)

        Returns:
            List of versions sorted newest to oldest
        """
        versions = list(self.versions.keys())

        if status is not None:
            versions = [v for v in versions if v.status == status]

        return sorted(versions, reverse=True)

    def get_version_info(self, version: APIVersion) -> Optional[Dict[str, Any]]:
        """
        Get version metadata.

        Args:
            version: API version

        Returns:
            Version metadata or None if not registered
        """
        return self.versions.get(version)

    def deprecate_version(
        self,
        version: APIVersion,
        sunset_date: Optional[datetime] = None,
        message: Optional[str] = None,
    ) -> None:
        """
        Mark version as deprecated.

        Args:
            version: Version to deprecate
            sunset_date: When version will be removed (defaults to 90 days from now)
            message: Deprecation message
        """
        if version not in self.versions:
            raise ValueError(f"Version {version} not registered")

        # Update version status
        version.status = VersionStatus.DEPRECATED
        version.deprecated_at = datetime.utcnow()

        if sunset_date is None:
            # Default: 90 days deprecation period
            sunset_date = datetime.utcnow() + timedelta(days=90)

        version.sunset_at = sunset_date

        # Update metadata
        self.versions[version]["deprecated_message"] = (
            message
            or f"API version {version} is deprecated. "
            f"It will be removed on {sunset_date.strftime('%Y-%m-%d')}."
        )

        logger.warning(
            f"Version {version} deprecated. Sunset date: {sunset_date.strftime('%Y-%m-%d')}"
        )

    def get_deprecation_headers(self, version: APIVersion) -> Dict[str, str]:
        """
        Get deprecation headers for response.

        Args:
            version: API version

        Returns:
            Dictionary of deprecation headers
        """
        headers = {}

        if version.status in (VersionStatus.DEPRECATED, VersionStatus.SUNSET):
            headers["Deprecation"] = "true"
            headers["X-API-Deprecated-Version"] = str(version)

            if version.sunset_at:
                # RFC 8594 Sunset header
                headers["Sunset"] = version.sunset_at.strftime("%a, %d %b %Y %H:%M:%S GMT")

                days_left = version.days_until_sunset()
                if days_left is not None:
                    headers["X-API-Sunset-Days"] = str(days_left)

            # Get deprecation message
            version_info = self.versions.get(version, {})
            if "deprecated_message" in version_info:
                headers["X-API-Deprecation-Message"] = version_info["deprecated_message"]

            # Suggest upgrade version
            latest_stable = self.get_latest_stable_version()
            if latest_stable and latest_stable > version:
                headers["X-API-Upgrade-To"] = str(latest_stable)

        return headers


# Alias for backward compatibility
VersionInfo = APIVersion

__all__ = [
    "VersioningStrategy",
    "VersionStatus",
    "APIVersion",
    "VersionInfo",
    "RouteVersionMapping",
    "VersionNegotiator",
    "VersionManager",
]
