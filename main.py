"""
FastAPI Application for MyDB Chatbot
Migrated from Flask for better performance and auto API docs
"""
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import logging
from datetime import datetime
from chatbot.chatbot_handler import ChatbotHandler
from services.chat_service import ChatService
from utils.rate_limiter import RateLimiter
from utils.metrics import get_metrics_collector
from utils.history_exporter import HistoryExporter
from utils.daily_reporter import get_daily_reporter
from utils.csv_exporter import CSVExporter
from utils.results_cache import ResultsCache
from utils.logger import setup_logger
from core.middleware import RequestIDMiddleware
from config import Config
from models.api_models import (
    ChatRequest, ChatResponse, ExecuteResponse,
    QueryResult, ResultsListResponse, HealthResponse,
    SuggestedQuery
)

# Authentication imports
from database.user_manager import UserManager
from database.db_connection import DatabaseConnection
from api.auth import router as auth_router, set_user_manager, get_current_user

# Task queue
from task_queue.background_task_queue import BackgroundTaskQueue

# Setup logging
setup_logger('chatbot', 'logs/chatbot.log', logging.DEBUG if Config.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MyDB Chatbot API",
    description="Text-to-SQL chatbot with visualization capabilities",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request ID middleware (added after CORS so it runs outermost — assigns
# request_id before any other processing, available to all logs via contextvar)
app.add_middleware(RequestIDMiddleware)

# Initialize components
logger.info("Initializing chatbot components...")
chatbot = None
chat_service = None
rate_limiter = None
results_cache = None
user_manager = None
metrics_collector = None
history_exporter = None

try:
    logger.info("Creating ChatbotHandler instance...")
    chatbot = ChatbotHandler()
    logger.info("ChatbotHandler created successfully")
    chat_service = ChatService(chatbot)
    logger.info("ChatService created successfully")
    
    logger.info("Creating RateLimiter instance...")
    rate_limiter = RateLimiter(
        max_requests=Config.MAX_REQUESTS_PER_MINUTE,
        time_window=Config.RATE_LIMIT_TIME_WINDOW,
    )
    logger.info("RateLimiter created successfully")

    logger.info("Creating ResultsCache instance...")
    results_cache = ResultsCache(ttl_seconds=Config.RESULTS_CACHE_TTL)
    logger.info("ResultsCache created successfully")

    # Initialize MetricsCollector
    logger.info("Creating MetricsCollector instance...")
    metrics_collector = get_metrics_collector(window_minutes=Config.METRICS_WINDOW_MINUTES)
    logger.info("MetricsCollector created successfully")
    
    # Initialize UserManager for authentication
    logger.info("Creating UserManager instance...")
    db_config = Config.get_db_config()
    db_conn = DatabaseConnection(db_config)
    user_manager = UserManager(db_conn)
    set_user_manager(user_manager)  # Set for auth router
    logger.info("UserManager created successfully")
    
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
    chat_service = None
    rate_limiter = None
    results_cache = None
    user_manager = None

# Include authentication router
app.include_router(auth_router)

# Global exception handler
@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(f"Request: {request.method} {request.url}")
    import traceback
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if Config.DEBUG else "An unexpected error occurred"
        }
    )


# ===== Helper Functions =====

def check_initialization():
    """Check if chatbot is initialized"""
    if not chatbot or not chat_service or not rate_limiter or not results_cache:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized. Please contact administrator."
        )

def check_rate_limit(user_id: str):
    """Check rate limit for user"""
    allowed, retry_after = rate_limiter.is_allowed(user_id)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Terlalu banyak permintaan. Silakan tunggu {int(retry_after)} detik.",
            headers={"Retry-After": str(int(retry_after))}
        )


# ===== API Endpoints =====

@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API info"""
    return {
        "name": "MyDB Chatbot API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/api/health"
    }

@app.get("/api/metrics", tags=["Monitoring"])
def get_metrics():
    """
    Get performance metrics
    
    Returns:
        dict: All metrics including query performance, errors, cache, usage, and LLM stats
    """
    if not metrics_collector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics collector not initialized"
        )
    
    return metrics_collector.get_all_metrics()

@app.get("/api/metrics/summary", tags=["Monitoring"])
def get_metrics_summary():
    """
    Get a condensed, human-readable metrics summary

    Lightweight version of /api/metrics for quick debugging and status
    widgets (overall status, uptime, error rate, LLM/query latency, cache
    hit rate) without parsing the full metrics payload.

    Returns:
        dict: status + condensed request/query/llm/cache stats
    """
    if not metrics_collector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Metrics collector not initialized"
        )

    return metrics_collector.get_summary()

@app.get("/api/history/export/stats", tags=["History"])
def get_export_stats(current_user: dict = Depends(get_current_user)):
    """
    Get statistics about exportable history data
    
    Returns:
        dict: Export statistics including total conversations and cached queries
    """
    user_id = str(current_user['user_id'])
    
    if not chatbot or not chatbot.conversation_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    # Create temporary exporter if not global
    exporter = HistoryExporter(chatbot.conversation_manager, chatbot.query_executor.cache_manager if chatbot.query_executor else None)
    
    return exporter.get_export_stats(user_id)

@app.get("/api/history/export/json", tags=["History"])
def export_history_json(current_user: dict = Depends(get_current_user)):
    """
    Export conversation history as JSON
    
    Returns:
        JSONResponse: Complete conversation history
    """
    user_id = str(current_user['user_id'])
    
    if not chatbot or not chatbot.conversation_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    exporter = HistoryExporter(chatbot.conversation_manager, chatbot.query_executor.cache_manager if chatbot.query_executor else None)
    json_export = exporter.export_full_history_json(user_id)
    
    return JSONResponse(
        content=json.loads(json_export),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=history_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"}
    )

@app.get("/api/history/export/csv", tags=["History"])
def export_history_csv(current_user: dict = Depends(get_current_user)):
    """
    Export conversation history as CSV
    
    Returns:
        Response: CSV file download
    """
    user_id = str(current_user['user_id'])
    
    if not chatbot or not chatbot.conversation_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from fastapi.responses import Response
    
    exporter = HistoryExporter(chatbot.conversation_manager)
    csv_export = exporter.export_conversation_csv(user_id)
    
    return Response(
        content=csv_export,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=history_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"}
    )

@app.get("/api/history/export/text", tags=["History"])
def export_history_text(current_user: dict = Depends(get_current_user)):
    """
    Export conversation history as formatted text
    
    Returns:
        Response: Text file download
    """
    user_id = str(current_user['user_id'])
    
    if not chatbot or not chatbot.conversation_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from fastapi.responses import Response
    
    exporter = HistoryExporter(chatbot.conversation_manager)
    text_export = exporter.export_conversation_text(user_id)
    
    return Response(
        content=text_export,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=history_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"}
    )

@app.get("/api/suggestions", tags=["Query"])
def get_query_suggestions(
    q: str = '',
    lang: str = 'id',
    limit: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user)
):
    """
    Get query suggestions/autocomplete
    
    Args:
        q: Partial query input (empty for general suggestions)
        lang: Language code (id, en)
        limit: Maximum suggestions to return
    
    Returns:
        dict: Suggestions list with types and scores
    """
    user_id = str(current_user['user_id'])
    
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from utils.query_suggestions import QuerySuggestionEngine
    
    # Create suggestion engine
    engine = QuerySuggestionEngine(
        chatbot.schema_manager,
        chatbot.conversation_manager
    )
    
    # Get suggestions
    suggestions = engine.get_suggestions(q, user_id, lang, limit)
    
    return {
        'query': q,
        'language': lang,
        'total': len(suggestions),
        'suggestions': suggestions
    }

@app.get("/api/schema/docs/markdown", tags=["Schema"])
def get_schema_docs_markdown(
    include_stats: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Get schema documentation in Markdown format
    
    Args:
        include_stats: Include table row counts
    
    Returns:
        Response: Markdown documentation
    """
    if not chatbot or not chatbot.schema_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from utils.schema_docs import SchemaDocGenerator
    from fastapi.responses import Response
    
    generator = SchemaDocGenerator(
        chatbot.schema_manager,
        chatbot.db_connection if hasattr(chatbot, 'db_connection') else None
    )
    
    markdown = generator.generate_markdown(include_stats)
    
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=schema_docs_{datetime.now().strftime('%Y%m%d')}.md"}
    )

@app.get("/api/schema/docs/html", tags=["Schema"])
def get_schema_docs_html(
    include_stats: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Get schema documentation in HTML format
    
    Args:
        include_stats: Include table row counts
    
    Returns:
        HTMLResponse: HTML documentation
    """
    if not chatbot or not chatbot.schema_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from utils.schema_docs import SchemaDocGenerator
    from fastapi.responses import HTMLResponse
    
    generator = SchemaDocGenerator(
        chatbot.schema_manager,
        chatbot.db_connection if hasattr(chatbot, 'db_connection') else None
    )
    
    html = generator.generate_html(include_stats)
    
    return HTMLResponse(content=html)

@app.get("/api/schema/docs/json", tags=["Schema"])
def get_schema_docs_json(
    include_stats: bool = False,
    current_user: dict = Depends(get_current_user)
):
    """
    Get schema documentation in JSON format
    
    Args:
        include_stats: Include table row counts
    
    Returns:
        JSONResponse: JSON documentation
    """
    if not chatbot or not chatbot.schema_manager:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot not initialized"
        )
    
    from utils.schema_docs import SchemaDocGenerator
    
    generator = SchemaDocGenerator(
        chatbot.schema_manager,
        chatbot.db_connection if hasattr(chatbot, 'db_connection') else None
    )
    
    json_docs = generator.generate_json(include_stats)
    
    return JSONResponse(content=json.loads(json_docs))

@app.post("/api/admin/daily-report", status_code=status.HTTP_202_ACCEPTED, tags=["Admin"])
def generate_daily_report(
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Trigger daily report generation (runs in background, returns 202 immediately).
    """
    tq = BackgroundTaskQueue(background_tasks)
    tq.enqueue(_background_daily_report)
    return {"status": "accepted", "message": "Daily report generation started in background"}


def _background_daily_report():
    """Background task: generate and persist daily report files."""
    try:
        reporter = get_daily_reporter()
        report_path = reporter.generate_daily_report()
        metrics_path = reporter.save_daily_metrics()
        logger.info(f"Background: daily report saved — {report_path}, {metrics_path}")
    except Exception as e:
        logger.error(f"Background: daily report failed: {e}")


@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """
    Handle chat messages from user (Protected - requires JWT token)
    
    Generates SQL queries based on natural language input
    """
    check_initialization()
    # Use authenticated user_id instead of request.user_id
    user_id = str(current_user['user_id'])
    logger.info(f"Chat endpoint called for user: {user_id}")
    
    try:
        # Check rate limit
        check_rate_limit(user_id)
        
        # Process message
        logger.info(f"Processing chat message from {user_id}")
        response_dict = chat_service.generate_queries(request.message, user_id)
        
        # Handle clarification response (NEW)
        if response_dict.get('type') == 'clarification_needed':
            from models.api_models import ClarificationOption
            return ChatResponse(
                success=True,
                type='clarification_needed',
                message=response_dict.get('message', ''),
                clarification_options=[
                    ClarificationOption(**opt) 
                    for opt in response_dict.get('clarification_options', [])
                ],
                original_query=response_dict.get('original_query')
            )
        
        # Normal SQL generation response
        return ChatResponse(
            success=response_dict['success'],
            type='sql_generated',
            message=response_dict.get('message', ''),
            suggested_queries=[
                SuggestedQuery(sql=q['sql'], explanation=q['explanation'])
                for q in response_dict.get('suggested_queries', [])
            ],
            query_count=response_dict.get('query_count', 0),
            error=response_dict.get('error')
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan: {str(e)}"
        )


@app.post("/api/execute/{query_index}", response_model=ExecuteResponse, tags=["Execution"])
def execute_query(
    query_index: int,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
):
    """
    Execute a suggested query by index (Protected - requires JWT token).

    Returns DB results immediately. If ENABLE_DATA_ANALYSIS is True,
    the LLM analysis is fired as a background task (analysis_status='pending').
    Poll GET /api/results/{result_id}/analysis to retrieve it when ready.
    """
    user_id = str(current_user['user_id'])
    check_initialization()

    try:
        check_rate_limit(user_id)

        logger.info(f"Executing query #{query_index} for {user_id}")
        result_dict = chat_service.execute_suggested_query(query_index, user_id)

        if not result_dict['success']:
            return ExecuteResponse(
                success=False,
                sql_query=result_dict.get('sql_query', ''),
                results=[],
                columns=[],
                row_count=0,
                nl_summary='',
                error=result_dict.get('error'),
                message=result_dict.get('message'),
            )

        handler = chat_service.get_handler()
        history = handler.conversation_manager.get_history(user_id, num_exchanges=1)
        user_question = history[0]['user_message'] if history else ''

        # Determine analysis status before storing
        has_cached_analysis = "🤖 **Analisis Otomatis:**" in result_dict['nl_summary']
        run_bg_analysis = (
            Config.ENABLE_DATA_ANALYSIS
            and result_dict['row_count'] > 0
            and not has_cached_analysis
        )
        analysis_status = 'pending' if run_bg_analysis else ('ready' if has_cached_analysis else 'disabled')

        result_id = results_cache.store(
            sql_query=result_dict['sql_query'],
            results=result_dict['results'],
            columns=result_dict['columns'],
            row_count=result_dict['row_count'],
            nl_summary=result_dict['nl_summary'],
            visualization=result_dict.get('visualization'),
            user_query=user_question,
        )
        # Patch the stored entry's analysis_status
        if result_id in results_cache.cache:
            results_cache.cache[result_id]['analysis_status'] = analysis_status

        logger.info(f"Stored result {result_id}, analysis_status={analysis_status}")

        if run_bg_analysis:
            cache_query = handler.query_executor.get_cache_query(result_dict['sql_query'])
            tq = BackgroundTaskQueue(background_tasks)
            tq.enqueue(
                _background_analysis,
                handler,
                cache_query,
                user_question,
                result_dict['columns'],
                result_dict['results'],
                result_id,
            )

        return ExecuteResponse(
            success=True,
            result_id=result_id,
            sql_query=result_dict['sql_query'],
            results=result_dict['results'],
            columns=result_dict['columns'],
            row_count=result_dict['row_count'],
            nl_summary=result_dict['nl_summary'],
            visualization=result_dict.get('visualization'),
            analysis_status=analysis_status,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in execute endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Terjadi kesalahan saat menjalankan query: {str(e)}",
        )


def _background_analysis(handler, cache_query, question, columns, rows, result_id):
    """Background task: run LLM analysis and update both caches."""
    analysis_text = handler.generate_analysis(cache_query, question, columns, rows)
    status = 'ready' if analysis_text else 'failed'
    results_cache.update_analysis(result_id, analysis_text, status)


@app.get("/api/results/{result_id}/analysis", tags=["Execution"])
def get_analysis(result_id: str, current_user: dict = Depends(get_current_user)):
    """
    Poll for background analysis status for a given result_id.

    Returns:
        {status: 'pending'|'ready'|'failed'|'disabled', analysis: str}
    """
    entry = results_cache.get(result_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Result not found or expired")
    analysis_status = entry.get('analysis_status', 'ready')
    # Extract only the analysis portion from nl_summary if present
    nl = entry.get('nl_summary', '')
    marker = "🤖 **Analisis Otomatis:**"
    analysis_text = nl.split(marker, 1)[1].strip() if marker in nl else ''
    return {
        "result_id": result_id,
        "analysis_status": analysis_status,
        "analysis": analysis_text,
    }


@app.get("/api/results", response_model=ResultsListResponse, tags=["Results Cache"])
def list_results(
    limit: int = Query(10, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
):
    """
    List recent query results for current user (Protected - requires JWT token)

    Args:
        limit: Max results to return (1–200, default 10)
        offset: Number of entries to skip (for pagination)
        current_user: Authenticated user from JWT token
    """
    check_initialization()

    try:
        total_count = results_cache.total()
        recent = results_cache.list_recent(limit=limit, offset=offset)
        return ResultsListResponse(
            success=True,
            results=recent,
            count=len(recent),
            total=total_count,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(f"Error listing results: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/results/{result_id}", response_model=QueryResult, tags=["Results Cache"])
def get_result(result_id: str):
    """
    Get specific query result by ID (for Streamlit)
    
    Args:
        result_id: Unique result identifier
    
    Returns:
        Full query result with data and visualization config
    """
    check_initialization()
    
    try:
        result = results_cache.get(result_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Result not found or expired: {result_id}"
            )
        
        return QueryResult(**result)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting result: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/export/csv/{query_index}", tags=["Export"])
def export_csv(query_index: int, user_id: str = "default"):
    """
    Export query results as CSV file
    
    Args:
        query_index: Index of the executed query
        user_id: User identifier
    
    Returns:
        CSV file download
    """
    check_initialization()
    
    try:
        # Get suggested queries from conversation manager
        suggested_queries = chatbot.conversation_manager.get_suggested_queries(user_id)
        
        if query_index < 0 or query_index >= len(suggested_queries):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid query index: {query_index}'
            )
        
        sql_query = suggested_queries[query_index]
        
        # Extract SQL string if it's a dict
        if isinstance(sql_query, dict):
            sql_query = sql_query.get('sql', sql_query.get('query', ''))
        
        if not sql_query:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Query not found'
            )
        
        # Execute query to get results
        exec_result = chatbot.query_executor.execute(sql_query, use_cache=True, user_id=user_id)
        
        if not exec_result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=exec_result.get('error', 'Failed to execute query')
            )
        
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
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in export CSV endpoint: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Health check endpoint (optimized - no slow test requests)
    
    Returns system status based on component initialization
    """
    db_status = "disconnected"
    llm_status = "disconnected"
    
    if chatbot:
        # LLM is connected if client exists (skip slow test_connection)
        if hasattr(chatbot, 'llm_client') and chatbot.llm_client:
            llm_status = "connected"
        
        # Database is connected if connection exists (skip slow test)
        if hasattr(chatbot, 'db_connection') and chatbot.db_connection:
            db_status = "connected"
    
    overall_status = "healthy" if (db_status == "connected" and llm_status == "connected") else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now().isoformat(),
        database=db_status,
        llm=llm_status
    )


@app.get("/api/cache/stats", tags=["Cache"])
def get_cache_stats():
    """
    Get query cache statistics
    
    Returns cache hit rate, total entries, size, and backend info
    """
    check_initialization()
    
    try:
        if not chatbot.query_executor.cache_manager:
            return {
                'enabled': False,
                'backend': 'none',
                'message': 'Cache is disabled'
            }
        
        stats = chatbot.query_executor.cache_manager.get_stats()
        return stats
    
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/cache/clear", tags=["Cache"])
def clear_cache(user_id: str = None):
    """
    Clear query cache
    
    Args:
        user_id: Optional - Clear only this user's cache. If None, clears all cache.
    
    Returns:
        Number of entries deleted
    """
    check_initialization()
    
    try:
        if not chatbot.query_executor.cache_manager:
            return {
                'success': False,
                'message': 'Cache is disabled'
            }
        
        if user_id:
            deleted_count = chatbot.query_executor.cache_manager.clear_user_cache(user_id)
            message = f"Cleared {deleted_count} cache entries for user {user_id}"
        else:
            success = chatbot.query_executor.cache_manager.clear_all()
            deleted_count = -1  # Unknown for clear_all
            message = "All cache entries cleared" if success else "Failed to clear cache"
        
        return {
            'success': True,
            'deleted_count': deleted_count,
            'message': message
        }
    
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.get("/api/cache/entries", tags=["Cache"])
def list_cache_entries(user_id: str = None, limit: int = Query(50, ge=1, le=500)):
    """
    List cached query entries
    
    Args:
        user_id: Optional - Filter by user
        limit: Maximum number of entries to return (default: 50)
    
    Returns:
        List of cached query metadata
    """
    check_initialization()
    
    try:
        if not chatbot.query_executor.cache_manager:
            return {
                'success': False,
                'entries': [],
                'message': 'Cache is disabled'
            }
        
        entries = chatbot.query_executor.cache_manager.list_entries(user_id, limit)
        
        return {
            'success': True,
            'entries': entries,
            'count': len(entries)
        }
    
    except Exception as e:
        logger.error(f"Error listing cache entries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )



@app.get("/api/cache/entry/{cache_key}", tags=["Cache"])
def get_cache_entry(cache_key: str):
    """
    Get full cached result by key
    """
    check_initialization()
    
    try:
        if not chatbot.query_executor.cache_manager:
            raise HTTPException(status_code=404, detail="Cache disabled")
            
        # Access cache directly to get full entry
        cache_data = chatbot.query_executor.cache_manager.cache.get(cache_key)
        
        if not cache_data:
            raise HTTPException(status_code=404, detail="Cache entry not found")
            
        return {
            'success': True,
            'data': cache_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving cache entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Feedback Endpoint =====

class FeedbackRequest(BaseModel):
    """Feedback request model"""
    result_id: str
    rating: int  # 1 for thumbs up, -1 for thumbs down
    comment: str = None


@app.post("/api/feedback", tags=["Feedback"])
def submit_feedback(
    feedback: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit user feedback on query results (Protected - requires JWT token)
    
    Args:
        feedback: Feedback data (result_id, rating, optional comment)
        current_user: Authenticated user from JWT token
    
    Returns:
        Success confirmation
    """
    check_initialization()
    
    try:
        user_id = str(current_user['user_id'])
        username = current_user['username']
        
        # Log feedback
        logger.info(f"Feedback received from {username} (ID: {user_id})")
        logger.info(f"Result ID: {feedback.result_id}, Rating: {feedback.rating}")
        if feedback.comment:
            logger.info(f"Comment: {feedback.comment}")
        
        # TODO: Store feedback in database for analytics
        # For now, just log it
        
        return {
            "success": True,
            "message": "Thank you for your feedback!",
            "user_id": user_id
        }
    
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ===== Run with uvicorn =====
if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting FastAPI app on {Config.HOST}:{Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Swagger UI available at: http://{Config.HOST}:{Config.PORT}/docs")
    
    uvicorn.run(
        "main:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )
