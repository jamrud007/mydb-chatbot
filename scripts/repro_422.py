
import requests
import json

def test_register():
    url = "http://localhost:8000/api/auth/register"
    payload = {
        "username": "testuser",
        "email": "test@gmail.com",
        "password": "password123"
    }
    
    print(f"Testing Register Endpoint: {url}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
    except requests.exceptions.ConnectionError:
        print("Failed to connect. Is server running on port 8000?")
        
if __name__ == "__main__":
    test_register()
