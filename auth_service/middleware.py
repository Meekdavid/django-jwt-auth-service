import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class ErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log detailed error information for 500 errors in production
    """
    
    def process_exception(self, request, exception):
        """
        Log detailed exception information when a 500 error occurs
        """
        error_details = {
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
            'GET': dict(request.GET),
            'POST': dict(request.POST) if request.method == 'POST' else {},
            'headers': dict(request.headers),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
        }
        
        logger.error(f"500 ERROR DETAILS: {error_details}")
        
        # Don't return a response - let Django handle it normally
        return None
    
    def process_response(self, request, response):
        """
        Log information about responses, especially 500s
        """
        if response.status_code >= 500:
            logger.error(f"500 RESPONSE: {request.path} -> {response.status_code}")
            logger.error(f"Response content: {response.content[:500]}")
        elif response.status_code >= 400:
            logger.warning(f"4XX RESPONSE: {request.path} -> {response.status_code}")
        
        return response
