from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
import hashlib

class EmailRateThrottle(AnonRateThrottle):
    """
    Rate limit based on email address for authentication-related endpoints.
    Useful for preventing brute force attacks on specific email accounts.
    """
    scope = 'email'
    
    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            # For authenticated users, use their email
            ident = request.user.email
        else:
            # For anonymous users, try to get email from request data
            email = None
            if hasattr(request, 'data') and isinstance(request.data, dict):
                email = request.data.get('email')
            elif hasattr(request, 'POST'):
                email = request.POST.get('email')
            
            if not email:
                # Fallback to IP-based throttling if no email provided
                return super().get_cache_key(request, view)
            
            ident = email.lower().strip()
        
        # Create a hash of the email to avoid storing emails in cache keys
        ident_hash = hashlib.md5(ident.encode('utf-8')).hexdigest()
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident_hash
        }

class LoginRateThrottle(EmailRateThrottle):
    """
    Specific rate limiting for login attempts.
    Combines IP and email-based throttling for maximum security.
    """
    scope = 'login'

class PasswordResetRateThrottle(EmailRateThrottle):
    """
    Specific rate limiting for password reset attempts.
    Prevents abuse of password reset functionality.
    """
    scope = 'password_reset'

class AuthCriticalRateThrottle(AnonRateThrottle):
    """
    Rate limiting for critical authentication operations.
    Applied to sensitive endpoints like account creation, password changes.
    """
    scope = 'auth_critical'

class CombinedRateThrottle:
    """
    Utility class to combine multiple throttling strategies.
    Checks all throttles and returns 429 if any limit is exceeded.
    """
    
    def __init__(self, throttle_classes):
        self.throttle_classes = throttle_classes
        self.throttles = []
    
    def __call__(self):
        """
        Returns a function that can be used as a throttle class.
        """
        throttle_classes = self.throttle_classes
        
        class Combined(AnonRateThrottle):
            def __init__(self):
                super().__init__()
                self.throttles = [cls() for cls in throttle_classes]
            
            def allow_request(self, request, view):
                """
                Check all throttles. If any throttle denies the request, deny overall.
                """
                for throttle in self.throttles:
                    if not throttle.allow_request(request, view):
                        # Store the throttle that caused the denial for wait time calculation
                        self._denied_throttle = throttle
                        return False
                return True
            
            def wait(self):
                """
                Return the wait time from the throttle that denied the request.
                """
                if hasattr(self, '_denied_throttle'):
                    return self._denied_throttle.wait()
                return None
        
        return Combined

# Pre-configured combined throttles for common use cases
LoginThrottles = CombinedRateThrottle([
    LoginRateThrottle,
    AnonRateThrottle,
])()

PasswordResetThrottles = CombinedRateThrottle([
    PasswordResetRateThrottle,
    AnonRateThrottle,
])()

AuthCriticalThrottles = CombinedRateThrottle([
    AuthCriticalRateThrottle,
    AnonRateThrottle,
])()
