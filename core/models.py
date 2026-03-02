# Core abstract models — inherited by all other app models for consistency
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model for all tables in the project.
    Provides:
    - UUID primary key (secure, non-sequential IDs)
    - Automatic created_at / updated_at timestamps
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,   # Generates a random UUID on creation
        editable=False
    )
    # Set once when record is created
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True)       # Updated on every .save()

    class Meta:
        abstract = True  # This tells Django: "Don't create a database table for this model"
        ordering = ['-created_at']  # Newest records first by default


class ContactInfoModel(models.Model):
    """
    Abstract mixin for address/contact fields.
    Inherited by both Business and Client models to avoid field duplication.
    """
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    class Meta:
        abstract = True  # No table created — fields are added to inheriting models
