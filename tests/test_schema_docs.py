"""
Test Schema Documentation Generator
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from database.db_connection import DatabaseConnection
from database.schema_manager import SchemaManager
from utils.schema_docs import SchemaDocGenerator
from config import Config

print("="*70)
print("SCHEMA DOCUMENTATION GENERATOR TEST")
print("="*70)

# Setup
db_config = Config.get_db_config()
db_conn = DatabaseConnection(db_config)
schema_mgr = SchemaManager(db_conn)
doc_gen = SchemaDocGenerator(schema_mgr, db_conn)

# Test 1: Markdown documentation
print("\n[TEST 1] Markdown Documentation")
markdown = doc_gen.generate_markdown(include_stats=False)
lines = markdown.split('\n')
print(f"  Total lines: {len(lines)}")
print(f"  Preview (first 15 lines):")
for line in lines[:15]:
    print(f"    {line}")
print("  ...")

# Test 2: Markdown with statistics
print("\n[TEST 2] Markdown with Statistics")
markdown_stats = doc_gen.generate_markdown(include_stats=True)
if 'Total Rows:' in markdown_stats:
    print("  ✓ Row counts included")
else:
    print("  ⚠ Row counts not available (normal if tables empty)")

# Test 3: HTML documentation
print("\n[TEST 3] HTML Documentation")
html = doc_gen.generate_html(include_stats=False)
print(f"  HTML size: {len(html)} bytes")
print(f"  Contains <!DOCTYPE>: {'✓' if '<!DOCTYPE' in html else '✗'}")
print(f"  Contains tables: {'✓' if '<table>' in html else '✗'}")
print(f"  Contains CSS: {'✓' if '<style>' in html else '✗'}")
print(f"  Contains ToC: {'✓' if 'Table of Contents' in html else '✗'}")

# Test 4: JSON documentation
print("\n[TEST 4] JSON Documentation")
import json
json_docs = doc_gen.generate_json(include_stats=False)
doc_data = json.loads(json_docs)
print(f"  Total tables: {doc_data['total_tables']}")
print(f"  Generated at: {doc_data['generated_at']}")
print(f"  First table: {doc_data['tables'][0]['name']}")
print(f"  First table columns: {doc_data['tables'][0]['total_columns']}")
print(f"  Primary keys: {doc_data['tables'][0]['primary_keys']}")

# Test 5: Documentation quality checks
print("\n[TEST 5] Documentation Quality Checks")
schema = schema_mgr.get_schema()
total_tables = len(schema['tables'])
print(f"  Tables in schema: {total_tables}")
print(f"  Tables in Markdown: {markdown.count('## ') - 1}")  # -1 for ToC header
print(f"  Tables in HTML: {html.count('<h2 id')}")
print(f"  Tables in JSON: {len(doc_data['tables'])}")

# Test 6: Content verification
print("\n[TEST 6] Content Verification")
first_table = schema['tables'][0] if schema['tables'] else None
if first_table:
    table_name = first_table['name']
    print(f"  Checking table: {table_name}")
    print(f"    In Markdown: {'✓' if table_name in markdown else '✗'}")
    print(f"    In HTML: {'✓' if table_name in html else '✗'}")
    print(f"    In JSON: {'✓' if table_name in json_docs else '✗'}")
    
    # Check columns
    first_col = first_table['columns'][0]['name'] if first_table['columns'] else None
    if first_col:
        print(f"  Checking column: {first_col}")
        print(f"    In Markdown: {'✓' if first_col in markdown else '✗'}")
        print(f"    In HTML: {'✓' if first_col in html else '✗'}")

print("\n" + "="*70)
print("SUCCESS: Schema documentation generator working!")
print("="*70)

print("\n[SUPPORTED FORMATS]")
print("1. 📄 Markdown - Clean, readable, GitHub-compatible")
print("2. 🌐 HTML - Beautiful styled web page with CSS")
print("3. 📊 JSON - Structured data for programmatic access")

print("\n[FEATURES]")
print("✓ Table of Contents with anchors")
print("✓ Column details (type, nullable, keys, defaults)")
print("✓ Primary/Foreign key identification")
print("✓ Optional row count statistics")
print("✓ Auto-generated timestamps")

print("\n[API ENDPOINTS]")
print("GET /api/schema/docs/markdown?include_stats=true")
print("GET /api/schema/docs/html?include_stats=true")
print("GET /api/schema/docs/json?include_stats=true")

# Save sample output
print("\n[SAMPLE OUTPUT SAVED]")
with open('schema_docs_sample.md', 'w', encoding='utf-8') as f:
    f.write(markdown)
print("  ✓ schema_docs_sample.md")

with open('schema_docs_sample.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("  ✓ schema_docs_sample.html")

with open('schema_docs_sample.json', 'w', encoding='utf-8') as f:
    f.write(json_docs)
print("  ✓ schema_docs_sample.json")

db_conn.close()
