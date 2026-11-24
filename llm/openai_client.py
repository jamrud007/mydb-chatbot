"""
OpenAI API Client for Chatbot
"""
import openai
import logging
import json
import re
import time
from llm.base_client import BaseLLMClient
from config import Config
from utils.metrics import get_metrics_collector

logger = logging.getLogger(__name__)

class OpenAIClient(BaseLLMClient):
    """Manages interactions with OpenAI API (and compatible providers like DeepSeek)"""
    
    def __init__(self, api_key=None, model_name="gpt-4o-mini", base_url=None):
        """
        Initialize OpenAI client
        
        Args:
            api_key: OpenAI API key (default from config)
            model_name: Model name to use (gpt-4o-mini, gpt-4o, deepseek-chat, etc.)
            base_url: Custom API base URL (e.g., for DeepSeek: https://api.deepseek.com)
        """
        super().__init__()
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model_name = model_name
        self.base_url = base_url
        
        # Configure OpenAI client
        openai.api_key = self.api_key
        
        # Use custom base URL if provided (for DeepSeek, etc.)
        if base_url:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=base_url)
            logger.info(f"OpenAIClient initialized with custom base URL: {base_url}")
        else:
            self.client = openai.OpenAI(api_key=self.api_key)
        
        # Chat history for context
        self.chat_history = []
        
        logger.info(f"OpenAIClient initialized with model: {model_name}")
    
    def get_response(self, prompt, expect_json=True):
        """
        Get response from OpenAI API
        
        Args:
            prompt: Prompt text
            expect_json: Whether to expect JSON response
        
        Returns:
            str: Response text (cleaned if JSON expected)
        """
        max_retries = 3
        retry_delay = 2  # seconds, doubles each attempt

        if expect_json:
            prompt += "\n\nPlease provide your response in valid JSON format only, without any markdown code blocks or additional text."

        logger.info(f"Sending prompt to OpenAI (length: {len(prompt)} chars)")

        messages = self.chat_history + [{"role": "user", "content": prompt}]

        last_error = None
        for attempt in range(1, max_retries + 1):
            _t0 = time.time()
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=Config.LLM_TEMPERATURE,
                    max_tokens=2000
                )

                response_text = response.choices[0].message.content
                _duration_ms = (time.time() - _t0) * 1000
                logger.info(f"Received response from OpenAI (length: {len(response_text)} chars)")
                get_metrics_collector().record_llm_call(_duration_ms, success=True)

                self.chat_history.append({"role": "user", "content": prompt})
                self.chat_history.append({"role": "assistant", "content": response_text})
                # Keep only last 3 exchanges (6 messages) to fit small context models
                if len(self.chat_history) > 6:
                    self.chat_history = self.chat_history[-6:]

                if expect_json:
                    response_text = self._clean_json_response(response_text)

                return response_text

            except (openai.APIConnectionError, openai.APITimeoutError) as e:
                _duration_ms = (time.time() - _t0) * 1000
                get_metrics_collector().record_llm_call(_duration_ms, success=False)
                last_error = e
                if attempt < max_retries:
                    logger.warning(f"OpenAI connection error (attempt {attempt}/{max_retries}), retrying in {retry_delay}s: {e}")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"OpenAI API error after {max_retries} attempts: {e}")
                    raise

            except Exception as e:
                get_metrics_collector().record_llm_call((time.time() - _t0) * 1000, success=False)
                logger.error(f"OpenAI API error: {e}")
                raise
    
    def _clean_json_response(self, response):
        """
        Clean JSON response from markdown or extra text
        
        Args:
            response: Raw response text
        
        Returns:
            str: Cleaned JSON string
        """
        # Remove markdown code blocks
        response = re.sub(r'```json\s*', '', response)
        response = re.sub(r'```\s*', '', response)
        
        # Try to find JSON object
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            response = json_match.group(0)
        
        return response.strip()
    
    def parse_json_response(self, response):
        """
        Parse JSON response with error handling
        
        Args:
            response: JSON string
        
        Returns:
            dict: Parsed JSON or error dict
        """
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
        """Reset chat session (clear history)"""
        self.chat_history = []
        logger.info("Chat session reset")
    
    def test_connection(self):
        """
        Test connection to OpenAI API
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Try a simple generation
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def get_chat_history(self):
        """Get chat history"""
        return self.chat_history
