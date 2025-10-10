from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from apps.core.admin_base import SuperuserAdmin, HospitalRestrictedAdmin
from .models import User, EmailVerification


class UserAdminMixin:
    """Mixin with common User admin functionality"""
    
    def get_list_display(self, request):
        """Dynamic list display based on user type"""
        base_display = ['email', 'role', 'is_verified', 'is_active', 'date_joined']
        
        if request.user.is_superuser:
            base_display.extend(['is_staff', 'is_superuser'])
        
        return base_display
    
    def get_list_filter(self, request):
        """Dynamic list filters"""
        base_filters = ['role', 'is_verified', 'is_active', 'date_joined']
        
        if request.user.is_superuser:
            base_filters.extend(['is_staff', 'is_superuser'])
        
        return base_filters
    
    def get_search_fields(self, request):
        """Search fields"""
        return ['email', 'username', 'first_name', 'last_name']
    
    def get_fieldsets(self, request, obj=None):
        """Organized fieldsets"""
        if request.user.is_superuser:
            return [
                ('Personal Information', {
                    'fields': ('username', 'email', 'first_name', 'last_name')
                }),
                ('Account Status', {
                    'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser')
                }),
                ('Permissions', {
                    'fields': ('groups', 'user_permissions'),
                    'classes': ('collapse',)
                }),
                ('Important Dates', {
                    'fields': ('last_login', 'date_joined'),
                    'classes': ('collapse',)
                })
            ]
        else:
            return [
                ('Personal Information', {
                    'fields': ('username', 'email', 'first_name', 'last_name')
                }),
                ('Account Status', {
                    'fields': ('role', 'is_verified', 'is_active')
                }),
                ('Important Dates', {
                    'fields': ('last_login', 'date_joined'),
                    'classes': ('collapse',)
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        """Readonly fields"""
        readonly = ['date_joined', 'last_login']
        
        if obj and not request.user.is_superuser:
            # Hospital users can't change certain fields
            readonly.extend(['is_staff', 'is_superuser', 'groups', 'user_permissions'])
        
        return readonly
    
    def get_queryset(self, request):
        """Filter users based on permissions"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'hospital') and request.user.hospital:
            # Hospital users only see users related to their hospital
            return qs.filter(
                Q(hospital=request.user.hospital) | 
                Q(role='DONOR')  # Hospital users can see all donors
            )
        
        return qs.none()


class SuperuserUserAdmin(UserAdminMixin, SuperuserAdmin):
    """Full-featured User admin for superusers"""
    
    search_fields = ['email', 'username', 'first_name', 'last_name']
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        # Add custom actions
        actions['activate_users'] = (
            self.activate_users,
            'activate_users',
            'Activate selected users'
        )
        actions['deactivate_users'] = (
            self.deactivate_users,
            'deactivate_users',
            'Deactivate selected users'
        )
        actions['verify_users'] = (
            self.verify_users,
            'verify_users',
            'Verify selected users'
        )
        
        return actions
    
    @admin.action(description="Activate selected users")
    def activate_users(self, request, queryset):
        """Activate selected users"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} users activated successfully.")
    
    @admin.action(description="Deactivate selected users")
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} users deactivated successfully.")
    
    @admin.action(description="Verify selected users")
    def verify_users(self, request, queryset):
        """Verify selected users"""
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} users verified successfully.")


class HospitalUserAdmin(UserAdminMixin, HospitalRestrictedAdmin):
    """Restricted User admin for hospital users"""
    
    def get_queryset(self, request):
        """Hospital users see limited users"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'hospital') and request.user.hospital:
            # Hospital users see their hospital users and all donors
            return qs.filter(
                Q(hospital=request.user.hospital) | 
                Q(role='DONOR')
            )
        
        return qs.none()
    
    def has_add_permission(self, request):
        """Hospital users can add donors"""
        return hasattr(request.user, 'hospital') and request.user.hospital
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can edit their hospital users and donors"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        if hasattr(request.user, 'hospital') and request.user.hospital:
            # Can edit hospital users or any donor
            return (
                (hasattr(obj, 'hospital') and obj.hospital == request.user.hospital) or
                obj.role == 'DONOR'
            )
        
        return False


# Register with dynamic admin class
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Dynamic User admin that adapts based on user type"""
    
    def __new__(cls, *args, **kwargs):
        # This will be overridden by the actual registration
        return super().__new__(cls)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


# Register EmailVerification
@admin.register(EmailVerification)
class EmailVerificationAdmin(SuperuserAdmin):
    """Admin for email verification codes"""
    
    list_display = ['user', 'code', 'created_at', 'expires_at', 'used', 'is_valid_display']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['user__email', 'code']
    readonly_fields = ['created_at', 'expires_at']
    date_hierarchy = 'created_at'
    
    def is_valid_display(self, obj):
        """Display if verification is valid"""
        if obj.is_valid():
            return format_html('<span style="color: green;">✓ Valid</span>')
        else:
            return format_html('<span style="color: red;">✗ Invalid</span>')
    
    is_valid_display.short_description = 'Valid'
    
    def get_queryset(self, request):
        """Superusers see all, others see none"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        return self.model.objects.none()


class DynamicUserAdmin(SuperuserUserAdmin):
    """Dynamic User admin that adapts based on user type"""
    
    def has_module_permission(self, request):
        """Control module access based on user type"""
        if request.user.is_superuser:
            return True
        # Hospital users and donors can see the Users module
        return request.user.is_authenticated
    
    def get_queryset(self, request):
        """Filter users based on permissions"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            # Hospital users see their hospital users and all donors
            return super().get_queryset(request).filter(
                Q(hospital=user_hospital) | 
                Q(role='DONOR')
            )
        
        # Donors see nothing (they shouldn't access admin)
        return super().get_queryset(request).none()
    
    def has_view_permission(self, request, obj=None):
        """Control view permissions"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            if obj is None:
                return True
            # Can view hospital users or any donor
            return (
                (hasattr(obj, 'hospital') and obj.hospital == user_hospital) or
                obj.role == 'DONOR'
            )
        
        return False
    
    def has_change_permission(self, request, obj=None):
        """Control change permissions"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            if obj is None:
                return True
            # Can edit hospital users or any donor
            return (
                (hasattr(obj, 'hospital') and obj.hospital == user_hospital) or
                obj.role == 'DONOR'
            )
        
        return False


# Register with dynamic admin class
if admin.site.is_registered(User):
    admin.site.unregister(User)
admin.site.register(User, DynamicUserAdmin)