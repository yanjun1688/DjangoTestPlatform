from rest_framework import serializers
from .models import Environment, EnvironmentVariable, EnvironmentUsageLog


class EnvironmentVariableSerializer(serializers.ModelSerializer):
    """环境变量序列化器"""
    masked_value = serializers.ReadOnlyField()

    class Meta:
        model = EnvironmentVariable
        fields = [
            'id', 'key', 'value', 'masked_value', 'description', 
            'is_secret', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        """根据请求上下文决定是否显示敏感信息"""
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # 如果是敏感信息且不是所有者，则隐藏真实值
        if instance.is_secret and request:
            if request.user != instance.environment.created_by:
                data['value'] = data['masked_value']
        
        return data


class EnvironmentSerializer(serializers.ModelSerializer):
    """环境序列化器"""
    variables = EnvironmentVariableSerializer(many=True, read_only=True)
    variables_count = serializers.IntegerField(source='variables.count', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Environment
        fields = [
            'id', 'name', 'description', 'is_active', 'is_default',
            'variables', 'variables_count', 'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by']

    def create(self, validated_data):
        """创建环境时设置创建者"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

    def validate(self, attrs):
        """验证环境数据"""
        request = self.context.get('request')
        
        # 如果设置为默认环境，检查用户是否已有默认环境
        if attrs.get('is_default', False) and request and request.user:
            existing_default = Environment.objects.filter(
                created_by=request.user,
                is_default=True
            )
            
            # 如果是更新操作，排除当前对象
            if self.instance:
                existing_default = existing_default.exclude(pk=self.instance.pk)
            
            if existing_default.exists():
                # 自动将其他默认环境设置为非默认
                existing_default.update(is_default=False)
        
        return attrs


class EnvironmentListSerializer(serializers.ModelSerializer):
    """环境列表序列化器（简化版）"""
    variables_count = serializers.IntegerField(source='variables.count', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Environment
        fields = [
            'id', 'name', 'description', 'is_active', 'is_default',
            'variables_count', 'created_by_username', 'created_at', 'updated_at'
        ]


class EnvironmentUsageLogSerializer(serializers.ModelSerializer):
    """环境使用日志序列化器"""
    environment_name = serializers.CharField(source='environment.name', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = EnvironmentUsageLog
        fields = [
            'id', 'environment', 'environment_name', 'user', 'user_username',
            'action', 'used_at', 'context'
        ]


class EnvironmentVariableCreateSerializer(serializers.ModelSerializer):
    """环境变量创建序列化器"""

    class Meta:
        model = EnvironmentVariable
        fields = ['key', 'value', 'description', 'is_secret']

    def validate_key(self, value):
        """验证变量名"""
        # 检查变量名格式
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', value):
            raise serializers.ValidationError(
                '变量名只能包含字母、数字和下划线，且不能以数字开头'
            )
        
        # 检查是否与环境中已有变量重名
        environment_id = self.context.get('environment_id')
        if environment_id:
            existing = EnvironmentVariable.objects.filter(
                environment_id=environment_id,
                key=value
            )
            
            # 如果是更新操作，排除当前对象
            if self.instance:
                existing = existing.exclude(pk=self.instance.pk)
            
            if existing.exists():
                raise serializers.ValidationError(f'变量名 "{value}" 在当前环境中已存在')
        
        return value