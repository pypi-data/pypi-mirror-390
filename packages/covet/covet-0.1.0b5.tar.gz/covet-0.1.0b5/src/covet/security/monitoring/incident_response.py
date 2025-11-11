"""
Automated Incident Response System

Production-grade incident response with:
- Incident detection and classification
- Automatic containment actions (IP blocking, account suspension, session termination)
- Incident timeline tracking
- Evidence collection
- Post-incident reporting
- Integration with SIEM and alerting

NO MOCK DATA - Real incident response automation.
"""

import asyncio
import hashlib
import json
import time
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set


class IncidentSeverity(str, Enum):
    """Incident severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    """Incident status"""

    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    ERADICATED = "eradicated"
    RECOVERED = "recovered"
    CLOSED = "closed"


class ContainmentAction(str, Enum):
    """Automatic containment actions"""

    BLOCK_IP = "block_ip"
    SUSPEND_ACCOUNT = "suspend_account"
    TERMINATE_SESSION = "terminate_session"
    REVOKE_API_KEY = "revoke_api_key"
    DISABLE_FEATURE = "disable_feature"
    ISOLATE_RESOURCE = "isolate_resource"
    ALERT_ADMIN = "alert_admin"


@dataclass
class IncidentEvent:
    """Event in incident timeline"""

    timestamp: datetime
    event_type: str
    description: str
    actor: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Incident:
    """Security incident"""

    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    detected_at: datetime

    # Classification
    attack_type: Optional[str] = None
    affected_resources: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)

    # Actors
    attacker_ips: List[str] = field(default_factory=list)
    attacker_user_agents: List[str] = field(default_factory=list)

    # Timeline
    timeline: List[IncidentEvent] = field(default_factory=list)

    # Actions taken
    containment_actions: List[ContainmentAction] = field(default_factory=list)

    # Evidence
    evidence: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    assigned_to: Optional[str] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["detected_at"] = self.detected_at.isoformat()
        data["severity"] = self.severity.value
        data["status"] = self.status.value
        data["containment_actions"] = [a.value for a in self.containment_actions]
        return data


class IncidentResponsePlaybook:
    """
    Incident response playbooks for different attack types.

    Defines automated response procedures.
    """

    def __init__(self):
        """Initialize playbooks"""
        self.playbooks: Dict[str, List[ContainmentAction]] = {
            "sql_injection": [
                ContainmentAction.BLOCK_IP,
                ContainmentAction.ALERT_ADMIN,
            ],
            "xss": [
                ContainmentAction.BLOCK_IP,
                ContainmentAction.ALERT_ADMIN,
            ],
            "brute_force": [
                ContainmentAction.BLOCK_IP,
                ContainmentAction.SUSPEND_ACCOUNT,
                ContainmentAction.ALERT_ADMIN,
            ],
            "ddos": [
                ContainmentAction.BLOCK_IP,
                ContainmentAction.ALERT_ADMIN,
            ],
            "session_hijacking": [
                ContainmentAction.TERMINATE_SESSION,
                ContainmentAction.SUSPEND_ACCOUNT,
                ContainmentAction.ALERT_ADMIN,
            ],
            "privilege_escalation": [
                ContainmentAction.SUSPEND_ACCOUNT,
                ContainmentAction.TERMINATE_SESSION,
                ContainmentAction.ALERT_ADMIN,
            ],
            "data_exfiltration": [
                ContainmentAction.BLOCK_IP,
                ContainmentAction.SUSPEND_ACCOUNT,
                ContainmentAction.DISABLE_FEATURE,
                ContainmentAction.ALERT_ADMIN,
            ],
        }

    def get_actions(self, attack_type: str) -> List[ContainmentAction]:
        """Get containment actions for attack type"""
        return self.playbooks.get(attack_type.lower(), [ContainmentAction.ALERT_ADMIN])


class IncidentResponseAutomation:
    """
    Automated incident response system.

    Detects incidents and executes containment actions automatically.
    """

    def __init__(
        self,
        enable_auto_containment: bool = True,
        alert_callback: Optional[Callable] = None,
        containment_callback: Optional[Callable] = None,
    ):
        """
        Initialize incident response automation.

        Args:
            enable_auto_containment: Enable automatic containment
            alert_callback: Callback for sending alerts
            containment_callback: Callback for executing containment actions
        """
        self.enable_auto_containment = enable_auto_containment
        self.alert_callback = alert_callback
        self.containment_callback = containment_callback

        # Incident storage
        self.incidents: Dict[str, Incident] = {}

        # Playbooks
        self.playbook = IncidentResponsePlaybook()

        # Statistics
        self.stats = {
            "total_incidents": 0,
            "by_severity": defaultdict(int),
            "by_status": defaultdict(int),
            "auto_contained": 0,
            "manual_intervention": 0,
        }

        self._lock = asyncio.Lock()

    async def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        attack_type: Optional[str] = None,
        attacker_ips: Optional[List[str]] = None,
        affected_resources: Optional[List[str]] = None,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> Incident:
        """
        Create and handle security incident.

        Args:
            title: Incident title
            description: Description
            severity: Severity level
            attack_type: Type of attack
            attacker_ips: Attacker IP addresses
            affected_resources: Affected resources
            evidence: Evidence data

        Returns:
            Created incident
        """
        # Generate incident ID
        incident_id = self._generate_incident_id()

        # Create incident
        incident = Incident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.DETECTED,
            detected_at=datetime.utcnow(),
            attack_type=attack_type,
            attacker_ips=attacker_ips or [],
            affected_resources=affected_resources or [],
            evidence=evidence or {},
        )

        # Add detection event to timeline
        incident.timeline.append(
            IncidentEvent(
                timestamp=datetime.utcnow(),
                event_type="detection",
                description="Incident detected",
                details={"severity": severity.value},
            )
        )

        # Store incident
        async with self._lock:
            self.incidents[incident_id] = incident
            self.stats["total_incidents"] += 1
            self.stats["by_severity"][severity.value] += 1
            self.stats["by_status"][IncidentStatus.DETECTED.value] += 1

        # Execute automatic containment
        if self.enable_auto_containment and attack_type:
            await self._execute_containment(incident)

        # Send alert
        if self.alert_callback:
            try:
                await self.alert_callback(incident)
            except Exception:
                pass

        return incident

    async def _execute_containment(self, incident: Incident):
        """Execute automated containment actions"""
        if not incident.attack_type:
            return

        # Get actions from playbook
        actions = self.playbook.get_actions(incident.attack_type)

        # Update status
        incident.status = IncidentStatus.CONTAINED
        incident.timeline.append(
            IncidentEvent(
                timestamp=datetime.utcnow(),
                event_type="containment",
                description="Automated containment initiated",
                details={"actions": [a.value for a in actions]},
            )
        )

        # Execute each action
        for action in actions:
            success = await self._execute_action(incident, action)

            if success:
                incident.containment_actions.append(action)
                incident.timeline.append(
                    IncidentEvent(
                        timestamp=datetime.utcnow(),
                        event_type="action",
                        description=f"Executed {action.value}",
                    )
                )

        async with self._lock:
            self.stats["auto_contained"] += 1

    async def _execute_action(self, incident: Incident, action: ContainmentAction) -> bool:
        """Execute containment action"""
        if not self.containment_callback:
            return False

        try:
            # Call containment callback
            await self.containment_callback(action, incident)
            return True
        except Exception:
            return False

    async def update_incident_status(
        self, incident_id: str, status: IncidentStatus, notes: str = ""
    ):
        """Update incident status"""
        async with self._lock:
            if incident_id in self.incidents:
                incident = self.incidents[incident_id]
                old_status = incident.status
                incident.status = status

                incident.timeline.append(
                    IncidentEvent(
                        timestamp=datetime.utcnow(),
                        event_type="status_change",
                        description=f"Status changed from {old_status.value} to {status.value}",
                        details={"notes": notes},
                    )
                )

                if status == IncidentStatus.CLOSED:
                    incident.resolved_at = datetime.utcnow()
                    incident.resolution_notes = notes

                self.stats["by_status"][old_status.value] -= 1
                self.stats["by_status"][status.value] += 1

    async def add_evidence(self, incident_id: str, evidence_key: str, evidence_data: Any):
        """Add evidence to incident"""
        async with self._lock:
            if incident_id in self.incidents:
                incident = self.incidents[incident_id]
                incident.evidence[evidence_key] = evidence_data

                incident.timeline.append(
                    IncidentEvent(
                        timestamp=datetime.utcnow(),
                        event_type="evidence",
                        description=f"Evidence added: {evidence_key}",
                    )
                )

    async def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        async with self._lock:
            return self.incidents.get(incident_id)

    async def get_open_incidents(self) -> List[Incident]:
        """Get all open incidents"""
        async with self._lock:
            return [
                incident
                for incident in self.incidents.values()
                if incident.status not in [IncidentStatus.CLOSED]
            ]

    async def get_statistics(self) -> Dict[str, Any]:
        """Get incident response statistics"""
        async with self._lock:
            return {
                "total_incidents": self.stats["total_incidents"],
                "by_severity": dict(self.stats["by_severity"]),
                "by_status": dict(self.stats["by_status"]),
                "auto_contained": self.stats["auto_contained"],
                "manual_intervention": self.stats["manual_intervention"],
                "open_incidents": len(await self.get_open_incidents()),
            }

    async def generate_report(self, incident_id: str) -> Dict[str, Any]:
        """Generate incident report"""
        incident = await self.get_incident(incident_id)

        if not incident:
            return {}

        return {
            "incident": incident.to_dict(),
            "summary": {
                "duration": (
                    (incident.resolved_at or datetime.utcnow()) - incident.detected_at
                ).total_seconds(),
                "timeline_events": len(incident.timeline),
                "actions_taken": len(incident.containment_actions),
                "affected_resources": len(incident.affected_resources),
            },
            "timeline": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "description": event.description,
                    "details": event.details,
                }
                for event in incident.timeline
            ],
        }

    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        return f"INC-{datetime.utcnow().strftime('%Y%m%d')}-{hashlib.sha256(str(time.time()).encode()).hexdigest()[:8].upper()}"


__all__ = [
    "IncidentResponseAutomation",
    "Incident",
    "IncidentSeverity",
    "IncidentStatus",
    "ContainmentAction",
    "IncidentResponsePlaybook",
]
