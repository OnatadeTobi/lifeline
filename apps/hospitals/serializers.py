from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Hospital
from apps.locations.models import LocalGovernment
from apps.locations.serializers import LocalGovernmentSerializer


User = get_user_model()


class HospitalRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(max_length=68, write_only=True, min_length=8)
    service_locations = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=LocalGovernment.objects.all()
    )
    
    class Meta:
        model = Hospital
        fields = [
            'email', 'password', 'password2', 'name', 'phone', 'address',
            'primary_location', 'service_locations'
        ]

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
        
        user = User.objects.create_user(
            email=email,
            username=email,
            password=password,
            role=User.UserRoles.HOSPITAL
        )
        
        hospital = Hospital.objects.create(user=user, **validated_data)
        hospital.service_locations.set(service_locations)
        
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