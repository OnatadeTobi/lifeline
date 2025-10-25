from django.http import JsonResponse
import logging

logger = logging.getLogger('ratelimit')

# Create your views here.
def ratelimit_error(request, exception):
    logger.warning(
        f"Rate limit exceeded for {request.method} {request.path} "
        f"from IP {request.META.get('REMOTE_ADDR')} "
        f"User: {request.user if request.user.is_authenticated else 'Anonymous'}"
    )
    
    return JsonResponse({
        'error': 'Rate limit exceeded',
        'detail': 'Please try again later'
    }, status=429)