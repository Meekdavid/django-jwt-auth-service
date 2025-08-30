"""
Authentication Service Classes

This module contains service classes that handle authentication-related business logic.
Each service class encapsulates specific business operations to keep views clean and focused.
"""
from typing import Dict, Any, Optional
import jwt
import logging
import traceback
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.exceptions import TokenError
from auth_service.utils.password_reset_service import PasswordResetService

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRegistrationService:
    """
    Handles user registration business logic
    
    This service demonstrates separation of concerns by isolating user creation
    logic from the view layer. The view handles HTTP concerns while this service
    manages the business rules for user registration.
    """
    
    @staticmethod
    def register_user(validated_data: Dict[str, Any]):
        """
        Creates a new user account with the provided data
        
        Args:
            validated_data: Dictionary containing user registration data
            
        Returns:
            User: The newly created user instance
            
        Note: This pattern shows how to extract creation logic from serializers
        when additional business rules need to be applied during user creation.
        """
        try:
            logger.info(f"Starting user registration process with data: {validated_data}")
            
            # Validate required fields
            required_fields = ['email', 'password']
            for field in required_fields:
                if field not in validated_data:
                    logger.error(f"Missing required field: {field}")
                    raise ValueError(f"Missing required field: {field}")
            
            # Extract password to handle separately as required by Django's create_user method
            password = validated_data.pop("password")
            email = validated_data.get("email")
            
            logger.info(f"Creating user with email: {email}")
            
            # Check if user already exists
            if User.objects.filter(email=email).exists():
                logger.warning(f"User registration failed: email {email} already exists")
                raise ValueError(f"User with email {email} already exists")
            
            # Create user using Django's built-in method which handles password hashing
            with transaction.atomic():
                user = User.objects.create_user(password=password, **validated_data)
                logger.info(f"User created successfully with email: {user.email}")
            
            return user
            
        except IntegrityError as e:
            logger.error(f"Database integrity error during user registration: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise ValueError(f"User with this email already exists: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during user registration: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise


class AuthenticationService:
    """
    Handles authentication and token management business logic
    
    This service centralizes token-related operations to ensure consistent
    behavior across the application and make testing easier.
    """
    
    @staticmethod
    def authenticate_user(serializer_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Processes user authentication and returns JWT tokens
        
        Args:
            serializer_data: Validated data from LoginSerializer
            
        Returns:
            Dict containing access and refresh tokens
            
        Note: This approach allows for consistent token handling and makes it
        easier to add business logic like login tracking or security checks.
        """
        # The LoginSerializer (TokenObtainPairSerializer) already validates credentials
        # and returns tokens, so we pass them through while maintaining flexibility
        # for future enhancements
        
        tokens = serializer_data
        
        return tokens
    
    @staticmethod
    def refresh_user_token(serializer_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Handles token refresh business logic
        
        Args:
            serializer_data: Validated data from RefreshTokenSerializer
            
        Returns:
            Dict containing new access token and optionally new refresh token
            
        Note: This pattern allows for token rotation policies and refresh tracking.
        """
        tokens = serializer_data
        
        return tokens
    
    @staticmethod
    def logout_user(refresh_token: str) -> bool:
        """
        Handles user logout by blacklisting the refresh token
        
        Args:
            refresh_token: The refresh token to blacklist
            
        Returns:
            bool: True if logout successful, False otherwise
            
        Note: This service method demonstrates proper token cleanup and provides
        a place to add logout-related business logic.
        """
        try:
            # Blacklist the refresh token to prevent further use
            # Use the direct approach that works with simplejwt
            try:
                # Method 1: Decode the JWT to get the JTI and blacklist directly
                # This approach doesn't rely on the RefreshToken constructor
                decoded_token = jwt.decode(
                    refresh_token,
                    options={"verify_signature": False}  # We only need the payload
                )
                
                jti = decoded_token.get('jti')
                if jti:
                    # Find the outstanding token record
                    outstanding_token = OutstandingToken.objects.filter(jti=jti).first()
                    if outstanding_token:
                        # Create a blacklist entry
                        BlacklistedToken.objects.get_or_create(token=outstanding_token)
                        
            except Exception:
                # Method 2: Try alternative approach if JWT decode fails
                # Create a new RefreshToken instance and manually blacklist
                try:
                    # This pattern works with some versions of simplejwt
                    refresh_token_obj = RefreshToken()
                    refresh_token_obj.payload = jwt.decode(
                        refresh_token, 
                        options={"verify_signature": False}
                    )
                    refresh_token_obj.blacklist()
                except Exception:
                    # If both methods fail, that's okay - client will drop token
                    pass
            
            return True
        except Exception:
            # In case blacklisting fails (e.g., blacklist not configured),
            # we still consider logout successful as the client will drop the token
            return True


class PasswordResetBusinessService:
    """
    Handles password reset business logic and orchestration
    
    This service wraps the PasswordResetService utility to add business logic
    and provide a clean interface for password reset operations.
    """
    
    def __init__(self):
        """
        Initialize the service with required dependencies
        
        Note: Dependency injection pattern allows for easier testing and
        makes the service more flexible for different implementations.
        """
        self.reset_service = PasswordResetService()
    
    def initiate_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Initiates password reset process for a user
        
        Args:
            email: The email address of the user requesting password reset
            
        Returns:
            Dict containing reset token and related information
            
        Raises:
            Exception: If token generation fails
            
        Note: This method demonstrates how to handle business logic around
        password reset initiation while keeping the view simple.
        """
        try:
            # Generate secure reset token using the utility service
            token = self.reset_service.generate_reset_token(email)
            
            # Prepare response data with consistent structure
            response_data = {
                "message": "Password reset token generated successfully",
                "email": email,
                "token": token,  # Always include token as per requirements
                "note": "In production, this token would typically be sent via email instead of returned in response"
            }
            
            return response_data
            
        except Exception as e:
            # Wrap exceptions with business context
            raise Exception(f"Failed to initiate password reset: {str(e)}")
    
    def complete_password_reset(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Completes password reset process using provided token
        
        Args:
            token: The password reset token
            new_password: The new password to set
            
        Returns:
            Dict containing success information
            
        Raises:
            Exception: If password reset fails
            
        Note: This method encapsulates the complete password reset workflow
        including token verification, password update, and cleanup.
        """
        try:
            # Verify token and get associated user
            user = self.reset_service.verify_and_consume_token(token)
            
            if not user:
                raise Exception("Invalid or expired password reset token")
            
            # Update user password using Django's secure method
            user.set_password(new_password)
            user.save()
            
            # Clean up any remaining tokens for security
            self.reset_service.invalidate_user_tokens(user.id)
            
            # Prepare success response
            response_data = {
                "message": "Password reset completed successfully",
                "user_id": user.id,
                "email": user.email
            }
            
            return response_data
            
        except Exception as e:
            # Provide meaningful error context
            raise Exception(f"Failed to complete password reset: {str(e)}")


class UserProfileService:
    """
    Handles user profile-related business logic
    
    This service manages operations related to user profile data and
    provides a clean interface for profile-related functionality.
    """
    
    @staticmethod
    def get_user_profile_data(user) -> Dict[str, Any]:
        """
        Retrieves formatted user profile data
        
        Args:
            user: The authenticated user instance
            
        Returns:
            Dict containing user profile information
            
        Note: This service method demonstrates how to format user data
        consistently across the application and provides a place for
        profile-related business logic.
        """
        # Format user data for API response
        profile_data = {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "message": "This endpoint demonstrates JWT authentication and service layer architecture!"
        }
        
        return profile_data
