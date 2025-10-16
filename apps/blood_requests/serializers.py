from rest_framework import serializers
from .models import BloodRequest, DonorResponse

import logging
logger = logging.getLogger('apps.blood_requests')


class BloodRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['blood_type', 'contact_phone', 'notes']
    
    def create(self, validated_data):
        user = self.context['request'].user
        
        # Check if user is a hospital
        if not hasattr(user, 'role') or user.role != 'HOSPITAL':
            logger.warning(
                f"Unauthorized blood request creation attempt - User: {user.email}, "
                f"Role: {getattr(user, 'role', 'unknown')}"
            )
            raise serializers.ValidationError(
                "Only hospital users can create blood requests."
            )
        
        # Get hospital profile safely
        hospital = getattr(user, 'hospital_profile', None)
        
        if not hospital:
            logger.error(
                f"Blood request creation failed - Hospital profile not found for user {user.email}"
            )
            raise serializers.ValidationError(
                "User does not have an associated hospital."
            )
        
        try:
            blood_request = BloodRequest.objects.create(
                hospital=hospital,
                **validated_data
            )

            logger.info(
                f"Blood request created - ID: {blood_request.id}, "
                f"Hospital: {hospital.name}, Blood Type: {blood_request.blood_type}, "
                f"Created by: {user.email}"
            )
            
            return blood_request
        
        except Exception as e:
            logger.exception(
                f"Unexpected error creating blood request - Hospital: {hospital.name}, "
                f"User: {user.email}, Error: {str(e)}"
            )
            raise serializers.ValidationError(
                "An error occurred while creating the blood request."
            )
        

class BloodRequestSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    hospital_location = serializers.CharField(source='hospital.primary_location.name', read_only=True)
    matched_donors_count = serializers.IntegerField(source='responses.count', read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'hospital_name', 'hospital_location', 'blood_type',
            'contact_phone', 'notes', 'status',
            'matched_donors_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']

class DonorResponseSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.user.email', read_only=True)
    donor_phone = serializers.CharField(source='donor.phone', read_only=True)
    donor_blood_type = serializers.CharField(source='donor.blood_type', read_only=True)
    
    class Meta:
        model = DonorResponse
        fields = ['id', 'donor_name', 'donor_phone', 'donor_blood_type', 'accepted_at']