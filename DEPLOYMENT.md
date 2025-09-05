# 部署指南

## 1. 生产环境部署

### 1.1 系统要求

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+ (推荐) 或 SQLite 3.8+
- Nginx (推荐)
- Redis (可选，用于缓存)

### 1.2 环境准备

```bash
# 创建项目目录
sudo mkdir -p /opt/django-test-platform
cd /opt/django-test-platform

# 克隆项目
git clone <repository-url> .

# 创建用户
sudo adduser --system --group --home /opt/django-test-platform testplatform
sudo chown -R testplatform:testplatform /opt/django-test-platform
```

### 1.3 后端部署

```bash
# 切换到项目用户
sudo -u testplatform -i
cd /opt/django-test-platform/blackend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件，设置生产环境配置

# 数据库迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件
python manage.py collectstatic --noinput

# 测试启动
python manage.py runserver 0.0.0.0:8000
```

### 1.4 前端部署

```bash
# 安装依赖
cd /opt/django-test-platform/frontend
npm install

# 创建生产环境配置
echo "VITE_API_URL=https://your-domain.com" > .env.production

# 构建生产版本
npm run build

# 部署到Nginx
sudo cp -r dist/* /var/www/html/
```

### 1.5 Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
    
    # API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态文件
    location /static/ {
        alias /opt/django-test-platform/blackend/staticfiles/;
    }
    
    # 媒体文件
    location /media/ {
        alias /opt/django-test-platform/blackend/media/;
    }
}
```

### 1.6 Systemd 服务配置

```ini
# /etc/systemd/system/django-test-platform.service
[Unit]
Description=Django Test Platform
After=network.target

[Service]
Type=exec
User=testplatform
Group=testplatform
WorkingDirectory=/opt/django-test-platform/blackend
Environment=PATH=/opt/django-test-platform/blackend/venv/bin
ExecStart=/opt/django-test-platform/blackend/venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    test_platform.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable django-test-platform
sudo systemctl start django-test-platform
sudo systemctl status django-test-platform
```

## 2. 数据库配置

### 2.1 PostgreSQL 配置

```sql
-- 创建数据库和用户
CREATE DATABASE test_platform_db;
CREATE USER test_platform_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE test_platform_db TO test_platform_user;
```

环境变量配置：
```bash
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=test_platform_db
DATABASE_USER=test_platform_user
DATABASE_PASSWORD=your_password
DATABASE_HOST=localhost
DATABASE_PORT=5432
```

### 2.2 数据备份策略

```bash
# 每日备份脚本
#!/bin/bash
# /opt/scripts/backup_db.sh

BACKUP_DIR="/opt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# PostgreSQL备份
pg_dump -h localhost -U test_platform_user test_platform_db > $BACKUP_DIR/db_backup_$DATE.sql

# 保留最近30天的备份
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete

# 备份媒体文件
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz /opt/django-test-platform/blackend/media/
```

设置定时任务：
```bash
# 添加到crontab
0 2 * * * /opt/scripts/backup_db.sh
```

## 3. 监控和日志

### 3.1 日志配置

生产环境日志配置（添加到settings.py）：
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django-test-platform/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/django-test-platform/error.log',
            'maxBytes': 1024 * 1024 * 10,  # 10 MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'api_test': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 3.2 系统监控

使用systemctl监控服务状态：
```bash
# 检查服务状态
sudo systemctl status django-test-platform

# 查看日志
sudo journalctl -u django-test-platform -f

# 重启服务
sudo systemctl restart django-test-platform
```

### 3.3 性能监控

安装和配置Django Debug Toolbar（仅开发环境）：
```bash
pip install django-debug-toolbar
```

## 4. 安全配置

### 4.1 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 4.2 SSL证书配置

使用Let's Encrypt获取免费SSL证书：
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 4.3 Django安全设置

生产环境settings.py安全配置：
```python
# 安全设置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# HTTPS强制
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 5. 故障排除

### 5.1 常见问题

1. **数据库连接错误**
   - 检查数据库服务状态
   - 验证环境变量配置
   - 检查网络连接

2. **静态文件404错误**
   - 运行 `python manage.py collectstatic`
   - 检查Nginx配置
   - 验证文件权限

3. **API请求超时**
   - 检查后端服务状态
   - 增加Nginx代理超时设置
   - 检查防火墙配置

### 5.2 性能优化

1. **数据库优化**
   - 添加适当的索引
   - 使用查询优化
   - 定期清理过期数据

2. **缓存配置**
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

3. **静态文件优化**
   - 启用Gzip压缩
   - 使用CDN
   - 设置合适的缓存头

## 6. 维护计划

### 6.1 定期维护任务

- **每日**: 检查系统日志、数据备份
- **每周**: 检查磁盘空间、更新依赖
- **每月**: 安全更新、性能分析
- **每季度**: 全面系统检查、容量规划

### 6.2 更新流程

```bash
# 1. 备份数据
/opt/scripts/backup_db.sh

# 2. 停止服务
sudo systemctl stop django-test-platform

# 3. 更新代码
git pull origin main

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 5. 数据库迁移
python manage.py migrate

# 6. 重新构建前端
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/html/

# 7. 重启服务
sudo systemctl start django-test-platform

# 8. 验证更新
curl -f http://localhost/api/health/
```