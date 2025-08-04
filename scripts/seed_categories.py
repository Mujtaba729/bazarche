#!/usr/bin/env python
"""
Script to seed category data for Railway deployment
"""
import os
import django

# Set Django settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
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
            order=i,
            is_active=True
        )
        print(f"Category '{name}' created.")
    else:
        print(f"Category '{name}' already exists.")

print("Categories seeding completed!") 