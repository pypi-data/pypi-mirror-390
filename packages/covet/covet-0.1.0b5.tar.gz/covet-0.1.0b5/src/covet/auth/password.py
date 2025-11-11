"""
Secure Password Hashing and Verification

Production-grade password handling with:
- Scrypt-based password hashing (OWASP recommended)
- Timing attack protection
- Configurable security parameters
- Password strength validation
- Common password detection

Security Features:
- Memory-hard algorithm (Scrypt) resistant to GPU attacks
- Salt automatically generated per password
- Constant-time comparison to prevent timing attacks
- Configurable work factors for future-proofing
- Protection against rainbow table attacks

Usage:
    from covet.auth import hash_password, verify_password

    # Hash password
    hashed = hash_password('SecurePass123!')

    # Verify password
    is_valid = verify_password('SecurePass123!', hashed)
"""

import hashlib
import hmac
import secrets
import time
from typing import Optional, Tuple

# Try to use scrypt from hashlib (Python 3.6+)
try:
    from hashlib import scrypt as _scrypt
    HAS_SCRYPT = True
except ImportError:
    HAS_SCRYPT = False
    _scrypt = None


class PasswordHasher:
    """
    Secure password hashing using Scrypt algorithm.

    Scrypt is recommended by OWASP for password hashing because:
    - Memory-hard (resistant to GPU/ASIC attacks)
    - Configurable work factors
    - Built-in salt generation
    - Industry standard (used by Tarsnap, Ethereum, etc.)

    Security Parameters:
        N (CPU/memory cost): 2^14 = 16384 (OWASP minimum for interactive)
        r (block size): 8 (OWASP recommendation)
        p (parallelization): 1 (OWASP recommendation)
        dklen (derived key length): 64 bytes

    These parameters provide strong protection while remaining suitable
    for interactive login (< 100ms on modern hardware).
    """

    def __init__(
        self,
        n: int = 16384,  # CPU/memory cost (2^14)
        r: int = 8,       # Block size
        p: int = 1,       # Parallelization factor
        dklen: int = 64,  # Derived key length
        salt_len: int = 32  # Salt length in bytes
    ):
        """
        Initialize password hasher.

        Args:
            n: CPU/memory cost factor (power of 2, minimum 2^14)
            r: Block size (typically 8)
            p: Parallelization factor (typically 1)
            dklen: Length of derived key in bytes
            salt_len: Length of salt in bytes (minimum 16)

        Security Notes:
            - Increase N for higher security (doubles memory/time per increment)
            - N=2^14 for interactive, 2^16 for high security, 2^20 for very high
            - Never decrease these values below OWASP recommendations
        """
        if not HAS_SCRYPT:
            raise ImportError(
                "Scrypt not available. Python 3.6+ required. "
                "Install with: pip install scrypt"
            )

        # Validate parameters
        if n < 16384:  # 2^14
            raise ValueError("N must be at least 16384 (2^14) per OWASP guidelines")
        if r < 1:
            raise ValueError("r must be at least 1")
        if p < 1:
            raise ValueError("p must be at least 1")
        if salt_len < 16:
            raise ValueError("Salt length must be at least 16 bytes")

        self.n = n
        self.r = r
        self.p = p
        self.dklen = dklen
        self.salt_len = salt_len

    def hash_password(self, password: str) -> str:
        """
        Hash password using Scrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password in format: scrypt$N$r$p$salt$hash

        Example:
            >>> hasher = PasswordHasher()
            >>> hashed = hasher.hash_password('MySecurePass123!')
            >>> print(hashed)
            'scrypt$16384$8$1$abc...def$123...789'
        """
        if not password:
            raise ValueError("Password cannot be empty")

        # Generate cryptographically secure random salt
        salt = secrets.token_bytes(self.salt_len)

        # Hash password
        key = _scrypt(
            password.encode('utf-8'),
            salt=salt,
            n=self.n,
            r=self.r,
            p=self.p,
            dklen=self.dklen
        )

        # Encode to hex for storage
        salt_hex = salt.hex()
        key_hex = key.hex()

        # Return formatted hash string
        return f"scrypt${self.n}${self.r}${self.p}${salt_hex}${key_hex}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password to verify
            password_hash: Previously hashed password

        Returns:
            True if password matches, False otherwise

        Security:
            Uses constant-time comparison to prevent timing attacks
        """
        if not password or not password_hash:
            return False

        try:
            # Parse hash string
            parts = password_hash.split('$')
            if len(parts) != 6 or parts[0] != 'scrypt':
                return False

            # Extract parameters
            n = int(parts[1])
            r = int(parts[2])
            p = int(parts[3])
            salt = bytes.fromhex(parts[4])
            stored_key = bytes.fromhex(parts[5])

            # Hash provided password with same parameters
            key = _scrypt(
                password.encode('utf-8'),
                salt=salt,
                n=n,
                r=r,
                p=p,
                dklen=len(stored_key)
            )

            # Constant-time comparison to prevent timing attacks
            return hmac.compare_digest(key, stored_key)

        except Exception:
            # Any error in verification = invalid password
            return False


# Global default hasher instance
_default_hasher = None


def get_hasher() -> PasswordHasher:
    """Get the default password hasher instance."""
    global _default_hasher
    if _default_hasher is None:
        _default_hasher = PasswordHasher()
    return _default_hasher


def hash_password(password: str) -> str:
    """
    Hash password using secure defaults.

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Example:
        >>> hashed = hash_password('MyPassword123!')
        >>> print(len(hashed))
        135
    """
    return get_hasher().hash_password(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verify password against hash.

    Args:
        password: Plain text password to verify
        password_hash: Previously hashed password

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password('MyPassword123!')
        >>> verify_password('MyPassword123!', hashed)
        True
        >>> verify_password('WrongPassword', hashed)
        False
    """
    return get_hasher().verify_password(password, password_hash)


def check_password_strength(password: str) -> Tuple[bool, list[str]]:
    """
    Check password strength against common requirements.

    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Not a common password

    Args:
        password: Password to check

    Returns:
        Tuple of (is_strong, list_of_issues)

    Example:
        >>> check_password_strength('weak')
        (False, ['Too short', 'No uppercase', ...])
        >>> check_password_strength('SecurePass123!')
        (True, [])
    """
    issues = []

    if not password:
        return False, ['Password is required']

    # Length check
    if len(password) < 8:
        issues.append('Password must be at least 8 characters')
    if len(password) > 128:
        issues.append('Password must not exceed 128 characters')

    # Character type checks
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)

    if not has_upper:
        issues.append('Password must contain at least one uppercase letter')
    if not has_lower:
        issues.append('Password must contain at least one lowercase letter')
    if not has_digit:
        issues.append('Password must contain at least one digit')
    if not has_special:
        issues.append('Password must contain at least one special character')

    # Common password check
    common_passwords = {
        'password', 'password123', '12345678', 'qwerty', 'abc123',
        'password1', '123456789', '12345', '1234567', 'welcome',
        'admin', 'letmein', 'monkey', 'dragon', '111111',
        'baseball', 'iloveyou', 'trustno1', 'sunshine', 'master'
    }

    if password.lower() in common_passwords:
        issues.append('Password is too common')

    return len(issues) == 0, issues


def generate_secure_password(length: int = 16) -> str:
    """
    Generate a cryptographically secure random password.

    Args:
        length: Password length (minimum 12)

    Returns:
        Random password string

    Example:
        >>> password = generate_secure_password(16)
        >>> len(password)
        16
        >>> check_password_strength(password)[0]
        True
    """
    if length < 12:
        raise ValueError("Password length must be at least 12")

    # Character sets
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    digits = '0123456789'
    special = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    all_chars = uppercase + lowercase + digits + special

    # Ensure at least one of each type
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]

    # Fill remaining length
    for _ in range(length - 4):
        password_chars.append(secrets.choice(all_chars))

    # Shuffle to avoid predictable pattern
    password_list = list(password_chars)
    for i in range(len(password_list)):
        j = secrets.randbelow(len(password_list))
        password_list[i], password_list[j] = password_list[j], password_list[i]

    return ''.join(password_list)


def estimate_hash_time() -> float:
    """
    Estimate time to hash a password (for performance tuning).

    Returns:
        Time in seconds

    Example:
        >>> time = estimate_hash_time()
        >>> print(f"Hash time: {time:.3f}s")
        Hash time: 0.085s
    """
    test_password = 'test_password_123'
    start = time.time()
    hash_password(test_password)
    return time.time() - start


__all__ = [
    'PasswordHasher',
    'hash_password',
    'verify_password',
    'check_password_strength',
    'generate_secure_password',
    'estimate_hash_time',
    'get_hasher',
]
