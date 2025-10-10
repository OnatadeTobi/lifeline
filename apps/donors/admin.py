from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from apps.core.admin_base import SuperuserAdmin, HospitalRestrictedAdmin
from .models import Donor


class DonorAdminMixin:
    """Mixin with common Donor admin functionality"""
    
    def get_list_display(self, request):
        """Dynamic list display"""
        base_display = [
            'email', 'phone', 'blood_type', 'is_available', 
            'is_eligible_display', 'last_donation_date', 'available_from'
        ]
        
        if request.user.is_superuser:
            base_display.extend(['service_locations_count', 'responses_count', 'created_at'])
        
        return base_display
    
    def get_list_filter(self, request):
        """Dynamic list filters"""
        base_filters = ['blood_type', 'is_available', 'created_at']
        
        if request.user.is_superuser:
            base_filters.extend(['service_locations', 'last_donation_date'])
        
        return base_filters
    
    def get_search_fields(self, request):
        """Search fields"""
        return [
            'user__email', 'user__first_name', 'user__last_name', 
            'phone', 'blood_type'
        ]
    
    def get_fieldsets(self, request, obj=None):
        """Organized fieldsets"""
        if request.user.is_superuser:
            return [
                ('Personal Information', {
                    'fields': ('user', 'phone')
                }),
                ('Donation Details', {
                    'fields': ('blood_type', 'is_available', 'last_donation_date', 'available_from')
                }),
                ('Service Areas', {
                    'fields': ('service_locations',)
                }),
                ('Statistics', {
                    'fields': ('responses_count',),
                    'classes': ('collapse',),
                    'description': 'Read-only statistics'
                }),
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            ]
        else:
            return [
                ('Personal Information', {
                    'fields': ('phone',)
                }),
                ('Donation Details', {
                    'fields': ('blood_type', 'is_available', 'last_donation_date', 'available_from')
                }),
                ('Service Areas', {
                    'fields': ('service_locations',)
                }),
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        """Readonly fields"""
        readonly = ['created_at', 'updated_at', 'responses_count']
        
        if not request.user.is_superuser:
            # Hospital users can't change user
            readonly.append('user')
        
        return readonly
    
    def email(self, obj):
        """Display donor email"""
        return obj.user.email
    email.short_description = 'Email'
    email.admin_order_field = 'user__email'
    
    def is_eligible_display(self, obj):
        """Display eligibility with color coding"""
        if obj.is_eligible_to_donate:
            return format_html('<span style="color: green;">✓ Eligible</span>')
        else:
            return format_html('<span style="color: red;">✗ Not Eligible</span>')
    is_eligible_display.short_description = 'Eligible'
    
    def service_locations_count(self, obj):
        """Display count of service locations"""
        return obj.service_locations.count()
    service_locations_count.short_description = 'Service Areas'
    
    def responses_count(self, obj):
        """Display count of donor responses"""
        return obj.responses.count()
    responses_count.short_description = 'Responses'


class SuperuserDonorAdmin(DonorAdminMixin, SuperuserAdmin):
    """Full-featured Donor admin for superusers"""
    
    filter_horizontal = ['service_locations']
    autocomplete_fields = ['user']
    date_hierarchy = 'created_at'
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'phone', 'blood_type']
    
    def get_queryset(self, request):
        """Annotate queryset with counts"""
        return super().get_queryset(request).annotate(
            responses_count=Count('responses')
        )
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        actions['activate_donors'] = (
            self.activate_donors,
            'activate_donors',
            'Activate selected donors'
        )
        actions['deactivate_donors'] = (
            self.deactivate_donors,
            'deactivate_donors',
            'Deactivate selected donors'
        )
        actions['mark_as_available'] = (
            self.mark_as_available,
            'mark_as_available',
            'Mark selected donors as available'
        )
        actions['update_donation_date'] = (
            self.update_donation_date,
            'update_donation_date',
            'Update last donation date to today'
        )
        
        return actions
    
    @admin.action(description="Activate selected donors")
    def activate_donors(self, request, queryset):
        """Activate selected donors"""
        count = queryset.update(user__is_active=True)
        self.message_user(request, f"{count} donors activated successfully.")
    
    @admin.action(description="Deactivate selected donors")
    def deactivate_donors(self, request, queryset):
        """Deactivate selected donors"""
        count = queryset.update(user__is_active=False)
        self.message_user(request, f"{count} donors deactivated successfully.")
    
    @admin.action(description="Mark selected donors as available")
    def mark_as_available(self, request, queryset):
        """Mark donors as available"""
        count = queryset.update(is_available=True)
        self.message_user(request, f"{count} donors marked as available.")
    
    @admin.action(description="Update last donation date to today")
    def update_donation_date(self, request, queryset):
        """Update last donation date"""
        count = queryset.update(last_donation_date=timezone.now())
        self.message_user(request, f"{count} donors' last donation date updated.")


class HospitalDonorAdmin(DonorAdminMixin, HospitalRestrictedAdmin):
    """Restricted Donor admin for hospital users"""
    
    filter_horizontal = ['service_locations']
    
    def get_queryset(self, request):
        """Hospital users see only their donors"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        # Hospital users can see only their donors
        if hasattr(request.user, 'hospital') and request.user.hospital:
            return qs.filter(hospital=request.user.hospital)

    # def get_queryset(self, request):

    #     qs = super().get_queryset(request)
    #     if request.user.is_superuser:
    #         return qs
        
    #     if hasattr(request.user, 'hospital') and request.user.hospital:
    #         # Only donors serving hospital’s areas
    #         return qs.filter(hospital=request.user.hospital)
    #     return qs.none()

    
    def has_add_permission(self, request):
        """Hospital users can add donors"""
        return hasattr(request.user, 'hospital') and request.user.hospital
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can edit donors"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Hospital users can edit any donor
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Hospital users cannot delete donors"""
        return False
    
    def get_actions(self, request):
        """Limited actions for hospital users"""
        actions = super().get_actions(request)
        
        actions['mark_as_available'] = (
            self.mark_as_available,
            'mark_as_available',
            'Mark selected donors as available'
        )
        
        return actions
    
    @admin.action(description="Mark selected donors as available")
    def mark_as_available(self, request, queryset):
        """Mark donors as available"""
        count = queryset.update(is_available=True)
        self.message_user(request, f"{count} donors marked as available.")


class DynamicDonorAdmin(SuperuserDonorAdmin):
    """Dynamic Donor admin that adapts based on user type"""
    
    def has_module_permission(self, request):
        """Control module access based on user type"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def get_queryset(self, request):
        """Hospital users see all donors"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            # Hospital users can see all donors
            return super().get_queryset(request).filter(user__is_active=True)
        
        return super().get_queryset(request).none()
    
    def has_add_permission(self, request):
        """Hospital users can add donors"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can edit donors"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete donors"""
        return request.user.is_superuser


# Register with dynamic admin class
if admin.site.is_registered(Donor):
    admin.site.unregister(Donor)
admin.site.register(Donor, DynamicDonorAdmin)