from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import HospitalRegistrationSerializer, HospitalSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

# Registration rate limits
@method_decorator(ratelimit(key='ip', rate='3/h', method=['POST']), name='dispatch') # 3 registrations per hour
class HospitalRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = HospitalRegistrationSerializer

# Profile updates - reasonable limits
@method_decorator(ratelimit(key='user', rate='20/h', method=['PUT', 'PATCH']), name='dispatch') # 20 updates per hour
class HospitalProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HospitalSerializer
    
    def get_object(self):
        return self.request.user.hospital_profile