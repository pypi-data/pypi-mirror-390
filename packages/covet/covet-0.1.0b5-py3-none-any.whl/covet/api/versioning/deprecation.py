"""
CovetPy API Deprecation Management

Handles API deprecation with:
- RFC 8594 Sunset header compliance
- Automatic deprecation warnings in responses
- Version lifecycle management
- Deprecation notices in documentation
- Automatic sunset date calculation

NO MOCK DATA - Real deprecation tracking and warning generation.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from covet.api.versioning.version_manager import APIVersion, VersionStatus

logger = logging.getLogger(__name__)


class DeprecationSeverity(str, Enum):
    """Deprecation warning severity levels."""

    INFO = "info"  # Informational, no action needed immediately
    WARNING = "warning"  # Action recommended, still plenty of time
    URGENT = "urgent"  # Action required soon
    CRITICAL = "critical"  # Sunset imminent


@dataclass
class DeprecationNotice:
    """
    Deprecation notice for an API version or endpoint.

    Attributes:
        version: Deprecated API version
        deprecated_at: When deprecation started
        sunset_at: When version will be removed
        message: Deprecation message
        replacement: Replacement version or endpoint
        severity: Deprecation severity
        migration_guide_url: URL to migration guide
        contact: Contact for questions
        metadata: Additional metadata
    """

    version: APIVersion
    deprecated_at: datetime
    sunset_at: datetime
    message: str
    replacement: Optional[str] = None
    severity: DeprecationSeverity = DeprecationSeverity.WARNING
    migration_guide_url: Optional[str] = None
    contact: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def days_until_sunset(self) -> int:
        """Calculate days until sunset."""
        delta = self.sunset_at - datetime.utcnow()
        return max(0, delta.days)

    def is_sunset_soon(self, threshold_days: int = 30) -> bool:
        """Check if sunset is within threshold."""
        return self.days_until_sunset() <= threshold_days

    def calculate_severity(self) -> DeprecationSeverity:
        """
        Calculate deprecation severity based on time until sunset.

        Returns:
            Calculated severity level
        """
        days_left = self.days_until_sunset()

        if days_left <= 7:
            return DeprecationSeverity.CRITICAL
        elif days_left <= 30:
            return DeprecationSeverity.URGENT
        elif days_left <= 90:
            return DeprecationSeverity.WARNING
        else:
            return DeprecationSeverity.INFO

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "version": str(self.version),
            "deprecated_at": self.deprecated_at.isoformat(),
            "sunset_at": self.sunset_at.isoformat(),
            "days_until_sunset": self.days_until_sunset(),
            "message": self.message,
            "replacement": self.replacement,
            "severity": self.severity.value,
            "migration_guide_url": self.migration_guide_url,
            "contact": self.contact,
            **self.metadata,
        }


@dataclass
class EndpointDeprecation:
    """
    Deprecation notice for specific endpoint.

    Attributes:
        path: Endpoint path
        method: HTTP method
        version: API version (if version-specific)
        deprecated_at: When deprecated
        sunset_at: When will be removed
        message: Deprecation message
        replacement: Replacement endpoint
        metadata: Additional metadata
    """

    path: str
    method: str
    deprecated_at: datetime
    sunset_at: datetime
    message: str
    version: Optional[APIVersion] = None
    replacement: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def days_until_sunset(self) -> int:
        """Calculate days until sunset."""
        delta = self.sunset_at - datetime.utcnow()
        return max(0, delta.days)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "method": self.method,
            "version": str(self.version) if self.version else None,
            "deprecated_at": self.deprecated_at.isoformat(),
            "sunset_at": self.sunset_at.isoformat(),
            "days_until_sunset": self.days_until_sunset(),
            "message": self.message,
            "replacement": self.replacement,
            **self.metadata,
        }


class DeprecationManager:
    """
    Manage API deprecations and generate warnings.

    Tracks version and endpoint deprecations, generates RFC 8594 compliant
    Sunset headers, and provides deprecation notices for documentation.

    NO MOCK DATA - Real deprecation tracking and warning generation.
    """

    def __init__(
        self,
        default_deprecation_period_days: int = 90,
        warning_threshold_days: int = 30,
        include_in_responses: bool = True,
        include_in_docs: bool = True,
    ):
        """
        Initialize deprecation manager.

        Args:
            default_deprecation_period_days: Default days before sunset
            warning_threshold_days: Days before sunset to escalate warnings
            include_in_responses: Include deprecation warnings in API responses
            include_in_docs: Include deprecation notices in documentation
        """
        self.default_deprecation_period_days = default_deprecation_period_days
        self.warning_threshold_days = warning_threshold_days
        self.include_in_responses = include_in_responses
        self.include_in_docs = include_in_docs

        # Deprecation registry
        self.version_deprecations: Dict[APIVersion, DeprecationNotice] = {}
        self.endpoint_deprecations: List[EndpointDeprecation] = []

        # Notification callbacks
        self.notification_callbacks: List[Callable[[DeprecationNotice], None]] = []

    def deprecate_version(
        self,
        version: APIVersion,
        message: Optional[str] = None,
        sunset_at: Optional[datetime] = None,
        replacement: Optional[str] = None,
        migration_guide_url: Optional[str] = None,
        contact: Optional[str] = None,
        notify: bool = True,
        **metadata,
    ) -> DeprecationNotice:
        """
        Deprecate an API version.

        Args:
            version: Version to deprecate
            message: Deprecation message
            sunset_at: When version will be removed (auto-calculated if None)
            replacement: Replacement version
            migration_guide_url: URL to migration guide
            contact: Contact for questions
            notify: Send notifications
            **metadata: Additional metadata

        Returns:
            Created deprecation notice
        """
        # Calculate sunset date if not provided
        if sunset_at is None:
            sunset_at = datetime.utcnow() + timedelta(days=self.default_deprecation_period_days)

        # Create default message if not provided
        if message is None:
            message = f"API version {version} is deprecated and will be removed on {sunset_at.strftime('%Y-%m-%d')}."
            if replacement:
                message += f" Please migrate to {replacement}."

        # Create deprecation notice
        notice = DeprecationNotice(
            version=version,
            deprecated_at=datetime.utcnow(),
            sunset_at=sunset_at,
            message=message,
            replacement=replacement,
            migration_guide_url=migration_guide_url,
            contact=contact,
            metadata=metadata,
        )

        # Calculate severity
        notice.severity = notice.calculate_severity()

        # Store notice
        self.version_deprecations[version] = notice

        # Update version status
        version.status = VersionStatus.DEPRECATED
        version.deprecated_at = notice.deprecated_at
        version.sunset_at = sunset_at

        logger.warning(
            f"Version {version} deprecated. Sunset: {sunset_at.strftime('%Y-%m-%d')} "
            f"({notice.days_until_sunset()} days)"
        )

        # Send notifications
        if notify:
            self._send_notifications(notice)

        return notice

    def deprecate_endpoint(
        self,
        path: str,
        method: str,
        message: str,
        sunset_at: Optional[datetime] = None,
        version: Optional[APIVersion] = None,
        replacement: Optional[str] = None,
        **metadata,
    ) -> EndpointDeprecation:
        """
        Deprecate specific endpoint.

        Args:
            path: Endpoint path
            method: HTTP method
            message: Deprecation message
            sunset_at: When endpoint will be removed
            version: API version (if version-specific)
            replacement: Replacement endpoint
            **metadata: Additional metadata

        Returns:
            Created endpoint deprecation
        """
        # Calculate sunset date if not provided
        if sunset_at is None:
            sunset_at = datetime.utcnow() + timedelta(days=self.default_deprecation_period_days)

        # Create deprecation
        deprecation = EndpointDeprecation(
            path=path,
            method=method.upper(),
            deprecated_at=datetime.utcnow(),
            sunset_at=sunset_at,
            message=message,
            version=version,
            replacement=replacement,
            metadata=metadata,
        )

        self.endpoint_deprecations.append(deprecation)

        logger.warning(
            f"Endpoint {method} {path} deprecated. " f"Sunset: {sunset_at.strftime('%Y-%m-%d')}"
        )

        return deprecation

    def get_version_deprecation(self, version: APIVersion) -> Optional[DeprecationNotice]:
        """
        Get deprecation notice for version.

        Args:
            version: API version

        Returns:
            Deprecation notice or None if not deprecated
        """
        return self.version_deprecations.get(version)

    def get_endpoint_deprecations(
        self, path: str, method: str, version: Optional[APIVersion] = None
    ) -> List[EndpointDeprecation]:
        """
        Get deprecations for endpoint.

        Args:
            path: Endpoint path
            method: HTTP method
            version: API version (optional filter)

        Returns:
            List of matching deprecations
        """
        return [
            dep
            for dep in self.endpoint_deprecations
            if dep.path == path
            and dep.method == method.upper()
            and (version is None or dep.version == version)
        ]

    def get_deprecation_headers(
        self, version: APIVersion, path: Optional[str] = None, method: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate RFC 8594 compliant deprecation headers.

        Args:
            version: API version
            path: Endpoint path (optional)
            method: HTTP method (optional)

        Returns:
            Dictionary of deprecation headers
        """
        headers = {}

        # Check version deprecation
        version_dep = self.get_version_deprecation(version)

        # Check endpoint deprecation
        endpoint_deps = []
        if path and method:
            endpoint_deps = self.get_endpoint_deprecations(path, method, version)

        # If either version or endpoint is deprecated
        if version_dep or endpoint_deps:
            headers["Deprecation"] = "true"

            # Use most urgent sunset date
            sunset_dates = []
            if version_dep:
                sunset_dates.append(version_dep.sunset_at)
            for dep in endpoint_deps:
                sunset_dates.append(dep.sunset_at)

            if sunset_dates:
                earliest_sunset = min(sunset_dates)
                # RFC 8594 format: HTTP-date
                headers["Sunset"] = earliest_sunset.strftime("%a, %d %b %Y %H:%M:%S GMT")

                # Additional custom headers
                days_left = (earliest_sunset - datetime.utcnow()).days
                headers["X-API-Sunset-Days"] = str(max(0, days_left))

            # Add deprecation messages
            messages = []
            if version_dep:
                messages.append(version_dep.message)
                if version_dep.replacement:
                    headers["X-API-Upgrade-To"] = version_dep.replacement
                if version_dep.migration_guide_url:
                    headers["Link"] = f'<{version_dep.migration_guide_url}>; rel="deprecation"'

            for dep in endpoint_deps:
                messages.append(dep.message)

            if messages:
                # Combine messages, limiting length
                combined = " ".join(messages)
                if len(combined) > 200:
                    combined = combined[:197] + "..."
                headers["X-API-Deprecation-Message"] = combined

        return headers

    def get_deprecation_warnings(
        self, version: APIVersion, path: Optional[str] = None, method: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get deprecation warnings for inclusion in API response.

        Args:
            version: API version
            path: Endpoint path (optional)
            method: HTTP method (optional)

        Returns:
            List of deprecation warning dictionaries
        """
        if not self.include_in_responses:
            return []

        warnings = []

        # Version deprecation
        version_dep = self.get_version_deprecation(version)
        if version_dep:
            warnings.append({"type": "version_deprecation", **version_dep.to_dict()})

        # Endpoint deprecation
        if path and method:
            endpoint_deps = self.get_endpoint_deprecations(path, method, version)
            for dep in endpoint_deps:
                warnings.append({"type": "endpoint_deprecation", **dep.to_dict()})

        return warnings

    def get_all_deprecations(self, active_only: bool = True) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all deprecations for documentation.

        Args:
            active_only: Only include deprecations that haven't sunset yet

        Returns:
            Dictionary with 'versions' and 'endpoints' lists
        """
        if not self.include_in_docs:
            return {"versions": [], "endpoints": []}

        now = datetime.utcnow()

        # Version deprecations
        version_list = []
        for version, notice in self.version_deprecations.items():
            if active_only and notice.sunset_at < now:
                continue
            version_list.append(notice.to_dict())

        # Endpoint deprecations
        endpoint_list = []
        for dep in self.endpoint_deprecations:
            if active_only and dep.sunset_at < now:
                continue
            endpoint_list.append(dep.to_dict())

        return {
            "versions": sorted(version_list, key=lambda x: x["sunset_at"]),
            "endpoints": sorted(endpoint_list, key=lambda x: x["sunset_at"]),
        }

    def register_notification_callback(self, callback: Callable[[DeprecationNotice], None]) -> None:
        """
        Register callback for deprecation notifications.

        Args:
            callback: Function to call when version is deprecated
        """
        self.notification_callbacks.append(callback)

    def _send_notifications(self, notice: DeprecationNotice) -> None:
        """
        Send deprecation notifications.

        Args:
            notice: Deprecation notice
        """
        for callback in self.notification_callbacks:
            try:
                callback(notice)
            except Exception as e:
                logger.error(f"Error in deprecation notification callback: {e}")

    def check_expired_deprecations(self) -> List[APIVersion]:
        """
        Check for deprecations that have reached sunset.

        Returns:
            List of versions that should be removed
        """
        now = datetime.utcnow()
        expired = []

        for version, notice in self.version_deprecations.items():
            if notice.sunset_at <= now:
                expired.append(version)
                logger.critical(f"Version {version} has reached sunset date and should be removed!")

        return expired

    def extend_deprecation(
        self, version: APIVersion, additional_days: int, reason: Optional[str] = None
    ) -> None:
        """
        Extend deprecation period for a version.

        Args:
            version: Version to extend
            additional_days: Days to add to sunset date
            reason: Reason for extension
        """
        notice = self.version_deprecations.get(version)
        if not notice:
            raise ValueError(f"Version {version} is not deprecated")

        old_sunset = notice.sunset_at
        notice.sunset_at = old_sunset + timedelta(days=additional_days)

        # Update version
        version.sunset_at = notice.sunset_at

        # Update severity
        notice.severity = notice.calculate_severity()

        logger.info(
            f"Extended deprecation for {version} by {additional_days} days. "
            f"New sunset: {notice.sunset_at.strftime('%Y-%m-%d')}. "
            f"Reason: {reason or 'Not specified'}"
        )


__all__ = [
    "DeprecationSeverity",
    "DeprecationNotice",
    "EndpointDeprecation",
    "DeprecationManager",
]
