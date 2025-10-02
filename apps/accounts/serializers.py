from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role', 'is_verified']
        read_only_fields = ['id', 'is_verified']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add user role to token response"""
    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        data['is_verified'] = self.user.is_verified
        return data