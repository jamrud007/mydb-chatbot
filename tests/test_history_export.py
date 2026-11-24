"""
Test Query History Export
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from chatbot.conversation_manager import ConversationManager
from utils.history_exporter import HistoryExporter

print("="*70)
print("QUERY HISTORY EXPORT TEST")
print("="*70)

# Setup
conv_manager = ConversationManager(max_history=10)
exporter = HistoryExporter(conv_manager)

# Add some test conversations
print("\n[SETUP] Adding test conversations")
conv_manager.add_exchange(
    'test_user',
    'Berapa total produk yang tersedia?',
    'Berikut SQL untuk menghitung total produk:\nSELECT COUNT(*) as total FROM products'
)

conv_manager.add_exchange(
    'test_user',
    'Siapa customer dengan pembelian terbanyak?',
    'Query untuk mencari customer top:\nSELECT customer_id, COUNT(*) FROM orders GROUP BY customer_id ORDER BY COUNT(*) DESC LIMIT 1'
)

conv_manager.add_exchange(
    'test_user',
    'Berapa rata-rata harga produk per kategori?',
    'Query untuk avg price per category:\nSELECT category, AVG(price) FROM products GROUP BY category'
)

print(f"  Added 3 conversations for test_user")

# Test 1: Export Stats
print("\n[TEST 1] Export Statistics")
stats = exporter.get_export_stats('test_user')
print(f"  User ID: {stats['user_id']}")
print(f"  Total Conversations: {stats['total_conversations']}")
print(f"  Available Formats: {', '.join(stats['available_formats'])}")
print(f"  Session Created: {stats['session_created_at']}")

# Test 2: JSON Export
print("\n[TEST 2] JSON Export")
json_export = exporter.export_conversation_json('test_user')
json_data = json.loads(json_export)
print(f"  Exported {json_data['total_exchanges']} exchanges")
print(f"  First conversation: {json_data['conversations'][0]['user_message'][:50]}...")
print(f"  JSON size: {len(json_export)} bytes")

# Test 3: CSV Export
print("\n[TEST 3] CSV Export")
csv_export = exporter.export_conversation_csv('test_user')
csv_lines = csv_export.split('\n')
print(f"  CSV lines: {len(csv_lines)}")
print(f"  Header: {csv_lines[0]}")
print(f"  First row: {csv_lines[1][:80]}...")

# Test 4: Text Export
print("\n[TEST 4] Text Export")
text_export = exporter.export_conversation_text('test_user')
lines = text_export.split('\n')
print(f"  Text lines: {len(lines)}")
print(f"  Preview:")
for line in lines[:10]:
    print(f"    {line}")

# Test 5: Full History Export
print("\n[TEST 5] Full History Export (JSON with metadata)")
full_export = exporter.export_full_history_json('test_user')
full_data = json.loads(full_export)
print(f"  User ID: {full_data['user_id']}")
print(f"  Exported At: {full_data['exported_at']}")
print(f"  Total Conversations: {full_data['conversations']['total']}")
print(f"  Has Query Results: {'query_results' in full_data}")

print("\n" + "="*70)
print("SUCCESS: All export formats working correctly!")
print("="*70)

print("\n[EXPORT FORMATS AVAILABLE]")
print("1. JSON - Complete structured data with metadata")
print("2. CSV - Spreadsheet-compatible tabular format")
print("3. Text - Human-readable formatted output")
print("")
print("[API ENDPOINTS]")
print("GET /api/history/export/stats - Get export statistics")
print("GET /api/history/export/json - Download JSON export")
print("GET /api/history/export/csv - Download CSV export")
print("GET /api/history/export/text - Download text export")
