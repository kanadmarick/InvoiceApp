from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class CustomUser(AbstractUser):
    """
    Custom User Model extending Django's AbstractUser.
    Uses UUID as primary key instead of auto-incrementing integers for security.
    Includes profile information directly in the user model (no separate Profile table).
    """
    # UUID primary key — prevents sequential ID guessing attacks
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Additional profile fields beyond what AbstractUser provides
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    is_premium = models.BooleanField(
        default=False, help_text="Premium user access")
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_image = models.ImageField(
        upload_to='profiles/', blank=True, null=True)
    # Auto-managed timestamps
    created_at = models.DateTimeField(
        auto_now_add=True)  # Set once on creation
    updated_at = models.DateTimeField(
        auto_now=True)       # Updated on every save

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return self.username

    @property
    def full_name(self) -> str:
        """Return full name or username if not set"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
