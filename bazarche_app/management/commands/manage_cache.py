from django.core.management.base import BaseCommand
from django.core.cache import cache
from bazarche_app.cache_manager import CacheManager
from bazarche_app.models import Product, Category, MainCategory
from django.db.models import Count

class Command(BaseCommand):
    help = 'مدیریت کش Redis'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['clear', 'warm', 'stats', 'products', 'categories'],
            help='عملیات مورد نظر'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='اجبار در عملیات'
        )

    def handle(self, *args, **options):
        action = options['action']
        force = options['force']

        if action == 'clear':
            self.clear_cache(force)
        elif action == 'warm':
            self.warm_cache(force)
        elif action == 'stats':
            self.show_stats()
        elif action == 'products':
            self.cache_products(force)
        elif action == 'categories':
            self.cache_categories(force)

    def clear_cache(self, force=False):
        """پاک کردن تمام کش"""
        if not force:
            confirm = input('آیا مطمئن هستید که می‌خواهید تمام کش را پاک کنید؟ (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('عملیات لغو شد.'))
                return

        CacheManager.clear_all_cache()
        self.stdout.write(
            self.style.SUCCESS('تمام کش با موفقیت پاک شد.')
        )

    def warm_cache(self, force=False):
        """گرم کردن کش با داده‌های پرکاربرد"""
        self.stdout.write('در حال گرم کردن کش...')
        
        # کش کردن محصولات
        self.cache_products(force)
        
        # کش کردن دسته‌بندی‌ها
        self.cache_categories(force)
        
        # کش کردن آمار
        total_products = Product.objects.filter(is_approved=True).count()
        CacheManager.cache_product_count(total_products)
        
        self.stdout.write(
            self.style.SUCCESS('کش با موفقیت گرم شد.')
        )

    def cache_products(self, force=False):
        """کش کردن محصولات"""
        self.stdout.write('در حال کش کردن محصولات...')
        
        # محصولات تایید شده
        products = Product.objects.filter(is_approved=True)
        
        # کش کردن لیست اصلی محصولات
        CacheManager.cache_products(products)
        
        # کش کردن محصولات بر اساس دسته‌بندی
        categories = Category.objects.all()
        for category in categories:
            category_products = products.filter(category=category)
            if category_products.exists():
                CacheManager.cache_products(
                    products=category_products,
                    category_id=category.id
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'{products.count()} محصول کش شد.')
        )

    def cache_categories(self, force=False):
        """کش کردن دسته‌بندی‌ها"""
        self.stdout.write('در حال کش کردن دسته‌بندی‌ها...')
        
        # دسته‌بندی‌های اصلی
        main_categories = MainCategory.objects.all()
        CacheManager.cache_main_categories(main_categories)
        
        # تمام دسته‌بندی‌ها
        categories = Category.objects.all()
        CacheManager.cache_categories(categories)
        
        self.stdout.write(
            self.style.SUCCESS(f'{categories.count()} دسته‌بندی کش شد.')
        )

    def show_stats(self):
        """نمایش آمار کش"""
        stats = CacheManager.get_cache_stats()
        
        self.stdout.write('=== آمار کش ===')
        self.stdout.write(f'وضعیت: {stats["status"]}')
        self.stdout.write(f'Backend: {stats["backend"]}')
        self.stdout.write(f'آدرس: {stats["location"]}')
        
        # تست اتصال
        try:
            cache.set('test_key', 'test_value', 10)
            test_value = cache.get('test_key')
            if test_value == 'test_value':
                self.stdout.write(
                    self.style.SUCCESS('اتصال به Redis موفق است.')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('مشکل در اتصال به Redis.')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطا در اتصال به Redis: {str(e)}')
            ) 