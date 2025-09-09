#!/usr/bin/env python
"""
管理员API测试脚本 - 修复CSRF令牌问题

专门测试需要管理员权限的API接口
"""

import os
import sys
import requests
import json
import time
from urllib.parse import urljoin

# 添加Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')

# 配置
BACKEND_URL = "http://127.0.0.1:8000"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


class AdminAPITester:
    """管理员API测试器，支持CSRF令牌处理"""
    
    def __init__(self, base_url=BACKEND_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.csrf_token = None
        self.auth_headers = {}
        
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            # 先访问主页获取CSRF令牌
            response = self.session.get(f"{self.base_url}/admin/")
            if response.status_code == 302:
                # 被重定向到登录页面
                login_url = response.headers.get('Location', '/admin/login/')
                if not login_url.startswith('http'):
                    login_url = urljoin(self.base_url, login_url)
                response = self.session.get(login_url)
            
            # 从cookie中获取CSRF令牌
            csrf_token = self.session.cookies.get('csrftoken')
            if csrf_token:
                self.csrf_token = csrf_token
                self.auth_headers['X-CSRFToken'] = csrf_token
                print(f"[INFO] CSRF令牌获取成功: {csrf_token[:10]}...")
                return True
            else:
                print("[WARNING] 未能从cookies获取CSRF令牌")
                # 尝试从HTML中解析
                if 'csrfmiddlewaretoken' in response.text:
                    import re
                    match = re.search(r'name=["\']csrfmiddlewaretoken["\'] value=["\']([^"\']+)["\']', response.text)
                    if match:
                        self.csrf_token = match.group(1)
                        self.auth_headers['X-CSRFToken'] = self.csrf_token
                        print(f"[INFO] 从HTML解析CSRF令牌成功")
                        return True
                return False
        except Exception as e:
            print(f"[ERROR] 获取CSRF令牌失败: {e}")
            return False
    
    def admin_login(self, username=ADMIN_USERNAME, password=ADMIN_PASSWORD):
        """管理员登录"""
        try:
            # 确保有CSRF令牌
            if not self.csrf_token:
                if not self.get_csrf_token():
                    print("[ERROR] 无法获取CSRF令牌，登录失败")
                    return False
            
            login_url = f"{self.base_url}/admin/login/"
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': self.csrf_token,
                'next': '/admin/'
            }
            
            # 确保设置正确的headers
            headers = {
                'Referer': login_url,
                'X-CSRFToken': self.csrf_token
            }
            
            response = self.session.post(login_url, data=login_data, headers=headers)
            
            # 检查是否登录成功
            if response.status_code in [200, 302]:
                # 验证是否真的登录成功
                admin_home = self.session.get(f"{self.base_url}/admin/")
                if admin_home.status_code == 200 and 'Django administration' in admin_home.text:
                    print(f"[SUCCESS] 管理员登录成功: {username}")
                    return True
                else:
                    print(f"[ERROR] 登录后验证失败")
                    return False
            else:
                print(f"[ERROR] 管理员登录失败: {response.status_code}")
                print(f"[DEBUG] 响应内容: {response.text[:200]}...")
                return False
        except Exception as e:
            print(f"[ERROR] 登录过程异常: {e}")
            return False
    
    def make_authenticated_request(self, method, endpoint, data=None, params=None):
        """发送认证的API请求"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # 准备headers
        headers = {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'  # 标识为AJAX请求
        }
        
        if self.csrf_token:
            headers['X-CSRFToken'] = self.csrf_token
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, headers=headers)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, headers=headers)
            elif method.upper() == 'PATCH':
                response = self.session.patch(url, json=data, headers=headers)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
                
            return response
        except Exception as e:
            print(f"[ERROR] 请求异常 {method} {url}: {e}")
            return None
    
    def test_admin_endpoint(self, method, endpoint, data=None, description=""):
        """测试管理员接口"""
        print(f"\n[ADMIN TEST] {method.upper()} {endpoint}")
        if description:
            print(f"[DESCRIPTION] {description}")
        
        response = self.make_authenticated_request(method, endpoint, data)
        
        if response is None:
            print(f"[FAIL] 请求失败")
            return False
        
        status_code = response.status_code
        print(f"[RESULT] 状态码: {status_code}")
        
        # 分析结果
        if status_code == 403:
            print(f"[FAIL] 权限被拒绝 - CSRF令牌可能有问题")
            print(f"[DEBUG] CSRF令牌: {self.csrf_token[:10] if self.csrf_token else 'None'}...")
            print(f"[DEBUG] 会话Cookie: {bool(self.session.cookies.get('sessionid'))}")
            return False
        elif status_code < 400:
            print(f"[PASS] 请求成功")
            return True
        else:
            print(f"[FAIL] 请求失败")
            try:
                print(f"[DETAIL] 响应内容: {response.text[:200]}...")
            except:
                pass
            return False


def run_admin_api_tests():
    """运行管理员API测试"""
    print("=" * 60)
    print("Django Test Platform - 管理员API测试")
    print("=" * 60)
    
    tester = AdminAPITester()
    
    # 管理员登录
    if not tester.admin_login():
        print("[CRITICAL] 管理员登录失败，无法继续测试")
        return False
    
    test_results = []
    
    # 定义管理员测试用例
    admin_test_cases = [
        # 特别关注文档中提到的问题接口
        ('POST', '/api-test/api-definitions/', {
            'name': 'Admin Test API',
            'path': '/admin/test/api',
            'method': 'GET',
            'description': 'Admin test API for CSRF testing',
            'headers': {},
            'body': {}
        }, "创建API定义 - 文档中的403问题"),
        
        ('POST', '/api-test/api-test-cases/batch_execute/', {
            'test_case_ids': [],
            'environment_id': 1
        }, "批量执行测试用例 - 文档中的403问题"),
        
        # 其他管理员操作
        ('GET', '/api-test/api-definitions/', None, "获取API定义列表"),
        ('GET', '/api-test/api-test-cases/', None, "获取测试用例列表"),
        ('GET', '/api-test/test-plans/', None, "获取测试计划列表"),
        
        # 用户管理
        ('GET', '/user-management/users/', None, "获取用户列表"),
        ('POST', '/user-management/users/', {
            'username': 'test_user_csrf',
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': 'tester'
        }, "创建新用户"),
        
        # Mock服务器管理
        ('GET', '/mock-server/mock-apis/', None, "获取Mock API列表"),
        ('POST', '/mock-server/mock-apis/', {
            'name': 'Test Mock API',
            'path': '/mock/test',
            'method': 'GET',
            'response_body': '{"status": "ok"}',
            'status_code': 200
        }, "创建Mock API"),
        
        # 报告管理
        ('GET', '/reports/test-reports/', None, "获取测试报告列表"),
        
        # 环境管理
        ('GET', '/environments/environments/', None, "获取环境列表"),
        ('POST', '/environments/environments/', {
            'name': 'Test Environment',
            'base_url': 'http://test.example.com',
            'description': 'Test environment for CSRF testing'
        }, "创建测试环境"),
    ]
    
    # 执行测试
    total_tests = len(admin_test_cases)
    passed_tests = 0
    
    for i, (method, endpoint, data, description) in enumerate(admin_test_cases, 1):
        print(f"\n[{i}/{total_tests}] 测试进度")
        
        success = tester.test_admin_endpoint(method, endpoint, data, description)
        test_results.append({
            'method': method,
            'endpoint': endpoint,
            'description': description,
            'success': success
        })
        
        if success:
            passed_tests += 1
        
        # 短暂延迟
        time.sleep(0.2)
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("管理员API测试结果汇总")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 特别关注CSRF相关的失败
    csrf_related_failures = []
    for test in test_results:
        if not test['success'] and ('403' in str(test) or 'CSRF' in test['description']):
            csrf_related_failures.append(test)
    
    if csrf_related_failures:
        print(f"\n⚠️  CSRF相关失败测试:")
        for test in csrf_related_failures:
            print(f"  - {test['method']} {test['endpoint']}: {test['description']}")
    
    # 显示所有失败的测试
    failed_tests = [t for t in test_results if not t['success']]
    if failed_tests:
        print(f"\n失败的测试详情:")
        for test in failed_tests:
            print(f"  - {test['method']} {test['endpoint']}: {test['description']}")
    
    return success_rate >= 70  # 70%以上成功率认为基本正常（管理员操作相对复杂）


if __name__ == '__main__':
    success = run_admin_api_tests()
    sys.exit(0 if success else 1)