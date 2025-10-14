"""
Base admin classes for the Lifeline application.
Provides common functionality for both superuser and hospital-restricted admin interfaces.
"""
import csv
from django.http import HttpResponse
from django.contrib import admin
from django.contrib.admin import ModelAdmin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from django.utils.html import format_html
from django.db.models import Q
from typing import Any, Optional


class BaseAdminMixin:
    """Common mixin for admin functionality"""
    
    def get_readonly_fields(self, request, obj=None):
        """Add system fields to readonly fields"""
        readonly = list(getattr(self, 'readonly_fields', []))
        if hasattr(self.model, '_meta'):
            # Add common system fields if they exist
            system_fields = ['created_at', 'updated_at', 'id']
            for field in system_fields:
                if hasattr(self.model, field) and field not in readonly:
                    readonly.append(field)
        return readonly
    
    def get_queryset(self, request):
        """Base queryset with proper ordering"""
        qs = super().get_queryset(request)
        # Default ordering by most recent
        if hasattr(self.model._meta, 'ordering') and self.model._meta.ordering:
            return qs
        # Fallback to created_at or id
        if hasattr(self.model, 'created_at'):
            return qs.order_by('-created_at')
        elif hasattr(self.model, 'id'):
            return qs.order_by('-id')
        return qs


class ExportCSVMixin:
    """Mixin to add CSV export functionality"""
    
    def export_as_csv(self, request, queryset):
        """Export selected records as CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.model._meta.verbose_name_plural}.csv"'
        
        writer = csv.writer(response)
        
        # Get field names
        field_names = [field.name for field in self.model._meta.fields]
        writer.writerow(field_names)
        
        # Write data
        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                if value is None:
                    row.append('')
                elif hasattr(value, '__str__'):
                    row.append(str(value))
                else:
                    row.append(value)
            writer.writerow(row)
        
        return response
    
    export_as_csv.short_description = "Export selected %(verbose_name_plural)s as CSV"


class SuperuserAdmin(BaseAdminMixin, ExportCSVMixin, UnfoldModelAdmin):
    """Full-featured admin for superusers"""
    
    def has_module_permission(self, request):
        """Superusers can see all modules"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Superusers can add records"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Superusers can change all records"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Superusers can delete all records"""
        return request.user.is_superuser
    
    def get_actions(self, request):
        """Get available actions for superuser"""
        actions = super().get_actions(request)
        if hasattr(self, 'export_as_csv'):
            actions['export_as_csv'] = (
                self.export_as_csv,
                'export_as_csv',
                'Export selected %(verbose_name_plural)s as CSV'
            )
        return actions


def get_user_hospital(request):
    """Helper function to get the hospital for a user"""
    if request.user.is_superuser:
        return None
    
    # Check both possible relationships
    
    if hasattr(request.user, 'hospital_profile'):
        return request.user.hospital_profile
    
    return None


class HospitalRestrictedAdmin(BaseAdminMixin, ExportCSVMixin, UnfoldModelAdmin):
    """Admin with hospital-based restrictions"""
    
    def get_queryset(self, request):
        """Filter data based on user's hospital"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        user_hospital = get_user_hospital(request)
        if not user_hospital:
            return qs.none()
        
        # Filter based on hospital relationship
        if hasattr(self.model, 'hospital_profile'):
            return qs.filter(hospita_profilel=user_hospital)
        elif hasattr(self.model, 'user') and user_hospital:
            # For models like Donor that have user relationship
            return qs.filter(user__hospital=user_hospital)
        elif self.model.__name__ == 'User':
            # For User model, show hospital users
            return qs.filter(hospital_profile=user_hospital)
        
        return qs.none()
    
    def has_module_permission(self, request):
        """Check if user can see this model at all"""
        if request.user.is_superuser:
            return True
        
        # Hospital users can see most models
        if hasattr(request.user, 'hospital_profile') and request.user.hospital_profile:
            return True
        
        return False
    
    def has_add_permission(self, request):
        """Control if user can add new records"""
        if request.user.is_superuser:
            return True
        
        # Hospital users can add most records
        return hasattr(request.user, 'hospital_profile') and request.user.hospital_profile
    
    def has_change_permission(self, request, obj=None):
        """Control if user can edit specific records"""
        if request.user.is_superuser:
            return True
        
        if not hasattr(request.user, 'hospital_profile') or not request.user.hospital_profile:
            return False
        
        if obj is None:
            return True
        
        # Check if this specific object belongs to user's hospital
        if hasattr(obj, 'hospital_profile'):
            return obj.hospital_profile == request.user.hospital_profile
        elif hasattr(obj, 'user') and hasattr(obj.user, 'hospital_profile'):
            return obj.user.hospital_profile == request.user.hospital_profile
        
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Control if user can delete specific records"""
        if request.user.is_superuser:
            return True
        
        if not hasattr(request.user, 'hospital_profile') or not request.user.hospital_profile:
            return False
        
        if obj is None:
            return True
        
        # Check if this specific object belongs to user's hospital
        if hasattr(obj, 'hospital_profile'):
            return obj.hospital_profile == request.user.hospital_profile
        elif hasattr(obj, 'user') and hasattr(obj.user, 'hospital_profile'):
            return obj.user.hospital == request.user.hospital_profile
        
        return False
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit dropdown choices to user's hospital"""
        if not request.user.is_superuser and hasattr(request.user, 'hospital_profile'):
            if db_field.name == "hospital_profile":
                kwargs["queryset"] = kwargs["queryset"].filter(id=request.user.hospital.id)
            elif db_field.name == "user" and hasattr(request.user, 'hospital_profile'):
                # Limit user choices to hospital users
                kwargs["queryset"] = kwargs["queryset"].filter(hospital_profile=request.user.hospital_profile)
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Limit many-to-many choices"""
        if not request.user.is_superuser and hasattr(request.user, 'hospital_profile'):
            if db_field.name in ["service_locations"] and hasattr(request.user, 'hospital_profile'):
                # Limit to hospital's service locations
                hospital_locations = request.user.hospital.service_locations.all()
                kwargs["queryset"] = kwargs["queryset"].filter(
                    id__in=hospital_locations.values_list('id', flat=True)
                )
        
        return super().formfield_for_manytomany(db_field, request, **kwargs)


def get_admin_class(is_superuser=True):
    """Factory function to get appropriate admin class"""
    return SuperuserAdmin if is_superuser else HospitalRestrictedAdmin


# Common field configurations
COMMON_FIELDSETS = {
    'timestamps': ('Timestamps', {
        'fields': ('created_at', 'updated_at'),
        'classes': ('collapse',)
    })
}

COMMON_LIST_FILTERS = {
    'default': ['created_at', 'updated_at'],
    'status': ['created_at', 'updated_at', 'status'],
    'verification': ['created_at', 'updated_at', 'is_verified'],
}

COMMON_SEARCH_FIELDS = {
    'user_based': ['user__email', 'user__first_name', 'user__last_name'],
    'hospital_based': ['hospital__name', 'hospital__user__email'],
    'location_based': ['primary_location__name', 'service_locations__name'],
}
