from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from .models import Hospital
from apps.locations.models import LocalGovernment
from apps.locations.serializers import LocalGovernmentSerializer

# Email Verification
from apps.accounts.models import EmailVerification
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

from apps.core.utils import mask_email
from smtplib import SMTPException
from django.db import transaction

import logging
logger = logging.getLogger('apps.hospitals')


User = get_user_model()


class HospitalRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=68, write_only=True, min_length=8)
    password2 = serializers.CharField(max_length=68, write_only=True, min_length=8)
    service_locations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalGovernment.objects.all()
    )

    # read-only fields from User
    user_email = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Hospital
        fields = [
            'email', 'password', 'password2', 'name', 'phone', 'address',
            'primary_location', 'service_locations', 'user_email'
        ]


    def get_user_email(self, obj):
        return obj.user.email

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        email = attrs.get('email')

        if password != password2:
            logger.warning(f"Password mismatch during hospital registration attempt for email: {mask_email(email)}")
            raise serializers.ValidationError("passwords do not match")
         
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            logger.warning(f"[HOSPITAL] Registration blocked - duplicate email detected: {mask_email(value)}")
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        validated_data.pop('password2', None)
        service_locations = validated_data.pop('service_locations')

        # Create user (handle possible race on unique email)
        try:
            with transaction.atomic():
                try:
                    user = User.objects.create_user(
                        email=email,
                        username=email,
                        password=password,
                        role='HOSPITAL'
                    )
                    logger.info("User account created successfully for hospital: %s", mask_email(email))

                except IntegrityError:
                    logger.error("IntegrityError during hospital registration for email: %s", mask_email(email), exc_info=True)
                    raise serializers.ValidationError({'email': 'Email already registered'})

                # Create Hospital profile
                hospital = Hospital.objects.create(user=user, **validated_data)
                hospital.service_locations.set(service_locations)
                logger.info("Hospital profile created for user: %s (ID: %s)", mask_email(email), hospital.id)

                # Create email verification code and send
                code = f"{random.randint(0, 999999):06d}"
                expires_at = timezone.now() + timedelta(hours=24)
                EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)
                logger.debug("Verification code created for Hospital: %s", mask_email(email))

                # Send verification email - this is the critical step
                subject = "Your Lifeline verification code"
                message = f"Your verification code is: {code}\nThis code expires in 24 hours."
            
                try:
                    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
                    logger.info("Verification email sent successfully to hospital: %s", mask_email(email))

                except SMTPException as e:  
                    logger.error("SMTP error sending email to %s", mask_email(email), exc_info=True)
                    # Raise to trigger transaction rollback
                    raise serializers.ValidationError({
                        'email': 'Failed to send verification email. Please try again later or contact support.'
                    })

                except Exception as e:
                    logger.error("[HOSPITAL] Failed to send verification email to %s: %s", mask_email(email), str(e), exc_info=True)
                    # Raise to trigger transaction rollback
                    raise serializers.ValidationError({
                        'email': 'Failed to send verification email. Please try again later.'
                    })
                
        except serializers.ValidationError:
            # Re-raise validation errors (they already have proper messages)
            raise
            
        except Exception as e:
            # Catch any other unexpected errors
            logger.error("[HOSPITAL] Unexpected error during registration for %s", mask_email(email), exc_info=True)
            raise serializers.ValidationError({
                'non_field_errors': 'Registration failed. Please try again later.'
            })

        return hospital
    

class HospitalSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    service_locations = LocalGovernmentSerializer(many=True, read_only=True)
    primary_location_detail = LocalGovernmentSerializer(source='primary_location', read_only=True)
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'email', 'name', 'phone', 'address',
            'primary_location', 'primary_location_detail',
            'service_locations', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']