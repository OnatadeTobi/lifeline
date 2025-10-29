from django.db import models
from django.conf import settings
from apps.locations.models import LocalGovernment

# Create your models here.
class Hospital(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=200, db_index=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    primary_location = models.ForeignKey(
        LocalGovernment,
        on_delete=models.PROTECT,
        related_name='primary_hospitals',
        db_index=True
    )
    service_locations = models.ManyToManyField(
        LocalGovernment,
        related_name='service_hospitals',
        help_text='Areas this hospital accepts donors from'
    )
    is_verified = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            # For public hospital directory: verified hospitals by location
            models.Index(fields=['is_verified', 'primary_location', 'name'], name='hospital_directory_idx'),
            # For finding verified hospitals (most common filter)
            models.Index(fields=['is_verified', '-created_at'], name='hospital_verified_idx'),
            # For location-based hospital search
            models.Index(fields=['primary_location', 'is_verified'], name='hospital_location_idx'),
            # For hospital search by name (partial matching with trigram in future)
            models.Index(fields=['name', 'is_verified'], name='hospital_name_idx'),
        ]

    def __str__(self):
        return self.name