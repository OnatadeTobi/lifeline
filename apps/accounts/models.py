from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class EmailVerification(models.Model):
    """Stores one-time verification codes for emails."""
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='email_verifications', db_index=True)
    code = models.CharField(max_length=10, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    used = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            # Composite index for the most common query: finding valid codes for a user
            models.Index(fields=['user', 'used', 'expires_at'], name='email_ver_valid_idx'),
            # Index for cleanup queries (finding expired codes)
            models.Index(fields=['expires_at', 'used'], name='email_ver_cleanup_idx'),
        ]

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
    role = models.CharField(max_length=20, choices=UserRoles.choices, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        permissions = [
            ("can_manage_hospital", "Can manage hospital data"),
            ("can_view_all_hospitals", "Can view all hospitals"),
            ("can_manage_donors", "Can manage donor data"),
            ("can_view_all_requests", "Can view all blood requests"),
        ]
        indexes = [
            # Composite index for filtering verified users by role
            models.Index(fields=['role', 'is_verified'], name='user_role_verified_idx'),
            # Index for filtering active verified users (common in blood matching)
            models.Index(fields=['is_verified', 'is_active'], name='user_verified_active_idx'),
        ]

    @property
    def donor_profile(self):
        """Compatibility alias used in tests: return the related Donor instance if present."""
        try:
            return getattr(self, 'donor')
        except Exception:
            # Reverse OneToOne descriptor raises RelatedObjectDoesNotExist if absent
            return None

    @property
    def hospital_profile(self):
        """Compatibility alias: return the related hospital_profile instance if present."""
        try:
            return getattr(self, 'hospital_profile')
        except Exception:
            return None