# Django 测试平台

一个基于Django + React的测试平台，支持API测试用例管理、执行和结果查看。

## 技术栈

- 后端：Django + Django REST Framework
- 前端：React + Vite
- 数据库：SQLite (开发环境)

## 项目结构

```
DjangoTestPlatform/
├── blackend/          # Django后端
│   ├── api_test/      # API测试应用
│   ├── testcases/     # 测试用例应用
│   └── test_platform/ # Django项目配置
└── frontend/          # React前端
    └── src/
        └── pages/     # 页面组件
```

## 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

## 快速启动

### 方法1: 使用批处理文件（Windows）

1. 启动后端：
   ```bash
   start_backend.bat
   ```

2. 启动前端（新开一个命令行窗口）：
   ```bash
   start_frontend.bat
   ```

### 方法2: 手动启动

#### 后端启动

1. 进入后端目录：
   ```bash
   cd blackend
   ```

2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

3. 运行数据库迁移：
   ```bash
   python manage.py migrate
   ```

4. 启动开发服务器：
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

#### 前端启动

1. 进入前端目录：
   ```bash
   cd frontend
   ```

2. 安装依赖：
   ```bash
   npm install
   ```

3. 启动开发服务器：
   ```bash
   npm run dev
   ```

## 访问地址

- 前端: http://localhost:5173
- 后端API: http://localhost:8000
- Django管理后台: http://localhost:8000/admin

## 功能特性

### API测试管理
- API定义管理（增删改查）
- 测试用例创建和执行
- 测试结果查看和分析

### 测试用例管理
- 测试用例的层级结构管理
- 测试计划制定
- 测试结果跟踪

## 已修复的问题

1. **API路径不匹配**: 修复了前端API调用路径错误
2. **权限问题**: 开发环境允许所有用户进行CRUD操作
3. **CORS配置**: 完善了跨域请求配置
4. **React版本**: 降级到稳定版本避免兼容性问题
5. **匿名用户问题**: 修复了创建数据时匿名用户导致的错误
6. **JSON解析错误**: 添加了安全的JSON解析和验证功能
7. **日志系统**: 实现了完整的前端日志记录和调试功能
8. **界面中文化**: 将所有前端界面改为中文显示
9. **功能精简**: 删除了测试套件功能，简化系统架构

## 开发注意事项

1. 确保后端在8000端口运行
2. 前端默认在5173端口运行
3. 数据库使用SQLite，文件位于`blackend/db.sqlite3`
4. 日志文件位于`blackend/debug.log`
5. 已创建默认管理员账户：用户名 `admin`，密码 `admin123`
6. 前端日志可在 `/debug` 页面查看

## 调试功能

### 前端日志系统
- 自动记录所有API请求和响应
- 记录表单数据和用户操作
- 支持不同日志级别（DEBUG, INFO, WARN, ERROR）
- 可在调试页面实时查看日志

### 调试页面
访问 `http://localhost:5173/debug` 可以：
- 查看实时日志记录
- 过滤不同级别的日志
- 查看系统信息
- 测试日志功能

### JSON字段处理
- 自动验证JSON格式
- 提供详细的错误信息
- 支持JSON格式化和压缩

## 故障排除

### 常见问题

1. **端口被占用**: 修改`settings.py`中的端口配置
2. **CORS错误**: 检查`settings.py`中的CORS配置
3. **数据库错误**: 运行`python manage.py migrate`
4. **前端依赖问题**: 删除`node_modules`后重新安装

### 调试模式

- 后端日志级别设置为DEBUG
- 前端控制台会显示详细的错误信息
- 使用浏览器开发者工具查看网络请求

## 功能模块

- **测试用例管理**：创建、编辑和管理测试用例
- **API测试**：执行和验证API请求
- **测试计划**：组织和执行测试计划
- **测试结果**：查看和分析测试结果

## 贡献指南

欢迎提交Pull Request。请确保代码风格一致并通过所有测试。