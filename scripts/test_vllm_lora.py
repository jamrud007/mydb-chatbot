"""
Test script untuk vLLM server dengan LoRA adapter
Usage: python scripts/test_vllm_lora.py
"""
import requests
import json
import sys

# Configuration
VLLM_BASE_URL = "http://localhost:8080/v1"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
LORA_NAME = "nl2sql"

def test_health():
    """Test vLLM server health"""
    print("🔍 Testing vLLM server health...")
    try:
        response = requests.get(f"{VLLM_BASE_URL.replace('/v1', '')}/health")
        if response.status_code == 200:
            print("✅ Server is healthy!")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to vLLM server. Is it running?")
        print(f"   Expected URL: {VLLM_BASE_URL}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_models():
    """List available models"""
    print("\n📋 Listing available models...")
    try:
        response = requests.get(f"{VLLM_BASE_URL}/models")
        if response.status_code == 200:
            models = response.json()
            print(f"✅ Available models: {json.dumps(models, indent=2)}")
            return True
        else:
            print(f"❌ Failed to list models: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sql_generation():
    """Test SQL generation dengan LoRA adapter"""
    print("\n🧪 Testing SQL generation with LoRA adapter...")
    
    test_queries = [
        "Find top 5 customers by total revenue",
        "Count total orders per category",
        "Get average order value by month"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}/3: {query} ---")
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert MySQL query generator for the ecommerce_olist database. Generate valid SQL queries in JSON format with 'sql' and 'explanation' keys."
                },
                {
                    "role": "user",
                    "content": f"Generate SQL query for: {query}"
                }
            ],
            "temperature": 0.1,
            "max_tokens": 512,
            "extra_body": {
                "lora_name": LORA_NAME
            }
        }
        
        try:
            response = requests.post(
                f"{VLLM_BASE_URL}/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"✅ Response:\n{content}\n")
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("vLLM + LoRA Adapter Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server health check failed. Please start vLLM server first:")
        print("   bash scripts/start_vllm_server.sh")
        print("   or")
        print("   scripts\\start_vllm_server.bat")
        sys.exit(1)
    
    # Test 2: List models
    test_models()
    
    # Test 3: SQL generation
    test_sql_generation()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
