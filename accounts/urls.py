from django.urls import path
from rest_framework.routers import DefaultRouter
from accounts.views import AuthViewSet

router = DefaultRouter()
router.register("auth", AuthViewSet, basename="auth")

urlpatterns = router.urls
