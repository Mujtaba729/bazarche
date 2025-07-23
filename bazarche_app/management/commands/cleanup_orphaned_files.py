from django.core.management.base import BaseCommand
from django.conf import settings
from bazarche_app.models import ProductImage, UserProfile
import os
import shutil

class Command(BaseCommand):
    help = 'تمیز کردن فایل‌های بدون صاحب (عکس‌های محصولات و پروفایل‌ها)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='نمایش فایل‌هایی که حذف می‌شوند بدون حذف کردن',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('حالت نمایش - هیچ فایلی حذف نمی‌شود'))
        
        # تمیز کردن عکس‌های محصولات
        self.cleanup_product_images(dry_run)
        
        # تمیز کردن عکس‌های پروفایل
        self.cleanup_profile_images(dry_run)
        
        # تمیز کردن پوشه‌های خالی
        self.cleanup_empty_directories(dry_run)
        
        self.stdout.write(self.style.SUCCESS('تمیز کردن تمام شد!'))

    def cleanup_product_images(self, dry_run):
        """تمیز کردن عکس‌های محصولات"""
        self.stdout.write('=== تمیز کردن عکس‌های محصولات ===')
        
        # دریافت همه عکس‌های موجود در دیتابیس
        db_images = set()
        for product_image in ProductImage.objects.all():
            if product_image.image:
                db_images.add(product_image.image.name)
        
        self.stdout.write(f'تعداد عکس‌های موجود در دیتابیس: {len(db_images)}')
        
        # دریافت همه فایل‌های موجود در پوشه
        file_images = set()
        product_images_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
        
        if os.path.exists(product_images_dir):
            for root, dirs, files in os.walk(product_images_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        relative_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                        file_images.add(relative_path)
        
        self.stdout.write(f'تعداد فایل‌های موجود در پوشه: {len(file_images)}')
        
        # پیدا کردن فایل‌های بدون صاحب
        orphaned_files = file_images - db_images
        
        if not orphaned_files:
            self.stdout.write('هیچ فایل بدون صاحبی پیدا نشد!')
            return
        
        self.stdout.write(f'تعداد فایل‌های بدون صاحب: {len(orphaned_files)}')
        
        # حذف فایل‌های بدون صاحب
        deleted_count = 0
        for file_path in orphaned_files:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if dry_run:
                self.stdout.write(f'حذف می‌شود: {file_path}')
            else:
                try:
                    os.remove(full_path)
                    self.stdout.write(f'حذف شد: {file_path}')
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'خطا در حذف {file_path}: {e}'))
        
        if not dry_run:
            self.stdout.write(f'تعداد فایل‌های حذف شده: {deleted_count}')

    def cleanup_profile_images(self, dry_run):
        """تمیز کردن عکس‌های پروفایل"""
        self.stdout.write('=== تمیز کردن عکس‌های پروفایل ===')
        
        # دریافت همه عکس‌های موجود در دیتابیس
        db_images = set()
        for profile in UserProfile.objects.all():
            if profile.avatar:
                db_images.add(profile.avatar.name)
        
        self.stdout.write(f'تعداد عکس‌های موجود در دیتابیس: {len(db_images)}')
        
        # دریافت همه فایل‌های موجود در پوشه
        file_images = set()
        avatars_dir = os.path.join(settings.MEDIA_ROOT, 'avatars')
        
        if os.path.exists(avatars_dir):
            for root, dirs, files in os.walk(avatars_dir):
                for file in files:
                    if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        relative_path = os.path.relpath(os.path.join(root, file), settings.MEDIA_ROOT)
                        file_images.add(relative_path)
        
        self.stdout.write(f'تعداد فایل‌های موجود در پوشه: {len(file_images)}')
        
        # پیدا کردن فایل‌های بدون صاحب
        orphaned_files = file_images - db_images
        
        if not orphaned_files:
            self.stdout.write('هیچ فایل بدون صاحبی پیدا نشد!')
            return
        
        self.stdout.write(f'تعداد فایل‌های بدون صاحب: {len(orphaned_files)}')
        
        # حذف فایل‌های بدون صاحب
        deleted_count = 0
        for file_path in orphaned_files:
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            if dry_run:
                self.stdout.write(f'حذف می‌شود: {file_path}')
            else:
                try:
                    os.remove(full_path)
                    self.stdout.write(f'حذف شد: {file_path}')
                    deleted_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'خطا در حذف {file_path}: {e}'))
        
        if not dry_run:
            self.stdout.write(f'تعداد فایل‌های حذف شده: {deleted_count}')

    def cleanup_empty_directories(self, dry_run):
        """تمیز کردن پوشه‌های خالی"""
        self.stdout.write('=== تمیز کردن پوشه‌های خالی ===')
        
        media_root = settings.MEDIA_ROOT
        deleted_dirs = 0
        
        for root, dirs, files in os.walk(media_root, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                try:
                    if not os.listdir(dir_path):  # پوشه خالی است
                        if dry_run:
                            self.stdout.write(f'حذف می‌شود: {os.path.relpath(dir_path, media_root)}')
                        else:
                            os.rmdir(dir_path)
                            self.stdout.write(f'حذف شد: {os.path.relpath(dir_path, media_root)}')
                            deleted_dirs += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'خطا در حذف پوشه {dir_path}: {e}'))
        
        if not dry_run:
            self.stdout.write(f'تعداد پوشه‌های حذف شده: {deleted_dirs}') 