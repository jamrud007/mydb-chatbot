import os
import sys
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def find_numeric_columns():
    """Find all numeric columns with interesting data"""
    
    connection = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = connection.cursor(dictionary=True)
    
    print("=" * 100)
    print("🔢 NUMERIC COLUMNS WITH UNIQUE/INTERESTING DATA")
    print("=" * 100)
    
    # 1. Price & Freight Analysis
    print("\n💰 PRICE & FREIGHT (Order Items):")
    print("-" * 100)
    cursor.execute("""
        SELECT 
            MIN(price) as min_price,
            MAX(price) as max_price,
            AVG(price) as avg_price,
            MIN(freight_value) as min_freight,
            MAX(freight_value) as max_freight,
            AVG(freight_value) as avg_freight,
            SUM(price) as total_revenue,
            COUNT(DISTINCT order_id) as total_orders
        FROM order_items
    """)
    result = cursor.fetchone()
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # 2. Product Dimensions
    print("\n📦 PRODUCT DIMENSIONS:")
    print("-" * 100)
    cursor.execute("""
        SELECT 
            MIN(product_weight_g) as min_weight,
            MAX(product_weight_g) as max_weight,
            AVG(product_weight_g) as avg_weight,
            MIN(product_length_cm) as min_length,
            MAX(product_length_cm) as max_length,
            AVG(product_photos_qty) as avg_photos
        FROM products
    """)
    result = cursor.fetchone()
    for key, value in result.items():
        print(f"  {key}: {value}")
    
    # 3. Payment Analysis
    print("\n💳 PAYMENT VALUES:")
    print("-" * 100)
    cursor.execute("""
        SELECT 
            payment_type,
            COUNT(*) as count,
            MIN(payment_value) as min_value,
            MAX(payment_value) as max_value,
            AVG(payment_value) as avg_value,
            SUM(payment_value) as total_value
        FROM order_payments
        GROUP BY payment_type
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"\n  {row['payment_type'].upper()}:")
        print(f"    Count: {row['count']}")
        print(f"    Min: R$ {row['min_value']:.2f}")
        print(f"    Max: R$ {row['max_value']:.2f}")
        print(f"    Avg: R$ {row['avg_value']:.2f}")
        print(f"    Total: R$ {row['total_value']:.2f}")
    
    # 4. Review Scores
    print("\n⭐ REVIEW SCORES:")
    print("-" * 100)
    cursor.execute("""
        SELECT 
            review_score,
            COUNT(*) as count
        FROM order_reviews
        GROUP BY review_score
        ORDER BY review_score DESC
    """)
    results = cursor.fetchall()
    for row in results:
        stars = "⭐" * row['review_score']
        print(f"  {stars} ({row['review_score']}): {row['count']} reviews")
    
    # 5. Product Performance Metrics
    print("\n📊 PRODUCT PERFORMANCE (Aggregated):")
    print("-" * 100)
    cursor.execute("""
        SELECT 
            product_category_name_english,
            total_orders,
            total_revenue,
            avg_price
        FROM product_performance
        ORDER BY total_revenue DESC
    """)
    results = cursor.fetchall()
    for row in results:
        print(f"\n  {row['product_category_name_english']}:")
        print(f"    Orders: {row['total_orders']}")
        print(f"    Revenue: R$ {row['total_revenue']:.2f}")
        print(f"    Avg Price: R$ {row['avg_price']:.2f}")
    
    cursor.close()
    connection.close()
    
    print("\n" + "=" * 100)
    print("✅ NUMERIC ANALYSIS COMPLETE")
    print("=" * 100)
    
    print("\n🎯 BEST NUMERIC COLUMNS FOR VISUALIZATION:")
    print("-" * 100)
    print("  1. ✅ price (order_items) - Harga produk")
    print("  2. ✅ freight_value (order_items) - Ongkir")
    print("  3. ✅ payment_value (order_payments) - Total pembayaran")
    print("  4. ✅ review_score (order_reviews) - Rating 1-5")
    print("  5. ✅ total_orders (product_performance) - Jumlah order per kategori")
    print("  6. ✅ total_revenue (product_performance) - Revenue per kategori")
    print("  7. ⚠️  product_weight_g (products) - Berat (varies widely)")
    print("  8. ⚠️  product_photos_qty (products) - Jumlah foto")

if __name__ == "__main__":
    find_numeric_columns()
