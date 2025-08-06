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

AFGHANISTAN_CITIES = [
    'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
    'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
    'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
    'پنجشیر'
]

class Command(BaseCommand):
    help = 'اضافه کردن داده‌های اولیه برای production (دسته‌بندی‌ها، شهرها و وضعیت محصولات)'

    def handle(self, *args, **options):
        self.stdout.write('شروع اضافه کردن داده‌های اولیه...')
        
        # اضافه کردن دسته‌بندی‌ها
        for name, icon in CATEGORY_ICON_MAP.items():
            category, created = Category.objects.get_or_create(
                name_fa=name,
                defaults={'icon': icon}
            )
            if created:
                self.stdout.write(f'دسته‌بندی "{name}" اضافه شد.')
            else:
                self.stdout.write(f'دسته‌بندی "{name}" قبلاً موجود است.')
        
        # اضافه کردن شهرها
        for city_name in AFGHANISTAN_CITIES:
            city, created = City.objects.get_or_create(name=city_name)
            if created:
                self.stdout.write(f'شهر "{city_name}" اضافه شد.')
            else:
                self.stdout.write(f'شهر "{city_name}" قبلاً موجود است.')
        
        self.stdout.write(
            self.style.SUCCESS('✅ داده‌های اولیه با موفقیت اضافه شدند!')
        ) 