"""
Blog Post Models

Handles blog posts, images, and metadata.
"""

from covet.database.orm import Model, Index
from covet.database.orm.fields import (
    CharField, TextField, DateTimeField, IntegerField, BooleanField, URLField
)
from covet.database.orm.relationships import ForeignKey, ManyToManyField
from covet.database.orm.aggregates import Count
from datetime import datetime
import re


class Category(Model):
    """
    Blog post category.

    Fields:
        name: Category name
        slug: URL-friendly slug
        description: Category description

    Example:
        category = await Category.create(
            name='Tutorials',
            slug='tutorials',
            description='Programming tutorials and guides'
        )
    """

    name = CharField(max_length=100, unique=True)
    slug = CharField(max_length=100, unique=True, db_index=True)
    description = TextField(nullable=True)

    class Meta:
        db_table = 'categories'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Tag(Model):
    """
    Blog post tag.

    Fields:
        name: Tag name
        slug: URL-friendly slug

    Example:
        tag = await Tag.create(name='Python', slug='python')
    """

    name = CharField(max_length=50, unique=True)
    slug = CharField(max_length=50, unique=True, db_index=True)

    class Meta:
        db_table = 'tags'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @classmethod
    async def get_or_create(cls, name: str) -> 'Tag':
        """
        Get existing tag or create new one.

        Args:
            name: Tag name

        Returns:
            Tag instance

        Example:
            tag = await Tag.get_or_create('python')
        """
        slug = slugify(name)

        # Try to get existing
        tag = await cls.objects.filter(slug=slug).first()
        if tag:
            return tag

        # Create new
        return await cls.create(name=name, slug=slug)


class Post(Model):
    """
    Blog post.

    Fields:
        title: Post title
        slug: URL-friendly slug
        content: Post content (Markdown)
        excerpt: Short summary
        author: Post author (User)
        category: Post category
        tags: Associated tags (many-to-many)
        status: draft/published/archived
        featured: Whether post is featured
        view_count: Number of views
        created_at: When post was created
        updated_at: Last update time
        published_at: When post was published

    Example:
        post = await Post.create(
            title='Getting Started with CovetPy',
            slug='getting-started-covetpy',
            content='# Introduction\n\nCovetPy is...',
            author_id=user.id,
            category_id=category.id,
            status='published'
        )

        # Add tags
        python_tag = await Tag.get_or_create('python')
        await post.tags.add(python_tag)
    """

    # Basic fields
    title = CharField(max_length=200, db_index=True)
    slug = CharField(max_length=200, unique=True, db_index=True)
    content = TextField()
    excerpt = TextField(nullable=True)

    # Relationships
    author = ForeignKey('User', on_delete='CASCADE', related_name='posts')
    category = ForeignKey(Category, on_delete='SET_NULL', related_name='posts', nullable=True)
    tags = ManyToManyField(Tag, related_name='posts')

    # Status
    STATUS_CHOICES = ['draft', 'published', 'archived']
    status = CharField(max_length=20, default='draft', db_index=True)

    featured = BooleanField(default=False)
    allow_comments = BooleanField(default=True)

    # Metrics
    view_count = IntegerField(default=0)

    # Timestamps
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    published_at = DateTimeField(nullable=True)

    class Meta:
        db_table = 'posts'
        ordering = ['-published_at', '-created_at']
        indexes = [
            Index(fields=['slug']),
            Index(fields=['status']),
            Index(fields=['author']),
            Index(fields=['published_at']),
            Index(fields=['-view_count'])  # For popular posts
        ]

    def clean(self) -> None:
        """Validate post data."""
        if not self.slug:
            self.slug = slugify(self.title)

        if self.status not in self.STATUS_CHOICES:
            raise ValueError(f'Invalid status: {self.status}')

        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = datetime.now()

    async def save(self, *args, **kwargs):
        """Save post with automatic slug generation."""
        if not self.slug:
            self.slug = slugify(self.title)

        # Ensure slug is unique
        if not self.id:
            original_slug = self.slug
            counter = 1
            while await Post.objects.filter(slug=self.slug).exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1

        await super().save(*args, **kwargs)

    async def increment_view_count(self) -> None:
        """Increment view count."""
        self.view_count += 1
        await self.save(update_fields=['view_count'])

    async def get_comment_count(self) -> int:
        """Get number of comments on this post."""
        from .comment import Comment
        return await Comment.objects.filter(post_id=self.id).count()

    async def get_related_posts(self, limit: int = 5):
        """
        Get related posts based on tags and category.

        Args:
            limit: Maximum number of related posts

        Returns:
            List of related Post objects

        Example:
            related = await post.get_related_posts(5)
        """
        # Get posts with same category or tags
        related_posts = await Post.objects.filter(
            status='published'
        ).exclude(
            id=self.id
        ).filter(
            category_id=self.category_id
        ).limit(limit)

        return related_posts

    def __str__(self) -> str:
        return self.title


class PostImage(Model):
    """
    Images associated with blog posts.

    Fields:
        post: Associated post
        image_url: Image URL
        caption: Image caption
        alt_text: Alt text for accessibility
        order: Display order

    Example:
        image = await PostImage.create(
            post_id=post.id,
            image_url='https://cdn.example.com/image.jpg',
            caption='Example image',
            alt_text='A screenshot showing...'
        )
    """

    post = ForeignKey(Post, on_delete='CASCADE', related_name='images')
    image_url = URLField()
    caption = CharField(max_length=255, nullable=True)
    alt_text = CharField(max_length=255, nullable=True)
    order = IntegerField(default=0)

    uploaded_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_images'
        ordering = ['order', 'uploaded_at']

    def __str__(self) -> str:
        return f'Image for {self.post.title}'


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text

    Example:
        slug = slugify('Hello World!')  # 'hello-world'
    """
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and special characters with hyphens
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)

    # Remove leading/trailing hyphens
    text = text.strip('-')

    return text


__all__ = ['Category', 'Tag', 'Post', 'PostImage', 'slugify']
