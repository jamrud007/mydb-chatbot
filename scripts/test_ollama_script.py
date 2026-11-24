"""
Test Ollama Connection and Configuration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.ollama_client import OllamaClient
from llm.llm_factory import LLMFactory
from config import Config

def test_ollama_direct():
    """Test Ollama client directly"""
    print("=" * 60)
    print("Testing Ollama Client Direct Connection")
    print("=" * 60)
    
    try:
        client = OllamaClient(
            base_url=Config.OLLAMA_BASE_URL,
            model=Config.OLLAMA_MODEL
        )
        
        print(f"✓ Ollama client created")
        print(f"  Base URL: {client.base_url}")
        print(f"  Model: {client.model}")
        
        # Test connection
        print("\nTesting connection...")
        if client.test_connection():
            print("✓ Connection successful!")
            
            # Get available models
            models = client.get_available_models()
            print(f"\nAvailable models ({len(models)}):")
            for model in models:
                marker = "★" if model == client.model else " "
                print(f"  {marker} {model}")
        else:
            print("✗ Connection failed!")
            print("\nTroubleshooting:")
            print("1. Check if Ollama is running: ollama serve")
            print(f"2. Pull the model: ollama pull {client.model}")
            return False
        
        # Test simple query
        print("\n" + "="*60)
        print("Testing simple query...")
        print("="*60)
        
        response = client.get_response("Say 'Hello, I am ready!' in one line.", expect_json=False)
        print(f"\nResponse: {response}")
        print("✓ Query successful!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_llm_factory():
    """Test LLM factory with configured provider"""
    print("\n" + "=" * 60)
    print("Testing LLM Factory")
    print("=" * 60)
    
    print(f"\nConfigured provider: {Config.AI_PROVIDER}")
    print(f"Fallback providers: {Config.AI_FALLBACK_PROVIDERS}")
    
    try:
        client = LLMFactory.create_with_fallback()
        print(f"✓ Created client: {client.provider_name}")
        
        if client.test_connection():
            print("✓ Connection successful!")
            return True
        else:
            print("✗ Connection failed!")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_sql_generation():
    """Test SQL query generation"""
    print("\n" + "=" * 60)
    print("Testing SQL Generation")
    print("=" * 60)
    
    try:
        client = LLMFactory.create_with_fallback()
        
        prompt = """Generate a SQL query to count all rows in a table called 'orders'.

Respond ONLY with valid JSON in this format:
{
  "suggested_queries": [
    {
      "sql": "SELECT COUNT(*) FROM orders",
      "explanation": "Count all orders"
    }
  ]
}"""
        
        print("\nSending prompt...")
        response = client.get_response(prompt, expect_json=True)
        print(f"\nRaw response:\n{response[:200]}...")
        
        parsed = client.parse_json_response(response)
        print(f"\nParsed JSON:")
        import json
        print(json.dumps(parsed, indent=2))
        
        if 'suggested_queries' in parsed:
            print("\n✓ SQL generation works!")
            return True
        else:
            print("\n✗ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🦙 MySQL Chatbot - Ollama Connection Test\n")
    
    results = []
    
    # Test 1: Direct Ollama connection
    results.append(("Ollama Direct", test_ollama_direct()))
    
    # Test 2: LLM Factory
    results.append(("LLM Factory", test_llm_factory()))
    
    # Test 3: SQL Generation
    results.append(("SQL Generation", test_sql_generation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(r[1] for r in results)
    
    if all_passed:
        print("\n🎉 All tests passed! Ready to use Ollama.")
        print("\nNext steps:")
        print("1. Setup database: mysql -u root -p < sample_db\\create_sample_db.sql")
        print("2. Configure .env file")
        print("3. Run: python app.py")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("1. Start Ollama: ollama serve")
        print(f"2. Pull model: ollama pull {Config.OLLAMA_MODEL}")
        print("3. Check Ollama is running on port 11434")
