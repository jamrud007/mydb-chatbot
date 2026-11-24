"""Force-verify a chatbot user in Oracle."""
from dotenv import load_dotenv
load_dotenv(override=True)
from core.config import Config
from database.db_connection import DatabaseConnection

db = DatabaseConnection(Config.get_db_config())
conn = db.get_connection()
cur = conn.cursor()
cur.execute("UPDATE chatbot_users SET is_verified=1 WHERE username='admin'")
conn.commit()
cur.execute("SELECT id, username, is_active, is_verified FROM chatbot_users")
for r in cur.fetchall():
    print(r)
cur.close()
conn.close()
print("Done")
