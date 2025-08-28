from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils.text import slugify
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

User = get_user_model()

class RegisterRequestSerializer(serializers.ModelSerializer):
    # write_only so it never appears in responses
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)

    class Meta:
        model = User
        fields = ("full_name", "email", "password")

    def validate_email(self, value: str):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate_password(self, value: str):
        # use Django's validators (configurable via AUTH_PASSWORD_VALIDATORS)
        validate_password(value)
        return value

    def create(self, validated_data):
        # manager handles hashing when using create_user if you pass password
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "date_joined")
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "date_joined")

class LoginSerializer(TokenObtainPairSerializer):
    # just inherits behavior; swagger will show inputs
    pass

class RefreshTokenSerializer(TokenRefreshSerializer):
    # inherits behavior from TokenRefreshSerializer
    pass

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    def validate_email(self, value: str):
        email = value.strip().lower()
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise serializers.ValidationError(
                "No active user account found with this email address."
            )
        return email

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    confirm_password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    
    def validate_new_password(self, value: str):
        # Use Django's password validators
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': 'Password confirmation does not match.'
            })
        return attrs
