#!/usr/bin/env python3
"""
CovetPy Middleware Example

Demonstrates how to create and use middleware in CovetPy.
Shows request/response processing, logging, and error handling.

Run with:
    python examples/middleware_demo.py

Or with uvicorn:
    pip install uvicorn[standard]
    uvicorn examples.middleware_demo:app --reload
"""

import time
import json
from typing import Callable
from covet import CovetPy, Request, Response, BaseHTTPMiddleware


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all incoming requests with timing information."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log request
        print(f"[REQUEST] {request.method} {request.url}")
        print(f"[HEADERS] {dict(request.headers)}")
        
        # Process request
        response = await call_next(request)
        
        # Calculate timing
        process_time = time.time() - start_time
        
        # Log response
        print(f"[RESPONSE] {response.status_code} ({process_time:.3f}s)")
        print(f"[RESPONSE HEADERS] {dict(response.headers)}")
        print("-" * 50)
        
        # Add timing header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """Add CORS headers to responses."""
    
    def __init__(self, app, allowed_origins=None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response("", status_code=200)
        else:
            response = await call_next(request)
        
        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Catch and handle errors gracefully."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            
            # Return JSON error response
            error_response = {
                "error": True,
                "message": str(e),
                "type": type(e).__name__,
                "path": str(request.url)
            }
            
            response = Response(
                json.dumps(error_response),
                status_code=500,
                headers={"Content-Type": "application/json"}
            )
            return response


# Create application with debug mode
app = CovetPy(debug=True)

# Add middleware (order matters - first added is outermost)
app.middleware(RequestLoggingMiddleware)
app.middleware(CORSMiddleware)
app.middleware(ErrorHandlingMiddleware)


@app.get("/")
async def home():
    """Simple home endpoint."""
    return {
        "message": "CovetPy Middleware Demo",
        "features": [
            "Request logging",
            "CORS support", 
            "Error handling",
            "Timing headers"
        ]
    }


@app.get("/slow")
async def slow_endpoint():
    """Endpoint that takes time to process."""
    import asyncio
    await asyncio.sleep(2)  # Simulate slow processing
    return {"message": "This endpoint took 2 seconds to process"}


@app.get("/error")
async def error_endpoint():
    """Endpoint that deliberately raises an error."""
    raise ValueError("This is a deliberate error for testing middleware")


@app.post("/echo")
async def echo_endpoint(request: Request):
    """Echo back the request data."""
    try:
        data = await request.json()
    except Exception:
        data = {"error": "Could not parse JSON"}
    
    return {
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "data": data
    }


@app.get("/headers")
async def headers_endpoint(request: Request):
    """Show all request headers."""
    return {
        "headers": dict(request.headers),
        "user_agent": request.headers.get("user-agent", "Unknown"),
        "content_type": request.headers.get("content-type", "Not specified")
    }


if __name__ == "__main__":
    print("=" * 60)
    print("CovetPy Middleware Demo")
    print("=" * 60)
    print("This example demonstrates middleware functionality:")
    print()
    print("Middleware Stack:")
    print("1. RequestLoggingMiddleware - Logs all requests/responses")
    print("2. CORSMiddleware - Adds CORS headers")
    print("3. ErrorHandlingMiddleware - Handles errors gracefully")
    print()
    print("Available endpoints:")
    print("  GET  /           - Home page with info")
    print("  GET  /slow       - Slow endpoint (2s delay)")
    print("  GET  /error      - Triggers an error")
    print("  POST /echo       - Echo request data")
    print("  GET  /headers    - Show request headers")
    print()
    print("Try these requests:")
    print("  curl http://localhost:8000/")
    print("  curl http://localhost:8000/slow")
    print("  curl http://localhost:8000/error") 
    print("  curl -X POST -H 'Content-Type: application/json' -d '{\"test\": \"data\"}' http://localhost:8000/echo")
    print()
    
    try:
        app.run(host="127.0.0.1", port=8000)
    except Exception as e:
        print(f"Failed to start server: {e}")
        print("\nTo run this example:")
        print("1. Install uvicorn: pip install uvicorn[standard]")
        print("2. Run: python examples/middleware_demo.py")
        print("3. Or: uvicorn examples.middleware_demo:app --reload")