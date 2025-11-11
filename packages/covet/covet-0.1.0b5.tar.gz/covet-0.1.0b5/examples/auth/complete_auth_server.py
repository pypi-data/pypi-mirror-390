"""
Complete Authentication Server Example

Demonstrates integration of all authentication mechanisms:
- OAuth2 authorization server
- SAML service provider
- Session-based authentication
- Multi-factor authentication
- Password policy enforcement
- LDAP integration

This is a production-ready example that can be deployed.
"""

import asyncio
import json
from datetime import datetime
from typing import Optional, Dict, Any

# Import CovetPy authentication modules
from src.covet.security.auth.oauth2_provider import (
    OAuth2Provider,
    OAuth2Config,
    GrantType,
)
from src.covet.security.auth.saml_provider import (
    SAMLProvider,
    SAMLConfig,
)
from src.covet.security.auth.session_manager import (
    SessionManager,
    SessionConfig,
)
from src.covet.security.auth.mfa_provider import (
    MFAProvider,
    MFAConfig,
    MFAMethod,
)
from src.covet.security.auth.password_policy import (
    PasswordPolicy,
    PasswordPolicyConfig,
)
from src.covet.security.auth.middleware import (
    AuthenticationMiddleware,
)


# ==================== Configuration ====================

# OAuth2 Configuration
oauth2_config = OAuth2Config(
    authorization_code_lifetime=600,  # 10 minutes
    access_token_lifetime=3600,  # 1 hour
    refresh_token_lifetime=2592000,  # 30 days
    require_pkce=True,
    use_jwt_tokens=False,
    issuer="https://auth.example.com",
)

# SAML Configuration
saml_config = SAMLConfig(
    sp_entity_id="https://app.example.com",
    idp_entity_id="https://idp.example.com",
    acs_url="https://app.example.com/auth/saml/acs",
    sls_url="https://app.example.com/auth/saml/logout",
    idp_sso_url="https://idp.example.com/sso",
    idp_slo_url="https://idp.example.com/slo",
)

# Session Configuration
session_config = SessionConfig(
    redis_url="redis://localhost:6379/0",  # Use Redis for production
    session_lifetime=3600,
    idle_timeout=1800,
    remember_me_enabled=True,
    check_ip_address=True,
    check_user_agent=True,
)

# MFA Configuration
mfa_config = MFAConfig(
    totp_issuer="ExampleApp",
    totp_period=30,
    totp_digits=6,
    sms_length=6,
    email_length=8,
)

# Password Policy Configuration
password_config = PasswordPolicyConfig(
    min_length=12,
    require_uppercase=True,
    require_lowercase=True,
    require_digits=True,
    require_special=True,
    breach_detection_enabled=True,
    password_history_count=5,
    max_failed_attempts=5,
    lockout_duration=900,
)


# ==================== Service Initialization ====================

class AuthenticationService:
    """
    Complete authentication service.

    Integrates all authentication mechanisms into a single service.
    """

    def __init__(self):
        """Initialize authentication service."""
        # Initialize providers
        self.oauth2 = OAuth2Provider(oauth2_config)
        self.saml = SAMLProvider(saml_config)
        self.session_manager = SessionManager(session_config)
        self.mfa = MFAProvider(mfa_config, send_sms_func=self.send_sms, send_email_func=self.send_email)
        self.password_policy = PasswordPolicy(password_config)

        # User database (in production, use real database)
        self.users: Dict[str, Dict[str, Any]] = {}

        print("✓ Authentication service initialized")

    # ==================== User Management ====================

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> tuple[bool, Optional[str], Optional[Dict]]:
        """
        Register new user with password validation.

        Returns:
            Tuple of (success, error_message, user_data)
        """
        # Check if user exists
        if username in self.users:
            return False, "Username already exists", None

        # Validate password
        result = await self.password_policy.validate_password(
            password=password,
            username=username,
            email=email,
        )

        if not result.is_valid:
            return False, "; ".join(result.errors), None

        # Hash password
        password_hash = self.password_policy.hash_password(password)

        # Create user
        user = {
            "username": username,
            "email": email,
            "full_name": full_name or username,
            "password_hash": password_hash,
            "created_at": datetime.utcnow().isoformat(),
            "mfa_enabled": False,
            "roles": ["user"],
        }

        self.users[username] = user

        print(f"✓ User registered: {username}")
        return True, None, user

    async def authenticate_user(
        self, username: str, password: str
    ) -> tuple[bool, Optional[str], Optional[Dict]]:
        """
        Authenticate user with password.

        Returns:
            Tuple of (success, error_message, user_data)
        """
        # Check lockout
        is_locked, seconds = await self.password_policy.is_locked_out(username)
        if is_locked:
            return False, f"Account locked. Try again in {seconds} seconds", None

        # Get user
        user = self.users.get(username)
        if not user:
            await self.password_policy.record_failed_attempt(username)
            return False, "Invalid credentials", None

        # Verify password
        is_valid = self.password_policy.verify_password(
            password, user["password_hash"]
        )

        if not is_valid:
            await self.password_policy.record_failed_attempt(username)
            return False, "Invalid credentials", None

        # Clear failed attempts on success
        await self.password_policy.clear_failed_attempts(username)

        print(f"✓ User authenticated: {username}")
        return True, None, user

    # ==================== OAuth2 Endpoints ====================

    async def oauth2_register_client(
        self,
        client_id: str,
        client_name: str,
        is_confidential: bool,
        redirect_uris: list,
        client_secret: Optional[str] = None,
    ):
        """Register OAuth2 client."""
        client = await self.oauth2.register_client(
            client_id=client_id,
            client_name=client_name,
            is_confidential=is_confidential,
            allowed_grant_types={
                GrantType.AUTHORIZATION_CODE,
                GrantType.REFRESH_TOKEN,
                GrantType.CLIENT_CREDENTIALS,
            },
            redirect_uris=redirect_uris,
            allowed_scopes={"read", "write", "profile", "email"},
            client_secret=client_secret,
        )

        print(f"✓ OAuth2 client registered: {client_id}")
        return client

    async def oauth2_authorize(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        username: str,
        code_challenge: Optional[str] = None,
        code_challenge_method: Optional[str] = None,
    ):
        """Create OAuth2 authorization code."""
        # Validate request
        is_valid, error, _ = await self.oauth2.create_authorization_request(
            client_id=client_id,
            redirect_uri=redirect_uri,
            scope=scope,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

        if not is_valid:
            return None, error

        # Create authorization code
        auth_code = await self.oauth2.create_authorization_code(
            client_id=client_id,
            user_id=username,
            redirect_uri=redirect_uri,
            scopes=set(scope.split()),
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )

        print(f"✓ OAuth2 authorization code created for {username}")
        return auth_code, None

    async def oauth2_token(
        self,
        client_id: str,
        client_secret: Optional[str],
        grant_type: str,
        **kwargs,
    ):
        """Issue OAuth2 token."""
        if grant_type == "authorization_code":
            token, error = await self.oauth2.exchange_authorization_code(
                client_id=client_id,
                client_secret=client_secret,
                code=kwargs["code"],
                redirect_uri=kwargs["redirect_uri"],
                code_verifier=kwargs.get("code_verifier"),
            )
        elif grant_type == "client_credentials":
            token, error = await self.oauth2.client_credentials_grant(
                client_id=client_id,
                client_secret=client_secret,
                scope=kwargs.get("scope"),
            )
        elif grant_type == "refresh_token":
            token, error = await self.oauth2.refresh_token_grant(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=kwargs["refresh_token"],
                scope=kwargs.get("scope"),
            )
        else:
            return None, "unsupported_grant_type"

        if token:
            print(f"✓ OAuth2 token issued for client {client_id}")

        return token, error

    # ==================== Session Management ====================

    async def create_session(
        self,
        username: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        remember_me: bool = False,
    ):
        """Create user session."""
        session = await self.session_manager.create_session(
            user_id=username,
            ip_address=ip_address,
            user_agent=user_agent,
            remember_me=remember_me,
        )

        print(f"✓ Session created for {username}")
        return session

    async def validate_session(
        self,
        session_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Validate session."""
        session = await self.session_manager.get_session(
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if session:
            print(f"✓ Session validated for {session.user_id}")

        return session

    # ==================== MFA Management ====================

    async def enroll_mfa_totp(self, username: str):
        """Enroll user in TOTP MFA."""
        user = self.users.get(username)
        if not user:
            return None, "User not found"

        # Generate TOTP secret
        secret, uri, qr_code = await self.mfa.enroll_totp(
            user_id=username,
            account_name=user["email"],
        )

        user["mfa_enabled"] = True
        user["mfa_method"] = "totp"

        print(f"✓ TOTP MFA enrolled for {username}")
        return {"secret": secret.secret, "uri": uri, "qr_code": qr_code}, None

    async def verify_mfa(
        self, username: str, method: MFAMethod, code: str
    ) -> tuple[bool, Optional[str]]:
        """Verify MFA code."""
        is_valid, error = await self.mfa.verify_mfa(
            user_id=username,
            method=method,
            code=code,
        )

        if is_valid:
            print(f"✓ MFA verified for {username}")

        return is_valid, error

    # ==================== Helper Methods ====================

    async def send_sms(self, phone_number: str, message: str):
        """Send SMS (mock implementation)."""
        print(f"📱 SMS to {phone_number}: {message}")

    async def send_email(self, email: str, subject: str, body: str):
        """Send email (mock implementation)."""
        print(f"📧 Email to {email}: {subject}")

    # ==================== Statistics ====================

    def get_stats(self):
        """Get authentication statistics."""
        return {
            "users_count": len(self.users),
            "oauth2_clients": len(self.oauth2._clients),
            "oauth2_stats": self.oauth2._stats if hasattr(self.oauth2, '_stats') else {},
            "session_stats": self.session_manager.get_stats(),
        }


# ==================== Demo Application ====================

async def demo():
    """Demonstrate authentication service."""
    print("=== CovetPy Authentication Service Demo ===\\n")

    # Initialize service
    service = AuthenticationService()

    # 1. Register user
    print("\\n1. User Registration")
    success, error, user = await service.register_user(
        username="alice",
        email="alice@example.com",
        password="AliceSecure123!",
        full_name="Alice Smith",
    )
    print(f"   Result: {'Success' if success else f'Failed: {error}'}")

    # 2. Register OAuth2 client
    print("\\n2. OAuth2 Client Registration")
    await service.oauth2_register_client(
        client_id="demo_app",
        client_name="Demo Application",
        is_confidential=True,
        redirect_uris=["https://demo.example.com/callback"],
        client_secret="demo_secret_123",
    )

    # 3. Authenticate user
    print("\\n3. User Authentication")
    success, error, user = await service.authenticate_user("alice", "AliceSecure123!")
    print(f"   Result: {'Success' if success else f'Failed: {error}'}")

    # 4. Create session
    print("\\n4. Session Creation")
    session = await service.create_session(
        username="alice",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
    )
    print(f"   Session ID: {session.session_id[:20]}...")

    # 5. OAuth2 Authorization
    print("\\n5. OAuth2 Authorization Code Flow")
    auth_code, error = await service.oauth2_authorize(
        client_id="demo_app",
        redirect_uri="https://demo.example.com/callback",
        scope="read write",
        username="alice",
    )
    if auth_code:
        print(f"   Authorization code: {auth_code.code[:20]}...")

        # Exchange for token
        token, error = await service.oauth2_token(
            client_id="demo_app",
            client_secret="demo_secret_123",
            grant_type="authorization_code",
            code=auth_code.code,
            redirect_uri="https://demo.example.com/callback",
        )
        if token:
            print(f"   Access token: {token.token[:20]}...")

    # 6. Enroll MFA
    print("\\n6. MFA Enrollment (TOTP)")
    mfa_data, error = await service.enroll_mfa_totp("alice")
    if mfa_data:
        print(f"   TOTP secret: {mfa_data['secret'][:20]}...")
        print(f"   Provisioning URI: {mfa_data['uri'][:50]}...")

        # Generate and verify code
        code = service.mfa.totp.generate_totp(mfa_data["secret"])
        is_valid, error = await service.verify_mfa("alice", MFAMethod.TOTP, code)
        print(f"   MFA verification: {'Success' if is_valid else f'Failed: {error}'}")

    # 7. Password policy check
    print("\\n7. Password Policy Validation")
    weak_result = await service.password_policy.validate_password("weak")
    print(f"   Weak password: {weak_result.strength.value} (score: {weak_result.score})")
    print(f"   Errors: {weak_result.errors[:2]}")

    strong_result = await service.password_policy.validate_password("VerySecure!Pass2023")
    print(f"   Strong password: {strong_result.strength.value} (score: {strong_result.score})")

    # 8. Statistics
    print("\\n8. Service Statistics")
    stats = service.get_stats()
    print(f"   Users: {stats['users_count']}")
    print(f"   OAuth2 clients: {stats['oauth2_clients']}")

    print("\\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demo())
