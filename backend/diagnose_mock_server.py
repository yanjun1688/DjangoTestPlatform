#!/usr/bin/env python
"""
简化的Mock Server测试
用于检查Mock Server是否正常工作
"""
import requests
import json
import time

def test_basic_request(url='http://localhost:8000'):
    """测试基本的服务器连接"""
    print(f"🔍 测试服务器连接: {url}")
    
    try:
        # 测试根路径
        response = requests.get(f"{url}/", timeout=5)
        print(f"   根路径状态码: {response.status_code}")
        
        # 测试Admin页面
        response = requests.get(f"{url}/admin/", timeout=5)
        print(f"   Admin页面状态码: {response.status_code}")
        
        # 测试API路径
        response = requests.get(f"{url}/api/", timeout=5)
        print(f"   API路径状态码: {response.status_code}")
        
        return True
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器，请确保Django开发服务器正在运行")
        print("   💡 启动命令: python manage.py runserver")
        return False
    except requests.exceptions.Timeout:
        print("   ❌ 请求超时")
        return False
    except Exception as e:
        print(f"   ❌ 连接测试失败: {str(e)}")
        return False

def test_mock_endpoints(url='http://localhost:8000'):
    """测试Mock端点"""
    print(f"\n🧪 测试Mock端点")
    
    # 测试不存在的Mock API
    try:
        response = requests.get(f"{url}/mock/api/test", timeout=5)
        print(f"   不存在的Mock API状态码: {response.status_code}")
        
        if response.status_code == 404:
            try:
                data = response.json()
                if 'error' in data and 'Mock API not found' in data['error']:
                    print("   ✅ Mock Server正常响应404错误")
                    return True
                else:
                    print(f"   ⚠️  响应格式异常: {data}")
            except json.JSONDecodeError:
                print(f"   ⚠️  非JSON响应: {response.text}")
        else:
            print(f"   ⚠️  意外的状态码: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ❌ Mock端点请求超时")
        return False
    except Exception as e:
        print(f"   ❌ Mock端点测试失败: {str(e)}")
        return False
    
    return True

def test_api_endpoints(url='http://localhost:8000'):
    """测试API管理端点"""
    print(f"\n📋 测试API管理端点")
    
    endpoints = [
        '/api/mock-server/mocks/',
        '/api/mock-server/logs/',
    ]
    
    results = []
    for endpoint in endpoints:
        try:
            response = requests.get(f"{url}{endpoint}", timeout=5)
            status_ok = response.status_code in [200, 401, 403]  # 200正常, 401/403认证问题
            print(f"   {endpoint}: {response.status_code} {'✅' if status_ok else '❌'}")
            results.append(status_ok)
        except requests.exceptions.Timeout:
            print(f"   {endpoint}: 超时 ❌")
            results.append(False)
        except Exception as e:
            print(f"   {endpoint}: 错误 ❌ ({str(e)})")
            results.append(False)
    
    return all(results)

def check_django_settings():
    """检查Django配置"""
    print("⚙️  检查Django配置")
    
    try:
        import os
        import sys
        
        # 检查当前目录
        current_dir = os.getcwd()
        print(f"   当前目录: {current_dir}")
        
        # 检查manage.py是否存在
        manage_py_path = os.path.join(current_dir, 'manage.py')
        if os.path.exists(manage_py_path):
            print("   ✅ manage.py 存在")
        else:
            print("   ❌ manage.py 不存在")
            return False
        
        # 检查mock_server应用是否存在
        mock_server_path = os.path.join(current_dir, 'mock_server')
        if os.path.exists(mock_server_path):
            print("   ✅ mock_server 应用目录存在")
        else:
            print("   ❌ mock_server 应用目录不存在")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ 配置检查失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🚀 Mock Server 快速诊断")
    print("=" * 50)
    
    # 检查Django配置
    if not check_django_settings():
        print("\n❌ Django配置检查失败")
        return False
    
    # 测试服务器连接
    if not test_basic_request():
        return False
    
    # 测试Mock端点
    if not test_mock_endpoints():
        return False
    
    # 测试API端点
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("🎉 基础诊断完成！")
    print("💡 如果所有测试都通过，Mock Server应该可以正常工作")
    print("💡 如果有超时问题，请检查:")
    print("   1. Django服务器是否正在运行")
    print("   2. 服务器端口是否正确(默认8000)")
    print("   3. 防火墙设置")
    print("   4. Mock API的delay_ms设置是否过大")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n❌ 诊断过程出错: {str(e)}")
        import traceback
        traceback.print_exc()