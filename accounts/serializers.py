from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()

class RegisterRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration request validation
    
    This serializer demonstrates input validation patterns while keeping
    business logic separate from data validation concerns.
    """
    # write_only ensures password never appears in API responses
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("full_name", "email", "password")

    def validate_email(self, value: str):
        """
        Validates email format and uniqueness
        
        This method shows how to implement field-level validation
        while keeping the actual user creation logic in service classes.
        """
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_password(self, value: str):
        """
        Validates password strength using Django's built-in validators
        
        This demonstrates how to leverage Django's password validation
        system for consistent security policies across the application.
        """
        # Use Django's validators (configurable via AUTH_PASSWORD_VALIDATORS)
        validate_password(value)
        return value

    # Note: Removed create() method - business logic moved to service layer
    # This keeps serializers focused on validation rather than business operations

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration response formatting
    
    This output serializer demonstrates clean data presentation
    without exposing sensitive information like passwords.
    """
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "date_joined")
    
class UserSerializer(serializers.ModelSerializer):
    """
    General user data serializer for profile information
    
    This serializer provides a consistent format for user data
    across different endpoints while maintaining security.
    """
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "date_joined")

class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for user authentication
    
    This inherits from TokenObtainPairSerializer to leverage
    built-in JWT token generation while allowing for customization.
    """
    # Inherits all validation and token generation logic
    # Custom business logic is handled in the service layer
    pass

class RefreshTokenSerializer(TokenRefreshSerializer):
    """
    Serializer for JWT token refresh operations
    
    This demonstrates the pattern of extending DRF's built-in serializers
    while keeping additional business logic in service classes.
    """
    # Inherits token refresh validation and generation logic
    pass

class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout request validation
    
    This serializer validates the refresh token format while
    the actual token blacklisting logic resides in the service layer.
    """
    refresh = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset request validation
    
    This validates the email input and user existence while keeping
    the token generation and email sending logic in service classes.
    """
    email = serializers.EmailField()
    
    def validate_email(self, value: str):
        """
        Validates email exists and belongs to an active user
        
        This validation ensures we only process reset requests
        for valid, active user accounts.
        """
        email = value.strip().lower()
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise serializers.ValidationError(
                "No active user account found with this email address."
            )
        return email

class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for password reset completion validation
    
    This handles input validation for password reset while keeping
    the token verification and password update logic in service classes.
    """
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    
    def validate_new_password(self, value: str):
        """
        Validates new password strength
        
        This ensures the new password meets security requirements
        before attempting the reset operation.
        """
        # Use Django's password validators for consistency
        validate_password(value)
        return value
    
    def validate(self, attrs):
        """
        Cross-field validation for password confirmation
        
        This method demonstrates how to validate that password
        fields match before processing the reset request.
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Password confirmation does not match.'
            })
        return attrs
