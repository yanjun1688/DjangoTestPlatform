# 开发指南

## 开发环境配置

### 前置要求
- Python 3.11+
- Node.js 18+
- Git

### 快速开始
```bash
# 克隆项目
git clone https://github.com/your-username/DjangoTestPlatform.git
cd DjangoTestPlatform

# 环境检查
python scripts/utils/check-environment.py

# 启动开发环境
scripts/dev/start-backend.sh   # 后端
scripts/dev/start-frontend.sh  # 前端
```

## 代码规范

### Python代码规范
- 遵循 PEP 8 标准
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查

### JavaScript代码规范
- 使用 ESLint 配置
- 使用 Prettier 进行格式化
- 遵循 React 最佳实践

## 测试规范

### 后端测试
- 使用 Pytest 测试框架
- 测试覆盖率要求 > 80%
- 模型、视图、服务层分别测试

### 前端测试
- 使用 Vitest 测试框架
- 组件测试使用 Testing Library
- E2E测试使用 Playwright

## Git工作流

### 分支命名规范
- `feature/功能名称` - 新功能开发
- `bugfix/问题描述` - Bug修复
- `hotfix/紧急修复` - 紧急修复
- `docs/文档更新` - 文档更新

### 提交信息规范
```
类型(范围): 描述

类型包括:
- feat: 新功能
- fix: Bug修复
- docs: 文档更新
- style: 代码格式化
- refactor: 重构
- test: 测试相关
- chore: 构建过程或辅助工具的变动
```

## 调试指南

### 后端调试
- 使用 Django Debug Toolbar
- 配置日志记录
- 使用 pdb 进行断点调试

### 前端调试
- 使用 React Developer Tools
- 浏览器开发者工具
- 网络请求调试

## 性能优化

### 后端优化
- 数据库查询优化
- 缓存策略
- API响应时间监控

### 前端优化
- 代码分割
- 懒加载
- 图片优化
- 缓存策略