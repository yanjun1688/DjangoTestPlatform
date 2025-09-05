# Generated migration for mock_server app

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MockAPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Mock名称')),
                ('path', models.CharField(help_text='例如: /api/user/profile 或 /user/profile/1', max_length=500, verbose_name='URL路径')),
                ('method', models.CharField(choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'), ('PATCH', 'PATCH'), ('HEAD', 'HEAD'), ('OPTIONS', 'OPTIONS')], default='GET', max_length=10, verbose_name='HTTP方法')),
                ('response_status_code', models.IntegerField(default=200, verbose_name='响应状态码')),
                ('response_headers', models.JSONField(blank=True, default=dict, help_text='JSON格式的响应头信息', verbose_name='响应头')),
                ('response_body', models.TextField(blank=True, help_text='返回的响应内容，可以是JSON、XML或纯文本', verbose_name='响应体')),
                ('description', models.TextField(blank=True, help_text='Mock API的用途说明', verbose_name='描述')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('delay_ms', models.IntegerField(default=0, help_text='模拟网络延迟，0表示无延迟', verbose_name='响应延迟(毫秒)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name': 'Mock API',
                'verbose_name_plural': 'Mock APIs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MockAPIUsageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_path', models.CharField(max_length=500, verbose_name='请求路径')),
                ('request_method', models.CharField(max_length=10, verbose_name='请求方法')),
                ('request_headers', models.JSONField(blank=True, default=dict, verbose_name='请求头')),
                ('request_body', models.TextField(blank=True, verbose_name='请求体')),
                ('response_status_code', models.IntegerField(verbose_name='响应状态码')),
                ('client_ip', models.GenericIPAddressField(verbose_name='客户端IP')),
                ('user_agent', models.TextField(blank=True, verbose_name='User-Agent')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='请求时间')),
                ('mock_api', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usage_logs', to='mock_server.mockapi', verbose_name='Mock API')),
            ],
            options={
                'verbose_name': 'Mock API使用日志',
                'verbose_name_plural': 'Mock API使用日志',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.AddConstraint(
            model_name='mockapi',
            constraint=models.UniqueConstraint(fields=('path', 'method'), name='unique_mock_path_method'),
        ),
    ]