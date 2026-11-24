"""
Ollama LLM Client for Local AI
"""
import requests
import logging
import json
from llm.base_client import BaseLLMClient
from exceptions.chatbot_exceptions import (
    OllamaConnectionError,
    OllamaTimeoutError,
    ModelNotFoundError,
    JSONParseError
)
from core.config import Config

logger = logging.getLogger(__name__)

class OllamaClient(BaseLLMClient):
    """Client for Ollama local LLM"""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1", timeout: int = None):
        """
        Initialize Ollama client
        
        Args:
            base_url: Base URL for Ollama API
            model: Model name to use
            timeout: Request timeout in seconds (default 600)
        """
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout if timeout is not None else Config.LLM_TIMEOUT
        self.chat_history = []
        self.provider_name = "ollama"

        logger.info(f"Ollama client initialized: {base_url}, model: {model}, timeout: {self.timeout}")
    
    def get_response(self, prompt, expect_json=True):
        """
        Get response from Ollama
        
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
            
            logger.info(f"Sending prompt to Ollama (model: {self.model}, length: {len(prompt)} chars)")
            
            # Prepare messages
            messages = self.chat_history + [
                {"role": "user", "content": prompt}
            ]
            
            # Call Ollama API
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "num_predict": 2048,  # Limit max tokens increased to prevent json truncation
                        "temperature": 0.2   # Explicitly low temperature for consistency
                    }
                },
                timeout=self.timeout  # Use configured timeout
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Extract response text
            response_text = result['message']['content']
            
            logger.debug(f"Received raw response from Ollama: {response_text}")
            logger.info(f"Received response from Ollama (length: {len(response_text)} chars)")
            
            # Update chat history
            self.chat_history.append({"role": "user", "content": prompt})
            self.chat_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 exchanges to manage context size
            if len(self.chat_history) > 20:  # 10 exchanges * 2 messages
                self.chat_history = self.chat_history[-20:]
            
            # Clean JSON if expected
            if expect_json:
                response_text = self._clean_json_response(response_text)
            
            return response_text
        
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to Ollama server at {self.base_url}")
            raise OllamaConnectionError(self.base_url)
        
        except requests.exceptions.Timeout as e:
            logger.error(f"Ollama request timeout: {e}")
            raise OllamaTimeoutError(self.timeout)
        
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    def reset_chat(self):
        """Reset chat history"""
        self.chat_history = []
        logger.info("Ollama chat history reset")
    
    def test_connection(self):
        """
        Test connection to Ollama server
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Check if server is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            # Check if model is available
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            
            if self.model not in model_names:
                logger.warning(f"Model '{self.model}' not found. Available models: {model_names}")
                raise ModelNotFoundError(self.model, model_names)
            
            logger.info(f"Ollama connection successful, model '{self.model}' available")
            return True
        
        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to Ollama at {self.base_url}")
            raise OllamaConnectionError(self.base_url)
        
        except Exception as e:
            logger.error(f"Ollama connection test failed: {e}")
            return False
    
    def get_available_models(self):
        """
        Get list of available models
        
        Returns:
            list: Available model names
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            return [m['name'] for m in models]
        except Exception as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def get_chat_history(self):
        """Get current chat history"""
        return self.chat_history
