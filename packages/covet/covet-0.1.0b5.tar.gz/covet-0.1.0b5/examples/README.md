# CovetPy Framework Examples

This directory contains real-world examples demonstrating the full capabilities of the CovetPy framework.

## 📁 Examples

### 1. Todo API (`todo_api/`)
A complete REST API with:
- **Authentication**: JWT-based user authentication
- **CRUD Operations**: Full Create, Read, Update, Delete
- **Database**: SQLite with ORM relationships
- **Middleware**: CORS, Rate limiting, Logging, Sessions
- **Pagination**: Efficient data pagination
- **Filtering**: Query parameters for filtering
- **Admin Panel**: Statistics and management

### 2. Blog Application (`real_blog_app.py`)
A blog platform featuring:
- User management
- Blog posts with categories
- Comments system
- View tracking
- Admin dashboard

### 3. Middleware Demo (`example_middleware_app.py`)
Shows middleware pipeline:
- Error handling
- CORS configuration
- Logging
- Session management

## 🚀 Quick Start

### Running the Todo API

```bash
cd examples/todo_api
python app.py
```

The API will be available at `http://localhost:8000`

#### Test Credentials:
- **Admin**: `admin` / `admin123`
- **User**: `johndoe` / `password123`

#### API Endpoints:

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `GET /auth/profile` - Get profile
- `PUT /auth/profile` - Update profile

**Todo Lists:**
- `GET /lists` - Get all lists
- `POST /lists` - Create list
- `GET /lists/{id}` - Get list details
- `PUT /lists/{id}` - Update list
- `DELETE /lists/{id}` - Delete list

**Todos:**
- `GET /todos` - Get all todos
- `POST /todos` - Create todo
- `GET /todos/{id}` - Get todo details
- `PATCH /todos/{id}/complete` - Toggle completion
- `POST /todos/{id}/comments` - Add comment

**Admin:**
- `GET /admin/stats` - System statistics (admin only)

## 📝 Example Request

### Register User
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123"
  }'
```

### Create Todo
```bash
curl -X POST http://localhost:8000/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Learn CovetPy",
    "list_id": 1,
    "priority": 3
  }'
```

## 🔧 Features Demonstrated

### ORM Features
- Model definitions with field types
- Foreign key relationships
- Query filtering
- Pagination
- Auto timestamps

### Authentication
- Password hashing with bcrypt
- JWT token generation
- Token verification
- Protected routes

### Middleware
- CORS handling
- Rate limiting
- Request logging
- Error handling
- Session management

### API Features
- RESTful routing
- JSON request/response
- Query parameters
- Path parameters
- Status codes
- Error responses

## 🏗️ Building Your Own App

Use these examples as templates for your own applications:

1. **Copy the structure** from `todo_api/`
2. **Define your models** in the Models section
3. **Set up middleware** for your needs
4. **Add your routes** following the patterns shown
5. **Test with the included credentials**

## 📚 Learn More

- [Framework Documentation](../docs/)
- [API Reference](../docs/API_DOCUMENTATION_GUIDE.md)
- [Database Guide](../docs/DATABASE_QUICK_START.md)

## 🤝 Contributing

Found a bug or want to add an example? Contributions are welcome!

---
Created by vipin08 - October 2025