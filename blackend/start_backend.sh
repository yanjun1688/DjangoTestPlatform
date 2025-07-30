#!/bin/bash
# Django后端启动脚本

echo "🚀 启动Django后端服务器"
echo "=========================="

# 检查Python环境
echo "📍 检查Python环境..."
python3 --version

# 检查当前目录
echo "📁 当前目录: $(pwd)"

# 检查是否有虚拟环境
if [ -d ".venv" ]; then
    echo "🔧 激活虚拟环境..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    echo "🔧 激活虚拟环境..."
    source venv/bin/activate
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
fi

# 安装依赖(如果需要)
echo "📦 检查依赖..."
if [ -f "requirements.txt" ]; then
    echo "正在安装Python依赖..."
    pip install -r requirements.txt
fi

# 运行数据库迁移
echo "🗄️  运行数据库迁移..."
python3 manage.py makemigrations
python3 manage.py migrate

# 创建超级用户(如果需要)
echo "👤 检查超级用户..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser('admin', 'admin@test.com', 'admin123')" | python3 manage.py shell

# 收集静态文件(生产环境需要)
echo "📂 收集静态文件..."
python3 manage.py collectstatic --noinput

echo "✅ 启动Django开发服务器..."
echo "🌐 服务器地址: http://localhost:8000"
echo "🔧 Admin地址: http://localhost:8000/admin"
echo "📝 Admin账号: admin / admin123"
echo "=========================="

# 启动服务器
python3 manage.py runserver 0.0.0.0:8000