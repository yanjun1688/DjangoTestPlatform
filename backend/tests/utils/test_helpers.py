"""
测试辅助工具模块

提供测试过程中常用的辅助函数和工具类
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
import json

User = get_user_model()


class BaseTestCase(TestCase):
    """基础测试类，提供常用的测试方法"""
    
    def setUp(self):
        """设置测试数据"""
        self.test_user = self.create_test_user()
        super().setUp()
    
    def create_test_user(self, username='testuser', email='test@example.com', password='testpass123'):
        """创建测试用户"""
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    
    def create_admin_user(self, username='admin', email='admin@example.com', password='adminpass123'):
        """创建管理员用户"""
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
    
    def assert_json_response(self, response, expected_data=None, status_code=200):
        """验证JSON响应"""
        self.assertEqual(response.status_code, status_code)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        if expected_data:
            response_data = json.loads(response.content.decode('utf-8'))
            for key, value in expected_data.items():
                self.assertIn(key, response_data)
                self.assertEqual(response_data[key], value)
    
    def assert_field_error(self, response, field_name, error_message=None):
        """验证字段错误"""
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content.decode('utf-8'))
        self.assertIn(field_name, response_data)
        
        if error_message:
            self.assertIn(error_message, str(response_data[field_name]))


def create_mock_file(content, filename='test.txt', content_type='text/plain'):
    """创建模拟文件对象"""
    from django.core.files.uploadedfile import SimpleUploadedFile
    return SimpleUploadedFile(filename, content.encode('utf-8'), content_type=content_type)


def create_test_csv_file(headers, rows, filename='test.csv'):
    """创建测试CSV文件"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)
    
    content = output.getvalue()
    return create_mock_file(content, filename, 'text/csv')


def create_test_json_file(data, filename='test.json'):
    """创建测试JSON文件"""
    content = json.dumps(data, ensure_ascii=False, indent=2)
    return create_mock_file(content, filename, 'application/json')


def skip_if_no_database(test_func):
    """装饰器：如果没有数据库连接则跳过测试"""
    from django.test import override_settings
    from django.db import connection
    from django.test.utils import skipUnlessDBFeature
    
    def wrapper(*args, **kwargs):
        try:
            connection.ensure_connection()
            return test_func(*args, **kwargs)
        except Exception:
            return skipUnlessDBFeature('supports_transactions')(test_func)(*args, **kwargs)
    
    return wrapper


class MockResponse:
    """模拟HTTP响应对象"""
    
    def __init__(self, json_data=None, status_code=200, headers=None):
        self.json_data = json_data or {}
        self.status_code = status_code
        self.headers = headers or {}
        self.text = json.dumps(json_data) if json_data else ''
    
    def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code} Error")


def assert_model_fields(test_case, model_instance, expected_fields):
    """验证模型字段值"""
    for field_name, expected_value in expected_fields.items():
        actual_value = getattr(model_instance, field_name)
        test_case.assertEqual(
            actual_value, 
            expected_value,
            f"字段 {field_name} 值不匹配: 期望 {expected_value}, 实际 {actual_value}"
        )


def clean_test_data():
    """清理测试数据"""
    from django.core.management import call_command
    call_command('flush', verbosity=0, interactive=False)