from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from django.conf import settings
import os
from .models import Product, ProductImage, UserProfile, AdminAlert
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count

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


@receiver(post_save, sender=Product)
def monitor_high_post_rate(sender, instance, created, **kwargs):
    """اگر کاربری در بازه کوتاه تعداد زیادی محصول ثبت کند، هشدار لاگی بده"""
    try:
        if not created or not instance.user:
            return
        now = timezone.now()
        one_hour = now - timedelta(hours=1)
        day = now - timedelta(days=1)
        user = instance.user
        count_1h = Product.objects.filter(user=user, created_at__gte=one_hour).count()
        count_1d = Product.objects.filter(user=user, created_at__gte=day).count()
        if count_1h >= 15 or count_1d >= 50:
            # ذخیره هشدار در ادمین
            AdminAlert.objects.create(
                user=user,
                count_last_hour=count_1h,
                count_last_day=count_1d,
                note='High posting rate'
            )
            print(f"[ADMIN ALERT] User '{user.username}' (ID={user.id}) posted {count_1h} items in last 1h and {count_1d} in last 24h.")
    except Exception:
        pass

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