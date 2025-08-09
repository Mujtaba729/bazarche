from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bazarche_app.models import UserProfile
import os

class Command(BaseCommand):
    help = 'Create admin user for production'

    def add_arguments(self, parser):
        # ثابت می‌کنیم تا همیشه همین کاربر ساخته شود
        parser.add_argument('--username', type=str, default='Mujtaba729', help='Admin username')
        parser.add_argument('--email', type=str, default='Mujtabahabibi729@gmail.com', help='Admin email')
        parser.add_argument('--password', type=str, default='Mujtaba$729', help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password') or 'Mujtaba$729'
        
        # Check if admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'کاربر {username} قبلاً وجود دارد')
            )
            return
        
        # Create or update superuser to desired credentials
        user, created = User.objects.get_or_create(username=username, defaults={
            'email': email,
            'is_superuser': True,
            'is_staff': True,
        })
        if created:
            user.set_password(password)
            user.save()
        else:
            # همواره رمز و ایمیل را به مقدار ثابت بروزرسانی کن
            user.email = email
            user.is_superuser = True
            user.is_staff = True
            user.set_password(password)
            user.save()
        
        # Create profile
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'full_name': 'مدیر سایت سودآوا',
                    'contact': '070-000-0000',
                    'password': 'simple_password_123'
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ کاربر مدیر {username} با موفقیت ایجاد شد')
            )
            self.stdout.write(f'📧 ایمیل: {email}')
            self.stdout.write(f'🔐 رمز عبور: {password}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'خطا در ایجاد پروفایل: {e}')
            )
