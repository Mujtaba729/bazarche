"""
Production settings for bazarche_project
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Import base settings but override DATABASES before import
import sys
sys.path.insert(0, str(BASE_DIR))

# Temporarily set DATABASES to SQLite before importing settings
os.environ['DJANGO_DB_ENGINE'] = 'sqlite3'

# Import base settings
from .settings import *

# Override database settings for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-jnbmyh*#%ux79z!^%n1$dhw^f3^k$-rzt&3=q*w@lq34)q62g+')

# Allow Railway domain
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.railway.app',
    '.render.com',
    '.herokuapp.com',
    '*',  # برای تست موقت
]



# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Add whitenoise middleware
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Security settings
SECURE_SSL_REDIRECT = False  # برای Railway موقتاً غیرفعال
SESSION_COOKIE_SECURE = False  # برای Railway موقتاً غیرفعال
CSRF_COOKIE_SECURE = False  # برای Railway موقتاً غیرفعال

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
} 