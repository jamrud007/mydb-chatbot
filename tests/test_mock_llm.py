
import pytest
from unittest.mock import MagicMock, patch
from chatbot.chatbot_handler import ChatbotHandler
from llm.base_client import BaseLLMClient

@pytest.fixture
def mock_llm_client():
    client = MagicMock(spec=BaseLLMClient)
    client.provider_name = "mock_provider"
    return client

@pytest.fixture
def chatbot(mock_llm_client):
    with patch('chatbot.chatbot_handler.LLMFactory') as MockFactory:
        MockFactory.create_client.return_value = mock_llm_client
        # Mock database components to avoid real DB connection
        with patch('chatbot.chatbot_handler.DatabaseConnection'), \
             patch('chatbot.chatbot_handler.SchemaManager'), \
             patch('chatbot.chatbot_handler.QueryExecutor'), \
             patch('chatbot.chatbot_handler.ConversationManager'):
             
            handler = ChatbotHandler()
            # Replace components with mocks for verification
            handler.llm_client = mock_llm_client
            handler.query_generator = MagicMock()
            handler.query_clarifier = MagicMock()
            handler.conversation_manager = MagicMock()
            handler.query_executor = MagicMock()
            
            return handler

def test_handle_user_message_success(chatbot):
    """Test successful message handling"""
    # Setup mocks
    chatbot.query_clarifier.analyze_query.return_value = {'is_ambiguous': False}
    chatbot.conversation_manager.get_context_string.return_value = "context"
    
    chatbot.query_generator.generate_queries.return_value = {
        'success': True,
        'explanation': 'Explanation',
        'suggested_queries': [{'sql': 'SELECT *', 'explanation': 'Get all'}]
    }
    
    # Execute
    response = chatbot.handle_user_message("Hello")
    
    # Verify
    assert response['success'] == True
    assert response['type'] == 'sql_generated'
    assert len(response['suggested_queries']) == 1
    chatbot.conversation_manager.add_exchange.assert_called_once()

def test_handle_user_message_failure(chatbot):
    """Test failure in query generation"""
    chatbot.query_clarifier.analyze_query.return_value = {'is_ambiguous': False}
    chatbot.query_generator.generate_queries.return_value = {
        'success': False,
        'explanation': 'Failed',
        'error': 'Error'
    }
    
    response = chatbot.handle_user_message("Bad query")
    
    assert response['success'] == False
    assert response['error'] == 'Error'

def test_ambiguous_query_handling(chatbot):
    """Test handling of ambiguous queries"""
    chatbot.query_clarifier.analyze_query.return_value = {
        'is_ambiguous': True, 
        'options': ['Opt1', 'Opt2']
    }
    
    response = chatbot.handle_user_message("Ambiguous")
    
    assert response['success'] == True
    assert response['type'] == 'clarification_needed'
    assert response['clarification_options'] == ['Opt1', 'Opt2']
