#!/usr/bin/env python3
"""
完整的项目测试报告生成器
汇总前后端测试结果
"""
import subprocess
import sys
import os
from datetime import datetime

def run_test_script(script_path, description):
    """运行测试脚本并返回结果"""
    print(f"\n🔄 运行 {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=60)
        
        success = result.returncode == 0
        output = result.stdout if result.stdout else result.stderr
        
        print(output)
        
        return {
            'name': description,
            'success': success,
            'output': output,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"❌ {description} 超时")
        return {
            'name': description,
            'success': False,
            'output': f"{description} 超时",
            'return_code': -1
        }
    except Exception as e:
        print(f"❌ {description} 执行失败: {str(e)}")
        return {
            'name': description,
            'success': False,
            'output': str(e),
            'return_code': -2
        }

def generate_test_report():
    """生成完整的测试报告"""
    print("🚀 Django测试平台 - 完整功能测试报告")
    print("=" * 80)
    print(f"⏰ 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 测试脚本列表
    test_scripts = [
        ('run_structure_tests.py', '后端结构测试'),
        ('run_frontend_tests.py', '前端结构测试'),
    ]
    
    results = []
    
    # 运行所有测试
    for script, description in test_scripts:
        if os.path.exists(script):
            result = run_test_script(script, description)
            results.append(result)
        else:
            print(f"⚠️  测试脚本不存在: {script}")
            results.append({
                'name': description,
                'success': False,
                'output': f"测试脚本 {script} 不存在",
                'return_code': -3
            })
    
    # 生成总结报告
    print("\n" + "=" * 80)
    print("📊 测试结果总结")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - passed_tests
    
    print(f"📈 测试统计:")
    print(f"   总测试套件: {total_tests}")
    print(f"   通过套件:   {passed_tests}")
    print(f"   失败套件:   {failed_tests}")
    print(f"   成功率:     {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 详细结果:")
    for result in results:
        status = "✅ 通过" if result['success'] else "❌ 失败"
        print(f"   {result['name']:20} {status}")
    
    # 失败详情
    if failed_tests > 0:
        print(f"\n❌ 失败详情:")
        for result in results:
            if not result['success']:
                print(f"\n{result['name']}:")
                print(f"   返回码: {result['return_code']}")
                # 只显示输出的最后几行
                output_lines = result['output'].split('\n')[-10:]
                for line in output_lines:
                    if line.strip():
                        print(f"   {line}")
    
    # 功能模块检查
    print(f"\n🎯 功能模块状态:")
    
    modules = {
        'Mock Server': check_mock_server_files(),
        'Visual Reports': check_reports_files(),
        'API Testing': check_api_test_files(),
        'User Management': check_user_management_files(),
        'Frontend': check_frontend_files()
    }
    
    for module, status in modules.items():
        status_text = "✅ 已实现" if status else "❌ 缺失"
        print(f"   {module:20} {status_text}")
    
    # 总体评估
    all_modules_ok = all(modules.values())
    all_tests_passed = passed_tests == total_tests
    
    print(f"\n" + "=" * 80)
    
    if all_tests_passed and all_modules_ok:
        print("🎉 项目状态: 优秀")
        print("💚 所有核心功能已实现并通过测试")
        print("✨ 系统已准备就绪，可以进行部署和使用")
    elif passed_tests >= total_tests * 0.8:  # 80%以上通过
        print("✅ 项目状态: 良好") 
        print("💛 大部分功能正常，少数问题需要修复")
        print("🔧 建议解决失败的测试后再部署")
    else:
        print("⚠️  项目状态: 需要改进")
        print("💔 存在较多问题，建议优先修复核心功能")
        print("🔨 请检查失败的测试并修复相关问题")
    
    print("=" * 80)
    
    return all_tests_passed and all_modules_ok

def check_mock_server_files():
    """检查Mock Server相关文件"""
    required_files = [
        'mock_server/models.py',
        'mock_server/views.py',
        'mock_server/serializers.py',
        'mock_server/urls.py',
        'mock_server/admin.py',
        '../frontend/src/pages/MockServerPage.jsx'
    ]
    
    return all(os.path.exists(f) for f in required_files)

def check_reports_files():
    """检查Reports相关文件"""
    required_files = [
        'reports/models.py',
        'reports/views.py', 
        'reports/serializers.py',
        'reports/urls.py',
        '../frontend/src/pages/TestReportPage.jsx',
        '../frontend/src/pages/ReportListPage.jsx'
    ]
    
    return all(os.path.exists(f) for f in required_files)

def check_api_test_files():
    """检查API Test相关文件"""
    required_files = [
        'api_test/models.py',
        'api_test/views.py',
        'api_test/serializers.py',
        'api_test/urls.py',
        '../frontend/src/pages/ApiDefinitionPage.jsx'
    ]
    
    return all(os.path.exists(f) for f in required_files)

def check_user_management_files():
    """检查User Management相关文件"""
    required_files = [
        'user_management/models.py',
        'user_management/views.py',
        'user_management/urls.py',
        '../frontend/src/pages/UserManagementPage.jsx',
        '../frontend/src/pages/LoginPage.jsx'
    ]
    
    return all(os.path.exists(f) for f in required_files)

def check_frontend_files():
    """检查前端核心文件"""
    required_files = [
        '../frontend/package.json',
        '../frontend/src/App.jsx',
        '../frontend/src/main.jsx',
        '../frontend/src/pages/DashboardPage.jsx'
    ]
    
    return all(os.path.exists(f) for f in required_files)

def main():
    """主函数"""
    try:
        success = generate_test_report()
        
        print(f"\n💡 后续步骤建议:")
        if success:
            print("   1. 运行数据库迁移: python manage.py makemigrations && python manage.py migrate")
            print("   2. 创建超级用户: python manage.py createsuperuser")  
            print("   3. 启动开发服务器: python manage.py runserver")
            print("   4. 启动前端开发服务器: cd ../frontend && npm run dev")
            print("   5. 访问 http://localhost:5173 测试功能")
        else:
            print("   1. 检查并修复失败的测试")
            print("   2. 确保所有依赖已正确安装")
            print("   3. 重新运行测试确认修复")
        
        return success
        
    except Exception as e:
        print(f"❌ 测试报告生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
        sys.exit(1)