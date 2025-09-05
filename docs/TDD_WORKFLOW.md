# TDD开发工作流指南

## 🎯 专注功能开发的TDD环境

### 环境准备（一次性设置）

```bash
# 1. 激活虚拟环境
cd backend
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. 安装依赖（仅在依赖变更时）
pip install -r requirements.txt

# 3. 数据库迁移（仅在模型变更时）
python manage.py migrate
```

### 🔄 TDD开发循环

#### 1. 快速启动开发服务器
```bash
# 使用简化的启动脚本
scripts\dev\quick-start.bat

# 或者手动启动（推荐用于开发）
cd backend
python manage.py runserver
```

#### 2. TDD循环：红-绿-重构

```bash
# 步骤1：写失败的测试（红）
# 在 backend/tests/{module}/ 下创建测试

# 步骤2：运行测试，确认失败
python run_tests.py --modules {module}

# 步骤3：写最少代码让测试通过（绿）
# 编写实现代码

# 步骤4：运行测试，确认通过
python run_tests.py --modules {module}

# 步骤5：重构代码
# 保持测试通过的前提下重构

# 步骤6：重复循环
```

### 📁 简化的项目结构

```
backend/
├── manage.py                 # Django管理脚本
├── requirements.txt          # 依赖管理
├── run_tests.py             # 统一测试管理器
├── .env.example             # 环境配置示例
├── test_platform/           # Django设置
├── {app_name}/              # 各功能模块
│   ├── models.py            # 数据模型
│   ├── views.py             # 视图逻辑  
│   ├── serializers.py       # API序列化
│   └── urls.py              # URL路由
└── tests/                   # 集中式测试目录
    ├── conftest.py          # pytest配置
    ├── utils/               # 测试工具
    └── {app_name}/          # 各模块测试
        ├── test_models.py   # 模型测试
        ├── test_views.py    # 视图测试
        └── test_services.py # 服务测试
```

### 🚀 推荐的开发命令

```bash
# 运行所有测试
python run_tests.py

# 运行特定模块测试
python run_tests.py --modules api_test

# 运行单元测试
python run_tests.py --type unit

# 快速检查（静默模式）
python run_tests.py --verbosity 0

# 列出所有测试
python run_tests.py --list
```

### 💡 TDD最佳实践

1. **测试先行**：先写测试，再写实现
2. **小步迭代**：每次只实现一个小功能
3. **频繁运行测试**：每次代码变更后立即运行相关测试
4. **保持测试简单**：一个测试只验证一个行为
5. **重构时保持测试通过**：重构代码但不改变行为

### 🔧 开发工具配置

#### VS Code 配置（推荐）
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./backend/.venv/Scripts/python.exe",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["backend/tests"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    }
}
```

#### PyCharm 配置
1. 设置项目解释器为 `backend/.venv/Scripts/python.exe`
2. 设置测试根目录为 `backend/tests`
3. 配置运行配置使用 Django 测试运行器

### 📝 提交规范

```bash
# 功能开发提交格式
git commit -m "feat: 添加用户登录功能

- 实现用户认证API
- 添加登录表单验证
- 更新相关测试用例

Tests: python run_tests.py --modules user_management"

# 测试添加提交格式  
git commit -m "test: 添加用户登录测试用例

- 测试有效登录场景
- 测试无效凭据处理
- 测试会话管理"
```

### 🎯 专注原则

1. **避免过度配置**：使用默认设置，除非有明确需求
2. **保持简单**：优先使用简单解决方案
3. **测试驱动**：让测试指导设计和实现
4. **快速反馈**：保持测试运行速度快
5. **功能完整**：每个功能都要有对应的测试覆盖