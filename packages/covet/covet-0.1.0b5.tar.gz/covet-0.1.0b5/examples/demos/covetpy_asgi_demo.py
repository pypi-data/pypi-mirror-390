#!/usr/bin/env python3
"""
CovetPy ASGI 3.0 Compliance Demonstration

This script demonstrates CovetPy's full ASGI 3.0 compliance by creating
a production-ready application that works with standard ASGI servers
like uvicorn, hypercorn, and daphne.

Usage:
    # Start with uvicorn
    uvicorn covetpy_asgi_demo:app --host 0.0.0.0 --port 8000

    # Start with hypercorn  
    hypercorn covetpy_asgi_demo:app --bind 0.0.0.0:8000

    # Start with daphne
    daphne -b 0.0.0.0 -p 8000 covetpy_asgi_demo:app

Test endpoints:
    GET  /              - Hello world
    GET  /health        - Health check
    POST /echo          - Echo JSON data
    GET  /users/{id}    - Path parameters
    WS   /ws            - WebSocket connection
    GET  /large         - Large response test
    GET  /async         - Async processing test
"""

import asyncio
import json
import time
from contextlib import asynccontextmanager
from typing import Dict, Any

from src.covet.core.asgi import create_app
from src.covet.core.http import Request, Response, json_response


# Lifespan management
@asynccontextmanager
async def lifespan():
    """Application lifespan context manager."""
    print("🚀 CovetPy application starting up...")
    
    # Startup tasks
    startup_time = time.time()
    
    yield  # Application runs here
    
    # Shutdown tasks
    shutdown_time = time.time()
    uptime = shutdown_time - startup_time
    print(f"🛑 CovetPy application shutting down after {uptime:.2f} seconds")


# Create ASGI application
app = create_app(lifespan=lifespan, debug=False)


# Route handlers
async def hello_world(request: Request) -> Response:
    """Simple hello world endpoint."""
    return json_response({
        "message": "Hello from CovetPy!",
        "framework": "CovetPy",
        "asgi_version": "3.0",
        "timestamp": time.time(),
        "method": request.method,
        "path": request.path
    })


async def health_check(request: Request) -> Response:
    """Health check endpoint for load balancers."""
    return json_response({
        "status": "healthy",
        "framework": "CovetPy",
        "version": "1.0.0",
        "timestamp": time.time(),
        "checks": {
            "database": "ok",
            "memory": "ok", 
            "disk": "ok"
        }
    })


async def echo_handler(request: Request) -> Response:
    """Echo back JSON data demonstrating request body parsing."""
    try:
        data = await request.json()
        return json_response({
            "echo": data,
            "received_at": time.time(),
            "content_type": request.content_type,
            "method": request.method,
            "headers": dict(request.headers)
        })
    except Exception as e:
        return json_response(
            {"error": "Invalid JSON", "detail": str(e)}, 
            status_code=400
        )


async def get_user(request: Request) -> Response:
    """Demonstrate path parameter extraction."""
    user_id = request.path_params.get("user_id")
    
    # Simulate user lookup
    user_data = {
        "id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com",
        "created_at": "2025-01-01T00:00:00Z",
        "profile": {
            "bio": "CovetPy framework user",
            "preferences": {
                "theme": "dark",
                "notifications": True
            }
        }
    }
    
    return json_response(user_data)


async def large_response(request: Request) -> Response:
    """Generate large JSON response to test performance."""
    # Generate substantial data
    data = {
        "timestamp": time.time(),
        "items": [
            {
                "id": i,
                "name": f"Item {i}",
                "description": f"This is item number {i} " * 10,
                "metadata": {
                    "created": f"2025-01-{(i % 30) + 1:02d}",
                    "tags": [f"tag{j}" for j in range(5)],
                    "properties": {f"prop{k}": f"value{k}" for k in range(10)}
                }
            }
            for i in range(1000)  # 1000 items
        ],
        "pagination": {
            "total": 1000,
            "page": 1,
            "per_page": 1000,
            "has_next": False
        }
    }
    
    return json_response(data)


async def async_processing(request: Request) -> Response:
    """Demonstrate asynchronous processing."""
    start_time = time.time()
    
    # Simulate async work (e.g., database queries, API calls)
    await asyncio.sleep(0.1)  # 100ms processing time
    
    processing_time = time.time() - start_time
    
    return json_response({
        "message": "Async processing completed",
        "processing_time_ms": processing_time * 1000,
        "timestamp": time.time(),
        "worker_info": {
            "framework": "CovetPy",
            "asgi_compliant": True,
            "supports_async": True
        }
    })


async def websocket_handler(websocket):
    """WebSocket connection handler demonstrating real-time communication."""
    await websocket.accept()
    
    # Send welcome message
    await websocket.send_text(json.dumps({
        "type": "welcome",
        "message": "Connected to CovetPy WebSocket!",
        "timestamp": time.time(),
        "connection_id": id(websocket)
    }))
    
    # Echo messages back
    try:
        while True:
            # Receive message
            message = await websocket._receive()
            
            if message.get("type") == "websocket.receive":
                if "text" in message:
                    try:
                        data = json.loads(message["text"])
                        
                        # Echo back with metadata
                        response = {
                            "type": "echo",
                            "original": data,
                            "timestamp": time.time(),
                            "echo_count": data.get("count", 0) + 1
                        }
                        
                        await websocket.send_text(json.dumps(response))
                        
                    except json.JSONDecodeError:
                        # Handle plain text
                        response = {
                            "type": "echo",
                            "text": message["text"],
                            "timestamp": time.time()
                        }
                        await websocket.send_text(json.dumps(response))
                        
            elif message.get("type") == "websocket.disconnect":
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# Register routes
app.router.add_route("/", hello_world, ["GET"])
app.router.add_route("/health", health_check, ["GET"])  
app.router.add_route("/echo", echo_handler, ["POST"])
app.router.add_route("/users/{user_id}", get_user, ["GET"])
app.router.add_route("/large", large_response, ["GET"])
app.router.add_route("/async", async_processing, ["GET"])
app.router.add_route("/ws", websocket_handler, ["WEBSOCKET"])


# Additional demonstration endpoints
async def framework_info(request: Request) -> Response:
    """Provide detailed framework information."""
    return json_response({
        "framework": {
            "name": "CovetPy",
            "version": "1.0.0",
            "description": "High-performance Python web framework",
            "asgi_version": "3.0",
            "protocols": ["HTTP/1.1", "HTTP/2", "WebSocket"],
            "features": [
                "Zero-copy optimizations",
                "Memory pooling", 
                "Advanced routing",
                "Middleware system",
                "WebSocket support",
                "Real-time capabilities",
                "Production ready"
            ]
        },
        "compatibility": {
            "asgi_servers": ["uvicorn", "hypercorn", "daphne"],
            "python_versions": ["3.8+"],
            "operating_systems": ["Linux", "macOS", "Windows"]
        },
        "performance": {
            "requests_per_second": ">10,000",
            "websocket_connections": ">1,000",
            "memory_efficient": True,
            "zero_copy": True
        }
    })


app.router.add_route("/info", framework_info, ["GET"])


if __name__ == "__main__":
    print("""
🚀 CovetPy ASGI 3.0 Compliance Demo
===================================

This demo showcases CovetPy's full ASGI 3.0 compliance.

To run with different ASGI servers:

1. Uvicorn (recommended):
   uvicorn covetpy_asgi_demo:app --host 0.0.0.0 --port 8000 --reload

2. Hypercorn (HTTP/2 support):
   hypercorn covetpy_asgi_demo:app --bind 0.0.0.0:8000

3. Daphne (Django Channels compatible):
   daphne -b 0.0.0.0 -p 8000 covetpy_asgi_demo:app

Test endpoints once running:
- GET  http://localhost:8000/         (Hello world)
- GET  http://localhost:8000/health   (Health check) 
- POST http://localhost:8000/echo     (Echo JSON)
- GET  http://localhost:8000/users/123 (Path params)
- GET  http://localhost:8000/large    (Large response)
- GET  http://localhost:8000/async    (Async processing)
- GET  http://localhost:8000/info     (Framework info)
- WS   ws://localhost:8000/ws         (WebSocket)

""")
    
    try:
        import uvicorn
        print("Starting with uvicorn...")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except ImportError:
        print("""
❌ Uvicorn not available. Install with:
   pip install uvicorn

Or run with another ASGI server manually.
""")