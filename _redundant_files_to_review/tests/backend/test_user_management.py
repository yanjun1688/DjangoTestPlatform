from django.test import TestCase
from django.contrib.auth import get_user_model
from user_management.models import User, UserLoginLog
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class UserModelTest(TestCase):
    """测试用户模型"""
    
    def test_create_user(self):
        """测试创建普通用户"""
        user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            phone='13800138000',
            department='IT'
        )
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'user')  # 默认角色
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertEqual(str(user), 'testuser (普通用户)')

    def test_create_admin_user(self):
        """测试创建管理员用户"""
        admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )
        
        self.assertEqual(admin.role, 'admin')
        self.assertTrue(admin.is_admin)
        self.assertEqual(str(admin), 'admin (管理员)')

    def test_create_superuser(self):
        """测试创建超级用户"""
        superuser = User.objects.create_superuser(
            username='superuser',
            password='password123',
            email='super@example.com'
        )
        
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_admin)  # 超级用户也被认为是管理员

class UserLoginLogTest(TestCase):
    """测试用户登录日志"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )

    def test_create_login_log(self):
        """测试创建登录日志"""
        log = UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 Test Browser',
            success=True
        )
        
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertTrue(log.success)
        self.assertIn('testuser', str(log))

    def test_failed_login_log(self):
        """测试失败登录日志"""
        log = UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 Test Browser',
            success=False
        )
        
        self.assertFalse(log.success)

class UserAuthAPITest(APITestCase):
    """测试用户认证相关API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )

    def test_user_list_requires_admin(self):
        """测试用户列表需要管理员权限"""
        # 未认证用户
        response = self.client.get('/api/user/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 普通用户
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 管理员用户
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/user/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_view_own_profile(self):
        """测试用户可以查看自己的资料"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/user/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_user_cannot_view_others_profile(self):
        """测试用户不能查看其他用户资料"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='password123'
        )
        
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/user/users/{other_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_all_profiles(self):
        """测试管理员可以查看所有用户资料"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/user/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_user(self):
        """测试管理员可以创建用户"""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com',
            'role': 'user',
            'department': 'IT'
        }
        response = self.client.post('/api/user/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_normal_user_cannot_create_user(self):
        """测试普通用户不能创建用户"""
        self.client.force_authenticate(user=self.user)
        data = {
            'username': 'newuser',
            'password': 'newpassword123',
            'email': 'new@example.com'
        }
        response = self.client.post('/api/user/users/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class UserViewSetTest(APITestCase):
    """测试用户管理视图集"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )

    def test_user_search_functionality(self):
        """测试用户搜索功能"""
        # 创建更多测试用户
        User.objects.create_user(username='john', email='john@example.com', first_name='John', last_name='Doe')
        User.objects.create_user(username='jane', email='jane@example.com', first_name='Jane', last_name='Smith')
        
        self.client.force_authenticate(user=self.admin)
        
        # 搜索用户名
        response = self.client.get('/api/user/users/?search=john')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'john')
        
        # 搜索邮箱
        response = self.client.get('/api/user/users/?search=jane@example.com')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], 'jane@example.com')

    def test_user_role_filter(self):
        """测试用户角色过滤"""
        self.client.force_authenticate(user=self.admin)
        
        # 过滤管理员
        response = self.client.get('/api/user/users/?role=admin')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        admin_users = [user for user in response.data if user['role'] == 'admin']
        self.assertTrue(len(admin_users) > 0)
        
        # 过滤普通用户
        response = self.client.get('/api/user/users/?role=user')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_users = [user for user in response.data if user['role'] == 'user']
        self.assertTrue(len(user_users) > 0)

    def test_user_active_status_filter(self):
        """测试用户活跃状态过滤"""
        # 创建已禁用用户
        disabled_user = User.objects.create_user(
            username='disabled',
            password='password123',
            is_active=False
        )
        
        self.client.force_authenticate(user=self.admin)
        
        # 过滤活跃用户
        response = self.client.get('/api/user/users/?is_active=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        active_users = [user for user in response.data if user['is_active']]
        self.assertTrue(len(active_users) > 0)
        
        # 过滤已禁用用户
        response = self.client.get('/api/user/users/?is_active=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        inactive_users = [user for user in response.data if not user['is_active']]
        self.assertTrue(len(inactive_users) > 0)

    def test_get_current_user_info(self):
        """测试获取当前用户信息"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_change_password_success(self):
        """测试修改密码成功"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'password123',
            'new_password': 'newpassword123'
        }
        response = self.client.post('/api/user/users/change_password/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '密码修改成功')
        
        # 验证密码已更改
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))

    def test_change_password_wrong_old_password(self):
        """测试修改密码时原密码错误"""
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword123'
        }
        response = self.client.post('/api/user/users/change_password/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], '原密码错误')

    def test_toggle_user_active_status(self):
        """测试切换用户启用状态"""
        self.client.force_authenticate(user=self.admin)
        
        # 禁用用户
        response = self.client.post(f'/api/user/users/{self.user.id}/toggle_active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        
        # 重新启用用户
        response = self.client.post(f'/api/user/users/{self.user.id}/toggle_active/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_active'])

class AuthViewSetTest(APITestCase):
    """测试认证视图集"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123',
            email='test@example.com'
        )

    def test_login_success(self):
        """测试登录成功"""
        data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = self.client.post('/api/user/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '登录成功')
        self.assertEqual(response.data['user']['username'], 'testuser')
        
        # 验证登录日志已创建
        self.assertEqual(UserLoginLog.objects.count(), 1)
        log = UserLoginLog.objects.first()
        self.assertEqual(log.user, self.user)
        self.assertTrue(log.success)

    def test_login_failure(self):
        """测试登录失败"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/user/auth/login/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_auth_authenticated(self):
        """测试检查认证状态（已认证）"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/auth/check_auth/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['authenticated'])
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_check_auth_unauthenticated(self):
        """测试检查认证状态（未认证）"""
        response = self.client.get('/api/user/auth/check_auth/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['authenticated'])

    def test_get_client_ip(self):
        """测试获取客户端IP地址"""
        from user_management.views import AuthViewSet
        
        # 模拟请求
        request = type('MockRequest', (), {
            'META': {
                'HTTP_X_FORWARDED_FOR': '192.168.1.1,10.0.0.1',
                'REMOTE_ADDR': '127.0.0.1'
            }
        })()
        
        auth_viewset = AuthViewSet()
        ip = auth_viewset.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
        
        # 测试没有X_FORWARDED_FOR的情况
        request.META = {'REMOTE_ADDR': '127.0.0.1'}
        ip = auth_viewset.get_client_ip(request)
        self.assertEqual(ip, '127.0.0.1')

class LogoutViewTest(APITestCase):
    """测试登出视图"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )

    def test_logout_post(self):
        """测试POST登出"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/user/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '登出成功')

    def test_logout_get(self):
        """测试GET登出"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '登出成功')

    def test_logout_unauthenticated(self):
        """测试未认证用户登出"""
        response = self.client.post('/api/user/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '登出成功')

class UserLoginLogViewSetTest(APITestCase):
    """测试用户登录日志视图集"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )
        
        # 创建登录日志
        UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Test Browser',
            success=True
        )
        UserLoginLog.objects.create(
            user=self.user,
            ip_address='192.168.1.2',
            user_agent='Test Browser',
            success=False
        )

    def test_list_login_logs_requires_admin(self):
        """测试列出登录日志需要管理员权限"""
        # 普通用户无权限
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/user/login-logs/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 管理员有权限
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/user/login-logs/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_login_logs_by_user(self):
        """测试按用户过滤登录日志"""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get(f'/api/user/login-logs/?user_id={self.user.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # 验证所有日志都属于指定用户
        for log in response.data:
            self.assertEqual(log['user'], self.user.id)

    def test_filter_login_logs_by_success(self):
        """测试按成功状态过滤登录日志"""
        self.client.force_authenticate(user=self.admin)
        
        # 过滤成功的登录
        response = self.client.get('/api/user/login-logs/?success=true')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        success_logs = [log for log in response.data if log['success']]
        self.assertTrue(len(success_logs) > 0)
        
        # 过滤失败的登录
        response = self.client.get('/api/user/login-logs/?success=false')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        failed_logs = [log for log in response.data if not log['success']]
        self.assertTrue(len(failed_logs) > 0)

class UserPermissionTest(APITestCase):
    """测试用户权限"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            password='password123'
        )
        self.admin = User.objects.create_user(
            username='admin',
            password='password123',
            role='admin'
        )

    def test_user_can_only_access_own_data(self):
        """测试用户只能访问自己的数据"""
        self.client.force_authenticate(user=self.user1)
        
        # 可以访问自己的数据
        response = self.client.get(f'/api/user/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 不能访问他人的数据
        response = self.client.get(f'/api/user/users/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_access_all_data(self):
        """测试管理员可以访问所有数据"""
        self.client.force_authenticate(user=self.admin)
        
        # 可以访问所有用户数据
        response = self.client.get(f'/api/user/users/{self.user1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.client.get(f'/api/user/users/{self.user2.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_own_profile(self):
        """测试用户可以更新自己的资料"""
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'first_name': 'Updated Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(f'/api/user/users/{self.user1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'Updated Name')
        self.assertEqual(self.user1.email, 'updated@example.com')

    def test_user_cannot_update_role(self):
        """测试用户不能修改自己的角色"""
        self.client.force_authenticate(user=self.user1)
        
        data = {'role': 'admin'}
        response = self.client.patch(f'/api/user/users/{self.user1.id}/', data)
        # 应该成功，但角色不会改变（在序列化器中处理）
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.role, 'user')  # 角色不应该改变