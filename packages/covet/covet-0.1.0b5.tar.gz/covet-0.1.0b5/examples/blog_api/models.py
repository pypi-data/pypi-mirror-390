"""
Database models for Blog API.

Models:
- User: Blog users with authentication
- Category: Post categories
- Tag: Post tags
- Post: Blog posts
- Comment: Post comments
"""

from covet.orm import Model
from covet.orm.fields import (
    AutoField, CharField, TextField, EmailField, DateTimeField,
    BooleanField, ForeignKey, ManyToManyField, IntegerField
)
from datetime import datetime
from typing import Optional, List


class User(Model):
    """User model for authentication and blog authoring."""

    id = AutoField(primary_key=True)
    username = CharField(max_length=50, unique=True, null=False, db_index=True)
    email = EmailField(unique=True, null=False, db_index=True)
    password_hash = CharField(max_length=255, null=False)
    first_name = CharField(max_length=50, blank=True, default='')
    last_name = CharField(max_length=50, blank=True, default='')
    bio = TextField(blank=True, default='')
    avatar_url = CharField(max_length=500, blank=True, default='')
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = 'users'
        ordering = ['-created_at']
        indexes = [
            ('username',),
            ('email',),
        ]

    def __str__(self):
        return self.username

    def get_full_name(self) -> str:
        """Return user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def to_dict(self, include_email: bool = False) -> dict:
        """Convert to dictionary (excludes password_hash)."""
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data


class Category(Model):
    """Blog post category."""

    id = AutoField(primary_key=True)
    name = CharField(max_length=100, unique=True, null=False)
    slug = CharField(max_length=100, unique=True, null=False, db_index=True)
    description = TextField(blank=True, default='')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        table_name = 'categories'
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
        }


class Tag(Model):
    """Blog post tag."""

    id = AutoField(primary_key=True)
    name = CharField(max_length=50, unique=True, null=False)
    slug = CharField(max_length=50, unique=True, null=False, db_index=True)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        table_name = 'tags'
        ordering = ['name']

    def __str__(self):
        return self.name

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
        }


class Post(Model):
    """Blog post."""

    id = AutoField(primary_key=True)
    title = CharField(max_length=200, null=False)
    slug = CharField(max_length=200, unique=True, null=False, db_index=True)
    content = TextField(null=False)
    excerpt = TextField(blank=True, default='')
    author = ForeignKey(User, on_delete='CASCADE', related_name='posts')
    category = ForeignKey(Category, on_delete='SET_NULL', null=True, related_name='posts')
    tags = ManyToManyField(Tag, related_name='posts')
    published = BooleanField(default=False)
    published_at = DateTimeField(null=True, blank=True)
    view_count = IntegerField(default=0)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = 'posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            ('slug',),
            ('published',),
            ('author_id',),
            ('category_id',),
            ('published_at',),
        ]

    def __str__(self):
        return self.title

    async def publish(self):
        """Publish the post."""
        self.published = True
        self.published_at = datetime.now()
        await self.save()

    async def unpublish(self):
        """Unpublish the post."""
        self.published = False
        self.published_at = None
        await self.save()

    async def increment_view_count(self):
        """Increment view count atomically."""
        from covet.orm import F
        await Post.objects.filter(id=self.id).update(
            view_count=F('view_count') + 1
        )
        self.view_count += 1

    async def get_tags(self) -> List['Tag']:
        """Get all tags for this post."""
        return await self.tags.all()

    async def get_comments_count(self) -> int:
        """Get number of comments."""
        return await Comment.objects.filter(post=self).count()

    def to_dict(self, include_content: bool = True, include_author: bool = True) -> dict:
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'excerpt': self.excerpt,
            'published': self.published,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'view_count': self.view_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_content:
            data['content'] = self.content

        if include_author and self.author:
            data['author'] = self.author.to_dict()

        if self.category:
            data['category'] = self.category.to_dict()

        return data


class Comment(Model):
    """Post comment."""

    id = AutoField(primary_key=True)
    post = ForeignKey(Post, on_delete='CASCADE', related_name='comments')
    author = ForeignKey(User, on_delete='CASCADE', related_name='comments')
    content = TextField(null=False)
    parent = ForeignKey('self', on_delete='CASCADE', null=True, blank=True, related_name='replies')
    is_edited = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        table_name = 'comments'
        ordering = ['-created_at']
        indexes = [
            ('post_id',),
            ('author_id',),
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"

    async def get_replies(self) -> List['Comment']:
        """Get all replies to this comment."""
        return await Comment.objects.filter(parent=self).all()

    async def get_replies_count(self) -> int:
        """Get number of replies."""
        return await Comment.objects.filter(parent=self).count()

    def to_dict(self, include_author: bool = True, include_post: bool = False) -> dict:
        """Convert to dictionary."""
        data = {
            'id': self.id,
            'content': self.content,
            'is_edited': self.is_edited,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_author and self.author:
            data['author'] = self.author.to_dict()

        if include_post and self.post:
            data['post'] = {
                'id': self.post.id,
                'title': self.post.title,
                'slug': self.post.slug,
            }

        if self.parent:
            data['parent_id'] = self.parent.id

        return data


# Helper function to create slug from title
def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        URL-friendly slug
    """
    import re
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = re.sub(r'^-+|-+$', '', text)
    return text


# Database initialization
async def init_database():
    """Initialize database with tables."""
    from covet.orm import get_connection

    connection = await get_connection()

    # Create tables
    await connection.create_tables([
        User,
        Category,
        Tag,
        Post,
        Comment,
    ])

    print("Database tables created successfully")


# Seed initial data
async def seed_initial_data():
    """Seed database with initial data for testing."""
    from covet.security import PasswordHasher

    hasher = PasswordHasher()

    # Create admin user
    admin_password = hasher.hash_password('admin123')
    admin = await User.objects.create(
        username='admin',
        email='admin@example.com',
        password_hash=admin_password,
        first_name='Admin',
        last_name='User',
        is_staff=True,
        bio='Blog administrator'
    )

    # Create demo user
    demo_password = hasher.hash_password('demo123')
    demo_user = await User.objects.create(
        username='demo',
        email='demo@example.com',
        password_hash=demo_password,
        first_name='Demo',
        last_name='User',
        bio='Demo user for testing'
    )

    # Create categories
    tutorials = await Category.objects.create(
        name='Tutorials',
        slug='tutorials',
        description='Step-by-step tutorials and guides'
    )

    articles = await Category.objects.create(
        name='Articles',
        slug='articles',
        description='In-depth articles and discussions'
    )

    news = await Category.objects.create(
        name='News',
        slug='news',
        description='Latest news and updates'
    )

    # Create tags
    python_tag = await Tag.objects.create(name='Python', slug='python')
    web_dev_tag = await Tag.objects.create(name='Web Development', slug='web-development')
    api_tag = await Tag.objects.create(name='API', slug='api')
    covetpy_tag = await Tag.objects.create(name='CovetPy', slug='covetpy')

    # Create sample posts
    post1 = await Post.objects.create(
        title='Getting Started with CovetPy',
        slug='getting-started-with-covetpy',
        content='CovetPy is a modern Python web framework...',
        excerpt='Learn how to build your first API with CovetPy',
        author=admin,
        category=tutorials,
        published=True,
        published_at=datetime.now()
    )
    await post1.tags.add(python_tag, web_dev_tag, covetpy_tag)

    post2 = await Post.objects.create(
        title='Building REST APIs with CovetPy',
        slug='building-rest-apis-with-covetpy',
        content='REST APIs are the backbone of modern web applications...',
        excerpt='Complete guide to building REST APIs',
        author=admin,
        category=tutorials,
        published=True,
        published_at=datetime.now()
    )
    await post2.tags.add(python_tag, api_tag, covetpy_tag)

    post3 = await Post.objects.create(
        title='CovetPy vs FastAPI: A Comparison',
        slug='covetpy-vs-fastapi-comparison',
        content='Both frameworks are excellent choices...',
        excerpt='Comparing two popular Python web frameworks',
        author=demo_user,
        category=articles,
        published=True,
        published_at=datetime.now()
    )
    await post3.tags.add(python_tag, web_dev_tag)

    # Create sample comments
    await Comment.objects.create(
        post=post1,
        author=demo_user,
        content='Great tutorial! Very helpful for beginners.'
    )

    await Comment.objects.create(
        post=post1,
        author=demo_user,
        content='Looking forward to more tutorials like this.'
    )

    await Comment.objects.create(
        post=post2,
        author=admin,
        content='Thanks for reading! Let me know if you have questions.'
    )

    print("Initial data seeded successfully")
    print(f"Created users: admin (password: admin123), demo (password: demo123)")
    print(f"Created {await Category.objects.count()} categories")
    print(f"Created {await Tag.objects.count()} tags")
    print(f"Created {await Post.objects.count()} posts")
    print(f"Created {await Comment.objects.count()} comments")


if __name__ == '__main__':
    """Run database initialization and seeding."""
    import asyncio

    async def main():
        await init_database()
        await seed_initial_data()

    asyncio.run(main())
