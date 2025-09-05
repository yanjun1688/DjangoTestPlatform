from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient

User = get_user_model()
from rest_framework import status
from django.urls import reverse
import json
import time

from mock_server.models import MockAPI, MockAPIUsageLog
from mock_server.serializers import MockAPIListSerializer, MockAPIDetailSerializer


class MockAPIModelTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_mock_api(self):
        """测试创建Mock API"""
        mock_api = MockAPI.objects.create(
            name='测试Mock API',
            path='/api/user/profile',
            method='GET',
            response_status_code=200,
            response_body='{"username": "testuser", "email": "test@example.com"}',
            created_by=self.user
        )
        
        self.assertEqual(mock_api.name, '测试Mock API')
        self.assertEqual(mock_api.path, '/api/user/profile')
        self.assertEqual(mock_api.method, 'GET')
        self.assertEqual(mock_api.response_status_code, 200)
        self.assertEqual(mock_api.created_by, self.user)
        self.assertTrue(mock_api.is_active)

    def test_mock_api_validation(self):
        """测试Mock API数据验证"""
        # 测试无效状态码
        with self.assertRaises(Exception):
            mock_api = MockAPI(
                name='无效状态码',
                path='/api/test',
                method='GET',
                response_status_code=999,  # 无效状态码
                created_by=self.user
            )
            mock_api.full_clean()

    def test_mock_api_path_normalization(self):
        """测试路径标准化"""
        mock_api = MockAPI.objects.create(
            name='路径测试',
            path='api/test/',  # 不以/开头，以/结尾
            method='GET',
            created_by=self.user
        )
        
        # 保存后路径应该被标准化
        self.assertEqual(mock_api.path, '/api/test')

    def test_mock_api_unique_constraint(self):
        """测试路径和方法的唯一性约束"""
        MockAPI.objects.create(
            name='第一个Mock',
            path='/api/test',
            method='GET',
            created_by=self.user
        )
        
        # 创建相同路径和方法的Mock应该失败
        with self.assertRaises(Exception):
            MockAPI.objects.create(
                name='重复Mock',
                path='/api/test',
                method='GET',
                created_by=self.user
            )

    def test_mock_api_properties(self):
        """测试Mock API属性方法"""
        mock_api = MockAPI.objects.create(
            name='属性测试',
            path='/api/test',
            method='GET',
            response_body='{"test": "data"}',
            created_by=self.user
        )
        
        # 测试full_url属性
        self.assertEqual(mock_api.full_url, '/mock/api/test')
        
        # 测试get_content_type方法
        self.assertEqual(mock_api.get_content_type(), 'application/json')
        
        # 测试get_response_body_json方法
        body_json = mock_api.get_response_body_json()
        self.assertEqual(body_json['test'], 'data')


class MockAPIViewSetTest(APITestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.mock_api = MockAPI.objects.create(
            name='测试Mock API',
            path='/api/user/profile',
            method='GET',
            response_status_code=200,
            response_body='{"username": "testuser"}',
            created_by=self.user
        )

    def test_list_mock_apis(self):
        """测试获取Mock API列表"""
        # 清理当前用户的Mock API数据
        MockAPI.objects.filter(created_by=self.user).delete()
        
        # 重新创建测试数据
        self.mock_api = MockAPI.objects.create(
            name='测试Mock API',
            path='/api/user/profile',
            method='GET',
            response_status_code=200,
            response_body='{"username": "testuser"}',
            created_by=self.user
        )
        
        url = '/api/mock-server/mocks/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['name'], '测试Mock API')
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['name'], '测试Mock API')

    def test_create_mock_api(self):
        """测试创建Mock API"""
        url = '/api/mock-server/mocks/'
        data = {
            'name': '新Mock API',
            'path': '/api/new',
            'method': 'POST',
            'response_status_code': 201,
            'response_body': '{"success": true}',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '新Mock API')
        self.assertEqual(response.data['created_by'], self.user.id)

    def test_update_mock_api(self):
        """测试更新Mock API"""
        url = f'/api/mock-server/mocks/{self.mock_api.id}/'
        data = {
            'name': '更新的Mock API',
            'path': '/api/user/profile',
            'method': 'GET',
            'response_status_code': 200,
            'response_body': '{"updated": true}',
            'is_active': True
        }
        
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '更新的Mock API')

    def test_delete_mock_api(self):
        """测试删除Mock API"""
        url = f'/api/mock-server/mocks/{self.mock_api.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MockAPI.objects.filter(id=self.mock_api.id).exists())

    def test_get_statistics(self):
        """测试获取统计信息"""
        url = '/api/mock-server/mocks/statistics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_mocks', response.data)
        self.assertIn('active_mocks', response.data)
        self.assertEqual(response.data['total_mocks'], 1)

    def test_test_mock_api(self):
        """测试Mock API测试功能"""
        url = f'/api/mock-server/mocks/{self.mock_api.id}/test/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('test_url', response.data)
        self.assertIn('curl_command', response.data)


class ServeMockAPITest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # 创建多个Mock API用于测试
        self.json_mock = MockAPI.objects.create(
            name='JSON Mock',
            path='/api/user/profile',
            method='GET',
            response_status_code=200,
            response_body='{"username": "MockUser", "email": "mock@test.com"}',
            response_headers={'Content-Type': 'application/json'},
            created_by=self.user
        )
        
        self.text_mock = MockAPI.objects.create(
            name='Text Mock',
            path='/api/hello',
            method='GET',
            response_status_code=200,
            response_body='Hello, World!',
            created_by=self.user
        )
        
        self.error_mock = MockAPI.objects.create(
            name='Error Mock',
            path='/api/error',
            method='POST',
            response_status_code=500,
            response_body='{"error": "Internal Server Error"}',
            created_by=self.user
        )
        
        self.delayed_mock = MockAPI.objects.create(
            name='Delayed Mock',
            path='/api/slow',
            method='GET',
            response_status_code=200,
            response_body='{"message": "Slow response"}',
            delay_ms=100,  # 100ms延迟
            created_by=self.user
        )

    def test_serve_json_mock(self):
        """测试JSON Mock API服务"""
        response = self.client.get('/mock/api/user/profile')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # 验证响应体
        response_data = json.loads(response.content.decode())
        self.assertEqual(response_data['username'], 'MockUser')
        self.assertEqual(response_data['email'], 'mock@test.com')

    def test_serve_text_mock(self):
        """测试文本Mock API服务"""
        response = self.client.get('/mock/api/hello')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), 'Hello, World!')

    def test_serve_error_mock(self):
        """测试错误Mock API服务"""
        response = self.client.post('/mock/api/error')
        
        self.assertEqual(response.status_code, 500)

    def test_serve_delayed_mock(self):
        """测试延迟Mock API服务"""
        start_time = time.time()
        response = self.client.get('/mock/api/slow')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        # 验证延迟时间（允许一些误差）
        self.assertGreater(end_time - start_time, 0.05)  # 至少50ms

    def test_serve_not_found(self):
        """测试不存在的Mock API"""
        response = self.client.get('/mock/api/notfound')
        
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content.decode())
        self.assertIn('error', response_data)
        self.assertIn('Mock API not found', response_data['error'])

    def test_method_not_allowed(self):
        """测试方法不匹配"""
        # JSON mock只支持GET，尝试POST
        response = self.client.post('/mock/api/user/profile')
        
        self.assertEqual(response.status_code, 404)

    def test_inactive_mock(self):
        """测试禁用的Mock API"""
        # 禁用mock
        self.json_mock.is_active = False
        self.json_mock.save()
        
        response = self.client.get('/mock/api/user/profile')
        self.assertEqual(response.status_code, 404)

    def test_usage_log_creation(self):
        """测试使用日志记录"""
        initial_log_count = MockAPIUsageLog.objects.count()
        
        response = self.client.get('/mock/api/user/profile')
        
        self.assertEqual(response.status_code, 200)
        
        # 验证日志记录
        final_log_count = MockAPIUsageLog.objects.count()
        self.assertEqual(final_log_count, initial_log_count + 1)
        
        # 验证日志内容
        log = MockAPIUsageLog.objects.latest('timestamp')
        self.assertEqual(log.mock_api, self.json_mock)
        self.assertEqual(log.request_method, 'GET')
        self.assertEqual(log.request_path, '/api/user/profile')
        self.assertEqual(log.response_status_code, 200)

    def test_custom_headers(self):
        """测试自定义响应头"""
        # 创建带自定义头的Mock
        custom_mock = MockAPI.objects.create(
            name='Custom Headers Mock',
            path='/api/custom',
            method='GET',
            response_status_code=200,
            response_body='OK',
            response_headers={
                'X-Custom-Header': 'CustomValue',
                'Cache-Control': 'no-cache'
            },
            created_by=self.user
        )
        
        response = self.client.get('/mock/api/custom')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Custom-Header'], 'CustomValue')
        self.assertEqual(response['Cache-Control'], 'no-cache')


class MockAPIIntegrationTest(APITestCase):
    def setUp(self):
        """设置集成测试"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_complete_workflow(self):
        """测试完整的Mock API工作流"""
        # 1. 创建Mock API
        create_data = {
            'name': '完整流程测试',
            'path': '/api/workflow',
            'method': 'GET',
            'response_status_code': 200,
            'response_body': '{"workflow": "test"}',
            'is_active': True
        }
        
        create_response = self.client.post('/api/mock-server/mocks/', create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        
        mock_id = create_response.data['id']
        
        # 2. 验证Mock API已创建
        detail_response = self.client.get(f'/api/mock-server/mocks/{mock_id}/')
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        
        # 3. 测试Mock服务
        mock_response = self.client.get('/mock/api/workflow')
        self.assertEqual(mock_response.status_code, 200)
        
        # 4. 验证使用日志
        logs_response = self.client.get('/api/mock-server/logs/')
        self.assertEqual(logs_response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(logs_response.data), 0)
        
        # 5. 获取统计信息
        stats_response = self.client.get('/api/mock-server/mocks/statistics/')
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertGreater(stats_response.data['total_mocks'], 0)
        
        # 6. 删除Mock API
        delete_response = self.client.delete(f'/api/mock-server/mocks/{mock_id}/')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)