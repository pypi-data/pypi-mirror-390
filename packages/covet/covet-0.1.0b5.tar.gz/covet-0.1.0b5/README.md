# CovetPy - High-Performance Python Web Framework

[![Python versions](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![PyPI version](https://img.shields.io/badge/pypi-v0.1.0b4-blue)](https://pypi.org/project/covet/)
[![License](https://img.shields.io/badge/license-Proprietary-green)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A high-performance Python web framework with Rust-optimized components, featuring a Django/Flask-style ORM and modern async capabilities.

## Features

- **Rust-Optimized Performance**: 40K+ RPS with HTTP/1.1 support
- **Django/Flask-Style ORM**: Intuitive QuerySet API with full type safety
- **Advanced Query Capabilities**: Q objects for complex OR/AND/NOT queries
- **High-Performance Bulk Operations**: 10-100x faster than loops
- **Built-in Security**: SQL injection prevention, DoS protection, LIKE escaping
- **Type-Safe Fields**: MoneyField, DateTimeField, EmailField with automatic validation
- **17+ Field Lookups**: `__gt`, `__gte`, `__contains`, `__in`, `__startswith`, etc.
- **Production-Ready Database Support**: MySQL, PostgreSQL, SQLite
- **HTTP/1.1 Protocol**: Persistent connections, keep-alive support

## Installation

```bash
pip install covet==0.1.0b4
```

## Quick Start

### Hello World

```python
from covet import CovetPy

app = CovetPy()

@app.route("/")
async def hello(request):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.run()
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

# Define model with Django-style fields
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
results = await User.objects.filter(
    Q(is_active=True) & (Q(age__gte=25) | Q(balance__gte=Money(Decimal('500'), 'USD')))
)

# Method chaining
top_users = await User.objects.filter(
    is_active=True
).exclude(
    age__lt=18
).order_by('-balance', 'username').limit(10)

# Bulk operations (10-100x faster)
users_list = [
    User(username=f'user{i}', email=f'user{i}@example.com',
         age=20+i, balance=Money(Decimal('100.00'), 'USD'))
    for i in range(100)
]
await User.objects.bulk_create(users_list)

# Aggregation
total_users = await User.objects.count()
user_exists = await User.objects.filter(username='john_doe').exists()
first_user = await User.objects.filter(is_active=True).first()
```

## Key Features

### 1. Django/Flask-Style ORM

- **QuerySet API**: Familiar `filter()`, `exclude()`, `order_by()`, `limit()` chaining
- **Field Lookups**: 17+ types including `__gt`, `__gte`, `__lt`, `__lte`, `__contains`, `__icontains`, `__in`, `__exact`, `__startswith`, `__endswith`
- **Q Objects**: Complex queries with OR (`|`), AND (`&`), and NOT (`~`) operators
- **Type Safety**: Automatic type conversion and validation for all fields
- **MoneyField**: Decimal-based money handling with currency support

### 2. High-Performance Bulk Operations

```python
# Bulk create - 10-100x faster than loops
products = [Product(...) for i in range(1000)]
await Product.objects.bulk_create(products)

# Bulk update
await Product.objects.filter(category='Electronics').update(
    discount=Decimal('0.10')
)
```

### 3. Built-in Security Features

- **SQL Injection Prevention**: Automatic parameterization of all queries
- **DoS Protection**: Automatic limit of 10,000 rows per query
- **LIKE Pattern Escaping**: Safe handling of wildcards in search queries
- **Input Validation**: Pydantic-based request validation

### 4. Real-World Example Application

See `example_app/complete_ecommerce_platform.py` for a production-ready e-commerce platform demonstrating:
- 6 models with relationships (User, Product, Order, OrderItem, Review, Cart)
- 15+ REST API endpoints
- JWT authentication support
- Shopping cart and order processing
- Advanced search with complex queries
- Statistics and analytics

## Database Support

### Supported Databases

- **MySQL**: Production-ready with connection pooling
- **PostgreSQL**: Full async support
- **SQLite**: Perfect for development and testing

### Connection Example

```python
# MySQL
from covet.database.adapters.mysql import MySQLAdapter

adapter = MySQLAdapter(
    host='localhost',
    user='root',
    password='password',
    database='myapp'
)

# PostgreSQL
from covet.database.adapters.postgresql import PostgreSQLAdapter

adapter = PostgreSQLAdapter(
    host='localhost',
    user='postgres',
    password='password',
    database='myapp'
)

# SQLite
from covet.database.adapters.sqlite import SQLiteAdapter

adapter = SQLiteAdapter(database_path='app.db')
```

## Performance

### Rust-Optimized ASGI

CovetPy includes Rust extensions for performance-critical operations:

```
Baseline (Pure Python):  1,395 RPS, 360ms avg latency
Optimized (Rust):        1,576 RPS, 323ms avg latency
Improvement:             +13% throughput, -10% latency
```

### Bulk Operations Performance

```
Individual inserts (loop): 100 records in 2.5 seconds
Bulk insert:              100 records in 0.025 seconds
Improvement:              100x faster
```

## Field Types

### Available Fields

- `AutoField` - Auto-incrementing primary key
- `CharField` - Variable-length string with max_length
- `TextField` - Unlimited text
- `EmailField` - Email validation
- `IntegerField` - Integer numbers
- `BooleanField` - True/False values
- `MoneyField` - Decimal-based money with currency
- `DateTimeField` - Date and time with auto_now/auto_now_add
- `JSONField` - JSON data storage
- `ForeignKey` - Relationships between models

### Field Lookups

All fields support these lookups:

- **Comparison**: `__gt`, `__gte`, `__lt`, `__lte`, `__exact`
- **Text Search**: `__contains`, `__icontains`, `__startswith`, `__istartswith`, `__endswith`, `__iendswith`
- **List Membership**: `__in`
- **Range**: `__range`
- **Null Checks**: `__isnull`

## Documentation

### Quick Links

- **Installation Guide**: See above
- **ORM Documentation**: `README.PyPI.md`
- **Example Applications**: `example_app/` directory
- **API Reference**: Coming soon

### Examples

- `example_app/complete_ecommerce_platform.py` - Full e-commerce platform (1100+ lines)
- `example_app/ecommerce_orm_app.py` - ORM-focused examples

## Requirements

- Python 3.9 or higher
- One of: MySQL 5.7+, PostgreSQL 12+, or SQLite 3.35+

## Development

### Setup

```bash
git clone https://github.com/vipin08/CovetPy.git
cd CovetPy

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/

# Code formatting
black src/ tests/
ruff check src/ tests/
```

### Building Rust Extensions

```bash
cd rust_extensions
maturin develop --release
```

## Version History

### 0.1.0b4 (Current - October 2025)

- Django/Flask-style ORM with QuerySet API
- MoneyField type safety with Decimal conversion
- Q objects for complex queries
- 17+ field lookups
- Bulk operations (10-100x faster)
- Built-in security features
- Complete e-commerce platform example
- Published to PyPI

### 0.1.0b3

- Initial ORM implementation
- MoneyField bug fixes
- LIKE ESCAPE syntax corrections

## Support

- **GitHub Issues**: https://github.com/vipin08/CovetPy/issues
- **Documentation**: https://github.com/vipin08/Covet-doc

## License

This project is licensed under a Proprietary License. See the [LICENSE](LICENSE) file for details.

## Author

**Vipin Kumar**
- GitHub: https://github.com/vipin08
- Documentation: https://github.com/vipin08/Covet-doc

---

**CovetPy** - High-performance Python web framework with Rust optimization and Django-style ORM.

Version: 0.1.0b4 | Status: Beta | [PyPI](https://pypi.org/project/covet/)
