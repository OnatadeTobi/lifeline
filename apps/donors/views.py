from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .serializers import DonorRegistrationSerializer, DonorSerializer
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

from apps.core.utils import mask_email

import logging
logger = logging.getLogger('apps.donors')

# Registration rate limits
@method_decorator(ratelimit(key='ip', rate='3/h', method=['POST']), name='dispatch') # 3 registrations per hour
class DonorRegistrationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = DonorRegistrationSerializer


# Profile updates - reasonable limits
@method_decorator(ratelimit(key='user', rate='20/h', method=['PUT', 'PATCH']), name='dispatch') # 20 updates per hour
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

    status = 'available' if donor.is_available else 'unavailable'
    logger.info(
        "Donor availability toggled: %s set to %s",
        mask_email(request.user.email),
        status
    )
    
    return Response({
        'is_available': donor.is_available,
        'message': f"Availability set to {'available' if donor.is_available else 'unavailable'}"
    })