"""
Authorization ASGI Middleware

Production-ready ASGI middleware for automatic authorization enforcement.

Features:
- Automatic policy enforcement for routes
- Request context injection
- User permission loading
- Performance optimization with caching
- Configurable route exemptions
- Integration with JWT authentication

Usage:
    from covet.security.authz import AuthorizationMiddleware

    app = AuthorizationMiddleware(
        app,
        pdp=policy_decision_point,
        exempt_paths=['/health', '/metrics'],
        default_action='read'
    )
"""

import asyncio
import json
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set

from .policy_engine import DecisionStrategy, PolicyDecisionPoint
from .rbac import RBACManager


class AuthorizationMiddleware:
    """
    ASGI middleware for authorization.

    Automatically enforces authorization policies on HTTP requests.
    """

    def __init__(
        self,
        app: Callable,
        pdp: Optional[PolicyDecisionPoint] = None,
        rbac_manager: Optional[RBACManager] = None,
        exempt_paths: Optional[List[str]] = None,
        exempt_patterns: Optional[List[str]] = None,
        optional_paths: Optional[List[str]] = None,
        default_action: str = "access",
        strategy: DecisionStrategy = DecisionStrategy.RBAC_FIRST,
        enable_audit: bool = True,
    ):
        """
        Initialize authorization middleware.

        Args:
            app: ASGI application
            pdp: Policy decision point (created if None)
            rbac_manager: RBAC manager (created if None)
            exempt_paths: Paths that don't require authorization
            exempt_patterns: Path patterns to exempt (regex)
            optional_paths: Paths where authorization is optional
            default_action: Default action if not specified
            strategy: Authorization strategy
            enable_audit: Enable audit logging
        """
        self.app = app
        self.pdp = pdp or PolicyDecisionPoint(strategy=strategy)
        self.rbac_manager = rbac_manager or RBACManager()
        self.exempt_paths = set(
            exempt_paths or ["/health", "/metrics", "/docs", "/openapi.json", "/favicon.ico"]
        )
        self.exempt_patterns = [re.compile(pattern) for pattern in (exempt_patterns or [])]
        self.optional_paths = set(optional_paths or [])
        self.default_action = default_action
        self.enable_audit = enable_audit

        # Performance metrics
        self._metrics = {
            "total_requests": 0,
            "authorized_requests": 0,
            "denied_requests": 0,
            "exempt_requests": 0,
            "total_time_ms": 0.0,
        }

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()
        path = scope.get("path", "/")
        method = scope.get("method", "GET")

        # Update metrics
        self._metrics["total_requests"] += 1

        # Check if path is exempt
        if self._is_exempt(path):
            self._metrics["exempt_requests"] += 1
            await self.app(scope, receive, send)
            return

        # Check if authorization is optional
        optional = path in self.optional_paths

        # Get user from scope (should be set by authentication middleware)
        user = scope.get("user")

        if not user:
            if optional:
                # Continue without authorization
                await self.app(scope, receive, send)
                return
            else:
                # Return 401 Unauthorized
                await self._send_error(
                    send, status=401, error="unauthorized", message="Authentication required"
                )
                return

        # Extract user ID
        user_id = str(user.get("id") or user.get("user_id") or user.get("sub"))

        # Determine resource type and action from path and method
        resource_type, action = self._extract_resource_and_action(path, method)

        # Evaluate authorization
        try:
            decision = await self.pdp.evaluate(
                user_id=user_id,
                resource_type=resource_type,
                resource_id="*",  # Route-level authorization
                action=action,
                user_attributes=user,
            )

            if not decision.allowed:
                # Access denied
                self._metrics["denied_requests"] += 1
                await self._send_error(
                    send, status=403, error="forbidden", message=f"Access denied: {decision.reason}"
                )
                return

            # Access granted
            self._metrics["authorized_requests"] += 1

            # Inject authorization decision into scope
            scope["authz_decision"] = decision
            scope["authz_context"] = {
                "user_id": user_id,
                "resource_type": resource_type,
                "action": action,
                "decision": decision.to_dict(),
            }

            # Update timing metrics
            elapsed_ms = (time.time() - start_time) * 1000
            self._metrics["total_time_ms"] += elapsed_ms

            # Call application
            await self.app(scope, receive, send)

        except Exception as e:
            # Authorization error
            await self._send_error(
                send,
                status=500,
                error="authorization_error",
                message=f"Authorization failed: {str(e)}",
            )

    def _is_exempt(self, path: str) -> bool:
        """
        Check if path is exempt from authorization.

        Args:
            path: Request path

        Returns:
            True if exempt
        """
        # Check exact matches
        if path in self.exempt_paths:
            return True

        # Check patterns
        for pattern in self.exempt_patterns:
            if pattern.match(path):
                return True

        return False

    def _extract_resource_and_action(self, path: str, method: str) -> tuple[str, str]:
        """
        Extract resource type and action from path and method.

        Args:
            path: Request path
            method: HTTP method

        Returns:
            Tuple of (resource_type, action)
        """
        # Remove leading/trailing slashes
        path = path.strip("/")

        # Split path into parts
        parts = path.split("/")

        # Extract resource type (usually first part)
        resource_type = parts[0] if parts else "unknown"

        # Map HTTP method to action
        method_to_action = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
            "HEAD": "read",
            "OPTIONS": "read",
        }

        action = method_to_action.get(method, self.default_action)

        return resource_type, action

    async def _send_error(self, send: Callable, status: int, error: str, message: str):
        """
        Send error response.

        Args:
            send: ASGI send callable
            status: HTTP status code
            error: Error type
            message: Error message
        """
        body = {
            "type": f"https://errors.covetpy.dev/{error}",
            "title": "Authorization Error" if status == 403 else "Authentication Error",
            "status": status,
            "detail": message,
        }

        await send(
            {
                "type": "http.response.start",
                "status": status,
                "headers": [
                    [b"content-type", b"application/json; charset=utf-8"],
                ],
            }
        )

        await send(
            {
                "type": "http.response.body",
                "body": json.dumps(body).encode("utf-8"),
            }
        )

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get middleware metrics.

        Returns:
            Metrics dictionary
        """
        total = self._metrics["total_requests"]
        if total > 0:
            avg_time = self._metrics["total_time_ms"] / total
            auth_rate = (self._metrics["authorized_requests"] / total) * 100
            deny_rate = (self._metrics["denied_requests"] / total) * 100
            exempt_rate = (self._metrics["exempt_requests"] / total) * 100
        else:
            avg_time = 0
            auth_rate = 0
            deny_rate = 0
            exempt_rate = 0

        return {
            "total_requests": total,
            "authorized_requests": self._metrics["authorized_requests"],
            "denied_requests": self._metrics["denied_requests"],
            "exempt_requests": self._metrics["exempt_requests"],
            "authorization_rate": f"{auth_rate:.2f}%",
            "denial_rate": f"{deny_rate:.2f}%",
            "exemption_rate": f"{exempt_rate:.2f}%",
            "average_time_ms": f"{avg_time:.2f}",
        }


class PermissionLoaderMiddleware:
    """
    ASGI middleware to load user permissions into request context.

    Loads user permissions from RBAC system and injects into scope.
    """

    def __init__(self, app: Callable, rbac_manager: Optional[RBACManager] = None):
        """
        Initialize permission loader middleware.

        Args:
            app: ASGI application
            rbac_manager: RBAC manager
        """
        self.app = app
        self.rbac_manager = rbac_manager or RBACManager()

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable):
        """ASGI interface."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get user from scope
        user = scope.get("user")

        if user:
            user_id = str(user.get("id") or user.get("user_id") or user.get("sub"))

            # Load user permissions
            permissions = await self.rbac_manager.get_user_permissions(user_id)

            # Load user roles
            roles = await self.rbac_manager.get_user_roles(user_id)

            # Inject into user dict
            user["permissions"] = list(permissions)
            user["roles"] = [role.name for role in roles]
            user["role_objects"] = roles

            # Update scope
            scope["user"] = user
            scope["user_permissions"] = permissions
            scope["user_roles"] = [role.name for role in roles]

        # Call application
        await self.app(scope, receive, send)


__all__ = [
    "AuthorizationMiddleware",
    "PermissionLoaderMiddleware",
]
