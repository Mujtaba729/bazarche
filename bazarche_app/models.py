from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib import admin

class MainCategory(models.Model):
    name_fa = models.CharField(max_length=100, verbose_name=_('نام (فارسی)'))
    name_ps = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (پشتو)'))
    name_en = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (انگلیسی)'))
    icon = models.CharField(max_length=50, help_text=_('نام آیکون از Bootstrap Icons'), default='bi-tag')
    order = models.IntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ به‌روزرسانی'))

    class Meta:
        verbose_name = _('دسته‌بندی اصلی')
        verbose_name_plural = _('دسته‌بندی‌های اصلی')
        ordering = ['order', 'name_fa']

    def __str__(self):
        return self.name_fa

class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories', verbose_name=_('دسته‌بندی اصلی'))
    name_fa = models.CharField(max_length=100, verbose_name=_('نام (فارسی)'))
    name_ps = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (پشتو)'))
    name_en = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (انگلیسی)'))
    icon = models.CharField(max_length=50, help_text=_('نام آیکون از Bootstrap Icons'), default='bi-tag')
    order = models.IntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ به‌روزرسانی'))

    class Meta:
        verbose_name = _('زیردسته‌بندی')
        verbose_name_plural = _('زیردسته‌بندی‌ها')
        ordering = ['order', 'name_fa']

    def __str__(self):
        return f"{self.main_category.name_fa} - {self.name_fa}"

class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('دسته‌بندی والد'))
    name_fa = models.CharField(max_length=100, verbose_name=_('نام (فارسی)'))
    name_ps = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (پشتو)'))
    name_en = models.CharField(max_length=100, blank=True, default='', verbose_name=_('نام (انگلیسی)'))
    icon = models.CharField(max_length=50, help_text=_('نام آیکون از Bootstrap Icons'), default='bi-tag')
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)], verbose_name=_('ترتیب نمایش'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ به‌روزرسانی'))

    class Meta:
        verbose_name = _('دسته‌بندی')
        verbose_name_plural = _('دسته‌بندی‌ها')
        ordering = ['order', 'name_fa']
        unique_together = ['parent', 'name_fa']

    def clean(self):
        if self.parent and self.parent.parent:
            raise ValidationError(_('دسته‌بندی نمی‌تواند بیش از دو سطح داشته باشد.'))

    def __str__(self):
        if self.parent:
            return f"{self.parent.name_fa} - {self.name_fa}"
        return self.name_fa

    @property
    def is_main_category(self):
        return self.parent is None

    @property
    def is_sub_category(self):
        return self.parent is not None

class Tag(models.Model):
    name_fa = models.CharField(max_length=50)
    name_ps = models.CharField(max_length=50, blank=True, null=True)
    name_en = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name_fa

class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('کاربر'))
    name_fa = models.CharField(max_length=200, verbose_name=_('نام (فارسی)'))
    name_ps = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('نام (پشتو)'))
    name_en = models.CharField(max_length=200, blank=True, null=True, verbose_name=_('نام (انگلیسی)'))
    description_fa = models.TextField(blank=True, null=True, verbose_name=_('توضیحات (فارسی)'))
    description_ps = models.TextField(blank=True, null=True, verbose_name=_('توضیحات (پشتو)'))
    description_en = models.TextField(blank=True, null=True, verbose_name=_('توضیحات (انگلیسی)'))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('دسته‌بندی'))
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('شهر'))
    price = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_('قیمت'))
    discount_price = models.PositiveIntegerField(null=True, blank=True, validators=[MinValueValidator(0)], verbose_name=_('قیمت با تخفیف'))
    is_featured = models.BooleanField(default=False, verbose_name=_('ویژه'))
    is_discounted = models.BooleanField(default=False, verbose_name=_('تخفیف‌دار'))
    is_suggested = models.BooleanField(default=False, verbose_name='محصول پیشنهادی')
    featured_cities = models.ManyToManyField('City', blank=True, related_name='featured_products', verbose_name=_('شهرهای ویژه'), help_text=_('اگر هیچ شهری انتخاب نشود، محصول در همه شهرها ویژه خواهد بود.'))
    discounted_cities = models.ManyToManyField('City', blank=True, related_name='discounted_products', verbose_name=_('شهرهای تخفیفی'), help_text=_('اگر هیچ شهری انتخاب نشود، محصول در همه شهرها تخفیفی خواهد بود.'))
    suggested_cities = models.ManyToManyField('City', blank=True, related_name='suggested_products', verbose_name=_('شهرهای پیشنهادی'), help_text=_('اگر هیچ شهری انتخاب نشود، محصول در همه شهرها پیشنهادی خواهد بود.'))
    seller_contact = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('اطلاعات تماس فروشنده'))
    is_approved = models.BooleanField(default=False, verbose_name=_('تایید شده'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('برچسب‌ها'))
    price_range = models.CharField(max_length=20, choices=[
        ('0-1000', '0 - 1,000 افغانی'),
        ('1000-5000', '1,000 - 5,000 افغانی'),
        ('5000-10000', '5,000 - 10,000 افغانی'),
        ('10000-50000', '10,000 - 50,000 افغانی'),
        ('50000-100000', '50,000 - 100,000 افغانی'),
        ('100000+', 'بیش از 100,000 افغانی'),
    ], verbose_name=_('رنج قیمت'))
    
    # وضعیت محصول (نو یا دست دوم)
    CONDITION_CHOICES = [
        ('new', 'نو'),
        ('used', 'دست دوم'),
    ]
    condition = models.CharField(
        max_length=10, 
        choices=CONDITION_CHOICES, 
        default='new', 
        verbose_name=_('وضعیت محصول')
    )

    def clean(self):
        # اگر محصول تخفیف‌دار است ولی قیمت تخفیف وارد نشده
        if self.is_discounted and not self.discount_price:
            raise ValidationError(_('برای محصولات تخفیف‌دار، قیمت با تخفیف الزامی است.'))

        # اگر قیمت تخفیف وارد شده، قیمت اصلی نیز باید وارد شود و قیمت تخفیف کمتر از قیمت اصلی باشد
        if self.discount_price is not None:
            if self.price is None:
                raise ValidationError(_('برای وارد کردن قیمت تخفیف، قیمت اصلی نیز الزامی است.'))
            if self.discount_price >= self.price:
                raise ValidationError(_('قیمت با تخفیف باید کمتر از قیمت اصلی باشد.'))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_fa

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.product.name_fa}"

class VisitLog(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    visit_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Visits for {self.product.name_fa} on {self.date}"

class ErrorReport(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    path = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    stack_trace = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Error at {self.timestamp} on {self.path} - {self.message[:50]}"
    
class UserFeedback(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    email = models.EmailField(blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return f"Feedback from {self.email or 'Anonymous'} at {self.timestamp} - {self.subject}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, verbose_name=_('نام و نام خانوادگی'))
    contact = models.CharField(max_length=100, verbose_name=_('شماره تماس یا ایمیل'))
    password = models.CharField(max_length=128, verbose_name=_('رمز عبور'))
    profile_id = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name=_('شناسه کاربر'))
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name=_('تصویر پروفایل'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ایجاد'))

    def __str__(self):
        return f"{self.full_name} (ID: {self.profile_id})"

    def save(self, *args, **kwargs):
        if not self.profile_id:
            # تولید شناسه منحصر به فرد
            import random
            import string
            while True:
                profile_id = ''.join(random.choices(string.digits, k=6))
                if not UserProfile.objects.filter(profile_id=profile_id).exists():
                    self.profile_id = profile_id
                    break
        super().save(*args, **kwargs)

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_('نام شهر'))
    order = models.IntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    created_at = models.DateTimeField(default=timezone.now, verbose_name=_('تاریخ ایجاد'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('تاریخ به‌روزرسانی'))

    class Meta:
        verbose_name = _('شهر')
        verbose_name_plural = _('شهرها')
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class AbuseReport(models.Model):
    REPORT_TYPES = [
        ('fake', 'محصول تقلبی'),
        ('inappropriate', 'محتوای نامناسب'),
        ('scam', 'کلاهبرداری'),
        ('duplicate', 'تکرار آگهی'),
        ('other', 'سایر'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='abuse_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'گزارش تخلف'
        verbose_name_plural = 'گزارش‌های تخلف'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'گزارش تخلف برای {self.product.name_fa} - {self.get_report_type_display()}'

class Advertisement(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('عنوان'))
    description = models.TextField(blank=True, verbose_name=_('توضیحات'))
    image = models.ImageField(upload_to='ads/', verbose_name=_('تصویر'))
    video = models.FileField(upload_to='ads/videos/', blank=True, null=True, verbose_name=_('ویدیو'))
    link = models.URLField(blank=True, verbose_name=_('لینک'))
    location = models.CharField(
        max_length=20,
        choices=[
            ('home', _('صفحه اصلی')),
            ('products', _('بین محصولات')),
            ('sidebar', _('نوار کناری')),
        ],
        verbose_name=_('موقعیت نمایش')
    )
    cities = models.ManyToManyField('City', blank=True, verbose_name=_('شهرها'), help_text=_('اگر هیچ شهری انتخاب نشود، تبلیغ در همه شهرها نمایش داده می‌شود.'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))
    display_order = models.IntegerField(default=0, verbose_name=_('ترتیب نمایش'))
    start_date = models.DateTimeField(verbose_name=_('تاریخ شروع'))
    end_date = models.DateTimeField(verbose_name=_('تاریخ پایان'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('تبلیغ')
        verbose_name_plural = _('تبلیغات')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def is_current(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

class JobAd(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('عنوان شغل'))
    description = models.TextField(verbose_name=_('توضیحات/مشخصات فنی کار'))
    contact = models.CharField(max_length=100, verbose_name=_('شماره تماس/راه ارتباطی'))
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_('شهر'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    owner_profile_id = models.CharField(max_length=10, verbose_name=_('شناسه کاربر'), null=True, blank=True, db_index=True)

    class Meta:
        verbose_name = _('آگهی شغلی')
        verbose_name_plural = _('آگهی‌های شغلی')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Request(models.Model):
    """مدل برای درخواستی‌های کاربران"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('کاربر'))
    request_text = models.TextField(verbose_name=_('متن درخواست'))
    contact = models.CharField(max_length=100, verbose_name=_('شماره تماس'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('تاریخ ثبت'))
    is_active = models.BooleanField(default=True, verbose_name=_('فعال'))

    class Meta:
        verbose_name = _('درخواست')
        verbose_name_plural = _('درخواستی‌ها')
        ordering = ['-created_at']

    def __str__(self):
        return f"درخواست از {self.contact} - {self.created_at.strftime('%Y/%m/%d')}"

@admin.register(JobAd)
class JobAdAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'contact', 'created_at')
    search_fields = ('title', 'description', 'contact')
    list_filter = ('city', 'created_at')
    ordering = ('-created_at',)


class AdminAlert(models.Model):
    """هشدارهای مدیریتی برای فعالیت غیرمعمول کاربران"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_alerts', verbose_name=_('کاربر'))
    count_last_hour = models.PositiveIntegerField(default=0, verbose_name=_('تعداد 1 ساعت اخیر'))
    count_last_day = models.PositiveIntegerField(default=0, verbose_name=_('تعداد 24 ساعت اخیر'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('زمان ثبت'))
    note = models.CharField(max_length=255, blank=True, verbose_name=_('توضیح'))

    class Meta:
        verbose_name = _('هشدار مدیریتی')
        verbose_name_plural = _('هشدارهای مدیریتی')
        ordering = ['-created_at']

    def __str__(self):
        return f"Alert: {self.user.username} - {self.count_last_hour}/1h, {self.count_last_day}/24h"
