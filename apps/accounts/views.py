from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .models import User
from .models import EmailVerification
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import random


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


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """Resend a verification code to the provided email."""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        code = f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timedelta(hours=24)
        EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)

        subject = "Your Lifeline verification code"
        message = f"Your verification code is: {code}\nThis code expires in 24 hours."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    except Exception:
        pass

    return Response({'message': 'Verification code resent if account exists'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request a password reset code to be emailed to the user."""
    email = request.data.get('email')
    if not email:
        return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        # don't reveal user existence
        return Response({'message': 'If an account exists, a reset code was sent'})

    try:
        code = f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timedelta(hours=1)
        EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)

        subject = "Your Lifeline password reset code"
        message = f"Your password reset code is: {code}\nThis code expires in 1 hour."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
    except Exception:
        pass

    return Response({'message': 'If an account exists, a reset code was sent'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_verify(request):
    """Verify a password reset code. Body: {email, code} -> returns success if valid"""
    email = request.data.get('email')
    code = request.data.get('code')
    if not email or not code:
        return Response({'error': 'email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({'error': 'Invalid code or email'}, status=status.HTTP_400_BAD_REQUEST)

    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()
    if not verification or not verification.is_valid():
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'Code valid'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset and set new password. Body: {email, code, new_password, new_password2}"""
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')

    if not all([email, code, new_password, new_password2]):
        return Response({'error': 'email, code and new_password/new_password2 are required'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != new_password2:
        return Response({'error': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()
    if not verification or not verification.is_valid():
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    # Set password
    user.set_password(new_password)
    user.save()

    verification.used = True
    verification.save()

    return Response({'message': 'Password updated successfully'})