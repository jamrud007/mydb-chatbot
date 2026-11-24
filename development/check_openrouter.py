import os
from dotenv import load_dotenv
import requests

load_dotenv()

print("=" * 70)
print("CHECKING OPENROUTER API KEY")
print("=" * 70)

api_key = os.getenv("OPENAI_API_KEY")
print(f"\nAPI Key: {api_key[:20]}...{api_key[-10:]}")

# Test 1: Check key info
print("\n[TEST 1] Checking key information...")
headers = {
    'Authorization': f'Bearer {api_key}',
    'HTTP-Referer': 'http://localhost',
    'X-Title': 'MySQL Chatbot'
}

try:
    r = requests.get('https://openrouter.ai/api/v1/auth/key', headers=headers)
    print(f"Status: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"\n✓ Key is VALID")
        print(f"  Label: {data.get('data', {}).get('label', 'N/A')}")
        print(f"  Usage: ${data.get('data', {}).get('usage', 0):.4f}")
        print(f"  Limit: ${data.get('data', {}).get('limit', 'unlimited')}")
        
        limit = data.get('data', {}).get('limit')
        usage = data.get('data', {}).get('usage', 0)
        
        if limit and usage >= limit:
            print(f"\n⚠ WARNING: Credit limit reached!")
            print(f"  Usage: ${usage:.4f} / ${limit:.4f}")
        elif limit:
            remaining = limit - usage
            print(f"\n✓ Credits remaining: ${remaining:.4f}")
    else:
        print(f"\n✗ Key check failed")
        print(f"Response: {r.text}")
        
except Exception as e:
    print(f"\n✗ Error: {e}")

# Test 2: Test model list
print("\n\n[TEST 2] Checking model availability...")
try:
    r = requests.get('https://openrouter.ai/api/v1/models', headers=headers)
    if r.status_code == 200:
        models = r.json().get('data', [])
        current_model = os.getenv("OPENAI_MODEL", "google/gemini-2.5-flash")
        
        # Find current model
        model_found = False
        for model in models:
            if model.get('id') == current_model:
                model_found = True
                print(f"\n✓ Current model '{current_model}' is available")
                print(f"  Pricing:")
                print(f"    Prompt: ${model.get('pricing', {}).get('prompt', 0)}/token")
                print(f"    Completion: ${model.get('pricing', {}).get('completion', 0)}/token")
                break
        
        if not model_found:
            print(f"\n⚠ Model '{current_model}' not found!")
            print("Available models include:")
            for model in models[:5]:
                print(f"  - {model.get('id')}")
    else:
        print(f"✗ Failed to get models: {r.status_code}")
        
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
