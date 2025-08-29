#!/usr/bin/env python
"""
Rate Limiting Integration Test Script for Auth Service

This script demonstrates and tests the rate limiting functionality
on login and forgot-password endpoints.

Usage:
    python scripts/test_rate_limiting.py

Requirements:
    - Django server running on http://127.0.0.1:8000
    - requests library (pip install requests)
"""

try:
    import requests  # type: ignore
except ImportError:
    print("❌ Error: 'requests' library not found.")
    print("Please install it with: pip install requests")
    import sys
    sys.exit(1)

import time
import json
import sys
import os
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
FORGOT_PASSWORD_URL = f"{BASE_URL}/api/auth/forgot-password/"
REGISTER_URL = f"{BASE_URL}/api/auth/register/"

def print_response(response: requests.Response, test_name: str) -> None:
    """Print formatted response information"""
    print(f"\n{'='*50}")
    print(f"TEST: {test_name}")
    print(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Status: {response.status_code}")
    
    # Check for rate limiting headers
    if 'X-RateLimit-Remaining' in response.headers:
        print(f"Rate Limit Remaining: {response.headers['X-RateLimit-Remaining']}")
    if 'Retry-After' in response.headers:
        print(f"Retry After: {response.headers['Retry-After']} seconds")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except json.JSONDecodeError:
        print(f"Response Text: {response.text}")
    print(f"{'='*50}")

def test_login_rate_limiting() -> None:
    """Test login endpoint rate limiting (5 attempts per minute)"""
    print(f"\n🔐 TESTING LOGIN RATE LIMITING (5/min)")
    
    login_data = {
        "email": "test@example.com",
        "password": "wrongpassword123"
    }
    
    for i in range(7):  # Try 7 times (should fail after 5)
        print(f"\nAttempt {i+1}/7")
        try:
            response = requests.post(LOGIN_URL, json=login_data, timeout=10)
            print_response(response, f"Login Attempt {i+1}")
            
            if response.status_code == 429:
                print("🚫 RATE LIMIT TRIGGERED!")
                break
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break
        
        time.sleep(1)  # Small delay between requests

def test_forgot_password_rate_limiting() -> None:
    """Test forgot-password endpoint rate limiting (3 attempts per minute)"""
    print(f"\n🔒 TESTING FORGOT PASSWORD RATE LIMITING (3/min)")
    
    forgot_data = {
        "email": "test@example.com"
    }
    
    for i in range(5):  # Try 5 times (should fail after 3)
        print(f"\nAttempt {i+1}/5")
        try:
            response = requests.post(FORGOT_PASSWORD_URL, json=forgot_data, timeout=10)
            print_response(response, f"Forgot Password Attempt {i+1}")
            
            if response.status_code == 429:
                print("🚫 RATE LIMIT TRIGGERED!")
                break
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break
        
        time.sleep(1)  # Small delay between requests

def test_registration_rate_limiting() -> None:
    """Test registration endpoint rate limiting (10 attempts per hour)"""
    print(f"\n📝 TESTING REGISTRATION RATE LIMITING (10/hour)")
    
    # We'll only test a few attempts to avoid creating many test users
    for i in range(3):
        register_data = {
            "email": f"ratelimitest{i}@example.com",
            "password": "testpassword123",
            "password2": "testpassword123",
            "full_name": f"Rate Limit Test User {i}"
        }
        
        print(f"\nAttempt {i+1}/3")
        try:
            response = requests.post(REGISTER_URL, json=register_data, timeout=10)
            print_response(response, f"Registration Attempt {i+1}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break
        
        time.sleep(1)

def check_server_connectivity() -> bool:
    """Check if the Django server is running and accessible"""
    try:
        response = requests.get(f"{BASE_URL}/swagger/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is accessible")
            return True
        else:
            print(f"⚠️ Server responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure Django server is running on port 8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server request timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking server connectivity: {e}")
        return False

def main() -> None:
    """Run all rate limiting tests"""
    print("🛡️ AUTH SERVICE RATE LIMITING TEST")
    print("="*60)
    print("This script tests the rate limiting functionality")
    print("of the authentication endpoints.")
    print("="*60)
    
    # Test server connectivity
    if not check_server_connectivity():
        sys.exit(1)
    
    try:
        # Run tests
        test_login_rate_limiting()
        
        print("\n" + "⏱️"*20 + " WAITING 5 SECONDS " + "⏱️"*20)
        time.sleep(5)  # Wait between test suites
        
        test_forgot_password_rate_limiting()
        
        print("\n" + "⏱️"*20 + " WAITING 5 SECONDS " + "⏱️"*20)
        time.sleep(5)  # Wait between test suites
        
        test_registration_rate_limiting()
        
        print(f"\n🎉 RATE LIMITING TESTS COMPLETED!")
        print("Check the responses above to see rate limiting in action.")
        print("429 status codes indicate successful rate limiting.")
        
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
