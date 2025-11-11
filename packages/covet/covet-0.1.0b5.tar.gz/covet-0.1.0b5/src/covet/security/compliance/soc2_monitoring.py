"""
SOC 2 Security Monitoring and Incident Response

Continuous monitoring and incident response for SOC 2 compliance.
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class SecurityEventSeverity(str, Enum):
    """Security event severity."""

    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident response status."""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


@dataclass
class SecurityEvent:
    """Security monitoring event."""

    event_id: str
    timestamp: datetime
    event_type: str
    severity: SecurityEventSeverity
    source: str
    description: str
    indicators: Dict[str, Any] = field(default_factory=dict)
    escalated: bool = False


@dataclass
class IncidentResponse:
    """Security incident response."""

    incident_id: str
    detected_at: datetime
    severity: SecurityEventSeverity
    status: IncidentStatus
    description: str
    affected_systems: List[str]
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    responders: List[str] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    lessons_learned: Optional[str] = None
    closed_at: Optional[datetime] = None


class SOC2Monitor:
    """SOC 2 security monitoring and incident response."""

    def __init__(self):
        """Initialize SOC 2 monitor."""
        self.events: List[SecurityEvent] = []
        self.incidents: Dict[str, IncidentResponse] = {}

    def log_event(
        self,
        event_type: str,
        severity: SecurityEventSeverity,
        source: str,
        description: str,
        **indicators,
    ) -> SecurityEvent:
        """Log security event."""
        event = SecurityEvent(
            event_id=f"evt_{secrets.token_hex(12)}",
            timestamp=datetime.utcnow(),
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            indicators=indicators,
        )

        self.events.append(event)

        # Auto-escalate critical events
        if severity == SecurityEventSeverity.CRITICAL:
            self.create_incident(
                description=description,
                severity=severity,
                affected_systems=[source],
            )

        return event

    def create_incident(
        self,
        description: str,
        severity: SecurityEventSeverity,
        affected_systems: List[str],
    ) -> IncidentResponse:
        """Create security incident."""
        incident = IncidentResponse(
            incident_id=f"inc_{secrets.token_hex(12)}",
            detected_at=datetime.utcnow(),
            severity=severity,
            status=IncidentStatus.DETECTED,
            description=description,
            affected_systems=affected_systems,
        )

        self.incidents[incident.incident_id] = incident
        return incident


__all__ = [
    "SOC2Monitor",
    "SecurityEvent",
    "IncidentResponse",
    "SecurityEventSeverity",
    "IncidentStatus",
]
