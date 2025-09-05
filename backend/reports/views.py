from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api_test.models import TestRun, ApiTestResult
from .serializers import (
    TestRunListSerializer, TestRunDetailSerializer, 
    TestRunCreateSerializer, ApiTestResultDetailSerializer
)
from testcases.permissions import IsAdminOrReadOnly


class TestRunViewSet(viewsets.ModelViewSet):
    """测试执行记录视图集"""
    queryset = TestRun.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TestRunListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TestRunCreateSerializer
        else:
            return TestRunDetailSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 支持按测试计划筛选
        test_plan_id = self.request.query_params.get('test_plan')
        if test_plan_id:
            queryset = queryset.filter(test_plan_id=test_plan_id)
        
        # 支持按状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 支持按执行者筛选
        executed_by = self.request.query_params.get('executed_by')
        if executed_by:
            queryset = queryset.filter(executed_by_id=executed_by)
        
        return queryset.select_related('test_plan', 'executed_by').prefetch_related('results')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """标记测试执行完成"""
        test_run = self.get_object()
        if test_run.status != 'running':
            return Response(
                {'error': '只有正在运行的测试执行才能标记为完成'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_run.complete()
        serializer = self.get_serializer(test_run)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_failed(self, request, pk=None):
        """标记测试执行失败"""
        test_run = self.get_object()
        error_message = request.data.get('error_message', '')
        
        if test_run.status != 'running':
            return Response(
                {'error': '只有正在运行的测试执行才能标记为失败'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        test_run.mark_failed(error_message)
        serializer = self.get_serializer(test_run)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def export_html(self, request, pk=None):
        """导出HTML报告"""
        test_run = self.get_object()
        
        # 准备报告数据
        context = {
            'test_run': test_run,
            'results': test_run.results.select_related('test_case__api').all(),
            'summary': {
                'total_tests': test_run.total_tests,
                'passed_tests': test_run.passed_tests,
                'failed_tests': test_run.failed_tests,
                'error_tests': test_run.error_tests,
                'success_rate': test_run.success_rate,
                'duration': test_run.duration_display,
            }
        }
        
        # 渲染HTML模板
        html_content = render_to_string('reports/test_report.html', context)
        
        # 返回HTML响应
        response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="test_report_{test_run.id}_{test_run.start_time.strftime("%Y%m%d_%H%M%S")}.html"'
        
        return response
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """获取测试执行统计信息"""
        test_run = self.get_object()
        results = test_run.results.all()
        
        # 按API分组统计
        api_stats = {}
        for result in results:
            api_key = f"{result.test_case.api.method} {result.test_case.api.name}"
            if api_key not in api_stats:
                api_stats[api_key] = {
                    'api_method': result.test_case.api.method,
                    'api_name': result.test_case.api.name,
                    'api_url': result.test_case.api.url,
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'error': 0,
                    'avg_response_time': 0,
                    'response_times': []
                }
            
            api_stats[api_key]['total'] += 1
            api_stats[api_key][result.status] += 1
            if result.response_time:
                api_stats[api_key]['response_times'].append(result.response_time)
        
        # 计算平均响应时间
        for api_key in api_stats:
            response_times = api_stats[api_key]['response_times']
            if response_times:
                api_stats[api_key]['avg_response_time'] = round(
                    sum(response_times) / len(response_times), 2
                )
            del api_stats[api_key]['response_times']  # 删除原始数据
        
        # 时间趋势分析（按小时统计）
        from django.db.models import Count
        from django.db.models.functions import TruncHour
        
        hourly_stats = results.annotate(
            hour=TruncHour('executed_at')
        ).values('hour').annotate(
            total=Count('id'),
            passed=Count('id', filter=models.Q(status='passed')),
            failed=Count('id', filter=models.Q(status='failed')),
            error=Count('id', filter=models.Q(status='error'))
        ).order_by('hour')
        
        return Response({
            'api_statistics': list(api_stats.values()),
            'hourly_trends': list(hourly_stats),
            'summary': {
                'total_apis': len(api_stats),
                'total_tests': test_run.total_tests,
                'passed_rate': test_run.success_rate,
                'avg_response_time': self._calculate_avg_response_time(results),
                'duration': test_run.duration_display
            }
        })
    
    def _calculate_avg_response_time(self, results):
        """计算平均响应时间"""
        response_times = [r.response_time for r in results if r.response_time is not None]
        if response_times:
            return round(sum(response_times) / len(response_times), 2)
        return 0