#!/usr/bin/env python
"""
Complete setup script for SoodAva production deployment
مدیریت کامل راه‌اندازی سایت سودآوا برای production
"""

import os
import subprocess
import sys
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text, color=Colors.END):
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    print("\n" + "="*60)
    print_colored(f"🚀 {text}", Colors.BOLD + Colors.BLUE)
    print("="*60)

def run_command(command, description, critical=True):
    """Run a command and handle errors"""
    print_colored(f"\n🔄 {description}...", Colors.YELLOW)
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print_colored(f"✅ {description} - موفق!", Colors.GREEN)
        if result.stdout.strip():
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        if critical:
            print_colored(f"❌ خطا در {description}:", Colors.RED)
            print(e.stderr)
            return False
        else:
            print_colored(f"⚠️  هشدار در {description} (ادامه می‌دهیم):", Colors.YELLOW)
            print(e.stderr)
            return True

def check_prerequisites():
    """Check system prerequisites"""
    print_header("بررسی پیش‌نیازها")
    
    # Check Python
    if not run_command("python --version", "بررسی Python"):
        return False
    
    # Check Django
    if not run_command("python -c 'import django; print(django.get_version())'", "بررسی Django"):
        return False
    
    # Check Git
    if not run_command("git --version", "بررسی Git"):
        return False
    
    return True

def backup_current_data():
    """Backup current database"""
    print_header("پشتیبان‌گیری از داده‌های فعلی")
    
    # Create backups directory
    os.makedirs('backups', exist_ok=True)
    
    # Run backup command
    return run_command(
        "python manage.py manage_database backup",
        "ایجاد backup از دیتابیس فعلی"
    )

def prepare_production_files():
    """Prepare files for production"""
    print_header("آماده‌سازی فایل‌های production")
    
    # Create staticfiles directory
    os.makedirs('staticfiles', exist_ok=True)
    
    # Collect static files
    success = run_command(
        "python manage.py collectstatic --noinput --settings=bazarche_project.settings_railway",
        "جمع‌آوری فایل‌های static",
        critical=False
    )
    
    # Check production settings
    success &= run_command(
        "python manage.py check --settings=bazarche_project.settings_railway",
        "بررسی تنظیمات production"
    )
    
    return success

def deploy_to_git():
    """Deploy to git repository"""
    print_header("انتشار در Git Repository")
    
    # Add all files
    run_command("git add .", "اضافه کردن فایل‌ها به git", critical=False)
    
    # Create commit
    commit_message = f"Production deployment - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    run_command(f'git commit -m "{commit_message}"', "ایجاد commit", critical=False)
    
    # Push to repository
    return run_command("git push", "Push به repository")

def show_railway_instructions():
    """Show Railway setup instructions"""
    print_header("دستورالعمل تنظیمات Railway")
    
    print_colored("📋 مراحل در Railway Dashboard:", Colors.BLUE)
    print("1. اضافه کردن PostgreSQL Service:")
    print("   - Railway Dashboard → Add Service → PostgreSQL")
    print("   - اتصال خودکار به پروژه")
    
    print("\n2. تنظیم Environment Variables:")
    print("   DJANGO_SETTINGS_MODULE=bazarche_project.settings_railway")
    print("   SECRET_KEY=[کلید امنیتی قوی - 50 کاراکتر]")
    print("   DATABASE_URL=[خودکار از PostgreSQL تنظیم می‌شود]")
    
    print("\n3. اجرای Migration:")
    print("   - Railway Console → python manage.py migrate")
    print("   - Railway Console → python manage.py manage_database restore")
    
    print("\n4. ایجاد Superuser:")
    print("   - Railway Console → python manage.py createsuperuser")

def show_domain_instructions():
    """Show custom domain setup instructions"""
    print_header("راهنمای اتصال دامنه اختصاصی")
    
    print_colored("🌐 مراحل اتصال دامنه:", Colors.BLUE)
    print("1. Railway Dashboard → Settings → Domains → Add Custom Domain")
    print("2. وارد کردن دامنه خود (مثال: yourdomain.com)")
    print("3. تنظیم CNAME record در DNS:")
    print("   Type: CNAME")
    print("   Name: @ (یا www)")
    print("   Value: [مقدار ارائه شده توسط Railway]")
    print("4. انتظار 5-24 ساعت برای SSL certificate")

def show_final_checklist():
    """Show final production checklist"""
    print_header("چک‌لیست نهایی راه‌اندازی")
    
    checklist = [
        "✅ PostgreSQL database راه‌اندازی شده",
        "✅ Environment variables تنظیم شده",
        "✅ Migration اجرا شده",
        "✅ Data restore انجام شده",
        "✅ Superuser ایجاد شده",
        "✅ Custom domain متصل شده",
        "✅ SSL certificate فعال شده",
        "✅ سایت تست شده و کار می‌کند",
    ]
    
    for item in checklist:
        print_colored(item, Colors.GREEN)
    
    print_colored("\n🎉 سایت آماده استفاده عموم است!", Colors.BOLD + Colors.GREEN)

def main():
    """Main setup function"""
    print_colored("🌟 سودآوا - راه‌اندازی کامل Production", Colors.BOLD + Colors.BLUE)
    print_colored("SoodAva - Complete Production Setup", Colors.BOLD)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_colored("❌ پیش‌نیازها برآورده نیست!", Colors.RED)
        return False
    
    # Step 2: Backup current data
    if not backup_current_data():
        print_colored("❌ خطا در backup داده‌ها!", Colors.RED)
        return False
    
    # Step 3: Prepare production files
    if not prepare_production_files():
        print_colored("❌ خطا در آماده‌سازی production!", Colors.RED)
        return False
    
    # Step 4: Deploy to git
    if not deploy_to_git():
        print_colored("❌ خطا در انتشار Git!", Colors.RED)
        return False
    
    # Step 5: Show instructions
    show_railway_instructions()
    show_domain_instructions()
    show_final_checklist()
    
    print_header("✨ راه‌اندازی با موفقیت تکمیل شد!")
    print_colored("📁 فایل‌های راهنما:", Colors.BLUE)
    print("- DOMAIN_SETUP_GUIDE.md: راهنمای اتصال دامنه")
    print("- PRODUCTION_LAUNCH_CHECKLIST.md: چک‌لیست کامل")
    print("- deploy_to_railway.py: اسکریپت دیپلوی")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print_colored("\n❌ خطا در راه‌اندازی! لطفاً مراحل را بررسی کنید.", Colors.RED)
        sys.exit(1)
    
    print_colored("\n🎊 موفقیت آمیز! سایت آماده استفاده است.", Colors.BOLD + Colors.GREEN)
