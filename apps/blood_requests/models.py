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

    hospital = models.ForeignKey('hospitals.Hospital', on_delete=models.CASCADE, related_name='requests', db_index=True)
    blood_type = models.CharField(max_length=3, choices=BloodType.choices, db_index=True)
    contact_phone = models.CharField(max_length=20)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=RequestStatus.choices, default=RequestStatus.OPEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Critical for donor matching: finding open requests by blood type
            models.Index(fields=['status', 'blood_type', '-created_at'], name='blood_req_matching_idx'),
            # For hospital dashboard: their requests by status
            models.Index(fields=['hospital', 'status', '-created_at'], name='blood_req_hospital_idx'),
            # For finding recent open requests (public feed)
            models.Index(fields=['status', '-created_at'], name='blood_req_open_idx'),
            # For analytics: requests by blood type and status
            models.Index(fields=['blood_type', 'status'], name='blood_req_analytics_idx'),
        ]

    def __str__(self):
        return f"{self.blood_type} - {self.hospital.name} ({self.status})"
    

class DonorResponse(models.Model):
    """Tracks which donors accepted which requests"""
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='responses', db_index=True)
    donor = models.ForeignKey("donors.Donor", on_delete=models.CASCADE, related_name='responses', db_index=True)
    accepted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    fulfilled = models.BooleanField(default=False, db_index=True)


    class Meta:
        unique_together = ['request', 'donor']
        indexes = [
            # For finding pending responses (accepted but not fulfilled)
            models.Index(fields=['fulfilled', 'accepted_at'], name='donor_resp_pending_idx'),
            # For donor history: their responses sorted by date
            models.Index(fields=['donor', '-accepted_at'], name='donor_resp_history_idx'),
            # For request fulfillment tracking
            models.Index(fields=['request', 'fulfilled'], name='donor_resp_fulfill_idx'),
        ]

