from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Comment, Notification, CommentMention

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()
    mentioned_users = UserSerializer(source='get_mentioned_users', many=True, read_only=True)
    
    # 用于创建评论时指定关联对象
    target_type = serializers.CharField(write_only=True, required=False)
    target_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'content', 'author', 'timestamp', 'updated_at',
            'parent_comment', 'replies', 'reply_count', 'is_reply',
            'mentioned_users', 'target_type', 'target_id', 'is_deleted'
        ]
        read_only_fields = ['timestamp', 'updated_at', 'author', 'is_deleted']
    
    def get_replies(self, obj):
        """获取回复列表"""
        if obj.is_reply:
            return []  # 回复不再显示子回复，避免层级过深
        
        replies = obj.replies.filter(is_deleted=False).order_by('timestamp')
        return CommentSerializer(replies, many=True, context=self.context).data
    
    def create(self, validated_data):
        """创建评论"""
        request = self.context['request']
        validated_data['author'] = request.user
        
        # 处理target_type和target_id
        target_type = validated_data.pop('target_type', None)
        target_id = validated_data.pop('target_id', None)
        
        if target_type and target_id:
            try:
                # 根据target_type获取ContentType
                if target_type == 'testcase':
                    from testcases.models import TestCase
                    content_type = ContentType.objects.get_for_model(TestCase)
                    target_object = TestCase.objects.get(id=target_id)
                elif target_type == 'testreport':
                    from api_test.models import TestRun
                    content_type = ContentType.objects.get_for_model(TestRun)
                    target_object = TestRun.objects.get(id=target_id)
                else:
                    raise serializers.ValidationError(f"不支持的目标类型: {target_type}")
                
                validated_data['content_type'] = content_type
                validated_data['object_id'] = target_id
                
            except Exception as e:
                raise serializers.ValidationError(f"无效的目标对象: {e}")
        
        comment = super().create(validated_data)
        
        # 处理@提及通知
        self._create_mention_notifications(comment)
        
        # 处理回复通知
        if comment.parent_comment:
            self._create_reply_notification(comment)
        
        return comment
    
    def _create_mention_notifications(self, comment):
        """创建@提及通知"""
        mentioned_users = comment.get_mentioned_users()
        for user in mentioned_users:
            # 创建提及记录
            CommentMention.objects.get_or_create(
                comment=comment,
                mentioned_user=user
            )
            
            # 创建通知
            Notification.create_notification(
                recipient=user,
                actor=comment.author,
                verb='mentioned',
                target=comment.content_object,
                action_object=comment,
                description=f"在评论中提及了你"
            )
    
    def _create_reply_notification(self, comment):
        """创建回复通知"""
        parent_author = comment.parent_comment.author
        if parent_author != comment.author:  # 不给自己发通知
            Notification.create_notification(
                recipient=parent_author,
                actor=comment.author,
                verb='replied',
                target=comment.content_object,
                action_object=comment,
                description=f"回复了你的评论"
            )


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    actor = UserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_name = serializers.SerializerMethodField()
    target_url = serializers.SerializerMethodField()
    action_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'actor', 'verb', 'description', 'read', 'timestamp',
            'target_type', 'target_name', 'target_url', 'action_content'
        ]
        read_only_fields = ['timestamp']
    
    def get_target_type(self, obj):
        """获取目标类型"""
        return obj.target_content_type.model
    
    def get_target_name(self, obj):
        """获取目标对象名称"""
        try:
            return str(obj.target)
        except:
            return "已删除的对象"
    
    def get_target_url(self, obj):
        """获取目标对象URL"""
        try:
            target_type = obj.target_content_type.model
            if target_type == 'testcase':
                return f"/test-cases?highlight={obj.target_object_id}"
            elif target_type == 'testrun':
                return f"/reports/{obj.target_object_id}"
            elif target_type == 'comment' and obj.action_object:
                # 如果是评论相关的通知，跳转到评论所在的页面
                comment = obj.action_object
                comment_target_type = comment.content_type.model
                if comment_target_type == 'testcase':
                    return f"/test-cases?highlight={comment.object_id}&comment={comment.id}"
                elif comment_target_type == 'testrun':
                    return f"/reports/{comment.object_id}?comment={comment.id}"
            return ""
        except:
            return ""
    
    def get_action_content(self, obj):
        """获取操作相关内容"""
        try:
            if obj.action_object and hasattr(obj.action_object, 'content'):
                content = obj.action_object.content
                return content[:100] + '...' if len(content) > 100 else content
            return ""
        except:
            return ""


class CommentCreateSerializer(serializers.Serializer):
    """简化的评论创建序列化器"""
    content = serializers.CharField(max_length=10000)
    target_type = serializers.ChoiceField(choices=['testcase', 'testreport'])
    target_id = serializers.IntegerField()
    parent_comment_id = serializers.IntegerField(required=False)


class UserSearchSerializer(serializers.ModelSerializer):
    """用户搜索序列化器"""
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'display_name']
    
    def get_display_name(self, obj):
        """获取显示名称"""
        if obj.first_name:
            return f"{obj.first_name} ({obj.username})"
        return obj.username