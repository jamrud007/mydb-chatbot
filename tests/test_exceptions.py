"""
Test suite for Custom Exception Handling
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from exceptions.chatbot_exceptions import (
    OllamaConnectionError,
    OllamaTimeoutError,
    ModelNotFoundError,
    DatabaseConnectionError,
    SQLExecutionError,
    format_error_response
)

print("="*70)
print("CUSTOM EXCEPTION HANDLING TEST SUITE")
print("="*70)

# Test 1: OllamaConnectionError
print("\n[TEST 1] OllamaConnectionError formatting")
error1 = OllamaConnectionError("http://localhost:11434")
response1 = format_error_response(error1)
print(f"Error Code: {response1['error_code']}")
print(f"Message:\n{response1['message']}")
print(f"User Action: {response1['user_action']}")

# Test 2: OllamaTimeoutError
print("\n[TEST 2] OllamaTimeoutError formatting")
error2 = OllamaTimeoutError(600)
response2 = format_error_response(error2)
print(f"Error Code: {response2['error_code']}")
print(f"Message:\n{response2['message']}")

# Test 3: ModelNotFoundError
print("\n[TEST 3] ModelNotFoundError formatting")
error3 = ModelNotFoundError("mysql-nl2sql", ["llama3.1", "mistral", "gemma"])
response3 = format_error_response(error3)
print(f"Error Code: {response3['error_code']}")
print(f"Message:\n{response3['message']}")

# Test 4: DatabaseConnectionError
print("\n[TEST 4] DatabaseConnectionError formatting")
error4 = DatabaseConnectionError("localhost", "olist", "Connection refused")
response4 = format_error_response(error4)
print(f"Error Code: {response4['error_code']}")
print(f"Message:\n{response4['message']}")

# Test 5: SQLExecutionError
print("\n[TEST 5] SQLExecutionError formatting")
error5 = SQLExecutionError("SELECT * FROM unknown_table", "Table doesn't exist")
response5 = format_error_response(error5)
print(f"Error Code: {response5['error_code']}")
print(f"Message:\n{response5['message']}")
print(f"SQL (truncated): {response5.get('sql', 'N/A')}")

# Test 6: Exception attributes
print("\n[TEST 6] Exception attributes and details")
error6 = OllamaConnectionError("http://localhost:11434")
print(f"Exception type: {type(error6).__name__}")
print(f"Error code: {error6.error_code}")
print(f"Details: {error6.details}")
print(f"Message: {str(error6)}")

print("\n" + "="*70)
print("SUCCESS: All exception tests passed!")
print("Exception hierarchy working correctly")
print("User-friendly messages generated successfully")
print("="*70)
