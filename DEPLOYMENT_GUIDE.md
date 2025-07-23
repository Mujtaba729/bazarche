# راهنمای کامل فعال‌سازی و مدیریت سایت بازارچه

## 🚀 مرحله ۱: فعال‌سازی سایت روی سرور

### گزینه‌های مختلف برای هاستینگ:

#### ۱. هاستینگ رایگان (برای شروع):
- **Vercel**: برای استاتیک سایت‌ها
- **Netlify**: برای استاتیک سایت‌ها  
- **Railway**: برای Django (محدودیت زمانی)
- **Render**: برای Django (محدودیت زمانی)

#### ۲. هاستینگ پولی (توصیه شده):
- **DigitalOcean**: از ۵ دلار در ماه
- **AWS**: از ۳ دلار در ماه
- **Google Cloud**: از ۵ دلار در ماه
- **Heroku**: از ۷ دلار در ماه

### تنظیمات مهم برای Production:

```python
# در فایل settings.py تغییر دهید:
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# اضافه کردن SECRET_KEY جدید
SECRET_KEY = 'your-new-secret-key-here'

# تنظیمات امنیتی
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

---

## 🔐 مرحله ۲: دسترسی به پنل مدیریت

### آدرس‌های مهم:
- **پنل مدیریت Django**: `your-domain.com/admin/`
- **آمار مدیریت**: `your-domain.com/app/admin-stats/`
- **مدیریت محصولات**: `your-domain.com/app/manage/products/`
- **گزارش‌های تخلف**: `your-domain.com/app/admin/abuse-reports/`

### ایجاد اکانت ادمین:
```bash
python manage.py createsuperuser
```

---

## 💾 مرحله ۳: مدیریت دیتابیس

### انتقال دیتابیس:
```bash
# بکاپ از دیتابیس محلی
python manage.py dumpdata > backup.json

# انتقال به سرور
python manage.py loaddata backup.json
```

### تنظیمات دیتابیس Production:
```python
# برای PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

---

## 🖥️ مرحله ۴: سرور و کامپیوتر

### سوال مهم: آیا کامپیوتر باید همیشه روشن باشد؟

**پاسخ: خیر!** اگر از هاستینگ ابری استفاده کنید:

#### ✅ گزینه‌های بدون نیاز به کامپیوتر:
1. **DigitalOcean Droplet**: سرور مجازی ۲۴/۷
2. **AWS EC2**: سرور ابری
3. **Google Cloud**: سرور ابری
4. **Heroku**: پلتفرم ابری

#### ❌ گزینه‌هایی که نیاز به کامپیوتر دارند:
- اجرای سرور روی کامپیوتر شخصی
- استفاده از ngrok (موقت)

### توصیه:
**از هاستینگ ابری استفاده کنید** تا سایت همیشه در دسترس باشد.

---

## ⚡ مرحله ۵: بهینه‌سازی و کش

### تنظیمات کش برای Production:
```python
# Redis برای کش (توصیه شده)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### نصب Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# CentOS/RHEL
sudo yum install redis
```

---

## 🔒 مرحله ۶: امنیت

### تنظیمات امنیتی ضروری:
```python
# در settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### SSL Certificate:
- **Let's Encrypt**: رایگان
- **Cloudflare**: رایگان
- **هوستینگ‌ها**: معمولاً رایگان

---

## 📊 مرحله ۷: مانیتورینگ و آمار

### ابزارهای مانیتورینگ:
1. **Google Analytics**: آمار بازدید
2. **Sentry**: ثبت خطاها
3. **UptimeRobot**: مانیتورینگ آپتایم
4. **Django Debug Toolbar**: برای توسعه

### دستورات مفید:
```bash
# بررسی وضعیت سرور
python manage.py check --deploy

# جمع‌آوری فایل‌های استاتیک
python manage.py collectstatic

# بهینه‌سازی دیتابیس
python manage.py dbshell
```

---

## 🚨 مرحله ۸: بکاپ و بازیابی

### بکاپ خودکار:
```bash
# اسکریپت بکاپ روزانه
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
python manage.py dumpdata > backup_$DATE.json
```

### بازیابی:
```bash
python manage.py loaddata backup_20241201_143022.json
```

---

## 📱 مرحله ۹: تست و بررسی

### چک‌لیست قبل از انتشار:
- [ ] DEBUG = False
- [ ] SECRET_KEY تغییر کرده
- [ ] ALLOWED_HOSTS تنظیم شده
- [ ] SSL فعال است
- [ ] بکاپ گرفته شده
- [ ] اکانت ادمین ایجاد شده
- [ ] فایل‌های استاتیک جمع‌آوری شده

### تست‌های ضروری:
1. ثبت محصول جدید
2. جستجو در سایت
3. تغییر زبان
4. پنل مدیریت
5. فرم تماس

---

## 🆘 مرحله ۱۰: عیب‌یابی

### مشکلات رایج:

#### مشکل: سایت لود نمی‌شود
```bash
# بررسی لاگ‌ها
tail -f /var/log/nginx/error.log
tail -f /var/log/django.log
```

#### مشکل: خطای ۵۰۰
```python
# در settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

## 📞 پشتیبانی و منابع

### منابع مفید:
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/)
- [DigitalOcean Django Tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-20-04)
- [Django Security](https://docs.djangoproject.com/en/5.1/topics/security/)

### نکات مهم:
1. **همیشه بکاپ بگیرید** قبل از هر تغییر
2. **از محیط مجازی استفاده کنید**
3. **رمزهای عبور قوی انتخاب کنید**
4. **به‌روزرسانی‌ها را نصب کنید**
5. **لاگ‌ها را بررسی کنید**

---

## 🎯 خلاصه مراحل:

1. **انتخاب هاستینگ** → DigitalOcean یا AWS
2. **انتقال کد** → Git یا FTP
3. **تنظیم دیتابیس** → PostgreSQL
4. **تنظیمات امنیتی** → SSL و HTTPS
5. **ایجاد ادمین** → `createsuperuser`
6. **تست کامل** → همه قابلیت‌ها
7. **مانیتورینگ** → Google Analytics
8. **بکاپ خودکار** → روزانه

**نکته مهم**: سایت شما روی سرور ابری اجرا می‌شود، پس نیازی به روشن نگه داشتن کامپیوتر نیست! 🎉 