"""
API测试模型的单元测试
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
import json
from .models import ApiDefinition, ApiTestCase, TestRun, ApiTestResult

User = get_user_model()

class ApiDefinitionModelTest(TestCase):
    """API定义模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.api_definition = ApiDefinition.objects.create(
            name='测试API',
            url='http://test.example.com/api/users',
            method='GET',
            headers='{"Content-Type": "application/json"}',
            params='{"page": "1"}',
            body='{}',
            description='用户列表API',
            module='用户模块',
            created_by=self.user
        )
    
    def test_api_definition_creation(self):
        """测试API定义创建"""
        self.assertEqual(self.api_definition.name, '测试API')
        self.assertEqual(self.api_definition.method, 'GET')
        self.assertEqual(self.api_definition.created_by, self.user)
        self.assertTrue(self.api_definition.created_at)
        self.assertTrue(self.api_definition.updated_at)
    
    def test_get_headers_valid_json(self):
        """测试获取有效JSON请求头"""
        headers = self.api_definition.get_headers()
        self.assertEqual(headers, {"Content-Type": "application/json"})
    
    def test_get_headers_invalid_json(self):
        """测试获取无效JSON请求头"""
        self.api_definition.headers = 'invalid json'
        self.api_definition.save()
        headers = self.api_definition.get_headers()
        self.assertEqual(headers, {})
    
    def test_get_params_valid_json(self):
        """测试获取有效JSON参数"""
        params = self.api_definition.get_params()
        self.assertEqual(params, {"page": "1"})
    
    def test_get_body_valid_json(self):
        """测试获取有效JSON请求体"""
        self.api_definition.body = '{"name": "test"}'
        self.api_definition.save()
        body = self.api_definition.get_body()
        self.assertEqual(body, {"name": "test"})
    
    def test_str_method(self):
        """测试字符串表示方法"""
        expected = f"{self.api_definition.method} {self.api_definition.name}"
        self.assertEqual(str(self.api_definition), expected)

class ApiTestCaseModelTest(TestCase):
    """API测试用例模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.api_definition = ApiDefinition.objects.create(
            name='测试API',
            url='http://test.example.com/api/users',
            method='POST',
            created_by=self.user
        )
        self.test_case = ApiTestCase.objects.create(
            name='创建用户测试',
            api=self.api_definition,
            headers='{"Authorization": "Bearer token"}',
            body='{"name": "testuser", "email": "test@example.com"}',
            assertions='[{"type": "status_code", "expected": 201}]',
            variables='{"user_id": "123"}',
            expected_status_code=201,
            max_response_time=5000,
            created_by=self.user
        )
    
    def test_test_case_creation(self):
        """测试用例创建"""
        self.assertEqual(self.test_case.name, '创建用户测试')
        self.assertEqual(self.test_case.api, self.api_definition)
        self.assertEqual(self.test_case.expected_status_code, 201)
        self.assertTrue(self.test_case.is_active)
    
    def test_get_assertions(self):
        """测试获取断言规则"""
        assertions = self.test_case.get_assertions()
        expected = [{"type": "status_code", "expected": 201}]
        self.assertEqual(assertions, expected)
    
    def test_get_variables(self):
        """测试获取变量"""
        variables = self.test_case.get_variables()
        self.assertEqual(variables, {"user_id": "123"})
    
    def test_get_body(self):
        """测试获取请求体"""
        body = self.test_case.get_body()
        expected = {"name": "testuser", "email": "test@example.com"}
        self.assertEqual(body, expected)

class TestRunModelTest(TestCase):
    """测试运行模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # 创建TestPlan需要先导入
        from testcases.models import TestPlan
        self.test_plan = TestPlan.objects.create(
            name='测试计划1',
            assignee=self.user
        )
        self.test_run = TestRun.objects.create(
            test_plan=self.test_plan,
            name='回归测试 2025-01-10',
            executed_by=self.user
        )
    
    def test_test_run_creation(self):
        """测试运行记录创建"""
        self.assertEqual(self.test_run.name, '回归测试 2025-01-10')
        self.assertEqual(self.test_run.status, 'running')
        self.assertEqual(self.test_run.total_tests, 0)
        self.assertEqual(self.test_run.executed_by, self.user)
        self.assertTrue(self.test_run.start_time)
    
    def test_duration_property(self):
        """测试执行时长属性"""
        # 设置结束时间
        end_time = timezone.now()
        self.test_run.end_time = end_time
        self.test_run.save()
        
        duration = self.test_run.duration
        self.assertIsNotNone(duration)
        self.assertGreaterEqual(duration.total_seconds(), 0)
    
    def test_success_rate_property(self):
        """测试成功率属性"""
        self.test_run.total_tests = 10
        self.test_run.passed_tests = 8
        self.test_run.save()
        
        success_rate = self.test_run.success_rate
        self.assertEqual(success_rate, 80.0)
    
    def test_success_rate_zero_tests(self):
        """测试零用例的成功率"""
        success_rate = self.test_run.success_rate
        self.assertEqual(success_rate, 0)
    
    def test_is_running_property(self):
        """测试是否正在运行属性"""
        self.assertTrue(self.test_run.is_running)
        
        self.test_run.status = 'completed'
        self.test_run.save()
        self.assertFalse(self.test_run.is_running)
    
    def test_complete_method(self):
        """测试完成方法"""
        self.test_run.complete()
        self.test_run.refresh_from_db()
        self.assertEqual(self.test_run.status, 'completed')
        self.assertIsNotNone(self.test_run.end_time)
    
    def test_str_method(self):
        """测试字符串表示"""
        expected = f"{self.test_run.name} - {self.test_plan.name}"
        self.assertEqual(str(self.test_run), expected)

class ApiTestResultModelTest(TestCase):
    """API测试结果模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.api_definition = ApiDefinition.objects.create(
            name='测试API',
            url='http://test.example.com/api/test',
            method='GET',
            created_by=self.user
        )
        self.test_case = ApiTestCase.objects.create(
            name='测试用例',
            api=self.api_definition,
            created_by=self.user
        )
    
    def test_result_creation_passed(self):
        """测试创建通过的结果"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='passed',
            response_code=200,
            response_time=150.5,
            response_body='{"success": true}',
            executed_by=self.user
        )
        
        self.assertEqual(result.status, 'passed')
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.response_time, 150.5)
        self.assertTrue(result.executed_at)
    
    def test_result_creation_failed(self):
        """测试创建失败的结果"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='failed',
            response_code=400,
            error_message='状态码断言失败',
            executed_by=self.user
        )
        
        self.assertEqual(result.status, 'failed')
        self.assertEqual(result.response_code, 400)
        self.assertIn('状态码断言失败', result.error_message)
    
    def test_result_creation_error(self):
        """测试创建错误的结果"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='error',
            error_message='连接超时',
            executed_by=self.user
        )
        
        self.assertEqual(result.status, 'error')
        self.assertIn('连接超时', result.error_message)
        self.assertIsNone(result.response_code)