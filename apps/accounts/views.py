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

import logging
logger = logging.getLogger('apps.accounts')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """Email verification using OTP code. Request body: {"email": "...", "code": "123456"}"""
    email = request.data.get('email')
    code = request.data.get('code')

    masked_email = f"{email[:3]}****@..." if email else None

    if not email or not code:
        logger.warning(f"Email verification attempt missing fields.")
        return Response({'error': 'email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        logger.warning(f"Email verification failed - User not found {masked_email}")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()

    if not verification or not verification.is_valid():
        logger.warning(f"Invalid or expired email verification attempt for user ID {user.id}")
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    # mark verified
    user.is_verified = True
    user.save()

    verification.used = True
    verification.save()

    logger.info(f"Email verified successfully for user: {masked_email}")

    return Response({'message': 'Email verified successfully'})


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification(request):
    """Resend a verification code to the provided email."""
    email = request.data.get('email')

    masked_email = f"{email[:3]}****@..." if email else None

    if not email:
        logger.warning("Resend verification attempt with no email provided.")
        return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        logger.warning(f"Resend verification attempted for non-existent email: {masked_email}")
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        code = f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timedelta(hours=24)
        print(code)

        EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)
        logger.info(f"New verification code generated for user ID {user.id}")

        subject = "Your Lifeline verification code"
        message = f"Your verification code is: {code}\nThis code expires in 24 hours."

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
        logger.debug(f"Verification email sent to: {masked_email}")

    except Exception as e:
        logger.error(f"Error resending verification for user ID {user.id if user else 'unknown'}: {e}")

    return Response({'message': 'Verification code resent if account exists'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request(request):
    """Request a password reset code to be emailed to the user."""
    email = request.data.get('email')

    masked_email = f"{email[:3]}****@..." if email else None

    if not email:
        logger.warning("Password reset requested with no email provided.")
        return Response({'error': 'email is required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        # don't reveal user existence
        logger.info(f"Password reset requested for non-existent email: {masked_email}")
        return Response({'message': 'If an account exists, a reset code was sent'})

    try:
        code = f"{random.randint(0, 999999):06d}"
        expires_at = timezone.now() + timedelta(hours=1)
        print(code)
        EmailVerification.objects.create(user=user, code=code, expires_at=expires_at)

        logger.info(f"Password reset code generated for user ID {user.id}")
        logger.debug(f"Code created for email {masked_email} (expires at {expires_at})")

        subject = "Your Lifeline password reset code"
        message = f"Your password reset code is: {code}\nThis code expires in 1 hour."
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

        logger.debug(f"Password reset email sent to {masked_email}")

    except Exception as e:
        logger.error(f"Error generating password reset for {masked_email}")

    return Response({'message': 'If an account exists, a reset code was sent'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_verify(request):
    """Verify a password reset code. Body: {email, code} -> returns success if valid"""
    email = request.data.get('email')
    code = request.data.get('code')

    masked_email = f"{email[:3]}****@..."

    if not email or not code:
        logger.warning("Password reset verification attempted without email or code.")
        return Response({'error': 'email and code are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.filter(email__iexact=email).first()
    if not user:
        logger.info(f"Password reset verification failed — user not found for {masked_email}")
        return Response({'error': 'Invalid code or email'}, status=status.HTTP_400_BAD_REQUEST)

    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()

    if not verification or not verification.is_valid():
        logger.warning(f"Invalid or expired password reset code attempt for {masked_email}")
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Password reset code verified successfully for {masked_email}")
    logger.debug(f"Verification ID {verification.id} validated for user ID {user.id}")

    return Response({'message': 'Code valid, you can reset your password'})


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm(request):
    """Confirm password reset and set new password. Body: {email, code, new_password, new_password2}"""
    email = request.data.get('email')
    code = request.data.get('code')
    new_password = request.data.get('new_password')
    new_password2 = request.data.get('new_password2')

    masked_email = f"{email[:3]}****@..." if email else None

    logger.info(f"Password reset confirm triggered for {masked_email}")

     # --- Validation checks ---
    if not all([email, code, new_password, new_password2]):
        logger.warning(f"Password reset confirm failed (missing fields) for {masked_email}")
        return Response({'error': 'email, code and new_password/new_password2 are required'}, status=status.HTTP_400_BAD_REQUEST)

    if new_password != new_password2:
        logger.warning(f"Password mismatch during reset for {masked_email}")
        return Response({'error': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

    # --- User existence check ---
    user = User.objects.filter(email__iexact=email).first()
    if not user:
        logger.warning(f"Password reset confirm failed - user not found for {masked_email}")
        return Response({'error': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    # --- Verify code ---
    verification = EmailVerification.objects.filter(user=user, code=code, used=False).order_by('-created_at').first()
    if not verification or not verification.is_valid():
        logger.warning(f"Password reset confirm failed - invalid/expired code for {masked_email}")
        return Response({'error': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    # --- Success path --- Set password
    user.set_password(new_password)
    user.save()

    verification.used = True
    verification.save()

    logger.info(f"Password reset successful for {masked_email} (verification ID: {getattr(verification, 'id', 'N/A')})")
    return Response({'message': 'Password updated successfully'})