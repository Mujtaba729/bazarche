from django.contrib.auth.models import User
from .models import VisitLog, MainCategory, Advertisement
from django.db.models import Sum
from django.utils import timezone

def site_stats(request):
    user_count = User.objects.count()
    total_visits = VisitLog.objects.aggregate(total=Sum('visit_count'))['total'] or 0
    return {"user_count": user_count, "total_visits": total_visits}

def main_categories(request):
    return {"main_categories": MainCategory.objects.all().order_by('order', 'name_fa')}

def search_query(request):
    """Always provide search_query to all templates"""
    return {"search_query": request.GET.get('q', '')}

def sidebar_advertisements(request):
    """Provide sidebar advertisements to all templates"""
    sidebar_ads = Advertisement.objects.filter(
        location='sidebar',
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('display_order', '-created_at')[:3]
    return {"sidebar_advertisements": sidebar_ads}