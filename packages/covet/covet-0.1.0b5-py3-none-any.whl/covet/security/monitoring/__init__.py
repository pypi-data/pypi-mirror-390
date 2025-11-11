"""
CovetPy Security Monitoring System

Production-grade security monitoring, intrusion detection, and incident response.

This module provides comprehensive security monitoring capabilities including:
- Intrusion Detection System (IDS) with ML-based anomaly detection
- Threat intelligence integration with IP reputation checking
- Comprehensive audit logging with SIEM integration
- Multi-channel alerting with escalation policies
- Security metrics collection (Prometheus)
- Automated incident response
- Forensics and evidence collection
- Honeypot systems for attacker tracking

Components:
- ids: Intrusion Detection System
- threat_intel: Threat intelligence integration
- audit_log: Enhanced audit logging
- alerting: Multi-channel alerting
- metrics: Security metrics
- incident_response: Automated incident handling
- forensics: Security forensics tools
- honeypot: Honeypot systems

Example:
    from covet.security.monitoring import IDS, ThreatIntelligence, SecurityAlerter

    # Initialize IDS
    ids = IDS()
    await ids.analyze_request(request)

    # Check threat intelligence
    threat = ThreatIntelligence()
    is_malicious = await threat.check_ip("1.2.3.4")

    # Send security alert
    alerter = SecurityAlerter()
    await alerter.send_alert("Critical security event detected")
"""

__version__ = "1.0.0"

from .alerting import Alert, AlertChannel, AlertSeverity, SecurityAlerter
from .audit_log import AuditLogger, EventCategory, EventType, SecurityEvent, Severity
from .forensics import AttackTrace, Evidence, EvidenceType, ForensicsCollector
from .honeypot import AttackerProfile, Honeypot, HoneypotInteraction, HoneypotType

# Import core components
from .ids import IDS, AttackType, DetectionResult, RequestProfile, ThreatLevel
from .incident_response import (
    ContainmentAction,
    Incident,
    IncidentResponseAutomation,
    IncidentSeverity,
)
from .metrics import PrometheusExporter, SecurityMetrics
from .threat_intel import IPReputation, ThreatCategory, ThreatIntelligence, ThreatScore

__all__ = [
    "__version__",
    # IDS
    "IDS",
    "AttackType",
    "ThreatLevel",
    "DetectionResult",
    "RequestProfile",
    # Threat Intelligence
    "ThreatIntelligence",
    "ThreatScore",
    "IPReputation",
    "ThreatCategory",
    # Audit Logging
    "AuditLogger",
    "SecurityEvent",
    "EventType",
    "EventCategory",
    "Severity",
    # Alerting
    "SecurityAlerter",
    "Alert",
    "AlertSeverity",
    "AlertChannel",
    # Metrics
    "SecurityMetrics",
    "PrometheusExporter",
    # Incident Response
    "IncidentResponseAutomation",
    "Incident",
    "IncidentSeverity",
    "ContainmentAction",
    # Forensics
    "ForensicsCollector",
    "Evidence",
    "EvidenceType",
    "AttackTrace",
    # Honeypot
    "Honeypot",
    "HoneypotType",
    "HoneypotInteraction",
    "AttackerProfile",
]
