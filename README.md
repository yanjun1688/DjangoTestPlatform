# Django测试平台

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2+-green.svg)
![React](https://img.shields.io/badge/React-18+-lightblue.svg)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Build](https://img.shields.io/badge/Build-Stable-success.svg)

**🚀 现代化企业级API测试管理平台**

*集API定义、测试用例管理、自动化执行、报告分析于一体的完整测试解决方案*

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [技术栈](#️-技术栈) • [部署指南](#-部署指南) • [API文档](#-api文档)

</div>

---

## 📖 项目简介

Django测试平台是一个现代化的企业级API测试管理系统，基于Django REST Framework和React构建。为开发团队、测试工程师和QA团队提供从API定义到测试报告的完整测试生命周期管理。

### 🎯 核心价值
- **🎯 统一测试管理**: 集中管理API定义、测试用例和测试数据
- **🚀 自动化执行**: 一键运行测试计划，生成详细测试报告
- **🎭 Mock服务**: 内置Mock服务器，支持API开发和联调
- **👥 团队协作**: 评论系统、通知机制，支持团队协作
- **📊 可视化报告**: 丰富的统计图表和趋势分析

## ✨ 功能特性

<table>
<tr>
<td width="50%">

### 🔧 核心功能
- **API管理**: RESTful API完整定义和管理
- **测试用例**: 可视化编辑，支持断言和数据驱动
- **自动化执行**: 批量执行和实时监控
- **环境管理**: 多环境配置和变量管理
- **Mock服务**: 动态API模拟和请求记录
- **报告分析**: 详细报告和统计分析

</td>
<td width="50%">

### 🌟 高级特性
- **树形用例结构**: 基于MPTT的层级管理
- **数据驱动测试**: CSV/JSON数据文件支持
- **实时通知**: @提及和通知系统
- **权限控制**: 细粒度权限管理
- **版本控制**: 测试用例版本管理
- **跨平台兼容**: Windows/Linux/macOS支持

</td>
</tr>
</table>

## 🚀 快速开始

### 系统要求
- **Python**: 3.11+ 
- **Node.js**: 18.x+
- **Git**: 2.x+

### 一键启动

```bash
# 克隆项目
git clone https://github.com/yourusername/DjangoTestPlatform.git
cd DjangoTestPlatform

# 后端启动
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/Mac  
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 前端启动 (新终端)
cd frontend
npm install
npm run dev
```

### 访问应用
- **前端**: http://localhost:5173
- **后端API**: http://localhost:8000
- **管理后台**: http://localhost:8000/admin

## 📁 项目结构

```
DjangoTestPlatform/
├── 📁 backend/               # Django后端
│   ├── 📁 api_test/         # API测试核心模块
│   ├── 📁 testcases/        # 测试用例管理
│   ├── 📁 user_management/  # 用户权限管理
│   ├── 📁 environments/     # 环境变量管理
│   ├── 📁 mock_server/      # Mock服务模块
│   ├── 📁 comments/         # 评论通知系统
│   ├── 📁 reports/          # 测试报告模块
│   └── 📁 tests/           # 统一测试目录
├── 📁 frontend/             # React前端
│   ├── 📁 src/components/   # UI组件
│   ├── 📁 src/pages/       # 页面组件
│   └── 📁 src/services/    # API服务
├── 📁 scripts/             # 管理脚本
├── 📁 docs/               # 项目文档
└── 📄 README.md           # 项目说明
```

## 🛠️ 技术栈

### 后端技术
- **框架**: Django 4.2 + Django REST Framework 3.14
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **树形结构**: django-mptt 0.16.0 (MPTT算法)
- **跨域处理**: django-cors-headers 4.3.1
- **版本控制**: django-reversion 5.0.1
- **环境配置**: python-dotenv 1.0.1
- **HTTP请求**: requests 2.31.0
- **测试框架**: pytest + pytest-django + factory-boy
- **代码质量**: flake8 + black
- **API文档**: drf-spectacular 0.27.0
- **生产部署**: gunicorn + whitenoise

### 前端技术
- **框架**: React 18.3 + Vite 6.1
- **UI库**: Ant Design 5.25 + @ant-design/icons 6.0
- **路由**: React Router DOM 6.0
- **HTTP客户端**: Axios 1.9
- **图表库**: Chart.js 4.4 + react-chartjs-2 5.2
- **拖拽**: React Beautiful DnD 13.1
- **工具**: prop-types + browserslist + bootstrap
- **开发工具**: ESLint 9.19 + Vitest 2.0 + jsdom

### 开发与测试
- **测试覆盖**: 单元测试 + 集成测试 + 端到端测试
- **代码规范**: ESLint + Black + Flake8
- **版本控制**: Git + GitHub
- **环境隔离**: Python虚拟环境 + Node.js包管理
- **构建工具**: Vite (前端) + Django管理命令 (后端)

## 📊 系统统计

- **📦 核心模块**: 7个业务模块
- **🗃️ 数据模型**: 21个核心模型
- **🔌 API接口**: 60+ RESTful接口
- **🧪 测试覆盖**: 180个测试用例
- **📝 代码量**: ~15,000行

## 🚀 部署指南

### 快速启动脚本
```bash
# Windows 用户
scripts\dev\quick-start.bat

# Linux/macOS 用户
chmod +x scripts/dev/quick-start.sh
./scripts/dev/quick-start.sh
```

### 手动部署

#### 开发环境
```bash
# 1. 后端服务
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 2. 前端服务 (新终端)
cd frontend
npm install
npm run dev
```

#### 生产环境
```bash
# 使用Gunicorn + Nginx
cd backend
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
gunicorn test_platform.wsgi:application --bind 0.0.0.0:8000

# 前端构建
cd frontend
npm run build
# 将 dist/ 目录部署到 Nginx 静态文件服务器
```

### 环境检查
```bash
# 检查系统环境
python scripts/utils/check-environment.py

# 验证TDD设置
python scripts/dev/verify_tdd_setup.py
```

## 📚 文档与资源

- [📄 项目文档](docs/) - 完整的项目文档
- [🛠️ API文档](http://localhost:8000/api/schema/swagger-ui/) - 交互式API文档
- [🧪 测试指南](backend/tests/) - 测试执行指南
- [📊 架构设计](docs/development/ARCHITECTURE.md) - 系统架构设计
- [🚀 部署指南](docs/deployment/) - 生产部署详细指南

## 🔧 常见问题

<details>
<summary><b>🔴 端口占用问题</b></summary>

**问题**: `Error: That port is already in use`

**解决方案**:
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/macOS
lsof -i :8000
kill -9 <PID>
```
</details>

<details>
<summary><b>🔴 依赖安装失败</b></summary>

**Python依赖**:
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**Node.js依赖**:
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```
</details>

<details>
<summary><b>🔴 数据库问题</b></summary>

**重置数据库**:
```bash
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```
</details>

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 许可证

本项目采用 [MIT许可证](LICENSE)

## 🙏 致谢

感谢以下开源项目：
- [Django](https://djangoproject.com/) - 强大的Python Web框架
- [React](https://reactjs.org/) - 现代化前端框架
- [Ant Design](https://ant.design/) - 企业级UI组件库

---

<div align="center">

**如果这个项目对您有帮助，请给它一个 ⭐️**

Made with ❤️ by Django Test Platform Team

</div>