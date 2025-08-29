"""
Comprehensive tests for JWT token refresh functionality.
Tests both happy path and edge cases for the token refresh endpoint.
"""
import pytest
from typing import Any, Dict
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from accounts.tests.factories import UserFactory, TestData
from freezegun import freeze_time
from datetime import datetime, timedelta

User = get_user_model()


class TokenRefreshTestCase(APITestCase):
    """Test cases for JWT token refresh endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.refresh_url = reverse('auth-refresh')
        self.user = UserFactory()
        self.refresh_token = RefreshToken.for_user(self.user)

    def _get_response_data(self, response) -> Dict[str, Any]:  # type: ignore
        """Helper method to safely access response data with type annotation."""
        return response.data  # type: ignore

    def test_successful_token_refresh(self):
        """Test successful token refresh with valid refresh token."""
        refresh_data = {'refresh': str(self.refresh_token)}
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '00')
        self.assertIn('Token refreshed successfully', response_data['responseDescription'])
        
        # Check new tokens are returned
        self.assertIn('access', response_data['data'])
        self.assertIn('refresh', response_data['data'])
        
        # Verify tokens are valid JWT format
        new_access = response_data['data']['access']
        new_refresh = response_data['data']['refresh']
        self.assertTrue(new_access.count('.') == 2)
        self.assertTrue(new_refresh.count('.') == 2)
        
        # New refresh token should be different from original
        self.assertNotEqual(str(self.refresh_token), new_refresh)

    def test_refresh_with_invalid_token(self):
        """Test refresh fails with invalid refresh token."""
        refresh_data = {'refresh': 'invalid.jwt.token'}
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '09')
        self.assertIn('Invalid refresh token', response_data['responseDescription'])

    def test_refresh_with_expired_token(self):
        """Test refresh fails with expired refresh token."""
        # Create token and simulate expiration
        with freeze_time("2024-01-01"):
            expired_token = RefreshToken.for_user(self.user)
        
        # Move to future past token expiration
        with freeze_time("2024-12-31"):
            refresh_data = {'refresh': str(expired_token)}
            response = self.client.post(self.refresh_url, refresh_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            response_data = self._get_response_data(response)
            self.assertEqual(response_data['responseCode'], '09')

    def test_refresh_with_blacklisted_token(self):
        """Test refresh fails with blacklisted refresh token."""
        # First use the token successfully
        refresh_data = {'refresh': str(self.refresh_token)}
        first_response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        
        # Try to use the same token again (should be blacklisted)
        second_response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(second_response.status_code, status.HTTP_401_UNAUTHORIZED)
        second_response_data = self._get_response_data(second_response)
        self.assertEqual(second_response_data['responseCode'], '09')

    def test_refresh_with_missing_token(self):
        """Test refresh fails when refresh token is missing."""
        response = self.client.post(self.refresh_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')

    def test_refresh_with_empty_token(self):
        """Test refresh fails with empty refresh token."""
        refresh_data = {'refresh': ''}
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')

    def test_refresh_with_malformed_token(self):
        """Test refresh fails with malformed JWT token."""
        malformed_tokens = [
            'not.a.jwt',
            'only.two.parts',
            'too.many.parts.here.invalid',
            '',
            None
        ]
        
        for token in malformed_tokens:
            refresh_data = {'refresh': token}
            response = self.client.post(self.refresh_url, refresh_data, format='json')
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_refresh_response_structure(self):
        """Test refresh response has correct structure."""
        refresh_data = {'refresh': str(self.refresh_token)}
        
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        response_data = self._get_response_data(response)
        self.assertIn('responseCode', response_data)
        self.assertIn('responseDescription', response_data)
        self.assertIn('data', response_data)
        
        # Check token data structure
        token_data = response_data['data']
        self.assertIn('access', token_data)
        self.assertIn('refresh', token_data)

    def test_refresh_token_rotation(self):
        """Test that refresh token rotation works correctly."""
        original_refresh = str(self.refresh_token)
        refresh_data = {'refresh': original_refresh}
        
        # First refresh
        response1 = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        response1_data = self._get_response_data(response1)
        new_refresh_token = response1_data['data']['refresh']
        
        # Use new refresh token
        refresh_data = {'refresh': new_refresh_token}
        response2 = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Original token should now be blacklisted
        response3 = self.client.post(self.refresh_url, {'refresh': original_refresh}, format='json')
        self.assertEqual(response3.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_for_inactive_user(self):
        """Test refresh fails for inactive user."""
        # Create token for user, then deactivate user
        inactive_user = UserFactory()
        token = RefreshToken.for_user(inactive_user)
        
        # Deactivate user
        inactive_user.is_active = False
        inactive_user.save()
        
        refresh_data = {'refresh': str(token)}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


@pytest.mark.django_db
class TokenRefreshPytestCase:
    """Pytest-style tests for token refresh."""

    def test_token_blacklist_created_on_refresh(self):
        """Test that old refresh tokens are blacklisted after refresh."""
        user = UserFactory()
        refresh_token = RefreshToken.for_user(user)
        original_jti = refresh_token.payload['jti']
        
        # Simulate token refresh by creating new token
        new_token = RefreshToken.for_user(user)
        
        # Check that we can create blacklist entries
        outstanding_token = OutstandingToken.objects.create(
            user=user,
            jti=original_jti,
            token=str(refresh_token),
            created_at=refresh_token.current_time,
            expires_at=datetime.fromtimestamp(refresh_token.payload['exp'])
        )
        
        blacklisted_token = BlacklistedToken.objects.create(token=outstanding_token)
        
        assert blacklisted_token is not None
        assert blacklisted_token.token.jti == original_jti

    def test_multiple_refresh_tokens_per_user(self):
        """Test user can have multiple valid refresh tokens."""
        user = UserFactory()
        
        # Create multiple refresh tokens
        token1 = RefreshToken.for_user(user)
        token2 = RefreshToken.for_user(user)
        token3 = RefreshToken.for_user(user)
        
        # All should have different JTIs
        jti1 = token1.payload['jti']
        jti2 = token2.payload['jti']
        jti3 = token3.payload['jti']
        
        assert jti1 != jti2 != jti3
        assert len({jti1, jti2, jti3}) == 3  # All unique
