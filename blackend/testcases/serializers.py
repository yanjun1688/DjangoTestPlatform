from rest_framework import serializers
from .models import TestCase, TestPlan, TestDataFile

class TestCaseSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(queryset=TestCase.objects.all(), allow_null=True, required=False)
    data_file = serializers.SerializerMethodField()

    class Meta:
        model = TestCase
        fields = '__all__'

    def get_children(self, obj):
        return TestCaseSerializer(obj.get_children(), many=True).data

    def get_data_file(self, obj):
        """获取关联的数据文件信息"""
        try:
            data_file = obj.data_file
            return {
                'id': data_file.id,
                'name': data_file.name,
                'file_type': data_file.file_type,
                'file_size': data_file.get_file_size_display(),
                'data_count': data_file.get_data_count(),
                'created_at': data_file.created_at,
            }
        except TestDataFile.DoesNotExist:
            return None

class TestDataFileSerializer(serializers.ModelSerializer):
    file_size_display = serializers.ReadOnlyField(source='get_file_size_display')
    data_count = serializers.ReadOnlyField(source='get_data_count')

    class Meta:
        model = TestDataFile
        fields = [
            'id', 'name', 'test_case', 'file', 'file_type', 
            'description', 'file_size_display', 'data_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """验证数据文件"""
        instance = TestDataFile(**data)
        
        # 如果有文件，进行验证
        if 'file' in data and data['file']:
            instance.file = data['file']
            errors = instance.validate_file()
            if errors:
                raise serializers.ValidationError({'file': errors})
        
        return data

class TestDataFileUploadSerializer(serializers.ModelSerializer):
    """用于文件上传的序列化器"""
    class Meta:
        model = TestDataFile
        fields = ['name', 'file', 'file_type', 'description']

    def validate_file(self, value):
        """验证上传的文件"""
        if not value:
            raise serializers.ValidationError("请选择文件")
        
        # 检查文件大小（10MB限制）
        max_size = 10 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(f"文件大小不能超过10MB，当前大小: {value.size / (1024*1024):.1f}MB")
        
        return value

    def validate(self, data):
        """交叉验证文件类型和文件扩展名"""
        if 'file' in data and 'file_type' in data:
            import os
            file_extension = os.path.splitext(data['file'].name)[1].lower()
            file_type = data['file_type']
            
            if file_type == 'csv' and file_extension != '.csv':
                raise serializers.ValidationError("CSV文件必须以.csv为扩展名")
            elif file_type == 'json' and file_extension != '.json':
                raise serializers.ValidationError("JSON文件必须以.json为扩展名")
        
        return data

class TestPlanSerializer(serializers.ModelSerializer):
    test_cases = serializers.PrimaryKeyRelatedField(queryset=TestCase.objects.all(), many=True, required=False)

    class Meta:
        model = TestPlan
        fields = '__all__' 