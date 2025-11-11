"""
Core Authentication Manager

Central authentication system that coordinates:
- User registration and login
- Password reset flow
- 2FA verification
- Session management
- JWT token management
- OAuth2 authentication
- Security monitoring and audit logging
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from .exceptions import (
    AccountLockedError,
    AuthException,
    InvalidCredentialsError,
    PasswordResetRequiredError,
    SecurityViolationError,
    TwoFactorRequiredError,
)
from .jwt_auth import JWTAuth, JWTConfig, TokenPair, get_jwt_auth
from .models import (
    LoginAttempt,
    LoginAttemptResult,
    PasswordPolicy,
    PasswordResetToken,
    User,
    UserStatus,
)
from .oauth2 import OAuth2Manager, OAuth2UserInfo, get_oauth2_manager
from .rbac import RBACManager, get_rbac_manager
from .session import SessionConfig, SessionManager, get_session_manager
from .two_factor import TwoFactorAuth, get_two_factor_auth


@dataclass
class AuthConfig:
    """Authentication system configuration"""

    # Password policy
    password_policy: PasswordPolicy = field(default_factory=PasswordPolicy)

    # Account lockout
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30

    # Password reset
    reset_token_expires_minutes: int = 15
    reset_max_attempts_per_hour: int = 3

    # Registration
    require_email_verification: bool = True
    allow_registration: bool = True
    default_user_role: str = "user"

    # Session settings
    remember_me_days: int = 30

    # Security settings
    audit_login_attempts: bool = True
    require_https: bool = True


@dataclass
class LoginResult:
    """Result of login attempt"""

    success: bool
    user: Optional[User] = None
    token_pair: Optional[TokenPair] = None
    session_id: Optional[str] = None
    requires_2fa: bool = False
    requires_password_reset: bool = False
    lockout_until: Optional[datetime] = None
    message: str = ""


@dataclass
class RegistrationResult:
    """Result of registration attempt"""

    success: bool
    user: Optional[User] = None
    message: str = ""
    verification_token: Optional[str] = None


class UserStore:
    """In-memory user store for development"""

    def __init__(self):
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, str] = {}  # email -> user_id
        self._users_by_username: Dict[str, str] = {}  # username -> user_id
        self._reset_tokens: Dict[str, PasswordResetToken] = {}
        self._login_attempts: List[LoginAttempt] = []

    def create_user(self, user: User) -> bool:
        """Create new user"""
        # Check for duplicates
        if user.id in self._users:
            return False
        if user.email in self._users_by_email:
            return False
        if user.username in self._users_by_username:
            return False

        # Store user
        self._users[user.id] = user
        self._users_by_email[user.email] = user.id
        self._users_by_username[user.username] = user.id

        return True

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        user_id = self._users_by_email.get(email.lower())
        return self._users.get(user_id) if user_id else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        user_id = self._users_by_username.get(username.lower())
        return self._users.get(user_id) if user_id else None

    def update_user(self, user: User):
        """Update user"""
        if user.id in self._users:
            self._users[user.id] = user

    def store_reset_token(self, token: PasswordResetToken):
        """Store password reset token"""
        self._reset_tokens[token.token_hash] = token

    def get_reset_token(self, token_hash: str) -> Optional[PasswordResetToken]:
        """Get password reset token"""
        return self._reset_tokens.get(token_hash)

    def delete_reset_token(self, token_hash: str):
        """Delete password reset token"""
        self._reset_tokens.pop(token_hash, None)

    def record_login_attempt(self, attempt: LoginAttempt):
        """Record login attempt"""
        self._login_attempts.append(attempt)

        # Clean old attempts (keep last 1000)
        if len(self._login_attempts) > 1000:
            self._login_attempts = self._login_attempts[-1000:]

    def get_recent_login_attempts(self, user_id: str, hours: int = 1) -> List[LoginAttempt]:
        """Get recent login attempts for user"""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            attempt
            for attempt in self._login_attempts
            if attempt.user_id == user_id and attempt.timestamp > cutoff
        ]


class AuthManager:
    """
    Core authentication manager
    """

    def __init__(
        self,
        config: Optional[AuthConfig] = None,
        user_store: Optional[UserStore] = None,
    ):
        self.config = config or AuthConfig()
        self.user_store = user_store or UserStore()
        self.jwt_auth = get_jwt_auth()
        self.session_manager = get_session_manager()
        self.oauth2_manager = get_oauth2_manager()
        self.two_factor_auth = get_two_factor_auth()
        self.rbac_manager = get_rbac_manager()

    def register_user(
        self,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> RegistrationResult:
        """
        Register new user

        Args:
            username: Unique username
            email: User email address
            password: User password
            first_name: First name (optional)
            last_name: Last name (optional)
            ip_address: Client IP address

        Returns:
            RegistrationResult with user and verification token
        """
        if not self.config.allow_registration:
            return RegistrationResult(False, message="Registration is disabled")

        # Validate inputs
        if not username or not email or not password:
            return RegistrationResult(False, message="Username, email, and password are required")

        # Check if user exists
        if self.user_store.get_user_by_email(email):
            return RegistrationResult(False, message="Email already exists")

        if self.user_store.get_user_by_username(username):
            return RegistrationResult(False, message="Username already exists")

        # Create user
        user_id = secrets.token_urlsafe(16)
        user = User(
            id=user_id,
            username=username.lower(),
            email=email.lower(),
            password_hash="",  # Will be set below
            first_name=first_name,
            last_name=last_name,
            status=(
                UserStatus.PENDING_VERIFICATION
                if self.config.require_email_verification
                else UserStatus.ACTIVE
            ),
        )

        # Set password
        if not user.set_password(password, self.config.password_policy):
            return RegistrationResult(False, message="Password does not meet policy requirements")

        # Add default role
        user.add_role(self.config.default_user_role)

        # Store user
        if not self.user_store.create_user(user):
            return RegistrationResult(False, message="Failed to create user")

        # Add to RBAC store
        if hasattr(self.rbac_manager.store, "add_user"):
            self.rbac_manager.store.add_user(user)

        # Generate verification token if needed
        verification_token = None
        if self.config.require_email_verification:
            verification_token = self.jwt_auth.create_verification_token(user)

        return RegistrationResult(
            success=True,
            user=user,
            message="User registered successfully",
            verification_token=verification_token,
        )

    def login(
        self,
        username_or_email: str,
        password: str,
        ip_address: str,
        user_agent: str,
        remember_me: bool = False,
    ) -> LoginResult:
        """
        Authenticate user login

        Args:
            username_or_email: Username or email
            password: User password
            ip_address: Client IP address
            user_agent: Client user agent
            remember_me: Whether to create long-lived session

        Returns:
            LoginResult with authentication status
        """
        # Find user
        user = self.user_store.get_user_by_email(
            username_or_email
        ) or self.user_store.get_user_by_username(username_or_email)

        login_attempt = LoginAttempt(
            user_id=user.id if user else "unknown",
            ip_address=ip_address,
            user_agent=user_agent,
            result=LoginAttemptResult.INVALID_CREDENTIALS,
            details={"username_or_email": username_or_email},
        )

        try:
            if not user:
                login_attempt.result = LoginAttemptResult.INVALID_CREDENTIALS
                self.user_store.record_login_attempt(login_attempt)
                return LoginResult(False, message="Invalid credentials")

            # Check account status
            if user.status == UserStatus.INACTIVE:
                return LoginResult(False, message="Account is inactive")

            if user.status == UserStatus.SUSPENDED:
                return LoginResult(False, message="Account is suspended")

            if user.status == UserStatus.PENDING_VERIFICATION:
                return LoginResult(False, message="Account requires email verification")

            # Check if account is locked
            if user.is_account_locked():
                login_attempt.result = LoginAttemptResult.ACCOUNT_LOCKED
                self.user_store.record_login_attempt(login_attempt)
                return LoginResult(
                    False, message="Account is locked", lockout_until=user.locked_until
                )

            # Verify password
            if not user.verify_password(password):
                user.record_failed_login()
                self.user_store.update_user(user)

                login_attempt.result = LoginAttemptResult.INVALID_CREDENTIALS
                self.user_store.record_login_attempt(login_attempt)

                return LoginResult(False, message="Invalid credentials")

            # Check if password reset is required
            if user.is_password_expired(self.config.password_policy):
                return LoginResult(
                    False,
                    requires_password_reset=True,
                    message="Password reset required",
                )

            # Check if 2FA is required
            if user.two_factor_enabled:
                login_attempt.result = LoginAttemptResult.TWO_FACTOR_REQUIRED
                self.user_store.record_login_attempt(login_attempt)

                return LoginResult(
                    False,
                    user=user,
                    requires_2fa=True,
                    message="Two-factor authentication required",
                )

            # Successful login
            user.record_successful_login(ip_address)
            self.user_store.update_user(user)

            # Create tokens and session
            token_pair = self.jwt_auth.create_token_pair(user)

            session = self.session_manager.create_session(user, ip_address, user_agent)
            if remember_me:
                # Extend session for remember me
                session.refresh(self.config.remember_me_days * 24 * 60)
                self.session_manager.store.set(session)

            login_attempt.result = LoginAttemptResult.SUCCESS
            self.user_store.record_login_attempt(login_attempt)

            return LoginResult(
                success=True,
                user=user,
                token_pair=token_pair,
                session_id=session.id,
                message="Login successful",
            )

        except Exception as e:
            # Log security event
            login_attempt.details["error"] = str(e)
            self.user_store.record_login_attempt(login_attempt)

            return LoginResult(False, message="Authentication failed")

    def verify_2fa_and_complete_login(
        self,
        user: User,
        totp_code: str,
        ip_address: str,
        user_agent: str,
        remember_me: bool = False,
    ) -> LoginResult:
        """
        Verify 2FA and complete login process
        """
        try:
            # Verify TOTP
            if self.two_factor_auth.verify_totp(user, totp_code, ip_address):
                # Successful 2FA
                user.record_successful_login(ip_address)
                self.user_store.update_user(user)

                # Create tokens and session
                token_pair = self.jwt_auth.create_token_pair(user)
                session = self.session_manager.create_session(user, ip_address, user_agent)

                if remember_me:
                    session.refresh(self.config.remember_me_days * 24 * 60)
                    self.session_manager.store.set(session)

                # Record successful login
                login_attempt = LoginAttempt(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    result=LoginAttemptResult.SUCCESS,
                )
                self.user_store.record_login_attempt(login_attempt)

                return LoginResult(
                    success=True,
                    user=user,
                    token_pair=token_pair,
                    session_id=session.id,
                    message="Login successful",
                )
            else:
                # Failed 2FA
                login_attempt = LoginAttempt(
                    user_id=user.id,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    result=LoginAttemptResult.TWO_FACTOR_FAILED,
                )
                self.user_store.record_login_attempt(login_attempt)

                return LoginResult(False, message="Invalid two-factor authentication code")

        except Exception:
            return LoginResult(False, message="Two-factor authentication failed")

    def logout(
        self,
        user: User,
        session_id: Optional[str] = None,
        access_token: Optional[str] = None,
        revoke_all_sessions: bool = False,
    ):
        """
        Logout user and invalidate tokens/sessions
        """
        if revoke_all_sessions:
            # Revoke all sessions for user
            self.session_manager.delete_user_sessions(user.id)
        elif session_id:
            # Revoke specific session
            self.session_manager.delete_session(session_id)

        if access_token:
            # Revoke JWT token
            self.jwt_auth.revoke_token(access_token)

    def initiate_password_reset(self, email: str, ip_address: str, user_agent: str) -> bool:
        """
        Initiate password reset flow

        Returns:
            bool: Always True to prevent email enumeration
        """
        user = self.user_store.get_user_by_email(email)

        # Always return True to prevent email enumeration
        if not user:
            return True

        # Check rate limiting
        recent_attempts = self.user_store.get_recent_login_attempts(user.id, hours=1)
        reset_attempts = [
            attempt
            for attempt in recent_attempts
            if attempt.details.get("action") == "password_reset"
        ]

        if len(reset_attempts) >= self.config.reset_max_attempts_per_hour:
            # Rate limited, but still return True
            return True

        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()

        reset_token_obj = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=datetime.utcnow()
            + timedelta(minutes=self.config.reset_token_expires_minutes),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        self.user_store.store_reset_token(reset_token_obj)

        # Record attempt
        login_attempt = LoginAttempt(
            user_id=user.id,
            ip_address=ip_address,
            user_agent=user_agent,
            result=LoginAttemptResult.SUCCESS,
            details={"action": "password_reset"},
        )
        self.user_store.record_login_attempt(login_attempt)

        # In a real implementation, send email with reset_token
        # For now, we'll just store it

        return True

    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Reset password using reset token
        """
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        reset_token_obj = self.user_store.get_reset_token(token_hash)

        if not reset_token_obj:
            return False

        if reset_token_obj.used:
            return False

        if datetime.utcnow() > reset_token_obj.expires_at:
            self.user_store.delete_reset_token(token_hash)
            return False

        # Get user
        user = self.user_store.get_user_by_id(reset_token_obj.user_id)
        if not user:
            return False

        # Set new password
        if not user.set_password(new_password, self.config.password_policy):
            return False

        # Mark token as used
        reset_token_obj.used = True
        self.user_store.update_user(user)
        self.user_store.delete_reset_token(token_hash)

        # Revoke all existing sessions for security
        self.session_manager.delete_user_sessions(user.id)

        return True

    def verify_email(self, verification_token: str) -> bool:
        """
        Verify user email using verification token
        """
        try:
            payload = self.jwt_auth.verify_token(verification_token)

            if payload.get("token_type") != "verification":
                return False

            user_id = payload.get("sub")
            user = self.user_store.get_user_by_id(user_id)

            if not user:
                return False

            if user.status == UserStatus.PENDING_VERIFICATION:
                user.status = UserStatus.ACTIVE
                self.user_store.update_user(user)

            return True

        except Exception:
            return False

    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """
        Change user password (requires current password)
        """
        # Verify current password
        if not user.verify_password(current_password):
            return False

        # Set new password
        if not user.set_password(new_password, self.config.password_policy):
            return False

        self.user_store.update_user(user)

        # Optionally revoke all sessions except current one
        # This would require session context

        return True


class TokenManager:
    """
    Token verification and management
    """

    def __init__(self, auth_manager: AuthManager):
        self.auth_manager = auth_manager
        self.jwt_auth = auth_manager.jwt_auth
        self.session_manager = auth_manager.session_manager

    def verify_bearer_token(self, token: str) -> Optional[User]:
        """Verify JWT bearer token and return user"""
        try:
            payload = self.jwt_auth.verify_token(token)
            user_id = payload.get("sub")

            if user_id:
                return self.auth_manager.user_store.get_user_by_id(user_id)

            return None

        except Exception:
            return None

    def verify_session_token(
        self, session_id: str, ip_address: Optional[str] = None
    ) -> Optional[User]:
        """Verify session token and return user"""
        try:
            session = self.session_manager.refresh_session(session_id, ip_address)

            if session:
                return self.auth_manager.user_store.get_user_by_id(session.user_id)

            return None

        except Exception:
            return None


# Global auth manager instance
_auth_manager_instance: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get auth manager singleton instance"""
    global _auth_manager_instance
    if _auth_manager_instance is None:
        _auth_manager_instance = AuthManager()
    return _auth_manager_instance


def configure_auth_manager(
    config: AuthConfig, user_store: Optional[UserStore] = None
) -> AuthManager:
    """Configure auth manager with custom settings"""
    global _auth_manager_instance
    _auth_manager_instance = AuthManager(config, user_store)
    return _auth_manager_instance
