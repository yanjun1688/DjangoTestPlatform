from django.test import TestCase
from django.contrib.auth import get_user_model
from api_test.models import ApiDefinition, ApiTestCase, TestRun, ApiTestResult
from testcases.models import TestPlan

User = get_user_model()

class TestRunModelIntegrationTest(TestCase):
    """测试执行记录模型集成测试"""
    
    def setUp(self):
        # 创建测试用户
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='admin'
        )
        
        # 创建测试数据
        self.test_plan = TestPlan.objects.create(
            name='测试计划1',
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
        
        self.test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user
        )
    
    def test_test_run_with_results(self):
        """测试包含测试结果的测试执行"""
        # 创建测试结果
        result1 = ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_code=200,
            response_time=100.0
        )
        
        result2 = ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='failed',
            response_code=500,
            response_time=200.0
        )
        
        # 更新统计信息
        self.test_run.update_statistics()
        
        # 验证统计信息
        self.assertEqual(self.test_run.total_tests, 2)
        self.assertEqual(self.test_run.passed_tests, 1)
        self.assertEqual(self.test_run.failed_tests, 1)
        self.assertEqual(self.test_run.error_tests, 0)
        self.assertEqual(self.test_run.success_rate, 50.0)
    
    def test_test_run_complete_flow(self):
        """测试完整的测试执行流程"""
        # 初始状态
        self.assertEqual(self.test_run.status, 'running')
        self.assertTrue(self.test_run.is_running)
        self.assertIsNone(self.test_run.end_time)
        
        # 标记完成
        self.test_run.complete()
        
        # 验证完成状态
        self.assertEqual(self.test_run.status, 'completed')
        self.assertFalse(self.test_run.is_running)
        self.assertIsNotNone(self.test_run.end_time)
    
    def test_test_run_failed_flow(self):
        """测试测试执行失败流程"""
        error_message = '测试环境异常'
        
        # 标记失败
        self.test_run.mark_failed(error_message)
        
        # 验证失败状态
        self.assertEqual(self.test_run.status, 'failed')
        self.assertFalse(self.test_run.is_running)
        self.assertEqual(self.test_run.error_message, error_message)
        self.assertIsNotNone(self.test_run.end_time)
    
    def test_avg_response_time_calculation(self):
        """测试平均响应时间计算"""
        # 创建多个测试结果
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_time=100.0
        )
        
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_time=200.0
        )
        
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_time=150.0
        )
        
        # 计算平均响应时间
        avg_time = self.test_run.avg_response_time
        self.assertEqual(avg_time, 150.0)
    
    def test_test_run_without_results(self):
        """测试没有测试结果的测试执行"""
        # 更新统计信息
        self.test_run.update_statistics()
        
        # 验证初始统计信息
        self.assertEqual(self.test_run.total_tests, 0)
        self.assertEqual(self.test_run.passed_tests, 0)
        self.assertEqual(self.test_run.failed_tests, 0)
        self.assertEqual(self.test_run.error_tests, 0)
        self.assertEqual(self.test_run.success_rate, 0)
        self.assertEqual(self.test_run.avg_response_time, 0)
    
    def test_duration_display(self):
        """测试执行时长显示"""
        from django.utils import timezone
        from datetime import timedelta
        
        # 设置开始和结束时间
        start_time = timezone.now() - timedelta(minutes=5, seconds=30)
        end_time = timezone.now()
        
        self.test_run.start_time = start_time
        self.test_run.end_time = end_time
        self.test_run.save()
        
        # 验证时长显示
        duration_display = self.test_run.duration_display
        self.assertIsInstance(duration_display, str)
        self.assertIn('分', duration_display)
    
    def test_test_run_string_representation(self):
        """测试测试执行的字符串表示"""
        expected = f"{self.test_run.name} - {self.test_plan.name}"
        self.assertEqual(str(self.test_run), expected)
        
        # 测试没有测试计划的情况
        no_plan_run = TestRun.objects.create(
            name='无计划测试',
            executed_by=self.user
        )
        expected_no_plan = "无计划测试 - 无测试计划"
        self.assertEqual(str(no_plan_run), expected_no_plan)