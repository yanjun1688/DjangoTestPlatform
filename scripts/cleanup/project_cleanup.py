#!/usr/bin/env python3
"""
Django测试平台项目清理脚本
识别和删除冗余文件、多余配置、以及无用的虚拟环境文件夹
"""

import os
import shutil
import sys
from pathlib import Path


class ProjectCleaner:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.redundant_files = []
        self.redundant_dirs = []
        self.cache_files = []
        self.log_files = []
        self.virtual_envs = []
        
    def scan_redundant_files(self):
        """扫描冗余文件"""
        print("扫描冗余文件...")
        
        # 定义冗余文件模式
        redundant_patterns = [
            # 临时文件
            '*.tmp', '*.temp', '*~', '*.bak', '*.swp',
            # 编辑器临时文件
            '.DS_Store', 'Thumbs.db', 'desktop.ini',
            # Python编译文件
            '*.pyc', '*.pyo', '*.pyd',
            # 旧的配置文件
            'requirements-dev.txt', 'requirements-tdd.txt',
            # 重复的测试脚本
            'run-all-tests.py',
            # 过时的报告文件
            'TEST_SUMMARY.md', 'RESTRUCTURE_REPORT.md',
            # 示例数据文件
            'sample_test_data.*',
            # 临时重构文件
            'restructure_project.py',
        ]
        
        for pattern in redundant_patterns:
            for file in self.project_root.rglob(pattern):
                if file.is_file():
                    self.redundant_files.append(file)
                    
        # 检查根目录的.env.example（应该只在backend目录）
        root_env_example = self.project_root / '.env.example'
        if root_env_example.exists():
            self.redundant_files.append(root_env_example)
    
    def scan_cache_files(self):
        """扫描缓存文件"""
        print("扫描缓存文件...")
        
        cache_patterns = [
            '__pycache__',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '.tox',
            'node_modules',
            '.next',
            'dist',
            'build',
        ]
        
        for pattern in cache_patterns:
            for path in self.project_root.rglob(pattern):
                if path.is_dir():
                    self.cache_files.append(path)
    
    def scan_virtual_envs(self):
        """扫描虚拟环境目录"""
        print("扫描虚拟环境目录...")
        
        venv_patterns = [
            'venv', 'env', '.venv', '.env',
            'virtualenv', 'django_env',
            'myenv', 'testenv'
        ]
        
        for venv_name in venv_patterns:
            venv_path = self.project_root / venv_name
            if venv_path.is_dir():
                # 检查是否为虚拟环境目录
                if self._is_virtual_env(venv_path):
                    self.virtual_envs.append(venv_path)
    
    def _is_virtual_env(self, path):
        """判断是否为虚拟环境目录"""
        indicators = [
            path / 'pyvenv.cfg',
            path / 'Scripts' / 'activate.bat',  # Windows
            path / 'bin' / 'activate',  # Unix/Linux
            path / 'lib' / 'python3.11',
        ]
        return any(indicator.exists() for indicator in indicators)
    
    def scan_log_files(self):
        """扫描日志文件"""
        print("扫描日志文件...")
        
        log_patterns = ['*.log', '*.log.*']
        
        for pattern in log_patterns:
            for file in self.project_root.rglob(pattern):
                if file.is_file():
                    self.log_files.append(file)
    
    def scan_empty_dirs(self):
        """扫描空目录"""
        print("扫描空目录...")
        
        for root, dirs, files in os.walk(self.project_root):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                if self._is_empty_dir(dir_path):
                    self.redundant_dirs.append(dir_path)
    
    def _is_empty_dir(self, dir_path):
        """检查目录是否为空"""
        try:
            return len(list(dir_path.iterdir())) == 0
        except (OSError, PermissionError):
            return False
    
    def generate_report(self):
        """生成清理报告"""
        print("\n" + "="*60)
        print("项目清理报告")
        print("="*60)
        
        print(f"\n📁 项目根目录: {self.project_root}")
        
        if self.redundant_files:
            print(f"\n🗑️  发现 {len(self.redundant_files)} 个冗余文件:")
            for file in self.redundant_files:
                rel_path = file.relative_to(self.project_root)
                print(f"   - {rel_path}")
        
        if self.cache_files:
            print(f"\n📦 发现 {len(self.cache_files)} 个缓存目录:")
            for cache_dir in self.cache_files:
                rel_path = cache_dir.relative_to(self.project_root)
                size = self._get_dir_size(cache_dir)
                print(f"   - {rel_path} ({size})")
        
        if self.virtual_envs:
            print(f"\n🐍 发现 {len(self.virtual_envs)} 个虚拟环境目录:")
            for venv in self.virtual_envs:
                rel_path = venv.relative_to(self.project_root)
                size = self._get_dir_size(venv)
                print(f"   - {rel_path} ({size})")
        
        if self.log_files:
            print(f"\n📝 发现 {len(self.log_files)} 个日志文件:")
            for log_file in self.log_files:
                rel_path = log_file.relative_to(self.project_root)
                size = self._get_file_size(log_file)
                print(f"   - {rel_path} ({size})")
        
        if self.redundant_dirs:
            print(f"\n📂 发现 {len(self.redundant_dirs)} 个空目录:")
            for empty_dir in self.redundant_dirs:
                rel_path = empty_dir.relative_to(self.project_root)
                print(f"   - {rel_path}")
        
        # 统计信息
        total_files = len(self.redundant_files) + len(self.log_files)
        total_dirs = len(self.cache_files) + len(self.virtual_envs) + len(self.redundant_dirs)
        
        print(f"\n📊 统计:")
        print(f"   - 冗余文件: {total_files} 个")
        print(f"   - 冗余目录: {total_dirs} 个")
        
        return total_files > 0 or total_dirs > 0
    
    def _get_file_size(self, file_path):
        """获取文件大小"""
        try:
            size = file_path.stat().st_size
            return self._format_size(size)
        except (OSError, PermissionError):
            return "未知"
    
    def _get_dir_size(self, dir_path):
        """获取目录大小"""
        try:
            total_size = 0
            for root, dirs, files in os.walk(dir_path):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, PermissionError):
                        continue
            return self._format_size(total_size)
        except (OSError, PermissionError):
            return "未知"
    
    def _format_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f}{size_names[i]}"
    
    def clean_redundant_files(self):
        """删除冗余文件"""
        if not self.redundant_files:
            return 0
        
        print(f"\n🗑️  开始删除 {len(self.redundant_files)} 个冗余文件...")
        deleted_count = 0
        
        for file in self.redundant_files:
            try:
                file.unlink()
                rel_path = file.relative_to(self.project_root)
                print(f"   ✅ 已删除: {rel_path}")
                deleted_count += 1
            except Exception as e:
                rel_path = file.relative_to(self.project_root)
                print(f"   ❌ 删除失败: {rel_path} - {e}")
        
        return deleted_count
    
    def clean_cache_dirs(self):
        """清理缓存目录"""
        if not self.cache_files:
            return 0
        
        print(f"\n📦 开始清理 {len(self.cache_files)} 个缓存目录...")
        cleaned_count = 0
        
        for cache_dir in self.cache_files:
            try:
                shutil.rmtree(cache_dir)
                rel_path = cache_dir.relative_to(self.project_root)
                print(f"   ✅ 已清理: {rel_path}")
                cleaned_count += 1
            except Exception as e:
                rel_path = cache_dir.relative_to(self.project_root)
                print(f"   ❌ 清理失败: {rel_path} - {e}")
        
        return cleaned_count
    
    def run_cleanup(self, auto_clean=False):
        """运行清理过程"""
        print("Django测试平台项目清理工具")
        print("="*60)
        
        # 扫描各类文件
        self.scan_redundant_files()
        self.scan_cache_files()
        self.scan_virtual_envs()
        self.scan_log_files()
        self.scan_empty_dirs()
        
        # 生成报告
        has_items = self.generate_report()
        
        if not has_items:
            print("\n✅ 项目很干净，没有发现冗余文件!")
            return
        
        if not auto_clean:
            print("\n" + "="*60)
            print("清理选项:")
            print("1. 删除冗余文件")
            print("2. 清理缓存目录")
            print("3. 全部清理")
            print("4. 退出")
            
            while True:
                choice = input("\n请选择操作 (1-4): ").strip()
                
                if choice == '1':
                    deleted = self.clean_redundant_files()
                    print(f"\n✅ 成功删除 {deleted} 个冗余文件")
                    break
                elif choice == '2':
                    cleaned = self.clean_cache_dirs()
                    print(f"\n✅ 成功清理 {cleaned} 个缓存目录")
                    break
                elif choice == '3':
                    deleted = self.clean_redundant_files()
                    cleaned = self.clean_cache_dirs()
                    print(f"\n✅ 清理完成!")
                    print(f"   - 删除冗余文件: {deleted} 个")
                    print(f"   - 清理缓存目录: {cleaned} 个")
                    break
                elif choice == '4':
                    print("退出清理工具")
                    break
                else:
                    print("无效选择，请输入 1-4")
        else:
            # 自动清理模式
            deleted = self.clean_redundant_files()
            cleaned = self.clean_cache_dirs()
            print(f"\n✅ 自动清理完成!")
            print(f"   - 删除冗余文件: {deleted} 个")
            print(f"   - 清理缓存目录: {cleaned} 个")


def main():
    """主函数"""
    # 获取项目根目录
    current_dir = Path(__file__).resolve().parent
    project_root = current_dir.parent.parent
    
    # 检查是否在正确的项目目录
    if not (project_root / 'backend' / 'manage.py').exists():
        print("❌ 错误: 未找到Django项目根目录")
        sys.exit(1)
    
    # 创建清理器
    cleaner = ProjectCleaner(project_root)
    
    # 检查命令行参数
    auto_clean = '--auto' in sys.argv
    
    try:
        cleaner.run_cleanup(auto_clean=auto_clean)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
    except Exception as e:
        print(f"\n❌ 清理过程中发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
