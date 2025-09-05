from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import json


class Environment(models.Model):
    """测试环境模型"""
    name = models.CharField(max_length=100, verbose_name='环境名称')
    description = models.TextField(blank=True, verbose_name='环境描述')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    is_default = models.BooleanField(default=False, verbose_name='是否为默认环境')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='environments',
        verbose_name='创建者'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '测试环境'
        verbose_name_plural = '测试环境'
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['created_by'],
                condition=models.Q(is_default=True),
                name='unique_default_environment_per_user'
            )
        ]

    def __str__(self):
        return f"{self.name} ({'默认' if self.is_default else ''})"

    def clean(self):
        """验证数据有效性"""
        super().clean()
        # 注意：这里的验证在序列化器级别已经处理，模型级别不需要再次验证
        # 因为序列化器会自动处理默认环境的更新逻辑

    def save(self, *args, **kwargs):
        # 如果设置为默认环境，自动将其他默认环境设为非默认
        if self.is_default:
            Environment.objects.filter(
                created_by=self.created_by,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)


class EnvironmentVariable(models.Model):
    """环境变量模型"""
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='variables',
        verbose_name='所属环境'
    )
    key = models.CharField(max_length=100, verbose_name='变量名')
    value = models.TextField(verbose_name='变量值')
    description = models.CharField(max_length=255, blank=True, verbose_name='变量描述')
    is_secret = models.BooleanField(default=False, verbose_name='是否为敏感信息')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '环境变量'
        verbose_name_plural = '环境变量'
        ordering = ['key']
        constraints = [
            models.UniqueConstraint(
                fields=['environment', 'key'],
                name='unique_variable_per_environment'
            )
        ]

    def __str__(self):
        return f"{self.environment.name}.{self.key}"

    @property
    def masked_value(self):
        """获取脱敏后的值"""
        if self.is_secret and self.value:
            return '*' * min(len(self.value), 8)
        return self.value


class EnvironmentUsageLog(models.Model):
    """环境使用日志"""
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        related_name='usage_logs',
        verbose_name='使用的环境'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='environment_usage_logs',
        verbose_name='使用者'
    )
    action = models.CharField(
        max_length=50,
        choices=[
            ('api_test', 'API测试'),
            ('test_plan', '测试计划执行'),
            ('manual_test', '手动测试'),
        ],
        verbose_name='使用场景'
    )
    used_at = models.DateTimeField(auto_now_add=True, verbose_name='使用时间')
    context = models.JSONField(default=dict, verbose_name='使用上下文')

    class Meta:
        verbose_name = '环境使用日志'
        verbose_name_plural = '环境使用日志'
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user.username} 使用 {self.environment.name} 进行 {self.get_action_display()}"