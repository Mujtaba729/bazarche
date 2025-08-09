from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from bazarche_app.models import UserProfile
import os

class Command(BaseCommand):
    help = 'Create admin user for production'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, default='admin', help='Admin username')
        parser.add_argument('--email', type=str, default='admin@soodava.com', help='Admin email')
        parser.add_argument('--password', type=str, help='Admin password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options.get('password') or 'admin123456'
        
        # Check if admin already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'کاربر {username} قبلاً وجود دارد')
            )
            return
        
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Create profile
        try:
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'phone_number': '070-000-0000',
                    'bio': 'مدیر سایت سودآوا',
                    'email_notifications': True,
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
