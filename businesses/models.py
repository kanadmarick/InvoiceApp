from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel, ContactInfoModel


class Business(BaseModel, ContactInfoModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255)
    gstin = models.CharField(max_length=15, blank=True, help_text="For Indian Tax compliance")
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    email = models.EmailField()
    brand_color = models.CharField(max_length=7, default='#000000')

    def __str__(self):
        return self.name
    
    @property
    def logo_url_safe(self):
        """Return logo URL if exists, None otherwise"""
        if self.logo:
            return self.logo.url
        return None
