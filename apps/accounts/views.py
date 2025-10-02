from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import User

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Email verification endpoint (simplified - just marks as verified)"""
    email = request.data.get('email')
    user = User.objects.filter(email=email).first()
    
    if user:
        user.is_verified = True
        user.save()
        return Response({'message': 'Email verified successfully'})
    
    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)