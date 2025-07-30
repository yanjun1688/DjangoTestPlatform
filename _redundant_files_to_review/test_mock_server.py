#!/usr/bin/env python
"""
Mock Server功能验证脚本
用于测试Mock Server的核心功能
"""
import os
import sys
import django
import requests
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from mock_server.models import MockAPI

def setup_test_data():
    """设置测试数据"""
    print("=== 设置测试数据 ===")
    
    # 创建测试用户
    user, created = User.objects.get_or_create(
        username='mock_test_user',
        defaults={'email': 'test@example.com'}
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ 创建测试用户: {user.username}")
    else:
        print(f"✅ 使用现有用户: {user.username}")
    
    # 清理现有的Mock APIs
    MockAPI.objects.filter(created_by=user).delete()
    
    # 创建测试Mock APIs
    mock_apis = [
        {
            'name': '用户信息接口',
            'path': '/api/user/profile',
            'method': 'GET',
            'response_status_code': 200,
            'response_body': '{"username": "MockUser", "email": "mock@test.com", "id": 123}',
            'response_headers': {'Content-Type': 'application/json'},
            'description': '模拟用户信息接口'
        },
        {
            'name': '创建用户接口',
            'path': '/api/user',
            'method': 'POST',
            'response_status_code': 201,
            'response_body': '{"id": 456, "message": "User created successfully"}',
            'response_headers': {'Content-Type': 'application/json'},
            'description': '模拟创建用户接口'
        },
        {
            'name': '错误接口',
            'path': '/api/error',
            'method': 'GET',
            'response_status_code': 500,
            'response_body': '{"error": "Internal Server Error", "code": "E001"}',
            'response_headers': {'Content-Type': 'application/json'},
            'description': '模拟错误响应'
        },
        {
            'name': '慢响应接口',
            'path': '/api/slow',
            'method': 'GET',
            'response_status_code': 200,
            'response_body': '{"message": "This is a slow response"}',
            'delay_ms': 500,
            'description': '模拟慢响应接口'
        }
    ]
    
    created_mocks = []
    for mock_data in mock_apis:
        mock_api = MockAPI.objects.create(
            created_by=user,
            **mock_data
        )
        created_mocks.append(mock_api)
        print(f"✅ 创建Mock API: {mock_api.method} {mock_api.path}")
    
    return user, created_mocks

def test_mock_apis(base_url='http://localhost:8000'):
    """测试Mock APIs"""
    print(f"\n=== 测试Mock APIs (服务器: {base_url}) ===")
    
    test_cases = [
        {
            'name': '测试用户信息接口',
            'method': 'GET',
            'url': f'{base_url}/mock/api/user/profile',
            'expected_status': 200,
            'expected_data': {'username': 'MockUser'}
        },
        {
            'name': '测试创建用户接口',
            'method': 'POST',
            'url': f'{base_url}/mock/api/user',
            'expected_status': 201,
            'expected_data': {'id': 456}
        },
        {
            'name': '测试错误接口',
            'method': 'GET',
            'url': f'{base_url}/mock/api/error',
            'expected_status': 500,
            'expected_data': {'error': 'Internal Server Error'}
        },
        {
            'name': '测试慢响应接口',
            'method': 'GET',
            'url': f'{base_url}/mock/api/slow',
            'expected_status': 200,
            'expected_data': {'message': 'This is a slow response'},
            'min_duration': 0.3  # 至少300ms
        },
        {
            'name': '测试不存在的接口',
            'method': 'GET',
            'url': f'{base_url}/mock/api/notfound',
            'expected_status': 404,
            'expected_data': {'error': 'Mock API not found'}
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        
        try:
            start_time = time.time()
            
            if test_case['method'] == 'GET':
                response = requests.get(test_case['url'], timeout=10)
            elif test_case['method'] == 'POST':
                response = requests.post(test_case['url'], timeout=10)
            else:
                response = requests.request(test_case['method'], test_case['url'], timeout=10)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   状态码: {response.status_code} (期望: {test_case['expected_status']})")
            print(f"   响应时间: {duration:.3f}s")
            
            # 检查状态码
            status_ok = response.status_code == test_case['expected_status']
            if status_ok:
                print("   ✅ 状态码正确")
            else:
                print("   ❌ 状态码不匹配")
            
            # 检查响应体
            data_ok = True
            try:
                response_data = response.json()
                for key, value in test_case['expected_data'].items():
                    if key not in response_data or response_data[key] != value:
                        data_ok = False
                        break
                
                if data_ok:
                    print("   ✅ 响应数据正确")
                    print(f"   📄 响应: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                else:
                    print("   ❌ 响应数据不匹配")
                    print(f"   📄 期望包含: {test_case['expected_data']}")
                    print(f"   📄 实际响应: {response_data}")
            except json.JSONDecodeError:
                print(f"   📄 响应 (非JSON): {response.text}")
                data_ok = False
            
            # 检查响应时间
            duration_ok = True
            if 'min_duration' in test_case:
                if duration >= test_case['min_duration']:
                    print("   ✅ 响应时间符合预期")
                else:
                    print(f"   ❌ 响应时间过快 (期望至少 {test_case['min_duration']}s)")
                    duration_ok = False
            
            results.append({
                'name': test_case['name'],
                'success': status_ok and data_ok and duration_ok,
                'status_code': response.status_code,
                'duration': duration
            })
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ 请求失败: {str(e)}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
        except Exception as e:
            print(f"   ❌ 测试异常: {str(e)}")
            results.append({
                'name': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    return results

def print_summary(results):
    """打印测试总结"""
    print("\n" + "="*50)
    print("🔍 测试结果总结")
    print("="*50)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"总测试数: {total_tests}")
    print(f"通过: {passed_tests}")
    print(f"失败: {failed_tests}")
    print(f"成功率: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print(f"\n❌ 失败的测试:")
        for result in results:
            if not result['success']:
                error_msg = result.get('error', '状态码或数据不匹配')
                print(f"   - {result['name']}: {error_msg}")
    
    print("\n" + "="*50)
    if failed_tests == 0:
        print("🎉 所有测试通过！Mock Server功能正常工作！")
    else:
        print("⚠️  部分测试失败，请检查Mock Server配置或服务状态。")
    print("="*50)

def main():
    """主函数"""
    print("🚀 Mock Server功能验证")
    print("="*50)
    
    try:
        # 设置测试数据
        user, mock_apis = setup_test_data()
        print(f"✅ 创建了 {len(mock_apis)} 个Mock API")
        
        # 显示创建的Mock APIs
        print(f"\n📋 Mock API列表:")
        for mock in mock_apis:
            status = "启用" if mock.is_active else "禁用"
            print(f"   {mock.method:6} {mock.path:20} -> {mock.response_status_code} ({status})")
        
        # 测试Mock APIs
        results = test_mock_apis()
        
        # 打印总结
        print_summary(results)
        
        # 清理提示
        print(f"\n💡 测试完成后，可以通过以下方式清理测试数据:")
        print(f"   python manage.py shell -c \"from django.contrib.auth import get_user_model
User = get_user_model(); User.objects.filter(username='mock_test_user').delete()\"")
        
    except Exception as e:
        print(f"❌ 验证过程出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)