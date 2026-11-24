"""
Custom LLM Client untuk llm.alimustofa.my.id
Bypass Cloudflare/WAF blocking dengan requests library
"""
import requests
import logging
import json
import re
from llm.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class CustomLLMClient(BaseLLMClient):
    """Client untuk custom LLM endpoint yang block OpenAI client"""
    
    def __init__(self, api_key=None, base_url="https://llm.alimustofa.my.id/v1", model_name="qwen2.5-sql-q5_k_m.gguf"):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model_name = model_name
        self.chat_history = []
        
        logger.info(f"CustomLLMClient initialized - URL: {base_url}, Model: {model_name}")
    
    def get_response(self, prompt, expect_json=True):
        """
        Get response from custom LLM endpoint
        
        Args:
            prompt: Prompt text
            expect_json: Whether to expect JSON response
        
        Returns:
            str: Response text
        """
        try:
            # Add JSON instruction if needed
            if expect_json:
                prompt += "\n\nPlease provide your response in valid JSON format only, without any markdown code blocks or additional text."
            
            logger.info(f"Sending prompt to custom LLM (length: {len(prompt)} chars)")
            
            # Prepare messages
            messages = self.chat_history + [
                {"role": "user", "content": prompt}
            ]
            
            # Send request using requests library (bypasses blocking)
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000
                },
                timeout=60
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract response text
            response_text = data['choices'][0]['message']['content']
            
            logger.info(f"Received response from custom LLM (length: {len(response_text)} chars)")
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": prompt})
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 20 messages
            if len(self.chat_history) > 20:
                self.chat_history = self.chat_history[-20:]
            
            # Clean JSON if expected
            if expect_json:
                response_text = self._clean_json_response(response_text)
            
            return response_text
        
        except Exception as e:
            logger.error(f"Custom LLM API error: {e}")
            raise
    
    def _clean_json_response(self, response):
        """Clean JSON response from markdown or extra text"""
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        return response.strip()
    
    def parse_json_response(self, response):
        """Parse JSON response with error handling"""
        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Response text: {response[:500]}")
            return {
                'error': 'Failed to parse LLM response',
                'raw_response': response
            }
    
    def reset_chat(self):
        """Reset chat session"""
        self.chat_history = []
        logger.info("Chat session reset")
    
    def test_connection(self):
        """Test connection to custom LLM endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Custom LLM connection test failed: {e}")
            return False
    
    def get_chat_history(self):
        """Get chat history"""
        return self.chat_history
