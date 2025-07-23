from django.core.management.base import BaseCommand
from bazarche_app.models import City

AFGHAN_CITIES = [
    "کابل", "هرات", "مزار شریف", "قندهار", "جلال‌آباد", "کندز", "پل‌خمری", "فیض‌آباد", "بامیان", "غزنی",
    "تخار", "پروان", "لوگر", "بدخشان", "بغلان", "بلخ", "دایکندی", "فراه", "فاریاب", "غور", "هلمند",
    "جوزجان", "کاپیسا", "خوست", "کنر", "لغمان", "نورستان", "نیمروز", "پکتیا", "پکتیکا", "پنجشیر",
    "سرپل", "سمنگان", "وردک", "زابل", "ارزگان"
]

class Command(BaseCommand):
    help = 'افزودن لیست کامل شهرهای افغانستان به مدل City'

    def handle(self, *args, **options):
        added = 0
        for order, name in enumerate(AFGHAN_CITIES, start=1):
            city, created = City.objects.get_or_create(name=name, defaults={'order': order})
            if created:
                added += 1
        self.stdout.write(self.style.SUCCESS(f'{added} شهر جدید اضافه شد.')) 