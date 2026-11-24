# 🌐 Remote Database Access Guide

Panduan lengkap untuk memberikan akses database MySQL localhost Anda kepada bot/aplikasi lain yang berjalan di komputer/server berbeda.

---

## 📋 Ringkasan

Bot/aplikasi lain akan bisa mengakses database MySQL Anda dengan:
- **Host**: IP publik komputer Anda (misal: `203.0.113.45`)
- **Port**: `3306` (default MySQL)
- **User**: `remote_bot` (user khusus dengan akses terbatas)
- **Password**: Password yang Anda tentukan
- **Database**: `ecommerce_olist` (sesuai `.env`)

---

## 🚀 Langkah Setup (Pilih Salah Satu)

### ✅ Opsi 1: Setup Otomatis (Recommended)

Gunakan script yang sudah disiapkan:

```bash
# Windows PowerShell
cd c:\Users\jamru\.gemini\antigravity\scratch\mysql-chatbot
python scripts/setup_remote_access.py
```

Script akan:
1. ✅ Membuat user MySQL baru untuk remote access
2. ✅ Update bind-address di MySQL configuration
3. ✅ Membuat firewall rule untuk port 3306
4. ✅ Memberikan panduan IP address untuk dibagikan

---

### 🔧 Opsi 2: Setup Manual

Jika ingin manual, ikuti langkah berikut:

#### **Step 1: Buat User MySQL untuk Remote Access**

```sql
-- Login ke MySQL
mysql -u root -p

-- Buat user baru (ganti 'password_yang_kuat' dengan password Anda)
CREATE USER 'remote_bot'@'%' IDENTIFIED BY 'password_yang_kuat';

-- Berikan akses ke database ecommerce_olist
-- Pilih salah satu sesuai kebutuhan:

-- A. Read-Only Access (SELECT saja) - RECOMMENDED untuk keamanan
GRANT SELECT ON ecommerce_olist.* TO 'remote_bot'@'%';

-- B. Full Access (SELECT, INSERT, UPDATE, DELETE)
-- GRANT ALL PRIVILEGES ON ecommerce_olist.* TO 'remote_bot'@'%';

-- Apply perubahan
FLUSH PRIVILEGES;

-- Verifikasi user sudah dibuat
SELECT user, host FROM mysql.user WHERE user = 'remote_bot';

-- Keluar
EXIT;
```

#### **Step 2: Update MySQL Configuration (Bind Address)**

MySQL secara default hanya menerima koneksi dari localhost. Kita perlu mengubahnya:

**Lokasi file konfigurasi MySQL:**
- Windows XAMPP: `C:\xampp\mysql\bin\my.ini`
- Windows MySQL standalone: `C:\ProgramData\MySQL\MySQL Server X.X\my.ini`
- Linux: `/etc/mysql/mysql.conf.d/mysqld.cnf`

**Edit file:**

```ini
# Cari baris ini (biasanya sekitar line 30-50):
bind-address = 127.0.0.1

# Ubah menjadi salah satu:
# Opsi 1: Izinkan semua IP (simpel, tapi kurang aman)
bind-address = 0.0.0.0

# Opsi 2: Izinkan IP tertentu saja (lebih aman, ganti dengan IP bot)
# bind-address = 192.168.1.100
```

**Restart MySQL Server:**

```bash
# Windows (XAMPP)
net stop mysql
net start mysql

# Windows (MySQL Service)
Restart-Service MySQL80

# Linux
sudo systemctl restart mysql
```

#### **Step 3: Buka Firewall untuk Port 3306**

**Windows Firewall:**

```powershell
# Buka PowerShell sebagai Administrator
# Buat rule untuk izinkan port 3306
New-NetFirewallRule -DisplayName "MySQL Remote Access" -Direction Inbound -Protocol TCP -LocalPort 3306 -Action Allow
```

**Linux (UFW):**

```bash
# Izinkan port 3306
sudo ufw allow 3306/tcp

# Atau izinkan IP tertentu saja (lebih aman)
sudo ufw allow from 192.168.1.100 to any port 3306
```

#### **Step 4: Dapatkan IP Address Anda**

**Windows:**
```powershell
# Cek IP lokal (untuk akses dalam jaringan lokal)
ipconfig

# Lihat bagian "IPv4 Address" di adapter yang aktif
# Contoh: 192.168.1.50

# Cek IP publik (untuk akses dari internet)
curl ifconfig.me
# Contoh: 203.0.113.45
```

**Linux:**
```bash
# IP lokal
ip addr show | grep inet

# IP publik
curl ifconfig.me
```

---

## 🔌 Connection String untuk Bot Lain

Setelah setup selesai, berikan informasi berikut ke bot/aplikasi lain:

### **Jika Bot dalam 1 Jaringan (LAN):**

```bash
# Format connection string
mysql://remote_bot:password_yang_kuat@192.168.1.50:3306/ecommerce_olist

# Atau dalam format .env:
DB_HOST=192.168.1.50         # Ganti dengan IP lokal Anda
DB_PORT=3306
DB_USER=remote_bot
DB_PASSWORD=password_yang_kuat
DB_NAME=ecommerce_olist
```

### **Jika Bot dari Internet (Public Access):**

> ⚠️ **PERINGATAN KEAMANAN**: Mengekspos database ke internet **sangat berisiko**!
> Pastikan:
> - Password super kuat (20+ karakter)
> - User hanya punya akses read-only
> - Pertimbangkan gunakan VPN atau SSH tunnel

```bash
# Format connection string
mysql://remote_bot:password_yang_kuat@203.0.113.45:3306/ecommerce_olist

# Atau dalam format .env:
DB_HOST=203.0.113.45         # Ganti dengan IP publik Anda
DB_PORT=3306
DB_USER=remote_bot
DB_PASSWORD=password_yang_kuat
DB_NAME=ecommerce_olist
```

**Catatan**: Jika Anda di belakang router, Anda perlu **Port Forwarding**:
1. Login ke router (biasanya 192.168.1.1)
2. Cari menu "Port Forwarding" atau "Virtual Server"
3. Forward port **3306** ke IP lokal komputer Anda (192.168.1.50)

---

## 🔒 Rekomendasi Keamanan

### ✅ Level 1: Basic Security (Minimum)
```sql
-- User dengan read-only access
GRANT SELECT ON ecommerce_olist.* TO 'remote_bot'@'%';
```

### ✅ Level 2: Medium Security (Recommended)
```sql
-- User hanya dari IP tertentu (ganti IP_BOT_LAIN)
CREATE USER 'remote_bot'@'192.168.1.100' IDENTIFIED BY 'password_yang_kuat';
GRANT SELECT ON ecommerce_olist.* TO 'remote_bot'@'192.168.1.100';

-- Firewall hanya izinkan IP tertentu
New-NetFirewallRule -DisplayName "MySQL Remote Access" `
  -Direction Inbound -Protocol TCP -LocalPort 3306 `
  -RemoteAddress 192.168.1.100 -Action Allow
```

### ✅ Level 3: High Security (Production)
```sql
-- Gunakan SSL/TLS untuk koneksi encrypt
-- Require SSL connection
GRANT SELECT ON ecommerce_olist.* TO 'remote_bot'@'%' REQUIRE SSL;

-- Atau gunakan SSH tunnel (tidak ekspos port 3306 ke internet)
# Dari komputer bot lain:
ssh -L 3306:localhost:3306 user@your-server-ip
# Kemudian connect ke localhost:3306
```

---

## 🧪 Testing Connection

### **Test dari Bot Lain (Python):**

```python
import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        connection = mysql.connector.connect(
            host='192.168.1.50',      # Ganti dengan IP Anda
            port=3306,
            user='remote_bot',
            password='password_yang_kuat',
            database='ecommerce_olist'
        )
        
        if connection.is_connected():
            print("✅ Koneksi berhasil!")
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            record = cursor.fetchone()
            print(f"📊 Database aktif: {record[0]}")
            
            # Test query
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"📋 Jumlah tabel: {len(tables)}")
            
    except Error as e:
        print(f"❌ Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Koneksi ditutup")

test_connection()
```

### **Test dengan MySQL Client:**

```bash
# Dari komputer bot lain
mysql -h 192.168.1.50 -P 3306 -u remote_bot -p ecommerce_olist

# Jika berhasil, akan muncul:
# MySQL [(ecommerce_olist)]>

# Test query
SHOW TABLES;
SELECT COUNT(*) FROM customers;
```

---

## ❓ Troubleshooting

### **Error: Can't connect to MySQL server**

**Solusi:**
1. ✅ Pastikan MySQL server berjalan: `net start mysql`
2. ✅ Cek firewall: `Get-NetFirewallRule -DisplayName "MySQL Remote Access"`
3. ✅ Ping IP server dari bot lain: `ping 192.168.1.50`
4. ✅ Cek MySQL mendengarkan di 0.0.0.0: `netstat -an | findstr 3306`

### **Error: Access denied for user 'remote_bot'@'IP'**

**Solusi:**
1. ✅ Cek password benar
2. ✅ Cek user exists: `SELECT user, host FROM mysql.user WHERE user = 'remote_bot';`
3. ✅ Cek privileges: `SHOW GRANTS FOR 'remote_bot'@'%';`
4. ✅ Re-create user dengan `DROP USER` lalu `CREATE USER` lagi

### **Error: Lost connection to MySQL server during query**

**Solusi:**
1. ✅ Cek `max_allowed_packet` di my.ini (set ke `64M` atau lebih)
2. ✅ Cek `wait_timeout` di my.ini (set ke `28800`)
3. ✅ Restart MySQL setelah edit config

---

## 🔄 Revoke Access (Cabut Akses)

Jika sudah tidak perlu akses:

```sql
-- Login ke MySQL
mysql -u root -p

-- Cabut semua privileges
REVOKE ALL PRIVILEGES ON ecommerce_olist.* FROM 'remote_bot'@'%';

-- Atau hapus user sepenuhnya
DROP USER 'remote_bot'@'%';

-- Apply perubahan
FLUSH PRIVILEGES;
```

**Hapus firewall rule:**
```powershell
Remove-NetFirewallRule -DisplayName "MySQL Remote Access"
```

---

## 📚 Referensi

- [MySQL 8.0 Remote Access](https://dev.mysql.com/doc/refman/8.0/en/connecting.html)
- [MySQL User Management](https://dev.mysql.com/doc/refman/8.0/en/account-management-statements.html)
- [MySQL Security Best Practices](https://dev.mysql.com/doc/refman/8.0/en/security-guidelines.html)

---

## ✅ Checklist Setup

Sebelum memberikan akses:

- [ ] User `remote_bot` sudah dibuat dengan password kuat
- [ ] Privileges sudah diberikan (SELECT atau ALL)
- [ ] `bind-address` sudah diubah ke `0.0.0.0`
- [ ] MySQL server sudah di-restart
- [ ] Firewall rule sudah dibuat untuk port 3306
- [ ] IP address sudah dicatat (lokal atau publik)
- [ ] Connection sudah di-test dari komputer lain
- [ ] Credentials sudah dibagikan ke bot lain (aman)

---

**🎉 Selamat! Database Anda sekarang bisa diakses secara remote!**
