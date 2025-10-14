from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from apps.core.admin_base import SuperuserAdmin, HospitalRestrictedAdmin
from .models import Hospital


class HospitalAdminMixin:
    """Mixin with common Hospital admin functionality"""
    
    def get_list_display(self, request):
        """Dynamic list display"""
        if request.user.is_superuser:
            return [
                'name', 'email', 'phone', 'primary_location', 
                'service_locations_count', 'is_verified', 'requests_count', 'created_at'
            ]
        else:
            return ['name', 'email', 'phone', 'primary_location', 'is_verified', 'created_at']
    
    def get_list_filter(self, request):
        """Dynamic list filters"""
        base_filters = ['is_verified', 'created_at', 'primary_location__state']
        
        if request.user.is_superuser:
            base_filters.extend(['primary_location'])
        
        return base_filters
    
    def get_search_fields(self, request):
        """Search fields"""
        return ['name', 'user__email', 'phone', 'address', 'primary_location__name']
    
    def get_fieldsets(self, request, obj=None):
        """Organized fieldsets"""
        if request.user.is_superuser:
            return [
                ('Hospital Information', {
                    'fields': ('user', 'name', 'phone', 'address')
                }),
                ('Location', {
                    'fields': ('primary_location', 'service_locations')
                }),
                ('Status', {
                    'fields': ('is_verified',)
                }),
                ('Statistics', {
                    'fields': ('requests_count',), #'donors_count'
                    'classes': ('collapse',),
                    'description': 'Read-only statistics'
                }),
                ('Timestamps', {
                    'fields': ('created_at',),
                    'classes': ('collapse',)
                })
            ]
        else:
            return [
                ('Hospital Information', {
                    'fields': ('name', 'phone', 'address')
                }),
                ('Location', {
                    'fields': ('primary_location', 'service_locations')
                }),
                ('Timestamps', {
                    'fields': ('created_at',),
                    'classes': ('collapse',)
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        """Readonly fields"""
        readonly = ['created_at', 'requests_count', 'donors_count']
        
        if not request.user.is_superuser:
            # Hospital users can't change user or verification status
            readonly.extend(['user', 'is_verified'])
        
        return readonly
    
    def email(self, obj):
        """Display hospital email"""
        return obj.user.email
    email.short_description = 'Email'
    email.admin_order_field = 'user__email'
    
    def service_locations_count(self, obj):
        """Display count of service locations"""
        return obj.service_locations.count()
    service_locations_count.short_description = 'Service Areas'
    
    def requests_count(self, obj):
        """Display count of blood requests"""
        return obj.requests.count()
    requests_count.short_description = 'Blood Requests'


class SuperuserHospitalAdmin(HospitalAdminMixin, SuperuserAdmin):
    """Full-featured Hospital admin for superusers"""
    
    filter_horizontal = ['service_locations']
    autocomplete_fields = ['user', 'primary_location']
    date_hierarchy = 'created_at'
    search_fields = ['name', 'user__email', 'phone', 'address', 'primary_location__name']
    
    def get_queryset(self, request):
        """Annotate queryset with counts"""
        return super().get_queryset(request).annotate(
            requests_count=Count('requests'),
            donors_count=Count('user__donor', distinct=True)
        )
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        actions['verify_hospitals'] = (
            self.verify_hospitals,
            'verify_hospitals',
            'Verify selected hospitals'
        )
        actions['unverify_hospitals'] = (
            self.unverify_hospitals,
            'unverify_hospitals',
            'Unverify selected hospitals'
        )
        
        return actions
    
    @admin.action(description="Verify selected hospitals")
    def verify_hospitals(self, request, queryset):
        """Verify selected hospitals"""
        count = queryset.update(is_verified=True)
        self.message_user(request, f"{count} hospitals verified successfully.")
    
    @admin.action(description="Unverify selected hospitals")
    def unverify_hospitals(self, request, queryset):
        """Unverify selected hospitals"""
        count = queryset.update(is_verified=False)
        self.message_user(request, f"{count} hospitals unverified successfully.")


class HospitalHospitalAdmin(HospitalAdminMixin, HospitalRestrictedAdmin):
    """Restricted Hospital admin for hospital users"""
    
    filter_horizontal = ['service_locations']
    autocomplete_fields = ['primary_location']
    
    def get_queryset(self, request):
        """Hospital users only see their own hospital"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'hospital_profile') and request.user.hospital_profile:
            return qs.filter(id=request.user.hospital.id)
        
        return qs.none()
    
    def has_add_permission(self, request):
        """Hospital users cannot add hospitals"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Hospital users cannot delete hospitals"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can only edit their own hospital"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        return obj == request.user.hospital_profile


class DynamicHospitalAdmin(SuperuserHospitalAdmin):
    """Dynamic Hospital admin that adapts based on user type"""
    
    def has_module_permission(self, request):
        """Control module access based on user type"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def get_queryset(self, request):
        """Hospital users only see their own hospital"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            return super().get_queryset(request).filter(id=user_hospital.id)
        
        return super().get_queryset(request).none()
    
    def has_add_permission(self, request):
        """Hospital users cannot add hospitals"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Hospital users cannot delete hospitals"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can only edit their own hospital"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return obj == user_hospital


# Register with dynamic admin class
if admin.site.is_registered(Hospital):
    admin.site.unregister(Hospital)
admin.site.register(Hospital, DynamicHospitalAdmin)