from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class EmailVerification(models.Model):
    """Stores one-time verification codes for emails."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='email_verifications')
    code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    def is_valid(self):
        return (not self.used) and (timezone.now() <= self.expires_at)

    def __str__(self):
        return f"Verification for {self.user.email} (used={self.used})"

# Create your models here.
class User(AbstractUser):
    class UserRoles(models.TextChoices):
        DONOR = 'DONOR', 'Donor'
        HOSPITAL = 'HOSPITAL', 'Hospital'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRoles.choices)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        permissions = [
            ("can_manage_hospital", "Can manage hospital data"),
            ("can_view_all_hospitals", "Can view all hospitals"),
            ("can_manage_donors", "Can manage donor data"),
            ("can_view_all_requests", "Can view all blood requests"),
        ]  