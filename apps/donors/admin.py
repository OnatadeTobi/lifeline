from django.contrib import admin
from .models import Donor

# Register your models here.
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['email', 'blood_type', 'is_available', 'is_eligible', 'last_donation_date']
    list_filter = ['blood_type', 'is_available']
    search_fields = ['user__email', 'phone']
    filter_horizontal = ['service_locations']
    
    def email(self, obj):
        return obj.user.email
    
    def is_eligible(self, obj):
        return obj.is_eligible_to_donate
    is_eligible.boolean = True