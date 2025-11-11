"""
CovetPy Cryptography & Key Management System
============================================

Enterprise-grade cryptographic operations and key management for CovetPy.

This module provides production-ready implementations of:
- Symmetric encryption (AES-GCM, AES-CBC, ChaCha20-Poly1305)
- Asymmetric encryption (RSA, ECDH, EdDSA)
- Cryptographic hashing (SHA-2/3, BLAKE2, Argon2, bcrypt)
- Key Management System (KMS) with rotation and versioning
- Cloud KMS integration (AWS KMS, Azure Key Vault)
- Digital signatures and certificate validation
- Cryptographically secure random generation

All implementations follow industry best practices:
- FIPS 140-2 compliant algorithms
- Constant-time operations where applicable
- Defense against timing attacks
- Secure key storage and rotation
- Comprehensive audit logging

NO MOCK DATA - All cryptographic operations use proven libraries:
- cryptography (PyCA Cryptography)
- PyNaCl (libsodium bindings)

Security Standards:
- PCI DSS compliant
- SOC 2 Type II ready
- OWASP ASVS Level 3
- NIST SP 800-series guidelines
"""

from .asymmetric import (
    AsymmetricCipher,
    ECCCipher,
    ECCCurve,
    HybridCipher,
    KeyPairGenerator,
    RSACipher,
    RSAKeySize,
)
from .hashing import (
    HashAlgorithm,
    HMACGenerator,
    PasswordHasher,
    constant_time_compare,
    hash_data,
    hash_password,
    verify_password,
)
from .kms import (
    KeyManagementSystem,
    KeyMetadata,
    KeyPurpose,
    KeyRotationPolicy,
    KeyStatus,
)
from .kms_aws import AWSKMSProvider
from .kms_azure import AzureKMSProvider
from .random import (
    CSPRNGGenerator,
    generate_password,
    generate_random_bytes,
    generate_token,
    generate_uuid,
)
from .signing import (
    DigitalSigner,
    JWTSigner,
    SignatureAlgorithm,
    verify_certificate_chain,
    verify_signature,
)
from .symmetric import (
    AESCipher,
    ChaCha20Cipher,
    EncryptionMode,
    KeyDerivation,
    SymmetricCipher,
    derive_key_argon2,
    derive_key_pbkdf2,
    derive_key_scrypt,
)

__version__ = "1.0.0"
__all__ = [
    # Symmetric encryption
    "AESCipher",
    "ChaCha20Cipher",
    "SymmetricCipher",
    "KeyDerivation",
    "EncryptionMode",
    "derive_key_pbkdf2",
    "derive_key_argon2",
    "derive_key_scrypt",
    # Asymmetric encryption
    "RSACipher",
    "ECCCipher",
    "HybridCipher",
    "KeyPairGenerator",
    "AsymmetricCipher",
    "RSAKeySize",
    "ECCCurve",
    # Hashing
    "HashAlgorithm",
    "PasswordHasher",
    "HMACGenerator",
    "hash_data",
    "hash_password",
    "verify_password",
    "constant_time_compare",
    # Random
    "generate_random_bytes",
    "generate_token",
    "generate_uuid",
    "generate_password",
    "CSPRNGGenerator",
    # Signing
    "DigitalSigner",
    "JWTSigner",
    "SignatureAlgorithm",
    "verify_signature",
    "verify_certificate_chain",
    # KMS
    "KeyManagementSystem",
    "KeyMetadata",
    "KeyStatus",
    "KeyPurpose",
    "KeyRotationPolicy",
    "AWSKMSProvider",
    "AzureKMSProvider",
]
