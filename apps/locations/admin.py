from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from apps.core.admin_base import SuperuserAdmin
from .models import State, LocalGovernment


class DynamicStateAdmin(SuperuserAdmin):
    """Admin for State model with dynamic permissions"""
    
    def has_module_permission(self, request):
        """Hospital users can view locations"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_view_permission(self, request, obj=None):
        """Hospital users can view states"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_add_permission(self, request):
        """Only superusers can add states"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only superusers can edit states"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete states"""
        return request.user.is_superuser


@admin.register(State)
class StateAdmin(DynamicStateAdmin):
    
    list_display = ["name", "code", "local_governments_count", "hospitals_count", "donors_count"]
    search_fields = ["name", "code"]
    ordering = ["name"]
    readonly_fields = ["local_governments_count", "hospitals_count", "donors_count"]
    
    fieldsets = [
        ('State Information', {
            'fields': ('name', 'code')
        }),
        ('Statistics', {
            'fields': ('local_governments_count', 'hospitals_count', 'donors_count'),
            'classes': ('collapse',),
            'description': 'Read-only statistics'
        })
    ]
    
    def get_queryset(self, request):
        """Annotate queryset with counts"""
        return super().get_queryset(request).annotate(
            local_governments_count=Count('local_governments'),
            hospitals_count=Count('local_governments__primary_hospitals'),
            donors_count=Count('local_governments__donors', distinct=True)
        )
    
    def local_governments_count(self, obj):
        """Display count of local governments"""
        return obj.local_governments.count()
    local_governments_count.short_description = 'Local Governments'
    
    def hospitals_count(self, obj):
        """Display count of hospitals"""
        return obj.local_governments.aggregate(
            count=Count('primary_hospitals')
        )['count']
    hospitals_count.short_description = 'Hospitals'
    
    def donors_count(self, obj):
        """Display count of donors"""
        return obj.local_governments.aggregate(
            count=Count('donors', distinct=True)
        )['count']
    donors_count.short_description = 'Donors'
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        # Add export functionality
        actions['export_states'] = (
            self.export_states,
            'export_states',
            'Export selected states as CSV'
        )
        
        return actions
    
    def export_states(self, request, queryset):
        """Export states as CSV"""
        return self.export_as_csv(request, queryset)


class DynamicLocalGovernmentAdmin(SuperuserAdmin):
    """Admin for LocalGovernment model with dynamic permissions"""
    
    def has_module_permission(self, request):
        """Hospital users can view locations"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_view_permission(self, request, obj=None):
        """Hospital users can view local governments"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        if hasattr(request.user, 'hospital') and request.user.hospital:
            user_hospital = request.user.hospital
        elif hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_add_permission(self, request):
        """Only superusers can add local governments"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Only superusers can edit local governments"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete local governments"""
        return request.user.is_superuser


@admin.register(LocalGovernment)
class LocalGovernmentAdmin(DynamicLocalGovernmentAdmin):
    
    list_display = ["name", "state", "hospitals_count", "donors_count", "service_hospitals_count"]
    list_filter = ["state", "state__name"]
    search_fields = ["name", "state__name", "state__code"]
    ordering = ["state", "name"]
    readonly_fields = ["hospitals_count", "donors_count", "service_hospitals_count"]
    autocomplete_fields = ["state"]
    
    fieldsets = [
        ('Location Information', {
            'fields': ('state', 'name')
        }),
        ('Statistics', {
            'fields': ('hospitals_count', 'donors_count', 'service_hospitals_count'),
            'classes': ('collapse',),
            'description': 'Read-only statistics'
        })
    ]
    
    def get_queryset(self, request):
        """Annotate queryset with counts"""
        return super().get_queryset(request).annotate(
            hospitals_count=Count('primary_hospitals'),
            donors_count=Count('donors'),
            service_hospitals_count=Count('service_hospitals')
        )
    
    def hospitals_count(self, obj):
        """Display count of primary hospitals"""
        return obj.primary_hospitals.count()
    hospitals_count.short_description = 'Primary Hospitals'
    
    def donors_count(self, obj):
        """Display count of donors"""
        return obj.donors.count()
    donors_count.short_description = 'Donors'
    
    def service_hospitals_count(self, obj):
        """Display count of hospitals that serve this area"""
        return obj.service_hospitals.count()
    service_hospitals_count.short_description = 'Service Hospitals'
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        # Add export functionality
        actions['export_local_governments'] = (
            self.export_local_governments,
            'export_local_governments',
            'Export selected local governments as CSV'
        )
        
        return actions
    
    def export_local_governments(self, request, queryset):
        """Export local governments as CSV"""
        return self.export_as_csv(request, queryset)