from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import re


class Comment(models.Model):
    """评论模型"""
    content = models.TextField(verbose_name='评论内容')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='评论作者'
    )
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # 支持评论回复
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='父评论'
    )
    
    # 通用外键关联 - 可以关联到TestCase、TestReport等任何模型
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # 是否已删除 (软删除)
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    
    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['content_type', 'object_id', '-timestamp']),
            models.Index(fields=['author', '-timestamp']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.author.username}: {content_preview}"
    
    @property
    def is_reply(self):
        """是否为回复"""
        return self.parent_comment is not None
    
    @property
    def reply_count(self):
        """回复数量"""
        return self.replies.filter(is_deleted=False).count()
    
    def get_mentioned_users(self):
        """提取评论中@提及的用户"""
        from user_management.models import User
        
        # 匹配@username格式，只匹配字母数字和下划线
        mentioned_usernames = re.findall(r'@([a-zA-Z0-9_]+)', self.content)
        if mentioned_usernames:
            return User.objects.filter(username__in=mentioned_usernames, is_active=True)
        return User.objects.none()
    
    def delete(self, using=None, keep_parents=False):
        """软删除"""
        self.is_deleted = True
        self.save()


class Notification(models.Model):
    """通知模型"""
    VERB_CHOICES = [
        ('mentioned', '提及了你'),
        ('replied', '回复了你的评论'),
        ('commented', '评论了'),
        ('test_completed', '测试完成'),
        ('test_failed', '测试失败'),
    ]
    
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='接收者'
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        verbose_name='触发用户'
    )
    verb = models.CharField(
        max_length=20,
        choices=VERB_CHOICES,
        verbose_name='动作类型'
    )
    
    # 通知目标对象 (可以是Comment、TestCase、TestReport等)
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='target_notifications'
    )
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_content_type', 'target_object_id')
    
    # 可选的关联对象 (比如具体的评论)
    action_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name='action_notifications',
        null=True,
        blank=True
    )
    action_object_id = models.PositiveIntegerField(null=True, blank=True)
    action_object = GenericForeignKey('action_content_type', 'action_object_id')
    
    description = models.CharField(max_length=255, blank=True, verbose_name='描述')
    read = models.BooleanField(default=False, verbose_name='是否已读')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['recipient', 'read', '-timestamp']),
            models.Index(fields=['recipient', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.actor.username} {self.get_verb_display()} -> {self.recipient.username}"
    
    def mark_as_read(self):
        """标记为已读"""
        if not self.read:
            self.read = True
            self.save(update_fields=['read'])
    
    @classmethod
    def create_notification(cls, recipient, actor, verb, target, action_object=None, description=''):
        """创建通知的便捷方法"""
        # 避免给自己发通知
        if recipient == actor:
            return None
            
        # 避免重复通知
        existing = cls.objects.filter(
            recipient=recipient,
            actor=actor,
            verb=verb,
            target_content_type=ContentType.objects.get_for_model(target),
            target_object_id=target.pk,
            read=False
        ).first()
        
        if existing:
            # 更新时间戳
            existing.timestamp = timezone.now()
            existing.save(update_fields=['timestamp'])
            return existing
        
        # 创建新通知
        notification_data = {
            'recipient': recipient,
            'actor': actor,
            'verb': verb,
            'target_content_type': ContentType.objects.get_for_model(target),
            'target_object_id': target.pk,
            'description': description,
        }
        
        if action_object:
            notification_data.update({
                'action_content_type': ContentType.objects.get_for_model(action_object),
                'action_object_id': action_object.pk,
            })
        
        return cls.objects.create(**notification_data)


class CommentMention(models.Model):
    """评论提及记录"""
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='mentions'
    )
    mentioned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_mentions'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['comment', 'mentioned_user']
        verbose_name = '评论提及'
        verbose_name_plural = '评论提及'
