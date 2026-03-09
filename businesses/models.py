from typing import Optional

from django.db import models
from django.conf import settings
from core.models import BaseModel, ContactInfoModel


# A business profile owned by a user — the entity that sends invoices
class Business(BaseModel, ContactInfoModel):
    # Links to CustomUser via AUTH_USER_MODEL; one user can own multiple
    # businesses
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='businesses')
    name = models.CharField(max_length=255)
    gstin = models.CharField(
        max_length=15,
        blank=True,
        help_text="For Indian Tax compliance")  # Goods & Services Tax ID
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    email = models.EmailField()
    # Hex color for invoice theming
    brand_color = models.CharField(max_length=7, default='#000000')

    def __str__(self):
        return self.name

    @property
    def logo_url_safe(self) -> Optional[str]:
        """Return logo URL if exists, None otherwise (avoids template errors)"""
        if self.logo:
            return self.logo.url
        return None
