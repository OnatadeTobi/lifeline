from django.utils.deprecation import MiddlewareMixin

class RateLimitHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if hasattr(request, 'limited'):
            response['X-RateLimit-Limit'] = str(getattr(request, '_ratelimit_limit', 0))
            response['X-RateLimit-Remaining'] = str(getattr(request, '_ratelimit_remaining', 0))
            response['X-RateLimit-Reset'] = str(getattr(request, '_ratelimit_reset', 0))
        return response