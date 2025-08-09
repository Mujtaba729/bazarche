#!/usr/bin/env python
"""
Script to backup current data before migration to PostgreSQL
"""

import os
import sys
import django
import json
from datetime import datetime

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')
django.setup()

from django.core import serializers
from django.contrib.auth.models import User
from bazarche_app.models import *

def backup_data():
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
    
    print("🔄 شروع backup داده‌ها...")
    
    for model_name, model_class in models_to_backup:
        try:
            queryset = model_class.objects.all()
            serialized_data = serializers.serialize('json', queryset)
            backup_data['data'][model_name] = json.loads(serialized_data)
            count = queryset.count()
            print(f"✅ {model_name}: {count} رکورد backup شد")
        except Exception as e:
            print(f"❌ خطا در backup {model_name}: {e}")
            backup_data['data'][model_name] = []
    
    # Save backup file
    backup_file = f"scripts/data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Backup ذخیره شد: {backup_file}")
    print(f"📊 کل رکوردها: {sum(len(data) for data in backup_data['data'].values())}")
    
    return backup_file

if __name__ == "__main__":
    backup_file = backup_data()
    print(f"\n🎉 Backup با موفقیت انجام شد!")
    print(f"📁 فایل: {backup_file}")
