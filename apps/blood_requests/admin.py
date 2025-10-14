from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from apps.core.admin_base import SuperuserAdmin, HospitalRestrictedAdmin
from .models import BloodRequest, DonorResponse


from django.core.mail import send_mail
from django.conf import settings

from .services import DonorMatchingService


class DonorResponseInline(admin.TabularInline):
    """Inline admin for donor responses"""
    model = DonorResponse
    extra = 0
    readonly_fields = ['accepted_at']
    fields = ['donor', 'accepted_at', 'fulfilled']
    autocomplete_fields = ['donor']


class BloodRequestAdminMixin:
    """Mixin with common BloodRequest admin functionality"""
    
    def get_list_display(self, request):
        """Dynamic list display"""
        base_display = [
            'id', 'hospital', 'blood_type', 'status_display', 
            'contact_phone', 'responses_count', 'created_at'
        ]
        
        if request.user.is_superuser:
            base_display.extend(['notes_preview'])
        
        return base_display
    
    def get_list_filter(self, request):
        """Dynamic list filters"""
        base_filters = ['status', 'blood_type', 'created_at']
        
        if request.user.is_superuser:
            base_filters.extend(['hospital', 'hospital__primary_location__state'])
        
        return base_filters
    
    def get_search_fields(self, request):
        """Search fields"""
        return [
            'hospital__name', 'hospital__user__email', 
            'contact_phone', 'notes', 'blood_type'
        ]
    
    def get_fieldsets(self, request, obj=None):
        """Organized fieldsets"""
        if request.user.is_superuser:
            return [
                ('Request Information', {
                    'fields': ('hospital', 'blood_type', 'contact_phone', 'notes')
                }),
                ('Status', {
                    'fields': ('status',)
                }),
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            ]
        else:
            return [
                ('Request Information', {
                    'fields': ('blood_type', 'contact_phone', 'notes')
                }),
                ('Status', {
                    'fields': ('status',)
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
            # Hospital users can't change hospital
            readonly.append('hospital')
        
        return readonly
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'OPEN': 'orange',
            'MATCHED': 'blue',
            'FULFILLED': 'green',
            'CANCELLED': 'red'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {};">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def responses_count(self, obj):
        """Display count of donor responses"""
        return obj.responses.count()
    responses_count.short_description = 'Responses'
    
    def notes_preview(self, obj):
        """Display notes preview"""
        if obj.notes:
            return obj.notes[:50] + '...' if len(obj.notes) > 50 else obj.notes
        return '-'
    notes_preview.short_description = 'Notes Preview'


class SuperuserBloodRequestAdmin(BloodRequestAdminMixin, SuperuserAdmin):
    """Full-featured BloodRequest admin for superusers"""
    
    inlines = [DonorResponseInline]
    autocomplete_fields = ['hospital']
    date_hierarchy = 'created_at'
    search_fields = ['hospital__name', 'hospital__user__email', 'contact_phone', 'notes', 'blood_type']
    
    def get_queryset(self, request):
        """Annotate queryset with counts"""
        return super().get_queryset(request).annotate(
            responses_count=Count('responses')
        )
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        actions['mark_as_fulfilled'] = (
            self.mark_as_fulfilled,
            'mark_as_fulfilled',
            'Mark selected requests as fulfilled'
        )
        actions['mark_as_cancelled'] = (
            self.mark_as_cancelled,
            'mark_as_cancelled',
            'Mark selected requests as cancelled'
        )
        actions['mark_as_open'] = (
            self.mark_as_open,
            'mark_as_open',
            'Mark selected requests as open'
        )
        
        return actions
    
    @admin.action(description="Mark selected requests as fulfilled")
    def mark_as_fulfilled(self, request, queryset):
        """Mark requests as fulfilled"""
        count = queryset.update(status='FULFILLED')
        self.message_user(request, f"{count} requests marked as fulfilled.")
    
    @admin.action(description="Mark selected requests as cancelled")
    def mark_as_cancelled(self, request, queryset):
        """Mark requests as cancelled"""
        count = queryset.update(status='CANCELLED')
        self.message_user(request, f"{count} requests marked as cancelled.")
    
    @admin.action(description="Mark selected requests as open")
    def mark_as_open(self, request, queryset):
        """Mark requests as open"""
        count = queryset.update(status='OPEN')
        self.message_user(request, f"{count} requests marked as open.")


class HospitalBloodRequestAdmin(BloodRequestAdminMixin, HospitalRestrictedAdmin):
    """Restricted BloodRequest admin for hospital users"""
    
    inlines = [DonorResponseInline]
    
    def get_queryset(self, request):
        """Hospital users only see their own requests"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'hospital_profile') and request.user.hospital_profile:
            return qs.filter(hospital=request.user.hospital_profile)
        
        return qs.none()
    
    def get_actions(self, request):
        """Available actions for hospital users"""
        actions = super().get_actions(request)
        
        actions['mark_as_fulfilled'] = (
            self.mark_as_fulfilled,
            'mark_as_fulfilled',
            'Mark selected requests as fulfilled'
        )
        actions['mark_as_cancelled'] = (
            self.mark_as_cancelled,
            'mark_as_cancelled',
            'Mark selected requests as cancelled'
        )
        
        return actions
    
    @admin.action(description="Mark selected requests as fulfilled")
    def mark_as_fulfilled(self, request, queryset):
        """Mark requests as fulfilled"""
        count = queryset.update(status='FULFILLED')
        self.message_user(request, f"{count} requests marked as fulfilled.")
    
    @admin.action(description="Mark selected requests as cancelled")
    def mark_as_cancelled(self, request, queryset):
        """Mark requests as cancelled"""
        count = queryset.update(status='CANCELLED')
        self.message_user(request, f"{count} requests marked as cancelled.")


class DonorResponseAdminMixin:
    """Mixin with common DonorResponse admin functionality"""
    
    def get_list_display(self, request):
        """Dynamic list display"""
        if request.user.is_superuser:
            return [
                'request', 'donor_email', 'donor_blood_type', 
                'accepted_at', 'fulfilled_display', 'request_status'
            ]
        else:
            return [
                'request', 'donor_email', 'donor_blood_type', 
                'accepted_at', 'fulfilled_display'
            ]
    
    def get_list_filter(self, request):
        """Dynamic list filters"""
        base_filters = ['fulfilled', 'accepted_at']
        
        if request.user.is_superuser:
            base_filters.extend(['donor__blood_type', 'request__hospital'])
        
        return base_filters
    
    def get_search_fields(self, request):
        """Search fields"""
        return [
            'donor__user__email', 'donor__user__first_name', 'donor__user__last_name',
            'request__hospital__name', 'request__contact_phone'
        ]
    
    def get_fieldsets(self, request, obj=None):
        """Organized fieldsets"""
        if request.user.is_superuser:
            return [
                ('Response Information', {
                    'fields': ('request', 'donor')
                }),
                ('Status', {
                    'fields': ('fulfilled',)
                }),
                ('Timestamps', {
                    'fields': ('accepted_at',),
                    'classes': ('collapse',)
                })
            ]
        else:
            return [
                ('Response Information', {
                    'fields': ('request', 'donor')
                }),
                ('Status', {
                    'fields': ('fulfilled',)
                }),
                ('Timestamps', {
                    'fields': ('accepted_at',),
                    'classes': ('collapse',)
                })
            ]
    
    def get_readonly_fields(self, request, obj=None):
        """Readonly fields"""
        readonly = ['accepted_at']
        
        if not request.user.is_superuser:
            # Hospital users can't change request or donor
            readonly.extend(['request', 'donor'])
        
        return readonly
    
    def donor_email(self, obj):
        """Display donor email"""
        return obj.donor.user.email
    donor_email.short_description = 'Donor Email'
    donor_email.admin_order_field = 'donor__user__email'
    
    def donor_blood_type(self, obj):
        """Display donor blood type"""
        return obj.donor.blood_type
    donor_blood_type.short_description = 'Blood Type'
    donor_blood_type.admin_order_field = 'donor__blood_type'
    
    def fulfilled_display(self, obj):
        """Display fulfilled status with color coding"""
        if obj.fulfilled:
            return format_html('<span style="color: green;">✓ Fulfilled</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Pending</span>')
    fulfilled_display.short_description = 'Fulfilled'
    fulfilled_display.admin_order_field = 'fulfilled'
    
    def request_status(self, obj):
        """Display request status"""
        return obj.request.get_status_display()
    request_status.short_description = 'Request Status'
    request_status.admin_order_field = 'request__status'


class SuperuserDonorResponseAdmin(DonorResponseAdminMixin, SuperuserAdmin):
    """Full-featured DonorResponse admin for superusers"""
    
    autocomplete_fields = ['request', 'donor']
    date_hierarchy = 'accepted_at'
    search_fields = ['donor__user__email', 'donor__user__first_name', 'donor__user__last_name', 'request__hospital__name', 'request__contact_phone']
    
    def get_actions(self, request):
        """Available actions for superusers"""
        actions = super().get_actions(request)
        
        actions['mark_as_fulfilled'] = (
            self.mark_as_fulfilled,
            'mark_as_fulfilled',
            'Mark selected responses as fulfilled'
        )
        actions['mark_as_pending'] = (
            self.mark_as_pending,
            'mark_as_pending',
            'Mark selected responses as pending'
        )
        
        return actions
    
    @admin.action(description="Mark selected responses as fulfilled")
    def mark_as_fulfilled(self, request, queryset):
        """Mark responses as fulfilled"""
        count = queryset.update(fulfilled=True)
        self.message_user(request, f"{count} responses marked as fulfilled.")
    
    @admin.action(description="Mark selected responses as pending")
    def mark_as_pending(self, request, queryset):
        """Mark responses as pending"""
        count = queryset.update(fulfilled=False)
        self.message_user(request, f"{count} responses marked as pending.")


class HospitalDonorResponseAdmin(DonorResponseAdminMixin, HospitalRestrictedAdmin):
    """Restricted DonorResponse admin for hospital users"""
    
    def get_queryset(self, request):
        """Hospital users only see responses to their requests"""
        qs = super().get_queryset(request)
        
        if request.user.is_superuser:
            return qs
        
        if hasattr(request.user, 'hospital_profile') and request.user.hospital_profile:
            return qs.filter(request__hospital=request.user.hospital_profile)
        
        return qs.none()
    
    def has_add_permission(self, request):
        """Hospital users cannot add responses"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Hospital users cannot delete responses"""
        return False
    
    def get_actions(self, request):
        """Available actions for hospital users"""
        actions = super().get_actions(request)
        
        actions['mark_as_fulfilled'] = (
            self.mark_as_fulfilled,
            'mark_as_fulfilled',
            'Mark selected responses as fulfilled'
        )
        
        return actions
    
    @admin.action(description="Mark selected responses as fulfilled")
    def mark_as_fulfilled(self, request, queryset):
        """Mark responses as fulfilled"""
        count = queryset.update(fulfilled=True)
        self.message_user(request, f"{count} responses marked as fulfilled.")


class DynamicBloodRequestAdmin(SuperuserBloodRequestAdmin):
    """Dynamic BloodRequest admin that adapts based on user type"""
    
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
        """Hospital users only see their own requests"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            return super().get_queryset(request).filter(hospital=user_hospital)
        
        return super().get_queryset(request).none()
    
    def has_add_permission(self, request):
        """Hospital users can add requests"""
        if request.user.is_superuser:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return user_hospital is not None
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can edit their own requests"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return obj.hospital == user_hospital
    
    
    
    def save_model(self, request, obj, form, change):
        if not obj.hospital_id:
            hospital = getattr(request.user, 'hospital_profile', None)
            if not hospital:
                raise ValueError("Hospital must be set before saving this blood request.")
            obj.hospital = hospital
        super().save_model(request, obj, form, change)

        # --- Send notifications to matching donors ---
        matching_donors = DonorMatchingService.find_compatible_donors(obj)
        for donor in matching_donors:
            self.send_donor_notification(donor, obj)


    def send_donor_notification(self, donor, request_obj):
        """Send email notification to donor"""
        subject = f"Urgent: {request_obj.blood_type} Blood Needed"
        message = f"""
        Hello {donor.user.first_name},

        A blood request has been posted that matches your profile:

        Blood Type: {request_obj.blood_type}
        Hospital: {request_obj.hospital.name}
        Address: {request_obj.hospital.address}
        Location: {request_obj.hospital.primary_location.name}
        Contact: {request_obj.contact_phone}

        If you can donate, please accept this request:
        Accept Link: {settings.FRONTEND_URL}/requests/{request_obj.id}/accept/

        Thank you for being a lifesaver!
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [donor.user.email],
            fail_silently=True
        )

    
    def has_delete_permission(self, request, obj=None):
        """Hospital users can delete their own requests"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return obj.hospital == user_hospital


class DynamicDonorResponseAdmin(SuperuserDonorResponseAdmin):
    """Dynamic DonorResponse admin that adapts based on user type"""
    
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
        """Hospital users only see responses to their requests"""
        if request.user.is_superuser:
            return super().get_queryset(request)
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        if user_hospital:
            return super().get_queryset(request).filter(request__hospital=user_hospital)
        
        return super().get_queryset(request).none()
    
    def has_add_permission(self, request):
        """Hospital users cannot add responses"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Hospital users cannot delete responses"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Hospital users can edit responses to their requests"""
        if request.user.is_superuser:
            return True
        
        if not obj:
            return True
        
        # Check if user is a hospital staff member
        user_hospital = None
        
        if hasattr(request.user, 'hospital_profile'):
            user_hospital = request.user.hospital_profile
        
        return obj.request.hospital == user_hospital


# Register with dynamic admin classes
if admin.site.is_registered(BloodRequest):
    admin.site.unregister(BloodRequest)
admin.site.register(BloodRequest, DynamicBloodRequestAdmin)

if admin.site.is_registered(DonorResponse):
    admin.site.unregister(DonorResponse)
admin.site.register(DonorResponse, DynamicDonorResponseAdmin)