from django.contrib import admin
from .models import BloodRequest, DonorResponse

# Register your models here.
admin.site.register(BloodRequest)
admin.site.register(DonorResponse)