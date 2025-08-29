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
    - Database connectivity (critical)
    - Redis connectivity (optional)
    - Basic system status
    
    Returns:
    - 200: Essential systems operational (database)
    - 503: Service unavailable (database failing)
    """
    logger.info("🏥 Health check requested")
    
    status = "healthy"
    checks = {}
    
    # Check database connectivity (critical)
    try:
        logger.info("🗄️ Testing database connection...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            checks["database"] = "connected"
            logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database health check failed: {e}")
        checks["database"] = "disconnected"
        status = "unhealthy"  # Database failure = unhealthy
    
    # Check Redis connectivity (optional)
    try:
        logger.info("💾 Testing cache connection...")
        cache.set("health_check", "ok", 10)
        redis_test = cache.get("health_check")
        if redis_test == "ok":
            checks["redis"] = "connected"
            logger.info("✅ Cache connection successful")
        else:
            checks["redis"] = "disconnected"
            # Don't mark as unhealthy - Redis is optional with dummy cache fallback
            logger.warning("⚠️ Redis not available, using fallback cache")
    except Exception as e:
        logger.warning(f"⚠️ Redis health check failed (using fallback): {e}")
        checks["redis"] = "disconnected"
        # Don't mark as unhealthy - Redis is optional
    
    # System info
    checks["status"] = status
    
    response_data = {
        "status": status,
        "checks": checks,
        "service": "Django JWT Auth Service",
        "version": "1.0.0"
    }
    
    status_code = 200 if status == "healthy" else 503
    logger.info(f"🏥 Health check result: {status} (HTTP {status_code})")
    return JsonResponse(response_data, status=status_code)
