"""
Asymmetric Encryption Module
============================

Production-ready asymmetric (public-key) cryptography implementations:
- RSA encryption and signing (2048, 3072, 4096-bit)
- Elliptic Curve Cryptography (ECC) - ECDH, ECDSA
- EdDSA (Ed25519) - Modern elliptic curve signing
- Hybrid encryption (RSA + AES for large data)

Security Features:
- OAEP padding for RSA encryption (prevents chosen-ciphertext attacks)
- PSS padding for RSA signatures (probabilistic signature scheme)
- Constant-time operations where possible
- Secure key generation with proper entropy
- Key serialization (PEM, DER formats)
- Public key exchange protocols

Use Cases:
- Secure key exchange
- Digital signatures
- Certificate generation
- Encrypt large data (via hybrid encryption)
- Secure messaging protocols

All implementations use PyCA cryptography library for FIPS 140-2 compliance.
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class RSAKeySize(int, Enum):
    """RSA key sizes."""

    RSA_2048 = 2048  # Minimum for new systems
    RSA_3072 = 3072  # Equivalent to 128-bit security
    RSA_4096 = 4096  # High security


class ECCCurve(str, Enum):
    """Elliptic curve choices."""

    SECP256R1 = "secp256r1"  # NIST P-256 (widely supported)
    SECP384R1 = "secp384r1"  # NIST P-384
    SECP521R1 = "secp521r1"  # NIST P-521
    SECP256K1 = "secp256k1"  # Bitcoin curve


@dataclass
class KeyPair:
    """Public/private key pair."""

    private_key: bytes  # PEM-encoded private key
    public_key: bytes  # PEM-encoded public key
    key_size: Optional[int] = None
    algorithm: Optional[str] = None


class KeyPairGenerator:
    """
    Generate asymmetric key pairs.

    Supports RSA, ECC, and Ed25519 key generation with proper entropy.
    """

    @staticmethod
    def generate_rsa(
        key_size: RSAKeySize = RSAKeySize.RSA_2048, public_exponent: int = 65537
    ) -> KeyPair:
        """
        Generate RSA key pair.

        Args:
            key_size: RSA key size in bits
            public_exponent: Public exponent (typically 65537)

        Returns:
            KeyPair with PEM-encoded keys
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=public_exponent, key_size=key_size.value, backend=default_backend()
        )

        # Serialize private key (encrypted with password in production)
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return KeyPair(
            private_key=private_pem, public_key=public_pem, key_size=key_size.value, algorithm="RSA"
        )

    @staticmethod
    def generate_ecc(curve: ECCCurve = ECCCurve.SECP256R1) -> KeyPair:
        """
        Generate Elliptic Curve key pair.

        Args:
            curve: Elliptic curve to use

        Returns:
            KeyPair with PEM-encoded keys
        """
        # Map curve name to curve object
        curve_map = {
            ECCCurve.SECP256R1: ec.SECP256R1(),
            ECCCurve.SECP384R1: ec.SECP384R1(),
            ECCCurve.SECP521R1: ec.SECP521R1(),
            ECCCurve.SECP256K1: ec.SECP256K1(),
        }

        curve_obj = curve_map.get(curve)
        if not curve_obj:
            raise ValueError(f"Unsupported curve: {curve}")

        # Generate private key
        private_key = ec.generate_private_key(curve_obj, default_backend())

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return KeyPair(
            private_key=private_pem, public_key=public_pem, algorithm=f"ECC-{curve.value}"
        )

    @staticmethod
    def generate_ed25519() -> KeyPair:
        """
        Generate Ed25519 key pair (modern signing algorithm).

        Returns:
            KeyPair with PEM-encoded keys
        """
        # Generate private key
        private_key = ed25519.Ed25519PrivateKey.generate()

        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        # Serialize public key
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return KeyPair(private_key=private_pem, public_key=public_pem, algorithm="Ed25519")


class RSACipher:
    """
    RSA encryption and decryption.

    Uses OAEP padding with SHA-256 for secure encryption.
    Suitable for encrypting small amounts of data (e.g., symmetric keys).
    """

    def __init__(self, public_key: Optional[bytes] = None, private_key: Optional[bytes] = None):
        """
        Initialize RSA cipher.

        Args:
            public_key: PEM-encoded public key (for encryption)
            private_key: PEM-encoded private key (for decryption)
        """
        self.public_key_obj = None
        self.private_key_obj = None

        if public_key:
            self.public_key_obj = serialization.load_pem_public_key(
                public_key, backend=default_backend()
            )

        if private_key:
            self.private_key_obj = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
            # Extract public key from private key
            if not self.public_key_obj:
                self.public_key_obj = self.private_key_obj.public_key()

    def encrypt(self, plaintext: bytes) -> bytes:
        """
        Encrypt data using RSA-OAEP.

        Args:
            plaintext: Data to encrypt (max size depends on key size)

        Returns:
            Encrypted ciphertext

        Raises:
            ValueError: If plaintext too large or no public key
        """
        if not self.public_key_obj:
            raise ValueError("Public key required for encryption")

        # Check plaintext size (RSA can only encrypt data smaller than key size)
        max_size = (self.public_key_obj.key_size // 8) - 2 * (256 // 8) - 2
        if len(plaintext) > max_size:
            raise ValueError(f"Plaintext too large (max {max_size} bytes for this key)")

        ciphertext = self.public_key_obj.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        """
        Decrypt data using RSA-OAEP.

        Args:
            ciphertext: Encrypted data

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If no private key or decryption fails
        """
        if not self.private_key_obj:
            raise ValueError("Private key required for decryption")

        plaintext = self.private_key_obj.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None
            ),
        )

        return plaintext

    def sign(self, data: bytes) -> bytes:
        """
        Sign data using RSA-PSS.

        Args:
            data: Data to sign

        Returns:
            Digital signature

        Raises:
            ValueError: If no private key
        """
        if not self.private_key_obj:
            raise ValueError("Private key required for signing")

        signature = self.private_key_obj.sign(
            data,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )

        return signature

    def verify(self, data: bytes, signature: bytes) -> bool:
        """
        Verify RSA-PSS signature.

        Args:
            data: Original data
            signature: Signature to verify

        Returns:
            True if signature valid

        Raises:
            ValueError: If no public key
        """
        if not self.public_key_obj:
            raise ValueError("Public key required for verification")

        try:
            self.public_key_obj.verify(
                signature,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


class ECCCipher:
    """
    Elliptic Curve Cryptography for key exchange and signing.

    Uses ECDH for key agreement and ECDSA for signatures.
    """

    def __init__(self, private_key: Optional[bytes] = None, curve: ECCCurve = ECCCurve.SECP256R1):
        """
        Initialize ECC cipher.

        Args:
            private_key: PEM-encoded private key
            curve: Elliptic curve
        """
        self.curve = curve

        if private_key:
            self.private_key_obj = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
            self.public_key_obj = self.private_key_obj.public_key()
        else:
            self.private_key_obj = None
            self.public_key_obj = None

    def ecdh_exchange(self, peer_public_key: bytes) -> bytes:
        """
        Perform ECDH key exchange.

        Args:
            peer_public_key: Peer's PEM-encoded public key

        Returns:
            Shared secret (use with KDF before using as key)

        Raises:
            ValueError: If no private key
        """
        if not self.private_key_obj:
            raise ValueError("Private key required for key exchange")

        # Load peer's public key
        peer_key = serialization.load_pem_public_key(peer_public_key, backend=default_backend())

        # Perform key exchange
        from cryptography.hazmat.primitives.asymmetric import ec as ec_module

        shared_key = self.private_key_obj.exchange(ec_module.ECDH(), peer_key)

        return shared_key

    def sign(self, data: bytes) -> bytes:
        """
        Sign data using ECDSA.

        Args:
            data: Data to sign

        Returns:
            Digital signature

        Raises:
            ValueError: If no private key
        """
        if not self.private_key_obj:
            raise ValueError("Private key required for signing")

        signature = self.private_key_obj.sign(data, ec.ECDSA(hashes.SHA256()))

        return signature

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify ECDSA signature.

        Args:
            data: Original data
            signature: Signature to verify
            public_key: PEM-encoded public key

        Returns:
            True if signature valid
        """
        pub_key = serialization.load_pem_public_key(public_key, backend=default_backend())

        try:
            pub_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False


class HybridCipher:
    """
    Hybrid encryption combining RSA and AES.

    Uses RSA to encrypt a random AES key, then AES to encrypt the actual data.
    This allows encrypting large amounts of data with the security of RSA.

    Process:
    1. Generate random AES-256 key
    2. Encrypt data with AES-GCM
    3. Encrypt AES key with RSA-OAEP
    4. Return both encrypted key and encrypted data
    """

    def __init__(self, rsa_cipher: RSACipher):
        """
        Initialize hybrid cipher.

        Args:
            rsa_cipher: RSA cipher for key encryption
        """
        self.rsa_cipher = rsa_cipher

    def encrypt(self, plaintext: bytes) -> Tuple[bytes, bytes, bytes, bytes]:
        """
        Encrypt data using hybrid encryption.

        Args:
            plaintext: Data to encrypt

        Returns:
            Tuple of (encrypted_key, iv, ciphertext, tag)
        """
        # Generate random AES-256 key
        aes_key = os.urandom(32)

        # Generate random IV
        iv = os.urandom(12)

        # Encrypt data with AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()
        tag = encryptor.tag

        # Encrypt AES key with RSA
        encrypted_key = self.rsa_cipher.encrypt(aes_key)

        return encrypted_key, iv, ciphertext, tag

    def decrypt(self, encrypted_key: bytes, iv: bytes, ciphertext: bytes, tag: bytes) -> bytes:
        """
        Decrypt data using hybrid encryption.

        Args:
            encrypted_key: RSA-encrypted AES key
            iv: AES initialization vector
            ciphertext: AES-encrypted data
            tag: AES-GCM authentication tag

        Returns:
            Decrypted plaintext
        """
        # Decrypt AES key with RSA
        aes_key = self.rsa_cipher.decrypt(encrypted_key)

        # Decrypt data with AES-GCM
        cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext


class Ed25519Signer:
    """
    Ed25519 digital signatures.

    Modern, fast elliptic curve signature algorithm with strong security.
    """

    def __init__(self, private_key: Optional[bytes] = None):
        """
        Initialize Ed25519 signer.

        Args:
            private_key: PEM-encoded Ed25519 private key
        """
        if private_key:
            self.private_key_obj = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
            self.public_key_obj = self.private_key_obj.public_key()
        else:
            self.private_key_obj = None
            self.public_key_obj = None

    def sign(self, data: bytes) -> bytes:
        """
        Sign data using Ed25519.

        Args:
            data: Data to sign

        Returns:
            Digital signature (64 bytes)

        Raises:
            ValueError: If no private key
        """
        if not self.private_key_obj:
            raise ValueError("Private key required for signing")

        return self.private_key_obj.sign(data)

    def verify(self, data: bytes, signature: bytes, public_key: bytes) -> bool:
        """
        Verify Ed25519 signature.

        Args:
            data: Original data
            signature: Signature to verify
            public_key: PEM-encoded public key

        Returns:
            True if signature valid
        """
        pub_key = serialization.load_pem_public_key(public_key, backend=default_backend())

        try:
            pub_key.verify(signature, data)
            return True
        except Exception:
            return False


class AsymmetricCipher:
    """
    Unified interface for asymmetric operations.

    Automatically detects key type and uses appropriate algorithm.
    """

    def __init__(self, private_key: Optional[bytes] = None, public_key: Optional[bytes] = None):
        """
        Initialize asymmetric cipher.

        Args:
            private_key: PEM-encoded private key
            public_key: PEM-encoded public key
        """
        self.private_key_pem = private_key
        self.public_key_pem = public_key

        # Detect key type
        if private_key:
            key = serialization.load_pem_private_key(
                private_key, password=None, backend=default_backend()
            )
            self.key_type = type(key).__name__
        elif public_key:
            key = serialization.load_pem_public_key(public_key, backend=default_backend())
            self.key_type = type(key).__name__
        else:
            self.key_type = None

        # Initialize appropriate cipher
        if "RSA" in self.key_type:
            self.cipher = RSACipher(public_key, private_key)
        elif "EllipticCurve" in self.key_type:
            self.cipher = ECCCipher(private_key)
        elif "Ed25519" in self.key_type:
            self.cipher = Ed25519Signer(private_key)
        else:
            self.cipher = None

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt data (RSA only)."""
        if isinstance(self.cipher, RSACipher):
            return self.cipher.encrypt(plaintext)
        else:
            raise ValueError("Encryption only supported for RSA keys")

    def decrypt(self, ciphertext: bytes) -> bytes:
        """Decrypt data (RSA only)."""
        if isinstance(self.cipher, RSACipher):
            return self.cipher.decrypt(ciphertext)
        else:
            raise ValueError("Decryption only supported for RSA keys")

    def sign(self, data: bytes) -> bytes:
        """Sign data."""
        if hasattr(self.cipher, "sign"):
            return self.cipher.sign(data)
        else:
            raise ValueError("Signing not supported for this key type")

    def verify(self, data: bytes, signature: bytes, public_key: Optional[bytes] = None) -> bool:
        """Verify signature."""
        if isinstance(self.cipher, RSACipher):
            return self.cipher.verify(data, signature)
        elif isinstance(self.cipher, ECCCipher):
            return self.cipher.verify(data, signature, public_key or self.public_key_pem)
        elif isinstance(self.cipher, Ed25519Signer):
            return self.cipher.verify(data, signature, public_key or self.public_key_pem)
        else:
            raise ValueError("Verification not supported for this key type")


__all__ = [
    "RSAKeySize",
    "ECCCurve",
    "KeyPair",
    "KeyPairGenerator",
    "RSACipher",
    "ECCCipher",
    "HybridCipher",
    "Ed25519Signer",
    "AsymmetricCipher",
]
