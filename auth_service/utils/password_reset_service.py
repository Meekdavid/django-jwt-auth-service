import secrets
import redis
from django.conf import settings
from django.contrib.auth import get_user_model
from typing import Optional

User = get_user_model()

class PasswordResetService:
    """
    Service for managing password reset tokens using Redis.
    Tokens have a 10-minute TTL and are automatically cleaned up.
    """
    
    def __init__(self):
        # Connect to Redis using Django cache configuration
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.token_prefix = "password_reset:"
        self.token_ttl = 600  # 10 minutes in seconds
    
    def generate_reset_token(self, email: str) -> str:
        """
        Generate a secure password reset token for the given email.
        
        Args:
            email: User's email address
            
        Returns:
            Secure token string
            
        Raises:
            User.DoesNotExist: If user with email doesn't exist
        """
        try:
            user = User.objects.get(email__iexact=email.strip().lower(), is_active=True)
        except User.DoesNotExist:
            raise User.DoesNotExist("No active user found with this email address")
        
        # Generate secure token using secrets module
        token = secrets.token_urlsafe(32)
        
        # Store token -> user_id mapping in Redis with TTL
        redis_key = f"{self.token_prefix}{token}"
        self.redis_client.setex(
            name=redis_key,
            time=self.token_ttl,
            value=str(user.id)
        )
        
        return token
    
    def verify_and_consume_token(self, token: str) -> Optional[User]:
        """
        Verify password reset token and return associated user.
        Token is consumed (deleted) upon successful verification.
        
        Args:
            token: Password reset token
            
        Returns:
            User object if token is valid, None otherwise
        """
        redis_key = f"{self.token_prefix}{token}"
        
        # Get user ID from Redis
        user_id = self.redis_client.get(redis_key)
        
        if not user_id:
            # Token doesn't exist or has expired
            return None
        
        try:
            # Get user object
            user = User.objects.get(id=int(user_id.decode()), is_active=True)
            
            # Delete token from Redis (consume it)
            self.redis_client.delete(redis_key)
            
            return user
            
        except (User.DoesNotExist, ValueError):
            # User doesn't exist or invalid user_id
            # Clean up invalid token
            self.redis_client.delete(redis_key)
            return None
    
    def invalidate_user_tokens(self, user_id: int) -> int:
        """
        Invalidate all password reset tokens for a specific user.
        Useful when user changes password through other means.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of tokens invalidated
        """
        pattern = f"{self.token_prefix}*"
        deleted_count = 0
        
        # Find all tokens and check if they belong to this user
        for key in self.redis_client.scan_iter(match=pattern):
            stored_user_id = self.redis_client.get(key)
            if stored_user_id and int(stored_user_id.decode()) == user_id:
                self.redis_client.delete(key)
                deleted_count += 1
        
        return deleted_count
    
    def get_token_ttl(self, token: str) -> Optional[int]:
        """
        Get remaining TTL for a token in seconds.
        
        Args:
            token: Password reset token
            
        Returns:
            TTL in seconds, None if token doesn't exist
        """
        redis_key = f"{self.token_prefix}{token}"
        ttl = self.redis_client.ttl(redis_key)
        return ttl if ttl > 0 else None
