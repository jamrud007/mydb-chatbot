import os
import sys
from dotenv import load_dotenv
import mysql.connector
from tabulate import tabulate

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def show_sample_data():
    """Display sample data from all main tables"""
    
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = connection.cursor(dictionary=True)
    
    print("=" * 100)
    print("📊 SAMPLE DATA FROM DATABASE: ecommerce_olist")
    print("=" * 100)
    
    # 1. Customers
    print("\n" + "=" * 100)
    print("👥 CUSTOMERS (Top 5)")
    print("=" * 100)
    cursor.execute("SELECT * FROM customers LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # 2. Orders
    print("\n" + "=" * 100)
    print("📦 ORDERS (Top 5)")
    print("=" * 100)
    cursor.execute("SELECT * FROM orders LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # 3. Products
    print("\n" + "=" * 100)
    print("🛍️ PRODUCTS (Top 5)")
    print("=" * 100)
    cursor.execute("SELECT * FROM products LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # 4. Order Items
    print("\n" + "=" * 100)
    print("📋 ORDER ITEMS (Top 5)")
    print("=" * 100)
    cursor.execute("SELECT * FROM order_items LIMIT 5")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # 5. Sellers
    print("\n" + "=" * 100)
    print("🏪 SELLERS (All)")
    print("=" * 100)
    cursor.execute("SELECT * FROM sellers")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    # 6. Product Categories
    print("\n" + "=" * 100)
    print("📂 PRODUCT CATEGORIES (Top 10)")
    print("=" * 100)
    cursor.execute("SELECT * FROM product_category_name_translation LIMIT 10")
    rows = cursor.fetchall()
    if rows:
        print(tabulate(rows, headers="keys", tablefmt="grid"))
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 100)
    print("✅ SAMPLE DATA DISPLAYED")
    print("=" * 100)

if __name__ == "__main__":
    show_sample_data()
