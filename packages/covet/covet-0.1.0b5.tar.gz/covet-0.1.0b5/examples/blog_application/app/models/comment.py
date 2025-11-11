"""
Comment Model

Handles comments and nested replies on blog posts.
"""

from covet.database.orm import Model, Index
from covet.database.orm.fields import TextField, DateTimeField, IntegerField
from covet.database.orm.relationships import ForeignKey


class Comment(Model):
    """
    Blog post comment with nested reply support.

    Fields:
        post: Associated blog post
        author: Comment author
        content: Comment text
        parent: Parent comment (for replies)
        upvotes: Number of upvotes
        downvotes: Number of downvotes
        is_spam: Spam flag
        is_approved: Moderation status
        created_at: When comment was posted
        updated_at: Last edit time

    Example:
        # Top-level comment
        comment = await Comment.create(
            post_id=post.id,
            author_id=user.id,
            content='Great article!'
        )

        # Reply to comment
        reply = await Comment.create(
            post_id=post.id,
            author_id=user.id,
            parent_id=comment.id,
            content='Thanks!'
        )
    """

    post = ForeignKey('Post', on_delete='CASCADE', related_name='comments')
    author = ForeignKey('User', on_delete='CASCADE', related_name='comments')
    content = TextField()

    # Nested comments support
    parent = ForeignKey(
        'self',
        on_delete='CASCADE',
        related_name='replies',
        nullable=True
    )

    # Engagement
    upvotes = IntegerField(default=0)
    downvotes = IntegerField(default=0)

    # Moderation
    is_spam = IntegerField(default=False)
    is_approved = IntegerField(default=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
        indexes = [
            Index(fields=['post']),
            Index(fields=['author']),
            Index(fields=['parent']),
            Index(fields=['is_approved'])
        ]

    async def get_reply_count(self) -> int:
        """Get number of replies to this comment."""
        return await Comment.objects.filter(parent_id=self.id).count()

    async def upvote(self) -> None:
        """Increment upvote count."""
        self.upvotes += 1
        await self.save(update_fields=['upvotes'])

    async def downvote(self) -> None:
        """Increment downvote count."""
        self.downvotes += 1
        await self.save(update_fields=['downvotes'])

    def __str__(self) -> str:
        return f'Comment by {self.author.username} on {self.post.title}'


__all__ = ['Comment']
