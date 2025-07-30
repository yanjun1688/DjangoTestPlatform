#!/usr/bin/env python3
"""
端到端评论系统测试
验证评论和通知功能在浏览器中的完整工作流程
"""

import os
import sys
import django
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from comments.models import Comment, Notification, CommentMention
from testcases.models import TestCase as TestCaseModel
from api_test.models import TestRun

User = get_user_model()

class EndToEndCommentTest(TestCase):
    """端到端评论系统测试"""
    
    def setUp(self):
        """准备测试数据"""
        # 创建测试用户
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123',
            first_name='测试',
            last_name='用户1',
            email='test1@example.com'
        )
        
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            first_name='测试',
            last_name='用户2',
            email='test2@example.com'
        )
        
        # 创建测试用例
        self.testcase = TestCaseModel.objects.create(
            title='端到端测试用例',
            description='用于测试评论系统的测试用例',
            precondition='用户已登录',
            status='blocked',
            priority='P1'
        )
        
        # 创建测试执行记录
        self.testrun = TestRun.objects.create(
            name='端到端测试执行',
            status='completed',
            total_tests=1,
            passed_tests=1,
            executed_by=self.user1
        )
        
        self.client = Client()
        
    def test_complete_comment_workflow(self):
        """测试完整的评论工作流程"""
        print("🚀 开始端到端评论系统测试\\n")
        
        # 步骤1: 用户1登录并创建评论
        print("📝 步骤1: 用户1登录并创建评论")
        self.client.force_login(self.user1)
        
        comment_data = {
            'content': '这是一个测试评论，@testuser2 请查看',
            'target_type': 'testcase',
            'target_id': self.testcase.id
        }
        
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps(comment_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        comment = Comment.objects.get(content__contains='测试评论')
        print(f"✅ 评论创建成功: {comment.content[:30]}...")
        
        # 步骤2: 验证@提及功能
        print("\\n📝 步骤2: 验证@提及功能")
        mentioned_users = comment.get_mentioned_users()
        self.assertIn(self.user2, mentioned_users)
        print(f"✅ @提及用户识别成功: {[u.username for u in mentioned_users]}")
        
        # 步骤3: 验证通知创建
        print("\\n📝 步骤3: 验证通知创建")
        notification = Notification.objects.filter(
            recipient=self.user2,
            verb='mentioned'
        ).first()
        self.assertIsNotNone(notification)
        print(f"✅ 通知创建成功: {notification}")
        
        # 步骤4: 用户2登录并查看通知
        print("\\n📝 步骤4: 用户2登录并查看通知")
        self.client.force_login(self.user2)
        
        response = self.client.get('/api/comments/notifications/summary/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['has_unread'])
        self.assertGreater(data['unread_count'], 0)
        print(f"✅ 通知摘要获取成功: {data['unread_count']} 条未读通知")
        
        # 步骤5: 获取通知列表
        print("\\n📝 步骤5: 获取通知列表")
        response = self.client.get('/api/comments/notifications/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreater(len(data['results']), 0)
        print(f"✅ 通知列表获取成功: {len(data['results'])} 条通知")
        
        # 步骤6: 用户2回复评论
        print("\\n📝 步骤6: 用户2回复评论")
        reply_data = {
            'content': '收到，我会处理的 @testuser1',
            'target_type': 'testcase',
            'target_id': self.testcase.id,
            'parent_comment_id': comment.id
        }
        
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps(reply_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        reply = Comment.objects.get(content__contains='收到，我会处理的')
        self.assertEqual(reply.parent_comment, comment)
        print(f"✅ 回复评论创建成功: {reply.content[:30]}...")
        
        # 步骤7: 验证回复通知
        print("\\n📝 步骤7: 验证回复通知")
        reply_notification = Notification.objects.filter(
            recipient=self.user1,
            verb='mentioned'
        ).first()
        self.assertIsNotNone(reply_notification)
        print(f"✅ 回复通知创建成功: {reply_notification}")
        
        # 步骤8: 获取评论列表
        print("\\n📝 步骤8: 获取评论列表")
        response = self.client.get(
            f'/api/comments/?target_type=testcase&target_id={self.testcase.id}'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        comments = data['results']
        self.assertGreater(len(comments), 0)
        print(f"✅ 评论列表获取成功: {len(comments)} 条评论")
        
        # 步骤9: 标记通知为已读
        print("\\n📝 步骤9: 标记通知为已读")
        self.client.force_login(self.user2)
        
        response = self.client.post(
            '/api/comments/notifications/mark-read/',
            data=json.dumps({'notification_ids': [notification.id]}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        print(f"✅ 通知标记已读成功")
        
        # 步骤10: 验证用户搜索
        print("\\n📝 步骤10: 验证用户搜索")
        response = self.client.get('/api/comments/users/search/?q=testuser')
        self.assertEqual(response.status_code, 200)
        users = response.json()
        self.assertGreater(len(users), 0)
        print(f"✅ 用户搜索成功: 找到 {len(users)} 个用户")
        
        print("\\n🎉 端到端评论系统测试完成！所有功能正常工作")
        
    def test_comment_permissions(self):
        """测试评论权限控制"""
        print("\\n🔒 测试评论权限控制")
        
        # 未登录用户访问API
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, 403)
        print("✅ 未登录用户正确被拒绝访问")
        
        # 登录用户可以访问
        self.client.force_login(self.user1)
        response = self.client.get('/api/comments/')
        self.assertEqual(response.status_code, 200)
        print("✅ 登录用户可以正常访问")
        
    def test_comment_validation(self):
        """测试评论数据验证"""
        print("\\n✅ 测试评论数据验证")
        
        self.client.force_login(self.user1)
        
        # 测试空评论
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps({
                'content': '',
                'target_type': 'testcase',
                'target_id': self.testcase.id
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ 空评论被正确拒绝")
        
        # 测试无效目标类型
        response = self.client.post(
            '/api/comments/create/',
            data=json.dumps({
                'content': '测试评论',
                'target_type': 'invalid',
                'target_id': self.testcase.id
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        print("✅ 无效目标类型被正确拒绝")

def run_e2e_tests():
    """运行端到端测试"""
    print("🚀 开始端到端测试\\n")
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    test_runner = get_runner(settings)()
    
    # 运行测试
    suite = test_runner.setup_test_environment()
    old_config = test_runner.setup_databases()
    
    try:
        test_case = EndToEndCommentTest()
        test_case.setUp()
        
        tests = [
            test_case.test_complete_comment_workflow,
            test_case.test_comment_permissions,
            test_case.test_comment_validation,
        ]
        
        passed = 0
        for test in tests:
            try:
                test()
                passed += 1
            except Exception as e:
                print(f"❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"\\n📊 测试结果: {passed}/{len(tests)} 通过")
        
        if passed == len(tests):
            print("\\n🎉 所有端到端测试通过！团队协作套件功能完整！")
        else:
            print(f"\\n⚠️ {len(tests) - passed} 个测试失败")
            
    finally:
        test_runner.teardown_databases(old_config)
        test_runner.teardown_test_environment()

if __name__ == '__main__':
    run_e2e_tests()