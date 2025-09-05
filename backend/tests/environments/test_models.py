from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from environments.models import Environment, EnvironmentVariable, EnvironmentUsageLog

User = get_user_model()

class EnvironmentModelTest(TestCase):
    """环境模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.environment = Environment.objects.create(
            name='测试环境',
            description='用于API测试的环境',
            is_active=True,
            is_default=True,
            created_by=self.user
        )
    
    def test_environment_creation(self):
        """测试环境创建"""
        self.assertEqual(self.environment.name, '测试环境')
        self.assertEqual(self.environment.description, '用于API测试的环境')
        self.assertTrue(self.environment.is_active)
        self.assertTrue(self.environment.is_default)
        self.assertEqual(self.environment.created_by, self.user)
    
    def test_environment_str_method(self):
        """测试环境字符串表示"""
        # 默认环境
        expected = f"{self.environment.name} (默认)"
        self.assertEqual(str(self.environment), expected)
        
        # 非默认环境
        non_default_env = Environment.objects.create(
            name='生产环境',
            is_default=False,
            created_by=self.user
        )
        expected_non_default = f"{non_default_env.name} ()"
        self.assertEqual(str(non_default_env), expected_non_default)
    
    def test_default_environment_constraint(self):
        """测试默认环境唯一性约束"""
        # 创建第二个默认环境，应该自动取消第一个的默认状态
        env2 = Environment.objects.create(
            name='生产环境',
            is_default=True,
            created_by=self.user
        )
        
        # 刷新第一个环境的状态
        self.environment.refresh_from_db()
        
        # 验证只有一个默认环境
        self.assertFalse(self.environment.is_default)
        self.assertTrue(env2.is_default)
    
    def test_environment_ordering(self):
        """测试环境排序"""
        # 创建非默认环境
        env2 = Environment.objects.create(
            name='开发环境',
            is_default=False,
            created_by=self.user
        )
        
        # 获取所有环境，默认环境应该在前
        environments = list(Environment.objects.all())
        self.assertEqual(environments[0], self.environment)  # 默认环境在前
        self.assertEqual(environments[1], env2)
    
    def test_multiple_users_default_environments(self):
        """测试多用户的默认环境"""
        # 创建另一个用户
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123'
        )
        
        # 为第二个用户创建默认环境
        env2 = Environment.objects.create(
            name='用户2的默认环境',
            is_default=True,
            created_by=user2
        )
        
        # 两个用户应该都有自己的默认环境
        self.assertTrue(self.environment.is_default)
        self.assertTrue(env2.is_default)
        self.assertEqual(self.environment.created_by, self.user)
        self.assertEqual(env2.created_by, user2)

class EnvironmentVariableModelTest(TestCase):
    """环境变量模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.environment = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        self.env_var = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='API_URL',
            value='https://api.test.com',
            description='API基础URL',
            is_secret=False
        )
    
    def test_environment_variable_creation(self):
        """测试环境变量创建"""
        self.assertEqual(self.env_var.environment, self.environment)
        self.assertEqual(self.env_var.key, 'API_URL')
        self.assertEqual(self.env_var.value, 'https://api.test.com')
        self.assertEqual(self.env_var.description, 'API基础URL')
        self.assertFalse(self.env_var.is_secret)
    
    def test_environment_variable_str_method(self):
        """测试环境变量字符串表示"""
        expected = f"{self.environment.name}.{self.env_var.key}"
        self.assertEqual(str(self.env_var), expected)
    
    def test_masked_value_property(self):
        """测试敏感信息脱敏"""
        # 非敏感信息，直接返回原值
        self.assertEqual(self.env_var.masked_value, 'https://api.test.com')
        
        # 敏感信息，返回脱敏值
        secret_var = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='API_KEY',
            value='secret123456789',
            is_secret=True
        )
        self.assertEqual(secret_var.masked_value, '********')
        
        # 短的敏感信息
        short_secret = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='PIN',
            value='1234',
            is_secret=True
        )
        self.assertEqual(short_secret.masked_value, '****')
        
        # 空值敏感信息
        empty_secret = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='EMPTY',
            value='',
            is_secret=True
        )
        self.assertEqual(empty_secret.masked_value, '')
    
    def test_unique_key_per_environment(self):
        """测试环境内变量名唯一性"""
        # 在同一环境中创建重复键名应该失败
        with self.assertRaises(IntegrityError):
            EnvironmentVariable.objects.create(
                environment=self.environment,
                key='API_URL',  # 重复的键名
                value='https://api.duplicate.com'
            )
    
    def test_different_environments_same_key(self):
        """测试不同环境可以有相同的变量名"""
        # 创建另一个环境
        env2 = Environment.objects.create(
            name='生产环境',
            created_by=self.user
        )
        
        # 在不同环境中使用相同键名应该成功
        var2 = EnvironmentVariable.objects.create(
            environment=env2,
            key='API_URL',  # 与第一个环境相同的键名
            value='https://api.prod.com'
        )
        
        self.assertEqual(var2.key, 'API_URL')
        self.assertEqual(var2.environment, env2)
        self.assertNotEqual(var2.environment, self.environment)
    
    def test_environment_variable_ordering(self):
        """测试环境变量排序"""
        # 创建多个变量
        var_b = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='B_VAR',
            value='value_b'
        )
        
        var_a = EnvironmentVariable.objects.create(
            environment=self.environment,
            key='A_VAR',
            value='value_a'
        )
        
        # 获取所有变量，显式指定排序
        variables = list(EnvironmentVariable.objects.filter(environment=self.environment).order_by('key'))
        keys = [var.key for var in variables]
        # 验证排序是否正确（字母序）
        expected_keys = sorted(['API_URL', 'A_VAR', 'B_VAR'])
        self.assertEqual(keys, expected_keys)

class EnvironmentUsageLogModelTest(TestCase):
    """环境使用日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.environment = Environment.objects.create(
            name='测试环境',
            created_by=self.user
        )
        self.usage_log = EnvironmentUsageLog.objects.create(
            environment=self.environment,
            user=self.user,
            action='api_test',
            context={'test_case_id': 123}
        )
    
    def test_usage_log_creation(self):
        """测试使用日志创建"""
        self.assertEqual(self.usage_log.environment, self.environment)
        self.assertEqual(self.usage_log.user, self.user)
        self.assertEqual(self.usage_log.action, 'api_test')
        self.assertEqual(self.usage_log.context, {'test_case_id': 123})
        self.assertIsNotNone(self.usage_log.used_at)
    
    def test_usage_log_str_method(self):
        """测试使用日志字符串表示"""
        expected = f"{self.user.username} 使用 {self.environment.name} 进行 API测试"
        self.assertEqual(str(self.usage_log), expected)
    
    def test_usage_log_action_choices(self):
        """测试使用场景选择"""
        # 测试测试计划执行
        plan_log = EnvironmentUsageLog.objects.create(
            environment=self.environment,
            user=self.user,
            action='test_plan'
        )
        self.assertEqual(plan_log.get_action_display(), '测试计划执行')
        
        # 测试手动测试
        manual_log = EnvironmentUsageLog.objects.create(
            environment=self.environment,
            user=self.user,
            action='manual_test'
        )
        self.assertEqual(manual_log.get_action_display(), '手动测试')
    
    def test_usage_log_ordering(self):
        """测试使用日志排序"""
        import time
        time.sleep(0.01)  # 确保时间不同
        
        # 创建第二个日志
        log2 = EnvironmentUsageLog.objects.create(
            environment=self.environment,
            user=self.user,
            action='test_plan'
        )
        
        # 获取所有日志，应该按时间倒序
        logs = list(EnvironmentUsageLog.objects.all())
        self.assertEqual(logs[0].id, log2.id)  # 最新的在前
        self.assertEqual(logs[1].id, self.usage_log.id)

class EnvironmentIntegrationTest(TestCase):
    """环境管理集成测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
    
    def test_complete_environment_setup(self):
        """测试完整的环境配置流程"""
        # 1. 创建环境
        env = Environment.objects.create(
            name='完整测试环境',
            description='包含所有配置的测试环境',
            is_default=True,
            created_by=self.user
        )
        
        # 2. 添加环境变量
        variables = [
            ('BASE_URL', 'https://api.test.com', False),
            ('API_KEY', 'secret_key_123', True),
            ('TIMEOUT', '30', False),
            ('DEBUG', 'true', False),
        ]
        
        for key, value, is_secret in variables:
            EnvironmentVariable.objects.create(
                environment=env,
                key=key,
                value=value,
                is_secret=is_secret
            )
        
        # 3. 验证环境配置
        self.assertEqual(env.variables.count(), 4)
        
        # 验证敏感信息脱敏
        api_key_var = env.variables.get(key='API_KEY')
        self.assertTrue(api_key_var.is_secret)
        self.assertEqual(api_key_var.masked_value, '********')
        
        # 验证非敏感信息正常显示
        base_url_var = env.variables.get(key='BASE_URL')
        self.assertFalse(base_url_var.is_secret)
        self.assertEqual(base_url_var.masked_value, 'https://api.test.com')
        
        # 4. 记录使用日志
        EnvironmentUsageLog.objects.create(
            environment=env,
            user=self.user,
            action='api_test',
            context={'test_run_id': 456}
        )
        
        # 验证使用日志
        self.assertEqual(env.usage_logs.count(), 1)
        log = env.usage_logs.first()
        self.assertEqual(log.action, 'api_test')
        self.assertEqual(log.context['test_run_id'], 456)
    
    def test_environment_switching(self):
        """测试环境切换"""
        # 创建多个环境
        dev_env = Environment.objects.create(
            name='开发环境',
            is_default=True,
            created_by=self.user
        )
        
        test_env = Environment.objects.create(
            name='测试环境',
            is_default=False,
            created_by=self.user
        )
        
        prod_env = Environment.objects.create(
            name='生产环境',
            is_default=False,
            created_by=self.user
        )
        
        # 验证初始默认环境
        self.assertTrue(dev_env.is_default)
        self.assertFalse(test_env.is_default)
        self.assertFalse(prod_env.is_default)
        
        # 切换到测试环境
        test_env.is_default = True
        test_env.save()
        
        # 刷新其他环境状态
        dev_env.refresh_from_db()
        prod_env.refresh_from_db()
        
        # 验证切换结果
        self.assertFalse(dev_env.is_default)
        self.assertTrue(test_env.is_default)
        self.assertFalse(prod_env.is_default)
        
        # 验证只有一个默认环境
        default_count = Environment.objects.filter(
            created_by=self.user,
            is_default=True
        ).count()
        self.assertEqual(default_count, 1)