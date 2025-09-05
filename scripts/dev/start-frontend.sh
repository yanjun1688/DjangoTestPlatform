#!/bin/bash
# React前端启动脚本

echo "🎨 启动React前端服务器"
echo "========================"

# 检查Node.js环境
echo "📍 检查Node.js环境..."
node --version
npm --version

# 检查当前目录
echo "📁 当前目录: $(pwd)"

# 安装依赖
echo "📦 安装npm依赖..."
npm install

# 检查是否安装成功
if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败，尝试清理缓存..."
    rm -rf node_modules package-lock.json
    npm install
fi

# 启动开发服务器
echo "✅ 启动React开发服务器..."
echo "🌐 前端地址: http://localhost:5173"
echo "🔗 后端API: http://localhost:8000"
echo "========================"

# 启动Vite开发服务器
npm run dev