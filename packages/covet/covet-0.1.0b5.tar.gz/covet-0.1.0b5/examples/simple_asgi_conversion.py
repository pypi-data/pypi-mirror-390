"""
Simple ASGI Conversion Example for CovetPy
==========================================

This example shows how to convert an existing CovetPy application
to be ASGI 3.0 compatible and run it with uvicorn.

Usage:
    # Run with uvicorn
    uvicorn simple_asgi_conversion:app --reload --port 8000
    
    # Or run directly
    python simple_asgi_conversion.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covet.core.asgi_app import create_asgi_app
from covet.core.routing import CovetRouter
from covet.core.http import Request, Response


# Step 1: Create your application components
def create_router():
    """Create a router with some example routes."""
    router = CovetRouter()
    
    # Simple GET route
    async def home(request: Request):
        return Response({
            "message": "Welcome to CovetPy ASGI!",
            "path": request.path,
            "method": request.method
        })
    
    # Route with path parameters
    async def user_profile(request: Request):
        user_id = request.path_params.get("user_id")
        return Response({
            "user_id": int(user_id),
            "profile": f"Profile for user {user_id}"
        })
    
    # POST route that handles JSON
    async def create_user(request: Request):
        if request.is_json():
            data = await request.json()
            return Response({
                "created": True,
                "user": data
            }, status_code=201)
        else:
            return Response({
                "error": "JSON data required"
            }, status_code=400)
    
    # Add routes to router
    router.add_route("/", home, ["GET"])
    router.add_route("/users/{user_id}", user_profile, ["GET"])
    router.add_route("/users", create_user, ["POST"])
    
    return router


# Step 2: Create the ASGI application
def create_app():
    """Create the ASGI-compatible CovetPy application."""
    router = create_router()
    
    # Create ASGI app with the router
    app = create_asgi_app(
        router=router,
        debug=True,  # Enable debug mode for development
        enable_lifespan=True  # Enable startup/shutdown events
    )
    
    # Add startup event
    async def startup():
        print("🚀 CovetPy ASGI app starting up!")
        print("Available routes:")
        for route_info in router.get_all_routes():
            print(f"  {route_info['method']} {route_info['path']}")
    
    # Add shutdown event
    async def shutdown():
        print("👋 CovetPy ASGI app shutting down!")
    
    app.add_startup_handler(startup)
    app.add_shutdown_handler(shutdown)
    
    return app


# Step 3: Create the ASGI application instance
app = create_app()


# Step 4: Add a simple development server function
def run_dev_server():
    """Run the application with uvicorn for development."""
    try:
        import uvicorn
        print("Starting development server...")
        uvicorn.run(
            "simple_asgi_conversion:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Install with: pip install uvicorn")
        print("Or run with: uvicorn simple_asgi_conversion:app --reload")


if __name__ == "__main__":
    print("CovetPy ASGI Conversion Example")
    print("===============================")
    print()
    print("This example shows how to create an ASGI-compatible CovetPy app.")
    print()
    print("To run with uvicorn:")
    print("  uvicorn simple_asgi_conversion:app --reload --port 8000")
    print()
    print("Available endpoints:")
    print("  GET  /                    - Home page")
    print("  GET  /users/{user_id}     - User profile")
    print("  POST /users               - Create user (send JSON)")
    print()
    print("Starting development server...")
    
    run_dev_server()