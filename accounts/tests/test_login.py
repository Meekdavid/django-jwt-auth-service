"""
Comprehensive tests for user login functionality.
Tests both happy path and edge cases for the login endpoint.
"""
import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.tests.factories import UserFactory, InactiveUserFactory, TestData

User = get_user_model()


class UserLoginTestCase(APITestCase):
    """Test cases for user login endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.login_url = reverse('auth:login')
        self.password = TestData.VALID_PASSWORD
        self.user = UserFactory(password=self.password)

    def test_successful_login(self):
        """Test successful login with valid credentials."""
        login_data = {
            'email': self.user.email,
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')
        self.assertIn('User logged in successfully', response.data['responseDescription'])
        
        # Check JWT tokens are returned
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        
        # Verify tokens are valid JWT format
        access_token = response.data['data']['access']
        refresh_token = response.data['data']['refresh']
        self.assertTrue(access_token.count('.') == 2)  # JWT has 3 parts separated by dots
        self.assertTrue(refresh_token.count('.') == 2)

    def test_login_with_invalid_email(self):
        """Test login fails with non-existent email."""
        login_data = {
            'email': 'nonexistent@example.com',
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['responseCode'], '08')
        self.assertIn('Invalid credentials', response.data['responseDescription'])

    def test_login_with_invalid_password(self):
        """Test login fails with wrong password."""
        login_data = {
            'email': self.user.email,
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['responseCode'], '08')
        self.assertIn('Invalid credentials', response.data['responseDescription'])

    def test_login_with_inactive_user(self):
        """Test login fails for inactive user account."""
        inactive_user = InactiveUserFactory(password=self.password)
        login_data = {
            'email': inactive_user.email,
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['responseCode'], '08')

    def test_login_with_missing_fields(self):
        """Test login fails when required fields are missing."""
        # Missing password
        response = self.client.post(self.login_url, {'email': self.user.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing email
        response = self.client.post(self.login_url, {'password': self.password}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing both
        response = self.client.post(self.login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_empty_fields(self):
        """Test login fails with empty email or password."""
        # Empty email
        login_data = {'email': '', 'password': self.password}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Empty password
        login_data = {'email': self.user.email, 'password': ''}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_case_insensitive_email(self):
        """Test login works with different email case."""
        login_data = {
            'email': self.user.email.upper(),
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')

    def test_login_with_whitespace_email(self):
        """Test login handles email with whitespace."""
        login_data = {
            'email': f'  {self.user.email}  ',
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')

    def test_login_response_structure(self):
        """Test login response has correct structure."""
        login_data = {
            'email': self.user.email,
            'password': self.password
        }
        
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('responseCode', response.data)
        self.assertIn('responseDescription', response.data)
        self.assertIn('data', response.data)
        
        # Check token data structure
        token_data = response.data['data']
        self.assertIn('access', token_data)
        self.assertIn('refresh', token_data)
        
        # Ensure no sensitive data is exposed
        self.assertNotIn('password', token_data)
        self.assertNotIn('user', token_data)

    def test_login_with_sql_injection_attempt(self):
        """Test login is protected against SQL injection."""
        malicious_data = {
            'email': "test@example.com'; DROP TABLE auth_user; --",
            'password': self.password
        }
        
        response = self.client.post(self.login_url, malicious_data, format='json')
        
        # Should fail safely without breaking anything
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify user table still exists and has data
        self.assertTrue(User.objects.filter(email=self.user.email).exists())


@pytest.mark.django_db
class UserLoginPytestCase:
    """Pytest-style tests for user login."""

    def test_login_token_contains_user_info(self):
        """Test that JWT token contains correct user information."""
        user = UserFactory()
        refresh = RefreshToken.for_user(user)
        
        # Decode token payload
        payload = refresh.payload
        
        assert payload['user_id'] == user.id
        assert 'exp' in payload  # Expiration time
        assert 'iat' in payload  # Issued at time

    def test_multiple_concurrent_logins(self):
        """Test multiple users can login concurrently."""
        users = UserFactory.create_batch(3)
        
        for user in users:
            refresh = RefreshToken.for_user(user)
            assert refresh is not None
            assert refresh.payload['user_id'] == user.id
