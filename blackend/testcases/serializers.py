from rest_framework import serializers
from .models import TestCase, TestPlan

class TestCaseSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(queryset=TestCase.objects.all(), allow_null=True, required=False)

    class Meta:
        model = TestCase
        fields = '__all__'

    def get_children(self, obj):
        return TestCaseSerializer(obj.get_children(), many=True).data

class TestPlanSerializer(serializers.ModelSerializer):
    test_cases = serializers.PrimaryKeyRelatedField(queryset=TestCase.objects.all(), many=True, required=False)

    class Meta:
        model = TestPlan
        fields = '__all__' 