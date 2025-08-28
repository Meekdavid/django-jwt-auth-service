from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.core.cache import cache
import redis
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """
    Health check endpoint for deployment monitoring.
    
    Checks:
    - Database connectivity
    - Redis connectivity
    - Basic system status
    
    Returns:
    - 200: All systems operational
    - 503: Service unavailable (dependencies failing)
    """
    status = "healthy"
    checks = {}
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        checks["database"] = "disconnected"
        status = "unhealthy"
    
    # Check Redis connectivity
    try:
        cache.set("health_check", "ok", 10)
        redis_test = cache.get("health_check")
        if redis_test == "ok":
            checks["redis"] = "connected"
        else:
            checks["redis"] = "disconnected"
            status = "unhealthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        checks["redis"] = "disconnected"
        status = "unhealthy"
    
    # System info
    checks["status"] = status
    
    response_data = {
        "status": status,
        "checks": checks,
        "service": "Django JWT Auth Service",
        "version": "1.0.0"
    }
    
    status_code = 200 if status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)
