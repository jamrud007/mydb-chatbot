"""
Test suite for SQL Validator - Windows Compatible
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from utils.sql_validator import SQLValidator
from database.schema_manager import SchemaManager
from database.db_connection import DatabaseConnection
from config import Config

# Initialize components
db_config = Config.get_db_config()
db_connection = DatabaseConnection(db_config)
schema_manager = SchemaManager(db_connection)
validator = SQLValidator(schema_manager)

print("="*70)
print("SQL VALIDATOR TEST SUITE")
print("="*70)

# Test 1: Typo Auto-Correction
print("\n[TEST 1] Auto-correct table name typo (product_categoory)")
sql1 = "SELECT * FROM product_categoory_name_translation LIMIT 5"
result1 = validator.validate_and_fix(sql1)
print(f"Valid: {result1['valid']}")
if result1['corrections']:
    for corr in result1['corrections']:
        print(f"  Corrected: {corr['original']} -> {corr['corrected']} (similarity: {corr['similarity']})")
print(f"Fixed SQL: {result1['fixed_sql'][:80]}...")

# Test 2: Unsafe Operation (should block)
print("\n[TEST 2] Unsafe operation (DELETE) - should FAIL")
sql2 = "DELETE FROM customers WHERE id = 1"
result2 = validator.validate_and_fix(sql2)
print(f"Valid: {result2['valid']} (Expected: False)")
print(f"Error Type: {result2.get('error_type')}")

# Test 3: Valid Query (should pass)
print("\n[TEST 3] Valid query - should PASS")
sql3 = "SELECT * FROM orders WHERE order_status = 'delivered' LIMIT 10"
result3 = validator.validate_and_fix(sql3)
print(f"Valid: {result3['valid']} (Expected: True)")
print(f"Changed: {result3['changed']}")

# Test 4: The Original Issue - product_categoory in complex query
print("\n[TEST 4] Original issue - multiple 'product_categoory' typos")
sql4 = """SELECT p.product_category_name_english
FROM products p
JOIN product_categoory_name_translation t 
ON p.product_categoory_name = t.product_categoory_name"""

result4 = validator.validate_and_fix(sql4)
print(f"Valid: {result4['valid']}")
if result4['corrections']:
    print(f"Corrections applied: {len(result4['corrections'])}")
    for corr in result4['corrections']:
        print(f"  - {corr['original']} -> {corr['corrected']}")
elif not result4['valid']:
    print(f"Error: {result4['error']}")

print("\n" + "="*70)
if result4['valid'] and result4['corrections']:
    print("SUCCESS: Validator working correctly!")
    print(f"Auto-corrected {len(result4['corrections'])} typo(s)")
else:
    print("CHECK RESULTS ABOVE")
print("="*70)

# Close connection
db_connection.close()
