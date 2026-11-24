"""
Script untuk merge LoRA adapter dengan base model dan convert ke GGUF
Run di environment yang punya RAM cukup (16GB+)
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

print("=" * 60)
print("🔄 LoRA to GGUF Conversion Pipeline")
print("=" * 60)
print()

# Configuration
BASE_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
LORA_ADAPTER = "./nl2sql-json-v2-adapter-manual"
OUTPUT_DIR = "./merged-mistral-nl2sql"

print(f"📦 Base Model: {BASE_MODEL}")
print(f"🔧 LoRA Adapter: {LORA_ADAPTER}")
print(f"💾 Output Directory: {OUTPUT_DIR}")
print()

# Step 1: Load base model
print("Step 1/4: Loading base model...")
print("This may take 5-10 minutes (downloading ~14GB)...")
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
print("✅ Base model loaded")
print()

# Step 2: Load LoRA adapter
print("Step 2/4: Loading LoRA adapter...")
model = PeftModel.from_pretrained(
    base_model,
    LORA_ADAPTER
)
print("✅ LoRA adapter loaded")
print()

# Step 3: Merge LoRA weights into base model
print("Step 3/4: Merging LoRA weights...")
print("This will take 2-5 minutes...")
merged_model = model.merge_and_unload()
print("✅ Merge complete")
print()

# Step 4: Save merged model
print("Step 4/4: Saving merged model...")
os.makedirs(OUTPUT_DIR, exist_ok=True)

merged_model.save_pretrained(
    OUTPUT_DIR,
    safe_serialization=True,  # Save as safetensors
    max_shard_size="5GB"
)
print("✅ Model saved")
print()

# Save tokenizer
print("Saving tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.save_pretrained(OUTPUT_DIR)
print("✅ Tokenizer saved")
print()

print("=" * 60)
print("✅ MERGE COMPLETE!")
print("=" * 60)
print()
print(f"Merged model location: {OUTPUT_DIR}/")
print()
print("Next steps:")
print("  1. Convert to GGUF: bash scripts/convert_to_gguf.sh")
print("  2. Import to Ollama: ollama create mysql-nl2sql -f Modelfile")
print("  3. Test: ollama run mysql-nl2sql")
print()
print("Files created:")
for root, dirs, files in os.walk(OUTPUT_DIR):
    for file in files[:10]:  # Show first 10 files
        filepath = os.path.join(root, file)
        size = os.path.getsize(filepath) / (1024**3)  # GB
        print(f"  - {file} ({size:.2f} GB)")
print()
