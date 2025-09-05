#!/bin/bash
# 环境检查脚本

echo "🔍 Django项目环境检查"
echo "=========================="

# 智能检测Python命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
    if [[ "$PYTHON_VERSION" == "3."* ]]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ 错误: 未找到Python 3.x，请先安装Python 3.x"
    exit 1
fi

echo "📍 使用Python命令: $PYTHON_CMD"

# 切换到backend目录（如果需要）
if [ ! -f "check_environment.py" ] && [ -f "blackend/check_environment.py" ]; then
    cd blackend
fi

# 运行环境检查
echo "🚀 运行环境检查脚本..."
$PYTHON_CMD check_environment.py

exit_code=$?
if [ $exit_code -eq 0 ]; then
    echo
    echo "✅ 环境检查完成"
else
    echo
    echo "❌ 环境检查发现问题"
fi

exit $exit_code