"""
Flask Web Application for MySQL Chatbot
"""
from flask import Flask, render_template, request, jsonify
import logging
from chatbot.chatbot_handler import ChatbotHandler
from utils.rate_limiter import RateLimiter
from utils.csv_exporter import CSVExporter
from utils.logger import setup_logger
from config import Config
from api.analytics import analytics_bp  # Import blueprint

# Setup logging
setup_logger('chatbot', 'logs/chatbot.log', logging.DEBUG if Config.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # Support for Indonesian characters
app.register_blueprint(analytics_bp) # Register analytics blueprint

# Initialize components
logger.info("Initializing chatbot components...")
chatbot = None
rate_limiter = None

try:
    logger.info("Creating ChatbotHandler instance...")
    chatbot = ChatbotHandler()
    logger.info("ChatbotHandler created successfully")
    
    logger.info("Creating RateLimiter instance...")
    rate_limiter = RateLimiter(
        max_requests=Config.MAX_REQUESTS_PER_MINUTE,
        time_window=60
    )
    logger.info("RateLimiter created successfully")
    
    # Test database connection (non-fatal)
    logger.info("Testing database connection...")
    if chatbot.test_connection():
        logger.info("✓ Database connection successful!")
    else:
        logger.warning("⚠ Database connection failed - chatbot will run with limited functionality")
    
    logger.info("✓✓✓ Chatbot initialized successfully! ✓✓✓")
except Exception as e:
    logger.error(f"❌ Failed to initialize chatbot: {e}")
    import traceback
    logger.error(traceback.format_exc())
    chatbot = None
    rate_limiter = None


@app.route('/')
def index():
    """Render chat interface"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from user
    
    Request JSON:
        {
            "message": "user message",
            "user_id": "optional user id"
        }
    
    Response JSON:
        {
            "success": true/false,
            "message": "bot response",
            "suggested_queries": [...],
            "query_count": number,
            "error": "error message if any"
        }
    """
    logger.info(f"Chat endpoint called. Chatbot object: {chatbot}")
    if not chatbot:
        logger.error("Chatbot is None!")
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized',
            'message': 'Server error. Please contact administrator.'
        }), 500
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        user_id = data.get('user_id', 'default')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Empty message',
                'message': 'Please enter a question.'
            }), 400
        
        # Check rate limit
        allowed, retry_after = rate_limiter.is_allowed(user_id)
        if not allowed:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': f'Terlalu banyak permintaan. Silakan tunggu {int(retry_after)} detik.',
                'retry_after': retry_after
            }), 429
        
        # Process message
        logger.info(f"Processing chat message from {user_id}")
        response = chatbot.handle_user_message(user_message, user_id)
        
        return jsonify(response)
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Terjadi kesalahan. Silakan coba lagi.'
        }), 500


@app.route('/api/execute/<int:query_index>', methods=['POST'])
def execute_query(query_index):
    """
    Execute a suggested query by index
    
    Args:
        query_index: Index of suggested query (0-based)
    
    Request JSON:
        {
            "user_id": "optional user id"
        }
    
    Response JSON:
        {
            "success": true/false,
            "sql_query": "executed query",
            "results": [...],
            "columns": [...],
            "row_count": number,
            "table_formatted": "ascii table",
            "nl_summary": "natural language summary",
            "error": "error if any"
        }
    """
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'default')
        
        # Check rate limit
        allowed, retry_after = rate_limiter.is_allowed(user_id)
        if not allowed:
            return jsonify({
                'success': False,
                'error': 'Rate limit exceeded',
                'message': f'Terlalu banyak permintaan. Silakan tunggu {int(retry_after)} detik.',
                'retry_after': retry_after
            }), 429
        
        # Execute query
        logger.info(f"Executing query #{query_index} for {user_id}")
        result = chatbot.execute_query_by_index(query_index, user_id)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in execute endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Terjadi kesalahan saat menjalankan query.'
        }), 500


@app.route('/api/schema', methods=['GET'])
def get_schema():
    """
    Get database schema
    
    Response JSON:
        {
            "success": true/false,
            "schema": {...},
            "error": "error if any"
        }
    """
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        result = chatbot.get_schema_info()
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error in schema endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    
    Response JSON:
        {
            "status": "healthy/unhealthy",
            "database": "connected/disconnected",
            "chatbot": "initialized/not_initialized",
            "ai_provider": "ollama/gemini/etc",
            "provider_status": "connected/disconnected"
        }
    """
    db_status = "disconnected"
    chatbot_status = "not_initialized"
    ai_provider = "unknown"
    provider_status = "disconnected"
    
    if chatbot:
        chatbot_status = "initialized"
        try:
            ai_provider = chatbot.llm_client.provider_name
            provider_status = "connected" if chatbot.llm_client.test_connection() else "disconnected"
        except:
            pass
        
        if chatbot.test_connection():
            db_status = "connected"
    
    overall_status = "healthy" if (db_status == "connected" and chatbot_status == "initialized" and provider_status == "connected") else "unhealthy"
    
    return jsonify({
        'status': overall_status,
        'database': db_status,
        'chatbot': chatbot_status,
        'ai_provider': ai_provider,
        'provider_status': provider_status
    })


@app.route('/api/provider', methods=['GET'])
def get_provider_info():
    """
    Get current AI provider information
    
    Response JSON:
        {
            "provider": "provider_name",
            "model": "model_name",
            "status": "connected/disconnected"
        }
    """
    if not chatbot:
        return jsonify({
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        provider_info = chatbot.llm_client.get_provider_info()
        provider_info['model'] = getattr(chatbot.llm_client, 'model_name', getattr(chatbot.llm_client, 'model', 'unknown'))
        return jsonify(provider_info)
    except Exception as e:
        logger.error(f"Error getting provider info: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/export/csv/<int:query_index>', methods=['GET'])
def export_csv(query_index):
    """
    Export query results as CSV file
    
    Args:
        query_index: Index of the executed query
    
    Query Params:
        user_id: User identifier (optional, default='default')
    
    Response:
        CSV file download
    """
    if not chatbot:
        return jsonify({
            'success': False,
            'error': 'Chatbot not initialized'
        }), 500
    
    try:
        user_id = request.args.get('user_id', 'default')
        
        # Get suggested queries from conversation manager
        suggested_queries = chatbot.conversation_manager.get_suggested_queries(user_id)
        
        if query_index < 0 or query_index >= len(suggested_queries):
            return jsonify({
                'success': False,
                'error': f'Invalid query index: {query_index}'
            }), 400
        
        sql_query = suggested_queries[query_index]
        
        # Extract SQL string if it's a dict
        if isinstance(sql_query, dict):
            sql_query = sql_query.get('sql', sql_query.get('query', ''))
        
        if not sql_query:
            return jsonify({
                'success': False,
                'error': 'Query not found'
            }), 400
        
        # Execute query to get results
        exec_result = chatbot.query_executor.execute(sql_query)
        
        if not exec_result['success']:
            return jsonify({
                'success': False,
                'error': exec_result.get('error', 'Failed to execute query')
            }), 400
        
        # Generate filename from SQL query
        sql_words = sql_query.split()[:5]
        filename = '_'.join(sql_words) + '.csv'
        filename = filename.replace('SELECT', 'export').replace('*', 'all')
        filename = ''.join(c for c in filename if c.isalnum() or c in ('_', '-', '.'))
        
        # Generate CSV response
        return CSVExporter.generate_csv_response(
            exec_result['rows'],
            exec_result['columns'],
            filename=filename
        )
    
    except Exception as e:
        logger.error(f"Error in export CSV endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Starting Flask app on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
