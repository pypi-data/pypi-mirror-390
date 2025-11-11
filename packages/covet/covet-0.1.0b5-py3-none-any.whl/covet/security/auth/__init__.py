"""
CovetPy Authentication System

Production-grade authentication with OAuth2, SAML, LDAP, and MFA support.

This package provides enterprise-ready authentication mechanisms:
- OAuth2 2.0 (RFC 6749, RFC 7636 PKCE, RFC 7662, RFC 7009)
- SAML 2.0 Service Provider and Identity Provider
- LDAP/Active Directory authentication
- Multi-Factor Authentication (TOTP, SMS, Email, Backup Codes)
- Session Management with Redis backend
- Password Policy Engine with breach detection
- Authentication middleware for ASGI applications

All implementations follow security best practices and relevant RFCs.
"""

from .ldap_provider import (
    LDAPConfig,
    LDAPConnection,
    LDAPGroup,
    LDAPProvider,
    LDAPUser,
)
from .mfa_provider import (
    BackupCodesProvider,
    EmailOTPProvider,
    MFAConfig,
    MFAMethod,
    MFAProvider,
    SMSOTPProvider,
    TOTPProvider,
)
from .middleware import (
    AuthenticationMiddleware,
    OAuth2Middleware,
    SAMLMiddleware,
    SessionMiddleware,
)
from .oauth2_provider import (
    GrantType,
    OAuth2AuthorizationCode,
    OAuth2Client,
    OAuth2Config,
    OAuth2Provider,
    OAuth2Token,
    PKCEChallenge,
)
from .oauth2_provider import TokenType as OAuth2TokenType
from .password_policy import (
    BreachDetector,
    PasswordPolicy,
    PasswordPolicyConfig,
    PasswordStrength,
    PasswordValidator,
)
from .saml_provider import (
    SAMLAssertion,
    SAMLBinding,
    SAMLConfig,
    SAMLProvider,
    SAMLRequest,
    SAMLResponse,
)
from .session_manager import (
    RedisSessionStore,
    Session,
    SessionConfig,
    SessionManager,
    SessionStore,
)

__all__ = [
    # OAuth2
    "OAuth2Provider",
    "OAuth2Client",
    "OAuth2Token",
    "OAuth2AuthorizationCode",
    "GrantType",
    "OAuth2TokenType",
    "PKCEChallenge",
    "OAuth2Config",
    # SAML
    "SAMLProvider",
    "SAMLConfig",
    "SAMLAssertion",
    "SAMLRequest",
    "SAMLResponse",
    "SAMLBinding",
    # LDAP
    "LDAPProvider",
    "LDAPConfig",
    "LDAPUser",
    "LDAPGroup",
    "LDAPConnection",
    # MFA
    "MFAProvider",
    "TOTPProvider",
    "SMSOTPProvider",
    "EmailOTPProvider",
    "BackupCodesProvider",
    "MFAConfig",
    "MFAMethod",
    # Session Management
    "SessionManager",
    "Session",
    "SessionConfig",
    "SessionStore",
    "RedisSessionStore",
    # Password Policy
    "PasswordPolicy",
    "PasswordPolicyConfig",
    "PasswordStrength",
    "PasswordValidator",
    "BreachDetector",
    # Middleware
    "AuthenticationMiddleware",
    "OAuth2Middleware",
    "SAMLMiddleware",
    "SessionMiddleware",
]

__version__ = "1.0.0"
