
import pytest
from unittest.mock import MagicMock, patch
from chatbot.chatbot_handler import ChatbotHandler

@pytest.fixture
def mock_dependencies():
    """Mock all external dependencies of ChatbotHandler"""
    with patch('chatbot.chatbot_handler.DatabaseConnection') as db_conn, \
         patch('chatbot.chatbot_handler.SchemaManager') as schema_mgr, \
         patch('chatbot.chatbot_handler.QueryExecutor') as query_exec, \
         patch('chatbot.chatbot_handler.LLMFactory') as llm_factory, \
         patch('chatbot.chatbot_handler.QueryGenerator') as query_gen, \
         patch('chatbot.chatbot_handler.QueryClarifier') as query_clar, \
         patch('chatbot.chatbot_handler.ConversationManager') as conv_mgr, \
         patch('chatbot.chatbot_handler.VisualizationHelper') as viz_helper:
        
        mocks = {
            'db_conn': db_conn,
            'schema_mgr': schema_mgr,
            'query_exec': query_exec,
            'llm_factory': llm_factory,
            'query_gen': query_gen,
            'query_clar': query_clar,
            'conv_mgr': conv_mgr,
            'viz_helper': viz_helper
        }
        yield mocks

@pytest.fixture
def chatbot(mock_dependencies):
    """Initialize ChatbotHandler with mocked dependencies"""
    return ChatbotHandler()

def test_init(mock_dependencies):
    """Test initialization of ChatbotHandler"""
    handler = ChatbotHandler()
    assert mock_dependencies['db_conn'].called
    assert mock_dependencies['llm_factory'].create_client.called
    assert mock_dependencies['query_gen'].called
    assert mock_dependencies['conv_mgr'].called

def test_handle_user_message_ambiguous(chatbot, mock_dependencies):
    """Test handling of ambiguous user message"""
    # Setup
    mock_clarifier = mock_dependencies['query_clar'].return_value
    mock_clarifier.analyze_query.return_value = {
        'is_ambiguous': True,
        'options': ['Option A', 'Option B']
    }
    
    # Execute
    response = chatbot.handle_user_message("ambiguous query", user_id="test_user")
    
    # Verify
    assert response['success'] is True
    assert response['type'] == 'clarification_needed'
    assert len(response['clarification_options']) == 2
    mock_dependencies['query_gen'].return_value.generate_queries.assert_not_called()

def test_handle_user_message_success(chatbot, mock_dependencies):
    """Test successful SQL generation"""
    # Setup
    mock_dependencies['query_clar'].return_value.analyze_query.return_value = {'is_ambiguous': False}
    mock_dependencies['conv_mgr'].return_value.get_context_string.return_value = ""
    
    mock_gen = mock_dependencies['query_gen'].return_value
    mock_gen.generate_queries.return_value = {
        'success': True,
        'explanation': 'Valid SQL',
        'suggested_queries': [{'sql': 'SELECT * FROM users'}]
    }
    
    # Execute
    response = chatbot.handle_user_message("show users", user_id="test_user")
    
    # Verify
    assert response['success'] is True
    assert response['type'] == 'sql_generated'
    assert response['query_count'] == 1
    mock_dependencies['conv_mgr'].return_value.add_exchange.assert_called_once()

def test_handle_user_message_failure(chatbot, mock_dependencies):
    """Test failed SQL generation"""
    # Setup
    mock_dependencies['query_clar'].return_value.analyze_query.return_value = {'is_ambiguous': False}
    mock_gen = mock_dependencies['query_gen'].return_value
    mock_gen.generate_queries.return_value = {
        'success': False,
        'error': 'Too complex'
    }
    
    # Execute
    response = chatbot.handle_user_message("complex query", user_id="test_user")
    
    # Verify
    assert response['success'] is False
    assert response['error'] == 'Too complex'

def test_execute_query_valid(chatbot, mock_dependencies):
    """Test valid query execution"""
    # Setup
    mock_conv = mock_dependencies['conv_mgr'].return_value
    mock_conv.get_suggested_queries.return_value = [
        {'sql': 'SELECT * FROM test', 'explanation': 'Test query'}
    ]
    mock_conv.get_history.return_value = [{'user_message': 'test query'}]
    
    mock_exec = mock_dependencies['query_exec'].return_value
    mock_exec.execute.return_value = {
        'success': True,
        'rows': [{'id': 1}],
        'columns': ['id'],
        'row_count': 1,
        'nl_summary': 'Found 1 row'
    }
    mock_exec.format_results_as_table.return_value = {"headers": ["id"], "rows": [[1]]}
    
    mock_dependencies['viz_helper'].analyze_for_visualization.return_value = {'can_visualize': False}

    # Execute
    response = chatbot.execute_query_by_index(0, user_id="test_user")
    
    # Verify
    assert response['success'] is True
    assert response['row_count'] == 1
    assert response['table_formatted'] is not None
    mock_exec.execute.assert_called_once()

def test_execute_query_invalid_index(chatbot, mock_dependencies):
    """Test execution with invalid index"""
    # Setup
    mock_dependencies['conv_mgr'].return_value.get_suggested_queries.return_value = []
    
    # Execute
    response = chatbot.execute_query_by_index(0, user_id="test_user")
    
    # Verify
    assert response['success'] is False
    assert "Invalid query index" in response['error']

def test_execute_query_db_error(chatbot, mock_dependencies):
    """Test execution where DB returns error"""
    # Setup
    mock_conv = mock_dependencies['conv_mgr'].return_value
    mock_conv.get_suggested_queries.return_value = [{'sql': 'SELECT * FROM bad', 'explanation': ''}]
    
    mock_exec = mock_dependencies['query_exec'].return_value
    mock_exec.execute.return_value = {
        'success': False,
        'error': 'Syntax Error'
    }
    
    # Mock LLM response for friendly error
    mock_llm_client = mock_dependencies['llm_factory'].create_client.return_value
    mock_llm_client.get_response.return_value = "Friendly error message"

    # Execute
    response = chatbot.execute_query_by_index(0, user_id="test_user")
    
    # Verify
    assert response['success'] is False
    assert response['error'] == 'Syntax Error'
    assert response['message'] == "Friendly error message"
