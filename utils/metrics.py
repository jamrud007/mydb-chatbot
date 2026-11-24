"""
Metrics Collection for Performance Monitoring
Tracks query performance, error rates, and usage patterns
"""
import time
import threading
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import statistics


def _format_uptime(seconds: int) -> str:
    """Format a duration in seconds as a human-readable string (e.g. '2h 5m 3s')"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if not parts or secs:
        parts.append(f"{secs}s")
    return " ".join(parts)


class MetricsCollector:
    """
    Thread-safe metrics collector for monitoring application performance
    
    Tracks:
    - Query execution times (avg, p50, p95, p99)
    - Error rates by type
    - Request counts per user
    - Cache hit rates
    - Slow query detection
    """
    
    def __init__(self, window_minutes: int = 60):
        """
        Initialize metrics collector
        
        Args:
            window_minutes: Time window for metrics (default: 60 minutes)
        """
        self.window_minutes = window_minutes
        self.window_seconds = window_minutes * 60
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Query performance metrics
        self.query_durations: deque = deque(maxlen=10000)  # (timestamp, duration_ms)
        self.slow_queries: List[Dict] = []  # Queries > 5s
        
        # Error tracking
        self.errors: defaultdict = defaultdict(int)  # {error_type: count}
        self.error_history: deque = deque(maxlen=1000)  # (timestamp, error_type)
        
        # Usage tracking
        self.user_requests: defaultdict = defaultdict(int)  # {user_id: count}
        self.hourly_requests: defaultdict = defaultdict(int)  # {hour: count}
        
        # Cache metrics
        self.cache_hits = 0
        self.cache_misses = 0
        
        # LLM metrics
        self.llm_calls = 0
        self.llm_failures = 0
        self.llm_durations: deque = deque(maxlen=1000)
        
        # Start time
        self.start_time = time.time()
    
    def record_query_duration(self, duration_ms: float, user_id: str = 'unknown', 
                             query: str = '', from_cache: bool = False):
        """
        Record query execution duration
        
        Args:
            duration_ms: Query duration in milliseconds
            user_id: User identifier
            query: SQL query (optional)
            from_cache: Whether result was from cache
        """
        with self.lock:
            timestamp = time.time()
            
            # Record duration
            self.query_durations.append((timestamp, duration_ms))
            
            # Track slow queries (> 5 seconds)
            if duration_ms > 5000 and not from_cache:
                self.slow_queries.append({
                    'timestamp': datetime.fromtimestamp(timestamp).isoformat(),
                    'duration_ms': duration_ms,
                    'user_id': user_id,
                    'query': query[:200]  # Truncate for storage
                })
                # Keep only last 100 slow queries
                if len(self.slow_queries) > 100:
                    self.slow_queries.pop(0)
            
            # Update cache metrics
            if from_cache:
                self.cache_hits += 1
            else:
                self.cache_misses += 1
            
            # Track user requests
            self.user_requests[user_id] += 1
            
            # Track hourly distribution
            hour = datetime.fromtimestamp(timestamp).hour
            self.hourly_requests[hour] += 1
    
    def record_error(self, error_type: str, user_id: str = 'unknown'):
        """
        Record an error occurrence
        
        Args:
            error_type: Type of error (e.g., 'SQL_EXECUTION_ERROR')
            user_id: User identifier
        """
        with self.lock:
            timestamp = time.time()
            self.errors[error_type] += 1
            self.error_history.append((timestamp, error_type))
    
    def record_llm_call(self, duration_ms: float, success: bool = True):
        """
        Record LLM API call
        
        Args:
            duration_ms: Call duration in milliseconds
            success: Whether call succeeded
        """
        with self.lock:
            self.llm_calls += 1
            if success:
                self.llm_durations.append(duration_ms)
            else:
                self.llm_failures += 1
    
    def _get_recent_durations(self) -> List[float]:
        """Get query durations within the time window"""
        with self.lock:
            cutoff = time.time() - self.window_seconds
            return [dur for ts, dur in self.query_durations if ts > cutoff]
    
    def get_query_stats(self) -> Dict:
        """
        Get query performance statistics
        
        Returns:
            dict: Query performance metrics
        """
        durations = self._get_recent_durations()
        
        if not durations:
            return {
                'total_queries': 0,
                'avg_duration_ms': 0,
                'median_duration_ms': 0,
                'p95_duration_ms': 0,
                'p99_duration_ms': 0,
                'min_duration_ms': 0,
                'max_duration_ms': 0,
                'slow_query_count': 0
            }
        
        sorted_durations = sorted(durations)
        count = len(sorted_durations)
        
        cutoff = time.time() - self.window_seconds
        slow_in_window = sum(
            1 for sq in self.slow_queries
            if sq.get('timestamp', '') >= datetime.fromtimestamp(cutoff).isoformat()
        )
        return {
            'total_queries': count,
            'avg_duration_ms': round(statistics.mean(sorted_durations), 2),
            'median_duration_ms': round(statistics.median(sorted_durations), 2),
            'p95_duration_ms': round(sorted_durations[int(count * 0.95)] if count > 0 else 0, 2),
            'p99_duration_ms': round(sorted_durations[int(count * 0.99)] if count > 0 else 0, 2),
            'min_duration_ms': round(min(sorted_durations), 2),
            'max_duration_ms': round(max(sorted_durations), 2),
            'slow_query_count': slow_in_window,
            'slow_query_count_all_time': len(self.slow_queries),
        }
    
    def get_error_stats(self) -> Dict:
        """
        Get error statistics
        
        Returns:
            dict: Error metrics
        """
        with self.lock:
            # Count recent errors (within window)
            cutoff = time.time() - self.window_seconds
            recent_errors = defaultdict(int)
            for ts, error_type in self.error_history:
                if ts > cutoff:
                    recent_errors[error_type] += 1
            
            total_errors = sum(recent_errors.values())
            
            return {
                'total_errors': total_errors,
                'errors_by_type': dict(recent_errors),
                'all_time_errors': dict(self.errors)
            }
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache performance statistics
        
        Returns:
            dict: Cache metrics
        """
        with self.lock:
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'total_requests': total_requests,
                'hit_rate_percent': round(hit_rate, 2)
            }
    
    def get_usage_stats(self) -> Dict:
        """
        Get usage statistics
        
        Returns:
            dict: Usage metrics
        """
        with self.lock:
            # Top users by request count
            top_users = sorted(
                self.user_requests.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Peak hours
            peak_hours = sorted(
                self.hourly_requests.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                'total_users': len(self.user_requests),
                'total_requests': sum(self.user_requests.values()),
                'top_users': [{'user_id': uid, 'requests': count} for uid, count in top_users],
                'peak_hours': [{'hour': hour, 'requests': count} for hour, count in peak_hours]
            }
    
    def get_llm_stats(self) -> Dict:
        """
        Get LLM performance statistics
        
        Returns:
            dict: LLM metrics
        """
        with self.lock:
            success_rate = ((self.llm_calls - self.llm_failures) / self.llm_calls * 100) if self.llm_calls > 0 else 0
            avg_duration = statistics.mean(self.llm_durations) if self.llm_durations else 0
            
            return {
                'total_calls': self.llm_calls,
                'failures': self.llm_failures,
                'success_rate_percent': round(success_rate, 2),
                'avg_duration_ms': round(avg_duration, 2)
            }
    
    def get_all_metrics(self) -> Dict:
        """
        Get all metrics in one call
        
        Returns:
            dict: All metrics
        """
        uptime_seconds = int(time.time() - self.start_time)
        
        return {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'uptime_seconds': uptime_seconds,
            'window_minutes': self.window_minutes,
            'query_performance': self.get_query_stats(),
            'errors': self.get_error_stats(),
            'cache': self.get_cache_stats(),
            'usage': self.get_usage_stats(),
            'llm': self.get_llm_stats(),
            'slow_queries': self.slow_queries[-10:]  # Last 10 slow queries
        }

    def get_summary(self) -> Dict:
        """
        Get a condensed, human-readable summary for quick debugging/dashboards.

        Unlike get_all_metrics(), this collapses each section down to the few
        numbers that matter for an at-a-glance health check (status, uptime,
        error rate, LLM/query latency, cache hit rate).

        Returns:
            dict: status + condensed request/query/llm/cache stats
        """
        query_stats = self.get_query_stats()
        error_stats = self.get_error_stats()
        cache_stats = self.get_cache_stats()
        llm_stats = self.get_llm_stats()

        total_requests = query_stats['total_queries']
        total_errors = error_stats['total_errors']
        denom = total_requests + total_errors
        error_rate_percent = round((total_errors / denom * 100) if denom > 0 else 0, 2)

        status = 'ok'
        if total_errors > 0 and error_rate_percent >= 20:
            status = 'critical'
        elif error_rate_percent >= 5 or (llm_stats['total_calls'] > 0 and llm_stats['success_rate_percent'] < 90):
            status = 'degraded'

        uptime_seconds = int(time.time() - self.start_time)

        return {
            'status': status,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'uptime_seconds': uptime_seconds,
            'uptime_human': _format_uptime(uptime_seconds),
            'window_minutes': self.window_minutes,
            'requests': {
                'total': total_requests,
                'errors': total_errors,
                'error_rate_percent': error_rate_percent,
            },
            'query': {
                'avg_duration_ms': query_stats['avg_duration_ms'],
                'p95_duration_ms': query_stats['p95_duration_ms'],
                'slow_query_count': query_stats['slow_query_count'],
            },
            'llm': {
                'total_calls': llm_stats['total_calls'],
                'success_rate_percent': llm_stats['success_rate_percent'],
                'avg_duration_ms': llm_stats['avg_duration_ms'],
            },
            'cache': {
                'hit_rate_percent': cache_stats['hit_rate_percent'],
            },
            'top_errors': dict(
                sorted(error_stats['errors_by_type'].items(), key=lambda kv: kv[1], reverse=True)[:5]
            ),
        }

    def reset(self):
        """Reset all metrics (admin function)"""
        with self.lock:
            self.query_durations.clear()
            self.slow_queries.clear()
            self.errors.clear()
            self.error_history.clear()
            self.user_requests.clear()
            self.hourly_requests.clear()
            self.cache_hits = 0
            self.cache_misses = 0
            self.llm_calls = 0
            self.llm_failures = 0
            self.llm_durations.clear()
            self.start_time = time.time()


# ============================================================================
# GLOBAL METRICS INSTANCE (Singleton pattern)
# ============================================================================

_metrics_instance: Optional[MetricsCollector] = None
_metrics_lock = threading.Lock()

def get_metrics_collector(window_minutes: int = 60) -> MetricsCollector:
    """
    Get or create the global metrics collector instance
    
    Args:
        window_minutes: Time window for metrics (only used on first call)
    
    Returns:
        MetricsCollector instance
    """
    global _metrics_instance
    
    if _metrics_instance is None:
        with _metrics_lock:
            if _metrics_instance is None:  # Double-check locking
                _metrics_instance = MetricsCollector(window_minutes)
    
    return _metrics_instance
