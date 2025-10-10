"""
Custom admin site that provides dynamic admin classes based on user type.
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model

User = get_user_model()


class DynamicAdminSite(AdminSite):
    """Custom admin site that provides different admin interfaces based on user type"""
    
    def get_model_admin_class(self, model):
        """Get the appropriate admin class for a model based on context"""
        # This will be called by the admin site to determine which admin class to use
        # We'll override the registration methods to handle this dynamically
        """Not used — all role-specific behavior is handled in admin classes."""
        pass
    
    def register(self, model_or_iterable, admin_class=None, **options):
        """Override registration to handle dynamic admin classes"""
        if admin_class is None:
            # Use the default admin class for now
            # The actual dynamic behavior will be handled in the admin classes themselves
            admin_class = admin.ModelAdmin
        
        super().register(model_or_iterable, admin_class, **options)


class DynamicModelAdmin:
    """Mixin that provides dynamic behavior based on user type"""
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self._user_type = None
    
    def get_user_type(self, request):
        """Determine user type for the current request"""
        if not hasattr(self, '_user_type') or self._user_type is None:
            if request.user.is_superuser:
                self._user_type = 'superuser'
            elif hasattr(request.user, 'hospital') and request.user.hospital:
                self._user_type = 'hospital'
            else:
                self._user_type = 'none'
        
        return self._user_type
    
    def get_list_display(self, request):
        """Override to provide dynamic list display"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_list_display_{user_type}'):
            return getattr(self, f'get_list_display_{user_type}')(request)
        elif hasattr(self, 'get_list_display_base'):
            return self.get_list_display_base(request)
        else:
            return super().get_list_display(request)
    
    def get_list_filter(self, request):
        """Override to provide dynamic list filters"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_list_filter_{user_type}'):
            return getattr(self, f'get_list_filter_{user_type}')(request)
        elif hasattr(self, 'get_list_filter_base'):
            return self.get_list_filter_base(request)
        else:
            return super().get_list_filter(request)
    
    def get_search_fields(self, request):
        """Override to provide dynamic search fields"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_search_fields_{user_type}'):
            return getattr(self, f'get_search_fields_{user_type}')(request)
        elif hasattr(self, 'get_search_fields_base'):
            return self.get_search_fields_base(request)
        else:
            return super().get_search_fields(request)
    
    def get_fieldsets(self, request, obj=None):
        """Override to provide dynamic fieldsets"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_fieldsets_{user_type}'):
            return getattr(self, f'get_fieldsets_{user_type}')(request, obj)
        elif hasattr(self, 'get_fieldsets_base'):
            return self.get_fieldsets_base(request, obj)
        else:
            return super().get_fieldsets(request, obj)
    
    def get_readonly_fields(self, request, obj=None):
        """Override to provide dynamic readonly fields"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_readonly_fields_{user_type}'):
            return getattr(self, f'get_readonly_fields_{user_type}')(request, obj)
        elif hasattr(self, 'get_readonly_fields_base'):
            return self.get_readonly_fields_base(request, obj)
        else:
            return super().get_readonly_fields(request, obj)
    
    def get_queryset(self, request):
        """Override to provide dynamic queryset filtering"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_queryset_{user_type}'):
            return getattr(self, f'get_queryset_{user_type}')(request)
        elif hasattr(self, 'get_queryset_base'):
            return self.get_queryset_base(request)
        else:
            return super().get_queryset(request)
    
    def get_actions(self, request):
        """Override to provide dynamic actions"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'get_actions_{user_type}'):
            return getattr(self, f'get_actions_{user_type}')(request)
        elif hasattr(self, 'get_actions_base'):
            return self.get_actions_base(request)
        else:
            return super().get_actions(request)
    
    def has_module_permission(self, request):
        """Override to provide dynamic module permissions"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'has_module_permission_{user_type}'):
            return getattr(self, f'has_module_permission_{user_type}')(request)
        elif hasattr(self, 'has_module_permission_base'):
            return self.has_module_permission_base(request)
        else:
            return super().has_module_permission(request)
    
    def has_add_permission(self, request):
        """Override to provide dynamic add permissions"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'has_add_permission_{user_type}'):
            return getattr(self, f'has_add_permission_{user_type}')(request)
        elif hasattr(self, 'has_add_permission_base'):
            return self.has_add_permission_base(request)
        else:
            return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj=None):
        """Override to provide dynamic change permissions"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'has_change_permission_{user_type}'):
            return getattr(self, f'has_change_permission_{user_type}')(request, obj)
        elif hasattr(self, 'has_change_permission_base'):
            return self.has_change_permission_base(request, obj)
        else:
            return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """Override to provide dynamic delete permissions"""
        user_type = self.get_user_type(request)
        
        if hasattr(self, f'has_delete_permission_{user_type}'):
            return getattr(self, f'has_delete_permission_{user_type}')(request, obj)
        elif hasattr(self, 'has_delete_permission_base'):
            return self.has_delete_permission_base(request, obj)
        else:
            return super().has_delete_permission(request, obj)


def create_dynamic_admin_class(base_admin_class):
    """Factory function to create dynamic admin classes"""
    
    class DynamicAdmin(DynamicModelAdmin, base_admin_class):
        """Dynamic admin class that adapts based on user type"""
        pass
    
    return DynamicAdmin

