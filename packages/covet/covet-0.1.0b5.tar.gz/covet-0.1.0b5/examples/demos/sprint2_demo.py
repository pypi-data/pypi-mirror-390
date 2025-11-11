#!/usr/bin/env python3
"""
Sprint 2 Demo - CovetPy Enhanced Features
Showcases database ORM, authentication, and enhanced routing
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from minimal_covet import create_app
from covet.database.simple_orm import (
    DatabaseConnection, create_model, Field, 
    primary_key, text_field, datetime_field, integer_field
)
from covet.security.simple_auth import SimpleAuth, auth_middleware, require_auth, require_role

# Initialize application
app = create_app()

# Initialize database
db = DatabaseConnection("sprint2_demo.db")

# Create User model
User = create_model('users', {
    'id': primary_key(),
    'username': text_field(nullable=False, unique=True),
    'email': text_field(nullable=False),
    'full_name': text_field(),
    'created_at': datetime_field(nullable=False)
}, db)

# Create Post model  
Post = create_model('posts', {
    'id': primary_key(),
    'title': text_field(nullable=False),
    'content': text_field(nullable=False),
    'author_id': integer_field(nullable=False),
    'created_at': datetime_field(nullable=False),
    'published': integer_field(nullable=False)  # SQLite doesn't have boolean
}, db)

# Create tables
User.create_table()
Post.create_table()

# Initialize authentication
auth = SimpleAuth("your-secret-key-here")

# Register a demo admin user
try:
    admin_user = auth.register_user(
        username="admin",
        password="admin123", 
        email="admin@example.com",
        roles=["admin", "user"]
    )
    print("✅ Admin user created: admin/admin123")
except ValueError:
    print("ℹ️  Admin user already exists")

# Register a demo regular user
try:
    regular_user = auth.register_user(
        username="user",
        password="user123",
        email="user@example.com", 
        roles=["user"]
    )
    print("✅ Regular user created: user/user123")
except ValueError:
    print("ℹ️  Regular user already exists")

# Add middleware (would be automatic in full framework)
def apply_middleware(request):
    """Apply authentication middleware"""
    return auth_middleware(auth)(request)

# Root endpoint
@app.get("/")
async def root(request):
    """API information"""
    return app.json_response({
        "message": "CovetPy Sprint 2 Demo API",
        "version": "2.0.0",
        "features": [
            "Enhanced routing with path parameters", 
            "Database ORM with SQLite",
            "JWT Authentication",
            "Role-based access control",
            "CRUD operations"
        ],
        "endpoints": {
            "auth": {
                "POST /auth/login": "Login with username/password",
                "POST /auth/register": "Register new user",
                "GET /auth/me": "Get current user info"
            },
            "users": {
                "GET /users": "List all users (admin only)",
                "GET /users/{id}": "Get user by ID",
                "PUT /users/{id}": "Update user",
                "DELETE /users/{id}": "Delete user (admin only)"
            },
            "posts": {
                "GET /posts": "List all posts",
                "POST /posts": "Create new post (authenticated)",
                "GET /posts/{id}": "Get post by ID",
                "PUT /posts/{id}": "Update post (author only)",
                "DELETE /posts/{id}": "Delete post (author or admin)"
            }
        }
    })

# Authentication endpoints
@app.post("/auth/login") 
async def login(request):
    """Login endpoint"""
    try:
        data = request.json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return app.json_response({
                "error": "Username and password required"
            }, status=400)
        
        user = auth.authenticate(username, password)
        if not user:
            return app.json_response({
                "error": "Invalid credentials"
            }, status=401)
        
        token = auth.create_token(user)
        
        return app.json_response({
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email,
                "roles": user.roles
            }
        })
        
    except Exception as e:
        return app.json_response({
            "error": f"Login failed: {str(e)}"
        }, status=500)

@app.post("/auth/register")
async def register(request):
    """Registration endpoint"""
    try:
        data = request.json()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        
        if not username or not password:
            return app.json_response({
                "error": "Username and password required"
            }, status=400)
        
        user = auth.register_user(username, password, email, roles=["user"])
        
        # Also create user in database
        db_user = User(
            username=username,
            email=email,
            full_name=data.get('full_name', ''),
            created_at=user.created_at.isoformat()
        )
        db_user.save()
        
        return app.json_response({
            "message": "Registration successful",
            "user": {
                "id": user.user_id,
                "username": user.username,
                "email": user.email
            }
        })
        
    except ValueError as e:
        return app.json_response({
            "error": str(e)
        }, status=400)
    except Exception as e:
        return app.json_response({
            "error": f"Registration failed: {str(e)}"
        }, status=500)

@app.get("/auth/me")
async def get_current_user(request):
    """Get current user info"""
    request = apply_middleware(request)
    
    if not request.user:
        return app.json_response({
            "error": "Authentication required"
        }, status=401)
    
    return app.json_response({
        "user": {
            "id": request.user.user_id,
            "username": request.user.username,
            "email": request.user.email,
            "roles": request.user.roles
        }
    })

# User endpoints
@app.get("/users")
async def list_users(request):
    """List all users (admin only)"""
    request = apply_middleware(request)
    
    if not request.user:
        return app.json_response({"error": "Authentication required"}, status=401)
    
    if "admin" not in request.user.roles:
        return app.json_response({"error": "Admin role required"}, status=403)
    
    users = User.all()
    return app.json_response({
        "users": [user.to_dict() for user in users]
    })

@app.get("/users/{id}")
async def get_user(request):
    """Get user by ID"""
    user_id = request.path_params.get('id')
    if not user_id:
        return app.json_response({"error": "User ID required"}, status=400)
    
    user = User.get(user_id)
    if not user:
        return app.json_response({"error": "User not found"}, status=404)
    
    return app.json_response({"user": user.to_dict()})

# Post endpoints
@app.get("/posts")
async def list_posts(request):
    """List all published posts"""
    posts = Post.filter(published=1)
    return app.json_response({
        "posts": [post.to_dict() for post in posts]
    })

@app.post("/posts")
async def create_post(request):
    """Create new post (authenticated users only)"""
    request = apply_middleware(request)
    
    if not request.user:
        return app.json_response({"error": "Authentication required"}, status=401)
    
    try:
        data = request.json()
        title = data.get('title')
        content = data.get('content')
        published = data.get('published', False)
        
        if not title or not content:
            return app.json_response({
                "error": "Title and content required"
            }, status=400)
        
        # Find user in database by username
        db_users = User.filter(username=request.user.username)
        if not db_users:
            return app.json_response({
                "error": "Database user not found"
            }, status=400)
        
        db_user = db_users[0]
        
        post = Post(
            title=title,
            content=content,
            author_id=db_user.id,
            published=1 if published else 0
        )
        post.save()
        
        return app.json_response({
            "message": "Post created successfully",
            "post": post.to_dict()
        })
        
    except Exception as e:
        return app.json_response({
            "error": f"Failed to create post: {str(e)}"
        }, status=500)

@app.get("/posts/{id}")
async def get_post(request):
    """Get post by ID"""
    post_id = request.path_params.get('id')
    if not post_id:
        return app.json_response({"error": "Post ID required"}, status=400)
    
    post = Post.get(post_id)
    if not post:
        return app.json_response({"error": "Post not found"}, status=404)
    
    return app.json_response({"post": post.to_dict()})

# Health check with database status
@app.get("/health")
async def health_check(request):
    """Enhanced health check"""
    try:
        # Test database connection
        User.all()
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return app.json_response({
        "status": "healthy",
        "version": "Sprint 2",
        "database": db_status,
        "authentication": "enabled",
        "features": ["ORM", "JWT", "Path Parameters", "Role-based Access"]
    })

# API documentation
@app.get("/docs")
async def api_docs(request):
    """API documentation"""
    return app.json_response({
        "title": "CovetPy Sprint 2 API",
        "description": "Enhanced web framework with database and authentication",
        "version": "2.0.0",
        "authentication": {
            "type": "JWT Bearer Token",
            "header": "Authorization: Bearer <token>",
            "endpoints": {
                "login": "POST /auth/login",
                "register": "POST /auth/register"
            }
        },
        "models": {
            "User": {
                "fields": ["id", "username", "email", "full_name", "created_at"]
            },
            "Post": {
                "fields": ["id", "title", "content", "author_id", "created_at", "published"]
            }
        },
        "examples": {
            "login": {
                "request": {"username": "admin", "password": "admin123"},
                "response": {"token": "jwt-token", "user": "user-object"}
            },
            "create_post": {
                "headers": {"Authorization": "Bearer <token>"},
                "request": {"title": "My Post", "content": "Post content", "published": True}
            }
        }
    })

if __name__ == "__main__":
    print("🚀 CovetPy Sprint 2 Demo")
    print("=" * 50)
    print("Enhanced Features:")
    print("  ✅ Database ORM with SQLite")
    print("  ✅ JWT Authentication") 
    print("  ✅ Role-based Access Control")
    print("  ✅ Path Parameters (/users/{id})")
    print("  ✅ CRUD Operations")
    print("  ✅ Middleware Support")
    print("=" * 50)
    print("Demo Users:")
    print("  👤 admin / admin123 (admin, user roles)")
    print("  👤 user / user123 (user role)")
    print("=" * 50)
    print("Key Endpoints:")
    print("  🔑 POST /auth/login - Login")
    print("  📝 POST /auth/register - Register")
    print("  👥 GET /users - List users (admin)")
    print("  📄 GET /posts - List posts")
    print("  ✍️  POST /posts - Create post (auth)")
    print("  📚 GET /docs - API documentation")
    print("=" * 50)
    print("Server starting on http://127.0.0.1:8000")
    print("Try: curl -X POST http://127.0.0.1:8000/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
    
    app.run(host="127.0.0.1", port=8000)