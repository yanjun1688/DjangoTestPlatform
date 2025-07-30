from django.contrib import admin
from .models import ApiDefinition, ApiTestCase, ApiTestResult

@admin.register(ApiDefinition)
class ApiDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'method', 'url', 'module', 'created_by', 'created_at')
    list_filter = ('method', 'module', 'created_by')
    search_fields = ('name', 'url', 'description')

@admin.register(ApiTestCase)
class ApiTestCaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'api', 'created_by', 'created_at')
    list_filter = ('api', 'created_by')
    search_fields = ('name', 'description')

@admin.register(ApiTestResult)
class ApiTestResultAdmin(admin.ModelAdmin):
    list_display = ('test_case', 'status', 'response_code', 'response_time', 'executed_by', 'executed_at')
    list_filter = ('status', 'executed_by')
    search_fields = ('test_case__name', 'error_message') 