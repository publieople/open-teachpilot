# TeachPilot 安全性配置说明

## 目录

1. [环境变量安全](#环境变量安全)
2. [数据库安全](#数据库安全)
3. [API 安全](#api 安全)
4. [HTTPS 配置](#https 配置)
5. [访问控制](#访问控制)
6. [数据备份](#数据备份)

---

## 环境变量安全

### 必须配置的安全变量

```bash
# .env 文件

# 应用密钥（必须修改）
# 生成方法：openssl rand -hex 32
WEBUI_SECRET_KEY=your-secure-random-key-here

# 数据库密码（生产环境必须修改）
DB_PASSWORD=your-secure-db-password

# Redis 密码（生产环境必须修改）
REDIS_PASSWORD=your-secure-redis-password

# OpenRouter API Key
OPENROUTER_API_KEY=sk-or-v1-your-api-key

# CORS 允许的来源（生产环境必须指定具体域名）
CORS_ALLOW_ORIGIN=https://your-domain.com
```

### 密钥生成

```bash
# 生成 WEBUI_SECRET_KEY
openssl rand -hex 32

# 生成强密码
openssl rand -base64 32
```

---

## 数据库安全

### PostgreSQL 安全配置

1. **修改默认密码**
   ```bash
   # 在 docker-compose.teachpilot.prod.yaml 中
   POSTGRES_PASSWORD=your-secure-password
   ```

2. **限制网络访问**
   ```yaml
   networks:
     - teachpilot-network  # 数据库只在内部网络暴露
   ```

3. **定期备份**
   ```bash
   # 备份数据库
   docker exec teachpilot-postgres pg_dump -U teachpilot teachpilot > backup.sql
   
   # 恢复数据库
   cat backup.sql | docker exec -i teachpilot-postgres psql -U teachpilot -d teachpilot
   ```

---

## API 安全

### 速率限制

TeachPilot 内置 API 速率限制，防止滥用：

```python
# 后端配置
RATE_LIMIT_DEFAULT = "100/minute"
RATE_LIMIT_UPLOAD = "10/minute"
```

### API Key 管理

1. **不要在前端代码中硬编码 API Key**
2. **使用环境变量存储敏感密钥**
3. **定期轮换 API Key**

### CORS 配置

```bash
# 开发环境（允许所有来源）
CORS_ALLOW_ORIGIN=*

# 生产环境（必须指定具体域名）
CORS_ALLOW_ORIGIN=https://your-domain.com,https://www.your-domain.com
```

---

## HTTPS 配置

### Nginx SSL 配置

创建 `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream teachpilot {
        server teachpilot-app:8080;
    }

    # HTTP 重定向到 HTTPS
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS 配置
    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;

        # SSL 安全配置
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        # 安全头
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        location / {
            proxy_pass http://teachpilot;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

### 获取 SSL 证书

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
apt-get install certbot

# 获取证书
certbot certonly --standalone -d your-domain.com

# 证书位置
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

---

## 访问控制

### 用户角色

TeachPilot 支持以下角色：

| 角色 | 权限 |
|------|------|
| `admin` | 完全访问权限，包括用户管理、系统设置 |
| `teacher` | 创建课程、布置作业、批改作业、查看学生进度 |
| `student` | 学习课程、提交作业、查看成绩 |

### 权限配置

在管理员面板中配置用户角色和权限：

1. 进入 `设置` → `用户管理`
2. 选择用户并分配角色
3. 配置细粒度权限（可选）

### 会话安全

```bash
# 会话过期时间（秒）
SESSION_EXPIRE=86400  # 24 小时

# 强制 HTTPS Cookie
SESSION_COOKIE_SECURE=true
```

---

## 数据备份

### 自动备份脚本

创建 `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份 PostgreSQL
docker exec teachpilot-postgres pg_dump -U teachpilot teachpilot > $BACKUP_DIR/postgres.sql

# 备份 ChromaDB
docker cp teachpilot-chromadb:/chroma/chroma $BACKUP_DIR/chroma

# 备份应用数据
docker cp teachpilot-app:/app/backend/data $BACKUP_DIR/app-data

# 压缩备份
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# 删除 7 天前的备份
find /backups -name "*.tar.gz" -mtime +7 -delete

echo "备份完成：$BACKUP_DIR.tar.gz"
```

### 定时备份

```bash
# 添加到 crontab（每天凌晨 2 点备份）
0 2 * * * /path/to/backup.sh
```

---

## 安全审计日志

### 启用日志记录

```bash
# 日志格式（生产环境建议使用 JSON）
LOG_FORMAT=json

# 日志级别
GLOBAL_LOG_LEVEL=INFO
```

### 查看日志

```bash
# 查看应用日志
docker-compose -f docker-compose.teachpilot.prod.yaml logs -f teachpilot

# 查看 Nginx 访问日志
docker exec teachpilot-nginx tail -f /var/log/nginx/access.log

# 查看 Nginx 错误日志
docker exec teachpilot-nginx tail -f /var/log/nginx/error.log
```

---

## 安全检查清单

部署前请确认：

- [ ] 修改了所有默认密码
- [ ] 生成了唯一的 WEBUI_SECRET_KEY
- [ ] 配置了正确的 CORS 允许来源
- [ ] 启用了 HTTPS
- [ ] 配置了防火墙规则
- [ ] 设置了定期备份
- [ ] 限制了数据库网络访问
- [ ] 配置了日志记录
- [ ] 更新了所有依赖到最新版本

---

## 安全事件响应

如发现安全漏洞或可疑活动：

1. **立即隔离**：停止受影响的服务
2. **保存证据**：备份相关日志
3. **评估影响**：确定受影响的范围
4. **修复漏洞**：应用安全补丁
5. **恢复服务**：确认安全后恢复运行
6. **事后分析**：记录事件并改进

---

**安全联系方式**：如有安全问题，请联系项目维护团队。
