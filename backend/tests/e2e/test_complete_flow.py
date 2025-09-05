"""
端到端测试

模拟用户完整的操作流程，从登录到完成测试任务的全过程
"""

from django.test import TestCase, LiveServerTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

from tests.utils.test_helpers import BaseTestCase
from tests.utils.mock_data import MockDataGenerator

User = get_user_model()


class CompleteUserJourneyTest(BaseTestCase):
    """完整用户旅程测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
        # 创建测试用户
        self.tester = User.objects.create_user(
            username='tester001',
            email='tester@example.com',
            password='testerpass123',
            role='user'
        )
        
        # 创建管理员用户
        self.admin = self.create_admin_user()
    
    def test_complete_testing_journey(self):
        """测试完整的测试流程"""
        
        # === 第一阶段：管理员准备测试环境 ===
        self.client.force_authenticate(user=self.admin)
        
        # 1. 创建测试环境
        env_data = {
            'name': 'E2E测试环境',
            'description': '端到端测试专用环境',
            'is_active': True,
            'is_default': True
        }
        
        response = self.client.post('/api/environments/', env_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        environment_id = response.json()['id']
        
        # 2. 添加环境变量
        env_var_data = {
            'environment': environment_id,
            'key': 'API_BASE_URL',
            'value': 'https://api.e2e-test.com',
            'description': 'E2E测试API基础URL'
        }
        
        response = self.client.post('/api/environments/variables/', env_var_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 3. 创建API定义
        api_data = {
            'name': 'E2E用户管理API',
            'method': 'POST',
            'url': 'https://api.e2e-test.com/users',
            'description': '用户创建API',
            'timeout': 30
        }
        
        response = self.client.post('/api-test/api-definitions/', api_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        api_id = response.json()['id']
        
        # === 第二阶段：测试人员创建测试用例 ===
        self.client.force_authenticate(user=self.tester)
        
        # 4. 创建测试用例
        testcase_data = {
            'name': 'E2E用户创建测试',
            'api': api_id,
            'expected_status_code': 201,
            'request_headers': {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer test_token'
            },
            'request_body': json.dumps({
                'username': 'e2e_test_user',
                'email': 'e2e@test.com',
                'password': 'testpass123'
            }),
            'assertions': [
                {'field': 'status', 'operator': 'equals', 'value': 'success'},
                {'field': 'data.username', 'operator': 'equals', 'value': 'e2e_test_user'}
            ]
        }
        
        response = self.client.post('/api-test/test-cases/', testcase_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        testcase_id = response.json()['id']
        
        # 5. 创建测试计划
        plan_data = {
            'name': 'E2E完整测试计划',
            'status': 'pending'
        }
        
        response = self.client.post('/testcases/', plan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        plan_id = response.json()['id']
        
        # 6. 将测试用例添加到计划
        response = self.client.patch(
            f'/testcases/{plan_id}/',
            {'test_cases': [testcase_id]},
            format='json'
        )
        # 根据实际API响应调整状态码检查
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT])
        
        # === 第三阶段：执行测试 ===
        
        # 7. 创建测试执行
        run_data = {
            'name': 'E2E测试执行',
            'test_plan': plan_id,
            'description': '端到端测试执行'
        }
        
        response = self.client.post('/api/reports/test-runs/', run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        run_id = response.json()['id']
        
        # 8. 模拟测试执行结果
        from api_test.models import ApiTestCase, TestRun, ApiTestResult
        
        test_case = ApiTestCase.objects.get(id=testcase_id)
        test_run = TestRun.objects.get(id=run_id)
        
        # 创建成功的测试结果
        result = ApiTestResult.objects.create(
            test_case=test_case,
            test_run=test_run,
            status='passed',
            response_code=201,
            response_time=250.5,
            response_body=json.dumps({
                'status': 'success',
                'data': {
                    'id': 123,
                    'username': 'e2e_test_user',
                    'email': 'e2e@test.com',
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }),
            assertion_results=[
                {'field': 'status', 'passed': True, 'actual': 'success', 'expected': 'success'},
                {'field': 'data.username', 'passed': True, 'actual': 'e2e_test_user', 'expected': 'e2e_test_user'}
            ]
        )
        
        # 9. 完成测试执行
        response = self.client.post(f'/api/reports/test-runs/{run_id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # === 第四阶段：查看测试结果 ===
        
        # 10. 获取测试执行详情
        response = self.client.get(f'/api/reports/test-runs/{run_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        result_data = response.json()
        self.assertEqual(result_data['name'], 'E2E测试执行')
        self.assertEqual(result_data['status'], 'completed')
        self.assertEqual(result_data['total_tests'], 1)
        self.assertEqual(result_data['passed_tests'], 1)
        self.assertEqual(result_data['success_rate'], 100.0)
        
        # 11. 获取统计信息
        response = self.client.get(f'/api/reports/test-runs/{run_id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats = response.json()
        self.assertIn('summary', stats)
        self.assertIn('api_statistics', stats)
        self.assertEqual(stats['summary']['total_tests'], 1)
        self.assertEqual(stats['summary']['passed_rate'], 100.0)
        
        # 12. 导出测试报告
        response = self.client.get(f'/api/reports/test-runs/{run_id}/export_html/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Type'].startswith('text/html'))
        
        # === 第五阶段：协作功能 ===
        
        # 13. 添加评论
        from comments.models import Comment
        from django.contrib.contenttypes.models import ContentType
        from testcases.models import TestCase as TestCaseModel
        
        # 为测试用例创建一个TestCase对象用于评论
        tc_model = TestCaseModel.objects.create(
            title='E2E测试用例模型',
            description='用于评论的测试用例'
        )
        
        comment_data = {
            'content': f'E2E测试执行完成，测试通过率100%。@{self.admin.username}',
            'target_type': 'testcase',
            'target_id': tc_model.id
        }
        
        response = self.client.post('/api/comments/create/', comment_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # 14. 切换到管理员查看通知
        self.client.force_authenticate(user=self.admin)
        
        response = self.client.get('/api/comments/notifications/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        notification_summary = response.json()
        self.assertIn('unread_count', notification_summary)
        
        # 验证整个流程完成
        final_test_run = TestRun.objects.get(id=run_id)
        self.assertEqual(final_test_run.status, 'completed')
        self.assertEqual(final_test_run.total_tests, 1)
        self.assertEqual(final_test_run.passed_tests, 1)
        self.assertEqual(final_test_run.success_rate, 100.0)
    
    def test_data_driven_testing_journey(self):
        """数据驱动测试完整流程"""
        self.client.force_authenticate(user=self.admin)
        
        # 1. 创建带数据文件的测试用例
        from testcases.models import TestCase as TestCaseModel, TestDataFile
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # 创建测试用例
        testcase = TestCaseModel.objects.create(
            title='数据驱动E2E测试',
            description='使用外部数据文件的测试',
            assignee=self.admin
        )
        
        # 创建CSV测试数据
        csv_content = \"\"\"username,email,expected_status\nuser1,user1@test.com,201\nuser2,user2@test.com,201\ninvalid_user,,400\"\"\"\n        \n        csv_file = SimpleUploadedFile(\n            \"e2e_test_data.csv\",\n            csv_content.encode('utf-8'),\n            content_type=\"text/csv\"\n        )\n        \n        # 创建数据文件\n        data_file = TestDataFile.objects.create(\n            name='E2E测试数据',\n            test_case=testcase,\n            file=csv_file,\n            file_type='csv',\n            description='端到端测试的用户数据'\n        )\n        \n        # 2. 验证数据文件解析\n        parsed_data = data_file.parse_file()\n        self.assertEqual(len(parsed_data['headers']), 3)\n        self.assertEqual(len(parsed_data['rows']), 3)\n        self.assertIn('username', parsed_data['headers'])\n        self.assertIn('email', parsed_data['headers'])\n        self.assertIn('expected_status', parsed_data['headers'])\n        \n        # 3. 验证数据文件统计\n        data_count = data_file.get_data_count()\n        self.assertEqual(data_count, 3)\n        \n        # 4. 获取预览数据\n        preview_data = data_file.get_preview_data(max_rows=2)\n        self.assertEqual(len(preview_data['rows']), 2)\n        \n        # 验证数据驱动测试流程完成\n        self.assertEqual(testcase.data_file, data_file)\n        self.assertTrue(data_file.file.name.endswith('.csv'))