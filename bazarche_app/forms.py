from django import forms
from .models import UserFeedback, Product, Tag, UserProfile, Category, City, JobAd, Request
from django.utils import translation
from django.contrib.auth.models import User
import re
from django.utils.translation import gettext_lazy as _

AFGHANISTAN_PROVINCES = [
    'کابل', 'هرات', 'بلخ', 'قندهار', 'ننگرهار', 'پکتیا', 'پکتیکا', 'خوست', 'غزنی', 'بامیان',
    'پروان', 'کاپیسا', 'لوگر', 'وردک', 'فراه', 'بادغیس', 'جوزجان', 'سرپل', 'سمنگان', 'تخار',
    'کندز', 'بدخشان', 'نورستان', 'لغمان', 'کنر', 'هلمند', 'زابل', 'ارزگان', 'دایکندی', 'فاریاب',
    'پنجشیر'
]

class UserFeedbackForm(forms.ModelForm):
    class Meta:
        model = UserFeedback
        fields = ['email', 'subject', 'message']
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ایمیل یا شماره تلفن شما'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'موضوع پیام'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'متن پیام خود را وارد کنید'}),
        }
        labels = {
            'email': 'ایمیل یا شماره تلفن',
            'subject': 'موضوع',
            'message': 'پیام',
        }

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(name_fa__in=[
            'وسایل نقلیه', 'لوازم دیجیتال', 'لوازم خانگی', 'وسایل شخصی',
            'سرگرمی و فراغت', 'تجهیزات و صنعتی', 'املاک'
        ]).order_by('order', 'name_fa'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='دسته‌بندی'
    )
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='شهر'
    )
    tags = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.RadioSelect,
        required=True,
        label='وضعیت محصول'
    )
    price_range = forms.ChoiceField(
        choices=[
            ('0-1000', '0 - 1,000 افغانی'),
            ('1000-5000', '1,000 - 5,000 افغانی'),
            ('5000-10000', '5,000 - 10,000 افغانی'),
            ('10000-50000', '10,000 - 50,000 افغانی'),
            ('50000-100000', '50,000 - 100,000 افغانی'),
            ('100000+', 'بیش از 100,000 افغانی'),
        ],
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='رنج قیمت'
    )
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='نام محصول'
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control'}),
        label='توضیحات'
    )
    seller_contact = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تماس یا ایمیل'}),
        label='اطلاعات تماس'
    )
    terms_accepted = forms.BooleanField(
        label=_('قوانین و مقررات را مطالعه کرده و می‌پذیرم'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=True,
        error_messages={'required': _("پذیرش قوانین و مقررات الزامی است.")}
    )

    class Meta:
        model = Product
        fields = [
            'category', 'city', 'price', 'discount_price',
            'is_featured', 'is_discounted', 'seller_contact', 'tags',
            'price_range'
        ]
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'discount_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_discounted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seller_contact': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'category': 'دسته‌بندی',
            'city': 'شهر',
            'price': 'قیمت',
            'discount_price': 'قیمت تخفیف‌خورده',
            'is_featured': 'ویژه',
            'is_discounted': 'تخفیف‌دار',
            'seller_contact': 'اطلاعات تماس فروشنده',
            'tags': 'برچسب‌ها',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_lang = translation.get_language()
        if self.instance:
            if current_lang == 'ps':
                self.fields['name'].initial = self.instance.name_ps
                self.fields['description'].initial = self.instance.description_ps
            elif current_lang == 'en':
                self.fields['name'].initial = self.instance.name_en
                self.fields['description'].initial = self.instance.description_en
            else:
                self.fields['name'].initial = self.instance.name_fa
                self.fields['description'].initial = self.instance.description_fa
        self.fields['description'].required = False
        self.fields['city'].required = False
        self.fields['price'].required = False
        self.fields['discount_price'].required = False
        self.fields['seller_contact'].required = True
        self.fields['name'].required = True

    def clean_images(self):
        # حذف اعتبارسنجی اینجا چون در view مدیریت می‌شود
        return None

class UserRegistrationForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label=_('نام و نام خانوادگی'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('نام و نام خانوادگی خود را وارد کنید')})
    )
    contact = forms.CharField(
        max_length=100,
        label=_('شماره تماس یا ایمیل'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('شماره تماس یا ایمیل خود را وارد کنید')})
    )
    password = forms.CharField(
        label=_('رمز عبور'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('رمز عبور خود را وارد کنید')}),
        help_text=_('رمز عبور قابل مشاهده است')
    )
    terms_accepted = forms.BooleanField(
        label=_('قوانین و مقررات را مطالعه کرده و می‌پذیرم'),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        required=True,
        error_messages={'required': _("پذیرش قوانین و مقررات الزامی است.")}
    )

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'contact']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تماس یا ایمیل'}),
        }
        labels = {
            'full_name': 'نام کامل',
            'contact': 'شماره تماس یا ایمیل',
        }

class UserProfileForm(forms.ModelForm):
    name = forms.CharField(
        max_length=100,
        label=_('نام و نام خانوادگی'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('نام و نام خانوادگی')})
    )
    contact = forms.CharField(
        max_length=100,
        label=_('شماره تماس یا ایمیل'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('شماره تماس یا ایمیل')})
    )
    password = forms.CharField(
        label=_('رمز عبور'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('رمز عبور')}),
        help_text=_('رمز عبور قابل مشاهده است'),
        required=False
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label=_('تصویر پروفایل (اختیاری)')
    )

    class Meta:
        model = UserProfile
        fields = ['avatar']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['name'].initial = self.instance.full_name
            self.fields['contact'].initial = self.instance.contact

class JobAdForm(forms.ModelForm):
    owner_profile_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    class Meta:
        model = JobAd
        fields = ['title', 'description', 'contact', 'city', 'owner_profile_id']

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['request_text', 'contact']
        widgets = {
            'request_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'درخواست خود را اینجا بنویسید...',
                'rows': 4
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'شماره تماس یا ایمیل'
            })
        }
        labels = {
            'request_text': 'متن درخواست',
            'contact': 'شماره تماس'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان شغل'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'توضیحات و مشخصات فنی کار'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'شماره تماس یا راه ارتباطی'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'عنوان شغل',
            'description': 'توضیحات/مشخصات فنی کار',
            'contact': 'شماره تماس/راه ارتباطی',
            'city': 'شهر',
        }
