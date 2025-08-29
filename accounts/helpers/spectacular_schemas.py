from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, inline_serializer
from rest_framework import serializers
from typing import Dict, Any, Optional, Type, Union
from accounts.serializers import (
    RegisterRequestSerializer, RegisterSerializer,
    LoginSerializer, LogoutSerializer, RefreshTokenSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)

# Create inline serializers for response schemas
def create_response_serializer(data_serializer: Optional[Type[serializers.Serializer]] = None, description: str = "Success") -> Any:
    """Create a standardized response serializer"""
    # Use Any to avoid type checking issues with DRF spectacular's dynamic serializer creation
    fields: Dict[str, Any] = {
        'responseCode': serializers.CharField(default="00", help_text="Response code"),
        'responseDescription': serializers.CharField(default=description, help_text="Response description"),
    }
    
    if data_serializer:
        fields['data'] = data_serializer()
    
    return inline_serializer(
        name=f'{description.replace(" ", "")}Response',
        fields=fields
    )

# Enhanced schema decorators with comprehensive documentation
def register_user_spectacular_schema():
    return extend_schema(
        operation_id="auth_register",
        summary="🔐 Register New User",
        description="""
        **Create a new user account with comprehensive validation.**
        
        This endpoint allows new users to register by providing their full name, email address (which serves as the username), and a secure password.
        
        **Security Features:**
        - ✅ Email uniqueness validation
        - ✅ Password strength requirements  
        - ✅ Password confirmation matching
        - ✅ Automatic user profile creation
        - 🛡️ Rate limiting: 10 registrations per hour per IP
        
        **Rate Limiting:**
        - **Limit**: 10 registrations per hour per IP address
        - **Response**: HTTP 429 when limit exceeded
        """,
        request=RegisterRequestSerializer,
        responses={
            201: OpenApiResponse(
                response=create_response_serializer(RegisterSerializer, "User registered successfully"),
                description="✅ User Successfully Created",
                examples=[
                    OpenApiExample(
                        "Success Example",
                        value={
                            "responseCode": "00",
                            "responseDescription": "User registered successfully",
                            "data": {
                                "id": 1,
                                "email": "user@example.com",
                                "full_name": "John Doe",
                                "date_joined": "2025-08-28T19:30:00Z"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                response=inline_serializer(
                    name='RegisterErrorResponse',
                    fields={
                        'responseCode': serializers.CharField(default="07"),
                        'responseDescription': serializers.CharField(default="Invalid input data provided"),
                        'data': inline_serializer(
                            name='RegisterErrors',
                            fields={
                                'email': serializers.ListField(child=serializers.CharField()),
                                'password': serializers.ListField(child=serializers.CharField()),
                                'password2': serializers.ListField(child=serializers.CharField()),
                            }
                        )
                    }
                ),
                description="❌ Validation Error"
            ),
            429: OpenApiResponse(
                response=inline_serializer(
                    name='RateLimitResponse',
                    fields={
                        'responseCode': serializers.CharField(default="429"),
                        'responseDescription': serializers.CharField(default="Rate limit exceeded"),
                        'data': inline_serializer(
                            name='RateLimitError',
                            fields={
                                'detail': serializers.CharField(default="Request was throttled. Expected available in 3600 seconds.")
                            }
                        )
                    }
                ),
                description="🚫 Rate Limit Exceeded"
            ),
        },
        tags=["🔐 Authentication & Authorization"],
    )

# Simple placeholder functions for other endpoints (using existing drf-yasg schemas)
def login_user_spectacular_schema():
    return extend_schema(
        operation_id="auth_login",
        summary="🔑 User Login",
        description="Authenticate user credentials and obtain JWT access tokens.",
        request=LoginSerializer,
        tags=["🔐 Authentication & Authorization"],
    )

def refresh_token_spectacular_schema():
    return extend_schema(
        operation_id="auth_refresh",
        summary="🔄 Refresh JWT Token",
        description="Refresh JWT access token using a valid refresh token.",
        request=RefreshTokenSerializer,
        tags=["🔐 Authentication & Authorization"],
    )

def logout_user_spectacular_schema():
    return extend_schema(
        operation_id="auth_logout",
        summary="🚪 User Logout",
        description="Securely logout and invalidate refresh tokens.",
        request=LogoutSerializer,
        tags=["🔐 Authentication & Authorization"],
    )

def forgot_password_spectacular_schema():
    return extend_schema(
        operation_id="auth_forgot_password",
        summary="🔒 Forgot Password",
        description="Initiate password reset process using secure tokenization.",
        request=ForgotPasswordSerializer,
        tags=["🔐 Authentication & Authorization"],
    )

def reset_password_spectacular_schema():
    return extend_schema(
        operation_id="auth_reset_password",
        summary="🔄 Reset Password",
        description="Complete password reset using verification token.",
        request=ResetPasswordSerializer,
        tags=["🔐 Authentication & Authorization"],
    )

def protected_test_spectacular_schema():
    return extend_schema(
        operation_id="auth_protected_test",
        summary="🛡️ Protected Endpoint Test",
        description="Test endpoint to verify JWT authentication is working correctly.",
        tags=["🔐 Authentication & Authorization"],
    )
