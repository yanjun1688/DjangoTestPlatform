# API 文档

## 概述

Django测试平台提供RESTful API接口，支持完整的API测试功能。

## 基础信息

- **基础URL**: `http://localhost:8000/api/`
- **认证方式**: Token认证
- **数据格式**: JSON
- **字符编码**: UTF-8

## 认证

### 获取Token
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "your_username",
  "password": "your_password"
}
```

### 使用Token
```http
Authorization: Token your_token_here
```

## 核心API端点

### 用户认证
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `POST /api/auth/register/` - 用户注册

### API定义管理
- `GET /api/definitions/` - 获取API定义列表
- `POST /api/definitions/` - 创建API定义
- `GET /api/definitions/{id}/` - 获取单个API定义
- `PUT /api/definitions/{id}/` - 更新API定义
- `DELETE /api/definitions/{id}/` - 删除API定义

### 测试用例管理
- `GET /api/testcases/` - 获取测试用例列表
- `POST /api/testcases/` - 创建测试用例
- `GET /api/testcases/{id}/` - 获取单个测试用例
- `PUT /api/testcases/{id}/` - 更新测试用例
- `DELETE /api/testcases/{id}/` - 删除测试用例

### 测试执行
- `POST /api/test-runs/` - 创建测试运行
- `GET /api/test-runs/{id}/` - 获取测试运行结果
- `POST /api/execute/` - 执行单个测试用例

### 报告
- `GET /api/reports/` - 获取报告列表
- `GET /api/reports/{id}/` - 获取报告详情

## 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "Success",
  "data": {
    // 响应数据
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Error message",
  "errors": {
    "field": ["error details"]
  }
}
```

## 状态码

- `200` - 成功
- `201` - 创建成功
- `400` - 请求错误
- `401` - 未授权
- `403` - 禁止访问
- `404` - 资源不存在
- `500` - 服务器错误

## 使用示例

### 创建API定义
```bash
curl -X POST http://localhost:8000/api/definitions/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "获取用户信息",
    "method": "GET",
    "url": "https://api.example.com/users/1",
    "headers": {"Content-Type": "application/json"},
    "description": "获取用户详细信息"
  }'
```

### 执行测试用例
```bash
curl -X POST http://localhost:8000/api/execute/ \
  -H "Authorization: Token your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": 1,
    "environment_id": 1
  }'
```