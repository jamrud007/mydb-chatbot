import requests
import json
import time

print("=" * 60)
print("TESTING API /api/chat ENDPOINT")
print("=" * 60)

url = "http://localhost:8000/api/chat"
payload = {
    "message": "Top 5 kategori dengan revenue tertinggi",
    "user_id": "test_user"
}

print(f"\nSending request to: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nWaiting for response...")

start_time = time.time()

try:
    response = requests.post(url, json=payload, timeout=60)
    elapsed = time.time() - start_time
    
    print(f"\n✅ Response received in {elapsed:.2f} seconds")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nSuccess: {data.get('success')}")
        print(f"Message: {data.get('message', '')[:100]}...")
        print(f"Suggested Queries: {data.get('query_count', 0)}")
    else:
        print(f"\nError Response:")
        print(response.text)
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"\n❌ TIMEOUT after {elapsed:.2f} seconds")
    print("LLM provider is taking too long to respond")
    
except Exception as e:
    elapsed = time.time() - start_time
    print(f"\n❌ ERROR after {elapsed:.2f} seconds")
    print(f"Error: {str(e)}")

print("\n" + "=" * 60)
