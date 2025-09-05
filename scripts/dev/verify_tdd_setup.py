#!/usr/bin/env python3
"""
TDD开发环境验证脚本

验证项目是否已正确配置用于测试驱动开发
"""

from pathlib import Path
import subprocess
import sys

def check_project_structure():
    """检查项目结构是否适合TDD开发"""
    print("🔍 检查项目结构...")
    
    project_root = Path(__file__).parent.parent.parent
    backend_root = project_root / "backend"
    
    # 必需的文件和目录
    required_items = [
        (backend_root / "manage.py", "Django管理脚本"),
        (backend_root / "requirements.txt", "依赖管理文件"),
        (backend_root / "run_tests.py", "统一测试管理器"),
        (backend_root / "tests", "集中式测试目录"),
        (backend_root / "tests" / "conftest.py", "pytest配置"),
        (project_root / "scripts" / "dev" / "quick-start.bat", "快速启动脚本"),
    ]
    
    all_good = True
    for item_path, description in required_items:
        if item_path.exists():
            print(f"  ✅ {description}: {item_path.name}")
        else:
            print(f"  ❌ 缺少 {description}: {item_path}")
            all_good = False
    
    # 检查是否还有冗余文件
    redundant_checks = [
        (backend_root / "create_test_data.py", "测试数据脚本"),
        (backend_root / "diagnose_mock_server.py", "诊断脚本"),
        (backend_root / ".env.template", "重复配置文件"),
        (backend_root / "testdata", "测试数据目录"),
    ]
    
    for item_path, description in redundant_checks:
        if item_path.exists():
            print(f"  ⚠️  仍存在冗余文件 {description}: {item_path}")
            all_good = False
    
    return all_good

def check_test_environment():
    """检查测试环境是否正常"""
    print("\n🧪 检查测试环境...")
    
    try:
        # 切换到backend目录
        backend_root = Path(__file__).parent.parent.parent / "backend"
        
        # 检查测试管理器是否可用
        result = subprocess.run(
            [sys.executable, "run_tests.py", "--list"],
            cwd=backend_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("  ✅ 测试管理器正常工作")
            return True
        else:
            print(f"  ❌ 测试管理器错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ 测试管理器响应超时")
        return False
    except Exception as e:
        print(f"  ❌ 测试环境检查失败: {e}")
        return False

def check_django_setup():
    """检查Django环境是否正常"""
    print("\n⚙️  检查Django环境...")
    
    try:
        backend_root = Path(__file__).parent.parent.parent / "backend"
        
        # 检查Django配置
        result = subprocess.run(
            [sys.executable, "manage.py", "check"],
            cwd=backend_root,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            print("  ✅ Django配置正常")
            return True
        else:
            print(f"  ❌ Django配置错误: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("  ❌ Django检查超时")
        return False
    except Exception as e:
        print(f"  ❌ Django环境检查失败: {e}")
        return False

def main():
    """主验证流程"""
    print("🎯 TDD开发环境验证")
    print("=" * 50)
    
    # 检查项目结构
    structure_ok = check_project_structure()
    
    # 检查测试环境
    test_env_ok = check_test_environment()
    
    # 检查Django环境
    django_ok = check_django_setup()
    
    print("\n" + "=" * 50)
    print("📋 验证结果：")
    
    if structure_ok and test_env_ok and django_ok:
        print("✅ 环境验证通过！项目已准备好进行TDD开发")
        print("\n🚀 开始TDD开发：")
        print("  1. 运行 scripts/dev/quick-start.bat 启动服务")
        print("  2. 使用 python run_tests.py 运行测试")
        print("  3. 遵循 红-绿-重构 循环")
        print("  4. 查看 docs/TDD_WORKFLOW.md 了解详细流程")
        return True
    else:
        print("❌ 环境验证失败，请检查以上问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)