import os
import sys
from google import genai

# Fix encoding untuk Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("GOOGLE_API_KEY tidak ditemukan!")
    api_key = input("Masukkan GOOGLE_API_KEY: ").strip()

print("Mengambil daftar model yang tersedia...")
print("=" * 70)

try:
    client = genai.Client(api_key=api_key)
    
    # List all available models
    models = client.models.list()
    
    print(f"\n✓ Ditemukan {len(list(models))} model\n")
    print("-" * 70)
    
    # List models again for iteration (since models is a generator)
    for model in client.models.list():
        model_name = model.name if hasattr(model, 'name') else str(model)
        print(f"📦 {model_name}")
        
        # Show supported generation methods if available
        if hasattr(model, 'supported_generation_methods'):
            methods = model.supported_generation_methods
            if methods:
                print(f"   ✓ Supported: {', '.join(methods)}")
    
    print("-" * 70)
    print("\n✓ Berhasil mengambil daftar model!")
    
except Exception as e:
    print(f"✗ Error: {str(e)}")
    print("\nPastikan:")
    print("1. API key valid")
    print("2. Koneksi internet aktif")
