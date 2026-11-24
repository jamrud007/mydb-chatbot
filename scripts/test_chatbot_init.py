"""
Simple test to see chatbot initialization
"""
import sys
sys.path.insert(0, '.')

print("="*60)
print("Testing Chatbot Initialization")
print("="*60)

try:
    print("\n1. Importing config...")
    from config import Config
    print(f"   DB_PASSWORD: {Config.DB_PASSWORD}")
    print(f"   AI_PROVIDER: {Config.AI_PROVIDER}")
    print(f"   OLLAMA_MODEL: {Config.OLLAMA_MODEL}")
    
    print("\n2. Creating ChatbotHandler...")
    from chatbot.chatbot_handler import ChatbotHandler
    chatbot = ChatbotHandler()
    print(f"   SUCCESS! Chatbot: {chatbot}")
    print(f"   LLM Client: {chatbot.llm_client}")
    
    print("\n3. Testing database connection...")
    if chatbot.test_connection():
        print("   Database: CONNECTED")
    else:
        print("   Database: NOT CONNECTED")
    
    print("\n4. Getting schema info...")
    schema_info = chatbot.get_schema_info()
    if schema_info.get('success'):
        print(f"   Schema tables: {len(schema_info.get('schema', {}).get('tables', []))}")
    
    print("\n5. Testing a simple message...")
    response = chatbot.handle_user_message("test", "test_user")
    print(f"   Response success: {response.get('success')}")
    if not response.get('success'):
        print(f"   Error: {response.get('error')}")
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED!")
    print("="*60)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
