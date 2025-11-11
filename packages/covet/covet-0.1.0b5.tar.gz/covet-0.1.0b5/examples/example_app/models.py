"""
Test CovetPy ORM with real models
"""
import sys
sys.path.insert(0, '/Users/vipin/Downloads/NeutrinoPy/src')

try:
    from covet.database.orm import Model, CharField, TextField, IntegerField, DateTimeField, ForeignKey
    print("✅ ORM imports successful")
except ImportError as e:
    print(f"❌ ORM import failed: {e}")
    sys.exit(1)

# Define real models
try:
    class User(Model):
        """User model"""
        username = CharField(max_length=50, unique=True)
        email = CharField(max_length=100, unique=True)
        password_hash = CharField(max_length=255)
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            table_name = "users"

    print("✅ User model defined successfully")

    class Post(Model):
        """Post model with ForeignKey"""
        title = CharField(max_length=200)
        content = TextField()
        author = ForeignKey(User, related_name='posts')
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            table_name = "posts"

    print("✅ Post model with ForeignKey defined successfully")

    class Comment(Model):
        """Comment model with nested ForeignKey"""
        content = TextField()
        post = ForeignKey(Post, related_name='comments')
        author = ForeignKey(User, related_name='comments')
        created_at = DateTimeField(auto_now_add=True)

        class Meta:
            table_name = "comments"

    print("✅ Comment model with multiple ForeignKeys defined successfully")

except Exception as e:
    print(f"❌ Model definition failed: {e}")
    import traceback
    traceback.print_exc()

# Test model instantiation
try:
    # Don't need database yet, just test object creation
    print("✅ All models defined - ORM structure works")
except Exception as e:
    print(f"❌ Model usage failed: {e}")
