import time
from django.core.cache import cache
from django.http import HttpResponse

class RateLimitMiddleware:
    """
    Simple rate limiting middleware that limits requests per IP address.
    Limits to 60 requests per minute by default.
    """
    RATE_LIMIT = 60
    TIME_WINDOW = 60  # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exempt healthcheck paths from rate limiting
        if request.path.startswith('/health') or request.path.startswith('/app/health'):
            return self.get_response(request)

        ip = self.get_client_ip(request)
        if not ip:
            return self.get_response(request)

        cache_key = f"rl:{ip}"
        request_times = cache.get(cache_key, [])

        now = time.time()
        # Remove timestamps older than TIME_WINDOW
        request_times = [t for t in request_times if now - t < self.TIME_WINDOW]

        if len(request_times) >= self.RATE_LIMIT:
            return HttpResponse("تعداد درخواست‌ها بیش از حد مجاز است. لطفا بعدا تلاش کنید.", status=429)

        request_times.append(now)
        cache.set(cache_key, request_times, timeout=self.TIME_WINDOW)

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
