#!/usr/bin/env python3
"""
Script to seed initial data for Contabo server
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

from bazarche_app.models import City, Tag

AFGHANISTAN_PROVINCES = [
    'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
    'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
    'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
    'پنجشیر', 'نیمروز'
]

print("Creating Afghan cities...")

for i, name in enumerate(AFGHANISTAN_PROVINCES):
    if not City.objects.filter(name_fa=name).exists():
        City.objects.create(name_fa=name, name_en=name, order=i)
        print(f"✅ City '{name}' created.")
    else:
        print(f"ℹ️ City '{name}' already exists.")

print("\nCreating tags...")

for name in ['نو', 'دست دوم']:
    if not Tag.objects.filter(name_fa=name).exists():
        Tag.objects.create(name_fa=name, name_en=name)
        print(f"✅ Tag '{name}' created.")
    else:
        print(f"ℹ️ Tag '{name}' already exists.")

print("\n🎉 Initial data seeding completed!")
