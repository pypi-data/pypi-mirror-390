"""
OAuth2 Authentication System

Production-ready OAuth2 implementation with:
- Multiple provider support (Google, GitHub, Microsoft, etc.)
- PKCE (Proof Key for Code Exchange) for security
- State parameter for CSRF protection
- Secure token handling and storage
- User profile mapping and synchronization
"""

import base64
import hashlib
import json
import secrets
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol

import httpx

from .exceptions import AuthException, OAuth2Error
from .models import User


class OAuth2Provider(Enum):
    """Supported OAuth2 providers"""

    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    FACEBOOK = "facebook"
    DISCORD = "discord"


@dataclass
class OAuth2Config:
    """OAuth2 provider configuration"""

    provider: OAuth2Provider
    client_id: str
    client_secret: str

    # URLs (can be auto-configured for known providers)
    authorization_url: Optional[str] = None
    token_url: Optional[str] = None
    userinfo_url: Optional[str] = None

    # Scopes
    scopes: List[str] = field(default_factory=list)

    # Security settings
    use_pkce: bool = True  # Always use PKCE for security
    state_expires_minutes: int = 10

    # Redirect URI
    redirect_uri: str = ""


@dataclass
class OAuth2State:
    """OAuth2 state information for CSRF protection"""

    state: str
    code_verifier: Optional[str] = None  # For PKCE
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default_factory=lambda: datetime.utcnow() + timedelta(minutes=10))
    redirect_url: Optional[str] = None  # Where to redirect after auth

    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at


@dataclass
class OAuth2UserInfo:
    """User information from OAuth2 provider"""

    provider: OAuth2Provider
    provider_user_id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Dict[str, Any] = field(default_factory=dict)


class OAuth2StateStore:
    """In-memory OAuth2 state store"""

    def __init__(self):
        self._states: Dict[str, OAuth2State] = {}

    def store_state(self, state: OAuth2State) -> None:
        """Store OAuth2 state"""
        self._states[state.state] = state
        self._cleanup_expired()

    def get_state(self, state_key: str) -> Optional[OAuth2State]:
        """Get OAuth2 state"""
        self._cleanup_expired()
        return self._states.get(state_key)

    def remove_state(self, state_key: str) -> None:
        """Remove OAuth2 state"""
        self._states.pop(state_key, None)

    def _cleanup_expired(self) -> None:
        """Remove expired states"""
        expired_keys = [key for key, state in self._states.items() if state.is_expired()]
        for key in expired_keys:
            self._states.pop(key, None)


class PKCE:
    """PKCE (Proof Key for Code Exchange) implementation"""

    @staticmethod
    def generate_code_verifier() -> str:
        """Generate code verifier for PKCE"""
        # 43-128 characters, base64url-encoded
        random_bytes = secrets.token_bytes(32)
        return base64.urlsafe_b64encode(random_bytes).decode("utf-8").rstrip("=")

    @staticmethod
    def generate_code_challenge(code_verifier: str) -> str:
        """Generate code challenge from verifier using S256 method"""
        digest = hashlib.sha256(code_verifier.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")


class OAuth2Provider_:
    """Base OAuth2 provider implementation"""

    def __init__(self, config: OAuth2Config):
        self.config = config
        self._configure_provider_defaults()

    def _configure_provider_defaults(self):
        """Configure default URLs and scopes for known providers"""
        if self.config.provider == OAuth2Provider.GOOGLE:
            self.config.authorization_url = (
                self.config.authorization_url or "https://accounts.google.com/o/oauth2/auth"
            )
            self.config.token_url = self.config.token_url or "https://oauth2.googleapis.com/token"
            self.config.userinfo_url = (
                self.config.userinfo_url or "https://www.googleapis.com/oauth2/v2/userinfo"
            )
            if not self.config.scopes:
                self.config.scopes = ["openid", "email", "profile"]

        elif self.config.provider == OAuth2Provider.GITHUB:
            self.config.authorization_url = (
                self.config.authorization_url or "https://github.com/login/oauth/authorize"
            )
            self.config.token_url = (
                self.config.token_url or "https://github.com/login/oauth/access_token"
            )
            self.config.userinfo_url = self.config.userinfo_url or "https://api.github.com/user"
            if not self.config.scopes:
                self.config.scopes = ["user:email"]

        elif self.config.provider == OAuth2Provider.MICROSOFT:
            self.config.authorization_url = (
                self.config.authorization_url
                or "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
            )
            self.config.token_url = (
                self.config.token_url
                or "https://login.microsoftonline.com/common/oauth2/v2.0/token"
            )
            self.config.userinfo_url = (
                self.config.userinfo_url or "https://graph.microsoft.com/v1.0/me"
            )
            if not self.config.scopes:
                self.config.scopes = ["openid", "email", "profile"]

    def generate_authorization_url(self, state: OAuth2State) -> str:
        """Generate OAuth2 authorization URL"""
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "response_type": "code",
            "state": state.state,
        }

        # Add PKCE parameters
        if self.config.use_pkce and state.code_verifier:
            code_challenge = PKCE.generate_code_challenge(state.code_verifier)
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"

        # Provider-specific parameters
        if self.config.provider == OAuth2Provider.GOOGLE:
            params["access_type"] = "offline"
            params["prompt"] = "consent"

        query_string = urllib.parse.urlencode(params)
        return f"{self.config.authorization_url}?{query_string}"

    async def exchange_code_for_token(self, code: str, state: OAuth2State) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        data = {
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.config.redirect_uri,
        }

        # Add PKCE verifier
        if self.config.use_pkce and state.code_verifier:
            data["code_verifier"] = state.code_verifier

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    self.config.token_url, data=data, headers=headers, timeout=30.0
                )
                response.raise_for_status()

                token_data = response.json()

                if "error" in token_data:
                    raise OAuth2Error(
                        f"Token exchange failed: {token_data.get('error_description', token_data['error'])}",
                        token_data["error"],
                        self.config.provider.value,
                    )

                return token_data

            except httpx.HTTPError as e:
                raise OAuth2Error(
                    f"HTTP error during token exchange: {str(e)}",
                    "http_error",
                    self.config.provider.value,
                )
            except json.JSONDecodeError as e:
                raise OAuth2Error(
                    f"Invalid JSON response: {str(e)}",
                    "invalid_response",
                    self.config.provider.value,
                )

    async def get_user_info(self, access_token: str) -> OAuth2UserInfo:
        """Get user information using access token"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.config.userinfo_url, headers=headers, timeout=30.0)
                response.raise_for_status()

                user_data = response.json()

                # Parse user data based on provider
                if self.config.provider == OAuth2Provider.GOOGLE:
                    return self._parse_google_user_data(user_data)
                elif self.config.provider == OAuth2Provider.GITHUB:
                    return await self._parse_github_user_data(user_data, access_token)
                elif self.config.provider == OAuth2Provider.MICROSOFT:
                    return self._parse_microsoft_user_data(user_data)
                else:
                    return self._parse_generic_user_data(user_data)

            except httpx.HTTPError as e:
                raise OAuth2Error(
                    f"HTTP error getting user info: {str(e)}",
                    "http_error",
                    self.config.provider.value,
                )
            except json.JSONDecodeError as e:
                raise OAuth2Error(
                    f"Invalid JSON response: {str(e)}",
                    "invalid_response",
                    self.config.provider.value,
                )

    def _parse_google_user_data(self, data: Dict[str, Any]) -> OAuth2UserInfo:
        """Parse Google user data"""
        return OAuth2UserInfo(
            provider=self.config.provider,
            provider_user_id=data["id"],
            email=data.get("email", ""),
            username=data.get("email", "").split("@")[0],
            first_name=data.get("given_name"),
            last_name=data.get("family_name"),
            avatar_url=data.get("picture"),
            raw_data=data,
        )

    async def _parse_github_user_data(
        self, data: Dict[str, Any], access_token: str
    ) -> OAuth2UserInfo:
        """Parse GitHub user data"""
        # GitHub requires separate API call for email if not public
        email = data.get("email")
        if not email:
            email = await self._get_github_primary_email(access_token)

        return OAuth2UserInfo(
            provider=self.config.provider,
            provider_user_id=str(data["id"]),
            email=email or "",
            username=data.get("login"),
            first_name=data.get("name", "").split(" ")[0] if data.get("name") else None,
            last_name=(
                " ".join(data.get("name", "").split(" ")[1:])
                if data.get("name") and " " in data.get("name", "")
                else None
            ),
            avatar_url=data.get("avatar_url"),
            raw_data=data,
        )

    async def _get_github_primary_email(self, access_token: str) -> Optional[str]:
        """Get primary email from GitHub API"""
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.github.com/user/emails", headers=headers, timeout=30.0
                )
                response.raise_for_status()

                emails = response.json()
                for email in emails:
                    if email.get("primary") and email.get("verified"):
                        return email.get("email")

                return None

            except Exception:
                return None

    def _parse_microsoft_user_data(self, data: Dict[str, Any]) -> OAuth2UserInfo:
        """Parse Microsoft user data"""
        return OAuth2UserInfo(
            provider=self.config.provider,
            provider_user_id=data["id"],
            email=data.get("userPrincipalName") or data.get("mail", ""),
            username=(
                data.get("userPrincipalName", "").split("@")[0]
                if data.get("userPrincipalName")
                else None
            ),
            first_name=data.get("givenName"),
            last_name=data.get("surname"),
            avatar_url=None,  # Microsoft Graph requires separate call for photo
            raw_data=data,
        )

    def _parse_generic_user_data(self, data: Dict[str, Any]) -> OAuth2UserInfo:
        """Parse generic user data"""
        return OAuth2UserInfo(
            provider=self.config.provider,
            provider_user_id=str(data.get("id", "")),
            email=data.get("email", ""),
            username=data.get("username") or data.get("login"),
            first_name=data.get("first_name") or data.get("given_name"),
            last_name=data.get("last_name") or data.get("family_name"),
            avatar_url=data.get("avatar_url") or data.get("picture"),
            raw_data=data,
        )


class OAuth2Manager:
    """
    OAuth2 authentication manager
    """

    def __init__(self):
        self._providers: Dict[OAuth2Provider, OAuth2Provider_] = {}
        self._state_store = OAuth2StateStore()

    def add_provider(self, config: OAuth2Config) -> None:
        """Add OAuth2 provider"""
        provider = OAuth2Provider_(config)
        self._providers[config.provider] = provider

    def get_provider(self, provider_name: OAuth2Provider) -> Optional[OAuth2Provider_]:
        """Get OAuth2 provider"""
        return self._providers.get(provider_name)

    def create_authorization_url(
        self, provider_name: OAuth2Provider, redirect_url: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create OAuth2 authorization URL

        Returns:
            tuple: (authorization_url, state)
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise OAuth2Error(
                f"Provider {provider_name.value} not configured", "provider_not_found"
            )

        # Generate state and PKCE parameters
        state_value = secrets.token_urlsafe(32)
        code_verifier = PKCE.generate_code_verifier() if provider.config.use_pkce else None

        state = OAuth2State(
            state=state_value, code_verifier=code_verifier, redirect_url=redirect_url
        )

        # Store state
        self._state_store.store_state(state)

        # Generate authorization URL
        auth_url = provider.generate_authorization_url(state)

        return auth_url, state_value

    async def handle_callback(
        self, provider_name: OAuth2Provider, code: str, state: str
    ) -> OAuth2UserInfo:
        """
        Handle OAuth2 callback

        Returns:
            OAuth2UserInfo object
        """
        provider = self.get_provider(provider_name)
        if not provider:
            raise OAuth2Error(
                f"Provider {provider_name.value} not configured", "provider_not_found"
            )

        # Verify state
        stored_state = self._state_store.get_state(state)
        if not stored_state:
            raise OAuth2Error("Invalid or expired state parameter", "invalid_state")

        # Remove state to prevent reuse
        self._state_store.remove_state(state)

        try:
            # Exchange code for token
            token_data = await provider.exchange_code_for_token(code, stored_state)

            # Get user information
            access_token = token_data["access_token"]
            user_info = await provider.get_user_info(access_token)

            return user_info

        except OAuth2Error:
            raise
        except Exception as e:
            raise OAuth2Error(
                f"OAuth2 callback failed: {str(e)}",
                "callback_error",
                provider_name.value,
            )

    def get_configured_providers(self) -> List[OAuth2Provider]:
        """Get list of configured providers"""
        return list(self._providers.keys())


# Global OAuth2 manager instance
_oauth2_manager_instance: Optional[OAuth2Manager] = None


def get_oauth2_manager() -> OAuth2Manager:
    """Get OAuth2 manager singleton instance"""
    global _oauth2_manager_instance
    if _oauth2_manager_instance is None:
        _oauth2_manager_instance = OAuth2Manager()
    return _oauth2_manager_instance


def configure_oauth2_provider(
    provider: OAuth2Provider,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    scopes: Optional[List[str]] = None,
) -> None:
    """Configure OAuth2 provider"""
    config = OAuth2Config(
        provider=provider,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scopes=scopes or [],
    )

    manager = get_oauth2_manager()
    manager.add_provider(config)
