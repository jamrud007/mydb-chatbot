"""
Base LLM Client Interface
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)

class BaseLLMClient(ABC):
    """Abstract base class for all LLM clients"""

    def __init__(self, **kwargs: Any) -> None:
        self.provider_name = self.__class__.__name__.replace('Client', '')
        logger.info(f"Initializing {self.provider_name} client")

    @abstractmethod
    def get_response(self, prompt: str, expect_json: bool = True) -> str:
        """Get response from LLM."""
        pass

    @abstractmethod
    def reset_chat(self) -> None:
        """Reset chat session/history."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to LLM provider."""
        pass

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON response with error handling."""
        import json
        
        try:
            # Clean JSON response
            response = self._clean_json_response(response)
            return json.loads(response)
        except json.JSONDecodeError as e:
            # Fallback for Python-style dicts (single quotes) which 7B models often produce
            try:
                import ast
                # ast.literal_eval safely evaluates a string containing a Python literal
                # This handles single quotes correctly unlike naive string replacement
                fixed_response = ast.literal_eval(response)
                if isinstance(fixed_response, dict):
                    return fixed_response
            except:
                pass
            
            # Log the full failed response for debugging
            logger.error(f"Failed to parse JSON response: {e}")
            print(f"\nDEBUG RAW RESPONSE START:\n{response}\nDEBUG RAW RESPONSE END\n")
            logger.error(f"Raw Invalid Response START:\n{response}\nEND Raw Response")
            
            return {
                'error': 'Failed to parse LLM response',
                'raw_response': response,
                'details': str(e)
            }
    
    def _clean_json_response(self, response: str) -> str:
        """Clean JSON response from markdown or extra text."""
        if not response:
            return ""
            
        # 1. Remove markdown code blocks (```json ... ```)
        if '```' in response:
            # Try to find json block specifically
            import re
            json_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_block:
                return json_block.group(1)
            # Or just any code block
            code_block = re.search(r'```\s*(.*?)\s*```', response, re.DOTALL)
            if code_block:
                response = code_block.group(1)
        
        # 2. Find the first '{' and last '}'
        start = response.find('{')
        end = response.rfind('}')
        
        if start != -1 and end != -1 and end > start:
            response = response[start:end+1]
        
        # 3. Basic cleanup
        response = response.strip()
        
        # 4. Handle common local LLM mistakes (optional)
        # e.g. trailing commas is invalid JSON but common
        # response = re.sub(r',\s*}', '}', response)
        
        return response
    
    def get_provider_info(self) -> Dict[str, str]:
        """Get provider information."""
        return {
            'provider': self.provider_name,
            'status': 'connected' if self.test_connection() else 'disconnected'
        }
