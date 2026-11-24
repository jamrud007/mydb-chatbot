"""
Test suite for Rate Limiting
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
from utils.rate_limiter import RateLimiter

print("="*70)
print("RATE LIMITING TEST SUITE")
print("="*70)

# Test 1: Basic rate limiting
print("\n[TEST 1] Basic rate limiting (10 requests in 60s)")
limiter = RateLimiter(max_requests=5, window_seconds=10)

user_id = "test_user_1"
allowed_count = 0
denied_count = 0

for i in range(7):
    is_allowed, retry_after = limiter.is_allowed(user_id)
    if is_allowed:
        allowed_count += 1
        print(f"  Request {i+1}: ALLOWED")
    else:
        denied_count += 1
        print(f"  Request {i+1}: DENIED (retry after {retry_after}s)")

print(f"Result: {allowed_count} allowed, {denied_count} denied (Expected: 5 allowed, 2 denied)")
assert allowed_count == 5, "Should allow exactly 5 requests"
assert denied_count == 2, "Should deny 2 requests"

# Test 2: Stats retrieval
print("\n[TEST 2] Stats retrieval")
stats = limiter.get_stats(user_id)
print(f"  Requests in window: {stats['requests_in_window']}/{stats['max_requests']}")
print(f"  Remaining: {stats['remaining']}")
print(f"  Window: {stats['window_seconds']}s")
assert stats['requests_in_window'] == 5, "Should show 5 requests"
assert stats['remaining'] == 0, "Should have 0 remaining"

# Test 3: Different users are isolated
print("\n[TEST 3] Different users are isolated")
user2_allowed, _ = limiter.is_allowed("test_user_2")
print(f"  User 2 first request: {'ALLOWED' if user2_allowed else 'DENIED'}")
assert user2_allowed, "Different user should not be affected by first user's limit"

# Test 4: Window expiration
print("\n[TEST 4] Sliding window expiration")
print("  Waiting 11 seconds for window to slide...")
time.sleep(11)
is_allowed, _ = limiter.is_allowed(user_id)
print(f"  After window expiration: {'ALLOWED' if is_allowed else 'DENIED'}")
assert is_allowed, "Requests should be allowed after window expires"

# Test 5: Reset functionality
print("\n[TEST 5] Manual reset")
limiter2 = RateLimiter(max_requests=2, window_seconds=60)
limiter2.is_allowed("reset_test")
limiter2.is_allowed("reset_test")
is_allowed_before, _ = limiter2.is_allowed("reset_test")
print(f"  Before reset (3rd request): {'ALLOWED' if is_allowed_before else 'DENIED'}")

limiter2.reset("reset_test")
is_allowed_after, _ = limiter2.is_allowed("reset_test")
print(f"  After reset (1st request): {'ALLOWED' if is_allowed_after else 'DENIED'}")
assert not is_allowed_before, "Should be denied before reset"
assert is_allowed_after, "Should be allowed after reset"

# Test 6: Thread safety (basic check)
print("\n[TEST 6] Thread safety")
from threading import Thread

limiter3 = RateLimiter(max_requests=10, window_seconds=1)
results = []

def make_request():
    is_allowed, _ = limiter3.is_allowed("concurrent_user")
    results.append(is_allowed)

threads = [Thread(target=make_request) for _ in range(15)]
for t in threads:
    t.start()
for t in threads:
    t.join()

allowed_concurrent = sum(results)
print(f"  Concurrent requests: {allowed_concurrent} allowed out of 15")
print(f"  (Should be exactly 10 with thread-safe implementation)")
assert allowed_concurrent == 10, "Thread-safe limiter should allow exactly 10"

print("\n" + "="*70)
print("SUCCESS: All rate limiting tests passed!")
print("Sliding window algorithm working correctly")
print("Thread-safe implementation verified")
print("="*70)
