from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Donor
from .serializers import DonorRegistrationSerializer, DonorSerializer


class DonorRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = DonorRegistrationSerializer

class DonorProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DonorSerializer
    
    def get_object(self):
        return self.request.user.donor

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_availability(request):
    """Toggle donor availability status"""
    donor = request.user.donor
    donor.is_available = not donor.is_available
    donor.save()
    
    return Response({
        'is_available': donor.is_available,
        'message': f"Availability set to {'available' if donor.is_available else 'unavailable'}"
    })