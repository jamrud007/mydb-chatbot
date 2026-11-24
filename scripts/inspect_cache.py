import sqlite3
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DB_PATH = "./data/cache.db"

def inspect_cache():
    if not os.path.exists(DB_PATH):
        print(f"Cache file not found at: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM query_cache")
        count = cursor.fetchone()['count']
        
        print(f"\nTime: {datetime.now()}")
        print(f"Cache Database: {DB_PATH}")
        print(f"Total Cached Queries: {count}")
        print("-" * 100)

        # Get recent entries
        cursor.execute("""
            SELECT id, user_question, query_text, row_count, created_at, access_count 
            FROM query_cache 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No cache entries found.")
        else:
            print(f"{'ID':<5} {'Time':<20} {'Rows':<5} {'Hits':<5} {'Question / Query'}")
            print("-" * 100)
            for row in rows:
                question = row['user_question'] if row['user_question'] else "Unknown Query"
                # If question is too long, truncate it
                if len(question) > 50:
                    question = question[:47] + "..."
                
                print(f"{row['id']:<5} {row['created_at']:<20} {row['row_count']:<5} {row['access_count']:<5} {question}")
                # Print SQL on next line if useful, or just keep it simple
                # print(f"      SQL: {row['query_text'][:80]}...")
                
        print("-" * 100)
        conn.close()

    except Exception as e:
        print(f"Error inspecting cache: {e}")

if __name__ == "__main__":
    inspect_cache()
