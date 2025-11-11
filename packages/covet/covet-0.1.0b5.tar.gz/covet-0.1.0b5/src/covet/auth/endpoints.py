"""
Authentication API Endpoints

Secure REST API endpoints for:
- User registration and login
- Password reset flow
- 2FA setup and verification
- OAuth2 authentication
- Session management
- User profile management
"""

import json
from dataclasses import asdict
from typing import Any, Callable, Dict, Optional

from ..core.http import Request, Response
from ..core.routing import Router
from .auth import AuthManager, get_auth_manager
from .exceptions import (
    AuthException,
    InvalidCredentialsError,
    PermissionDeniedError,
    TwoFactorRequiredError,
)
from .exceptions import to_dict as exception_to_dict
from .oauth2 import OAuth2Provider, get_oauth2_manager
from .two_factor import get_two_factor_auth


class AuthEndpoints:
    """
    Authentication API endpoints
    """

    def __init__(self, auth_manager: Optional[AuthManager] = None):
        self.auth_manager = auth_manager or get_auth_manager()
        self.two_factor_auth = get_two_factor_auth()
        self.oauth2_manager = get_oauth2_manager()
        self.router = Router()
        self._setup_routes()

    def _setup_routes(self):
        """Setup authentication routes"""
        # Authentication
        self.router.post("/auth/register", self.register)
        self.router.post("/auth/login", self.login)
        self.router.post("/auth/logout", self.logout)
        self.router.post("/auth/refresh", self.refresh_token)

        # Password management
        self.router.post("/auth/password/reset", self.initiate_password_reset)
        self.router.post("/auth/password/reset/confirm", self.confirm_password_reset)
        self.router.post("/auth/password/change", self.change_password)

        # Email verification
        self.router.post("/auth/email/verify", self.verify_email)
        self.router.post("/auth/email/resend", self.resend_verification)

        # Two-factor authentication
        self.router.post("/auth/2fa/setup", self.setup_2fa)
        self.router.post("/auth/2fa/verify", self.verify_2fa)
        self.router.post("/auth/2fa/disable", self.disable_2fa)
        self.router.post("/auth/2fa/backup-codes", self.generate_backup_codes)

        # OAuth2
        self.router.get("/auth/oauth2/{provider}/authorize", self.oauth2_authorize)
        self.router.post("/auth/oauth2/{provider}/callback", self.oauth2_callback)

        # User profile
        self.router.get("/auth/profile", self.get_profile)
        self.router.put("/auth/profile", self.update_profile)
        self.router.get("/auth/sessions", self.get_sessions)
        self.router.delete("/auth/sessions/{session_id}", self.delete_session)

    def register(self, request: Request) -> Response:
        """Register new user"""
        try:
            data = self._parse_json(request)

            # Validate required fields
            username = data.get("username", "").strip()
            email = data.get("email", "").strip().lower()
            password = data.get("password", "")
            first_name = data.get("first_name", "").strip()
            last_name = data.get("last_name", "").strip()

            if not all([username, email, password]):
                return self._error_response("Username, email, and password are required", 400)

            # Get client info
            ip_address = self._get_client_ip(request)

            # Register user
            result = self.auth_manager.register_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name or None,
                last_name=last_name or None,
                ip_address=ip_address,
            )

            if not result.success:
                return self._error_response(result.message, 400)

            response_data = {
                "message": result.message,
                "user": result.user.to_dict(),
                "requires_verification": result.verification_token is not None,
            }

            if result.verification_token:
                # In production, send email instead of returning token
                response_data["verification_token"] = result.verification_token

            return self._json_response(response_data, 201)

        except Exception as e:
            return self._handle_exception(e)

    def login(self, request: Request) -> Response:
        """User login"""
        try:
            data = self._parse_json(request)

            username_or_email = data.get("username_or_email", "").strip()
            password = data.get("password", "")
            remember_me = data.get("remember_me", False)

            if not username_or_email or not password:
                return self._error_response("Username/email and password are required", 400)

            # Get client info
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "")

            # Attempt login
            result = self.auth_manager.login(
                username_or_email=username_or_email,
                password=password,
                ip_address=ip_address,
                user_agent=user_agent,
                remember_me=remember_me,
            )

            if not result.success:
                if result.requires_2fa:
                    return self._json_response(
                        {
                            "requires_2fa": True,
                            "message": result.message,
                            "user_id": result.user.id,  # Temporary for 2FA verification
                        },
                        200,
                    )

                if result.requires_password_reset:
                    return self._error_response("Password reset required", 403)

                if result.lockout_until:
                    return self._error_response(
                        f"Account locked until {result.lockout_until.isoformat()}", 423
                    )

                return self._error_response(result.message, 401)

            # Successful login
            response_data = {
                "message": result.message,
                "user": result.user.to_dict(),
                "access_token": result.token_pair.access_token,
                "refresh_token": result.token_pair.refresh_token,
                "expires_at": result.token_pair.access_expires_at.isoformat(),
            }

            response = self._json_response(response_data)

            # Set session cookie
            if result.session_id:
                session_headers = self.auth_manager.session_manager.create_cookie_headers(
                    self.auth_manager.session_manager.get_session(result.session_id)
                )
                for header, value in session_headers.items():
                    response.headers[header] = value

            return response

        except Exception as e:
            return self._handle_exception(e)

    def verify_2fa(self, request: Request) -> Response:
        """Verify 2FA and complete login"""
        try:
            data = self._parse_json(request)

            user_id = data.get("user_id", "")
            totp_code = data.get("totp_code", "").strip()
            backup_code = data.get("backup_code", "").strip()
            remember_me = data.get("remember_me", False)

            if not user_id or (not totp_code and not backup_code):
                return self._error_response("User ID and TOTP/backup code required", 400)

            # Get user
            user = self.auth_manager.user_store.get_user_by_id(user_id)
            if not user:
                return self._error_response("Invalid user", 400)

            # Get client info
            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "")

            # Verify 2FA
            if totp_code:
                result = self.auth_manager.verify_2fa_and_complete_login(
                    user=user,
                    totp_code=totp_code,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    remember_me=remember_me,
                )
            else:
                # Verify backup code
                if self.two_factor_auth.verify_backup_code(user, backup_code, ip_address):
                    result = self.auth_manager.verify_2fa_and_complete_login(
                        user=user,
                        totp_code="000000",  # Dummy code since backup code verified
                        ip_address=ip_address,
                        user_agent=user_agent,
                        remember_me=remember_me,
                    )
                else:
                    return self._error_response("Invalid backup code", 401)

            if not result.success:
                return self._error_response(result.message, 401)

            # Successful 2FA verification
            response_data = {
                "message": result.message,
                "user": result.user.to_dict(),
                "access_token": result.token_pair.access_token,
                "refresh_token": result.token_pair.refresh_token,
                "expires_at": result.token_pair.access_expires_at.isoformat(),
            }

            response = self._json_response(response_data)

            # Set session cookie
            if result.session_id:
                session = self.auth_manager.session_manager.get_session(result.session_id)
                session_headers = self.auth_manager.session_manager.create_cookie_headers(session)
                for header, value in session_headers.items():
                    response.headers[header] = value

            return response

        except Exception as e:
            return self._handle_exception(e)

    def logout(self, request: Request) -> Response:
        """User logout"""
        try:
            # Get current user
            user = self._get_current_user(request)
            if not user:
                return self._error_response("Authentication required", 401)

            # Get tokens/sessions to revoke
            access_token = self._get_bearer_token(request)
            session_id = self._get_session_id(request)

            data = self._parse_json(request) if request.content else {}
            revoke_all_sessions = data.get("revoke_all_sessions", False)

            # Logout
            self.auth_manager.logout(
                user=user,
                session_id=session_id,
                access_token=access_token,
                revoke_all_sessions=revoke_all_sessions,
            )

            response_data = {"message": "Logged out successfully"}
            response = self._json_response(response_data)

            # Clear session cookie
            logout_headers = self.auth_manager.session_manager.create_logout_cookie_headers()
            for header, value in logout_headers.items():
                response.headers[header] = value

            return response

        except Exception as e:
            return self._handle_exception(e)

    def setup_2fa(self, request: Request) -> Response:
        """Setup 2FA for user"""
        try:
            user = self._get_current_user(request)
            if not user:
                return self._error_response("Authentication required", 401)

            if user.two_factor_enabled:
                return self._error_response("2FA is already enabled", 400)

            # Setup TOTP
            secret, provisioning_uri, qr_code = self.two_factor_auth.setup_totp(user)

            # Update user in store
            self.auth_manager.user_store.update_user(user)

            # Return setup information
            response_data = {
                "secret": secret,
                "provisioning_uri": provisioning_uri,
                # Base64 encode
                "qr_code": f"data:image/png;base64,{qr_code.decode('latin1')}",
                "backup_codes_count": self.two_factor_auth.get_backup_codes_count(user),
            }

            return self._json_response(response_data)

        except Exception as e:
            return self._handle_exception(e)

    def disable_2fa(self, request: Request) -> Response:
        """Disable 2FA for user"""
        try:
            user = self._get_current_user(request)
            if not user:
                return self._error_response("Authentication required", 401)

            data = self._parse_json(request)
            password = data.get("password", "")

            # Verify password before disabling 2FA
            if not user.verify_password(password):
                return self._error_response("Invalid password", 401)

            # Disable 2FA
            self.two_factor_auth.disable_totp(user)
            self.auth_manager.user_store.update_user(user)

            return self._json_response({"message": "2FA disabled successfully"})

        except Exception as e:
            return self._handle_exception(e)

    def initiate_password_reset(self, request: Request) -> Response:
        """Initiate password reset"""
        try:
            data = self._parse_json(request)
            email = data.get("email", "").strip().lower()

            if not email:
                return self._error_response("Email is required", 400)

            ip_address = self._get_client_ip(request)
            user_agent = request.headers.get("User-Agent", "")

            # Always return success to prevent email enumeration
            self.auth_manager.initiate_password_reset(email, ip_address, user_agent)

            return self._json_response(
                {"message": "If the email exists, a password reset link has been sent"}
            )

        except Exception as e:
            return self._handle_exception(e)

    def oauth2_authorize(self, request: Request) -> Response:
        """Initiate OAuth2 authorization"""
        try:
            provider_name = request.path_params.get("provider")
            if not provider_name:
                return self._error_response("Provider required", 400)

            try:
                provider = OAuth2Provider(provider_name)
            except ValueError:
                return self._error_response("Unsupported provider", 400)

            redirect_url = request.query_params.get("redirect_url")

            # Create authorization URL
            auth_url, state = self.oauth2_manager.create_authorization_url(provider, redirect_url)

            return self._json_response({"authorization_url": auth_url, "state": state})

        except Exception as e:
            return self._handle_exception(e)

    def oauth2_callback(self, request: Request) -> Response:
        """Handle OAuth2 callback"""
        try:
            provider_name = request.path_params.get("provider")
            if not provider_name:
                return self._error_response("Provider required", 400)

            try:
                OAuth2Provider(provider_name)
            except ValueError:
                return self._error_response("Unsupported provider", 400)

            data = self._parse_json(request)
            code = data.get("code", "")
            state = data.get("state", "")

            if not code or not state:
                return self._error_response("Code and state required", 400)

            # Handle OAuth2 callback
            # Note: This would be async in a real implementation
            # user_info = await self.oauth2_manager.handle_callback(provider,
            # code, state)

            # For now, return a placeholder response
            return self._json_response(
                {"message": "OAuth2 callback received", "provider": provider_name}
            )

        except Exception as e:
            return self._handle_exception(e)

    def get_profile(self, request: Request) -> Response:
        """Get user profile"""
        try:
            user = self._get_current_user(request)
            if not user:
                return self._error_response("Authentication required", 401)

            return self._json_response(
                {
                    "user": user.to_dict(),
                    "permissions": self.auth_manager.rbac_manager.get_user_permissions_list(
                        user.id
                    ),
                    "roles": self.auth_manager.rbac_manager.get_user_roles_list(user.id),
                }
            )

        except Exception as e:
            return self._handle_exception(e)

    def _parse_json(self, request: Request) -> Dict[str, Any]:
        """Parse JSON request body"""
        try:
            if hasattr(request, "json"):
                return request.json()
            else:
                content = request.content.decode("utf-8") if request.content else "{}"
                return json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise ValueError("Invalid JSON")

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For", "")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP", "")
        if real_ip:
            return real_ip

        # Fallback to remote address
        return getattr(request, "remote_addr", "127.0.0.1")

    def _get_bearer_token(self, request: Request) -> Optional[str]:
        """Extract bearer token from Authorization header"""
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]
        return None

    def _get_session_id(self, request: Request) -> Optional[str]:
        """Extract session ID from cookie"""
        cookies = getattr(request, "cookies", {})
        return cookies.get("session_id")

    def _get_current_user(self, request: Request) -> Optional:
        """Get current authenticated user"""
        # Try JWT token first
        token = self._get_bearer_token(request)
        if token:
            token_manager = self.auth_manager
            return token_manager.jwt_auth.verify_token(token)

        # Try session
        session_id = self._get_session_id(request)
        if session_id:
            self._get_client_ip(request)
            session = self.auth_manager.session_manager.get_session(session_id)
            if session:
                return self.auth_manager.user_store.get_user_by_id(session.user_id)

        return None

    def _json_response(self, data: Dict[str, Any], status_code: int = 200) -> Response:
        """Create JSON response"""
        return Response(
            content=json.dumps(data),
            status_code=status_code,
            headers={"Content-Type": "application/json"},
        )

    def _error_response(self, message: str, status_code: int) -> Response:
        """Create error response"""
        return self._json_response({"error": True, "message": message}, status_code)

    def _handle_exception(self, exception: Exception) -> Response:
        """Handle authentication exceptions"""
        if isinstance(exception, AuthException):
            return self._json_response(exception_to_dict(exception), exception.status_code)
        else:
            # Log unexpected exceptions in production
            return self._error_response("Internal server error", 500)


def create_auth_router(auth_manager: Optional[AuthManager] = None) -> Router:
    """Create authentication router"""
    endpoints = AuthEndpoints(auth_manager)
    return endpoints.router
