"""
Two-Factor Authentication (2FA) System

Production-ready 2FA implementation with:
- TOTP (Time-based One-Time Password) support
- Backup codes for recovery
- QR code generation for authenticator apps
- Rate limiting for verification attempts
- Secure secret generation and storage
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional, Tuple

try:
    import qrcode

    HAS_QRCODE = True
except ImportError:
    qrcode = None
    HAS_QRCODE = False

from .exceptions import (
    RateLimitExceededError,
    TwoFactorInvalidError,
    TwoFactorRequiredError,
)
from .models import TwoFactorSecret, User


@dataclass
class TwoFactorConfig:
    """2FA configuration settings"""

    # TOTP settings
    secret_length: int = 32  # Base32 characters
    issuer: str = "CovetPy"
    time_step: int = 30  # seconds
    digits: int = 6
    algorithm: str = "SHA1"  # SHA1, SHA256, SHA512

    # Backup codes
    backup_codes_count: int = 10
    backup_code_length: int = 8

    # Security settings
    verification_window: int = 1  # Allow ±1 time step
    max_verification_attempts: int = 5
    lockout_duration_minutes: int = 15

    # QR code settings
    qr_code_size: int = 200


@dataclass
class VerificationAttempt:
    """Track 2FA verification attempts"""

    user_id: str
    timestamp: datetime
    success: bool
    ip_address: Optional[str] = None


class TOTPGenerator:
    """Time-based One-Time Password generator"""

    @staticmethod
    def generate_secret(length: int = 32) -> str:
        """Generate base32-encoded secret"""
        # Generate random bytes
        random_bytes = secrets.token_bytes(length)
        # Encode as base32 (without padding)
        return base64.b32encode(random_bytes).decode("utf-8").rstrip("=")

    @staticmethod
    def generate_totp(
        secret: str,
        timestamp: Optional[int] = None,
        time_step: int = 30,
        digits: int = 6,
        algorithm: str = "SHA1",
    ) -> str:
        """Generate TOTP code"""
        if timestamp is None:
            timestamp = int(time.time())

        # Calculate time counter
        counter = timestamp // time_step

        # Convert counter to bytes (big-endian 8-byte integer)
        counter_bytes = struct.pack(">Q", counter)

        # Choose hash algorithm
        if algorithm == "SHA1":
            hash_func = hashlib.sha1
        elif algorithm == "SHA256":
            hash_func = hashlib.sha256
        elif algorithm == "SHA512":
            hash_func = hashlib.sha512
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")

        # Decode base32 secret
        try:
            # Add padding if needed
            secret_padded = secret + "=" * (8 - len(secret) % 8)
            secret_bytes = base64.b32decode(secret_padded)
        except Exception:
            raise ValueError("Invalid secret format")

        # Generate HMAC
        hmac_result = hmac.new(secret_bytes, counter_bytes, hash_func).digest()

        # Dynamic truncation
        offset = hmac_result[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_result[offset : offset + 4])[0]
        truncated &= 0x7FFFFFFF

        # Generate OTP
        otp = truncated % (10**digits)

        # Pad with leading zeros
        return str(otp).zfill(digits)

    @staticmethod
    def verify_totp(
        secret: str,
        token: str,
        timestamp: Optional[int] = None,
        time_step: int = 30,
        digits: int = 6,
        algorithm: str = "SHA1",
        window: int = 1,
    ) -> bool:
        """Verify TOTP code with time window"""
        if timestamp is None:
            timestamp = int(time.time())

        # Check current time and window
        for i in range(-window, window + 1):
            check_time = timestamp + (i * time_step)
            expected_token = TOTPGenerator.generate_totp(
                secret, check_time, time_step, digits, algorithm
            )

            # Constant-time comparison to prevent timing attacks
            if secrets.compare_digest(token, expected_token):
                return True

        return False


class BackupCodeGenerator:
    """Backup code generator for 2FA recovery"""

    @staticmethod
    def generate_backup_codes(count: int = 10, length: int = 8) -> List[str]:
        """Generate cryptographically secure backup codes"""
        codes = []
        for _ in range(count):
            # Generate random code with uppercase letters and digits
            code = "".join(
                secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(length)
            )
            codes.append(code)
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code for secure storage"""
        # Use SHA-256 for backup code hashing
        return hashlib.sha256(code.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_backup_code(code: str, hashed_codes: List[str]) -> bool:
        """Verify backup code against hashed list"""
        code_hash = BackupCodeGenerator.hash_backup_code(code)
        return code_hash in hashed_codes


class QRCodeGenerator:
    """QR code generator for TOTP setup"""

    @staticmethod
    def generate_provisioning_uri(
        secret: str,
        account_name: str,
        issuer: str,
        algorithm: str = "SHA1",
        digits: int = 6,
        period: int = 30,
    ) -> str:
        """Generate provisioning URI for authenticator apps"""
        # Format: otpauth://totp/issuer:accountname?secret=...&issuer=...
        params = {
            "secret": secret,
            "issuer": issuer,
            "algorithm": algorithm,
            "digits": str(digits),
            "period": str(period),
        }

        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"otpauth://totp/{issuer}:{account_name}?{query_string}"

    @staticmethod
    def generate_qr_code(provisioning_uri: str, size: int = 200) -> bytes:
        """Generate QR code image as PNG bytes"""
        if not HAS_QRCODE:
            raise ImportError(
                "qrcode library not installed. " "Install with: pip install qrcode[pil]"
            )

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Resize if needed
        if size != 200:
            img = img.resize((size, size))

        # Convert to bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        return img_bytes.getvalue()


class RateLimiter:
    """Rate limiter for 2FA verification attempts"""

    def __init__(self, max_attempts: int = 5, window_minutes: int = 15):
        self.max_attempts = max_attempts
        self.window_minutes = window_minutes
        self.attempts: List[VerificationAttempt] = []

    def is_rate_limited(self, user_id: str, ip_address: Optional[str] = None) -> bool:
        """Check if user/IP is rate limited"""
        now = datetime.utcnow()
        window_start = now - timedelta(minutes=self.window_minutes)

        # Clean old attempts
        self.attempts = [attempt for attempt in self.attempts if attempt.timestamp > window_start]

        # Count failed attempts in window
        failed_attempts = [
            attempt
            for attempt in self.attempts
            if (attempt.user_id == user_id or (ip_address and attempt.ip_address == ip_address))
            and not attempt.success
        ]

        return len(failed_attempts) >= self.max_attempts

    def record_attempt(self, user_id: str, success: bool, ip_address: Optional[str] = None):
        """Record verification attempt"""
        attempt = VerificationAttempt(
            user_id=user_id,
            timestamp=datetime.utcnow(),
            success=success,
            ip_address=ip_address,
        )
        self.attempts.append(attempt)


class TwoFactorAuth:
    """
    Two-Factor Authentication manager
    """

    def __init__(self, config: Optional[TwoFactorConfig] = None):
        self.config = config or TwoFactorConfig()
        self.rate_limiter = RateLimiter(
            max_attempts=self.config.max_verification_attempts,
            window_minutes=self.config.lockout_duration_minutes,
        )

    def setup_totp(self, user: User) -> Tuple[str, str, bytes]:
        """
        Setup TOTP for user

        Returns:
            tuple: (secret, provisioning_uri, qr_code_png)
        """
        # Generate secret
        secret = TOTPGenerator.generate_secret(self.config.secret_length)

        # Generate backup codes
        backup_codes = BackupCodeGenerator.generate_backup_codes(
            self.config.backup_codes_count, self.config.backup_code_length
        )

        # Hash backup codes for storage
        hashed_backup_codes = [BackupCodeGenerator.hash_backup_code(code) for code in backup_codes]

        # Create 2FA secret object
        TwoFactorSecret(secret=secret, backup_codes=hashed_backup_codes)

        # Enable 2FA for user
        user.enable_two_factor(secret, hashed_backup_codes)

        # Generate provisioning URI
        account_name = user.email or user.username
        provisioning_uri = QRCodeGenerator.generate_provisioning_uri(
            secret=secret,
            account_name=account_name,
            issuer=self.config.issuer,
            algorithm=self.config.algorithm,
            digits=self.config.digits,
            period=self.config.time_step,
        )

        # Generate QR code
        qr_code = QRCodeGenerator.generate_qr_code(provisioning_uri, self.config.qr_code_size)

        return secret, provisioning_uri, qr_code

    def verify_totp(self, user: User, token: str, ip_address: Optional[str] = None) -> bool:
        """
        Verify TOTP token

        Args:
            user: User object
            token: TOTP token to verify
            ip_address: Client IP address for rate limiting

        Returns:
            bool: True if token is valid

        Raises:
            TwoFactorRequiredError: If 2FA is not enabled
            RateLimitExceededError: If rate limited
            TwoFactorInvalidError: If token is invalid
        """
        if not user.two_factor_enabled or not user.two_factor_secret:
            raise TwoFactorRequiredError("Two-factor authentication is not enabled")

        # Check rate limiting
        if self.rate_limiter.is_rate_limited(user.id, ip_address):
            raise RateLimitExceededError("Too many verification attempts")

        # Verify TOTP
        is_valid = TOTPGenerator.verify_totp(
            secret=user.two_factor_secret.secret,
            token=token,
            time_step=self.config.time_step,
            digits=self.config.digits,
            algorithm=self.config.algorithm,
            window=self.config.verification_window,
        )

        # Record attempt
        self.rate_limiter.record_attempt(user.id, is_valid, ip_address)

        if is_valid:
            # Update last used timestamp
            user.two_factor_secret.last_used_at = datetime.utcnow()

        return is_valid

    def verify_backup_code(self, user: User, code: str, ip_address: Optional[str] = None) -> bool:
        """
        Verify backup code

        Args:
            user: User object
            code: Backup code to verify
            ip_address: Client IP address for rate limiting

        Returns:
            bool: True if code is valid and unused
        """
        if not user.two_factor_enabled or not user.two_factor_secret:
            raise TwoFactorRequiredError("Two-factor authentication is not enabled")

        # Check rate limiting
        if self.rate_limiter.is_rate_limited(user.id, ip_address):
            raise RateLimitExceededError("Too many verification attempts")

        # Verify backup code
        code_hash = BackupCodeGenerator.hash_backup_code(code.upper())
        is_valid = code_hash in user.two_factor_secret.backup_codes

        # Record attempt
        self.rate_limiter.record_attempt(user.id, is_valid, ip_address)

        if is_valid:
            # Remove used backup code
            user.two_factor_secret.backup_codes.remove(code_hash)
            user.two_factor_secret.last_used_at = datetime.utcnow()

        return is_valid

    def generate_recovery_codes(self, user: User) -> List[str]:
        """
        Generate new backup codes for user

        Returns:
            List of new backup codes (unhashed)
        """
        if not user.two_factor_enabled:
            raise TwoFactorRequiredError("Two-factor authentication is not enabled")

        # Generate new backup codes
        backup_codes = BackupCodeGenerator.generate_backup_codes(
            self.config.backup_codes_count, self.config.backup_code_length
        )

        # Hash and store
        hashed_backup_codes = [BackupCodeGenerator.hash_backup_code(code) for code in backup_codes]

        user.two_factor_secret.backup_codes = hashed_backup_codes

        return backup_codes

    def disable_totp(self, user: User):
        """Disable 2FA for user"""
        user.disable_two_factor()

    def get_backup_codes_count(self, user: User) -> int:
        """Get number of remaining backup codes"""
        if not user.two_factor_enabled or not user.two_factor_secret:
            return 0
        return len(user.two_factor_secret.backup_codes)

    def is_setup_required(self, user: User) -> bool:
        """Check if 2FA setup is required for user"""
        # This could be based on user role, security policy, etc.
        return user.security_settings.require_2fa and not user.two_factor_enabled


# Global 2FA instance
_two_factor_auth_instance: Optional[TwoFactorAuth] = None


def get_two_factor_auth() -> TwoFactorAuth:
    """Get 2FA singleton instance"""
    global _two_factor_auth_instance
    if _two_factor_auth_instance is None:
        _two_factor_auth_instance = TwoFactorAuth()
    return _two_factor_auth_instance


def configure_two_factor_auth(config: TwoFactorConfig) -> TwoFactorAuth:
    """Configure 2FA with custom settings"""
    global _two_factor_auth_instance
    _two_factor_auth_instance = TwoFactorAuth(config)
    return _two_factor_auth_instance
