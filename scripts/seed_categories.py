#!/usr/bin/env python3
"""
Script to seed category data for Contabo server
"""
import os
import sys
import django

# Add project directory to Python path
project_path = '/var/www/bazarche_app'
sys.path.insert(0, project_path)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')

# Setup Django
django.setup()

from bazarche_app.models import Category

# Main categories
MAIN_CATEGORIES = [
    'وسایل نقلیه',
    'لوازم خانگی',
    'لوازم دیجیتال',
    'وسایل شخصی',
    'سرگرمی و فراغت',
    'تجهیزات و صنعتی',
    'املاک'
]

print("Creating categories...")

for i, name in enumerate(MAIN_CATEGORIES):
    if not Category.objects.filter(name_fa=name).exists():
        Category.objects.create(
            name_fa=name,
            name_en=name,  # You can add English names later
            order=i
        )
        print(f"Category '{name}' created.")
    else:
        print(f"Category '{name}' already exists.")

print("Categories seeding completed!") 