from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle

from accounts.serializers import (
    RegisterRequestSerializer, RegisterSerializer,
    LoginSerializer, LogoutSerializer, RefreshTokenSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from auth_service.utils.response_utils import success_response, error_response
from auth_service.utils.password_reset_service import PasswordResetService
from auth_service.utils.throttles import LoginRateThrottle, PasswordResetRateThrottle, AuthCriticalRateThrottle

from accounts.helpers.openapi_auth_schemas import (
    register_user_schema, login_user_schema, logout_user_schema,
    refresh_token_schema, protected_test_schema, forgot_password_schema, reset_password_schema
)
from accounts.helpers.spectacular_schemas import (
    register_user_spectacular_schema, login_user_spectacular_schema, logout_user_spectacular_schema,
    refresh_token_spectacular_schema, protected_test_spectacular_schema, 
    forgot_password_spectacular_schema, reset_password_spectacular_schema
)

from rest_framework_simplejwt.tokens import RefreshToken

class AuthViewSet(ViewSet):
    permission_classes = [AllowAny]

    @register_user_spectacular_schema()  # New drf-spectacular
    @register_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="register", throttle_classes=[AuthCriticalRateThrottle])
    def register(self, request):
        ser = RegisterRequestSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)
        user = ser.save()
        out = RegisterSerializer(user).data
        return success_response(out, "User registered successfully", status=201)

    @login_user_spectacular_schema()  # New drf-spectacular
    @login_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="login", throttle_classes=[LoginRateThrottle, AnonRateThrottle])
    def login(self, request):
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            # TokenObtainPairSerializer returns 401 on bad creds
            return error_response("08", "Authentication failed", data=ser.errors, status=401)
        tokens = ser.validated_data  # {"access": "...", "refresh": "..."}
        return success_response(tokens, "User logged in successfully", status=200)

    @refresh_token_spectacular_schema()  # New drf-spectacular
    @refresh_token_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="refresh")
    def refresh(self, request):
        ser = RefreshTokenSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("09", "Invalid refresh token", data=ser.errors, status=401)
        tokens = ser.validated_data  # {"access": "...", "refresh": "..."}
        return success_response(tokens, "Token refreshed successfully", status=200)

    @logout_user_spectacular_schema()  # New drf-spectacular
    @logout_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="logout", permission_classes=[IsAuthenticated])
    def logout(self, request):
        ser = LogoutSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)

        # If you enabled blacklist in SIMPLE_JWT settings and added app to INSTALLED_APPS,
        # you can blacklist the refresh token here.
        try:
            token = RefreshToken(ser.validated_data["refresh"])
            token.blacklist()  # requires 'rest_framework_simplejwt.token_blacklist'
        except Exception:
            # If blacklist not configured, just return OK so client drops token.
            pass

        return success_response({"message": "Logged out"}, "User logged out successfully", status=200)

    @protected_test_spectacular_schema()  # New drf-spectacular
    @protected_test_schema()  # Legacy drf-yasg
    @action(methods=["get"], detail=False, url_path="protected-test", permission_classes=[IsAuthenticated])
    def protected_test(self, request):
        """
        Protected test endpoint that requires valid JWT access token
        """
        user_data = {
            "user_id": request.user.id,
            "email": request.user.email,
            "full_name": request.user.full_name,
            "message": "This endpoint requires a valid JWT access token!"
        }
        return success_response(user_data, "Protected endpoint accessed successfully", status=200)

    @forgot_password_spectacular_schema()  # New drf-spectacular
    @forgot_password_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="forgot-password", throttle_classes=[PasswordResetRateThrottle, AnonRateThrottle])
    def forgot_password(self, request):
        """
        Generate password reset token and store in Redis with 10-minute TTL
        """
        ser = ForgotPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)
        
        email = ser.validated_data["email"]
        
        try:
            # Initialize password reset service
            reset_service = PasswordResetService()
            
            # Generate secure token
            token = reset_service.generate_reset_token(email)
            
            # In development, return token in response
            # In production, this would trigger an email with the token
            response_data = {
                "message": "Password reset token generated successfully",
                "email": email
            }
            
            # Only include token in development environment
            from django.conf import settings
            if settings.DEBUG:
                response_data["token"] = token
                response_data["dev_note"] = "Token included for development. In production, this will be sent via email."
            else:
                response_data["production_note"] = "Password reset instructions have been sent to your email address."
            
            return success_response(response_data, "Password reset initiated successfully", status=200)
            
        except Exception as e:
            return error_response("10", "Failed to generate reset token", data={"detail": str(e)}, status=500)

    @reset_password_spectacular_schema()  # New drf-spectacular
    @reset_password_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="reset-password", throttle_classes=[AuthCriticalRateThrottle])
    def reset_password(self, request):
        """
        Verify token from Redis and reset user password
        """
        ser = ResetPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)
        
        token = ser.validated_data["token"]
        new_password = ser.validated_data["new_password"]
        
        try:
            # Initialize password reset service
            reset_service = PasswordResetService()
            
            # Verify and consume token
            user = reset_service.verify_and_consume_token(token)
            
            if not user:
                return error_response("11", "Invalid or expired token", 
                                    data={"detail": "The password reset token is invalid or has expired."}, 
                                    status=400)
            
            # Reset user password
            user.set_password(new_password)
            user.save()
            
            # Invalidate any remaining tokens for this user
            reset_service.invalidate_user_tokens(user.id)
            
            response_data = {
                "message": "Password reset successfully",
                "user_id": user.id,
                "email": user.email
            }
            
            return success_response(response_data, "Password reset completed successfully", status=200)
            
        except Exception as e:
            return error_response("12", "Failed to reset password", data={"detail": str(e)}, status=500)