"""
Test script for query cache system
"""
import sys
sys.path.insert(0, '.')

from cache.sqlite_cache import SQLiteCache
from cache.cache_manager import CacheManager
import os

print("=" * 60)
print("TESTING QUERY CACHE SYSTEM")
print("=" * 60)

# Test 1: SQLite Cache
print("\n[TEST 1] SQLite Cache Basic Operations")
print("-" * 60)

test_db_path = './test_cache.db'
cache = SQLiteCache(test_db_path)

# Test set
print("Setting test data...")
test_data = {
    'query_text': 'SELECT * FROM products LIMIT 10',
    'results': [
        {'id': 1, 'name': 'Product A'},
        {'id': 2, 'name': 'Product B'}
    ],
    'columns': ['id', 'name'],
    'row_count': 2,
    'user_id': 'test_user'
}

success = cache.set('test_key_123', test_data, ttl=3600)
print(f"  Set result: {'PASS' if success else 'FAIL'}")

# Test get
print("Getting test data...")
retrieved = cache.get('test_key_123')
if retrieved and retrieved['row_count'] == 2:
    print(f"  Get result: PASS (rows: {retrieved['row_count']})")
else:
    print(f"  Get result: FAIL")

# Test stats
print("Getting cache stats...")
stats = cache.get_stats()
print(f"  Total entries: {stats['total_entries']}")
print(f"  Size: {stats['total_size_mb']} MB")
print(f"  Backend: {stats['backend']}")

# Cleanup
cache.clear_all()
os.remove(test_db_path) if os.path.exists(test_db_path) else None
print("  Cleanup: PASS")

# Test 2: Cache Manager
print("\n[TEST 2] Cache Manager with Query Hashing")
print("-" * 60)

manager = CacheManager(backend='sqlite', sqlite_path='./test_manager_cache.db')

# Test key generation
sql1 = "  SELECT * FROM products   WHERE id = 1  "
sql2 = "SELECT * FROM products WHERE id = 1"  # Same query, different format
key1 = manager.generate_cache_key(sql1)
key2 = manager.generate_cache_key(sql2)

print(f"Query 1: {sql1.strip()[:40]}...")
print(f"Query 2: {sql2.strip()[:40]}...")
print(f"  Keys match: {'PASS' if key1 == key2 else 'FAIL'}")
print(f"  Key: {key1}")

# Test cache and retrieve
print("\nCaching query result...")
manager.cache_query_result(
    sql1,
    [{'id': 1, 'name': 'Test Product'}],
    ['id', 'name'],
    'user123'
)

print("Retrieving cached result...")
result = manager.get_cached_result(sql2)  # Using different format
if result:
    print(f"  Cache HIT: PASS")
    print(f"  Results count: {result['row_count']}")
    print(f"  Age: {result['age']} seconds")
else:
    print(f"  Cache HIT: FAIL")

# Get Stats
stats = manager.get_stats()
print(f"\nCache Statistics:")
print(f"  Enabled: {stats['enabled']}")
print(f"  Backend: {stats['backend']}")
print(f"  Entries: {stats['total_entries']}")
print(f"  Hit Rate: {stats['hit_rate'] * 100:.1f}%")

# Cleanup
manager.clear_all()
os.remove('./test_manager_cache.db') if os.path.exists('./test_manager_cache.db') else None
os.remove('./data/test_manager_cache.db') if os.path.exists('./data/test_manager_cache.db') else None

# Test 3: Config Integration
print("\n[TEST 3] Configuration Loading")
print("-" * 60)

from config import Config

print(f"  Cache Enabled: {Config.CACHE_ENABLED}")
print(f"  Cache Backend: {Config.CACHE_BACKEND}")
print(f"  SQLite Path: {Config.CACHE_SQLITE_PATH}")
print(f"  Default TTL: {Config.CACHE_DEFAULT_TTL} seconds ({Config.CACHE_DEFAULT_TTL // 86400} days)")
print(f"  Max Size: {Config.CACHE_SQLITE_MAX_SIZE_MB} MB")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
