"""
HIPAA Business Associate Agreement (BAA) Support

45 CFR § 164.502(e) - Business Associate Contracts

This module provides framework for BAA compliance including:
- BAA agreement management
- Breach notification procedures
- Subcontractor management
- Compliance attestation
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Set


class BAAStatus(str, Enum):
    """BAA agreement status."""

    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"


class BreachSeverity(str, Enum):
    """Breach severity level."""

    LOW = "low"  # < 10 individuals
    MEDIUM = "medium"  # 10-499 individuals
    HIGH = "high"  # >= 500 individuals
    CRITICAL = "critical"  # Immediate risk of harm


@dataclass
class BusinessAssociateAgreement:
    """Business Associate Agreement."""

    baa_id: str
    covered_entity_name: str
    business_associate_name: str
    effective_date: datetime
    expiration_date: datetime
    status: BAAStatus

    # Required BAA provisions
    permitted_uses: Set[str]
    permitted_disclosures: Set[str]
    prohibited_uses: Set[str]

    # Security requirements
    safeguards_required: List[str]
    breach_notification_days: int = 60

    # Subcontractors
    subcontractors_permitted: bool = False
    subcontractors: List[str] = field(default_factory=list)

    # Metadata
    signed_by_ce: Optional[str] = None
    signed_by_ba: Optional[str] = None
    signed_date_ce: Optional[datetime] = None
    signed_date_ba: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if BAA is active."""
        if self.status != BAAStatus.ACTIVE:
            return False

        now = datetime.utcnow()
        return self.effective_date <= now < self.expiration_date

    def requires_renewal(self, days_before: int = 90) -> bool:
        """Check if BAA requires renewal."""
        if not self.is_active():
            return False

        days_until_expiration = (self.expiration_date - datetime.utcnow()).days
        return days_until_expiration <= days_before


@dataclass
class BreachNotification:
    """HIPAA breach notification."""

    notification_id: str
    baa_id: str
    breach_date: datetime
    discovery_date: datetime
    notification_date: datetime
    severity: BreachSeverity

    # Breach details
    individuals_affected: int
    phi_involved: Set[str]
    breach_description: str
    cause: str
    mitigation_steps: List[str]

    # Notification status
    ce_notified: bool = False
    ce_notification_date: Optional[datetime] = None
    hhs_required: bool = False  # >= 500 individuals
    hhs_notified: bool = False
    media_notification_required: bool = False

    def is_reportable(self) -> bool:
        """Check if breach is reportable under HIPAA."""
        # Breaches affecting 500+ individuals must be reported to HHS
        return self.individuals_affected >= 500


class BAAManager:
    """Business Associate Agreement manager."""

    def __init__(self):
        """Initialize BAA manager."""
        self.agreements: dict[str, BusinessAssociateAgreement] = {}
        self.breach_notifications: List[BreachNotification] = []

    def create_baa(
        self,
        covered_entity: str,
        business_associate: str,
        effective_date: datetime,
        duration_years: int = 3,
        permitted_uses: Optional[Set[str]] = None,
    ) -> BusinessAssociateAgreement:
        """Create new BAA."""
        baa = BusinessAssociateAgreement(
            baa_id=f"baa_{secrets.token_hex(12)}",
            covered_entity_name=covered_entity,
            business_associate_name=business_associate,
            effective_date=effective_date,
            expiration_date=effective_date + timedelta(days=duration_years * 365),
            status=BAAStatus.DRAFT,
            permitted_uses=permitted_uses or {"treatment", "payment", "operations"},
            permitted_disclosures={"required_by_law", "to_covered_entity"},
            prohibited_uses={"marketing", "sale_of_phi"},
            safeguards_required=[
                "encryption_at_rest",
                "encryption_in_transit",
                "access_controls",
                "audit_logging",
                "breach_notification",
            ],
        )

        self.agreements[baa.baa_id] = baa
        return baa

    def report_breach(
        self,
        baa_id: str,
        breach_date: datetime,
        individuals_affected: int,
        phi_involved: Set[str],
        description: str,
        cause: str,
    ) -> BreachNotification:
        """Report HIPAA breach."""
        discovery_date = datetime.utcnow()

        # Determine severity
        if individuals_affected >= 500:
            severity = BreachSeverity.HIGH
        elif individuals_affected >= 10:
            severity = BreachSeverity.MEDIUM
        else:
            severity = BreachSeverity.LOW

        notification = BreachNotification(
            notification_id=f"breach_{secrets.token_hex(12)}",
            baa_id=baa_id,
            breach_date=breach_date,
            discovery_date=discovery_date,
            notification_date=discovery_date,
            severity=severity,
            individuals_affected=individuals_affected,
            phi_involved=phi_involved,
            breach_description=description,
            cause=cause,
            mitigation_steps=[],
            hhs_required=individuals_affected >= 500,
            media_notification_required=individuals_affected >= 500,
        )

        self.breach_notifications.append(notification)
        return notification


__all__ = [
    "BAAManager",
    "BusinessAssociateAgreement",
    "BreachNotification",
    "BAAStatus",
    "BreachSeverity",
]
