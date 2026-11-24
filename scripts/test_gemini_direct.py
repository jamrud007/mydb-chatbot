
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load env directly
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

print(f"Testing Gemini API...")
print(f"Key: {api_key[:5]}...")
print(f"Model: {model_name}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    print("Sending request...")
    response = model.generate_content("Hello, reply with 'Gemini OK'")
    print(f"RESPONSE: {response.text}")
except Exception as e:
    print(f"ERROR: {e}")
