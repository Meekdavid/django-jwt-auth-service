from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from accounts.serializers import (
    RegisterRequestSerializer, RegisterSerializer,
    LoginSerializer, LogoutSerializer, RefreshTokenSerializer,
    ForgotPasswordSerializer, ResetPasswordSerializer
)

# Envelope helper for pretty responses
def wrap_response(body_schema_or_serializer, code="00", description="Success"):
    # Accept DRF serializer instance OR drf_yasg openapi.Schema
    if hasattr(body_schema_or_serializer, "fields") or hasattr(body_schema_or_serializer, "get_fields"):
        data_schema = body_schema_or_serializer
    else:
        data_schema = body_schema_or_serializer

    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "responseCode": openapi.Schema(type=openapi.TYPE_STRING, example=code),
            "responseDescription": openapi.Schema(type=openapi.TYPE_STRING, example=description),
            "data": data_schema if isinstance(data_schema, openapi.Schema) else data_schema
        }
    )

def register_user_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🔐 Register New User",
        operation_description="""
        **Create a new user account with comprehensive validation.**
        
        This endpoint allows new users to register by providing their full name, email address (which serves as the username), and a secure password. The password must be confirmed to ensure accuracy.
        
        **Security Features:**
        - ✅ Email uniqueness validation
        - ✅ Password strength requirements
        - ✅ Password confirmation matching
        - ✅ Automatic user profile creation
        - ✅ Immediate account activation
        - 🛡️ Rate limiting: 10 registrations per hour per IP
        
        **Rate Limiting:**
        - **Limit**: 10 registrations per hour per IP address
        - **Response**: HTTP 429 when limit exceeded
        - **Reset**: Limits reset every hour
        
        **Password Requirements:**
        - Minimum 8 characters
        - Must contain at least one letter and one number
        - Cannot be too common or entirely numeric
        """,
        security=[],  # public endpoint
        request_body=RegisterRequestSerializer,
        responses={
            201: openapi.Response(
                "✅ User Successfully Created", 
                wrap_response(RegisterSerializer(), code="00", description="User registered successfully")
            ),
            400: openapi.Response(
                "❌ Validation Error", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["User with this email already exists."]
                        ),
                        "password": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This password is too short. It must contain at least 8 characters."]
                        ),
                        "password2": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["Password fields didn't match."]
                        )
                    }
                ), code="07", description="Invalid input data provided")
            ),
            429: openapi.Response(
                "🚫 Rate Limit Exceeded",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Request was throttled. Expected available in 3600 seconds."
                        )
                    }
                ), code="429", description="Too many registration attempts - rate limit exceeded")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def login_user_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🔑 User Login",
        operation_description="""
        **Authenticate user credentials and obtain JWT access tokens.**
        
        This endpoint authenticates a user using their email and password, returning JWT access and refresh tokens for secure API access.
        
        **Authentication Flow:**
        - 🔍 Validates email and password credentials
        - 🎯 Returns JWT access token (1-hour validity)
        - 🔄 Returns JWT refresh token (7-day validity)
        - 🛡️ Enables access to protected endpoints
        
        **Token Usage:**
        - **Access Token**: Include in Authorization header as `Bearer <access_token>`
        - **Refresh Token**: Use with /refresh endpoint to get new access tokens
        
        **Security Features:**
        - ✅ Token rotation enabled
        - ✅ Automatic token blacklisting on refresh
        - ✅ Configurable token lifetimes
        - ✅ Secure JWT signing
        - 🛡️ Rate limiting: 5 login attempts per minute per IP/email
        
        **Rate Limiting:**
        - **Limit**: 5 login attempts per minute per IP address and email
        - **Response**: HTTP 429 when limit exceeded
        - **Reset**: Limits reset every minute
        - **Purpose**: Prevents brute force attacks
        """,
        security=[],  # public endpoint
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                "✅ Login Successful", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4NzY1NDMwLCJpYXQiOjE2OTg3NjE4MzAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxfQ.example_signature",
                            description="JWT Access Token (valid for 1 hour)"
                        ),
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTM2NjYzMCwiaWF0IjoxNjk4NzYxODMwLCJqdGkiOiIwOTg3NjU0MzIxIiwidXNlcl9pZCI6MX0.example_refresh_signature",
                            description="JWT Refresh Token (valid for 7 days)"
                        ),
                    }
                ), code="00", description="User logged in successfully")
            ),
            401: openapi.Response(
                "❌ Authentication Failed", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "non_field_errors": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["No active account found with the given credentials"]
                        )
                    }
                ), code="08", description="Invalid email or password provided")
            ),
            429: openapi.Response(
                "🚫 Rate Limit Exceeded",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Request was throttled. Expected available in 45 seconds."
                        )
                    }
                ), code="429", description="Too many login attempts - rate limit exceeded")
            ),
            400: openapi.Response(
                "❌ Validation Error",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This field is required."]
                        ),
                        "password": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This field is required."]
                        )
                    }
                ), code="07", description="Missing or invalid request data")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def refresh_token_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🔄 Refresh JWT Token",
        operation_description="""
        **Refresh JWT access token using a valid refresh token.**
        
        When your access token expires (after 1 hour), use this endpoint to obtain a new access token without requiring the user to log in again.
        
        **Token Refresh Flow:**
        - 📥 Provide your current refresh token
        - 🔄 Receive a new access token (1-hour validity)
        - 🔄 Receive a new refresh token (7-day validity) if rotation is enabled
        - 🗑️ Old refresh token is automatically blacklisted
        
        **Security Features:**
        - ✅ Automatic token rotation (old tokens invalidated)
        - ✅ Refresh token blacklisting
        - ✅ Extended refresh token lifetime (7 days)
        - ✅ Prevents token replay attacks
        
        **Usage Notes:**
        - Refresh tokens are single-use when rotation is enabled
        - Store the new refresh token for future use
        - Access tokens should be used for API requests
        """,
        security=[],  # refresh token is passed in request body, not header
        request_body=RefreshTokenSerializer,
        responses={
            200: openapi.Response(
                "✅ Token Refreshed Successfully", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "access": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk4NzY5MDMwLCJpYXQiOjE2OTg3NjU0MzAsImp0aSI6ImFiY2RlZmdoaWoiLCJ1c2VyX2lkIjoxfQ.new_access_signature",
                            description="New JWT Access Token (valid for 1 hour)"
                        ),
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY5OTM3MDIzMCwiaWF0IjoxNjk4NzY1NDMwLCJqdGkiOiJrbG1ub3BxcnN0IiwidXNlcl9pZCI6MX0.new_refresh_signature",
                            description="New JWT Refresh Token (valid for 7 days)"
                        ),
                    }
                ), code="00", description="Token refreshed successfully")
            ),
            401: openapi.Response(
                "❌ Invalid Refresh Token", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Token is invalid or expired"
                        ),
                        "code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="token_not_valid"
                        )
                    }
                ), code="09", description="Refresh token is invalid, expired, or blacklisted")
            ),
            400: openapi.Response(
                "❌ Validation Error",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This field is required."]
                        )
                    }
                ), code="07", description="Missing or malformed refresh token")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def logout_user_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🚪 User Logout",
        operation_description="""
        **Securely logout and invalidate refresh tokens.**
        
        This endpoint allows authenticated users to logout by blacklisting their refresh token, ensuring it cannot be used for future token refreshes.
        
        **Logout Process:**
        - 🔐 Requires valid JWT access token in Authorization header
        - 🗑️ Blacklists the provided refresh token
        - ✅ Prevents further use of the refresh token
        - 🛡️ Enhances security by invalidating session tokens
        
        **Security Features:**
        - ✅ Token blacklisting (prevents token reuse)
        - ✅ Graceful degradation (works even without blacklist)
        - ✅ Immediate token invalidation
        - ✅ Session cleanup
        
        **Client Implementation:**
        - Clear stored tokens from client storage
        - Redirect user to login page
        - Remove Authorization headers from future requests
        """,
        security=[{
            "Bearer": [],
            "description": "JWT Access Token required in Authorization header"
        }],
        request_body=LogoutSerializer,
        responses={
            200: openapi.Response(
                "✅ Logout Successful", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Logged out",
                            description="Confirmation message"
                        )
                    }
                ), code="00", description="User logged out successfully")
            ),
            401: openapi.Response(
                "❌ Unauthorized", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Given token not valid for any token type"
                        ),
                        "code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="token_not_valid"
                        )
                    }
                ), code="08", description="Access token missing, invalid, or expired")
            ),
            400: openapi.Response(
                "❌ Validation Error",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This field is required."]
                        )
                    }
                ), code="07", description="Missing or invalid refresh token in request body")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def protected_test_schema():
    return swagger_auto_schema(
        method="get",
        operation_summary="🛡️ Protected Endpoint Test",
        operation_description="""
        **Test endpoint to verify JWT authentication is working correctly.**
        
        This endpoint demonstrates how protected routes work and can be used to test JWT token validation.
        
        **Access Requirements:**
        - 🔐 Valid JWT access token required
        - ⏰ Token must not be expired (1-hour lifetime)
        - ✅ Token must be properly formatted
        - 🎯 User account must be active
        
        **Response Data:**
        - Returns authenticated user information
        - Confirms token is valid and not expired
        - Demonstrates successful API access
        
        **Usage Example:**
        ```
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
        ```
        
        **Security Features:**
        - ✅ JWT signature verification
        - ✅ Token expiration checking
        - ✅ User authentication validation
        - ✅ Automatic error handling for invalid tokens
        """,
        security=[{
            "Bearer": [],
            "description": "JWT Access Token required in Authorization header"
        }],
        responses={
            200: openapi.Response(
                "✅ Access Granted", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, 
                            example=1,
                            description="Authenticated user's ID"
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="testuser@example.com",
                            description="Authenticated user's email address"
                        ),
                        "full_name": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Test User",
                            description="Authenticated user's full name"
                        ),
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="This endpoint requires a valid JWT access token!",
                            description="Confirmation message"
                        )
                    }
                ), code="00", description="Protected endpoint accessed successfully")
            ),
            401: openapi.Response(
                "❌ Unauthorized", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Given token not valid for any token type"
                        ),
                        "code": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="token_not_valid"
                        )
                    }
                ), code="08", description="Access token missing, invalid, or expired")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def forgot_password_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🔒 Forgot Password",
        operation_description="""
        **Initiate password reset process using secure tokenization.**
        
        This endpoint generates a secure password reset token for users who have forgotten their password. The token is stored in Redis with a 10-minute expiration for enhanced security.
        
        **Password Reset Flow:**
        - 📧 User provides their registered email address
        - 🔐 System generates a secure token using `secrets.token_urlsafe()`
        - ⏰ Token is stored in Redis with 10-minute TTL (Time To Live)
        - 📨 In production: Token sent via email (not exposed in response)
        - 🔧 In development: Token included in response for testing
        
        **Security Features:**
        - ✅ Secure token generation (32-byte URL-safe tokens)
        - ✅ Automatic token expiration (10 minutes)
        - ✅ Redis-based storage for scalability
        - ✅ Email validation (only active users)
        - ✅ No exposure of user existence to unauthorized users
        - 🛡️ Rate limiting: 3 reset attempts per minute per IP/email
        
        **Rate Limiting:**
        - **Limit**: 3 password reset attempts per minute per IP and email
        - **Response**: HTTP 429 when limit exceeded
        - **Reset**: Limits reset every minute
        - **Purpose**: Prevents abuse of password reset functionality
        
        **Environment Behavior:**
        - **Development**: Token returned in response for testing
        - **Production**: Email notification sent (token not exposed)
        """,
        security=[],  # public endpoint
        request_body=ForgotPasswordSerializer,
        responses={
            200: openapi.Response(
                "✅ Reset Token Generated", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Password reset token generated successfully",
                            description="Confirmation message"
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="user@example.com",
                            description="Email address where reset instructions are sent"
                        ),
                        "token": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
                            description="[DEV ONLY] Secure reset token (hidden in production)"
                        ),
                        "dev_note": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Token included for development. In production, this will be sent via email.",
                            description="[DEV ONLY] Development environment notice"
                        ),
                        "production_note": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Password reset instructions have been sent to your email address.",
                            description="[PROD ONLY] Production environment message"
                        )
                    }
                ), code="00", description="Password reset initiated successfully")
            ),
            400: openapi.Response(
                "❌ Validation Error", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "email": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["No active user account found with this email address."]
                        )
                    }
                ), code="07", description="Invalid email or user not found")
            ),
            500: openapi.Response(
                "❌ Server Error",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Redis connection failed"
                        )
                    }
                ), code="10", description="Failed to generate reset token")
            ),
            429: openapi.Response(
                "🚫 Rate Limit Exceeded",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Request was throttled. Expected available in 120 seconds."
                        )
                    }
                ), code="429", description="Too many password reset attempts - rate limit exceeded")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )

def reset_password_schema():
    return swagger_auto_schema(
        method="post",
        operation_summary="🔄 Reset Password",
        operation_description="""
        **Complete password reset using verification token.**
        
        This endpoint verifies the password reset token and updates the user's password. The token is consumed (deleted) upon successful verification to prevent reuse.
        
        **Password Reset Completion:**
        - 🔍 Verifies token exists and hasn't expired
        - 👤 Retrieves associated user account
        - 🔒 Updates user password with secure hashing
        - 🗑️ Consumes (deletes) the reset token
        - 🧹 Invalidates any other reset tokens for the user
        
        **Security Features:**
        - ✅ Token verification and consumption (single-use)
        - ✅ Automatic token cleanup after use
        - ✅ Password strength validation
        - ✅ Password confirmation matching
        - ✅ User account status verification
        - ✅ Secure password hashing (Django's built-in)
        - 🛡️ Rate limiting: 10 reset operations per hour per IP
        
        **Rate Limiting:**
        - **Limit**: 10 password reset operations per hour per IP
        - **Response**: HTTP 429 when limit exceeded
        - **Reset**: Limits reset every hour
        - **Purpose**: Prevents automated abuse
        
        **Token Lifecycle:**
        - **Generation**: 10-minute TTL in Redis
        - **Verification**: Token must exist and not be expired
        - **Consumption**: Token deleted after successful use
        - **Cleanup**: All user tokens invalidated after reset
        
        **Error Scenarios:**
        - Token expired (>10 minutes old)
        - Token already used (consumed)
        - Token doesn't exist
        - Password validation failure
        """,
        security=[],  # public endpoint (token-based verification)
        request_body=ResetPasswordSerializer,
        responses={
            200: openapi.Response(
                "✅ Password Reset Successful", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="Password reset successfully",
                            description="Success confirmation message"
                        ),
                        "user_id": openapi.Schema(
                            type=openapi.TYPE_INTEGER, 
                            example=1,
                            description="ID of the user whose password was reset"
                        ),
                        "email": openapi.Schema(
                            type=openapi.TYPE_STRING, 
                            example="user@example.com",
                            description="Email of the user whose password was reset"
                        )
                    }
                ), code="00", description="Password reset completed successfully")
            ),
            400: openapi.Response(
                "❌ Invalid Request", 
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="The password reset token is invalid or has expired."
                        ),
                        "token": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This field is required."]
                        ),
                        "new_password": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["This password is too short. It must contain at least 8 characters."]
                        ),
                        "confirm_password": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING),
                            example=["Password confirmation does not match."]
                        )
                    }
                ), code="11", description="Invalid or expired token, or validation errors")
            ),
            500: openapi.Response(
                "❌ Server Error",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Database connection failed"
                        )
                    }
                ), code="12", description="Failed to reset password")
            ),
            429: openapi.Response(
                "🚫 Rate Limit Exceeded",
                wrap_response(openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            example="Request was throttled. Expected available in 2400 seconds."
                        )
                    }
                ), code="429", description="Too many password reset operations - rate limit exceeded")
            ),
        },
        tags=["🔐 Authentication & Authorization"]
    )
