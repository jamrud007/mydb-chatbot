"""
Gemini API Client for Chatbot
"""
import google.generativeai as genai
import logging
import json
import re
from llm.base_client import BaseLLMClient
from config import Config

logger = logging.getLogger(__name__)

class GeminiClient(BaseLLMClient):
    """Manages interactions with Google Gemini API"""
    
    def __init__(self, api_key=None, model_name="gemini-pro"):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (default from config)
            model_name: Model name to use
        """
        super().__init__()
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(model_name)
        
        # Start chat session
        self.chat = self.model.start_chat(history=[])
        
        logger.info("GeminiClient initialized successfully")
    
    def get_response(self, prompt, expect_json=True):
        """
        Get response from Gemini API
        
        Args:
            prompt: Prompt text
            expect_json: Whether to expect JSON response
        
        Returns:
            str: Response text (cleaned if JSON expected)
        """
        try:
            # Add JSON instruction if needed
            if expect_json:
                prompt += "\n\nPlease provide your response in valid JSON format only, without any markdown code blocks or additional text."
            
            logger.info(f"Sending prompt to Gemini (length: {len(prompt)} chars)")
            
            # Send message
            response = self.chat.send_message(prompt)
            
            # Extract text from response
            response_text = response.text
            
            logger.info(f"Received response from Gemini (length: {len(response_text)} chars)")
            
            # Clean JSON if expected
            if expect_json:
                response_text = self._clean_json_response(response_text)
            
            return response_text
        
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
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
        self.chat = self.model.start_chat(history=[])
        logger.info("Chat session reset")
    
    def test_connection(self):
        """
        Test connection to Gemini API
        
        Returns:
            bool: True if connection successful
        """
        try:
            # Try a simple generation
            test_response = self.model.generate_content("Hello")
            return bool(test_response.text)
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
    
    def get_chat_history(self):
        """Get chat history"""
        return self.chat.history
