
import mysql.connector
from mysql.connector import Error
import sys
import os

# Add parent dir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config

def migrate_db():
    print("Migrating Database Schema...")
    
    try:
        conn = mysql.connector.connect(**Config.get_db_config())
        cursor = conn.cursor()
        
        # Add is_verified column
        try:
            print("Adding is_verified column...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE;")
            print("[OK] Added is_verified")
        except Error as e:
            if "Duplicate column" in str(e):
                print("[SKIP] is_verified already exists")
            else:
                print(f"[FAIL] Failed to add is_verified: {e}")

        # Add verification_code column
        try:
            print("Adding verification_code column...")
            cursor.execute("ALTER TABLE users ADD COLUMN verification_code VARCHAR(6);")
            print("[OK] Added verification_code")
        except Error as e:
            if "Duplicate column" in str(e):
                print("[SKIP] verification_code already exists")
            else:
                print(f"[FAIL] Failed to add verification_code: {e}")
        
        conn.commit()
        print("Migration Complete.")
        
    except Error as e:
        print(f"❌ Database error: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    migrate_db()
