# MySQL Setup Script

## After MySQL Installation

1. **Set MySQL root password** (during installation or after):
   - Default password prompt will appear
   - Remember this password for `.env` configuration

2. **Update .env file**:
   ```
   DB_PASSWORD=your_mysql_password_here
   ```

3. **Create database and load sample data**:
   ```bash
   # Login to MySQL
   mysql -u root -p
   
   # Create database
   CREATE DATABASE ecommerce_olist CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   EXIT;
   
   # Load sample data
   mysql -u root -p < sample_db\create_sample_db.sql
   ```

4. **Verify database**:
   ```bash
   mysql -u root -p ecommerce_olist -e "SHOW TABLES;"
   ```

## Quick Alternative (If installer hangs):

Download portable MySQL:
https://dev.mysql.com/downloads/mysql/

Or use XAMPP (includes MySQL + phpMyAdmin):
```bash
winget install ApacheFriends.Xampp.8.2
```

## Test Connection After Setup

```bash
python deploy_check.py
```

Should show all checks passed!
