from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import json

User = get_user_model()

from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult, TestRun
from testcases.models import TestPlan
from reports.serializers import TestRunListSerializer, TestRunDetailSerializer


class TestRunViewSetTest(APITestCase):
    def setUp(self):
        """设置测试数据"""
        self.client = APIClient()
        
        # 清理现有数据，确保测试隔离
        TestRun.objects.all().delete()
        TestPlan.objects.all().delete()
        ApiTestResult.objects.all().delete()
        ApiDefinition.objects.all().delete()
        ApiTestCase.objects.all().delete()
        User.objects.all().delete()
        
        # 创建用户
        self.user = User.objects.create_user(
            username='testuser2025',
            email='test2025@example.com',
            password='testpass123'
        )
        # 设置用户为超级用户或给予需要的权限
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_authenticate(user=self.user)
        
        # 创建测试计划
        self.test_plan = TestPlan.objects.create(
            name='测试计划1',
            status='pending',
            assignee=self.user
        )
        
        # 创建API定义和测试用例
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
        
        # 创建测试执行
        self.test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user,
            status='completed',
            end_time=timezone.now()
        )
        
        # 创建测试结果
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='passed',
            response_code=200,
            response_time=150.0
        )
        
        ApiTestResult.objects.create(
            test_case=self.test_case,
            test_run=self.test_run,
            status='failed',
            response_code=500,
            response_time=200.0
        )

    def test_list_test_runs(self):
        """测试获取测试执行列表"""
        # 清理当前用户的测试数据
        TestRun.objects.all().delete()
        
        # 重新创建测试执行
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user,
            status='completed',
            end_time=timezone.now()
        )
        
        url = '/api/reports/test-runs/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['name'], '测试执行1')
        else:
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['name'], '测试执行1')

    def test_retrieve_test_run(self):
        """测试获取单个测试执行详情"""
        url = f'/api/reports/test-runs/{self.test_run.pk}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], '测试执行1')
        self.assertEqual(len(response.data['results']), 2)

    def test_create_test_run(self):
        """测试创建测试执行"""
        url = '/api/reports/test-runs/'
        data = {
            'name': '新测试执行',
            'test_plan': self.test_plan.id,
            'description': '测试描述'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], '新测试执行')
        # 修复: 检查executed_by字段是否存在
        if 'executed_by' in response.data:
            self.assertEqual(response.data['executed_by'], self.user.id)
        else:
            # 如果序列化器不返回executed_by，检查数据库中的实际值
            created_run = TestRun.objects.get(name='新测试执行')
            self.assertEqual(created_run.executed_by, self.user)

    def test_filter_by_test_plan(self):
        """测试按测试计划过滤"""
        # 清理当前数据
        TestRun.objects.all().delete()
        
        # 重新创建测试执行
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user,
            status='completed'
        )
        
        url = '/api/reports/test-runs/'
        response = self.client.get(url, {'test_plan': self.test_plan.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_filter_by_status(self):
        """测试按状态过滤"""
        # 清理当前数据
        TestRun.objects.all().delete()
        
        # 重新创建测试执行
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user,
            status='completed'
        )
        
        url = '/api/reports/test-runs/'
        response = self.client.get(url, {'status': 'completed'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_search_by_name(self):
        """测试按名称搜索"""
        # 清理当前数据
        TestRun.objects.all().delete()
        
        # 重新创建测试执行
        test_run = TestRun.objects.create(
            name='测试执行1',
            test_plan=self.test_plan,
            executed_by=self.user,
            status='completed'
        )
        
        url = '/api/reports/test-runs/'
        response = self.client.get(url, {'search': '测试执行1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：检查分页结果中的results字段
        if 'results' in response.data:
            self.assertEqual(len(response.data['results']), 1)
        else:
            self.assertEqual(len(response.data), 1)

    def test_statistics_endpoint(self):
        """测试统计信息接口"""
        url = f'/api/reports/test-runs/{self.test_run.pk}/statistics/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 修复: 根据实际API响应格式调整验证
        self.assertIn('summary', response.data)
        self.assertIn('api_statistics', response.data)
        self.assertIn('hourly_trends', response.data)
        
        # 验证summary中包含的统计数据
        summary = response.data['summary']
        expected_summary_keys = ['total_apis', 'total_tests', 'passed_rate', 'avg_response_time', 'duration']
        for key in expected_summary_keys:
            self.assertIn(key, summary)

    def test_export_html_endpoint(self):
        """测试HTML导出接口"""
        url = f'/api/reports/test-runs/{self.test_run.pk}/export_html/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 修复：Content-Type可能包含charset
        self.assertTrue(response['Content-Type'].startswith('text/html'))
        self.assertIn('attachment', response['Content-Disposition'])

    def test_delete_test_run(self):
        """测试删除测试执行"""
        url = f'/api/reports/test-runs/{self.test_run.pk}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(TestRun.objects.filter(pk=self.test_run.pk).exists())


class TestRunSerializerTest(TestCase):
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
            executed_by=self.user,
            status='completed'
        )

    def test_list_serializer(self):
        """测试列表序列化器"""
        serializer = TestRunListSerializer(instance=self.test_run)
        data = serializer.data
        
        expected_fields = [
            'id', 'name', 'status', 'test_plan_name', 'executed_by_username',
            'start_time', 'duration_display', 'total_tests', 'passed_tests',
            'failed_tests', 'error_tests', 'success_rate'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)

    def test_detail_serializer(self):
        """测试详情序列化器"""
        serializer = TestRunDetailSerializer(instance=self.test_run)
        data = serializer.data
        
        expected_fields = [
            'id', 'name', 'description', 'status', 'test_plan', 'test_plan_detail',
            'executed_by', 'executed_by_username', 'start_time', 'end_time',
            'duration_display', 'total_tests', 'passed_tests', 'failed_tests',
            'error_tests', 'success_rate', 'avg_response_time', 'results'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)