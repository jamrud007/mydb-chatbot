"""
Debug script untuk test Streamlit API call
"""
import httpx
import json

print("=" * 60)
print("TESTING STREAMLIT -> API COMMUNICATION")
print("=" * 60)

API_BASE_URL = "http://localhost:8000"

# Test 1: Health check
print("\n[TEST 1] Health Check")
try:
    with httpx.Client(timeout=5.0) as client:
        r = client.get(f"{API_BASE_URL}/api/health")
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Chat endpoint
print("\n[TEST 2] Chat Endpoint (with 120s timeout)")
try:
    with httpx.Client(timeout=120.0) as client:
        payload = {
            "message": "Top 5 kategori dengan revenue tertinggi",
            "user_id": "test_streamlit"
        }
        print(f"Sending: {json.dumps(payload, indent=2)}")
        print("Waiting for response (max 120s)...")
        
        r = client.post(f"{API_BASE_URL}/api/chat", json=payload)
        print(f"\nStatus: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Success: {data.get('success')}")
            print(f"Message: {data.get('message', '')[:100]}...")
            print(f"Query Count: {data.get('query_count')}")
            
            if data.get('suggested_queries'):
                print(f"\nFirst suggested query:")
                q = data['suggested_queries'][0]
                print(f"  SQL: {q.get('sql', '')[:100]}...")
                print(f"  Explanation: {q.get('explanation', '')[:100]}...")
        else:
            print(f"Error: {r.text}")
            
except httpx.TimeoutException:
    print("TIMEOUT! LLM took too long")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
