
import os
import sys
from dotenv import load_dotenv

# Ensure we can import from current directory
sys.path.append(os.getcwd())

from config import Config
from llm.llm_factory import LLMFactory

def test_ollama():
    print("Loading environment...")
    load_dotenv()
    
    provider = Config.AI_PROVIDER
    base_url = Config.OLLAMA_BASE_URL
    model = Config.OLLAMA_MODEL
    
    print(f"Provider: {provider}")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    if provider != 'ollama':
        print("ERROR: AI_PROVIDER is not set to 'ollama'")
        return
    
    print("\nInitializing Client...")
    try:
        client = LLMFactory.create_client()
    except Exception as e:
        print(f"Failed to create client: {e}")
        return

    print("\nTesting Connection...")
    if client.test_connection():
        print("SUCCESS: Connection established and model found.")
    else:
        print("FAILURE: Could not connect or model not found.")
        return

    print("\nTesting Generation...")
    try:
        response = client.get_response("Hello, say 'Ollama is working' if you can read this.", expect_json=False)
        print(f"Response: {response}")
    except Exception as e:
        print(f"Generation failed: {e}")

if __name__ == "__main__":
    test_ollama()
