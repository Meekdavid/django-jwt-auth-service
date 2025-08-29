"""
Comprehensive tests for user logout functionality.
Tests both happy path and edge cases for the logout endpoint.
"""
import pytest
from typing import Dict, Any
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.tests.factories import UserFactory, TestData

User = get_user_model()


class UserLogoutTestCase(APITestCase):
    """Test cases for user logout endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.logout_url = reverse('auth-logout')
        self.user = UserFactory()
        self.refresh_token = RefreshToken.for_user(self.user)
        self.access_token = self.refresh_token.access_token

    def _get_response_data(self, response) -> Dict[str, Any]:  # type: ignore
        """Helper method to safely access response data with type annotation."""
        return response.data  # type: ignore

    def test_successful_logout(self):
        """Test successful logout with valid tokens."""
        # Authenticate with access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore  # type: ignore
        
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((self._get_response_data(response))['responseCode'], '00')
        self.assertIn('User logged out successfully', (self._get_response_data(response))['responseDescription'])
        
        # Verify response contains logout confirmation
        self.assertIn('message', (self._get_response_data(response))['data'])
        self.assertEqual((self._get_response_data(response))['data']['message'], 'Logged out')

    def test_logout_without_authentication(self):
        """Test logout fails without authentication."""
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual((self._get_response_data(response))['responseCode'], '08')

    def test_logout_with_invalid_access_token(self):
        """Test logout fails with invalid access token."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid.jwt.token')  # type: ignore
        
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual((self._get_response_data(response))['responseCode'], '08')

    def test_logout_with_expired_access_token(self):
        """Test logout fails with expired access token."""
        # Create an access token and simulate expiration
        expired_access = self.refresh_token.access_token
        expired_access.set_exp(lifetime=timedelta(seconds=-1))  # Set to expired
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {expired_access}')  # type: ignore
        
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_missing_refresh_token(self):
        """Test logout fails when refresh token is missing."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        response = self.client.post(self.logout_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '07')

    def test_logout_with_invalid_refresh_token(self):
        """Test logout fails with invalid refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        logout_data = {'refresh': 'invalid.jwt.token'}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '07')

    def test_logout_with_empty_refresh_token(self):
        """Test logout fails with empty refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        logout_data = {'refresh': ''}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '07')

    def test_logout_blacklists_refresh_token(self):
        """Test that logout blacklists the refresh token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        # Logout
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Try to use the refresh token after logout
        refresh_url = reverse('auth-refresh')
        refresh_response = self.client.post(refresh_url, logout_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_multiple_times(self):
        """Test that multiple logout attempts handle gracefully."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        logout_data = {'refresh': str(self.refresh_token)}
        
        # First logout should succeed
        response1 = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second logout with same token should fail
        response2 = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_response_structure(self):
        """Test logout response has correct structure."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('responseCode', self._get_response_data(response))
        self.assertIn('responseDescription', self._get_response_data(response))
        self.assertIn('data', self._get_response_data(response))
        
        # Check data structure
        data = (self._get_response_data(response))['data']
        self.assertIn('message', data)
        
        # Ensure no sensitive data is exposed
        self.assertNotIn('refresh', data)
        self.assertNotIn('access', data)

    def test_logout_with_different_user_token(self):
        """Test logout with refresh token from different user fails."""
        # Create another user and their tokens
        other_user = UserFactory()
        other_refresh = RefreshToken.for_user(other_user)
        
        # Authenticate as first user but try to logout with other user's token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        
        logout_data = {'refresh': str(other_refresh)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        # This should fail as the tokens don't match the authenticated user
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_preserves_other_user_sessions(self):
        """Test that logging out one user doesn't affect other users."""
        # Create another user and their tokens
        other_user = UserFactory()
        other_refresh = RefreshToken.for_user(other_user)
        other_access = other_refresh.access_token
        
        # Logout first user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')  # type: ignore
        logout_data = {'refresh': str(self.refresh_token)}
        response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Other user should still be able to use their tokens
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {other_access}')  # type: ignore
        protected_url = reverse('auth-protected-test')
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@pytest.mark.django_db
class UserLogoutPytestCase:
    """Pytest-style tests for user logout."""

    def test_logout_clears_user_session(self):
        """Test that logout properly clears user session data."""
        user = UserFactory()
        refresh_token = RefreshToken.for_user(user)
        
        # Simulate logout by blacklisting token
        refresh_token.blacklist()
        
        # Token should now be blacklisted
        assert refresh_token.check_blacklist() is True

    def test_concurrent_logouts(self):
        """Test multiple users can logout concurrently."""
        users = UserFactory.create_batch(3)
        tokens = [RefreshToken.for_user(user) for user in users]
        
        # All users logout
        for token in tokens:
            token.blacklist()
        
        # All tokens should be blacklisted
        for token in tokens:
            assert token.check_blacklist() is True
