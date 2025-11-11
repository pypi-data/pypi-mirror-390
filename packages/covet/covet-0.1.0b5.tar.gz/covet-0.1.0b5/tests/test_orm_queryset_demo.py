"""
ORM QuerySet API Demonstration

This file shows how to use Django-style ORM queries instead of raw SQL.
Compares raw SQL approach vs ORM QuerySet approach side-by-side.
"""

import asyncio
from decimal import Decimal
from src.covet.database.orm.models import Model
from src.covet.database.orm.fields import (
    AutoField, CharField, EmailField, SlugField,
    IPAddressField, JSONField, DateTimeField, BooleanField,
    TextField, PositiveIntegerField, MoneyField, Money,
    BigAutoField, PositiveSmallIntegerField, HStoreField, InetField
)
from src.covet.database.adapters.mysql import MySQLAdapter


# ============================================================================
# Model Definitions (same as integration test)
# ============================================================================

class User(Model):
    """User model with ORM QuerySet support."""
    __tablename__ = 'users'
    __database__ = 'default'

    id = AutoField()
    username = CharField(max_length=50, unique=True)
    email = EmailField(unique=True)
    slug = SlugField(max_length=50, unique=True)
    last_login_ip = IPAddressField(null=True)
    preferences = JSONField(null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    is_active = BooleanField(default=True)


class Product(Model):
    """Product model with ORM QuerySet support."""
    __tablename__ = 'products'
    __database__ = 'default'

    id = AutoField()
    name = CharField(max_length=200)
    slug = SlugField(max_length=200, unique=True)
    description = TextField()
    price = MoneyField(max_digits=10, decimal_places=2, currency='USD')
    stock = PositiveIntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Order(Model):
    """Order model with relationships."""
    __tablename__ = 'orders'
    __database__ = 'default'

    id = BigAutoField()
    user_id = IntegerField()
    product_id = IntegerField()
    quantity = PositiveIntegerField(default=1)
    total_amount = MoneyField(max_digits=10, decimal_places=2, currency='USD')
    status = CharField(max_length=20, default='pending')
    order_ip = InetField(null=True)
    created_at = DateTimeField(auto_now_add=True)


class Review(Model):
    """Review model."""
    __tablename__ = 'reviews'
    __database__ = 'default'

    id = AutoField()
    user_id = IntegerField()
    product_id = IntegerField()
    rating = PositiveSmallIntegerField(min_value=1, max_value=5)
    title = CharField(max_length=200)
    comment = TextField()
    metadata = HStoreField(null=True)
    created_at = DateTimeField(auto_now_add=True)


# ============================================================================
# COMPARISON: Raw SQL vs ORM QuerySet
# ============================================================================

async def demo_comparisons():
    """
    Demonstrate ORM QuerySet usage vs raw SQL.
    Shows the same queries written both ways.
    """

    # Setup database connection
    adapter = MySQLAdapter(
        host='localhost',
        user='root',
        password='12345678',
        database='covet_test_realworld'
    )
    await adapter.connect()

    # Set the adapter for models
    User._adapter = adapter
    Product._adapter = adapter
    Order._adapter = adapter
    Review._adapter = adapter

    print("=" * 80)
    print("ORM QUERYSET API DEMONSTRATION")
    print("=" * 80)

    # ========================================================================
    # Example 1: Get All Records
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Retrieve All Users")
    print("=" * 80)

    print("\n❌ RAW SQL (Old Way):")
    print("```python")
    print('users = await adapter.fetch_all("SELECT id, username, email FROM users")')
    print("```")

    print("\n✅ ORM QUERYSET (New Way - Django/Flask Style):")
    print("```python")
    print("users = await User.objects.all()")
    print("```")

    # Execute
    users = await User.objects.all()
    print(f"\n📊 Result: Retrieved {len(users)} users")
    for user in users:
        print(f"   - {user.username} ({user.email})")

    # ========================================================================
    # Example 2: Filter with WHERE Clause
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Get Active Users Only")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('active_users = await adapter.fetch_all(')
    print('    "SELECT * FROM users WHERE is_active = %s", (True,)')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET (Django/Flask Style):")
    print("```python")
    print("active_users = await User.objects.filter(is_active=True)")
    print("```")

    # Execute
    active_users = await User.objects.filter(is_active=True)
    print(f"\n📊 Result: Found {len(active_users)} active users")

    # ========================================================================
    # Example 3: Get Single Record
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Get User by ID")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('user = await adapter.fetch_one(')
    print('    "SELECT * FROM users WHERE id = %s", (1,)')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET:")
    print("```python")
    print("user = await User.objects.get(id=1)")
    print("```")

    # Execute
    try:
        user = await User.objects.get(id=1)
        print(f"\n📊 Result: {user.username} ({user.email})")
    except User.DoesNotExist:
        print("\n⚠️ User not found")

    # ========================================================================
    # Example 4: Complex Filtering with Field Lookups
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Products with Stock > 100")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('products = await adapter.fetch_all(')
    print('    "SELECT name, stock FROM products WHERE stock > %s", (100,)')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET with Field Lookup:")
    print("```python")
    print("products = await Product.objects.filter(stock__gt=100)")
    print("```")

    # Execute
    products = await Product.objects.filter(stock__gt=100)
    print(f"\n📊 Result: Found {len(products)} products")
    for product in products:
        print(f"   - {product.name}: {product.stock} units")

    # ========================================================================
    # Example 5: UPDATE Operation
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Update Product Stock")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('await adapter.execute(')
    print('    "UPDATE products SET stock = stock + 50 WHERE name = %s",')
    print('    ("Wireless Mouse",)')
    print(')')
    print('updated = await adapter.fetch_one(')
    print('    "SELECT name, stock FROM products WHERE name = %s",')
    print('    ("Wireless Mouse",)')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET - Method 1 (bulk update):")
    print("```python")
    print("await Product.objects.filter(name='Wireless Mouse').update(stock=F('stock') + 50)")
    print("```")

    print("\n✅ ORM QUERYSET - Method 2 (instance update):")
    print("```python")
    print("product = await Product.objects.get(name='Wireless Mouse')")
    print("product.stock += 50")
    print("await product.save()")
    print("```")

    # Execute Method 2
    try:
        product = await Product.objects.get(name='Wireless Mouse')
        old_stock = product.stock
        product.stock += 50
        await product.save()
        print(f"\n📊 Result: Updated {product.name} stock from {old_stock} to {product.stock}")
    except Product.DoesNotExist:
        print("\n⚠️ Product not found")

    # ========================================================================
    # Example 6: Chaining Multiple Filters
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Chain Multiple Filters")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('products = await adapter.fetch_all(')
    print('    """SELECT * FROM products ')
    print('       WHERE stock > %s ')
    print('       AND name LIKE %s')
    print('       ORDER BY stock DESC')
    print('       LIMIT 10""",')
    print('    (100, "%Mouse%")')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET (Method Chaining):")
    print("```python")
    print("products = await Product.objects.filter(")
    print("    stock__gt=100,")
    print("    name__icontains='Mouse'")
    print(").order_by('-stock').limit(10)")
    print("```")

    # Execute
    products = await Product.objects.filter(
        stock__gt=100,
        name__icontains='Mouse'
    ).order_by('-stock').limit(10)
    print(f"\n📊 Result: Found {len(products)} matching products")

    # ========================================================================
    # Example 7: DELETE Operation
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Soft Delete (Deactivate User)")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('await adapter.execute(')
    print('    "UPDATE users SET is_active = %s WHERE username = %s",')
    print('    (False, "bob_wilson")')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET:")
    print("```python")
    print("user = await User.objects.get(username='bob_wilson')")
    print("user.is_active = False")
    print("await user.save()")
    print("```")

    # Or bulk update:
    print("\n✅ ORM QUERYSET (Bulk Update):")
    print("```python")
    print("await User.objects.filter(username='bob_wilson').update(is_active=False)")
    print("```")

    # ========================================================================
    # Example 8: Exclude Filter
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Get All Users EXCEPT Inactive")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('users = await adapter.fetch_all(')
    print('    "SELECT * FROM users WHERE is_active != %s", (False,)')
    print(')')
    print("```")

    print("\n✅ ORM QUERYSET:")
    print("```python")
    print("users = await User.objects.exclude(is_active=False)")
    print("# OR equivalently:")
    print("users = await User.objects.filter(is_active=True)")
    print("```")

    # ========================================================================
    # Example 9: Count Records
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 9: Count Active Users")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('result = await adapter.fetch_one(')
    print('    "SELECT COUNT(*) as count FROM users WHERE is_active = %s", (True,)')
    print(')')
    print('count = result["count"]')
    print("```")

    print("\n✅ ORM QUERYSET:")
    print("```python")
    print("count = await User.objects.filter(is_active=True).count()")
    print("```")

    # Execute
    count = await User.objects.filter(is_active=True).count()
    print(f"\n📊 Result: {count} active users")

    # ========================================================================
    # Example 10: EXISTS Check
    # ========================================================================
    print("\n" + "=" * 80)
    print("EXAMPLE 10: Check if Product Exists")
    print("=" * 80)

    print("\n❌ RAW SQL:")
    print("```python")
    print('result = await adapter.fetch_one(')
    print('    "SELECT EXISTS(SELECT 1 FROM products WHERE slug = %s) as exists",')
    print('    ("laptop-pro",)')
    print(')')
    print('exists = bool(result["exists"])')
    print("```")

    print("\n✅ ORM QUERYSET:")
    print("```python")
    print("exists = await Product.objects.filter(slug='laptop-pro').exists()")
    print("```")

    # ========================================================================
    # Summary of Available Field Lookups
    # ========================================================================
    print("\n" + "=" * 80)
    print("AVAILABLE FIELD LOOKUPS")
    print("=" * 80)

    print("""
    The ORM supports Django-style field lookups:

    Exact matching:
    - field__exact='value'      → field = 'value'
    - field='value'              → Same as __exact (shorthand)

    Comparisons:
    - field__gt=10               → field > 10
    - field__gte=10              → field >= 10
    - field__lt=10               → field < 10
    - field__lte=10              → field <= 10

    String operations:
    - field__contains='text'     → field LIKE '%text%'
    - field__icontains='text'    → field ILIKE '%text%' (case-insensitive)
    - field__startswith='text'   → field LIKE 'text%'
    - field__endswith='text'     → field LIKE '%text'

    NULL checks:
    - field__isnull=True         → field IS NULL
    - field__isnull=False        → field IS NOT NULL

    List operations:
    - field__in=[1, 2, 3]        → field IN (1, 2, 3)

    Ranges:
    - field__range=(1, 10)       → field BETWEEN 1 AND 10
    """)

    # ========================================================================
    # Summary of Available QuerySet Methods
    # ========================================================================
    print("\n" + "=" * 80)
    print("AVAILABLE QUERYSET METHODS")
    print("=" * 80)

    print("""
    Retrieving data:
    - .all()                     → Get all records
    - .filter(**kwargs)          → Filter records (AND conditions)
    - .exclude(**kwargs)         → Exclude records (NOT conditions)
    - .get(**kwargs)             → Get single record (raises DoesNotExist)
    - .first()                   → Get first record or None
    - .last()                    → Get last record or None
    - .exists()                  → Check if any records exist (bool)
    - .count()                   → Count matching records

    Ordering and limiting:
    - .order_by('field')         → ORDER BY field ASC
    - .order_by('-field')        → ORDER BY field DESC
    - .limit(n)                  → LIMIT n
    - .offset(n)                 → OFFSET n
    - [start:end]                → Slice support (LIMIT/OFFSET)

    Modifying data:
    - .update(**kwargs)          → Bulk UPDATE
    - .delete()                  → Bulk DELETE

    Field selection:
    - .values('field1', 'field2')      → Return dicts with selected fields
    - .values_list('field1', 'field2') → Return tuples
    - .only('field1', 'field2')        → Defer other fields
    - .defer('field1', 'field2')       → Defer specified fields

    Distinct:
    - .distinct()                → SELECT DISTINCT

    Aggregation:
    - .aggregate(avg=Avg('field'))     → Aggregate functions
    - .annotate(count=Count('field'))  → Add calculated fields

    Eager loading (for relationships):
    - .select_related('fk_field')      → JOIN related tables
    - .prefetch_related('m2m_field')   → Separate queries for M2M

    Chaining:
    All methods return new QuerySet → can chain infinitely!

    Example chaining:
    results = await User.objects.filter(
        is_active=True
    ).exclude(
        username='guest'
    ).order_by(
        '-created_at'
    ).limit(10)
    """)

    print("\n" + "=" * 80)
    print("✅ DEMONSTRATION COMPLETE")
    print("=" * 80)
    print("\n🎯 Key Takeaways:")
    print("   1. Use Model.objects instead of raw SQL")
    print("   2. Chain methods for complex queries")
    print("   3. Use field lookups (__gt, __contains, etc.)")
    print("   4. More readable, maintainable, and type-safe")
    print("   5. Automatic SQL generation and escaping")
    print("\n")

    await adapter.close()


if __name__ == "__main__":
    asyncio.run(demo_comparisons())
