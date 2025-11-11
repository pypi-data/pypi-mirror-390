# Blog API Example

A complete REST API built with CovetPy demonstrating:

- User authentication with JWT
- CRUD operations for blog posts and comments
- ORM models with relationships
- Caching for performance
- Pagination and filtering
- Input validation and error handling
- Full test coverage

## Features

- **User Management**: Registration, login, profile management
- **Blog Posts**: Create, read, update, delete posts
- **Comments**: Add comments to posts
- **Categories & Tags**: Organize posts with categories and tags
- **Authentication**: JWT-based authentication and RBAC
- **Caching**: Redis caching for improved performance
- **Pagination**: Efficient pagination for large datasets
- **Search**: Full-text search for posts

## Project Structure

```
blog_api/
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── config.py                # Configuration
├── main.py                  # Application entry point
├── models.py                # Database models
├── schemas.py               # Pydantic schemas
├── auth.py                  # Authentication logic
├── routes/                  # API routes
│   ├── __init__.py
│   ├── users.py             # User routes
│   ├── posts.py             # Post routes
│   └── comments.py          # Comment routes
├── services/                # Business logic
│   ├── __init__.py
│   ├── user_service.py
│   ├── post_service.py
│   └── comment_service.py
└── tests/                   # Test suite
    ├── __init__.py
    ├── test_users.py
    ├── test_posts.py
    └── test_comments.py
```

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL or SQLite
- Redis (optional, for caching)

### Setup

1. Clone or navigate to this directory:

```bash
cd examples/blog_api
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:

```bash
python -m covet migrate
```

6. Create initial data (optional):

```bash
python -m scripts.seed_data
```

## Running the Application

### Development Server

```bash
python main.py
```

The API will be available at http://localhost:8000

### Production Server

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Endpoints

### Authentication

#### Register a new user

```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123!"
}
```

Response:
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePassword123!"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

### Posts

#### List all posts (with pagination)

```bash
GET /api/posts?page=1&limit=20
```

Response:
```json
{
  "posts": [
    {
      "id": 1,
      "title": "Getting Started with CovetPy",
      "slug": "getting-started-with-covetpy",
      "excerpt": "Learn how to build APIs with CovetPy...",
      "content": "Full post content...",
      "author": {
        "id": 1,
        "username": "john_doe"
      },
      "category": {
        "id": 1,
        "name": "Tutorials"
      },
      "tags": ["python", "web-development"],
      "published_at": "2025-10-10T10:00:00Z",
      "created_at": "2025-10-10T09:00:00Z",
      "updated_at": "2025-10-10T09:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3
  }
}
```

#### Get a single post

```bash
GET /api/posts/{post_id}
# or by slug:
GET /api/posts/slug/{slug}
```

#### Create a post (authenticated)

```bash
POST /api/posts
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "My First Post",
  "content": "This is the content of my post...",
  "excerpt": "Brief summary...",
  "category_id": 1,
  "tags": ["python", "tutorial"],
  "published": true
}
```

#### Update a post (authenticated, author only)

```bash
PUT /api/posts/{post_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Updated Title",
  "content": "Updated content..."
}
```

#### Delete a post (authenticated, author only)

```bash
DELETE /api/posts/{post_id}
Authorization: Bearer <access_token>
```

### Comments

#### List comments for a post

```bash
GET /api/posts/{post_id}/comments
```

#### Add a comment (authenticated)

```bash
POST /api/posts/{post_id}/comments
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Great post! Thanks for sharing."
}
```

#### Update a comment (authenticated, author only)

```bash
PUT /api/comments/{comment_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "content": "Updated comment content..."
}
```

#### Delete a comment (authenticated, author only)

```bash
DELETE /api/comments/{comment_id}
Authorization: Bearer <access_token>
```

### Categories

#### List all categories

```bash
GET /api/categories
```

#### Get posts in a category

```bash
GET /api/categories/{category_id}/posts
```

### Tags

#### List all tags

```bash
GET /api/tags
```

#### Get posts with a tag

```bash
GET /api/tags/{tag_name}/posts
```

### Search

#### Search posts

```bash
GET /api/search?q=covetpy&category=tutorials&tags=python
```

## Testing

### Run all tests

```bash
pytest tests/
```

### Run with coverage

```bash
pytest tests/ --cov=. --cov-report=html
```

### Run specific test file

```bash
pytest tests/test_posts.py -v
```

## Example Usage

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Register a user
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "username": "alice",
        "email": "alice@example.com",
        "password": "SecurePass123!"
    }
)
data = response.json()
access_token = data["access_token"]

# Create a post
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(
    f"{BASE_URL}/posts",
    headers=headers,
    json={
        "title": "My First Post",
        "content": "This is my first blog post!",
        "excerpt": "Introduction to blogging",
        "category_id": 1,
        "tags": ["blogging", "first-post"]
    }
)
post = response.json()
print(f"Created post: {post['title']}")

# List all posts
response = requests.get(f"{BASE_URL}/posts?page=1&limit=10")
posts = response.json()
print(f"Found {len(posts['posts'])} posts")

# Add a comment
response = requests.post(
    f"{BASE_URL}/posts/{post['id']}/comments",
    headers=headers,
    json={"content": "Great post!"}
)
comment = response.json()
print(f"Added comment: {comment['content']}")
```

### cURL Examples

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SecurePass123!"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}'

# Create post (replace TOKEN with actual access token)
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My Post","content":"Post content","category_id":1}'

# List posts
curl http://localhost:8000/api/posts?page=1&limit=10

# Get single post
curl http://localhost:8000/api/posts/1
```

## Architecture

### Database Schema

```
users
├── id (PK)
├── username (unique)
├── email (unique)
├── password_hash
├── created_at
└── updated_at

categories
├── id (PK)
├── name
└── slug

posts
├── id (PK)
├── title
├── slug (unique)
├── content
├── excerpt
├── author_id (FK -> users)
├── category_id (FK -> categories)
├── published_at
├── created_at
└── updated_at

tags
├── id (PK)
├── name (unique)
└── slug

post_tags
├── post_id (FK -> posts)
└── tag_id (FK -> tags)

comments
├── id (PK)
├── post_id (FK -> posts)
├── author_id (FK -> users)
├── content
├── created_at
└── updated_at
```

### Caching Strategy

- **Posts List**: Cached for 5 minutes
- **Single Post**: Cached for 15 minutes
- **Comments**: Cached for 5 minutes
- **Categories/Tags**: Cached for 1 hour

Cache is automatically invalidated when content is created, updated, or deleted.

### Security Features

- **Password Hashing**: bcrypt with salt
- **JWT Authentication**: Access + refresh tokens
- **CSRF Protection**: Enabled for state-changing operations
- **Rate Limiting**: 100 requests per minute per IP
- **Input Validation**: Pydantic schemas
- **SQL Injection Prevention**: ORM parameterized queries
- **XSS Protection**: Output sanitization

## Performance

With caching enabled:

- List posts: ~5ms (cached) / ~50ms (uncached)
- Get single post: ~2ms (cached) / ~20ms (uncached)
- Create post: ~30ms
- Add comment: ~25ms

Benchmarks on MacBook Pro M1, PostgreSQL database, Redis cache.

## Configuration

Edit `.env` file:

```env
# Application
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost/blog_db
# Or use SQLite for development:
# DATABASE_URL=sqlite:///./blog.db

# Redis (optional)
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=True

# JWT
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Pagination
DEFAULT_PAGE_SIZE=20
MAX_PAGE_SIZE=100

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60  # seconds
```

## Troubleshooting

### Database Connection Error

```
Error: Could not connect to database
Solution: Check DATABASE_URL in .env file
```

### Redis Connection Error

```
Error: Could not connect to Redis
Solution: Either start Redis or set CACHE_ENABLED=False in .env
```

### Import Errors

```
Error: ModuleNotFoundError
Solution: Make sure all dependencies are installed: pip install -r requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Learn More

- [CovetPy Documentation](https://docs.covetpy.com)
- [ORM Guide](../../docs/tutorials/02-orm-guide.md)
- [Security Guide](../../docs/tutorials/04-security-guide.md)
- [Deployment Guide](../../docs/deployment/docker.md)

## Support

- GitHub Issues: https://github.com/covetpy/covetpy/issues
- Documentation: https://docs.covetpy.com
- Community: https://discord.gg/covetpy
