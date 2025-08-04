"""
Production settings for bazarche_project
"""
import os
from .settings import *

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

# Database configuration for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Add Railway environment variables
import os
if os.environ.get('RAILWAY_ENVIRONMENT'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

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