#!/usr/bin/env python
"""
Script to create superuser for Railway deployment
"""
import os
import django

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings_railway')
django.setup()

from django.contrib.auth import get_user_model
from django.core.management import execute_from_command_line

User = get_user_model()

# Check if superuser already exists
if not User.objects.filter(is_superuser=True).exists():
    print("Creating superuser...")
    # Create superuser
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
    )
    print("Superuser created successfully!")
else:
    print("Superuser already exists!") 