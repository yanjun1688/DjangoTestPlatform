#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Django测试平台项目重构脚本
自动化执行项目目录重组和文件迁移
"""
import os
import shutil
import sys
from pathlib import Path
import subprocess
import json

class Colors:
    """彩色输出"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class ProjectRestructurer:
    """项目重构器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_restructure"
        self.dry_run = False
        
    def print_colored(self, message, color=Colors.END):
        """彩色输出"""
        print(f"{color}{message}{Colors.END}")
    
    def check_git_status(self):
        """检查Git状态"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, cwd=self.project_root)
            if result.stdout.strip():
                self.print_colored("⚠️  检测到未提交的Git更改", Colors.YELLOW)
                self.print_colored("建议先提交或储藏当前更改", Colors.YELLOW)
                if input("是否继续？(y/N): ").lower() != 'y':
                    return False
        except FileNotFoundError:
            self.print_colored("ℹ️  未检测到Git仓库", Colors.BLUE)
        return True
    
    def create_backup(self):
        """创建备份"""
        self.print_colored("📦 创建项目备份...", Colors.CYAN)
        
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # 创建备份，排除一些不必要的目录
        exclude_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', 'venv', '.venv'}
        
        self.backup_dir.mkdir()
        
        for item in self.project_root.iterdir():
            if item.name not in exclude_dirs and item != self.backup_dir:
                if item.is_dir():
                    shutil.copytree(item, self.backup_dir / item.name, 
                                  ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
                else:
                    shutil.copy2(item, self.backup_dir)
        
        self.print_colored(f"✅ 备份已创建: {self.backup_dir}", Colors.GREEN)
    
    def create_new_directories(self):
        """创建新的目录结构"""
        self.print_colored("📁 创建新目录结构...", Colors.CYAN)
        
        new_dirs = [
            # 文档目录
            "docs/api",
            "docs/deployment", 
            "docs/development",
            "docs/user-guide",
            
            # 脚本目录
            "scripts/dev",
            "scripts/test",
            "scripts/build", 
            "scripts/utils",
            
            # 后端应用目录
            "backend/apps",
            "backend/config/settings",
            "backend/tests/integration",
            "backend/tests/fixtures",
            "backend/tests/utils",
            "backend/static",
            "backend/media",
            "backend/logs",
            "backend/locale",
            
            # 前端重组目录
            "frontend/src/components/common",
            "frontend/src/components/layout",
            "frontend/src/components/business",
            "frontend/src/pages/auth",
            "frontend/src/pages/dashboard",
            "frontend/src/pages/test-management", 
            "frontend/src/pages/reports",
            "frontend/src/pages/settings",
            "frontend/src/hooks",
            "frontend/src/services/api",
            "frontend/src/services/utils",
            "frontend/src/store/auth",
            "frontend/src/store/testcase",
            "frontend/src/styles/themes",
            "frontend/src/tests/components",
            "frontend/src/tests/pages",
            "frontend/src/tests/utils",
            
            # 部署目录
            "deployment/docker",
            "deployment/nginx",
            "deployment/systemd",
            "deployment/kubernetes",
            
            # 数据目录
            "data/fixtures",
            "data/backups",
            "data/uploads",
            
            # 临时目录
            "temp/logs",
            "temp/cache", 
            "temp/reports",
        ]
        
        for dir_path in new_dirs:
            full_path = self.project_root / dir_path
            if not self.dry_run:
                full_path.mkdir(parents=True, exist_ok=True)
            self.print_colored(f"  ✓ {dir_path}", Colors.GREEN)
    
    def rename_backend_directory(self):
        """重命名后端目录"""
        self.print_colored("🔄 重命名后端目录...", Colors.CYAN)
        
        old_backend = self.project_root / "blackend"
        new_backend = self.project_root / "backend"
        
        if old_backend.exists() and not new_backend.exists():
            if not self.dry_run:
                old_backend.rename(new_backend)
            self.print_colored("  ✓ blackend → backend", Colors.GREEN)
        elif new_backend.exists():
            self.print_colored("  ℹ️  backend目录已存在", Colors.BLUE)
        else:
            self.print_colored("  ⚠️  未找到blackend目录", Colors.YELLOW)
    
    def reorganize_scripts(self):
        """重组脚本文件"""
        self.print_colored("📝 重组脚本文件...", Colors.CYAN)
        
        # 脚本文件映射（注意：backend目录可能还叫blackend）
        backend_dir = "backend" if (self.project_root / "backend").exists() else "blackend"
        
        script_mappings = [
            # 开发脚本
            (f"{backend_dir}/start_backend.sh", "scripts/dev/start-backend.sh"),
            ("frontend/start_frontend.sh", "scripts/dev/start-frontend.sh"),
            ("scripts/start_backend.bat", "scripts/dev/start-backend.bat"),
            ("scripts/start_frontend.bat", "scripts/dev/start-frontend.bat"),
            
            # 测试脚本
            (f"{backend_dir}/run_all_tests.py", "scripts/test/run-all-tests.py"),
            ("scripts/run_tests.sh", "scripts/test/run-tests.sh"),
            
            # 工具脚本
            (f"{backend_dir}/check_environment.py", "scripts/utils/check-environment.py"),
            ("scripts/check_environment.sh", "scripts/utils/check-environment.sh"),
            ("scripts/check_environment.bat", "scripts/utils/check-environment.bat"),
            ("scripts/setup_wsl_env.sh", "scripts/utils/setup-wsl-env.sh"),
            ("scripts/install_commands.sh", "scripts/build/install-commands.sh"),
            ("scripts/setup_and_test.py", "scripts/build/setup-and-test.py"),
        ]
        
        for src, dst in script_mappings:
            src_path = self.project_root / src
            dst_path = self.project_root / dst
            
            if src_path.exists():
                if not self.dry_run:
                    dst_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(src_path), str(dst_path))
                self.print_colored(f"  ✓ {src} → {dst}", Colors.GREEN)
            else:
                self.print_colored(f"  ⚠️  未找到: {src}", Colors.YELLOW)
    
    def reorganize_backend_structure(self):
        """重组后端结构"""
        self.print_colored("🔧 重组后端结构...", Colors.CYAN)
        
        backend_dir = self.project_root / "backend"
        if not backend_dir.exists():
            self.print_colored("  ❌ backend目录不存在", Colors.RED)
            return
        
        # 移动Django项目配置
        old_config = backend_dir / "test_platform"
        new_config = backend_dir / "config"
        
        if old_config.exists() and not new_config.exists():
            if not self.dry_run:
                old_config.rename(new_config)
            self.print_colored("  ✓ test_platform → config", Colors.GREEN)
        
        # 移动应用到apps目录
        apps_to_move = [
            "api_test", "testcases", "user_management", "reports", 
            "mock_server", "comments", "environments"
        ]
        
        apps_dir = backend_dir / "apps"
        if not self.dry_run:
            apps_dir.mkdir(exist_ok=True)
        
        for app_name in apps_to_move:
            app_path = backend_dir / app_name
            target_path = apps_dir / app_name
            
            if app_path.exists() and not target_path.exists():
                if not self.dry_run:
                    shutil.move(str(app_path), str(target_path))
                self.print_colored(f"  ✓ {app_name} → apps/{app_name}", Colors.GREEN)
    
    def create_environment_templates(self):
        """创建环境变量模板"""
        self.print_colored("🌐 创建环境配置模板...", Colors.CYAN)
        
        # 后端环境变量模板
        backend_env_template = '''# Django后端环境变量配置模板
# 复制此文件为.env并根据实际情况修改

# Django基础配置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,testserver

# 数据库配置
DATABASE_ENGINE=django.db.backends.sqlite3
DATABASE_NAME=db.sqlite3
# PostgreSQL配置（如果使用）
# DATABASE_ENGINE=django.db.backends.postgresql
# DATABASE_NAME=test_platform_db
# DATABASE_USER=postgres
# DATABASE_PASSWORD=your-password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432

# CORS配置
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# 邮件配置（可选）
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password

# Redis配置（如果使用）
# REDIS_URL=redis://localhost:6379/0

# 日志级别
LOG_LEVEL=INFO

# 文件上传配置
MAX_UPLOAD_SIZE=10485760  # 10MB
'''
        
        # 前端环境变量模板
        frontend_env_template = '''# React前端环境变量配置模板
# 复制此文件为.env并根据实际情况修改

# API基础URL
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# 应用配置
VITE_APP_TITLE=Django测试平台
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=true

# 第三方服务配置（如果使用）
# VITE_ANALYTICS_ID=your-analytics-id
# VITE_SENTRY_DSN=your-sentry-dsn
'''
        
        # 写入模板文件
        templates = [
            ("backend/.env.example", backend_env_template),
            ("frontend/.env.example", frontend_env_template),
            (".env.example", "# 项目根目录环境变量\n# 用于Docker Compose等全局配置\n\n# 应用版本\nAPP_VERSION=1.0.0\n\n# 数据库\nPOSTGRES_DB=test_platform_db\nPOSTGRES_USER=postgres\nPOSTGRES_PASSWORD=password\n")
        ]
        
        for file_path, content in templates:
            full_path = self.project_root / file_path
            if not self.dry_run:
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.write_text(content, encoding='utf-8')
            self.print_colored(f"  ✓ {file_path}", Colors.GREEN)
    
    def update_configuration_files(self):
        """更新配置文件"""
        self.print_colored("⚙️  更新配置文件引用...", Colors.CYAN)
        
        # 这里只是提示，实际的文件内容更新需要手动处理
        config_updates = [
            "backend/config/settings/base.py - 更新应用路径引用",
            "backend/config/urls.py - 更新应用URL引用", 
            "frontend/src/config/api.js - 更新API配置",
            "scripts/dev/* - 更新脚本中的路径引用",
            "package.json - 更新脚本命令",
        ]
        
        for update in config_updates:
            self.print_colored(f"  📝 TODO: {update}", Colors.YELLOW)
    
    def create_summary_report(self):
        """创建重构总结报告"""
        self.print_colored("📊 生成重构报告...", Colors.CYAN)
        
        report_content = f"""# 项目重构完成报告

## 重构时间
{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 主要变更

### 1. 目录重命名
- `blackend/` → `backend/`
- `test_platform/` → `backend/config/`

### 2. 脚本文件重组
- 所有启动脚本移至 `scripts/dev/`
- 所有测试脚本移至 `scripts/test/`
- 所有工具脚本移至 `scripts/utils/`

### 3. 后端应用重组
- 所有Django应用移至 `backend/apps/`
- 测试文件重新组织

### 4. 环境配置完善
- 创建后端环境变量模板
- 创建前端环境变量模板
- 创建项目级环境变量模板

## 后续手动操作

### 必须完成的配置更新
1. 更新 `backend/config/settings/base.py` 中的应用路径
2. 更新 `backend/config/urls.py` 中的应用引用
3. 更新前端API配置文件
4. 更新脚本文件中的路径引用
5. 测试所有功能是否正常

### 建议操作
1. 更新 README.md 文档
2. 更新部署文档
3. 运行完整测试套件验证
4. 更新CI/CD配置（如果有）

## 备份位置
{self.backup_dir}

## 验证步骤
1. 运行环境检查脚本: `python scripts/utils/check-environment.py`
2. 启动后端服务: `scripts/dev/start-backend.sh` (Linux/Mac) 或 `scripts/dev/start-backend.bat` (Windows)
3. 启动前端服务: `scripts/dev/start-frontend.sh` (Linux/Mac) 或 `scripts/dev/start-frontend.bat` (Windows)
4. 运行测试: `python scripts/test/run-all-tests.py`
"""
        
        report_path = self.project_root / "RESTRUCTURE_REPORT.md"
        if not self.dry_run:
            report_path.write_text(report_content, encoding='utf-8')
        
        self.print_colored(f"📄 重构报告已生成: {report_path}", Colors.GREEN)
    
    def run_restructure(self, dry_run=False):
        """执行重构"""
        self.dry_run = dry_run
        
        if dry_run:
            self.print_colored("🔍 执行预览模式（不会实际修改文件）", Colors.YELLOW)
        else:
            self.print_colored("🚀 开始项目重构", Colors.BOLD)
        
        try:
            # 检查Git状态
            if not dry_run and not self.check_git_status():
                return False
            
            # 创建备份
            if not dry_run:
                self.create_backup()
            
            # 执行重构步骤（注意顺序：先移动脚本，再重命名目录）
            self.create_new_directories()
            self.reorganize_scripts()  # 先移动脚本（在blackend目录还存在时）
            self.rename_backend_directory()  # 再重命名目录
            self.reorganize_backend_structure()
            self.create_environment_templates()
            self.update_configuration_files()
            
            if not dry_run:
                self.create_summary_report()
            
            if dry_run:
                self.print_colored("\n✅ 预览完成！使用 --execute 参数执行实际重构", Colors.GREEN)
            else:
                self.print_colored("\n🎉 项目重构完成！", Colors.GREEN)
                self.print_colored("请查看 RESTRUCTURE_REPORT.md 了解详细信息", Colors.CYAN)
                self.print_colored("⚠️  请手动完成配置文件更新后再测试项目", Colors.YELLOW)
            
            return True
            
        except Exception as e:
            self.print_colored(f"❌ 重构过程中出错: {e}", Colors.RED)
            return False

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Django测试平台项目重构工具')
    parser.add_argument('--project-root', default='.', 
                       help='项目根目录路径（默认当前目录）')
    parser.add_argument('--dry-run', action='store_true',
                       help='预览模式，不实际修改文件')
    parser.add_argument('--execute', action='store_true',
                       help='执行实际重构')
    
    args = parser.parse_args()
    
    if not args.dry_run and not args.execute:
        print("请指定 --dry-run（预览）或 --execute（执行）参数")
        return 1
    
    project_root = os.path.abspath(args.project_root)
    restructurer = ProjectRestructurer(project_root)
    
    print(f"项目根目录: {project_root}")
    
    if args.dry_run:
        success = restructurer.run_restructure(dry_run=True)
    else:
        print("⚠️  即将开始项目重构，这将修改项目结构")
        if input("确认继续？(y/N): ").lower() == 'y':
            success = restructurer.run_restructure(dry_run=False)
        else:
            print("操作已取消")
            return 0
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())