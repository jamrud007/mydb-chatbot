# 🚀 CPU-Only Deployment Guide untuk Fine-tuned Model

Deploy fine-tuned Mistral-7B LoRA di server CPU (tanpa GPU) dengan GGUF + Ollama.

## 📋 Overview

**Strategi:**
1. Merge LoRA adapter dengan base model
2. Convert ke GGUF format
3. Quantize untuk CPU optimization (Q4_K_M)
4. Deploy dengan Ollama

**Hasil:**
- Model size: ~4GB (dari 14GB)
- RAM required: 6-8GB
- Inference time: 5-10 detik (acceptable untuk chatbot)
- Cost: Murah (CPU instance)

---

## 🛠️ Step 1: Persiapan (Di Local/Server dengan RAM 16GB+)

### Install Dependencies

```bash
# Python dependencies
pip install torch transformers peft sentencepiece protobuf

# Atau dari requirements
pip install -r requirements.txt
```

### Check Resources

```bash
# Check available RAM
free -h

# Need at least 16GB RAM for conversion
```

---

## 🔄 Step 2: Merge LoRA dengan Base Model

```bash
# Di directory project
cd mysql-chatbot

# Run merge script
python scripts/merge_lora_to_base.py
```

**Expected output:**
```
🔄 LoRA to GGUF Conversion Pipeline
Step 1/4: Loading base model... (5-10 minutes)
Step 2/4: Loading LoRA adapter...
Step 3/4: Merging LoRA weights... (2-5 minutes)
Step 4/4: Saving merged model...
✅ MERGE COMPLETE!

Merged model location: ./merged-mistral-nl2sql/
```

**Files created:**
- `merged-mistral-nl2sql/model-00001-of-00003.safetensors` (~5GB each)
- `merged-mistral-nl2sql/config.json`
- `merged-mistral-nl2sql/tokenizer.json`

---

## 📦 Step 3: Convert ke GGUF

```bash
# Run conversion script
bash scripts/convert_to_gguf.sh
```

**Expected output:**
```
🔄 Converting to GGUF Format
📥 Cloning llama.cpp...
🔄 Converting to GGUF (FP16)... (5-10 minutes)
✅ FP16 GGUF created: merged-mistral-nl2sql-f16.gguf (14GB)

🗜️  Quantizing to Q4_K_M... (2-3 minutes)
✅ Quantized model created: merged-mistral-nl2sql-Q4_K_M.gguf (4GB)
```

**Files created:**
- `merged-mistral-nl2sql-f16.gguf` (14GB) - Full precision
- `merged-mistral-nl2sql-Q4_K_M.gguf` (4GB) - **Use this for CPU**

---

## 🐋 Step 4: Import ke Ollama

### A. Install Ollama

**Ubuntu/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download dari https://ollama.com/download

**Verify:**
```bash
ollama --version
```

### B. Create Modelfile

```bash
# Create Modelfile
cat > Modelfile << 'EOF'
# Modelfile for mysql-nl2sql
FROM ./merged-mistral-nl2sql-Q4_K_M.gguf

TEMPLATE """[INST] {{ .System }}

{{ .Prompt }} [/INST]"""

PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.1

SYSTEM """You are an expert MySQL query generator for the ecommerce_olist database. Generate valid SQL queries in JSON format with 'sql' and 'explanation' keys."""
EOF
```

### C. Import Model

```bash
# Create Ollama model
ollama create mysql-nl2sql -f Modelfile

# Expected output:
# transferring model data
# using existing layer sha256:xxxx
# creating new layer sha256:yyyy
# writing manifest
# success
```

### D. Verify Import

```bash
# List models
ollama list

# Should show:
# NAME              ID          SIZE    MODIFIED
# mysql-nl2sql      abc123...   4.0 GB  2 minutes ago
```

---

## ✅ Step 5: Test Model

### Quick Test

```bash
# Test inference
ollama run mysql-nl2sql "Generate SQL to find top 5 customers by revenue"
```

**Expected output:**
```json
{
  "sql": "SELECT customer_id, SUM(order_total) as total_revenue FROM orders GROUP BY customer_id ORDER BY total_revenue DESC LIMIT 5",
  "explanation": "This query aggregates order totals by customer and returns the top 5 by revenue."
}
```

### Test Script

```bash
# Use test script
python scripts/test_ollama.py
```

---

## 🚀 Step 6: Deploy ke Alibaba Cloud

### A. Upload Model ke Server

**Option 1: Direct Upload**
```bash
# From local to server (will take time, ~4GB)
scp merged-mistral-nl2sql-Q4_K_M.gguf user@server:/home/user/mysql-chatbot/
scp Modelfile user@server:/home/user/mysql-chatbot/
```

**Option 2: Build on Server**
```bash
# SSH to server
ssh user@server

# Clone repo
git clone <your-repo>
cd mysql-chatbot

# Run conversion on server (need 16GB RAM)
python scripts/merge_lora_to_base.py
bash scripts/convert_to_gguf.sh
```

### B. Install Ollama on Server

```bash
# On Alibaba Cloud server
curl -fsSL https://ollama.com/install.sh | sh

# Verify
ollama --version
```

### C. Import Model

```bash
# Import to Ollama
ollama create mysql-nl2sql -f Modelfile

# Verify
ollama list
```

### D. Start Ollama Server

```bash
# Start Ollama as service (runs on port 11434)
ollama serve

# Or run in background
nohup ollama serve > ollama.log 2>&1 &
```

### E. Configure Chatbot

Edit `.env`:
```env
# LLM Configuration
AI_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mysql-nl2sql

# Critical: Increase Timeout for CPU Inference
# Add/Edit this in config.py or code if not env-controlled, 
# but for Streamlit ensure header timeout is 600s
STREAMLIT_TIMEOUT=600

# Database config...
DB_HOST=localhost
DB_PASSWORD=your_password

# NOTE: Ensure you apply the JSON parsing fixes in `llm/base_client.py` 
# and `streamlit_app.py` regex fix before deploying!
```

### F. Start Services

```bash
# Start backend
python main.py

# Start frontend (in another terminal)
streamlit run streamlit_app.py
```

---

## 📊 Performance Expectations

### CPU Inference (Alibaba Cloud, 4-core CPU)

| Metric | Value |
|--------|-------|
| **First token** | 3-5 seconds |
| **Tokens/second** | 5-10 tokens/sec |
| **Total inference** | 5-10 seconds |
| **RAM usage** | 6-8 GB |
| **CPU usage** | 80-100% during inference |

**Acceptable untuk:**
- ✅ Development/testing
- ✅ Production dengan traffic rendah-sedang (<100 users)
- ✅ Internal tools

**Tidak ideal untuk:**
- ❌ High traffic (>1000 concurrent users)
- ❌ Real-time applications (<1s latency)

---

## 🔧 Optimizations

### 1. Increase CPU Cores

Ollama supports multi-threading:
```bash
# Set environment variable
export OLLAMA_NUM_PARALLEL=4  # Number of CPU cores
ollama serve
```

### 2. Use Smaller Quantization

For even faster inference (dengan sedikit accuracy loss):
```bash
# Quantize to Q3_K_M (smaller, faster)
./llama.cpp/quantize merged-mistral-nl2sql-f16.gguf \
    merged-mistral-nl2sql-Q3_K_M.gguf Q3_K_M

# ~3GB, faster
```

### 3. Increase RAM

Consider upgrading server to 16GB or 32GB RAM for better performance.

---

## 🐛 Troubleshooting

### "Out of memory" during conversion

```bash
# Use smaller batch size
python scripts/merge_lora_to_base.py --batch-size 1

# Or run on local machine with more RAM
```

### Ollama "model not found"

```bash
# List models
ollama list

# Recreate
ollama create mysql-nl2sql -f Modelfile
```

### Slow inference (>30 seconds)

```bash
# Check CPU cores
nproc

# Increase parallelism
export OLLAMA_NUM_PARALLEL=8
ollama serve
```

---

## 💰 Cost Comparison

| Deployment | Cost/month | Inference Speed |
|------------|-----------|-----------------|
| **CPU (Alibaba)** | $30-50 | 5-10s |
| **GPU (T4)** | $360+ | 1-2s |
| **Serverless GPU** | $50-100 (pay-per-use) | 1-2s |

**CPU deployment adalah most cost-effective untuk traffic sedang!**

---

## ✅ Quick Commands

```bash
# Merge LoRA
python scripts/merge_lora_to_base.py

# Convert to GGUF
bash scripts/convert_to_gguf.sh

# Import to Ollama
ollama create mysql-nl2sql -f Modelfile

# Test
ollama run mysql-nl2sql "test query"

# Deploy
ollama serve  # Terminal 1
python main.py  # Terminal 2
streamlit run streamlit_app.py  # Terminal 3
```

---

## 🎯 Next Steps

1. ✅ Merge LoRA adapter
2. ✅ Convert to GGUF + quantize
3. ✅ Import to Ollama
4. ✅ Deploy to Alibaba Cloud CPU server
5. ✅ Configure chatbot
6. ✅ Test & monitor performance

**Total setup time: 30-60 minutes** (mostly waiting for conversion)
