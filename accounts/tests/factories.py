"""
Test factories for creating test data using factory_boy.
These factories help create consistent test data for all authentication tests.
"""
import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from faker import Faker

User = get_user_model()
fake = Faker()


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances for testing."""
    
    class Meta:
        model = User
        django_get_or_create = ('email',)
    
    email = factory.Sequence(lambda n: f"testuser{n}@example.com")
    full_name = factory.LazyAttribute(lambda obj: fake.name())
    is_active = True
    is_staff = False
    is_superuser = False

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for the user."""
        if not create:
            return
        
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class AdminUserFactory(UserFactory):
    """Factory for creating admin User instances."""
    
    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f"admin{n}@example.com")


class InactiveUserFactory(UserFactory):
    """Factory for creating inactive User instances."""
    
    is_active = False
    email = factory.Sequence(lambda n: f"inactive{n}@example.com")


# Common test data constants
class TestData:
    """Common test data used across multiple test files."""
    
    VALID_PASSWORD = "SecurePass123!"
    DEFAULT_PASSWORD = "SecurePass123!"  # Add this for backwards compatibility
    WEAK_PASSWORD = "123"
    INVALID_EMAIL = "invalid-email"
    
    VALID_USER_DATA = {
        "email": "newuser@example.com",
        "password": VALID_PASSWORD,
        "password2": VALID_PASSWORD,
        "full_name": "New Test User"
    }
    
    INVALID_USER_DATA = {
        "email": INVALID_EMAIL,
        "password": WEAK_PASSWORD,
        "password2": "different_password",
        "full_name": ""
    }
    
    LOGIN_DATA = {
        "email": "testuser@example.com",
        "password": VALID_PASSWORD
    }
    
    INVALID_LOGIN_DATA = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
