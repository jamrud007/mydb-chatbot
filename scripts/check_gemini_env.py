import sys
from google import genai
from dotenv import load_dotenv
import os

# Fix encoding untuk Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load API key dari file .env
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ GOOGLE_API_KEY tidak ditemukan di file .env!")
    exit(1)

print("✓ API key loaded dari file .env")
print("Testing Gemini API...")
print("-" * 60)

try:
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Jelaskan apa itu AI dalam 1 kalimat",
    )
    
    print("\n✓ Berhasil! Response dari Gemini:")
    print("-" * 60)
    print(response.text)
    print("-" * 60)
    
except Exception as e:
    print(f"❌ Error: {str(e)[:200]}")
