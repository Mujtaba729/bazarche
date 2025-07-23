from django.core.management.base import BaseCommand
from bazarche_app.models import Category

class Command(BaseCommand):
    help = 'Creates main categories with their icons'

    def handle(self, *args, **kwargs):
        # حذف همه دسته‌بندی‌های موجود
        Category.objects.all().delete()
        
        categories = [
            {
                'name_fa': 'وسایل نقلیه',
                'name_ps': 'موټرونه',
                'name_en': 'Vehicles',
                'icon': 'bi-car-front',
                'order': 1
            },
            {
                'name_fa': 'لوازم دیجیتال',
                'name_ps': 'ډیجیټل توکي',
                'name_en': 'Digital Devices',
                'icon': 'bi-laptop',
                'order': 2
            },
            {
                'name_fa': 'لوازم خانگی',
                'name_ps': 'کورنی توکي',
                'name_en': 'Home Appliances',
                'icon': 'bi-house',
                'order': 3
            },
            {
                'name_fa': 'وسایل شخصی',
                'name_ps': 'شخصي توکي',
                'name_en': 'Personal Items',
                'icon': 'bi-person',
                'order': 4
            },
            {
                'name_fa': 'سرگرمی و فراغت',
                'name_ps': 'تفریح او فراغت',
                'name_en': 'Entertainment & Leisure',
                'icon': 'bi-controller',
                'order': 5
            },
            {
                'name_fa': 'تجهیزات و صنعتی',
                'name_ps': 'صنعتي او تجهیزات',
                'name_en': 'Industrial & Equipment',
                'icon': 'bi-gear',
                'order': 6
            },
            {
                'name_fa': 'خدمات',
                'name_ps': 'خدمات',
                'name_en': 'Services',
                'icon': 'bi-briefcase',
                'order': 7
            },
            {
                'name_fa': 'املاک',
                'name_ps': 'املاک',
                'name_en': 'Real Estate',
                'icon': 'bi-building',
                'order': 8
            },
            {
                'name_fa': 'اجتماعی',
                'name_ps': 'ټولنیز',
                'name_en': 'Social',
                'icon': 'bi-people',
                'order': 9
            },
            {
                'name_fa': 'استخدام و کاریابی',
                'name_ps': 'استخدام او کاریابي',
                'name_en': 'Jobs & Employment',
                'icon': 'bi-person-badge',
                'order': 10
            }
        ]

        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name_fa=category_data['name_fa'],
                defaults=category_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created category "{category_data["name_fa"]}"')
                )
