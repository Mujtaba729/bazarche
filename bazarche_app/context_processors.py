from django.contrib.auth.models import User
from .models import VisitLog, MainCategory
from django.db.models import Sum

def site_stats(request):
    user_count = User.objects.count()
    total_visits = VisitLog.objects.aggregate(total=Sum('visit_count'))['total'] or 0
    return {"user_count": user_count, "total_visits": total_visits}

def main_categories(request):
    return {"main_categories": MainCategory.objects.all().order_by('order', 'name_fa')}