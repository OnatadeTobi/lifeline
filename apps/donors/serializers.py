from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Donor
from apps.locations.models import LocalGovernment
from apps.locations.serializers import LocalGovernmentSerializer
from apps.accounts.models import EmailVerification
import random

from apps.core.utils import mask_email

import logging
logger = logging.getLogger('apps.donors')


User = get_user_model()

class DonorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(max_length=100, write_only=True)
    last_name = serializers.CharField(max_length=100, write_only=True)
    password = serializers.CharField(max_length=68, write_only=True, min_length=8)
    password2 = serializers.CharField(max_length=68, write_only=True, min_length=8)
    service_locations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalGovernment.objects.all()
    )

    # read-only fields from User
    user_first_name = serializers.SerializerMethodField(read_only=True)
    user_last_name = serializers.SerializerMethodField(read_only=True)
    user_email = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Donor
        fields = ['email', 'first_name', 'last_name', 'password',
                  'password2', 'phone', 'blood_type', 'service_locations',
                  'user_first_name', 'user_last_name', 'user_email']

    def get_user_first_name(self, obj):
        return obj.user.first_name

    def get_user_last_name(self, obj):
        return obj.user.last_name

    def get_user_email(self, obj):
        return obj.user.email

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        email = attrs.get('email')

        if password != password2:
            logger.warning(f"Password mismatch during donor registration attempt for email: {mask_email(email)}")
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def validate_email(self, value):
        """Ensure email is unique."""
        if User.objects.filter(email__iexact=value).exists():
            logger.warning(f"[DONOR] Registration blocked - duplicate email detected: {mask_email(value)}")
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        first_name=validated_data.pop('first_name')
        last_name=validated_data.pop('last_name')
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        service_locations = validated_data.pop('service_locations')
        
        # Create user (handle possible race on unique email)
        try:
            user = User.objects.create_user(
                email=email,
                username=email,
                first_name=first_name,
                last_name=last_name,
                password=password,
                role='DONOR'
            )
            logger.info("User account created successfully for donor: %s", mask_email(email))
        except IntegrityError:
            # Turn DB constraint into serializer validation error
            logger.error("IntegrityError during donor registration for email: %s", mask_email(email), exc_info=True)
            raise serializers.ValidationError({'email': 'Email already registered'})
        
        # Create donor profile
        donor = Donor.objects.create(user=user, **validated_data)
        donor.service_locations.set(service_locations)
        logger.info("Donor profile created for user: %s (ID: %s)", mask_email(email), donor.id)

        
        # Create email verification code (6-digit) and send email
        try:
            code = f"{random.randint(0, 999999):06d}"
            expires_at = timezone.now() + timedelta(hours=24)
            EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)

            subject = "Your Lifeline verification code"
            message = f"Your verification code is: {code}\nThis code expires in 24 hours."
            print(code)
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
            logger.info("Verification email sent successfully to donor: %s", mask_email(email))
        except Exception as e:
            # Don't fail registration if email sending/verification model has issue
            logger.error("[DONOR] Failed to send verification email to %s: %s", mask_email(email), str(e), exc_info=True)

        return donor

class DonorSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    service_locations = LocalGovernmentSerializer(many=True, read_only=True)
    is_eligible = serializers.BooleanField(source='is_eligible_to_donate', read_only=True)
    
    class Meta:
        model = Donor
        fields = [
            'id', 'email', 'phone', 'blood_type', 'is_available',
            'service_locations', 'last_donation_date', 'available_from',
            'is_eligible', 'created_at'
        ]
        read_only_fields = ['id', 'last_donation_date', 'available_from', 'created_at']