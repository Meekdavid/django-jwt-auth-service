"""
Comprehensive tests for password reset functionality.
Tests both happy path and edge cases for forgot-password and reset-password endpoints.
"""
import pytest
from typing import Any, Dict
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from accounts.tests.factories import UserFactory, TestData
from auth_service.utils.password_reset_service import PasswordResetService
from freezegun import freeze_time
from unittest.mock import patch
import secrets

User = get_user_model()


class ForgotPasswordTestCase(APITestCase):
    """Test cases for forgot password endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.forgot_password_url = reverse('auth-forgot-password')
        self.user = UserFactory()
        
        # Clear cache before each test
        cache.clear()

    def _get_response_data(self, response) -> Dict[str, Any]:  # type: ignore
        """Helper method to safely access response data with type annotation."""
        return response.data  # type: ignore

    def test_successful_forgot_password(self):
        """Test successful forgot password request."""
        forgot_data = {'email': self.user.email}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '00')
        self.assertIn('Password reset initiated successfully', response_data['responseDescription'])
        
        # Check response contains email
        self.assertIn('email', response_data['data'])
        self.assertEqual(response_data['data']['email'], self.user.email)
        
        # In development, token should be returned
        self.assertIn('token', response_data['data'])

    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email."""
        forgot_data = {'email': 'nonexistent@example.com'}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('No user found with this email', response_data['responseDescription'])

    def test_forgot_password_invalid_email_format(self):
        """Test forgot password with invalid email format."""
        forgot_data = {'email': 'invalid-email-format'}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')

    def test_forgot_password_empty_email(self):
        """Test forgot password with empty email."""
        forgot_data = {'email': ''}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')

    def test_forgot_password_missing_email(self):
        """Test forgot password without email field."""
        response = self.client.post(self.forgot_password_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')

    def test_forgot_password_case_insensitive(self):
        """Test forgot password works with different email case."""
        forgot_data = {'email': self.user.email.upper()}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '00')

    def test_forgot_password_stores_token_in_redis(self):
        """Test forgot password stores reset token in Redis."""
        forgot_data = {'email': self.user.email}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify token was stored in Redis
        reset_service = PasswordResetService()
        stored_user_id: str = reset_service.redis_client.get(  # type: ignore
            f"password_reset:{(self._get_response_data(response))['data']['token']}"
        )
        self.assertEqual(int(stored_user_id), self.user.id)

    def test_forgot_password_token_expiration(self):
        """Test forgot password token has correct expiration."""
        forgot_data = {'email': self.user.email}
        
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        token = (self._get_response_data(response))['data']['token']
        
        # Check token TTL in Redis
        reset_service = PasswordResetService()
        ttl: int = reset_service.redis_client.ttl(f"password_reset:{token}")  # type: ignore
        
        # Should be around 10 minutes (600 seconds)
        self.assertGreater(ttl, 590)
        self.assertLessEqual(ttl, 600)

    @patch('auth_service.utils.password_reset_service.logger')
    def test_forgot_password_multiple_requests(self, mock_logger):
        """Test multiple forgot password requests for same user."""
        forgot_data = {'email': self.user.email}
        
        # First request
        response1 = self.client.post(self.forgot_password_url, forgot_data, format='json')
        token1 = (self._get_response_data(response1))['data']['token']
        
        # Second request
        response2 = self.client.post(self.forgot_password_url, forgot_data, format='json')
        token2 = (self._get_response_data(response2))['data']['token']
        
        # Both should succeed but with different tokens
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertNotEqual(token1, token2)


class ResetPasswordTestCase(APITestCase):
    """Test cases for reset password endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.reset_password_url = reverse('auth-reset-password')
        self.user = UserFactory()
        self.reset_service = PasswordResetService()
        self.reset_token = self.reset_service.generate_reset_token(self.user.id)
        self.new_password = "NewSecurePass123!"
        
        # Clear cache before each test
        cache.clear()

    def _get_response_data(self, response) -> Dict[str, Any]:  # type: ignore
        """Helper method to safely access response data with type annotation."""
        return response.data  # type: ignore

    def test_successful_password_reset(self):
        """Test successful password reset with valid token."""
        reset_data = {
            'token': self.reset_token,
            'password': self.new_password,
            'password2': self.new_password
        }
        
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual((self._get_response_data(response))['responseCode'], '00')
        self.assertIn('Password reset completed successfully', (self._get_response_data(response))['responseDescription'])
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))
        
        # Verify response contains user info
        self.assertIn('user_id', (self._get_response_data(response))['data'])
        self.assertIn('email', (self._get_response_data(response))['data'])
        self.assertEqual((self._get_response_data(response))['data']['user_id'], self.user.id)

    def test_reset_password_invalid_token(self):
        """Test reset password with invalid token."""
        reset_data = {
            'token': 'invalid-token',
            'password': self.new_password,
            'password2': self.new_password
        }
        
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '11')
        self.assertIn('Invalid or expired token', (self._get_response_data(response))['responseDescription'])

    def test_reset_password_expired_token(self):
        """Test reset password with expired token."""
        # Create token and wait for expiration
        with freeze_time("2024-01-01 12:00:00"):
            expired_token = self.reset_service.generate_reset_token(self.user.id)
        
        # Move to future past token expiration
        with freeze_time("2024-01-01 12:15:00"):  # 15 minutes later
            reset_data = {
                'token': expired_token,
                'password': self.new_password,
                'password2': self.new_password
            }
            
            response = self.client.post(self.reset_password_url, reset_data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual((self._get_response_data(response))['responseCode'], '11')

    def test_reset_password_mismatched_passwords(self):
        """Test reset password with mismatched passwords."""
        reset_data = {
            'token': self.reset_token,
            'password': self.new_password,
            'password2': 'DifferentPassword123!'
        }
        
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '07')
        self.assertIn('password2', (self._get_response_data(response))['data'])

    def test_reset_password_weak_password(self):
        """Test reset password with weak password."""
        weak_password = '123'
        reset_data = {
            'token': self.reset_token,
            'password': weak_password,
            'password2': weak_password
        }
        
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '07')
        self.assertIn('password', (self._get_response_data(response))['data'])

    def test_reset_password_missing_fields(self):
        """Test reset password with missing required fields."""
        # Missing token
        response = self.client.post(self.reset_password_url, {
            'password': self.new_password,
            'password2': self.new_password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing password
        response = self.client.post(self.reset_password_url, {
            'token': self.reset_token,
            'password2': self.new_password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing password2
        response = self.client.post(self.reset_password_url, {
            'token': self.reset_token,
            'password': self.new_password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reset_password_token_consumed(self):
        """Test reset password token is consumed after use."""
        reset_data = {
            'token': self.reset_token,
            'password': self.new_password,
            'password2': self.new_password
        }
        
        # First use should succeed
        response1 = self.client.post(self.reset_password_url, reset_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Second use with same token should fail
        response2 = self.client.post(self.reset_password_url, reset_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response2))['responseCode'], '11')

    def test_reset_password_for_nonexistent_user(self):
        """Test reset password handles deleted user gracefully."""
        # Create token, then delete user
        token = self.reset_service.generate_reset_token(self.user.id)
        user_id = self.user.id
        self.user.delete()
        
        reset_data = {
            'token': token,
            'password': self.new_password,
            'password2': self.new_password
        }
        
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual((self._get_response_data(response))['responseCode'], '11')


@pytest.mark.django_db
class PasswordResetPytestCase:
    """Pytest-style tests for password reset."""

    def test_password_reset_service_token_generation(self):
        """Test password reset service generates valid tokens."""
        user = UserFactory()
        service = PasswordResetService()
        
        token = service.generate_reset_token(user.id)
        
        assert token is not None
        assert len(token) > 20  # Should be reasonably long
        assert isinstance(token, str)

    def test_password_reset_service_token_verification(self):
        """Test password reset service verifies tokens correctly."""
        user = UserFactory()
        service = PasswordResetService()
        
        token = service.generate_reset_token(user.id)
        verified_user_id = service.verify_and_consume_token(token)
        
        assert verified_user_id == user.id

    def test_password_reset_service_token_consumption(self):
        """Test password reset service consumes tokens after verification."""
        user = UserFactory()
        service = PasswordResetService()
        
        token = service.generate_reset_token(user.id)
        
        # First verification should succeed
        user_id1 = service.verify_and_consume_token(token)
        assert user_id1 == user.id
        
        # Second verification should fail (token consumed)
        user_id2 = service.verify_and_consume_token(token)
        assert user_id2 is None
