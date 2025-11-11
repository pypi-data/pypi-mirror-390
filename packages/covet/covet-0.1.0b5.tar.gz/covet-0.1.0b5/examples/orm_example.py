"""
CovetPy ORM Example Application

A complete example demonstrating the Django-style ORM capabilities
of CovetPy, including models, relationships, queries, and signals.

This example implements a simplified blog platform with:
- Users (authors)
- Posts (blog articles)
- Comments (on posts)
- Tags (many-to-many with posts)
- Categories (for organizing posts)
"""

import asyncio
import logging
from datetime import datetime, timedelta
from covet.database.orm import (
    Model, CharField, TextField, EmailField, DateTimeField,
    BooleanField, IntegerField, ForeignKey, ManyToManyField,
    Index, Count, Avg
)
from covet.database.orm.signals import post_save, pre_delete, receiver


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

class User(Model):
    """User/Author model."""

    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)
    full_name = CharField(max_length=200)
    bio = TextField(nullable=True)
    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['email']),
            Index(fields=['username']),
            Index(fields=['is_active', 'is_staff'])
        ]

    def clean(self):
        """Custom validation."""
        if 'admin' in self.username.lower() and not self.is_staff:
            raise ValueError("Admin username requires staff privileges")

    def __str__(self):
        return f"User({self.username})"


class Category(Model):
    """Post category model."""

    name = CharField(max_length=100, unique=True)
    slug = CharField(max_length=100, unique=True)
    description = TextField(nullable=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return f"Category({self.name})"


class Tag(Model):
    """Tag model for posts."""

    name = CharField(max_length=50, unique=True)
    slug = CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self):
        return f"Tag({self.name})"


class Post(Model):
    """Blog post model."""

    title = CharField(max_length=200)
    slug = CharField(max_length=200, unique=True)
    content = TextField()
    excerpt = TextField(nullable=True)

    # Relationships
    author = ForeignKey(User, on_delete='CASCADE', related_name='posts')
    category = ForeignKey(
        Category,
        on_delete='SET_NULL',
        nullable=True,
        related_name='posts'
    )
    tags = ManyToManyField(Tag, related_name='posts')

    # Status
    published = BooleanField(default=False)
    featured = BooleanField(default=False)
    views = IntegerField(default=0)

    # Timestamps
    published_at = DateTimeField(nullable=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            Index(fields=['slug']),
            Index(fields=['published', 'published_at']),
            Index(fields=['author', 'published'])
        ]
        unique_together = [('slug', 'author')]

    def clean(self):
        """Validate post data."""
        if self.published and not self.published_at:
            self.published_at = datetime.now()

    def __str__(self):
        return f"Post({self.title})"


class Comment(Model):
    """Comment model."""

    post = ForeignKey(Post, on_delete='CASCADE', related_name='comments')
    author = ForeignKey(User, on_delete='CASCADE', related_name='comments')
    content = TextField()
    approved = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['post', 'approved']),
            Index(fields=['author'])
        ]

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"


# ============================================================================
# SIGNAL HANDLERS
# ============================================================================

@receiver(post_save, sender=User)
async def user_created_handler(sender, instance, created, **kwargs):
    """Handle user creation."""
    if created:
        logger.info(f"New user registered: {instance.username}")
        # In real app: send welcome email, create profile, etc.


@receiver(post_save, sender=Post)
async def post_published_handler(sender, instance, created, **kwargs):
    """Handle post publication."""
    if instance.published and created:
        logger.info(f"New post published: {instance.title}")
        # In real app: notify followers, send to RSS, etc.


@receiver(pre_delete, sender=Post)
async def post_deleted_handler(sender, instance, **kwargs):
    """Handle post deletion."""
    logger.info(f"Deleting post: {instance.title}")
    # In real app: clean up files, notify author, etc.


# ============================================================================
# EXAMPLE USAGE FUNCTIONS
# ============================================================================

async def create_sample_data():
    """Create sample blog data."""
    logger.info("Creating sample data...")

    # Create users
    alice = await User.objects.create(
        username='alice',
        email='alice@example.com',
        full_name='Alice Johnson',
        bio='Tech enthusiast and blogger',
        is_staff=True
    )

    bob = await User.objects.create(
        username='bob',
        email='bob@example.com',
        full_name='Bob Smith',
        bio='Software developer'
    )

    # Create categories
    tech_cat = await Category.objects.create(
        name='Technology',
        slug='technology',
        description='Tech news and tutorials'
    )

    dev_cat = await Category.objects.create(
        name='Development',
        slug='development',
        description='Software development topics'
    )

    # Create tags
    python_tag = await Tag.objects.create(name='Python', slug='python')
    orm_tag = await Tag.objects.create(name='ORM', slug='orm')
    web_tag = await Tag.objects.create(name='Web Dev', slug='web-dev')
    tutorial_tag = await Tag.objects.create(name='Tutorial', slug='tutorial')

    # Create posts
    post1 = await Post.objects.create(
        title='Complete Guide to CovetPy ORM',
        slug='covetpy-orm-guide',
        content='This is a comprehensive guide to using the CovetPy ORM...',
        excerpt='Learn how to use CovetPy ORM',
        author=alice,
        category=tech_cat,
        published=True,
        featured=True,
        views=150
    )
    await post1.tags.add(python_tag, orm_tag, tutorial_tag)

    post2 = await Post.objects.create(
        title='Building Web Apps with CovetPy',
        slug='building-web-apps',
        content='Learn how to build modern web applications...',
        excerpt='Web development tutorial',
        author=alice,
        category=dev_cat,
        published=True,
        views=89
    )
    await post2.tags.add(python_tag, web_tag, tutorial_tag)

    post3 = await Post.objects.create(
        title='Database Performance Tips',
        slug='database-performance',
        content='Optimize your database queries...',
        excerpt='Performance optimization guide',
        author=bob,
        category=dev_cat,
        published=False  # Draft
    )
    await post3.tags.add(orm_tag)

    # Create comments
    await Comment.objects.create(
        post=post1,
        author=bob,
        content='Great tutorial! Very helpful.',
        approved=True
    )

    await Comment.objects.create(
        post=post1,
        author=bob,
        content='Thanks for sharing this.',
        approved=True
    )

    logger.info("Sample data created successfully!")


async def demonstrate_queries():
    """Demonstrate various ORM query capabilities."""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING ORM QUERIES")
    logger.info("="*60)

    # 1. Simple queries
    logger.info("\n1. Get all published posts:")
    published_posts = await Post.objects.filter(published=True).all()
    for post in published_posts:
        logger.info(f"   - {post.title} (views: {post.views})")

    # 2. Query with relationships (select_related)
    logger.info("\n2. Posts with author info (optimized with select_related):")
    posts_with_authors = await Post.objects.select_related('author', 'category').all()
    for post in posts_with_authors:
        logger.info(f"   - {post.title} by {post.author.username}")

    # 3. Field lookups
    logger.info("\n3. Search posts with 'ORM' in title (case-insensitive):")
    orm_posts = await Post.objects.filter(
        title__icontains='orm'
    ).all()
    for post in orm_posts:
        logger.info(f"   - {post.title}")

    # 4. Complex filtering
    logger.info("\n4. Popular published posts (views >= 100):")
    popular_posts = await Post.objects.filter(
        published=True,
        views__gte=100
    ).order_by('-views').all()
    for post in popular_posts:
        logger.info(f"   - {post.title} ({post.views} views)")

    # 5. Aggregation
    logger.info("\n5. Statistics:")
    stats = await Post.objects.filter(published=True).aggregate(
        total_posts=Count('*'),
        avg_views=Avg('views')
    )
    logger.info(f"   Total published posts: {stats['total_posts']}")
    logger.info(f"   Average views: {stats['avg_views']:.1f}")

    # 6. Annotation
    logger.info("\n6. Posts with comment count:")
    posts_with_counts = await Post.objects.annotate(
        comment_count=Count('comments')
    ).filter(comment_count__gte=1).all()
    for post in posts_with_counts:
        logger.info(f"   - {post.title} ({post.comment_count} comments)")

    # 7. Values queries
    logger.info("\n7. Post titles and slugs only (as dicts):")
    post_data = await Post.objects.filter(
        published=True
    ).values('title', 'slug')
    for data in post_data:
        logger.info(f"   - {data['title']} -> {data['slug']}")

    # 8. Reverse relationships
    logger.info("\n8. Alice's posts (reverse ForeignKey):")
    alice = await User.objects.get(username='alice')
    alice_posts = await alice.posts.filter(published=True).all()
    logger.info(f"   Alice has {len(alice_posts)} published posts:")
    for post in alice_posts:
        logger.info(f"   - {post.title}")

    # 9. ManyToMany queries
    logger.info("\n9. Posts tagged with 'Python':")
    python_tag = await Tag.objects.get(slug='python')
    python_posts = await python_tag.posts.all()
    for post in python_posts:
        logger.info(f"   - {post.title}")

    # 10. Get or create
    logger.info("\n10. Get or create tag:")
    tag, created = await Tag.objects.get_or_create(
        slug='django',
        defaults={'name': 'Django'}
    )
    logger.info(f"   Tag: {tag.name} (created: {created})")

    # 11. Update queries
    logger.info("\n11. Incrementing view counts:")
    await Post.objects.filter(
        slug='covetpy-orm-guide'
    ).update(views=200)
    logger.info("   View count updated")

    # 12. Count and exists
    logger.info("\n12. Quick checks:")
    total_users = await User.objects.count()
    has_drafts = await Post.objects.filter(published=False).exists()
    logger.info(f"   Total users: {total_users}")
    logger.info(f"   Has draft posts: {has_drafts}")


async def demonstrate_crud():
    """Demonstrate CRUD operations."""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING CRUD OPERATIONS")
    logger.info("="*60)

    # CREATE
    logger.info("\n1. CREATE - New user:")
    new_user = await User.objects.create(
        username='charlie',
        email='charlie@example.com',
        full_name='Charlie Brown'
    )
    logger.info(f"   Created: {new_user.username} (ID: {new_user.id})")

    # READ
    logger.info("\n2. READ - Get user:")
    user = await User.objects.get(username='charlie')
    logger.info(f"   Found: {user.full_name}")

    # UPDATE
    logger.info("\n3. UPDATE - Update user:")
    user.bio = 'Newly added bio text'
    await user.save()
    logger.info(f"   Updated bio for {user.username}")

    # Refresh from DB
    logger.info("\n4. REFRESH - Reload from database:")
    await user.refresh()
    logger.info(f"   Refreshed: {user.username}")

    # DELETE
    logger.info("\n5. DELETE - Remove user:")
    username = user.username
    await user.delete()
    logger.info(f"   Deleted: {username}")

    # Verify deletion
    try:
        await User.objects.get(username='charlie')
    except User.DoesNotExist:
        logger.info("   Verified: User no longer exists")


async def demonstrate_validation():
    """Demonstrate validation capabilities."""
    logger.info("\n" + "="*60)
    logger.info("DEMONSTRATING VALIDATION")
    logger.info("="*60)

    # 1. Field validation
    logger.info("\n1. Email validation:")
    try:
        invalid_user = User(
            username='test',
            email='not-an-email',
            full_name='Test User'
        )
        invalid_user.validate()
    except ValueError as e:
        logger.info(f"   Caught validation error: {e}")

    # 2. Custom validation
    logger.info("\n2. Custom clean() validation:")
    try:
        admin_user = User(
            username='admin_user',
            email='admin@example.com',
            full_name='Admin',
            is_staff=False
        )
        admin_user.clean()
    except ValueError as e:
        logger.info(f"   Caught clean() error: {e}")


async def main():
    """Main example runner."""
    logger.info("="*60)
    logger.info("COVETPY ORM EXAMPLE APPLICATION")
    logger.info("="*60)

    try:
        # Create sample data
        await create_sample_data()

        # Demonstrate various features
        await demonstrate_queries()
        await demonstrate_crud()
        await demonstrate_validation()

        logger.info("\n" + "="*60)
        logger.info("EXAMPLE COMPLETED SUCCESSFULLY!")
        logger.info("="*60)

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == '__main__':
    asyncio.run(main())
