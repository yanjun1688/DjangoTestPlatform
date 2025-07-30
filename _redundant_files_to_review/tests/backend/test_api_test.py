from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.contrib.auth import get_user_model
from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult
from api_test.views import ApiTestService
import json
import requests

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
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        ApiTestService.execute_test_case(variable_case, self.user)
        mock_request.assert_called_once()
        _args, kwargs = mock_request.call_args
        self.assertIn('url', kwargs)
        self.assertEqual(kwargs['url'], 'http://testserver/api/users')

    @patch('api_test.views.requests.request')
    def test_execute_test_case_connection_error(self, mock_request):
        """连接错误"""
        mock_request.side_effect = requests.exceptions.ConnectionError('连接错误')
        result = ApiTestService.execute_test_case(self.api_test_case, self.user)
        self.assertEqual(result.status, 'error')
        self.assertIn('连接错误', result.error_message)

    @patch('api_test.views.requests.request')
    def test_execute_test_case_timeout(self, mock_request):
        """请求超时"""
        mock_request.side_effect = requests.exceptions.Timeout('请求超时')
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

    @patch('api_test.views.requests.request')
    def test_execute_test_case_response_time_check(self, mock_request):
        """响应时间检查"""
        self.api_test_case.max_response_time = 100  # 100ms
        self.api_test_case.save()
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '{"status": "success"}'
        mock_response.headers = {}
        mock_request.return_value = mock_response
        
        # Mock time.time to simulate slow response
        with patch('api_test.views.time.time', side_effect=[0, 0.5]):  # 500ms response
            result = ApiTestService.execute_test_case(self.api_test_case, self.user)
            self.assertEqual(result.status, 'failed')
            self.assertIn('响应时间断言失败', result.error_message)

class ApiDefinitionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_api_definition(self):
        """测试创建API定义"""
        api = ApiDefinition.objects.create(
            name='Test API',
            url='http://example.com/api',
            method='POST',
            headers='{"Content-Type": "application/json"}',
            params='{"param": "value"}',
            body='{"key": "value"}',
            description='Test API Description',
            module='Test Module',
            created_by=self.user
        )
        
        self.assertEqual(api.name, 'Test API')
        self.assertEqual(api.method, 'POST')
        self.assertEqual(str(api), 'POST Test API')

    def test_api_definition_json_methods(self):
        """测试JSON字段解析方法"""
        api = ApiDefinition.objects.create(
            name='Test API',
            url='http://example.com/api',
            method='GET',
            headers='{"Authorization": "Bearer token"}',
            params='{"q": "search"}',
            body='{"data": "test"}',
            created_by=self.user
        )
        
        self.assertEqual(api.get_headers(), {"Authorization": "Bearer token"})
        self.assertEqual(api.get_params(), {"q": "search"})
        self.assertEqual(api.get_body(), {"data": "test"})

    def test_api_definition_invalid_json(self):
        """测试无效JSON的处理"""
        api = ApiDefinition.objects.create(
            name='Test API',
            url='http://example.com/api',
            method='GET',
            headers='invalid json',
            params='',
            body='null',
            created_by=self.user
        )
        
        self.assertEqual(api.get_headers(), {})
        self.assertEqual(api.get_params(), {})
        self.assertEqual(api.get_body(), {})

class ApiTestCaseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.api = ApiDefinition.objects.create(
            name='Test API',
            url='http://example.com/api',
            method='GET',
            created_by=self.user
        )

    def test_create_api_test_case(self):
        """测试创建API测试用例"""
        test_case = ApiTestCase.objects.create(
            name='Test Case',
            api=self.api,
            headers='{"Authorization": "Bearer token"}',
            params='{"limit": 10}',
            body='{}',
            assertions='[{"type": "status_code", "expected": 200}]',
            variables='{"user_id": 123}',
            expected_status_code=200,
            max_response_time=1000,
            created_by=self.user
        )
        
        self.assertEqual(test_case.name, 'Test Case')
        self.assertEqual(test_case.api, self.api)
        self.assertTrue(test_case.is_active)
        self.assertEqual(str(test_case), 'Test Case')

    def test_api_test_case_json_methods(self):
        """测试JSON字段解析方法"""
        test_case = ApiTestCase.objects.create(
            name='Test Case',
            api=self.api,
            assertions='[{"type": "json_path", "field": "status", "expected": "ok"}]',
            variables='{"env": "test"}',
            created_by=self.user
        )
        
        assertions = test_case.get_assertions()
        variables = test_case.get_variables()
        
        self.assertEqual(len(assertions), 1)
        self.assertEqual(assertions[0]['type'], 'json_path')
        self.assertEqual(variables['env'], 'test')

class ApiTestResultModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.api = ApiDefinition.objects.create(
            name='Test API',
            url='http://example.com/api',
            method='GET',
            created_by=self.user
        )
        self.test_case = ApiTestCase.objects.create(
            name='Test Case',
            api=self.api,
            created_by=self.user
        )

    def test_create_api_test_result(self):
        """测试创建API测试结果"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='passed',
            response_code=200,
            response_time=150.5,
            response_body='{"status": "ok"}',
            response_headers='{"Content-Type": "application/json"}',
            assertion_results='[{"type": "status_code", "passed": true}]',
            executed_by=self.user
        )
        
        self.assertEqual(result.test_case, self.test_case)
        self.assertEqual(result.status, 'passed')
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.response_time, 150.5)
        self.assertEqual(str(result), 'Test Case - passed')

    def test_api_test_result_json_methods(self):
        """测试JSON字段解析方法"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='passed',
            response_headers='{"Content-Type": "application/json", "X-Custom": "value"}',
            assertion_results='[{"type": "status_code", "passed": true, "message": "OK"}]',
            executed_by=self.user
        )
        
        headers = result.get_response_headers()
        assertions = result.get_assertion_results()
        
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['X-Custom'], 'value')
        self.assertEqual(len(assertions), 1)
        self.assertTrue(assertions[0]['passed'])

class ApiTestVariableReplacementTest(TestCase):
    def test_replace_variables_in_string(self):
        """测试字符串中的变量替换"""
        data = "Hello {name}, your id is {id}"
        variables = {"name": "John", "id": 123}
        result = ApiTestService._replace_variables(data, variables)
        self.assertEqual(result, "Hello John, your id is 123")

    def test_replace_variables_in_dict(self):
        """测试字典中的变量替换"""
        data = {"url": "https://api.example.com/users/{user_id}", "token": "Bearer {token}"}
        variables = {"user_id": 456, "token": "abc123"}
        result = ApiTestService._replace_variables(data, variables)
        self.assertEqual(result["url"], "https://api.example.com/users/456")
        self.assertEqual(result["token"], "Bearer abc123")

    def test_replace_variables_in_list(self):
        """测试列表中的变量替换"""
        data = ["user_{id}", "admin_{admin_id}"]
        variables = {"id": 1, "admin_id": 2}
        result = ApiTestService._replace_variables(data, variables)
        self.assertEqual(result, ["user_1", "admin_2"])

    def test_replace_variables_no_variables(self):
        """测试没有变量的情况"""
        data = "Hello World"
        variables = {}
        result = ApiTestService._replace_variables(data, variables)
        self.assertEqual(result, "Hello World")

class ApiTestAssertionTest(TestCase):
    def test_json_path_assertion_success(self):
        """测试JSON路径断言成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "success", "data": {"count": 5}}
        
        assertion = {"type": "json_path", "field": "status", "expected": "success"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['actual'], "success")

    def test_json_path_assertion_failure(self):
        """测试JSON路径断言失败"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "error"}
        
        assertion = {"type": "json_path", "field": "status", "expected": "success"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertFalse(result['passed'])
        self.assertEqual(result['actual'], "error")

    def test_json_path_assertion_nested(self):
        """测试嵌套JSON路径断言"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": {"user": {"name": "John"}}}
        
        assertion = {"type": "json_path", "field": "data.user.name", "expected": "John"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertTrue(result['passed'])
        self.assertEqual(result['actual'], "John")

    def test_contains_assertion_success(self):
        """测试包含断言成功"""
        mock_response = MagicMock()
        mock_response.text = "Success: Operation completed successfully"
        
        assertion = {"type": "contains", "expected": "Success"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertTrue(result['passed'])

    def test_contains_assertion_failure(self):
        """测试包含断言失败"""
        mock_response = MagicMock()
        mock_response.text = "Error: Operation failed"
        
        assertion = {"type": "contains", "expected": "Success"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertFalse(result['passed'])

    def test_not_contains_assertion_success(self):
        """测试不包含断言成功"""
        mock_response = MagicMock()
        mock_response.text = "Success: Operation completed"
        
        assertion = {"type": "not_contains", "expected": "Error"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertTrue(result['passed'])

    def test_header_assertion_success(self):
        """测试响应头断言成功"""
        mock_response = MagicMock()
        mock_response.headers = {"Content-Type": "application/json"}
        
        assertion = {"type": "header", "header_name": "Content-Type", "expected": "application/json"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertTrue(result['passed'])

    def test_unsupported_assertion_type(self):
        """测试不支持的断言类型"""
        mock_response = MagicMock()
        
        assertion = {"type": "unknown_type", "expected": "value"}
        result = ApiTestService._execute_assertion(assertion, mock_response)
        
        self.assertFalse(result['passed'])
        self.assertIn("不支持的断言类型", result['message'])

class ApiTestJSONValueTest(TestCase):
    def test_get_json_value_simple(self):
        """测试获取简单JSON值"""
        data = {"name": "John", "age": 30}
        result = ApiTestService._get_json_value(data, "name")
        self.assertEqual(result, "John")

    def test_get_json_value_nested(self):
        """测试获取嵌套JSON值"""
        data = {"user": {"profile": {"name": "John", "age": 30}}}
        result = ApiTestService._get_json_value(data, "user.profile.name")
        self.assertEqual(result, "John")

    def test_get_json_value_array(self):
        """测试获取数组中的值"""
        data = {"users": [{"name": "John"}, {"name": "Jane"}]}
        result = ApiTestService._get_json_value(data, "users.0.name")
        self.assertEqual(result, "John")

    def test_get_json_value_not_found(self):
        """测试获取不存在的值"""
        data = {"name": "John"}
        result = ApiTestService._get_json_value(data, "age")
        self.assertIsNone(result)

    def test_get_json_value_invalid_path(self):
        """测试无效路径"""
        data = {"name": "John"}
        result = ApiTestService._get_json_value(data, "user.profile.name")
        self.assertIsNone(result)