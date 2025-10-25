import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestRateLimiting:
    def test_login_rate_limit(self, api_client):
        url = reverse('token_obtain_pair')
        data = {'email': 'test@example.com', 'password': 'wrongpass'}

        # Make 6 requests (1 over limit)
        for i in range(6):
            # Use a dedicated REMOTE_ADDR to avoid interference from other tests
            response = api_client.post(url, data, REMOTE_ADDR='10.0.0.1')
            if i < 5:
                assert response.status_code != 429
            else:
                assert response.status_code == 429
                assert 'Rate limit exceeded' in response.json()['error']

    def test_password_reset_rate_limit(self, api_client):
        url = reverse('password_reset_request')
        data = {'email': 'test@example.com'}

        # Make 4 requests (1 over limit)
        for i in range(4):
            # Use a different REMOTE_ADDR for this test to isolate counters
            response = api_client.post(url, data, REMOTE_ADDR='10.0.0.2')
            if i < 3:
                assert response.status_code != 429
            else:
                assert response.status_code == 429