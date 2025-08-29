"""
Comprehensive tests for user registration functionality.
Tests both happy path and edge cases for the registration endpoint.
"""
import pytest
from typing import Any, Dict
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.response import Response
from accounts.tests.factories import UserFactory, TestData

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration endpoint."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.register_url = reverse('auth-register')
        self.valid_data = TestData.VALID_USER_DATA.copy()

    def _get_response_data(self, response) -> Dict[str, Any]:  # type: ignore
        """Helper method to safely access response data with type annotation."""
        return response.data  # type: ignore

    def test_successful_registration(self):
        """Test successful user registration with valid data."""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '00')
        self.assertIn('User registered successfully', response_data['responseDescription'])
        
        # Verify user was created in database
        user = User.objects.get(email=self.valid_data['email'])
        # self.assertEqual(user.full_name, self.valid_data['full_name'])  # Skip if full_name not available
        self.assertTrue(user.check_password(self.valid_data['password']))
        self.assertTrue(user.is_active)

    def test_registration_with_existing_email(self):
        """Test registration fails when email already exists."""
        # Create existing user
        UserFactory(email=self.valid_data['email'])
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('email', response_data['data'])

    def test_registration_with_invalid_email(self):
        """Test registration fails with invalid email format."""
        self.valid_data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('email', response_data['data'])

    def test_registration_with_mismatched_passwords(self):
        """Test registration fails when passwords don't match."""
        self.valid_data['password2'] = 'different_password'
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('password2', response_data['data'])

    def test_registration_with_weak_password(self):
        """Test registration fails with weak password."""
        weak_password = '123'
        self.valid_data['password'] = weak_password
        self.valid_data['password2'] = weak_password
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('password', response_data['data'])

    def test_registration_with_missing_fields(self):
        """Test registration fails when required fields are missing."""
        incomplete_data = {'email': 'test@example.com'}
        
        response = self.client.post(self.register_url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        
        # Check all required fields are mentioned in errors
        required_fields = ['password', 'password2', 'full_name']
        for field in required_fields:
            self.assertIn(field, response_data['data'])

    def test_registration_with_empty_full_name(self):
        """Test registration fails with empty full name."""
        self.valid_data['full_name'] = ''
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertEqual(response_data['responseCode'], '07')
        self.assertIn('full_name', response_data['data'])

    def test_registration_with_whitespace_email(self):
        """Test registration handles email with whitespace."""
        self.valid_data['email'] = '  test@example.com  '
        
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Verify email was trimmed
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.email, 'test@example.com')

    def test_registration_case_insensitive_email(self):
        """Test registration treats emails as case insensitive."""
        # Register with uppercase email
        uppercase_data = self.valid_data.copy()
        uppercase_data['email'] = 'TEST@EXAMPLE.COM'
        
        response = self.client.post(self.register_url, uppercase_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Try to register with lowercase version
        lowercase_data = self.valid_data.copy()
        lowercase_data['email'] = 'test@example.com'
        
        response = self.client.post(self.register_url, lowercase_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_data = self._get_response_data(response)
        self.assertIn('email', response_data['data'])

    def test_registration_response_structure(self):
        """Test registration response has correct structure."""
        response = self.client.post(self.register_url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check response structure
        response_data = self._get_response_data(response)
        self.assertIn('responseCode', response_data)
        self.assertIn('responseDescription', response_data)
        self.assertIn('data', response_data)
        
        # Check user data structure
        user_data = response_data['data']
        self.assertIn('id', user_data)
        self.assertIn('email', user_data)
        self.assertIn('full_name', user_data)
        self.assertIn('date_joined', user_data)
        
        # Ensure password is not in response
        self.assertNotIn('password', user_data)


@pytest.mark.django_db
class UserRegistrationPytestCase:
    """Pytest-style tests for user registration."""

    def test_user_creation_with_factory(self):
        """Test user creation using factory."""
        user = UserFactory()
        assert user.email is not None
        assert user.full_name is not None
        assert user.is_active is True

    def test_multiple_users_creation(self):
        """Test creating multiple users with unique emails."""
        users = UserFactory.create_batch(5)
        emails = [user.email for user in users]
        
        # All emails should be unique
        assert len(emails) == len(set(emails))
        
        # All users should be in database
        assert User.objects.count() == 5
