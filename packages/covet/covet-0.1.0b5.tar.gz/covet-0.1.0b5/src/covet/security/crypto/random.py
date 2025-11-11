"""
Cryptographically Secure Random Generation
==========================================

Production-ready cryptographically secure pseudorandom number generator (CSPRNG)
for generating secure tokens, passwords, UUIDs, and random bytes.

All functions use os.urandom() and secrets module which provide cryptographically
strong random data suitable for:
- Authentication tokens
- Session IDs
- Password reset tokens
- API keys
- Encryption keys
- Nonces and IVs
- Security-sensitive random data

NEVER use Python's random module for security purposes - it's not cryptographically secure!

Security Standards:
- Uses system CSPRNG (/dev/urandom on Unix, CryptGenRandom on Windows)
- Suitable for PCI DSS, SOC 2, and cryptographic operations
- Resistant to prediction and timing attacks
"""

import os
import secrets
import string
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class PasswordStrength(str, Enum):
    """Password strength levels."""

    WEAK = "weak"  # 8 chars, letters + numbers
    MEDIUM = "medium"  # 12 chars, letters + numbers + symbols
    STRONG = "strong"  # 16 chars, full charset
    VERY_STRONG = "very_strong"  # 24+ chars, full charset


@dataclass
class PasswordConfig:
    """Password generation configuration."""

    length: int = 16
    use_uppercase: bool = True
    use_lowercase: bool = True
    use_digits: bool = True
    use_symbols: bool = True
    exclude_ambiguous: bool = True  # Exclude O0, l1I, etc.
    min_uppercase: int = 1
    min_lowercase: int = 1
    min_digits: int = 1
    min_symbols: int = 1


class CSPRNGGenerator:
    """
    Cryptographically Secure Pseudorandom Number Generator.

    Provides high-level interface for generating secure random data
    for various security purposes.
    """

    # Character sets for password generation
    UPPERCASE = string.ascii_uppercase
    LOWERCASE = string.ascii_lowercase
    DIGITS = string.digits
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    # Ambiguous characters to exclude
    AMBIGUOUS = "O0l1I|"

    def __init__(self):
        """Initialize CSPRNG generator."""
        self._entropy_pool_size = 0
        self._check_entropy()

    def _check_entropy(self):
        """Check system entropy pool (Linux only)."""
        try:
            with open("/proc/sys/kernel/random/entropy_avail", "r") as f:
                self._entropy_pool_size = int(f.read().strip())
        except (FileNotFoundError, PermissionError):
            # Not on Linux or no permission
            self._entropy_pool_size = -1

    @property
    def entropy_available(self) -> int:
        """
        Get available entropy in system pool.

        Returns:
            Entropy in bits (-1 if not available)
        """
        self._check_entropy()
        return self._entropy_pool_size

    def generate_bytes(self, length: int) -> bytes:
        """
        Generate cryptographically secure random bytes.

        Args:
            length: Number of bytes to generate

        Returns:
            Random bytes

        Raises:
            ValueError: If length is negative
        """
        if length < 0:
            raise ValueError("Length must be non-negative")

        return secrets.token_bytes(length)

    def generate_hex(self, length: int) -> str:
        """
        Generate random hexadecimal string.

        Args:
            length: Length of hex string (will generate length/2 bytes)

        Returns:
            Random hex string
        """
        return secrets.token_hex(length // 2)

    def generate_urlsafe(self, length: int) -> str:
        """
        Generate URL-safe random string (base64url encoding).

        Args:
            length: Approximate length of string

        Returns:
            Random URL-safe string
        """
        return secrets.token_urlsafe(length)

    def generate_token(self, length: int = 32, charset: Optional[str] = None) -> str:
        """
        Generate random token from specified charset.

        Args:
            length: Token length
            charset: Character set to use (default: alphanumeric)

        Returns:
            Random token
        """
        if charset is None:
            charset = string.ascii_letters + string.digits

        return "".join(secrets.choice(charset) for _ in range(length))

    def generate_password(self, config: Optional[PasswordConfig] = None) -> str:
        """
        Generate cryptographically secure password.

        Args:
            config: Password configuration

        Returns:
            Random password meeting requirements

        Raises:
            ValueError: If configuration is invalid
        """
        if config is None:
            config = PasswordConfig()

        # Build character set
        charset = ""
        if config.use_uppercase:
            charset += self.UPPERCASE
        if config.use_lowercase:
            charset += self.LOWERCASE
        if config.use_digits:
            charset += self.DIGITS
        if config.use_symbols:
            charset += self.SYMBOLS

        if not charset:
            raise ValueError("At least one character type must be enabled")

        # Remove ambiguous characters if requested
        if config.exclude_ambiguous:
            charset = "".join(c for c in charset if c not in self.AMBIGUOUS)

        # Validate minimum requirements don't exceed length
        min_total = (
            config.min_uppercase + config.min_lowercase + config.min_digits + config.min_symbols
        )
        if min_total > config.length:
            raise ValueError("Minimum requirements exceed password length")

        # Generate password with requirements
        while True:
            password = "".join(secrets.choice(charset) for _ in range(config.length))

            # Check requirements
            if config.use_uppercase and config.min_uppercase > 0:
                if sum(c in self.UPPERCASE for c in password) < config.min_uppercase:
                    continue

            if config.use_lowercase and config.min_lowercase > 0:
                if sum(c in self.LOWERCASE for c in password) < config.min_lowercase:
                    continue

            if config.use_digits and config.min_digits > 0:
                if sum(c in self.DIGITS for c in password) < config.min_digits:
                    continue

            if config.use_symbols and config.min_symbols > 0:
                if sum(c in self.SYMBOLS for c in password) < config.min_symbols:
                    continue

            return password

    def generate_passphrase(
        self, word_count: int = 6, separator: str = "-", wordlist: Optional[List[str]] = None
    ) -> str:
        """
        Generate memorable passphrase (diceware-style).

        Args:
            word_count: Number of words
            separator: Word separator
            wordlist: Custom wordlist (uses built-in if None)

        Returns:
            Random passphrase
        """
        if wordlist is None:
            # Use EFF long wordlist subset for demonstration
            # In production, load from file
            wordlist = self._get_default_wordlist()

        words = [secrets.choice(wordlist) for _ in range(word_count)]
        return separator.join(words)

    def _get_default_wordlist(self) -> List[str]:
        """
        Get default wordlist for passphrase generation.

        In production, this should load from EFF wordlist or similar.
        """
        return [
            "abandon",
            "ability",
            "able",
            "about",
            "above",
            "absent",
            "absorb",
            "abstract",
            "absurd",
            "abuse",
            "access",
            "accident",
            "account",
            "accuse",
            "achieve",
            "acid",
            "acoustic",
            "acquire",
            "across",
            "act",
            "action",
            "actor",
            "actress",
            "actual",
            "adapt",
            "add",
            "addict",
            "address",
            "adjust",
            "admit",
            "adult",
            "advance",
            "advice",
            "aerobic",
            "affair",
            "afford",
            "afraid",
            "again",
            "agent",
            "agree",
            "ahead",
            "aim",
            "airport",
            "aisle",
            "alarm",
            "album",
            "alcohol",
            "alert",
            "alien",
            "alive",
            "almost",
            "alone",
            "alpha",
            "already",
            "also",
            "alter",
            "always",
            "amateur",
            "amazing",
            "among",
            "amount",
            "amused",
            "analyst",
            "anchor",
            "ancient",
            "anger",
            "angle",
            "angry",
            "animal",
            "ankle",
            "announce",
            "annual",
            "another",
            "answer",
            "antenna",
            "antique",
            "anxiety",
        ]

    def generate_uuid(self, version: int = 4) -> str:
        """
        Generate UUID.

        Args:
            version: UUID version (4 = random, 1 = time-based)

        Returns:
            UUID string
        """
        if version == 4:
            return str(uuid.uuid4())
        elif version == 1:
            return str(uuid.uuid1())
        else:
            raise ValueError(f"Unsupported UUID version: {version}")

    def generate_api_key(self, prefix: Optional[str] = None, length: int = 32) -> str:
        """
        Generate API key with optional prefix.

        Format: {prefix}_{random_string}

        Args:
            prefix: Key prefix (e.g., 'pk_live')
            length: Length of random portion

        Returns:
            API key
        """
        random_part = self.generate_urlsafe(length)

        if prefix:
            return f"{prefix}_{random_part}"
        return random_part

    def generate_session_id(self, length: int = 32) -> str:
        """
        Generate session ID.

        Args:
            length: Session ID length

        Returns:
            URL-safe session ID
        """
        return self.generate_urlsafe(length)

    def generate_nonce(self, length: int = 16) -> bytes:
        """
        Generate cryptographic nonce.

        Args:
            length: Nonce length in bytes

        Returns:
            Random nonce bytes
        """
        return self.generate_bytes(length)

    def generate_salt(self, length: int = 16) -> bytes:
        """
        Generate salt for key derivation.

        Args:
            length: Salt length in bytes (minimum 16 recommended)

        Returns:
            Random salt bytes
        """
        if length < 16:
            raise ValueError("Salt should be at least 16 bytes")

        return self.generate_bytes(length)

    def generate_otp_secret(self, length: int = 20) -> str:
        """
        Generate TOTP/HOTP shared secret.

        Args:
            length: Secret length in bytes

        Returns:
            Base32-encoded secret
        """
        import base64

        secret_bytes = self.generate_bytes(length)
        return base64.b32encode(secret_bytes).decode("utf-8").rstrip("=")

    def random_int(self, min_value: int, max_value: int) -> int:
        """
        Generate cryptographically secure random integer.

        Args:
            min_value: Minimum value (inclusive)
            max_value: Maximum value (inclusive)

        Returns:
            Random integer
        """
        return secrets.randbelow(max_value - min_value + 1) + min_value

    def random_choice(self, sequence: List) -> any:
        """
        Choose random element from sequence.

        Args:
            sequence: Sequence to choose from

        Returns:
            Random element
        """
        return secrets.choice(sequence)

    def shuffle(self, sequence: List) -> List:
        """
        Cryptographically secure shuffle.

        Args:
            sequence: List to shuffle

        Returns:
            Shuffled list (new list)
        """
        shuffled = sequence.copy()
        n = len(shuffled)

        for i in range(n - 1, 0, -1):
            j = self.random_int(0, i)
            shuffled[i], shuffled[j] = shuffled[j], shuffled[i]

        return shuffled


# Global generator instance
_generator = CSPRNGGenerator()


# Convenience functions


def generate_random_bytes(length: int) -> bytes:
    """Generate random bytes."""
    return _generator.generate_bytes(length)


def generate_token(length: int = 32, charset: Optional[str] = None) -> str:
    """Generate random token."""
    return _generator.generate_token(length, charset)


def generate_uuid(version: int = 4) -> str:
    """Generate UUID."""
    return _generator.generate_uuid(version)


def generate_password(
    length: int = 16, strength: PasswordStrength = PasswordStrength.STRONG
) -> str:
    """
    Generate secure password.

    Args:
        length: Password length
        strength: Password strength level

    Returns:
        Random password
    """
    if strength == PasswordStrength.WEAK:
        config = PasswordConfig(length=max(length, 8), use_symbols=False, min_symbols=0)
    elif strength == PasswordStrength.MEDIUM:
        config = PasswordConfig(length=max(length, 12), use_symbols=True, min_symbols=1)
    elif strength == PasswordStrength.STRONG:
        config = PasswordConfig(length=max(length, 16), use_symbols=True, min_symbols=2)
    else:  # VERY_STRONG
        config = PasswordConfig(
            length=max(length, 24), use_symbols=True, min_symbols=3, exclude_ambiguous=False
        )

    return _generator.generate_password(config)


def generate_api_key(prefix: Optional[str] = None, length: int = 32) -> str:
    """Generate API key."""
    return _generator.generate_api_key(prefix, length)


def generate_session_id(length: int = 32) -> str:
    """Generate session ID."""
    return _generator.generate_session_id(length)


def generate_salt(length: int = 16) -> bytes:
    """Generate cryptographic salt."""
    return _generator.generate_salt(length)


def generate_nonce(length: int = 16) -> bytes:
    """Generate cryptographic nonce."""
    return _generator.generate_nonce(length)


__all__ = [
    "PasswordStrength",
    "PasswordConfig",
    "CSPRNGGenerator",
    "generate_random_bytes",
    "generate_token",
    "generate_uuid",
    "generate_password",
    "generate_api_key",
    "generate_session_id",
    "generate_salt",
    "generate_nonce",
]
