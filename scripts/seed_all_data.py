#!/usr/bin/env python3
"""
Comprehensive script to seed all initial data for Contabo server
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

from bazarche_app.models import City, Tag, Category

# All provinces of Afghanistan (34 provinces)
AFGHANISTAN_PROVINCES = [
    'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
    'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
    'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
    'پنجشیر', 'نیمروز', 'غور', 'دایکندی'
]

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

# Product tags
PRODUCT_TAGS = ['نو', 'دست دوم']

print("=== Starting data seeding ===")

# Create cities
print("\n--- Creating cities ---")
for i, name in enumerate(AFGHANISTAN_PROVINCES):
    if not City.objects.filter(name=name).exists():
        City.objects.create(name=name, order=i)
        print(f"✅ City '{name}' created.")
    else:
        print(f"ℹ️ City '{name}' already exists.")

# Create categories
print("\n--- Creating categories ---")
for i, name in enumerate(MAIN_CATEGORIES):
    if not Category.objects.filter(name_fa=name).exists():
        Category.objects.create(
            name_fa=name,
            name_en=name,
            order=i
        )
        print(f"✅ Category '{name}' created.")
    else:
        print(f"ℹ️ Category '{name}' already exists.")

# Create tags
print("\n--- Creating tags ---")
for name in PRODUCT_TAGS:
    if not Tag.objects.filter(name_fa=name).exists():
        Tag.objects.create(name_fa=name, name_en=name)
        print(f"✅ Tag '{name}' created.")
    else:
        print(f"ℹ️ Tag '{name}' already exists.")

print("\n=== Data seeding completed successfully! ===") 