"""
User and Profile Models

Handles user authentication, profiles, and permissions.
"""

from covet.database.orm import Model, Index
from covet.database.orm.fields import (
    CharField, EmailField, BooleanField, DateTimeField,
    TextField, URLField
)
from covet.database.orm.relationships import OneToOneField
from covet.security.passwords import hash_password, verify_password
from datetime import datetime
import secrets


class User(Model):
    """
    User model for authentication.

    Fields:
        username: Unique username (3-50 chars)
        email: Unique email address
        password_hash: Hashed password (bcrypt)
        is_active: Whether user account is active
        is_staff: Whether user can access admin
        is_superuser: Whether user has all permissions
        date_joined: When user registered
        last_login: Last login timestamp

    Methods:
        set_password(password): Hash and set password
        check_password(password): Verify password
        create_auth_token(): Generate JWT token

    Example:
        user = await User.create(
            username='alice',
            email='alice@example.com'
        )
        user.set_password('secure-password')
        await user.save()
    """

    username = CharField(max_length=50, unique=True, db_index=True)
    email = EmailField(unique=True, db_index=True)
    password_hash = CharField(max_length=255)

    is_active = BooleanField(default=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    date_joined = DateTimeField(auto_now_add=True)
    last_login = DateTimeField(nullable=True)

    class Meta:
        db_table = 'users'
        ordering = ['-date_joined']
        indexes = [
            Index(fields=['username']),
            Index(fields=['email']),
            Index(fields=['is_active', 'is_staff'])
        ]

    def set_password(self, password: str) -> None:
        """
        Hash and set user password.

        Args:
            password: Plain text password

        Example:
            user.set_password('my-secure-password')
            await user.save()
        """
        self.password_hash = hash_password(password)

    def check_password(self, password: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password to check

        Returns:
            True if password matches, False otherwise

        Example:
            if user.check_password('entered-password'):
                # Password correct
                pass
        """
        return verify_password(password, self.password_hash)

    async def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login = datetime.now()
        await self.save(update_fields=['last_login'])

    def __str__(self) -> str:
        return self.username


class Profile(Model):
    """
    User profile with additional information.

    Fields:
        user: OneToOne relationship to User
        bio: User biography
        avatar_url: Profile picture URL
        website: Personal website
        location: User location
        github_username: GitHub profile
        twitter_username: Twitter handle

    Example:
        profile = await Profile.create(
            user_id=user.id,
            bio='Software developer interested in Python',
            website='https://alice.dev'
        )
    """

    user = OneToOneField(User, on_delete='CASCADE', related_name='profile')

    bio = TextField(nullable=True)
    avatar_url = URLField(nullable=True)
    website = URLField(nullable=True)
    location = CharField(max_length=100, nullable=True)

    github_username = CharField(max_length=100, nullable=True)
    twitter_username = CharField(max_length=100, nullable=True)

    # Notification preferences
    email_on_comment = BooleanField(default=True)
    email_on_reply = BooleanField(default=True)

    class Meta:
        db_table = 'profiles'

    def __str__(self) -> str:
        return f"Profile for {self.user.username}"


class PasswordResetToken(Model):
    """
    Password reset tokens for email-based password recovery.

    Fields:
        user: User requesting password reset
        token: Unique reset token
        created_at: When token was created
        expires_at: When token expires
        used: Whether token has been used

    Example:
        token = await PasswordResetToken.create(
            user_id=user.id,
            token=secrets.token_urlsafe(32),
            expires_at=datetime.now() + timedelta(hours=24)
        )
    """

    user = OneToOneField(User, on_delete='CASCADE', related_name='reset_token')
    token = CharField(max_length=255, unique=True, db_index=True)

    created_at = DateTimeField(auto_now_add=True)
    expires_at = DateTimeField()
    used = BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'

    @classmethod
    async def create_for_user(cls, user: User) -> 'PasswordResetToken':
        """
        Create password reset token for user.

        Args:
            user: User requesting password reset

        Returns:
            Created PasswordResetToken

        Example:
            reset_token = await PasswordResetToken.create_for_user(user)
            # Send email with reset_token.token
        """
        from datetime import timedelta

        # Delete any existing tokens
        await cls.objects.filter(user_id=user.id).delete()

        # Create new token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=24)

        return await cls.create(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )

    def is_valid(self) -> bool:
        """Check if token is valid (not used, not expired)."""
        return not self.used and datetime.now() < self.expires_at

    async def mark_used(self) -> None:
        """Mark token as used."""
        self.used = True
        await self.save(update_fields=['used'])


__all__ = ['User', 'Profile', 'PasswordResetToken']
