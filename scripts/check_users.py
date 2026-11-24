"""List chatbot app users and reset password if needed."""
from dotenv import load_dotenv
load_dotenv(override=True)

import mysql.connector, os

conn = mysql.connector.connect(
    host='localhost', port=3306,
    user='root', password='root123',
    database='ecommerce_olist'
)
cur = conn.cursor()

# Find user tables
cur.execute("SHOW TABLES")
tables = [t[0] for t in cur.fetchall()]
user_tables = [t for t in tables if 'user' in t.lower()]
print("User tables:", user_tables)

for t in user_tables:
    print(f"\n--- {t} ---")
    cur.execute(f"SELECT * FROM {t} LIMIT 20")
    cols = [d[0] for d in cur.description]
    print("Columns:", cols)
    for row in cur.fetchall():
        # mask password field
        row_dict = dict(zip(cols, row))
        if 'password' in [c.lower() for c in cols]:
            for k in row_dict:
                if 'password' in k.lower():
                    row_dict[k] = '***hidden***'
        print(row_dict)

conn.close()
