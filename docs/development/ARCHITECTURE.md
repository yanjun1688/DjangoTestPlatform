# Django测试平台架构文档

## 📋 目录
- [系统概述](#系统概述)
- [技术架构](#技术架构)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
- [数据流程](#数据流程)
- [API设计](#api设计)
- [数据库设计](#数据库设计)
- [安全架构](#安全架构)

## 🎯 系统概述

### 项目背景
Django测试平台是一个基于Django后端和React前端的综合性API测试平台，旨在为开发者和测试人员提供完整的API测试解决方案。

### 核心功能
- **API定义管理**: 支持配置请求方法、URL、Headers、Body等
- **测试用例管理**: 支持断言、变量提取、数据驱动测试
- **测试计划编排**: 将多个测试用例组织成可执行的测试套件
- **自动化执行**: 一键运行测试计划并获取实时结果
- **详细报告**: 生成包含统计信息和单条结果的测试报告
- **Mock服务**: 模拟第三方或未完成的API接口
- **用户管理**: 基础的用户认证与权限控制

### 目标用户
- 开发者：API开发和自测
- 测试工程师：接口测试和自动化
- QA团队：质量保证和回归测试

## 🏗️ 技术架构

### 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Browser Client                            │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                  Nginx (Reverse Proxy)                      │
│  - Static File Serving                                      │
│  - Load Balancing                                           │
│  - SSL Termination                                          │
└─────────────────┬───────────────────┬───────────────────────┘
                  │                   │
        Frontend  │                   │ Backend API
┌─────────────────▼─────────────────┐ │
│        React Frontend             │ │
│  - Vite Build Tool                │ │
│  - Ant Design UI                  │ │
│  - API Client (Axios)             │ │
│  - State Management               │ │
└───────────────────────────────────┘ │
                                      │
┌─────────────────────────────────────▼───────────────────────┐
│                Django Backend                               │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐   │
│  │   Django REST   │ │   Business   │ │   Data Access   │   │
│  │   Framework     │ │   Logic      │ │   Layer        │   │
│  │   (Views)       │ │  (Services)  │ │   (Models)     │   │
│  └─────────────────┘ └──────────────┘ └─────────────────┘   │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐   │
│  │   Authentication│ │   Mock       │ │   File Storage  │   │
│  │   & Permission  │ │   Server     │ │   Management    │   │
│  └─────────────────┘ └──────────────┘ └─────────────────┘   │
└─────────────────────────────────────┬───────────────────────┘
                                      │
┌─────────────────────────────────────▼───────────────────────┐
│                 Data Layer                                  │
│  ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐   │
│  │    SQLite       │ │    File      │ │     Redis       │   │
│  │  (Development)  │ │   Storage    │ │   (Optional)    │   │
│  │   PostgreSQL    │ │              │ │                 │   │
│  │  (Production)   │ │              │ │                 │   │
│  └─────────────────┘ └──────────────┘ └─────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈
- **后端**: Django 4.2+, Django REST Framework, Python 3.11+
- **前端**: React 18+, Vite, Ant Design, TypeScript/JavaScript
- **数据库**: SQLite (开发), PostgreSQL (生产)
- **缓存**: Redis (可选)
- **Web服务器**: Nginx + Gunicorn
- **测试框架**: Pytest (后端), Vitest (前端)

### 架构模式
- **前后端分离**: React前端 + Django API后端
- **RESTful API**: 标准化的API接口设计
- **MVC模式**: Django后端采用Model-View-Controller模式
- **组件化开发**: React组件化前端开发
- **分层架构**: 表现层、业务层、数据访问层

## 📂 目录结构

### 项目根目录
```
DjangoTestPlatform/
├── backend/                    # Django后端
├── frontend/                   # React前端
├── scripts/                    # 管理脚本
│   ├── dev/                   # 开发脚本
│   ├── test/                  # 测试脚本
│   ├── build/                 # 构建脚本
│   └── utils/                 # 工具脚本
├── docs/                      # 项目文档
│   ├── api/                   # API文档
│   ├── deployment/            # 部署文档
│   ├── development/           # 开发文档
│   └── user-guide/            # 用户指南
├── deployment/                # 部署配置
│   ├── docker/               # Docker配置
│   ├── nginx/                # Nginx配置
│   └── systemd/              # 系统服务配置
├── data/                     # 数据目录
│   ├── fixtures/             # 初始数据
│   ├── backups/              # 数据备份
│   └── uploads/              # 用户上传
└── temp/                     # 临时文件
```

### 后端目录结构
```
backend/
├── manage.py                  # Django管理脚本
├── requirements.txt           # Python依赖
├── .env.example              # 环境变量模板
├── test_platform/           # Django项目配置
│   ├── settings.py          # 设置文件
│   ├── urls.py             # 根URL配置
│   ├── wsgi.py             # WSGI配置
│   └── asgi.py             # ASGI配置
├── api_test/               # API测试核心模块
│   ├── models.py           # 数据模型
│   ├── views.py            # API视图
│   ├── serializers.py      # 序列化器
│   ├── services.py         # 业务逻辑
│   ├── urls.py             # URL配置
│   └── tests/              # 单元测试
├── testcases/              # 测试用例管理
├── user_management/        # 用户管理
├── reports/                # 报告生成
├── mock_server/            # Mock服务
├── comments/               # 评论系统
├── environments/           # 环境管理
├── static/                 # 静态文件
├── media/                  # 媒体文件
└── tests/                  # 集成测试
```

### 前端目录结构
```
frontend/
├── src/
│   ├── components/         # 可复用组件
│   │   ├── common/        # 通用组件
│   │   ├── layout/        # 布局组件
│   │   └── business/      # 业务组件
│   ├── pages/             # 页面组件
│   │   ├── auth/          # 认证页面
│   │   ├── dashboard/     # 仪表板
│   │   ├── test-management/ # 测试管理
│   │   ├── reports/       # 报告页面
│   │   └── settings/      # 设置页面
│   ├── hooks/             # React Hooks
│   ├── services/          # API服务层
│   │   ├── api/          # API调用
│   │   └── utils/        # 工具函数
│   ├── store/             # 状态管理
│   ├── utils/             # 通用工具
│   ├── styles/            # 样式文件
│   └── tests/             # 前端测试
├── public/                # 公共资源
├── .env.example          # 前端环境变量模板
├── package.json          # 项目配置
├── vite.config.js        # Vite配置
└── vitest.config.js      # 测试配置
```

## 🔧 核心模块

### 1. API测试模块 (api_test)
**功能**: 核心测试执行引擎
- `models.py`: API定义、测试用例、测试结果数据模型
- `services.py`: 测试执行逻辑、断言处理、变量提取
- `views.py`: RESTful API接口
- `serializers.py`: 数据序列化和验证

**关键组件**:
- `ApiDefinition`: API接口定义
- `ApiTestCase`: 测试用例
- `TestRun`: 测试执行记录
- `ApiTestResult`: 测试结果

### 2. 测试用例管理 (testcases)
**功能**: 测试用例和测试数据管理
- 测试用例的CRUD操作
- 测试数据文件管理
- 测试用例分类和标签

### 3. 用户管理 (user_management)
**功能**: 用户认证和权限控制
- 用户注册和登录
- 权限分配和管理
- 用户配置文件

### 4. 报告模块 (reports)
**功能**: 测试报告生成和展示
- 测试结果统计
- 图表生成
- 报告导出

### 5. Mock服务 (mock_server)
**功能**: API模拟服务
- Mock API配置
- 动态响应生成
- 模拟延迟和错误

### 6. 环境管理 (environments)
**功能**: 测试环境配置
- 多环境支持
- 环境变量管理
- 环境切换

### 7. 评论系统 (comments)
**功能**: 协作和反馈
- 测试用例评论
- 问题跟踪
- 团队协作

## 🔄 数据流程

### 1. 测试执行流程
```
用户操作 → 前端页面 → API调用 → Django View → 
Service层处理 → 执行HTTP请求 → 断言验证 → 
结果存储 → 响应返回 → 前端展示
```

### 2. API测试生命周期
```
1. API定义创建 → 2. 测试用例编写 → 3. 测试计划编排 → 
4. 测试执行 → 5. 结果收集 → 6. 报告生成 → 
7. 结果分析 → 8. 问题修复 → 9. 回归测试
```

### 3. 数据流图
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend   │───▶│  Database   │
│   (React)   │    │  (Django)   │    │ (SQLite/PG) │
└─────────────┘    └─────────────┘    └─────────────┘
       ▲                   │                   │
       │                   ▼                   │
       │            ┌─────────────┐            │
       │            │ HTTP Client │            │
       │            │ (Requests)  │            │
       │            └─────────────┘            │
       │                   │                   │
       │                   ▼                   │
       │            ┌─────────────┐            │
       │            │ Target API  │            │
       │            │ (External)  │            │
       │            └─────────────┘            │
       │                                       │
       └───────────────────────────────────────┘
```

## 🔌 API设计

### RESTful API规范
- 使用标准HTTP方法 (GET, POST, PUT, DELETE)
- 统一的响应格式
- 适当的状态码使用
- API版本管理

### 核心API端点
```
# 认证相关
POST /api/auth/login/          # 用户登录
POST /api/auth/logout/         # 用户登出
POST /api/auth/register/       # 用户注册

# API定义
GET    /api/definitions/       # 获取API定义列表
POST   /api/definitions/       # 创建API定义
GET    /api/definitions/{id}/  # 获取单个API定义
PUT    /api/definitions/{id}/  # 更新API定义
DELETE /api/definitions/{id}/  # 删除API定义

# 测试用例
GET    /api/testcases/         # 获取测试用例列表
POST   /api/testcases/         # 创建测试用例
GET    /api/testcases/{id}/    # 获取单个测试用例
PUT    /api/testcases/{id}/    # 更新测试用例
DELETE /api/testcases/{id}/    # 删除测试用例

# 测试执行
POST   /api/test-runs/         # 创建测试运行
GET    /api/test-runs/{id}/    # 获取测试运行结果
POST   /api/execute/           # 执行单个测试用例

# 报告
GET    /api/reports/           # 获取报告列表
GET    /api/reports/{id}/      # 获取报告详情

# Mock服务
GET    /api/mocks/             # 获取Mock配置列表
POST   /api/mocks/             # 创建Mock配置
```

### 响应格式标准
```json
// 成功响应
{
  "code": 200,
  "message": "Success",
  "data": {
    // 响应数据
  }
}

// 错误响应
{
  "code": 400,
  "message": "Error message",
  "errors": {
    "field": ["error details"]
  }
}

// 分页响应
{
  "code": 200,
  "message": "Success",
  "data": {
    "count": 100,
    "next": "http://api/endpoint/?page=2",
    "previous": null,
    "results": [
      // 数据项
    ]
  }
}
```

## 🗄️ 数据库设计

### 核心数据表

#### API定义表 (api_definitions)
```sql
CREATE TABLE api_definitions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    method VARCHAR(10) NOT NULL,
    url TEXT NOT NULL,
    headers TEXT,
    params TEXT,
    body TEXT,
    description TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by_id INTEGER REFERENCES auth_user(id)
);
```

#### 测试用例表 (test_cases)
```sql
CREATE TABLE test_cases (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    api_definition_id INTEGER REFERENCES api_definitions(id),
    test_data TEXT,
    assertions TEXT,
    variables TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by_id INTEGER REFERENCES auth_user(id)
);
```

#### 测试运行表 (test_runs)
```sql
CREATE TABLE test_runs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200),
    status VARCHAR(20) DEFAULT 'running',
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    created_by_id INTEGER REFERENCES auth_user(id)
);
```

#### 测试结果表 (test_results)
```sql
CREATE TABLE test_results (
    id SERIAL PRIMARY KEY,
    test_run_id INTEGER REFERENCES test_runs(id),
    test_case_id INTEGER REFERENCES test_cases(id),
    status VARCHAR(20),
    response_time DECIMAL,
    response_data TEXT,
    error_message TEXT,
    created_at TIMESTAMP
);
```

### 数据库关系图
```
┌─────────────────┐     ┌─────────────────┐
│   auth_user     │────▶│ api_definitions │
│                 │     │                 │
└─────────────────┘     └─────────┬───────┘
                                  │
                        ┌─────────▼───────┐
                        │   test_cases    │
                        │                 │
                        └─────────┬───────┘
                                  │
┌─────────────────┐     ┌─────────▼───────┐
│   test_runs     │◀────│  test_results   │
│                 │     │                 │
└─────────────────┘     └─────────────────┘
```

## 🔒 安全架构

### 认证和授权
- **JWT Token**: 基于Token的无状态认证
- **Session管理**: Django Session框架
- **权限控制**: 基于角色的访问控制 (RBAC)

### 数据安全
- **输入验证**: DRF序列化器验证
- **SQL注入防护**: Django ORM参数化查询
- **XSS防护**: 前端数据转义和Content Security Policy
- **CSRF防护**: Django CSRF Token机制

### API安全
- **Rate Limiting**: API调用频率限制
- **HTTPS强制**: 生产环境强制HTTPS
- **CORS配置**: 跨域请求控制
- **敏感数据加密**: 密码等敏感信息加密存储

### 部署安全
- **环境变量**: 敏感配置通过环境变量管理
- **文件权限**: 适当的文件系统权限设置
- **防火墙配置**: 仅开放必要端口
- **SSL证书**: 使用有效的SSL证书

## 📈 性能和可扩展性

### 性能优化策略
- **数据库优化**: 索引优化、查询优化
- **缓存机制**: Redis缓存热点数据
- **静态文件优化**: CDN分发、Gzip压缩
- **代码分割**: 前端按需加载

### 可扩展性设计
- **水平扩展**: 支持多实例部署
- **数据库分离**: 读写分离支持
- **微服务化**: 模块化设计便于服务拆分
- **容器化**: Docker支持容器化部署

### 监控和日志
- **应用监控**: 系统性能监控
- **错误跟踪**: 异常信息收集
- **日志管理**: 结构化日志记录
- **健康检查**: 服务健康状态监控

---

## 📝 维护说明

此文档应定期更新以反映系统架构的变更。建议：
- 每次重大功能更新时更新相关章节
- 每季度进行一次完整的文档审查
- 新团队成员入职时使用此文档进行架构介绍

**文档版本**: v1.0  
**最后更新**: 2025-09-05  
**维护者**: 开发团队