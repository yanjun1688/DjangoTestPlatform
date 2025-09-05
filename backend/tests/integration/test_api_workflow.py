"""
API工作流集成测试

测试API测试平台的完整工作流程，包括：
- 用户注册和认证
- 测试用例创建和管理
- API定义和测试执行
- 报告生成和查看
"""

from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
import json

from api_test.models import ApiDefinition, ApiTestCase, TestRun, ApiTestResult
from testcases.models import TestCase as TestCaseModel, TestPlan
from environments.models import Environment, EnvironmentVariable
from tests.utils.test_helpers import BaseTestCase
from tests.utils.mock_data import MockDataGenerator

User = get_user_model()


class APIWorkflowIntegrationTest(BaseTestCase):
    """API工作流集成测试"""
    
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.admin_user = self.create_admin_user()
        
        # 创建测试环境
        self.environment = Environment.objects.create(
            name='集成测试环境',
            description='用于集成测试的环境',
            is_default=True,
            created_by=self.admin_user
        )
        
        # 添加环境变量
        EnvironmentVariable.objects.create(
            environment=self.environment,
            key='BASE_URL',
            value='https://api.example.com',
            description='API基础URL'
        )
        
        EnvironmentVariable.objects.create(
            environment=self.environment,
            key='API_KEY',
            value='test_api_key_123',
            description='API密钥',
            is_secret=True
        )
    
    def test_complete_api_testing_workflow(self):
        """测试完整的API测试工作流"""
        # 1. 用户认证
        self.client.force_authenticate(user=self.admin_user)
        
        # 2. 创建API定义
        api_data = {
            'name': '用户信息查询API',
            'method': 'GET',
            'url': 'https://api.example.com/users/1',
            'description': '查询用户详细信息',
            'timeout': 10
        }
        
        response = self.client.post('/api-test/api-definitions/', api_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        api_definition = ApiDefinition.objects.get(name='用户信息查询API')
        
        # 3. 创建测试用例
        testcase_data = {
            'name': '查询用户信息测试',
            'api': api_definition.id,
            'expected_status_code': 200,
            'request_headers': {'Accept': 'application/json'},
            'request_params': {'format': 'json'},
            'assertions': [
                {'field': 'status', 'operator': 'equals', 'value': 'success'},
                {'field': 'data.id', 'operator': 'equals', 'value': '1'}
            ]
        }
        
        response = self.client.post('/api-test/test-cases/', testcase_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_case = ApiTestCase.objects.get(name='查询用户信息测试')
        
        # 4. 创建测试计划
        plan_data = {
            'name': '用户API测试计划',
            'status': 'pending'
        }
        
        response = self.client.post('/testcases/', plan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_plan = TestPlan.objects.get(name='用户API测试计划')
        
        # 5. 创建测试执行
        run_data = {
            'name': '用户API测试执行',
            'test_plan': test_plan.id,
            'description': '集成测试执行'
        }
        
        response = self.client.post('/api/reports/test-runs/', run_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        test_run = TestRun.objects.get(name='用户API测试执行')
        
        # 6. 创建测试结果
        result_data = {
            'test_case': test_case.id,
            'test_run': test_run.id,
            'status': 'passed',
            'response_code': 200,
            'response_time': 150.5,
            'response_body': json.dumps({
                'status': 'success',
                'data': {'id': '1', 'name': 'John Doe', 'email': 'john@example.com'}
            }),
            'assertion_results': [
                {'field': 'status', 'passed': True, 'actual': 'success', 'expected': 'success'},
                {'field': 'data.id', 'passed': True, 'actual': '1', 'expected': '1'}
            ]
        }
        
        result = ApiTestResult.objects.create(**result_data)
        
        # 7. 验证测试执行状态更新
        test_run.update_statistics()
        test_run.refresh_from_db()
        
        self.assertEqual(test_run.total_tests, 1)
        self.assertEqual(test_run.passed_tests, 1)
        self.assertEqual(test_run.failed_tests, 0)
        self.assertEqual(test_run.success_rate, 100.0)
        
        # 8. 完成测试执行
        response = self.client.post(f'/api/reports/test-runs/{test_run.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        test_run.refresh_from_db()
        self.assertEqual(test_run.status, 'completed')
        self.assertIsNotNone(test_run.end_time)
        
        # 9. 获取测试报告
        response = self.client.get(f'/api/reports/test-runs/{test_run.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        report_data = response.json()
        
        self.assertEqual(report_data['name'], '用户API测试执行')
        self.assertEqual(report_data['status'], 'completed')
        self.assertEqual(len(report_data['results']), 1)
        
        # 10. 导出HTML报告
        response = self.client.get(f'/api/reports/test-runs/{test_run.id}/export_html/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response['Content-Type'].startswith('text/html'))
    
    def test_test_plan_execution_workflow(self):
        """测试计划执行工作流"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 创建多个测试用例
        api1 = ApiDefinition.objects.create(
            name='登录API',
            method='POST',
            url='https://api.example.com/auth/login'
        )
        
        api2 = ApiDefinition.objects.create(
            name='获取用户列表API',
            method='GET',
            url='https://api.example.com/users'
        )
        
        testcase1 = ApiTestCase.objects.create(
            name='用户登录测试',
            api=api1,
            expected_status_code=200
        )
        
        testcase2 = ApiTestCase.objects.create(
            name='获取用户列表测试',
            api=api2,
            expected_status_code=200
        )
        
        # 创建测试计划并关联测试用例
        test_plan = TestPlan.objects.create(
            name='完整功能测试计划',
            assignee=self.admin_user,
            status='pending'
        )
        
        # 创建测试执行
        test_run = TestRun.objects.create(
            name='完整功能测试执行',
            test_plan=test_plan,
            executed_by=self.admin_user
        )
        
        # 执行所有测试用例
        for i, test_case in enumerate([testcase1, testcase2]):
            status_choice = 'passed' if i == 0 else 'failed'
            response_code = 200 if i == 0 else 500
            
            ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status=status_choice,
                response_code=response_code,
                response_time=100.0 + i * 50
            )
        
        # 更新统计信息
        test_run.update_statistics()
        test_run.refresh_from_db()
        
        # 验证统计结果
        self.assertEqual(test_run.total_tests, 2)
        self.assertEqual(test_run.passed_tests, 1)
        self.assertEqual(test_run.failed_tests, 1)
        self.assertEqual(test_run.success_rate, 50.0)
        
        # 获取统计报告
        response = self.client.get(f'/api/reports/test-runs/{test_run.id}/statistics/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        stats_data = response.json()
        self.assertIn('summary', stats_data)
        self.assertIn('api_statistics', stats_data)
        self.assertEqual(stats_data['summary']['total_tests'], 2)
        self.assertEqual(stats_data['summary']['passed_rate'], 50.0)
    
    def test_environment_switching_workflow(self):
        """测试环境切换工作流"""
        self.client.force_authenticate(user=self.admin_user)
        
        # 创建生产环境
        prod_env = Environment.objects.create(
            name='生产环境',
            description='生产环境配置',
            is_default=False,
            created_by=self.admin_user
        )
        
        EnvironmentVariable.objects.create(
            environment=prod_env,
            key='BASE_URL',
            value='https://api.prod.com',
            description='生产环境API基础URL'
        )
        
        # 切换到生产环境
        self.environment.is_default = False
        self.environment.save()
        
        prod_env.is_default = True
        prod_env.save()
        
        # 验证环境切换
        default_env = Environment.objects.filter(
            created_by=self.admin_user,
            is_default=True
        ).first()
        
        self.assertEqual(default_env, prod_env)
        
        # 记录环境使用日志
        from environments.models import EnvironmentUsageLog
        EnvironmentUsageLog.objects.create(
            environment=prod_env,
            user=self.admin_user,
            action='api_test',
            context={'test_type': 'integration'}
        )
        
        # 验证使用日志
        logs = EnvironmentUsageLog.objects.filter(environment=prod_env)
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs.first().action, 'api_test')


class CrossModuleIntegrationTest(BaseTestCase):
    """跨模块集成测试"""
    
    def setUp(self):
        super().setUp()
        self.admin_user = self.create_admin_user()
    
    def test_user_testcase_assignment_workflow(self):
        """用户和测试用例分配工作流"""
        # 创建测试用例
        testcase = TestCaseModel.objects.create(
            title='跨模块集成测试用例',
            description='测试跨模块功能',
            assignee=self.admin_user
        )
        
        # 创建测试计划
        test_plan = TestPlan.objects.create(
            name='跨模块测试计划',
            assignee=self.admin_user
        )
        test_plan.test_cases.add(testcase)
        
        # 验证关联关系
        self.assertEqual(testcase.assignee, self.admin_user)
        self.assertIn(testcase, test_plan.test_cases.all())
        self.assertIn(test_plan, testcase.plans.all())
        
        # 验证用户的关联测试用例
        user_testcases = self.admin_user.testcases.all()
        self.assertIn(testcase, user_testcases)
        
        # 验证用户的关联测试计划
        user_testplans = self.admin_user.testplans.all()
        self.assertIn(test_plan, user_testplans)
    
    def test_comment_notification_workflow(self):
        """评论和通知工作流"""
        from comments.models import Comment, Notification
        from django.contrib.contenttypes.models import ContentType
        
        # 创建被评论的测试用例
        testcase = TestCaseModel.objects.create(
            title='被评论的测试用例',
            assignee=self.admin_user
        )
        
        # 创建评论者
        commenter = self.create_test_user(username='commenter')
        
        # 创建评论并提及用户
        content_type = ContentType.objects.get_for_model(TestCaseModel)
        comment = Comment.objects.create(
            content=f'测试评论，提及@{self.admin_user.username}',
            author=commenter,
            content_type=content_type,
            object_id=testcase.id
        )
        
        # 创建通知
        notification = Notification.create_notification(
            recipient=self.admin_user,
            actor=commenter,
            verb='mentioned',
            target=testcase,
            description='您在测试用例中被提及'
        )
        
        # 验证通知创建
        self.assertIsNotNone(notification)
        self.assertEqual(notification.recipient, self.admin_user)
        self.assertEqual(notification.actor, commenter)
        self.assertFalse(notification.read)
        
        # 验证评论关联
        self.assertEqual(comment.content_object, testcase)
        self.assertEqual(comment.author, commenter)