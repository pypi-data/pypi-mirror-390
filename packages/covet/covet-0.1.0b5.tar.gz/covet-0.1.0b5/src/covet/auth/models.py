"""
Secure User Models with Password Hashing and RBAC

Production-ready user models with:
- Secure password hashing using scrypt/bcrypt
- Account lockout protection
- Password policy enforcement
- Audit trail
- RBAC support
"""

import hashlib
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class UserStatus(Enum):
    """User account status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class LoginAttemptResult(Enum):
    """Login attempt results for security monitoring"""

    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    ACCOUNT_LOCKED = "account_locked"
    TWO_FACTOR_REQUIRED = "two_factor_required"
    TWO_FACTOR_FAILED = "two_factor_failed"


@dataclass
class PasswordPolicy:
    """Password policy configuration"""

    min_length: int = 12
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digits: bool = True
    require_special_chars: bool = True
    max_age_days: int = 90
    history_count: int = 5  # Remember last N passwords
    special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?"


@dataclass
class SecuritySettings:
    """Security settings for accounts"""

    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    require_2fa: bool = False
    password_reset_timeout_minutes: int = 15


class PasswordHasher:
    """Secure password hashing using scrypt with salting"""

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, bytes]:
        """
        Hash password using scrypt with secure parameters

        Returns:
            tuple: (hash_string, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(32)

        # scrypt parameters: N=32768, r=8, p=1 (recommended for interactive
        # use)
        key = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=32768,  # CPU/memory cost
            r=8,  # Block size
            p=1,  # Parallelization
            dklen=64,  # Derived key length
        )

        # Combine salt and key for storage
        hash_string = salt.hex() + ":" + key.hex()
        return hash_string, salt

    @staticmethod
    def verify_password(password: str, hash_string: str) -> bool:
        """Verify password against stored hash"""
        try:
            salt_hex, key_hex = hash_string.split(":")
            salt = bytes.fromhex(salt_hex)
            stored_key = bytes.fromhex(key_hex)

            # Recompute hash with same parameters
            new_key = hashlib.scrypt(
                password.encode("utf-8"), salt=salt, n=32768, r=8, p=1, dklen=64
            )

            # Constant-time comparison to prevent timing attacks
            return secrets.compare_digest(stored_key, new_key)
        except (ValueError, TypeError):
            return False


@dataclass
class Permission:
    """Individual permission"""

    id: str
    name: str
    description: str
    resource: str  # e.g., "users", "posts", "admin"
    action: str  # e.g., "read", "write", "delete", "admin"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Role:
    """User role with permissions"""

    id: str
    name: str
    description: str
    permissions: Set[str] = field(default_factory=set)  # Permission IDs
    is_system_role: bool = False  # Cannot be deleted
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def has_permission(self, permission_id: str) -> bool:
        """Check if role has specific permission"""
        return permission_id in self.permissions

    def add_permission(self, permission_id: str):
        """Add permission to role"""
        self.permissions.add(permission_id)
        self.updated_at = datetime.utcnow()

    def remove_permission(self, permission_id: str):
        """Remove permission from role"""
        self.permissions.discard(permission_id)
        self.updated_at = datetime.utcnow()


@dataclass
class TwoFactorSecret:
    """2FA secret and backup codes"""

    secret: str
    backup_codes: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used_at: Optional[datetime] = None


@dataclass
class LoginAttempt:
    """Security audit trail for login attempts"""

    user_id: str
    ip_address: str
    user_agent: str
    result: LoginAttemptResult
    timestamp: datetime = field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PasswordResetToken:
    """Secure password reset token"""

    user_id: str
    token_hash: str  # Hashed token for security
    expires_at: datetime
    used: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class User:
    """
    Secure user model with comprehensive security features
    """

    id: str
    username: str
    email: str
    password_hash: str
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    roles: Set[str] = field(default_factory=set)  # Role IDs

    # Security fields
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    last_login_ip: Optional[str] = None
    password_changed_at: datetime = field(default_factory=datetime.utcnow)
    password_history: List[str] = field(default_factory=list)

    # 2FA
    two_factor_enabled: bool = False
    two_factor_secret: Optional[TwoFactorSecret] = None

    # Profile information
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

    # OAuth2 connections
    oauth2_connections: Dict[str, str] = field(default_factory=dict)  # provider -> user_id

    # Audit trail
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_activity_at: Optional[datetime] = None

    # Security settings
    security_settings: SecuritySettings = field(default_factory=SecuritySettings)

    def set_password(self, password: str, policy: PasswordPolicy) -> bool:
        """
        Set password with policy validation and history check

        Returns:
            bool: True if password was set successfully
        """
        # Validate password policy
        if not self._validate_password_policy(password, policy):
            return False

        # Check password history
        if self._is_password_in_history(password):
            return False

        # Hash new password
        hash_string, _ = PasswordHasher.hash_password(password)

        # Update password history
        if self.password_hash:  # Don't add initial password to history
            self.password_history.append(self.password_hash)
            # Keep only last N passwords
            if len(self.password_history) > policy.history_count:
                self.password_history = self.password_history[-policy.history_count :]

        self.password_hash = hash_string
        self.password_changed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Reset failed attempts on successful password change
        self.failed_login_attempts = 0
        self.locked_until = None

        return True

    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        return PasswordHasher.verify_password(password, self.password_hash)

    def is_password_expired(self, policy: PasswordPolicy) -> bool:
        """Check if password has expired according to policy"""
        if policy.max_age_days <= 0:
            return False

        expiry_date = self.password_changed_at + timedelta(days=policy.max_age_days)
        return datetime.utcnow() > expiry_date

    def is_account_locked(self) -> bool:
        """Check if account is currently locked"""
        if self.status == UserStatus.LOCKED:
            return True

        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True

        return False

    def record_failed_login(self):
        """Record failed login attempt and potentially lock account"""
        self.failed_login_attempts += 1

        if self.failed_login_attempts >= self.security_settings.max_login_attempts:
            lockout_duration = timedelta(minutes=self.security_settings.lockout_duration_minutes)
            self.locked_until = datetime.utcnow() + lockout_duration

    def record_successful_login(self, ip_address: str):
        """Record successful login and reset failed attempts"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
        self.last_activity_at = datetime.utcnow()

    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return role_name in self.roles

    def add_role(self, role_id: str):
        """Add role to user"""
        self.roles.add(role_id)
        self.updated_at = datetime.utcnow()

    def remove_role(self, role_id: str):
        """Remove role from user"""
        self.roles.discard(role_id)
        self.updated_at = datetime.utcnow()

    def add_oauth2_connection(self, provider: str, provider_user_id: str):
        """Add OAuth2 connection"""
        self.oauth2_connections[provider] = provider_user_id
        self.updated_at = datetime.utcnow()

    def enable_two_factor(self, secret: str, backup_codes: List[str]):
        """Enable 2FA with secret and backup codes"""
        self.two_factor_secret = TwoFactorSecret(secret=secret, backup_codes=backup_codes)
        self.two_factor_enabled = True
        self.updated_at = datetime.utcnow()

    def disable_two_factor(self):
        """Disable 2FA"""
        self.two_factor_enabled = False
        self.two_factor_secret = None
        self.updated_at = datetime.utcnow()

    def _validate_password_policy(self, password: str, policy: PasswordPolicy) -> bool:
        """Validate password against policy"""
        if len(password) < policy.min_length:
            return False

        if policy.require_uppercase and not any(c.isupper() for c in password):
            return False

        if policy.require_lowercase and not any(c.islower() for c in password):
            return False

        if policy.require_digits and not any(c.isdigit() for c in password):
            return False

        if policy.require_special_chars and not any(c in policy.special_chars for c in password):
            return False

        return True

    def _is_password_in_history(self, password: str) -> bool:
        """Check if password was used recently"""
        for old_hash in self.password_history:
            if PasswordHasher.verify_password(password, old_hash):
                return True
        return False

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert user to dictionary for API responses"""
        result = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "status": self.status.value,
            "roles": list(self.roles),
            "first_name": self.first_name,
            "last_name": self.last_name,
            "two_factor_enabled": self.two_factor_enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_login_at": (self.last_login_at.isoformat() if self.last_login_at else None),
            "last_activity_at": (
                self.last_activity_at.isoformat() if self.last_activity_at else None
            ),
        }

        if include_sensitive:
            result.update(
                {
                    "failed_login_attempts": self.failed_login_attempts,
                    "locked_until": (self.locked_until.isoformat() if self.locked_until else None),
                    "last_login_ip": self.last_login_ip,
                    "oauth2_connections": list(self.oauth2_connections.keys()),
                    "password_changed_at": self.password_changed_at.isoformat(),
                }
            )

        return result


@dataclass
class Session:
    """User session for session-based authentication"""

    id: str
    user_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_accessed_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True
    data: Dict[str, Any] = field(default_factory=dict)  # Session data storage

    def is_expired(self) -> bool:
        """Check if session has expired"""
        if not self.is_active:
            return True

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return True

        return False

    def refresh(self, timeout_minutes: int = 60):
        """Refresh session expiration"""
        self.last_accessed_at = datetime.utcnow()
        self.expires_at = datetime.utcnow() + timedelta(minutes=timeout_minutes)

    def invalidate(self):
        """Invalidate session"""
        self.is_active = False
