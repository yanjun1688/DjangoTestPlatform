#!/usr/bin/env python3
"""
Django单元测试运行器
使用Django的内置测试客户端进行测试，不需要启动服务器
"""
import io
import sys

# Set stdout to utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import django
from django.conf import settings
from django.test.utils import get_runner

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')

# 配置最小的Django设置来运行测试
if not settings.configured:
    from test_platform import settings as project_settings
    settings.configure(
        **{key: getattr(project_settings, key) for key in dir(project_settings) if key.isupper()}
    )

django.setup()

def run_mock_server_tests():
    """运行Mock Server相关的单元测试"""
    print("🧪 运行Mock Server单元测试")
    print("=" * 50)
    
    try:
        from django.test import TestCase, Client
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from mock_server.models import MockAPI, MockAPIUsageLog
        import json
        
        # 测试1: 模型创建
        print("📋 测试1: MockAPI模型创建")
        try:
            # 创建测试用户
            user, created = User.objects.get_or_create(
                username='testuser',
                defaults={'email': 'test@example.com', 'password': 'testpass'}
            )
            
            # 创建Mock API
            mock_api = MockAPI.objects.create(
                name='测试Mock API',
                path='/api/test',
                method='GET',
                response_status_code=200,
                response_body='{"test": "success"}',
                created_by=user
            )
            
            assert mock_api.name == '测试Mock API'
            assert mock_api.path == '/api/test'
            assert mock_api.method == 'GET'
            assert mock_api.is_active == True
            
            print("   ✅ MockAPI模型创建成功")
            
        except Exception as e:
            print(f"   ❌ MockAPI模型测试失败: {str(e)}")
            return False
        
        # 测试2: Mock服务
        print("\n🌐 测试2: Mock服务功能")
        try:
            client = Client()
            
            # 测试存在的Mock API
            response = client.get('/mock/api/test')
            assert response.status_code == 200
            
            response_data = json.loads(response.content.decode())
            assert response_data['test'] == 'success'
            
            print("   ✅ Mock服务返回正确响应")
            
            # 测试不存在的Mock API
            response = client.get('/mock/api/notfound')
            assert response.status_code == 404
            
            response_data = json.loads(response.content.decode())
            assert 'Mock API not found' in response_data['error']
            
            print("   ✅ Mock服务正确处理404")
            
        except Exception as e:
            print(f"   ❌ Mock服务测试失败: {str(e)}")
            return False
        
        # 测试3: 使用日志记录
        print("\n📝 测试3: 使用日志记录")
        try:
            initial_log_count = MockAPIUsageLog.objects.count()
            
            # 发起请求
            client.get('/mock/api/test')
            
            final_log_count = MockAPIUsageLog.objects.count()
            assert final_log_count == initial_log_count + 1
            
            # 检查日志内容
            log = MockAPIUsageLog.objects.latest('timestamp')
            assert log.mock_api == mock_api
            assert log.request_method == 'GET'
            assert log.request_path == '/api/test'
            
            print("   ✅ 使用日志记录正常")
            
        except Exception as e:
            print(f"   ❌ 使用日志测试失败: {str(e)}")
            return False
        
        # 测试4: API管理接口
        print("\n🔧 测试4: API管理接口")
        try:
            from rest_framework.test import APIClient
            from django.contrib.auth import authenticate
            
            api_client = APIClient()
            api_client.force_authenticate(user=user)
            
            # 测试获取Mock API列表
            response = api_client.get('/api/mock-server/mocks/')
            assert response.status_code == 200
            assert len(response.data) >= 1
            
            print("   ✅ Mock API列表接口正常")
            
            # 测试创建Mock API
            new_mock_data = {
                'name': '新Mock API',
                'path': '/api/new',
                'method': 'POST',
                'response_status_code': 201,
                'response_body': '{"created": true}',
                'is_active': True
            }
            
            response = api_client.post('/api/mock-server/mocks/', new_mock_data, format='json')
            assert response.status_code == 201
            assert response.data['name'] == '新Mock API'
            
            print("   ✅ Mock API创建接口正常")
            
            # 测试统计接口
            response = api_client.get('/api/mock-server/mocks/statistics/')
            assert response.status_code == 200
            assert 'total_mocks' in response.data
            assert response.data['total_mocks'] >= 2
            
            print("   ✅ 统计接口正常")
            
        except Exception as e:
            print(f"   ❌ API管理接口测试失败: {str(e)}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 所有Mock Server单元测试通过！")
        print("=" * 50)
        
        return True
        
    except ImportError as e:
        print(f"❌ 导入模块失败: {str(e)}")
        print("💡 请确保已安装所有依赖并运行了数据库迁移")
        return False
    except Exception as e:
        print(f"❌ 测试运行出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_reports_tests():
    """运行Reports相关的单元测试"""
    print("\n📊 运行Reports单元测试")
    print("=" * 50)
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from api_test.models import ApiDefinition, ApiTestCase, ApiTestResult, TestRun
        from testcases.models import TestPlan
        from rest_framework.test import APIClient
        
        # 创建测试数据
        user = User.objects.get_or_create(username='reportuser')[0]
        
        test_plan = TestPlan.objects.create(
            name='报告测试计划',
            status='pending',
            assignee=user
        )
        
        api_def = ApiDefinition.objects.create(
            name='报告测试API',
            method='GET',
            url='http://test.com/api'
        )
        
        test_case = ApiTestCase.objects.create(
            name='报告测试用例',
            api=api_def,
            expected_status_code=200
        )
        
        test_run = TestRun.objects.create(
            name='报告测试执行',
            test_plan=test_plan,
            executed_by=user
        )
        
        # 创建测试结果
        ApiTestResult.objects.create(
            test_case=test_case,
            test_run=test_run,
            status='passed',
            response_code=200,
            response_time=150.0
        )
        
        print("   ✅ 测试数据创建成功")
        
        # 测试API接口
        api_client = APIClient()
        api_client.force_authenticate(user=user)
        
        # 测试获取报告列表
        response = api_client.get('/api/reports/test-runs/')
        assert response.status_code == 200
        print("   ✅ 报告列表接口正常")
        
        # 测试获取报告详情
        response = api_client.get(f'/api/reports/test-runs/{test_run.id}/')
        assert response.status_code == 200
        assert response.data['name'] == '报告测试执行'
        print("   ✅ 报告详情接口正常")
        
        # 测试统计接口
        response = api_client.get(f'/api/reports/test-runs/{test_run.id}/statistics/')
        assert response.status_code == 200
        assert 'total_tests' in response.data
        print("   ✅ 报告统计接口正常")
        
        print("   🎉 Reports单元测试通过！")
        return True
        
    except Exception as e:
        print(f"   ❌ Reports测试失败: {str(e)}")
        return False

def run_api_test_tests():
    """运行API Test相关的单元测试"""
    print("\n🔬 运行API Test单元测试")
    print("=" * 50)
    
    try:
        from django.test import Client
        from django.contrib.auth import get_user_model
        User = get_user_model()
        from api_test.models import ApiDefinition, ApiTestCase
        from rest_framework.test import APIClient
        
        # 创建测试数据
        user = User.objects.get_or_create(username='apitestuser')[0]
        
        api_def = ApiDefinition.objects.create(
            name='API测试定义',
            method='GET',
            url='http://example.com/api/test'
        )
        
        test_case = ApiTestCase.objects.create(
            name='API测试用例',
            api=api_def,
            expected_status_code=200
        )
        
        print("   ✅ API测试数据创建成功")
        
        # 测试API接口
        api_client = APIClient()
        api_client.force_authenticate(user=user)
        
        # 测试获取API定义列表
        response = api_client.get('/api-test/api-definitions/')
        assert response.status_code == 200
        print("   ✅ API定义列表接口正常")
        
        # 测试获取测试用例列表
        response = api_client.get('/api-test/api-test-cases/')
        assert response.status_code == 200
        print("   ✅ 测试用例列表接口正常")
        
        print("   🎉 API Test单元测试通过！")
        return True
        
    except Exception as e:
        print(f"   ❌ API Test测试失败: {str(e)}")
        return False

def main():
    """运行所有后端单元测试"""
    print("🚀 Django后端单元测试")
    print("=" * 60)
    
    results = []
    
    # 运行各模块测试
    results.append(("Mock Server", run_mock_server_tests()))
    results.append(("Reports", run_reports_tests()))
    results.append(("API Test", run_api_test_tests()))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📋 测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for module, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{module:20} {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个模块测试通过")
    success_rate = (passed / total) * 100
    print(f"成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 所有后端单元测试都通过了！")
    else:
        print(f"\n⚠️  有 {total - passed} 个模块测试失败")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试运行器出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
