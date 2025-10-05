from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Hospital


@admin.register(Hospital)
class HospitalAdmin(ModelAdmin):
    list_display = ['name', 'email', 'primary_location', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'primary_location']
    search_fields = ['name', 'user__email']
    filter_horizontal = ['service_locations']
    
    actions = ['verify_hospitals', 'unverify_hospitals']
    
    def email(self, obj):
        return obj.user.email
    
    @admin.action(description="Verify selected hospitals")
    def verify_hospitals(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, f"{queryset.count()} hospitals verified")
    
    @admin.action(description="Unverify selected hospitals")
    def unverify_hospitals(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, f"{queryset.count()} hospitals unverified")