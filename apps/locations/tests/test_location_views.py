"""
Test suite for location functionality.
"""
import pytest
from django.urls import reverse
from rest_framework import status
from apps.core.tests.factories import StateFactory, LocalGovernmentFactory

pytestmark = pytest.mark.django_db


class TestLocationListing:
    def test_list_states(self, api_client):
        """Test listing all states"""
        state1 = StateFactory()
        state2 = StateFactory()
        url = reverse('state_list')

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        state_ids = [state['id'] for state in response.data['results']]
        assert state1.id in state_ids
        assert state2.id in state_ids

    def test_list_local_governments(self, api_client):
        """Test listing local governments for a specific state"""
        state = StateFactory()
        lga1 = LocalGovernmentFactory(state=state)
        lga2 = LocalGovernmentFactory(state=state)
        other_state_lga = LocalGovernmentFactory()

        url = reverse('lga_list', kwargs={'state_id': state.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        lga_ids = [lga['id'] for lga in response.data['results']]
        assert lga1.id in lga_ids
        assert lga2.id in lga_ids
        assert other_state_lga.id not in lga_ids

    def test_list_all_local_governments(self, api_client):
        """Test listing all local governments without state filter"""
        lga1 = LocalGovernmentFactory()
        lga2 = LocalGovernmentFactory()
        lga3 = LocalGovernmentFactory()

        url = reverse('lga_list_all')
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3
        lga_ids = [lga['id'] for lga in response.data['results']]
        assert lga1.id in lga_ids
        assert lga2.id in lga_ids
        assert lga3.id in lga_ids