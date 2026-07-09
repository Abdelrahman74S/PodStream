from django.db import models
from django.contrib.auth.models import AbstractUser

from Accounts.storages import MediaStorage

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        LISTENER = 'listener', 'Listener'
        PODCASTER = 'podcaster', 'Podcaster'
        
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.LISTENER)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True, storage=MediaStorage())
    bio = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.role:
            self.role = self.Role.LISTENER
        if self.role == self.Role.ADMIN:
            self.is_staff = True
            self.is_superuser = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email} - ({self.get_role_display()})"

