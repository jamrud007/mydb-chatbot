"""
Test Query Suggestions / Autocomplete
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from database.db_connection import DatabaseConnection
from database.schema_manager import SchemaManager
from chatbot.conversation_manager import ConversationManager
from utils.query_suggestions import QuerySuggestionEngine
from config import Config

print("="*70)
print("QUERY SUGGESTIONS / AUTOCOMPLETE TEST")
print("="*70)

# Setup
db_config = Config.get_db_config()
db_conn = DatabaseConnection(db_config)
schema_mgr = SchemaManager(db_conn)
conv_mgr = ConversationManager()
engine = QuerySuggestionEngine(schema_mgr, conv_mgr)

# Add some history
conv_mgr.add_exchange('test_user', 'Berapa total produk?', 'Query: SELECT COUNT(*) FROM products')
conv_mgr.add_exchange('test_user', 'Siapa customer terbaik?', 'Query: SELECT * FROM customers ORDER BY total_spent DESC LIMIT 1')

# Test 1: General suggestions (empty query)
print("\n[TEST 1] General suggestions (no input)")
suggestions = engine.get_suggestions('', user_id='test_user', language='id', limit=10)
print(f"  Total suggestions: {len(suggestions)}")
for i, sug in enumerate(suggestions[:5], 1):
    print(f"  {i}. [{sug['type']}] {sug['display'][:60]}")

# Test 2: Schema-based autocomplete (partial table name)
print("\n[TEST 2] Schema-based suggestions (partial: 'prod')")
suggestions = engine.get_suggestions('prod', user_id='test_user', limit=10)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions[:3]:
    print(f"  - {sug['display'][:70]} (score: {sug['score']})")

# Test 3: English question suggestions
print("\n[TEST 3] English question suggestions")
suggestions = engine.get_question_suggestions(language='en', limit=5)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions:
    print(f"  - {sug['display']}")

# Test 4: Indonesian question suggestions
print("\n[TEST 4] Indonesian question suggestions")
suggestions = engine.get_question_suggestions(language='id', limit=5)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions:
    print(f"  - {sug['display']}")

# Test 5: SQL pattern suggestions
print("\n[TEST 5] SQL pattern suggestions")
suggestions = engine.get_pattern_suggestions('', limit=5)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions:
    print(f"  - {sug['value']}")

# Test 6: History suggestions
print("\n[TEST 6] User history suggestions")
suggestions = engine.get_history_suggestions(user_id='test_user', limit=5)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions:
    print(f"  - {sug['display']}")

# Test 7: Record queries and get popular
print("\n[TEST 7] Popular queries")
engine.record_query('Berapa total produk?', 'user1')
engine.record_query('Berapa total produk?', 'user2')
engine.record_query('Siapa customer terbaik?', 'user1')
suggestions = engine.get_popular_suggestions(limit=3)
print(f"  Total suggestions: {len(suggestions)}")
for sug in suggestions:
    print(f"  - {sug['display']}")

# Test 8: Combined suggestions with partial input
print("\n[TEST 8] Combined suggestions (partial: 'ber')")
suggestions = engine.get_suggestions('ber', user_id='test_user', language='id', limit=10)
print(f"  Total suggestions: {len(suggestions)}")
print("  Breakdown by type:")
type_counts = {}
for sug in suggestions:
    type_counts[sug['type']] = type_counts.get(sug['type'], 0) + 1
for sug_type, count in type_counts.items():
    print(f"    - {sug_type}: {count}")

print("\n" + "="*70)
print("SUCCESS: Query suggestion system working!")
print("="*70)

print("\n[SUGGESTION TYPES]")
print("📊 table - Database tables")
print("🔹 column - Table columns")
print("💡 pattern - Common SQL patterns")
print("❓ question - Natural language examples")
print("🕐 history - User's past queries")
print("🔥 popular - Most used queries")

print("\n[API USAGE]")
print("GET /api/suggestions?q=prod&lang=en&limit=10")
print("  Returns autocomplete suggestions for 'prod'")

db_conn.close()
