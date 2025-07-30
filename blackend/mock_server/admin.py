from django.contrib import admin
from .models import MockAPI, MockAPIUsageLog


@admin.register(MockAPI)
class MockAPIAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'method', 'path', 'response_status_code', 
        'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['method', 'response_status_code', 'is_active', 'created_at']
    search_fields = ['name', 'path', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('请求配置', {
            'fields': ('path', 'method')
        }),
        ('响应配置', {
            'fields': ('response_status_code', 'response_headers', 'response_body', 'delay_ms')
        }),
        ('元数据', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新建时设置创建者
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(MockAPIUsageLog)
class MockAPIUsageLogAdmin(admin.ModelAdmin):
    list_display = [
        'mock_api', 'request_method', 'request_path', 
        'response_status_code', 'client_ip', 'timestamp'
    ]
    list_filter = ['request_method', 'response_status_code', 'timestamp']
    search_fields = ['request_path', 'client_ip']
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        # 禁止手动添加日志
        return False
    
    def has_change_permission(self, request, obj=None):
        # 禁止修改日志
        return False