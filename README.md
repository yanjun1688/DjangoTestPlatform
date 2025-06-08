# Django Test Platform

一个基于Django和React的测试平台，用于管理测试用例和API测试。

## 技术栈

- 后端：Django + Django REST Framework
- 前端：React + Vite
- 数据库：SQLite (开发环境)

## 项目结构

```
DjangoTestPlatform/
├── blackend/            # Django后端代码
│   ├── api_test/        # API测试模块
│   ├── testcases/       # 测试用例管理模块
│   ├── test_platform/   # Django项目配置
│   ├── manage.py        # Django管理脚本
│   └── requirements.txt # Python依赖
└── frontend/            # React前端代码
    ├── src/             # 前端源代码
    └── vite.config.js   # Vite配置
```

## 安装与运行

### 后端开发环境

1. 创建并激活虚拟环境：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. 安装依赖：
   ```bash
   cd blackend
   pip install -r requirements.txt
   ```

3. 运行开发服务器：
   ```bash
   python manage.py runserver
   ```

### 前端开发环境

1. 安装依赖：
   ```bash
   cd frontend
   npm install
   ```

2. 运行开发服务器：
   ```bash
   npm run dev
   ```

## 功能模块

- **测试用例管理**：创建、编辑和管理测试用例
- **API测试**：执行和验证API请求
- **测试计划**：组织和执行测试计划
- **测试结果**：查看和分析测试结果

## 贡献指南

欢迎提交Pull Request。请确保代码风格一致并通过所有测试。