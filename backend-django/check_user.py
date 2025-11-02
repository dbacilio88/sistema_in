#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from authentication.models import User

try:
    u = User.objects.get(username='admin')
    print(f'Username: {u.username}')
    print(f'Email: {u.email}')
    print(f'Is active: {u.is_active}')
    print(f'Is locked: {u.is_account_locked()}')
    print(f'Check password "admin123": {u.check_password("admin123")}')
except User.DoesNotExist:
    print('User admin not found')
