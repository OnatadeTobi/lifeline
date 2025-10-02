from rest_framework import serializers
from .models import State, LocalGovernment

class LocalGovernmentSerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    
    class Meta:
        model = LocalGovernment
        fields = ['id', 'name', 'state', 'state_name']

class StateSerializer(serializers.ModelSerializer):
    local_governments = LocalGovernmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = State
        fields = ['id', 'name', 'code', 'local_governments']