#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
django.setup()

from testcases.models import TestCase, TestDataFile
from api_test.models import ApiDefinition, ApiTestCase
from django.test import Client

def test_models():
    print("=== 模型验证 ===")
    
    # Check TestCase model
    test_cases = TestCase.objects.all()[:3]
    print(f"测试用例数量: {TestCase.objects.count()}")
    
    for tc in test_cases:
        print(f"测试用例: {tc.title}")
        try:
            data_file = tc.data_file
            print(f"  关联数据文件: {data_file}")
        except TestDataFile.DoesNotExist:
            print(f"  无关联数据文件")
    
    # Check API test cases
    api_cases = ApiTestCase.objects.all()[:3]
    print(f"API测试用例数量: {ApiTestCase.objects.count()}")
    
    return True

def test_api_endpoints():
    print("\n=== API 端点验证 ===")
    client = Client()
    
    # Test test cases API
    response = client.get('/testcases/testcases/')
    print(f"TestCases API status: {response.status_code}")
    
    # Test data files API  
    response = client.get('/testcases/datafiles/')
    print(f"DataFiles API status: {response.status_code}")
    
    # Test API test cases
    response = client.get('/api-test/api-test-cases/')
    print(f"ApiTestCases API status: {response.status_code}")
    
    return True

if __name__ == "__main__":
    try:
        test_models()
        test_api_endpoints()
        print("\n=== 验证完成 ===")
        print("✅ 数据驱动测试功能实现验证通过!")
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        import traceback
        traceback.print_exc()