
import sys
import os
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

def run_security_audit():
    print("[SECURITY] Starting Security Audit...")
    print("=" * 60)
    
    client = TestClient(app)
    
    # 1. Test Protected Endpoint Access (No Token)
    print("\n1. Testing Protected Endpoint (No Token)...")
    response = client.get("/api/auth/me")
    if response.status_code == 403 or response.status_code == 401:
        print("   [PASS] Access denied as expected (Status: 403/401)")
    else:
        print(f"   [FAIL] Unexpected status code: {response.status_code}")

    # 2. Test Protected Endpoint (Invalid Token)
    print("\n2. Testing Protected Endpoint (Invalid Token)...")
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
    if response.status_code == 401 or response.status_code == 403:
        print("   [PASS] Access denied as expected (Status: 403/401)")
    else:
        print(f"   [FAIL] Unexpected status code: {response.status_code}")

    # 3. Test Login (SQL Injection Attempt)
    print("\n3. Testing Login SQL Injection...")
    payload = {
        "username_or_email": "' OR '1'='1",
        "password": "password"
    }
    
    response = client.post("/api/auth/login", json=payload)
    if response.status_code != 200:
        print(f"   [PASS] SQL Injection attempt failed (Status: {response.status_code})")
    else:
        print("   [FAIL] Login succeeded with SQL injection payload!")

    print("\n" + "=" * 60)
    print("Security Audit Complete.")

if __name__ == "__main__":
    run_security_audit()
