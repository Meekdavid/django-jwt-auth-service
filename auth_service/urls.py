"""
URL configuration for auth_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache

# drf-yasg imports (backward compatibility)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# drf-spectacular imports (new documentation system)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

def healthz(_request):
    db_ok = True
    cache_ok = True
    try:
        connection.ensure_connection()
    except Exception:
        db_ok = False
    try:
        cache.set("healthz", "ok", 5)
        cache_ok = cache.get("healthz") == "ok"
    except Exception:
        cache_ok = False
    return JsonResponse({"status": "ok", "db": db_ok, "cache": cache_ok})

schema_view = get_schema_view(
    openapi.Info(
        title="Auth Service API",
        default_version="v1",
        description="User registration & JWT auth (PostgreSQL + Redis project)",
        contact=openapi.Contact(email="dev@billstation.example"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz", healthz),
    path("api/", include("accounts.urls")),
    
    # Legacy drf-yasg documentation (backward compatibility)
    path("docs.json", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    
    # New drf-spectacular documentation (recommended)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Alternative paths for easier access
    path("swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui-alt"),
    path("schema/", SpectacularAPIView.as_view(), name="schema-alt"),
]
