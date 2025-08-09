#!/usr/bin/env python
"""
Complete deployment script for Railway with data persistence
"""

import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - موفق!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطا در {description}:")
        print(e.stderr)
        return False

def main():
    print("🚀 شروع فرآیند دیپلوی کامل به Railway...")
    print("=" * 60)
    
    # Step 1: Create backup of current data
    print("\n1️⃣ مرحله اول: Backup داده‌های فعلی")
    if not run_command(
        "python manage.py manage_database backup",
        "ایجاد backup از داده‌های فعلی"
    ):
        print("❌ خطا در backup! فرآیند متوقف شد.")
        return False
    
    # Step 2: Collect static files
    print("\n2️⃣ مرحله دوم: جمع‌آوری فایل‌های static")
    if not run_command(
        "python manage.py collectstatic --noinput --settings=bazarche_project.settings_railway",
        "جمع‌آوری فایل‌های static"
    ):
        print("⚠️  خطا در collectstatic - ادامه می‌دهیم...")
    
    # Step 3: Test production settings
    print("\n3️⃣ مرحله سوم: تست تنظیمات production")
    if not run_command(
        "python manage.py check --settings=bazarche_project.settings_railway",
        "بررسی تنظیمات production"
    ):
        print("❌ خطا در تنظیمات production! فرآیند متوقف شد.")
        return False
    
    # Step 4: Push to git
    print("\n4️⃣ مرحله چهارم: Push به Git")
    run_command("git add .", "اضافه کردن فایل‌ها به git")
    run_command(
        f'git commit -m "Production deployment - {datetime.now().strftime("%Y-%m-%d %H:%M")}"',
        "ایجاد commit"
    )
    
    if not run_command("git push", "Push به repository"):
        print("❌ خطا در push! فرآیند متوقف شد.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 فرآیند دیپلوی تکمیل شد!")
    print("\n📋 مراحل بعدی در Railway Dashboard:")
    print("1. یک PostgreSQL database اضافه کنید")
    print("2. DATABASE_URL environment variable تنظیم شود")
    print("3. DJANGO_SETTINGS_MODULE=bazarche_project.settings_railway")
    print("4. SECRET_KEY environment variable تنظیم کنید")
    print("\n📁 فایل‌های backup در پوشه backups/ ذخیره شدند")
    print("🔄 پس از راه‌اندازی PostgreSQL، دستور زیر را اجرا کنید:")
    print("   python manage.py manage_database restore")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
    print("\n✨ آماده برای استفاده!")
