# Django测试平台

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2+-green.svg)
![React](https://img.shields.io/badge/React-18+-lightblue.svg)
![Tests](https://img.shields.io/badge/Tests-180%20passed-brightgreen.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**企业级API测试平台 - 完整的测试解决方案**

[快速开始](#-快速开始) • [功能特性](#-功能特性) • [技术栈](#️-技术栈) • [部署](#-部署)

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
- **框架**: Django 5.2 + Django REST Framework
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **测试**: 180个单元测试用例，100%通过率
- **特性**: MPTT树形结构、版本控制、权限管理

### 前端技术
- **框架**: React 18 + TypeScript
- **构建**: Vite
- **UI库**: Ant Design
- **状态管理**: Redux Toolkit

## 📊 系统统计

- **📦 核心模块**: 7个业务模块
- **🗃️ 数据模型**: 21个核心模型
- **🔌 API接口**: 60+ RESTful接口
- **🧪 测试覆盖**: 180个测试用例
- **📝 代码量**: ~15,000行

## 🚀 部署

### 开发环境
```bash
# 后端
cd backend
python manage.py runserver

# 前端
cd frontend
npm run dev
```

### 生产环境
```bash
# 使用Docker
docker-compose up -d

# 或手动部署
# 参考 docs/deployment/README.md
```

## 📚 文档

- [📋 功能清单](backend/BACKEND_FUNCTION_LIST.md) - 完整功能列表
- [🧪 测试报告](backend/UNIT_TEST_EXECUTION_REPORT.md) - 测试执行结果
- [📊 测试总结](backend/TEST_SUMMARY.md) - 测试覆盖分析
- [🔄 更新日志](CHANGELOG.md) - 版本变更记录

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