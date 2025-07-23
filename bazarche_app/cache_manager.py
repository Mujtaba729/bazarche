from django.core.cache import cache
from django.core.cache import caches
from django.db.models import Q
from .models import Product, Category, MainCategory
import json
import hashlib

class CacheManager:
    """مدیریت کش برای بهبود عملکرد سایت"""
    
    @staticmethod
    def get_cache_key(prefix, *args):
        """ایجاد کلید کش از پارامترهای ورودی"""
        key_parts = [prefix] + [str(arg) for arg in args]
        return ':'.join(key_parts)
    
    @staticmethod
    def get_products_cache_key(category_id=None, city_id=None, search_query=None, page=1):
        """کلید کش برای محصولات"""
        cache_key = f"products:list"
        if category_id:
            cache_key += f":cat_{category_id}"
        if city_id:
            cache_key += f":city_{city_id}"
        if search_query:
            # استفاده از hash برای جستجوهای طولانی
            search_hash = hashlib.md5(search_query.encode()).hexdigest()[:8]
            cache_key += f":search_{search_hash}"
        cache_key += f":page_{page}"
        return cache_key
    
    @staticmethod
    def cache_products(products, category_id=None, city_id=None, search_query=None, page=1, timeout=600):
        """کش کردن لیست محصولات"""
        cache_key = CacheManager.get_products_cache_key(category_id, city_id, search_query, page)
        
        # تبدیل QuerySet به لیست برای کش
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'title': product.name_fa,
                'description': product.description_fa,
                'price': str(product.price),
                'city_name': product.city.name if product.city else None,
                'category_name': product.category.name_fa if product.category else None,
                'image_url': product.image.url if hasattr(product, 'image') and product.image else None,
                'created_at': product.created_at.isoformat(),
                'is_suggested': product.is_suggested,
            })
        
        cache.set(cache_key, products_data, timeout)
        return cache_key
    
    @staticmethod
    def get_cached_products(category_id=None, city_id=None, search_query=None, page=1):
        """دریافت محصولات از کش"""
        cache_key = CacheManager.get_products_cache_key(category_id, city_id, search_query, page)
        return cache.get(cache_key)
    
    @staticmethod
    def clear_products_cache():
        """پاک کردن کش محصولات"""
        # پاک کردن تمام کلیدهای مربوط به محصولات
        cache_keys = [
            'products:list',
            'products:count',
            'products:categories',
        ]
        for key in cache_keys:
            try:
                cache.delete_pattern(f"{key}*")
            except AttributeError:
                # اگر delete_pattern وجود نداشت (مثلاً LocMemCache)
                # همه کلیدهای کش را بگیر و کلیدهای مربوط به محصولات را پاک کن
                if hasattr(cache, 'keys'):
                    keys = cache.keys(f"{key}*")
                    for k in keys:
                        cache.delete(k)
    
    @staticmethod
    def cache_categories(categories, timeout=1800):  # 30 دقیقه
        """کش کردن دسته‌بندی‌ها"""
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'name_en': category.name_en,
                'name_fa': category.name_fa,
                'product_count': category.product_set.count(),
            })
        
        cache.set('categories:all', categories_data, timeout)
        return 'categories:all'
    
    @staticmethod
    def get_cached_categories():
        """دریافت دسته‌بندی‌ها از کش"""
        return cache.get('categories:all')
    
    @staticmethod
    def cache_main_categories(categories, timeout=1800):
        """کش کردن دسته‌بندی‌های اصلی"""
        categories_data = []
        for category in categories:
            categories_data.append({
                'id': category.id,
                'name': category.name,
                'name_en': category.name_en,
                'name_fa': category.name_fa,
                'product_count': category.product_set.count(),
            })
        
        cache.set('main_categories:all', categories_data, timeout)
        return 'main_categories:all'
    
    @staticmethod
    def get_cached_main_categories():
        """دریافت دسته‌بندی‌های اصلی از کش"""
        return cache.get('main_categories:all')
    
    @staticmethod
    def cache_product_count(count, timeout=300):
        """کش کردن تعداد محصولات"""
        cache.set('products:total_count', count, timeout)
    
    @staticmethod
    def get_cached_product_count():
        """دریافت تعداد محصولات از کش"""
        return cache.get('products:total_count')
    
    @staticmethod
    def invalidate_product_cache(product_id):
        """باطل کردن کش محصول خاص"""
        # پاک کردن کش محصول
        cache.delete(f'product:detail:{product_id}')
        
        # پاک کردن کش لیست محصولات
        CacheManager.clear_products_cache()
    
    @staticmethod
    def cache_product_detail(product, timeout=600):
        """کش کردن جزئیات محصول"""
        product_data = {
            'id': product.id,
            'title': product.name_fa,
            'description': product.description_fa,
            'price': str(product.price),
            'city_name': product.city.name if product.city else None,
            'category_name': product.category.name_fa if product.category else None,
            'image_url': product.image.url if hasattr(product, 'image') and product.image else None,
            'created_at': product.created_at.isoformat(),
            'is_suggested': product.is_suggested,
            'owner_name': product.owner.username if hasattr(product, 'owner') and product.owner else None,
        }
        
        cache_key = f'product:detail:{product.id}'
        cache.set(cache_key, product_data, timeout)
        return cache_key
    
    @staticmethod
    def get_cached_product_detail(product_id):
        """دریافت جزئیات محصول از کش"""
        return cache.get(f'product:detail:{product_id}')
    
    @staticmethod
    def clear_all_cache():
        """پاک کردن تمام کش"""
        cache.clear()
        print("تمام کش پاک شد")
    
    @staticmethod
    def get_cache_stats():
        """دریافت آمار کش"""
        try:
            # این فقط برای نمایش است، در Redis واقعی نیاز به دسترسی مستقیم داریم
            return {
                'status': 'فعال',
                'backend': 'Redis',
                'location': '127.0.0.1:6379'
            }
        except Exception as e:
            return {
                'status': 'خطا',
                'error': str(e)
            } 