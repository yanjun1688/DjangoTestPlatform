from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from user_management.models import UserLoginLog

User = get_user_model()

class UserModelTest(TestCase):
    """用户模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='user',
            phone='13800138000',
            department='测试部门'
        )
    
    def test_user_creation(self):
        """测试用户创建"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.role, 'user')
        self.assertEqual(self.user.phone, '13800138000')
        self.assertEqual(self.user.department, '测试部门')
        self.assertTrue(self.user.is_active)
    
    def test_user_str_method(self):
        """测试用户字符串表示"""
        expected = f"{self.user.username} ({self.user.get_role_display()})"
        self.assertEqual(str(self.user), expected)
    
    def test_is_admin_property(self):
        """测试管理员属性"""
        # 普通用户
        self.assertFalse(self.user.is_admin)
        
        # 角色为admin的用户
        admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            role='admin'
        )
        self.assertTrue(admin_user.is_admin)
        
        # 超级用户
        super_user = User.objects.create_superuser(
            username='superuser',
            password='superpass123'
        )
        self.assertTrue(super_user.is_admin)
    
    def test_user_role_choices(self):
        """测试用户角色选择"""
        # 测试admin角色
        admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            role='admin'
        )
        self.assertEqual(admin_user.role, 'admin')
        self.assertEqual(admin_user.get_role_display(), '管理员')
        
        # 测试默认角色
        default_user = User.objects.create_user(
            username='defaultuser',
            password='defaultpass123'
        )
        self.assertEqual(default_user.role, 'user')
        self.assertEqual(default_user.get_role_display(), '普通用户')

class UserLoginLogModelTest(TestCase):
    """用户登录日志模型测试"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.login_log = UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 Test Browser',
            success=True
        )
    
    def test_login_log_creation(self):
        """测试登录日志创建"""
        self.assertEqual(self.login_log.user, self.user)
        self.assertEqual(self.login_log.ip_address, '192.168.1.1')
        self.assertEqual(self.login_log.user_agent, 'Mozilla/5.0 Test Browser')
        self.assertTrue(self.login_log.success)
        self.assertIsNotNone(self.login_log.login_time)
    
    def test_login_log_str_method(self):
        """测试登录日志字符串表示"""
        expected = f"{self.user.username} - {self.login_log.login_time}"
        self.assertEqual(str(self.login_log), expected)
    
    def test_failed_login_log(self):
        """测试失败登录日志"""
        failed_log = UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.100',
            success=False
        )
        self.assertFalse(failed_log.success)
        self.assertEqual(failed_log.ip_address, '192.168.1.100')
    
    def test_login_log_ordering(self):
        """测试登录日志排序"""
        import time
        # 稍微等待一下以确保时间不同
        time.sleep(0.01)
        
        # 创建另一个登录日志
        second_log = UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.2'
        )
        
        # 获取所有日志，应该按登录时间倒序
        logs = list(UserLoginLog.objects.all())
        # 比较ID而不是对象本身，因为时间可能相同
        self.assertEqual(logs[0].id, second_log.id)  # 最新的在前
        self.assertEqual(logs[1].id, self.login_log.id)
