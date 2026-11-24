#!/bin/bash
# Start vLLM Server with Mistral-7B LoRA Adapter
# Usage: bash scripts/start_vllm_server.sh

set -e

echo "🚀 Starting vLLM Server with LoRA Adapter..."

# Configuration
BASE_MODEL="mistralai/Mistral-7B-Instruct-v0.3"
LORA_PATH="./nl2sql-json-v2-adapter-manual"
HOST="0.0.0.0"
PORT="8080"
MAX_MODEL_LEN="4096"

# Check if LoRA adapter exists
if [ ! -d "$LORA_PATH" ]; then
    echo "❌ Error: LoRA adapter not found at $LORA_PATH"
    echo "Please ensure your fine-tuned adapter is in the correct directory."
    exit 1
fi

echo "📦 Base Model: $BASE_MODEL"
echo "🔧 LoRA Adapter: $LORA_PATH"
echo "🌐 Server: http://$HOST:$PORT"

# Start vLLM server
python -m vllm.entrypoints.openai.api_server \
    --model "$BASE_MODEL" \
    --enable-lora \
    --lora-modules nl2sql="$LORA_PATH" \
    --host "$HOST" \
    --port "$PORT" \
    --dtype auto \
    --max-model-len "$MAX_MODEL_LEN" \
    --gpu-memory-utilization 0.9 \
    --trust-remote-code

echo "✅ Server started successfully!"
