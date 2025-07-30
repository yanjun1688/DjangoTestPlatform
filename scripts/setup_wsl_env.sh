#!/bin/bash

echo "=== Django测试平台 WSL环境配置脚本 ==="
echo "正在配置WSL环境以运行Django测试平台..."

# 更新包列表
echo "1. 更新包列表..."
sudo apt update

# 安装Python3和pip
echo "2. 安装Python3和pip..."
sudo apt install -y python3 python3-pip python3-venv

# 安装Node.js和npm
echo "3. 安装Node.js和npm..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
echo "4. 验证安装..."
echo "Python版本: $(python3 --version)"
echo "pip版本: $(pip3 --version)"
echo "Node.js版本: $(node --version)"
echo "npm版本: $(npm --version)"

# 升级pip
echo "5. 升级pip..."
pip3 install --upgrade pip --user

# 安装Python依赖
echo "6. 安装Python依赖..."
cd /mnt/d/Project/DjangoTestPlatform/blackend

# 创建requirements.txt如果不存在
if [ ! -f "requirements.txt" ]; then
    echo "创建requirements.txt..."
    cat > requirements.txt << EOF
Django>=4.2.0
djangorestframework>=3.14.0
django-cors-headers>=4.0.0
django-mptt>=0.14.0
django-reversion>=5.0.0
requests>=2.28.0
python-decouple>=3.6
EOF
fi

# 安装Python依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt --user

# 创建Django数据库
echo "7. 创建Django数据库..."
export DJANGO_SETTINGS_MODULE=test_platform.settings
python3 manage.py migrate

# 安装Node.js依赖
echo "8. 安装Node.js依赖..."
cd /mnt/d/Project/DjangoTestPlatform/frontend

# 删除可能存在的node_modules和package-lock.json
rm -rf node_modules package-lock.json

# 安装依赖
npm install

echo "9. 环境配置完成！"
echo ""
echo "=== 运行测试 ==="

# 运行后端测试
echo "运行后端测试..."
cd /mnt/d/Project/DjangoTestPlatform/blackend
python3 manage.py test 2>&1 | tee backend_test_results.txt

# 运行前端测试
echo "运行前端测试..."
cd /mnt/d/Project/DjangoTestPlatform/frontend
npm test 2>&1 | tee frontend_test_results.txt

# 生成测试报告
echo ""
echo "=== 测试报告 ==="
echo "后端测试结果保存在: /mnt/d/Project/DjangoTestPlatform/blackend/backend_test_results.txt"
echo "前端测试结果保存在: /mnt/d/Project/DjangoTestPlatform/frontend/frontend_test_results.txt"

# 统计测试文件
echo ""
echo "=== 测试文件统计 ==="
echo "后端测试文件数量:"
find /mnt/d/Project/DjangoTestPlatform/blackend -name "test_*.py" | wc -l
find /mnt/d/Project/DjangoTestPlatform/tests/backend -name "test_*.py" 2>/dev/null | wc -l

echo "前端测试文件数量:"
find /mnt/d/Project/DjangoTestPlatform/frontend/src -name "*.test.js" -o -name "*.test.jsx" 2>/dev/null | wc -l

echo ""
echo "=== 完成 ==="
echo "环境配置和测试完成！"
echo "如果遇到权限问题，请运行: sudo chmod +x setup_wsl_env.sh"