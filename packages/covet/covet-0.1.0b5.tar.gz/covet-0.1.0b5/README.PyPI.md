# CovetPy - High-Performance Python Web Framework

A high-performance Python web framework with Rust-optimized components, featuring a Django/Flask-style ORM and modern async capabilities.

## Features

- **Rust-Optimized Performance**: Optional Rust extensions for high-performance routing and HTTP parsing
- **Django/Flask-Style ORM**: Intuitive QuerySet API with full type safety
- **Advanced Query Capabilities**: Q objects for complex OR/AND/NOT queries
- **High-Performance Bulk Operations**: Optimized create, update, and delete operations
- **Built-in Security**: SQL injection prevention, DoS protection, XSS protection, JWT authentication
- **Type-Safe Fields**: MoneyField, DateTimeField, EmailField with automatic validation
- **17+ Field Lookups**: `__gt`, `__gte`, `__contains`, `__in`, `__startswith`, and more
- **Production-Ready Database Support**: MySQL, PostgreSQL, SQLite
- **ASGI 3.0 Native**: Full async/await support throughout
- **Enterprise Features**: Connection pooling, health checks, Prometheus metrics, rate limiting

## Installation

```bash
pip install covet
```

With optional features:

```bash
# With database support
pip install covet[database]

# With security features
pip install covet[security]

# Full installation (all features)
pip install covet[full]
```

## Quick Start

### Hello World

```python
from covet import Covet

app = Covet()

@app.route('/')
async def hello(request):
    return {'message': 'Hello World'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
```

### Django/Flask-Style ORM

```python
from decimal import Decimal
from covet.database.adapters.mysql import MySQLAdapter
from covet.database.orm import Model, Q
from covet.database.orm.fields import (
    AutoField, CharField, EmailField, IntegerField,
    BooleanField, MoneyField, Money, DateTimeField
)
from covet.database.orm.managers import ModelManager
from covet.database.orm.adapter_registry import register_adapter

# Setup database connection
adapter = MySQLAdapter(
    host='localhost',
    user='root',
    password='password',
    database='myapp'
)
await adapter.connect()
register_adapter('default', adapter)

# Define model
class User(Model):
    id = AutoField()
    username = CharField(max_length=50, unique=True)
    email = EmailField(unique=True)
    age = IntegerField()
    is_active = BooleanField(default=True)
    balance = MoneyField(max_digits=10, decimal_places=2, currency='USD')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

# Setup model manager
User._adapter = adapter
User.objects = ModelManager(User)

# Create user
user = User(
    username='john_doe',
    email='john@example.com',
    age=30,
    is_active=True,
    balance=Money(Decimal('1000.00'), 'USD')
)
await user.save()

# Query with field lookups
active_users = await User.objects.filter(
    is_active=True,
    age__gte=18
)

# Complex queries with Q objects
from covet.database.orm import Q

users = await User.objects.filter(
    Q(username__startswith='john') | Q(email__contains='example.com')
)
```

### RESTful API with JWT Authentication

```python
from covet import Covet
from covet.security.jwt import JWTAuth

app = Covet()
jwt_auth = JWTAuth(secret_key='your-secret-key')

@app.route('/api/auth/login', methods=['POST'])
async def login(request):
    data = await request.json()
    # Validate user credentials
    token = jwt_auth.create_token(user_id=1, username='john_doe')
    return {'token': token}

@app.route('/api/protected', methods=['GET'])
async def protected(request):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    payload = jwt_auth.verify_token(token)
    return {'user_id': payload['user_id']}

if __name__ == '__main__':
    app.run()
```

### High-Performance Bulk Operations

```python
# Bulk create (10-100x faster than loops)
users_data = [
    {'username': f'user_{i}', 'email': f'user{i}@example.com', 'age': 20 + i}
    for i in range(1000)
]
await User.objects.bulk_create(users_data)

# Bulk update
await User.objects.filter(age__lt=18).bulk_update({'is_active': False})

# Bulk delete
await User.objects.filter(is_active=False).bulk_delete()
```

## Core Features

### ASGI 3.0 Native

CovetPy implements the ASGI 3.0 protocol natively, providing:
- Full async/await support
- WebSocket support
- HTTP/2 ready (via uvicorn)
- Compatible with any ASGI server (uvicorn, hypercorn, daphne)

### Django-Style ORM

- **QuerySet API**: Familiar Django-style chaining
- **Field Types**: 15+ field types with automatic validation
- **Lookups**: 17+ field lookups (`__gt`, `__gte`, `__contains`, `__in`, etc.)
- **Q Objects**: Complex OR/AND/NOT queries
- **Type Safety**: Full type hints and validation
- **Performance**: Optimized bulk operations

### Built-in Security

- **SQL Injection Prevention**: Parameterized queries only
- **XSS Protection**: HTML sanitization with bleach
- **JWT Authentication**: Built-in JWT support
- **RBAC**: Role-Based Access Control
- **Rate Limiting**: Request rate limiting with Redis/Memory backend
- **DoS Protection**: Query size limits, request size limits
- **Password Hashing**: Secure bcrypt hashing

### Monitoring & Observability

- **Prometheus Metrics**: Built-in metrics export
- **Health Checks**: Database and system health endpoints
- **Structured Logging**: JSON logging support
- **Performance Profiling**: Request timing and profiling

## Database Support

CovetPy provides production-ready adapters for:

- **MySQL**: Full async support via aiomysql
- **PostgreSQL**: Full async support via asyncpg
- **SQLite**: Async support via aiosqlite

All adapters include:
- Connection pooling (5-20 connections default)
- Automatic reconnection
- Transaction support
- Query logging
- Performance monitoring

## Production Deployment

### With uvicorn (Recommended)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### With gunicorn + uvicorn workers

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install covet[full]

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Performance

CovetPy is designed for high performance:

- **Sub-millisecond latency**: For simple routes
- **Optional Rust extensions**: For HTTP parsing and routing acceleration
- **Efficient connection pooling**: Minimizes database overhead
- **Lazy query evaluation**: Queries execute only when needed
- **Result caching**: Automatic QuerySet result caching

## Requirements

- Python 3.9+
- Core dependencies:
  - pydantic>=2.12.0
  - uvicorn[standard]>=0.37.0
  - PyJWT>=2.8.0
  - prometheus-client>=0.23.1
  - psutil>=7.1.0

## License

Proprietary - Copyright Vipin Kumar

## Links

- PyPI: https://pypi.org/project/covet/
- Documentation: Coming soon
- Bug Reports: GitHub issues

## Version

Current version: 0.1.0b4 (Beta 4)

This is a beta release. The API may change in future releases.
