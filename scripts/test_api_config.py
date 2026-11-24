import os
import sys
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("🔍 Checking Gemini API Configuration...")
print("=" * 60)

# Check environment variables
api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
provider = os.getenv("AI_PROVIDER")

print(f"AI_PROVIDER: {provider}")
print(f"GEMINI_MODEL: {model}")
print(f"GEMINI_API_KEY: {api_key[:20]}...{api_key[-10:] if api_key else 'NOT FOUND'}")
print("=" * 60)

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env!")
    exit(1)

# Test API connection
print("\n🧪 Testing Gemini API connection...")
try:
    from google import genai
    
    client = genai.Client(api_key=api_key)
    
    print(f"✓ Client created with model: {model}")
    
    # Test simple request
    print("\n📤 Sending test request...")
    response = client.models.generate_content(
        model=model,
        contents="Say 'Hello' in one word"
    )
    
    print(f"\n✅ SUCCESS! API is working!")
    print(f"Response: {response.text}")
    print("\n" + "=" * 60)
    print("✓ Gemini API configuration is correct!")
    print("✓ You can now start the chatbot server")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)[:500]}")
    print("\n" + "=" * 60)
    print("❌ Gemini API test failed!")
    print("\nPossible causes:")
    print("1. Invalid API key")
    print("2. Quota exceeded")
    print("3. Model not available")
    print("4. Network connection issue")
