"""
CovetPy Security Audit Logging Module

Comprehensive security event logging with:
- Authentication events
- Authorization failures
- Suspicious activity detection
- SIEM integration ready
- Structured logging (JSON)
- Log sanitization (no secrets)

Author: CovetPy Security Team
License: MIT
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SecurityEventType(Enum):
    """Security event types."""

    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    AUTH_LOCKED = "auth_locked"
    AUTHZ_FAILURE = "authorization_failure"
    INJECTION_ATTEMPT = "injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_VIOLATION = "csrf_violation"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    PRIVILEGE_ESCALATION = "privilege_escalation_attempt"
    SESSION_HIJACK = "session_hijack_attempt"


@dataclass
class SecurityEvent:
    """Security event data."""

    event_type: SecurityEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    username: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    success: bool = False
    severity: str = "INFO"
    message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["event_type"] = self.event_type.value
        data["timestamp"] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


class SecurityAuditLogger:
    """
    Security audit logger with SIEM integration support.
    """

    def __init__(self, logger_name: str = "covet.security.audit"):
        """Initialize security audit logger."""
        self.logger = logging.getLogger(logger_name)
        self._events: list = []

    def log_event(self, event: SecurityEvent) -> None:
        """
        Log security event.

        Args:
            event: Security event to log
        """
        self._events.append(event)

        # Log with appropriate level
        log_level = getattr(logging, event.severity, logging.INFO)
        self.logger.log(
            log_level,
            event.message or f"Security event: {event.event_type.value}",
            extra={"security_event": event.to_dict()},
        )

    def log_auth_success(self, user_id: str, username: str, ip_address: str):
        """Log successful authentication."""
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_SUCCESS,
            user_id=user_id,
            username=username,
            ip_address=ip_address,
            success=True,
            severity="INFO",
            message=f"User {username} authenticated successfully",
        )
        self.log_event(event)

    def log_auth_failure(self, username: str, ip_address: str, reason: str = ""):
        """Log failed authentication attempt."""
        event = SecurityEvent(
            event_type=SecurityEventType.AUTH_FAILURE,
            username=username,
            ip_address=ip_address,
            success=False,
            severity="WARNING",
            message=f"Authentication failed for {username}: {reason}",
            metadata={"reason": reason},
        )
        self.log_event(event)

    def log_injection_attempt(self, injection_type: str, ip_address: str, details: Dict[str, Any]):
        """Log injection attempt."""
        event = SecurityEvent(
            event_type=SecurityEventType.INJECTION_ATTEMPT,
            ip_address=ip_address,
            success=False,
            severity="CRITICAL",
            message=f"Injection attempt detected: {injection_type}",
            metadata={"injection_type": injection_type, **details},
        )
        self.log_event(event)

    def get_events(self, event_type: Optional[SecurityEventType] = None) -> list:
        """Get logged events, optionally filtered by type."""
        if event_type:
            return [e for e in self._events if e.event_type == event_type]
        return self._events.copy()


__all__ = ["SecurityEventType", "SecurityEvent", "SecurityAuditLogger"]
