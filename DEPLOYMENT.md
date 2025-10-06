# Quick Orders System - 部署指南

## 服务器架构

根据您的架构图，系统将部署在以下目录结构：

```
/home/renfu/htdocs/py-sites/
├── shop/                    # 您的 Flask 应用
│   ├── application/         # Flask 应用核心代码
│   ├── templates/          # 模板文件
│   ├── static/            # 静态文件
│   ├── routes/            # 路由
│   ├── models/            # 数据模型
│   ├── migrations/        # 数据库迁移
│   ├── venv/              # 虚拟环境
│   ├── logs/              # 日志文件
│   ├── uploads/           # 上传文件
│   ├── wsgi.py            # WSGI 入口点
│   ├── gunicorn.conf.py   # Gunicorn 配置
│   ├── config_production.py # 生产环境配置
│   └── .env               # 环境变量
├── nginx/
│   └── shop.py-sites.com.conf # Nginx 配置
└── certs/
    ├── origin.crt         # SSL 证书
    └── origin.key         # SSL 私钥
```

## 部署步骤

### 1. 准备服务器环境

```bash
# 创建目录结构
mkdir -p /home/renfu/htdocs/py-sites/shop/{logs,uploads}
mkdir -p /home/renfu/htdocs/py-sites/nginx
mkdir -p /home/renfu/htdocs/py-sites/certs
```

### 2. 上传项目文件

将以下文件复制到 `/home/renfu/htdocs/py-sites/shop/` 目录：

- `application/` - 整个目录
- `templates/` - 整个目录  
- `static/` - 整个目录
- `routes/` - 整个目录
- `models/` - 整个目录
- `migrations/` - 整个目录
- `wsgi.py` - WSGI 入口文件
- `gunicorn.conf.py` - Gunicorn 配置
- `config_production.py` - 生产配置
- `requirements.txt` - 依赖文件

### 3. 设置虚拟环境

```bash
cd /home/renfu/htdocs/py-sites/shop

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4. 配置环境变量

创建 `.env` 文件：

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False

# Database Configuration
DATABASE_URL=sqlite:///quick_orders.db
# 或使用 PostgreSQL:
# DATABASE_URL=postgresql://username:password@localhost/quick_orders

# Admin Configuration
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-admin-password

# 其他配置...
```

### 5. 初始化数据库

```bash
# 设置 Flask 应用
export FLASK_APP=wsgi.py

# 运行数据库迁移
flask db upgrade

# 创建初始数据（如果需要）
python scripts/setup_database.py
```

### 6. 配置 Nginx

将 `nginx_shop.conf` 文件复制到 `/home/renfu/htdocs/py-sites/nginx/shop.py-sites.com.conf`

修改域名和证书路径：

```nginx
server_name your-domain.com;  # 改为您的域名
ssl_certificate /path/to/your/cert.crt;
ssl_certificate_key /path/to/your/cert.key;
```

重新加载 Nginx：

```bash
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### 7. 启动应用

```bash
cd /home/renfu/htdocs/py-sites/shop
source venv/bin/activate

# 使用 Gunicorn 启动
gunicorn -c gunicorn.conf.py wsgi:app
```

### 8. 设置系统服务（可选）

创建 systemd 服务文件 `/etc/systemd/system/quick-orders.service`：

```ini
[Unit]
Description=Quick Orders Gunicorn Application
After=network.target

[Service]
User=renfu
Group=renfu
WorkingDirectory=/home/renfu/htdocs/py-sites/shop
Environment="PATH=/home/renfu/htdocs/py-sites/shop/venv/bin"
ExecStart=/home/renfu/htdocs/py-sites/shop/venv/bin/gunicorn -c gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable quick-orders
sudo systemctl start quick-orders
```

## app.py vs wsgi.py 的影响

### 开发环境 (app.py)
- 使用 `app.run(debug=True, ...)` 启动开发服务器
- 包含调试信息和自动重载
- 适合本地开发

### 生产环境 (wsgi.py)  
- 使用 `gunicorn -c gunicorn.conf.py wsgi:app` 启动
- 无调试模式，性能优化
- 支持多进程和负载均衡
- 通过 Nginx 反向代理提供 HTTPS 支持

## 监控和日志

### 查看日志

```bash
# 应用日志
tail -f /home/renfu/htdocs/py-sites/shop/logs/gunicorn.access.log
tail -f /home/renfu/htdocs/py-sites/shop/logs/gunicorn.error.log

# Nginx 日志
tail -f /home/renfu/htdocs/py-sites/shop/logs/nginx.access.log
tail -f /home/renfu/htdocs/py-sites/shop/logs/nginx.error.log
```

### 重启服务

```bash
# 重启应用
sudo systemctl restart quick-orders

# 重启 Nginx
sudo systemctl restart nginx
```

## 故障排除

### 常见问题

1. **权限问题**：确保 `renfu` 用户有读写权限
2. **端口冲突**：检查 8000 端口是否被占用
3. **SSL 证书**：确保证书文件路径正确
4. **数据库连接**：检查数据库 URL 和权限

### 测试部署

```bash
# 测试本地连接
curl http://127.0.0.1:8000

# 测试外部访问
curl https://your-domain.com
```

## 性能优化

1. **启用 Gzip 压缩**（在 Nginx 配置中）
2. **设置静态文件缓存**
3. **使用 CDN**（如果需要）
4. **数据库连接池**
5. **Redis 缓存**（可选）

部署完成后，您的 Quick Orders 系统将在生产环境中稳定运行！
