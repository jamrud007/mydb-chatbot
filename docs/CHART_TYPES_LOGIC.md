# 📊 Chart Type Selection Logic

## Kondisi Chart Type yang Tersedia

Sistem memiliki **4 jenis chart** dan memilih secara otomatis berdasarkan karakteristik data:

---

## 1. 🥧 **PIE CHART**

### Kondisi:
- ✅ Hanya 1 kolom numeric
- ✅ Data ≤ 10 baris
- ✅ Bukan time series
- ✅ Semua nilai positif (tidak ada negatif)
- ✅ Distribusi cukup seimbang (tidak ada 1 nilai >80% dari total)

### Contoh Query:
```sql
-- Status pesanan (part-to-whole relationship)
SELECT order_status, COUNT(*) as total
FROM orders
GROUP BY order_status;

-- Kategori produk (distribusi)
SELECT category, COUNT(*) as count
FROM products
GROUP BY category
LIMIT 5;
```

### Kapan TIDAK cocok:
- Lebih dari 10 kategori
- Ada nilai negatif
- 1 kategori mendominasi (>80%)
- **Lebih cocok untuk "proportion/distribution", bukan "comparison"**

---

## 2. 📈 **LINE CHART**

### Kondisi:
- ✅ Ada kolom **date/time** terdeteksi
- ✅ Ada kolom numeric untuk nilai

### Deteksi Time Series:
```
- Nama kolom: date, time, month, year, day, week, tanggal, bulan, tahun
- Format nilai: YYYY-MM-DD, timestamps
```

### Contoh Query:
```sql
-- Orders per bulan
SELECT DATE_FORMAT(order_date, '%Y-%m') as month, COUNT(*) as total_orders
FROM orders
GROUP BY month
ORDER BY month;

-- Penjualan harian
SELECT order_date, SUM(price) as daily_sales
FROM orders
GROUP BY order_date;
```

### Kegunaan:
- Menunjukkan **trend** dan perubahan seiring waktu
- Growth, seasonality analysis

---

## 3. 📊 **HORIZONTAL BAR CHART**

### Kondisi:
- ✅ Data > 8 baris, ATAU
- ✅ Label rata-rata panjang > 15 karakter

### Contoh Query:
```sql
-- Banyak kategori dengan nama panjang
SELECT product_category_name_english as category, COUNT(*) as count
FROM products
JOIN product_category_name_translation USING(product_category_name)
GROUP BY category
ORDER BY count DESC
LIMIT 20;
```

### Kegunaan:
- Label lebih mudah dibaca (tidak rotated)
- Best untuk comparison dengan banyak kategori

---

## 4. 📊 **VERTICAL BAR CHART** (Default)

### Kondisi:
- ✅ Ada kolom categorical (string)
- ✅ Ada kolom numeric
- ✅ Tidak memenuhi kriteria pie/line/horizontal bar

### Contoh Query:
```sql
-- Top 10 cities (comparison)
SELECT customer_city, COUNT(*) as total_customers
FROM customers
GROUP BY customer_city
ORDER BY total_customers DESC
LIMIT 10;

-- Product count by category
SELECT category, COUNT(*) as product_count
FROM products
GROUP BY category
ORDER BY product_count DESC
LIMIT 5;
```

### Kegunaan:
- **Membandingkan nilai** antar kategori
- **Best for "Top N" analysis**

---

## 🤔 Kenapa Query Anda Jadi Pie Chart?

### Your Query: "Top 10 cities by customer count"

**Hasil:**
```
10 rows:
belém: 1
belo horizonte: 1
brasilia: 1
curitiba: 1
fortaleza: 1
porto alegre: 1
recife: 1
rio de janeiro: 1
salvador: 1
sao paulo: 1
```

**Logika AI:**
1. ✅ Single numeric column (`total_customers`)
2. ✅ Exactly 10 rows (≤10)
3. ✅ No time series
4. ✅ All values = 1 (perfectly balanced)
5. ✅ All positive

→ **PIE CHART DIPILIH** untuk menunjukkan "distribusi" dari 10 kota

---

## 💡 Rekomendasi Perbaikan

Untuk query **"Top 10"**, sebenarnya **BAR CHART lebih cocok** karena:
- Fokusnya adalah **comparison** (siapa yang terbanyak?)
- Bukan **proportion** (berapa % dari total?)

### Solusi:

#### Opsi 1: Adjust Logic (Rekomendasi)
Tambahkan deteksi kata kunci "TOP" → paksa bar chart

#### Opsi 2: Minimum Rows untuk Pie
Ubah kondisi: **pie chart minimal 3 rows, maksimal 8 rows**
- <3 rows: bar chart  
- >8 rows: bar/horizontal bar

#### Opsi 3: User Override
Tambahkan tombol untuk switch chart type (user bisa pilih sendiri)

---

## 🔧 Mau Saya Perbaiki?

Saya bisa adjust logika agar:

**PIE CHART** hanya untuk:
- Query dengan keyword: "distribution", "percentage", "proportion"
- 3-8 rows (bukan 10)
- Nilai yang beragam (tidak semua sama)

**BAR CHART** untuk:
- Query dengan keyword: "top", "highest", "most", "terbanyak"
- Comparison scenarios
- >2 rows

Mau saya implement perubahan ini? 🚀
