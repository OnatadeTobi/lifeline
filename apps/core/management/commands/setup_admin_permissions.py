"""
Management command to set up admin permissions and groups for the Lifeline application.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import User
from apps.hospitals.models import Hospital
from apps.donors.models import Donor
from apps.blood_requests.models import BloodRequest, DonorResponse
from apps.locations.models import State, LocalGovernment


class Command(BaseCommand):
    help = 'Set up admin permissions and groups for the Lifeline application'

    def handle(self, *args, **options):
        self.stdout.write('Setting up admin permissions and groups...')
        
        # Create groups
        hospital_admin_group, created = Group.objects.get_or_create(name='Hospital Admin')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created Hospital Admin group')
            )
        else:
            self.stdout.write('Hospital Admin group already exists')
        
        # Define permissions for hospital admin group
        hospital_permissions = [
            # User permissions (limited)
            ('accounts', 'user', 'view_user'),
            
            # Hospital permissions (own hospital only)
            ('hospitals', 'hospital', 'view_hospital'),
            ('hospitals', 'hospital', 'change_hospital'),
            
            # Blood request permissions (own hospital only)
            ('blood_requests', 'bloodrequest', 'view_bloodrequest'),
            ('blood_requests', 'bloodrequest', 'add_bloodrequest'),
            ('blood_requests', 'bloodrequest', 'change_bloodrequest'),
            
            # Donor response permissions (own hospital only)
            ('blood_requests', 'donorresponse', 'view_donorresponse'),
            ('blood_requests', 'donorresponse', 'change_donorresponse'),
            
            # No location permissions - restricted to superadmin only
        ]
        
        # Add permissions to hospital admin group
        for app_label, model_name, permission_codename in hospital_permissions:
            try:
                content_type = ContentType.objects.get(
                    app_label=app_label,
                    model=model_name
                )
                permission = Permission.objects.get(
                    codename=permission_codename,
                    content_type=content_type
                )
                hospital_admin_group.permissions.add(permission)
                self.stdout.write(
                    f'Added {permission_codename} permission for {model_name}'
                )
            except (ContentType.DoesNotExist, Permission.DoesNotExist) as e:
                self.stdout.write(
                    self.style.WARNING(
                        f'Could not find permission {permission_codename} for {model_name}: {e}'
                    )
                )
        
        # Create superuser group with all permissions
        superuser_group, created = Group.objects.get_or_create(name='Super Admin')
        if created:
            self.stdout.write(
                self.style.SUCCESS('Created Super Admin group')
            )
        else:
            self.stdout.write('Super Admin group already exists')
        
        # Add all permissions to superuser group
        all_permissions = Permission.objects.all()
        superuser_group.permissions.set(all_permissions)
        self.stdout.write(
            f'Added {all_permissions.count()} permissions to Super Admin group'
        )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully set up admin permissions and groups!')
        )
        
        # Display summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('PERMISSION SETUP SUMMARY')
        self.stdout.write('='*50)
        
        self.stdout.write(f'\nHospital Admin Group:')
        self.stdout.write(f'  - Users: {hospital_admin_group.user_set.count()}')
        self.stdout.write(f'  - Permissions: {hospital_admin_group.permissions.count()}')
        
        self.stdout.write(f'\nSuper Admin Group:')
        self.stdout.write(f'  - Users: {superuser_group.user_set.count()}')
        self.stdout.write(f'  - Permissions: {superuser_group.permissions.count()}')
        
        self.stdout.write('\nTo assign users to groups:')
        self.stdout.write('  - Use Django admin interface')
        self.stdout.write('  - Or create users programmatically and assign groups')
        
        self.stdout.write('\nExample usage:')
        self.stdout.write('  # Create a hospital admin user')
        self.stdout.write('  user = User.objects.create_user(email="admin@hospital.com", ...)')
        self.stdout.write('  user.groups.add(hospital_admin_group)')
        
        self.stdout.write('\n' + '='*50)

