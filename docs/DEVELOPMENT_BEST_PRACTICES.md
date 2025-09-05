# 开发环境最佳实践配置

## 虚拟环境管理

### 1. 推荐的虚拟环境工作流

```bash
# 首次设置（只需一次）
python -m venv .venv
.venv\Scripts\activate  # Windows
# 或 source .venv/bin/activate  # Linux/Mac

# 安装依赖（只需在依赖变更时）
pip install -r requirements.txt

# 日常开发
# 启动时只需激活虚拟环境，无需重复安装
.venv\Scripts\activate
python manage.py runserver
```

### 2. 避免依赖污染的策略

#### ✅ 推荐做法：
- 使用专用的开发虚拟环境（.venv）
- 只在依赖文件更改时重新安装
- 使用智能检查脚本（如 quick-start.bat）
- 定期清理虚拟环境：删除 .venv 文件夹重新创建

#### ❌ 避免做法：
- 每次启动都强制安装依赖
- 在系统Python环境中直接安装项目依赖
- 混用多个虚拟环境工具

### 3. 快速启动脚本

我们提供了两个启动脚本：

**quick-start.bat** - 日常开发使用
- 智能检查依赖，不强制重装
- 跳过不必要的步骤
- 快速启动服务器

**start-backend-windows.bat** - 完整设置
- 完整的环境检查和设置
- 适用于首次运行或环境重置
- 包含所有初始化步骤

### 4. 依赖管理建议

```bash
# 检查当前安装的包
pip list

# 检查过时的包
pip list --outdated

# 只在需要时更新特定包
pip install --upgrade django

# 生成当前环境的依赖文件
pip freeze > requirements-current.txt
```

### 5. 开发环境隔离

为不同项目使用不同的虚拟环境：
```
project1/
  .venv/          # 项目1的虚拟环境
  requirements.txt
  
project2/
  .venv/          # 项目2的虚拟环境  
  requirements.txt
```

这样可以避免：
- 依赖版本冲突
- 全局环境污染
- 项目间的相互影响