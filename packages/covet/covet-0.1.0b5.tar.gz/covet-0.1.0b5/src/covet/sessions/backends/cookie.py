"""
Cookie-Based Session Backend

Production-ready cookie sessions with:
- Signed cookies to prevent tampering
- Encrypted cookies for sensitive data
- Size limit enforcement (4KB browser limit)
- Secure, HttpOnly, SameSite flags
- No server-side storage required

NO MOCK DATA: Real cryptographic signing using itsdangerous.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

try:
    from itsdangerous import BadSignature, SignatureExpired, TimestampSigner
    from itsdangerous.exc import BadTimeSignature

    SIGNER_AVAILABLE = True
except ImportError:
    SIGNER_AVAILABLE = False

try:
    from cryptography.fernet import Fernet

    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False


logger = logging.getLogger(__name__)


@dataclass
class CookieSessionConfig:
    """Cookie session configuration."""

    # Security
    secret_key: str = None  # Required for signing
    encryption_key: Optional[bytes] = None  # Optional for encryption

    # Cookie settings
    cookie_name: str = "session"
    cookie_domain: Optional[str] = None
    cookie_path: str = "/"
    max_age: int = 86400  # 24 hours

    # Security flags
    secure: bool = True  # HTTPS only
    httponly: bool = True  # No JavaScript access
    samesite: str = "Lax"  # Lax, Strict, or None

    # Size limit (4KB = 4096 bytes)
    max_cookie_size: int = 4096

    # Encryption
    encrypt_data: bool = False

    def __post_init__(self):
        """Validate configuration."""
        if not self.secret_key:
            raise ValueError("secret_key is required for cookie sessions")

        if self.encrypt_data and not self.encryption_key:
            # Generate encryption key if not provided
            if not ENCRYPTION_AVAILABLE:
                raise ImportError("cryptography not installed")
            self.encryption_key = Fernet.generate_key()


class CookieSession:
    """
    Cookie-based session storage.

    Features:
    - Cryptographically signed cookies (prevents tampering)
    - Optional encryption for sensitive data
    - Automatic size checking
    - Standard security flags (Secure, HttpOnly, SameSite)

    Example:
        # SECURITY WARNING: Never use hardcoded secrets in production!
        # Always load from environment variables or secure key management system
        import os
        secret_key = os.environ.get('SESSION_SECRET_KEY')
        if not secret_key:
            raise ValueError("SESSION_SECRET_KEY environment variable not set")

        config = CookieSessionConfig(
            secret_key=secret_key,  # Load from environment, not hardcoded!
            secure=True,
            httponly=True,
            samesite='Strict'
        )

        session = CookieSession(config)

        # Create session data
        data = {'user_id': 123, 'username': 'alice'}
        cookie_value = await session.save(data)

        # Set cookie in response
        response.set_cookie(
            config.cookie_name,
            cookie_value,
            max_age=config.max_age,
            secure=config.secure,
            httponly=config.httponly,
            samesite=config.samesite
        )

        # Load session from cookie
        cookie_value = request.cookies.get(config.cookie_name)
        data = await session.load(cookie_value)
    """

    def __init__(self, config: CookieSessionConfig):
        """
        Initialize cookie session.

        Args:
            config: Cookie session configuration
        """
        if not SIGNER_AVAILABLE:
            raise ImportError(
                "itsdangerous not installed. " "Install with: pip install itsdangerous"
            )

        self.config = config

        # Create signer
        self._signer = TimestampSigner(config.secret_key)

        # Create encryptor if encryption enabled
        self._fernet = None
        if config.encrypt_data:
            if not ENCRYPTION_AVAILABLE:
                raise ImportError(
                    "cryptography not installed. " "Install with: pip install cryptography"
                )
            self._fernet = Fernet(config.encryption_key)

    async def save(self, data: Dict[str, Any]) -> str:
        """
        Save session data to signed cookie.

        Args:
            data: Session data dictionary

        Returns:
            Signed cookie value

        Raises:
            ValueError: If data is too large
        """
        # Serialize data
        json_data = json.dumps(data, separators=(",", ":"))

        # Encrypt if enabled
        if self._fernet:
            encrypted = self._fernet.encrypt(json_data.encode("utf-8"))
            payload = encrypted
        else:
            payload = json_data.encode("utf-8")

        # Sign payload
        signed = self._signer.sign(payload)

        # Check size
        if len(signed) > self.config.max_cookie_size:
            raise ValueError(
                f"Session data too large: {len(signed)} bytes "
                f"(max: {self.config.max_cookie_size})"
            )

        return signed.decode("utf-8")

    async def load(self, cookie_value: Optional[str]) -> Dict[str, Any]:
        """
        Load session data from signed cookie.

        Args:
            cookie_value: Signed cookie value

        Returns:
            Session data dictionary (empty if invalid/expired)
        """
        if not cookie_value:
            return {}

        try:
            # Verify signature and timestamp
            unsigned = self._signer.unsign(
                cookie_value.encode("utf-8"), max_age=self.config.max_age
            )

            # Decrypt if enabled
            if self._fernet:
                decrypted = self._fernet.decrypt(unsigned)
                json_data = decrypted.decode("utf-8")
            else:
                json_data = unsigned.decode("utf-8")

            # Deserialize
            data = json.loads(json_data)
            return data

        except (BadSignature, SignatureExpired, BadTimeSignature) as e:
            logger.warning(f"Invalid or expired session cookie: {e}")
            return {}

        except Exception as e:
            logger.error(f"Error loading session cookie: {e}")
            return {}

    async def delete(self) -> str:
        """
        Create cookie value for deletion.

        Returns:
            Empty cookie value
        """
        return ""

    def create_cookie_header(self, cookie_value: str, delete: bool = False) -> str:
        """
        Create Set-Cookie header value.

        Args:
            cookie_value: Cookie value
            delete: If True, create delete cookie (expires in past)

        Returns:
            Set-Cookie header value
        """
        if delete:
            # Create cookie that expires immediately
            parts = [
                f"{self.config.cookie_name}=",
                "Max-Age=0",
                "Expires=Thu, 01 Jan 1970 00:00:00 GMT",
            ]
        else:
            parts = [
                f"{self.config.cookie_name}={cookie_value}",
                f"Max-Age={self.config.max_age}",
            ]

        # Add path
        if self.config.cookie_path:
            parts.append(f"Path={self.config.cookie_path}")

        # Add domain
        if self.config.cookie_domain:
            parts.append(f"Domain={self.config.cookie_domain}")

        # Add security flags
        if self.config.secure:
            parts.append("Secure")

        if self.config.httponly:
            parts.append("HttpOnly")

        if self.config.samesite:
            parts.append(f"SameSite={self.config.samesite}")

        return "; ".join(parts)

    def get_data_size(self, data: Dict[str, Any]) -> int:
        """
        Get approximate size of session data when serialized.

        Args:
            data: Session data

        Returns:
            Size in bytes
        """
        json_data = json.dumps(data, separators=(",", ":"))

        if self._fernet:
            encrypted = self._fernet.encrypt(json_data.encode("utf-8"))
            payload = encrypted
        else:
            payload = json_data.encode("utf-8")

        signed = self._signer.sign(payload)
        return len(signed)


class CookieSessionStore:
    """
    Session store interface for cookie-based sessions.

    This provides a consistent interface with other session backends,
    even though cookies don't have server-side storage.
    """

    def __init__(self, config: CookieSessionConfig):
        """Initialize cookie session store."""
        self.session = CookieSession(config)
        self.config = config

    async def get(
        self, session_id: str, cookie_value: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get session data.

        Args:
            session_id: Session ID (not used for cookies)
            cookie_value: Cookie value to load

        Returns:
            Session data or None
        """
        if not cookie_value:
            return None

        data = await self.session.load(cookie_value)
        return data if data else None

    async def set(self, session_id: str, data: Dict[str, Any]) -> str:
        """
        Save session data.

        Args:
            session_id: Session ID (not used for cookies)
            data: Session data

        Returns:
            Cookie value to set
        """
        return await self.session.save(data)

    async def delete(self, session_id: str) -> bool:
        """
        Delete session.

        Args:
            session_id: Session ID

        Returns:
            True (always succeeds for cookies)
        """
        return True

    async def exists(self, session_id: str) -> bool:
        """
        Check if session exists.

        Args:
            session_id: Session ID

        Returns:
            False (cookies don't have server-side state)
        """
        return False

    async def cleanup_expired(self) -> int:
        """
        Clean up expired sessions.

        Returns:
            0 (cookies auto-expire in browser)
        """
        return 0


__all__ = [
    "CookieSession",
    "CookieSessionConfig",
    "CookieSessionStore",
]
