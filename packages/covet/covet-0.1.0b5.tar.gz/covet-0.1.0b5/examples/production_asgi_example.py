#!/usr/bin/env python3
"""
Production-Ready CovetPy ASGI Server Example
Demonstrates how to create and deploy a CovetPy application with ASGI.

This example shows:
1. Creating a CovetPy application
2. Setting up routes and middleware
3. Running with various ASGI servers
4. Production deployment considerations
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any

# Add the src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

try:
    from covet.core.app_pure import CovetApplication
    from covet.core.server import CovetServer
    from covet.core.http import Request, Response, json_response, StreamingResponse
    from covet.core.config import Config, Environment
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def create_production_app() -> CovetApplication:
    """Create a production-ready CovetPy application."""
    
    # Create configuration
    config = Config(
        environment=Environment.PRODUCTION,
        enable_cors=True,
        enable_compression=True,
        max_request_body_size=16 * 1024 * 1024,  # 16MB
        request_timeout=30.0,
        websocket_timeout=60.0
    )
    
    # Create application
    app = CovetApplication(
        title="CovetPy Production API",
        version="1.0.0",
        description="High-performance API built with CovetPy ASGI framework",
        config=config,
        debug=False  # Production mode
    )
    
    # Add middleware (automatically applied based on config)
    
    # Health and monitoring endpoints
    @app.get("/health")
    async def health_check(request: Request) -> Response:
        """Health check endpoint for load balancers."""
        return json_response({
            "status": "healthy",
            "service": "covetpy-api",
            "version": "1.0.0",
            "environment": "production"
        })
    
    @app.get("/metrics")
    async def metrics(request: Request) -> Response:
        """Basic metrics endpoint."""
        # In production, you'd gather real metrics
        return json_response({
            "requests_total": 1000,
            "active_connections": 50,
            "uptime_seconds": 3600,
            "memory_usage_mb": 128
        })
    
    # API endpoints
    @app.get("/")
    async def root(request: Request) -> Response:
        """API root endpoint."""
        return json_response({
            "message": "Welcome to CovetPy Production API",
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/health"
        })
    
    @app.get("/api/users")
    async def list_users(request: Request) -> Response:
        """List users with pagination."""
        page = int(request.query.get("page", "1"))
        limit = min(int(request.query.get("limit", "10")), 100)
        
        # Simulate database query
        users = [
            {"id": i, "name": f"User {i}", "email": f"user{i}@example.com"}
            for i in range((page-1)*limit + 1, page*limit + 1)
        ]
        
        return json_response({
            "users": users,
            "page": page,
            "limit": limit,
            "total": 1000
        })
    
    @app.get("/api/users/{user_id}")
    async def get_user(request: Request) -> Response:
        """Get a specific user."""
        user_id = request.path_params.get("user_id")
        
        # Simulate database lookup
        if user_id == "999":
            return json_response(
                {"error": "User not found"}, 
                status_code=404
            )
        
        return json_response({
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "created_at": "2023-01-01T00:00:00Z"
        })
    
    @app.post("/api/users")
    async def create_user(request: Request) -> Response:
        """Create a new user."""
        try:
            data = await request.json()
        except Exception:
            return json_response(
                {"error": "Invalid JSON data"}, 
                status_code=400
            )
        
        # Validate required fields
        if "name" not in data or "email" not in data:
            return json_response(
                {"error": "Missing required fields: name, email"}, 
                status_code=400
            )
        
        # Simulate user creation
        new_user = {
            "id": "new_123",
            "name": data["name"],
            "email": data["email"],
            "created_at": "2023-01-01T00:00:00Z"
        }
        
        return json_response(new_user, status_code=201)
    
    @app.get("/api/stream")
    async def stream_data(request: Request) -> Response:
        """Stream data endpoint."""
        async def generate_data():
            for i in range(100):
                yield f"data: Event {i}\\n"
                await asyncio.sleep(0.01)  # Small delay
        
        return StreamingResponse(
            generate_data(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    
    # Error handling
    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return json_response(
            {"error": "Invalid value", "details": str(exc)},
            status_code=400
        )
    
    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        # Log the error (in production)
        return json_response(
            {"error": "Internal server error"},
            status_code=500
        )
    
    return app


def run_with_builtin_server():
    """Run with CovetPy's built-in ASGI server."""
    print("Starting with CovetPy built-in ASGI server...")
    
    app = create_production_app()
    
    server = CovetServer(
        app.asgi,  # Use ASGI interface
        host="0.0.0.0",
        port=8000,
        debug=False,
        access_log=True
    )
    
    print("Server running on http://0.0.0.0:8000")
    print("Available endpoints:")
    print("  GET  /           - API root")
    print("  GET  /health     - Health check")
    print("  GET  /metrics    - Metrics")
    print("  GET  /api/users  - List users")
    print("  GET  /api/users/{id} - Get user")
    print("  POST /api/users  - Create user")
    print("  GET  /api/stream - Stream data")
    
    asyncio.run(server.serve())


def run_with_uvicorn():
    """Run with uvicorn (if available)."""
    try:
        import uvicorn
        
        app = create_production_app()
        
        print("Starting with uvicorn ASGI server...")
        uvicorn.run(
            app.asgi,
            host="0.0.0.0",
            port=8000,
            workers=4,  # Multiple workers
            access_log=True,
            server_header=True,
            date_header=True
        )
        
    except ImportError:
        print("uvicorn not available, falling back to built-in server")
        run_with_builtin_server()


def run_with_hypercorn():
    """Run with hypercorn (if available)."""
    try:
        import hypercorn.asyncio
        from hypercorn.config import Config as HypercornConfig
        
        app = create_production_app()
        
        print("Starting with hypercorn ASGI server...")
        
        config = HypercornConfig()
        config.bind = "0.0.0.0:8000"
        config.workers = 4
        
        asyncio.run(hypercorn.asyncio.serve(app.asgi, config))
        
    except ImportError:
        print("hypercorn not available, falling back to uvicorn")
        run_with_uvicorn()


def main():
    """Main entry point with server selection."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CovetPy Production ASGI Server")
    parser.add_argument(
        "--server", 
        choices=["builtin", "uvicorn", "hypercorn", "auto"],
        default="auto",
        help="ASGI server to use"
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to"
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("CovetPy Production ASGI Server")
    print("="*60)
    print(f"Server: {args.server}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print("="*60)
    
    try:
        if args.server == "builtin":
            run_with_builtin_server()
        elif args.server == "uvicorn":
            run_with_uvicorn()
        elif args.server == "hypercorn":
            run_with_hypercorn()
        else:  # auto
            # Try servers in order of preference
            run_with_hypercorn()
            
    except KeyboardInterrupt:
        print("\\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()