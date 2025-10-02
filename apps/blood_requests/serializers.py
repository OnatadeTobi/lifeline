from rest_framework import serializers
from .models import BloodRequest, DonorResponse


class BloodRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodRequest
        fields = ['blood_type', 'urgency', 'contact_phone', 'notes']
    
    def create(self, validated_data):
        # Hospital is set from request.user
        hospital = self.context['request'].user.hospital
        blood_request = BloodRequest.objects.create(
            hospital=hospital,
            **validated_data
        )
        return blood_request

class BloodRequestSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    hospital_location = serializers.CharField(source='hospital.primary_location.name', read_only=True)
    matched_donors_count = serializers.IntegerField(source='responses.count', read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'hospital_name', 'hospital_location', 'blood_type',
            'urgency', 'contact_phone', 'notes', 'status',
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