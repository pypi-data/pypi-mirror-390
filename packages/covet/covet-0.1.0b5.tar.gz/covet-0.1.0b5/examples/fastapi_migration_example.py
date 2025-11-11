"""
FastAPI to Covet Migration Example

This file demonstrates a complete migration from FastAPI to Covet,
showing before/after code for common patterns.

Run this example:
    # Install dependencies
    pip install covetpy pydantic

    # Run FastAPI version (commented out)
    # uvicorn fastapi_migration_example:fastapi_app --reload

    # Run Covet version
    python fastapi_migration_example.py
"""

# ==============================================================================
# BEFORE: FastAPI Implementation
# ==============================================================================

"""
# File: fastapi_app.py (BEFORE migration)

from fastapi import FastAPI, Request, Response, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import uvicorn

# ===== FastAPI App Setup =====
fastapi_app = FastAPI(
    title="Blog API",
    description="RESTful blog API with authentication",
    version="1.0.0"
)

# CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Pydantic Models (FastAPI) =====

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    slug: str
    created_at: str
    tags: List[str]


# ===== Database (Mock for example) =====

users_db = {}
posts_db = {}
sessions_db = {}


# ===== Authentication Helpers (FastAPI) =====

def verify_token(token: str) -> Optional[dict]:
    \"\"\"Verify session token and return user data.\"\"\"
    return sessions_db.get(token)


async def get_current_user(request: Request) -> dict:
    \"\"\"
    Dependency: Get current authenticated user.
    FastAPI automatically injects this.
    \"\"\"
    # Get token from cookies (FastAPI - cookies is a dict)
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user


# ===== Routes (FastAPI) =====

@fastapi_app.get("/")
async def root():
    \"\"\"Root endpoint.\"\"\"
    return {"message": "Blog API - FastAPI Version"}


@fastapi_app.post("/api/auth/register")
async def register(user: UserCreate):
    \"\"\"
    Register a new user.
    FastAPI automatically parses and validates request body.
    \"\"\"
    # Check if user exists
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user (mock)
    user_id = len(users_db) + 1
    users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": f"hashed_{user.password}",  # Mock hashing
    }

    return {"user_id": user_id, "username": user.username}


@fastapi_app.post("/api/auth/login")
async def login(username: str, password: str, response: Response):
    \"\"\"
    Login and set session cookie.
    FastAPI automatically extracts form parameters.
    \"\"\"
    user = users_db.get(username)
    if not user or user["password_hash"] != f"hashed_{password}":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    token = f"token_{user['id']}"
    sessions_db[token] = user

    # Set cookie (FastAPI)
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=3600,
    )

    return {"message": "Logged in successfully"}


@fastapi_app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    \"\"\"
    Get current user profile.
    FastAPI automatically injects current_user via Depends.
    \"\"\"
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
    }


@fastapi_app.post("/api/posts", response_model=PostResponse)
async def create_post(
    post: PostCreate,
    current_user: dict = Depends(get_current_user)
):
    \"\"\"
    Create a blog post.
    FastAPI automatically parses JSON body and validates with Pydantic.
    \"\"\"
    from datetime import datetime

    post_id = len(posts_db) + 1

    # Generate slug from title
    slug = post.title.lower().replace(" ", "-")

    new_post = {
        "id": post_id,
        "title": post.title,
        "content": post.content,
        "author_id": current_user["id"],
        "slug": slug,
        "created_at": datetime.now().isoformat(),
        "tags": post.tags,
    }

    posts_db[post_id] = new_post

    return new_post


@fastapi_app.get("/api/posts")
async def list_posts(
    limit: int = 10,
    offset: int = 0,
    tag: Optional[str] = None
):
    \"\"\"
    List blog posts with pagination.
    FastAPI automatically extracts query parameters.
    \"\"\"
    all_posts = list(posts_db.values())

    # Filter by tag
    if tag:
        all_posts = [p for p in all_posts if tag in p.get("tags", [])]

    # Paginate
    paginated = all_posts[offset : offset + limit]

    return {
        "posts": paginated,
        "total": len(all_posts),
        "limit": limit,
        "offset": offset,
    }


@fastapi_app.get("/api/posts/{post_id}")
async def get_post(post_id: int):
    \"\"\"
    Get a single post by ID.
    FastAPI automatically converts path param to int.
    \"\"\"
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@fastapi_app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    \"\"\"
    Upload a file.
    FastAPI automatically handles multipart/form-data.
    \"\"\"
    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }


# Catch-all OPTIONS for CORS (FastAPI supports {path:path})
@fastapi_app.route("/{path:path}", methods=["OPTIONS"])
async def handle_options(path: str):
    \"\"\"Handle CORS preflight for all routes.\"\"\"
    return Response(status_code=200)


if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
"""

# ==============================================================================
# AFTER: Covet Implementation
# ==============================================================================

from covet import Covet, Request, Response
from covet.exceptions import HTTPException
from covet.middleware import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ===== Covet App Setup =====
app = Covet(
    title="Blog API",
    description="RESTful blog API with authentication",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Pydantic Models (Same as FastAPI) =====

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class PostCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    slug: str
    created_at: str
    tags: List[str]


# ===== Database (Mock for example) =====

users_db = {}
posts_db = {}
sessions_db = {}


# ===== Authentication Helpers (Covet) =====

def verify_token(token: str) -> Optional[dict]:
    """Verify session token and return user data."""
    return sessions_db.get(token)


async def get_current_user(request: Request) -> dict:
    """
    Get current authenticated user from request.
    Covet: Must be called explicitly in route handlers.
    """
    # CHANGE #1: request.cookies() instead of request.cookies
    # In Covet, cookies is a function that returns a dict
    token = request.cookies().get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")

    return user


# ===== Routes (Covet) =====

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Blog API - Covet Version"}


@app.post("/api/auth/register")
async def register(request: Request):
    """
    Register a new user.

    CHANGE #2: Must manually parse request body in Covet.
    FastAPI does this automatically via dependency injection.
    """
    # Parse JSON body manually
    data = await request.json()

    # Validate with Pydantic
    user = UserCreate(**data)

    # Check if user exists
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Create user (mock)
    user_id = len(users_db) + 1
    users_db[user.username] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": f"hashed_{user.password}",  # Mock hashing
    }

    return {"user_id": user_id, "username": user.username}


@app.post("/api/auth/login")
async def login(request: Request):
    """
    Login and set session cookie.

    CHANGE #3: Must manually parse form data in Covet.
    """
    # Parse form data
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    user = users_db.get(username)
    if not user or user["password_hash"] != f"hashed_{password}":
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create session
    token = f"token_{user['id']}"
    sessions_db[token] = user

    # Set cookie (same as FastAPI)
    response = Response({"message": "Logged in successfully"})
    response.set_cookie(
        key="session_token",
        value=token,
        httponly=True,
        max_age=3600,
    )

    return response


@app.get("/api/profile")
async def get_profile(request: Request):
    """
    Get current user profile.

    CHANGE #4: No automatic dependency injection in Covet.
    Must call get_current_user() manually.
    """
    current_user = await get_current_user(request)

    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
    }


@app.post("/api/posts")
async def create_post(request: Request):
    """
    Create a blog post.

    CHANGE #5: Manual JSON parsing and auth check in Covet.
    """
    # Check authentication
    current_user = await get_current_user(request)

    # Parse and validate JSON body
    data = await request.json()
    post = PostCreate(**data)

    from datetime import datetime

    post_id = len(posts_db) + 1

    # Generate slug from title
    slug = post.title.lower().replace(" ", "-")

    new_post = {
        "id": post_id,
        "title": post.title,
        "content": post.content,
        "author_id": current_user["id"],
        "slug": slug,
        "created_at": datetime.now().isoformat(),
        "tags": post.tags,
    }

    posts_db[post_id] = new_post

    return new_post


@app.get("/api/posts")
async def list_posts(request: Request):
    """
    List blog posts with pagination.

    CHANGE #6: Must manually extract query parameters in Covet.
    """
    # Extract query parameters
    limit = int(request.query_params.get("limit", "10"))
    offset = int(request.query_params.get("offset", "0"))
    tag = request.query_params.get("tag")

    all_posts = list(posts_db.values())

    # Filter by tag
    if tag:
        all_posts = [p for p in all_posts if tag in p.get("tags", [])]

    # Paginate
    paginated = all_posts[offset : offset + limit]

    return {
        "posts": paginated,
        "total": len(all_posts),
        "limit": limit,
        "offset": offset,
    }


@app.get("/api/posts/<int:post_id>")
async def get_post(request: Request, post_id: int):
    """
    Get a single post by ID.

    CHANGE #7: Path parameters passed as function arguments in Covet.
    Syntax: <int:post_id> instead of {post_id}
    """
    post = posts_db.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@app.post("/api/upload")
async def upload_file(request: Request):
    """
    Upload a file.

    CHANGE #8: Must manually parse multipart form data in Covet.
    """
    # Parse multipart form
    form = await request.form()
    file = form.get("file")

    if not file:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
    }


# CHANGE #9: Catch-all OPTIONS not supported yet - use middleware
@app.middleware("http")
async def cors_middleware(request, call_next):
    """
    Handle CORS preflight for all routes.

    Covet doesn't support {path:path} syntax yet, so we use middleware
    to handle OPTIONS requests globally.
    """
    if request.method == "OPTIONS":
        return Response(
            status=200,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    response = await call_next(request)

    # Add CORS headers to all responses
    response.headers["Access-Control-Allow-Origin"] = "*"

    return response


# ==============================================================================
# Summary of Changes: FastAPI → Covet
# ==============================================================================

"""
MIGRATION SUMMARY
=================

1. Cookie Access:
   FastAPI: request.cookies.get("token")
   Covet:   request.cookies().get("token")  # Function call!

2. Request Body Parsing:
   FastAPI: async def handler(user: UserCreate)  # Automatic
   Covet:   data = await request.json(); user = UserCreate(**data)  # Manual

3. Form Data:
   FastAPI: async def handler(username: str, password: str)  # Automatic
   Covet:   form = await request.form(); username = form.get("username")  # Manual

4. Query Parameters:
   FastAPI: async def handler(limit: int = 10)  # Automatic
   Covet:   limit = int(request.query_params.get("limit", "10"))  # Manual

5. Path Parameters:
   FastAPI: @app.get("/posts/{post_id}"); async def handler(post_id: int)
   Covet:   @app.get("/posts/<int:post_id>"); async def handler(request, post_id: int)

6. Dependency Injection:
   FastAPI: current_user: dict = Depends(get_current_user)  # Automatic
   Covet:   current_user = await get_current_user(request)  # Manual

7. File Uploads:
   FastAPI: async def handler(file: UploadFile = File(...))  # Automatic
   Covet:   form = await request.form(); file = form.get("file")  # Manual

8. Catch-All Routes:
   FastAPI: @app.route("/{path:path}", methods=["OPTIONS"])  # Supported
   Covet:   Use middleware for OPTIONS handling  # Workaround

9. Response Objects:
   FastAPI: Return dict or Response object
   Covet:   Same - return dict or Response object

10. Exception Handling:
    FastAPI: raise HTTPException(status_code=404)
    Covet:   raise HTTPException(status_code=404)  # Same!


BENEFITS OF COVET
=================

1. Performance: 40x faster routing and HTTP handling (Rust-based)
2. Built-in ORM: Django-style ORM included
3. Simpler: Less magic, more explicit
4. Async-First: Built for asyncio from the ground up
5. Production Ready: Enterprise features out of the box


MIGRATION CHECKLIST
===================

✅ Update cookie access: request.cookies → request.cookies()
✅ Add manual JSON parsing: await request.json()
✅ Add manual form parsing: await request.form()
✅ Add manual query param extraction: request.query_params.get()
✅ Update path param syntax: {param} → <type:param>
✅ Remove Depends() - call functions directly
✅ Replace catch-all routes with middleware
✅ Test all endpoints thoroughly
✅ Update authentication flows
✅ Verify CORS handling
"""


if __name__ == "__main__":
    print("=" * 80)
    print("FastAPI to Covet Migration Example")
    print("=" * 80)
    print()
    print("This example shows:")
    print("  - User registration and login")
    print("  - Session-based authentication")
    print("  - CRUD operations for blog posts")
    print("  - File uploads")
    print("  - Query parameters and pagination")
    print("  - CORS handling")
    print()
    print("Key Differences:")
    print("  1. request.cookies() instead of request.cookies")
    print("  2. Manual JSON/form parsing instead of automatic")
    print("  3. Explicit authentication checks instead of Depends()")
    print("  4. Middleware for OPTIONS instead of catch-all routes")
    print()
    print("To run this example:")
    print("  python examples/fastapi_migration_example.py")
    print()
    print("=" * 80)

    # Start Covet app
    app.run(host="0.0.0.0", port=8000)
