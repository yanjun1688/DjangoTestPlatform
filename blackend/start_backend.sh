#!/bin/bash
# Django后端启动脚本 - 跨平台兼容版本

echo "🚀 启动Django后端服务器"
echo "=========================="

# 检测操作系统
OS_TYPE="unknown"
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    OS_TYPE="windows"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
fi

echo "🖥️  检测到操作系统: $OS_TYPE"

# 智能检测Python命令（优先使用虚拟环境中的Python）
PYTHON_CMD=""

# 如果已经在虚拟环境中，直接使用python
if [ -n "$VIRTUAL_ENV" ]; then
    echo "🔍 检测到已在虚拟环境中: $VIRTUAL_ENV"
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    fi
fi

# 如果不在虚拟环境中，按优先级检测
if [ -z "$PYTHON_CMD" ]; then
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_VERSION=$(python --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
        if [[ "$PYTHON_VERSION" == "3."* ]]; then
            PYTHON_CMD="python"
        fi
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ 错误: 未找到Python 3.x，请先安装Python 3.x"
    exit 1
fi

echo "📍 使用Python命令: $PYTHON_CMD"
$PYTHON_CMD --version

# 检查当前目录
echo "📁 当前目录: $(pwd)"

# 检查manage.py是否存在
if [ ! -f "manage.py" ]; then
    echo "❌ 错误: 未找到manage.py文件，请确保在Django项目根目录下运行"
    exit 1
fi

# 检查并激活虚拟环境
echo "🔧 检查虚拟环境..."
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ 已在虚拟环境中: $(basename $VIRTUAL_ENV)"
elif [ -d ".venv" ]; then
    echo "激活虚拟环境: .venv"
    if [ "$OS_TYPE" == "windows" ]; then
        source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate
    else
        source .venv/bin/activate
    fi
    # 激活后重新设置Python命令
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    fi
    echo "✅ 虚拟环境已激活"
elif [ -d "venv" ]; then
    echo "激活虚拟环境: venv"
    if [ "$OS_TYPE" == "windows" ]; then
        source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
    else
        source venv/bin/activate
    fi
    # 激活后重新设置Python命令
    if command -v python &> /dev/null; then
        PYTHON_CMD="python"
    fi
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，建议创建虚拟环境"
    echo "   可运行: $PYTHON_CMD -m venv .venv"
    echo "   然后激活: source .venv/bin/activate （Linux/Mac） 或 .venv\\Scripts\\activate （Windows）"
fi

# 安装依赖
echo "📦 检查并安装依赖..."
if [ -f "requirements.txt" ]; then
    echo "正在安装Python依赖..."
    $PYTHON_CMD -m pip install --upgrade pip
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败，请检查requirements.txt文件"
        exit 1
    fi
    echo "✅ 依赖安装成功"
else
    echo "⚠️  未找到requirements.txt文件"
fi

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
$PYTHON_CMD manage.py makemigrations
if [ $? -ne 0 ]; then
    echo "⚠️  makemigrations执行有警告，继续执行migrate"
fi

$PYTHON_CMD manage.py migrate
if [ $? -ne 0 ]; then
    echo "❌ 数据库迁移失败"
    exit 1
fi

# 创建超级用户(如果需要)
echo "👤 检查超级用户..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); created = not User.objects.filter(is_superuser=True).exists(); User.objects.create_superuser('admin', 'admin@test.com', 'admin123') if created else None; print('超级用户已创建' if created else '超级用户已存在')" | $PYTHON_CMD manage.py shell

# 收集静态文件(生产环境需要)
echo "📂 收集静态文件..."
$PYTHON_CMD manage.py collectstatic --noinput

echo "✅ 准备启动Django开发服务器..."
echo "🌐 服务器地址: http://localhost:8000"
echo "🔧 Admin地址: http://localhost:8000/admin"
echo "📝 Admin账号: admin / admin123"
echo "🔄 按Ctrl+C停止服务器"
echo "=========================="

# 启动服务器
$PYTHON_CMD manage.py runserver 0.0.0.0:8000 