"""
API Versioning

Support for multiple API versioning strategies:
- URL path versioning (/v1/users)
- Header versioning (Accept: application/vnd.api.v1+json)
- Query parameter versioning (?version=1)
"""

import re
from enum import Enum
from typing import Any, Callable, Dict, Optional


class VersioningStrategy(str, Enum):
    """API versioning strategies."""

    URL_PATH = "url_path"  # /v1/users
    HEADER = "header"  # Accept: application/vnd.api.v1+json
    QUERY_PARAM = "query_param"  # ?version=1
    SUBDOMAIN = "subdomain"  # v1.api.example.com


class APIVersion:
    """
    Represents an API version.

    Features:
    - Semantic versioning (major.minor.patch)
    - Version comparison
    - Deprecation support
    """

    def __init__(
        self,
        major: int,
        minor: int = 0,
        patch: int = 0,
        deprecated: bool = False,
        sunset_date: Optional[str] = None,
    ):
        """
        Initialize API version.

        Args:
            major: Major version number
            minor: Minor version number
            patch: Patch version number
            deprecated: Whether this version is deprecated
            sunset_date: ISO 8601 date when version will be removed
        """
        self.major = major
        self.minor = minor
        self.patch = patch
        self.deprecated = deprecated
        self.sunset_date = sunset_date

    @classmethod
    def parse(cls, version_str: str) -> "APIVersion":
        """
        Parse version string.

        Args:
            version_str: Version string (e.g., "v1", "1.2", "1.2.3")

        Returns:
            APIVersion instance
        """
        # Remove 'v' prefix if present
        version_str = version_str.lstrip("v")

        # Parse parts
        parts = version_str.split(".")
        major = int(parts[0]) if len(parts) > 0 else 1
        minor = int(parts[1]) if len(parts) > 1 else 0
        patch = int(parts[2]) if len(parts) > 2 else 0

        return cls(major=major, minor=minor, patch=patch)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"APIVersion({self.major}, {self.minor}, {self.patch})"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, APIVersion):
            return False
        return (self.major, self.minor, self.patch) == (
            other.major,
            other.minor,
            other.patch,
        )

    def __lt__(self, other) -> bool:
        """Less than comparison."""
        if not isinstance(other, APIVersion):
            return NotImplemented
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )

    def __le__(self, other) -> bool:
        """Less than or equal comparison."""
        return self == other or self < other

    def __gt__(self, other) -> bool:
        """Greater than comparison."""
        return not self <= other

    def __ge__(self, other) -> bool:
        """Greater than or equal comparison."""
        return not self < other


class VersionNegotiator:
    """
    Negotiate API version from request.

    Supports multiple versioning strategies and falls back to default version.
    """

    def __init__(
        self,
        strategy: VersioningStrategy = VersioningStrategy.URL_PATH,
        default_version: APIVersion = APIVersion(1, 0, 0),
        header_name: str = "Accept",
        param_name: str = "version",
    ):
        """
        Initialize version negotiator.

        Args:
            strategy: Versioning strategy to use
            default_version: Default version if none specified
            header_name: Header name for header versioning
            param_name: Query parameter name for param versioning
        """
        self.strategy = strategy
        self.default_version = default_version
        self.header_name = header_name
        self.param_name = param_name

    def negotiate(
        self, path: str, headers: Dict[str, str], query_params: Dict[str, str]
    ) -> APIVersion:
        """
        Negotiate API version from request.

        Args:
            path: Request path
            headers: Request headers
            query_params: Query parameters

        Returns:
            Negotiated API version
        """
        if self.strategy == VersioningStrategy.URL_PATH:
            return self._negotiate_url_path(path)
        elif self.strategy == VersioningStrategy.HEADER:
            return self._negotiate_header(headers)
        elif self.strategy == VersioningStrategy.QUERY_PARAM:
            return self._negotiate_query_param(query_params)
        else:
            return self.default_version

    def _negotiate_url_path(self, path: str) -> APIVersion:
        """Extract version from URL path."""
        # Match /v1/, /v2.1/, etc.
        match = re.match(r"^/v?(\d+(?:\.\d+)?(?:\.\d+)?)", path)
        if match:
            return APIVersion.parse(match.group(1))
        return self.default_version

    def _negotiate_header(self, headers: Dict[str, str]) -> APIVersion:
        """Extract version from header."""
        header_value = headers.get(self.header_name, "")

        # Match application/vnd.api.v1+json, application/vnd.api.v2.1+json,
        # etc.
        match = re.search(r"\.v(\d+(?:\.\d+)?(?:\.\d+)?)\+", header_value)
        if match:
            return APIVersion.parse(match.group(1))

        return self.default_version

    def _negotiate_query_param(self, query_params: Dict[str, str]) -> APIVersion:
        """Extract version from query parameter."""
        version_str = query_params.get(self.param_name)
        if version_str:
            return APIVersion.parse(version_str)
        return self.default_version


class VersionRouter:
    """
    Route requests to version-specific handlers.

    Maintains separate handler registries for each API version.
    """

    def __init__(self, negotiator: VersionNegotiator):
        """
        Initialize version router.

        Args:
            negotiator: Version negotiator
        """
        self.negotiator = negotiator
        self.handlers: Dict[APIVersion, Dict[str, Callable]] = {}
        self.deprecated_versions: Dict[APIVersion, Dict[str, Any]] = {}

    def register(self, version: APIVersion, path: str, handler: Callable, methods: list[str]):
        """
        Register handler for specific version.

        Args:
            version: API version
            path: Route path
            handler: Handler function
            methods: HTTP methods
        """
        if version not in self.handlers:
            self.handlers[version] = {}

        for method in methods:
            key = f"{method.upper()}:{path}"
            self.handlers[version][key] = handler

    def deprecate_version(
        self,
        version: APIVersion,
        sunset_date: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Mark version as deprecated.

        Args:
            version: Version to deprecate
            sunset_date: ISO 8601 date when version will be removed
            message: Deprecation message
        """
        version.deprecated = True
        version.sunset_date = sunset_date

        self.deprecated_versions[version] = {
            "sunset_date": sunset_date,
            "message": message or f"API version {version} is deprecated",
        }

    def route(
        self,
        path: str,
        method: str,
        headers: Dict[str, str],
        query_params: Dict[str, str],
    ) -> tuple[Optional[Callable], APIVersion, Optional[Dict[str, str]]]:
        """
        Route request to appropriate version handler.

        Args:
            path: Request path
            method: HTTP method
            headers: Request headers
            query_params: Query parameters

        Returns:
            Tuple of (handler, version, deprecation_headers)
        """
        # Negotiate version
        version = self.negotiator.negotiate(path, headers, query_params)

        # Remove version from path if using URL path strategy
        if self.negotiator.strategy == VersioningStrategy.URL_PATH:
            path = re.sub(r"^/v?\d+(?:\.\d+)?(?:\.\d+)?", "", path)
            if not path:
                path = "/"

        # Find handler
        key = f"{method.upper()}:{path}"

        # Try exact version
        if version in self.handlers and key in self.handlers[version]:
            handler = self.handlers[version][key]
            deprecation_headers = self._get_deprecation_headers(version)
            return handler, version, deprecation_headers

        # Try to find closest compatible version (same major version)
        compatible_versions = [
            v for v in self.handlers.keys() if v.major == version.major and v >= version
        ]

        if compatible_versions:
            closest_version = min(compatible_versions)
            if key in self.handlers[closest_version]:
                handler = self.handlers[closest_version][key]
                deprecation_headers = self._get_deprecation_headers(closest_version)
                return handler, closest_version, deprecation_headers

        # Not found
        return None, version, None

    def _get_deprecation_headers(self, version: APIVersion) -> Optional[Dict[str, str]]:
        """Get deprecation headers if version is deprecated."""
        if version in self.deprecated_versions:
            headers = {"Deprecation": "true", "X-API-Deprecated-Version": str(version)}

            info = self.deprecated_versions[version]
            if info.get("sunset_date"):
                headers["Sunset"] = info["sunset_date"]

            if info.get("message"):
                headers["X-API-Deprecation-Message"] = info["message"]

            return headers

        return None


__all__ = [
    "VersioningStrategy",
    "APIVersion",
    "VersionNegotiator",
    "VersionRouter",
]
