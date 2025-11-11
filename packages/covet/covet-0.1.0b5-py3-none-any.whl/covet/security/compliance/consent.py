"""
GDPR Consent Management (Articles 6, 7, 8)

Requirements:
- Freely given consent
- Specific and informed
- Unambiguous indication
- Clear affirmative action
- Easy to withdraw
- Documented proof of consent
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class ConsentType(str, Enum):
    """Types of consent."""

    EXPLICIT = "explicit"  # GDPR Article 9 - Special categories
    IMPLIED = "implied"  # Legitimate interest
    CONTRACT = "contract"  # Necessary for contract
    LEGAL = "legal"  # Legal obligation


class ProcessingPurpose(str, Enum):
    """Data processing purposes."""

    ESSENTIAL = "essential"  # Core service delivery
    ANALYTICS = "analytics"  # Usage analytics
    MARKETING = "marketing"  # Marketing communications
    PERSONALIZATION = "personalization"  # Personalized experience
    RESEARCH = "research"  # Research and development
    THIRD_PARTY_SHARING = "third_party_sharing"  # Share with partners


@dataclass
class ConsentRecord:
    """Consent record."""

    consent_id: str
    user_id: str
    purpose: ProcessingPurpose
    consent_type: ConsentType
    granted: bool
    granted_at: datetime
    withdrawn_at: Optional[datetime] = None
    consent_method: str = "web_form"  # How consent was obtained
    consent_text: str = ""  # Text shown to user
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    parent_consent: bool = False  # For users under 16
    expires_at: Optional[datetime] = None

    def is_active(self) -> bool:
        """Check if consent is active."""
        if not self.granted:
            return False
        if self.withdrawn_at:
            return False
        if self.expires_at and datetime.utcnow() >= self.expires_at:
            return False
        return True


@dataclass
class ConsentAuditTrail:
    """Audit trail for consent changes."""

    trail_id: str
    user_id: str
    purpose: ProcessingPurpose
    action: str  # "granted", "withdrawn", "updated"
    timestamp: datetime
    details: Dict[str, any] = field(default_factory=dict)


class ConsentManager:
    """GDPR consent management system."""

    def __init__(self):
        """Initialize consent manager."""
        self.consents: Dict[str, List[ConsentRecord]] = {}
        self.audit_trail: List[ConsentAuditTrail] = []

    def grant_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
        consent_type: ConsentType = ConsentType.EXPLICIT,
        consent_text: str = "",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> ConsentRecord:
        """
        Grant consent for data processing.

        Args:
            user_id: User identifier
            purpose: Processing purpose
            consent_type: Type of consent
            consent_text: Text shown to user
            ip_address: User IP address
            user_agent: User agent string

        Returns:
            Consent record
        """
        consent = ConsentRecord(
            consent_id=f"consent_{secrets.token_hex(12)}",
            user_id=user_id,
            purpose=purpose,
            consent_type=consent_type,
            granted=True,
            granted_at=datetime.utcnow(),
            consent_method="web_form",
            consent_text=consent_text,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if user_id not in self.consents:
            self.consents[user_id] = []
        self.consents[user_id].append(consent)

        # Audit trail
        self._audit_consent(
            user_id,
            purpose,
            "granted",
            {
                "consent_id": consent.consent_id,
                "consent_type": consent_type,
            },
        )

        return consent

    def withdraw_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
    ) -> bool:
        """
        Withdraw consent for data processing.

        Args:
            user_id: User identifier
            purpose: Processing purpose

        Returns:
            True if consent was withdrawn
        """
        if user_id not in self.consents:
            return False

        withdrawn = False
        for consent in self.consents[user_id]:
            if consent.purpose == purpose and consent.is_active():
                consent.withdrawn_at = datetime.utcnow()
                withdrawn = True

                # Audit trail
                self._audit_consent(
                    user_id,
                    purpose,
                    "withdrawn",
                    {
                        "consent_id": consent.consent_id,
                    },
                )

        return withdrawn

    def check_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
    ) -> bool:
        """
        Check if user has given active consent.

        Args:
            user_id: User identifier
            purpose: Processing purpose

        Returns:
            True if consent is active
        """
        if user_id not in self.consents:
            return False

        for consent in self.consents[user_id]:
            if consent.purpose == purpose and consent.is_active():
                return True

        return False

    def get_user_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get all consents for user."""
        return self.consents.get(user_id, [])

    def get_active_consents(self, user_id: str) -> List[ConsentRecord]:
        """Get active consents for user."""
        consents = self.consents.get(user_id, [])
        return [c for c in consents if c.is_active()]

    def _audit_consent(
        self,
        user_id: str,
        purpose: ProcessingPurpose,
        action: str,
        details: Dict[str, any],
    ):
        """Record consent change in audit trail."""
        audit = ConsentAuditTrail(
            trail_id=f"audit_{secrets.token_hex(12)}",
            user_id=user_id,
            purpose=purpose,
            action=action,
            timestamp=datetime.utcnow(),
            details=details,
        )
        self.audit_trail.append(audit)


__all__ = [
    "ConsentManager",
    "ConsentType",
    "ConsentRecord",
    "ConsentAuditTrail",
    "ProcessingPurpose",
]
