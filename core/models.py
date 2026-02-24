# Create your models here.
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    The blueprint for all tables in the project.
    - Uses UUIDs (Secure, non-predictable IDs).
    - Tracks when records are created/updated.
    """
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This tells Django: "Don't create a table for this!"
        ordering = ['-created_at']


class ContactInfoModel(models.Model):
    """
    Shared address fields. 
    Inherited by both your Business and your Clients.
    """
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, default='India')

    class Meta:
        abstract = True
