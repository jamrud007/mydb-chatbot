
from database.db_connection import DatabaseConnection
from database.schema_manager import SchemaManager
from config import Config

def print_llm_schema():
    print("Initializing components...")
    db_config = Config.get_db_config()
    db = DatabaseConnection(db_config)
    schema_manager = SchemaManager(db)
    
    print("\n--- FORMATTED SCHEMA FOR LLM ---")
    schema_text = schema_manager.format_schema_for_llm()
    print(schema_text)
    
    if "product_category_name_translation" in schema_text:
        print("\n[OK] Translation table found in schema.")
    else:
        print("\n[FAIL] Translation table NOT found in schema.")
        
    if "product_category_name_english" in schema_text:
        print("[OK] English column found in schema.")
    else:
        print("[FAIL] English column NOT found in schema.")

if __name__ == "__main__":
    print_llm_schema()
