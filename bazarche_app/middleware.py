from django.utils import translation

class CustomLocaleMiddleware:
    """
    Middleware to activate language from session on each request.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang_code = request.session.get('django_language')
        if lang_code:
            translation.activate(lang_code)
            request.LANGUAGE_CODE = lang_code
        response = self.get_response(request)
        translation.deactivate()
        return response
