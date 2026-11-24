# 🛠️ MySQL Workbench Setup Guide

## Installation Progress
✅ Downloading MySQL Workbench 8.0.45...
⏳ Please wait for installation to complete

---

## After Installation Complete:

### 1️⃣ Open MySQL Workbench
- Start Menu → MySQL Workbench 8.0 CE
- Or search "MySQL Workbench"

### 2️⃣ Create New Connection

**Click** the "+" icon next to "MySQL Connections"

**Fill in connection details:**
```
Connection Name: Ecommerce Olist
Connection Method: Standard (TCP/IP)
Hostname: 127.0.0.1
Port: 3306
Username: root
Password: (click "Store in Vault" → enter: root123)
Default Schema: ecommerce_olist
```

### 3️⃣ Test Connection
- Click "Test Connection" button
- Should say: "Successfully made the MySQL connection"
- Click "OK"

### 4️⃣ Connect & Browse
- Double-click your new connection
- Navigate via left sidebar:
  - Schemas → ecommerce_olist → Tables
  - Right-click table → "Select Rows - Limit 1000"

---

## 📊 Quick Queries to Try:

```sql
-- View all customers
SELECT * FROM customers LIMIT 10;

-- Count orders by status
SELECT order_status, COUNT(*) as count
FROM orders
GROUP BY order_status;

-- Top products by sales
SELECT 
    p.product_category_name,
    COUNT(*) as total_sales
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC
LIMIT 5;
```

---

## 🎯 Keyboard Shortcuts:

- **Execute Query**: `Ctrl + Enter`
- **Format Query**: `Ctrl + B`
- **New Query Tab**: `Ctrl + T`
- **Comment Line**: `Ctrl + /`

---

## ✅ Verification Steps:

After connecting, verify:
1. ☐ Can see all 13 tables in left sidebar
2. ☐ Can run SELECT query successfully
3. ☐ Can view table data in grid
4. ☐ Connection stays active

---

## 🆘 Troubleshooting:

**"Can't connect to MySQL server"**
- Check MySQL service is running
- Verify credentials (root / root123)
- Check port 3306 not blocked

**"Access denied for user 'root'"**
- Password might be wrong
- Try empty password first
- Or reset MySQL root password

---

## 📝 Next Steps:

Once connected, you can:
- ✅ Browse all tables visually
- ✅ Write & test custom queries
- ✅ Export data to CSV/Excel
- ✅ Create database diagrams
- ✅ Manage users & permissions

---

**Installation in progress...**
Please wait for completion message.
