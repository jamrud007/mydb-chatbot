"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# ===== Chat Endpoint Models =====

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's question")
    user_id: str = Field(default="default", description="User identifier")


class SuggestedQuery(BaseModel):
    sql: str
    explanation: str


class ClarificationOption(BaseModel):
    """Option for clarifying ambiguous query"""
    interpretation: str
    example_query: str
    chart_type: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    message: str
    type: str = 'sql_generated'  # 'sql_generated' or 'clarification_needed'
    
    # For SQL generation (existing)
    suggested_queries: List[SuggestedQuery] = []
    query_count: int = 0
    error: Optional[str] = None
    
    # For clarification (NEW)
    clarification_options: Optional[List[ClarificationOption]] = None
    original_query: Optional[str] = None


# ===== Execute Endpoint Models =====

class ExecuteResponse(BaseModel):
    success: bool
    result_id: Optional[str] = None
    sql_query: str
    results: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    nl_summary: str
    visualization: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    message: Optional[str] = None
    # 'pending' = analysis running in background
    # 'ready'   = analysis already included in nl_summary (cache hit)
    # 'disabled'= ENABLE_DATA_ANALYSIS=False
    analysis_status: str = 'ready'


# ===== Results Cache Models =====

class QueryResult(BaseModel):
    """Cached query result"""
    id: str
    user_query: str
    sql_query: str
    results: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    nl_summary: str
    visualization: Optional[Dict[str, Any]]
    created_at: str


class QueryResultSummary(BaseModel):
    """Lightweight summary for listing"""
    id: str
    user_query: str
    sql_query: str  # Truncated
    row_count: int
    created_at: str
    has_visualization: bool


class ResultsListResponse(BaseModel):
    """Response for /api/results"""
    success: bool
    results: List[QueryResultSummary]
    count: int
    total: int = 0
    limit: int = 10
    offset: int = 0


# ===== Health Check Model =====

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    database: str
    llm: str
