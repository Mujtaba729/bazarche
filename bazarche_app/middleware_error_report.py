import traceback
from django.utils.deprecation import MiddlewareMixin
from .models import ErrorReport

class ErrorReportMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        try:
            user = request.user if request.user.is_authenticated else None
            stack_trace = traceback.format_exc()
            ErrorReport.objects.create(
                path=request.path,
                method=request.method,
                user=user,
                message=str(exception),
                stack_trace=stack_trace
            )
        except Exception:
            # Avoid infinite loop if error occurs in logging
            pass
        return None
