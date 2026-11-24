"""Test which LLM client the factory creates."""
from dotenv import load_dotenv
load_dotenv(override=True)
from core.config import Config

print(f"AI_PROVIDER    : {Config.AI_PROVIDER}")
print(f"OPENAI_BASE_URL: {Config.OPENAI_BASE_URL}")
print(f"OPENAI_MODEL   : {Config.OPENAI_MODEL}")
print()

from llm.llm_factory import LLMFactory
client = LLMFactory.create_client()
print(f"Client class   : {type(client).__name__}")
print(f"Provider name  : {client.provider_name}")
print()

# Quick test
print("Testing generate_queries...")
result = client.get_response("reply with just: HELLO", expect_json=False)
print(f"Response: {result}")
