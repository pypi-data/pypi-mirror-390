"""
Blog API - Main Application

A complete REST API built with CovetPy featuring:
- User authentication with JWT
- Blog posts with categories and tags
- Comments system
- Caching for performance
- Full CRUD operations

Usage:
    python main.py                      # Development server
    gunicorn main:app ...               # Production server
"""

import os
import asyncio
from typing import Optional
from covet import CovetPy
from covet.orm import get_connection
from covet.cache import CacheManager, CacheConfig, CacheBackend
from covet.security import SimpleAuth, auth_middleware
from covet.middleware import CORSMiddleware

# Import models
from models import User, Post, Comment, Category, Tag, init_database

# Configuration
DEBUG = os.getenv('DEBUG', 'True') == 'True'
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./blog.db')
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True') == 'True'

# Create application
app = CovetPy(debug=DEBUG)

# Initialize authentication
auth = SimpleAuth(SECRET_KEY)

# Initialize cache
if CACHE_ENABLED:
    try:
        cache_config = CacheConfig(
            backend=CacheBackend.REDIS if REDIS_URL else CacheBackend.MEMORY,
            key_prefix='blog:',
            default_ttl=300
        )
        cache = CacheManager(cache_config)
    except Exception as e:
        print(f"Warning: Could not initialize cache: {e}")
        print("Falling back to memory cache")
        cache = CacheManager(backend='memory')
else:
    cache = CacheManager(backend='memory')


# ============================================================================
# Authentication Routes
# ============================================================================

@app.post("/api/auth/register")
async def register(request):
    """Register a new user."""
    from covet.security import PasswordHasher
    import json

    # Parse request body
    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    # Validate required fields
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not username or not email or not password:
        return {"error": "username, email, and password are required"}, 400

    # Check if user exists
    existing_user = await User.objects.filter(username=username).first()
    if existing_user:
        return {"error": "Username already taken"}, 400

    existing_email = await User.objects.filter(email=email).first()
    if existing_email:
        return {"error": "Email already registered"}, 400

    # Create user
    hasher = PasswordHasher()
    password_hash = hasher.hash_password(password)

    user = await User.objects.create(
        username=username,
        email=email,
        password_hash=password_hash,
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        bio=data.get('bio', '')
    )

    # Generate tokens
    access_token = auth.create_token({'user_id': user.id, 'username': user.username})

    return {
        "message": "User registered successfully",
        "user": user.to_dict(include_email=True),
        "access_token": access_token
    }, 201


@app.post("/api/auth/login")
async def login(request):
    """Login user."""
    from covet.security import PasswordHasher

    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return {"error": "username and password are required"}, 400

    # Find user
    user = await User.objects.filter(username=username).first()
    if not user:
        return {"error": "Invalid credentials"}, 401

    # Verify password
    hasher = PasswordHasher()
    if not hasher.verify_password(password, user.password_hash):
        return {"error": "Invalid credentials"}, 401

    # Check if user is active
    if not user.is_active:
        return {"error": "Account is inactive"}, 403

    # Generate tokens
    access_token = auth.create_token({'user_id': user.id, 'username': user.username})

    return {
        "message": "Login successful",
        "user": user.to_dict(include_email=True),
        "access_token": access_token
    }


# ============================================================================
# Post Routes
# ============================================================================

@app.get("/api/posts")
async def list_posts(request):
    """List all published posts with pagination."""
    # Parse query parameters
    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 20))
    category_slug = request.query_params.get('category')
    tag_slug = request.query_params.get('tag')
    search = request.query_params.get('q', '').strip()

    # Build query
    query = Post.objects.filter(published=True)

    # Filter by category
    if category_slug:
        category = await Category.objects.filter(slug=category_slug).first()
        if category:
            query = query.filter(category=category)

    # Filter by search
    if search:
        from covet.orm import Q
        query = query.filter(
            Q(title__icontains=search) | Q(content__icontains=search)
        )

    # Get total count
    total = await query.count()

    # Paginate
    offset = (page - 1) * limit
    posts = await query.offset(offset).limit(limit).select_related('author', 'category').all()

    # Convert to dict
    posts_data = []
    for post in posts:
        post_dict = post.to_dict(include_content=False)
        # Get tags
        tags = await post.get_tags()
        post_dict['tags'] = [tag.to_dict() for tag in tags]
        posts_data.append(post_dict)

    return {
        "posts": posts_data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    }


@app.get("/api/posts/{post_id}")
async def get_post(post_id: int):
    """Get a single post by ID."""
    post = await Post.objects.filter(id=post_id, published=True).select_related('author', 'category').first()

    if not post:
        return {"error": "Post not found"}, 404

    # Increment view count
    await post.increment_view_count()

    # Get post data
    post_dict = post.to_dict(include_content=True)

    # Get tags
    tags = await post.get_tags()
    post_dict['tags'] = [tag.to_dict() for tag in tags]

    # Get comments count
    post_dict['comments_count'] = await post.get_comments_count()

    return {"post": post_dict}


@app.get("/api/posts/slug/{slug}")
async def get_post_by_slug(slug: str):
    """Get a post by slug."""
    post = await Post.objects.filter(slug=slug, published=True).select_related('author', 'category').first()

    if not post:
        return {"error": "Post not found"}, 404

    # Increment view count
    await post.increment_view_count()

    # Get post data
    post_dict = post.to_dict(include_content=True)

    # Get tags
    tags = await post.get_tags()
    post_dict['tags'] = [tag.to_dict() for tag in tags]

    # Get comments count
    post_dict['comments_count'] = await post.get_comments_count()

    return {"post": post_dict}


@app.post("/api/posts")
async def create_post(request):
    """Create a new post (authenticated)."""
    # Check authentication
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return {"error": "Authentication required"}, 401

    try:
        payload = auth.verify_token(token)
        user_id = payload.get('user_id')
    except Exception:
        return {"error": "Invalid token"}, 401

    # Get user
    user = await User.objects.get(id=user_id)

    # Parse request body
    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    # Validate required fields
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return {"error": "title and content are required"}, 400

    # Generate slug
    from models import slugify
    slug = slugify(title)

    # Check if slug exists
    existing_post = await Post.objects.filter(slug=slug).first()
    if existing_post:
        # Append number to slug
        counter = 1
        while await Post.objects.filter(slug=f"{slug}-{counter}").first():
            counter += 1
        slug = f"{slug}-{counter}"

    # Get category
    category = None
    category_id = data.get('category_id')
    if category_id:
        category = await Category.objects.get(id=category_id)

    # Create post
    from datetime import datetime
    published = data.get('published', False)

    post = await Post.objects.create(
        title=title,
        slug=slug,
        content=content,
        excerpt=data.get('excerpt', '')[:500],  # Limit excerpt length
        author=user,
        category=category,
        published=published,
        published_at=datetime.now() if published else None
    )

    # Add tags
    tag_names = data.get('tags', [])
    for tag_name in tag_names:
        tag_slug = slugify(tag_name)
        tag, created = await Tag.objects.get_or_create(
            slug=tag_slug,
            defaults={'name': tag_name}
        )
        await post.tags.add(tag)

    return {
        "message": "Post created successfully",
        "post": post.to_dict()
    }, 201


# ============================================================================
# Comment Routes
# ============================================================================

@app.get("/api/posts/{post_id}/comments")
async def list_comments(post_id: int, request):
    """List comments for a post."""
    # Check if post exists
    post = await Post.objects.get(id=post_id)
    if not post:
        return {"error": "Post not found"}, 404

    # Get comments
    comments = await Comment.objects.filter(
        post=post,
        parent__isnull=True  # Only top-level comments
    ).select_related('author').order_by('-created_at').all()

    # Convert to dict
    comments_data = []
    for comment in comments:
        comment_dict = comment.to_dict()
        comment_dict['replies_count'] = await comment.get_replies_count()
        comments_data.append(comment_dict)

    return {
        "comments": comments_data,
        "count": len(comments_data)
    }


@app.post("/api/posts/{post_id}/comments")
async def create_comment(post_id: int, request):
    """Add a comment to a post (authenticated)."""
    # Check authentication
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return {"error": "Authentication required"}, 401

    try:
        payload = auth.verify_token(token)
        user_id = payload.get('user_id')
    except Exception:
        return {"error": "Invalid token"}, 401

    # Get user and post
    user = await User.objects.get(id=user_id)
    post = await Post.objects.get(id=post_id)

    # Parse request body
    try:
        data = await request.json()
    except Exception:
        return {"error": "Invalid JSON"}, 400

    content = data.get('content', '').strip()
    if not content:
        return {"error": "content is required"}, 400

    # Create comment
    comment = await Comment.objects.create(
        post=post,
        author=user,
        content=content
    )

    return {
        "message": "Comment added successfully",
        "comment": comment.to_dict()
    }, 201


# ============================================================================
# Category and Tag Routes
# ============================================================================

@app.get("/api/categories")
async def list_categories():
    """List all categories."""
    categories = await Category.objects.all()
    return {
        "categories": [cat.to_dict() for cat in categories],
        "count": len(categories)
    }


@app.get("/api/tags")
async def list_tags():
    """List all tags."""
    tags = await Tag.objects.all()
    return {
        "tags": [tag.to_dict() for tag in tags],
        "count": len(tags)
    }


# ============================================================================
# Health Check
# ============================================================================

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Blog API",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """API root with documentation."""
    return {
        "message": "Blog API",
        "version": "1.0.0",
        "endpoints": {
            "authentication": {
                "POST /api/auth/register": "Register a new user",
                "POST /api/auth/login": "Login user"
            },
            "posts": {
                "GET /api/posts": "List all posts (paginated)",
                "GET /api/posts/{id}": "Get a single post",
                "GET /api/posts/slug/{slug}": "Get post by slug",
                "POST /api/posts": "Create a post (authenticated)"
            },
            "comments": {
                "GET /api/posts/{id}/comments": "List comments for a post",
                "POST /api/posts/{id}/comments": "Add comment (authenticated)"
            },
            "categories": {
                "GET /api/categories": "List all categories"
            },
            "tags": {
                "GET /api/tags": "List all tags"
            }
        },
        "documentation": "https://docs.covetpy.com"
    }


# ============================================================================
# Application Startup/Shutdown
# ============================================================================

@app.on_event("startup")
async def startup():
    """Run on application startup."""
    print("Starting Blog API...")

    # Initialize database
    try:
        await init_database()
        print("✓ Database initialized")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")

    # Connect cache
    if CACHE_ENABLED:
        try:
            await cache.connect()
            print("✓ Cache connected")
        except Exception as e:
            print(f"✗ Cache connection failed: {e}")

    print("✓ Blog API started successfully")
    print(f"  Running on http://127.0.0.1:8000")
    print(f"  Debug mode: {DEBUG}")
    print(f"  Database: {DATABASE_URL}")
    print(f"  Cache: {CACHE_ENABLED}")


@app.on_event("shutdown")
async def shutdown():
    """Run on application shutdown."""
    print("Shutting down Blog API...")

    # Disconnect cache
    if CACHE_ENABLED:
        try:
            await cache.disconnect()
            print("✓ Cache disconnected")
        except Exception as e:
            print(f"✗ Cache disconnection failed: {e}")

    print("✓ Blog API shut down successfully")


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Blog API - CovetPy Example Application")
    print("=" * 60)
    print()

    # Run the application
    app.run(
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", 8000)),
        debug=DEBUG
    )
