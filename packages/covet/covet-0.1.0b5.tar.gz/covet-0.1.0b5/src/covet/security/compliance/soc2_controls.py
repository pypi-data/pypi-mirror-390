"""
SOC 2 Security Controls Framework

SOC 2 Trust Services Criteria:
- CC1: Control Environment
- CC2: Communication and Information
- CC3: Risk Assessment
- CC4: Monitoring Activities
- CC5: Control Activities
- CC6: Logical and Physical Access Controls
- CC7: System Operations
- CC8: Change Management
- CC9: Risk Mitigation
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ControlCategory(str, Enum):
    """SOC 2 control categories."""

    CONTROL_ENVIRONMENT = "CC1"
    COMMUNICATION = "CC2"
    RISK_ASSESSMENT = "CC3"
    MONITORING = "CC4"
    CONTROL_ACTIVITIES = "CC5"
    ACCESS_CONTROLS = "CC6"
    SYSTEM_OPERATIONS = "CC7"
    CHANGE_MANAGEMENT = "CC8"
    RISK_MITIGATION = "CC9"


class ControlStatus(str, Enum):
    """Control implementation status."""

    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    IMPLEMENTED = "implemented"
    OPERATING_EFFECTIVELY = "operating_effectively"
    DEFICIENT = "deficient"


@dataclass
class SecurityControl:
    """SOC 2 security control."""

    control_id: str
    category: ControlCategory
    name: str
    description: str
    requirements: List[str]
    status: ControlStatus
    implemented_at: Optional[datetime] = None
    last_tested: Optional[datetime] = None
    test_results: Optional[str] = None
    responsible_party: Optional[str] = None
    evidence: List[str] = field(default_factory=list)


@dataclass
class ControlAssessment:
    """Control assessment result."""

    assessment_id: str
    control_id: str
    assessed_at: datetime
    assessor: str
    result: ControlStatus
    findings: List[str]
    recommendations: List[str]
    evidence_reviewed: List[str]


class SOC2ControlFramework:
    """SOC 2 control framework implementation."""

    def __init__(self):
        """Initialize SOC 2 controls."""
        self.controls: Dict[str, SecurityControl] = {}
        self.assessments: List[ControlAssessment] = []
        self._initialize_controls()

    def _initialize_controls(self):
        """Initialize standard SOC 2 controls."""
        controls = [
            # CC6: Access Controls
            SecurityControl(
                control_id="CC6.1",
                category=ControlCategory.ACCESS_CONTROLS,
                name="Logical Access Security",
                description="System access is restricted to authorized users",
                requirements=[
                    "User authentication required",
                    "Multi-factor authentication for privileged access",
                    "Password complexity requirements",
                    "Account lockout after failed attempts",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC6.2",
                category=ControlCategory.ACCESS_CONTROLS,
                name="Authorization",
                description="Access rights are granted based on job requirements",
                requirements=[
                    "Role-based access control",
                    "Principle of least privilege",
                    "Regular access reviews",
                    "Segregation of duties",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC6.3",
                category=ControlCategory.ACCESS_CONTROLS,
                name="User Access Removal",
                description="Access is removed when no longer required",
                requirements=[
                    "Timely removal of terminated user access",
                    "Automated access revocation",
                    "Access recertification process",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Team",
            ),
            # CC7: System Operations
            SecurityControl(
                control_id="CC7.1",
                category=ControlCategory.SYSTEM_OPERATIONS,
                name="Security Incident Detection",
                description="Security incidents are detected and responded to",
                requirements=[
                    "Security monitoring tools",
                    "Incident response procedures",
                    "Security event logging",
                    "Incident escalation process",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Operations",
            ),
            SecurityControl(
                control_id="CC7.2",
                category=ControlCategory.SYSTEM_OPERATIONS,
                name="System Monitoring",
                description="Systems are monitored for performance and availability",
                requirements=[
                    "Uptime monitoring",
                    "Performance metrics",
                    "Capacity planning",
                    "Alerting mechanisms",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Operations Team",
            ),
            SecurityControl(
                control_id="CC7.3",
                category=ControlCategory.SYSTEM_OPERATIONS,
                name="Backup and Recovery",
                description="Data backup and recovery procedures are implemented",
                requirements=[
                    "Regular automated backups",
                    "Backup testing",
                    "Disaster recovery plan",
                    "Recovery time objectives defined",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Operations Team",
            ),
            # CC8: Change Management
            SecurityControl(
                control_id="CC8.1",
                category=ControlCategory.CHANGE_MANAGEMENT,
                name="Change Control",
                description="Changes to systems are authorized and tested",
                requirements=[
                    "Change approval process",
                    "Testing before deployment",
                    "Rollback procedures",
                    "Change documentation",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Engineering Team",
            ),
            # CC5: Control Activities - Encryption
            SecurityControl(
                control_id="CC5.1",
                category=ControlCategory.CONTROL_ACTIVITIES,
                name="Data Encryption",
                description="Sensitive data is encrypted in transit and at rest",
                requirements=[
                    "TLS 1.3 for data in transit",
                    "AES-256 for data at rest",
                    "Key management procedures",
                    "Encryption key rotation",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Team",
            ),
            SecurityControl(
                control_id="CC5.2",
                category=ControlCategory.CONTROL_ACTIVITIES,
                name="Vulnerability Management",
                description="Vulnerabilities are identified and remediated",
                requirements=[
                    "Regular vulnerability scans",
                    "Patch management process",
                    "Penetration testing",
                    "Remediation tracking",
                ],
                status=ControlStatus.NOT_IMPLEMENTED,
                responsible_party="Security Team",
            ),
        ]

        for control in controls:
            self.controls[control.control_id] = control

    def assess_control(
        self,
        control_id: str,
        assessor: str,
        result: ControlStatus,
        findings: List[str],
        recommendations: List[str],
        evidence: List[str],
    ) -> ControlAssessment:
        """
        Assess control effectiveness.

        Args:
            control_id: Control identifier
            assessor: Person conducting assessment
            result: Assessment result
            findings: Assessment findings
            recommendations: Recommendations for improvement
            evidence: Evidence reviewed

        Returns:
            Control assessment
        """
        control = self.controls.get(control_id)
        if not control:
            raise ValueError(f"Control not found: {control_id}")

        assessment = ControlAssessment(
            assessment_id=f"assess_{secrets.token_hex(12)}",
            control_id=control_id,
            assessed_at=datetime.utcnow(),
            assessor=assessor,
            result=result,
            findings=findings,
            recommendations=recommendations,
            evidence_reviewed=evidence,
        )

        self.assessments.append(assessment)

        # Update control status
        control.status = result
        control.last_tested = datetime.utcnow()
        control.test_results = f"{len(findings)} findings, {len(recommendations)} recommendations"

        return assessment

    def get_compliance_score(self) -> float:
        """
        Calculate overall compliance score.

        Returns:
            Compliance score (0-100)
        """
        if not self.controls:
            return 0.0

        status_scores = {
            ControlStatus.NOT_IMPLEMENTED: 0,
            ControlStatus.PARTIALLY_IMPLEMENTED: 50,
            ControlStatus.IMPLEMENTED: 75,
            ControlStatus.OPERATING_EFFECTIVELY: 100,
            ControlStatus.DEFICIENT: 25,
        }

        total_score = sum(status_scores[c.status] for c in self.controls.values())
        max_score = len(self.controls) * 100

        return (total_score / max_score) * 100 if max_score > 0 else 0.0

    def get_controls_by_category(
        self,
        category: ControlCategory,
    ) -> List[SecurityControl]:
        """Get all controls in a category."""
        return [c for c in self.controls.values() if c.category == category]

    def get_deficient_controls(self) -> List[SecurityControl]:
        """Get controls that need attention."""
        return [
            c
            for c in self.controls.values()
            if c.status in (ControlStatus.NOT_IMPLEMENTED, ControlStatus.DEFICIENT)
        ]


__all__ = [
    "SOC2ControlFramework",
    "SecurityControl",
    "ControlCategory",
    "ControlStatus",
    "ControlAssessment",
]
