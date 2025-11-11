"""
Production-Grade Security Audit Logging System

This module provides comprehensive security event logging and audit trails
for tracking authentication, authorization, and suspicious activity.

Security Benefits:
- Compliance with SOC 2, PCI-DSS, HIPAA audit requirements
- Forensic investigation support
- Intrusion detection and incident response
- Security metric collection and monitoring

Threat Detection:
- Failed authentication attempts (brute force)
- Authorization failures (privilege escalation)
- Rate limit violations (DoS attacks)
- Suspicious patterns (credential stuffing, enumeration)
- Data access violations

Example Usage:
    from covet.security.audit_logger import SecurityAuditLogger, AuditEvent

    # Initialize logger
    logger = SecurityAuditLogger(
        log_file="/var/log/app/security.log",
        console_output=True,
        structured_format=True
    )

    # Log authentication attempt
    logger.log_auth_attempt(
        username="john_doe",
        ip_address="192.168.1.100",
        success=True,
        method="password"
    )

    # Log authorization failure
    logger.log_authz_failure(
        user_id="user123",
        resource="/admin/users",
        action="DELETE",
        reason="insufficient_permissions"
    )

    # Detect suspicious patterns
    if logger.is_suspicious_activity("192.168.1.100"):
        logger.log_security_alert("Possible brute force attack detected")
"""

import hashlib
import json
import logging
import os
import sys
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from threading import Lock
from typing import Any, Deque, Dict, List, Optional, Set


class AuditEventType(Enum):
    """Security audit event types."""

    # Authentication events
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_LOGOUT = "auth_logout"
    AUTH_TOKEN_CREATED = "auth_token_created"
    AUTH_TOKEN_REVOKED = "auth_token_revoked"
    AUTH_TOKEN_EXPIRED = "auth_token_expired"

    # Authorization events
    AUTHZ_SUCCESS = "authz_success"
    AUTHZ_FAILURE = "authz_failure"
    PERMISSION_DENIED = "permission_denied"
    ROLE_ASSIGNED = "role_assigned"
    ROLE_REVOKED = "role_revoked"

    # Rate limiting events
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    RATE_LIMIT_WARNING = "rate_limit_warning"

    # Suspicious activity
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_DETECTED = "brute_force_detected"
    CREDENTIAL_STUFFING = "credential_stuffing"
    ENUMERATION_ATTEMPT = "enumeration_attempt"

    # Data access events
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    SENSITIVE_DATA_ACCESS = "sensitive_data_access"

    # Security configuration changes
    CONFIG_CHANGE = "config_change"
    SECURITY_POLICY_CHANGE = "security_policy_change"

    # General security events
    SECURITY_ALERT = "security_alert"
    SECURITY_WARNING = "security_warning"
    SECURITY_ERROR = "security_error"


class AuditSeverity(Enum):
    """Audit event severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """
    Security audit event.

    Contains all relevant information for security forensics and compliance.
    """

    # Core event information
    event_id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    message: str

    # Actor information
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

    # Action information
    endpoint: Optional[str] = None
    method: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None

    # Result information
    success: bool = False
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    reason: Optional[str] = None

    # Additional context
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)

    # Security context
    auth_method: Optional[str] = None
    permissions_required: List[str] = field(default_factory=list)
    permissions_granted: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        # Convert enums to strings
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        # Convert datetime to ISO format
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)


class AuditLogFormatter(logging.Formatter):
    """Custom formatter for structured audit logs."""

    def __init__(self, structured: bool = True):
        """
        Initialize formatter.

        Args:
            structured: Use JSON format if True, plain text otherwise
        """
        self.structured = structured
        if not structured:
            super().__init__(
                fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )

    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        if self.structured and hasattr(record, "audit_event"):
            # Format as JSON
            event: AuditEvent = record.audit_event
            return event.to_json()
        else:
            # Use default formatting
            return super().format(record)


class SecurityAuditLogger:
    """
    Production-grade security audit logger with threat detection.

    Features:
    - Structured JSON logging for SIEM integration
    - Automatic anomaly detection
    - Rate limit violation tracking
    - Failed authentication tracking
    - Suspicious pattern detection
    - Thread-safe operation
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        console_output: bool = True,
        structured_format: bool = True,
        log_level: str = "INFO",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        enable_anomaly_detection: bool = True,
    ):
        """
        Initialize security audit logger.

        Args:
            log_file: Path to log file (None = logs to stdout only)
            console_output: Enable console output
            structured_format: Use JSON format
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            max_bytes: Maximum log file size before rotation
            backup_count: Number of backup files to keep
            enable_anomaly_detection: Enable automatic threat detection
        """
        self.structured_format = structured_format
        self.enable_anomaly_detection = enable_anomaly_detection

        # Create logger
        self.logger = logging.getLogger("covet.security.audit")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        self.logger.propagate = False

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add console handler
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(AuditLogFormatter(structured_format))
            self.logger.addHandler(console_handler)

        # Add file handler with rotation
        if log_file:
            from logging.handlers import RotatingFileHandler

            # Ensure directory exists
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler.setFormatter(AuditLogFormatter(structured_format))
            self.logger.addHandler(file_handler)

        # Anomaly detection state
        self._lock = Lock()
        self._failed_auth_attempts: Dict[str, Deque[datetime]] = defaultdict(
            lambda: deque(maxlen=100)
        )
        self._rate_limit_violations: Dict[str, int] = defaultdict(int)
        self._suspicious_ips: Set[str] = set()

        # Thresholds for anomaly detection
        self.failed_auth_threshold = 5  # failures in window
        self.failed_auth_window = 300  # 5 minutes
        self.rate_limit_threshold = 10  # violations before alert

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = datetime.utcnow().isoformat()
        random_data = os.urandom(16)
        return hashlib.sha256(
            f"{timestamp}{random_data.hex()}".encode()
        ).hexdigest()[:16]

    def _log_event(self, event: AuditEvent):
        """
        Log an audit event.

        Args:
            event: Audit event to log
        """
        # Map severity to logging level
        level_map = {
            AuditSeverity.DEBUG: logging.DEBUG,
            AuditSeverity.INFO: logging.INFO,
            AuditSeverity.WARNING: logging.WARNING,
            AuditSeverity.ERROR: logging.ERROR,
            AuditSeverity.CRITICAL: logging.CRITICAL,
        }

        level = level_map.get(event.severity, logging.INFO)

        # Create log record with audit event attached
        record = self.logger.makeRecord(
            self.logger.name,
            level,
            "(audit)",
            0,
            event.message,
            (),
            None,
        )
        record.audit_event = event

        self.logger.handle(record)

    def log_auth_attempt(
        self,
        username: str,
        ip_address: str,
        success: bool,
        method: str = "password",
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log authentication attempt.

        Args:
            username: Username attempting authentication
            ip_address: Client IP address
            success: Whether authentication succeeded
            method: Authentication method (password, token, oauth, etc.)
            user_id: User ID if known
            user_agent: Client user agent
            session_id: Session ID if applicable
            metadata: Additional metadata
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=(
                AuditEventType.AUTH_SUCCESS if success
                else AuditEventType.AUTH_FAILURE
            ),
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            timestamp=datetime.utcnow(),
            message=(
                f"Authentication {'succeeded' if success else 'failed'} "
                f"for user {username} from {ip_address}"
            ),
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            success=success,
            auth_method=method,
            metadata=metadata or {},
            tags=["authentication"],
        )

        self._log_event(event)

        # Track failed attempts for anomaly detection
        if not success and self.enable_anomaly_detection:
            self._track_failed_auth(username, ip_address)

    def log_authz_failure(
        self,
        user_id: str,
        resource: str,
        action: str,
        ip_address: Optional[str] = None,
        reason: Optional[str] = None,
        required_permissions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log authorization failure.

        Args:
            user_id: User ID attempting action
            resource: Resource being accessed
            action: Action being attempted
            ip_address: Client IP address
            reason: Reason for denial
            required_permissions: Permissions required
            metadata: Additional metadata
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=AuditEventType.AUTHZ_FAILURE,
            severity=AuditSeverity.WARNING,
            timestamp=datetime.utcnow(),
            message=(
                f"Authorization failed: User {user_id} attempted {action} "
                f"on {resource}"
            ),
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            success=False,
            reason=reason,
            permissions_required=required_permissions or [],
            metadata=metadata or {},
            tags=["authorization", "access_denied"],
        )

        self._log_event(event)

    def log_rate_limit_violation(
        self,
        ip_address: str,
        endpoint: str,
        limit: int,
        window: int,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log rate limit violation.

        Args:
            ip_address: Client IP address
            endpoint: Endpoint that was rate limited
            limit: Rate limit value
            window: Rate limit window in seconds
            user_id: User ID if authenticated
            metadata: Additional metadata
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=AuditEventType.RATE_LIMIT_EXCEEDED,
            severity=AuditSeverity.WARNING,
            timestamp=datetime.utcnow(),
            message=(
                f"Rate limit exceeded: {ip_address} exceeded {limit} "
                f"requests per {window}s on {endpoint}"
            ),
            user_id=user_id,
            ip_address=ip_address,
            endpoint=endpoint,
            success=False,
            metadata={
                **(metadata or {}),
                "limit": limit,
                "window": window,
            },
            tags=["rate_limit", "abuse"],
        )

        self._log_event(event)

        # Track violations for anomaly detection
        if self.enable_anomaly_detection:
            self._track_rate_limit_violation(ip_address)

    def log_suspicious_activity(
        self,
        ip_address: str,
        activity_type: str,
        description: str,
        severity: AuditSeverity = AuditSeverity.WARNING,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log suspicious activity.

        Args:
            ip_address: Client IP address
            activity_type: Type of suspicious activity
            description: Detailed description
            severity: Event severity
            user_id: User ID if applicable
            metadata: Additional metadata
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=AuditEventType.SUSPICIOUS_ACTIVITY,
            severity=severity,
            timestamp=datetime.utcnow(),
            message=f"Suspicious activity detected: {description}",
            user_id=user_id,
            ip_address=ip_address,
            success=False,
            metadata={
                **(metadata or {}),
                "activity_type": activity_type,
            },
            tags=["suspicious", "security_alert"],
        )

        self._log_event(event)

        # Mark IP as suspicious
        with self._lock:
            self._suspicious_ips.add(ip_address)

    def log_data_access(
        self,
        user_id: str,
        resource: str,
        action: str,
        sensitive: bool = False,
        ip_address: Optional[str] = None,
        record_count: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log data access event.

        Args:
            user_id: User ID accessing data
            resource: Resource being accessed
            action: Action performed (read, write, delete)
            sensitive: Whether data is sensitive (PII, financial, etc.)
            ip_address: Client IP address
            record_count: Number of records accessed
            metadata: Additional metadata
        """
        event_type = (
            AuditEventType.SENSITIVE_DATA_ACCESS if sensitive
            else AuditEventType.DATA_ACCESS
        )

        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=event_type,
            severity=AuditSeverity.INFO if not sensitive else AuditSeverity.WARNING,
            timestamp=datetime.utcnow(),
            message=(
                f"{'Sensitive ' if sensitive else ''}Data access: "
                f"User {user_id} performed {action} on {resource}"
            ),
            user_id=user_id,
            ip_address=ip_address,
            resource=resource,
            action=action,
            success=True,
            metadata={
                **(metadata or {}),
                "sensitive": sensitive,
                "record_count": record_count,
            },
            tags=["data_access"] + (["sensitive"] if sensitive else []),
        )

        self._log_event(event)

    def log_security_alert(
        self,
        message: str,
        severity: AuditSeverity = AuditSeverity.CRITICAL,
        alert_type: str = "generic",
        ip_address: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Log security alert.

        Args:
            message: Alert message
            severity: Alert severity
            alert_type: Type of alert
            ip_address: Related IP address
            user_id: Related user ID
            metadata: Additional metadata
        """
        event = AuditEvent(
            event_id=self._generate_event_id(),
            event_type=AuditEventType.SECURITY_ALERT,
            severity=severity,
            timestamp=datetime.utcnow(),
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            success=False,
            metadata={
                **(metadata or {}),
                "alert_type": alert_type,
            },
            tags=["security_alert", "incident"],
        )

        self._log_event(event)

    def _track_failed_auth(self, username: str, ip_address: str):
        """
        Track failed authentication attempts for anomaly detection.

        Detects potential brute force attacks based on:
        - Multiple failures from same IP
        - Multiple failures for same username
        """
        with self._lock:
            now = datetime.utcnow()

            # Track by IP
            self._failed_auth_attempts[ip_address].append(now)

            # Track by username
            username_key = f"user:{username}"
            self._failed_auth_attempts[username_key].append(now)

            # Check for brute force attack
            self._check_brute_force(ip_address, "ip")
            self._check_brute_force(username_key, "username")

    def _check_brute_force(self, key: str, key_type: str):
        """Check for brute force attack pattern."""
        attempts = self._failed_auth_attempts[key]
        if len(attempts) < self.failed_auth_threshold:
            return

        # Count recent failures
        cutoff = datetime.utcnow() - timedelta(seconds=self.failed_auth_window)
        recent_failures = sum(1 for dt in attempts if dt > cutoff)

        if recent_failures >= self.failed_auth_threshold:
            # Brute force detected
            identifier = key.replace("user:", "")
            self.log_security_alert(
                message=(
                    f"Possible brute force attack detected: "
                    f"{recent_failures} failed attempts for {key_type} {identifier}"
                ),
                severity=AuditSeverity.CRITICAL,
                alert_type="brute_force",
                ip_address=identifier if key_type == "ip" else None,
                metadata={
                    "key_type": key_type,
                    "failure_count": recent_failures,
                    "window_seconds": self.failed_auth_window,
                },
            )

    def _track_rate_limit_violation(self, ip_address: str):
        """Track rate limit violations for anomaly detection."""
        with self._lock:
            self._rate_limit_violations[ip_address] += 1

            if self._rate_limit_violations[ip_address] >= self.rate_limit_threshold:
                self.log_security_alert(
                    message=(
                        f"Excessive rate limit violations from {ip_address}: "
                        f"{self._rate_limit_violations[ip_address]} violations"
                    ),
                    severity=AuditSeverity.CRITICAL,
                    alert_type="rate_limit_abuse",
                    ip_address=ip_address,
                )

    def is_suspicious_activity(self, ip_address: str) -> bool:
        """
        Check if IP address has shown suspicious activity.

        Args:
            ip_address: IP address to check

        Returns:
            True if IP is marked as suspicious
        """
        with self._lock:
            return ip_address in self._suspicious_ips

    def get_failed_auth_count(self, identifier: str, key_type: str = "ip") -> int:
        """
        Get recent failed authentication count.

        Args:
            identifier: IP address or username
            key_type: "ip" or "username"

        Returns:
            Number of recent failures
        """
        key = identifier if key_type == "ip" else f"user:{identifier}"

        with self._lock:
            attempts = self._failed_auth_attempts.get(key, deque())
            cutoff = datetime.utcnow() - timedelta(seconds=self.failed_auth_window)
            return sum(1 for dt in attempts if dt > cutoff)

    def clear_suspicious_ip(self, ip_address: str):
        """
        Clear suspicious flag for IP address.

        Args:
            ip_address: IP address to clear
        """
        with self._lock:
            self._suspicious_ips.discard(ip_address)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit logger statistics.

        Returns:
            Dictionary of statistics
        """
        with self._lock:
            return {
                "tracked_ips": len(self._failed_auth_attempts),
                "suspicious_ips": len(self._suspicious_ips),
                "rate_limit_violations": len(self._rate_limit_violations),
            }


# Global audit logger instance
_audit_logger: Optional[SecurityAuditLogger] = None


def get_audit_logger() -> SecurityAuditLogger:
    """Get global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SecurityAuditLogger()
    return _audit_logger


def configure_audit_logger(
    log_file: Optional[str] = None,
    console_output: bool = True,
    structured_format: bool = True,
    log_level: str = "INFO",
) -> SecurityAuditLogger:
    """
    Configure global audit logger.

    Args:
        log_file: Path to log file
        console_output: Enable console output
        structured_format: Use JSON format
        log_level: Logging level

    Returns:
        Configured audit logger
    """
    global _audit_logger
    _audit_logger = SecurityAuditLogger(
        log_file=log_file,
        console_output=console_output,
        structured_format=structured_format,
        log_level=log_level,
    )
    return _audit_logger


__all__ = [
    "SecurityAuditLogger",
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "get_audit_logger",
    "configure_audit_logger",
]
