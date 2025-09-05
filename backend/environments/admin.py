from django.contrib import admin
from .models import Environment, EnvironmentVariable, EnvironmentUsageLog


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_by', 'is_default', 'is_active', 'variables_count', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    search_fields = ['name', 'description', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def variables_count(self, obj):
        return obj.variables.count()
    variables_count.short_description = '变量数量'


@admin.register(EnvironmentVariable)
class EnvironmentVariableAdmin(admin.ModelAdmin):
    list_display = ['key', 'environment', 'is_secret', 'created_at']
    list_filter = ['is_secret', 'created_at', 'environment']
    search_fields = ['key', 'description', 'environment__name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('environment')


@admin.register(EnvironmentUsageLog)
class EnvironmentUsageLogAdmin(admin.ModelAdmin):
    list_display = ['environment', 'user', 'action', 'used_at']
    list_filter = ['action', 'used_at', 'environment']
    search_fields = ['environment__name', 'user__username']
    readonly_fields = ['used_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('environment', 'user')