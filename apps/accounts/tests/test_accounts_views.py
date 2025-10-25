"""
Test suite for account management functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import EmailVerification
from apps.core.tests.factories import UserFactory
from django.utils import timezone
from datetime import timedelta

pytestmark = pytest.mark.django_db


class TestAuthentication:
    def test_login_valid_credentials(self, api_client):
        """Test login with valid credentials"""
        user = UserFactory(email="test@example.com")
        user.set_password("testpass123")
        user.save()

        url = reverse('token_obtain_pair')
        response = api_client.post(url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_invalid_credentials(self, api_client):
        """Test login with invalid credentials"""
        user = UserFactory(email="test@example.com")
        user.set_password("testpass123")
        user.save()

        url = reverse('token_obtain_pair')
        response = api_client.post(url, {
            'email': 'test@example.com',
            'password': 'wrongpass'
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_token_refresh(self, api_client):
        """Test refreshing access token"""
        user = UserFactory()
        url = reverse('token_obtain_pair')
        auth_response = api_client.post(url, {
            'email': user.email,
            'password': 'testpass123'
        })

        refresh_url = reverse('token_refresh')
        response = api_client.post(refresh_url, {
            'refresh': auth_response.data['refresh']
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data


class TestEmailVerification:
    def test_verify_email_valid_code(self, api_client):
        """Test email verification with valid code"""
        user = UserFactory(is_verified=False)
        verification = EmailVerification.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('verify_email')
        response = api_client.post(url, {
            'email': user.email,
            'code': '123456'
        })

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_verified
        verification.refresh_from_db()
        assert verification.used

    def test_verify_email_invalid_code(self, api_client):
        """Test email verification with invalid code"""
        user = UserFactory(is_verified=False)
        EmailVerification.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('verify_email')
        response = api_client.post(url, {
            'email': user.email,
            'code': '654321'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert not user.is_verified

    def test_verify_email_expired_code(self, api_client):
        """Test email verification with expired code"""
        user = UserFactory(is_verified=False)
        EmailVerification.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() - timedelta(minutes=1)
        )

        url = reverse('verify_email')
        response = api_client.post(url, {
            'email': user.email,
            'code': '123456'
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert not user.is_verified


class TestPasswordReset:
    def test_password_reset_request(self, api_client):
        """Test requesting a password reset"""
        user = UserFactory()
        url = reverse('password_reset_request')
        response = api_client.post(url, {'email': user.email})

        assert response.status_code == status.HTTP_200_OK
        assert EmailVerification.objects.filter(user=user).exists()

    def test_password_reset_verify(self, api_client):
        """Test verifying a password reset code"""
        user = UserFactory()
        verification = EmailVerification.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('password_reset_verify')
        response = api_client.post(url, {
            'email': user.email,
            'code': '123456'
        })

        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_confirm(self, api_client):
        """Test confirming a password reset"""
        user = UserFactory()
        verification = EmailVerification.objects.create(
            user=user,
            code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('password_reset_confirm')
        response = api_client.post(url, {
            'email': user.email,
            'code': '123456',
            'new_password': 'newpass123',
            'new_password2': 'newpass123'
        })

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('newpass123')