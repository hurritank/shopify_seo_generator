# 🚀 Hướng dẫn Deploy Production

## 📋 Tổng quan

Khi deploy lên server production, bạn cần chạy **API Server** để expose API endpoints.

## 🎯 File cần chạy

### Option 1: Sử dụng `run_api_prod.py` (Khuyến nghị)

```bash
python run_api_prod.py
```

**File này có:**
- ✅ Không có auto-reload (phù hợp production)
- ✅ Hỗ trợ multiple workers
- ✅ Cấu hình qua environment variables

### Option 2: Sử dụng uvicorn trực tiếp (Linh hoạt hơn)

```bash
uvicorn src.api.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --no-reload \
  --log-level info
```

### Option 3: Sử dụng gunicorn + uvicorn workers (Best Practice)

```bash
gunicorn src.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

**Lưu ý:** Cần cài thêm `gunicorn`:
```bash
pip install gunicorn
```

---

## ⚙️ Cấu hình Environment Variables

Tạo file `.env` trên server:

```bash
# API Server
HOST=0.0.0.0
PORT=8000
WORKERS=4

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxx

# Optional - Trending Keywords
SERPAPI_KEY=xxxxxxx
APIFY_TOKEN=xxxxxxx
USE_PYTRENDS=True
```

---

## 🔧 Setup trên Server

### 1. Clone/Copy project lên server

```bash
# Clone từ Git
git clone <your-repo-url>
cd seo_generator

# Hoặc copy files lên server
scp -r seo_generator/ user@server:/path/to/
```

### 2. Cài đặt dependencies

```bash
# Tạo virtual environment
python3 -m venv venv
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt

# Nếu dùng gunicorn
pip install gunicorn
```

### 3. Cấu hình .env

```bash
# Tạo file .env
nano .env

# Điền các API keys
OPENAI_API_KEY=sk-...
HOST=0.0.0.0
PORT=8000
WORKERS=4
```

### 4. Chạy API Server

#### Cách 1: Chạy trực tiếp (Testing)

```bash
python run_api_prod.py
```

#### Cách 2: Chạy với nohup (Background)

```bash
nohup python run_api_prod.py > api.log 2>&1 &
```

#### Cách 3: Chạy với systemd (Production - Khuyến nghị)

Tạo file `/etc/systemd/system/seo-generator-api.service`:

```ini
[Unit]
Description=SEO Generator API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/seo_generator
Environment="PATH=/path/to/seo_generator/venv/bin"
ExecStart=/path/to/seo_generator/venv/bin/python run_api_prod.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable và start service:**
```bash
sudo systemctl enable seo-generator-api
sudo systemctl start seo-generator-api
sudo systemctl status seo-generator-api
```

#### Cách 4: Chạy với Supervisor

Tạo file `/etc/supervisor/conf.d/seo-generator-api.conf`:

```ini
[program:seo-generator-api]
command=/path/to/seo_generator/venv/bin/python run_api_prod.py
directory=/path/to/seo_generator
user=your-user
autostart=true
autorestart=true
stderr_logfile=/var/log/seo-generator-api.err.log
stdout_logfile=/var/log/seo-generator-api.out.log
```

**Reload và start:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start seo-generator-api
```

---

## 🌐 Reverse Proxy với Nginx

Cấu hình Nginx để proxy requests đến API:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (nếu cần)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Reload Nginx:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔒 Security Best Practices

### 1. Firewall

```bash
# Chỉ mở port 8000 cho localhost (qua Nginx)
# Hoặc chỉ mở cho IP cụ thể
sudo ufw allow from YOUR_IP to any port 8000
```

### 2. SSL/HTTPS

Sử dụng Let's Encrypt với Nginx:

```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Rate Limiting

Thêm rate limiting trong Nginx:

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

server {
    location / {
        limit_req zone=api_limit burst=20;
        proxy_pass http://127.0.0.1:8000;
    }
}
```

---

## 📊 Monitoring

### 1. Health Check

```bash
# Kiểm tra API có hoạt động không
curl http://localhost:8000/health
```

### 2. Logs

```bash
# Xem logs
tail -f api_server.log

# Hoặc với systemd
sudo journalctl -u seo-generator-api -f
```

### 3. Process Monitoring

```bash
# Kiểm tra process đang chạy
ps aux | grep run_api_prod

# Hoặc với systemd
sudo systemctl status seo-generator-api
```

---

## 🔄 Update & Restart

### Với systemd:

```bash
# Pull code mới
cd /path/to/seo_generator
git pull

# Restart service
sudo systemctl restart seo-generator-api
```

### Với supervisor:

```bash
sudo supervisorctl restart seo-generator-api
```

---

## 📝 Checklist trước khi Deploy

- [ ] Đã cài đặt tất cả dependencies
- [ ] Đã cấu hình `.env` với API keys
- [ ] Đã test API hoạt động: `curl http://localhost:8000/health`
- [ ] Đã setup reverse proxy (Nginx)
- [ ] Đã setup SSL/HTTPS
- [ ] Đã setup firewall
- [ ] Đã setup monitoring/logging
- [ ] Đã setup auto-restart (systemd/supervisor)
- [ ] Đã test từ bên ngoài (nếu cần)

---

## 🐛 Troubleshooting

### API không chạy

```bash
# Kiểm tra logs
tail -f api_server.log

# Kiểm tra port có bị chiếm không
sudo lsof -i :8000

# Kiểm tra process
ps aux | grep python
```

### Lỗi import

```bash
# Đảm bảo đang ở đúng directory
cd /path/to/seo_generator

# Đảm bảo venv đã activate
source venv/bin/activate

# Test import
python -c "from src.api.main import app; print('OK')"
```

### Lỗi permission

```bash
# Đảm bảo user có quyền
chmod +x run_api_prod.py

# Đảm bảo có quyền ghi logs
touch api_server.log
chmod 666 api_server.log
```

---

## 📚 Tài liệu tham khảo

- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Deployment](https://www.uvicorn.org/deployment/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)

---

**Version:** 2.0.0  
**Last Updated:** 2025-01-08
