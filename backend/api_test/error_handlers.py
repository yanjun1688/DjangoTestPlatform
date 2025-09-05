"""
统一错误处理机制
提供分层的错误处理和用户友好的错误信息
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import ValidationError, PermissionDenied
import requests

logger = logging.getLogger(__name__)

class APIError:
    """API错误类型定义"""
    
    # 通用错误
    UNKNOWN_ERROR = ('UNKNOWN_ERROR', '未知错误')
    VALIDATION_ERROR = ('VALIDATION_ERROR', '数据验证失败')
    PERMISSION_DENIED = ('PERMISSION_DENIED', '权限不足')
    NOT_FOUND = ('NOT_FOUND', '资源未找到')
    
    # 网络错误
    CONNECTION_ERROR = ('CONNECTION_ERROR', '网络连接失败')
    TIMEOUT_ERROR = ('TIMEOUT_ERROR', '请求超时')
    HTTP_ERROR = ('HTTP_ERROR', 'HTTP请求错误')
    
    # 业务错误
    TEST_EXECUTION_ERROR = ('TEST_EXECUTION_ERROR', '测试执行失败')
    DATA_PARSING_ERROR = ('DATA_PARSING_ERROR', '数据解析失败')
    FILE_OPERATION_ERROR = ('FILE_OPERATION_ERROR', '文件操作失败')

def custom_exception_handler(exc, context):
    """自定义异常处理器"""
    response = exception_handler(exc, context)
    
    if response is not None:
        # DRF已处理的异常
        custom_response_data = {
            'error': True,
            'code': 'DRF_ERROR',
            'message': '请求处理失败',
            'details': response.data,
            'status_code': response.status_code
        }
        response.data = custom_response_data
        
    else:
        # 未被DRF处理的异常
        if isinstance(exc, Http404):
            custom_response_data = {
                'error': True,
                'code': APIError.NOT_FOUND[0],
                'message': APIError.NOT_FOUND[1],
                'details': str(exc),
                'status_code': 404
            }
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data = {
                'error': True,
                'code': APIError.PERMISSION_DENIED[0],
                'message': APIError.PERMISSION_DENIED[1],
                'details': str(exc),
                'status_code': 403
            }
            response = Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)
            
        elif isinstance(exc, ValidationError):
            custom_response_data = {
                'error': True,
                'code': APIError.VALIDATION_ERROR[0],
                'message': APIError.VALIDATION_ERROR[1],
                'details': exc.message_dict if hasattr(exc, 'message_dict') else str(exc),
                'status_code': 400
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            # 记录未处理的异常
            logger.exception('Unhandled exception occurred', exc_info=exc)
            custom_response_data = {
                'error': True,
                'code': APIError.UNKNOWN_ERROR[0],
                'message': APIError.UNKNOWN_ERROR[1],
                'details': str(exc) if hasattr(exc, '__str__') else '服务器内部错误',
                'status_code': 500
            }
            response = Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response

def handle_request_exception(exc, context_info=None):
    """
    处理requests库的异常
    
    Args:
        exc: requests异常对象
        context_info: 额外的上下文信息
        
    Returns:
        tuple: (error_code, error_message, details)
    """
    context = context_info or {}
    
    if isinstance(exc, requests.exceptions.ConnectionError):
        return (
            APIError.CONNECTION_ERROR[0],
            APIError.CONNECTION_ERROR[1],
            {
                'original_error': str(exc),
                'context': context,
                'suggestion': '请检查网络连接或目标服务是否可用'
            }
        )
    elif isinstance(exc, requests.exceptions.Timeout):
        return (
            APIError.TIMEOUT_ERROR[0],
            APIError.TIMEOUT_ERROR[1],
            {
                'original_error': str(exc),
                'context': context,
                'suggestion': '请求超时，建议稍后重试或检查网络状况'
            }
        )
    elif isinstance(exc, requests.exceptions.HTTPError):
        return (
            APIError.HTTP_ERROR[0],
            APIError.HTTP_ERROR[1],
            {
                'original_error': str(exc),
                'context': context,
                'status_code': getattr(exc.response, 'status_code', None),
                'response_text': getattr(exc.response, 'text', None)
            }
        )
    else:
        return (
            APIError.UNKNOWN_ERROR[0],
            f'网络请求异常: {APIError.UNKNOWN_ERROR[1]}',
            {
                'original_error': str(exc),
                'context': context,
                'error_type': type(exc).__name__
            }
        )

def create_error_result(test_case, error_code, error_message, details, user=None, test_run=None):
    """
    创建统一格式的错误结果
    
    Args:
        test_case: 测试用例对象
        error_code: 错误代码
        error_message: 错误消息
        details: 错误详情
        user: 执行用户
        test_run: 测试运行记录
        
    Returns:
        ApiTestResult对象
    """
    from api_test.models import ApiTestResult
    
    return ApiTestResult.objects.create(
        test_case=test_case,
        test_run=test_run,
        status='error',
        error_message=f'[{error_code}] {error_message}',
        response_body=str(details) if details else '',
        executed_by=user
    )

class TestExecutionError(Exception):
    """测试执行自定义异常"""
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code or APIError.TEST_EXECUTION_ERROR[0]
        self.details = details or {}
        super().__init__(self.message)

class DataParsingError(Exception):
    """数据解析自定义异常"""
    def __init__(self, message, error_code=None, details=None):
        self.message = message
        self.error_code = error_code or APIError.DATA_PARSING_ERROR[0]
        self.details = details or {}
        super().__init__(self.message)