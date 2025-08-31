from django.contrib import admin
from .models import Product, ProductImage, Category, Tag, VisitLog, UserFeedback, MainCategory, SubCategory, AbuseReport, Advertisement, Request, AdminAlert

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_ps', 'name_en', 'icon', 'order')
    list_editable = ('order',)
    search_fields = ('name_fa', 'name_ps', 'name_en')
    ordering = ('order', 'name_fa')

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'main_category', 'icon', 'order')
    list_filter = ('main_category',)
    list_editable = ('order',)
    search_fields = ('name_fa', 'name_ps', 'name_en')
    ordering = ('main_category', 'order', 'name_fa')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'is_featured', 'is_discounted', 'is_suggested', 'city')
    list_filter = ('is_featured', 'is_discounted', 'is_suggested', 'city', 'featured_cities', 'discounted_cities', 'suggested_cities')
    filter_horizontal = ('tags', 'featured_cities', 'discounted_cities', 'suggested_cities')
    fieldsets = (
        (None, {
            'fields': ('name_fa', 'category', 'city', 'price', 'discount_price', 'seller_contact', 'is_approved')
        }),
        ('ویژگی‌ها', {
            'fields': ('is_featured', 'featured_cities', 'is_discounted', 'discounted_cities', 'is_suggested', 'suggested_cities', 'tags', 'price_range')
        }),
    )
admin.site.unregister(Product)
admin.site.register(Product, ProductAdmin)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_fa', 'name_ps', 'name_en')
    search_fields = ('name_fa', 'name_ps', 'name_en')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name_fa',)
    search_fields = ('name_fa', 'name_ps', 'name_en')

@admin.register(VisitLog)
class VisitLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'visit_count', 'date')
    list_filter = ('date',)

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'subject', 'short_message', 'timestamp', 'user')
    list_filter = ('timestamp',)
    search_fields = ('email', 'subject', 'message')
    readonly_fields = ('timestamp', 'user')
    ordering = ('-timestamp',)
    
    def short_message(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    short_message.short_description = 'پیام'

@admin.register(AbuseReport)
class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ('product', 'report_type', 'created_at', 'is_reviewed')
    list_filter = ('report_type', 'is_reviewed', 'created_at')
    search_fields = ('product__name_fa', 'description')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'is_active', 'start_date', 'end_date', 'created_at', 'display_position')
    list_filter = ('location', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_editable = ('is_active',)
    filter_horizontal = ('cities',)
    
    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': ('title', 'description', 'image', 'link')
        }),
        ('تنظیمات نمایش', {
            'fields': ('location', 'is_active', 'display_order', 'cities')
        }),
        ('زمان‌بندی', {
            'fields': ('start_date', 'end_date')
        }),
    )
    
    def display_position(self, obj):
        if obj.location == 'home':
            return 'صفحه اصلی'
        elif obj.location == 'products':
            return 'بین محصولات'
        elif obj.location == 'sidebar':
            return 'نوار کناری'
        else:
            return obj.location
    display_position.short_description = 'محل نمایش'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('contact', 'short_request', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('request_text', 'contact')
    readonly_fields = ('created_at', 'user')
    ordering = ('-created_at',)
    
    def short_request(self, obj):
        return obj.request_text[:100] + '...' if len(obj.request_text) > 100 else obj.request_text
    short_request.short_description = 'درخواست'

@admin.register(AdminAlert)
class AdminAlertAdmin(admin.ModelAdmin):
    list_display = ('user', 'count_last_hour', 'count_last_day', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    ordering = ('-created_at',)

# UserProfile Admin
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'profile_id', 'contact', 'created_at', 'user')
    list_filter = ('created_at',)
    search_fields = ('full_name', 'contact', 'profile_id', 'user__username')
    readonly_fields = ('profile_id', 'created_at', 'user')
    ordering = ('-created_at',)
    
    def full_name(self, obj):
        return obj.full_name if obj.full_name else 'نام ثبت نشده'
    full_name.short_description = 'نام و نام خانوادگی'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

# Customize User Admin to show all info in Users section
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'full_name', 'profile_id', 'contact', 'email', 'date_joined', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__full_name', 'userprofile__contact')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('اطلاعات پروفایل', {'fields': ('get_profile_info',)}),
    )
    
    readonly_fields = ('date_joined', 'get_profile_info')
    
    def full_name(self, obj):
        try:
            return obj.userprofile.full_name if obj.userprofile.full_name else f"{obj.first_name} {obj.last_name}".strip() or 'نام ثبت نشده'
        except:
            return f"{obj.first_name} {obj.last_name}".strip() or 'نام ثبت نشده'
    full_name.short_description = 'نام و نام خانوادگی'
    
    def profile_id(self, obj):
        try:
            return obj.userprofile.profile_id if obj.userprofile.profile_id else 'شناسه ندارد'
        except:
            return 'شناسه ندارد'
    profile_id.short_description = 'شناسه کاربری'
    
    def contact(self, obj):
        try:
            return obj.userprofile.contact if obj.userprofile.contact else 'شماره ندارد'
        except:
            return 'شماره ندارد'
    contact.short_description = 'شماره تماس'
    
    def get_profile_info(self, obj):
        try:
            profile = obj.userprofile
            return f"شناسه: {profile.profile_id}, شماره: {profile.contact}, تاریخ ایجاد: {profile.created_at}"
        except:
            return 'پروفایل موجود نیست'
    get_profile_info.short_description = 'اطلاعات پروفایل'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('userprofile')

# Unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
