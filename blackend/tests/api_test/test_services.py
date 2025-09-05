from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult
from api_test.views import ApiTestService
import json

User = get_user_model()

class ApiTestServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.api_definition = ApiDefinition.objects.create(
            name='Test API',
            url='http://testserver/api/test',
            method='GET',
            headers='{"Content-Type": "application/json"}',
            params='{"param1": "value1"}',
            body='{}',
            created_by=self.user
        )
        self.api_test_case = ApiTestCase.objects.create(
            name='Test Case 1',
            api=self.api_definition,
            headers='{}',
            params='{}',
            body='{}',
            assertions='[]',
            variables='{}',
            expected_status_code=200,
            created_by=self.user
        )

    @patch('api_test.views.requests.request')
    def test_execute_test_case_success(self, mock_request):
        """测试用例正常通过"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_request.return_value = mock_response

        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'passed')
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.test_case, self.api_test_case)
        self.assertEqual(ApiTestResult.objects.count(), 1)

    @patch('api_test.views.requests.request')
    def test_execute_test_case_status_code_failure(self, mock_request):
        """状态码断言失败"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = '{"error": "Not Found"}'
        mock_response.headers = {}
        mock_request.return_value = mock_response

        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'failed')
        self.assertEqual(result.response_code, 404)
        self.assertIn("状态码断言失败", result.error_message)

    def test_execute_disabled_test_case(self):
        """用例被禁用"""
        self.api_test_case.is_active = False
        self.api_test_case.save()
        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'error')
        self.assertEqual(result.error_message, '测试用例已禁用')

    @patch('api_test.views.requests.request')
    def test_execute_test_case_with_variables(self, mock_request):
        """变量替换"""
        self.api_definition.url = 'http://testserver/api/{path}'
        self.api_definition.save()
        variable_case = ApiTestCase.objects.create(
            name='Test Case with Variables',
            api=self.api_definition,
            variables='{"path": "users"}',
            expected_status_code=200,
            created_by=self.user
        )
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_request.return_value = mock_response
        ApiTestService.execute_test_case(variable_case, self.user)
        mock_request.assert_called_once()
        _args, kwargs = mock_request.call_args
        self.assertIn('url', kwargs)
        self.assertEqual(kwargs['url'], 'http://testserver/api/users')

    @patch('api_test.views.requests.request', side_effect=Exception('连接错误，无法访问目标服务器'))
    def test_execute_test_case_connection_error(self, mock_request):
        """连接错误"""
        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'error')
        self.assertIn('连接错误', result.error_message)

    @patch('api_test.views.requests.request', side_effect=Exception('请求超时'))
    def test_execute_test_case_timeout(self, mock_request):
        """请求超时"""
        # 这里模拟超时异常
        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'error')
        self.assertIn('请求超时', result.error_message)

    @patch('api_test.views.requests.request')
    def test_execute_test_case_custom_assertion_fail(self, mock_request):
        """自定义断言失败"""
        # 用例断言：响应JSON的status字段应为success
        self.api_test_case.assertions = json.dumps([
            {"type": "json_path", "field": "status", "expected": "success"}
        ])
        self.api_test_case.save()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "fail"}'
        mock_response.headers = {'Content-Type': 'application/json'}
        mock_response.json.return_value = {"status": "fail"}
        mock_request.return_value = mock_response
        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'failed')
        self.assertIn('断言失败', result.error_message)