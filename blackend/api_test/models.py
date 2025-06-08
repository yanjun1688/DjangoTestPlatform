from django.db import models
from django.contrib.auth.models import User
import json

class ApiDefinition(models.Model):
    """接口定义模型"""
    name = models.CharField(max_length=200, verbose_name='接口名称')
    url = models.CharField(max_length=500, verbose_name='接口URL')
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
    ]
    method = models.CharField(max_length=10, choices=METHOD_CHOICES, default='GET', verbose_name='请求方法')
    headers = models.TextField(default='{}', verbose_name='请求头', help_text='JSON格式')
    params = models.TextField(default='{}', verbose_name='URL参数', help_text='JSON格式')
    body = models.TextField(default='{}', verbose_name='请求体', help_text='JSON格式')
    description = models.TextField(blank=True, verbose_name='接口描述')
    module = models.CharField(max_length=100, blank=True, verbose_name='所属模块')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_definitions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.method} {self.name}"

    def get_headers(self):
        try:
            return json.loads(self.headers)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_params(self):
        try:
            return json.loads(self.params)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_body(self):
        try:
            return json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return {}

class ApiTestCase(models.Model):
    """接口测试用例模型"""
    name = models.CharField(max_length=200, verbose_name='用例名称')
    api = models.ForeignKey(ApiDefinition, on_delete=models.CASCADE, related_name='test_cases')
    headers = models.TextField(default='{}', verbose_name='请求头', help_text='JSON格式，会覆盖接口定义的请求头')
    params = models.TextField(default='{}', verbose_name='URL参数', help_text='JSON格式，会覆盖接口定义的参数')
    body = models.TextField(default='{}', verbose_name='请求体', help_text='JSON格式，会覆盖接口定义的请求体')
    assertions = models.TextField(default='[]', verbose_name='断言规则', help_text='JSON格式的断言规则列表')
    variables = models.TextField(default='{}', verbose_name='变量', help_text='JSON格式的变量定义')
    description = models.TextField(blank=True, verbose_name='用例描述')
    # 新增字段：预期状态码
    expected_status_code = models.IntegerField(default=200, verbose_name='预期状态码')
    # 新增字段：最大响应时间(毫秒)
    max_response_time = models.IntegerField(null=True, blank=True, verbose_name='最大响应时间(ms)')
    # 新增字段：是否启用
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_test_cases')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_headers(self):
        try:
            return json.loads(self.headers)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_params(self):
        try:
            return json.loads(self.params)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_body(self):
        try:
            return json.loads(self.body)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_assertions(self):
        try:
            return json.loads(self.assertions)
        except (json.JSONDecodeError, TypeError):
            return []

    def get_variables(self):
        try:
            return json.loads(self.variables)
        except (json.JSONDecodeError, TypeError):
            return {}

class ApiTestResult(models.Model):
    """接口测试结果模型"""
    test_case = models.ForeignKey(ApiTestCase, on_delete=models.CASCADE, related_name='results')
    STATUS_CHOICES = [
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='error')
    response_code = models.IntegerField(null=True, verbose_name='响应状态码')
    response_time = models.FloatField(null=True, verbose_name='响应时间(ms)')
    response_body = models.TextField(blank=True, verbose_name='响应内容')
    response_headers = models.TextField(default='{}', verbose_name='响应头', help_text='JSON格式')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    assertion_results = models.TextField(default='[]', verbose_name='断言结果详情', help_text='JSON格式')
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_test_results')
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.test_case.name} - {self.status}"

    def get_response_headers(self):
        try:
            return json.loads(self.response_headers)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_assertion_results(self):
        try:
            return json.loads(self.assertion_results)
        except (json.JSONDecodeError, TypeError):
            return []

class ApiTestSuite(models.Model):
    """接口测试套件模型"""
    name = models.CharField(max_length=200, verbose_name='套件名称')
    test_cases = models.ManyToManyField(ApiTestCase, related_name='suites')
    description = models.TextField(blank=True, verbose_name='套件描述')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='api_test_suites')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name