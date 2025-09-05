# Django测试平台部署指南

## 📋 目录
- [系统要求](#系统要求)
- [快速部署](#快速部署)
- [开发环境部署](#开发环境部署)
- [生产环境部署](#生产环境部署)
- [Docker部署](#docker部署)
- [配置管理](#配置管理)
- [监控与维护](#监控与维护)
- [故障排除](#故障排除)

## 🖥️ 系统要求

### 最小配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM或更多
- **磁盘**: 50GB SSD
- **网络**: 100Mbps带宽

### 软件依赖
- **Python**: 3.11+ (推荐3.11.9)
- **Node.js**: 18.x+ (推荐LTS版本)
- **数据库**: SQLite 3.8+ (开发) / PostgreSQL 12+ (生产)
- **Web服务器**: Nginx 1.18+ (生产环境)
- **进程管理**: systemd (Linux) / PM2 (可选)

## ⚡ 快速部署

### 一键部署脚本
```bash
# 克隆项目
git clone https://github.com/your-username/DjangoTestPlatform.git
cd DjangoTestPlatform

# 使用快速部署脚本
chmod +x scripts/build/quick-deploy.sh
./scripts/build/quick-deploy.sh
```

### Windows快速部署
```cmd
# 克隆项目
git clone https://github.com/your-username/DjangoTestPlatform.git
cd DjangoTestPlatform

# 运行Windows部署脚本
scripts\build\quick-deploy.bat
```

## 🔧 开发环境部署

### 1. 环境准备
```bash
# 检查Python版本
python --version  # 应该显示 3.11+

# 检查Node.js版本
node --version     # 应该显示 18.x+

# 检查Git
git --version
```

### 2. 项目设置
```bash
# 克隆项目
git clone https://github.com/your-username/DjangoTestPlatform.git
cd DjangoTestPlatform

# 运行环境检查
python scripts/utils/check-environment.py
```

### 3. 后端设置
```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 加载测试数据 (可选)
python manage.py loaddata fixtures/sample_data.json
```

### 4. 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env.local
# 编辑 .env.local 文件
```

### 5. 启动开发服务器
```bash
# 启动后端服务器 (终端1)
scripts/dev/start-backend.sh   # Linux/Mac
scripts\dev\start-backend.bat  # Windows

# 启动前端服务器 (终端2)
scripts/dev/start-frontend.sh  # Linux/Mac
scripts\dev\start-frontend.bat # Windows
```

### 6. 验证部署
- 后端API: http://localhost:8000
- 前端应用: http://localhost:5173
- 管理界面: http://localhost:8000/admin

## 🚀 生产环境部署

### 1. 服务器准备
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础软件
sudo apt install -y python3.11 python3.11-venv python3-pip nodejs npm nginx postgresql postgresql-contrib git supervisor

# 创建应用用户
sudo adduser --system --group --home /opt/django-test-platform testplatform
sudo mkdir -p /opt/django-test-platform
sudo chown testplatform:testplatform /opt/django-test-platform
```

### 2. 应用部署
```bash
# 切换到应用用户
sudo -u testplatform -i
cd /opt/django-test-platform

# 克隆代码
git clone https://github.com/your-username/DjangoTestPlatform.git .

# 后端部署
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 配置生产环境变量
cp .env.example .env
# 编辑 .env 文件设置生产配置:
# DEBUG=False
# ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# DATABASE_ENGINE=django.db.backends.postgresql
# 等等...

# 数据库迁移
python manage.py migrate
python manage.py collectstatic --noinput

# 前端构建
cd ../frontend
npm install
npm run build
```

### 3. PostgreSQL配置
```bash
# 切换到postgres用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE django_test_platform_db;
CREATE USER django_test_platform_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE django_test_platform_db TO django_test_platform_user;
ALTER USER django_test_platform_user CREATEDB;
\q
```

### 4. Nginx配置
```bash
# 创建Nginx配置文件
sudo nano /etc/nginx/sites-available/django-test-platform
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # 安全头设置
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # 前端静态文件
    location / {
        root /opt/django-test-platform/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
        
        # 缓存设置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Django管理界面
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Django静态文件
    location /static/ {
        alias /opt/django-test-platform/backend/staticfiles/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # 媒体文件
    location /media/ {
        alias /opt/django-test-platform/backend/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Gzip压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;
}
```

启用站点：
```bash
sudo ln -s /etc/nginx/sites-available/django-test-platform /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Systemd服务配置
```bash
# 创建systemd服务文件
sudo nano /etc/systemd/system/django-test-platform.service
```

```ini
[Unit]
Description=Django Test Platform
Documentation=https://github.com/your-username/DjangoTestPlatform
After=network.target postgresql.service

[Service]
Type=exec
User=testplatform
Group=testplatform
WorkingDirectory=/opt/django-test-platform/backend
Environment=PATH=/opt/django-test-platform/backend/.venv/bin
Environment=DJANGO_SETTINGS_MODULE=test_platform.settings
EnvironmentFile=/opt/django-test-platform/backend/.env
ExecStart=/opt/django-test-platform/backend/.venv/bin/gunicorn \
    --workers 3 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 30 \
    --keep-alive 2 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/django-test-platform/access.log \
    --error-logfile /var/log/django-test-platform/error.log \
    test_platform.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5
StandardOutput=null
StandardError=journal

[Install]
WantedBy=multi-user.target
```

创建日志目录并启动服务：
```bash
sudo mkdir -p /var/log/django-test-platform
sudo chown testplatform:testplatform /var/log/django-test-platform

sudo systemctl daemon-reload
sudo systemctl enable django-test-platform
sudo systemctl start django-test-platform
sudo systemctl status django-test-platform
```

### 6. SSL证书配置
```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 测试自动续期
sudo certbot renew --dry-run
```

## 🐳 Docker部署

### 1. Docker Compose配置
创建 `deployment/docker/docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      POSTGRES_DB: django_test_platform_db
      POSTGRES_USER: django_test_platform_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U django_test_platform_user"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../../backend
      dockerfile: ../deployment/docker/Dockerfile.backend
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      - DATABASE_ENGINE=django.db.backends.postgresql
      - DATABASE_HOST=db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ../../frontend
      dockerfile: ../deployment/docker/Dockerfile.frontend
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - static_volume:/var/www/static
      - media_volume:/var/www/media
      - frontend_dist:/var/www/html
    depends_on:
      - backend
      - frontend

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
  frontend_dist:
```

### 2. Docker镜像构建
后端Dockerfile (`deployment/docker/Dockerfile.backend`):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 收集静态文件
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "test_platform.wsgi:application"]
```

前端Dockerfile (`deployment/docker/Dockerfile.frontend`):
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# 复制package.json文件
COPY package*.json ./

# 安装依赖
RUN npm ci --only=production

# 复制源代码
COPY . .

# 构建应用
RUN npm run build

FROM nginx:alpine

# 复制构建结果
COPY --from=builder /app/dist /var/www/html

# 复制Nginx配置
COPY deployment/docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 3. Docker部署命令
```bash
# 进入部署目录
cd deployment/docker

# 创建环境变量文件
cp .env.example .env
# 编辑 .env 文件

# 构建并启动服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 执行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

## ⚙️ 配置管理

### 环境变量配置

#### 后端配置 (backend/.env)
```bash
# Django基础配置
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,localhost

# 数据库配置
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=django_test_platform_db
DATABASE_USER=django_test_platform_user
DATABASE_PASSWORD=your_secure_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

# Redis配置 (可选)
REDIS_URL=redis://localhost:6379/0

# CORS配置
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com

# 邮件配置 (可选)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# 文件上传配置
MAX_UPLOAD_SIZE=10485760  # 10MB
MEDIA_ROOT=/opt/django-test-platform/backend/media

# 日志配置
LOG_LEVEL=INFO
LOG_DIR=/var/log/django-test-platform

# 安全配置
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### 前端配置 (frontend/.env.production)
```bash
# API配置
VITE_API_BASE_URL=https://your-domain.com
VITE_API_TIMEOUT=30000

# 应用配置
VITE_APP_TITLE=Django测试平台
VITE_APP_VERSION=1.0.0

# 功能开关
VITE_ENABLE_MOCK=false
VITE_ENABLE_DEBUG=false

# 监控配置 (可选)
VITE_SENTRY_DSN=your-sentry-dsn
VITE_ANALYTICS_ID=your-analytics-id
```

### 多环境配置管理
```bash
# 开发环境
backend/.env.development
frontend/.env.development

# 测试环境
backend/.env.testing  
frontend/.env.testing

# 生产环境
backend/.env.production
frontend/.env.production
```

## 📊 监控与维护

### 1. 日志管理
```bash
# 查看应用日志
sudo journalctl -u django-test-platform -f

# 查看Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 查看应用自定义日志
sudo tail -f /var/log/django-test-platform/access.log
sudo tail -f /var/log/django-test-platform/error.log
```

### 2. 性能监控
```bash
# 系统资源监控
htop
iostat -x 1
free -h
df -h

# 数据库监控 (PostgreSQL)
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# 应用性能监控
curl -f http://localhost:8000/api/health/
```

### 3. 数据备份策略
```bash
#!/bin/bash
# scripts/build/backup.sh

# 配置
BACKUP_DIR="/opt/backups/django-test-platform"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# 创建备份目录
mkdir -p $BACKUP_DIR

# 数据库备份
pg_dump -h localhost -U django_test_platform_user django_test_platform_db \
    | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# 媒体文件备份
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz \
    /opt/django-test-platform/backend/media/

# 清理过期备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "media_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
```

设置定时任务：
```bash
# 编辑crontab
sudo crontab -e

# 添加备份任务 (每天凌晨2点)
0 2 * * * /opt/django-test-platform/scripts/build/backup.sh >> /var/log/backup.log 2>&1
```

### 4. 健康检查
创建健康检查脚本 (`scripts/utils/health-check.sh`):
```bash
#!/bin/bash

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "=== Django测试平台健康检查 ==="

# 检查后端服务
echo -n "后端服务状态: "
if curl -f -s http://localhost:8000/api/health/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 正常${NC}"
else
    echo -e "${RED}✗ 异常${NC}"
fi

# 检查前端服务
echo -n "前端服务状态: "
if curl -f -s http://localhost/ > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 正常${NC}"
else
    echo -e "${RED}✗ 异常${NC}"
fi

# 检查数据库连接
echo -n "数据库连接: "
if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓ 正常${NC}"
else
    echo -e "${RED}✗ 异常${NC}"
fi

# 检查磁盘空间
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
echo -n "磁盘使用率: $DISK_USAGE% "
if [ $DISK_USAGE -lt 80 ]; then
    echo -e "${GREEN}✓ 正常${NC}"
elif [ $DISK_USAGE -lt 90 ]; then
    echo -e "${YELLOW}⚠ 警告${NC}"
else
    echo -e "${RED}✗ 危险${NC}"
fi

# 检查内存使用
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.1f", $3*100/$2}')
echo "内存使用率: ${MEMORY_USAGE}%"
```

## 🔧 故障排除

### 常见问题及解决方案

#### 1. 数据库连接错误
**症状**: `django.db.utils.OperationalError: could not connect to server`

**解决方案**:
```bash
# 检查PostgreSQL服务状态
sudo systemctl status postgresql

# 检查数据库配置
cat backend/.env | grep DATABASE

# 测试数据库连接
sudo -u postgres psql -c "\l"

# 重启数据库服务
sudo systemctl restart postgresql
```

#### 2. 静态文件404错误
**症状**: CSS/JS文件无法加载

**解决方案**:
```bash
# 重新收集静态文件
cd backend
source .venv/bin/activate
python manage.py collectstatic --noinput

# 检查Nginx配置
sudo nginx -t
sudo systemctl reload nginx

# 检查文件权限
ls -la /opt/django-test-platform/backend/staticfiles/
```

#### 3. 前端构建失败
**症状**: npm run build 失败

**解决方案**:
```bash
# 清理node_modules
cd frontend
rm -rf node_modules package-lock.json

# 重新安装依赖
npm install

# 检查Node.js版本
node --version  # 应该是18.x+

# 重新构建
npm run build
```

#### 4. 服务启动失败
**症状**: systemctl start django-test-platform 失败

**解决方案**:
```bash
# 查看详细错误信息
sudo journalctl -u django-test-platform -n 50

# 检查配置文件
sudo systemctl cat django-test-platform

# 手动测试启动
sudo -u testplatform -i
cd /opt/django-test-platform/backend
source .venv/bin/activate
gunicorn --bind 127.0.0.1:8000 test_platform.wsgi:application
```

### 性能问题诊断

#### 1. 应用响应慢
```bash
# 检查系统资源
htop
iostat -x 1

# 检查数据库查询
# 在Django中启用查询日志
# settings.py中添加:
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# 分析慢查询
sudo -u postgres psql -c "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;"
```

#### 2. 内存使用过高
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head

# 调整Gunicorn worker数量
# 编辑 /etc/systemd/system/django-test-platform.service
# 修改 --workers 参数

sudo systemctl daemon-reload
sudo systemctl restart django-test-platform
```

### 更新部署流程
```bash
#!/bin/bash
# scripts/build/deploy-update.sh

set -e

echo "开始更新部署..."

# 1. 备份当前版本
./scripts/build/backup.sh

# 2. 停止服务
sudo systemctl stop django-test-platform

# 3. 更新代码
git fetch origin
git checkout main
git pull origin main

# 4. 更新后端
cd backend
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
cd ..

# 5. 更新前端
cd frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/
cd ..

# 6. 重启服务
sudo systemctl start django-test-platform
sudo systemctl reload nginx

# 7. 健康检查
sleep 10
./scripts/utils/health-check.sh

echo "更新部署完成！"
```

## 📋 部署检查清单

### 生产环境部署前检查
- [ ] 服务器硬件配置满足要求
- [ ] 操作系统更新到最新版本
- [ ] 防火墙配置正确
- [ ] SSL证书配置完成
- [ ] 数据库备份策略配置
- [ ] 监控和日志配置完成
- [ ] 环境变量安全配置
- [ ] 性能测试通过
- [ ] 安全测试通过

### 部署后验证
- [ ] 前端页面正常访问
- [ ] API接口正常响应
- [ ] 用户登录功能正常
- [ ] 数据库读写正常
- [ ] 静态文件加载正常
- [ ] HTTPS重定向正常
- [ ] 邮件发送功能正常 (如果配置)
- [ ] 定时任务运行正常
- [ ] 日志记录正常

---

## 📞 技术支持

如有部署问题，请：
1. 查看本文档的故障排除章节
2. 检查应用日志和系统日志
3. 在项目Issue中搜索相关问题
4. 创建新的Issue并提供详细的错误信息

**文档版本**: v1.0  
**最后更新**: 2025-09-05  
**维护者**: 开发团队