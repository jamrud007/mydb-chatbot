"""
Test Structured Logging
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import logging
from utils.structured_logger import StructuredLogger, TimingContext, setup_structured_logging

print("="*70)
print("STRUCTURED LOGGING TEST")
print("="*70)

# Test 1: Basic structured logging
print("\n[TEST 1] Basic structured logging with context")
logger = StructuredLogger('test_app', min_level=logging.DEBUG)

logger.info('user_login', user_id='user123', ip_address='192.168.1.1')
logger.warning('rate_limit_approaching', user_id='user123', requests=9, limit=10)
logger.debug('cache_hit', key='query:abc123', ttl=3600)

# Test 2: Context setting
print("\n[TEST 2] Global context (request_id)")
logger.set_context(request_id='req-abc-123', environment='test')
logger.info('request_started', method='POST', path='/api/chat')
logger.info('request_completed', status_code=200)
logger.clear_context()

# Test 3: Error logging
print("\n[TEST 3] Error logging with exception")
try:
    result = 10 / 0
except Exception as e:
    logger.error('division_error', error=e, numerator=10, denominator=0)

# Test 4: Timing context
print("\n[TEST 4] Timing context (automatic duration tracking)")
with TimingContext(logger, 'database_query', user_id='user456', query='SELECT *'):
    time.sleep(0.1)  # Simulate work

# Test 5: Failed timing
print("\n[TEST 5] Failed operation timing")
try:
    with TimingContext(logger, 'api_call', endpoint='/external'):
        time.sleep(0.05)
        raise ValueError("API returned 500")
except ValueError:
    pass  # Error logged by TimingContext

# Test 6: High-volume logging simulation
print("\n[TEST 6] High-volume logging (10 events)")
start = time.time()
for i in range(10):
    logger.info('batch_event', 
                batch_id=f'batch_{i}', 
                item_count=100, 
                processed=i*100)
elapsed = (time.time() - start) * 1000
print(f"Logged 10 events in {elapsed:.1f}ms")

print("\n" + "="*70)
print("STRUCTURED LOGGING FEATURES DEMONSTRATED:")
print("- JSON output format")
print("- Context fields (user_id, request_id, etc.)")
print("- Automatic timestamps (ISO 8601 UTC)")
print("- Exception handling with traceback")
print("- Timing context with duration tracking")
print("- Event-based logging (instead of messages)")
print("="*70)

print("\n[EXAMPLE JSON OUTPUT]")
print("The console output above is already in JSON format!")
print("Each line can be parsed and indexed by log aggregation tools")
print("(e.g., ELK Stack, Splunk, CloudWatch Insights)")
