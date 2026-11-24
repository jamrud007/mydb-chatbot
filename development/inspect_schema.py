
import mysql.connector
from config import Config

def inspect_schema():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # Check products table
        print("\n--- PRODUCTS Table ---")
        cursor.execute("DESCRIBE products")
        for col in cursor.fetchall():
            print(f"{col[0]} ({col[1]})")
            
        # Check for translation table
        print("\n--- Tables ---")
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        print(tables)
        
        if 'product_category_name_translation' in tables:
            print("\n--- TRANSLATION Table ---")
            cursor.execute("DESCRIBE product_category_name_translation")
            for col in cursor.fetchall():
                print(f"{col[0]} ({col[1]})")
                
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    inspect_schema()
