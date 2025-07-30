import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
django.setup()

from comments.models import Comment, Notification, CommentMention
from testcases.models import TestCase as TestCaseModel
from api_test.models import TestRun

User = get_user_model()


class CommentsAPITestCase(TestCase):
    """评论系统API测试"""
    
    def setUp(self):
        """测试数据准备"""
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username='user1',
            password='testpass123',
            first_name='用户1'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            password='testpass123',
            first_name='用户2'
        )
        
        # 创建测试用例
        self.testcase = TestCaseModel.objects.create(
            title='测试用例1',
            description='测试描述',
            status='blocked',
            priority='P1'
        )
        
        # 创建测试执行记录
        self.testrun = TestRun.objects.create(
            name='测试执行1',
            status='completed',
            total_tests=1,
            passed_tests=1,
            executed_by=self.user1
        )
        
        self.client = Client()
    
    def test_comment_creation(self):
        """测试评论创建"""
        print("🧪 测试评论创建...")
        
        # 登录用户
        self.client.force_login(self.user1)
        
        # 创建评论
        comment_data = {
            'content': '这是一个测试评论 @user2',
            'target_type': 'testcase',
            'target_id': self.testcase.id
        }
        
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # 检查评论是否创建成功
        comment = Comment.objects.get(content__contains='测试评论')
        self.assertEqual(comment.author, self.user1)
        self.assertEqual(comment.object_id, self.testcase.id)
        
        print("✅ 评论创建成功")
    
    def test_mention_notification(self):
        """测试@提及通知"""
        print("🧪 测试@提及通知...")
        
        # 创建包含@提及的评论
        content_type = ContentType.objects.get_for_model(TestCaseModel)
        comment = Comment.objects.create(
            content='测试@提及功能 @user2',
            author=self.user1,
            content_type=content_type,
            object_id=self.testcase.id
        )
        
        # 检查提及记录
        mentioned_users = comment.get_mentioned_users()
        self.assertIn(self.user2, mentioned_users)
        
        # 创建提及记录和通知
        CommentMention.objects.create(
            comment=comment,
            mentioned_user=self.user2
        )
        
        Notification.create_notification(
            recipient=self.user2,
            actor=self.user1,
            verb='mentioned',
            target=self.testcase,
            action_object=comment
        )
        
        # 检查通知是否创建
        notification = Notification.objects.get(recipient=self.user2)
        self.assertEqual(notification.verb, 'mentioned')
        self.assertFalse(notification.read)
        
        print("✅ @提及通知测试成功")
    
    def test_comment_api_endpoints(self):
        """测试评论API端点"""
        print("🧪 测试评论API端点...")
        
        self.client.force_login(self.user1)
        
        # 测试获取评论列表
        response = self.client.get(
            f'/api/comments/?target_type=testcase&target_id={self.testcase.id}'
        )
        self.assertEqual(response.status_code, 200)
        
        # 测试用户搜索
        response = self.client.get('/api/comments/users/search/?q=user')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 1)
        
        # 测试通知摘要
        response = self.client.get('/api/comments/notifications/summary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('unread_count', data)
        
        print("✅ API端点测试成功")
    
    def test_notification_api(self):
        """测试通知API"""
        print("🧪 测试通知API...")
        
        self.client.force_login(self.user2)
        
        # 创建测试通知
        Notification.create_notification(
            recipient=self.user2,
            actor=self.user1,
            verb='mentioned',
            target=self.testcase
        )
        
        # 测试获取通知列表
        response = self.client.get('/api/comments/notifications/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        
        # 测试标记已读
        notification = Notification.objects.get(recipient=self.user2)
        response = self.client.post(
            '/api/comments/notifications/mark-read/',
            data=json.dumps({'notification_ids': [notification.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        
        # 验证已标记为已读
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        
        print("✅ 通知API测试成功")


def run_tests():
    """运行所有单元测试"""
    print("🚀 开始团队协作套件单元测试\n")
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    test_runner = get_runner(settings)()
    
    # 运行特定测试
    suite = test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()
    
    try:
        # 创建测试实例并运行
        test_case = CommentsAPITestCase()
        test_case.setUp()
        
        tests = [
            test_case.test_comment_creation,
            test_case.test_mention_notification,
            test_case.test_comment_api_endpoints,
            test_case.test_notification_api,
        ]
        
        passed = 0
        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"❌ 测试失败: {e}")
        
        print(f"\n📊 测试结果: {passed}/{len(tests)} 通过")
        
    finally:
        test_runner.teardown_databases(old_config)
        test_runner.teardown_test_environment()


if __name__ == '__main__':
    run_tests()