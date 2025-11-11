#!/usr/bin/env python3
"""
Working Middleware Example for CovetPy
======================================
Demonstrates middleware integration with the framework.
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet import Covet
from covet.middleware.base import (
    CORSMiddleware,
    LoggingMiddleware,
    SessionMiddleware,
    ErrorHandlingMiddleware
)

# Create app with debug mode
app = Covet(debug=True)

# Add middleware to the app
# Note: Middleware executes in the order added
app.add_middleware(ErrorHandlingMiddleware(debug=True))
app.add_middleware(CORSMiddleware(origins="*", methods=["GET", "POST", "PUT", "DELETE"]))
app.add_middleware(LoggingMiddleware())
app.add_middleware(SessionMiddleware())

# Define routes
@app.get('/')
async def home(request):
    """Home page"""
    return {
        'message': 'Welcome to CovetPy with Middleware!',
        'middleware': [
            'CORS enabled',
            'Logging active',
            'Session management',
            'Error handling'
        ]
    }

@app.get('/session')
async def session_demo(request):
    """Demonstrate session middleware"""
    # Get or create visit count
    if hasattr(request, 'session'):
        count = request.session.get('visit_count', 0)
        request.session['visit_count'] = count + 1

        return {
            'session_id': getattr(request, 'session_id', 'unknown'),
            'visit_count': count + 1,
            'session_data': request.session
        }
    else:
        return {'error': 'Session middleware not active'}

@app.get('/error')
async def error_demo(request):
    """Demonstrate error handling middleware"""
    raise ValueError("This is a test error to show error handling!")

@app.post('/data')
async def post_data(request):
    """Demonstrate POST with CORS"""
    data = await request.json()
    return {
        'received': data,
        'method': request.method,
        'headers': dict(request.headers)
    }

@app.get('/protected')
async def protected_route(request):
    """Example of a route that could use authentication middleware"""
    # In a real app, AuthenticationMiddleware would check tokens
    user = getattr(request, 'user', None)

    if user:
        return {'message': f'Hello {user}!'}
    else:
        return {'message': 'This route could be protected with AuthenticationMiddleware'}

# Main entry point
if __name__ == '__main__':
    print("\n" + "="*60)
    print("CovetPy Middleware Example")
    print("="*60)
    print("\nMiddleware Stack:")
    print("1. ErrorHandlingMiddleware - Catches and formats errors")
    print("2. CORSMiddleware - Adds CORS headers")
    print("3. LoggingMiddleware - Logs requests/responses")
    print("4. SessionMiddleware - Manages sessions")

    print("\nAvailable Routes:")
    print("GET  / - Home page")
    print("GET  /session - Session demo (tracks visits)")
    print("GET  /error - Error handling demo")
    print("POST /data - CORS demo")
    print("GET  /protected - Authentication example")

    print("\nStarting server on http://localhost:8000")
    print("Press Ctrl+C to stop")
    print("-"*60 + "\n")

    # Run the app
    app.run(host='127.0.0.1', port=8000)