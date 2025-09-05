#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一测试运行器
运行所有后端单元测试并生成详细报告
"""
import os
import sys
import time
import logging
from datetime import datetime
import django
from django.core.management import execute_from_command_line
from django.test.utils import get_runner
from django.conf import settings
from django.apps import apps
from django.db import connection

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_results.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class TestReporter:
    """测试报告生成器"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.test_results = {}
        self.total_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.passed_tests = 0
    
    def start_testing(self):
        """开始测试"""
        self.start_time = datetime.now()
        logger.info("=" * 60)
        logger.info("🚀 Django测试平台 - 单元测试开始")
        logger.info(f"⏰ 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
    
    def end_testing(self, failures):
        """结束测试"""
        self.end_time = datetime.now()
        duration = self.end_time - self.start_time
        
        logger.info("=" * 60)
        logger.info("📊 测试结果汇总")
        logger.info("=" * 60)
        logger.info(f"⏰ 结束时间: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"⏱️  总耗时: {duration.total_seconds():.2f}秒")
        logger.info(f"📈 总测试数: {self.total_tests}")
        logger.info(f"✅ 通过: {self.passed_tests}")
        logger.info(f"❌ 失败: {failures}")
        
        if failures == 0:
            logger.info("🎉 所有测试通过！")
        else:
            logger.warning(f"⚠️  有 {failures} 个测试失败")
        
        success_rate = ((self.total_tests - failures) / self.total_tests * 100) if self.total_tests > 0 else 0
        logger.info(f"📊 成功率: {success_rate:.1f}%")
        logger.info("=" * 60)
        
        return failures == 0
    
    def log_app_info(self):
        """记录应用信息"""
        logger.info("📱 已注册的Django应用:")
        for app_config in apps.get_app_configs():
            if not app_config.name.startswith('django.'):
                logger.info(f"   • {app_config.label}: {app_config.name}")
    
    def log_database_info(self):
        """记录数据库信息"""
        db_settings = settings.DATABASES['default']
        logger.info(f"💾 数据库引擎: {db_settings['ENGINE']}")
        if 'NAME' in db_settings:
            logger.info(f"💾 数据库名称: {db_settings['NAME']}")

def check_environment():
    """检查测试环境"""
    logger.info("🔍 检查测试环境...")
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    logger.info(f"🐍 Python版本: {python_version}")
    
    # 检查Django版本
    import django
    logger.info(f"🎸 Django版本: {django.get_version()}")
    
    # 检查关键依赖
    try:
        import rest_framework
        logger.info(f"🔧 DRF版本: {rest_framework.__version__}")
    except ImportError:
        logger.warning("⚠️  Django REST Framework未安装")
    
    return True

def get_test_modules():
    """获取测试模块列表"""
    test_modules = []
    test_base_dir = 'tests'
    
    if os.path.exists(test_base_dir):
        for item in os.listdir(test_base_dir):
            if os.path.isdir(os.path.join(test_base_dir, item)) and not item.startswith('_'):
                test_modules.append(f'tests.{item}')
    
    # 添加应用内的测试
    app_tests = [
        'api_test.tests',
        'api_test.test_models',
        'api_test.test_services',
        'testcases.tests',
        'user_management.tests',
        'reports.tests',
        'comments.tests',
        'environments.tests',
        'mock_server.tests',
    ]
    
    # 过滤存在的测试模块
    for test_module in app_tests:
        try:
            module_path = test_module.replace('.', '/') + '.py'
            if os.path.exists(module_path):
                test_modules.append(test_module)
        except:
            pass
    
    return test_modules

def main():
    """主函数"""
    # 设置Django环境
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_platform.settings')
    django.setup()
    
    reporter = TestReporter()
    reporter.start_testing()
    
    try:
        # 检查环境
        if not check_environment():
            logger.error("❌ 环境检查失败")
            return 1
        
        # 记录应用和数据库信息
        reporter.log_app_info()
        reporter.log_database_info()
        
        # 获取测试模块
        test_modules = get_test_modules()
        if not test_modules:
            logger.warning("⚠️  未找到测试模块")
            test_modules = ['tests']  # 使用默认测试目录
        
        logger.info(f"🧪 将运行以下测试模块: {test_modules}")
        
        # 使用Django的测试运行器
        TestRunner = get_runner(settings)
        test_runner = TestRunner(verbosity=2, interactive=False, keepdb=False)
        
        # 运行测试
        failures = test_runner.run_tests(test_modules)
        
        # 生成报告
        success = reporter.end_testing(failures)
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"❌ 测试运行出错: {e}")
        logger.exception("详细错误信息:")
        return 1
    
    finally:
        # 清理
        if reporter.end_time is None:
            reporter.end_time = datetime.now()
        logger.info("🧹 测试运行完成")

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)