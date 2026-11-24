#!/bin/bash
# Convert merged model to GGUF format
# Run after merge_lora_to_base.py

set -e

echo "=========================================="
echo "🔄 Converting to GGUF Format"
echo "=========================================="
echo ""

# Configuration
MERGED_MODEL_DIR="./merged-mistral-nl2sql"
OUTPUT_FILE="./merged-mistral-nl2sql-f16.gguf"
QUANTIZED_FILE="./merged-mistral-nl2sql-Q4_K_M.gguf"

# Check if merged model exists
if [ ! -d "$MERGED_MODEL_DIR" ]; then
    echo "❌ Error: Merged model not found at $MERGED_MODEL_DIR"
    echo "Please run: python scripts/merge_lora_to_base.py first"
    exit 1
fi

# Step 1: Clone llama.cpp if not exists
if [ ! -d "llama.cpp" ]; then
    echo "📥 Cloning llama.cpp..."
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    make
    cd ..
    echo "✅ llama.cpp installed"
else
    echo "✅ llama.cpp already exists"
fi
echo ""

# Step 2: Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -q torch transformers sentencepiece protobuf
echo "✅ Dependencies installed"
echo ""

# Step 3: Convert to GGUF (FP16)
echo "🔄 Converting to GGUF (FP16)..."
echo "This will take 5-10 minutes..."
python llama.cpp/convert.py "$MERGED_MODEL_DIR" \
    --outfile "$OUTPUT_FILE" \
    --outtype f16

if [ -f "$OUTPUT_FILE" ]; then
    echo "✅ FP16 GGUF created: $OUTPUT_FILE"
    SIZE=$(du -h "$OUTPUT_FILE" | cut -f1)
    echo "   Size: $SIZE"
else
    echo "❌ Conversion failed"
    exit 1
fi
echo ""

# Step 4: Quantize to Q4_K_M (recommended for CPU)
echo "🗜️  Quantizing to Q4_K_M..."
echo "This will reduce size from ~14GB to ~4GB..."
./llama.cpp/quantize "$OUTPUT_FILE" "$QUANTIZED_FILE" Q4_K_M

if [ -f "$QUANTIZED_FILE" ]; then
    echo "✅ Quantized model created: $QUANTIZED_FILE"
    SIZE=$(du -h "$QUANTIZED_FILE" | cut -f1)
    echo "   Size: $SIZE"
else
    echo "❌ Quantization failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ CONVERSION COMPLETE!"
echo "=========================================="
echo ""
echo "Files created:"
echo "  1. FP16 GGUF: $OUTPUT_FILE (~14GB)"
echo "  2. Q4_K_M GGUF: $QUANTIZED_FILE (~4GB) ← Use this for CPU"
echo ""
echo "Next steps:"
echo "  1. Create Modelfile: cat > Modelfile << 'EOF'"
echo "FROM $QUANTIZED_FILE"
echo ""
echo "TEMPLATE \"\"\"[INST] {{ .System }}"
echo ""
echo "{{ .Prompt }} [/INST]\"\"\""
echo ""
echo "PARAMETER temperature 0.1"
echo "PARAMETER top_p 0.9"
echo ""
echo "SYSTEM \"\"\"You are an expert MySQL query generator.\"\"\""
echo "EOF"
echo ""
echo "  2. Import to Ollama: ollama create mysql-nl2sql -f Modelfile"
echo "  3. Test: ollama run mysql-nl2sql 'Generate SQL to find top customers'"
echo ""
