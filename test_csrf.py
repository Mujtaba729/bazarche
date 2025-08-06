#!/usr/bin/env python
"""
Test script for CSRF functionality
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazarche_project.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_csrf():
    """Test CSRF functionality"""
    client = Client()
    
    # Test GET request to register_product (should work)
    response = client.get('/app/register/')
    print(f"GET /app/register/ - Status: {response.status_code}")
    
    # Test POST request without CSRF (should fail)
    response = client.post('/app/register/', {})
    print(f"POST /app/register/ without CSRF - Status: {response.status_code}")
    
    # Test with CSRF token
    response = client.get('/app/register/')
    csrf_token = response.cookies.get('csrftoken')
    if csrf_token:
        print(f"CSRF Token found: {csrf_token.value[:10]}...")
    else:
        print("No CSRF token found")

if __name__ == '__main__':
    test_csrf() 