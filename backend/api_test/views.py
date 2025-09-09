from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
import requests
import json
import time
import os
from .models import ApiDefinition, ApiTestCase, ApiTestResult, TestRun
from .serializers import (
    ApiDefinitionSerializer, ApiTestCaseSerializer,
    ApiTestResultSerializer
)
from .error_handlers import (
    handle_request_exception, create_error_result, 
    TestExecutionError, APIError
)
from testcases.models import TestDataFile
from environments.models import Environment
from environments.views import log_environment_usage
import re
import logging

logger = logging.getLogger(__name__)

class ApiTestService:
    """API测试执行服务"""
    
    @staticmethod
    def execute_test_case(test_case, user, test_run=None, environment=None):
        """执行单个测试用例（支持数据驱动和环境变量）"""
        if not test_case.is_active:
            return ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status='error',
                error_message='测试用例已禁用',
                executed_by=user
            )
        
        # 检查是否有关联的数据文件
        # 注意：ApiTestCase没有直接的data_file关系，需要通过名称或其他方式关联
        data_file = None
        if hasattr(test_case, 'data_file_relation'):
            # 如果有直接关系
            data_file = test_case.data_file_relation
        else:
            # 尝试通过名称查找关联的TestCase和其数据文件
            try:
                from testcases.models import TestCase
                related_test_case = TestCase.objects.filter(title__icontains=test_case.name).first()
                if related_test_case and hasattr(related_test_case, 'data_file'):
                    data_file = related_test_case.data_file
            except:
                pass
        
        if data_file:
            return ApiTestService._execute_data_driven_test(test_case, data_file, user, test_run, environment)
        else:
            # 没有数据文件，执行普通测试
            return ApiTestService._execute_single_test(test_case, user, {}, test_run=test_run, environment=environment)

    @staticmethod
    def _execute_data_driven_test(test_case, data_file, user, test_run=None, environment=None):
        """执行数据驱动测试"""
        try:
            # 解析数据文件
            parsed_data = data_file.parse_file()
            headers = parsed_data['headers']
            rows = parsed_data['rows']
            
            if not rows:
                return ApiTestResult.objects.create(
                    test_case=test_case,
                    test_run=test_run,
                    status='error',
                    error_message='数据文件中没有找到测试数据',
                    executed_by=user
                )
            
            # 为每一行数据执行测试
            results = []
            total_tests = len(rows)
            passed_tests = 0
            failed_tests = 0
            error_tests = 0
            
            for row_index, row in enumerate(rows):
                # 构建变量字典
                variables = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        variables[header] = row[i]
                
                # 执行单次测试
                result = ApiTestService._execute_single_test(
                    test_case, user, variables, row_index + 1, test_run, environment
                )
                results.append(result)
                
                # 统计结果
                if result.status == 'passed':
                    passed_tests += 1
                elif result.status == 'failed':
                    failed_tests += 1
                else:
                    error_tests += 1
            
            # 创建汇总结果
            overall_status = 'passed' if failed_tests == 0 and error_tests == 0 else 'failed'
            if error_tests > 0:
                overall_status = 'error'
            
            summary_result = ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status=overall_status,
                response_code=None,
                response_time=None,
                response_body=json.dumps({
                    'data_driven_summary': {
                        'total_tests': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'errors': error_tests,
                        'success_rate': f"{(passed_tests / total_tests * 100):.1f}%"
                    },
                    'individual_results': [
                        {
                            'row': i + 1,
                            'status': result.status,
                            'response_code': result.response_code,
                            'response_time': result.response_time,
                            'error_message': result.error_message or None
                        }
                        for i, result in enumerate(results)
                    ]
                }),
                error_message=f'数据驱动测试完成: {passed_tests}/{total_tests} 通过' if overall_status != 'error' else '数据驱动测试执行出错',
                assertion_results=json.dumps([]),
                executed_by=user
            )
            
            return summary_result
            
        except Exception as e:
            return ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status='error',
                error_message=f'数据驱动测试执行失败: {str(e)}',
                executed_by=user
            )

    @staticmethod
    def _execute_single_test(test_case, user, variables=None, row_number=None, test_run=None, environment=None):
        """执行单次测试（原有逻辑，增加了变量支持和环境变量支持）"""
        if variables is None:
            variables = {}
        
        api = test_case.api
        
        # 准备请求数据
        headers = {**api.get_headers(), **test_case.get_headers()}
        params = {**api.get_params(), **test_case.get_params()}
        body = test_case.get_body() or api.get_body()
        
        # 合并用例变量和数据驱动变量
        all_variables = {**test_case.get_variables(), **variables}
        
        # 获取环境变量
        env_variables = {}
        if environment:
            env_variables = {var.key: var.value for var in environment.variables.all()}
            # 记录环境使用
            log_environment_usage(environment, user, 'api_test', {
                'test_case_id': test_case.id,
                'test_case_name': test_case.name,
                'api_url': api.url,
                'api_method': api.method
            })
        
        # 合并所有变量（环境变量优先级最高）
        all_variables = {**all_variables, **env_variables}
        
        # 处理变量替换
        if all_variables:
            url = ApiTestService._replace_variables(api.url, all_variables)
            headers = ApiTestService._replace_variables(headers, all_variables)
            params = ApiTestService._replace_variables(params, all_variables)
            body = ApiTestService._replace_variables(body, all_variables)
        else:
            url = api.url
        
        try:
            # 发送请求
            start_time = time.time()
            response = requests.request(
                method=api.method,
                url=url,
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
                if row_number:
                    error_message = f"[数据行{row_number}] {error_message}"
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
                if row_number:
                    time_error = f"[数据行{row_number}] {time_error}"
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
                if row_number and not assertion_result['passed']:
                    assertion_result['message'] = f"[数据行{row_number}] {assertion_result['message']}"
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
                test_run=test_run,
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
            error_msg = '请求超时'
            if row_number:
                error_msg = f"[数据行{row_number}] {error_msg}"
            return ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status='error',
                error_message=error_msg,
                executed_by=user
            )
        except requests.exceptions.ConnectionError:
            error_msg = '连接错误，无法访问目标服务器'
            if row_number:
                error_msg = f"[数据行{row_number}] {error_msg}"
            return ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status='error',
                error_message=error_msg,
                executed_by=user
            )
        except Exception as e:
            error_msg = f'执行异常: {str(e)}'
            if row_number:
                error_msg = f"[数据行{row_number}] {error_msg}"
            return ApiTestResult.objects.create(
                test_case=test_case,
                test_run=test_run,
                status='error',
                error_message=error_msg,
                executed_by=user
            )
    
    @staticmethod
    def _replace_variables(data, variables):
        """替换数据中的变量，支持{{variable}}格式"""
        if isinstance(data, dict):
            return {k: ApiTestService._replace_variables(v, variables) for k, v in data.items()}
        elif isinstance(data, list):
            return [ApiTestService._replace_variables(item, variables) for item in data]
        elif isinstance(data, str):
            # 使用正则表达式替换{{variable}}格式的变量
            def replace_match(match):
                var_name = match.group(1)
                return str(variables.get(var_name, match.group(0)))
            
            # 替换{{variable}}格式
            data = re.sub(r'\{\{(\w+)\}\}', replace_match, data)
            
            # 兼容旧的{variable}格式
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
    
    @staticmethod
    def execute_test_plan(test_plan, user, run_name=None, environment=None):
        """执行测试计划，创建测试执行记录"""
        from testcases.models import TestPlan
        
        # 如果传入的是测试计划ID，获取对象
        if isinstance(test_plan, int):
            test_plan = TestPlan.objects.get(id=test_plan)
        
        # 创建测试执行记录
        if not run_name:
            run_name = f"{test_plan.name} - {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        test_run = TestRun.objects.create(
            name=run_name,
            test_plan=test_plan,
            executed_by=user,
            status='running'
        )
        
        try:
            # 获取测试计划关联的所有API测试用例
            api_test_cases = []
            for test_case in test_plan.test_cases.filter(is_active=True):
                # 查找关联的API测试用例
                related_api_cases = ApiTestCase.objects.filter(
                    name__icontains=test_case.title
                ).filter(is_active=True)
                api_test_cases.extend(related_api_cases)
            
            if not api_test_cases:
                test_run.mark_failed("测试计划中没有找到可执行的API测试用例")
                return test_run
            
            results = []
            # 执行每个测试用例
            for api_test_case in api_test_cases:
                try:
                    result = ApiTestService.execute_test_case(api_test_case, user, test_run, environment)
                    results.append(result)
                except Exception as e:
                    # 记录单个用例执行错误
                    error_result = ApiTestResult.objects.create(
                        test_case=api_test_case,
                        test_run=test_run,
                        status='error',
                        error_message=f'用例执行异常: {str(e)}',
                        executed_by=user
                    )
                    results.append(error_result)
            
            # 完成测试执行
            test_run.complete()
            return test_run
            
        except Exception as e:
            test_run.mark_failed(f"测试计划执行失败: {str(e)}")
            return test_run


class ApiDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ApiDefinition.objects.all().select_related('created_by').order_by('-created_at')
    serializer_class = ApiDefinitionSerializer
    permission_classes = []  # 所有用户可以执行所有操作，不区分角色

    def perform_create(self, serializer):
        # 处理匿名用户的情况
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)


class ApiTestCaseViewSet(viewsets.ModelViewSet):
    queryset = ApiTestCase.objects.all().select_related('api', 'created_by').prefetch_related('results').order_by('-created_at')
    serializer_class = ApiTestCaseSerializer
    permission_classes = []  # 所有用户可以执行所有操作，不区分角色

    def perform_create(self, serializer):
        # 处理匿名用户的情况
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(created_by=user)

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        """执行单个测试用例"""
        test_case = self.get_object()
        # 处理匿名用户的情况
        user = request.user if request.user.is_authenticated else None
        
        # 获取环境参数
        environment = None
        environment_id = request.data.get('environment_id')
        if environment_id:
            try:
                environment = Environment.objects.get(id=environment_id, created_by=user)
            except Environment.DoesNotExist:
                return Response(
                    {'error': '指定的环境不存在或无权访问'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        result = ApiTestService.execute_test_case(test_case, user, environment=environment)
        return Response(ApiTestResultSerializer(result).data)

    @action(detail=False, methods=['post'])
    def batch_execute(self, request):
        """批量执行测试用例"""
        case_ids = request.data.get('case_ids', [])
        if not case_ids:
            return Response({'error': '请提供要执行的测试用例ID列表'}, status=status.HTTP_400_BAD_REQUEST)
        
        test_cases = ApiTestCase.objects.filter(id__in=case_ids)
        results = []
        # 处理匿名用户的情况
        user = request.user if request.user.is_authenticated else None
        
        # 获取环境参数
        environment = None
        environment_id = request.data.get('environment_id')
        if environment_id:
            try:
                environment = Environment.objects.get(id=environment_id, created_by=user)
            except Environment.DoesNotExist:
                return Response(
                    {'error': '指定的环境不存在或无权访问'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        for test_case in test_cases:
            result = ApiTestService.execute_test_case(test_case, user, environment=environment)
            results.append(ApiTestResultSerializer(result).data)
        
        summary = {
            'total_cases': len(results),
            'passed': len([r for r in results if r['status'] == 'passed']),
            'failed': len([r for r in results if r['status'] == 'failed']),
            'errors': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
        
        return Response(summary)

    @action(detail=False, methods=['post'])
    def execute_test_plan(self, request):
        """执行测试计划"""
        test_plan_id = request.data.get('test_plan_id')
        run_name = request.data.get('run_name')
        
        if not test_plan_id:
            return Response(
                {'error': '请提供测试计划ID'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = request.user if request.user.is_authenticated else None
            
            # 获取环境参数
            environment = None
            environment_id = request.data.get('environment_id')
            if environment_id:
                try:
                    environment = Environment.objects.get(id=environment_id, created_by=user)
                except Environment.DoesNotExist:
                    return Response(
                        {'error': '指定的环境不存在或无权访问'}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            test_run = ApiTestService.execute_test_plan(test_plan_id, user, run_name, environment)
            
            from reports.serializers import TestRunDetailSerializer
            serializer = TestRunDetailSerializer(test_run)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': f'执行测试计划失败: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ApiTestResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ApiTestResult.objects.all().order_by('-executed_at')
    serializer_class = ApiTestResultSerializer
    permission_classes = []  # 统一权限配置：不限制访问

    def get_queryset(self):
        queryset = super().get_queryset()
        test_case_id = self.request.query_params.get('test_case_id')
        status_filter = self.request.query_params.get('status')
        
        if test_case_id:
            queryset = queryset.filter(test_case_id=test_case_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
            
        return queryset

@api_view(['GET'])
@permission_classes([])  # 统一权限配置：不限制访问
def api_test_debug_log(request):
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug.log')
    if not os.path.exists(log_path):
        return Response({'log': ''})
    
    # 尝试多种编码格式读取日志文件
    content = None
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16']
    
    for encoding in encodings:
        try:
            with open(log_path, encoding=encoding) as f:
                lines = f.readlines()
            content = lines
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            # 处理其他可能的文件读取错误
            continue
    
    if content is None:
        return Response({'log': '日志文件编码错误，无法读取。请检查日志文件格式。'})
    
    # 只返回包含api_test关键字的日志
    try:
        api_test_lines = [line for line in content if 'api_test' in line or 'API测试' in line or 'TestCase' in line]
        log_content = ''.join(api_test_lines)[-10000:]  # 最多返回最后10000字符
    except Exception as e:
        log_content = f'处理日志内容时出错: {str(e)}'
    
    return Response({'log': log_content})