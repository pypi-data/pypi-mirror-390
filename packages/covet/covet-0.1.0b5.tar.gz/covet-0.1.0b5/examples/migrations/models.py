"""
Example Models for Testing CovetPy Migration System

These models demonstrate various field types and relationships.
"""

import sys
from pathlib import Path

# Add CovetPy to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from covet.orm.fields import (
    AutoField,
    CharField,
    TextField,
    IntegerField,
    BooleanField,
    DateTimeField,
    DecimalField,
    ForeignKey,
)
from covet.orm.models import Model


class User(Model):
    """User model."""

    id = AutoField()
    username = CharField(max_length=50, unique=True, null=False)
    email = CharField(max_length=100, unique=True, null=False)
    password = CharField(max_length=255, null=False)
    first_name = CharField(max_length=50, null=True)
    last_name = CharField(max_length=50, null=True)
    is_active = BooleanField(default=True, null=False)
    is_admin = BooleanField(default=False, null=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = "users"
        indexes = ["username", "email"]


class Category(Model):
    """Category model."""

    id = AutoField()
    name = CharField(max_length=100, unique=True, null=False)
    description = TextField(null=True)
    slug = CharField(max_length=100, unique=True, null=False)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        table_name = "categories"


class Product(Model):
    """Product model."""

    id = AutoField()
    name = CharField(max_length=200, null=False)
    description = TextField(null=True)
    price = DecimalField(max_digits=10, decimal_places=2, null=False)
    stock = IntegerField(default=0, null=False)
    category_id = ForeignKey(Category, on_delete="CASCADE", related_name="products")
    is_active = BooleanField(default=True, null=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = "products"
        indexes = ["name", "category_id"]


class Order(Model):
    """Order model."""

    id = AutoField()
    user_id = ForeignKey(User, on_delete="CASCADE", related_name="orders")
    status = CharField(
        max_length=20,
        default="pending",
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("shipped", "Shipped"),
            ("delivered", "Delivered"),
            ("cancelled", "Cancelled"),
        ],
    )
    total = DecimalField(max_digits=10, decimal_places=2, null=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = "orders"
        indexes = ["user_id", "status"]


class OrderItem(Model):
    """Order item model."""

    id = AutoField()
    order_id = ForeignKey(Order, on_delete="CASCADE", related_name="items")
    product_id = ForeignKey(Product, on_delete="RESTRICT", related_name="order_items")
    quantity = IntegerField(null=False)
    price = DecimalField(max_digits=10, decimal_places=2, null=False)

    class Meta:
        table_name = "order_items"
        indexes = ["order_id", "product_id"]


# Import all models to register them
__all__ = ["User", "Category", "Product", "Order", "OrderItem"]
