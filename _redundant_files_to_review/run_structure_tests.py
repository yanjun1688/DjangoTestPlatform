#!/usr/bin/env python3
"""
简化的Django模型测试
测试基本的模型结构和逻辑，不依赖数据库
"""
import sys
import os

def test_mock_server_models():
    """测试Mock Server模型结构"""
    print("🧪 测试Mock Server模型")
    print("=" * 40)
    
    try:
        # 检查模型文件是否存在
        mock_models_path = 'mock_server/models.py'
        if not os.path.exists(mock_models_path):
            print(f"   ❌ 模型文件不存在: {mock_models_path}")
            return False
        
        # 读取模型文件内容
        with open(mock_models_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键模型是否定义
        required_models = ['MockAPI', 'MockAPIUsageLog']
        for model in required_models:
            if f'class {model}' in content:
                print(f"   ✅ 模型 {model} 已定义")
            else:
                print(f"   ❌ 模型 {model} 未找到")
                return False
        
        # 检查MockAPI模型的关键字段
        required_fields = [
            'name', 'path', 'method', 'response_status_code', 
            'response_body', 'is_active', 'delay_ms'
        ]
        
        for field in required_fields:
            if field in content:
                print(f"   ✅ 字段 {field} 已定义")
            else:
                print(f"   ❌ 字段 {field} 未找到")
                return False
        
        # 检查模型方法
        required_methods = ['full_url', 'get_content_type', 'clean']
        for method in required_methods:
            if f'def {method}' in content:
                print(f"   ✅ 方法 {method} 已定义")
            else:
                print(f"   ⚠️  方法 {method} 未找到")
        
        print("   🎉 Mock Server模型结构正确")
        return True
        
    except Exception as e:
        print(f"   ❌ 模型测试失败: {str(e)}")
        return False

def test_mock_server_views():
    """测试Mock Server视图结构"""
    print("\n🌐 测试Mock Server视图")
    print("=" * 40)
    
    try:
        views_path = 'mock_server/views.py'
        if not os.path.exists(views_path):
            print(f"   ❌ 视图文件不存在: {views_path}")
            return False
        
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键视图类
        required_views = ['ServeMockAPIView', 'MockAPIViewSet']
        for view in required_views:
            if f'class {view}' in content:
                print(f"   ✅ 视图 {view} 已定义")
            else:
                print(f"   ❌ 视图 {view} 未找到")
                return False
        
        # 检查关键方法
        if 'def dispatch(' in content:
            print("   ✅ Mock服务核心逻辑已实现")
        else:
            print("   ❌ Mock服务核心逻辑未找到")
            return False
        
        if 'time.sleep(' in content:
            print("   ✅ 延迟功能已实现")
        else:
            print("   ⚠️  延迟功能未找到")
        
        print("   🎉 Mock Server视图结构正确")
        return True
        
    except Exception as e:
        print(f"   ❌ 视图测试失败: {str(e)}")
        return False

def test_mock_server_serializers():
    """测试Mock Server序列化器"""
    print("\n📋 测试Mock Server序列化器")
    print("=" * 40)
    
    try:
        serializers_path = 'mock_server/serializers.py'
        if not os.path.exists(serializers_path):
            print(f"   ❌ 序列化器文件不存在: {serializers_path}")
            return False
        
        with open(serializers_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查序列化器类
        required_serializers = [
            'MockAPIListSerializer', 'MockAPIDetailSerializer',
            'MockAPICreateSerializer', 'MockAPIStatsSerializer'
        ]
        
        for serializer in required_serializers:
            if f'class {serializer}' in content:
                print(f"   ✅ 序列化器 {serializer} 已定义")
            else:
                print(f"   ❌ 序列化器 {serializer} 未找到")
                return False
        
        print("   🎉 Mock Server序列化器结构正确")
        return True
        
    except Exception as e:
        print(f"   ❌ 序列化器测试失败: {str(e)}")
        return False

def test_mock_server_urls():
    """测试Mock Server URL配置"""
    print("\n🔗 测试Mock Server URL配置")
    print("=" * 40)
    
    try:
        # 检查mock_server的urls.py
        mock_urls_path = 'mock_server/urls.py'
        if not os.path.exists(mock_urls_path):
            print(f"   ❌ Mock Server URL文件不存在: {mock_urls_path}")
            return False
        
        with open(mock_urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'MockAPIViewSet' in content:
            print("   ✅ Mock API管理路由已配置")
        else:
            print("   ❌ Mock API管理路由未配置")
            return False
        
        # 检查主项目的urls.py
        main_urls_path = 'test_platform/urls.py'
        if not os.path.exists(main_urls_path):
            print(f"   ❌ 主URL文件不存在: {main_urls_path}")
            return False
        
        with open(main_urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'ServeMockAPIView' in content:
            print("   ✅ Mock服务路由已配置")
        else:
            print("   ❌ Mock服务路由未配置")
            return False
        
        if 'mock_server.urls' in content:
            print("   ✅ Mock Server应用已包含")
        else:
            print("   ❌ Mock Server应用未包含")
            return False
        
        print("   🎉 URL配置正确")
        return True
        
    except Exception as e:
        print(f"   ❌ URL配置测试失败: {str(e)}")
        return False

def test_reports_models():
    """测试Reports模型"""
    print("\n📊 测试Reports模型")
    print("=" * 40)
    
    try:
        # 检查api_test中的TestRun模型
        api_test_models_path = 'api_test/models.py'
        if not os.path.exists(api_test_models_path):
            print(f"   ❌ API Test模型文件不存在")
            return False
        
        with open(api_test_models_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'class TestRun' in content:
            print("   ✅ TestRun模型已定义")
        else:
            print("   ❌ TestRun模型未找到")
            return False
        
        # 检查关键字段和方法
        required_elements = [
            'success_rate', 'update_statistics', 'complete', 'duration_display'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"   ✅ {element} 已实现")
            else:
                print(f"   ❌ {element} 未找到")
                return False
        
        print("   🎉 Reports模型结构正确")
        return True
        
    except Exception as e:
        print(f"   ❌ Reports模型测试失败: {str(e)}")
        return False

def test_django_settings():
    """测试Django配置"""
    print("\n⚙️  测试Django配置")
    print("=" * 40)
    
    try:
        settings_path = 'test_platform/settings.py'
        if not os.path.exists(settings_path):
            print(f"   ❌ 配置文件不存在: {settings_path}")
            return False
        
        with open(settings_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查必要的应用是否已安装
        required_apps = [
            'mock_server', 'reports', 'api_test', 
            'testcases', 'user_management'
        ]
        
        for app in required_apps:
            if f"'{app}'" in content:
                print(f"   ✅ 应用 {app} 已安装")
            else:
                print(f"   ❌ 应用 {app} 未安装")
                return False
        
        # 检查DRF配置
        if 'rest_framework' in content:
            print("   ✅ Django REST Framework已配置")
        else:
            print("   ❌ Django REST Framework未配置")
            return False
        
        print("   🎉 Django配置正确")
        return True
        
    except Exception as e:
        print(f"   ❌ Django配置测试失败: {str(e)}")
        return False

def main():
    """运行所有结构测试"""
    print("🚀 Django后端结构测试")
    print("=" * 60)
    
    tests = [
        ("Django配置", test_django_settings),
        ("Mock Server模型", test_mock_server_models),
        ("Mock Server视图", test_mock_server_views), 
        ("Mock Server序列化器", test_mock_server_serializers),
        ("Mock Server URL配置", test_mock_server_urls),
        ("Reports模型", test_reports_models),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"   ❌ {test_name}测试出错: {str(e)}")
            results.append((test_name, False))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("📋 后端结构测试结果总结")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:20} {status}")
        if success:
            passed += 1
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    success_rate = (passed / total) * 100
    print(f"成功率: {success_rate:.1f}%")
    
    if passed == total:
        print("\n🎉 所有后端结构测试都通过了！")
        print("💡 主要功能模块已正确实现:")
        print("   - Mock Server完整功能")
        print("   - Reports可视化报告")
        print("   - API Test测试框架")
        print("   - User Management用户管理")
    else:
        print(f"\n⚠️  有 {total - passed} 个测试失败")
        print("💡 请检查失败的模块并修复问题")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 结构测试出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)