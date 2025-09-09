#!/usr/bin/env python
"""
后端API全面测试脚本 - 修复CSRF令牌问题

该脚本用于测试所有后端API接口，支持CSRF令牌处理
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
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"


class APITester:
    """API测试器，支持CSRF令牌处理"""
    
    def __init__(self, base_url=BACKEND_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.csrf_token = None
        self.auth_headers = {}
        
    def get_csrf_token(self):
        """获取CSRF令牌"""
        try:
            # 访问登录页面获取CSRF令牌
            login_url = f"{self.base_url}/admin/login/"
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # 从cookie中获取CSRF令牌
            csrf_token = self.session.cookies.get('csrftoken')
            if csrf_token:
                self.csrf_token = csrf_token
                self.auth_headers['X-CSRFToken'] = csrf_token
                print(f"[INFO] CSRF令牌获取成功: {csrf_token[:10]}...")
                return True
            else:
                print("[WARNING] 未能获取CSRF令牌")
                return False
        except Exception as e:
            print(f"[ERROR] 获取CSRF令牌失败: {e}")
            return False
    
    def login(self, username=TEST_USERNAME, password=TEST_PASSWORD):
        """用户登录"""
        try:
            # 确保有CSRF令牌
            if not self.csrf_token:
                self.get_csrf_token()
            
            login_url = f"{self.base_url}/admin/login/"
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': self.csrf_token,
                'next': '/admin/'
            }
            
            response = self.session.post(login_url, data=login_data, headers=self.auth_headers)
            
            # 检查是否登录成功（通常会重定向）
            if response.status_code in [200, 302] and 'sessionid' in self.session.cookies:
                print(f"[SUCCESS] 用户登录成功: {username}")
                return True
            else:
                print(f"[ERROR] 用户登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"[ERROR] 登录过程异常: {e}")
            return False
    
    def make_request(self, method, endpoint, data=None, params=None):
        """发送API请求，自动处理CSRF令牌"""
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))
        
        # 准备headers
        headers = {'Content-Type': 'application/json'}
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
    
    def test_api_endpoint(self, method, endpoint, data=None, expected_status=None):
        """测试单个API接口"""
        print(f"\n[TEST] {method.upper()} {endpoint}")
        
        response = self.make_request(method, endpoint, data)
        
        if response is None:
            print(f"[FAIL] 请求失败")
            return False
        
        status_code = response.status_code
        print(f"[RESULT] 状态码: {status_code}")
        
        # 检查预期状态码
        if expected_status and status_code != expected_status:
            print(f"[FAIL] 预期状态码 {expected_status}, 实际 {status_code}")
            try:
                print(f"[DETAIL] 响应内容: {response.text[:200]}...")
            except:
                pass
            return False
        
        # 基本的成功状态码检查
        if status_code < 400:
            print(f"[PASS] 请求成功")
            try:
                # 尝试解析JSON响应
                response_data = response.json()
                if isinstance(response_data, dict) and len(response_data) > 0:
                    print(f"[INFO] 响应数据字段数: {len(response_data)}")
            except:
                print(f"[INFO] 非JSON响应")
            return True
        else:
            print(f"[FAIL] 请求失败")
            try:
                print(f"[DETAIL] 响应内容: {response.text[:200]}...")
            except:
                pass
            return False


def run_comprehensive_api_tests():
    """运行全面的API测试"""
    print("=" * 60)
    print("Django Test Platform - 后端API全面测试")
    print("=" * 60)
    
    tester = APITester()
    
    # 登录
    if not tester.login():
        print("[CRITICAL] 登录失败，无法继续测试")
        return False
    
    test_results = []
    
    # 定义测试用例
    test_cases = [
        # API定义相关
        ('GET', '/api-test/api-definitions/', None, 200),
        ('POST', '/api-test/api-definitions/', {
            'name': 'Test API',
            'url': '/test/api',
            'method': 'GET',
            'description': 'Test API for CSRF testing'
        }, 201),
        
        # 测试用例相关
        ('GET', '/api-test/api-test-cases/', None, 200),
        
        # 批量执行测试 - 这是文档中特别提到的问题
        ('POST', '/api-test/api-test-cases/batch_execute/', {
            'test_case_ids': [],
            'environment_id': 1
        }, None),  # 暂时不指定预期状态码
        
        # 调试日志 - 第一个修复的问题
        ('GET', '/api-test/debug-log/', None, 200),
        
        # 其他核心接口
        ('GET', '/testcases/testcases/', None, 200),
        ('GET', '/testcases/testplans/', None, 200),
        ('GET', '/api-test/api-test-results/', None, 200),
        ('GET', '/api/user/users/', None, 200),
        ('GET', '/api/environments/environments/', None, 200),
        ('GET', '/api/reports/test-runs/', None, 200),
        ('GET', '/api/comments/', None, 200),
    ]
    
    # 执行测试
    total_tests = len(test_cases)
    passed_tests = 0
    
    for i, (method, endpoint, data, expected_status) in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] 测试进度")
        
        success = tester.test_api_endpoint(method, endpoint, data, expected_status)
        test_results.append({
            'method': method,
            'endpoint': endpoint,
            'success': success
        })
        
        if success:
            passed_tests += 1
        
        # 短暂延迟，避免请求过快
        time.sleep(0.1)
    
    # 测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"成功率: {success_rate:.1f}%")
    
    # 显示失败的测试
    failed_tests = [t for t in test_results if not t['success']]
    if failed_tests:
        print(f"\n失败的测试:")
        for test in failed_tests:
            print(f"  - {test['method']} {test['endpoint']}")
    
    return success_rate >= 80  # 80%以上成功率认为基本正常


if __name__ == '__main__':
    success = run_comprehensive_api_tests()
    sys.exit(0 if success else 1)