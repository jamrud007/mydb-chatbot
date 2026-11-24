# Docker Deployment Guide - vLLM + Full Stack

Complete containerized deployment of MyDB Chatbot, with optional self-hosted vLLM (Mistral-7B + LoRA) GPU inference.

All commands below are run from the **project root** (where `docker-compose.yml` lives).

---

## Deployment Modes

`docker-compose.yml` defines a single stack with an optional `vllm` service gated behind the `vllm` Docker Compose profile.

### Mode 1: Without vLLM (cloud LLM)

For development, or if you don't have a GPU. Backend uses Gemini/OpenAI/DeepSeek per your `.env`.

```bash
docker-compose up -d
```

**Services:** MySQL, Redis, Backend (FastAPI), Frontend (Streamlit)

### Mode 2: With vLLM (self-hosted, GPU)

For a fully self-hosted stack using the fine-tuned Mistral-7B + LoRA model.

```bash
docker-compose --profile vllm up -d
# or explicitly:
COMPOSE_PROFILES=vllm docker-compose up -d
```

**Services:** MySQL, Redis, **vLLM** (Mistral-7B + LoRA), Backend (FastAPI, points at vLLM), Frontend (Streamlit)

---

## Prerequisites

### For Mode 1 (no vLLM)
- Docker
- Docker Compose

### For Mode 2 (with vLLM)
- Docker + Docker Compose
- **NVIDIA GPU**: 8GB+ VRAM (RTX 3090/4090 or A100 recommended)
- **NVIDIA Drivers**: 525.x or newer, CUDA 11.8/12.1
- **NVIDIA Container Toolkit** (for GPU passthrough)
- **System Memory**: 16GB+ RAM, ~20GB free disk space
- **LoRA adapter**: `nl2sql-json-v2-adapter-manual/` must exist at the project root before building the `vllm` image — it is gitignored (large artifact) and must be provided locally, e.g. by copying your fine-tuned adapter into place.

### Install NVIDIA Container Toolkit (Ubuntu/Debian)

```bash
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

**Verify GPU access:**
```bash
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

---

## Configure Environment

Copy the appropriate template to `.env` at the project root:

```bash
# For Mode 2 (vLLM, GPU)
cp docker/.env.docker.vllm.example .env

# Edit configuration (set DB_PASSWORD at minimum)
nano .env
```

**Important variables:**
- `DB_PASSWORD` - MySQL password (required)
- `AI_PROVIDER` - `gemini`, `openai` (vLLM-compatible), `ollama`, or `deepseek`
- `OPENAI_BASE_URL` - `http://vllm:8080/v1` for Mode 2
- `OPENAI_MODEL` - `mistralai/Mistral-7B-Instruct-v0.3`
- `VLLM_PORT` - vLLM API port (default: 8080)
- `BACKEND_PORT` - Backend API port (default: 5000)
- `FRONTEND_PORT` - Streamlit UI port (default: 8501)

For a non-Docker (bare-metal) setup, see [`.env.vllm.example`](../.env.vllm.example) instead.

---

## Deploy

```bash
# Build and start (Mode 2: with vLLM)
docker-compose --profile vllm up -d --build

# View logs
docker-compose logs -f
```

**Expected startup sequence:**
1. MySQL (60-90s)
2. Redis (5-10s)
3. vLLM (120-180s) - longest, downloads/loads the model
4. Backend (30-60s)
5. Frontend (10-20s)

### Monitor Startup

```bash
# Watch all containers
docker-compose ps

# Check specific service logs
docker-compose logs -f vllm
docker-compose logs -f backend
```

### Verify Services

```bash
# vLLM server
curl http://localhost:8080/v1/models

# Backend API
curl http://localhost:5000/api/health
```

Frontend: open http://localhost:8501

---

## Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8501 | Streamlit UI |
| **Backend API** | http://localhost:5000 | FastAPI endpoints |
| **vLLM API** | http://localhost:8080 | OpenAI-compatible API (Mode 2 only) |
| **MySQL** | localhost:3307 | Database (external access) |
| **Redis** | localhost:6379 | Cache |

---

## Management Commands

### Stop / Start
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

### Restart a Single Service
```bash
docker-compose restart vllm
docker-compose restart backend
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service, last 100 lines
docker-compose logs -f --tail=100 vllm
```

### Rebuild After Code Changes
```bash
docker-compose --profile vllm up -d --build
docker-compose --profile vllm up -d --build backend
```

### Shell Access
```bash
docker exec -it mysql-chatbot-backend bash
docker exec -it mydb-chatbot-vllm bash
docker exec -it mysql-chatbot-db mysql -u root -p
```

---

## Resource Monitoring

```bash
# GPU usage from host
nvidia-smi

# GPU usage from vLLM container
docker exec mydb-chatbot-vllm nvidia-smi

# Container resource stats
docker stats
```

### Expected Resource Usage

| Container | CPU | Memory | GPU VRAM |
|-----------|-----|--------|----------|
| vLLM | 20-40% | 4-6GB | 6-8GB |
| Backend | 5-10% | 500MB-1GB | - |
| Frontend | 5-10% | 300-500MB | - |
| MySQL | 2-5% | 200-400MB | - |
| Redis | 1-3% | 50-100MB | - |

---

## Troubleshooting

### vLLM Container Fails to Start

```bash
# Check GPU access
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi

# Check vLLM logs
docker logs mydb-chatbot-vllm
```

**Common issues:**
- CUDA out of memory -> reduce `--gpu-memory-utilization` in `docker/Dockerfile.vllm`
- Model download timeout -> increase health check `start_period`
- GPU not found -> install NVIDIA Container Toolkit
- Build fails on `COPY nl2sql-json-v2-adapter-manual` -> the LoRA adapter directory is missing locally (see Prerequisites)

### Backend Cannot Connect to vLLM

```bash
# Check vLLM health
docker exec mydb-chatbot-vllm curl http://localhost:8080/health

# Check network
docker network ls
docker network inspect <project>_chatbot-network

# Verify environment
docker exec mysql-chatbot-backend env | grep OPENAI
```

### Frontend Cannot Connect to Backend

```bash
curl http://localhost:5000/api/health
docker exec mysql-chatbot-frontend env | grep BACKEND
```

### Database Connection Errors

```bash
docker-compose logs mysql
docker exec mysql-chatbot-db mysqladmin ping -h localhost -u root -p
```

---

## Security Considerations (Production)

1. **Change default passwords** in `.env`:
   ```env
   DB_PASSWORD=strong_random_password_here
   ```

2. **Remove external port mappings** for internal-only services (MySQL, Redis) in `docker-compose.yml`.

3. **Enable read-only mode**:
   ```env
   READ_ONLY_MODE=True
   ```

4. **Use Docker secrets** instead of plain env vars for credentials in production.

---

## Updating

### Update Application Code
```bash
git pull
docker-compose --profile vllm up -d --build
```

### Update LoRA Adapter
```bash
# Replace adapter folder at project root, then rebuild vLLM
docker-compose --profile vllm up -d --build vllm
```

### Update vLLM Version

Edit `docker/Dockerfile.vllm` (`pip3 install vllm>=...`), then rebuild:
```bash
docker-compose --profile vllm up -d --build vllm
```

---

## Health Checks

All services have automatic health checks:

- **vLLM**: starts after 120s, checks every 30s
- **MySQL**: starts after 60s, checks every 10s
- **Backend**: starts after 40s, checks every 30s
- **Frontend**: starts after 40s, checks every 30s

```bash
docker-compose ps
```

---

## Additional Resources

- [Docker GPU Support](https://docs.docker.com/compose/gpu-support/)
- [NVIDIA Container Toolkit](https://github.com/NVIDIA/nvidia-container-toolkit)
- [vLLM Documentation](https://docs.vllm.ai/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
