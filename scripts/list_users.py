import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from database.db_connection import DatabaseConnection
from database.user_manager import UserManager

def list_users():
    try:
        db_config = Config.get_db_config()
        db_conn = DatabaseConnection(db_config)
        user_mgr = UserManager(db_conn)
        
        users = user_mgr.get_all_users()
        
        print(f"\n{'ID':<5} {'Username':<20} {'Email':<30} {'Created At':<20}")
        print("-" * 80)
        
        for user in users:
            print(f"{user['id']:<5} {user['username']:<20} {user['email']:<30} {user['created_at']}")
            
        print("\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_users()
