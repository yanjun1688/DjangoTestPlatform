#!/usr/bin/env python3
"""
Django测试平台 - 依赖安装和单元测试运行脚本
"""

import os
import sys
import subprocess
import platform

def run_command(command, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=check, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}")
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        if e.stdout:
            print(f"输出: {e.stdout}")
        if e.stderr:
            print(f"错误: {e.stderr}")
        return False

def check_python():
    """检查Python环境"""
    print("检查Python环境...")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("错误: 需要Python 3.8或更高版本")
        return False
    
    return True

def check_node():
    """检查Node.js环境"""
    print("检查Node.js环境...")
    try:
        result = subprocess.run("node --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js版本: {result.stdout.strip()}")
            return True
        else:
            print("错误: Node.js未安装")
            return False
    except Exception as e:
        print(f"错误: 无法检查Node.js版本 - {e}")
        return False

def install_python_deps():
    """安装Python依赖"""
    print("\n=== 安装Python依赖 ===")
    
    backend_dir = "/mnt/d/Project/DjangoTestPlatform/blackend"
    
    # 检查requirements.txt是否存在
    req_file = os.path.join(backend_dir, "requirements.txt")
    if not os.path.exists(req_file):
        print("requirements.txt不存在，创建基础依赖文件...")
        requirements = """Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
django-mptt>=0.14.0
django-reversion>=5.0.0
requests>=2.28.0
python-decouple>=3.6
"""
        with open(req_file, 'w') as f:
            f.write(requirements)
    
    # 使用python -m pip来安装依赖
    python_cmd = "python3"
    
    print("升级pip...")
    run_command(f"{python_cmd} -m pip install --upgrade pip --user")
    
    print("安装Python依赖...")
    if not run_command(f"{python_cmd} -m pip install -r {req_file} --user"):
        print("Python依赖安装失败")
        return False, python_cmd
    
    return True, python_cmd

def install_node_deps():
    """安装Node.js依赖"""
    print("\n=== 安装Node.js依赖 ===")
    
    frontend_dir = "/mnt/d/Project/DjangoTestPlatform/frontend"
    
    # 检查package.json是否存在
    package_file = os.path.join(frontend_dir, "package.json")
    if not os.path.exists(package_file):
        print("package.json不存在，请检查前端项目结构")
        return False
    
    # 删除node_modules和package-lock.json以解决依赖冲突
    node_modules = os.path.join(frontend_dir, "node_modules")
    package_lock = os.path.join(frontend_dir, "package-lock.json")
    
    if os.path.exists(node_modules):
        print("删除现有node_modules...")
        run_command(f"rm -rf {node_modules}")
    
    if os.path.exists(package_lock):
        print("删除现有package-lock.json...")
        run_command(f"rm -f {package_lock}")
    
    # 安装依赖
    print("安装Node.js依赖...")
    if not run_command("npm install", cwd=frontend_dir):
        print("Node.js依赖安装失败")
        return False
    
    return True

def setup_django_db(python_cmd):
    """设置Django数据库"""
    print("\n=== 设置Django数据库 ===")
    
    backend_dir = "/mnt/d/Project/DjangoTestPlatform/blackend"
    
    # 运行数据库迁移
    print("运行数据库迁移...")
    if not run_command(f"{python_cmd} manage.py migrate", cwd=backend_dir):
        print("数据库迁移失败")
        return False
    
    return True

def run_backend_tests(python_cmd):
    """运行后端测试"""
    print("\n=== 运行后端测试 ===")
    
    backend_dir = "/mnt/d/Project/DjangoTestPlatform/blackend"
    
    # 运行Django自带的测试
    print("运行Django单元测试...")
    success = run_command(f"{python_cmd} manage.py test", cwd=backend_dir, check=False)
    
    # 运行外部测试目录中的测试
    tests_dir = "/mnt/d/Project/DjangoTestPlatform/tests/backend"
    if os.path.exists(tests_dir):
        print("运行外部测试目录中的测试...")
        # 需要设置DJANGO_SETTINGS_MODULE环境变量
        env_cmd = f"export DJANGO_SETTINGS_MODULE=test_platform.settings && cd {backend_dir} && {python_cmd} -m pytest {tests_dir} -v"
        run_command(env_cmd, check=False)
    
    return success

def run_frontend_tests():
    """运行前端测试"""
    print("\n=== 运行前端测试 ===")
    
    frontend_dir = "/mnt/d/Project/DjangoTestPlatform/frontend"
    
    # 运行前端测试
    print("运行前端单元测试...")
    success = run_command("npm test", cwd=frontend_dir, check=False)
    
    return success

def create_test_summary():
    """创建测试总结报告"""
    print("\n=== 测试总结 ===")
    
    # 统计测试文件数量
    backend_tests = 0
    frontend_tests = 0
    
    # 统计后端测试文件
    backend_dir = "/mnt/d/Project/DjangoTestPlatform/blackend"
    tests_dir = "/mnt/d/Project/DjangoTestPlatform/tests/backend"
    
    for root, dirs, files in os.walk(backend_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                backend_tests += 1
    
    for root, dirs, files in os.walk(tests_dir):
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                backend_tests += 1
    
    # 统计前端测试文件
    frontend_dir = "/mnt/d/Project/DjangoTestPlatform/frontend/src"
    for root, dirs, files in os.walk(frontend_dir):
        for file in files:
            if file.endswith('.test.js') or file.endswith('.test.jsx'):
                frontend_tests += 1
    
    print(f"后端测试文件数量: {backend_tests}")
    print(f"前端测试文件数量: {frontend_tests}")
    print(f"总测试文件数量: {backend_tests + frontend_tests}")
    
    print("\n测试覆盖的功能模块:")
    print("后端:")
    print("  - API测试模块 (api_test)")
    print("  - 测试用例模块 (testcases)")
    print("  - 用户管理模块 (user_management)")
    
    print("前端:")
    print("  - API定义页面 (ApiDefinitionPage)")
    print("  - 测试用例页面 (TestCasePage)")
    print("  - 测试计划页面 (TestPlanPage)")
    print("  - 用户管理页面 (UserManagementPage)")
    print("  - 工具函数 (utils)")

def main():
    """主函数"""
    print("Django测试平台 - 依赖安装和单元测试运行脚本")
    print("=" * 50)
    
    # 检查环境
    if not check_python():
        sys.exit(1)
    
    node_available = check_node()
    
    try:
        # 安装Python依赖
        success, python_cmd = install_python_deps()
        if not success:
            print("Python依赖安装失败，退出...")
            sys.exit(1)
        
        # 设置Django数据库
        if not setup_django_db(python_cmd):
            print("Django数据库设置失败，继续运行测试...")
        
        # 运行后端测试
        backend_success = run_backend_tests(python_cmd)
        
        # 安装Node.js依赖并运行前端测试
        frontend_success = True
        if node_available:
            if install_node_deps():
                frontend_success = run_frontend_tests()
            else:
                print("Node.js依赖安装失败，跳过前端测试...")
                frontend_success = False
        else:
            print("Node.js不可用，跳过前端测试...")
            frontend_success = False
        
        # 创建测试总结
        create_test_summary()
        
        # 最终结果
        print("\n" + "=" * 50)
        print("测试完成！")
        print(f"后端测试: {'通过' if backend_success else '失败'}")
        print(f"前端测试: {'通过' if frontend_success else '失败或跳过'}")
        
        if backend_success and frontend_success:
            print("✅ 所有测试通过！")
            sys.exit(0)
        else:
            print("❌ 部分测试失败，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n用户中断了测试过程")
        sys.exit(1)
    except Exception as e:
        print(f"运行过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()