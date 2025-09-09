#!/usr/bin/env python
"""
统一测试执行脚本
集中管理所有类型的测试执行

使用方法:
    python run_all_tests.py                    # 执行所有测试
    python run_all_tests.py --unit             # 只执行单元测试
    python run_all_tests.py --api              # 只执行API测试
    python run_all_tests.py --functional       # 只执行功能测试
    python run_all_tests.py --integration      # 只执行集成测试
    python run_all_tests.py --e2e              # 只执行E2E测试
    python run_all_tests.py --performance      # 只执行性能测试
    python run_all_tests.py --verbose          # 详细输出
    python run_all_tests.py --coverage         # 生成覆盖率报告
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# 添加项目根目录到Python路径
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')

# 导入Django
import django
django.setup()

class TestRunner:
    """测试执行器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent
        self.manage_py = self.project_root / 'manage.py'
        
    def run_django_tests(self, test_paths, verbose=False, coverage=False):
        """
        运行Django测试
        
        Args:
            test_paths: 测试路径列表
            verbose: 是否显示详细输出
            coverage: 是否生成覆盖率报告
        """
        cmd = ['python', str(self.manage_py), 'test']
        
        if verbose:
            cmd.append('--verbosity=2')
        
        # 添加测试路径
        for path in test_paths:
            cmd.append(f'tests.{path}')
        
        if coverage:
            # 使用coverage运行测试
            cmd = ['coverage', 'run', '--source=.'] + cmd[1:]
        
        print(f"执行命令: {' '.join(cmd)}")
        print("=" * 80)
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root)
        end_time = time.time()
        
        print("=" * 80)
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")
        
        if coverage and result.returncode == 0:
            print("\n生成覆盖率报告...")
            subprocess.run(['coverage', 'report'], cwd=self.project_root)
            subprocess.run(['coverage', 'html'], cwd=self.project_root)
            print("HTML覆盖率报告已生成: htmlcov/index.html")
        
        return result.returncode

    def run_pytest_tests(self, test_paths, verbose=False, coverage=False):
        """
        运行pytest测试
        
        Args:
            test_paths: 测试路径列表
            verbose: 是否显示详细输出
            coverage: 是否生成覆盖率报告
        """
        cmd = ['pytest']
        
        if verbose:
            cmd.append('-v')
        
        if coverage:
            cmd.extend(['--cov=.', '--cov-report=html', '--cov-report=term'])
        
        # 添加测试路径
        for path in test_paths:
            full_path = self.test_dir / path
            if full_path.exists():
                cmd.append(str(full_path))
        
        print(f"执行命令: {' '.join(cmd)}")
        print("=" * 80)
        
        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root)
        end_time = time.time()
        
        print("=" * 80)
        print(f"测试完成，耗时: {end_time - start_time:.2f}秒")
        
        return result.returncode

    def run_unit_tests(self, verbose=False, coverage=False):
        """运行单元测试"""
        print("🧪 运行单元测试...")
        return self.run_django_tests(['unit'], verbose, coverage)

    def run_api_tests(self, verbose=False, coverage=False):
        """运行API测试"""
        print("🔌 运行API测试...")
        return self.run_django_tests(['api'], verbose, coverage)

    def run_functional_tests(self, verbose=False, coverage=False):
        """运行功能测试"""
        print("⚙️ 运行功能测试...")
        return self.run_django_tests(['functional'], verbose, coverage)

    def run_integration_tests(self, verbose=False, coverage=False):
        """运行集成测试"""
        print("🔗 运行集成测试...")
        return self.run_django_tests(['integration'], verbose, coverage)

    def run_e2e_tests(self, verbose=False, coverage=False):
        """运行E2E测试"""
        print("🌐 运行E2E测试...")
        return self.run_django_tests(['e2e'], verbose, coverage)

    def run_performance_tests(self, verbose=False, coverage=False):
        """运行性能测试"""
        print("⚡ 运行性能测试...")
        return self.run_django_tests(['performance'], verbose, coverage)

    def run_all_tests(self, verbose=False, coverage=False):
        """运行所有测试"""
        print("🚀 运行所有测试...")
        
        test_types = [
            ('单元测试', self.run_unit_tests),
            ('API测试', self.run_api_tests),
            ('功能测试', self.run_functional_tests),
            ('集成测试', self.run_integration_tests),
            ('E2E测试', self.run_e2e_tests),
            ('性能测试', self.run_performance_tests),
        ]
        
        results = {}
        total_start_time = time.time()
        
        for test_name, test_func in test_types:
            print(f"\n{'='*60}")
            print(f"开始执行: {test_name}")
            print(f"{'='*60}")
            
            start_time = time.time()
            result = test_func(verbose, False)  # 不在每个测试中生成覆盖率
            end_time = time.time()
            
            results[test_name] = {
                'result': result,
                'time': end_time - start_time
            }
        
        total_end_time = time.time()
        
        # 如果需要覆盖率报告，最后生成一次
        if coverage:
            print(f"\n{'='*60}")
            print("生成整体覆盖率报告...")
            print(f"{'='*60}")
            self.run_django_tests(['unit', 'api', 'functional', 'integration', 'e2e'], verbose, True)
        
        # 输出测试摘要
        print(f"\n{'='*80}")
        print("🎯 测试执行摘要")
        print(f"{'='*80}")
        
        total_passed = 0
        total_failed = 0
        
        for test_name, result_info in results.items():
            status = "✅ 通过" if result_info['result'] == 0 else "❌ 失败"
            time_str = f"{result_info['time']:.2f}秒"
            print(f"{test_name:12s} - {status:8s} ({time_str})")
            
            if result_info['result'] == 0:
                total_passed += 1
            else:
                total_failed += 1
        
        print(f"\n总耗时: {total_end_time - total_start_time:.2f}秒")
        print(f"通过: {total_passed}, 失败: {total_failed}")
        
        # 返回0表示所有测试都通过
        return 0 if total_failed == 0 else 1

    def check_environment(self):
        """检查测试环境"""
        print("🔍 检查测试环境...")
        
        # 检查manage.py是否存在
        if not self.manage_py.exists():
            print(f"❌ 找不到 manage.py 文件: {self.manage_py}")
            return False
        
        # 检查测试目录是否存在
        required_dirs = ['unit', 'api', 'functional', 'integration', 'e2e', 'performance']
        for dir_name in required_dirs:
            test_dir = self.test_dir / dir_name
            if not test_dir.exists():
                print(f"⚠️  测试目录不存在: {test_dir}")
        
        print("✅ 环境检查完成")
        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Django测试平台统一测试执行脚本')
    
    # 测试类型选项
    parser.add_argument('--unit', action='store_true', help='只执行单元测试')
    parser.add_argument('--api', action='store_true', help='只执行API测试')
    parser.add_argument('--functional', action='store_true', help='只执行功能测试')
    parser.add_argument('--integration', action='store_true', help='只执行集成测试')
    parser.add_argument('--e2e', action='store_true', help='只执行E2E测试')
    parser.add_argument('--performance', action='store_true', help='只执行性能测试')
    
    # 其他选项
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--coverage', '-c', action='store_true', help='生成覆盖率报告')
    parser.add_argument('--check', action='store_true', help='只检查环境，不运行测试')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # 检查环境
    if not runner.check_environment():
        return 1
    
    if args.check:
        return 0
    
    # 确定要运行的测试类型
    test_flags = [args.unit, args.api, args.functional, args.integration, args.e2e, args.performance]
    
    if not any(test_flags):
        # 如果没有指定测试类型，运行所有测试
        return runner.run_all_tests(args.verbose, args.coverage)
    
    # 运行指定的测试类型
    exit_code = 0
    
    if args.unit:
        exit_code |= runner.run_unit_tests(args.verbose, args.coverage)
    
    if args.api:
        exit_code |= runner.run_api_tests(args.verbose, args.coverage)
    
    if args.functional:
        exit_code |= runner.run_functional_tests(args.verbose, args.coverage)
    
    if args.integration:
        exit_code |= runner.run_integration_tests(args.verbose, args.coverage)
    
    if args.e2e:
        exit_code |= runner.run_e2e_tests(args.verbose, args.coverage)
    
    if args.performance:
        exit_code |= runner.run_performance_tests(args.verbose, args.coverage)
    
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)