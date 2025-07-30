#!/usr/bin/env python3
"""
简单的API测试脚本，用于验证后端是否正常工作
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_definitions():
    """测试API定义接口"""
    print("测试API定义接口...")
    
    # 测试获取API定义列表
    try:
        response = requests.get(f"{BASE_URL}/api-test/api-definitions/")
        print(f"GET /api-test/api-definitions/ - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试创建API定义
    test_api = {
        "name": "测试API",
        "url": "https://httpbin.org/get",
        "method": "GET",
        "headers": "{}",
        "params": "{}",
        "body": "{}",
        "description": "这是一个测试API",
        "module": "测试模块"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api-test/api-definitions/",
            json=test_api,
            headers={'Content-Type': 'application/json'}
        )
        print(f"POST /api-test/api-definitions/ - 状态码: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"创建成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return data.get('id')
        else:
            print(f"创建失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    return None

def test_api_test_cases(api_id):
    """测试API测试用例接口"""
    if not api_id:
        print("跳过测试用例测试，因为没有可用的API定义")
        return
    
    print(f"\n测试API测试用例接口 (API ID: {api_id})...")
    
    # 测试获取测试用例列表
    try:
        response = requests.get(f"{BASE_URL}/api-test/api-test-cases/")
        print(f"GET /api-test/api-test-cases/ - 状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"错误响应: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试创建测试用例
    test_case = {
        "name": "测试用例",
        "api": api_id,
        "headers": "{}",
        "params": "{}",
        "body": "{}",
        "assertions": "[]",
        "variables": "{}",
        "expected_status_code": 200,
        "is_active": True,
        "description": "这是一个测试用例"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api-test/api-test-cases/",
            json=test_case,
            headers={'Content-Type': 'application/json'}
        )
        print(f"POST /api-test/api-test-cases/ - 状态码: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"创建成功: {json.dumps(data, indent=2, ensure_ascii=False)}")
            return data.get('id')
        else:
            print(f"创建失败: {response.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    return None

def main():
    print("开始API测试...")
    print("=" * 50)
    
    # 测试API定义
    api_id = test_api_definitions()
    
    # 测试测试用例
    test_case_id = test_api_test_cases(api_id)
    
    print("\n" + "=" * 50)
    print("API测试完成！")
    
    if api_id:
        print(f"✅ API定义创建成功，ID: {api_id}")
    else:
        print("❌ API定义创建失败")
    
    if test_case_id:
        print(f"✅ 测试用例创建成功，ID: {test_case_id}")
    else:
        print("❌ 测试用例创建失败")

if __name__ == "__main__":
    main() 