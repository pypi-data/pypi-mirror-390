"""
Security Manager and Audit Logging

Comprehensive security monitoring and audit logging system:
- Security event logging and monitoring
- Threat detection and alerting
- Compliance reporting
- Security metrics and analytics
- Incident response automation
"""

import hashlib
import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .exceptions import SecurityViolationError
from .models import LoginAttempt, LoginAttemptResult, User

logger = logging.getLogger(__name__)


class SecurityEventType(Enum):
    """Types of security events"""

    # Authentication events
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET = "password_reset"

    # Authorization events
    PERMISSION_DENIED = "permission_denied"
    ROLE_CHANGE = "role_change"
    PRIVILEGE_ESCALATION = "privilege_escalation"

    # Account events
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_DISABLED = "account_disabled"
    TWO_FACTOR_ENABLED = "two_factor_enabled"
    TWO_FACTOR_DISABLED = "two_factor_disabled"

    # Security violations
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SUSPICIOUS_LOGIN = "suspicious_login"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    CSRF_VIOLATION = "csrf_violation"

    # System events
    SESSION_HIJACK_ATTEMPT = "session_hijack_attempt"
    TOKEN_MANIPULATION = "token_manipulation"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"


class SecurityEventSeverity(Enum):
    """Security event severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event record"""

    event_type: SecurityEventType
    severity: SecurityEventSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # User and session info
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Network info
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Event details
    description: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    # Response info
    action_taken: Optional[str] = None
    blocked: bool = False

    # Compliance tracking
    compliance_tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = self.event_type.value
        data["severity"] = self.severity.value
        return data


@dataclass
class SecurityMetrics:
    """Security metrics and statistics"""

    # Authentication metrics
    total_logins: int = 0
    failed_logins: int = 0
    successful_logins: int = 0

    # Account metrics
    active_users: int = 0
    locked_accounts: int = 0
    two_factor_enabled_users: int = 0

    # Security events
    security_violations: int = 0
    blocked_requests: int = 0

    # Time-based metrics
    events_last_hour: int = 0
    events_last_day: int = 0

    # Top threats
    top_attacking_ips: List[tuple[str, int]] = field(default_factory=list)
    top_targeted_users: List[tuple[str, int]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class ThreatDetector:
    """Real-time threat detection system"""

    def __init__(self):
        self.failed_login_threshold = 5
        self.failed_login_window_minutes = 15
        self.suspicious_ip_threshold = 10
        self.rapid_request_threshold = 100
        self.rapid_request_window_seconds = 60

        # Tracking data
        self.failed_logins: Dict[str, deque] = defaultdict(deque)  # user_id -> timestamps
        self.ip_activity: Dict[str, deque] = defaultdict(deque)  # ip -> timestamps
        self.request_counts: Dict[str, deque] = defaultdict(deque)  # ip -> timestamps

        self.lock = threading.RLock()

    def detect_threats(self, event: SecurityEvent) -> List[SecurityEvent]:
        """Detect threats based on security event"""
        threats = []

        with self.lock:
            # Detect brute force attacks
            if event.event_type == SecurityEventType.LOGIN_FAILED:
                if self._is_brute_force_attack(event):
                    threats.append(
                        SecurityEvent(
                            event_type=SecurityEventType.BRUTE_FORCE_ATTEMPT,
                            severity=SecurityEventSeverity.HIGH,
                            user_id=event.user_id,
                            ip_address=event.ip_address,
                            description=f"Brute force attack detected from {event.ip_address}",
                            details={"original_event": event.to_dict()},
                        )
                    )

            # Detect suspicious IP activity
            if event.ip_address:
                self._track_ip_activity(event.ip_address)
                if self._is_suspicious_ip(event.ip_address):
                    threats.append(
                        SecurityEvent(
                            event_type=SecurityEventType.SUSPICIOUS_LOGIN,
                            severity=SecurityEventSeverity.MEDIUM,
                            ip_address=event.ip_address,
                            description=f"Suspicious activity from IP {event.ip_address}",
                            details={"activity_count": len(self.ip_activity[event.ip_address])},
                        )
                    )

            # Detect rapid requests (potential DDoS)
            if event.ip_address:
                self._track_request_rate(event.ip_address)
                if self._is_rapid_requests(event.ip_address):
                    threats.append(
                        SecurityEvent(
                            event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                            severity=SecurityEventSeverity.MEDIUM,
                            ip_address=event.ip_address,
                            description=f"Rapid requests detected from {event.ip_address}",
                            details={"request_count": len(self.request_counts[event.ip_address])},
                        )
                    )

        return threats

    def _is_brute_force_attack(self, event: SecurityEvent) -> bool:
        """Check if failed login indicates brute force attack"""
        if not event.user_id:
            return False

        now = time.time()
        window_start = now - (self.failed_login_window_minutes * 60)

        # Track failed login
        self.failed_logins[event.user_id].append(now)

        # Clean old entries
        while (
            self.failed_logins[event.user_id]
            and self.failed_logins[event.user_id][0] < window_start
        ):
            self.failed_logins[event.user_id].popleft()

        return len(self.failed_logins[event.user_id]) >= self.failed_login_threshold

    def _track_ip_activity(self, ip_address: str):
        """Track IP activity"""
        now = time.time()
        window_start = now - (60 * 60)  # 1 hour window

        self.ip_activity[ip_address].append(now)

        # Clean old entries
        while self.ip_activity[ip_address] and self.ip_activity[ip_address][0] < window_start:
            self.ip_activity[ip_address].popleft()

    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Check if IP has suspicious activity"""
        return len(self.ip_activity[ip_address]) >= self.suspicious_ip_threshold

    def _track_request_rate(self, ip_address: str):
        """Track request rate for IP"""
        now = time.time()
        window_start = now - self.rapid_request_window_seconds

        self.request_counts[ip_address].append(now)

        # Clean old entries
        while self.request_counts[ip_address] and self.request_counts[ip_address][0] < window_start:
            self.request_counts[ip_address].popleft()

    def _is_rapid_requests(self, ip_address: str) -> bool:
        """Check if IP is making rapid requests"""
        return len(self.request_counts[ip_address]) >= self.rapid_request_threshold


class AuditLogger:
    """Secure audit logging system"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file or "security_audit.log"
        # Keep last 10k events in memory
        self.events: deque = deque(maxlen=10000)
        self.lock = threading.RLock()

    def log_event(self, event: SecurityEvent):
        """Log security event"""
        with self.lock:
            # Add to memory store
            self.events.append(event)

            # Write to file
            self._write_to_file(event)

    def _write_to_file(self, event: SecurityEvent):
        """Write event to log file"""
        try:
            log_entry = {
                "timestamp": event.timestamp.isoformat(),
                "event_type": event.event_type.value,
                "severity": event.severity.value,
                "user_id": event.user_id,
                "ip_address": event.ip_address,
                "description": event.description,
                "details": event.details,
                "checksum": self._calculate_checksum(event),
            }

            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        except Exception as e:
            # In production, use proper logging
            logger.error("Failed to write audit log: {e}")

    def _calculate_checksum(self, event: SecurityEvent) -> str:
        """Calculate checksum for log integrity"""
        data = f"{event.timestamp.isoformat()}{event.event_type.value}{event.user_id or ''}{event.ip_address or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[SecurityEventType] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> List[SecurityEvent]:
        """Query security events"""
        with self.lock:
            events = list(self.events)

            # Apply filters
            if start_time:
                events = [e for e in events if e.timestamp >= start_time]

            if end_time:
                events = [e for e in events if e.timestamp <= end_time]

            if event_type:
                events = [e for e in events if e.event_type == event_type]

            if user_id:
                events = [e for e in events if e.user_id == user_id]

            if ip_address:
                events = [e for e in events if e.ip_address == ip_address]

            return events


class ComplianceReporter:
    """Generate compliance reports"""

    def __init__(self, audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    def generate_access_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate access control compliance report"""
        events = self.audit_logger.get_events(start_time, end_time)

        access_events = [
            e
            for e in events
            if e.event_type
            in [
                SecurityEventType.LOGIN_SUCCESS,
                SecurityEventType.LOGIN_FAILED,
                SecurityEventType.PERMISSION_DENIED,
            ]
        ]

        return {
            "period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
            "summary": {
                "total_access_attempts": len(access_events),
                "successful_logins": len(
                    [e for e in access_events if e.event_type == SecurityEventType.LOGIN_SUCCESS]
                ),
                "failed_logins": len(
                    [e for e in access_events if e.event_type == SecurityEventType.LOGIN_FAILED]
                ),
                "permission_denials": len(
                    [
                        e
                        for e in access_events
                        if e.event_type == SecurityEventType.PERMISSION_DENIED
                    ]
                ),
            },
            "events": [e.to_dict() for e in access_events],
        }

    def generate_security_report(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Generate security incident report"""
        events = self.audit_logger.get_events(start_time, end_time)

        security_events = [
            e
            for e in events
            if e.event_type
            in [
                SecurityEventType.BRUTE_FORCE_ATTEMPT,
                SecurityEventType.SUSPICIOUS_LOGIN,
                SecurityEventType.RATE_LIMIT_EXCEEDED,
                SecurityEventType.CSRF_VIOLATION,
            ]
        ]

        # Group by severity
        by_severity = defaultdict(list)
        for event in security_events:
            by_severity[event.severity.value].append(event)

        return {
            "period": {"start": start_time.isoformat(), "end": end_time.isoformat()},
            "summary": {
                "total_incidents": len(security_events),
                "critical": len(by_severity["critical"]),
                "high": len(by_severity["high"]),
                "medium": len(by_severity["medium"]),
                "low": len(by_severity["low"]),
            },
            "incidents_by_severity": {
                severity: [e.to_dict() for e in events] for severity, events in by_severity.items()
            },
        }


class SecurityManager:
    """
    Central security management system
    """

    def __init__(self, log_file: Optional[str] = None):
        self.audit_logger = AuditLogger(log_file)
        self.threat_detector = ThreatDetector()
        self.compliance_reporter = ComplianceReporter(self.audit_logger)
        self.alert_handlers: List[Callable[[SecurityEvent], None]] = []
        self.metrics = SecurityMetrics()

    def log_security_event(self, event: SecurityEvent):
        """Log security event and detect threats"""
        # Log the event
        self.audit_logger.log_event(event)

        # Update metrics
        self._update_metrics(event)

        # Detect threats
        threats = self.threat_detector.detect_threats(event)

        # Log and handle threats
        for threat in threats:
            self.audit_logger.log_event(threat)
            self._handle_threat(threat)

    def add_alert_handler(self, handler: Callable[[SecurityEvent], None]):
        """Add security alert handler"""
        self.alert_handlers.append(handler)

    def _update_metrics(self, event: SecurityEvent):
        """Update security metrics"""
        if event.event_type == SecurityEventType.LOGIN_SUCCESS:
            self.metrics.successful_logins += 1
            self.metrics.total_logins += 1
        elif event.event_type == SecurityEventType.LOGIN_FAILED:
            self.metrics.failed_logins += 1
            self.metrics.total_logins += 1
        elif event.event_type in [
            SecurityEventType.BRUTE_FORCE_ATTEMPT,
            SecurityEventType.SUSPICIOUS_LOGIN,
            SecurityEventType.CSRF_VIOLATION,
        ]:
            self.metrics.security_violations += 1

        if event.blocked:
            self.metrics.blocked_requests += 1

    def _handle_threat(self, threat: SecurityEvent):
        """Handle detected threat"""
        # Send alerts
        for handler in self.alert_handlers:
            try:
                handler(threat)
            except Exception as e:
                # Log error handling failure

                # Automatic response based on threat type
                pass
        if threat.event_type == SecurityEventType.BRUTE_FORCE_ATTEMPT:
            # Could implement automatic IP blocking here
            pass
        elif threat.event_type == SecurityEventType.RATE_LIMIT_EXCEEDED:
            # Could implement temporary rate limiting here

            pass

    def get_security_metrics(self) -> SecurityMetrics:
        """Get current security metrics"""
        # Update time-based metrics
        now = datetime.utcnow()
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)

        recent_events = self.audit_logger.get_events(hour_ago)
        daily_events = self.audit_logger.get_events(day_ago)

        self.metrics.events_last_hour = len(recent_events)
        self.metrics.events_last_day = len(daily_events)

        return self.metrics

    def generate_compliance_report(
        self, report_type: str, start_time: datetime, end_time: datetime
    ) -> Dict[str, Any]:
        """Generate compliance report"""
        if report_type == "access":
            return self.compliance_reporter.generate_access_report(start_time, end_time)
        elif report_type == "security":
            return self.compliance_reporter.generate_security_report(start_time, end_time)
        else:
            raise ValueError(f"Unknown report type: {report_type}")


# Global security manager instance
_security_manager_instance: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    """Get security manager singleton instance"""
    global _security_manager_instance
    if _security_manager_instance is None:
        _security_manager_instance = SecurityManager()
    return _security_manager_instance


def configure_security_manager(log_file: Optional[str] = None) -> SecurityManager:
    """Configure security manager with custom settings"""
    global _security_manager_instance
    _security_manager_instance = SecurityManager(log_file)
    return _security_manager_instance


# Convenience functions for logging common events
def log_login_success(user_id: str, ip_address: str, session_id: Optional[str] = None):
    """Log successful login"""
    security_manager = get_security_manager()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_SUCCESS,
        severity=SecurityEventSeverity.LOW,
        user_id=user_id,
        ip_address=ip_address,
        session_id=session_id,
        description=f"User {user_id} logged in successfully",
    )
    security_manager.log_security_event(event)


def log_login_failed(user_id: Optional[str], ip_address: str, reason: str = ""):
    """Log failed login"""
    security_manager = get_security_manager()
    event = SecurityEvent(
        event_type=SecurityEventType.LOGIN_FAILED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
        description=f"Login failed for user {user_id or 'unknown'}: {reason}",
        details={"failure_reason": reason},
    )
    security_manager.log_security_event(event)


def log_permission_denied(user_id: str, resource: str, action: str, ip_address: str):
    """Log permission denied"""
    security_manager = get_security_manager()
    event = SecurityEvent(
        event_type=SecurityEventType.PERMISSION_DENIED,
        severity=SecurityEventSeverity.MEDIUM,
        user_id=user_id,
        ip_address=ip_address,
        description=f"Permission denied for {resource}:{action}",
        details={"resource": resource, "action": action},
    )
    security_manager.log_security_event(event)
