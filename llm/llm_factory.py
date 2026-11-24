"""
LLM Factory - Creates appropriate LLM client based on configuration
"""
import logging
from typing import Any, Dict, List, Optional

from config import Config
from llm.base_client import BaseLLMClient

logger = logging.getLogger(__name__)

class LLMFactory:
    """Factory for creating LLM clients"""
    
    @staticmethod
    def create_client(provider: Optional[str] = None) -> BaseLLMClient:
        """Create LLM client based on provider (None → Config.AI_PROVIDER)."""
        provider = provider or Config.AI_PROVIDER
        provider = provider.lower()
        
        logger.info(f"Creating LLM client for provider: {provider}")
        
        if provider == 'ollama':
            from llm.ollama_client import OllamaClient
            return OllamaClient(
                base_url=Config.OLLAMA_BASE_URL,
                model=Config.OLLAMA_MODEL
            )
        
        elif provider == 'gemini':
            from llm.gemini_client import GeminiClient
            return GeminiClient(
                api_key=Config.GEMINI_API_KEY,
                model_name=Config.GEMINI_MODEL
            )
        
        
        elif provider == 'openai':
            # Check if using custom endpoint that blocks OpenAI client
            if Config.OPENAI_BASE_URL and 'alimustofa.my.id' in Config.OPENAI_BASE_URL:
                from llm.custom_llm_client import CustomLLMClient
                logger.info("Using CustomLLMClient to bypass blocking")
                return CustomLLMClient(
                    api_key=Config.OPENAI_API_KEY,
                    base_url=Config.OPENAI_BASE_URL,
                    model_name=Config.OPENAI_MODEL
                )
            else:
                from llm.openai_client import OpenAIClient
                return OpenAIClient(
                    api_key=Config.OPENAI_API_KEY,
                    model_name=Config.OPENAI_MODEL,
                    base_url=Config.OPENAI_BASE_URL
                )
        
        elif provider == 'deepseek':
            from llm.openai_client import OpenAIClient
            return OpenAIClient(
                api_key=Config.DEEPSEEK_API_KEY,
                model_name=Config.DEEPSEEK_MODEL,
                base_url=Config.DEEPSEEK_BASE_URL
            )
        
        elif provider == 'claude':
            # Future implementation
            raise NotImplementedError("Claude provider not yet implemented")
        
        else:
            raise ValueError(f"Unknown provider: {provider}. Supported: ollama, gemini, openai, deepseek")
    
    @staticmethod
    def create_with_fallback() -> BaseLLMClient:
        """Create LLM client with automatic fallback."""
        # Try primary provider
        try:
            client = LLMFactory.create_client(Config.AI_PROVIDER)
            if client.test_connection():
                logger.info(f"Using primary provider: {Config.AI_PROVIDER}")
                return client
            else:
                logger.warning(f"Primary provider {Config.AI_PROVIDER} connection failed")
        except Exception as e:
            logger.error(f"Failed to create primary provider {Config.AI_PROVIDER}: {e}")
        
        # Try fallback providers
        fallback_providers = Config.AI_FALLBACK_PROVIDERS
        if not fallback_providers:
            raise Exception(f"Primary provider {Config.AI_PROVIDER} failed and no fallback configured")
        
        for fallback in fallback_providers:
            try:
                logger.info(f"Trying fallback provider: {fallback}")
                client = LLMFactory.create_client(fallback)
                if client.test_connection():
                    logger.info(f"Using fallback provider: {fallback}")
                    return client
            except Exception as e:
                logger.error(f"Fallback provider {fallback} failed: {e}")
                continue
        
        raise Exception("All AI providers failed to connect")
    
    @staticmethod
    def get_available_providers() -> List[str]:
        """Get list of available (implemented) providers."""
        return ['ollama', 'gemini', 'openai', 'deepseek']
    
    @staticmethod
    def test_provider(provider: str) -> Dict[str, Any]:
        """Test if a provider is available and working."""
        try:
            client = LLMFactory.create_client(provider)
            is_connected = client.test_connection()
            
            return {
                'provider': provider,
                'available': True,
                'connected': is_connected,
                'error': None
            }
        except Exception as e:
            return {
                'provider': provider,
                'available': False,
                'connected': False,
                'error': str(e)
            }
