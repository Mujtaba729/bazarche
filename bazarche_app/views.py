from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.utils import translation
from django.utils.translation import gettext as _
from django.db.models import F, Value, CharField, Q
from django.db.models.functions import Coalesce
from django.db.models import Count
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from django.contrib.auth.models import User
from .models import Product, ProductImage, Category, Tag, VisitLog, UserFeedback, MainCategory, City, AbuseReport, Advertisement, JobAd, Request
from .forms import ProductForm, UserFeedbackForm, UserRegistrationForm, UserProfileEditForm, UserProfileForm, JobAdForm, RequestForm
from django.utils import timezone
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.core.files.base import ContentFile
from PIL import Image, ImageOps
import io
import os
from django import forms
from .cache_manager import CacheManager
from datetime import timedelta

def get_language_suffix():
    lang = translation.get_language()
    if lang not in ['fa', 'ps', 'en']:
        lang = 'fa'
    return lang

@cache_page(60 * 5)  # 5 minutes cache
def featured_products(request):
    lang = get_language_suffix()
    name_field = F(f'name_{lang}')
    description_field = F(f'description_{lang}')
    products = Product.objects.filter(is_approved=True, is_featured=True).annotate(
        name_display=Coalesce(name_field, Value(''), output_field=CharField()),
        description_display=Coalesce(description_field, Value(''), output_field=CharField())
    ).order_by('-created_at')
    return render(request, 'product_list.html', {
        'products': products,
        'title': 'محصولات ویژه',
    })

@cache_page(60 * 5)  # 5 minutes cache
def discounted_products(request):
    lang = get_language_suffix()
    name_field = F(f'name_{lang}')
    description_field = F(f'description_{lang}')
    products = Product.objects.filter(is_approved=True, is_discounted=True).annotate(
        name_display=Coalesce(name_field, Value(''), output_field=CharField()),
        description_display=Coalesce(description_field, Value(''), output_field=CharField())
    ).order_by('-created_at')
    return render(request, 'product_list.html', {
        'products': products,
        'title': 'محصولات تخفیف‌دار',
    })

def feedback(request):
    if request.method == 'POST':
        form = UserFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "پیام شما با موفقیت ارسال شد. متشکریم!")
            return redirect('feedback')
        else:
            messages.error(request, "فرم دارای خطا است. لطفا اصلاح کنید.")
    else:
        form = UserFeedbackForm()
    return render(request, 'feedback.html', {'form': form})

def get_cities_context(request):
    """Get cities for context"""
    cities = City.objects.annotate(
        product_count=Count('product', filter=Q(product__is_approved=True))
    ).order_by('order', 'name')
    
    # Get selected city name if any
    selected_city = None
    city_id = request.GET.get('city_id')
    if city_id:
        try:
            city = City.objects.get(id=city_id)
            selected_city = city.name
        except (City.DoesNotExist, ValueError):
            pass
    
    return {
        'cities': cities,
        'selected_city': selected_city,
        'selected_city_id': city_id
    }

def get_categories_context():
    """Get categories for context"""
    categories_list = [
        'وسایل نقلیه',
        'لوازم دیجیتال',
        'لوازم خانگی',
        'وسایل شخصی',
        'سرگرمی و فراغت',
        'تجهیزات و صنعتی',
        'خدمات',
        'املاک',
        'اجتماعی',
        #'استخدام و کاریابی',  # حذف شد
        'کتاب و مجله',
    ]
    main_categories = list(Category.objects.filter(name_fa__in=categories_list).order_by('order', 'name_fa'))

    # Fallback icon fixes for known categories (display-level; does not write DB)
    fallback_icon_by_name = {
        'وسایل نقلیه': 'bi-car-front',
    }
    for cat in main_categories:
        if (not getattr(cat, 'icon', None)) or getattr(cat, 'icon', '').strip() in {'', 'bi-tag', 'bi-car'}:
            if cat.name_fa in fallback_icon_by_name:
                setattr(cat, 'icon', fallback_icon_by_name[cat.name_fa])

    return {
        'categories': main_categories,
        'all_categories': main_categories,
        'main_categories': main_categories
    }

def get_price_ranges():
    """Get price ranges for context"""
    return {
        'price_ranges': [
            ('0-1000', '0 - 1,000 افغانی'),
            ('1000-5000', '1,000 - 5,000 افغانی'),
            ('5000-10000', '5,000 - 10,000 افغانی'),
            ('10000-50000', '10,000 - 50,000 افغانی'),
            ('50000-100000', '50,000 - 100,000 افغانی'),
            ('100000+', 'بیش از 100,000 افغانی'),
        ]
    }

def get_tags_context():
    """Get tags for context"""
    return {
        'tags': Tag.objects.all().order_by('name_fa')
    }

def home(request):
    """نمایش صفحه اصلی با کش"""
    # دریافت تبلیغات
    from django.utils import timezone
    now = timezone.now()
    advertisements = Advertisement.objects.filter(
        is_active=True,
        location='home',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('display_order', '-created_at')[:3]

    # دریافت پارامترهای فیلتر
    category_id = request.GET.get('category')
    city_id = request.GET.get('city_id')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-created_at')
    price_range = request.GET.get('price_range')
    tag_id = request.GET.get('tag')
    page = request.GET.get('page', 1)

    # نمایش محصولات با امکان فیلتر بر اساس عبارت جستجو
    products_qs = Product.objects.filter(is_approved=True)

    # فیلتر بر اساس شهر
    if city_id:
        products_qs = products_qs.filter(city_id=city_id)

    # فیلتر جستجو در صفحه خانه اگر q وجود داشته باشد
    if search_query:
        products_qs = products_qs.filter(
            Q(name_fa__icontains=search_query) |
            Q(description_fa__icontains=search_query) |
            Q(tags__name_fa__icontains=search_query)
        ).distinct()

    products_qs = products_qs.order_by('-created_at')
    products_data = list(products_qs)

    # Get featured, suggested, and discounted products for priority
    featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
    suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
    discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
    remaining_products = sorted([
        p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
    ], key=lambda p: p.created_at, reverse=True)

    # Combine all products: featured -> suggested -> discounted -> remaining (همه به ترتیب جدیدترین)
    all_products = featured_products + suggested_products + discounted_products + remaining_products
    
    # Get advertisements for product placement
    from django.utils import timezone
    now = timezone.now()
    product_advertisements = Advertisement.objects.filter(
        is_active=True,
        location='products',
        start_date__lte=now,
        end_date__gte=now
    ).order_by('display_order', '-created_at')
    
    # Insert advertisements into products list
    products_with_ads = []
    ad_index = 0
    
    for i, product in enumerate(all_products):
        products_with_ads.append(product)
        
        # Add advertisement every 10 products
        if (i + 1) % 10 == 0 and ad_index < len(product_advertisements):
            products_with_ads.append(product_advertisements[ad_index])
            ad_index += 1
    
    # Pagination
    paginator = Paginator(products_with_ads, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories and other context
    categories_context = get_categories_context()
    
    context = {
        'products': page_obj,
        'advertisements': advertisements,
        'cities': City.objects.all(),
        'tags': Tag.objects.all(),
        'price_ranges': [
            ('0-1000', '0 - 1,000 افغانی'),
            ('1000-5000', '1,000 - 5,000 افغانی'),
            ('5000-10000', '5,000 - 10,000 افغانی'),
            ('10000-50000', '10,000 - 50,000 افغانی'),
            ('50000-100000', '50,000 - 100,000 افغانی'),
            ('100000+', 'بیش از 100,000 افغانی'),
        ],
        'sort_options': [
            ('-created_at', 'جدیدترین'),
            ('created_at', 'قدیمی‌ترین'),
            ('price', 'ارزان‌ترین'),
            ('-price', 'گران‌ترین'),
            ('name_fa', 'نام (الف-ی)'),
            ('-name_fa', 'نام (ی-الف)'),
        ],
        'search_query': search_query,
        **categories_context
    }
    
    return render(request, 'home.html', context)

def load_more_products(request):
    """API endpoint برای لود محصولات بیشتر"""
    from django.http import JsonResponse
    from django.core.paginator import Paginator
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # دریافت پارامترهای فیلتر
        category_id = request.GET.get('category')
        city_id = request.GET.get('city_id')
        search_query = request.GET.get('q')
        page = int(request.GET.get('page', 1))
        
        logger.info(f"Loading page {page} with filters - category: {category_id}, city: {city_id}, search: {search_query}")
        
        # نمایش محصولات با امکان فیلتر
        products_qs = Product.objects.filter(is_approved=True)
        
        # فیلتر بر اساس شهر
        if city_id:
            products_qs = products_qs.filter(city_id=city_id)
        
        # فیلتر جستجو
        if search_query:
            products_qs = products_qs.filter(
                Q(name_fa__icontains=search_query) |
                Q(description_fa__icontains=search_query) |
                Q(tags__name_fa__icontains=search_query)
            ).distinct()
        
        products_qs = products_qs.order_by('-created_at')
        products_data = list(products_qs)
        
        logger.info(f"Total products found: {len(products_data)}")
        
        # Get featured, suggested, and discounted products for priority
        featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
        suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
        discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
        remaining_products = sorted([
            p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
        ], key=lambda p: p.created_at, reverse=True)
        
        # Combine all products
        all_products = featured_products + suggested_products + discounted_products + remaining_products
        
        logger.info(f"Combined products: {len(all_products)}")
        
        # Get advertisements for product placement
        from django.utils import timezone
        now = timezone.now()
        product_advertisements = Advertisement.objects.filter(
            is_active=True,
            location='products',
            start_date__lte=now,
            end_date__gte=now
        ).order_by('display_order', '-created_at')
        
        # Insert advertisements into products list
        products_with_ads = []
        ad_index = 0
        
        for i, product in enumerate(all_products):
            products_with_ads.append(product)
            
            # Add advertisement every 10 products
            if (i + 1) % 10 == 0 and ad_index < len(product_advertisements):
                products_with_ads.append(product_advertisements[ad_index])
                ad_index += 1
        
        # Pagination
        paginator = Paginator(products_with_ads, 20)
        page_obj = paginator.get_page(page)
        
        logger.info(f"Page {page} has {len(page_obj)} items, has_next: {page_obj.has_next()}")
        
        # Convert products to JSON
        products_data = []
        for product in page_obj:
            if hasattr(product, 'name_fa'):  # It's a product
                products_data.append({
                    'id': product.id,
                    'name': product.name_fa or product.name_en or product.name_ps,
                    'price': product.price,
                    'discount_price': product.discount_price,
                    'city': product.city.name if product.city else None,
                    'image': product.images.first().image.url if product.images.first() else None,
                    'is_featured': product.is_featured,
                    'is_discounted': product.is_discounted,
                    'is_suggested': product.is_suggested,
                    'created_at': product.created_at.strftime('%Y-%m-%d %H:%M'),
                    'url': f'/product/{product.id}/',
                    'type': 'product'
                })
            else:  # It's an advertisement
                products_data.append({
                    'id': f'ad_{product.id}',
                    'title': product.title,
                    'image': product.image.url if product.image else None,
                    'link': product.link,
                    'type': 'advertisement'
                })
        
        response_data = {
            'products': products_data,
            'has_next': page_obj.has_next(),
            'current_page': page,
            'total_pages': paginator.num_pages,
            'total_products': paginator.count
        }
        
        logger.info(f"Returning {len(products_data)} products")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Error in load_more_products: {str(e)}")
        return JsonResponse({
            'products': [],
            'has_next': False,
            'current_page': page,
            'total_pages': 0,
            'error': str(e)
        })

def about(request):
    """صفحه درباره ما"""
    context = {}
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'about.html', context)

def contact_us(request):
    """Contact us page view"""
    if request.method == 'POST':
        form = UserFeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('پیام شما با موفقیت ارسال شد.'))
            return redirect('app:contact_us')
    else:
        form = UserFeedbackForm()
    
    context = {
        'form': form
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'contact_us.html', context)

def set_language(request):
    lang_code = request.GET.get('lang')
    next_url = request.GET.get('next', '/')
    if lang_code and lang_code in dict(settings.LANGUAGES).keys():
        request.session['django_language'] = lang_code
        translation.activate(lang_code)
    return redirect(next_url)

@staff_member_required
def manage_products(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin/manage_products.html', {'products': products})

@staff_member_required
def approve_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_approved = True
    product.save()
    messages.success(request, f"محصول {product.name_fa} تایید شد.")
    return redirect('manage_products')

@csrf_protect
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, f"محصول {product.name_fa} حذف شد.")
    return redirect('manage_products')

@csrf_protect
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    tags = Tag.objects.all()
    
    if request.method == 'POST':
        product.name_fa = request.POST.get('name_fa', '').strip()
        product.name_ps = request.POST.get('name_ps', '').strip()
        product.name_en = request.POST.get('name_en', '').strip()
        product.description_fa = request.POST.get('description_fa', '').strip()
        product.description_ps = request.POST.get('description_ps', '').strip()
        product.description_en = request.POST.get('description_en', '').strip()
        product.category_id = request.POST.get('category')
        product.city = request.POST.get('city', '').strip()
        product.price = request.POST.get('price') or None
        product.discount_price = request.POST.get('discount_price') or None
        product.is_featured = bool(request.POST.get('is_featured'))
        product.is_discounted = bool(request.POST.get('is_discounted'))
        product.seller_contact = request.POST.get('seller_contact', '').strip()
        
        tags_selected = request.POST.getlist('tags')
        if tags_selected:
            product.tags.set(tags_selected)
        else:
            product.tags.clear()
        
        product.save()
        messages.success(request, f"محصول {product.name_fa} به‌روزرسانی شد.")
        return redirect('manage_products')
    
    return render(request, 'admin/edit_product.html', {
        'product': product,
        'categories': categories,
        'tags': tags,
    })

@csrf_protect
@login_required
def manage_categories(request):
    categories = Category.objects.all().order_by('name_fa')
    return render(request, 'admin/manage_categories.html', {'categories': categories})

@csrf_protect
@login_required
def add_category(request):
    if request.method == 'POST':
        name_fa = request.POST.get('name_fa', '').strip()
        name_ps = request.POST.get('name_ps', '').strip()
        name_en = request.POST.get('name_en', '').strip()
        
        if not name_fa:
            messages.error(request, "نام دسته‌بندی (دری) الزامی است.")
            return redirect('manage_categories')
        
        Category.objects.create(name_fa=name_fa, name_ps=name_ps, name_en=name_en)
        messages.success(request, "دسته‌بندی جدید اضافه شد.")
        return redirect('manage_categories')
    
    return render(request, 'admin/add_category.html')

@csrf_protect
@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.name_fa = request.POST.get('name_fa', '').strip()
        category.name_ps = request.POST.get('name_ps', '').strip()
        category.name_en = request.POST.get('name_en', '').strip()
        
        if not category.name_fa:
            messages.error(request, "نام دسته‌بندی (دری) الزامی است.")
            return redirect('manage_categories')
        
        category.save()
        messages.success(request, "دسته‌بندی به‌روزرسانی شد.")
        return redirect('manage_categories')
    
    return render(request, 'admin/edit_category.html', {'category': category})

@csrf_protect
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, "دسته‌بندی حذف شد.")
    return redirect('manage_categories')

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template.loader import render_to_string

def product_list(request):
    """Product list view"""
    # Get active advertisements for products page
    advertisements = Advertisement.objects.filter(
        location='products',
        is_active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now()
    ).order_by('-created_at')[:3]  # Get up to 3 most recent ads

    # Get filter parameters
    category_id = request.GET.get('category')
    main_category_id = request.GET.get('main_category')
    city_id = request.GET.get('city_id')
    search_query = request.GET.get('q')
    sort_by = request.GET.get('sort', '-created_at')
    price_range = request.GET.get('price_range')
    tag_id = request.GET.get('tag')
    is_featured = request.GET.get('featured') == 'true'
    is_discounted = request.GET.get('discounted') == 'true'
    
    # Base queryset
    products = Product.objects.filter(is_approved=True)
    
    # Get featured, suggested and discounted products
    featured_products = Product.objects.filter(is_approved=True, is_featured=True).order_by('-created_at')[:8]
    suggested_products = Product.objects.filter(is_approved=True, is_suggested=True).order_by('-created_at')[:8]
    discounted_products = Product.objects.filter(is_approved=True, is_discounted=True).order_by('-created_at')[:8]
    
    # Apply filters
    if main_category_id:
        # Get all categories that belong to this main category
        categories = Category.objects.filter(id=main_category_id)
        products = products.filter(category__in=categories)
    elif category_id:
        products = products.filter(category_id=category_id)
    if city_id:
        products = products.filter(city_id=city_id)
    if search_query:
        products = products.filter(
            Q(name_fa__icontains=search_query) |
            Q(description_fa__icontains=search_query) |
            Q(tags__name_fa__icontains=search_query)
        ).distinct()
    if price_range:
        if price_range == '0-1000':
            products = products.filter(price__gte=0, price__lte=1000)
        elif price_range == '1000-5000':
            products = products.filter(price__gt=1000, price__lte=5000)
        elif price_range == '5000-10000':
            products = products.filter(price__gt=5000, price__lte=10000)
        elif price_range == '10000-50000':
            products = products.filter(price__gt=10000, price__lte=50000)
        elif price_range == '50000-100000':
            products = products.filter(price__gt=50000, price__lte=100000)
        elif price_range == '100000+':
            products = products.filter(price__gt=100000)
    if tag_id:
        products = products.filter(tags__id=tag_id)
    if is_featured:
        products = products.filter(is_featured=True)
    if is_discounted:
        products = products.filter(is_discounted=True)
    
    # Apply sorting
    products = products.order_by(sort_by)
    
    # Get selected city name if any
    selected_city = None
    if city_id:
        try:
            city = City.objects.get(id=city_id)
            selected_city = city.name
        except (City.DoesNotExist, ValueError):
            pass
    
    context = {
        'advertisements': advertisements,
        'products': products,
        'featured_products': featured_products,
        'suggested_products': suggested_products,
        'discounted_products': discounted_products,
        'selected_category': category_id,
        'selected_main_category': main_category_id,
        'selected_city': selected_city,
        'selected_city_id': city_id,
        'search_query': search_query,
        'sort_by': sort_by,
        'selected_price_range': price_range,
        'selected_tag': tag_id,
        'is_featured': is_featured,
        'is_discounted': is_discounted,
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    context.update(get_price_ranges())
    context.update(get_tags_context())
    return render(request, 'product_list.html', context)

def product_detail(request, pk):
    """نمایش جزئیات محصول با کش"""
    # بررسی کش برای جزئیات محصول
    cached_product = CacheManager.get_cached_product_detail(pk)
    
    if cached_product:
        # استفاده از کش
        product_data = cached_product
        product = None  # برای سازگاری با کد موجود
    else:
        # دریافت از دیتابیس
        product = get_object_or_404(
            Product.objects.select_related('category')
            .prefetch_related('tags', 'images'),
            pk=pk,
            is_approved=True
        )
        
        # کش کردن جزئیات محصول
        CacheManager.cache_product_detail(product)
        
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
    
    # دریافت محصولات مرتبط
    if product:
        related_products = Product.objects.filter(
            category=product.category, 
            is_approved=True
        ).exclude(pk=pk).order_by('?')[:4]
        
        seller_products = Product.objects.filter(
            seller_contact=product.seller_contact,
            is_approved=True
        ).exclude(pk=pk).order_by('-created_at')[:4]
    else:
        # اگر از کش استفاده می‌کنیم، محصولات مرتبط را از دیتابیس می‌گیریم
        category_name = product_data.get('category_name')
        if category_name:
            category = Category.objects.filter(name_fa=category_name).first()
            if category:
                related_products = Product.objects.filter(
                    category=category,
                    is_approved=True
                ).exclude(pk=pk).order_by('?')[:4]
            else:
                related_products = []
        else:
            related_products = []
        
        seller_products = []  # برای سادگی، seller_products را خالی می‌گذاریم
    
    if not product:
        # اگر از کش فقط آیدی یا دیکشنری داشتیم، محصول را از دیتابیس بگیر
        product = Product.objects.get(pk=pk)
    context = {
        'product': product,
        'related_products': related_products,
        'seller_products': seller_products,
    }
    return render(request, 'product_detail.html', context)

from .forms import ProductForm, UserRegistrationForm
from .models import UserProfile
from django.contrib.auth import authenticate, login

from django.contrib.auth.decorators import login_required

from django.utils import translation
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ProductForm
from .models import Product, ProductImage

def compress_image(image_file, max_size=(600, 600), quality=50):
    """
    فشرده‌سازی فوق‌العاده سریع برای سرعت حداکثر:
    - کاهش کیفیت به 50 برای سرعت بیشتر
    - کاهش اندازه عکس به 600x600 برای سرعت بیشتر
    - پرهیز از پردازش فایل‌های کوچک
    - استفاده از الگوریتم‌های سریع‌ترین
    """
    try:
        # اگر فایل خیلی کوچک است، همان را برگردان
        original_size_bytes = getattr(image_file, 'size', None)
        if original_size_bytes is not None and original_size_bytes <= 150 * 1024:  # 150KB
            return image_file

        # باز کردن تصویر
        img = Image.open(image_file)

        # تبدیل به RGB اگر RGBA/LA/P باشد (سریع‌تر)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # کاهش ابعاد اگر بزرگ است (الگوریتم سریع‌ترین)
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.NEAREST)

        # ذخیره با پارامترهای سریع‌ترین
        output = io.BytesIO()
        img.save(
            output,
            format='JPEG',
            quality=quality,
            optimize=False,
            progressive=False,
            subsampling=2
        )
        output.seek(0)

        # نام فایل خروجی
        filename = os.path.splitext(image_file.name)[0] + '.jpg'
        return ContentFile(output.getvalue(), filename)
    except Exception:
        # در صورت خطا، فایل اصلی را استفاده کن
        return image_file

def get_product_form_context(form):
    """تابع کمکی برای ایجاد context فرم محصول"""
    return {
        'form': form,
        'categories': Category.objects.filter(name_fa__in=[
            'وسایل نقلیه',
            'لوازم دیجیتال',
            'لوازم خانگی',
            'وسایل شخصی',
            'سرگرمی و فراغت',
            'تجهیزات و صنعتی',
            'خدمات',
            'املاک',
            'اجتماعی',
            'استخدام و کاریابی',
            'کتاب و مجله',
        ]).order_by('order', 'name_fa'),
    }

@csrf_protect
@login_required
def register_product(request):
    current_lang = translation.get_language()
    
    # Ensure user is authenticated
    if not request.user.is_authenticated:
        messages.error(request, "لطفا ابتدا وارد شوید.")
        return redirect('app:login')
    
    if request.method == 'POST':
        try:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                category = form.cleaned_data.get('category')
                name = form.cleaned_data.get('name', '')
                description = form.cleaned_data.get('description', '')
                seller_contact = form.cleaned_data.get('seller_contact', '')
                
                city_value = form.cleaned_data.get('city')
                if isinstance(city_value, City):
                    city_instance = city_value
                else:
                    city_instance = City.objects.get(name=city_value)
                product = Product(
                    user=request.user,
                    category=category,
                    city=city_instance,
                    condition='new',  # پیش‌فرض نو
                    price=form.cleaned_data.get('price'),
                    discount_price=form.cleaned_data.get('discount_price'),
                    price_range='100000+',  # پیش‌فرض بیش از 100,000 افغانی
                    is_featured=False,  # Set default False, user cannot set
                    is_discounted=False,  # Set default False, user cannot set
                    seller_contact=seller_contact,  # استفاده از شماره تماس وارد شده توسط کاربر
                    is_approved=True  # تغییر به True برای تایید خودکار
                )
                # Set name and description based on current language
                if current_lang == 'ps':
                    product.name_ps = name
                    product.description_ps = description
                elif current_lang == 'en':
                    product.name_en = name
                    product.description_en = description
                else:
                    product.name_fa = name
                    product.description_fa = description

                product.save()
                # پاک کردن کش محصولات بعد از ثبت محصول جدید
                from .cache_manager import CacheManager
                CacheManager.clear_products_cache()
                
                # اعتبارسنجی عکس‌ها
                images = request.FILES.getlist('images')
                
                # بررسی وجود حداقل یک عکس
                if not images:
                    messages.error(request, "لطفا حداقل یک عکس برای محصول خود آپلود کنید.")
                    product.delete()
                    return render(request, 'register_product.html', get_product_form_context(form))
                
                # بررسی حداکثر تعداد عکس (5 عکس)
                if len(images) > 5:
                    messages.error(request, "شما می‌توانید حداکثر ۵ عکس برای هر محصول آپلود کنید.")
                    product.delete()
                    return render(request, 'register_product.html', get_product_form_context(form))
                
                # ذخیره عکس‌ها با فشرده‌سازی فوق‌العاده سریع
                try:
                    # پردازش سریع عکس‌ها بدون نمایش پیام
                    for img in images:
                        compressed_img = compress_image(img)
                        ProductImage.objects.create(product=product, image=compressed_img)
                    
                    messages.success(request, "محصول شما با موفقیت ثبت شد و در سایت نمایش داده خواهد شد.")
                    return redirect('app:home')
                except Exception as e:
                    messages.error(request, f"خطا در آپلود عکس‌ها: {str(e)}")
                    product.delete()
                    return render(request, 'register_product.html', get_product_form_context(form))
            else:
                messages.error(request, "فرم دارای خطا است. لطفا اصلاح کنید.")
                return render(request, 'register_product.html', get_product_form_context(form))
        except Exception as e:
            messages.error(request, f"خطا در پردازش فرم: {str(e)}")
            form = ProductForm()
            return render(request, 'register_product.html', get_product_form_context(form))
    else:
        form = ProductForm()
        # Remove is_featured and is_discounted fields from form
        form.fields.pop('is_featured', None)
        form.fields.pop('is_discounted', None)
        return render(request, 'register_product.html', get_product_form_context(form))

class ResetPasswordForm(forms.Form):
    profile_id = forms.CharField(label='شناسه کاربری', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شناسه کاربری'}))
    new_password = forms.CharField(label='رمز عبور جدید', max_length=128, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'رمز عبور جدید'}))


def reset_password(request):
    message = None
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            profile_id = form.cleaned_data['profile_id']
            new_password = form.cleaned_data['new_password']
            try:
                profile = UserProfile.objects.get(profile_id=profile_id)
                user = profile.user
                user.set_password(new_password)
                user.save()
                profile.password = new_password
                profile.save()
                message = 'رمز عبور با موفقیت تغییر کرد. اکنون می‌توانید وارد شوید.'
            except UserProfile.DoesNotExist:
                form.add_error('profile_id', 'شناسه کاربری معتبر نیست.')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form, 'message': message})

def set_language(request):
    """
    View to set the language preference and redirect to a given URL.
    The URL and the language code need to be specified in the request parameters.
    """
    lang_code = request.GET.get('lang', 'fa')
    next_url = request.GET.get('next', '/')

    # Debugging logs
    print(f"Requested language: {lang_code}")
    print(f"Redirecting to: {next_url}")

    # Check if the language code is supported
    if lang_code in dict(settings.LANGUAGES):
        translation.activate(lang_code)
        request.session['django_language'] = lang_code
        print(f"Language {lang_code} activated and stored in session.")
    else:
        print(f"Language {lang_code} is not supported.")

    return redirect(next_url)

@staff_member_required
def admin_stats(request):
    """
    نمایش سریع، امن و بهینه آمار بازدید محصولات و عملکرد سایت برای مدیر
    """
    # مجموع کل بازدید محصولات - کوئری fail-safe
    total_visits = VisitLog.objects.aggregate(total=Sum('visit_count'))['total'] or 0

    # تعداد کل محصولات و تایید شده
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products = Product.objects.filter(is_approved=False).count()
    
    # آمار محصولات ویژه و تخفیف‌دار
    featured_products = Product.objects.filter(is_approved=True, is_featured=True).count()
    discounted_products = Product.objects.filter(is_approved=True, is_discounted=True).count()
    
    # آمار دسته‌بندی‌ها
    categories_stats = []
    try:
        categories_stats = (
            Product.objects.filter(is_approved=True)
            .values('category__name_fa', 'category__id')
            .annotate(count=Count('id'))
            .order_by('-count')[:10]
        )
    except Exception:
        pass

    # محصولات پربازدید - با مدیریت خطا
    top_products = []
    try:
        top_products = list(
            VisitLog.objects.select_related('product')
            .values('product__id', 'product__name_fa')
            .annotate(total_views=Sum('visit_count'))
            .order_by('-total_views')[:7]
        )
    except Exception:
        pass

    # بازدیدهای اخیر - با مدیریت خطا
    recent_logs = []
    try:
        recent_logs = list(
            VisitLog.objects.select_related('product')
            .order_by('-date')[:25]
        )
    except Exception:
        pass

    # آمار کاربران
    total_users = User.objects.count()
    new_users_24h = User.objects.filter(date_joined__gte=timezone.now()-timezone.timedelta(hours=24)).count()
    # کاربرانی که بیشترین محصول را ثبت کرده‌اند
    top_users_by_products = (
        Product.objects.values('user__id', 'user__username')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )

    context = {
        'total_visits': total_visits,
        'total_products': total_products,
        'total_users': total_users,
        'new_users_24h': new_users_24h,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'featured_products': featured_products,
        'discounted_products': discounted_products,
        'categories_stats': categories_stats,
        'top_products': top_products,
        'recent_logs': recent_logs,
        'top_users_by_products': list(top_users_by_products),
    }
    return render(request, 'admin/stats.html', context)

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            contact = form.cleaned_data['contact']
            password = form.cleaned_data['password']
            
            # Check if user already exists
            if User.objects.filter(username=contact).exists():
                messages.error(request, 'کاربری با این اطلاعات قبلاً ثبت شده است.')
                return render(request, 'register_user.html', {'form': form})
            
            # Create user with contact as username
            user = User.objects.create_user(
                username=contact, 
                email=contact if '@' in contact else '', 
                password=password
            )
            
            # Create user profile
            profile = UserProfile.objects.create(
                user=user, 
                full_name=name, 
                contact=contact, 
                password=password
            )
            
            # Auto login
            from django.contrib.auth import authenticate, login
            user = authenticate(request, username=contact, password=password)
            if user:
                login(request, user)
                # پیام ویژه بعد از ثبت‌نام
                messages.success(request, f'ثبت‌نام با موفقیت انجام شد!\nشناسه کاربری شما: {profile.profile_id}\nلطفاً شناسه کاربری و رمز عبور خود را در جای امن یادداشت کنید. در صورت فراموشی رمز عبور، فقط با شناسه کاربری می‌توانید رمز جدید تعیین کنید.')
            
            return redirect('app:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

@login_required
def user_dashboard(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user, defaults={
        'full_name': request.user.get_full_name() or request.user.username,
        'contact': request.user.username,
        'password': 'simple_password_123'
    })
    
    # فیلتر کردن محصولات بر اساس کاربر
    products = Product.objects.filter(user=request.user).order_by('-created_at')
    
    # محصولات پیشنهادی (بدون دکمه حذف)
    suggested_products = Product.objects.filter(is_suggested=True, is_approved=True).order_by('-created_at')[:6]
    
    # لیست آگهی‌های شغلی کاربر
    user_jobads = JobAd.objects.filter(owner_profile_id=profile.profile_id)
    
    # Get user's requests
    user_requests = Request.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'user_dashboard.html', {
        'profile': profile,
        'products': products,
        'suggested_products': suggested_products,
        'is_user_dashboard': True,
        'user_jobads': user_jobads,
        'user_requests': user_requests,
    })

@login_required
def delete_user_product(request, pk):
    product = get_object_or_404(Product, pk=pk, user=request.user)
    product.delete()
    messages.success(request, 'محصول با موفقیت حذف شد.')
    return redirect('app:user_dashboard')

def landing(request):
    """Landing page view"""
    # Get cities with product counts
    cities = City.objects.annotate(
        product_count=Count('product', filter=Q(product__is_approved=True))
    ).order_by('-product_count')
    
    context = {
        'cities': cities,
    }
    return render(request, 'landing.html', context)

@csrf_protect
def report_abuse(request, pk):
    """View for reporting product abuse"""
    product = get_object_or_404(Product, pk=pk, is_approved=True)
    
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        description = request.POST.get('description')
        
        if report_type and description:
            # Save the abuse report
            AbuseReport.objects.create(
                product=product,
                report_type=report_type,
                description=description
            )
            messages.success(request, _('گزارش تخلف شما با موفقیت ثبت شد. تیم ما در اسرع وقت آن را بررسی خواهد کرد.'))
            return redirect('app:product_detail', pk=pk)
        else:
            messages.error(request, _('لطفا تمام فیلدها را پر کنید.'))
    
    return redirect('app:product_detail', pk=pk)

@staff_member_required
def abuse_reports(request):
    """View for managing abuse reports"""
    reports = AbuseReport.objects.all().select_related('product')
    return render(request, 'admin/abuse_reports.html', {
        'reports': reports
    })

@staff_member_required
def review_abuse_report(request, pk):
    """View for reviewing an abuse report"""
    report = get_object_or_404(AbuseReport, pk=pk)
    if request.method == 'POST':
        report.is_reviewed = True
        report.save()
        messages.success(request, _('گزارش تخلف بررسی شد.'))
        return redirect('app:abuse_reports')
    return render(request, 'admin/review_abuse_report.html', {
        'report': report
    })

@login_required
def user_products(request):
    """نمایش محصولات کاربر"""
    products = Product.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'products': products,
        'profile': request.user.userprofile
    }
    return render(request, 'user_products.html', context)

def category_detail(request, category_id):
    """نمایش محصولات یک دسته‌بندی"""
    category = get_object_or_404(Category, id=category_id)
    
    # دریافت محصولات دسته‌بندی با اولویت‌بندی
    products_qs = Product.objects.filter(
        category=category,
        is_approved=True
    )
    
    # اولویت‌بندی محصولات: ویژه -> پیشنهادی -> تخفیف‌دار -> بقیه
    products_data = list(products_qs)
    
    featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
    suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
    discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
    remaining_products = sorted([
        p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
    ], key=lambda p: p.created_at, reverse=True)
    
    # ترکیب محصولات با اولویت
    all_products = featured_products + suggested_products + discounted_products + remaining_products
    
    # Pagination
    paginator = Paginator(all_products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'products': page_obj,
        'total_products': len(products_data),
        'featured_count': len(featured_products),
        'suggested_count': len(suggested_products),
        'discounted_count': len(discounted_products),
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'category_detail.html', context)

def city_detail(request, city_id):
    """نمایش محصولات یک شهر"""
    city = get_object_or_404(City, id=city_id)
    
    # دریافت محصولات شهر با اولویت‌بندی
    products_qs = Product.objects.filter(
        city=city,
        is_approved=True
    )
    
    # اولویت‌بندی محصولات: ویژه -> پیشنهادی -> تخفیف‌دار -> بقیه
    products_data = list(products_qs)
    
    featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
    suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
    discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
    remaining_products = sorted([
        p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
    ], key=lambda p: p.created_at, reverse=True)
    
    # ترکیب محصولات با اولویت
    all_products = featured_products + suggested_products + discounted_products + remaining_products
    
    # Pagination
    paginator = Paginator(all_products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'city': city,
        'products': page_obj,
        'total_products': len(products_data),
        'featured_count': len(featured_products),
        'suggested_count': len(suggested_products),
        'discounted_count': len(discounted_products),
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'city_detail.html', context)

def tag_detail(request, tag_id):
    """نمایش محصولات یک برچسب"""
    tag = get_object_or_404(Tag, id=tag_id)
    
    # دریافت محصولات برچسب با اولویت‌بندی
    products_qs = Product.objects.filter(
        tags=tag,
        is_approved=True
    )
    
    # اولویت‌بندی محصولات: ویژه -> پیشنهادی -> تخفیف‌دار -> بقیه
    products_data = list(products_qs)
    
    featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
    suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
    discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
    remaining_products = sorted([
        p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
    ], key=lambda p: p.created_at, reverse=True)
    
    # ترکیب محصولات با اولویت
    all_products = featured_products + suggested_products + discounted_products + remaining_products
    
    # Pagination
    paginator = Paginator(all_products, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'products': page_obj,
        'total_products': len(products_data),
        'featured_count': len(featured_products),
        'suggested_count': len(suggested_products),
        'discounted_count': len(discounted_products),
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'tag_detail.html', context)

def search(request):
    """جستجوی محصولات"""
    query = request.GET.get('q', '')
    city_id = request.GET.get('city_id')
    
    if query:
        products_qs = Product.objects.filter(
            Q(name_fa__icontains=query) |
            Q(description_fa__icontains=query) |
            Q(tags__name_fa__icontains=query)
        ).filter(is_approved=True).distinct()
        
        # فیلتر بر اساس شهر
        if city_id:
            products_qs = products_qs.filter(city_id=city_id)
        
        # اولویت‌بندی محصولات: ویژه -> پیشنهادی -> تخفیف‌دار -> بقیه
        products_data = list(products_qs)
        
        featured_products = sorted([p for p in products_data if p.is_featured], key=lambda p: p.created_at, reverse=True)
        suggested_products = sorted([p for p in products_data if p.is_suggested and not p.is_featured], key=lambda p: p.created_at, reverse=True)
        discounted_products = sorted([p for p in products_data if p.is_discounted and not p.is_featured and not p.is_suggested], key=lambda p: p.created_at, reverse=True)
        remaining_products = sorted([
            p for p in products_data if not (p.is_featured or p.is_suggested or p.is_discounted)
        ], key=lambda p: p.created_at, reverse=True)
        
        # ترکیب محصولات با اولویت
        all_products = featured_products + suggested_products + discounted_products + remaining_products
        
        # Pagination
        paginator = Paginator(all_products, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        products = page_obj
    else:
        products = Product.objects.none()
        page_obj = None
    
    context = {
        'products': products,
        'query': query,
        'city_id': city_id,
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'search_results.html', context)

def contact(request):
    """صفحه تماس با ما"""
    if request.method == 'POST':
        form = UserFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            if request.user.is_authenticated:
                feedback.user = request.user
            feedback.save()
            messages.success(request, _('پیام شما با موفقیت ارسال شد. ما در اسرع وقت با شما تماس خواهیم گرفت.'))
            return redirect('app:contact')
    else:
        form = UserFeedbackForm()
    
    context = {
        'form': form
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'contact.html', context)

def terms(request):
    """صفحه شرایط و مقررات"""
    context = {}
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'terms.html', context)

def privacy(request):
    """صفحه حریم خصوصی"""
    context = {}
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'privacy.html', context)

def faq(request):
    """صفحه سوالات متداول"""
    context = {}
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'faq.html', context)

def health(request):
    """ساده‌ترین هلت‌چک برای Railway"""
    return HttpResponse("ok")

@user_passes_test(lambda u: u.is_superuser)
def status(request):
    """صفحه status کامل - فقط برای ادمین"""
    from django.contrib.sessions.models import Session
    from django.utils import timezone
    from datetime import timedelta
    import psutil
    import os
    from django.db import connection
    
    # آمار کاربران
    total_users = User.objects.count()
    active_users_today = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=1)).count()
    active_users_week = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count()
    active_users_month = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    new_users_today = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=1)).count()
    
    # آمار محصولات
    total_products = Product.objects.count()
    approved_products = Product.objects.filter(is_approved=True).count()
    pending_products = Product.objects.filter(is_approved=False).count()
    featured_products = Product.objects.filter(is_featured=True).count()
    discounted_products = Product.objects.filter(is_discounted=True).count()
    products_today = Product.objects.filter(created_at__gte=timezone.now() - timedelta(days=1)).count()
    
    # آمار دسته‌بندی‌ها
    total_categories = Category.objects.count()
    total_cities = City.objects.count()
    
    # آمار جاب‌ها و درخواست‌ها
    total_jobs = JobAd.objects.count() if 'JobAd' in globals() else 0
    total_requests = Request.objects.count() if 'Request' in globals() else 0
    
    # آمار سیستم
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        cpu_percent = psutil.cpu_percent(interval=1)
        
        system_stats = {
            'memory_total': round(memory.total / (1024**3), 2),  # GB
            'memory_used': round(memory.used / (1024**3), 2),   # GB
            'memory_percent': memory.percent,
            'disk_total': round(disk.total / (1024**3), 2),     # GB
            'disk_used': round(disk.used / (1024**3), 2),       # GB
            'disk_percent': round((disk.used / disk.total) * 100, 1),
            'cpu_percent': cpu_percent,
        }
    except:
        system_stats = {
            'memory_total': 'N/A',
            'memory_used': 'N/A', 
            'memory_percent': 'N/A',
            'disk_total': 'N/A',
            'disk_used': 'N/A',
            'disk_percent': 'N/A',
            'cpu_percent': 'N/A',
        }
    
    # آمار دیتابیس
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()))")
            db_size = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM pg_stat_activity WHERE state = 'active'")
            active_connections = cursor.fetchone()[0]
            
            cursor.execute("SELECT count(*) FROM pg_stat_activity")
            total_connections = cursor.fetchone()[0]
    except:
        db_size = 'N/A'
        active_connections = 'N/A'
        total_connections = 'N/A'
    
    # آمار media files
    try:
        media_path = os.path.join(settings.BASE_DIR, 'media')
        media_size = 0
        media_files = 0
        for dirpath, dirnames, filenames in os.walk(media_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    media_size += os.path.getsize(fp)
                    media_files += 1
        media_size_mb = round(media_size / (1024**2), 2)  # MB
    except:
        media_size_mb = 'N/A'
        media_files = 'N/A'
    
    # آمار session های فعال
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now()).count()
    
    context = {
        'title': 'گزارش وضعیت سیستم',
        # آمار کاربران
        'total_users': total_users,
        'active_users_today': active_users_today,
        'active_users_week': active_users_week,
        'active_users_month': active_users_month,
        'new_users_today': new_users_today,
        'active_sessions': active_sessions,
        
        # آمار محصولات
        'total_products': total_products,
        'approved_products': approved_products,
        'pending_products': pending_products,
        'featured_products': featured_products,
        'discounted_products': discounted_products,
        'products_today': products_today,
        
        # آمار عمومی
        'total_categories': total_categories,
        'total_cities': total_cities,
        'total_jobs': total_jobs,
        'total_requests': total_requests,
        
        # آمار سیستم
        'system_stats': system_stats,
        'db_size': db_size,
        'active_connections': active_connections,
        'total_connections': total_connections,
        'media_size_mb': media_size_mb,
        'media_files': media_files,
        
        # زمان
        'current_time': timezone.now(),
    }
    
    return render(request, 'admin/system_status.html', context)

def sitemap(request):
    """تولید فایل sitemap.xml"""
    # Get all approved products
    products = Product.objects.filter(is_approved=True).order_by('-created_at')
    
    # Get all categories
    categories = Category.objects.all()
    
    # Get all cities
    cities = City.objects.all()
    
    # Get all tags
    tags = Tag.objects.all()
    
    # Get the current time
    current_time = timezone.now().strftime('%Y-%m-%d')
    
    # Render the sitemap template
    sitemap_xml = render_to_string('sitemap.xml', {
        'products': products,
        'categories': categories,
        'cities': cities,
        'tags': tags,
        'current_time': current_time,
    })
    
    # Return the XML response
    return HttpResponse(sitemap_xml, content_type='application/xml')

def robots(request):
    """تولید فایل robots.txt"""
    robots_txt = render_to_string('robots.txt', {
        'sitemap_url': request.build_absolute_uri(reverse('app:sitemap'))
    })
    return HttpResponse(robots_txt, content_type='text/plain')

@login_required
def edit_profile(request):
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'full_name': request.user.get_full_name() or request.user.username,
            'contact': request.user.username,
            'password': 'simple_password_123'
        }
    )
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update the profile with new data
            profile.full_name = form.cleaned_data['name']
            profile.contact = form.cleaned_data['contact']
            if form.cleaned_data.get('password'):
                profile.password = form.cleaned_data['password']
            if form.cleaned_data.get('avatar'):
                profile.avatar = form.cleaned_data['avatar']
            profile.save()
            messages.success(request, _('پروفایل شما با موفقیت بروزرسانی شد.'))
            return redirect('app:user_dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    return render(request, 'edit_profile.html', {
        'form': form,
        'title': _('ویرایش پروفایل')
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('رمز عبور شما با موفقیت تغییر کرد.'))
            return redirect('app:user_dashboard')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'change_password.html', {
        'form': form,
        'title': _('تغییر رمز عبور')
    })

@login_required
def update_notification_settings(request):
    if request.method == 'POST':
        email_notifications = request.POST.get('email_notifications') == 'on'
        sms_notifications = request.POST.get('sms_notifications') == 'on'
        
        profile = request.user.profile
        profile.email_notifications = email_notifications
        profile.sms_notifications = sms_notifications
        profile.save()
        
        messages.success(request, _('تنظیمات اعلان‌ها با موفقیت بروزرسانی شد.'))
        return redirect('app:user_dashboard')
    
    return redirect('app:user_dashboard')

def jobs_list(request):
    """نمایش لیست آگهی‌های شغلی با سرچ ساده"""
    query = request.GET.get('q', '')
    city_id = request.GET.get('city')
    jobs = JobAd.objects.all()
    if query:
        jobs = jobs.filter(title__icontains=query) | jobs.filter(description__icontains=query)
    if city_id:
        jobs = jobs.filter(city_id=city_id)
    jobs = jobs.order_by('-created_at')
    cities = City.objects.all()
    context = {
        'jobs': jobs,
        'query': query,
        'cities': cities,
        'selected_city': city_id,
    }
    return render(request, 'jobs/jobs_list.html', context)

@login_required
def jobad_create(request):
    """ثبت آگهی شغلی جدید"""
    if request.method == 'POST':
        form = JobAdForm(request.POST)
        if form.is_valid():
            jobad = form.save(commit=False)
            if hasattr(request.user, 'userprofile'):
                jobad.owner_profile_id = request.user.userprofile.profile_id
            jobad.save()
            messages.success(request, 'آگهی شغلی با موفقیت ثبت شد.')
            return redirect('app:jobs_list')
    else:
        initial = {}
        if hasattr(request.user, 'userprofile'):
            initial['owner_profile_id'] = request.user.userprofile.profile_id
        form = JobAdForm(initial=initial)
    return render(request, 'jobs/jobad_create.html', {'form': form})

def jobad_detail(request, pk):
    from django.shortcuts import get_object_or_404
    job = get_object_or_404(JobAd, pk=pk)
    return render(request, 'jobs/jobad_detail.html', {'job': job})

@login_required
def delete_jobad(request, pk):
    from django.shortcuts import get_object_or_404, redirect
    from .models import UserProfile
    # دریافت پروفایل کاربر فعلی
    profile = get_object_or_404(UserProfile, user=request.user)
    # فقط اگر آگهی متعلق به این پروفایل بود اجازه حذف بده
    job = get_object_or_404(JobAd, pk=pk, owner_profile_id=profile.profile_id)
    job.delete()
    return redirect('app:user_dashboard')

@staff_member_required
def contact_messages(request):
    """صفحه مدیریت پیام‌های تماس"""
    messages_list = UserFeedback.objects.all().order_by('-timestamp')
    
    # فیلتر بر اساس جستجو
    search_query = request.GET.get('q', '')
    if search_query:
        messages_list = messages_list.filter(
            Q(email__icontains=search_query) |
            Q(subject__icontains=search_query) |
            Q(message__icontains=search_query)
        )
    
    # فیلتر بر اساس تاریخ
    date_filter = request.GET.get('date', '')
    if date_filter:
        if date_filter == 'today':
            messages_list = messages_list.filter(timestamp__date=timezone.now().date())
        elif date_filter == 'week':
            messages_list = messages_list.filter(timestamp__gte=timezone.now() - timedelta(days=7))
        elif date_filter == 'month':
            messages_list = messages_list.filter(timestamp__gte=timezone.now() - timedelta(days=30))
    
    context = {
        'messages': messages_list,
        'search_query': search_query,
        'date_filter': date_filter,
        'total_messages': UserFeedback.objects.count(),
        'today_messages': UserFeedback.objects.filter(timestamp__date=timezone.now().date()).count(),
    }
    return render(request, 'admin/contact_messages.html', context)

def requests_list(request):
    """نمایش لیست درخواستی‌ها"""
    requests_list = Request.objects.filter(is_active=True).order_by('-created_at')
    
    # فیلتر بر اساس جستجو
    search_query = request.GET.get('q', '')
    if search_query:
        requests_list = requests_list.filter(
            Q(request_text__icontains=search_query) |
            Q(contact__icontains=search_query)
        )
    
    context = {
        'requests': requests_list,
        'search_query': search_query,
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'requests/requests_list.html', context)

@login_required
def request_create(request):
    """ثبت درخواست جدید"""
    if request.method == 'POST':
        form = RequestForm(request.POST)
        if form.is_valid():
            request_obj = form.save(commit=False)
            request_obj.user = request.user
            request_obj.save()
            messages.success(request, 'درخواست شما با موفقیت ثبت شد.')
            return redirect('app:requests_list')
    else:
        form = RequestForm()
    
    context = {
        'form': form
    }
    context.update(get_cities_context(request))
    context.update(get_categories_context())
    return render(request, 'requests/request_create.html', context)

@login_required
def delete_user_request(request, pk):
    """حذف درخواست کاربر"""
    request_obj = get_object_or_404(Request, pk=pk)
    if request_obj.user == request.user:
        request_obj.delete()
        messages.success(request, 'درخواست شما با موفقیت حذف شد.')
    return redirect('app:user_dashboard')
