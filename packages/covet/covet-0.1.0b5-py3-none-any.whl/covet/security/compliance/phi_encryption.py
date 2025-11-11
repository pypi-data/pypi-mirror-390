"""
HIPAA PHI (Protected Health Information) Encryption

45 CFR § 164.312(a)(2)(iv) - Encryption and Decryption
45 CFR § 164.312(e)(2)(ii) - Encryption

SECURITY FEATURES:
- AES-256-GCM encryption for PHI
- Automatic PHI classification and detection
- Field-level encryption for databases
- Access logging for all PHI operations
- Key separation for different data types
- Compliance with HIPAA Security Rule

PHI CATEGORIES:
- Direct identifiers (name, SSN, medical record number)
- Healthcare data (diagnoses, treatments, medications)
- Payment information (insurance, claims)
- Biometric data
- Genetic information

THREAT MODEL:
- Unauthorized PHI disclosure
- Data breaches
- Insider threats
- Lost or stolen devices
- Improper disposal
"""

import re
import secrets
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .encryption_at_rest import DataEncryptionService, KeyManagementService


class PHICategory(str, Enum):
    """Categories of Protected Health Information."""

    # Direct identifiers
    NAME = "name"
    SSN = "ssn"
    MEDICAL_RECORD_NUMBER = "mrn"
    PATIENT_ID = "patient_id"
    ACCOUNT_NUMBER = "account_number"

    # Contact information
    EMAIL = "email"
    PHONE = "phone"
    ADDRESS = "address"

    # Dates (except year)
    DATE_OF_BIRTH = "date_of_birth"
    DATE_OF_SERVICE = "date_of_service"
    DATE_OF_DEATH = "date_of_death"

    # Healthcare data
    DIAGNOSIS = "diagnosis"
    TREATMENT = "treatment"
    MEDICATION = "medication"
    LAB_RESULT = "lab_result"
    VITAL_SIGNS = "vital_signs"

    # Financial
    INSURANCE_INFO = "insurance"
    PAYMENT_INFO = "payment"

    # Biometric
    FINGERPRINT = "fingerprint"
    VOICEPRINT = "voiceprint"
    FACIAL_PHOTO = "facial_photo"

    # Genetic
    GENETIC_INFO = "genetic"

    # Device identifiers
    DEVICE_ID = "device_id"
    IP_ADDRESS = "ip_address"

    # Other
    OTHER_PHI = "other_phi"


class PHIClassification(str, Enum):
    """PHI data classification levels."""

    NON_PHI = "non_phi"
    LIMITED_DATA_SET = "limited_dataset"  # De-identified with some identifiers
    PHI = "phi"  # Protected Health Information
    SENSITIVE_PHI = "sensitive_phi"  # Extra sensitive (mental health, HIV, etc.)


@dataclass
class PHIField:
    """PHI field configuration."""

    field_name: str
    category: PHICategory
    classification: PHIClassification
    required: bool = False
    description: str = ""
    regex_pattern: Optional[str] = None


@dataclass
class PHIAccessLog:
    """PHI access log entry."""

    log_id: str
    timestamp: datetime
    user_id: str
    patient_id: str
    action: str  # "read", "write", "decrypt", "export"
    phi_categories: Set[PHICategory]
    ip_address: Optional[str] = None
    purpose: Optional[str] = None
    success: bool = True
    audit_trail: Dict[str, Any] = field(default_factory=dict)


class PHIEncryptionService:
    """
    HIPAA-compliant PHI encryption service.

    FEATURES:
    - Automatic PHI detection and classification
    - Field-level encryption for structured data
    - Access logging for compliance
    - Key separation for different PHI categories
    - Minimum necessary principle enforcement
    """

    def __init__(
        self,
        kms: KeyManagementService,
        encryption_service: DataEncryptionService,
        audit_logger=None,
    ):
        """
        Initialize PHI encryption service.

        Args:
            kms: Key management service
            encryption_service: Data encryption service
            audit_logger: Audit logger for PHI access
        """
        self.kms = kms
        self.encryption = encryption_service
        self.audit_logger = audit_logger

        # PHI field patterns for detection
        self.phi_patterns = {
            PHICategory.SSN: r"\b\d{3}-\d{2}-\d{4}\b",
            PHICategory.EMAIL: r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            PHICategory.PHONE: r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
            PHICategory.DATE_OF_BIRTH: r"\b\d{1,2}/\d{1,2}/\d{4}\b",
        }

        # Access logs
        self.access_logs: List[PHIAccessLog] = []

        # Generate keys for different PHI categories
        self.phi_key = kms.generate_key(key_id="phi_general")
        self.sensitive_phi_key = kms.generate_key(key_id="phi_sensitive")

    def classify_data(self, data: str) -> PHIClassification:
        """
        Automatically classify data as PHI.

        Args:
            data: Data to classify

        Returns:
            PHI classification level
        """
        # Check for PHI patterns
        detected_categories = set()

        for category, pattern in self.phi_patterns.items():
            if re.search(pattern, data):
                detected_categories.add(category)

        if not detected_categories:
            return PHIClassification.NON_PHI

        # Check for sensitive PHI keywords
        sensitive_keywords = [
            "hiv",
            "aids",
            "mental health",
            "psychiatric",
            "substance abuse",
            "drug abuse",
            "alcohol",
            "sexual assault",
            "domestic violence",
        ]

        data_lower = data.lower()
        if any(keyword in data_lower for keyword in sensitive_keywords):
            return PHIClassification.SENSITIVE_PHI

        return PHIClassification.PHI

    def detect_phi_categories(self, data: str) -> Set[PHICategory]:
        """
        Detect PHI categories in data.

        Args:
            data: Data to analyze

        Returns:
            Set of detected PHI categories
        """
        categories = set()

        for category, pattern in self.phi_patterns.items():
            if re.search(pattern, data):
                categories.add(category)

        return categories

    def encrypt_phi(
        self,
        data: str,
        patient_id: str,
        user_id: str,
        categories: Optional[Set[PHICategory]] = None,
        classification: Optional[PHIClassification] = None,
    ) -> str:
        """
        Encrypt PHI data.

        Args:
            data: PHI data to encrypt
            patient_id: Patient identifier
            user_id: User performing encryption
            categories: PHI categories (auto-detected if not provided)
            classification: PHI classification (auto-classified if not provided)

        Returns:
            Encrypted PHI data (JSON)
        """
        # Auto-detect categories if not provided
        if categories is None:
            categories = self.detect_phi_categories(data)

        # Auto-classify if not provided
        if classification is None:
            classification = self.classify_data(data)

        # Select appropriate key
        if classification == PHIClassification.SENSITIVE_PHI:
            key_id = "phi_sensitive"
        else:
            key_id = "phi_general"

        # Encrypt data
        encrypted = self.encryption.encrypt_string(
            plaintext=data,
            key_id=key_id,
            associated_data=patient_id,  # Bind to patient
            metadata={
                "patient_id": patient_id,
                "classification": classification,
                "categories": [c.value for c in categories],
            },
        )

        # Log access
        self._log_access(
            user_id=user_id,
            patient_id=patient_id,
            action="encrypt",
            phi_categories=categories,
            success=True,
        )

        return encrypted

    def decrypt_phi(
        self,
        encrypted_data: str,
        patient_id: str,
        user_id: str,
        purpose: Optional[str] = None,
    ) -> str:
        """
        Decrypt PHI data.

        Args:
            encrypted_data: Encrypted PHI data
            patient_id: Patient identifier
            user_id: User requesting decryption
            purpose: Purpose of access (for audit)

        Returns:
            Decrypted PHI data
        """
        try:
            # Decrypt data
            decrypted = self.encryption.decrypt_string(
                encrypted_json=encrypted_data,
                associated_data=patient_id,
            )

            # Extract metadata
            import json

            encrypted_obj = json.loads(encrypted_data)
            metadata = encrypted_obj.get("metadata", {})
            categories = set(PHICategory(c) for c in metadata.get("categories", []))

            # Log access
            self._log_access(
                user_id=user_id,
                patient_id=patient_id,
                action="decrypt",
                phi_categories=categories,
                purpose=purpose,
                success=True,
            )

            return decrypted

        except Exception as e:
            # Log failed access
            self._log_access(
                user_id=user_id,
                patient_id=patient_id,
                action="decrypt",
                phi_categories=set(),
                purpose=purpose,
                success=False,
                audit_trail={"error": str(e)},
            )
            raise

    def encrypt_record(
        self,
        record: Dict[str, Any],
        phi_fields: List[PHIField],
        patient_id: str,
        user_id: str,
    ) -> Dict[str, Any]:
        """
        Encrypt PHI fields in a record.

        Args:
            record: Data record
            phi_fields: PHI field definitions
            patient_id: Patient identifier
            user_id: User performing encryption

        Returns:
            Record with encrypted PHI fields
        """
        encrypted_record = record.copy()

        for field in phi_fields:
            if field.field_name in record:
                value = record[field.field_name]

                if value is not None:
                    # Convert to string if needed
                    value_str = str(value)

                    # Encrypt field
                    encrypted_value = self.encrypt_phi(
                        data=value_str,
                        patient_id=patient_id,
                        user_id=user_id,
                        categories={field.category},
                        classification=field.classification,
                    )

                    encrypted_record[field.field_name] = encrypted_value

        return encrypted_record

    def decrypt_record(
        self,
        encrypted_record: Dict[str, Any],
        phi_fields: List[PHIField],
        patient_id: str,
        user_id: str,
        purpose: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Decrypt PHI fields in a record.

        Args:
            encrypted_record: Record with encrypted PHI
            phi_fields: PHI field definitions
            patient_id: Patient identifier
            user_id: User requesting decryption
            purpose: Purpose of access

        Returns:
            Record with decrypted PHI fields
        """
        decrypted_record = encrypted_record.copy()

        for field in phi_fields:
            if field.field_name in encrypted_record:
                encrypted_value = encrypted_record[field.field_name]

                if encrypted_value is not None:
                    # Decrypt field
                    decrypted_value = self.decrypt_phi(
                        encrypted_data=encrypted_value,
                        patient_id=patient_id,
                        user_id=user_id,
                        purpose=purpose,
                    )

                    decrypted_record[field.field_name] = decrypted_value

        return decrypted_record

    def _log_access(
        self,
        user_id: str,
        patient_id: str,
        action: str,
        phi_categories: Set[PHICategory],
        purpose: Optional[str] = None,
        success: bool = True,
        audit_trail: Optional[Dict[str, Any]] = None,
    ):
        """Log PHI access for HIPAA compliance."""
        log_entry = PHIAccessLog(
            log_id=f"phi_{secrets.token_hex(16)}",
            timestamp=datetime.utcnow(),
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            phi_categories=phi_categories,
            purpose=purpose,
            success=success,
            audit_trail=audit_trail or {},
        )

        self.access_logs.append(log_entry)

        # Also log to main audit logger
        if self.audit_logger:
            from .audit_logger import AuditEventType, AuditLevel

            self.audit_logger.log(
                event_type=(
                    AuditEventType.DATA_READ if action == "decrypt" else AuditEventType.DATA_WRITE
                ),
                action=action,
                result="success" if success else "failure",
                user_id=user_id,
                resource=f"patient:{patient_id}",
                level=AuditLevel.SECURITY,
                details={
                    "patient_id": patient_id,
                    "phi_categories": [c.value for c in phi_categories],
                    "purpose": purpose,
                },
            )

    def get_patient_access_log(
        self,
        patient_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[PHIAccessLog]:
        """Get access log for specific patient."""
        logs = [log for log in self.access_logs if log.patient_id == patient_id]

        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]

        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]

        return logs

    def get_user_access_log(
        self,
        user_id: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> List[PHIAccessLog]:
        """Get access log for specific user."""
        logs = [log for log in self.access_logs if log.user_id == user_id]

        if start_time:
            logs = [log for log in logs if log.timestamp >= start_time]

        if end_time:
            logs = [log for log in logs if log.timestamp <= end_time]

        return logs


__all__ = [
    "PHIEncryptionService",
    "PHICategory",
    "PHIClassification",
    "PHIField",
    "PHIAccessLog",
]
