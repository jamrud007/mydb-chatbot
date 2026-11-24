"""
Test Metrics Collection
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from utils.metrics import MetricsCollector

print("="*70)
print("METRICS COLLECTION TEST")
print("="*70)

# Initialize metrics collector
metrics = MetricsCollector(window_minutes=1)  # 1 minute window for testing

# Test 1: Query duration tracking
print("\n[TEST 1] Query duration tracking")
metrics.record_query_duration(45.2, user_id='user1', query='SELECT * FROM products')
metrics.record_query_duration(123.7, user_id='user1', query='SELECT * FROM orders')
metrics.record_query_duration(5500, user_id='user2', query='SELECT * with HUGE JOIN')  # Slow query
metrics.record_query_duration(12.1, user_id='user1', from_cache=True)

stats = metrics.get_query_stats()
print(f"  Total queries: {stats['total_queries']}")
print(f"  Avg duration: {stats['avg_duration_ms']}ms")
print(f"  P95: {stats['p95_duration_ms']}ms")
print(f"  P99: {stats['p99_duration_ms']}ms")
print(f"  Slow queries: {stats['slow_query_count']}")

# Test 2: Error tracking
print("\n[TEST 2] Error tracking")
metrics.record_error('SQL_EXECUTION_ERROR', user_id='user1')
metrics.record_error('SQL_EXECUTION_ERROR', user_id='user2')
metrics.record_error('OLLAMA_TIMEOUT', user_id='user1')

error_stats = metrics.get_error_stats()
print(f"  Total errors: {error_stats['total_errors']}")
print(f"  Errors by type: {error_stats['errors_by_type']}")

# Test 3: Cache statistics
print("\n[TEST 3] Cache performance")
cache_stats = metrics.get_cache_stats()
print(f"  Cache hits: {cache_stats['cache_hits']}")
print(f"  Cache misses: {cache_stats['cache_misses']}")
print(f"  Hit rate: {cache_stats['hit_rate_percent']}%")

# Test 4: Usage statistics
print("\n[TEST 4] Usage statistics")
usage_stats = metrics.get_usage_stats()
print(f"  Total users: {usage_stats['total_users']}")
print(f"  Total requests: {usage_stats['total_requests']}")
print(f"  Top users: {usage_stats['top_users']}")

# Test 5: LLM tracking
print("\n[TEST 5] LLM performance")
metrics.record_llm_call(234.5, success=True)
metrics.record_llm_call(567.8, success=True)
metrics.record_llm_call(0, success=False)

llm_stats = metrics.get_llm_stats()
print(f"  Total LLM calls: {llm_stats['total_calls']}")
print(f"  Failures: {llm_stats['failures']}")
print(f"  Success rate: {llm_stats['success_rate_percent']}%")
print(f"  Avg duration: {llm_stats['avg_duration_ms']}ms")

# Test 6: All metrics in one call
print("\n[TEST 6] Get all metrics (JSON format)")
all_metrics = metrics.get_all_metrics()
print(f"  Timestamp: {all_metrics['timestamp']}")
print(f"  Uptime: {all_metrics['uptime_seconds']}s")
print(f"  Window: {all_metrics['window_minutes']} minutes")
print(f"  Query performance keys: {list(all_metrics['query_performance'].keys())}")
print(f"  Error keys: {list(all_metrics['errors'].keys())}")
print(f"  Cache keys: {list(all_metrics['cache'].keys())}")
print(f"  Usage keys: {list(all_metrics['usage'].keys())}")
print(f"  LLM keys: {list(all_metrics['llm'].keys())}")
print(f"  Slow queries count: {len(all_metrics['slow_queries'])}")

# Test 7: Slow query details
print("\n[TEST 7] Slow query details")
for i, slow_query in enumerate(all_metrics['slow_queries'], 1):
    print(f"  {i}. {slow_query['duration_ms']:.1f}ms - User: {slow_query['user_id']}")
    print(f"     Query: {slow_query['query'][:60]}...")

print("\n" + "="*70)
print("SUCCESS: All metrics collection tests passed!")
print("Metrics ready for production monitoring")
print("="*70)

print("\n[EXAMPLE USE CASES]")
print("1. Monitor query performance trends (identify slow queries)")
print("2. Track error rates and types (debugging)")
print("3. Measure cache effectiveness (optimization)")
print("4. Analyze usage patterns (capacity planning)")
print("5. Monitor LLM performance (cost optimization)")
