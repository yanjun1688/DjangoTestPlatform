from rest_framework import serializers
from api_test.models import TestRun, ApiTestResult
from testcases.serializers import TestPlanSerializer


class TestRunListSerializer(serializers.ModelSerializer):
    """测试执行记录列表序列化器"""
    duration_display = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    test_plan_name = serializers.CharField(source='test_plan.name', read_only=True)
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)
    
    class Meta:
        model = TestRun
        fields = [
            'id', 'name', 'status', 'test_plan', 'test_plan_name',
            'total_tests', 'passed_tests', 'failed_tests', 'error_tests',
            'success_rate', 'start_time', 'end_time', 'duration_display',
            'executed_by', 'executed_by_username', 'description'
        ]


class ApiTestResultDetailSerializer(serializers.ModelSerializer):
    """API测试结果详情序列化器"""
    test_case_name = serializers.CharField(source='test_case.name', read_only=True)
    api_method = serializers.CharField(source='test_case.api.method', read_only=True)
    api_url = serializers.CharField(source='test_case.api.url', read_only=True)
    api_name = serializers.CharField(source='test_case.api.name', read_only=True)
    response_headers_dict = serializers.JSONField(source='get_response_headers', read_only=True)
    assertion_results_list = serializers.JSONField(source='get_assertion_results', read_only=True)
    
    class Meta:
        model = ApiTestResult
        fields = [
            'id', 'test_case', 'test_case_name', 'api_method', 'api_url', 'api_name',
            'status', 'response_code', 'response_time', 'response_body', 
            'response_headers_dict', 'error_message', 'assertion_results_list',
            'executed_at'
        ]


class TestRunDetailSerializer(serializers.ModelSerializer):
    """测试执行记录详情序列化器"""
    duration_display = serializers.ReadOnlyField()
    success_rate = serializers.ReadOnlyField()
    is_running = serializers.ReadOnlyField()
    test_plan_detail = TestPlanSerializer(source='test_plan', read_only=True)
    executed_by_username = serializers.CharField(source='executed_by.username', read_only=True)
    results = ApiTestResultDetailSerializer(many=True, read_only=True)
    
    # 统计数据
    avg_response_time = serializers.SerializerMethodField()
    response_time_distribution = serializers.SerializerMethodField()
    status_distribution = serializers.SerializerMethodField()
    
    class Meta:
        model = TestRun
        fields = [
            'id', 'name', 'status', 'test_plan', 'test_plan_detail',
            'total_tests', 'passed_tests', 'failed_tests', 'error_tests',
            'success_rate', 'start_time', 'end_time', 'duration_display',
            'is_running', 'executed_by', 'executed_by_username', 'description',
            'results', 'avg_response_time', 'response_time_distribution',
            'status_distribution'
        ]
    
    def get_avg_response_time(self, obj):
        """计算平均响应时间"""
        results = obj.results.filter(response_time__isnull=False)
        if results.exists():
            total_time = sum(result.response_time for result in results)
            return round(total_time / results.count(), 2)
        return 0
    
    def get_response_time_distribution(self, obj):
        """响应时间分布统计"""
        results = obj.results.filter(response_time__isnull=False)
        distribution = {
            '0-100ms': 0,
            '100-500ms': 0,
            '500-1000ms': 0,
            '1000-3000ms': 0,
            '3000ms+': 0
        }
        
        for result in results:
            time = result.response_time
            if time <= 100:
                distribution['0-100ms'] += 1
            elif time <= 500:
                distribution['100-500ms'] += 1
            elif time <= 1000:
                distribution['500-1000ms'] += 1
            elif time <= 3000:
                distribution['1000-3000ms'] += 1
            else:
                distribution['3000ms+'] += 1
        
        return distribution
    
    def get_status_distribution(self, obj):
        """状态分布统计"""
        return {
            'passed': obj.passed_tests,
            'failed': obj.failed_tests,
            'error': obj.error_tests
        }


class TestRunCreateSerializer(serializers.ModelSerializer):
    """测试执行记录创建序列化器"""
    
    class Meta:
        model = TestRun
        fields = [
            'name', 'test_plan', 'description'
        ]
    
    def create(self, validated_data):
        # 设置执行者为当前用户
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['executed_by'] = request.user
        return super().create(validated_data)