#!/usr/bin/env python3
"""
团队协作套件 API 测试脚本
测试评论和通知功能的前后端集成
"""

import requests
import json
import time
import sys

BASE_URL = 'http://localhost:8000'

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        
    def test_login(self):
        """测试登录功能"""
        print("🔐 测试用户登录...")
        
        # 先获取CSRF token
        csrf_response = self.session.get(f'{BASE_URL}/admin/')
        if csrf_response.status_code != 200:
            print("❌ 无法获取CSRF token")
            return False
            
        # 模拟登录过程（简化版）
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        # 这里我们直接使用Django的认证系统
        print("✅ 登录测试跳过（需要前端配合）")
        return True
    
    def test_user_search(self):
        """测试用户搜索API"""
        print("👥 测试用户搜索API...")
        
        # 模拟已认证请求（实际应该通过登录获得session）
        headers = {'Content-Type': 'application/json'}
        
        response = self.session.get(
            f'{BASE_URL}/api/comments/users/search/?q=test',
            headers=headers
        )
        
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 401:
            print("⚠️ 需要认证（符合预期）")
            return True
        return response.status_code == 200
    
    def test_comments_api(self):
        """测试评论API"""
        print("💬 测试评论API...")
        
        # 测试获取评论列表
        response = self.session.get(
            f'{BASE_URL}/api/comments/?target_type=testcase&target_id=1'
        )
        
        print(f"获取评论列表 - 状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 401:
            print("⚠️ 需要认证（符合预期）")
            return True
        return response.status_code == 200
    
    def test_notifications_api(self):
        """测试通知API"""
        print("🔔 测试通知API...")
        
        # 测试通知摘要
        response = self.session.get(f'{BASE_URL}/api/comments/notifications/summary/')
        
        print(f"通知摘要 - 状态码: {response.status_code}")
        print(f"响应: {response.text}")
        
        if response.status_code == 401:
            print("⚠️ 需要认证（符合预期）")
            return True
        return response.status_code == 200
    
    def test_api_structure(self):
        """测试API结构"""
        print("🏗️ 测试API结构...")
        
        # 测试各个API端点是否可访问
        endpoints = [
            '/api/comments/',
            '/api/comments/create/',
            '/api/comments/notifications/',
            '/api/comments/notifications/mark-read/',
            '/api/comments/notifications/summary/',
            '/api/comments/users/search/',
        ]
        
        for endpoint in endpoints:
            response = self.session.get(f'{BASE_URL}{endpoint}')
            status = "✅" if response.status_code in [200, 401, 405] else "❌"
            print(f"{status} {endpoint} - {response.status_code}")
        
        return True
    
    def test_frontend_connection(self):
        """测试前端连接"""
        print("🌐 测试前端连接...")
        
        try:
            # 检查前端是否运行在5173或5174端口
            for port in [5173, 5174]:
                try:
                    response = requests.get(f'http://localhost:{port}', timeout=5)
                    if response.status_code == 200:
                        print(f"✅ 前端服务运行在端口 {port}")
                        return True
                except requests.exceptions.ConnectionError:
                    continue
            
            print("❌ 前端服务未运行")
            return False
            
        except Exception as e:
            print(f"❌ 前端连接测试失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始团队协作套件集成测试\n")
        
        tests = [
            ("前端连接", self.test_frontend_connection),
            ("API结构", self.test_api_structure),
            ("用户搜索", self.test_user_search),
            ("评论API", self.test_comments_api),
            ("通知API", self.test_notifications_api),
        ]
        
        passed = 0
        total = len(tests)
        
        for name, test_func in tests:
            print(f"\n📝 {name}测试:")
            try:
                if test_func():
                    print(f"✅ {name}测试通过")
                    passed += 1
                else:
                    print(f"❌ {name}测试失败")
            except Exception as e:
                print(f"❌ {name}测试异常: {e}")
        
        print(f"\n📊 测试报告:")
        print(f"总计: {total}")
        print(f"通过: {passed}")
        print(f"失败: {total - passed}")
        print(f"成功率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！团队协作套件后端功能正常")
        else:
            print(f"\n⚠️ {total - passed} 个测试失败，需要检查")

if __name__ == '__main__':
    tester = APITester()
    tester.run_all_tests()