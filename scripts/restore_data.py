#!/usr/bin/env python
"""
Script to restore data from backup file to PostgreSQL
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings_railway')
django.setup()

from django.core import serializers
from django.contrib.auth.models import User
from django.db import transaction
from bazarche_app.models import *

def restore_data(backup_file):
    """Restore data from backup file"""
    
    if not os.path.exists(backup_file):
        print(f"❌ فایل backup پیدا نشد: {backup_file}")
        return False
    
    print(f"🔄 شروع restore از: {backup_file}")
    
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
                print(f"⚠️  داده‌ای برای {model_name} در backup موجود نیست")
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
                        print(f"⚠️  خطا در ذخیره {model_name} object: {e}")
                        continue
                
                total_restored += count
                print(f"✅ {model_name}: {count} رکورد restore شد")
                
            except Exception as e:
                print(f"❌ خطا در restore {model_name}: {e}")
                continue
    
    print(f"\n🎉 Restore تکمیل شد!")
    print(f"📊 کل رکوردهای restore شده: {total_restored}")
    
    return True

def find_latest_backup():
    """Find the latest backup file"""
    scripts_dir = os.path.dirname(__file__)
    backup_files = [f for f in os.listdir(scripts_dir) if f.startswith('data_backup_') and f.endswith('.json')]
    
    if not backup_files:
        return None
    
    # Sort by filename (which includes timestamp)
    backup_files.sort(reverse=True)
    return os.path.join(scripts_dir, backup_files[0])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        backup_file = sys.argv[1]
    else:
        backup_file = find_latest_backup()
        if not backup_file:
            print("❌ هیچ فایل backup پیدا نشد!")
            sys.exit(1)
        print(f"📁 استفاده از آخرین backup: {backup_file}")
    
    success = restore_data(backup_file)
    if success:
        print("\n✨ داده‌ها با موفقیت restore شدند!")
    else:
        print("\n❌ خطا در restore داده‌ها!")
        sys.exit(1)
