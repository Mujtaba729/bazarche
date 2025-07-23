from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.conf import settings
import os
from .models import Product, ProductImage, UserProfile

@receiver(pre_delete, sender=Product)
def delete_product_files(sender, instance, **kwargs):
    """حذف عکس‌های محصول وقتی محصول حذف می‌شه"""
    try:
        # حذف عکس‌های محصول
        for product_image in instance.images.all():
            if product_image.image:
                file_path = os.path.join(settings.MEDIA_ROOT, str(product_image.image))
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"عکس محصول حذف شد: {file_path}")
    except Exception as e:
        print(f"خطا در حذف عکس‌های محصول: {e}")

@receiver(pre_delete, sender=ProductImage)
def delete_product_image_file(sender, instance, **kwargs):
    """حذف فایل عکس وقتی ProductImage حذف می‌شه"""
    try:
        if instance.image:
            file_path = os.path.join(settings.MEDIA_ROOT, str(instance.image))
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"فایل عکس حذف شد: {file_path}")
    except Exception as e:
        print(f"خطا در حذف فایل عکس: {e}")

@receiver(pre_delete, sender=UserProfile)
def delete_profile_avatar(sender, instance, **kwargs):
    """حذف عکس پروفایل وقتی UserProfile حذف می‌شه"""
    try:
        if instance.avatar:
            file_path = os.path.join(settings.MEDIA_ROOT, str(instance.avatar))
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"عکس پروفایل حذف شد: {file_path}")
    except Exception as e:
        print(f"خطا در حذف عکس پروفایل: {e}") 