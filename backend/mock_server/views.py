from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
import json
import time
import logging

from .models import MockAPI, MockAPIUsageLog
from .serializers import (
    MockAPIListSerializer, MockAPIDetailSerializer,
    MockAPICreateSerializer, MockAPIUpdateSerializer,
    MockAPIUsageLogSerializer, MockAPIStatsSerializer
)

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """获取客户端IP地址"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(csrf_exempt, name='dispatch')
class ServeMockAPIView(View):
    """核心Mock服务视图 - 处理所有Mock API请求"""
    
    def dispatch(self, request, full_path, *args, **kwargs):
        """处理所有HTTP方法的Mock请求"""
        try:
            # 确保路径以/开头
            if not full_path.startswith('/'):
                full_path = '/' + full_path
            
            # 移除尾部斜杠(除非是根路径)
            if full_path != '/' and full_path.endswith('/'):
                full_path = full_path.rstrip('/')
            
            method = request.method.upper()
            
            logger.info(f"Mock request: {method} {full_path}")
            
            # 查找匹配的Mock API
            try:
                mock_api = MockAPI.objects.get(
                    path=full_path,
                    method=method,
                    is_active=True
                )
            except MockAPI.DoesNotExist:
                # 记录未找到的请求
                self._log_request(
                    None, request, full_path, method, 404
                )
                
                return JsonResponse({
                    'error': 'Mock API not found',
                    'message': f'No active mock found for {method} {full_path}',
                    'available_mocks': self._get_available_mocks(),
                    'suggestion': f'You can create a mock for {method} {full_path} in the Mock Server management page.'
                }, status=404)
            
            # 模拟延迟
            if mock_api.delay_ms > 0:
                time.sleep(mock_api.delay_ms / 1000.0)
            
            # 准备响应头
            response_headers = mock_api.response_headers or {}
            
            # 如果没有指定Content-Type，自动推断
            if 'Content-Type' not in response_headers:
                response_headers['Content-Type'] = mock_api.get_content_type()
            
            # 创建响应
            response = HttpResponse(
                content=mock_api.response_body,
                status=mock_api.response_status_code,
                content_type=response_headers.get('Content-Type', 'text/plain')
            )
            
            # 设置自定义响应头
            for header, value in response_headers.items():
                if header.lower() != 'content-type':
                    response[header] = value
            
            # 记录请求日志
            self._log_request(
                mock_api, request, full_path, method, 
                mock_api.response_status_code
            )
            
            logger.info(
                f"Mock response: {mock_api.response_status_code} for {method} {full_path}"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error serving mock API: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error',
                'message': str(e)
            }, status=500)
    
    def _log_request(self, mock_api, request, path, method, status_code):
        """记录请求日志"""
        try:
            # 获取请求头(排除敏感信息)
            request_headers = {}
            for header, value in request.META.items():
                if header.startswith('HTTP_'):
                    header_name = header[5:].replace('_', '-').title()
                    # 排除敏感信息
                    if header_name.lower() not in ['authorization', 'cookie']:
                        request_headers[header_name] = value
            
            # 获取请求体
            request_body = ''
            if hasattr(request, 'body'):
                try:
                    request_body = request.body.decode('utf-8')
                    # 限制日志长度
                    if len(request_body) > 1000:
                        request_body = request_body[:1000] + '...[truncated]'
                except UnicodeDecodeError:
                    request_body = '[Binary data]'
            
            MockAPIUsageLog.objects.create(
                mock_api=mock_api,
                request_path=path,
                request_method=method,
                request_headers=request_headers,
                request_body=request_body,
                response_status_code=status_code,
                client_ip=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as e:
            logger.error(f"Error logging mock request: {str(e)}")
    
    def _get_available_mocks(self):
        """获取可用的Mock API列表"""
        try:
            mocks = MockAPI.objects.filter(is_active=True).values(
                'method', 'path', 'name'
            )[:10]  # 限制返回数量
            return [
                f"{mock['method']} {mock['path']} ({mock['name']})"
                for mock in mocks
            ]
        except Exception:
            return []


class MockAPIViewSet(viewsets.ModelViewSet):
    """Mock API管理ViewSet"""
    queryset = MockAPI.objects.all()
    permission_classes = []  # 空权限列表，允许所有用户访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['method', 'response_status_code', 'is_active']
    search_fields = ['name', 'path', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MockAPIListSerializer
        elif self.action == 'create':
            return MockAPICreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MockAPIUpdateSerializer
        else:
            return MockAPIDetailSerializer
    
    def perform_create(self, serializer):
        """创建Mock API时设置创建者"""
        serializer.save(created_by=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """创建Mock API并返回详细信息"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        # 使用DetailSerializer返回完整的对象信息
        instance = serializer.instance
        detail_serializer = MockAPIDetailSerializer(instance, context={'request': request})
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取Mock API统计信息"""
        try:
            total_mocks = MockAPI.objects.count()
            active_mocks = MockAPI.objects.filter(is_active=True).count()
            total_requests = MockAPIUsageLog.objects.count()
            
            # 今日请求数
            today = timezone.now().date()
            requests_today = MockAPIUsageLog.objects.filter(
                timestamp__date=today
            ).count()
            
            # 最常用的Mock API
            most_used_data = MockAPIUsageLog.objects.values(
                'mock_api__name', 'mock_api__method', 'mock_api__path'
            ).annotate(
                count=Count('id')
            ).order_by('-count').first()
            
            most_used_mock = {}
            if most_used_data:
                most_used_mock = {
                    'name': most_used_data['mock_api__name'],
                    'method': most_used_data['mock_api__method'],
                    'path': most_used_data['mock_api__path'],
                    'count': most_used_data['count']
                }
            
            # 方法分布
            method_distribution = dict(
                MockAPI.objects.values('method').annotate(
                    count=Count('id')
                ).values_list('method', 'count')
            )
            
            # 状态码分布
            status_code_distribution = dict(
                MockAPIUsageLog.objects.values('response_status_code').annotate(
                    count=Count('id')
                ).values_list('response_status_code', 'count')
            )
            
            stats_data = {
                'total_mocks': total_mocks,
                'active_mocks': active_mocks,
                'total_requests': total_requests,
                'requests_today': requests_today,
                'most_used_mock': most_used_mock,
                'method_distribution': method_distribution,
                'status_code_distribution': status_code_distribution
            }
            
            serializer = MockAPIStatsSerializer(stats_data)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error getting mock statistics: {str(e)}")
            return Response(
                {'error': '获取统计信息失败', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """测试Mock API"""
        try:
            mock_api = self.get_object()
            
            # 构造测试请求URL
            test_url = f"/mock{mock_api.path}"
            
            return Response({
                'mock_api': MockAPIDetailSerializer(mock_api).data,
                'test_url': test_url,
                'curl_command': self._generate_curl_command(mock_api),
                'test_info': {
                    'method': mock_api.method,
                    'expected_status': mock_api.response_status_code,
                    'expected_headers': mock_api.response_headers,
                    'expected_body': mock_api.response_body[:200] + '...' if len(mock_api.response_body) > 200 else mock_api.response_body
                }
            })
            
        except Exception as e:
            return Response(
                {'error': '生成测试信息失败', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_curl_command(self, mock_api):
        """生成curl测试命令"""
        base_url = "http://localhost:8000"  # 可以从设置中获取
        curl_cmd = f"curl -X {mock_api.method} '{base_url}/mock{mock_api.path}'"
        
        if mock_api.response_headers:
            for header, value in mock_api.response_headers.items():
                curl_cmd += f" -H '{header}: {value}'"
        
        curl_cmd += " -v"
        return curl_cmd


class MockAPIUsageLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Mock API使用日志ViewSet"""
    queryset = MockAPIUsageLog.objects.all()
    serializer_class = MockAPIUsageLogSerializer
    permission_classes = []  # 空权限列表，允许所有用户访问
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['mock_api', 'request_method', 'response_status_code']
    search_fields = ['request_path', 'client_ip']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近的请求日志"""
        try:
            limit = min(int(request.query_params.get('limit', 50)), 100)
            logs = self.queryset[:limit]
            serializer = self.get_serializer(logs, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': '获取日志失败', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )