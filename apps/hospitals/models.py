from django.db import models
from django.conf import settings
from apps.locations.models import LocalGovernment

# Create your models here.
class Hospital(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hospital_profile')
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    primary_location = models.ForeignKey(
        LocalGovernment,
        on_delete=models.PROTECT,
        related_name='primary_hospitals'
    )
    service_locations = models.ManyToManyField(
        LocalGovernment,
        related_name='service_hospitals',
        help_text='Areas this hospital accepts donors from'
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name