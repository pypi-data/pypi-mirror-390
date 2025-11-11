"""
Integration tests for the core CovetPy framework.

Tests the complete framework integration including:
- Application factory
- Dependency injection
- Configuration management
- Middleware pipeline
- Plugin system
- Error handling
"""

import pytest
import asyncio
from pathlib import Path
from fastapi import APIRouter
from fastapi.testclient import TestClient

try:
    from covet import (
        Covet, Config,
        Container, Singleton, 
        Plugin, PluginMetadata,
        get_logger
    )
    from covet.config import Environment
    COVET_FRAMEWORK_AVAILABLE = True
except ImportError:
    Covet = None
    Config = None
    Environment = None
    Container = None
    Singleton = None
    Plugin = None
    PluginMetadata = None
    get_logger = None
    COVET_FRAMEWORK_AVAILABLE = False


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestConfig:
    """Test configuration setup."""
    
    def test_config_creation(self):
        """Test basic configuration creation."""
        config = Config(
            app_name="Test App",
            environment=Environment.TESTING,
            debug=True
        )
        
        assert config.app_name == "Test App"
        assert config.environment == Environment.TESTING
        assert config.debug is True
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = Config()
        
        # Should have default values
        assert config.app_name == "CovetPy App"
        assert config.environment == Environment.DEVELOPMENT
        assert config.server.host == "127.0.0.1"
        assert config.server.port == 8000


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestContainer:
    """Test dependency injection container."""
    
    def test_service_registration(self):
        """Test service registration and resolution."""
        container = Container()
        
        @Singleton
        class TestService:
            def get_message(self):
                return "Hello from TestService"
        
        container.register_singleton(TestService)
        
        # Resolve service
        service = container.resolve(TestService)
        assert service.get_message() == "Hello from TestService"
        
        # Should return same instance (singleton)
        service2 = container.resolve(TestService)
        assert service is service2
    
    def test_dependency_injection(self):
        """Test automatic dependency injection."""
        container = Container()
        
        @Singleton
        class DatabaseService:
            def connect(self):
                return "connected"
        
        @Singleton
        class UserService:
            def __init__(self, db_service: DatabaseService):
                self.db_service = db_service
            
            def get_users(self):
                connection = self.db_service.connect()
                return f"users from {connection} db"
        
        container.register_singleton(DatabaseService)
        container.register_singleton(UserService)
        
        user_service = container.resolve(UserService)
        result = user_service.get_users()
        
        assert result == "users from connected db"


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestApplicationFactory:
    """Test application factory functionality."""
    
    def test_app_creation(self):
        """Test basic app creation."""
        config = Config(
            app_name="Test App",
            environment=Environment.TESTING,
            debug=True
        )
        
        app = Covet.create_app(config=config)
        
        assert app.config.app_name == "Test App"
        assert app.config.environment == Environment.TESTING
        assert app.fastapi_app is not None
    
    @pytest.mark.asyncio
    async def test_app_initialization(self):
        """Test app initialization."""
        app = Covet.create_app()
        await app.initialize()
        
        assert app._initialized is True
        assert app.container is not None
        assert app.plugin_manager is not None


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestPluginSystem:
    """Test plugin system functionality."""
    
    @pytest.mark.asyncio
    async def test_plugin_lifecycle(self):
        """Test plugin installation and activation."""
        
        class TestPlugin(Plugin):
            @property
            def metadata(self):
                return PluginMetadata(
                    name="test-plugin",
                    version="1.0.0",
                    description="Test plugin"
                )
            
            async def install(self, container):
                container.register_singleton(TestPluginService)
            
            async def activate(self, app, container):
                router = APIRouter()
                
                @router.get("/plugin-test")
                async def plugin_endpoint():
                    return {"plugin": "test-plugin", "status": "active"}
                
                app.include_router(router)
                await super().activate(app, container)
        
        @Singleton
        class TestPluginService:
            def get_data(self):
                return "plugin data"
        
        # Create app and plugin
        app = Covet.create_app()
        await app.initialize()
        
        plugin = TestPlugin()
        
        # Install and activate plugin
        await plugin.install(app.container)
        await plugin.activate(app.fastapi_app, app.container)
        
        # Verify service is available
        service = app.container.resolve(TestPluginService)
        assert service.get_data() == "plugin data"


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestMiddleware:
    """Test middleware functionality."""
    
    def test_middleware_stack_creation(self):
        """Test middleware stack creation and configuration."""
        from covet.core.middleware import (
            MiddlewareStack, ErrorHandlingMiddleware,
            RequestLoggingMiddleware, MiddlewareConfig
        )
        
        stack = MiddlewareStack()
        
        # Add middleware
        stack.add(
            ErrorHandlingMiddleware,
            MiddlewareConfig(priority=1000)
        )
        
        stack.add(
            RequestLoggingMiddleware,
            MiddlewareConfig(priority=900)
        )
        
        # Check order
        ordered = stack.get_ordered_middleware()
        assert len(ordered) == 2
        assert isinstance(ordered[0], ErrorHandlingMiddleware)
        assert isinstance(ordered[1], RequestLoggingMiddleware)


@pytest.mark.skipif(not COVET_FRAMEWORK_AVAILABLE, reason="Covet framework modules not available")
class TestIntegration:
    """Test complete framework integration."""
    
    @pytest.mark.asyncio
    async def test_full_application_setup(self):
        """Test complete application setup with all components."""
        
        # Create configuration
        config = Config(
            app_name="Integration Test App",
            environment=Environment.TESTING,
            debug=True
        )
        
        # Create application
        app = Covet.create_app(config=config)
        
        # Register a service
        @Singleton
        class MessageService:
            def get_message(self):
                return "Hello from integration test!"
        
        app.container.register_singleton(MessageService)
        
        # Add a route
        router = APIRouter()
        
        @router.get("/test")
        async def test_endpoint():
            service = app.container.resolve(MessageService)
            return {"message": service.get_message()}
        
        app.include_router(router)
        
        # Initialize application
        await app.initialize()
        
        # Test with client
        client = TestClient(app.fastapi_app)
        response = client.get("/test")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Hello from integration test!"
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling integration."""
        from covet.core.exceptions import CovetError
        
        app = Covet.create_app()
        await app.initialize()
        
        @app.fastapi_app.get("/error")
        async def error_endpoint():
            raise CovetError("Test error", error_code="TEST_ERROR")
        
        client = TestClient(app.fastapi_app)
        response = client.get("/error")
        
        assert response.status_code == 500
        data = response.json()
        assert data["error_code"] == "TEST_ERROR"
        assert data["message"] == "Test error"
    
    def test_configuration_loading(self):
        """Test configuration loading from different sources."""
        # Test default configuration
        config1 = Config()
        assert config1.app_name == "CovetPy App"
        
        # Test custom configuration
        config2 = Config(
            app_name="Custom App",
            debug=True
        )
        assert config2.app_name == "Custom App"
        assert config2.debug is True
    
    @pytest.mark.asyncio 
    async def test_logging_integration(self):
        """Test logging system integration."""
        from covet.core.logging import get_logger, setup_logging, LoggingConfig
        
        # Setup logging
        log_config = LoggingConfig(
            level="DEBUG",
            structured=True
        )
        setup_logging(log_config)
        
        # Get logger
        logger = get_logger("test.integration")
        
        # Test logging (basic smoke test)
        logger.info("Test log message")
        logger.debug("Debug message") 
        logger.warning("Warning message")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])