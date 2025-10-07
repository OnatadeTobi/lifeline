from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import BloodRequest, DonorResponse


@admin.register(BloodRequest)
class BloodRequestAdmin(ModelAdmin):
    list_display = ['id', 'hospital', 'blood_type', 'status', 'created_at']
    list_filter = ['status', 'blood_type', 'created_at']
    search_fields = ['hospital__name', 'contact_phone']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DonorResponse)
class DonorResponseAdmin(ModelAdmin): 
    list_display = ['request', 'donor', 'accepted_at', 'fulfilled']
    list_filter = ['accepted_at', 'fulfilled']
    search_fields = ['donor__user__email', 'request__hospital__name']



# from django.contrib import admin
# from .models import BloodRequest, DonorResponse

# # Register your models here.
# @admin.register(BloodRequest)
# class BloodRequestAdmin(admin.ModelAdmin):
#     list_display = ['id', 'hospital', 'blood_type', 'status', 'created_at']
#     list_filter = ['status', 'blood_type', 'created_at']
#     search_fields = ['hospital__name', 'contact_phone']
#     readonly_fields = ['created_at', 'updated_at']

# @admin.register(DonorResponse)
# class DonorResponseAdmin(admin.ModelAdmin):
#     list_display = ['request', 'donor', 'accepted_at']
#     list_filter = ['accepted_at']
#     search_fields = ['donor__user__email', 'request__hospital__name']