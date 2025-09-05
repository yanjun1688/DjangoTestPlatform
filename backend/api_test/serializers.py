from rest_framework import serializers
from .models import ApiDefinition, ApiTestCase, ApiTestResult

class ApiDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiDefinition
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class ApiTestCaseSerializer(serializers.ModelSerializer):
    api_name = serializers.CharField(source='api.name', read_only=True)
    api_url = serializers.CharField(source='api.url', read_only=True)
    api_method = serializers.CharField(source='api.method', read_only=True)

    class Meta:
        model = ApiTestCase
        fields = '__all__'
        read_only_fields = ('created_by', 'created_at', 'updated_at')

class ApiTestResultSerializer(serializers.ModelSerializer):
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)

    class Meta:
        model = ApiTestResult
        fields = '__all__'
        read_only_fields = ('executed_by', 'executed_at') 