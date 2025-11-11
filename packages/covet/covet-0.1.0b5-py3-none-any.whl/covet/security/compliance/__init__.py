"""
CovetPy Security Compliance Framework

This module provides comprehensive compliance implementations for:
- PCI DSS (Payment Card Industry Data Security Standard)
- HIPAA (Health Insurance Portability and Accountability Act)
- GDPR (General Data Protection Regulation)
- SOC 2 (Service Organization Control 2)

Each compliance standard is implemented with:
- Technical controls (encryption, access control, audit logging)
- Policy enforcement mechanisms
- Compliance validation and reporting
- Automated compliance checking

SECURITY ARCHITECTURE:
- Defense in depth with multiple security layers
- Principle of least privilege
- Secure by default configurations
- Comprehensive audit trails
- Automated compliance monitoring

NO MOCK DATA: Production-ready implementations with real cryptography,
database operations, and compliance validation.
"""

from .access_control import (
    AccessControlManager,
    AccessDecision,
    AccessPolicy,
    LeastPrivilegeEnforcer,
)
from .audit_logger import (
    AuditEvent,
    AuditLevel,
    AuditLogger,
    ComplianceAuditLog,
    TamperProofLogger,
)
from .baa import (
    BAAManager,
    BreachNotification,
    BusinessAssociateAgreement,
)
from .compliance_validator import (
    ComplianceReport,
    ComplianceScore,
    ComplianceValidator,
    ValidationResult,
)
from .consent import (
    ConsentAuditTrail,
    ConsentManager,
    ConsentRecord,
    ConsentType,
)
from .encryption_at_rest import (
    DataEncryptionService,
    EncryptionKey,
    KeyManagementService,
    KeyRotationPolicy,
)
from .gdpr_deletion import (
    DeletionRequest,
    DeletionVerification,
    RightToDeletionService,
)
from .gdpr_portability import (
    DataExportFormat,
    DataPortabilityService,
    ExportRequest,
)
from .hipaa_audit import (
    HIPAAAuditEvent,
    HIPAAAuditLogger,
    HIPAAComplianceReport,
)
from .phi_encryption import (
    PHIAccessLog,
    PHIClassification,
    PHIEncryptionService,
)
from .retention import (
    DataRetentionPolicy,
    RetentionManager,
    SecureDeletion,
)
from .soc2_controls import (
    ControlAssessment,
    ControlCategory,
    SecurityControl,
    SOC2ControlFramework,
)
from .soc2_monitoring import (
    IncidentResponse,
    SecurityEvent,
    SOC2Monitor,
)

__all__ = [
    # Encryption at rest
    "DataEncryptionService",
    "EncryptionKey",
    "KeyManagementService",
    "KeyRotationPolicy",
    # Audit logging
    "AuditLogger",
    "AuditEvent",
    "AuditLevel",
    "TamperProofLogger",
    "ComplianceAuditLog",
    # Access control
    "AccessControlManager",
    "AccessPolicy",
    "AccessDecision",
    "LeastPrivilegeEnforcer",
    # PHI encryption
    "PHIEncryptionService",
    "PHIClassification",
    "PHIAccessLog",
    # HIPAA audit
    "HIPAAAuditLogger",
    "HIPAAAuditEvent",
    "HIPAAComplianceReport",
    # BAA
    "BAAManager",
    "BusinessAssociateAgreement",
    "BreachNotification",
    # Retention
    "DataRetentionPolicy",
    "RetentionManager",
    "SecureDeletion",
    # GDPR portability
    "DataPortabilityService",
    "DataExportFormat",
    "ExportRequest",
    # GDPR deletion
    "RightToDeletionService",
    "DeletionRequest",
    "DeletionVerification",
    # Consent
    "ConsentManager",
    "ConsentType",
    "ConsentRecord",
    "ConsentAuditTrail",
    # SOC 2 controls
    "SOC2ControlFramework",
    "SecurityControl",
    "ControlCategory",
    "ControlAssessment",
    # SOC 2 monitoring
    "SOC2Monitor",
    "SecurityEvent",
    "IncidentResponse",
    # Compliance validation
    "ComplianceValidator",
    "ComplianceScore",
    "ComplianceReport",
    "ValidationResult",
]

# Version information
__version__ = "1.0.0"
__compliance_standards__ = ["PCI-DSS-4.0", "HIPAA", "GDPR", "SOC-2-Type-II"]
