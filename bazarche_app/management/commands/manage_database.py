from django.core.management.base import BaseCommand
from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from bazarche_app.models import *
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Manage database backup and restore operations'

    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['backup', 'restore', 'migrate-to-postgres'],
            help='Action to perform'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Backup file path for restore operation'
        )
        parser.add_argument(
            '--monitor-posts',
            action='store_true',
            help='Report users with high product posting rate in recent window'
        )

    def handle(self, *args, **options):
        action = options['action']
        if options.get('monitor_posts'):
            from django.utils import timezone
            from datetime import timedelta
            from django.db import models as dj_models
            window_minutes = 10
            threshold = 15
            since = timezone.now() - timedelta(minutes=window_minutes)
            qs = (
                Product.objects.filter(created_at__gte=since)
                .values('user__username')
                .annotate(count=dj_models.Count('id'))
                .filter(count__gte=threshold)
                .order_by('-count')
            )
            if qs:
                self.stdout.write(self.style.WARNING(f"Users over threshold in last {window_minutes}m:"))
                for row in qs:
                    self.stdout.write(f" - {row['user__username']}: {row['count']}")
            else:
                self.stdout.write("No users above threshold in the last window.")
            return
        
        if action == 'backup':
            self.backup_data()
        elif action == 'restore':
            backup_file = options.get('file')
            if not backup_file:
                backup_file = self.find_latest_backup()
            if backup_file:
                self.restore_data(backup_file)
            else:
                self.stdout.write(self.style.ERROR('❌ هیچ فایل backup پیدا نشد!'))
        elif action == 'migrate-to-postgres':
            self.migrate_to_postgres()

    def backup_data(self):
        """Create a backup of all important data"""
        
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'data': {}
        }
        
        # Models to backup
        models_to_backup = [
            ('users', User),
            ('main_categories', MainCategory),
            ('categories', Category),
            ('cities', City),
            ('user_profiles', UserProfile),
            ('products', Product),
            ('advertisements', Advertisement),
            ('job_ads', JobAd),
            ('requests', Request),
            ('abuse_reports', AbuseReport),
        ]
        
        self.stdout.write("🔄 شروع backup داده‌ها...")
        
        for model_name, model_class in models_to_backup:
            try:
                queryset = model_class.objects.all()
                serialized_data = serializers.serialize('json', queryset)
                backup_data['data'][model_name] = json.loads(serialized_data)
                count = queryset.count()
                self.stdout.write(f"✅ {model_name}: {count} رکورد backup شد")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"❌ خطا در backup {model_name}: {e}"))
                backup_data['data'][model_name] = []
        
        # Save backup file
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        backup_file = os.path.join(backup_dir, f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f"💾 Backup ذخیره شد: {backup_file}"))
        self.stdout.write(f"📊 کل رکوردها: {sum(len(data) for data in backup_data['data'].values())}")
        
        return backup_file

    def restore_data(self, backup_file):
        """Restore data from backup file"""
        
        if not os.path.exists(backup_file):
            self.stdout.write(self.style.ERROR(f"❌ فایل backup پیدا نشد: {backup_file}"))
            return False
        
        self.stdout.write(f"🔄 شروع restore از: {backup_file}")
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        # Order matters for foreign key dependencies
        restore_order = [
            'users',
            'main_categories', 
            'categories',
            'cities',
            'user_profiles',
            'products',
            'advertisements',
            'job_ads',
            'requests',
            'abuse_reports',
        ]
        
        total_restored = 0
        
        with transaction.atomic():
            for model_name in restore_order:
                if model_name not in backup_data['data']:
                    self.stdout.write(self.style.WARNING(f"⚠️  داده‌ای برای {model_name} در backup موجود نیست"))
                    continue
                    
                try:
                    # Deserialize and save
                    data_json = json.dumps(backup_data['data'][model_name])
                    objects = serializers.deserialize('json', data_json)
                    
                    count = 0
                    for obj in objects:
                        try:
                            obj.save()
                            count += 1
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f"⚠️  خطا در ذخیره {model_name} object: {e}"))
                            continue
                    
                    total_restored += count
                    self.stdout.write(f"✅ {model_name}: {count} رکورد restore شد")
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ خطا در restore {model_name}: {e}"))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Restore تکمیل شد!"))
        self.stdout.write(f"📊 کل رکوردهای restore شده: {total_restored}")
        
        return True

    def find_latest_backup(self):
        """Find the latest backup file"""
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            return None
            
        backup_files = [f for f in os.listdir(backup_dir) if f.startswith('data_backup_') and f.endswith('.json')]
        
        if not backup_files:
            return None
        
        # Sort by filename (which includes timestamp)
        backup_files.sort(reverse=True)
        return os.path.join(backup_dir, backup_files[0])

    def migrate_to_postgres(self):
        """Complete migration process to PostgreSQL"""
        self.stdout.write(self.style.SUCCESS("🚀 شروع مهاجرت به PostgreSQL..."))
        
        # Step 1: Create backup
        self.stdout.write("1️⃣ ایجاد backup از داده‌های فعلی...")
        backup_file = self.backup_data()
        
        # Step 2: Instructions for user
        self.stdout.write(self.style.SUCCESS("\n✨ مراحل بعدی:"))
        self.stdout.write("2️⃣ در Railway dashboard:")
        self.stdout.write("   - یک PostgreSQL service اضافه کنید")
        self.stdout.write("   - DATABASE_URL environment variable را تنظیم کنید")
        self.stdout.write("3️⃣ دستورات زیر را اجرا کنید:")
        self.stdout.write("   python manage.py migrate --settings=bazarche_project.settings_railway")
        self.stdout.write(f"   python manage.py manage_database restore --file={backup_file} --settings=bazarche_project.settings_railway")
        self.stdout.write("\n📁 فایل backup: " + backup_file)
