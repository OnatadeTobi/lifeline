from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import User
from .models import EmailVerification
from django.utils import timezone

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Email verification using OTP code. Request body: {"email": "...", "code": "123456"}"""
    email = request.data.get('email')
    code = request.data.get('code')

    if not email or not code:
        return Response({'error': 'email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()
    if not verification or not verification.is_valid():
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    # mark verified
    user.is_verified = True
    user.save()

    verification.used = True
    verification.save()

    return Response({'message': 'Email verified successfully'})