from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Comment, Notification, CommentMention
from .serializers import (
    CommentSerializer, NotificationSerializer, 
    CommentCreateSerializer, UserSearchSerializer
)

User = get_user_model()


class CommentPagination(PageNumberPagination):
    """评论分页器"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CommentListCreateView(generics.ListCreateAPIView):
    """评论列表和创建视图"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentPagination
    
    def get_queryset(self):
        """获取评论查询集"""
        target_type = self.request.query_params.get('target_type')
        target_id = self.request.query_params.get('target_id')
        
        if not target_type or not target_id:
            return Comment.objects.none()
        
        try:
            # 根据target_type获取ContentType
            if target_type == 'testcase':
                from testcases.models import TestCase
                content_type = ContentType.objects.get_for_model(TestCase)
            elif target_type == 'testreport':
                from api_test.models import TestRun
                content_type = ContentType.objects.get_for_model(TestRun)
            else:
                return Comment.objects.none()
            
            # 只返回顶级评论（非回复）
            return Comment.objects.filter(
                content_type=content_type,
                object_id=target_id,
                parent_comment__isnull=True,
                is_deleted=False
            ).select_related('author').prefetch_related('replies__author')
            
        except Exception:
            return Comment.objects.none()


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """评论详情视图"""
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Comment.objects.filter(is_deleted=False)
    
    def perform_destroy(self, instance):
        """软删除评论"""
        # 只有作者或管理员可以删除
        if instance.author == self.request.user or self.request.user.is_staff:
            instance.delete()  # 调用模型的软删除方法
        else:
            return Response(
                {"error": "只有评论作者或管理员可以删除评论"},
                status=status.HTTP_403_FORBIDDEN
            )
    
    def perform_update(self, serializer):
        """更新评论"""
        # 只有作者可以编辑
        if serializer.instance.author != self.request.user:
            return Response(
                {"error": "只有评论作者可以编辑评论"},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_comment(request):
    """创建评论的简化API"""
    serializer = CommentCreateSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data
        
        try:
            # 获取目标对象
            target_type = data['target_type']
            target_id = data['target_id']
            
            if target_type == 'testcase':
                from testcases.models import TestCase
                target_object = get_object_or_404(TestCase, id=target_id)
                content_type = ContentType.objects.get_for_model(TestCase)
            elif target_type == 'testreport':
                from api_test.models import TestRun
                target_object = get_object_or_404(TestRun, id=target_id)
                content_type = ContentType.objects.get_for_model(TestRun)
            else:
                return Response(
                    {"error": "不支持的目标类型"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 创建评论
            comment_data = {
                'content': data['content'],
                'author': request.user,
                'content_type': content_type,
                'object_id': target_id,
            }
            
            # 处理父评论
            if 'parent_comment_id' in data:
                parent_comment = get_object_or_404(
                    Comment, 
                    id=data['parent_comment_id'],
                    is_deleted=False
                )
                comment_data['parent_comment'] = parent_comment
            
            comment = Comment.objects.create(**comment_data)
            
            # 处理@提及通知
            mentioned_users = comment.get_mentioned_users()
            for user in mentioned_users:
                CommentMention.objects.get_or_create(
                    comment=comment,
                    mentioned_user=user
                )
                
                Notification.create_notification(
                    recipient=user,
                    actor=request.user,
                    verb='mentioned',
                    target=target_object,
                    action_object=comment,
                    description=f"在评论中提及了你"
                )
            
            # 处理回复通知
            if comment.parent_comment:
                parent_author = comment.parent_comment.author
                if parent_author != request.user:
                    Notification.create_notification(
                        recipient=parent_author,
                        actor=request.user,
                        verb='replied',
                        target=target_object,
                        action_object=comment,
                        description=f"回复了你的评论"
                    )
            
            # 返回创建的评论
            serializer = CommentSerializer(comment, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NotificationListView(generics.ListAPIView):
    """通知列表视图"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentPagination
    
    def get_queryset(self):
        """获取当前用户的通知"""
        queryset = Notification.objects.filter(
            recipient=self.request.user
        ).select_related('actor', 'target_content_type', 'action_content_type')
        
        # 过滤已读/未读
        read_filter = self.request.query_params.get('read')
        if read_filter is not None:
            queryset = queryset.filter(read=read_filter.lower() == 'true')
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_as_read(request):
    """标记通知为已读"""
    notification_ids = request.data.get('notification_ids', [])
    
    if notification_ids:
        # 标记指定通知为已读
        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            recipient=request.user
        ).update(read=True)
    else:
        # 标记所有通知为已读
        updated_count = Notification.objects.filter(
            recipient=request.user,
            read=False
        ).update(read=True)
    
    return Response({
        "message": f"已标记 {updated_count} 条通知为已读",
        "updated_count": updated_count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_summary(request):
    """获取通知摘要"""
    user = request.user
    unread_count = Notification.objects.filter(
        recipient=user,
        read=False
    ).count()
    
    return Response({
        "unread_count": unread_count,
        "has_unread": unread_count > 0
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users(request):
    """搜索用户（用于@提及功能）"""
    query = request.query_params.get('q', '').strip()
    
    if len(query) < 2:
        return Response([])
    
    # 搜索用户名、姓名
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query),
        is_active=True
    ).exclude(id=request.user.id)[:10]  # 最多返回10个结果
    
    serializer = UserSearchSerializer(users, many=True)
    return Response(serializer.data)
