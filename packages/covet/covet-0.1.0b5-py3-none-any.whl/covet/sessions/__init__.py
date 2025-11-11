"""
CovetPy Session Management

Production-ready session management with multiple backend support:
- Cookie sessions (signed/encrypted, no server storage)
- Database sessions (persistent SQL storage)
- Redis sessions (fast distributed storage)
- Memory sessions (development only)

Features:
- Security (CSRF, session fixation prevention, hijacking detection)
- Dictionary-like session interface
- Flash messages
- Automatic saving
- Session regeneration

Example:
    from covet.sessions import (
        SessionManager, SessionConfig, SessionBackend,
        SessionMiddleware, SessionMiddlewareConfig
    )

    # Create session manager
    config = SessionConfig(
        backend=SessionBackend.REDIS,
        csrf_enabled=True,
        regenerate_on_login=True
    )

    manager = SessionManager(config)
    await manager.connect()

    # Use in ASGI app
    middleware_config = SessionMiddlewareConfig(
        session_config=config,
        cookie_secure=True,
        validate_ip=True
    )

    app = SessionMiddleware(app, config=middleware_config)

    # Use in handlers
    async def handler(request):
        session = request.state.session

        # Dictionary interface
        session['user_id'] = 123
        user_id = session.get('user_id')

        # Flash messages
        session.flash('Login successful', 'success')

        # Security
        await session.regenerate()  # After login

        return response
"""

from .backends import (
    CookieSession,
    CookieSessionConfig,
    CookieSessionStore,
    DatabaseSessionConfig,
    DatabaseSessionStore,
    MemorySessionConfig,
    MemorySessionStore,
    RedisSessionConfig,
    RedisSessionStore,
    SessionData,
)
from .flash import (
    FlashCategory,
    flash,
    get_flashed_messages,
)
from .manager import (
    Session,
    SessionBackend,
    SessionConfig,
    SessionManager,
    configure_session_manager,
    get_session_manager,
)
from .middleware import (
    SessionMiddleware,
    SessionMiddlewareConfig,
    get_session,
)

__all__ = [
    # Backends
    "CookieSession",
    "CookieSessionConfig",
    "CookieSessionStore",
    "DatabaseSessionStore",
    "DatabaseSessionConfig",
    "RedisSessionStore",
    "RedisSessionConfig",
    "MemorySessionStore",
    "MemorySessionConfig",
    "SessionData",
    # Manager
    "Session",
    "SessionManager",
    "SessionConfig",
    "SessionBackend",
    "get_session_manager",
    "configure_session_manager",
    # Middleware
    "SessionMiddleware",
    "SessionMiddlewareConfig",
    "get_session",
    # Flash
    "FlashCategory",
    "flash",
    "get_flashed_messages",
]


__version__ = "1.0.0"
