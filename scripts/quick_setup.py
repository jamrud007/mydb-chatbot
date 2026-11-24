"""
Quick Setup Script - Run this for fast deployment
"""
import subprocess
import sys

def run_cmd(cmd, description):
    """Run command and show status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"  [OK] {description} complete")
            if result.stdout.strip():
                print(f"  Output: {result.stdout.strip()[:200]}")
            return True
        else:
            print(f"  [FAIL] {description} failed")
            if result.stderr.strip():
                print(f"  Error: {result.stderr.strip()[:200]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  [TIMEOUT] {description} took too long")
        return False
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False

def main():
    print("="*60)
    print("  Quick Setup - MySQL Chatbot")
    print("="*60)
    
    # Step 1: Check Ollama
    print("\n[Step 1/3] Checking Ollama...")
    if run_cmd("ollama list", "List Ollama models"):
        print("  Ollama is installed and running!")
    else:
        print("\n  Ollama not found or not running.")
        print("  Please:")
        print("  1. Install: winget install Ollama.Ollama")
        print("  2. Start Ollama from Start menu")
        print("  3. Pull model: ollama pull llama3.1")
        return False
    
    # Step 2: Test Ollama connection
    print("\n[Step 2/3] Testing Ollama connection...")
    if run_cmd('python tests\\test_ollama.py', "Test Ollama"):
        print("  Ollama test passed!")
    else:
        print("  Ollama test failed. Please check:")
        print("  - Is Ollama running?")
        print("  - Is llama3.1 model pulled?")
        return False
    
    # Step 3: Run application
    print("\n[Step 3/3] Ready to run application!")
    print("\nTo start the application:")
    print("  python app.py")
    print("\nThen open: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n" + "="*60)
        print("  Setup incomplete. Please fix issues above.")
        print("="*60)
        sys.exit(1)
    else:
        print("\n" + "="*60)
        print("  Setup complete! Ready to deploy.")
        print("="*60)
        sys.exit(0)
