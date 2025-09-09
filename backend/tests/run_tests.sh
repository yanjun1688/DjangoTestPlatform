#!/bin/bash
# Linux/macOS Shell脚本 - 便捷测试执行
# 使用方法: ./run_tests.sh

echo "=========================================="
echo "Django测试平台 - 集中化测试执行器"
echo "=========================================="
echo ""

# 进入脚本所在目录
cd "$(dirname "$0")"

# 检查Python是否可用
if ! command -v python &> /dev/null; then
    echo "错误: Python未安装或不在PATH环境变量中"
    exit 1
fi

echo "选择要执行的测试类型:"
echo ""
echo "1. 执行所有测试"
echo "2. 单元测试 (Unit Tests)"
echo "3. API测试 (API Tests)"
echo "4. 功能测试 (Functional Tests)"
echo "5. 集成测试 (Integration Tests)"
echo "6. E2E测试 (End-to-End Tests)"
echo "7. 性能测试 (Performance Tests)"
echo "8. 检查环境"
echo "9. 退出"
echo ""

read -p "请输入选择 (1-9): " choice

case $choice in
    1)
        echo "执行所有测试..."
        python run_all_tests.py --verbose
        ;;
    2)
        echo "执行单元测试..."
        python run_all_tests.py --unit --verbose
        ;;
    3)
        echo "执行API测试..."
        python run_all_tests.py --api --verbose
        ;;
    4)
        echo "执行功能测试..."
        python run_all_tests.py --functional --verbose
        ;;
    5)
        echo "执行集成测试..."
        python run_all_tests.py --integration --verbose
        ;;
    6)
        echo "执行E2E测试..."
        python run_all_tests.py --e2e --verbose
        ;;
    7)
        echo "执行性能测试..."
        python run_all_tests.py --performance --verbose
        ;;
    8)
        echo "检查测试环境..."
        python run_all_tests.py --check
        ;;
    9)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选择，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "测试执行完成！"