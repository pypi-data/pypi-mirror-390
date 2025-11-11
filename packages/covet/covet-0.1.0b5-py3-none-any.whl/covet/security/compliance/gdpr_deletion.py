"""
GDPR Right to Deletion (Article 17 - Right to be Forgotten)

Individuals have the right to have their personal data erased when:
- Data no longer necessary for original purpose
- Individual withdraws consent
- Individual objects to processing
- Data processed unlawfully
- Legal obligation requires erasure
"""

import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set


class DeletionReason(str, Enum):
    """Reasons for data deletion."""

    USER_REQUEST = "user_request"
    CONSENT_WITHDRAWN = "consent_withdrawn"
    PURPOSE_FULFILLED = "purpose_fulfilled"
    UNLAWFUL_PROCESSING = "unlawful_processing"
    LEGAL_OBLIGATION = "legal_obligation"
    RETENTION_EXPIRED = "retention_expired"


class DeletionStatus(str, Enum):
    """Deletion request status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass
class DeletionRequest:
    """GDPR deletion request."""

    request_id: str
    user_id: str
    reason: DeletionReason
    requested_at: datetime
    status: DeletionStatus
    verified: bool = False
    completed_at: Optional[datetime] = None
    deleted_items: List[str] = field(default_factory=list)
    failed_items: List[str] = field(default_factory=list)
    verification_hash: Optional[str] = None


@dataclass
class DeletionVerification:
    """Verification of data deletion."""

    verification_id: str
    request_id: str
    verified_at: datetime
    items_checked: int
    items_deleted: int
    items_remaining: int
    verification_passed: bool
    details: Dict[str, any] = field(default_factory=dict)


class RightToDeletionService:
    """GDPR right to deletion service."""

    def __init__(self, secure_deletion=None):
        """
        Initialize deletion service.

        Args:
            secure_deletion: Secure deletion implementation
        """
        self.deletion_requests: Dict[str, DeletionRequest] = {}
        self.verifications: List[DeletionVerification] = []
        self.secure_deletion = secure_deletion
        self.legal_holds: Set[str] = set()

    def create_deletion_request(
        self,
        user_id: str,
        reason: DeletionReason,
    ) -> DeletionRequest:
        """
        Create deletion request.

        Args:
            user_id: User requesting deletion
            reason: Reason for deletion

        Returns:
            Deletion request
        """
        # Check for legal holds
        if user_id in self.legal_holds:
            request = DeletionRequest(
                request_id=f"del_req_{secrets.token_hex(12)}",
                user_id=user_id,
                reason=reason,
                requested_at=datetime.utcnow(),
                status=DeletionStatus.REJECTED,
            )
            self.deletion_requests[request.request_id] = request
            return request

        request = DeletionRequest(
            request_id=f"del_req_{secrets.token_hex(12)}",
            user_id=user_id,
            reason=reason,
            requested_at=datetime.utcnow(),
            status=DeletionStatus.PENDING,
        )

        self.deletion_requests[request.request_id] = request
        return request

    def process_deletion(
        self,
        request_id: str,
        data_sources: List[str],
    ) -> DeletionRequest:
        """
        Process deletion request.

        Args:
            request_id: Request identifier
            data_sources: Data sources to delete from

        Returns:
            Updated deletion request
        """
        request = self.deletion_requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        request.status = DeletionStatus.IN_PROGRESS

        # Delete from each data source
        for source in data_sources:
            try:
                # In production, actually delete from each source
                request.deleted_items.append(source)
            except Exception as e:
                request.failed_items.append(f"{source}: {str(e)}")

        # Update status
        if not request.failed_items:
            request.status = DeletionStatus.COMPLETED
            request.completed_at = datetime.utcnow()
        else:
            request.status = DeletionStatus.FAILED

        return request

    def verify_deletion(
        self,
        request_id: str,
        data_sources: List[str],
    ) -> DeletionVerification:
        """
        Verify data has been deleted.

        Args:
            request_id: Deletion request ID
            data_sources: Data sources to verify

        Returns:
            Deletion verification
        """
        request = self.deletion_requests.get(request_id)
        if not request:
            raise ValueError(f"Request not found: {request_id}")

        items_checked = len(data_sources)
        items_deleted = 0
        items_remaining = 0

        # Check each data source
        for source in data_sources:
            # In production, actually check if data exists
            if source in request.deleted_items:
                items_deleted += 1
            else:
                items_remaining += 1

        verification = DeletionVerification(
            verification_id=f"ver_{secrets.token_hex(12)}",
            request_id=request_id,
            verified_at=datetime.utcnow(),
            items_checked=items_checked,
            items_deleted=items_deleted,
            items_remaining=items_remaining,
            verification_passed=(items_remaining == 0),
        )

        self.verifications.append(verification)
        request.verified = verification.verification_passed

        return verification


__all__ = [
    "RightToDeletionService",
    "DeletionRequest",
    "DeletionVerification",
    "DeletionReason",
    "DeletionStatus",
]
