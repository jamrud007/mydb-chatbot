
import mysql.connector
from config import Config

def count_categories():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()
        
        # Count distinct categories in products table
        cursor.execute("SELECT COUNT(DISTINCT product_category_name) FROM products")
        count_products = cursor.fetchone()[0]
        
        # Count categories in translation table
        cursor.execute("SELECT COUNT(*) FROM product_category_name_translation")
        count_translation = cursor.fetchone()[0]
        
        print(f"Total Unique Categories in Products: {count_products}")
        print(f"Total Translated Categories: {count_translation}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    count_categories()
