# Docker Deployment Guide
## MySQL Chatbot - Containerized Setup

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed (Windows/Mac) or Docker Engine (Linux)
- Docker Compose v2.0+
- Minimum 4GB RAM available for containers
- 10GB free disk space

### 1. Setup Environment

```bash
# Copy environment template
cp .env.docker .env

# Edit .env with your API keys
# IMPORTANT: Update OPENAI_API_KEY or GEMINI_API_KEY
notepad .env  # Windows
nano .env     # Linux/Mac
```

### 2. Build and Start

```bash
# Build images and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access Services

- **Frontend (Streamlit):** http://localhost:8501
- **Backend (FastAPI API):** http://localhost:8000
- **Backend Docs:** http://localhost:8000/docs
- **MySQL:** localhost:3306
- **Redis:** localhost:6379

---

## 📋 Docker Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart services
docker-compose restart

# View logs
docker-compose logs -f [service_name]
```

### Building & Updating

```bash
# Rebuild images
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Pull latest images
docker-compose pull

# Update and restart
docker-compose up -d --build
```

### Debugging

```bash
# Execute command in running container
docker-compose exec backend bash
docker-compose exec mysql mysql -u root -p

# View container stats
docker stats

# Inspect service
docker-compose logs backend --tail 100

# Check health status
docker-compose ps
```

---

## 🗄️ Database Setup

### Initial Database Load

Database will auto-initialize from `sample_db/` folder on first run.

**Manual import:**
```bash
# Copy SQL file to container
docker cp your_data.sql mysql-chatbot-db:/tmp/

# Import
docker-compose exec mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < /tmp/your_data.sql
```

### Backup & Restore

**Backup:**
```bash
# Backup database
docker-compose exec mysql mysqldump -u root -p${DB_PASSWORD} ${DB_NAME} > backup_$(date +%Y%m%d).sql

# Backup with Docker volume
docker run --rm --volumes-from mysql-chatbot-db -v $(pwd):/backup ubuntu tar cvf /backup/mysql-backup.tar /var/lib/mysql
```

**Restore:**
```bash
# Restore from SQL
docker-compose exec -T mysql mysql -u root -p${DB_PASSWORD} ${DB_NAME} < backup.sql

# Restore from volume backup
docker run --rm --volumes-from mysql-chatbot-db -v $(pwd):/backup ubuntu tar xvf /backup/mysql-backup.tar
```

---

## 🔧 Configuration

### Environment Variables

Edit `.env` file:

```env
# Required
OPENAI_API_KEY=sk-or-v1-xxx  # Your OpenRouter/OpenAI key
DB_PASSWORD=secure_password  # Change default!

# Optional tuning
DEBUG=False
READ_ONLY_MODE=True
CACHE_DEFAULT_TTL=604800  # 7 days
```

### Resource Limits

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 📊 Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Service health
docker-compose ps

# Logs
docker-compose logs -f --tail=100
```

### Health Checks

All services include health checks:
- MySQL: `mysqladmin ping`
- Redis: `redis-cli ping`
- Backend: `curl /health`
- Frontend: `curl /_stcore/health`

Check status:
```bash
docker-compose ps
# Look for "healthy" status
```

---

## 🔒 Production Deployment

### Security Checklist

- [ ] Change default `DB_PASSWORD`
- [ ] Set `DEBUG=False`
- [ ] Enable `READ_ONLY_MODE=True`
- [ ] Use strong API keys
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS (use nginx reverse proxy)
- [ ] Regular backups automated
- [ ] Monitor logs for errors

### Nginx Reverse Proxy

Create `nginx.conf`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
    }
}
```

### Auto-start on Boot

```bash
# Enable Docker auto-start
sudo systemctl enable docker

# Restart policy already set in docker-compose.yml
# (restart: unless-stopped)
```

---

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use:**
```bash
# Change ports in .env
BACKEND_PORT=8001
FRONTEND_PORT=8502

# Or stop conflicting service
sudo netstat -tulpn | grep :8000
```

**2. Permission denied:**
```bash
# Fix ownership
sudo chown -R $USER:$USER logs/ cache/
```

**3. Database connection failed:**
```bash
# Check MySQL is healthy
docker-compose ps mysql

# View MySQL logs
docker-compose logs mysql

# Verify credentials in .env
```

**4. Out of memory:**
```bash
# Increase Docker memory limit (Docker Desktop)
# Settings → Resources → Memory: 4GB+

# Or reduce workers
# In docker-compose.yml: --workers 1
```

**5. Backend fails to start:**
```bash
# Check logs
docker-compose logs backend

# Rebuild image
docker-compose build --no-cache backend

# Check dependencies
docker-compose exec backend pip list
```

---

## 📦 Volume Management

### List Volumes
```bash
docker volume ls
```

### Inspect Volume
```bash
docker volume inspect mysql-chatbot_mysql-data
```

### Cleanup Unused Volumes
```bash
# CAUTION: Only do this if you're sure
docker volume prune
```

---

## 🔄 Update & Maintenance

### Update Application Code

```bash
# 1. Pull latest code
git pull

# 2. Rebuild containers
docker-compose up -d --build

# 3. View logs to verify
docker-compose logs -f
```

### Update Dependencies

```bash
# 1. Update requirements.txt

# 2. Rebuild
docker-compose build --no-cache

# 3. Restart
docker-compose up -d
```

---

## 📈 Scaling

### Multiple Workers

```bash
# Edit docker-compose.yml
services:
  backend:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Load Balancing

Use nginx or traefik for load balancing multiple instances:

```yaml
services:
  backend:
    deploy:
      replicas: 3
```

---

## ✅ Health Check

Quick health check script:

```bash
#!/bin/bash
echo "Checking MySQL Chatbot services..."

curl -f http://localhost:8000/health && echo "✅ Backend healthy" || echo "❌ Backend down"
curl -f http://localhost:8501/_stcore/health && echo "✅ Frontend healthy" || echo "❌ Frontend down"
docker-compose exec -T mysql mysqladmin ping -u root -p${DB_PASSWORD} && echo "✅ MySQL healthy" || echo "❌ MySQL down"
docker-compose exec -T redis redis-cli ping && echo "✅ Redis healthy" || echo "❌ Redis down"
```

---

## 💡 Tips

1. **Use Docker volumes for persistence** - Don't store data in containers
2. **Monitor logs regularly** - `docker-compose logs -f`
3. **Backup before updates** - Database + volumes
4. **Keep images updated** - `docker-compose pull`
5. **Use `.dockerignore`** - Reduces build time

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Check `.env` configuration
4. Rebuild: `docker-compose up -d --build`

---

**Deployment Time:** ~5-10 minutes  
**Minimum Resources:** 4GB RAM, 10GB disk  
**Tested on:** Docker 24.0+, Docker Compose 2.0+
