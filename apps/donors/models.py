from django.db import models
from django.conf import settings
from apps.locations.models import LocalGovernment

# Create your models here.

class BloodType(models.TextChoices):
    A_POSITIVE = 'A+', 'A+'
    A_NEGATIVE = 'A-', 'A-'
    B_POSITIVE = 'B+', 'B+'
    B_NEGATIVE = 'B-', 'B-'
    AB_POSITIVE = 'AB+', 'AB+'
    AB_NEGATIVE = 'AB-', 'AB-'
    O_POSITIVE = 'O+', 'O+'
    O_NEGATIVE = 'O-', 'O-'

class Donor(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    blood_type = models.CharField(max_length=3, choices=BloodType.choices)
    is_available = models.BooleanField(default=True)
    last_donation_date = models.DateTimeField(null=True, blank=True)
    available_from = models.DateField(null=True, blank=True)    # Auto-calculated
    service_locations = models.ManyToManyField(
        LocalGovernment,
        related_name='donors',
        help_text='Areas where donor can travel to donate..'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} ({self.blood_type})"
    
    @property
    def is_eligible_to_donate(self):
        """Check if donor can donate (56 days cooldown)"""
        if not self.available_from:
            return True
        from django.utils import timezone
        return timezone.now().date() >= self.available_from