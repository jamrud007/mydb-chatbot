
import os
import sys
import logging
from dotenv import load_dotenv

# Ensure we can import from current directory
sys.path.append(os.getcwd())

# Setup basic logging to console
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

from chatbot.chatbot_handler import ChatbotHandler
from config import Config

def test_specific_query():
    print("=" * 60)
    print("TESTING SPECIFIC QUERY")
    print("=" * 60)

    # Load environment
    load_dotenv()
    
    # Initialize Chatbot
    print("\nInitializing ChatbotHandler...")
    try:
        chatbot = ChatbotHandler()
        if chatbot.test_connection():
            print("[OK] Database connection successful")
        else:
            print("[WARN] Database connection failed")
            return
    except Exception as e:
        print(f"[ERROR] Failed to initialize chatbot: {e}")
        return

    # Specific Query
    # "tampilkan 10 kota customer"
    user_query = "tampilkan 10 kota customer"
    user_id = "test_user_deepseek_city"

    print(f"\nProcessing Query: '{user_query}'")
    
    try:
        # Step 1: Handle User Message (Generate SQL)
        response = chatbot.handle_user_message(user_query, user_id)
        
        if not response['success']:
            print(f"[ERROR] Failed to process message: {response.get('error')}")
            return
            
        print("\n[OK] Message Processed Successfully")
        
        suggested_queries = response.get('suggested_queries', [])
        if not suggested_queries:
            print("[WARN] No suggested queries found.")
            return

        print(f"Found {len(suggested_queries)} suggested queries.")
        
        # Step 2: Execute the first suggested query
        print("\nExecuting first suggested query...")
        query_index = 0
        first_query = suggested_queries[0]
        sql = first_query['sql']
        explanation = first_query['explanation']
        
        print(f"SQL: {sql}")
        print(f"Explanation: {explanation}")
        
        result = chatbot.execute_query_by_index(query_index, user_id)
        
        if not result['success']:
            print(f"[ERROR] Query execution failed: {result.get('error')}")
            if 'message' in result:
                 print(f"Message: {result['message']}")
            return

        print(f"\n[OK] Query Executed Successfully")
        print(f"Row Count: {result['row_count']}")
        print(f"Columns: {result['columns']}")
        
        print(f"\nResults (First 10 rows):")
        for i, row in enumerate(result['results'][:10]):
            print(f"Row {i+1}: {row}")
            
        print("-" * 30)
        if result.get('nl_summary'):
            try:
                print(f"Summary: {result['nl_summary']}")
            except UnicodeEncodeError:
                # Fallback: Strip non-ascii characters entirely for Windows console safety
                safe_summary = result['nl_summary'].encode('ascii', 'ignore').decode('ascii')
                print(f"Summary: {safe_summary}")
             
        if result.get('visualization'):
             print(f"\nVisualization Config Generated: Yes")
    
    except Exception as e:
        print(f"\n[ERROR] Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_specific_query()
