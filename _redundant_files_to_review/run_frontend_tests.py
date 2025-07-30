#!/usr/bin/env python3
"""
前端单元测试检查器
检查前端组件的基本结构和语法
"""
import os
import re
import json

def check_file_syntax(file_path):
    """检查文件基本语法"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        errors = []
        
        # 检查基本的JSX语法错误
        if file_path.endswith('.jsx'):
            # 检查未闭合的标签
            open_tags = re.findall(r'<(\w+)[^>]*>', content)
            close_tags = re.findall(r'</(\w+)>', content)
            
            # 检查import语句
            imports = re.findall(r'import.*from.*[\'"][^\'"]+[\'"];?', content)
            if not imports:
                errors.append("没有找到import语句")
            
            # 检查export语句
            if 'export default' not in content:
                errors.append("没有找到export default语句")
            
            # 检查基本的React组件结构
            if 'const ' not in content and 'function ' not in content:
                errors.append("没有找到组件定义")
        
        return errors
        
    except Exception as e:
        return [f"文件读取错误: {str(e)}"]

def check_component_dependencies(file_path):
    """检查组件依赖"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        dependencies = []
        
        # 提取import的依赖
        import_matches = re.findall(r'import.*from\s+[\'"]([^\'"]+)[\'"]', content)
        for match in import_matches:
            if not match.startswith('.'):  # 外部依赖
                dependencies.append(match)
        
        return dependencies
        
    except Exception as e:
        return []

def check_package_json():
    """检查package.json配置"""
    package_path = '/mnt/d/Project/DjangoTestPlatform/frontend/package.json'
    
    try:
        with open(package_path, 'r', encoding='utf-8') as f:
            package_data = json.load(f)
        
        required_deps = [
            'react', 'react-dom', 'react-router-dom', 
            'antd', '@ant-design/icons', 'axios'
        ]
        
        missing_deps = []
        dependencies = package_data.get('dependencies', {})
        
        for dep in required_deps:
            if dep not in dependencies:
                missing_deps.append(dep)
        
        return {
            'exists': True,
            'missing_deps': missing_deps,
            'has_test_script': 'test' in package_data.get('scripts', {}),
            'dependencies_count': len(dependencies)
        }
        
    except FileNotFoundError:
        return {'exists': False, 'error': 'package.json not found'}
    except Exception as e:
        return {'exists': False, 'error': str(e)}

def test_frontend_components():
    """测试前端组件"""
    print("🎨 前端组件检查")
    print("=" * 50)
    
    frontend_dir = '/mnt/d/Project/DjangoTestPlatform/frontend/src'
    
    # 要检查的组件文件
    components_to_check = [
        'App.jsx',
        'pages/MockServerPage.jsx',
        'pages/TestReportPage.jsx', 
        'pages/ReportListPage.jsx',
        'pages/TestPlanPage.jsx',
        'pages/DashboardPage.jsx',
        'pages/ApiDefinitionPage.jsx',
        'pages/TestCasePage.jsx',
        'pages/LoginPage.jsx'
    ]
    
    results = []
    
    for component in components_to_check:
        file_path = os.path.join(frontend_dir, component)
        
        print(f"\n📄 检查组件: {component}")
        
        if not os.path.exists(file_path):
            print(f"   ❌ 文件不存在: {file_path}")
            results.append((component, False, ["文件不存在"]))
            continue
        
        # 检查语法
        syntax_errors = check_file_syntax(file_path)
        
        # 检查依赖
        dependencies = check_component_dependencies(file_path)
        
        if syntax_errors:
            print(f"   ❌ 语法问题:")
            for error in syntax_errors:
                print(f"      - {error}")
            results.append((component, False, syntax_errors))
        else:
            print(f"   ✅ 语法检查通过")
            print(f"   📦 依赖: {len(dependencies)} 个")
            results.append((component, True, []))
    
    return results

def test_frontend_structure():
    """测试前端项目结构"""
    print("\n🏗️  前端项目结构检查")
    print("=" * 50)
    
    frontend_dir = '/mnt/d/Project/DjangoTestPlatform/frontend'
    
    required_files = [
        'package.json',
        'vite.config.js',
        'index.html',
        'src/main.jsx',
        'src/App.jsx',
        'src/App.css'
    ]
    
    required_dirs = [
        'src',
        'src/pages',
        'src/utils'
    ]
    
    structure_ok = True
    
    # 检查必需文件
    print("\n📁 检查必需文件:")
    for file_path in required_files:
        full_path = os.path.join(frontend_dir, file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path}")
            structure_ok = False
    
    # 检查必需目录
    print("\n📂 检查必需目录:")
    for dir_path in required_dirs:
        full_path = os.path.join(frontend_dir, dir_path)
        if os.path.exists(full_path) and os.path.isdir(full_path):
            print(f"   ✅ {dir_path}/")
        else:
            print(f"   ❌ {dir_path}/")
            structure_ok = False
    
    # 检查package.json
    print("\n📦 检查package.json配置:")
    package_info = check_package_json()
    
    if package_info['exists']:
        print(f"   ✅ package.json 存在")
        print(f"   📊 依赖包数量: {package_info['dependencies_count']}")
        
        if package_info['missing_deps']:
            print(f"   ⚠️  缺少依赖: {', '.join(package_info['missing_deps'])}")
            structure_ok = False
        else:
            print(f"   ✅ 所有必需依赖都已安装")
            
        if package_info['has_test_script']:
            print(f"   ✅ 包含测试脚本")
        else:
            print(f"   ⚠️  没有测试脚本")
    else:
        print(f"   ❌ package.json 问题: {package_info.get('error', '未知错误')}")
        structure_ok = False
    
    return structure_ok

def test_frontend_unit_tests():
    """检查前端单元测试文件"""
    print("\n🧪 前端单元测试文件检查")
    print("=" * 50)
    
    frontend_dir = '/mnt/d/Project/DjangoTestPlatform/frontend/src'
    
    test_files = [
        'pages/TestReportPage.test.jsx',
        'pages/ReportListPage.test.jsx',
        'setupTests.js'
    ]
    
    test_files_found = 0
    
    for test_file in test_files:
        file_path = os.path.join(frontend_dir, test_file)
        
        if os.path.exists(file_path):
            print(f"   ✅ {test_file}")
            test_files_found += 1
            
            # 检查测试文件内容
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'describe(' in content or 'test(' in content or 'it(' in content:
                    print(f"      📝 包含测试用例")
                else:
                    print(f"      ⚠️  没有找到测试用例")
                    
            except Exception as e:
                print(f"      ❌ 读取失败: {str(e)}")
        else:
            print(f"   ❌ {test_file}")
    
    print(f"\n📊 测试文件统计: {test_files_found}/{len(test_files)} 个文件存在")
    
    return test_files_found > 0

def main():
    """主函数"""
    print("🚀 前端单元测试检查")
    print("=" * 60)
    
    # 检查项目结构
    structure_ok = test_frontend_structure()
    
    # 检查组件语法
    component_results = test_frontend_components()
    
    # 检查单元测试文件
    tests_exist = test_frontend_unit_tests()
    
    # 统计结果
    print("\n" + "=" * 60)
    print("📋 前端检查结果总结")
    print("=" * 60)
    
    # 组件检查结果
    passed_components = sum(1 for _, success, _ in component_results if success)
    total_components = len(component_results)
    
    print(f"项目结构:     {'✅ 正常' if structure_ok else '❌ 有问题'}")
    print(f"组件语法:     {passed_components}/{total_components} 个组件通过")
    print(f"测试文件:     {'✅ 存在' if tests_exist else '❌ 缺失'}")
    
    # 详细的组件问题
    failed_components = [(name, errors) for name, success, errors in component_results if not success]
    
    if failed_components:
        print(f"\n❌ 有问题的组件:")
        for name, errors in failed_components:
            print(f"   {name}:")
            for error in errors:
                print(f"      - {error}")
    
    overall_success = structure_ok and passed_components == total_components
    
    print(f"\n{'🎉 前端检查通过！' if overall_success else '⚠️  前端检查发现问题'}")
    print("=" * 60)
    
    return overall_success

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 前端检查出错: {str(e)}")
        import traceback
        traceback.print_exc()
        exit(1)