#!/usr/bin/env python
"""
Apply the AdminAlert migration on the current environment.
Usage (local):     python scripts/apply_admin_alert_migration.py
Usage (Railway):   railway run python scripts/apply_admin_alert_migration.py
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Prefer production settings on Railway if not explicitly set
if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PROJECT_ID'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings_railway')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')

import django
from django.core.management import call_command

def main():
    django.setup()
    # Apply only the AdminAlert migration (safe to re-run)
    call_command('migrate', 'bazarche_app', '0019_adminalert', interactive=False, verbosity=1)
    print('✅ AdminAlert migration applied successfully.')

if __name__ == '__main__':
    main()


