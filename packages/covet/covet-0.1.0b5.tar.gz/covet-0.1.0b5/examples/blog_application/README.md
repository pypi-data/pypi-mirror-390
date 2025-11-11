# CovetPy Blog Application Example

A complete, production-ready blog application built with CovetPy, demonstrating:

- User authentication and authorization
- Post creation with rich text
- Comments and nested replies
- Tags and categories
- Search functionality
- Image uploads
- Email notifications
- RSS feeds
- RESTful API
- Admin panel

## Features

### User Management
- User registration and login
- JWT authentication
- Password reset via email
- User profiles with avatars
- Role-based permissions (admin, author, reader)

### Blog Posts
- Create, read, update, delete posts
- Rich text editor support
- Draft and published states
- Scheduled publishing
- SEO-friendly URLs (slugs)
- Image uploads
- View count tracking

### Comments
- Nested comments (replies)
- Upvote/downvote
- Spam detection
- Comment moderation
- Email notifications

### Tags and Categories
- Multiple tags per post
- Hierarchical categories
- Tag cloud
- Filter posts by tag/category

### Search
- Full-text search
- Search suggestions
- Recent searches

## Installation

```bash
# Clone repository
git clone https://github.com/covetpy/examples
cd examples/blog_application

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database
createdb blog_db

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/password-reset` - Request password reset
- `POST /api/auth/password-reset-confirm` - Confirm password reset

### Posts
- `GET /api/posts/` - List posts
- `POST /api/posts/` - Create post (auth required)
- `GET /api/posts/{id}/` - Get post detail
- `PUT /api/posts/{id}/` - Update post (author/admin)
- `DELETE /api/posts/{id}/` - Delete post (author/admin)
- `GET /api/posts/search?q=query` - Search posts

### Comments
- `GET /api/posts/{id}/comments/` - List comments for post
- `POST /api/posts/{id}/comments/` - Add comment
- `POST /api/comments/{id}/reply/` - Reply to comment
- `PUT /api/comments/{id}/` - Edit comment (author)
- `DELETE /api/comments/{id}/` - Delete comment (author/admin)

### Tags & Categories
- `GET /api/tags/` - List tags
- `GET /api/categories/` - List categories
- `GET /api/posts/tag/{slug}/` - Posts by tag
- `GET /api/posts/category/{slug}/` - Posts by category

## Project Structure

```
blog_application/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User, Profile
│   │   ├── post.py          # Post, PostImage
│   │   ├── comment.py       # Comment
│   │   ├── tag.py           # Tag, Category
│   │   └── analytics.py     # PageView, SearchQuery
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── posts.py         # Post endpoints
│   │   ├── comments.py      # Comment endpoints
│   │   └── tags.py          # Tag/Category endpoints
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py          # Pydantic validation schemas
│   │   ├── post.py
│   │   └── comment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Authentication logic
│   │   ├── post_service.py  # Post business logic
│   │   └── email_service.py # Email notifications
│   └── middleware/
│       ├── __init__.py
│       └── auth.py          # JWT authentication middleware
├── config/
│   ├── __init__.py
│   ├── settings.py          # Application settings
│   ├── database.py          # Database configuration
│   └── email.py             # Email configuration
├── migrations/              # Database migrations
├── static/                  # Static files (CSS, JS, images)
├── templates/               # HTML templates
├── tests/                   # Unit and integration tests
├── manage.py                # Management commands
├── requirements.txt
└── README.md
```

## Example Usage

### Create a Blog Post

```python
import httpx

# Login
async with httpx.AsyncClient() as client:
    # Register/Login
    response = await client.post('http://localhost:8000/api/auth/login', json={
        'username': 'alice',
        'password': 'secret123'
    })
    token = response.json()['token']

    # Create post
    headers = {'Authorization': f'Bearer {token}'}
    response = await client.post('http://localhost:8000/api/posts/', headers=headers, json={
        'title': 'My First Blog Post',
        'content': 'This is the content of my blog post...',
        'tags': ['python', 'covetpy'],
        'category': 'tutorials',
        'status': 'published'
    })

    post = response.json()
    print(f"Created post: {post['title']}")
```

### Add Comments

```python
# Add comment to post
response = await client.post(
    f'http://localhost:8000/api/posts/{post["id"]}/comments/',
    headers=headers,
    json={
        'content': 'Great post! Very helpful.'
    }
)

comment = response.json()

# Reply to comment
response = await client.post(
    f'http://localhost:8000/api/comments/{comment["id"]}/reply/',
    headers=headers,
    json={
        'content': 'Thank you!'
    }
)
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_posts.py

# Run with verbose output
pytest -v
```

## Deployment

See [deployment guide](../../docs/deployment/production.md) for production deployment instructions.

## License

MIT License - See LICENSE file for details.
