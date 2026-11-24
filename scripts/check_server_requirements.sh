#!/bin/bash
# Server Readiness Check Script for vLLM Deployment
# Run this on your Alibaba Cloud server
# Usage: bash scripts/check_server_requirements.sh

set -e

echo "=========================================="
echo "🔍 vLLM Deployment Readiness Check"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

# ========================================
# 1. OS & System Info
# ========================================
echo "1️⃣  System Information"
echo "----------------------------------------"
echo "OS: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"
echo "Hostname: $(hostname)"
echo ""

# ========================================
# 2. NVIDIA GPU Check
# ========================================
echo "2️⃣  GPU Detection"
echo "----------------------------------------"
if command -v nvidia-smi &> /dev/null; then
    check_pass "nvidia-smi found"
    echo ""
    nvidia-smi --query-gpu=index,name,memory.total,driver_version,cuda_version --format=csv
    echo ""
    
    # Check VRAM (need at least 8GB)
    VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1)
    if [ "$VRAM" -ge 8000 ]; then
        check_pass "GPU Memory: ${VRAM}MB (>= 8GB required)"
    else
        check_warn "GPU Memory: ${VRAM}MB (8GB+ recommended for Mistral-7B)"
    fi
else
    check_fail "nvidia-smi not found - NVIDIA drivers not installed"
fi
echo ""

# ========================================
# 3. Docker Check
# ========================================
echo "3️⃣  Docker"
echo "----------------------------------------"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    check_pass "Docker installed: $DOCKER_VERSION"
    
    # Check if Docker daemon is running
    if docker ps &> /dev/null; then
        check_pass "Docker daemon is running"
    else
        check_fail "Docker daemon is not running"
    fi
    
    # Check Docker version
    DOCKER_VER=$(docker version --format '{{.Server.Version}}' 2>/dev/null | cut -d '.' -f1)
    if [ "$DOCKER_VER" -ge 20 ]; then
        check_pass "Docker version >= 20.x"
    else
        check_warn "Docker version < 20.x (upgrade recommended)"
    fi
else
    check_fail "Docker not installed"
fi
echo ""

# ========================================
# 4. Docker Compose Check
# ========================================
echo "4️⃣  Docker Compose"
echo "----------------------------------------"
if command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    check_pass "docker-compose installed: $COMPOSE_VERSION"
elif docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    check_pass "docker compose (plugin) installed: $COMPOSE_VERSION"
else
    check_fail "Docker Compose not installed"
fi
echo ""

# ========================================
# 5. NVIDIA Container Toolkit
# ========================================
echo "5️⃣  NVIDIA Container Toolkit"
echo "----------------------------------------"
if dpkg -l | grep -q nvidia-container-toolkit; then
    check_pass "nvidia-container-toolkit installed"
    
    # Test GPU access in Docker
    if docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi &> /dev/null; then
        check_pass "GPU accessible from Docker containers"
    else
        check_fail "GPU NOT accessible from Docker (restart Docker daemon?)"
    fi
else
    check_fail "nvidia-container-toolkit not installed"
fi
echo ""

# ========================================
# 6. Disk Space
# ========================================
echo "6️⃣  Disk Space"
echo "----------------------------------------"
AVAILABLE_GB=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
echo "Available space: ${AVAILABLE_GB}GB"
if [ "$AVAILABLE_GB" -ge 20 ]; then
    check_pass "Sufficient disk space (>= 20GB free)"
else
    check_warn "Low disk space (20GB+ recommended)"
fi
echo ""

# ========================================
# 7. Memory Check
# ========================================
echo "7️⃣  System Memory"
echo "----------------------------------------"
TOTAL_MEM_GB=$(free -g | awk 'NR==2 {print $2}')
echo "Total RAM: ${TOTAL_MEM_GB}GB"
if [ "$TOTAL_MEM_GB" -ge 16 ]; then
    check_pass "Sufficient RAM (>= 16GB)"
else
    check_warn "RAM < 16GB (16GB+ recommended)"
fi
echo ""

# ========================================
# 8. Network Ports
# ========================================
echo "8️⃣  Required Ports Availability"
echo "----------------------------------------"
PORTS=(8080 5000 8501 3306 6379)
for PORT in "${PORTS[@]}"; do
    if ! nc -z localhost $PORT 2>/dev/null; then
        check_pass "Port $PORT is available"
    else
        check_warn "Port $PORT is already in use"
    fi
done
echo ""

# ========================================
# 9. Python (Optional - for local testing)
# ========================================
echo "9️⃣  Python (Optional)"
echo "----------------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    check_pass "Python installed: $PYTHON_VERSION"
else
    check_warn "Python not installed (optional for local testing)"
fi
echo ""

# ========================================
# 10. Git (for cloning repo)
# ========================================
echo "🔟 Git"
echo "----------------------------------------"
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    check_pass "Git installed: $GIT_VERSION"
else
    check_warn "Git not installed (needed to clone repository)"
fi
echo ""

# ========================================
# Summary
# ========================================
echo "=========================================="
echo "📊 SUMMARY"
echo "=========================================="
echo ""

# Critical checks
CRITICAL_PASS=0
CRITICAL_TOTAL=5

echo "Critical Requirements:"
command -v nvidia-smi &> /dev/null && ((CRITICAL_PASS++)) || echo "  ❌ NVIDIA Drivers"
command -v docker &> /dev/null && ((CRITICAL_PASS++)) || echo "  ❌ Docker"
(command -v docker-compose &> /dev/null || docker compose version &> /dev/null 2>&1) && ((CRITICAL_PASS++)) || echo "  ❌ Docker Compose"
dpkg -l | grep -q nvidia-container-toolkit && ((CRITICAL_PASS++)) || echo "  ❌ NVIDIA Container Toolkit"
[ "$AVAILABLE_GB" -ge 20 ] && ((CRITICAL_PASS++)) || echo "  ⚠️  Disk Space (< 20GB)"

echo ""
echo "Status: $CRITICAL_PASS/$CRITICAL_TOTAL critical requirements met"
echo ""

if [ "$CRITICAL_PASS" -eq "$CRITICAL_TOTAL" ]; then
    echo -e "${GREEN}✅ Server is READY for vLLM deployment!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Clone repository: git clone <your-repo-url>"
    echo "  2. cd mysql-chatbot"
    echo "  3. cp docker/.env.docker.vllm .env"
    echo "  4. Edit .env and set DB_PASSWORD"
    echo "  5. docker-compose --profile vllm up -d"
    exit 0
else
    echo -e "${RED}❌ Server is NOT ready. Please fix the issues above.${NC}"
    echo ""
    echo "Installation guides:"
    echo "  - NVIDIA Drivers: https://docs.nvidia.com/datacenter/tesla/tesla-installation-notes/"
    echo "  - Docker: https://docs.docker.com/engine/install/ubuntu/"
    echo "  - NVIDIA Container Toolkit: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html"
    exit 1
fi
