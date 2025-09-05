#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查脚本 - 适配重构后的项目结构
检查Django项目运行所需的环境和依赖
"""
import os
import sys
import subprocess
import platform
import importlib
from pathlib import Path

class Colors:
    """颜色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class EnvironmentChecker:
    """环境检查器"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.success_items = []
    
    def print_colored(self, message, color=Colors.END):
        """彩色输出"""
        print(f"{color}{message}{Colors.END}")
    
    def check_python_version(self):
        """检查Python版本"""
        self.print_colored("🐍 检查Python版本...", Colors.CYAN)
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version.major == 3 and version.minor >= 8:
            self.print_colored(f"  ✅ Python版本: {version_str} (支持)", Colors.GREEN)
            self.success_items.append(f"Python {version_str}")
        elif version.major == 3 and version.minor >= 6:
            self.print_colored(f"  ⚠️  Python版本: {version_str} (可用但建议升级到3.8+)", Colors.YELLOW)
            self.warnings.append(f"Python版本 {version_str} 偏低，建议升级到3.8+")
        else:
            self.print_colored(f"  ❌ Python版本: {version_str} (不支持，需要3.6+)", Colors.RED)
            self.issues.append(f"Python版本 {version_str} 不支持")
    
    def check_pip(self):
        """检查pip"""
        self.print_colored("📦 检查pip...", Colors.CYAN)
        
        try:
            import pip
            pip_version = pip.__version__
            self.print_colored(f"  ✅ pip版本: {pip_version}", Colors.GREEN)
            self.success_items.append(f"pip {pip_version}")
        except ImportError:
            try:
                result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    pip_info = result.stdout.strip()
                    self.print_colored(f"  ✅ {pip_info}", Colors.GREEN)
                    self.success_items.append("pip")
                else:
                    self.print_colored("  ❌ pip未安装", Colors.RED)
                    self.issues.append("pip未安装")
            except Exception as e:
                self.print_colored(f"  ❌ pip检查失败: {e}", Colors.RED)
                self.issues.append("pip检查失败")
    
    def check_django_project(self):
        """检查Django项目（重构后的结构）"""
        self.print_colored("🎯 检查Django项目结构...", Colors.CYAN)
        
        # 检查manage.py（在backend目录中）
        manage_path = Path('backend/manage.py')
        if manage_path.exists():
            self.print_colored("  ✅ manage.py 存在", Colors.GREEN)
            self.success_items.append("manage.py")
        else:
            self.print_colored("  ❌ manage.py 不存在", Colors.RED)
            self.issues.append("manage.py不存在，请确保在项目根目录")
        
        # 检查settings.py（在backend/test_platform目录中）
        settings_path = Path('backend/test_platform/settings.py')
        if settings_path.exists():
            self.print_colored("  ✅ settings.py 存在", Colors.GREEN)
            self.success_items.append("settings.py")
        else:
            self.print_colored("  ❌ settings.py 不存在", Colors.RED)
            self.issues.append("settings.py不存在")
        
        # 检查requirements.txt（在backend目录中）
        requirements_path = Path('backend/requirements.txt')
        if requirements_path.exists():
            self.print_colored("  ✅ requirements.txt 存在", Colors.GREEN)
            self.success_items.append("requirements.txt")
        else:
            self.print_colored("  ⚠️  requirements.txt 不存在", Colors.YELLOW)
            self.warnings.append("requirements.txt不存在")
    
    def check_virtual_environment(self):
        """检查虚拟环境"""
        self.print_colored("🏠 检查虚拟环境...", Colors.CYAN)
        
        # 检查是否在虚拟环境中
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if in_venv:
            self.print_colored("  ✅ 当前在虚拟环境中", Colors.GREEN)
            self.success_items.append("虚拟环境激活")
        else:
            # 检查是否存在虚拟环境目录
            venv_dirs = ['backend/.venv', 'backend/venv', '.venv', 'venv', 'env']
            venv_found = False
            
            for venv_dir in venv_dirs:
                if os.path.exists(venv_dir):
                    self.print_colored(f"  ⚠️  找到虚拟环境目录 {venv_dir}，但未激活", Colors.YELLOW)
                    self.warnings.append(f"虚拟环境 {venv_dir} 存在但未激活")
                    venv_found = True
                    break
            
            if not venv_found:
                self.print_colored("  ⚠️  未使用虚拟环境，建议创建虚拟环境", Colors.YELLOW)
                self.warnings.append("建议使用虚拟环境")
    
    def check_required_packages(self):
        """检查必需的Python包"""
        self.print_colored("📚 检查必需的Python包...", Colors.CYAN)
        
        required_packages = [
            ('django', 'Django'),
            ('rest_framework', 'Django REST Framework'),
            ('corsheaders', 'django-cors-headers'),
            ('mptt', 'django-mptt'),
            ('reversion', 'django-reversion'),
            ('requests', 'requests'),
            ('dotenv', 'python-dotenv'),
        ]
        
        for package_name, display_name in required_packages:
            try:
                module = importlib.import_module(package_name)
                version = getattr(module, '__version__', 'unknown')
                self.print_colored(f"  ✅ {display_name}: {version}", Colors.GREEN)
                self.success_items.append(f"{display_name} {version}")
            except ImportError:
                self.print_colored(f"  ❌ {display_name} 未安装", Colors.RED)
                self.issues.append(f"{display_name}未安装")
    
    def check_database(self):
        """检查数据库连接"""
        self.print_colored("🗄️  检查数据库设置...", Colors.CYAN)
        
        try:
            # 添加backend目录到Python路径
            backend_path = os.path.abspath('backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
            import django
            django.setup()
            
            from django.conf import settings
            from django.db import connection
            
            db_engine = settings.DATABASES['default']['ENGINE']
            if 'sqlite3' in db_engine:
                self.print_colored("  ✅ 使用SQLite数据库", Colors.GREEN)
                self.success_items.append("SQLite数据库")
            elif 'postgresql' in db_engine:
                self.print_colored("  ✅ 使用PostgreSQL数据库", Colors.GREEN)
                self.success_items.append("PostgreSQL数据库")
            else:
                self.print_colored(f"  ℹ️  数据库引擎: {db_engine}", Colors.BLUE)
            
            # 尝试连接数据库
            connection.ensure_connection()
            self.print_colored("  ✅ 数据库连接正常", Colors.GREEN)
            self.success_items.append("数据库连接")
            
        except Exception as e:
            self.print_colored(f"  ⚠️  数据库检查失败: {e}", Colors.YELLOW)
            self.warnings.append(f"数据库检查失败: {e}")
    
    def check_system_info(self):
        """检查系统信息"""
        self.print_colored("💻 系统信息...", Colors.CYAN)
        
        system_info = {
            "操作系统": platform.system(),
            "系统版本": platform.version(),
            "架构": platform.machine(),
            "处理器": platform.processor() or "Unknown",
        }
        
        for key, value in system_info.items():
            if value:
                self.print_colored(f"  ℹ️  {key}: {value}", Colors.BLUE)
    
    def check_restructured_directories(self):
        """检查重构后的目录结构"""
        self.print_colored("📁 检查重构后的目录结构...", Colors.CYAN)
        
        expected_dirs = [
            'backend',
            'frontend', 
            'scripts/dev',
            'scripts/test',
            'scripts/utils',
            'docs',
            'deployment',
            'data'
        ]
        
        for dir_path in expected_dirs:
            if os.path.exists(dir_path):
                self.print_colored(f"  ✅ {dir_path}/ 存在", Colors.GREEN)
                self.success_items.append(f"{dir_path}目录")
            else:
                self.print_colored(f"  ⚠️  {dir_path}/ 不存在", Colors.YELLOW)
                self.warnings.append(f"{dir_path}目录不存在")
    
    def generate_recommendations(self):
        """生成建议"""
        if self.issues or self.warnings:
            self.print_colored("\n📋 建议和解决方案:", Colors.BOLD)
            
            if self.issues:
                self.print_colored("\n❌ 必须解决的问题:", Colors.RED)
                for issue in self.issues:
                    self.print_colored(f"  • {issue}", Colors.RED)
                
                self.print_colored("\n解决方案:", Colors.YELLOW)
                if any("Python版本" in issue for issue in self.issues):
                    self.print_colored("  • 升级Python到3.8或更高版本", Colors.YELLOW)
                if any("pip" in issue for issue in self.issues):
                    self.print_colored("  • 安装pip: python -m ensurepip --upgrade", Colors.YELLOW)
                if any("未安装" in issue for issue in self.issues):
                    self.print_colored("  • 安装依赖: cd backend && pip install -r requirements.txt", Colors.YELLOW)
            
            if self.warnings:
                self.print_colored("\n⚠️  建议改进:", Colors.YELLOW)
                for warning in self.warnings:
                    self.print_colored(f"  • {warning}", Colors.YELLOW)
                
                if any("虚拟环境" in warning for warning in self.warnings):
                    self.print_colored("\n创建和激活虚拟环境:", Colors.CYAN)
                    self.print_colored("  cd backend && python -m venv .venv", Colors.CYAN)
                    if platform.system() == "Windows":
                        self.print_colored("  backend\\.venv\\Scripts\\activate", Colors.CYAN)
                    else:
                        self.print_colored("  source backend/.venv/bin/activate", Colors.CYAN)
        else:
            self.print_colored("\n🎉 所有检查通过！环境配置正常。", Colors.GREEN)
    
    def run_all_checks(self):
        """运行所有检查"""
        self.print_colored("=" * 60, Colors.BOLD)
        self.print_colored("🔍 Django项目环境检查 - 重构版本", Colors.BOLD)
        self.print_colored("=" * 60, Colors.BOLD)
        
        self.check_system_info()
        print()
        self.check_python_version()
        print()
        self.check_pip()
        print()
        self.check_virtual_environment()
        print()
        self.check_django_project()
        print()
        self.check_restructured_directories()
        print()
        self.check_required_packages()
        print()
        self.check_database()
        print()
        
        # 显示汇总
        self.print_colored("=" * 60, Colors.BOLD)
        self.print_colored("📊 检查汇总", Colors.BOLD)
        self.print_colored("=" * 60, Colors.BOLD)
        
        if self.success_items:
            self.print_colored(f"✅ 正常项目 ({len(self.success_items)}):", Colors.GREEN)
            for item in self.success_items[:5]:  # 只显示前5个
                self.print_colored(f"  • {item}", Colors.GREEN)
            if len(self.success_items) > 5:
                self.print_colored(f"  ... 以及其他 {len(self.success_items) - 5} 项", Colors.GREEN)
        
        if self.issues:
            self.print_colored(f"\n❌ 问题项目 ({len(self.issues)}):", Colors.RED)
            for issue in self.issues:
                self.print_colored(f"  • {issue}", Colors.RED)
        
        if self.warnings:
            self.print_colored(f"\n⚠️  警告项目 ({len(self.warnings)}):", Colors.YELLOW)
            for warning in self.warnings:
                self.print_colored(f"  • {warning}", Colors.YELLOW)
        
        self.generate_recommendations()
        
        # 返回状态
        if self.issues:
            return False
        elif self.warnings:
            return True  # 有警告但可以运行
        else:
            return True

def main():
    """主函数"""
    checker = EnvironmentChecker()
    success = checker.run_all_checks()
    
    print("\n" + "=" * 60)
    if success and not checker.issues:
        checker.print_colored("🚀 环境检查完成，可以运行Django项目！", Colors.GREEN)
        checker.print_colored("💡 项目重构已完成，使用新的启动方式:", Colors.CYAN)
        checker.print_colored("   后端: scripts/dev/start-backend.sh 或 scripts/dev/start-backend.bat", Colors.CYAN)
        checker.print_colored("   前端: scripts/dev/start-frontend.sh 或 scripts/dev/start-frontend.bat", Colors.CYAN)
        return 0
    elif not checker.issues:
        checker.print_colored("⚠️  环境检查完成，有一些建议改进的地方", Colors.YELLOW)
        return 0
    else:
        checker.print_colored("❌ 环境检查发现问题，请先解决后再运行项目", Colors.RED)
        return 1

if __name__ == '__main__':
    sys.exit(main())