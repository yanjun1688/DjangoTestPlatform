from django.db import models
from django.conf import settings
from django.utils import timezone
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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='api_definitions')
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
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='api_test_cases')
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

class TestRun(models.Model):
    """测试执行记录模型"""
    test_plan = models.ForeignKey(
        'testcases.TestPlan', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='test_runs',
        verbose_name='测试计划'
    )
    name = models.CharField(max_length=200, verbose_name='执行名称', help_text='如：回归测试 2025-01-10')
    STATUS_CHOICES = [
        ('running', '运行中'),
        ('completed', '已完成'),
        ('failed', '执行失败'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='running', verbose_name='执行状态')
    total_tests = models.IntegerField(default=0, verbose_name='总用例数')
    passed_tests = models.IntegerField(default=0, verbose_name='通过用例数') 
    failed_tests = models.IntegerField(default=0, verbose_name='失败用例数')
    error_tests = models.IntegerField(default=0, verbose_name='错误用例数')
    start_time = models.DateTimeField(default=timezone.now, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='test_runs',
        verbose_name='执行者'
    )
    description = models.TextField(blank=True, verbose_name='执行描述')
    error_message = models.TextField(blank=True, verbose_name='错误信息')
    
    class Meta:
        verbose_name = '测试执行记录'
        verbose_name_plural = '测试执行记录'
        ordering = ['-start_time']
    
    def __str__(self):
        if self.test_plan:
            return f"{self.name} - {self.test_plan.name}"
        return f"{self.name} - 无测试计划"
    
    @property
    def duration(self):
        """执行时长"""
        if self.end_time and self.start_time:
            return self.end_time - self.start_time
        elif self.start_time:
            # 如果还在运行中，返回到现在的时长
            return timezone.now() - self.start_time
        return None
    
    @property
    def duration_display(self):
        """友好的时长显示"""
        duration = self.duration
        if duration is None:
            return "未知"
        
        duration_seconds = duration.total_seconds()
        if duration_seconds < 60:
            return f"{duration_seconds:.1f}秒"
        elif duration_seconds < 3600:
            return f"{duration_seconds/60:.1f}分钟"
        else:
            return f"{duration_seconds/3600:.1f}小时"
    
    @property
    def success_rate(self):
        """成功率"""
        if self.total_tests == 0:
            return 0
        return (self.passed_tests / self.total_tests) * 100
    
    @property
    def avg_response_time(self):
        """平均响应时间"""
        results = self.results.filter(response_time__isnull=False)
        if not results.exists():
            return 0
        response_times = [result.response_time for result in results]
        return sum(response_times) / len(response_times)
    
    @property
    def is_running(self):
        """是否正在运行"""
        return self.status == 'running'
    
    def update_statistics(self):
        """更新统计信息"""
        results = self.results.all()
        self.total_tests = results.count()
        self.passed_tests = results.filter(status='passed').count()
        self.failed_tests = results.filter(status='failed').count()
        self.error_tests = results.filter(status='error').count()
        self.save()
    
    def complete(self):
        """标记执行完成"""
        self.status = 'completed'
        self.end_time = timezone.now()
        self.update_statistics()
        self.save()
    
    def mark_failed(self, error_message=None):
        """标记执行失败"""
        self.status = 'failed'
        self.end_time = timezone.now()
        if error_message:
            self.error_message = error_message
            self.description = f"{self.description}\n执行失败: {error_message}".strip()
        self.update_statistics()
        self.save()

class ApiTestResult(models.Model):
    """接口测试结果模型"""
    test_case = models.ForeignKey(ApiTestCase, on_delete=models.CASCADE, related_name='results')
    test_run = models.ForeignKey(
        TestRun, 
        on_delete=models.CASCADE, 
        related_name='results', 
        null=True, 
        blank=True,
        verbose_name='测试执行记录'
    )
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
    executed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='api_test_results')
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