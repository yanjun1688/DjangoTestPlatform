from rest_framework import serializers
from .models import MockAPI, MockAPIUsageLog
import json


class MockAPIListSerializer(serializers.ModelSerializer):
    """Mock API列表序列化器"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    full_url = serializers.CharField(read_only=True)
    
    class Meta:
        model = MockAPI
        fields = [
            'id', 'name', 'path', 'method', 'response_status_code',
            'is_active', 'delay_ms', 'description', 'full_url',
            'created_by_username', 'created_at', 'updated_at'
        ]


class MockAPIDetailSerializer(serializers.ModelSerializer):
    """Mock API详情序列化器"""
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    full_url = serializers.CharField(read_only=True)
    content_type = serializers.SerializerMethodField()
    response_body_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = MockAPI
        fields = [
            'id', 'name', 'path', 'method', 'response_status_code',
            'response_headers', 'response_body', 'response_body_preview',
            'description', 'is_active', 'delay_ms', 'full_url',
            'content_type', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def get_content_type(self, obj):
        return obj.get_content_type()
    
    def get_response_body_preview(self, obj):
        """获取响应体预览(限制长度)"""
        if not obj.response_body:
            return ''
        
        preview = obj.response_body[:200]
        if len(obj.response_body) > 200:
            preview += '...'
        return preview


class MockAPICreateSerializer(serializers.ModelSerializer):
    """Mock API创建序列化器"""
    
    class Meta:
        model = MockAPI
        fields = [
            'name', 'path', 'method', 'response_status_code',
            'response_headers', 'response_body', 'description',
            'is_active', 'delay_ms'
        ]
    
    def validate_path(self, value):
        """验证路径格式"""
        if not value.startswith('/'):
            value = '/' + value
        
        # 移除尾部斜杠(除非是根路径)
        if value != '/' and value.endswith('/'):
            value = value.rstrip('/')
        
        return value
    
    def validate_response_headers(self, value):
        """验证响应头格式"""
        if value:
            if isinstance(value, str):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    raise serializers.ValidationError('响应头必须是有效的JSON格式')
            
            if not isinstance(value, dict):
                raise serializers.ValidationError('响应头必须是JSON对象格式')
        
        return value or {}
    
    def validate_response_status_code(self, value):
        """验证状态码"""
        if not (100 <= value <= 599):
            raise serializers.ValidationError('HTTP状态码必须在100-599范围内')
        return value
    
    def validate_delay_ms(self, value):
        """验证延迟时间"""
        if value < 0:
            raise serializers.ValidationError('延迟时间不能为负数')
        if value > 30000:  # 最大30秒
            raise serializers.ValidationError('延迟时间不能超过30秒')
        return value
    
    def validate(self, attrs):
        """验证路径和方法的唯一性"""
        path = attrs.get('path')
        method = attrs.get('method')
        
        # 检查是否已存在相同路径和方法的Mock API
        queryset = MockAPI.objects.filter(path=path, method=method)
        
        # 如果是更新操作，排除当前对象
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f'路径 {path} 和方法 {method} 的组合已存在'
            )
        
        return attrs


class MockAPIUpdateSerializer(MockAPICreateSerializer):
    """Mock API更新序列化器"""
    
    class Meta(MockAPICreateSerializer.Meta):
        pass


class MockAPIUsageLogSerializer(serializers.ModelSerializer):
    """Mock API使用日志序列化器"""
    mock_api_name = serializers.CharField(source='mock_api.name', read_only=True)
    
    class Meta:
        model = MockAPIUsageLog
        fields = [
            'id', 'mock_api', 'mock_api_name', 'request_path', 
            'request_method', 'request_headers', 'request_body',
            'response_status_code', 'client_ip', 'user_agent', 'timestamp'
        ]


class MockAPIStatsSerializer(serializers.Serializer):
    """Mock API统计信息序列化器"""
    total_mocks = serializers.IntegerField()
    active_mocks = serializers.IntegerField()
    total_requests = serializers.IntegerField()
    requests_today = serializers.IntegerField()
    most_used_mock = serializers.DictField()
    method_distribution = serializers.DictField()
    status_code_distribution = serializers.DictField()