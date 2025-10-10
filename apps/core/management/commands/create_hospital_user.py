"""
Management command to create hospital users and assign them properly.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from apps.accounts.models import User
from apps.hospitals.models import Hospital


class Command(BaseCommand):
    help = 'Create a hospital user and assign them to a hospital'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for the hospital user',
            required=True
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Username for the hospital user',
            required=True
        )
        parser.add_argument(
            '--hospital-id',
            type=int,
            help='ID of the hospital to assign this user to',
            required=True
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user (optional, will prompt if not provided)',
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name of the user',
            default=''
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name of the user',
            default=''
        )

    def handle(self, *args, **options):
        email = options['email']
        username = options['username']
        hospital_id = options['hospital_id']
        password = options['password']
        first_name = options['first_name']
        last_name = options['last_name']

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            raise CommandError(f'User with email {email} already exists')

        if User.objects.filter(username=username).exists():
            raise CommandError(f'User with username {username} already exists')

        # Check if hospital exists
        try:
            hospital = Hospital.objects.get(id=hospital_id)
        except Hospital.DoesNotExist:
            raise CommandError(f'Hospital with ID {hospital_id} does not exist')

        # Get or prompt for password
        if not password:
            import getpass
            password = getpass.getpass('Enter password: ')
            if not password:
                raise CommandError('Password is required')

        # Create the user
        user = User.objects.create_user(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='HOSPITAL',
            is_verified=True,
            is_staff=True,  # This is required for admin access
            hospital=hospital
        )

        # Assign to hospital admin group
        try:
            hospital_group = Group.objects.get(name='Hospital Admin')
            user.groups.add(hospital_group)
            self.stdout.write(
                self.style.SUCCESS(f'Added user to Hospital Admin group')
            )
        except Group.DoesNotExist:
            self.stdout.write(
                self.style.WARNING('Hospital Admin group not found. Run setup_admin_permissions first.')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created hospital user:\n'
                f'  Email: {user.email}\n'
                f'  Username: {user.username}\n'
                f'  Hospital: {hospital.name}\n'
                f'  Role: {user.role}\n'
                f'  Staff: {user.is_staff}\n'
                f'  Verified: {user.is_verified}\n'
                f'  Active: {user.is_active}'
            )
        )

        self.stdout.write('\nThe user can now login to the admin panel at /admin/')

