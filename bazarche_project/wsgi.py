"""
WSGI config for bazarche_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Prefer production settings automatically on Railway
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('RAILWAY_PROJECT_ID'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings_railway')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')

application = get_wsgi_application()
