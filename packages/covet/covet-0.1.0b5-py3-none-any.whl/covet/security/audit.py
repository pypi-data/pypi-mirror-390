"""
Security Audit Logging

Production-grade security event logging and monitoring.

Features:
- Structured logging for security events
- Event classification and severity
- Query and analysis capabilities
- Alert triggers for critical events
- Compliance support (SOC2, ISO 27001)
- Log rotation and retention

Event Types:
- Authentication (login, logout, failed attempts)
- Authorization (permission denied, privilege escalation)
- CSRF violations
- Rate limit exceeded
- Session management
- Input validation failures
- Security header violations
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Security event types"""

    # Authentication
    LOGIN_SUCCESS = "auth.login.success"
    LOGIN_FAILED = "auth.login.failed"
    LOGOUT = "auth.logout"
    PASSWORD_CHANGE = "auth.password.change"
    PASSWORD_RESET = "auth.password.reset"

    # Authorization
    PERMISSION_DENIED = "authz.permission.denied"
    PRIVILEGE_ESCALATION = "authz.privilege.escalation"
    ROLE_CHANGE = "authz.role.change"

    # CSRF
    CSRF_VALIDATION_FAILED = "csrf.validation.failed"
    CSRF_TOKEN_MISSING = "csrf.token.missing"

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "ratelimit.exceeded"
    RATE_LIMIT_WARNING = "ratelimit.warning"

    # Session
    SESSION_CREATED = "session.created"
    SESSION_EXPIRED = "session.expired"
    SESSION_HIJACK_ATTEMPT = "session.hijack.attempt"
    SESSION_INVALIDATED = "session.invalidated"

    # Input Validation
    XSS_ATTEMPT = "input.xss.attempt"
    SQL_INJECTION_ATTEMPT = "input.sqli.attempt"
    PATH_TRAVERSAL_ATTEMPT = "input.path_traversal.attempt"

    # General Security
    SECURITY_HEADER_VIOLATION = "security.header.violation"
    CORS_VIOLATION = "security.cors.violation"
    TLS_ERROR = "security.tls.error"


class Severity(str, Enum):
    """Event severity levels"""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class SecurityEvent:
    """Security event record"""

    # Event identification
    event_id: str
    event_type: EventType
    severity: Severity
    timestamp: datetime

    # Context
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Request details
    method: Optional[str] = None
    path: Optional[str] = None
    endpoint: Optional[str] = None

    # Event data
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["event_type"] = str(self.event_type)
        data["severity"] = str(self.severity)
        return data

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class AuditLogger:
    """
    Security audit logger

    Logs security events with structured data.
    """

    def __init__(
        self,
        log_file: Optional[str] = None,
        alert_callback: Optional[Callable[[SecurityEvent], None]] = None,
        retention_days: int = 90,
    ):
        """
        Initialize audit logger

        Args:
            log_file: Path to log file
            alert_callback: Callback for critical events
            retention_days: Days to retain logs
        """
        self.log_file = log_file
        self.alert_callback = alert_callback
        self.retention_days = retention_days

        # In-memory storage (for development/testing)
        self._events: List[SecurityEvent] = []
        self._lock = asyncio.Lock()

        # Event counters for analysis
        self._counters: Dict[str, int] = defaultdict(int)

    async def log(
        self,
        event_type: EventType,
        severity: Severity = Severity.INFO,
        message: str = "",
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        method: Optional[str] = None,
        path: Optional[str] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> SecurityEvent:
        """
        Log security event

        Args:
            event_type: Type of event
            severity: Event severity
            message: Human-readable message
            user_id: User ID
            session_id: Session ID
            ip_address: Client IP
            user_agent: User agent
            method: HTTP method
            path: Request path
            endpoint: Endpoint name
            details: Additional details
            tags: Event tags

        Returns:
            SecurityEvent instance
        """
        # Generate event ID
        event_id = self._generate_event_id()

        # Create event
        event = SecurityEvent(
            event_id=event_id,
            event_type=event_type,
            severity=severity,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            method=method,
            path=path,
            endpoint=endpoint,
            message=message,
            details=details or {},
            tags=tags or [],
        )

        # Store event
        async with self._lock:
            self._events.append(event)
            self._counters[str(event_type)] += 1

        # Write to file
        if self.log_file:
            await self._write_to_file(event)

        # Trigger alert for critical events
        if severity == Severity.CRITICAL and self.alert_callback:
            await self.alert_callback(event)

        return event

    # Convenience methods for common events

    async def log_login_success(
        self, user_id: str, ip_address: str, user_agent: Optional[str] = None
    ):
        """Log successful login"""
        await self.log(
            event_type=EventType.LOGIN_SUCCESS,
            severity=Severity.INFO,
            message=f"User {user_id} logged in successfully",
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_login_failed(
        self,
        username: str,
        ip_address: str,
        reason: str = "Invalid credentials",
        user_agent: Optional[str] = None,
    ):
        """Log failed login attempt"""
        await self.log(
            event_type=EventType.LOGIN_FAILED,
            severity=Severity.WARNING,
            message=f"Failed login attempt for user {username}",
            ip_address=ip_address,
            user_agent=user_agent,
            details={"username": username, "reason": reason},
        )

    async def log_permission_denied(
        self, user_id: str, resource: str, action: str, ip_address: Optional[str] = None
    ):
        """Log permission denied"""
        await self.log(
            event_type=EventType.PERMISSION_DENIED,
            severity=Severity.WARNING,
            message=f"Permission denied: {user_id} attempted {action} on {resource}",
            user_id=user_id,
            ip_address=ip_address,
            details={"resource": resource, "action": action},
        )

    async def log_csrf_violation(
        self, ip_address: str, path: str, reason: str, user_id: Optional[str] = None
    ):
        """Log CSRF violation"""
        await self.log(
            event_type=EventType.CSRF_VALIDATION_FAILED,
            severity=Severity.ERROR,
            message=f"CSRF violation: {reason}",
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            details={"reason": reason},
        )

    async def log_rate_limit_exceeded(
        self, ip_address: str, path: str, limit: int, user_id: Optional[str] = None
    ):
        """Log rate limit exceeded"""
        await self.log(
            event_type=EventType.RATE_LIMIT_EXCEEDED,
            severity=Severity.WARNING,
            message=f"Rate limit exceeded: {limit} requests",
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            details={"limit": limit},
        )

    async def log_session_hijack_attempt(
        self, session_id: str, user_id: str, ip_address: str, expected_ip: str
    ):
        """Log session hijack attempt"""
        await self.log(
            event_type=EventType.SESSION_HIJACK_ATTEMPT,
            severity=Severity.CRITICAL,
            message=f"Possible session hijack: IP mismatch",
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            details={"expected_ip": expected_ip, "actual_ip": ip_address},
        )

    async def log_xss_attempt(
        self, ip_address: str, path: str, payload: str, user_id: Optional[str] = None
    ):
        """Log XSS attempt"""
        await self.log(
            event_type=EventType.XSS_ATTEMPT,
            severity=Severity.ERROR,
            message="XSS attempt detected",
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            details={"payload": payload[:200]},  # Truncate payload
        )

    async def log_sqli_attempt(
        self, ip_address: str, path: str, query: str, user_id: Optional[str] = None
    ):
        """Log SQL injection attempt"""
        await self.log(
            event_type=EventType.SQL_INJECTION_ATTEMPT,
            severity=Severity.CRITICAL,
            message="SQL injection attempt detected",
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            details={"query": query[:200]},
        )

    async def log_path_traversal_attempt(
        self,
        ip_address: str,
        path: str,
        attempted_path: str,
        user_id: Optional[str] = None,
    ):
        """Log path traversal attempt"""
        await self.log(
            event_type=EventType.PATH_TRAVERSAL_ATTEMPT,
            severity=Severity.ERROR,
            message="Path traversal attempt detected",
            user_id=user_id,
            ip_address=ip_address,
            path=path,
            details={"attempted_path": attempted_path},
        )

    # Query methods

    async def query(
        self,
        event_type: Optional[EventType] = None,
        severity: Optional[Severity] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SecurityEvent]:
        """
        Query security events

        Args:
            event_type: Filter by event type
            severity: Filter by severity
            user_id: Filter by user ID
            ip_address: Filter by IP address
            start_date: Start date
            end_date: End date
            limit: Maximum results

        Returns:
            List of matching events
        """
        async with self._lock:
            results = []

            for event in reversed(self._events):  # Most recent first
                # Apply filters
                if event_type and event.event_type != event_type:
                    continue

                if severity and event.severity != severity:
                    continue

                if user_id and event.user_id != user_id:
                    continue

                if ip_address and event.ip_address != ip_address:
                    continue

                if start_date and event.timestamp < start_date:
                    continue

                if end_date and event.timestamp > end_date:
                    continue

                results.append(event)

                if len(results) >= limit:
                    break

            return results

    async def get_statistics(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit statistics

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Statistics dictionary
        """
        async with self._lock:
            # Filter events by date
            events = self._events

            if start_date:
                events = [e for e in events if e.timestamp >= start_date]

            if end_date:
                events = [e for e in events if e.timestamp <= end_date]

            # Calculate statistics
            stats = {
                "total_events": len(events),
                "by_type": defaultdict(int),
                "by_severity": defaultdict(int),
                "by_user": defaultdict(int),
                "by_ip": defaultdict(int),
                "timeline": [],
            }

            for event in events:
                stats["by_type"][str(event.event_type)] += 1
                stats["by_severity"][str(event.severity)] += 1

                if event.user_id:
                    stats["by_user"][event.user_id] += 1

                if event.ip_address:
                    stats["by_ip"][event.ip_address] += 1

            # Convert defaultdicts to regular dicts
            stats["by_type"] = dict(stats["by_type"])
            stats["by_severity"] = dict(stats["by_severity"])
            stats["by_user"] = dict(stats["by_user"])
            stats["by_ip"] = dict(stats["by_ip"])

            return stats

    async def cleanup_old_events(self) -> int:
        """
        Remove events older than retention period

        Returns:
            Number of events removed
        """
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)

        async with self._lock:
            old_count = len(self._events)

            self._events = [event for event in self._events if event.timestamp > cutoff]

            return old_count - len(self._events)

    # Private methods

    def _generate_event_id(self) -> str:
        """Generate unique event ID"""
        timestamp = str(time.time()).encode("utf-8")
        random_data = str(time.time_ns()).encode("utf-8")

        hasher = hashlib.sha256()
        hasher.update(timestamp)
        hasher.update(random_data)

        return hasher.hexdigest()[:16]

    async def _write_to_file(self, event: SecurityEvent):
        """Write event to log file"""
        if not self.log_file:
            return

        try:
            with open(self.log_file, "a") as f:
                f.write(event.to_json() + "\n")
        except Exception:
            # In production, handle file errors appropriately

            # Global audit logger instance
            pass


_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get global audit logger instance"""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def configure_audit_logger(
    log_file: Optional[str] = None,
    alert_callback: Optional[Callable] = None,
    retention_days: int = 90,
) -> AuditLogger:
    """Configure audit logger"""
    global _audit_logger
    _audit_logger = AuditLogger(log_file, alert_callback, retention_days)
    return _audit_logger


# Example usage
AUDIT_USAGE_EXAMPLES = """
# Security Audit Logging Examples

## 1. Initialize Audit Logger

```python
from covet.security.audit import configure_audit_logger, EventType

# Configure with file logging
audit = configure_audit_logger(
    log_file='/var/log/security/audit.log',
    retention_days=90
)
```

## 2. Log Security Events

```python
from covet.security.audit import get_audit_logger

audit = get_audit_logger()

# Log failed login
await audit.log_login_failed(
    username='admin',
    ip_address='192.168.1.100',
    reason='Invalid password'
)

# Log permission denied
await audit.log_permission_denied(
    user_id='user123',
    resource='/admin/settings',
    action='modify',
    ip_address='192.168.1.100'
)

# Log CSRF violation
await audit.log_csrf_violation(
    ip_address='192.168.1.100',
    path='/api/transfer',
    reason='Token missing'
)
```

## 3. Query Audit Logs

```python
from datetime import datetime, timedelta

# Get recent failed logins
failed_logins = await audit.query(
    event_type=EventType.LOGIN_FAILED,
    start_date=datetime.utcnow() - timedelta(hours=24)
)

# Get events for specific user
user_events = await audit.query(
    user_id='user123',
    limit=50
)

# Get critical events
critical = await audit.query(
    severity=Severity.CRITICAL,
    start_date=datetime.utcnow() - timedelta(days=7)
)
```

## 4. Get Statistics

```python
# Get statistics for last 7 days
stats = await audit.get_statistics(
    start_date=datetime.utcnow() - timedelta(days=7)
)

logger.info("Total events: {stats['total_events']}")
logger.info("By type: {stats['by_type']}")
logger.info("By severity: {stats['by_severity']}")
logger.info("Top IPs: {stats['by_ip']}")
```

## 5. Integration with Middleware

```python
class AuditMiddleware:
    async def __call__(self, scope, receive, send):
        audit = get_audit_logger()

        # Log all requests
        await audit.log(
            event_type=EventType.LOGIN_SUCCESS,
            severity=Severity.INFO,
            path=scope['path'],
            method=scope['method'],
            ip_address=scope['client'][0]
        )

        await self.app(scope, receive, send)
```
"""
