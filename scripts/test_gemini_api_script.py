import os
import sys
from google import genai
from google.genai.errors import ClientError

# Fix encoding untuk Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Cara 1: Gunakan environment variable GOOGLE_API_KEY
# Cara 2: Atau set langsung di sini (tidak recommended untuk production)
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("=" * 60)
    print("GOOGLE_API_KEY tidak ditemukan!")
    print("=" * 60)
    print("\nUntuk mendapatkan API key:")
    print("1. Kunjungi: https://aistudio.google.com/apikey")
    print("2. Buat API key baru")
    print("3. Set environment variable:")
    print('   setx GOOGLE_API_KEY "your-api-key-here"')
    print("\nAtau langsung masukkan API key di sini:")
    api_key = input("Masukkan GOOGLE_API_KEY: ").strip()
    
    if not api_key:
        print("API key tidak boleh kosong!")
        exit(1)

print("Testing Gemini API...")
print("-" * 60)

# Daftar model yang akan dicoba (urut berdasarkan prioritas)
models_to_try = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
]

success = False
for model_name in models_to_try:
    try:
        print(f"\nMencoba model: {model_name}")
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
            model=model_name,
            contents="Explain how AI works in a few words",
        )
        
        print("✓ Berhasil! Response dari Gemini:")
        print("-" * 60)
        print(response.text)
        print("-" * 60)
        print(f"\n✓ API Gemini berfungsi dengan baik menggunakan model: {model_name}")
        success = True
        break
        
    except ClientError as e:
        error_code = getattr(e, 'status_code', None) or (e.details.get('code') if hasattr(e, 'details') else None)
        if error_code == 429 or '429' in str(e):
            print(f"✗ Quota habis untuk model {model_name}")
            print(f"   Detail: {str(e)[:200]}...")
            continue
        elif error_code == 404 or '404' in str(e) or 'NOT_FOUND' in str(e):
            print(f"✗ Model {model_name} tidak tersedia")
            continue
        else:
            print(f"✗ Client Error: {str(e)[:250]}")
            continue
    except Exception as e:
        print(f"✗ Error: {str(e)[:200]}")
        continue

if not success:
    print("\n" + "=" * 60)
    print("SEMUA MODEL GAGAL!")
    print("=" * 60)
    print("\nKemungkinan penyebab:")
    print("1. API key quota sudah habis untuk hari ini")
    print("2. API key tidak valid")
    print("3. Koneksi internet bermasalah")
    print("\nSolusi:")
    print("- Tunggu beberapa menit/jam untuk quota reset")
    print("- Cek usage di: https://aistudio.google.com/")
    print("- Atau buat API key baru")
