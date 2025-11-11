"""
Uvicorn Integration Examples for CovetPy ASGI Implementation
===========================================================

This file contains comprehensive examples showing how to use CovetPy
with uvicorn and other ASGI servers for production deployment.

Examples include:
- Basic ASGI app with uvicorn
- Full-featured application with middleware
- WebSocket integration
- Lifespan events
- Production configuration
- Docker deployment
- Load testing
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

# Import CovetPy ASGI components
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from covet.core.asgi_app import CovetASGIApp, create_asgi_app
from covet.core.asgi_integration import make_asgi_compatible, integrate_with_uvicorn
from covet.core.routing import CovetRouter
from covet.core.middleware import MiddlewareStack
from covet.core.http import Request, Response

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Example 1: Basic ASGI Application
# =================================

def create_basic_app():
    """Create a basic CovetPy ASGI application."""
    
    # Create router and add routes
    router = CovetRouter()
    
    async def hello(request: Request):
        return Response({"message": "Hello from CovetPy ASGI!"})
    
    async def echo(request: Request):
        data = await request.json() if request.is_json() else {}
        return Response({
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "data": data
        })
    
    async def health(request: Request):
        return Response({
            "status": "healthy",
            "timestamp": time.time(),
            "version": "1.0.0"
        })
    
    router.add_route("/", hello, ["GET"])
    router.add_route("/echo", echo, ["POST", "PUT"])
    router.add_route("/health", health, ["GET"])
    
    # Create ASGI app
    app = create_asgi_app(router=router, debug=True)
    
    return app


# Example 2: Application with Middleware
# =====================================

class TimingMiddleware:
    """Custom timing middleware."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        start_time = time.time()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add timing header
                headers = list(message.get("headers", []))
                duration = time.time() - start_time
                headers.append([
                    b"x-response-time", 
                    f"{duration:.3f}s".encode()
                ])
                message["headers"] = headers
            await send(message)
            
        await self.app(scope, receive, send_wrapper)


class LoggingMiddleware:
    """Request logging middleware."""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        method = scope.get("method", "")
        path = scope.get("path", "")
        start_time = time.time()
        
        logger.info(f"Started {method} {path}")
        
        status_code = 500
        
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 500)
            await send(message)
            
        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration = time.time() - start_time
            logger.info(f"Completed {method} {path} {status_code} in {duration:.3f}s")


def create_middleware_app():
    """Create an ASGI app with custom middleware."""
    
    router = CovetRouter()
    
    async def api_handler(request: Request):
        # Simulate some work
        await asyncio.sleep(0.1)
        return Response({
            "api": "v1",
            "message": "This request was processed with middleware",
            "request_id": request.headers.get("x-request-id", "unknown")
        })
    
    async def slow_handler(request: Request):
        # Simulate slow operation
        await asyncio.sleep(1.0)
        return Response({"message": "Slow operation completed"})
    
    router.add_route("/api/data", api_handler, ["GET"])
    router.add_route("/slow", slow_handler, ["GET"])
    
    # Create base app
    app = create_asgi_app(router=router, debug=True)
    
    # Wrap with middleware (order matters!)
    app = TimingMiddleware(app)
    app = LoggingMiddleware(app)
    
    return app


# Example 3: WebSocket Integration
# ===============================

def create_websocket_app():
    """Create an ASGI app with WebSocket support."""
    
    router = CovetRouter()
    
    # Store active WebSocket connections
    active_connections = set()
    
    async def websocket_endpoint(websocket):
        """WebSocket endpoint for real-time communication."""
        await websocket.accept()
        active_connections.add(websocket)
        
        try:
            logger.info(f"WebSocket connected: {websocket.path}")
            
            # Send welcome message
            await websocket.send_json({
                "type": "welcome",
                "message": "Connected to CovetPy WebSocket!",
                "connections": len(active_connections)
            })
            
            # Echo messages back with timestamp
            while True:
                try:
                    # Receive message
                    message = await websocket.receive_text()
                    data = json.loads(message)
                    
                    # Echo back with timestamp
                    response = {
                        "type": "echo",
                        "original": data,
                        "timestamp": time.time(),
                        "connections": len(active_connections)
                    }
                    
                    await websocket.send_json(response)
                    
                    # Broadcast to other connections if specified
                    if data.get("broadcast"):
                        broadcast_msg = {
                            "type": "broadcast",
                            "from": "user",
                            "message": data.get("message", ""),
                            "timestamp": time.time()
                        }
                        
                        for conn in active_connections:
                            if conn != websocket:
                                try:
                                    await conn.send_json(broadcast_msg)
                                except:
                                    pass  # Connection might be closed
                                    
                except Exception as e:
                    logger.error(f"WebSocket error: {e}")
                    break
                    
        finally:
            active_connections.discard(websocket)
            logger.info(f"WebSocket disconnected. Active: {len(active_connections)}")
    
    async def websocket_info(request: Request):
        """HTTP endpoint to get WebSocket info."""
        return Response({
            "websocket_endpoint": "/ws",
            "active_connections": len(active_connections),
            "supported_messages": [
                "echo", "broadcast"
            ]
        })
    
    # Add routes
    router.add_route("/ws", websocket_endpoint, ["WEBSOCKET"])
    router.add_route("/ws/info", websocket_info, ["GET"])
    
    return create_asgi_app(router=router, debug=True)


# Example 4: Application with Lifespan Events
# ===========================================

# Global state for demonstration
app_state = {
    "start_time": None,
    "requests_processed": 0,
    "background_task": None
}

async def background_task():
    """Background task that runs during app lifetime."""
    while True:
        try:
            await asyncio.sleep(10)
            logger.info(f"Background task: {app_state['requests_processed']} requests processed")
        except asyncio.CancelledError:
            logger.info("Background task cancelled")
            break


def create_lifespan_app():
    """Create an ASGI app with lifespan events."""
    
    router = CovetRouter()
    
    async def stats_handler(request: Request):
        app_state["requests_processed"] += 1
        
        uptime = 0
        if app_state["start_time"]:
            uptime = time.time() - app_state["start_time"]
            
        return Response({
            "uptime_seconds": uptime,
            "requests_processed": app_state["requests_processed"],
            "background_task_running": app_state["background_task"] is not None
        })
    
    async def reset_stats(request: Request):
        app_state["requests_processed"] = 0
        return Response({"message": "Stats reset"})
    
    router.add_route("/stats", stats_handler, ["GET"])
    router.add_route("/reset", reset_stats, ["POST"])
    
    # Create app with lifespan events
    app = create_asgi_app(router=router, debug=True)
    
    # Add startup handler
    async def startup():
        logger.info("Application startup")
        app_state["start_time"] = time.time()
        app_state["background_task"] = asyncio.create_task(background_task())
        
    # Add shutdown handler
    async def shutdown():
        logger.info("Application shutdown")
        if app_state["background_task"]:
            app_state["background_task"].cancel()
            try:
                await app_state["background_task"]
            except asyncio.CancelledError:
                pass
    
    app.add_startup_handler(startup)
    app.add_shutdown_handler(shutdown)
    
    return app


# Example 5: Production Configuration
# ==================================

def create_production_app():
    """Create a production-ready ASGI application."""
    
    router = CovetRouter()
    
    # API endpoints
    async def api_v1_users(request: Request):
        if request.method == "GET":
            return Response({
                "users": [
                    {"id": 1, "name": "Alice"},
                    {"id": 2, "name": "Bob"}
                ]
            })
        elif request.method == "POST":
            data = await request.json()
            return Response({
                "created": True,
                "user": data
            }, status_code=201)
    
    async def api_v1_user_detail(request: Request):
        user_id = request.path_params.get("user_id")
        return Response({
            "id": int(user_id),
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com"
        })
    
    # Add API routes
    router.add_route("/api/v1/users", api_v1_users, ["GET", "POST"])
    router.add_route("/api/v1/users/{user_id}", api_v1_user_detail, ["GET"])
    
    # Health check
    async def health_check(request: Request):
        return Response({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": time.time()
        })
    
    router.add_route("/health", health_check, ["GET"])
    
    # Create production app (debug=False)
    app = create_asgi_app(router=router, debug=False)
    
    # Add production startup tasks
    async def startup():
        logger.info("Production app starting up")
        # Initialize database connections, caches, etc.
        
    async def shutdown():
        logger.info("Production app shutting down")
        # Clean up resources
        
    app.add_startup_handler(startup)
    app.add_shutdown_handler(shutdown)
    
    return app


# Example 6: Running with Uvicorn
# ===============================

def run_basic_example():
    """Run the basic example with uvicorn."""
    app = create_basic_app()
    
    try:
        import uvicorn
        uvicorn.run(
            app,
            host="127.0.0.1",
            port=8000,
            log_level="info",
            access_log=True
        )
    except ImportError:
        print("uvicorn not installed. Install with: pip install uvicorn")


def run_production_example():
    """Run production example with uvicorn."""
    app = create_production_app()
    
    try:
        import uvicorn
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8000,
            workers=4,  # Multiple workers for production
            log_level="info",
            access_log=True,
            server_header=False,  # Security
            date_header=False,    # Security
        )
    except ImportError:
        print("uvicorn not installed. Install with: pip install uvicorn[standard]")


# Example 7: Docker Deployment
# ============================

DOCKERFILE_CONTENT = '''
# Dockerfile for CovetPy ASGI Application
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY examples/ ./examples/

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uvicorn", "examples.asgi_uvicorn_examples:production_app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
'''

REQUIREMENTS_TXT_CONTENT = '''
# Requirements for CovetPy ASGI deployment
uvicorn[standard]==0.24.0
gunicorn==21.2.0  # Alternative ASGI server
httptools==0.6.1
uvloop==0.19.0    # For better performance on Linux
'''

DOCKER_COMPOSE_CONTENT = '''
version: '3.8'

services:
  covetpy-app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=info
      - WORKERS=4
    restart: unless-stopped
    
  # Optional: Add nginx for load balancing
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - covetpy-app
    restart: unless-stopped
'''


# Example 8: Load Testing Script
# =============================

async def load_test_example():
    """Simple load testing for the ASGI app."""
    import aiohttp
    import time
    
    async def make_request(session, url):
        try:
            async with session.get(url) as response:
                return response.status, await response.text()
        except Exception as e:
            return 0, str(e)
    
    # Test configuration
    BASE_URL = "http://localhost:8000"
    CONCURRENT_REQUESTS = 100
    TOTAL_REQUESTS = 1000
    
    print(f"Load testing {BASE_URL}")
    print(f"Concurrent requests: {CONCURRENT_REQUESTS}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    
    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Create tasks for concurrent requests
        tasks = []
        for i in range(TOTAL_REQUESTS):
            url = f"{BASE_URL}/health"
            tasks.append(make_request(session, url))
            
            # Batch requests to control concurrency
            if len(tasks) >= CONCURRENT_REQUESTS:
                results = await asyncio.gather(*tasks)
                success_count = sum(1 for status, _ in results if status == 200)
                print(f"Batch completed: {success_count}/{len(tasks)} successful")
                tasks = []
        
        # Process remaining tasks
        if tasks:
            results = await asyncio.gather(*tasks)
            success_count = sum(1 for status, _ in results if status == 200)
            print(f"Final batch: {success_count}/{len(tasks)} successful")
    
    duration = time.time() - start_time
    rps = TOTAL_REQUESTS / duration
    
    print(f"Load test completed in {duration:.2f} seconds")
    print(f"Requests per second: {rps:.2f}")


# Example Apps for Direct Use
# ===========================

# Export apps for direct uvicorn usage
basic_app = create_basic_app()
middleware_app = create_middleware_app()
websocket_app = create_websocket_app()
lifespan_app = create_lifespan_app()
production_app = create_production_app()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "basic":
            print("Running basic example...")
            run_basic_example()
        elif example == "middleware":
            print("Running middleware example...")
            app = create_middleware_app()
            try:
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8000)
            except ImportError:
                print("uvicorn not installed")
        elif example == "websocket":
            print("Running WebSocket example...")
            app = create_websocket_app()
            try:
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8000)
            except ImportError:
                print("uvicorn not installed")
        elif example == "lifespan":
            print("Running lifespan example...")
            app = create_lifespan_app()
            try:
                import uvicorn
                uvicorn.run(app, host="127.0.0.1", port=8000)
            except ImportError:
                print("uvicorn not installed")
        elif example == "production":
            print("Running production example...")
            run_production_example()
        elif example == "loadtest":
            print("Running load test...")
            asyncio.run(load_test_example())
        else:
            print(f"Unknown example: {example}")
    else:
        print("Available examples:")
        print("  python asgi_uvicorn_examples.py basic")
        print("  python asgi_uvicorn_examples.py middleware")
        print("  python asgi_uvicorn_examples.py websocket")
        print("  python asgi_uvicorn_examples.py lifespan")
        print("  python asgi_uvicorn_examples.py production")
        print("  python asgi_uvicorn_examples.py loadtest")
        print("\nOr use with uvicorn directly:")
        print("  uvicorn asgi_uvicorn_examples:basic_app --reload")
        print("  uvicorn asgi_uvicorn_examples:production_app --workers 4")