"""
Test Query Timeout
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from database.db_connection import DatabaseConnection
from config import Config

print("="*70)
print("QUERY TIMEOUT TEST")
print("="*70)

# Initialize DB connection
db_config = Config.get_db_config()
db_conn = DatabaseConnection(db_config)

print(f"\n[CONFIG] Query timeout set to: {Config.QUERY_TIMEOUT_SECONDS} seconds")

# Test 1: Normal fast query (should succeed)
print("\n[TEST 1] Fast query (should complete)")
try:
    columns, rows = db_conn.execute_query("SELECT 1")
    print(f"  Result: SUCCESS - Got {len(rows)} row(s)")
except Exception as e:
    print(f"  Result: FAILED - {e}")

# Test 2: Simulated slow query (should timeout)
print(f"\n[TEST 2] Slow query simulation (SLEEP {Config.QUERY_TIMEOUT_SECONDS + 5}s)")
print(f"  Expected: Query should timeout after {Config.QUERY_TIMEOUT_SECONDS}s")

start_time = time.time()
try:
    # This will sleep longer than timeout
    sleep_time = Config.QUERY_TIMEOUT_SECONDS + 5
    columns, rows = db_conn.execute_query(f"SELECT SLEEP({sleep_time})")
    elapsed = time.time() - start_time
    print(f"  Result: UNEXPECTED SUCCESS after {elapsed:.1f}s")
    print(f"  WARNING: Timeout did not work!")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  Result: TIMEOUT as expected after {elapsed:.1f}s")
    print(f"  Error: {str(e)[:100]}")
    
    # Verify it timed out around the configured time
    if abs(elapsed - Config.QUERY_TIMEOUT_SECONDS) < 5:
        print(f"  Status: PASS - Timed out within tolerance")
    else:
        print(f"  Status: CHECK - Timing seems off")

# Test 3: Query just under timeout (should succeed)
safe_time = max(1, Config.QUERY_TIMEOUT_SECONDS - 5)
print(f"\n[TEST 3] Query just under timeout (SLEEP {safe_time}s)")
start_time = time.time()
try:
    columns, rows = db_conn.execute_query(f"SELECT SLEEP({safe_time})")
    elapsed = time.time() - start_time
    print(f"  Result: SUCCESS - Completed in {elapsed:.1f}s")
except Exception as e:
    elapsed = time.time() - start_time
    print(f"  Result: FAILED unexpectedly after {elapsed:.1f}s")
    print(f"  Error: {e}")

print("\n" + "="*70)
print("TEST COMPLETE")
print(f"Query timeout is configured to {Config.QUERY_TIMEOUT_SECONDS} seconds")
print("Long-running queries will be terminated automatically")
print("="*70)

db_conn.close()
