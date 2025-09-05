# 📦 依赖管理

## 单一requirements.txt

项目使用一个统一的 `requirements.txt` 文件管理所有依赖，简化维护工作。

### 🚀 快速开始

```bash
# 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 2. 安装所有依赖
pip install -r requirements.txt

# 3. 数据库迁移
python manage.py migrate

# 4. 启动开发服务器
python manage.py runserver
```

### 📋 依赖包含

- **Django核心**：Web框架和REST API
- **测试框架**：pytest系列，支持TDD开发
- **代码质量**：flake8, black代码检查和格式化
- **开发工具**：ipython, ipdb调试工具
- **生产部署**：gunicorn, whitenoise, PostgreSQL

### 🎯 一键启动

使用快速启动脚本：
```bash
scripts\dev\quick-start.bat
```

该脚本会自动：
- 检查并激活虚拟环境
- 智能检查依赖是否需要安装
- 运行数据库迁移
- 启动Django开发服务器

### 🧪 运行测试

```bash
# 运行所有测试
python run_tests.py

# 运行特定模块
python run_tests.py --modules api_test

# 运行单元测试
python run_tests.py --type unit
```

### 💡 最佳实践

1. **虚拟环境隔离**：始终在虚拟环境中工作
2. **依赖锁定**：使用固定版本号确保环境一致性
3. **按需安装**：启动脚本智能检查，避免重复安装
4. **专注开发**：所有必需工具一次性安装完成