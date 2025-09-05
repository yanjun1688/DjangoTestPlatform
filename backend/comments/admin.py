from django.contrib import admin
from .models import Comment, Notification, CommentMention


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'content_preview', 'content_object_display', 'timestamp', 'is_deleted']
    list_filter = ['is_deleted', 'timestamp', 'content_type']
    search_fields = ['content', 'author__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp', 'updated_at']
    raw_id_fields = ['author', 'parent_comment']
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = '内容预览'
    
    def content_object_display(self, obj):
        return f"{obj.content_type.name}: {obj.content_object}"
    content_object_display.short_description = '关联对象'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'actor', 'verb', 'target_display', 'read', 'timestamp']
    list_filter = ['read', 'verb', 'timestamp']
    search_fields = ['recipient__username', 'actor__username', 'description']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    raw_id_fields = ['recipient', 'actor']
    
    def target_display(self, obj):
        return f"{obj.target_content_type.name}: {obj.target}"
    target_display.short_description = '目标对象'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(read=True)
        self.message_user(request, f'已将 {updated} 条通知标记为已读')
    mark_as_read.short_description = '标记为已读'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(read=False)
        self.message_user(request, f'已将 {updated} 条通知标记为未读')
    mark_as_unread.short_description = '标记为未读'


@admin.register(CommentMention)
class CommentMentionAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'mentioned_user', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['mentioned_user__username', 'comment__content']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    raw_id_fields = ['comment', 'mentioned_user']
