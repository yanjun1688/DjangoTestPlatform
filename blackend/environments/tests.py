from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from .models import Environment, EnvironmentVariable, EnvironmentUsageLog

User = get_user_model()


class EnvironmentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_create_environment(self):
        """测试创建环境"""
        env = Environment.objects.create(
            name='开发环境',
            description='用于开发测试',
            created_by=self.user
        )
        
        self.assertEqual(env.name, '开发环境')
        self.assertEqual(env.created_by, self.user)
        self.assertTrue(env.is_active)
        self.assertFalse(env.is_default)

    def test_default_environment_constraint(self):
        """测试默认环境约束"""
        # 创建第一个默认环境
        env1 = Environment.objects.create(
            name='环境1',
            is_default=True,
            created_by=self.user
        )
        
        # 创建第二个默认环境，应该自动将第一个设为非默认
        env2 = Environment.objects.create(
            name='环境2',
            is_default=True,
            created_by=self.user
        )
        
        env1.refresh_from_db()
        self.assertFalse(env1.is_default)
        self.assertTrue(env2.is_default)

    def test_environment_variable_creation(self):
        """测试环境变量创建"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        var = EnvironmentVariable.objects.create(
            environment=env,
            key='base_url',
            value='https://api.example.com',
            description='基础URL'
        )
        
        self.assertEqual(var.key, 'base_url')
        self.assertEqual(var.environment, env)
        self.assertFalse(var.is_secret)

    def test_secret_variable_masking(self):
        """测试敏感变量脱敏"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        secret_var = EnvironmentVariable.objects.create(
            environment=env,
            key='api_key',
            value='secret123456',
            is_secret=True
        )
        
        self.assertEqual(secret_var.masked_value, '********')


class EnvironmentAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_environment_api(self):
        """测试创建环境API"""
        url = '/api/environments/environments/'
        data = {
            'name': '开发环境',
            'description': '用于开发测试',
            'is_active': True
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '开发环境')
        self.assertEqual(response.data['created_by'], self.user.id)

    def test_list_environments_api(self):
        """测试获取环境列表API"""
        # 创建测试环境
        Environment.objects.create(
            name='环境1',
            created_by=self.user
        )
        Environment.objects.create(
            name='环境2',
            created_by=self.user
        )
        
        url = '/api/environments/environments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_set_default_environment_api(self):
        """测试设置默认环境API"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        url = f'/api/environments/environments/{env.id}/set_default/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        env.refresh_from_db()
        self.assertTrue(env.is_default)

    def test_clone_environment_api(self):
        """测试克隆环境API"""
        # 创建源环境和变量
        source_env = Environment.objects.create(
            name='源环境',
            created_by=self.user
        )
        EnvironmentVariable.objects.create(
            environment=source_env,
            key='base_url',
            value='https://api.example.com'
        )
        
        url = f'/api/environments/environments/{source_env.id}/clone/'
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '源环境 (副本)')
        self.assertEqual(response.data['variables_count'], 1)

    def test_manage_environment_variables_api(self):
        """测试管理环境变量API"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        # 添加变量
        url = f'/api/environments/environments/{env.id}/variables/'
        data = {
            'key': 'base_url',
            'value': 'https://api.example.com',
            'description': '基础URL'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['key'], 'base_url')
        
        # 获取变量列表
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_replace_variables_api(self):
        """测试变量替换API"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        EnvironmentVariable.objects.create(
            environment=env,
            key='base_url',
            value='https://api.example.com'
        )
        EnvironmentVariable.objects.create(
            environment=env,
            key='version',
            value='v1'
        )
        
        url = f'/api/environments/environments/{env.id}/replace_variables/'
        data = {
            'text': '{{base_url}}/{{version}}/users'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['replaced_text'], 'https://api.example.com/v1/users')
        self.assertEqual(response.data['variables_used'], ['base_url', 'version'])

    def test_environment_usage_stats_api(self):
        """测试环境使用统计API"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        # 创建使用日志
        EnvironmentUsageLog.objects.create(
            environment=env,
            user=self.user,
            action='api_test'
        )
        
        url = '/api/environments/environments/usage_stats/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['usage_count'], 1)

    def test_variable_key_validation(self):
        """测试变量名验证"""
        env = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        
        url = f'/api/environments/environments/{env.id}/variables/'
        
        # 测试无效变量名
        invalid_names = ['123invalid', 'invalid-name', 'invalid name', '']
        
        for invalid_name in invalid_names:
            data = {
                'key': invalid_name,
                'value': 'test_value'
            }
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # 测试有效变量名
        valid_data = {
            'key': 'valid_name',
            'value': 'test_value'
        }
        response = self.client.post(url, valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_isolation(self):
        """测试用户隔离"""
        # 创建另一个用户
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # 创建其他用户的环境
        other_env = Environment.objects.create(
            name='其他用户环境',
            created_by=other_user
        )
        
        # 当前用户不应该看到其他用户的环境
        url = '/api/environments/environments/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # 不应该看到其他用户的环境