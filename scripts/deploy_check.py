"""
Production Deployment Checklist - Simple Version
"""
import os
import sys
import subprocess
from pathlib import Path

def check_python():
    """Check Python installation"""
    print("\n[1/6] Checking Python...")
    try:
        result = subprocess.run("python --version", capture_output=True, text=True, shell=True)
        print(f"  [OK] {result.stdout.strip()}")
        return True
    except:
        print("  [FAIL] Python not found")
        return False

def check_venv():
    """Check virtual environment"""
    print("\n[2/6] Checking Virtual Environment...")
    if Path("venv").exists():
        print("  [OK] Virtual environment exists")
        return True
    else:
        print("  [FAIL] Virtual environment not found")
        print("  Action: python -m venv venv")
        return False

def check_ollama():
    """Check Ollama server"""
    print("\n[3/6] Checking Ollama...")
    try:
        result = subprocess.run(
            "curl -s http://localhost:11434/api/tags",
            capture_output=True,
            text=True,
            shell=True,
            timeout=5
        )
        if "models" in result.stdout.lower():
            print("  [OK] Ollama server running")
            if "llama3.1" in result.stdout.lower():
                print("  [OK] llama3.1 model available")
                return True
            else:
                print("  [WARN] llama3.1 not found")
                print("  Action: ollama pull llama3.1")
                return False
        else:
            print("  [FAIL] Ollama not responding")
            print("  Action: ollama serve")
            return False
    except:
        print("  [FAIL] Cannot connect to Ollama")
        print("  Action: Start Ollama service")
        return False

def check_mysql():
    """Check MySQL installation"""
    print("\n[4/6] Checking MySQL...")
    try:
        result = subprocess.run("mysql --version", capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"  [OK] {result.stdout.strip()}")
            return True
        else:
            print("  [FAIL] MySQL not in PATH")
            print("  Note: MySQL may be installed but not in system PATH")
            return False
    except:
        print("  [FAIL] MySQL not found")
        return False

def check_env():
    """Check .env configuration"""
    print("\n[5/6] Checking Configuration...")
    if not Path(".env").exists():
        print("  [FAIL] .env file not found")
        print("  Action: copy .env.example .env")
        return False
    
    print("  [OK] .env file exists")
    
    with open(".env") as f:
        content = f.read()
    
    issues = []
    if "AI_PROVIDER=ollama" not in content:
        issues.append("AI_PROVIDER not set to ollama")
    
    if "DB_PASSWORD=" in content and "your_password" in content:
        issues.append("DB_PASSWORD needs to be set")
    
    if issues:
        for issue in issues:
            print(f"  [WARN] {issue}")
        return False
    
    print("  [OK] Configuration looks good")
    return True

def check_dependencies():
    """Check Python dependencies"""
    print("\n[6/6] Checking Dependencies...")
    try:
        import flask
        print("  [OK] flask installed")
    except ImportError:
        print("  [FAIL] flask not installed")
        print("  Action: pip install -r requirements.txt")
        return False
    
    try:
        import mysql.connector
        print("  [OK] mysql-connector-python installed")
    except ImportError:
        print("  [FAIL] mysql-connector-python not installed")
        print("  Action: pip install -r requirements.txt")
        return False
    
    try:
        import requests
        print("  [OK] requests installed")
    except ImportError:
        print("  [FAIL] requests not installed") 
        print("  Action: pip install -r requirements.txt")
        return False
    
    return True

def main():
    print("="*60)
    print("  MySQL Chatbot - Production Deployment Check")
    print("="*60)
    
    checks = [
        ("Python", check_python()),
        ("Virtual Environment", check_venv()),
        ("Ollama", check_ollama()),
        ("MySQL", check_mysql()),
        ("Configuration", check_env()),
        ("Dependencies", check_dependencies())
    ]
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    
    for name, status in checks:
        symbol = "[OK]  " if status else "[FAIL]"
        print(f"{symbol} {name}")
    
    passed = sum(1 for _, status in checks if status)
    total = len(checks)
    
    print(f"\nResult: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n" + "="*60)
        print("  System ready for deployment!")
        print("="*60)
        print("\nNext steps:")
        print("1. Setup database: mysql -u root -p < sample_db\\create_sample_db.sql")
        print("2. Test Ollama: python tests\\test_ollama.py")
        print("3. Run app: python app.py")
    else:
        print("\n" + "="*60)
        print("  Please fix issues above before deployment")
        print("="*60)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck cancelled by user")
        sys.exit(1)
