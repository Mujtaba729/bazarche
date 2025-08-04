import os
import django
import sys

# تنظیم محیط Django
import os
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
django.setup()

from bazarche_app.models import City, Tag

AFGHANISTAN_PROVINCES = [
    'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
    'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
    'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
    'پنجشیر', 'نیمروز', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب', 'پنجشیر', 'کاپیسا', 'لوگر', 'وردک'
]

for i, name in enumerate(AFGHANISTAN_PROVINCES):
    if not City.objects.filter(name=name).exists():
        City.objects.create(name=name, order=i)
        print(f"City '{name}' created.")
    else:
        print(f"City '{name}' already exists.")

for name in ['نو', 'دست دوم']:
    if not Tag.objects.filter(name_fa=name).exists():
        Tag.objects.create(name_fa=name)
        print(f"Tag '{name}' created.")
    else:
        print(f"Tag '{name}' already exists.")
