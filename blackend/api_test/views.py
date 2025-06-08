from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
import requests
import json
import time
from .models import ApiDefinition, ApiTestCase, ApiTestResult, ApiTestSuite
from .serializers import (
    ApiDefinitionSerializer, ApiTestCaseSerializer,
    ApiTestResultSerializer, ApiTestSuiteSerializer
)
from testcases.permissions import IsAdminOrReadOnly

class ApiTestService:
    """API测试执行服务"""
    
    @staticmethod
    def execute_test_case(test_case, user):
        """执行单个测试用例"""
        if not test_case.is_active:
            return ApiTestResult.objects.create(
                test_case=test_case,
                status='error',
                error_message='测试用例已禁用',
                executed_by=user
            )
        
        api = test_case.api
        
        # 准备请求数据
        headers = {**api.get_headers(), **test_case.get_headers()}
        params = {**api.get_params(), **test_case.get_params()}
        body = test_case.get_body() or api.get_body()
        
        # 处理变量替换
        variables = test_case.get_variables()
        if variables:
            headers = ApiTestService._replace_variables(headers, variables)
            params = ApiTestService._replace_variables(params, variables)
            body = ApiTestService._replace_variables(body, variables)
        
        try:
            # 发送请求
            start_time = time.time()
            response = requests.request(
                method=api.method,
                url=api.url,
                headers=headers,
                params=params,
                json=body if api.method in ['POST', 'PUT', 'PATCH'] and body else None,
                timeout=30  # 设置超时时间
            )
            end_time = time.time()
            
            # 计算响应时间
            response_time = (end_time - start_time) * 1000
            
            # 执行断言检查
            assertion_results = []
            status_result = 'passed'
            error_message = ''
            
            # 1. 检查状态码
            expected_status = test_case.expected_status_code
            if response.status_code != expected_status:
                status_result = 'failed'
                error_message = f"状态码断言失败: 期望 {expected_status}, 实际 {response.status_code}"
                assertion_results.append({
                    'type': 'status_code',
                    'expected': expected_status,
                    'actual': response.status_code,
                    'passed': False,
                    'message': error_message
                })
            else:
                assertion_results.append({
                    'type': 'status_code',
                    'expected': expected_status,
                    'actual': response.status_code,
                    'passed': True,
                    'message': '状态码检查通过'
                })
            
            # 2. 检查响应时间
            if test_case.max_response_time and response_time > test_case.max_response_time:
                status_result = 'failed'
                time_error = f"响应时间断言失败: 期望小于 {test_case.max_response_time}ms, 实际 {response_time:.2f}ms"
                if not error_message:
                    error_message = time_error
                assertion_results.append({
                    'type': 'response_time',
                    'expected': f"<{test_case.max_response_time}ms",
                    'actual': f"{response_time:.2f}ms",
                    'passed': False,
                    'message': time_error
                })
            elif test_case.max_response_time:
                assertion_results.append({
                    'type': 'response_time',
                    'expected': f"<{test_case.max_response_time}ms",
                    'actual': f"{response_time:.2f}ms",
                    'passed': True,
                    'message': '响应时间检查通过'
                })
            
            # 3. 执行自定义断言
            custom_assertions = test_case.get_assertions()
            for assertion in custom_assertions:
                assertion_result = ApiTestService._execute_assertion(assertion, response)
                assertion_results.append(assertion_result)
                if not assertion_result['passed'] and status_result == 'passed':
                    status_result = 'failed'
                    if not error_message:
                        error_message = assertion_result['message']
            
            # 获取响应头
            response_headers = dict(response.headers)
            
            # 创建测试结果
            result = ApiTestResult.objects.create(
                test_case=test_case,
                status=status_result,
                response_code=response.status_code,
                response_time=response_time,
                response_body=response.text,
                response_headers=json.dumps(response_headers),
                error_message=error_message,
                assertion_results=json.dumps(assertion_results),
                executed_by=user
            )
            
            return result
            
        except requests.exceptions.Timeout:
            return ApiTestResult.objects.create(
                test_case=test_case,
                status='error',
                error_message='请求超时',
                executed_by=user
            )
        except requests.exceptions.ConnectionError:
            return ApiTestResult.objects.create(
                test_case=test_case,
                status='error',
                error_message='连接错误，无法访问目标服务器',
                executed_by=user
            )
        except Exception as e:
            return ApiTestResult.objects.create(
                test_case=test_case,
                status='error',
                error_message=f'执行异常: {str(e)}',
                executed_by=user
            )
    
    @staticmethod
    def _replace_variables(data, variables):
        """替换数据中的变量"""
        if isinstance(data, dict):
            return {k: ApiTestService._replace_variables(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [ApiTestService._replace_variables(item, variables) for item in data]
        elif isinstance(data, str):
            for var_name, var_value in variables.items():
                data = data.replace(f"{{{var_name}}}", str(var_value))
            return data
        return data
    
    @staticmethod
    def _execute_assertion(assertion, response):
        """执行单个断言"""
        try:
            assertion_type = assertion.get('type')
            expected = assertion.get('expected')
            field = assertion.get('field', '')
            
            if assertion_type == 'json_path':
                # JSON路径断言
                try:
                    response_json = response.json()
                    actual = ApiTestService._get_json_value(response_json, field)
                    passed = actual == expected
                    return {
                        'type': assertion_type,
                        'field': field,
                        'expected': expected,
                        'actual': actual,
                        'passed': passed,
                        'message': f"JSON路径 {field} 断言{'通过' if passed else '失败'}"
                    }
                except Exception as e:
                    return {
                        'type': assertion_type,
                        'field': field,
                        'expected': expected,
                        'actual': None,
                        'passed': False,
                        'message': f"JSON路径断言执行失败: {str(e)}"
                    }
            
            elif assertion_type == 'contains':
                # 包含断言
                actual = response.text
                passed = expected in actual
                return {
                    'type': assertion_type,
                    'expected': expected,
                    'actual': f"响应体长度: {len(actual)}",
                    'passed': passed,
                    'message': f"包含断言{'通过' if passed else '失败'}"
                }
            
            elif assertion_type == 'not_contains':
                # 不包含断言
                actual = response.text
                passed = expected not in actual
                return {
                    'type': assertion_type,
                    'expected': f"不包含: {expected}",
                    'actual': f"响应体长度: {len(actual)}",
                    'passed': passed,
                    'message': f"不包含断言{'通过' if passed else '失败'}"
                }
            
            elif assertion_type == 'header':
                # 响应头断言
                header_name = assertion.get('header_name')
                actual = response.headers.get(header_name)
                passed = actual == expected
                return {
                    'type': assertion_type,
                    'field': header_name,
                    'expected': expected,
                    'actual': actual,
                    'passed': passed,
                    'message': f"响应头 {header_name} 断言{'通过' if passed else '失败'}"
                }
            
            else:
                return {
                    'type': assertion_type,
                    'expected': expected,
                    'actual': None,
                    'passed': False,
                    'message': f"不支持的断言类型: {assertion_type}"
                }
                
        except Exception as e:
            return {
                'type': assertion.get('type', 'unknown'),
                'expected': assertion.get('expected'),
                'actual': None,
                'passed': False,
                'message': f"断言执行异常: {str(e)}"
            }
    
    @staticmethod
    def _get_json_value(data, path):
        """根据路径获取JSON值，支持点号分隔的路径"""
        keys = path.split('.')
        current = data
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                current = current[index] if 0 <= index < len(current) else None
            else:
                return None
        return current


class ApiDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ApiDefinition.objects.all()
    serializer_class = ApiDefinitionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ApiTestCaseViewSet(viewsets.ModelViewSet):
    queryset = ApiTestCase.objects.all()
    serializer_class = ApiTestCaseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行单个测试用例"""
        test_case = self.get_object()
        result = ApiTestService.execute_test_case(test_case, request.user)
        return Response(ApiTestResultSerializer(result).data)

    @action(detail=False, methods=['post'])
    def batch_execute(self, request):
        """批量执行测试用例"""
        case_ids = request.data.get('case_ids', [])
        if not case_ids:
            return Response({'error': '请提供要执行的测试用例ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        
        test_cases = ApiTestCase.objects.filter(id__in=case_ids)
        results = []
        
        for test_case in test_cases:
            result = ApiTestService.execute_test_case(test_case, request.user)
            results.append(ApiTestResultSerializer(result).data)
        
        summary = {
            'total_cases': len(results),
            'passed': len([r for r in results if r['status'] == 'passed']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'errors': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
        
        return Response(summary)


class ApiTestResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApiTestResult.objects.all().order_by('-executed_at')
    serializer_class = ApiTestResultSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        test_case_id = self.request.query_params.get('test_case_id')
        status_filter = self.request.query_params.get('status')
        
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset


class ApiTestSuiteViewSet(viewsets.ModelViewSet):
    queryset = ApiTestSuite.objects.all()
    serializer_class = ApiTestSuiteSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行测试套件中的所有测试用例"""
        suite = self.get_object()
        results = []
        
        for test_case in suite.test_cases.filter(is_active=True):
            result = ApiTestService.execute_test_case(test_case, request.user)
            results.append(ApiTestResultSerializer(result).data)
        
        # 返回套件执行的汇总信息
        summary = {
            'suite_id': suite.id,
            'suite_name': suite.name,
            'total_cases': len(results),
            'passed': len([r for r in results if r['status'] == 'passed']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'errors': len([r for r in results if r['status'] == 'error']),
            'execution_time': sum([r.get('response_time', 0) for r in results if r.get('response_time')]),
            'results': results
        }
        
        return Response(summary)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """获取测试套件的历史执行结果"""
        suite = self.get_object()
        results = ApiTestResult.objects.filter(
            test_case__in=suite.test_cases.all()
        ).order_by('-executed_at')[:50]  # 限制返回最近50条结果
        
        return Response(ApiTestResultSerializer(results, many=True).data)