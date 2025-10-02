from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import State, LocalGovernment
from .serializers import StateSerializer, LocalGovernmentSerializer

class StateListView(generics.ListAPIView):
    """Public endpoint - no auth required"""
    permission_classes = [AllowAny]
    queryset = State.objects.all()
    serializer_class = StateSerializer

class LocalGovernmentListView(generics.ListAPIView):
    """Get LGAs for a specific state"""
    permission_classes = [AllowAny]
    serializer_class = LocalGovernmentSerializer
    
    def get_queryset(self):
        state_id = self.kwargs.get('state_id')
        if state_id:
            return LocalGovernment.objects.filter(state_id=state_id)
        return LocalGovernment.objects.all()