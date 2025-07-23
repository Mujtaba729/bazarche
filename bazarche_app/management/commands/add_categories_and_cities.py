from bazarche_app.models import Category, City
from django.core.management.base import BaseCommand

CATEGORY_ICON_MAP = {
    'وسایل نقلیه': 'bi-car',
    'لوازم دیجیتال': 'bi-phone',
    'لوازم خانگی': 'bi-house',
    'وسایل شخصی': 'bi-person',
    'سرگرمی و فراغت': 'bi-controller',
    'تجهیزات و صنعتی': 'bi-tools',
    'املاک': 'bi-building',
}

class Command(BaseCommand):
    help = 'افزودن دسته‌بندی‌ها با آیکون و شهرهای افغانستان به دیتابیس'

    def handle(self, *args, **options):
        for name, icon in CATEGORY_ICON_MAP.items():
            Category.objects.update_or_create(name_fa=name, defaults={'icon': icon})
        provinces = [
            'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
            'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
            'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
            'پنجشیر'
        ]
        for name in provinces:
            City.objects.get_or_create(name=name)
        self.stdout.write(self.style.SUCCESS('دسته‌بندی‌ها با آیکون و شهرها با موفقیت اضافه شدند.'))