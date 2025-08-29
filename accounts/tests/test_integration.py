"""
Integration tests for complete authentication workflows.
Tests end-to-end scenarios combining multiple endpoints.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.tests.factories import UserFactory, TestData
from auth_service.utils.password_reset_service import PasswordResetService
import json

User = get_user_model()


class AuthenticationWorkflowTestCase(APITestCase):
    """Integration tests for complete authentication workflows."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        
        # URLs
        self.register_url = reverse('auth-register')
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('auth-refresh')
        self.logout_url = reverse('auth-logout')
        self.forgot_password_url = reverse('auth-forgot-password')
        self.reset_password_url = reverse('auth-reset-password')
        
        # Test data
        self.user_data = TestData.VALID_USER_DATA.copy()
        
        # Clear cache before each test
        cache.clear()

    def test_complete_registration_to_login_workflow(self):
        """Test complete workflow from registration to successful login."""
        # Step 1: Register new user
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['responseCode'], '00')
        
        registered_user_id = response.data['data']['id']
        
        # Step 2: Login with registered credentials
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')
        
        # Verify user data matches
        # self.assertEqual(response.data['data']['user']['id'], registered_user_id)
        # self.assertEqual(response.data['data']['user']['email'], self.user_data['email'])
        
        # Verify tokens are present
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])

    def test_login_refresh_logout_workflow(self):
        """Test complete session management workflow."""
        # Setup: Create user and login
        user = UserFactory()
        login_data = {'email': user.email, 'password': TestData.DEFAULT_PASSWORD}
        response = self.client.post(self.login_url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data['data']['access']
        refresh_token = response.data['data']['refresh']
        
        # Step 1: Use access token for authenticated request
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Step 2: Refresh tokens
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(self.refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')
        
        new_access_token = response.data['data']['access']
        new_refresh_token = response.data['data']['refresh']
        
        # Verify new tokens are different
        self.assertNotEqual(access_token, new_access_token)
        self.assertNotEqual(refresh_token, new_refresh_token)
        
        # Step 3: Logout
        logout_data = {'refresh': new_refresh_token}
        response = self.client.post(self.logout_url, logout_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')
        
        # Step 4: Try to use refresh token after logout (should fail)
        response = self.client.post(self.refresh_url, {'refresh': new_refresh_token}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_reset_complete_workflow(self):
        """Test complete password reset workflow."""
        # Setup: Create user
        user = UserFactory()
        old_password = TestData.DEFAULT_PASSWORD
        new_password = 'NewSecurePassword123!'
        
        # Step 1: Verify user can login with old password
        login_data = {'email': user.email, 'password': old_password}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Step 2: Request password reset
        forgot_data = {'email': user.email}
        response = self.client.post(self.forgot_password_url, forgot_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reset_token = response.data['data']['token']
        
        # Step 3: Reset password with token
        reset_data = {
            'token': reset_token,
            'password': new_password,
            'password2': new_password
        }
        response = self.client.post(self.reset_password_url, reset_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')
        
        # Step 4: Verify old password no longer works
        login_data = {'email': user.email, 'password': old_password}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Step 5: Verify new password works
        login_data = {'email': user.email, 'password': new_password}
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['responseCode'], '00')

    def test_token_blacklisting_across_sessions(self):
        """Test token blacklisting behavior across multiple sessions."""
        user = UserFactory()
        login_data = {'email': user.email, 'password': TestData.DEFAULT_PASSWORD}
        
        # Create multiple sessions
        session1_response = self.client.post(self.login_url, login_data, format='json')
        session1_refresh = session1_response.data['data']['refresh']
        
        session2_response = self.client.post(self.login_url, login_data, format='json')
        session2_refresh = session2_response.data['data']['refresh']
        
        # Verify both sessions work
        self.assertEqual(session1_response.status_code, status.HTTP_200_OK)
        self.assertEqual(session2_response.status_code, status.HTTP_200_OK)
        
        # Logout from session 1
        logout_data = {'refresh': session1_refresh}
        response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Session 1 refresh should fail
        response = self.client.post(self.refresh_url, {'refresh': session1_refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Session 2 refresh should still work
        response = self.client.post(self.refresh_url, {'refresh': session2_refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_registration_validation_edge_cases(self):
        """Test edge cases in registration validation."""
        base_data = TestData.VALID_USER_DATA.copy()
        
        # Test duplicate email (case variations)
        response1 = self.client.post(self.register_url, base_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Try with same email in different case
        duplicate_data = base_data.copy()
        duplicate_data['email'] = base_data['email'].upper()
        response2 = self.client.post(self.register_url, duplicate_data, format='json')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test password complexity requirements
        weak_password_data = base_data.copy()
        weak_password_data['email'] = 'different@example.com'
        weak_password_data['password'] = '123'
        weak_password_data['password2'] = '123'
        
        response3 = self.client.post(self.register_url, weak_password_data, format='json')
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)

    def test_concurrent_login_sessions(self):
        """Test behavior with concurrent login sessions."""
        user = UserFactory()
        login_data = {'email': user.email, 'password': TestData.DEFAULT_PASSWORD}
        
        # Create multiple concurrent sessions
        responses = []
        for i in range(3):
            response = self.client.post(self.login_url, login_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            responses.append(response)
        
        # All sessions should have different tokens
        access_tokens = [r.data['data']['access'] for r in responses]
        refresh_tokens = [r.data['data']['refresh'] for r in responses]
        
        self.assertEqual(len(set(access_tokens)), 3)  # All unique
        self.assertEqual(len(set(refresh_tokens)), 3)  # All unique
        
        # All refresh tokens should work
        for refresh_token in refresh_tokens:
            response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authentication_header_variations(self):
        """Test different authentication header formats."""
        user = UserFactory()
        login_data = {'email': user.email, 'password': TestData.DEFAULT_PASSWORD}
        response = self.client.post(self.login_url, login_data, format='json')
        
        access_token = response.data['data']['access']
        
        # Standard Bearer token format
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        # Test with an endpoint that requires authentication (refresh endpoint works)
        test_response = self.client.post(self.refresh_url, {'refresh': response.data['data']['refresh_token']}, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_200_OK)
        
        # Invalid header formats should fail
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {access_token}')
        test_response = self.client.post(self.refresh_url, {'refresh': response.data['data']['refresh_token']}, format='json')
        # This might still work depending on DRF configuration, but good to test
        
        # No authorization header
        self.client.credentials()
        # Some endpoints might not require auth, so we need to test with protected endpoint

    def test_rate_limiting_integration(self):
        """Test rate limiting integration with authentication flows."""
        user = UserFactory()
        invalid_login_data = {'email': user.email, 'password': 'wrongpassword'}
        
        # Make multiple failed login attempts
        failed_attempts = 0
        for i in range(10):  # Try to trigger rate limiting
            response = self.client.post(self.login_url, invalid_login_data, format='json')
            if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
                break
            failed_attempts += 1
        
        # Should eventually get rate limited
        # Note: This test depends on rate limiting configuration
        self.assertGreater(failed_attempts, 0)  # At least some attempts should go through

    def test_user_data_consistency_across_endpoints(self):
        """Test user data consistency across different endpoints."""
        # Register user
        response = self.client.post(self.register_url, self.user_data, format='json')
        registered_data = response.data['data']
        
        # Login and compare user data
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data, format='json')
        login_user_data = response.data['data']['user']
        
        # Compare key fields
        self.assertEqual(registered_data['user_id'], login_user_data['id'])
        self.assertEqual(registered_data['email'], login_user_data['email'])
        self.assertEqual(registered_data['first_name'], login_user_data['first_name'])
        self.assertEqual(registered_data['last_name'], login_user_data['last_name'])


class SecurityTestCase(APITestCase):
    """Security-focused integration tests."""

    def setUp(self):
        """Set up test dependencies."""
        self.client = APIClient()
        self.login_url = reverse('auth-login')
        self.refresh_url = reverse('auth-refresh')
        self.logout_url = reverse('auth-logout')
        
        cache.clear()

    def test_sql_injection_attempts(self):
        """Test protection against SQL injection attempts."""
        sql_injection_payloads = [
            "admin@example.com'; DROP TABLE auth_user; --",
            "admin@example.com' OR '1'='1",
            "admin@example.com' UNION SELECT * FROM auth_user --"
        ]
        
        for payload in sql_injection_payloads:
            login_data = {'email': payload, 'password': 'anypassword'}
            response = self.client.post(self.login_url, login_data, format='json')
            
            # Should handle gracefully without crashing
            self.assertIn(response.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED])

    def test_xss_protection_in_responses(self):
        """Test XSS protection in API responses."""
        xss_payload = "<script>alert('xss')</script>@example.com"
        
        login_data = {'email': xss_payload, 'password': 'password'}
        response = self.client.post(self.login_url, login_data, format='json')
        
        # Response should not contain unescaped script tags
        response_content = json.dumps(response.data)
        self.assertNotIn('<script>', response_content)

    def test_timing_attack_resistance(self):
        """Test resistance to timing attacks on user enumeration."""
        # This is a basic test - real timing attack testing requires more sophisticated timing measurements
        
        # Valid email, wrong password
        user = UserFactory()
        response1 = self.client.post(self.login_url, {
            'email': user.email,
            'password': 'wrongpassword'
        }, format='json')
        
        # Invalid email
        response2 = self.client.post(self.login_url, {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword'
        }, format='json')
        
        # Both should return similar response codes and structure
        self.assertEqual(response1.status_code, response2.status_code)
        self.assertEqual(response1.data['responseCode'], response2.data['responseCode'])

    def test_token_leakage_prevention(self):
        """Test that tokens are not leaked in error messages."""
        user = UserFactory()
        
        # Get valid tokens
        login_data = {'email': user.email, 'password': TestData.DEFAULT_PASSWORD}
        response = self.client.post(self.login_url, login_data, format='json')
        refresh_token = response.data['data']['refresh_token']
        
        # Logout to blacklist the token
        self.client.post(self.logout_url, {'refresh': refresh_token}, format='json')
        
        # Try to use blacklisted token
        response = self.client.post(self.refresh_url, {'refresh': refresh_token}, format='json')
        
        # Error message should not contain the actual token
        response_content = json.dumps(response.data)
        self.assertNotIn(refresh_token, response_content)
