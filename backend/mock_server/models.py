from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import json



class MockAPI(models.Model):
    """Mock API模型，用于存储Mock接口的配置信息"""
    
    HTTP_METHODS = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
        ('PATCH', 'PATCH'),
        ('HEAD', 'HEAD'),
        ('OPTIONS', 'OPTIONS'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Mock名称')
    path = models.CharField(
        max_length=500, 
        verbose_name='URL路径',
        help_text="例如: /api/user/profile 或 /user/profile/1"
    )
    method = models.CharField(
        max_length=10, 
        choices=HTTP_METHODS, 
        default='GET',
        verbose_name='HTTP方法'
    )
    response_status_code = models.IntegerField(
        default=200,
        verbose_name='响应状态码'
    )
    response_headers = models.JSONField(
        default=dict, 
        blank=True,
        verbose_name='响应头',
        help_text='JSON格式的响应头信息'
    )
    response_body = models.TextField(
        blank=True,
        verbose_name='响应体',
        help_text='返回的响应内容，可以是JSON、XML或纯文本'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述',
        help_text='Mock API的用途说明'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    delay_ms = models.IntegerField(
        default=0,
        verbose_name='响应延迟(毫秒)',
        help_text='模拟网络延迟，0表示无延迟'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        unique_together = ('path', 'method')
        verbose_name = 'Mock API'
        verbose_name_plural = 'Mock APIs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.method} {self.path} - {self.name}"
    
    def clean(self):
        """验证数据有效性"""
        super().clean()
        
        # 验证路径格式
        if not self.path.startswith('/'):
            raise ValidationError({'path': 'URL路径必须以/开头'})
        
        # 验证状态码
        if not (100 <= self.response_status_code <= 599):
            raise ValidationError({'response_status_code': 'HTTP状态码必须在100-599范围内'})
        
        # 验证响应头是否为有效JSON
        if self.response_headers:
            try:
                if isinstance(self.response_headers, str):
                    json.loads(self.response_headers)
            except (json.JSONDecodeError, TypeError):
                raise ValidationError({'response_headers': '响应头必须是有效的JSON格式'})
        
        # 验证延迟时间
        if self.delay_ms < 0:
            raise ValidationError({'delay_ms': '延迟时间不能为负数'})
    
    def save(self, *args, **kwargs):
        """保存前进行数据清理"""
        # 先进行路径标准化
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        if self.path != '/' and self.path.endswith('/'):
            self.path = self.path.rstrip('/')
        
        # 确保方法为大写
        self.method = self.method.upper()
        
        # 然后进行验证
        self.full_clean()
        
        super().save(*args, **kwargs)
    
    @property
    def full_url(self):
        """获取完整的Mock URL"""
        return f"/mock{self.path}"
    
    def get_response_body_json(self):
        """尝试将响应体解析为JSON"""
        try:
            return json.loads(self.response_body) if self.response_body else {}
        except json.JSONDecodeError:
            return self.response_body
    
    def get_content_type(self):
        """根据响应体内容推断Content-Type"""
        if not self.response_body:
            return 'text/plain'
        
        # 检查自定义响应头中是否指定了Content-Type
        if self.response_headers and 'Content-Type' in self.response_headers:
            return self.response_headers['Content-Type']
        
        # 尝试解析JSON
        try:
            json.loads(self.response_body)
            return 'application/json'
        except json.JSONDecodeError:
            # 检查是否为XML
            if self.response_body.strip().startswith('<'):
                return 'application/xml'
            return 'text/plain'


class MockAPIUsageLog(models.Model):
    """Mock API使用日志"""
    
    mock_api = models.ForeignKey(
        MockAPI,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        verbose_name='Mock API'
    )
    request_path = models.CharField(
        max_length=500,
        verbose_name='请求路径'
    )
    request_method = models.CharField(
        max_length=10,
        verbose_name='请求方法'
    )
    request_headers = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='请求头'
    )
    request_body = models.TextField(
        blank=True,
        verbose_name='请求体'
    )
    response_status_code = models.IntegerField(
        verbose_name='响应状态码'
    )
    client_ip = models.GenericIPAddressField(
        verbose_name='客户端IP'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User-Agent'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='请求时间'
    )
    
    class Meta:
        verbose_name = 'Mock API使用日志'
        verbose_name_plural = 'Mock API使用日志'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.request_method} {self.request_path} - {self.timestamp}"