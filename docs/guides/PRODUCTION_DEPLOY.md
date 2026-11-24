# Streamlit Production Deployment Guide
## Quick Deploy to Production

---

## ✅ **Pre-Deployment Checklist**

### **1. Environment Setup**
```bash
# Copy production environment
cp .env.production .env

# Edit with your actual values
nano .env

# CRITICAL: Update these!
# - DB_PASSWORD (use strong password!)
# - OPENAI_API_KEY (your production key)
# - DB_HOST (your production database)
```

### **2. Security Checks**
- [ ] `DEBUG=False` in .env
- [ ] `READ_ONLY_MODE=True` in .env
- [ ] Strong `DB_PASSWORD` (16+ chars, mixed case, numbers, symbols)
- [ ] Valid `OPENAI_API_KEY` (production key, not dev)
- [ ] `.env` in `.gitignore` (never commit!)

### **3. Performance Settings**
- [ ] `CACHE_TYPE=redis` (for better performance)
- [ ] `CACHE_DEFAULT_TTL=604800` (7 days cache)
- [ ] `RATE_LIMIT_REQUESTS=10` (prevent abuse)

---

## 🚀 **Deployment Options**

### **Option 1: Docker (Recommended)** ⭐

**Quick Start:**
```bash
# 1. Setup environment
cp .env.production .env
# Edit .env with your values

# 2. Deploy with Docker
cd docker/
docker-compose up -d

# 3. Check status
docker-compose ps
docker-compose logs -f

# 4. Access
# Frontend: http://your-server:8501
# Backend: http://your-server:8000
```

**Behind Nginx:**
```nginx
# /etc/nginx/sites-available/chatbot
server {
    listen 80;
    server_name chatbot.example.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

### **Option 2: PM2 (Server)** 

**Setup:**
```bash
# 1. Install PM2
npm install -g pm2

# 2. Start services
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2" \
  --name chatbot-backend \
  --interpreter python3

pm2 start "streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0" \
  --name chatbot-frontend \
  --interpreter python3

# 3. Save & enable auto-start
pm2 save
pm2 startup

# 4. Monitor
pm2 status
pm2 logs
pm2 monit
```

---

### **Option 3: Systemd (Linux)**

**Backend Service:**
```bash
# /etc/systemd/system/chatbot-backend.service
[Unit]
Description=MySQL Chatbot Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/mysql-chatbot
Environment="PATH=/var/www/mysql-chatbot/venv/bin"
ExecStart=/var/www/mysql-chatbot/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

**Frontend Service:**
```bash
# /etc/systemd/system/chatbot-frontend.service
[Unit]
Description=MySQL Chatbot Frontend
After=network.target chatbot-backend.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/mysql-chatbot
Environment="PATH=/var/www/mysql-chatbot/venv/bin"
ExecStart=/var/www/mysql-chatbot/venv/bin/streamlit run streamlit_app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable & Start:**
```bash
sudo systemctl enable chatbot-backend chatbot-frontend
sudo systemctl start chatbot-backend chatbot-frontend
sudo systemctl status chatbot-backend chatbot-frontend
```

---

## 🔒 **SSL/HTTPS Setup (Required for Production)**

### **With Let's Encrypt (Free):**

```bash
# 1. Install certbot
sudo apt install certbot python3-certbot-nginx

# 2. Get certificate
sudo certbot --nginx -d chatbot.example.com

# 3. Auto-renewal
sudo certbot renew --dry-run
```

**Nginx config will auto-update to:**
```nginx
server {
    listen 443 ssl;
    server_name chatbot.example.com;
    
    ssl_certificate /etc/letsencrypt/live/chatbot.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chatbot.example.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        # ... proxy settings
    }
}
```

---

## 📊 **Post-Deployment Monitoring**

### **Health Checks:**
```bash
# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:8501/_stcore/health

# Database connection
docker-compose exec mysql mysqladmin ping
```

### **Log Monitoring:**
```bash
# Docker
docker-compose logs -f frontend
docker-compose logs -f backend

# PM2
pm2 logs chatbot-frontend
pm2 logs chatbot-backend

# Systemd
sudo journalctl -u chatbot-frontend -f
sudo journalctl -u chatbot-backend -f
```

### **Performance Metrics:**
```bash
# Docker stats
docker stats

# PM2 monitoring
pm2 monit

# Server resources
htop
```

---

## 🔄 **Backup Strategy**

### **Database Backup:**
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
docker-compose exec mysql mysqldump -u root -p${DB_PASSWORD} ${DB_NAME} > backup_${DATE}.sql

# Keep last 7 days
find /backups/*.sql -mtime +7 -delete
```

### **Application Backup:**
```bash
# Backup .env and configs
tar -czf chatbot_config_${DATE}.tar.gz .env* .streamlit/ docker/
```

---

## 📈 **Scaling Tips**

### **Horizontal Scaling (Multiple Instances):**
```yaml
# docker-compose.yml
services:
  frontend:
    deploy:
      replicas: 3  # Run 3 instances
    
  backend:
    command: uvicorn main:app --workers 4  # 4 workers per instance
```

### **Vertical Scaling (More Resources):**
```yaml
services:
  frontend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## 🐛 **Troubleshooting**

**Frontend won't start:**
```bash
# Check logs
pm2 logs chatbot-frontend

# Common issue: Port in use
sudo lsof -i :8501
sudo kill -9 <PID>
```

**Backend errors:**
```bash
# Check database connection
docker-compose exec backend python -c "import pymysql; print('DB OK')"

# Check API key
docker-compose logs backend | grep "API"
```

**Slow performance:**
```bash
# Check Redis cache
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli info stats

# Increase cache TTL in .env
CACHE_DEFAULT_TTL=604800  # 7 days
```

---

## ✅ **Production Checklist**

**Before Go-Live:**
- [ ] `.env.production` configured with real values
- [ ] SSL certificate installed (HTTPS)
- [ ] Firewall rules configured (ports 80, 443)
- [ ] Database backups automated
- [ ] Monitoring setup (logs, health checks)
- [ ] Rate limiting enabled
- [ ] Error tracking configured (Sentry optional)
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

**After Go-Live:**
- [ ] Monitor logs for 1st week
- [ ] Check performance metrics daily
- [ ] Verify backups running
- [ ] Test auto-restart (reboot server)
- [ ] Update documentation
- [ ] Train users

---

## 🎯 **Quick Commands Reference**

```bash
# Start all
docker-compose up -d                    # Docker
pm2 start all                          # PM2
sudo systemctl start chatbot-*         # Systemd

# Stop all
docker-compose down                    # Docker
pm2 stop all                          # PM2
sudo systemctl stop chatbot-*         # Systemd

# Restart
docker-compose restart                 # Docker
pm2 restart all                       # PM2
sudo systemctl restart chatbot-*      # Systemd

# View logs
docker-compose logs -f                 # Docker
pm2 logs                              # PM2
sudo journalctl -f                    # Systemd

# Check status
docker-compose ps                      # Docker
pm2 status                            # PM2
sudo systemctl status chatbot-*       # Systemd
```

---

## 🚀 **One-Command Deploy (Docker)**

```bash
# Complete deployment in one command
cp .env.production .env && \
cd docker/ && \
docker-compose up -d && \
docker-compose ps
```

---

**Deployment Time:** 15-30 minutes  
**Minimum Server:** 2 vCPU, 4GB RAM, 50GB SSD  
**Recommended:** 4 vCPU, 8GB RAM, 100GB SSD  
**Cost:** $20-40/month (DigitalOcean/AWS)

**You're ready for production! 🎉**
