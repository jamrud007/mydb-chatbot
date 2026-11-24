# Cara Akses MySQL Database Langsung

## 1️⃣ MySQL Command Line (Tercepat)

### Windows:
```bash
mysql -u root -p
# Enter password: root123

# Setelah login:
USE ecommerce_olist;
SHOW TABLES;
SELECT * FROM customers;
```

## 2️⃣ MySQL Workbench (GUI - Recommended)

1. Download: https://dev.mysql.com/downloads/workbench/
2. Install dan buka
3. Klik "+" untuk new connection
4. Isi:
   - Connection Name: Ecommerce Olist
   - Hostname: 127.0.0.1
   - Port: 3306
   - Username: root
   - Password: root123
5. Test Connection → OK
6. Double click connection
7. Browse tables di kiri sidebar

## 3️⃣ DBeaver (Free, Universal)

1. Download: https://dbeaver.io/download/
2. Install
3. Database → New Connection → MySQL
4. Isi credentials sama seperti di atas

## 4️⃣ Via Chatbot (Sudah Ada!)

Buka: http://localhost:5000
Klik tombol "View Schema" di pojok kanan atas
Akan tampil semua tables dan columns

## 5️⃣ phpMyAdmin (Jika installed)

Biasanya di: http://localhost/phpmyadmin
(Hanya jika Anda pakai XAMPP/WAMP)

---

## 🎯 Rekomendasi:

**Untuk quick check**: 
- MySQL Command Line (cepat)
- Chatbot "View Schema" button

**Untuk analisis mendalam**:
- MySQL Workbench (official, powerful)
- DBeaver (multi-database support)

---

## 📌 Connection Info:
```
Host: localhost
Port: 3306
User: root
Password: root123
Database: ecommerce_olist
```
