from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult, TestRun
from testcases.models import TestPlan

User = get_user_model()


class TestRunModelTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_plan = TestPlan.objects.create(
            name='测试计划1',
            status='pending',
            assignee=self.user
        )
        
        self.api_definition = ApiDefinition.objects.create(
            name='测试API',
            method='GET',
            url='https://api.example.com/test'
        )
        
        self.test_case = ApiTestCase.objects.create(
            name='测试用例1',
            api=self.api_definition,
            expected_status_code=200
        )

    def test_create_test_run(self):
        """测试创建TestRun"""
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        self.assertEqual(test_run.name, '测试执行1')
        self.assertEqual(test_run.test_plan, self.test_plan)
        self.assertEqual(test_run.executed_by, self.user)
        self.assertEqual(test_run.status, 'running')
        self.assertIsNotNone(test_run.start_time)
        self.assertIsNone(test_run.end_time)

    def test_test_run_duration_property(self):
        """测试TestRun duration属性"""
        start_time = timezone.now() - timedelta(minutes=5)
        end_time = timezone.now()
        
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user,
            start_time=start_time,
            end_time=end_time,
            status='completed'
        )
        
        duration = test_run.duration
        self.assertIsNotNone(duration)
        self.assertGreater(duration.total_seconds(), 0)

    def test_test_run_duration_display_property(self):
        """测试TestRun duration_display属性"""
        start_time = timezone.now() - timedelta(minutes=5, seconds=30)
        end_time = timezone.now()
        
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user,
            start_time=start_time,
            end_time=end_time,
            status='completed'
        )
        
        duration_display = test_run.duration_display
        self.assertIsInstance(duration_display, str)
        self.assertIn('分', duration_display)

    def test_test_run_statistics_methods(self):
        """测试TestRun统计方法"""
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        # 创建测试结果
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=test_run,
            status='passed',
            response_code=200,
            response_time=100.5
        )
        
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=test_run,
            status='failed',
            response_code=500,
            response_time=200.3
        )
        
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=test_run,
            status='error',
            error_message='连接错误'
        )
        
        # 更新统计信息
        test_run.update_statistics()
        
        # 测试统计属性
        self.assertEqual(test_run.total_tests, 3)
        self.assertEqual(test_run.passed_tests, 1)
        self.assertEqual(test_run.failed_tests, 1)
        self.assertEqual(test_run.error_tests, 1)
        self.assertAlmostEqual(test_run.success_rate, 33.33, places=1)

    def test_update_statistics_method(self):
        """测试update_statistics方法"""
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        # 创建测试结果
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=test_run,
            status='passed',
            response_code=200,
            response_time=150.0
        )
        
        # 调用update_statistics
        test_run.update_statistics()
        
        # 刷新对象
        test_run.refresh_from_db()
        
        self.assertEqual(test_run.total_tests, 1)
        self.assertEqual(test_run.passed_tests, 1)
        self.assertEqual(test_run.failed_tests, 0)
        self.assertEqual(test_run.error_tests, 0)
        self.assertEqual(test_run.success_rate, 100.0)
        self.assertEqual(test_run.avg_response_time, 150.0)

    def test_complete_method(self):
        """测试complete方法"""
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        self.assertEqual(test_run.status, 'running')
        self.assertIsNone(test_run.end_time)
        
        # 调用complete方法
        test_run.complete()
        
        self.assertEqual(test_run.status, 'completed')
        self.assertIsNotNone(test_run.end_time)

    def test_mark_failed_method(self):
        """测试mark_failed方法"""
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        error_message = '测试执行失败'
        test_run.mark_failed(error_message)
        
        self.assertEqual(test_run.status, 'failed')
        self.assertEqual(test_run.error_message, error_message)
        self.assertIsNotNone(test_run.end_time)

    def test_avg_response_time_calculation(self):
        """测试平均响应时间计算"""
        test_run = TestRun.objects.create(
            name='测试执行',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        # 创建多个测试结果
        response_times = [100.0, 200.0, 300.0]
        for i, time in enumerate(response_times):
            ApiTestResult.objects.create(
                test_case=self.test_case,
                test_run=test_run,
                status='passed',
                response_code=200,
                response_time=time
            )
        
        # 刷新统计
        test_run.update_statistics()
        test_run.refresh_from_db()
        
        expected_avg = sum(response_times) / len(response_times)
        self.assertEqual(test_run.avg_response_time, expected_avg)

    def test_string_representation(self):
        """测试字符串表示"""
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        expected_str = f"测试执行1 - {self.test_plan.name}"
        self.assertEqual(str(test_run), expected_str)

    def test_test_run_without_test_plan(self):
        """测试没有测试计划的TestRun"""
        test_run = TestRun.objects.create(
            name='独立测试执行',
            executed_by=self.user
        )
        
        self.assertIsNone(test_run.test_plan)
        self.assertEqual(str(test_run), '独立测试执行 - 无测试计划')


class ApiTestResultModelTest(TestCase):
    def setUp(self):
        """设置测试数据"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.test_plan = TestPlan.objects.create(
            name='测试计划1',
            status='pending',
            assignee=self.user
        )
        
        self.test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user
        )
        
        self.api_definition = ApiDefinition.objects.create(
            name='测试API',
            method='GET',
            url='https://api.example.com/test'
        )
        
        self.test_case = ApiTestCase.objects.create(
            name='测试用例1',
            api=self.api_definition,
            expected_status_code=200
        )

    def test_create_api_test_result_with_test_run(self):
        """测试创建关联TestRun的ApiTestResult"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_code=200,
            response_time=150.5
        )
        
        self.assertEqual(result.test_case, self.test_case)
        self.assertEqual(result.test_run, self.test_run)
        self.assertEqual(result.status, 'passed')
        self.assertEqual(result.response_code, 200)
        self.assertEqual(result.response_time, 150.5)

    def test_api_test_result_properties(self):
        """测试ApiTestResult的属性访问"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_code=200,
            response_time=150.5
        )
        
        # 测试通过关联字段访问相关属性
        self.assertEqual(result.test_case.name, self.test_case.name)
        self.assertEqual(result.test_case.api.name, self.api_definition.name)
        self.assertEqual(result.test_case.api.method, self.api_definition.method)
        self.assertEqual(result.test_case.api.url, self.api_definition.url)

    def test_api_test_result_without_test_run(self):
        """测试没有test_run的ApiTestResult"""
        result = ApiTestResult.objects.create(
            test_case=self.test_case,
            status='passed',
            response_code=200
        )
        
        self.assertIsNone(result.test_run)
        self.assertEqual(result.test_case, self.test_case)