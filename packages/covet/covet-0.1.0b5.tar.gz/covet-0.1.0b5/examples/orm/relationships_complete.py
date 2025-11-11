"""
Complete Relationship Examples for CovetPy ORM

Demonstrates all relationship types:
1. ForeignKey (Many-to-One)
2. OneToOneField
3. ManyToManyField (with and without through)
4. GenericForeignKey
5. Self-referential relationships
6. Polymorphic models

Run this to see relationship patterns in action.
"""

import asyncio
from datetime import datetime

from src.covet.database.orm.models import Model
from src.covet.database.orm.fields import (
    CharField, TextField, IntegerField, DateTimeField,
    EmailField, BooleanField
)
from src.covet.database.orm.relationships import (
    ForeignKey, OneToOneField, ManyToManyField,
    GenericForeignKey, GenericRelation,
    CASCADE, PROTECT, SET_NULL
)


# =============================================================================
# 1. FOREIGNKEY (Many-to-One)
# =============================================================================

class Author(Model):
    """Author can have many books."""
    name = CharField(max_length=100)
    email = EmailField(unique=True)
    bio = TextField(nullable=True)

    class Meta:
        db_table = 'authors'


class Book(Model):
    """Book belongs to one author."""
    title = CharField(max_length=200)
    isbn = CharField(max_length=20, unique=True)
    published_date = DateTimeField()

    # ForeignKey relationship
    author = ForeignKey(
        Author,
        on_delete=CASCADE,
        related_name='books'
    )

    class Meta:
        db_table = 'books'


async def foreignkey_example():
    """Demonstrate ForeignKey usage."""
    print("\n=== ForeignKey Example ===")

    # Create author
    author = await Author.create(
        name='Alice Johnson',
        email='alice@example.com',
        bio='Bestselling author'
    )

    # Create books
    book1 = await Book.create(
        title='Python Mastery',
        isbn='978-0-123456-78-9',
        published_date=datetime.now(),
        author=author
    )

    book2 = await Book.create(
        title='Advanced Python',
        isbn='978-0-987654-32-1',
        published_date=datetime.now(),
        author=author
    )

    # Forward relation: book -> author
    print(f"Book: {book1.title}")
    print(f"Author: {(await book1.author).name}")

    # Reverse relation: author -> books
    books = await author.books.all()
    print(f"\nAuthor: {author.name}")
    print(f"Books: {[b.title for b in books]}")


# =============================================================================
# 2. ONETOONEFIELD
# =============================================================================

class User(Model):
    """User model."""
    username = CharField(max_length=100, unique=True)
    email = EmailField(unique=True)

    class Meta:
        db_table = 'users'


class UserProfile(Model):
    """One-to-one profile for user."""
    user = OneToOneField(
        User,
        on_delete=CASCADE,
        related_name='profile'
    )

    bio = TextField(nullable=True)
    avatar_url = CharField(max_length=500, nullable=True)
    date_of_birth = DateTimeField(nullable=True)

    class Meta:
        db_table = 'user_profiles'


async def onetoone_example():
    """Demonstrate OneToOneField usage."""
    print("\n=== OneToOneField Example ===")

    # Create user
    user = await User.create(
        username='bob',
        email='bob@example.com'
    )

    # Create profile
    profile = await UserProfile.create(
        user=user,
        bio='Software developer',
        avatar_url='https://example.com/avatar.jpg'
    )

    # Forward relation: profile -> user
    print(f"Profile bio: {profile.bio}")
    print(f"User: {(await profile.user).username}")

    # Reverse relation: user -> profile
    user_profile = await user.profile
    print(f"\nUser: {user.username}")
    print(f"Bio: {user_profile.bio}")


# =============================================================================
# 3. MANYTOMANYFIELD
# =============================================================================

class Tag(Model):
    """Tag model for posts."""
    name = CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'tags'


class Post(Model):
    """Blog post with many tags."""
    title = CharField(max_length=200)
    content = TextField()
    author = ForeignKey(User, on_delete=CASCADE, related_name='posts')

    # ManyToMany relationship
    tags = ManyToManyField(Tag, related_name='posts')

    class Meta:
        db_table = 'posts'


async def manytomany_example():
    """Demonstrate ManyToManyField usage."""
    print("\n=== ManyToManyField Example ===")

    # Create user and post
    user = await User.objects.get(username='bob')
    post = await Post.create(
        title='Python Tips',
        content='Here are some Python tips...',
        author=user
    )

    # Create tags
    tag1 = await Tag.create(name='Python')
    tag2 = await Tag.create(name='Programming')
    tag3 = await Tag.create(name='Tutorial')

    # Add tags to post
    await post.tags.add(tag1, tag2, tag3)

    # Get all tags for post
    post_tags = await post.tags.all()
    print(f"Post: {post.title}")
    print(f"Tags: {[t.name for t in post_tags]}")

    # Reverse: get all posts for tag
    python_posts = await tag1.posts.all()
    print(f"\nTag: {tag1.name}")
    print(f"Posts: {[p.title for p in python_posts]}")

    # Remove a tag
    await post.tags.remove(tag3)
    print(f"\nAfter removing 'Tutorial': {[t.name for t in await post.tags.all()]}")

    # Set to specific list
    await post.tags.set([tag1])
    print(f"After set: {[t.name for t in await post.tags.all()]}")


# =============================================================================
# 4. MANYTOMANY WITH THROUGH MODEL
# =============================================================================

class Group(Model):
    """Group model."""
    name = CharField(max_length=100)
    description = TextField(nullable=True)

    class Meta:
        db_table = 'groups'


class Membership(Model):
    """Through model for User-Group relationship."""
    user = ForeignKey(User, on_delete=CASCADE)
    group = ForeignKey(Group, on_delete=CASCADE)

    # Extra fields
    date_joined = DateTimeField(auto_now_add=True)
    role = CharField(max_length=50, default='member')
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'memberships'
        unique_together = [('user', 'group')]


class GroupWithMembers(Model):
    """Group with custom through model."""
    name = CharField(max_length=100)

    # ManyToMany with through
    members = ManyToManyField(
        User,
        through=Membership,
        through_fields=('group', 'user'),
        related_name='groups'
    )

    class Meta:
        db_table = 'groups_with_members'


async def manytomany_through_example():
    """Demonstrate ManyToMany with through model."""
    print("\n=== ManyToMany with Through Model Example ===")

    user = await User.objects.get(username='bob')
    group = await Group.create(
        name='Developers',
        description='Developer community'
    )

    # Add member with extra data
    await group.members.add(user, through_defaults={'role': 'admin'})

    # Access through model
    membership = await Membership.objects.get(user=user, group=group)
    print(f"User: {user.username}")
    print(f"Group: {group.name}")
    print(f"Role: {membership.role}")
    print(f"Joined: {membership.date_joined}")


# =============================================================================
# 5. GENERIC FOREIGN KEY
# =============================================================================

from src.covet.database.orm.relationships import ContentType


class Comment(Model):
    """Generic comment that can attach to any model."""
    content_type_id = IntegerField()
    object_id = IntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    text = TextField()
    author = ForeignKey(User, on_delete=CASCADE, related_name='comments')
    created_at = DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comments'


class PostWithComments(Post):
    """Post with generic comments."""
    comments = GenericRelation(Comment)

    class Meta:
        proxy = True


class Photo(Model):
    """Photo model."""
    caption = CharField(max_length=200)
    url = CharField(max_length=500)
    owner = ForeignKey(User, on_delete=CASCADE, related_name='photos')

    # Generic relation
    comments = GenericRelation(Comment)

    class Meta:
        db_table = 'photos'


async def generic_fk_example():
    """Demonstrate GenericForeignKey usage."""
    print("\n=== GenericForeignKey Example ===")

    user = await User.objects.get(username='bob')

    # Create post and photo
    post = await Post.objects.first()

    photo = await Photo.create(
        caption='Sunset',
        url='https://example.com/sunset.jpg',
        owner=user
    )

    # Create comments on different objects
    post_comment = await Comment.create(
        content_object=post,
        text='Great post!',
        author=user
    )

    photo_comment = await Comment.create(
        content_object=photo,
        text='Beautiful photo!',
        author=user
    )

    # Access generic FK
    print(f"Post comment on: {type(await post_comment.content_object).__name__}")
    print(f"Photo comment on: {type(await photo_comment.content_object).__name__}")

    # Reverse access through generic relation
    post_comments = await post.comments.all()
    photo_comments = await photo.comments.all()

    print(f"\nPost has {len(post_comments)} comments")
    print(f"Photo has {len(photo_comments)} comments")


# =============================================================================
# 6. SELF-REFERENTIAL RELATIONSHIPS
# =============================================================================

class Category(Model):
    """Hierarchical category with self-reference."""
    name = CharField(max_length=100)

    parent = ForeignKey(
        'self',
        on_delete=SET_NULL,
        nullable=True,
        related_name='children'
    )

    class Meta:
        db_table = 'categories'


async def self_referential_example():
    """Demonstrate self-referential relationships."""
    print("\n=== Self-Referential Relationship Example ===")

    # Create hierarchy
    electronics = await Category.create(name='Electronics')

    computers = await Category.create(
        name='Computers',
        parent=electronics
    )

    laptops = await Category.create(
        name='Laptops',
        parent=computers
    )

    desktops = await Category.create(
        name='Desktops',
        parent=computers
    )

    # Navigate tree
    print(f"Root: {electronics.name}")

    children = await electronics.children.all()
    print(f"Children: {[c.name for c in children]}")

    parent = await laptops.parent
    print(f"\nLaptops parent: {parent.name}")

    siblings = await laptops.get_siblings()
    print(f"Laptops siblings: {[s.name for s in siblings]}")


# =============================================================================
# 7. SYMMETRIC M2M (FRIENDS)
# =============================================================================

class UserWithFriends(User):
    """User with symmetric friendship."""
    friends = ManyToManyField('self', symmetrical=True)

    class Meta:
        proxy = True


async def symmetric_m2m_example():
    """Demonstrate symmetric ManyToMany."""
    print("\n=== Symmetric ManyToMany Example ===")

    alice = await User.create(username='alice', email='alice@example.com')
    bob = await User.objects.get(username='bob')
    charlie = await User.create(username='charlie', email='charlie@example.com')

    # Add friend (symmetric - works both ways)
    await alice.friends.add(bob)
    await alice.friends.add(charlie)

    # Check both sides
    alice_friends = await alice.friends.all()
    bob_friends = await bob.friends.all()

    print(f"Alice's friends: {[f.username for f in alice_friends]}")
    print(f"Bob's friends: {[f.username for f in bob_friends]}")


# =============================================================================
# MAIN RUNNER
# =============================================================================

async def main():
    """Run all examples."""
    print("=" * 70)
    print("CovetPy ORM - Complete Relationship Examples")
    print("=" * 70)

    try:
        await foreignkey_example()
        await onetoone_example()
        await manytomany_example()
        await manytomany_through_example()
        await generic_fk_example()
        await self_referential_example()
        await symmetric_m2m_example()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(main())
