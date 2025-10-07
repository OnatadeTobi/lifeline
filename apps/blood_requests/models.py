from django.db import models

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

class BloodRequest(models.Model):
    class RequestStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        MATCHED = 'MATCHED', 'Matched'
        FULFILLED = 'FULFILLED', 'Fulfilled'
        CANCELLED = 'CANCELLED', 'Cancelled'

    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, related_name='requests')
    blood_type = models.CharField(max_length=3, choices=BloodType.choices)
    contact_phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.blood_type} - {self.hospital.name} ({self.status})"
    

class DonorResponse(models.Model):
    """Tracks which donors accepted which requests"""
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='responses')
    donor = models.ForeignKey("donors.Donor", on_delete=models.CASCADE, related_name='responses')
    accepted_at = models.DateTimeField(auto_now_add=True)
    fulfilled = models.BooleanField(default=False)


    class Meta:
        unique_together = ['request', 'donor']

