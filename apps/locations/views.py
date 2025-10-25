from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import State, LocalGovernment
from .serializers import StateSerializer, LocalGovernmentSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Public endpoints - prevent scraping
@method_decorator(ratelimit(key='ip', rate='1000/h'), name='dispatch') # 1000 requests per hour
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