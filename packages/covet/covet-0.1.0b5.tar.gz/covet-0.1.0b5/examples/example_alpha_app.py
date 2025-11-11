#!/usr/bin/env python3
"""
Example Alpha Application - Demonstrates basic CovetPy functionality
"""
import sys
sys.path.insert(0, 'src')

from covet import CovetPy

# Create application
app = CovetPy(debug=True)

# Define routes
@app.route("/")
async def home(request):
    """Home page"""
    return {
        "message": "Welcome to CovetPy Alpha v0.1.0!",
        "status": "operational",
        "framework": "CovetPy",
        "version": "0.1.0-alpha"
    }

@app.get("/health")
async def health_check(request):
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "covetpy-alpha"
    }

@app.get("/api/users/{user_id}")
async def get_user(request, user_id: int):
    """Get user by ID"""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "type": "example"
    }

@app.post("/api/users")
async def create_user(request):
    """Create a new user"""
    # In a real app, this would parse request body
    return {
        "message": "User created (example)",
        "status": "success"
    }

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CovetPy Alpha v0.1.0 - Example Application")
    print("="*60)
    print("\nApplication configured with 4 routes:")
    print("  - GET  /")
    print("  - GET  /health")
    print("  - GET  /api/users/{user_id}")
    print("  - POST /api/users")
    print("\n✅ Application ready to run!")
    print("="*60 + "\n")

    # Note: Requires uvicorn to actually run
    # To run: uvicorn example_alpha_app:app --host 0.0.0.0 --port 8000
