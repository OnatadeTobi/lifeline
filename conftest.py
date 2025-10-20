"""
Core test utilities and fixtures for Lifeline test suite.
"""
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from apps.core.tests.factories import (
    UserFactory, HospitalFactory, DonorFactory,
    StateFactory, LocalGovernmentFactory,
    BloodRequestFactory, DonorResponseFactory
)

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client():
    """Returns an authenticated API client"""
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user

@pytest.fixture
def donor_client():
    """Returns an API client authenticated as a donor"""
    client = APIClient()
    donor = DonorFactory()
    client.force_authenticate(user=donor.user)
    return client, donor

@pytest.fixture
def hospital_client():
    """Returns an API client authenticated as a hospital"""
    client = APIClient()
    hospital = HospitalFactory()
    client.force_authenticate(user=hospital.user)
    return client, hospital

@pytest.fixture
def state():
    """Creates a test state"""
    return StateFactory()

@pytest.fixture
def local_government(state):
    """Creates a test LGA in the given state"""
    return LocalGovernmentFactory(state=state)

@pytest.fixture
def blood_request(hospital_client):
    """Creates a test blood request"""
    _, hospital = hospital_client
    return BloodRequestFactory(hospital=hospital)

@pytest.fixture
def donor_response(blood_request, donor_client):
    """Creates a test donor response"""
    _, donor = donor_client
    return DonorResponseFactory(request=blood_request, donor=donor)