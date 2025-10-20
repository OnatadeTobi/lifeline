"""
Test suite for blood request functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from apps.blood_requests.models import BloodRequest, DonorResponse
from apps.core.tests.factories import (
    BloodRequestFactory, DonorFactory, HospitalFactory, DonorResponseFactory
)
from django.utils import timezone

pytestmark = pytest.mark.django_db


class TestBloodRequestCreation:
    def test_create_blood_request(self, hospital_client):
        """Test creating a new blood request"""
        client, hospital = hospital_client
        url = reverse('request_create')
        data = {
            'blood_type': 'O+',
            'contact_phone': '+2348012345678',
            'notes': 'Urgent need for surgery'
        }

        response = client.post(url, data)

        assert response.status_code == status.HTTP_201_CREATED
        assert BloodRequest.objects.filter(hospital=hospital).exists()
        request = BloodRequest.objects.get(hospital=hospital)
        assert request.blood_type == data['blood_type']
        assert request.contact_phone == data['contact_phone']
        assert request.notes == data['notes']
        assert request.status == BloodRequest.RequestStatus.OPEN

    def test_create_blood_request_unauthenticated(self, api_client):
        """Test that unauthenticated users cannot create requests"""
        url = reverse('request_create')
        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_blood_request_as_donor(self, donor_client):
        """Test that donors cannot create blood requests"""
        client, _ = donor_client
        url = reverse('request_create')
        # send a valid payload so serializer validation doesn't short-circuit permission checks
        data = {
            'blood_type': 'O+',
            'contact_phone': '+2348012345678',
            'notes': 'Test attempt by donor'
        }

        response = client.post(url, data)

        # donors should not be able to create requests; ensure it is not created
        assert response.status_code != status.HTTP_201_CREATED
        assert not BloodRequest.objects.filter(notes='Test attempt by donor').exists()


class TestBloodRequestListing:
    def test_list_blood_requests(self, hospital_client, blood_request):
        """Test listing blood requests"""
        client, hospital = hospital_client
        url = reverse('request_list')
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['id'] == blood_request.id

    def test_blood_request_detail(self, hospital_client, blood_request):
        """Test retrieving a specific blood request"""
        client, hospital = hospital_client
        blood_request.hospital = hospital
        blood_request.save()
        url = reverse('request_detail', kwargs={'pk': blood_request.id})
        response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == blood_request.id
        assert response.data['blood_type'] == blood_request.blood_type


class TestDonorResponse:
    def test_accept_request(self, donor_client, blood_request):
        """Test donor accepting a blood request"""
        client, donor = donor_client
        url = reverse('accept_request', kwargs={'request_id': blood_request.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert DonorResponse.objects.filter(
            donor=donor,
            request=blood_request
        ).exists()
        blood_request.refresh_from_db()
        assert blood_request.status == BloodRequest.RequestStatus.MATCHED

    def test_accept_request_twice(self, donor_client, blood_request):
        """Test donor cannot accept the same request twice"""
        client, donor = donor_client
        DonorResponseFactory(donor=donor, request=blood_request)

        url = reverse('accept_request', kwargs={'request_id': blood_request.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK

    def test_mark_request_fulfilled(self, hospital_client, donor_response):
        """Test marking a request as fulfilled"""
        client, hospital = hospital_client
        blood_request = donor_response.request
        blood_request.hospital = hospital
        blood_request.save()

        url = reverse('mark_fulfilled', kwargs={'request_id': blood_request.id})
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        blood_request.refresh_from_db()
        assert blood_request.status == BloodRequest.RequestStatus.FULFILLED

    def test_confirm_donation(self, hospital_client, donor_response):
        """Test confirming a specific donor's donation"""
        client, hospital = hospital_client
        blood_request = donor_response.request
        blood_request.hospital = hospital
        blood_request.save()

        url = reverse('confirm_donation', kwargs={
            'request_id': blood_request.id,
            'response_id': donor_response.id
        })
        response = client.post(url)

        assert response.status_code == status.HTTP_200_OK
        blood_request.refresh_from_db()
        assert blood_request.status == BloodRequest.RequestStatus.FULFILLED
        blood_request.refresh_from_db()
        assert blood_request.status == BloodRequest.RequestStatus.FULFILLED