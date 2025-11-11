#!/usr/bin/env python3
"""
CovetPy ORM Demonstration

A simple demonstration of the CovetPy ORM capabilities.
"""

import os
import sys
import tempfile
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from covet.orm import (
    Model, CharField, IntegerField, BooleanField, DateTimeField, 
    TextField, JSONField, AutoField, ForeignKey,
    ConnectionConfig, register_database,
    Q, Count, Avg
)


# Define Models
class User(Model):
    """User model."""
    
    id = AutoField()
    username = CharField(max_length=50, unique=True)
    email = CharField(max_length=100)
    is_active = BooleanField(default=True)
    created_at = DateTimeField()
    
    class Meta:
        table_name = 'users'


class Post(Model):
    """Post model."""
    
    id = AutoField()
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, on_delete='CASCADE')
    view_count = IntegerField(default=0)
    is_published = BooleanField(default=False)
    created_at = DateTimeField()
    
    class Meta:
        table_name = 'posts'


def main():
    """Main demonstration."""
    print("🚀 CovetPy ORM Demonstration")
    print("=" * 40)
    
    # Setup database
    print("Setting up database...")
    db_file = tempfile.mktemp(suffix='.db')
    
    config = ConnectionConfig(
        engine='sqlite',
        database=db_file
    )
    
    register_database('default', config)
    print(f"✓ Database: {db_file}")
    
    # Create tables (simplified for demo)
    from covet.orm.connection import get_connection_pool
    pool = get_connection_pool()
    
    with pool.connection() as conn:
        # Create users table
        conn.execute("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)
        
        # Create posts table
        conn.execute("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                author_id INTEGER NOT NULL,
                view_count INTEGER DEFAULT 0,
                is_published INTEGER DEFAULT 0,
                created_at TEXT,
                FOREIGN KEY (author_id) REFERENCES users(id)
            )
        """)
        
        conn.commit()
    
    print("✓ Tables created")
    
    # Create some users
    print("\nCreating users...")
    
    users_data = [
        {'username': 'alice', 'email': 'alice@example.com'},
        {'username': 'bob', 'email': 'bob@example.com'},
        {'username': 'charlie', 'email': 'charlie@example.com'},
    ]
    
    users = []
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            created_at=datetime.now()
        )
        user.save()
        users.append(user)
        print(f"  ✓ Created user: {user.username} (ID: {user.id})")
    
    # Create some posts
    print("\nCreating posts...")
    
    posts_data = [
        {'title': 'Getting Started with CovetPy', 'content': 'CovetPy is amazing!', 'author': users[0]},
        {'title': 'Advanced ORM Features', 'content': 'Deep dive into ORM capabilities.', 'author': users[1]},
        {'title': 'Performance Tips', 'content': 'How to optimize your queries.', 'author': users[0]},
        {'title': 'Async Operations', 'content': 'Using async with CovetPy ORM.', 'author': users[2]},
    ]
    
    posts = []
    for i, post_data in enumerate(posts_data):
        post = Post(
            title=post_data['title'],
            content=post_data['content'],
            author=post_data['author'],
            view_count=(i + 1) * 100,
            is_published=i % 2 == 0,
            created_at=datetime.now()
        )
        post.save()
        posts.append(post)
        print(f"  ✓ Created post: {post.title} (ID: {post.id})")
    
    # Demonstrate queries
    print("\n📊 Query Demonstrations")
    print("-" * 30)
    
    # Basic queries
    print("1. Basic Queries:")
    all_users = User.objects.all()
    print(f"   Total users: {len(all_users)}")
    
    active_users = User.objects.filter(is_active=True)
    print(f"   Active users: {active_users.count()}")
    
    # Debug: Check how many alice users exist
    alice_users = User.objects.filter(username='alice')
    print(f"   Alice users found: {alice_users.count()}")
    
    if alice_users.count() > 0:
        alice = alice_users.first()
        print(f"   Found user: {alice.username} ({alice.email})")
    else:
        print("   No alice user found!")
        alice = None
    
    # Advanced queries
    print("\n2. Advanced Queries:")
    
    published_posts = Post.objects.filter(is_published=True)
    print(f"   Published posts: {published_posts.count()}")
    
    high_view_posts = Post.objects.filter(view_count__gt=200)
    print(f"   High-view posts: {high_view_posts.count()}")
    
    if alice:
        alice_posts = Post.objects.filter(author=alice)
        print(f"   Alice's posts: {alice_posts.count()}")
    else:
        print("   Cannot check Alice's posts - Alice not found")
    
    # Complex queries with Q objects
    print("\n3. Complex Queries:")
    
    popular_or_published = Post.objects.filter(
        Q(view_count__gt=300) | Q(is_published=True)
    )
    print(f"   Popular or published posts: {popular_or_published.count()}")
    
    # Ordering
    print("\n4. Ordering:")
    
    top_posts = Post.objects.all().order_by('-view_count')[:2]
    print("   Top posts by views:")
    for post in top_posts:
        print(f"     - {post.title} ({post.view_count} views)")
    
    # Aggregation
    print("\n5. Aggregation:")
    
    stats = Post.objects.all().aggregate(
        total_posts=Count('id'),
        avg_views=Avg('view_count')
    )
    print(f"   Total posts: {stats.get('total_posts', 0)}")
    print(f"   Average views: {stats.get('avg_views', 0):.1f}")
    
    # Updates
    print("\n6. Updates:")
    
    # Update single object
    if alice:
        alice.email = 'alice.new@example.com'
        alice.save()
        print(f"   Updated Alice's email: {alice.email}")
    else:
        print("   Cannot update Alice - not found")
    
    # Bulk update
    updated_count = Post.objects.filter(is_published=False).update(is_published=True)
    print(f"   Published {updated_count} posts")
    
    # Final stats
    print("\n📈 Final Statistics:")
    print(f"   Total users: {User.objects.count()}")
    print(f"   Total posts: {Post.objects.count()}")
    print(f"   Published posts: {Post.objects.filter(is_published=True).count()}")
    
    print(f"\n✅ Demo completed successfully!")
    print(f"📁 Database file: {db_file}")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)