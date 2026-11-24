"""Test LLM connection from Python requests."""
import requests, json

BASE_URL = "https://llm.alimustofa.my.id/v1"
API_KEY  = "halotecllm"
MODEL    = "qwen2.5-sql-q5_k_m.gguf"

print(f"Testing: {BASE_URL}")

try:
    r = requests.post(
        f"{BASE_URL}/chat/completions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        json={"model": MODEL, "messages": [{"role": "user", "content": "reply: OK"}], "max_tokens": 5, "temperature": 0.0},
        timeout=30
    )
    print(f"Status : {r.status_code}")
    print(f"Response: {r.json()['choices'][0]['message']['content']}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
