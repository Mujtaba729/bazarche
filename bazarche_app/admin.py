from django.contrib import admin
from .models import Product, ProductImage, Category, Tag, VisitLog, UserFeedback, MainCategory, SubCategory, AbuseReport, Advertisement, Request

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
