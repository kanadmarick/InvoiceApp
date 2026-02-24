from django.db import models
from django.contrib.auth.models import User
from core.models import BaseModel


class Profile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True)
    is_premium = models.BooleanField(default=False)  # For your future monetization

    def __str__(self):
        return self.user.username
