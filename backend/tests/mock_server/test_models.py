from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse
import json
from mock_server.models import MockAPI, MockAPIUsageLog

User = get_user_model()

class MockAPIModelTest(TestCase):
    """Mock API模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mock_api = MockAPI.objects.create(
            name='测试用户API',
            path='/api/users/1',
            method='GET',
            response_status_code=200,
            response_headers={'Content-Type': 'application/json'},
            response_body='{"id": 1, "name": "test user"}',
            description='获取用户信息的Mock API',
            created_by=self.user
        )
    
    def test_mock_api_creation(self):
        """测试Mock API创建"""
        self.assertEqual(self.mock_api.name, '测试用户API')
        self.assertEqual(self.mock_api.path, '/api/users/1')
        self.assertEqual(self.mock_api.method, 'GET')
        self.assertEqual(self.mock_api.response_status_code, 200)
        self.assertTrue(self.mock_api.is_active)
        self.assertEqual(self.mock_api.delay_ms, 0)
    
    def test_mock_api_str_method(self):
        """测试Mock API字符串表示"""
        expected = f"{self.mock_api.method} {self.mock_api.path} - {self.mock_api.name}"
        self.assertEqual(str(self.mock_api), expected)
    
    def test_path_normalization(self):
        """测试路径标准化"""
        # 测试自动添加前导斜杠
        mock_api = MockAPI.objects.create(
            name='测试路径标准化',
            path='api/test',  # 没有前导斜杠
            method='POST',
            created_by=self.user
        )
        self.assertEqual(mock_api.path, '/api/test')
        
        # 测试自动移除尾随斜杠
        mock_api2 = MockAPI.objects.create(
            name='测试路径标准化2',
            path='/api/test/',  # 有尾随斜杠
            method='PUT',
            created_by=self.user
        )
        self.assertEqual(mock_api2.path, '/api/test')
    
    def test_method_uppercase(self):
        """测试HTTP方法自动转大写"""
        mock_api = MockAPI.objects.create(
            name='测试方法大写',
            path='/api/lowercase',
            method='post',  # 小写
            created_by=self.user
        )
        self.assertEqual(mock_api.method, 'POST')
    
    def test_full_url_property(self):
        """测试完整URL属性"""
        expected_url = f"/mock{self.mock_api.path}"
        self.assertEqual(self.mock_api.full_url, expected_url)
    
    def test_get_response_body_json(self):
        """测试JSON响应体解析"""
        # 有效JSON
        json_data = self.mock_api.get_response_body_json()
        self.assertEqual(json_data, {"id": 1, "name": "test user"})
        
        # 无效JSON
        self.mock_api.response_body = 'not json'
        self.mock_api.save()
        result = self.mock_api.get_response_body_json()
        self.assertEqual(result, 'not json')
        
        # 空响应体
        self.mock_api.response_body = ''
        self.mock_api.save()
        result = self.mock_api.get_response_body_json()
        self.assertEqual(result, {})
    
    def test_get_content_type(self):
        """测试Content-Type推断"""
        # JSON响应
        content_type = self.mock_api.get_content_type()
        self.assertEqual(content_type, 'application/json')
        
        # 自定义Content-Type
        self.mock_api.response_headers = {'Content-Type': 'application/xml'}
        self.mock_api.save()
        content_type = self.mock_api.get_content_type()
        self.assertEqual(content_type, 'application/xml')
        
        # XML响应
        self.mock_api.response_headers = {}
        self.mock_api.response_body = '<xml>test</xml>'
        self.mock_api.save()
        content_type = self.mock_api.get_content_type()
        self.assertEqual(content_type, 'application/xml')
        
        # 纯文本响应
        self.mock_api.response_body = 'plain text'
        self.mock_api.save()
        content_type = self.mock_api.get_content_type()
        self.assertEqual(content_type, 'text/plain')
        
        # 空响应体
        self.mock_api.response_body = ''
        self.mock_api.save()
        content_type = self.mock_api.get_content_type()
        self.assertEqual(content_type, 'text/plain')
    
    def test_validation_invalid_path(self):
        """测试无效路径验证"""
        mock_api = MockAPI(
            name='无效路径测试',
            path='invalid',  # 不以/开头
            method='GET',
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            mock_api.full_clean()
    
    def test_validation_invalid_status_code(self):
        """测试无效状态码验证"""
        mock_api = MockAPI(
            name='无效状态码测试',
            path='/api/test',
            method='GET',
            response_status_code=99,  # 无效状态码
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            mock_api.full_clean()
    
    def test_validation_invalid_delay(self):
        """测试无效延迟时间验证"""
        mock_api = MockAPI(
            name='无效延迟测试',
            path='/api/test',
            method='GET',
            delay_ms=-1,  # 负数延迟
            created_by=self.user
        )
        with self.assertRaises(ValidationError):
            mock_api.full_clean()
    
    def test_unique_path_method_constraint(self):
        """测试路径和方法的唯一性约束"""
        # 创建重复的路径和方法应该失败
        with self.assertRaises(Exception):  # 数据库完整性错误
            MockAPI.objects.create(
                name='重复API',
                path='/api/users/1',
                method='GET',
                created_by=self.user
            )

class MockAPIUsageLogModelTest(TestCase):
    """Mock API使用日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.mock_api = MockAPI.objects.create(
            name='测试API',
            path='/api/test',
            method='GET',
            created_by=self.user
        )
        self.usage_log = MockAPIUsageLog.objects.create(
            mock_api=self.mock_api,
            request_path='/api/test',
            request_method='GET',
            request_headers={'Accept': 'application/json'},
            request_body='',
            response_status_code=200,
            client_ip='192.168.1.100',
            user_agent='Mozilla/5.0 Test Browser'
        )
    
    def test_usage_log_creation(self):
        """测试使用日志创建"""
        self.assertEqual(self.usage_log.mock_api, self.mock_api)
        self.assertEqual(self.usage_log.request_path, '/api/test')
        self.assertEqual(self.usage_log.request_method, 'GET')
        self.assertEqual(self.usage_log.response_status_code, 200)
        self.assertEqual(self.usage_log.client_ip, '192.168.1.100')
        self.assertIsNotNone(self.usage_log.timestamp)
    
    def test_usage_log_str_method(self):
        """测试使用日志字符串表示"""
        expected = f"{self.usage_log.request_method} {self.usage_log.request_path} - {self.usage_log.timestamp}"
        self.assertEqual(str(self.usage_log), expected)
    
    def test_usage_log_ordering(self):
        """测试使用日志排序"""
        import time
        time.sleep(0.01)  # 确保时间不同
        
        # 创建第二个日志
        second_log = MockAPIUsageLog.objects.create(
            mock_api=self.mock_api,
            request_path='/api/test',
            request_method='POST',
            response_status_code=201,
            client_ip='192.168.1.101'
        )
        
        # 获取所有日志，应该按时间倒序
        logs = list(MockAPIUsageLog.objects.all())
        self.assertEqual(logs[0].id, second_log.id)  # 最新的在前
        self.assertEqual(logs[1].id, self.usage_log.id)

class MockAPIIntegrationTest(TestCase):
    """Mock API集成测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
        # 创建几个测试用的Mock API
        self.mock_api_get = MockAPI.objects.create(
            name='获取用户',
            path='/api/user/1',
            method='GET',
            response_status_code=200,
            response_body='{"id": 1, "name": "张三"}',
            created_by=self.user
        )
        
        self.mock_api_post = MockAPI.objects.create(
            name='创建用户',
            path='/api/user',
            method='POST',
            response_status_code=201,
            response_body='{"id": 2, "name": "李四", "created": true}',
            delay_ms=100,
            created_by=self.user
        )
        
        self.mock_api_error = MockAPI.objects.create(
            name='服务器错误',
            path='/api/error',
            method='GET',
            response_status_code=500,
            response_body='{"error": "Internal Server Error"}',
            created_by=self.user
        )
    
    def test_mock_api_response_content_types(self):
        """测试不同类型的响应内容"""
        # JSON响应
        self.assertEqual(self.mock_api_get.get_content_type(), 'application/json')
        
        # 创建XML响应的Mock API
        xml_mock = MockAPI.objects.create(
            name='XML响应',
            path='/api/xml',
            method='GET',
            response_body='<user><id>1</id><name>张三</name></user>',
            created_by=self.user
        )
        self.assertEqual(xml_mock.get_content_type(), 'application/xml')
        
        # 创建纯文本响应的Mock API
        text_mock = MockAPI.objects.create(
            name='文本响应',
            path='/api/text',
            method='GET',
            response_body='Hello World',
            created_by=self.user
        )
        self.assertEqual(text_mock.get_content_type(), 'text/plain')
    
    def test_mock_api_with_delay(self):
        """测试带延迟的Mock API"""
        self.assertEqual(self.mock_api_post.delay_ms, 100)
        self.assertTrue(self.mock_api_post.delay_ms > 0)
    
    def test_mock_api_status_codes(self):
        """测试不同状态码的Mock API"""
        self.assertEqual(self.mock_api_get.response_status_code, 200)
        self.assertEqual(self.mock_api_post.response_status_code, 201)
        self.assertEqual(self.mock_api_error.response_status_code, 500)
    
    def test_mock_api_path_variations(self):
        """测试路径变化处理"""
        # 测试路径参数
        param_mock = MockAPI.objects.create(
            name='参数路径',
            path='/api/user/{id}',
            method='GET',
            response_body='{"id": "{id}", "name": "参数用户"}',
            created_by=self.user
        )
        self.assertEqual(param_mock.path, '/api/user/{id}')
        
        # 测试查询参数路径
        query_mock = MockAPI.objects.create(
            name='查询参数',
            path='/api/users',
            method='GET',
            response_body='[{"id": 1}, {"id": 2}]',
            created_by=self.user
        )
        self.assertEqual(query_mock.path, '/api/users')