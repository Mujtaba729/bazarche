#!/usr/bin/env python
"""
Comprehensive script to seed all initial data for Railway deployment
"""
import os
import django

# Set Django settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
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

# Product status options
PRODUCT_STATUS = ['فعال', 'غیرفعال', 'فروخته شده', 'رزرو شده']

print("=== Starting data seeding ===")

# Create cities
print("\n--- Creating cities ---")
for i, name in enumerate(AFGHANISTAN_PROVINCES):
    if not City.objects.filter(name=name).exists():
        City.objects.create(name=name, order=i)
        print(f"City '{name}' created.")
    else:
        print(f"City '{name}' already exists.")

# Create categories
print("\n--- Creating categories ---")
for i, name in enumerate(MAIN_CATEGORIES):
    if not Category.objects.filter(name_fa=name).exists():
        Category.objects.create(
            name_fa=name,
            name_en=name,
            order=i,
            is_active=True
        )
        print(f"Category '{name}' created.")
    else:
        print(f"Category '{name}' already exists.")

# Create tags
print("\n--- Creating tags ---")
for name in PRODUCT_TAGS:
    if not Tag.objects.filter(name_fa=name).exists():
        Tag.objects.create(name_fa=name)
        print(f"Tag '{name}' created.")
    else:
        print(f"Tag '{name}' already exists.")

print("\n=== Data seeding completed successfully! ===") 