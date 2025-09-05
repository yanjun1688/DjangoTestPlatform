from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
import json

from comments.models import Comment, Notification, CommentMention
from testcases.models import TestCase as TestCaseModel
from api_test.models import TestRun

User = get_user_model()


class CommentModelTest(TestCase):
    """评论模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.testcase = TestCaseModel.objects.create(
            title='测试用例',
            description='测试描述'
        )
    
    def test_comment_creation(self):
        """测试评论创建"""
        content_type = ContentType.objects.get_for_model(TestCaseModel)
        comment = Comment.objects.create(
            content='测试评论',
            author=self.user,
            content_type=content_type,
            object_id=self.testcase.id
        )
        
        self.assertEqual(comment.content, '测试评论')
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content_object, self.testcase)
        self.assertFalse(comment.is_deleted)
    
    def test_mention_extraction(self):
        """测试@提及提取"""
        content_type = ContentType.objects.get_for_model(TestCaseModel)
        
        # 创建被提及的用户
        mentioned_user = User.objects.create_user(
            username='mentioned',
            password='testpass123'
        )
        # 确保用户是活跃的
        mentioned_user.is_active = True
        mentioned_user.save()
        
        comment = Comment.objects.create(
            content='测试@mentioned用户提及',
            author=self.user,
            content_type=content_type,
            object_id=self.testcase.id
        )
        
        mentioned_users = comment.get_mentioned_users()
        self.assertIn(mentioned_user, mentioned_users)


class NotificationModelTest(TestCase):
    """通知模型测试"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        self.testcase = TestCaseModel.objects.create(
            title='测试用例',
            description='测试描述'
        )
    
    def test_notification_creation(self):
        """测试通知创建"""
        notification = Notification.create_notification(
            recipient=self.user2,
            actor=self.user1,
            verb='mentioned',
            target=self.testcase,
            description='测试通知'
        )
        
        self.assertEqual(notification.recipient, self.user2)
        self.assertEqual(notification.actor, self.user1)
        self.assertEqual(notification.verb, 'mentioned')
        self.assertFalse(notification.read)
    
    def test_duplicate_notification_prevention(self):
        """测试重复通知防止"""
        # 创建第一个通知
        notification1 = Notification.create_notification(
            recipient=self.user2,
            actor=self.user1,
            verb='mentioned',
            target=self.testcase
        )
        
        # 尝试创建重复通知
        notification2 = Notification.create_notification(
            recipient=self.user2,
            actor=self.user1,
            verb='mentioned',
            target=self.testcase
        )
        
        # 应该返回相同的通知对象
        self.assertEqual(notification1.id, notification2.id)