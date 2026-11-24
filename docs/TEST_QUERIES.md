# 🧪 Test Queries for All Chart Types

## 📊 BAR CHART Examples

### 1. Top 10 Cities by Customer Count
```
Top 10 cities by customer count
```
**Expected**: Vertical Bar Chart (comparison)

### 2. Product Count by Category
```
How many products in each category?
```
**Expected**: Vertical Bar Chart

### 3. Top 5 Sellers
```
Show me the top 5 sellers by number of orders
```
**Expected**: Vertical Bar Chart

### 4. Customer Count per State
```
Count customers grouped by state, show top 15
```
**Expected**: Vertical Bar Chart (or horizontal if >8 rows)

---

## 📈 LINE CHART Examples

### 5. Orders Per Month
```
Show total orders per month in 2017
```
**Expected**: Line Chart (time series)

### 6. Daily Sales Trend
```
What is the daily sales trend for the last 30 days?
```
**Expected**: Line Chart

### 7. Monthly Revenue
```
Show monthly revenue over time
```
**Expected**: Line Chart

### 8. Orders by Year
```
Count orders grouped by year
```
**Expected**: Line Chart

---

## 🥧 PIE CHART Examples

### 9. Order Status Distribution (Best Case)
```
Show distribution of order status (delivered, shipped, canceled)
```
**Expected**: Pie Chart (5-8 categories, proportional)

### 10. Payment Type Distribution
```
What percentage of orders use each payment type?
```
**Expected**: Pie Chart

### 11. Category Distribution (Limited)
```
Show product distribution across top 5 categories
```
**Expected**: Pie Chart (if balanced distribution)

---

## 📊 HORIZONTAL BAR CHART Examples

### 12. Top 20 Product Categories
```
List all product categories with their counts
```
**Expected**: Horizontal Bar (>8 rows)

### 13. Long Category Names
```
Show product count by full category name in English
```
**Expected**: Horizontal Bar (long labels)

---

## ❌ NO CHART Examples

### 14. Too Many Rows
```
Show all customers with their cities
```
**Expected**: Table only (>50 rows)

### 15. No Numeric Data
```
List all product category names
```
**Expected**: Table only (no numeric column)

### 16. Single Row Result
```
What is the total number of customers?
```
**Expected**: Table only (<2 rows)

---

## 🎯 Specific Database Queries (E-commerce Olist)

### For BAR CHART:
```sql
-- Top sellers
SELECT seller_id, COUNT(*) as total_orders
FROM order_items
GROUP BY seller_id
ORDER BY total_orders DESC
LIMIT 10;

-- Top product categories
SELECT product_category_name, COUNT(*) as product_count
FROM products
GROUP BY product_category_name
ORDER BY product_count DESC
LIMIT 10;
```

### For LINE CHART:
```sql
-- Orders over time
SELECT DATE_FORMAT(order_purchase_timestamp, '%Y-%m') as month,
       COUNT(*) as order_count
FROM orders
WHERE YEAR(order_purchase_timestamp) = 2017
GROUP BY month
ORDER BY month;

-- Daily orders
SELECT DATE(order_purchase_timestamp) as date,
       COUNT(*) as daily_orders
FROM orders
WHERE order_purchase_timestamp >= DATE_SUB(NOW(), INTERVAL 90 DAY)
GROUP BY date
ORDER BY date;
```

### For PIE CHART:
```sql
-- Payment types (should be balanced)
SELECT payment_type, COUNT(*) as count
FROM order_payments
GROUP BY payment_type;

-- Order status
SELECT order_status, COUNT(*) as status_count
FROM orders
GROUP BY order_status;
```

---

## 🔧 Testing Checklist

Try these questions in the chatbot:

- [ ] "Top 10 cities by customer count" → Should be BAR not PIE
- [ ] "Show orders per month" → LINE chart
- [ ] "Distribution of payment types" → PIE chart
- [ ] "List 20 product categories" → HORIZONTAL BAR
- [ ] "Total orders by year" → LINE chart
- [ ] "Order status breakdown" → PIE chart
- [ ] "Top 5 sellers" → BAR chart
- [ ] "Customer count per state" → BAR or HORIZONTAL

---

## 💡 Expected Improvements Needed

After testing, we may need to adjust:

1. **Keyword Detection**:
   - "top N" → force BAR chart
   - "over time", "per month", "trend" → force LINE chart
   - "distribution", "percentage", "breakdown" → force PIE chart

2. **Data Characteristics**:
   - Pie chart: 3-7 rows optimal (not 10)
   - Bar chart: 2-15 rows
   - Horizontal bar: >8 rows or avg label length >15

3. **Balance Check**:
   - Pie chart: avoid if all values are same
   - Pie chart: avoid if 1 value > 70% of total

---

**Ready to test!** 🚀

Copy these queries and paste ke chatbot untuk lihat hasilnya!
