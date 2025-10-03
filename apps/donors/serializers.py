from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Donor
from apps.locations.models import LocalGovernment
from apps.locations.serializers import LocalGovernmentSerializer
#from rest_framework.exceptions import ValidationError

User = get_user_model()

class DonorRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(max_length=68, write_only=True, min_length=8)
    password2 = serializers.CharField(max_length=68, write_only=True, min_length=8)
    service_locations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalGovernment.objects.all()
    )
    
    class Meta:
        model = Donor
        fields = ['email', 'password', 'password2', 'phone', 'blood_type', 'service_locations']

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')
        if password != password2:
            raise serializers.ValidationError("passwords do not match")
         
        return attrs
    
    def create(self, validated_data):
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        service_locations = validated_data.pop('service_locations')
        
        # Create user
        user = User.objects.create_user(
            email=email,
            username=email,
            password=password,
            role=User.UserRoles.DONOR
        )
        
        # Create donor profile
        donor = Donor.objects.create(user=user, **validated_data)
        donor.service_locations.set(service_locations)
        
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