from django.shortcuts import render
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from typing import Dict, Any
import logging
import traceback

from accounts.serializers import (
    RegisterRequestSerializer, RegisterSerializer,
    LoginSerializer, LogoutSerializer, RefreshTokenSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)
from accounts.services.auth_services import (
    UserRegistrationService, AuthenticationService, 
    PasswordResetBusinessService, UserProfileService
)
from auth_service.utils.response_utils import success_response, error_response
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

# Configure logger
logger = logging.getLogger(__name__)

class AuthViewSet(ViewSet):
    permission_classes = [AllowAny]

    @register_user_spectacular_schema()  # New drf-spectacular
    @register_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="register", throttle_classes=[AuthCriticalRateThrottle])
    def register(self, request):
        """
        Handles user registration by validating input and delegating to service layer
        
        This endpoint demonstrates clean separation of concerns where the view
        handles HTTP protocol concerns while business logic resides in service classes.
        """
        try:
            logger.info(f"Registration attempt for request data: {request.data}")
            
            # Step 1: Validate the incoming request data using serializer
            ser = RegisterRequestSerializer(data=request.data)
            if not ser.is_valid():
                logger.warning(f"Registration validation failed: {ser.errors}")
                return error_response("07", "Invalid input", data=ser.errors, status=400)
            
            # Step 2: Delegate user creation to the service layer
            validated_data = ser.validated_data
            if not isinstance(validated_data, dict):
                logger.error("Registration: validated_data is not a dictionary")
                return error_response("07", "Invalid data format", status=400)
            
            logger.info(f"Calling UserRegistrationService.register_user with data: {validated_data}")
            user = UserRegistrationService.register_user(validated_data)
            
            # Step 3: Format the response using output serializer
            user_data = RegisterSerializer(user).data
            logger.info(f"User registered successfully: {user.email}")
            
            return success_response(user_data, "User registered successfully", status=201)
            
        except Exception as e:
            logger.error(f"Registration failed with exception: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return error_response("10", "Registration failed", data={"detail": str(e), "traceback": traceback.format_exc()}, status=500)

    @login_user_spectacular_schema()  # New drf-spectacular
    @login_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="login", throttle_classes=[LoginRateThrottle, AnonRateThrottle])
    def login(self, request):
        """
        Authenticates user credentials and returns JWT tokens
        
        This endpoint shows how to validate credentials through serializers
        and delegate token generation to the service layer for clean architecture.
        """
        # Step 1: Validate credentials using the login serializer
        ser = LoginSerializer(data=request.data)
        if not ser.is_valid():
            # TokenObtainPairSerializer returns 401 on bad credentials
            return error_response("08", "Authentication failed", data=ser.errors, status=401)
        
        # Step 2: Process authentication through service layer
        validated_data = ser.validated_data
        if not isinstance(validated_data, dict):
            return error_response("08", "Invalid data format", status=400)
            
        tokens = AuthenticationService.authenticate_user(validated_data)
        
        return success_response(tokens, "User logged in successfully", status=200)

    @refresh_token_spectacular_schema()  # New drf-spectacular
    @refresh_token_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="refresh")
    def refresh(self, request):
        """
        Refreshes JWT access token using valid refresh token
        
        This endpoint demonstrates token refresh workflow using service layer
        to handle the business logic while keeping the view focused on HTTP concerns.
        """
        # Step 1: Validate the refresh token
        ser = RefreshTokenSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("09", "Invalid refresh token", data=ser.errors, status=401)
        
        # Step 2: Generate new tokens through service layer
        validated_data = ser.validated_data
        if not isinstance(validated_data, dict):
            return error_response("09", "Invalid data format", status=400)
            
        tokens = AuthenticationService.refresh_user_token(validated_data)
        
        return success_response(tokens, "Token refreshed successfully", status=200)

    @logout_user_spectacular_schema()  # New drf-spectacular
    @logout_user_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="logout", permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        Handles user logout by blacklisting the refresh token
        
        This endpoint shows how to perform secure logout by delegating
        token management to the service layer while handling validation in the view.
        """
        # Step 1: Validate the refresh token format
        ser = LogoutSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)

        # Step 2: Extract refresh token and delegate logout to service
        # Type-safe access to validated data after successful validation
        validated_data = ser.validated_data
        if not isinstance(validated_data, dict):
            return error_response("07", "Invalid data format", status=400)
            
        refresh_token = validated_data.get("refresh")
        if not refresh_token:
            return error_response("07", "Refresh token is required", status=400)
        
        # Step 3: Perform logout through service layer
        logout_successful = AuthenticationService.logout_user(refresh_token)
        
        if logout_successful:
            return success_response({"message": "Logged out"}, "User logged out successfully", status=200)
        else:
            return error_response("10", "Logout failed", status=500)

    @protected_test_spectacular_schema()  # New drf-spectacular
    @protected_test_schema()  # Legacy drf-yasg
    @action(methods=["get"], detail=False, url_path="protected-test", permission_classes=[IsAuthenticated])
    def protected_test(self, request):
        """
        Demonstrates protected endpoint access with JWT authentication
        
        This endpoint shows how to use service layer to format user data
        while keeping the view simple and focused on request/response handling.
        """
        # Delegate user data formatting to service layer
        user_data = UserProfileService.get_user_profile_data(request.user)
        
        return success_response(user_data, "Protected endpoint accessed successfully", status=200)

    @forgot_password_spectacular_schema()  # New drf-spectacular
    @forgot_password_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="forgot-password", throttle_classes=[PasswordResetRateThrottle, AnonRateThrottle])
    def forgot_password(self, request):
        """
        Initiates password reset process by generating secure token
        
        This endpoint demonstrates how to delegate business logic to service layer
        while keeping validation and HTTP concerns in the view layer.
        """
        # Step 1: Validate the email input
        ser = ForgotPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)
        
        # Step 2: Extract validated email
        # Type-safe access to validated data after successful validation
        validated_data = ser.validated_data
        if not isinstance(validated_data, dict):
            return error_response("07", "Invalid data format", status=400)
            
        email = validated_data.get("email")
        if not email:
            return error_response("07", "Email is required", status=400)
        
        try:
            # Step 3: Delegate password reset initiation to service layer
            reset_service = PasswordResetBusinessService()
            response_data = reset_service.initiate_password_reset(email)
            
            return success_response(response_data, "Password reset initiated successfully", status=200)
            
        except Exception as e:
            return error_response("10", "Failed to generate reset token", data={"detail": str(e)}, status=500)

    @reset_password_spectacular_schema()  # New drf-spectacular
    @reset_password_schema()  # Legacy drf-yasg
    @action(methods=["post"], detail=False, url_path="reset-password", throttle_classes=[AuthCriticalRateThrottle])
    def reset_password(self, request):
        """
        Completes password reset using token verification
        
        This endpoint shows how to handle password reset completion by
        validating input and delegating the business logic to service layer.
        """
        # Step 1: Validate the reset request data
        ser = ResetPasswordSerializer(data=request.data)
        if not ser.is_valid():
            return error_response("07", "Invalid input", data=ser.errors, status=400)
        
        # Step 2: Extract validated data
        # Type-safe access to validated data after successful validation
        validated_data = ser.validated_data
        if not isinstance(validated_data, dict):
            return error_response("07", "Invalid data format", status=400)
            
        token = validated_data.get("token")
        new_password = validated_data.get("new_password")
        
        if not token or not new_password:
            return error_response("07", "Token and new password are required", status=400)
        
        try:
            # Step 3: Delegate password reset completion to service layer
            reset_service = PasswordResetBusinessService()
            response_data = reset_service.complete_password_reset(token, new_password)
            
            return success_response(response_data, "Password reset completed successfully", status=200)
            
        except Exception as e:
            return error_response("12", "Failed to reset password", data={"detail": str(e)}, status=500)