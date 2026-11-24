# 🚀 Alibaba Cloud Deployment Guide

Panduan lengkap deploy MySQL Chatbot dengan vLLM di Alibaba Cloud.

## 📋 Step 1: Check Server Requirements

SSH ke server Alibaba Cloud Anda, lalu jalankan:

```bash
# Download check script
curl -O https://raw.githubusercontent.com/your-repo/mysql-chatbot/main/scripts/check_server_requirements.sh

# Atau jika sudah clone repo
bash scripts/check_server_requirements.sh
```

**Script akan cek:**
- ✅ NVIDIA GPU & Driver
- ✅ Docker & Docker Compose
- ✅ NVIDIA Container Toolkit
- ✅ Disk space (>20GB)
- ✅ RAM (>16GB)
- ✅ Port availability

---

## 🔧 Step 2: Install Missing Requirements

### A. NVIDIA Drivers (jika belum)

```bash
# Check GPU model
lspci | grep -i nvidia

# Install driver (Ubuntu)
sudo apt update
sudo apt install -y ubuntu-drivers-common
sudo ubuntu-drivers autoinstall

# Verify
nvidia-smi
```

### B. Docker

```bash
# Remove old versions
sudo apt remove docker docker-engine docker.io containerd runc

# Install dependencies
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### C. NVIDIA Container Toolkit

```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install
sudo apt update
sudo apt install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker

# Restart Docker
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

## 📦 Step 3: Deploy Application

### Clone Repository

```bash
# Install git if needed
sudo apt install -y git

# Clone your repo
git clone https://github.com/your-username/mysql-chatbot.git
cd mysql-chatbot
```

### Configure Environment

```bash
# Copy vLLM template
cp docker/.env.docker.vllm .env

# Edit configuration
nano .env
```

**Required changes in `.env`:**
```env
# Database
DB_PASSWORD=your_secure_password_here

# Optional: Change ports if needed
VLLM_PORT=8080
BACKEND_PORT=5000
FRONTEND_PORT=8501
```

### Start Services

```bash
# Build and start all services with vLLM
docker-compose --profile vllm up -d

# Monitor logs
docker-compose logs -f

# Expected startup time: 3-5 minutes (first time)
```

### Verify Deployment

```bash
# Check all containers
docker-compose ps

# Test vLLM
curl http://localhost:8080/v1/models

# Test backend
curl http://localhost:5000/api/health

# Test frontend (if you opened port 8501)
curl http://localhost:8501
```

---

## 🌐 Step 4: Configure Network Access

### A. Alibaba Cloud Security Group

Di Alibaba Cloud Console:

1. Navigate to **ECS** → **Instances**
2. Click your instance → **Security Groups**
3. Add **Inbound Rules**:

| Port | Protocol | Source | Description |
|------|----------|--------|-------------|
| 8501 | TCP | 0.0.0.0/0 | Streamlit Frontend |
| 5000 | TCP | 0.0.0.0/0 | FastAPI Backend (optional) |
| 22 | TCP | Your IP | SSH Access |

**Security Note:** 
- Port 8080 (vLLM) - JANGAN dibuka ke public
- Port 3306 (MySQL) - JANGAN dibuka ke public
- Port 6379 (Redis) - JANGAN dibuka ke public

### B. Nginx Reverse Proxy (Production)

Untuk HTTPS dan domain:

```bash
# Install nginx
sudo apt install -y nginx certbot python3-certbot-nginx

# Configure nginx
sudo nano /etc/nginx/sites-available/chatbot
```

**nginx config:**
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
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Step 5: Monitoring

### Check Resource Usage

```bash
# GPU monitoring
nvidia-smi -l 1  # Update every 1 second

# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f vllm
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100
```

### Performance Expectations

**Initial Load (Cold Start):**
- vLLM model download: 2-3 minutes
- vLLM model loading: 1-2 minutes
- First inference: 3-5 seconds

**After Warmup:**
- Inference latency: 0.5-2 seconds
- Throughput: 15-30 tokens/second (depends on GPU)

---

## 🔄 Step 6: Updates & Maintenance

### Update Application

```bash
# Pull latest code
cd mysql-chatbot
git pull

# Rebuild and restart
docker-compose --profile vllm up -d --build
```

### Update LoRA Adapter

```bash
# Upload new adapter via SCP
scp -r ./nl2sql-json-v2-adapter-manual-v2 user@server:/path/to/mysql-chatbot/

# Rename/replace
mv nl2sql-json-v2-adapter-manual nl2sql-json-v2-adapter-manual.old
mv nl2sql-json-v2-adapter-manual-v2 nl2sql-json-v2-adapter-manual

# Rebuild vLLM container
docker-compose up -d --build vllm
```

### Backup Database

```bash
# Backup MySQL
docker exec mysql-chatbot-db mysqldump -u root -p ecommerce_olist > backup.sql

# Restore
docker exec -i mysql-chatbot-db mysql -u root -p ecommerce_olist < backup.sql
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs <service-name>

# Restart specific service
docker-compose restart <service-name>

# Full restart
docker-compose down
docker-compose --profile vllm up -d
```

### GPU Out of Memory

Edit `docker/Dockerfile.vllm`, reduce memory usage:
```dockerfile
CMD ["python3", "-m", "vllm.entrypoints.openai.api_server", \
     "--gpu-memory-utilization", "0.7", \  # Reduce from 0.9
     "--max-model-len", "2048", \  # Reduce from 4096
     ...
]
```

### Slow Performance

```bash
# Check GPU utilization
nvidia-smi

# If GPU not fully utilized, increase batch size
# Edit Dockerfile.vllm:
--max-num-batched-tokens 8192
```

---

## ✅ Quick Command Reference

```bash
# Start all services
docker-compose --profile vllm up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Restart single service
docker-compose restart vllm

# Check status
docker-compose ps

# GPU monitoring
nvidia-smi -l 1

# Access shell
docker exec -it mysql-chatbot-backend bash
```

---

## 🎯 Access Your Chatbot

**Public URL:**
- Frontend: `http://your-server-ip:8501`
- With nginx: `https://your-domain.com`

**Internal URLs:**
- Backend API: `http://localhost:5000`
- vLLM API: `http://localhost:8080`

---

## 📞 Support

Jika ada masalah:
1. Check logs: `docker-compose logs -f`
2. Run health check: `bash scripts/check_server_requirements.sh`
3. Verify GPU: `nvidia-smi`

**Common Issues:**
- CUDA OOM → Reduce `--gpu-memory-utilization`
- Slow startup → Check internet (model download)
- Permission denied → `sudo usermod -aG docker $USER`
