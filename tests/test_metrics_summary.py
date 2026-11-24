"""
Test suite for MetricsCollector.get_summary()
Verifies the condensed summary behind /api/metrics/summary is structured
and human-readable enough for quick debugging.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from utils.metrics import MetricsCollector, _format_uptime

print("="*70)
print("METRICS SUMMARY TEST SUITE")
print("="*70)

# Test 1: Uptime formatting
print("\n[TEST 1] Uptime formatting")
print(f"  5s      -> {_format_uptime(5)}")
print(f"  65s     -> {_format_uptime(65)}")
print(f"  3661s   -> {_format_uptime(3661)}")
print(f"  90061s  -> {_format_uptime(90061)}")
assert _format_uptime(5) == "5s"
assert _format_uptime(65) == "1m 5s"
assert _format_uptime(3661) == "1h 1m 1s"
assert _format_uptime(90061) == "1d 1h 1m 1s"

# Test 2: Summary with no traffic yet
print("\n[TEST 2] Summary with no traffic")
metrics = MetricsCollector(window_minutes=60)
summary = metrics.get_summary()
print(f"  status: {summary['status']}")
print(f"  uptime_human: {summary['uptime_human']}")
print(f"  requests: {summary['requests']}")
assert summary['status'] == 'ok'
assert summary['requests']['total'] == 0
assert summary['requests']['error_rate_percent'] == 0
assert 'uptime_human' in summary

# Test 3: Status stays 'ok' with healthy traffic
print("\n[TEST 3] Summary stays 'ok' with healthy traffic")
metrics.record_query_duration(45.2, user_id='user1', query='SELECT * FROM products')
metrics.record_query_duration(120.0, user_id='user2', query='SELECT * FROM orders')
metrics.record_llm_call(300.0, success=True)
summary = metrics.get_summary()
print(f"  status: {summary['status']}, requests={summary['requests']}, llm={summary['llm']}")
assert summary['status'] == 'ok'
assert summary['requests']['total'] == 2
assert summary['llm']['total_calls'] == 1

# Test 4: Status degrades to 'critical' when error rate is high
print("\n[TEST 4] Status degrades when error rate climbs")
metrics2 = MetricsCollector(window_minutes=60)
metrics2.record_query_duration(50.0, user_id='user1')
metrics2.record_error('SQL_EXECUTION_ERROR', user_id='user1')
summary2 = metrics2.get_summary()
print(f"  1 query + 1 error -> status={summary2['status']}, error_rate={summary2['requests']['error_rate_percent']}%")
assert summary2['requests']['error_rate_percent'] == 50.0
assert summary2['status'] == 'critical'

# Test 5: top_errors sorted by frequency
print("\n[TEST 5] top_errors sorted by frequency")
metrics3 = MetricsCollector(window_minutes=60)
for _ in range(3):
    metrics3.record_error('OLLAMA_TIMEOUT', user_id='user1')
metrics3.record_error('SQL_EXECUTION_ERROR', user_id='user1')
summary3 = metrics3.get_summary()
top_errors = list(summary3['top_errors'].items())
print(f"  top_errors: {top_errors}")
assert top_errors[0] == ('OLLAMA_TIMEOUT', 3)

print("\n" + "="*70)
print("SUCCESS: /api/metrics/summary payload is structured and human-readable")
print("="*70)
