#!/usr/bin/env python3
"""
Hello World CovetPy Application
Demonstrates the working CovetPy framework
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Try to use the existing CovetPy structure first
    from covet.core.app import create_app
    print("Using CovetPy core app")
    app = create_app()
except ImportError as e:
    print(f"CovetPy core import failed: {e}")
    print("Falling back to minimal implementation...")
    
    # Fall back to our minimal implementation
    from minimal_covet import create_app, Request, Response
    app = create_app()


@app.get("/")
async def hello_world(request):
    """Simple hello world endpoint"""
    return app.json_response({
        "message": "Hello World from CovetPy!",
        "framework": "CovetPy",
        "version": "0.1.0",
        "path": request.path,
        "method": request.method,
        "status": "Working!"
    })


@app.get("/health")
async def health_check(request):
    """Health check endpoint"""
    return app.json_response({
        "status": "healthy",
        "message": "CovetPy server is running perfectly!",
        "framework": "CovetPy"
    })


@app.get("/info")
async def info(request):
    """Information about the framework"""
    return app.json_response({
        "framework": "CovetPy",
        "description": "Zero-dependency Python web framework",
        "features": [
            "Pure Python implementation",
            "Zero external dependencies",
            "Fast HTTP server",
            "JSON responses",
            "Route decorators",
            "Async support"
        ],
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Hello World"},
            {"path": "/health", "method": "GET", "description": "Health Check"},
            {"path": "/info", "method": "GET", "description": "Framework Info"},
            {"path": "/echo", "method": "POST", "description": "Echo request"}
        ]
    })


@app.post("/echo")
async def echo(request):
    """Echo endpoint for testing POST requests"""
    try:
        data = request.json()
        return app.json_response({
            "echo": data,
            "method": request.method,
            "path": request.path,
            "message": "Successfully echoed your JSON data"
        })
    except Exception:
        return app.json_response({
            "echo": request.text(),
            "method": request.method,
            "path": request.path,
            "message": "Successfully echoed your text data"
        })


if __name__ == "__main__":
    print("="*60)
    print("🚀 CovetPy Hello World Application")
    print("="*60)
    print("Framework: CovetPy")
    print("Description: Zero-dependency Python web framework")
    print("Port: 8000")
    print("="*60)
    print("Available endpoints:")
    print("  GET  / - Hello World")
    print("  GET  /health - Health Check")
    print("  GET  /info - Framework Information")
    print("  POST /echo - Echo Request")
    print("="*60)
    print("Starting server...")
    print("Visit http://127.0.0.1:8000 to test!")
    print("Press Ctrl+C to stop the server")
    print("="*60)
    
    app.run(host="127.0.0.1", port=8000)