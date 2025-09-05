"""
Pytest 配置文件
提供全局测试配置和 fixtures
"""
import pytest
import django
from django.conf import settings
from django.test.utils import get_runner
import os
import sys

# 确保 Django 设置正确加载
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')

def pytest_configure(config):
    """配置 pytest"""
    django.setup()

@pytest.fixture(scope='session')
def django_db_setup():
    """数据库设置"""
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }

@pytest.fixture
def api_client():
    """API 客户端 fixture"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def user_factory():
    """用户工厂 fixture"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    def create_user(**kwargs):
        defaults = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    
    return create_user