#!/usr/bin/env python3
"""
Todo API - Complete Real-World Example
=======================================
A full-featured REST API showcasing all CovetPy features:
- CRUD operations with SQLite
- JWT Authentication
- Middleware pipeline
- Input validation
- Error handling
- Database migrations
- Pagination
- Filtering and sorting
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from covet import Covet
from covet.middleware.base import (
    CORSMiddleware,
    LoggingMiddleware,
    ErrorHandlingMiddleware,
    RateLimitMiddleware,
    SessionMiddleware
)
from covet.auth import Auth
from covet.auth.password import hash_password, verify_password
from covet.orm.simple_orm_fixed import (
    Database, Model,
    IntegerField, CharField, TextField, DateTimeField, BooleanField, ForeignKey
)

# Initialize app and database
app = Covet(debug=True)
db = Database('todo.db')

# ===========================
# MODELS
# ===========================

class User(Model):
    """User model with authentication"""
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100, unique=True)
    password_hash = CharField(max_length=255)
    full_name = CharField(max_length=100, null=True)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(null=True)


class TodoList(Model):
    """Todo list (project/category)"""
    name = CharField(max_length=100)
    description = TextField(null=True)
    owner = ForeignKey(User, on_delete='CASCADE')
    color = CharField(max_length=7, default='#007bff')
    is_archived = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Todo(Model):
    """Individual todo item"""
    title = CharField(max_length=200)
    description = TextField(null=True)
    list = ForeignKey(TodoList, on_delete='CASCADE')
    assigned_to = ForeignKey(User, on_delete='SET NULL', null=True)
    priority = IntegerField(default=1)  # 1=Low, 2=Medium, 3=High
    is_completed = BooleanField(default=False)
    completed_at = DateTimeField(null=True)
    due_date = DateTimeField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Comment(Model):
    """Comments on todos"""
    todo = ForeignKey(Todo, on_delete='CASCADE')
    author = ForeignKey(User, on_delete='CASCADE')
    content = TextField()
    created_at = DateTimeField(auto_now_add=True)


# Create tables
print("Creating database tables...")
db.create_tables([User, TodoList, Todo, Comment])
print("✅ Database initialized")

# ===========================
# MIDDLEWARE SETUP
# ===========================

app.add_middleware(ErrorHandlingMiddleware(debug=True))
app.add_middleware(CORSMiddleware(
    origins="*",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    headers=["Content-Type", "Authorization"]
))
app.add_middleware(LoggingMiddleware())
app.add_middleware(RateLimitMiddleware(max_requests=100, window_seconds=60))
app.add_middleware(SessionMiddleware())

# Initialize authentication
auth = Auth(app, secret_key='todo-api-secret-key-2025')

# ===========================
# HELPER FUNCTIONS
# ===========================

def verify_token(request):
    """Verify JWT token from Authorization header"""
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None

    token = auth_header.replace('Bearer ', '')
    try:
        payload = auth.verify_token(token)
        user_id = payload.get('user_id')
        if user_id:
            return User.objects.get(id=int(user_id))
    except:
        pass
    return None


def paginate(query, page=1, per_page=10):
    """Paginate query results"""
    total = query.count() if hasattr(query, 'count') else len(query)
    offset = (page - 1) * per_page
    items = query[offset:offset + per_page] if isinstance(query, list) else query.all()[offset:offset + per_page]

    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page
    }

# ===========================
# PUBLIC ROUTES
# ===========================

@app.get('/')
async def home(request):
    """API documentation"""
    return {
        'name': 'Todo API',
        'version': '1.0.0',
        'endpoints': {
            'auth': {
                'POST /auth/register': 'Register new user',
                'POST /auth/login': 'Login user',
                'GET /auth/profile': 'Get current user profile',
                'PUT /auth/profile': 'Update profile'
            },
            'lists': {
                'GET /lists': 'Get all todo lists',
                'POST /lists': 'Create new list',
                'GET /lists/{id}': 'Get list details',
                'PUT /lists/{id}': 'Update list',
                'DELETE /lists/{id}': 'Delete list'
            },
            'todos': {
                'GET /todos': 'Get all todos',
                'POST /todos': 'Create new todo',
                'GET /todos/{id}': 'Get todo details',
                'PUT /todos/{id}': 'Update todo',
                'DELETE /todos/{id}': 'Delete todo',
                'PATCH /todos/{id}/complete': 'Mark todo as complete'
            },
            'comments': {
                'GET /todos/{id}/comments': 'Get todo comments',
                'POST /todos/{id}/comments': 'Add comment'
            }
        }
    }

# ===========================
# AUTHENTICATION ROUTES
# ===========================

@app.post('/auth/register')
async def register(request):
    """Register new user"""
    data = await request.json()

    # Validate input
    required = ['username', 'email', 'password']
    for field in required:
        if field not in data:
            return {'error': f'{field} is required'}, 400

    # Check if user exists
    existing = User.objects.filter(username=data['username']).first()
    if existing:
        return {'error': 'Username already taken'}, 409

    existing_email = User.objects.filter(email=data['email']).first()
    if existing_email:
        return {'error': 'Email already registered'}, 409

    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        password_hash=hash_password(data['password']),
        full_name=data.get('full_name', '')
    )
    user.save()

    # Create default todo list
    default_list = TodoList(
        name='Personal',
        description='Default personal todo list',
        owner=user.id
    )
    default_list.save()

    # Generate token
    token = auth.create_token(user_id=str(user.id))

    return {
        'message': 'User registered successfully',
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }
    }, 201


@app.post('/auth/login')
async def login(request):
    """Login user"""
    data = await request.json()

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return {'error': 'Username and password required'}, 400

    # Find user
    user = User.objects.filter(username=username).first()
    if not user or not verify_password(password, user.password_hash):
        return {'error': 'Invalid credentials'}, 401

    if not user.is_active:
        return {'error': 'Account is disabled'}, 403

    # Update last login
    user.last_login = datetime.now().isoformat()
    user.save()

    # Generate token
    token = auth.create_token(user_id=str(user.id))

    return {
        'token': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }
    }


@app.get('/auth/profile')
async def get_profile(request):
    """Get current user profile"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'is_admin': user.is_admin,
        'created_at': str(user.created_at),
        'last_login': str(user.last_login) if user.last_login else None
    }


@app.put('/auth/profile')
async def update_profile(request):
    """Update user profile"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    data = await request.json()

    # Update allowed fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'email' in data:
        # Check if email is already taken
        existing = User.objects.filter(email=data['email']).first()
        if existing and existing.id != user.id:
            return {'error': 'Email already in use'}, 409
        user.email = data['email']
    if 'password' in data:
        user.password_hash = hash_password(data['password'])

    user.save()

    return {
        'message': 'Profile updated successfully',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name
        }
    }

# ===========================
# TODO LIST ROUTES
# ===========================

@app.get('/lists')
async def get_lists(request):
    """Get all todo lists for current user"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    # Get query parameters
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 10))
    include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'

    # Query lists
    lists = TodoList.objects.filter(owner=user.id)
    if not include_archived:
        lists = [l for l in lists.all() if not l.is_archived]
    else:
        lists = lists.all()

    # Add todo counts
    for lst in lists:
        todos = Todo.objects.filter(list=lst.id).all()
        lst.todo_count = len(todos)
        lst.completed_count = len([t for t in todos if t.is_completed])

    # Paginate
    result = paginate(lists, page, per_page)

    return {
        'lists': [
            {
                'id': l.id,
                'name': l.name,
                'description': l.description,
                'color': l.color,
                'is_archived': l.is_archived,
                'todo_count': l.todo_count,
                'completed_count': l.completed_count,
                'created_at': str(l.created_at)
            } for l in result['items']
        ],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    }


@app.post('/lists')
async def create_list(request):
    """Create new todo list"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    data = await request.json()

    if 'name' not in data:
        return {'error': 'List name is required'}, 400

    todo_list = TodoList(
        name=data['name'],
        description=data.get('description', ''),
        color=data.get('color', '#007bff'),
        owner=user.id
    )
    todo_list.save()

    return {
        'message': 'List created successfully',
        'list': {
            'id': todo_list.id,
            'name': todo_list.name,
            'description': todo_list.description,
            'color': todo_list.color
        }
    }, 201


@app.get('/lists/{list_id}')
async def get_list(request, list_id):
    """Get list details with todos"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo_list = TodoList.objects.get(id=int(list_id))
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'List not found'}, 404

    # Get todos in this list
    todos = Todo.objects.filter(list=todo_list.id).all()

    return {
        'id': todo_list.id,
        'name': todo_list.name,
        'description': todo_list.description,
        'color': todo_list.color,
        'is_archived': todo_list.is_archived,
        'created_at': str(todo_list.created_at),
        'todos': [
            {
                'id': t.id,
                'title': t.title,
                'priority': t.priority,
                'is_completed': t.is_completed,
                'due_date': str(t.due_date) if t.due_date else None
            } for t in todos
        ]
    }


@app.put('/lists/{list_id}')
async def update_list(request, list_id):
    """Update todo list"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo_list = TodoList.objects.get(id=int(list_id))
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'List not found'}, 404

    data = await request.json()

    # Update fields
    if 'name' in data:
        todo_list.name = data['name']
    if 'description' in data:
        todo_list.description = data['description']
    if 'color' in data:
        todo_list.color = data['color']
    if 'is_archived' in data:
        todo_list.is_archived = data['is_archived']

    todo_list.save()

    return {
        'message': 'List updated successfully',
        'list': {
            'id': todo_list.id,
            'name': todo_list.name,
            'description': todo_list.description,
            'color': todo_list.color,
            'is_archived': todo_list.is_archived
        }
    }


@app.delete('/lists/{list_id}')
async def delete_list(request, list_id):
    """Delete todo list"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo_list = TodoList.objects.get(id=int(list_id))
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'List not found'}, 404

    todo_list.delete()

    return {'message': 'List deleted successfully'}

# ===========================
# TODO ROUTES
# ===========================

@app.get('/todos')
async def get_todos(request):
    """Get all todos for current user"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    # Get query parameters
    page = int(request.query_params.get('page', 1))
    per_page = int(request.query_params.get('per_page', 10))
    list_id = request.query_params.get('list_id')
    is_completed = request.query_params.get('is_completed')
    priority = request.query_params.get('priority')

    # Get user's lists
    user_lists = TodoList.objects.filter(owner=user.id).all()
    list_ids = [l.id for l in user_lists]

    # Query todos
    todos = []
    for lid in list_ids:
        list_todos = Todo.objects.filter(list=lid).all()
        todos.extend(list_todos)

    # Apply filters
    if list_id:
        todos = [t for t in todos if t.list == int(list_id)]
    if is_completed is not None:
        completed = is_completed.lower() == 'true'
        todos = [t for t in todos if t.is_completed == completed]
    if priority:
        todos = [t for t in todos if t.priority == int(priority)]

    # Sort by priority and date
    todos.sort(key=lambda t: (-t.priority, t.created_at), reverse=True)

    # Paginate
    result = paginate(todos, page, per_page)

    return {
        'todos': [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'list_id': t.list,
                'priority': t.priority,
                'is_completed': t.is_completed,
                'due_date': str(t.due_date) if t.due_date else None,
                'created_at': str(t.created_at)
            } for t in result['items']
        ],
        'pagination': {
            'page': result['page'],
            'per_page': result['per_page'],
            'total': result['total'],
            'pages': result['pages']
        }
    }


@app.post('/todos')
async def create_todo(request):
    """Create new todo"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    data = await request.json()

    # Validate input
    if 'title' not in data:
        return {'error': 'Title is required'}, 400
    if 'list_id' not in data:
        return {'error': 'List ID is required'}, 400

    # Verify list ownership
    try:
        todo_list = TodoList.objects.get(id=int(data['list_id']))
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'List not found'}, 404

    # Create todo
    todo = Todo(
        title=data['title'],
        description=data.get('description', ''),
        list=todo_list.id,
        priority=data.get('priority', 1),
        due_date=data.get('due_date'),
        assigned_to=data.get('assigned_to')
    )
    todo.save()

    return {
        'message': 'Todo created successfully',
        'todo': {
            'id': todo.id,
            'title': todo.title,
            'description': todo.description,
            'priority': todo.priority,
            'list_id': todo.list
        }
    }, 201


@app.get('/todos/{todo_id}')
async def get_todo(request, todo_id):
    """Get todo details"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo = Todo.objects.get(id=int(todo_id))
        # Verify ownership through list
        todo_list = TodoList.objects.get(id=todo.list)
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'Todo not found'}, 404

    # Get comments
    comments = Comment.objects.filter(todo=todo.id).all()

    return {
        'id': todo.id,
        'title': todo.title,
        'description': todo.description,
        'list_id': todo.list,
        'priority': todo.priority,
        'is_completed': todo.is_completed,
        'completed_at': str(todo.completed_at) if todo.completed_at else None,
        'due_date': str(todo.due_date) if todo.due_date else None,
        'created_at': str(todo.created_at),
        'updated_at': str(todo.updated_at),
        'comments': [
            {
                'id': c.id,
                'content': c.content,
                'author_id': c.author,
                'created_at': str(c.created_at)
            } for c in comments
        ]
    }


@app.patch('/todos/{todo_id}/complete')
async def complete_todo(request, todo_id):
    """Mark todo as complete/incomplete"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo = Todo.objects.get(id=int(todo_id))
        # Verify ownership through list
        todo_list = TodoList.objects.get(id=todo.list)
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'Todo not found'}, 404

    # Toggle completion
    todo.is_completed = not todo.is_completed
    if todo.is_completed:
        todo.completed_at = datetime.now().isoformat()
    else:
        todo.completed_at = None
    todo.save()

    return {
        'message': f'Todo marked as {"completed" if todo.is_completed else "incomplete"}',
        'todo': {
            'id': todo.id,
            'title': todo.title,
            'is_completed': todo.is_completed,
            'completed_at': str(todo.completed_at) if todo.completed_at else None
        }
    }


@app.post('/todos/{todo_id}/comments')
async def add_comment(request, todo_id):
    """Add comment to todo"""
    user = verify_token(request)
    if not user:
        return {'error': 'Authentication required'}, 401

    try:
        todo = Todo.objects.get(id=int(todo_id))
        # Verify ownership through list
        todo_list = TodoList.objects.get(id=todo.list)
        if todo_list.owner != user.id:
            return {'error': 'Access denied'}, 403
    except:
        return {'error': 'Todo not found'}, 404

    data = await request.json()

    if 'content' not in data:
        return {'error': 'Comment content is required'}, 400

    comment = Comment(
        todo=todo.id,
        author=user.id,
        content=data['content']
    )
    comment.save()

    return {
        'message': 'Comment added successfully',
        'comment': {
            'id': comment.id,
            'content': comment.content,
            'created_at': str(comment.created_at)
        }
    }, 201

# ===========================
# ADMIN ROUTES
# ===========================

@app.get('/admin/stats')
async def admin_stats(request):
    """Get system statistics (admin only)"""
    user = verify_token(request)
    if not user or not user.is_admin:
        return {'error': 'Admin access required'}, 403

    return {
        'users': {
            'total': User.objects.count(),
            'active': len([u for u in User.objects.all() if u.is_active]),
            'admin': len([u for u in User.objects.all() if u.is_admin])
        },
        'lists': {
            'total': TodoList.objects.count(),
            'archived': len([l for l in TodoList.objects.all() if l.is_archived])
        },
        'todos': {
            'total': Todo.objects.count(),
            'completed': len([t for t in Todo.objects.all() if t.is_completed]),
            'high_priority': len([t for t in Todo.objects.all() if t.priority == 3])
        },
        'comments': {
            'total': Comment.objects.count()
        }
    }

# ===========================
# SEED DATA (for testing)
# ===========================

def seed_data():
    """Create sample data for testing"""
    # Check if data already exists
    if User.objects.count() > 0:
        print("✅ Sample data already exists")
        return

    print("Creating sample data...")

    # Create test users
    admin = User(
        username='admin',
        email='admin@example.com',
        password_hash=hash_password('admin123'),
        full_name='Admin User',
        is_admin=True
    )
    admin.save()

    user1 = User(
        username='johndoe',
        email='john@example.com',
        password_hash=hash_password('password123'),
        full_name='John Doe'
    )
    user1.save()

    # Create lists
    work_list = TodoList(
        name='Work Projects',
        description='Work-related tasks',
        owner=user1.id,
        color='#dc3545'
    )
    work_list.save()

    personal_list = TodoList(
        name='Personal',
        description='Personal tasks and reminders',
        owner=user1.id,
        color='#28a745'
    )
    personal_list.save()

    # Create todos
    todos = [
        ('Complete API documentation', work_list.id, 3, False),
        ('Review pull requests', work_list.id, 2, True),
        ('Team meeting preparation', work_list.id, 2, False),
        ('Buy groceries', personal_list.id, 1, False),
        ('Gym workout', personal_list.id, 1, True),
        ('Read book', personal_list.id, 1, False),
    ]

    for title, list_id, priority, completed in todos:
        todo = Todo(
            title=title,
            list=list_id,
            priority=priority,
            is_completed=completed,
            assigned_to=user1.id
        )
        if completed:
            todo.completed_at = datetime.now().isoformat()
        todo.save()

    print("✅ Sample data created")
    print("\nTest Credentials:")
    print("  Admin: admin / admin123")
    print("  User: johndoe / password123")

# Create seed data
seed_data()

# ===========================
# MAIN
# ===========================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Todo API - CovetPy Framework Example")
    print("="*60)
    print("\nEndpoints available at: http://localhost:8000")
    print("API documentation at: http://localhost:8000/")
    print("\nPress Ctrl+C to stop the server")
    print("="*60 + "\n")

    # Run the app
    app.run(host='127.0.0.1', port=8000)