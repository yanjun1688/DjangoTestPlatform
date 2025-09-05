from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
import json

from comments.models import Comment, Notification, CommentMention
from testcases.models import TestCase as TestCaseModel
from api_test.models import TestRun

User = get_user_model()


class CommentAPITest(TestCase):
    """评论API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.testcase = TestCaseModel.objects.create(
            title='测试用例',
            description='测试描述'
        )
        self.client = Client()
    
    def test_comment_list_requires_auth(self):
        """测试评论列表需要认证"""
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, 403)  # Django REST framework 返回403而不是401
    
    def test_create_comment_api(self):
        """测试评论创建API"""
        self.client.force_login(self.user)
        
        data = {
            'content': '测试评论内容',
            'target_type': 'testcase',
            'target_id': self.testcase.id
        }
        
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # 验证评论是否创建
        comment = Comment.objects.get(content='测试评论内容')
        self.assertEqual(comment.author, self.user)
    
    def test_user_search_api(self):
        """测试用户搜索API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/users/search/?q=test')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)


class NotificationAPITest(TestCase):
    """通知API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
    
    def test_notification_summary(self):
        """测试通知摘要API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/notifications/summary/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('unread_count', data)
        self.assertIn('has_unread', data)
    
    def test_notification_list(self):
        """测试通知列表API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/notifications/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
    
    def test_mark_notifications_read(self):
        """测试标记通知已读API"""
        self.client.force_login(self.user)
        
        # 创建另一个用户作为actor
        actor_user = User.objects.create_user(
            username='actor',
            password='testpass123'
        )
        
        # 创建测试通知
        testcase = TestCaseModel.objects.create(title='测试')
        notification = Notification.create_notification(
            recipient=self.user,
            actor=actor_user,
            verb='mentioned',
            target=testcase
        )
        
        # 确保通知已创建
        self.assertIsNotNone(notification)
        
        response = self.client.post(
            '/api/comments/notifications/mark-read/',
            data=json.dumps({'notification_ids': [notification.id]}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 验证通知已标记为已读
        notification.refresh_from_db()
        self.assertTrue(notification.read)
    """评论API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.testcase = TestCaseModel.objects.create(
            title='测试用例',
            description='测试描述'
        )
        self.client = Client()
    
    def test_comment_list_requires_auth(self):
        """测试评论列表需要认证"""
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, 403)  # Django REST framework 返回403而不是401
    
    def test_create_comment_api(self):
        """测试评论创建API"""
        self.client.force_login(self.user)
        
        data = {
            'content': '测试评论内容',
            'target_type': 'testcase',
            'target_id': self.testcase.id
        }
        
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # 验证评论是否创建
        comment = Comment.objects.get(content='测试评论内容')
        self.assertEqual(comment.author, self.user)
    
    def test_user_search_api(self):
        """测试用户搜索API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/users/search/?q=test')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)


class NotificationAPITest(TestCase):
    """通知API测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
    
    def test_notification_summary(self):
        """测试通知摘要API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/notifications/summary/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('unread_count', data)
        self.assertIn('has_unread', data)
    
    def test_notification_list(self):
        """测试通知列表API"""
        self.client.force_login(self.user)
        
        response = self.client.get('/api/comments/notifications/')
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIn('results', data)
    
    def test_mark_notifications_read(self):
        """测试标记通知已读API"""
        self.client.force_login(self.user)
        
        # 创建另一个用户作为actor
        actor_user = User.objects.create_user(
            username='actor',
            password='testpass123'
        )
        
        # 创建测试通知
        testcase = TestCaseModel.objects.create(title='测试')
        notification = Notification.create_notification(
            recipient=self.user,
            actor=actor_user,
            verb='mentioned',
            target=testcase
        )
        
        # 确保通知已创建
        self.assertIsNotNone(notification)
        
        response = self.client.post(
            '/api/comments/notifications/mark-read/',
            data=json.dumps({'notification_ids': [notification.id]}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        
        # 验证通知已标记为已读
        notification.refresh_from_db()
        self.assertTrue(notification.read)
