#!/usr/bin/env python
"""
统一测试管理脚本

提供便捷的测试执行、报告生成和测试管理功能
"""

import os
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')

try:
    import django
    django.setup()
    
    from django.core.management import call_command
    DJANGO_AVAILABLE = True
except ImportError:
    DJANGO_AVAILABLE = False
    print("警告: 无法导入Django，部分功能不可用")


class TestManager:
    """测试管理器"""
    
    def __init__(self):
        self.project_root = project_root
        self.tests_dir = self.project_root / 'tests'
        
        # 模块映射
        self.module_map = {
            'api_test': 'tests.api_test',
            'testcases': 'tests.testcases',
            'user_management': 'tests.user_management',
            'reports': 'tests.reports',
            'mock_server': 'tests.mock_server',
            'environments': 'tests.environments',
            'comments': 'tests.comments',
            'integration': 'tests.integration',
            'e2e': 'tests.e2e'
        }
        
        # 测试类型映射
        self.test_type_map = {
            'unit': [
                'tests.api_test',
                'tests.testcases',
                'tests.user_management',
                'tests.reports',
                'tests.mock_server',
                'tests.environments',
                'tests.comments'
            ],
            'integration': ['tests.integration'],
            'e2e': ['tests.e2e'],
            'all': list(self.module_map.values())
        }
    
    def list_tests(self, modules=None, test_type='all'):
        """列出可用的测试"""
        print(f"\n{'=' * 60}")
        print(f"可用的测试模块")
        print(f"{'=' * 60}\n")
        
        if modules:
            selected_modules = [m for m in modules if m in self.module_map]
        else:
            if test_type == 'all':
                selected_modules = list(self.module_map.keys())
            else:
                test_modules = self.test_type_map.get(test_type, [])
                selected_modules = [k for k, v in self.module_map.items() if v in test_modules]
        
        for module in selected_modules:
            module_path = self.module_map[module]
            print(f"📁 {module}")
            print(f"   路径: {module_path}")
            
            # 尝试列出测试文件
            try:
                module_dir = self.tests_dir / module
                if module_dir.exists():
                    test_files = list(module_dir.glob('test_*.py'))
                    if test_files:
                        print(f"   测试文件:")
                        for test_file in test_files:
                            print(f"     - {test_file.name}")
                    else:
                        print(f"   测试文件: 无")
                else:
                    print(f"   状态: 目录不存在")
            except Exception as e:
                print(f"   状态: 无法访问 ({e})")
            
            print()
    
    def run_tests(self, modules=None, test_type='all', verbosity=2):
        """运行测试"""
        
        print(f"\n{'=' * 60}")
        print(f"Django测试平台 - 测试执行器")
        print(f"{'=' * 60}\n")
        
        # 确定要运行的测试模块
        if modules:
            test_modules = [self.module_map.get(m, m) for m in modules if m in self.module_map]
        else:
            test_modules = self.test_type_map.get(test_type, self.test_type_map['all'])
        
        if not test_modules:
            print("❌ 没有找到匹配的测试模块")
            return False
        
        print(f"📋 测试配置:")
        print(f"   - 测试类型: {test_type}")
        print(f"   - 模块数量: {len(test_modules)}")
        print(f"   - 详细程度: {verbosity}")
        
        print(f"\n🎯 测试模块:")
        for module in test_modules:
            print(f"   - {module}")
        
        print(f"\n{'=' * 60}\n")
        
        if not DJANGO_AVAILABLE:
            print("❌ Django不可用，无法运行测试")
            return False
            
        try:
            # 使用Django test命令
            cmd_args = ['test'] + test_modules + ['--verbosity', str(verbosity)]
            call_command(*cmd_args)
            print("\n✅ 测试执行完成!")
            return True
        except SystemExit as e:
            success = e.code == 0
            if success:
                print("\n✅ 测试执行完成!")
            else:
                print("\n❌ 测试执行失败!")
            return success
        except Exception as e:
            print(f"\n❌ 测试执行出错: {str(e)}")
            return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Django测试平台统一测试管理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python run_tests.py                           # 运行所有测试
  python run_tests.py --type unit               # 运行单元测试
  python run_tests.py --modules api_test        # 运行API测试模块
  python run_tests.py --list                    # 列出所有可用测试
        """
    )
    
    parser.add_argument(
        '--modules', '-m',
        nargs='+',
        choices=list(TestManager().module_map.keys()),
        help='指定要运行的测试模块'
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['unit', 'integration', 'e2e', 'all'],
        default='all',
        help='指定测试类型 (默认: all)'
    )
    
    parser.add_argument(
        '--verbosity', '-v',
        type=int,
        choices=[0, 1, 2, 3],
        default=2,
        help='输出详细程度 (默认: 2)'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='列出可用的测试模块'
    )
    
    args = parser.parse_args()
    
    # 创建测试管理器
    test_manager = TestManager()
    
    # 执行对应的操作
    if args.list:
        test_manager.list_tests(args.modules, args.type)
        return
    
    # 运行测试
    success = test_manager.run_tests(
        modules=args.modules,
        test_type=args.type,
        verbosity=args.verbosity
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()