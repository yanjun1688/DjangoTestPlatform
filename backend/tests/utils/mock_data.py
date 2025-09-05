"""
模拟数据生成器

提供测试过程中需要的各种模拟数据
"""

import random
import string
from datetime import datetime, timedelta
from django.utils import timezone


class MockDataGenerator:
    """模拟数据生成器"""
    
    @staticmethod
    def random_string(length=10):
        """生成随机字符串"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_email():
        """生成随机邮箱"""
        username = MockDataGenerator.random_string(8)
        domains = ['example.com', 'test.com', 'demo.org']
        return f"{username}@{random.choice(domains)}"
    
    @staticmethod
    def random_phone():
        """生成随机手机号"""
        prefixes = ['138', '139', '158', '159', '188', '189']
        return random.choice(prefixes) + ''.join(random.choices(string.digits, k=8))
    
    @staticmethod
    def random_datetime(start_days_ago=30, end_days_ago=0):
        """生成随机日期时间"""
        start_date = timezone.now() - timedelta(days=start_days_ago)
        end_date = timezone.now() - timedelta(days=end_days_ago)
        
        time_between = end_date - start_date
        random_duration = random.random() * time_between.total_seconds()
        
        return start_date + timedelta(seconds=random_duration)
    
    @staticmethod
    def create_user_data(username=None, email=None):
        """创建用户数据"""
        return {
            'username': username or f"user_{MockDataGenerator.random_string(6)}",
            'email': email or MockDataGenerator.random_email(),
            'password': 'testpass123',
            'phone': MockDataGenerator.random_phone(),
            'department': random.choice(['开发部', '测试部', '产品部', '运维部'])
        }
    
    @staticmethod
    def create_testcase_data(title=None):
        """创建测试用例数据"""
        return {
            'title': title or f"测试用例_{MockDataGenerator.random_string(6)}",
            'description': '这是一个自动生成的测试用例描述',
            'precondition': '前置条件：系统正常运行',
            'module': random.choice(['用户管理', 'API测试', '数据管理', '报告系统']),
            'priority': random.choice(['P0', 'P1', 'P2']),
            'status': random.choice(['passed', 'failed', 'blocked']),
            'tags': ','.join(random.choices(['自动化', '手工', '回归', '冒烟'], k=2))
        }
    
    @staticmethod
    def create_api_data(name=None, url=None):
        """创建API数据"""
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
        paths = ['/api/users', '/api/products', '/api/orders', '/api/reports']
        
        return {
            'name': name or f"API_{MockDataGenerator.random_string(6)}",
            'method': random.choice(methods),
            'url': url or f"https://api.example.com{random.choice(paths)}",
            'description': '自动生成的API接口',
            'timeout': random.randint(5, 30)
        }
    
    @staticmethod
    def create_environment_data(name=None):
        """创建环境数据"""
        return {
            'name': name or f"环境_{MockDataGenerator.random_string(6)}",
            'description': '自动生成的测试环境',
            'is_active': True,
            'is_default': False
        }
    
    @staticmethod
    def create_test_results_data(count=10):
        """创建测试结果数据列表"""
        results = []
        for i in range(count):
            results.append({
                'status': random.choice(['passed', 'failed', 'error']),
                'response_code': random.choice([200, 201, 400, 404, 500]),
                'response_time': round(random.uniform(50, 2000), 2),
                'executed_at': MockDataGenerator.random_datetime(7, 0)
            })
        return results
    
    @staticmethod
    def create_csv_test_data(rows=5):
        """创建CSV测试数据"""
        headers = ['name', 'age', 'email', 'department']
        data_rows = []
        
        for i in range(rows):
            data_rows.append([
                f"用户{i+1}",
                str(random.randint(20, 60)),
                MockDataGenerator.random_email(),
                random.choice(['开发部', '测试部', '产品部'])
            ])
        
        return {
            'headers': headers,
            'rows': data_rows
        }
    
    @staticmethod
    def create_json_test_data(count=5):
        """创建JSON测试数据"""
        data = []
        
        for i in range(count):
            data.append({
                'id': i + 1,
                'name': f"项目{i+1}",
                'status': random.choice(['active', 'inactive', 'pending']),
                'created_at': MockDataGenerator.random_datetime(30, 0).isoformat(),
                'priority': random.randint(1, 5)
            })
        
        return data


# 预定义的测试数据集
SAMPLE_USER_DATA = {
    'username': 'sampleuser',
    'email': 'sample@example.com',
    'password': 'samplepass123',
    'phone': '13800000000',
    'department': '测试部'
}

SAMPLE_API_DATA = {
    'name': '用户登录API',
    'method': 'POST',
    'url': 'https://api.example.com/auth/login',
    'description': '用户登录接口',
    'timeout': 10
}

SAMPLE_TESTCASE_DATA = {
    'title': '用户登录功能测试',
    'description': '验证用户登录功能是否正常',
    'precondition': '用户已注册且账号状态正常',
    'module': '用户管理',
    'priority': 'P0',
    'status': 'blocked',
    'tags': '登录,功能测试'
}