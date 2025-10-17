from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Hospital
from .serializers import HospitalRegistrationSerializer, HospitalSerializer

class HospitalRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = HospitalRegistrationSerializer

class HospitalProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = HospitalSerializer
    
    def get_object(self):
        return self.request.user.hospital_profile