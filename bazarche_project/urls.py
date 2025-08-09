"""
URL configuration for bazarche_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.views.static import serve as django_serve
from django.views.generic import RedirectView
from django.templatetags.static import static
import os
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bazarche_app.views import landing, health

urlpatterns = [
    path('', landing, name='landing'),
    path('health/', health, name='root_health'),
    # استانداردهای عمومی در روت دامنه
    path('robots.txt', lambda request: __import__('bazarche_app.views', fromlist=['robots']).views.robots(request), name='robots_root'),
    path('sitemap.xml', lambda request: __import__('bazarche_app.views', fromlist=['sitemap']).views.sitemap(request), name='sitemap_root'),
    path('favicon.ico', RedirectView.as_view(url=static('favicon.ico'), permanent=True)),
    path('apple-touch-icon.png', RedirectView.as_view(url=static('apple-touch-icon.png'), permanent=True)),
    # ریدایرکت مسیرهای رایج بدون /app
    path('about', RedirectView.as_view(url='/app/about/', permanent=True)),
    path('contact', RedirectView.as_view(url='/app/contact/', permanent=True)),
    path('terms', RedirectView.as_view(url='/app/terms/', permanent=True)),
    path('privacy', RedirectView.as_view(url='/app/privacy/', permanent=True)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('app/', include(('bazarche_app.urls', 'bazarche_app'), namespace='app')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Temporary media serving in production (Railway) until external storage is configured
if not settings.DEBUG and os.environ.get('SERVE_MEDIA', '0') == '1':
    urlpatterns += [
        path('media/<path:path>', django_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
